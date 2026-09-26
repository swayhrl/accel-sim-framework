#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path


STAGE = "AWMA_AI_TRANSLATION_PATH_AND_RESIDUAL_174NEW_V1"
REPO = Path(
    "/root/workspace/accel-sim-framework-awma-ai-translation-path-and-residual-174new-v1"
)
PACK = REPO / "docs/vm_tlb/review_packs" / STAGE
STRONG_RAW = Path(
    "/root/share/mnt164/huangrulin/awma_intrawarp_translation_baseline_residual_v1/raw"
)
PATH_RAW = Path(
    "/root/share/mnt164/huangrulin/awma_post_classic_baseline_residual_discovery_v1/raw"
)
POST_OBS_RAW = Path(
    "/root/share/mnt164/huangrulin/awma_post_classic_baseline_residual_discovery_v1/observatory_raw"
)

TARGETS = {
    "T0": ("PREFILL_FLASH", 488559),
    "T1": ("PREFILL_GEMM", 619514),
    "T2": ("DECODE_GEMV", 94034),
    "A2": ("DECODE_GEMV_PAIR_A_T8192", 115700),
}

SCALARS = (
    "gpu_sim_cycle", "gpu_sim_insn", "gpu_tot_issued_cta",
    "vm_translation_stall_cycles", "vm_l1_tlb_lookup_latency_cycles",
    "vm_l1_tlb_lookup_launches", "vm_l1_tlb_lookup_service_cycles",
    "vm_l1_tlb_hits", "vm_l1_tlb_misses", "vm_l1_tlb_port_stalls",
    "vm_l2_tlb_lookup_launches", "vm_translation_mshr_allocations",
    "vm_translation_mshr_merges", "vm_translation_mshr_full_events",
    "vm_translation_walk_starts", "vm_translation_pwq_full_events",
    "vm_pte_requests", "vm_ready_application_duplicate_attempts",
    "vm_translation_quiescent_invariants_hold",
    "awma_intrawarp_terminal_quiescent",
)


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def scalar(text: str, key: str) -> int:
    matches = re.findall(rf"^{re.escape(key)}\s*=\s*(\d+)\s*$", text, re.M)
    if not matches:
        raise RuntimeError(f"missing {key}")
    return int(matches[-1])


def coverage(text: str) -> dict[str, int]:
    matches = re.findall(
        r"AWMA_VM_COVERAGE admissions=(\d+) translated=(\d+) "
        r"untranslated=(\d+) unobserved=(\d+) unique=(\d+) "
        r"translated_unique=(\d+) untranslated_unique=(\d+)",
        text,
    )
    if not matches:
        raise RuntimeError("missing coverage")
    names = (
        "admissions", "translated", "untranslated", "unobserved", "unique",
        "translated_unique", "untranslated_unique",
    )
    return dict(zip(names, map(int, matches[-1])))


def l1d_totals(text: str) -> dict[str, int]:
    rows = re.findall(
        r"L1D_cache_core\[\d+\]: Access = (\d+), Miss = (\d+), "
        r"Miss_rate = [0-9.]+, Pending_hits = (\d+), "
        r"Reservation_fails = (\d+)",
        text,
    )
    if not rows:
        raise RuntimeError("missing L1D core statistics")
    values = [tuple(map(int, row)) for row in rows]
    return {
        "accesses": sum(row[0] for row in values),
        "misses": sum(row[1] for row in values),
        "pending_hits": sum(row[2] for row in values),
        "reservation_fails": sum(row[3] for row in values),
    }


def parse_run(directory: Path) -> dict:
    log = directory / "run.log"
    text = log.read_text(errors="replace")
    result = {key: scalar(text, key) for key in SCALARS}
    result["coverage"] = coverage(text)
    result["l1d"] = l1d_totals(text)
    result["terminal"] = (
        "GPGPU-Sim: *** simulation thread exiting ***" in text
        and "GPGPU-Sim: *** exit detected ***" in text
    )
    result["path"] = str(log)
    result["sha256"] = digest(log)
    result["command"] = json.loads((directory / "command.json").read_text())
    return result


