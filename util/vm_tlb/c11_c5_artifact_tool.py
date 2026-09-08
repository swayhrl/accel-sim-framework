#!/usr/bin/env python3
"""Generate and validate C11's immutable C5 input/configuration artifacts.

This utility is deliberately input-only: it never invokes a simulator and it
never opens a trace payload.  It hashes only the small list/metadata/config
files and checks that every list entry names an existing immutable trace.
"""

from __future__ import print_function

import argparse
import hashlib
import json
import pathlib
import re
import sys


ROOT = pathlib.Path(__file__).resolve().parents[2]
CORE = pathlib.Path("/workspace/worktrees/gpgpu-sim-vm-m4b-speculative")
PAGE = 64 * 1024
PA_OFFSET = 3 * (1 << 46)
PA_OFFSET_HEX = "0x0000c00000000000"
EXPECTED = {
    "prefill": {
        "list": pathlib.Path(
            "/workspace/m4c-c3-formal-20260905-v1/prefill-generic/traces/kernelslist.g"),
        "trace_root": pathlib.Path(
            "/workspace/m4c-c3-formal-20260905-v1/prefill-generic/traces"),
        "list_sha": "a40d6832219e5b0a6232875bb181754ac121bb5f867c9b13c84370e2a2cb6e6f",
        "archive": pathlib.Path(
            "/workspace/m4a-rented-host-pilot/formal-prefill/m4a-llama-prefill-20260902T182016Z.tar.zst"),
        "archive_sha": "f96b7ea91b798e2ce8eb8f4592b1ef6512a762870471d2dbb85ab4777c97f181",
        "sidecar": pathlib.Path(
            "/workspace/m4a-rented-host-pilot/formal-prefill/extracted/m4a-llama-prefill-20260902T182016Z/allocation-sidecar.json"),
        "sidecar_sha": "8b605b8b19034613106a61ab993dcab60b6eb34509293074b123b44ceeaa839a",
        "source_sha": "08bd106f6597865e622465ee3bd13233f7d49fd1eef131965fd2692956091e7a",
        "object_map": ROOT / "configs/vm_tlb/object_maps/M4C_PREFILL_OBJECT_MAP.tsv",
        "object_map_sha": "7ec6e868f8190ba6493124cb518753ccc7d14cbbd2ad169777cac9fbd6742a85",
        "va": 0x7FD99E000000,
    },
    "decode1": {
        "list": pathlib.Path(
            "/workspace/m4c-c3-formal-20260905-v1/decode1-generic/traces/kernelslist.g"),
        "trace_root": pathlib.Path(
            "/workspace/m4c-c3-formal-20260905-v1/decode1-generic/traces"),
        "list_sha": "b6c42eb1932fcacefc2429b91a2015d38003a764a5319fe4bcbaf65b3d0cd0dc",
        "archive": pathlib.Path(
            "/workspace/m4a-rented-host-pilot/formal-decode1/m4a-llama-decode1-20260903T004138Z.tar.zst"),
        "archive_sha": "5bdd4b55ed0e1499cbfee756d289cbd8072f556db4f467a882a54e42cd32dcad",
        "sidecar": pathlib.Path(
            "/workspace/m4a-rented-host-pilot/formal-decode1/extracted/m4a-llama-decode1-20260903T004138Z/allocation-sidecar.json"),
        "sidecar_sha": "7a07d6715fe79abd24cfc0b12d2619555e0bf472f5285781e098940acefccaa7",
        "source_sha": "44bfae640360be7fc884589c65b261a791e7c388d9d88b7d2742d7eaea7dba4d",
        "object_map": ROOT / "configs/vm_tlb/object_maps/M4C_DECODE1_OBJECT_MAP.tsv",
        "object_map_sha": "b1dd8745d5a9fd418d03c4bab82627d820c161b6f990f913e6f90583e72e3340",
        "va": 0x7F7EC6000000,
    },
}
SIZE = 1012011008
BASE = ROOT / "gpu-simulator/gpgpu-sim/configs/tested-cfgs/SM86_RTX3070/gpgpusim.config"
TRACE_CFG = ROOT / "gpu-simulator/configs/tested-cfgs/SM86_RTX3070/trace.config"
SHELL = ROOT / "configs/vm_tlb/M4B_SPECULATIVE_SUBENTRY16_WEIGHT_SEGMENT.config"
CONFIG_DIR = ROOT / "configs/vm_tlb/c5_configs"
TRACE_MANIFEST_DIR = ROOT / "configs/vm_tlb/c5_trace_manifests"
REG_DIR = ROOT / "configs/vm_tlb/c5_registrations"
PACK = ROOT / ("docs/vm_tlb/review_packs/M4B_SPECULATIVE_DEVELOPMENT/"
               "C11_C5_PREFILL_PROVENANCE_CLOSURE")

