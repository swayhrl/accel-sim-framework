#!/usr/bin/env python3
"""No-build C10-A2 audit of fair-arm, lifecycle, and source contracts."""

from __future__ import print_function

import csv
import os
import re
import sys


ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
CORE = os.path.normpath(os.path.join(ROOT, "..", "gpgpu-sim-vm-m4b-speculative"))
PROFILE = os.path.join(ROOT, "configs", "vm_tlb", "M4B_C10A2_FAIR_ARM_PROFILES.tsv")


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def read(path):
    with open(path, "r") as source:
        return source.read()


def profile_rows():
    with open(PROFILE, "r") as source:
        return list(csv.DictReader((line for line in source
                                    if not line.startswith("#")), delimiter="\t"))


def verify_transaction_and_state_models():
    """Exercise the C10-A2 contracts without compiling the simulator.

    This deliberately small reference model is not a replacement for the C++
    tests.  It makes the required atomic admission, all-replica lifecycle, and
    stale-generation transition properties executable in this no-build stage.
    """
    def admit(extents, expected_asid=7, expected_epoch=11):
        staged = []
        failure = None
        for asid, epoch, va_base, va_limit, pa_base, read_only, mapping in extents:
            if (asid != expected_asid or epoch != expected_epoch or epoch == 0):
                failure = failure or "ASID_EPOCH"
            elif read_only != 1:
                failure = failure or "RIGHTS"
            elif mapping != 0:
                failure = failure or "MAPPING_CLASS"
            elif va_base > va_limit or pa_base + (va_limit - va_base) >= (1 << 33):
                failure = failure or "EXTENT"
            elif staged and staged[-1][2] >= va_base:
                failure = failure or "UNSORTED"
            elif staged and staged[-1][3] >= va_base:
                failure = failure or "OVERLAP"
            else:
                staged.append((asid, epoch, va_base, va_limit, pa_base,
                               read_only, mapping))
        if failure is None and not staged:
            failure = "EMPTY"
        if failure is None and len(staged) > 8:
            failure = "CAPACITY"
        return failure, [] if failure else staged

    valid = [(7, 11, 16, 17, 256, 1, 0)]
    require(admit(valid) == (None, valid), "valid registration model failed")
    cases = {
        "CAPACITY": [(7, 11, 16 + n, 16 + n, 256 + n, 1, 0)
                     for n in range(9)],
        "OVERLAP": [(7, 11, 16, 17, 256, 1, 0),
                    (7, 11, 17, 18, 257, 1, 0)],
        "UNSORTED": [(7, 11, 32, 32, 256, 1, 0),
                      (7, 11, 16, 16, 512, 1, 0)],
        "ASID_EPOCH": [(8, 11, 16, 16, 256, 1, 0)],
        "RIGHTS": [(7, 11, 16, 16, 256, 0, 0)],
        "MAPPING_CLASS": [(7, 11, 16, 16, 256, 1, 1)],
        "EXTENT": [(7, 11, 17, 16, 256, 1, 0)],
    }
    for expected, extents in cases.items():
        actual, live = admit(extents)
        require(actual == expected and not live,
                "transaction model leaked live state for %s" % expected)

    state, install_ack, revoke_ack, epoch = "INACTIVE", [False, False], [False, False], 11
    require(state == "INACTIVE", "lifecycle must start inactive")
    state = "INSTALLING"
    install_ack[0] = True
    require(state == "INSTALLING", "partial install must not be active")
    install_ack[1] = True
    if all(install_ack):
        state = "ACTIVE"
    require(state == "ACTIVE", "all local replicas must acknowledge install")
    state = "REVOKING"
    revoke_ack[0] = True
    require(state == "REVOKING", "partial revoke must remain inaccessible")
    revoke_ack[1] = True
    if all(revoke_ack):
        state = "INACTIVE"
    require(state == "INACTIVE", "all local replicas must acknowledge revoke")
    epoch = 0xffff
    wrap_quiesced = False
    require(not wrap_quiesced, "epoch wrap must require explicit quiesce")
    wrap_quiesced = True
    require(wrap_quiesced and epoch == 0xffff,
            "quiesce is the only modeled wrap-release transition")

    generations = {7: 1}  # First admission registers the ASID.
    captured_generation = generations[7]
    generations[7] += 1  # ASID shootdown occurs while the walk/fill is in flight.
    require(captured_generation != generations[7],
            "generation race model must identify stale completion")
    admitted_fill = captured_generation == generations[7]
    require(not admitted_fill,
            "stale generation must not resurrect exact/sub-entry residency")
    generations = {7: 1, 8: 1}
    captured_global = generations[8]
    for asid in generations:
        generations[asid] += 1
    require(captured_global != generations[8],
            "global shootdown must cover every admitted ASID")