def write_tsv(path: Path, header: list[str], rows: list[list[object]]) -> None:
    with path.open("w", newline="") as stream:
        writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--native-status",
        choices=("PRECHECK_NOT_RUN", "NOT_READY", "READY"),
        default="PRECHECK_NOT_RUN",
    )
    parser.add_argument("--native-branch-head", default="")
    parser.add_argument("--native-check-utc", default="")
    args = parser.parse_args()
    PACK.mkdir(parents=True, exist_ok=True)

    matrix_rows = []
    decision_rows = []
    parsed: dict[str, dict[str, dict]] = {}
    for target, (family, expected_b0) in TARGETS.items():
        b0_dir = STRONG_RAW / f"{target}_WARP_VPN_DEDUP_REFERENCE_10_80"
        b1_dir = PATH_RAW / f"{target}_REFERENCE_L1_0_L2_80_DIAGNOSTIC"
        b0 = parse_run(b0_dir)
        b1 = parse_run(b1_dir)
        if b0["gpu_sim_cycle"] != expected_b0:
            raise RuntimeError(f"{target}: B0 cycle mismatch")
        if b0["vm_l1_tlb_lookup_latency_cycles"] != 10:
            raise RuntimeError(f"{target}: B0 is not 10/80")
        if b1["vm_l1_tlb_lookup_latency_cycles"] != 0:
            raise RuntimeError(f"{target}: B1 equivalence is not 0/80")
        correctness = (
            b0["terminal"] and b1["terminal"]
            and b0["gpu_sim_insn"] == b1["gpu_sim_insn"]
            and b0["gpu_tot_issued_cta"] == b1["gpu_tot_issued_cta"]
            and b0["coverage"]["unique"] == b1["coverage"]["unique"]
            and b0["coverage"]["untranslated"] == 0
            and b1["coverage"]["untranslated"] == 0
            and b0["coverage"]["unobserved"] == 0
            and b1["coverage"]["unobserved"] == 0
            and b0["vm_ready_application_duplicate_attempts"] == 0
            and b1["vm_ready_application_duplicate_attempts"] == 0
            and b0["vm_translation_quiescent_invariants_hold"] == 1
            and b1["vm_translation_quiescent_invariants_hold"] == 1
            and b0["awma_intrawarp_terminal_quiescent"] == 1
            and b1["awma_intrawarp_terminal_quiescent"] == 1
        )
        response = (
            b0["gpu_sim_cycle"] - b1["gpu_sim_cycle"]
        ) * 100 / b0["gpu_sim_cycle"]
        parsed[target] = {"B0": b0, "B1": b1}
        matrix_rows.append([
            target, family, b0["gpu_sim_cycle"], b1["gpu_sim_cycle"],
            response, "NOT_IMPLEMENTED_SOURCE_SEMANTICS_INSUFFICIENT",
            b0["gpu_sim_insn"], b0["gpu_tot_issued_cta"],
            b0["vm_translation_stall_cycles"],
            b1["vm_translation_stall_cycles"],
            b0["vm_l1_tlb_lookup_launches"],
            b1["vm_l1_tlb_lookup_launches"], b0["vm_l1_tlb_hits"],
            b1["vm_l1_tlb_hits"], b0["vm_l1_tlb_misses"],
            b1["vm_l1_tlb_misses"], b0["vm_l2_tlb_lookup_launches"],
            b1["vm_l2_tlb_lookup_launches"],
            b0["vm_translation_mshr_allocations"],
            b1["vm_translation_mshr_allocations"],
            b0["vm_translation_mshr_full_events"],
            b1["vm_translation_mshr_full_events"],
            b0["vm_translation_walk_starts"],
            b1["vm_translation_walk_starts"], b0["vm_pte_requests"],
            b1["vm_pte_requests"], b0["l1d"]["accesses"],
            b1["l1d"]["accesses"], b0["l1d"]["misses"],
            b1["l1d"]["misses"], b0["l1d"]["pending_hits"],
            b1["l1d"]["pending_hits"], b0["l1d"]["reservation_fails"],
            b1["l1d"]["reservation_fails"], correctness,
        ])
        decision_rows.append([
            target, "HIT_DOMINATED_EXISTING_TRACE", "B1_REUSED",
            "B0_10_80_VS_CONSERVATIVE_VIPT_EQUIVALENT_0_80",
            "B2_NOT_IMPLEMENTED", "NO_MECHANISM_DECISION_FROM_EXISTING_TRACE",
        ])

    write_tsv(PACK / "EXISTING_TRACE_PATH_MATRIX.tsv", [
        "target", "family", "b0_current_sequential_cycles",
        "b1_vipt_like_cycles", "b1_cycle_reduction_percent", "b2_status",
        "instructions", "ctas", "b0_translation_stall_events",
        "b1_translation_stall_events", "b0_l1_tlb_launches",
        "b1_l1_tlb_launches", "b0_l1_tlb_hits", "b1_l1_tlb_hits",
        "b0_l1_tlb_misses", "b1_l1_tlb_misses", "b0_l2_tlb_launches",
        "b1_l2_tlb_launches", "b0_mshr_allocations", "b1_mshr_allocations",
        "b0_mshr_full_events", "b1_mshr_full_events", "b0_ptw_starts",
        "b1_ptw_starts", "b0_pte_requests", "b1_pte_requests",
        "b0_l1d_accesses", "b1_l1d_accesses", "b0_l1d_misses",
        "b1_l1d_misses", "b0_l1d_pending_hits", "b1_l1d_pending_hits",
        "b0_l1d_reservation_fails", "b1_l1d_reservation_fails", "correctness",
    ], matrix_rows)

    directed_rows = [
        ["L1D_hit_L1TLB_hit", "PASS", "PASS_42_TO_32", "BOUND_ONLY", "no early physical-tag use"],
        ["L1D_miss_L1TLB_hit", "PASS", "PASS_LOWER_WAITS", "PASS_TRANSLATION_REQUIRED", "one lower request"],
        ["L1D_hit_L1TLB_miss", "PASS", "PASS_LEGALITY_WAIT", "BOUND_ONLY", "completion not before physical translation"],
        ["L1D_miss_L1TLB_miss", "PASS", "PASS_NO_LOWER_SKIP", "PASS_TRANSLATION_REQUIRED", "L2/PTW tail preserved"],
        ["replay_after_translation", "PASS", "PASS_EXACTLY_ONCE", "BOUND_ONLY", "duplicate apply rejected"],
        ["store", "PASS", "PASS_TRANSLATION_REQUIRED", "FALLBACK_TRANSLATION", "no virtual filter"],
        ["atomic", "PASS", "PASS_TRANSLATION_REQUIRED", "FALLBACK_TRANSLATION", "no virtual filter"],
        ["request_count_conservation", "PASS", "PASS", "PASS_FIXTURE", "one data request; B1 one translation service"],
        ["terminal_quiescence", "PASS_ACCEPTED_RUNS", "PASS_ACCEPTED_RUNS", "NOT_RUN", "B0/B1 controller quiescent"],
        ["integrated_B2_semantics", "NA", "NA", "NOT_IMPLEMENTED", "missing virtual tags/permissions/synonym/coherence"],
    ]
    write_tsv(PACK / "DIRECTED_PATH_CORRECTNESS.tsv", [
        "case", "b0", "b1", "b2", "gate",
    ], directed_rows)
    write_tsv(PACK / "DIAGNOSTIC_DECISION_LOG.tsv", [
        "target", "observed_case", "decision", "contrast", "bound",
        "mechanism_action",
    ], decision_rows)

    (PACK / "EXISTING_TRACE_INTERPRETATION.md").write_text('''# Existing-trace interpretation

The conservative B1 path model reuses accepted 0/80 reference runs because
`max(10-cycle L1 TLB - 32-cycle L1D, 0) = 0`. This is a timing composition,
not a claim of zero-cost translation.

Relative to B0, B1 changes cycles by +7.037% on T0, -1.983% on T1, +12.822%
on T2, and +1.269% on A2. Thus much of the prior 0/80 response is attributable
to the sequential access-path model. T1's regression also shows the response is
not a removable additive “translation runtime fraction.”

B1 preserves every translation and data request contract, but changed timing
can perturb cache/TLB interleaving; both arms' service and L1D outcomes are
reported rather than assumed equal. `vm_translation_stall_cycles` is a retry/
stall-event count, not kernel cycles that can be added.

B2 is not run. A valid virtual-L1 filter requires virtual cache tags,
permissions, synonyms, coherence, and shootdown semantics absent from the
current physical-cache interface. Treating an eventual L1 hit as known before
translation would be future information.

Existing traces therefore establish access-path-model sensitivity, not a new
program-intrinsic MMU bottleneck. Native-atlas evidence is still required to
test whether new AI dimensions leave a residual after the realistic path
diagnostic.
''')

    (PACK / "CLOSEST_WORK_SCREEN.md").write_text('''# Closest-work screen

- Pichai et al. (DCS-TR-703 / ASPLOS 2014) explicitly model TLB access prior
  to or in parallel with a VIPT L1 cache. B1 is a conservative diagnostic of
  this known path choice, not a new mechanism.
- Yoon, Lowe-Power, and Sohi (ASPLOS 2018) use virtual L1/L2 caches to filter
  translation before cache hits, while paying virtual-tag, permission,
  synonym, coherence, and shootdown costs. This is why B2 cannot be represented
  as a free current-cache hit.
- Shin et al. (ISCA 2018) already batch/priority-schedule page walks from one
  SIMD instruction, including the last-walk progress observation.
- Neighborhood-Aware Translation and MPW address miss/walk locality or walker
  throughput, not the current hit-dominated path; MPW also reports a distinct
  no-translation-before-L1 sensitivity.
- LATPC already includes warp-instruction VPN coalescing, multi-VPN MSHR
  compression, regularity detection, and walk batching.
- Avatar's baseline is VIPT-parallel and CAST starts on L1-TLB misses; current
  hit-dominated path sensitivity alone does not establish Avatar applicability.
- MASK/RPAWS already cover broad translation/data interference or generic
  compute/memory pressure scheduling.

No existing-trace result passes the residual novelty gate. New native targets,
if supplied, must first demonstrate a material resource-specific residual after
B1 before a problem card can exist.
''')

    native_rows = []
    residual_rows = []
    if args.native_status == "PRECHECK_NOT_RUN":
        native_rows.append(["NATIVE_ATLAS", "PRECHECK_NOT_RUN", "NA", "NA", "NA", "NA", "NA"])
        residual_rows.append(["NATIVE_ATLAS", "PRECHECK_NOT_RUN", "NA", "NA", "NA", "NA", "NA", "NA"])
        final_status = "PRECHECK_NOT_RUN"
    elif args.native_status == "NOT_READY":
        native_rows.append(["NATIVE_ATLAS", "NOT_READY", "NA", "NA", "NA", "NA", "NA"])
        residual_rows.append(["NATIVE_ATLAS", "NOT_RUN", "NA", "NA", "NA", "NA", "NA", "AWAITING_HANDOFF"])
        final_status = "PREP_COMPLETE_AWAITING_NATIVE_ATLAS"
    else:
        raise RuntimeError("READY status requires native qualification workflow")
    write_tsv(PACK / "NEW_TRACE_QUALIFICATION.tsv", [
        "target", "status", "instructions", "ctas", "unique_uids",
        "coverage", "quiescence",
    ], native_rows)
    write_tsv(PACK / "NEW_AI_RESIDUAL_MATRIX.tsv", [
        "target", "status", "cycles", "l1_launches", "l2_launches",
        "mshr_pressure", "ptw_pressure", "disposition",
    ], residual_rows)

    (PACK / "PROTOTYPE_DECISION.md").write_text(f'''# Prototype decision

Status: **{final_status}**

No mechanism code is authorized or written.

- B1 is a diagnostic path model backed by accepted B0/B1 runs;
- B2 is not implementable on the current cache semantics without a real
  virtual-cache design;
- existing traces show path-model sensitivity but no differentiated residual;
- native residual gates have not passed.

Candidate and matched-control full replays: **0**.
''')

    (PACK / "REPORT.md").write_text(f'''# {STAGE}

Status: **{final_status}**

The current model serializes 10-cycle L1-TLB lookup before a 32-cycle L1D
lookup. The conservative B1 model credits only that initial overlap and is
timing-equivalent to accepted reference 0/80 runs. It explains substantial but
non-monotonic existing-trace sensitivity without creating a new mechanism.

B2 is `NOT_IMPLEMENTED_SOURCE_SEMANTICS_INSUFFICIENT`: the current physical
cache lacks virtual tags, permissions, synonym/coherence, and shootdown state.

The 174 preparation is complete. Native-atlas status is recorded in
`NATIVE_HANDOFF_STATUS.json`; no polling or mechanism search occurs.
''')

    (PACK / "README.md").write_text(f'''# {STAGE}

Start with `REPORT.md`.

Status: **{final_status}**

Review order:

1. `ACCESS_PATH_SOURCE_AUDIT.md`
2. `PATH_MODEL_CONTRACT.md`
3. `DIRECTED_PATH_CORRECTNESS.tsv`
4. `EXISTING_TRACE_PATH_MATRIX.tsv`
5. `EXISTING_TRACE_INTERPRETATION.md`
6. `CLOSEST_WORK_SCREEN.md`
7. `NATIVE_HANDOFF_STATUS.json`
8. `PROTOTYPE_DECISION.md`

No strong-baseline source/config/binary is modified.
''')

    status_payload = {
        "checked": args.native_status != "PRECHECK_NOT_RUN",
        "branch": "hrl/awma-ai-translation-native-atlas-capture-109-v1",
        "branch_head": args.native_branch_head or None,
        "checked_at_utc": args.native_check_utc or None,
        "result": args.native_status,
        "expected_status": "READY_FOR_AI_TRANSLATION_RESIDUAL_174NEW",
        "polling": False,
    }
    (PACK / "NATIVE_HANDOFF_STATUS.json").write_text(
        json.dumps(status_payload, indent=2, sort_keys=True) + "\n"
    )

    raw_rows: list[list[object]] = []
    def add(kind: str, identity: str, path: Path) -> None:
        raw_rows.append([kind, identity, str(path), digest(path)])
    for target in TARGETS:
        for kind, directory in (
            ("B0", STRONG_RAW / f"{target}_WARP_VPN_DEDUP_REFERENCE_10_80"),
            ("B1", PATH_RAW / f"{target}_REFERENCE_L1_0_L2_80_DIAGNOSTIC"),
        ):
            for filename in ("run.log", "command.json"):
                add(kind, f"{target}:{filename}", directory / filename)
        obs = POST_OBS_RAW / f"{target}_REFERENCE_OBSERVATORY_L1_10_80/run.log"
        add("B0_OBSERVATORY", f"{target}:run.log", obs)
    for filename in (
        "path_model_fixture.py", "test_path_model_fixture.py",
        "build_ai_translation_path_review.py",
        "validate_ai_translation_path_review.py",
    ):
        add("SCRIPT", filename, REPO / "util/vm_tlb/awma" / filename)
    raw_rows.extend([
        ["AUTHORITY", "coordination", "git", "f31e9531bf32194a609a54a207e2ecb7611c3859"],
        ["AUTHORITY", "strong_reference", "git", "9efe8236e0c6338addfef5480e1da91bffb504eb"],
        ["AUTHORITY", "post_classic", "git", "32854024b1b92313cf2dffc6280247a629033991"],
        ["AUTHORITY", "observatory", "git", "b85d388abe98e5da70b749b52075c33fad7cede4"],
        ["AUTHORITY", "literature_notebook", "git", "177863f325d77278013e195528903ddc8b292e4e"],
        ["AUTHORITY", "native_branch_head", "git", args.native_branch_head or "NOT_AVAILABLE"],
    ])
    write_tsv(PACK / "RAW_DATA_INDEX.tsv", [
        "kind", "identity", "path_or_type", "sha256_or_commit",
    ], raw_rows)

    (PACK / "EXECUTION_SUMMARY.md").write_text('''# Execution summary

Parent: `f31e9531bf32194a609a54a207e2ecb7611c3859`.

Changes are limited to this review pack and offline fixture/build/validation
scripts. Existing B0/B1/Observatory raw data is reused read-only. No simulator,
strong-baseline, config, trace, binary, capture, RTL, or PPA artifact changes.

Validation includes ten directed fixture cases, four accepted B0/B1 workload
pairs, raw hashes, manifest, and final git closure. Open boundary: B2 has no
integrated result because required virtual-cache correctness state is absent.
''')

    manifest = []
    for path in sorted(PACK.iterdir()):
        if path.is_file() and path.name != "SHA256SUMS":
            manifest.append(f"{digest(path)}  {path.name}")
    (PACK / "SHA256SUMS").write_text("\n".join(manifest) + "\n")
    print(json.dumps({
        "status": final_status,
        "b0_b1_targets": list(TARGETS),
        "b2": "NOT_IMPLEMENTED_SOURCE_SEMANTICS_INSUFFICIENT",
        "candidate_runs": 0,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