ARMS = (
    ("F0", 1, "NONE", 66000, "exact-768"),
    ("F1", 2, "NONE", 59802, "subentry-G96"),
    ("F2", 3, "NONE", 59125, "exact-688"),
    ("F5", 6, "NONE", 64745, "physical-PWC-120+exact-656"),
    ("F7", 8, "5", 65300, "Segment-N8+exact-320"),
    ("F7", 8, "10", 65300, "Segment-N8+exact-320"),
    ("F7", 8, "20", 65300, "Segment-N8+exact-320"),
    ("F8", 9, "5", 57734, "Segment-N8+G32"),
    ("F8", 9, "10", 57734, "Segment-N8+G32"),
    ("F8", 9, "20", 57734, "Segment-N8+G32"),
    ("F9", 10, "NONE", 56375, "exact-656-no-Segment"),
)


def digest(path):
    data = pathlib.Path(path).read_bytes()
    return hashlib.sha256(data).hexdigest()


def required(path):
    if not pathlib.Path(path).is_file():
        raise AssertionError("missing required input: %s" % path)


def required_dir(path):
    if not pathlib.Path(path).is_dir():
        raise AssertionError("missing required directory: %s" % path)


def write_if_changed(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = text.encode("utf-8")
    if path.is_file() and path.read_bytes() == encoded:
        return
    path.write_bytes(encoded)


def registration_path(roi):
    return REG_DIR / ("C11_C5_%s_V2_REGISTRATION.tsv" % roi.upper())


def config_name(roi, arm, lseg):
    suffix = "" if lseg == "NONE" else "_Lseg%s" % lseg
    return "C11_C5_%s_%s%s.config" % (roi.upper(), arm, suffix)


def config_body(roi, arm, arm_id, lseg):
    # Fair selection makes F0/F1/F2/F5/F9 Segment-disabled after parsing.
    # They intentionally seed a legal V2 map path so conventional PTW uses
    # the same driver PA backend; F7/F8 retain the requested Lseg point.
    seed_latency = 5 if lseg == "NONE" else int(lseg)
    registration = registration_path(roi)
    objmap = EXPECTED[roi]["object_map"]
    pieces = [
        "# C11 generated immutable C5 configuration bundle.\n",
        "# SPECULATIVE_CANDIDATE; REFERENCE_APPROX_SUBENTRY_16 where selected.\n",
        BASE.read_text(), TRACE_CFG.read_text(), SHELL.read_text(),
        "\n# C11 binding override: C9's 49-bit modeled PA namespace.\n",
        "-gpgpu_n_clusters 35\n-gpgpu_n_mem 12\n",
        "-gpgpu_vm_application_physical_limit 562949953421312\n",
        "-gpgpu_vm_pte_physical_base 562949953421312\n",
        "-gpgpu_vm_pte_physical_bytes 549755813888\n",
        "-gpgpu_vm_object_map %s\n" % objmap,
        "-gpgpu_vm_weight_segmentation_enable 1\n",
        "-gpgpu_vm_weight_segment_entries 8\n",
        "-gpgpu_vm_weight_segment_lookup_latency %u\n" % seed_latency,
        "-gpgpu_vm_weight_segment_map %s\n" % registration,
        "-gpgpu_vm_fair_arm %u\n" % arm_id,
        "-gpgpu_memory_telemetry_level 2\n",
        "-gpgpu_memory_telemetry_window_transactions 1000000\n",
    ]
    return "".join(pieces)


def generate():
    for path in (BASE, TRACE_CFG, SHELL):
        required(path)
    rows = ["roi\tarm\tlseg\tconfig_path\tconfig_sha256\tregistration_path\tregistration_sha256\tcharged_bits\trealized_geometry\n"]
    for roi in sorted(EXPECTED):
        data = EXPECTED[roi]
        trace_manifest = (
            "C11_C5_TRACE_MANIFEST_V1\n"
            "roi\t%s\nsource_list\t%s\nsource_list_sha256\t%s\n"
            "trace_root\t%s\narchive\t%s\narchive_sha256\t%s\n"
            "A_checkpoint\t14edbe200859f6ddf42bc3d459334f184a920a82\n"
            "list_mode\tPROVENANCE_BOUND_IMMUTABLE_SOURCE_NO_COPY\n" %
            (roi, data["list"], data["list_sha"], data["trace_root"],
             data["archive"], data["archive_sha"]))
        write_if_changed(TRACE_MANIFEST_DIR / ("C11_C5_%s_TRACE.tsv" % roi.upper()),
                         trace_manifest)
        reg = registration_path(roi)
        required(reg)
        reg_sha = digest(reg)
        for arm, arm_id, lseg, bits, geometry in ARMS:
            name = config_name(roi, arm, lseg)
            path = CONFIG_DIR / name
            write_if_changed(path, config_body(roi, arm, arm_id, lseg))
            rows.append("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" %
                        (roi, arm, lseg, path.relative_to(ROOT), digest(path),
                         reg.relative_to(ROOT), reg_sha, bits, geometry))
    write_if_changed(CONFIG_DIR / "C11_C5_CONFIG_MANIFEST.tsv", "".join(rows))


def ipoly32(higher, index):
    b = [(index >> n) & 1 for n in range(5)]
    a = [(higher >> n) & 1 for n in range(64)]
    equations = ((13, 12, 11, 10, 9, 6, 5, 3, 0),
                 (14, 13, 12, 11, 10, 7, 6, 4, 1),
                 (14, 10, 9, 8, 7, 6, 3, 2, 0),
                 (11, 10, 9, 8, 7, 4, 3, 1),
                 (12, 11, 10, 9, 8, 5, 4, 2))
    answer = 0
    for bit, terms in enumerate(equations):
        value = b[bit]
        for term in terms:
            value ^= a[term]
        answer |= value << bit
    return answer


def validate_trace(roi, facts):
    required(facts["list"])
    required_dir(facts["trace_root"])
    assert digest(facts["list"]) == facts["list_sha"]
    names = facts["list"].read_text().splitlines()
    assert names and len(names) == len(set(names))
    for name in names:
        assert re.match(r"^[A-Za-z0-9._-]+\.traceg\.xz$", name), name
        assert (facts["trace_root"] / name).is_file(), name
    required(facts["archive"])
    return len(names)


def validate_allocation(roi, facts):
    required(facts["sidecar"])
    required(facts["object_map"])
    assert digest(facts["sidecar"]) == facts["sidecar_sha"]
    assert digest(facts["object_map"]) == facts["object_map_sha"]
    sidecar = json.loads(facts["sidecar"].read_text())
    weights = [x for x in sidecar["allocations"] if x.get("object_kind") == "WEIGHT"]
    assert len(weights) == 1
    entry = weights[0]
    assert entry["allocation_id"] == "weight-flat-rank0"
    assert entry["classification_provenance"] == "m4a runtime flat-buffer binder"
    assert int(entry["simva_start"], 0) == facts["va"]
    assert entry["size_bytes"] == SIZE
    assert entry["lifetime"] == {"start_phase": "MODEL_LOAD", "end_phase": "DECODE"}
    assert facts["va"] % PAGE == 0 and SIZE % PAGE == 4096
    return SIZE // PAGE


def parse_registration(path):
    lines = pathlib.Path(path).read_text().splitlines()
    assert lines[0] == "M4B_WEIGHT_SEGMENT_REGISTRATION_V2"
    fields = {}
    descriptors = []
    for line in lines[1:]:
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if parts[0] == "descriptor":
            assert len(parts) == 8
            descriptors.append(tuple(int(value, 0) for value in parts[1:]))
        else:
            assert len(parts) == 2 and parts[0] not in fields
            fields[parts[0]] = parts[1]
    assert set(fields) == {"roi", "source_sha256", "archive_sha256",
                           "object_map_sha256", "provisioned_asid", "epoch"}
    return fields, descriptors


def validate_registration(roi, facts):
    registration = registration_path(roi)
    text = registration.read_text()
    assert ("# c11_runtime_allocation_sidecar_sha256 " +
            facts["sidecar_sha"]) in text
    assert "# c11_modeled_pa_policy C5_MODELED_PA_HIGH_UNUSED_BIT_V1" in text
    assert "# c11_full_page_admission 15442 pages; trailing 4096 bytes conventional" in text
    fields, desc = parse_registration(registration)
    assert fields["roi"] == roi and fields["source_sha256"] == facts["source_sha"]
    assert fields["archive_sha256"] == facts["archive_sha"]
    assert fields["object_map_sha256"] == facts["object_map_sha"]
    assert fields["provisioned_asid"] == "0" and fields["epoch"] == "1"
    assert 1 <= len(desc) <= 8
    admitted = SIZE // PAGE
    expected_vpn = facts["va"] // PAGE
    expected_ppn = (facts["va"] + PA_OFFSET) // PAGE
    prior_end = -1
    total = 0
    for asid, epoch, begin, end, ppn, ro, mapping_class in desc:
        assert (asid, epoch, ro, mapping_class) == (0, 1, 1, 0)
        assert begin > prior_end and end >= begin
        assert ppn != begin and ppn + end - begin < (1 << 33)
        prior_end = end
        total += end - begin + 1
    assert len(desc) == 1 and total == admitted
    assert desc[0][2:5] == (expected_vpn, expected_vpn + admitted - 1,
                             expected_ppn)


def validate_pa_policy(roi, facts):
    va = facts["va"]
    full_bytes = (SIZE // PAGE) * PAGE
    pa = va + PA_OFFSET
    assert va < (1 << 47) and pa < (1 << 49)
    assert pa + full_bytes <= (1 << 49)
    assert (pa >> 48) == 1 and (va >> 48) == 0
    # n_mem=12 and n_subpart=2 create the C5 gap path.  The selected offset
    # is 12*2^44: it preserves channel modulo, turns into +2^36 in the
    # IPOLY input (outside its consumed bits 0..14), and into +2^44 in the
    # L2 partition address (outside L2 IPOLY-64 consumed bits 0..18).
    assert PA_OFFSET == 12 * (1 << 44)
    base_text = BASE.read_text()
    shell_text = SHELL.read_text()
    assert "-gpgpu_memory_partition_indexing 2" in base_text
    assert "-gpgpu_n_mem 12" in shell_text
    assert "-gpgpu_n_sub_partition_per_mchannel 2" in shell_text
    assert "-gpgpu_cache:dl1 S:4:128:256,L:T:m:L:L," in shell_text
    assert "-gpgpu_cache:dl2 S:64:128:16,L:B:m:L:P," in shell_text
    mapping_match = re.search(r"-gpgpu_mem_addr_mapping dramid@8;([^\n]+)",
                              base_text)
    assert mapping_match
    mapping = "".join(c for c in mapping_match.group(1) if c != ".")
    assert len(mapping) == 64
    assigned_bits = [63 - index for index, char in enumerate(mapping)
                     if char.upper() in ("B", "R", "C", "S")]
    assert assigned_bits and max(assigned_bits) < 44
    for page in range(SIZE // PAGE):
        address = va + page * PAGE
        assert ((address >> 8) % 12) == (((address + PA_OFFSET) >> 8) % 12)
        before = (address >> 8) // 12
        after = ((address + PA_OFFSET) >> 8) // 12
        assert after - before == (1 << 36)
        for index in range(32):
            assert ipoly32(before, index) == ipoly32(after, index)
        before_part = (before << 8) | (address & 0xff)
        after_part = (after << 8) | ((address + PA_OFFSET) & 0xff)
        assert after_part - before_part == (1 << 44)
        # L2's 64-set IPOLY receives partition_address >> 13.  Its source
        # reads bits 0..18 only; the difference is bit 31.  L1 is linear and
        # likewise uses only low set-index bits.
        assert ((after_part >> 13) - (before_part >> 13)) == (1 << 31)
        assert ((after_part >> 13) & ((1 << 19) - 1)) == \
               ((before_part >> 13) & ((1 << 19) - 1))
    return pa


def validate_configs():
    manifest = CONFIG_DIR / "C11_C5_CONFIG_MANIFEST.tsv"
    required(manifest)
    rows = manifest.read_text().splitlines()
    assert len(rows) == 1 + len(EXPECTED) * len(ARMS)
    for line in rows[1:]:
        roi, arm, lseg, rel, sha, reg_rel, reg_sha, bits, geometry = line.split("\t")
        path = ROOT / rel
        assert digest(path) == sha and digest(ROOT / reg_rel) == reg_sha
        body = path.read_text()
        assert "-gpgpu_vm_fair_arm " in body
        assert "-gpgpu_vm_weight_segment_map " + str(ROOT / reg_rel) in body
        assert "-gpgpu_vm_application_physical_limit 562949953421312" in body
        assert arm in ("F0", "F1", "F2", "F5", "F7", "F8", "F9")
        assert int(bits) > 0 and geometry


def arm_label(arm):
    labels = ["PRIMARY_EQUAL_COST"]
    if arm in ("F1", "F8"):
        labels.append("REFERENCE_APPROX_SUBENTRY_16")
    if arm in ("F7", "F8"):
        labels.append("SPECULATIVE_CANDIDATE")
    return ";".join(labels)


def emit_review_tables(binary_sha, core_sha, binary_path, runtime_path):
    """Materialize only mechanical C5 tables after a validated full link."""
    manifest = CONFIG_DIR / "C11_C5_CONFIG_MANIFEST.tsv"
    required(manifest)
    binary = pathlib.Path(binary_path)
    runtime = pathlib.Path(runtime_path)
    required(binary)
    required(runtime)
    assert digest(binary) == binary_sha
    rows = manifest.read_text().splitlines()[1:]
    matrix = [
        "roi\tarm\tlseg\tclassification\tconfig_path\tconfig_sha256\t"
        "trace_list_sha256\tregistration_sha256\tcharged_bits\trealized_geometry\t"
        "framework_head\tcore_head\tbinary_sha256\n"
    ]
    commands = [
        "roi\tarm\tlseg\tconfig_path\tconfig_sha256\ttrace_list\ttrace_sha256\t"
        "trace_root\tregistration_path\tregistration_sha256\tbinary\tbinary_sha256\t"
        "runtime_libcudart\toutput_dir\tresume_policy\texact_command\n"
    ]
    # The executable C11 input/configuration anchor.  A later review-only
    # evidence commit does not change simulator code or any C5 input hash.
    framework_sha = "d64408a97d76a320a6d49468653d416e33677af8"
    for line in rows:
        roi, arm, lseg, rel, cfg_sha, reg_rel, reg_sha, bits, geometry = line.split("\t")
        facts = EXPECTED[roi]
        run_id = arm.lower() if lseg == "NONE" else "%s_lseg%s" % (arm.lower(), lseg)
        out = pathlib.Path("/workspace/vm-m4b-speculative/c5-results/") / \
            "C11_AUTHORIZED_NOT_RUN" / roi / run_id
        matrix.append("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" %
                      (roi, arm, lseg, arm_label(arm), rel, cfg_sha,
                       facts["list_sha"], reg_sha, bits, geometry, framework_sha,
                       core_sha, binary_sha))
        # The command deliberately starts with an authorization comment in the
        # table consumer, but contains no data-dependent or TODO argument.
        command = (
            "test ! -e '{out}' && mkdir -p '{out}/traces' && "
            "cp --reflink=auto '{trace_list}' '{out}/traces/kernelslist.g' && "
            "sha256sum '{out}/traces/kernelslist.g' | grep -q '^{trace_sha}  ' && "
            "while IFS= read -r f; do ln -s '{trace_root}/'\"$f\" "
            "'{out}/traces/'\"$f\"; done < '{out}/traces/kernelslist.g' && "
            "( cd '{out}' && GPGPUSIM_ROOT='{core}' LD_LIBRARY_PATH='{runtime_dir}' "
            "/usr/bin/time -v '{binary}' -config '{config}' -trace "
            "'{out}/traces/kernelslist.g' ) 2>&1 | tee '{out}/run.log'"
        ).format(out=out, trace_list=facts["list"], trace_sha=facts["list_sha"],
                 trace_root=facts["trace_root"], core=CORE,
                 runtime_dir=runtime.parent, binary=binary, config=ROOT / rel)
        commands.append("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" %
                        (roi, arm, lseg, rel, cfg_sha, facts["list"],
                         facts["list_sha"], facts["trace_root"], reg_rel,
                         reg_sha, binary, binary_sha, runtime, out,
                         "NO_RESUME; fresh directory only; restart requires all hash equality",
                         command))
    write_if_changed(PACK / "C5_ARM_MATRIX.tsv", "".join(matrix))
    write_if_changed(PACK / "C5_COMMAND_MANIFEST.tsv", "".join(commands))


def validate():
    for roi in sorted(EXPECTED):
        facts = EXPECTED[roi]
        count = validate_trace(roi, facts)
        pages = validate_allocation(roi, facts)
        validate_registration(roi, facts)
        pa = validate_pa_policy(roi, facts)
        print("%s\ttrace_kernels=%u\tfull_pages=%u\tmodeled_pa_start=0x%x" %
              (roi, count, pages, pa))
    validate_configs()
    source = (CORE / "src/gpgpu-sim/vm_translation.cc").read_text()
    assert "if (!m_weight_segments.registered_ppn(key, &ppn))" in source
    assert "config->segment = segment_config(false, 0, 0, config->segment.map_path);" in source
    print("C11_C5_INPUT_VALIDATOR PASS")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--generate", action="store_true")
    parser.add_argument("--validate", action="store_true")
    parser.add_argument("--emit-review-tables", action="store_true")
    parser.add_argument("--binary-sha256")
    parser.add_argument("--core-sha")
    parser.add_argument("--binary-path")
    parser.add_argument("--runtime-libcudart")
    args = parser.parse_args()
    if not args.generate and not args.validate and not args.emit_review_tables:
        parser.error("select --generate, --validate and/or --emit-review-tables")
    if args.generate:
        generate()
    if args.validate:
        validate()
    if args.emit_review_tables:
        if not all((args.binary_sha256, args.core_sha, args.binary_path,
                    args.runtime_libcudart)):
            parser.error("--emit-review-tables requires binary/core identities and paths")
        emit_review_tables(args.binary_sha256, args.core_sha, args.binary_path,
                           args.runtime_libcudart)


if __name__ == "__main__":
    main()