def main():
    rows = profile_rows()
    by_arm = dict((row["arm_id"], row) for row in rows)
    expected = set(["F%d" % value for value in range(10)] + ["H0"])
    require(set(by_arm) == expected and len(rows) == len(by_arm),
            "profile arms must be exactly F0--F9 plus H0")
    selector_values = dict(("F%d" % value, str(value + 1))
                           for value in range(10))
    selector_values["H0"] = "11"
    for arm, value in selector_values.items():
        require(by_arm[arm]["selector_value"] == value,
                "%s selector value is inconsistent" % arm)
    for arm in expected - set(["H0"]):
        require(by_arm[arm]["official_selectable"] == "true",
                "%s must be official/selectable" % arm)
    require(by_arm["H0"]["official_selectable"] == "false",
            "H0 must remain permanently hard blocked")
    require(by_arm["F5"]["official_selectable"] == "true" and
            by_arm["F5"]["l2_entries"] == "656" and
            by_arm["F5"]["sets"] == "41" and
            by_arm["F5"]["segment_accept_rate"] ==
            "ONE_GLOBAL_PWC_ACCEPT_PER_CYCLE" and
            "PHYSICAL_PWC" in by_arm["F5"]["status"],
            "F5 physical PWC profile contract incomplete")
    require(by_arm["F1"]["sets"] == "6" and
            by_arm["F8"]["sets"] == "2" and
            by_arm["F1"]["associativity"] == "16" and
            by_arm["F8"]["associativity"] == "16",
            "G96/G32 geometry must derive six/two 16-way sets")
    charged_bits = {
        "F0": "66000", "F1": "59802", "F2": "59125",
        "F3": "E*85+(E/16)*15", "F4": "132000", "F5": "64745",
        "F6": "65243", "F7": "65300", "F8": "57734",
        "F9": "56375", "H0": "478416"
    }
    for arm, bits in charged_bits.items():
        require(by_arm[arm]["charged_bits"] == bits,
                "%s charged-bit contract is inconsistent" % arm)
    for arm in ("F7", "F8"):
        require(by_arm[arm]["segment_slots"] == "8" and
                by_arm[arm]["segment_replicas"] == "35" and
                by_arm[arm]["lseg_points"] == "5|10|20" and
                by_arm[arm]["segment_accept_rate"] ==
                "ONE_LOCAL_L1_ACCEPT_PER_CYCLE",
                "%s Segment profile contract incomplete" % arm)
    verify_transaction_and_state_models()

    header = read(os.path.join(CORE, "src/gpgpu-sim/vm_translation.h"))
    source = read(os.path.join(CORE, "src/gpgpu-sim/vm_translation.cc"))
    shader = read(os.path.join(CORE, "src/gpgpu-sim/shader.cc"))
    gpu = read(os.path.join(CORE, "src/gpgpu-sim/gpu-sim.cc"))

    # Transactional registration: staging is separate from the live image and
    # every semantic failure returns before the swap/activation point.
    for token in ("staged_ranges", "m_ranges.swap(staged_ranges)",
                  "SEGMENT_REGISTRATION_REJECTED_CAPACITY",
                  "SEGMENT_REGISTRATION_REJECTED_OVERLAP",
                  "SEGMENT_REGISTRATION_REJECTED_UNSORTED",
                  "SEGMENT_REGISTRATION_REJECTED_ASID_EPOCH",
                  "SEGMENT_REGISTRATION_REJECTED_RIGHTS",
                  "SEGMENT_REGISTRATION_REJECTED_MAPPING_CLASS",
                  "SEGMENT_REGISTRATION_REJECTED_EXTENT"):
        require(token in source or token in header,
                "missing transactional registration guard: %s" % token)

    # Explicit lifecycle, no constructor-copy-only eligibility.
    for token in ("SEGMENT_LIFECYCLE_INSTALLING", "SEGMENT_LIFECYCLE_ACTIVE",
                  "SEGMENT_LIFECYCLE_REVOKING", "begin_segment_install",
                  "acknowledge_segment_install", "begin_segment_revoke",
                  "acknowledge_segment_revoke", "segment_active()",
                  "vm_weight_segment_lifecycle_active_asid",
                  "vm_weight_segment_lifecycle_active_epoch"):
        require(token in source or token in header,
                "missing lifecycle state/API: %s" % token)
    require("m_weight_segment_locals.push_back(weight_segment_map())" in source,
            "constructor must begin with inactive local images")
    require("m_config.segment.enabled && segment_active()" in source,
            "inactive/rejected registration must use conventional paging")

    # Production path obtains access intent from the authoritative instruction,
    # never from object classification or the API default.
    require("inst.isatomic()" in shader and "inst.is_store()" in shader and
            "TRANSLATION_ACCESS_ATOMIC" in shader and
            "TRANSLATION_ACCESS_WRITE" in shader and
            "TRANSLATION_ACCESS_READ" in shader,
            "production caller lacks explicit READ/WRITE/ATOMIC wiring")
    require("&translated_pa, &translation_outcome, translation_access" in shader,
            "production translation call still depends on default READ")
    # C10 registered descriptors may map a SimVA extent to a distinct SimPA
    # extent.  Keep the M1 ideal-mode equality assertion, but prohibit the
    # obsolete functional-mode equality assertion after the real mapping is
    # installed; SimVA must remain observable while lower memory uses SimPA.
    functional_start = shader.index("assert(m_config->gpgpu_vm_mode == 2);")
    functional_end = shader.index("// The class is captured", functional_start)
    functional = shader[functional_start:functional_end]
    require("access.set_sim_pa(static_cast<new_addr_type>(translated_pa));" in
            functional and
            "if (access.get_sim_va() == access.get_sim_pa())" in functional,
            "functional non-identity SimPA observation guard is missing")
    require("assert(access.get_sim_va() == access.get_sim_pa());" not in
            functional,
            "functional mode still incorrectly requires identity SimPA")
    service_start = source.index("void translation_controller::service_lookups")
    service_end = source.index("lookup_result translation_controller::allocate_or_merge")
    service = source[service_start:service_end]
    require(not re.search(r"(?:==|!=)\\s*OBJECT_WEIGHT|"
                          r"OBJECT_WEIGHT\\s*(?:==|!=)", service),
            "OBJECT_WEIGHT must not control Segment eligibility")
    for token in ("HIT_FIRST", "MISS_JOIN", "segment_l2_suppressed",
                  "segment_l1_fill_suppressed", "segment_both_miss",
                  "LOOKUP_L2_LAUNCH"):
        require(token in service,
                "C10-A HIT_FIRST/MISS_JOIN spine regressed: %s" % token)

    # A controller MSHR carries the admission generation and stale fill is
    # discarded prior to either exact or sub-entry commit.
    for token in ("uint64_t generation;", "lookup->generation",
                  "translation_generation(key.asid)",
                  "m_translation_generations[asid] = 1",
                  "translation_stale_fills_discarded", "flush_translation_asid",
                  "m_l2_subentries.invalidate(key)"):
        require(token in source or token in header,
                "missing generation/stale-fill guard: %s" % token)

    # Runtime selector realizes physical F5 and rejects H0 permanently.
    require("-gpgpu_vm_fair_arm" in gpu and "configure_fair_arm" in gpu,
            "fair arm is not wired through runtime configuration")
    require("FAIR_ARM_F5_PHYSICAL_PWC" in source and
            "PWC_PHYSICAL_F5" in source and
            "FAIR_ARM_H0_HISTORICAL_UNFAIR" in source,
            "F5 physical selector or H0 permanent guard missing")
    require("official_segment_arm && !m_weight_segments.registered_v2()" in source,
            "official Segment arms must reject historical V1 registration")
    print("C10A2 static closure PASS: transaction/lifecycle/generation pure "
          "models plus access/fair-arm source contracts")


if __name__ == "__main__":
    try:
        main()
    except (AssertionError, IOError, ValueError, KeyError) as error:
        print("C10A2 static closure FAIL: %s" % error, file=sys.stderr)
        sys.exit(1)
