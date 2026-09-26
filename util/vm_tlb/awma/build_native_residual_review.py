#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path


STAGE = "AWMA_AI_TRANSLATION_NATIVE_RESIDUAL_174NEW_V1"
STATUS = "NO_NEW_AI_TRANSLATION_PROBLEM_IDENTIFIED_V1"
REPO = Path(
    "/root/workspace/accel-sim-framework-awma-ai-translation-native-residual-174new-v1"
)
PACK = REPO / "docs/vm_tlb/review_packs" / STAGE
RAW = Path(
    "/root/share/mnt164/huangrulin/awma_ai_translation_native_residual_174new_v1/raw"
)
DERIVED = Path(
    "/root/share/mnt164/huangrulin/awma_ai_translation_native_residual_174new_v1/"
    "L2_GRAMMAR_REPAIRED_DETERMINISTIC"
)
GRAMMAR = Path(
    "/root/share/mnt164/huangrulin/awma_ai_translation_native_residual_174new_v1/"
    "l2_grammar_audit"
)

TARGETS = {
    "L1": {
        "role": "LLAMA_GEMV_SCALE8",
        "b0": "L1_WARP_REFERENCE_10_80",
        "b1": "L1_VIPT_LIKE_B1_0_80",
        "expected_ctas": 2048,
        "function_sha": "e52f28ddc664202dcf583dfef5266a7d06e21d90dcaf3c98eb3b6c993036ea9d",
        "trace_sha": "28ace77d25a0f14ef1f5f3cd04f8334e64ac1b476ecb60c2e52abdb1d6ea3e7e",
        "native_memory_instructions": 1052672,
        "native_active_refs": 33562624,
        "native_unique_4k": 8198,
        "native_one_page": 528384,
        "native_two_page": 524288,
    },
    "M1": {
        "role": "OLMOE_GEMV_SCALE1",
        "b0": "M1_WARP_REFERENCE_10_80",
        "b1": "M1_VIPT_LIKE_B1_0_80",
        "expected_ctas": 256,
        "function_sha": "e52f28ddc664202dcf583dfef5266a7d06e21d90dcaf3c98eb3b6c993036ea9d",
        "trace_sha": "38d08b64ced6a92ac773b6bc926471482162fea80dcec6aad897a84114387fd5",
        "native_memory_instructions": 131584,
        "native_active_refs": 4195328,
        "native_unique_4k": 1026,
        "native_one_page": 66048,
        "native_two_page": 65536,
    },
    "M2": {
        "role": "LOW_TRANSLATION_DEMAND_CONTROL",
        "b0": "M2_WARP_REFERENCE_10_80",
        "b1": None,
        "expected_ctas": 1,
        "function_sha": "6ad9926a5d68a14461329c938238552973df147d6fffb04afeafd4270ad83427",
        "trace_sha": "77740c7dd8b1dcf401128b2edb530d50f6421b4cbc5758d1bf2b5ca5e6453334",
        "native_memory_instructions": 2,
        "native_active_refs": 9,
        "native_unique_4k": 2,
        "native_one_page": 2,
        "native_two_page": 0,
    },
    "L2": {
        "role": "LLAMA_ATTENTION_LIKE_DERIVED_GRAMMAR",
        "b0": "L2_WARP_REFERENCE_10_80",
        "b1": "L2_VIPT_LIKE_B1_0_80",
        "expected_ctas": 64,
        "function_sha": "f161786ce964fe9303a4c7f1d0fdc76f21713ac6db25151f371fca82d3622f10",
        "trace_sha": "db391d6731d0568a0abf0283546c564d793adc0fbeecab7010831eb8329297e6",
        "native_memory_instructions": 8640,
        "native_active_refs": 266304,
        "native_unique_4k": 538,
        "native_one_page": 8256,
        "native_two_page": 384,
    },
}

SCALARS = (
    "gpu_sim_cycle", "gpu_sim_insn", "gpu_tot_issued_cta",
    "vm_translation_stall_cycles", "vm_l1_tlb_lookup_latency_cycles",
    "vm_l1_tlb_lookup_launches", "vm_l1_tlb_hits", "vm_l1_tlb_misses",
    "vm_l1_tlb_port_stalls", "vm_l2_tlb_lookup_launches",
    "vm_translation_mshr_allocations", "vm_translation_mshr_merges",
    "vm_translation_mshr_full_events", "vm_translation_pwq_full_events",
    "vm_translation_walk_starts", "vm_pte_requests",
    "vm_ready_application_duplicate_attempts",
    "vm_translation_quiescent_invariants_hold",
    "awma_intrawarp_terminal_quiescent", "awma_intrawarp_instruction_count",
    "awma_intrawarp_request_count", "awma_intrawarp_ref_groups",
    "awma_intrawarp_ref_followers", "awma_intrawarp_ref_head_wait_cycles",
)


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def scalar(text: str, key: str) -> int:
    values = re.findall(rf"^{re.escape(key)}\s*=\s*(\d+)\s*$", text, re.M)
    if not values:
        raise RuntimeError(f"missing {key}")
    return int(values[-1])


def coverage(text: str) -> dict[str, int]:
    values = re.findall(
        r"AWMA_VM_COVERAGE admissions=(\d+) translated=(\d+) "
        r"untranslated=(\d+) unobserved=(\d+) unique=(\d+) "
        r"translated_unique=(\d+) untranslated_unique=(\d+)", text,
    )
    names = (
        "admissions", "translated", "untranslated", "unobserved", "unique",
        "translated_unique", "untranslated_unique",
    )
    if not values:
        raise RuntimeError("missing coverage")
    return dict(zip(names, map(int, values[-1])))


def l1d(text: str) -> dict[str, int]:
    rows = re.findall(
        r"L1D_cache_core\[\d+\]: Access = (\d+), Miss = (\d+), "
        r"Miss_rate = [0-9.]+, Pending_hits = (\d+), "
        r"Reservation_fails = (\d+)", text,
    )
    if not rows:
        raise RuntimeError("missing L1D stats")
    parsed = [tuple(map(int, row)) for row in rows]
    return {
        "accesses": sum(row[0] for row in parsed),
        "misses": sum(row[1] for row in parsed),
        "pending_hits": sum(row[2] for row in parsed),
        "reservation_fails": sum(row[3] for row in parsed),
    }


def observatory(text: str, domain: str, metric: str) -> float:
    prefix = f"awma_observatory_metric\t{domain}\t{metric}\t"
    rows = [line.split("\t") for line in text.splitlines() if line.startswith(prefix)]
    if len(rows) != 1 or len(rows[0]) != 8:
        raise RuntimeError(f"missing Observatory {domain}.{metric}")
    return float(rows[0][4])


def parse(directory: Path) -> dict:
    text = (directory / "run.log").read_text(errors="replace")
    result = {key: scalar(text, key) for key in SCALARS}
    result["coverage"] = coverage(text)
    result["l1d"] = l1d(text)
    result["translation_not_ready"] = int(observatory(text, "translation", "translation_not_ready"))
    result["scheduler_dependency"] = int(observatory(text, "scheduler", "dependency_scoreboard"))
    result["scheduler_structural"] = int(observatory(text, "scheduler", "eligible_structural"))
    result["ldst_coal_stall"] = int(observatory(text, "memory", "ldst_coal_stall"))
    result["terminal"] = (
        "GPGPU-Sim: *** simulation thread exiting ***" in text
        and "GPGPU-Sim: *** exit detected ***" in text
    )
    result["path"] = str(directory / "run.log")
    result["sha256"] = digest(directory / "run.log")
    result["command"] = json.loads((directory / "command.json").read_text())
    result["grammar"] = json.loads((directory / "grammar.json").read_text())
    return result


def write_tsv(path: Path, header: list[str], rows: list[list[object]]) -> None:
    with path.open("w", newline="") as stream:
        writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)


def main() -> int:
    PACK.mkdir(parents=True, exist_ok=True)
    records: dict[str, dict[str, dict]] = {}
    qualification_rows = []
    for target, spec in TARGETS.items():
        b0 = parse(RAW / spec["b0"])
        if b0["gpu_tot_issued_cta"] != spec["expected_ctas"]:
            raise RuntimeError(f"{target}: CTA mismatch")
        if b0["command"]["trace_sha256"] != spec["trace_sha"]:
            raise RuntimeError(f"{target}: trace identity mismatch")
        if b0["command"]["function_sha256"] != spec["function_sha"]:
            raise RuntimeError(f"{target}: function identity mismatch")
        correct = (
            b0["terminal"] and b0["coverage"]["untranslated"] == 0
            and b0["coverage"]["unobserved"] == 0
            and b0["coverage"]["translated"] == b0["coverage"]["admissions"]
            and b0["coverage"]["translated_unique"] == b0["coverage"]["unique"]
            and b0["vm_ready_application_duplicate_attempts"] == 0
            and b0["vm_translation_quiescent_invariants_hold"] == 1
            and b0["awma_intrawarp_terminal_quiescent"] == 1
            and b0["grammar"]["status"] == "TRACEG_GRAMMAR_PASS"
        )
        records[target] = {"B0": b0, "correct": correct}
        authority = "L2_GRAMMAR_REPAIRED_DETERMINISTIC" if target == "L2" else "NATIVE_ATLAS_QUALIFIED"
        qualification_rows.append([
            target, authority, spec["trace_sha"], spec["function_sha"],
            b0["grammar"]["status"], b0["grammar"]["instructions"],
            b0["grammar"]["thread_blocks"], b0["gpu_sim_insn"],
            b0["gpu_tot_issued_cta"], b0["coverage"]["unique"],
            b0["coverage"]["admissions"], b0["coverage"]["translated"],
            b0["coverage"]["untranslated"], b0["coverage"]["unobserved"],
            b0["vm_ready_application_duplicate_attempts"], b0["terminal"],
            b0["vm_translation_quiescent_invariants_hold"],
            b0["awma_intrawarp_terminal_quiescent"], b0["gpu_sim_cycle"],
            correct,
        ])
    write_tsv(PACK / "NEW_TRACE_QUALIFICATION.tsv", [
        "target", "input_authority", "trace_sha256", "function_sha256",
        "grammar_status", "grammar_instructions", "grammar_thread_blocks",
        "sim_instructions", "sim_ctas", "unique_uids", "admissions",
        "translated", "untranslated", "unobserved", "duplicate_application",
        "terminal", "controller_quiescent", "reference_quiescent", "cycles",
        "correctness",
    ], qualification_rows)

    scale_rows = []
    for target in ("L1", "M1"):
        spec = TARGETS[target]
        b0 = records[target]["B0"]
        mem = spec["native_memory_instructions"]
        ctas = b0["gpu_tot_issued_cta"]
        scale_rows.append([
            target, ctas, 8 if target == "L1" else 1,
            b0["gpu_sim_insn"], b0["gpu_sim_insn"] / ctas,
            mem, mem / ctas, spec["native_active_refs"],
            spec["native_active_refs"] / ctas, spec["native_one_page"],
            spec["native_two_page"], spec["native_unique_4k"],
            spec["native_unique_4k"] / ctas,
            b0["awma_intrawarp_request_count"],
            b0["awma_intrawarp_request_count"] / ctas,
            b0["awma_intrawarp_request_count"] / mem,
            b0["vm_l1_tlb_lookup_launches"],
            b0["vm_l1_tlb_lookup_launches"] / ctas,
            b0["vm_l1_tlb_lookup_launches"] / mem,
            b0["vm_l1_tlb_misses"], b0["vm_l1_tlb_misses"] / ctas,
            b0["vm_l2_tlb_lookup_launches"] / ctas,
            b0["vm_translation_mshr_allocations"] / ctas,
            b0["vm_translation_walk_starts"] / ctas,
            b0["vm_pte_requests"] / ctas, b0["gpu_sim_cycle"],
        ])
    write_tsv(PACK / "L1_M1_SCALE_COMPARISON.tsv", [
        "target", "ctas", "cta_scale_vs_M1", "sim_instructions_total",
        "sim_instructions_per_cta", "memory_instructions_total",
        "memory_instructions_per_cta", "active_lane_refs_total",
        "active_lane_refs_per_cta", "native_one_page_instructions",
        "native_two_page_instructions", "native_unique_4k_pages",
        "native_unique_4k_pages_per_cta", "logical_requests_total",
        "logical_requests_per_cta", "logical_requests_per_memory_instruction",
        "l1_launches_total", "l1_launches_per_cta",
        "l1_launches_per_memory_instruction", "l1_misses_total",
        "l1_misses_per_cta", "l2_launches_per_cta", "mshr_alloc_per_cta",
        "ptw_starts_per_cta", "pte_requests_per_cta", "cycles_not_cross_model_comparable",
    ], scale_rows)

    residual_rows = []
    decision_rows = []
    classifications = {}
    for target, spec in TARGETS.items():
        b0 = records[target]["B0"]
        if spec["b1"] is None:
            b1 = None
            response = "NA"
            classification = "NO_MATERIAL_TRANSLATION_RESIDUAL"
            reason = "B0-only low-demand control: 4 L1 launches and 2 PTWs"
        else:
            b1 = parse(RAW / spec["b1"])
            records[target]["B1"] = b1
            if not (
                b1["terminal"]
                and b1["gpu_sim_insn"] == b0["gpu_sim_insn"]
                and b1["gpu_tot_issued_cta"] == b0["gpu_tot_issued_cta"]
                and b1["coverage"]["unique"] == b0["coverage"]["unique"]
                and b1["coverage"]["untranslated"] == 0
                and b1["coverage"]["unobserved"] == 0
                and b1["coverage"]["translated"] == b1["coverage"]["admissions"]
                and b1["coverage"]["translated_unique"] == b1["coverage"]["unique"]
                and b1["vm_ready_application_duplicate_attempts"] == 0
                and b1["vm_translation_quiescent_invariants_hold"] == 1
                and b1["awma_intrawarp_terminal_quiescent"] == 1
            ):
                raise RuntimeError(f"{target}: B1 correctness failed")
            response_value = (
                b0["gpu_sim_cycle"] - b1["gpu_sim_cycle"]
            ) * 100 / b0["gpu_sim_cycle"]
            response = response_value
            if response_value > 1.0:
                classification = "ACCESS_PATH_MODEL_SENSITIVE_ONLY"
                reason = "material B1 response; hit dominated; MSHR/PWQ full zero"
            else:
                classification = "NO_MATERIAL_TRANSLATION_RESIDUAL"
                reason = "B1 response not positive/material and miss-side pressure low"
        classifications[target] = classification
        residual_rows.append([
            target, spec["role"], b0["gpu_sim_cycle"],
            b1["gpu_sim_cycle"] if b1 else "NA", response,
            b0["vm_l1_tlb_lookup_launches"],
            b1["vm_l1_tlb_lookup_launches"] if b1 else "NA",
            b0["vm_l1_tlb_hits"], b0["vm_l1_tlb_misses"],
            b1["vm_l1_tlb_hits"] if b1 else "NA",
            b1["vm_l1_tlb_misses"] if b1 else "NA",
            b0["vm_l1_tlb_hits"] / b0["vm_l1_tlb_lookup_launches"],
            b0["vm_l2_tlb_lookup_launches"],
            b1["vm_l2_tlb_lookup_launches"] if b1 else "NA",
            b0["vm_translation_mshr_allocations"],
            b1["vm_translation_mshr_allocations"] if b1 else "NA",
            b0["vm_translation_mshr_merges"],
            b0["vm_translation_mshr_full_events"],
            b1["vm_translation_mshr_full_events"] if b1 else "NA",
            b0["vm_translation_pwq_full_events"],
            b0["vm_translation_walk_starts"], b0["vm_pte_requests"],
            b1["vm_translation_walk_starts"] if b1 else "NA",
            b1["vm_pte_requests"] if b1 else "NA",
            b0["l1d"]["accesses"], b0["l1d"]["misses"],
            b0["l1d"]["reservation_fails"],
            b1["l1d"]["accesses"] if b1 else "NA",
            b1["l1d"]["misses"] if b1 else "NA",
            b1["l1d"]["reservation_fails"] if b1 else "NA",
            b0["translation_not_ready"],
            b1["translation_not_ready"] if b1 else "NA",
            classification, records[target]["correct"],
        ])
        decision_rows.append([
            target,
            "CASE_H" if spec["b1"] else "LOW_DEMAND_CONTROL",
            "B1_0_80" if spec["b1"] else "NO_EXTRA_DIAGNOSTIC",
            response, classification, reason, "NO_PROTOTYPE",
        ])
    write_tsv(PACK / "NEW_AI_RESIDUAL_MATRIX.tsv", [
        "target", "role", "b0_cycles", "b1_cycles",
        "b1_cycle_reduction_percent", "b0_l1_launches", "b1_l1_launches",
        "b0_l1_hits", "b0_l1_misses", "b1_l1_hits",
        "b1_l1_misses", "b0_l1_hit_fraction", "b0_l2_launches",
        "b1_l2_launches", "b0_mshr_allocations", "b1_mshr_allocations",
        "b0_mshr_merges", "b0_mshr_full", "b1_mshr_full", "b0_pwq_full",
        "b0_ptw_starts", "b0_pte_requests", "b1_ptw_starts",
        "b1_pte_requests", "b0_l1d_accesses", "b0_l1d_misses",
        "b0_l1d_reservation_fails", "b1_l1d_accesses", "b1_l1d_misses",
        "b1_l1d_reservation_fails",
        "b0_translation_not_ready", "b1_translation_not_ready",
        "classification", "correctness",
    ], residual_rows)
    write_tsv(PACK / "DIAGNOSTIC_DECISION_LOG.tsv", [
        "target", "case", "diagnostic", "cycle_response_percent",
        "classification", "reason", "prototype_action",
    ], decision_rows)

    (PACK / "CLOSEST_WORK_SCREEN.md").write_text('''# Closest-work screen

No Native target exposes a differentiated residual after the strong baseline
and appropriate path diagnostic.

- L1 and M1 are hit-dominated exact-function scale controls. Their material
  response is explained by the accepted VIPT-like overlap. Pichai et al. and
  GPU virtual caching already cover this access-path class.
- L2's deterministic grammar repair enables a real attention-like simulation,
  but B1 changes cycles by only about -0.11%; it has no material residual.
- M2 is a two-instruction low-demand control, not evidence about MoE broadly.
- MSHR/PWQ full events are zero for all B0 Native targets. ISCA 2018,
  Neighborhood, LATPC, MPW, and NeuMMU therefore do not identify an uncovered
  measured bottleneck here.
- Avatar requires L1-TLB misses plus physical mapping/validation evidence.
  Native Atlas is virtual-only and the measured paths are hit-dominated, so no
  speculative mapping problem is inferred.
- MASK/RPAWS already cover broad translation/data or compute/memory pressure;
  no such generic observation is renamed as a problem.

Classes observed: `ACCESS_PATH_MODEL_SENSITIVE_ONLY` for L1/M1;
`NO_MATERIAL_TRANSLATION_RESIDUAL` for L2/M2. No class-D problem exists, so no
problem card is emitted.
''')

    (PACK / "PROTOTYPE_DECISION.md").write_text(f'''# Prototype decision

Final status: **{STATUS}**

No prototype is authorized or implemented. Candidate and matched-control
replays: **0**.

The only material responses (L1/M1) are access-path-model sensitive and already
covered at the capability level by primary work. L2/M2 have no material
translation residual. No finite, localized, differentiated class-D problem
survives.
''')

    (PACK / "REPORT.md").write_text(f'''# {STAGE}

Final status: **{STATUS}**

All four preregistered Native targets are simulator-qualified. L2 was unlocked
through deterministic, byte-identical consumer normalization of exact
`LDC.U8 width=0` implicit constant-load records; no address or instruction was
invented.

L1 and M1 are the same implementation at an exact 8x CTA scale. Per CTA they
match at 67,464 simulated instructions, 514 dynamic memory instructions,
16,388 active-lane refs and 770 logical translation requests. Their local page
behavior is therefore the same; aggregate working set differs.

B1 changes cycles by +13.955% on L1 and +19.793% on M1, classifying both as
`ACCESS_PATH_MODEL_SENSITIVE_ONLY`. L2 changes by -0.109% and M2 remains a tiny
B0-only control; both are `NO_MATERIAL_TRANSLATION_RESIDUAL`.

On L1/M1, B1 reduces translation-not-ready events while increasing L1D
reservation-failure attempts. The net cycle gain is therefore a path/schedule
response, not an additive translation-time fraction or a free real-hardware
speedup. Both arms' service and cache outcomes are retained in the matrix.

No target has MSHR/PWQ-full pressure, no walker/capacity diagnostic is run, and
no differentiated residual/problem card/prototype exists.
''')

    (PACK / "README.md").write_text(f'''# {STAGE}

Start with `REPORT.md`.

Final status: **{STATUS}**

Review order:

1. `NATIVE_INTERPRETATION_FREEZE.md`
2. `NEW_TRACE_QUALIFICATION.tsv`
3. `L1_M1_SCALE_COMPARISON.tsv`
4. `NEW_AI_RESIDUAL_MATRIX.tsv`
5. `L2_GRAMMAR_AUDIT.md`
6. `CLOSEST_WORK_SCREEN.md`
7. `PROTOTYPE_DECISION.md`

No strong-baseline, Native source artifact, simulator mechanism, or platform
parameter is modified.
''')

    raw_rows = []
    def add(kind: str, identity: str, path: Path) -> None:
        raw_rows.append([kind, identity, str(path), digest(path)])
    for target, spec in TARGETS.items():
        arms = [("B0", RAW / spec["b0"])]
        if spec["b1"]:
            arms.append(("B1", RAW / spec["b1"]))
        for arm, directory in arms:
            for filename in ("run.log", "command.json", "grammar.json", "rc.txt", "wall_seconds.txt"):
                add(arm, f"{target}:{filename}", directory / filename)
    for filename in ("AUTHORITY.json", "kernelslist.g", "kernel-7062-ctx_0x5c4fa771e8b0.traceg.xz"):
        add("L2_DERIVED", filename, DERIVED / filename)
    for filename in ("traceg_grammar_smoke", "L2_validator.json", "SPLITKV_canary_validator.json"):
        add("L2_GRAMMAR_AUDIT", filename, GRAMMAR / filename)
    for filename in (
        "prepare_l2_ldc_u8_derived_input.py", "run_native_atlas_residual.py",
        "build_native_residual_review.py",
        "validate_native_residual_review.py",
    ):
        add("SCRIPT", filename, REPO / "util/vm_tlb/awma" / filename)
    raw_rows.extend([
        ["AUTHORITY", "coordination", "git", "ec88f5d588f59cc0472a4365534bac3d229eb301"],
        ["AUTHORITY", "native_atlas", "git", "39548abdd83bf5058abc5ffedd9513286ddab271"],
        ["AUTHORITY", "path_model", "git", "a3756e1f3896c2ab292e2576c6271849c22eaf61"],
        ["AUTHORITY", "strong_reference", "git", "9efe8236e0c6338addfef5480e1da91bffb504eb"],
        ["AUTHORITY", "literature_notebook", "git", "177863f325d77278013e195528903ddc8b292e4e"],
    ])
    write_tsv(PACK / "RAW_DATA_INDEX.tsv", [
        "kind", "identity", "path_or_type", "sha256_or_commit",
    ], raw_rows)

    (PACK / "EXECUTION_SUMMARY.md").write_text('''# Execution summary

Parent coordination: `ec88f5d588f59cc0472a4365534bac3d229eb301`.

Changes are limited to the stage review pack, offline L2 authority, and
runner/build/validation scripts. Strong-reference and Native source artifacts
remain read-only. No node109 run, capture, mechanism, RTL/PPA, target
replacement, or parameter sweep occurs.

Full-kernel work: four B0 qualifications plus three B1 diagnostics. M2 is B0-
only. Prototype runs are zero. Open boundary: Native Atlas has virtual addresses
only, so physical mapping/speculation claims remain unavailable.
''')

    manifest = []
    for path in sorted(PACK.iterdir()):
        if path.is_file() and path.name != "SHA256SUMS":
            manifest.append(f"{digest(path)}  {path.name}")
    (PACK / "SHA256SUMS").write_text("\n".join(manifest) + "\n")
    print(json.dumps({
        "status": STATUS,
        "classifications": classifications,
        "b0_runs": 4, "b1_runs": 3, "candidate_runs": 0,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
