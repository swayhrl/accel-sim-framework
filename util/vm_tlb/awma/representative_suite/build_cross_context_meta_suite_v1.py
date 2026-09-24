#!/usr/bin/env python3
"""Build the frozen Qwen2.5 cross-context structural translation meta-suite.

No GPU, trace producer, simulator, or mechanism result is consumed.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path

from refine_suite_v3 import canonical_function_key

STAGE = "AWMA_QWEN25_CROSS_CONTEXT_TRANSLATION_META_SUITE_V1"
CROSS_SHA = "0a01aa5de4ab7132ab52d18d689e61b635061ae8"
S2_SHA = "ba1b4bdbca47e24a56909eec2764e738c509d2f1"
S2_CATALOG_SHA = "8af6142299a8699db56f69d3d15966ab6f7ad8de31070e4949abef7ee5235139"
S2_CLUSTER_SHA = "a59857d187c649352f9b3852ad9661234f87189679084f808849fb14706c5c79"
S2_TARGET_SHA = "afdecac9f5bfcaa581c15186217d349c47d354d4f68bfa2b3a2eb1ca79055ab6"
SCENARIOS = {
    "S2": ("S2_STRUCTURAL_CATALOG.tsv", 154876910, "ACCEPTED_S2"),
    "T256": ("T256_D32_DERIVED_CONTROL_STRATA.tsv", 113218961, "DERIVED_CONTROL"),
    "T8192": ("T8192_D32_ACCEPTED_S3_TEXT_STRATA.tsv", 317794729, "ACCEPTED_S3_TEXT"),
    "B4": ("B4_T2048_D32_REPLICATED_CONTROL_STRATA.tsv", 308549681, "REPLICATED_CONTROL"),
    "D128": ("T2048_D128_ACCEPTED_S2_TEXT_STRATA.tsv", 497208082, "ACCEPTED_S2_TEXT"),
}
SOURCE_SHA = {
    "T256_D32_DERIVED_CONTROL_STRATA.tsv": "bbbbd91571a9543db233a956d53328c9dcb1232e431009359afde5b501603ea3",
    "T8192_D32_ACCEPTED_S3_TEXT_STRATA.tsv": "162120eb1b0dc19f3351894308fb0380ef2040b06eb85e98f8b0b808c5418940",
    "B4_T2048_D32_REPLICATED_CONTROL_STRATA.tsv": "6d11a909fdf42c428bb54aacdb65f3881b75fc3762de72a14a64c2990d6470a2",
    "T2048_D128_ACCEPTED_S2_TEXT_STRATA.tsv": "5b45f511677f97948bca104323fef3beacd47f9bbca9a05684a2653a1bb2a141",
    "T256_D32_DERIVED_CONTROL_RECURRENCE.tsv": "0bd400dbf1d40ba0ae809445dd1568a32ba0047f6dc5ac3569b9f5a8f27841fa",
    "T8192_D32_ACCEPTED_S3_TEXT_RECURRENCE.tsv": "92a871f7b0039c6d1ed3dadccb362030164aea5415c0d70c014ae7b7744c6a84",
    "B4_T2048_D32_REPLICATED_CONTROL_RECURRENCE.tsv": "4343d8b3cec31b51487d8907b843d50b14888a40c21cd84b3f0b5a9b5ceaf547",
    "T2048_D128_ACCEPTED_S2_TEXT_RECURRENCE.tsv": "f73352dacbcff9a0ef76f8073e682e449ecd92b72652f6ab3ce03ea21d01b591",
}
ARCHETYPE = {
    "CUBLAS_GEMV": "GEMV", "CUBLAS_GEMM": "GEMM",
    "PYTORCH_FLASH_FWD": "FLASH", "AT_NATIVE_ELEMENTWISE": "ELEMENTWISE",
    "AT_NATIVE_UNROLLED_ELEMENTWISE": "ELEMENTWISE",
    "AT_NATIVE_VECTORIZED_ELEMENTWISE": "ELEMENTWISE",
    "AT_NATIVE_REDUCE": "REDUCE", "COPY_KERNEL": "COPY",
    "OTHER_EXACT_IMPLEMENTATION": "OTHER",
}


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def write(path: Path, rows: list[dict], columns: list[str] | None = None) -> None:
    fields = columns or list(rows[0])
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t",
                                lineterminator="\n", extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)


def fn_hash(name: str) -> str:
    return hashlib.sha256(name.encode()).hexdigest()


def implementation_family(name: str) -> str:
    kind = canonical_function_key(name)
    # GEMV contains several distinct exact template implementations in S2;
    # preserve them at Level 2 while allowing shape evolution within each.
    return kind + "_EXACT_" + fn_hash(name) if kind == "CUBLAS_GEMV" else kind


def archetype(family: str) -> str:
    return ARCHETYPE.get(family, family)


def recurrence(row: dict) -> str:
    phase = row["phase"]
    if phase == "PREFILL":
        return "ONE_OBSERVED_PASS"
    if phase != "DECODE":
        return "AUXILIARY"
    low = row["launches_per_decode_step_min"]
    high = row["launches_per_decode_step_max"]
    # S2 catalog includes zero-count absent steps in its min, whereas the
    # cross-context tables summarize only steps where this grid is present.
    # A one-step evolving grid has the same present-step recurrence in both.
    if high.isdigit() and (row["decode_step_count"] == "1" or
                           (low == "0" and row["launch_count"].isdigit() and
                            int(row["launch_count"]) == int(high))):
        return "ONE_STEP_SHAPE_" + high
    if low and high and low.isdigit() and high.isdigit() and low == high:
        return "STABLE_" + low
    return "VARIABLE_" + low + "_" + high


def normalize_s2(rows: list[dict]) -> list[dict]:
    result = []
    for row in rows:
        if row["catalog_row_type"] != "STRUCTURAL_STRATUM":
            continue
        result.append({
            "scenario": "S2", "phase": row["phase"],
            "normalized_kernel_family": row["normalized_kernel_family"],
            "exact_implementation": row["exact_implementation"],
            "grid": row["grid"], "block": row["block"],
            "launch_count": row["stratum_launch_count_s2"],
            "accumulated_gpu_duration_ns": row["stratum_accumulated_gpu_duration_ns"],
            "decode_step_count": row["decode_step_count"],
            "launches_per_decode_step_min": row["launches_per_decode_step_min"],
            "launches_per_decode_step_max": row["launches_per_decode_step_max"],
            "launches_per_decode_step_mean": row["launches_per_decode_step_mean"],
            "recurrence_stable": row["count_stable_across_32_decode_steps"],
        })
    return result


def enrich(row: dict) -> dict:
    row = dict(row)
    row["family_archetype"] = archetype(row["normalized_kernel_family"])
    row["exact_function_sha256"] = fn_hash(row["exact_implementation"])
    row["implementation_family_key"] = implementation_family(row["exact_implementation"])
    row["recurrence_signature"] = recurrence(row)
    row["mass_ns"] = int(row["accumulated_gpu_duration_ns"])
    row["level1"] = (row["phase"], row["family_archetype"])
    row["level2"] = (row["phase"], row["normalized_kernel_family"],
                     row["implementation_family_key"], row["recurrence_signature"])
    row["level2_impl"] = row["level2"][:3]
    row["level3"] = (row["phase"], row["exact_function_sha256"], row["grid"], row["block"])
    return row


def load_inputs(args: argparse.Namespace) -> tuple[dict[str, list[dict]], dict[str, list[dict]], list[dict], list[dict], dict]:
    expected = [(args.s2_catalog, S2_CATALOG_SHA), (args.s2_clusters, S2_CLUSTER_SHA),
                (args.s2_targets, S2_TARGET_SHA)]
    expected += [(args.cross_dir / name, digest) for name, digest in SOURCE_SHA.items()]
    for path, digest in expected:
        if sha(path) != digest:
            raise ValueError("authority SHA mismatch: " + str(path))
    clusters = read(args.s2_clusters)
    targets = [row for row in read(args.s2_targets) if row["suite"] == "BALANCED"]
    if len(targets) != 25 or len({row["cluster_id"] for row in targets}) != 23:
        raise ValueError("accepted S2 BALANCED target identity changed")
    raw: dict[str, list[dict]] = {}
    raw["S2"] = normalize_s2(read(args.s2_catalog))
    rec: dict[str, list[dict]] = {}
    for scenario, (name, expected_total, _) in SCENARIOS.items():
        if scenario != "S2":
            raw[scenario] = read(args.cross_dir / name)
            rec[scenario] = read(args.cross_dir / name.replace("_STRATA.tsv", "_RECURRENCE.tsv"))
        if sum(int(row["accumulated_gpu_duration_ns"]) for row in raw[scenario]) != expected_total:
            raise ValueError("scenario duration total changed: " + scenario)
    rows = {scenario: [enrich(row) for row in values] for scenario, values in raw.items()}
    selected = {row["cluster_id"] for row in targets}
    selected_clusters = [row for row in clusters if row["cluster_id"] in selected]
    if len(selected_clusters) != 23:
        raise ValueError("selected cluster catalog mismatch")
    full_mass = sum(int(row["represented_workload_mass_ns"]) for row in selected_clusters)
    if full_mass != 139333064:
        raise ValueError("accepted S2 BALANCED represented mass changed")
    receipts = json.loads(args.cross_receipt.read_text(encoding="utf-8"))
    if receipts["stage"] != "AWMA_QWEN25_CROSS_CONTEXT_STRUCTURAL_CENSUS_V1":
        raise ValueError("cross-context receipt stage changed")
    return rows, rec, selected_clusters, targets, receipts


def selected_identity(clusters: list[dict], s2_rows: list[dict]) -> tuple[set, set, set, dict[str, list[dict]]]:
    by3 = {row["level3"]: row for row in s2_rows}
    exact: set[tuple] = set()
    level2: set[tuple] = set()
    level1: set[tuple] = set()
    members: dict[str, list[dict]] = {}
    for cluster in clusters:
        found = []
        for grid in cluster["member_grids"].split(";"):
            key = (cluster["phase"], cluster["exact_implementation_sha256"], grid, cluster["block"])
            if key not in by3:
                raise ValueError("selected S2 cluster member missing exact source: " + cluster["cluster_id"])
            row = by3[key]
            found.append(row)
            exact.add(row["level3"])
            level2.add(row["level2"])
            level1.add(row["level1"])
        if len(found) != int(cluster["member_strata_count"]):
            raise ValueError("selected member count mismatch")
        members[cluster["cluster_id"]] = found
    if sum(row["mass_ns"] for row in s2_rows if row["level3"] in exact) != 139333064:
        raise ValueError("S2 exact represented coverage mismatch")
    return exact, level2, level1, members


def coverage(scenario: str, rows: list[dict], exact: set, level2: set, level1: set,
             suite: str, known_total: int) -> dict:
    total = sum(row["mass_ns"] for row in rows)
    if total != known_total:
        raise ValueError("coverage denominator mismatch")
    exact_mass = sum(row["mass_ns"] for row in rows if row["level3"] in exact)
    impl_mass = sum(row["mass_ns"] for row in rows if row["level3"] in exact or row["level2"] in level2)
    family_mass = sum(row["mass_ns"] for row in rows if row["level1"] in level1)
    if not 0 <= exact_mass <= impl_mass <= family_mass <= total:
        raise ValueError("hierarchical coverage not nested")
    high = [row for row in rows if row["level3"] not in exact and
            row["mass_ns"] / total >= 0.01 and row["phase"] != "AUXILIARY"]
    phase_total = Counter()
    phase_exact = Counter()
    for row in rows:
        phase_total[row["phase"]] += row["mass_ns"]
        if row["level3"] in exact:
            phase_exact[row["phase"]] += row["mass_ns"]
    return {
        "scenario": scenario, "suite": suite, "evidence_class": SCENARIOS[scenario][2],
        "full_scenario_gpu_duration_ns": total,
        "exact_covered_ns": exact_mass, "exact_coverage": exact_mass / total,
        "implementation_recurrence_covered_ns": impl_mass,
        "implementation_recurrence_coverage": impl_mass / total,
        "family_archetype_covered_ns": family_mass,
        "family_archetype_coverage": family_mass / total,
        "uncovered_exact_ns": total - exact_mass,
        "uncovered_implementation_ns": total - impl_mass,
        "uncovered_family_ns": total - family_mass,
        "prefill_exact_coverage": phase_exact["PREFILL"] / phase_total["PREFILL"],
        "decode_exact_coverage": phase_exact["DECODE"] / phase_total["DECODE"],
        "high_mass_exact_gap_strata_count": len(high),
        "high_mass_exact_gap_ns": sum(row["mass_ns"] for row in high),
    }


def horizon_extension(cluster: dict, scenario: str, rows: list[dict], member_rows: list[dict],
                      recurrence_rows: list[dict]) -> tuple[bool, int, int]:
    if scenario != "D128" or cluster["cluster_type"] != "DECODE_SHAPE_TRAJECTORY":
        return False, 0, 0
    member_shapes = {row["grid"] for row in member_rows}
    same_impl = [row for row in rows if row["phase"] == "DECODE" and
                 row["exact_function_sha256"] == cluster["exact_implementation_sha256"] and
                 row["block"] == cluster["block"]]
    novel = [row for row in same_impl if row["grid"] not in member_shapes]
    novel_shapes = {row["grid"] for row in novel}
    step_rows = [row for row in recurrence_rows if row["phase"] == "DECODE" and
                 fn_hash(row["exact_implementation"]) == cluster["exact_implementation_sha256"] and
                 row["block"] == cluster["block"] and row["grid"] in novel_shapes]
    steps = {int(row["decode_step"]) for row in step_rows}
    valid = bool(novel) and steps == set(range(33, 129)) and all(int(row["launch_count"]) == 48 for row in step_rows)
    return valid, len(novel), sum(row["mass_ns"] for row in novel)


def cluster_map(clusters: list[dict], members: dict[str, list[dict]],
                rows: dict[str, list[dict]], rec: dict[str, list[dict]]) -> list[dict]:
    out = []
    for scenario in SCENARIOS:
        scenario_rows = rows[scenario]
        b4_decode_gemm = sum(row["mass_ns"] for row in scenario_rows
                             if row["phase"] == "DECODE" and row["normalized_kernel_family"] == "CUBLAS_GEMM")
        for cluster in sorted(clusters, key=lambda x: x["cluster_id"]):
            own = members[cluster["cluster_id"]]
            exact_keys = {row["level3"] for row in own}
            l2_keys = {row["level2"] for row in own}
            l2_impl = {row["level2_impl"] for row in own}
            archetypes = {row["level1"] for row in own}
            exact_hits = [row for row in scenario_rows if row["level3"] in exact_keys]
            l2_hits = [row for row in scenario_rows if row["level2"] in l2_keys]
            impl_hits = [row for row in scenario_rows if row["level2_impl"] in l2_impl]
            family_hits = [row for row in scenario_rows if row["level1"] in archetypes]
            horizon, new_count, new_mass = horizon_extension(cluster, scenario, scenario_rows, own, rec.get(scenario, []))
            if horizon:
                status, reason = "HORIZON_EXTENSION_VARIANT", "SAME_EXACT_IMPLEMENTATION_AND_48_PER_STEP;NEW_GRIDS_ONLY_AT_STEPS_33_128"
            elif exact_hits:
                status, reason = "PORTABLE_EXACT", "FULL_EXACT_IMPLEMENTATION_GRID_BLOCK_PRESENT"
            elif l2_hits:
                same_exact_impl = any(row["exact_function_sha256"] == cluster["exact_implementation_sha256"] for row in l2_hits)
                status = "PORTABLE_IMPLEMENTATION_SHAPE_VARIANT"
                reason = ("SAME_EXACT_FUNCTION_AND_RECURRENCE;GRID_OR_BLOCK_DIFFERS"
                          if same_exact_impl else
                          "CANONICAL_IMPLEMENTATION_FAMILY_AND_RECURRENCE_MATCH;EXACT_SPECIALIZATION_DIFFERS")
            elif impl_hits:
                status, reason = "SCENARIO_SPECIFIC_DISPATCH", "IMPLEMENTATION_PRESENT_BUT_RECURRENCE_STRUCTURE_CHANGED"
            elif family_hits:
                status, reason = "SCENARIO_SPECIFIC_DISPATCH", "ARCHETYPE_PRESENT_WITH_DIFFERENT_IMPLEMENTATION"
            elif scenario == "B4" and cluster["phase"] == "DECODE" and cluster["normalized_kernel_family"] == "CUBLAS_GEMV" and b4_decode_gemm:
                status, reason = "SCENARIO_SPECIFIC_DISPATCH", "DECODE_GEMV_ABSENT_AND_GEMM_PRESENT;OPERATOR_EQUIVALENCE_UNKNOWN"
            else:
                status, reason = "ABSENT_IN_SCENARIO", "NO_SOURCE_SUPPORTED_PHASE_ARCHETYPE_MATCH"
            out.append({
                "scenario": scenario, "s2_cluster_id": cluster["cluster_id"],
                "s2_cluster_type": cluster["cluster_type"], "phase": cluster["phase"],
                "family_archetype": archetype(cluster["normalized_kernel_family"]),
                "normalized_kernel_family": cluster["normalized_kernel_family"],
                "level2_implementation_family_key": own[0]["implementation_family_key"],
                "level2_recurrence_signatures": ";".join(sorted({row["recurrence_signature"] for row in own})),
                "level3_member_shape_count": len(own),
                "s2_represented_mass_ns": cluster["represented_workload_mass_ns"],
                "classification": status, "classification_basis": reason,
                "matching_exact_shape_count": len({row["level3"] for row in exact_hits}),
                "matching_exact_scenario_mass_ns": sum(row["mass_ns"] for row in exact_hits),
                "matching_level2_scenario_mass_ns_nonadditive": sum(row["mass_ns"] for row in l2_hits),
                "matching_archetype_scenario_mass_ns_nonadditive": sum(row["mass_ns"] for row in family_hits),
                "new_horizon_shape_count": new_count,
                "new_horizon_mass_ns": new_mass,
            })
    return out


def classify_strata(scenario: str, rows: list[dict], exact: set, level2: set, level1: set) -> list[dict]:
    total = SCENARIOS[scenario][1]
    out = []
    for row in rows:
        if row["level3"] in exact:
            relation = "LEVEL3_EXACT"
        elif row["level2"] in level2:
            relation = "LEVEL2_IMPLEMENTATION_RECURRENCE"
        elif row["level1"] in level1:
            relation = "LEVEL1_ARCHETYPE_ONLY"
        else:
            relation = "UNCOVERED_ARCHETYPE"
        out.append({
            "scenario": scenario, "phase": row["phase"],
            "family_archetype": row["family_archetype"],
            "normalized_kernel_family": row["normalized_kernel_family"],
            "exact_implementation_sha256": row["exact_function_sha256"],
            "implementation_family_key": row["implementation_family_key"],
            "recurrence_signature": row["recurrence_signature"],
            "grid": row["grid"], "block": row["block"],
            "launch_count": row["launch_count"],
            "accumulated_gpu_duration_ns": row["mass_ns"],
            "scenario_gpu_time_share": row["mass_ns"] / total,
            "s2_balanced_relation": relation,
            "scenario_specific_high_mass_gap": "YES" if relation != "LEVEL3_EXACT" and
            row["mass_ns"] / total >= .01 and row["phase"] != "AUXILIARY" else "NO",
        })
    return out


def extension_candidates(rows: dict[str, list[dict]], rec: dict[str, list[dict]],
                         baseline_exact: set) -> list[dict]:
    grouped: dict[str, dict] = {}
    used: set[tuple[str, tuple]] = set()
    # A decode path is a trajectory only if each observed step has one grid,
    # recurrence is stable, and the grid moves monotonically.
    for scenario in ("T256", "T8192", "B4", "D128"):
        by_impl: dict[tuple, list[dict]] = defaultdict(list)
        for row in rows[scenario]:
            if row["phase"] == "DECODE" and row["level3"] not in baseline_exact:
                by_impl[(row["exact_function_sha256"], row["block"])].append(row)
        for (function, block), group in by_impl.items():
            if len(group) < 16 or len({row["grid"] for row in group}) < 16:
                continue
            shapes = {row["grid"] for row in group}
            step_rows = [row for row in rec[scenario] if row["phase"] == "DECODE" and
                         fn_hash(row["exact_implementation"]) == function and row["block"] == block and row["grid"] in shapes]
            per_step: dict[int, list[dict]] = defaultdict(list)
            for row in step_rows:
                per_step[int(row["decode_step"])].append(row)
            if len(per_step) < 16 or any(len({r["grid"] for r in values}) != 1 for values in per_step.values()):
                continue
            step_sequence = sorted(per_step)
            if step_sequence != list(range(step_sequence[0], step_sequence[-1] + 1)):
                continue
            grids = [int(per_step[step][0]["grid"].split(",")[0]) for step in step_sequence]
            if not (all(a < b for a, b in zip(grids, grids[1:])) or all(a > b for a, b in zip(grids, grids[1:]))):
                continue
            recurrence_counts = {int(per_step[step][0]["launch_count"]) for step in step_sequence}
            if len(recurrence_counts) != 1:
                continue
            if scenario == "D128" and (step_sequence[0] != 33 or step_sequence[-1] != 128):
                continue
            med_grid = statistics.median(grids)
            med_step = min(step_sequence, key=lambda step: (abs(grids[step - step_sequence[0]] - med_grid), step))
            chosen_steps = sorted({step_sequence[0], med_step, step_sequence[-1]})
            candidate_id = "EXT_TRJ_" + hashlib.sha256((scenario + "|" + function + "|" + block).encode()).hexdigest()[:12]
            targets = []
            for step in chosen_steps:
                observed = per_step[step][0]
                targets.append({"source_scenario": scenario, "decode_step": step, "grid": observed["grid"],
                                "block": block, "exact_implementation_sha256": function})
            candidate = {
                "candidate_id": candidate_id, "candidate_type": "HORIZON_SHAPE_CONTINUATION" if scenario == "D128" else "CONTEXT_SHAPE_TRAJECTORY",
                "phase": "DECODE", "family": group[0]["normalized_kernel_family"],
                "function_key": group[0]["implementation_family_key"],
                "recurrence_signature": group[0]["recurrence_signature"],
                "member_rows": [(scenario, row) for row in group], "targets": targets,
                "selection_reason": "SOURCE_MONOTONIC_GRID_RECURRENCE_" + str(next(iter(recurrence_counts))),
            }
            grouped[candidate_id] = candidate
            used.update((scenario, row["level3"]) for row in group)
    # Everything else is an exact implementation+grid+block candidate.
    exact_groups: dict[tuple, list[tuple[str, dict]]] = defaultdict(list)
    for scenario in ("T256", "T8192", "B4", "D128"):
        for row in rows[scenario]:
            if row["phase"] == "AUXILIARY" or row["level3"] in baseline_exact or (scenario, row["level3"]) in used:
                continue
            exact_groups[row["level3"]].append((scenario, row))
    for key, members in exact_groups.items():
        source_scenario, source_row = max(members, key=lambda pair: (pair[1]["mass_ns"], pair[0]))
        candidate_id = "EXT_EXACT_" + hashlib.sha256("|".join(key).encode()).hexdigest()[:12]
        grouped[candidate_id] = {
            "candidate_id": candidate_id, "candidate_type": "EXACT_SHAPE_EXTENSION",
            "phase": source_row["phase"], "family": source_row["normalized_kernel_family"],
            "function_key": source_row["implementation_family_key"],
            "recurrence_signature": source_row["recurrence_signature"],
            "member_rows": members,
            "targets": [{"source_scenario": source_scenario, "decode_step": "REPRESENTATIVE_STEP_UNRESOLVED",
                         "grid": source_row["grid"], "block": source_row["block"],
                         "exact_implementation_sha256": source_row["exact_function_sha256"]}],
            "selection_reason": "EXACT_IMPLEMENTATION_GRID_BLOCK_SHARED_WHERE_PRESENT",
        }
    candidates = list(grouped.values())
    for candidate in candidates:
        by_scenario = Counter()
        for scenario, row in candidate["member_rows"]:
            by_scenario[scenario] += row["mass_ns"]
        candidate["scenario_mass"] = dict(by_scenario)
        candidate["total_mass_ns"] = sum(by_scenario.values())
        candidate["scenario_count"] = len(by_scenario)
        candidate["max_scenario_share"] = max(by_scenario[s] / SCENARIOS[s][1] for s in by_scenario)
        candidate["level3_members"] = {(scenario, row["level3"]) for scenario, row in candidate["member_rows"]}
    # Candidate grouping must partition every non-S2 scenario exact gap.
    expected = {(scenario, row["level3"]) for scenario in ("T256", "T8192", "B4", "D128")
                for row in rows[scenario] if row["phase"] != "AUXILIARY" and row["level3"] not in baseline_exact}
    assigned = [member for candidate in candidates for member in candidate["level3_members"]]
    if set(assigned) != expected or len(assigned) != len(set(assigned)):
        raise ValueError("extension candidates do not partition exact shape gaps")
    return candidates


def select_extensions(candidates: list[dict], rows: dict[str, list[dict]]) -> list[dict]:
    selected = {candidate["candidate_id"] for candidate in candidates if candidate["max_scenario_share"] >= .03}
    # A shared exact shape with at least 10 ms across contexts is a useful
    # reuse point even if each individual scenario share is below 3%.
    selected.update(candidate["candidate_id"] for candidate in candidates
                    if candidate["scenario_count"] >= 2 and candidate["total_mass_ns"] >= 10_000_000)
    # Preserve a second material batch Decode GEMM implementation family.
    batch_gemm = [candidate for candidate in candidates if candidate["phase"] == "DECODE" and
                  candidate["family"] == "CUBLAS_GEMM" and candidate["scenario_mass"].get("B4", 0)]
    selected_impl = {candidate["function_key"] for candidate in batch_gemm if candidate["candidate_id"] in selected}
    distinct = [candidate for candidate in batch_gemm if candidate["function_key"] not in selected_impl and
                candidate["scenario_mass"]["B4"] / SCENARIOS["B4"][1] >= .02]
    if distinct:
        selected.add(max(distinct, key=lambda item: (item["scenario_mass"]["B4"], item["candidate_id"]))["candidate_id"])
    # Each scenario must have a source observed target for its distinctive axis.
    constraints = [
        ("T256", "PREFILL", "PYTORCH_FLASH_FWD"),
        ("T256", "PREFILL", "CUBLAS_GEMM"),
        ("T256", "DECODE", "PYTORCH_FLASH_FWD"),
        ("T256", "DECODE", "AT_NATIVE_ELEMENTWISE"),
        ("T8192", "PREFILL", "PYTORCH_FLASH_FWD"),
        ("T8192", "PREFILL", "CUBLAS_GEMM"),
        ("B4", "DECODE", "CUBLAS_GEMM"),
        ("B4", "DECODE", "PYTORCH_FLASH_FWD"),
        ("D128", "DECODE", "AT_NATIVE_ELEMENTWISE"),
    ]
    for scenario, phase, family in constraints:
        eligible = [candidate for candidate in candidates if candidate["phase"] == phase and
                    candidate["family"] == family and candidate["scenario_mass"].get(scenario, 0)]
        if not eligible:
            raise ValueError("missing required scenario extension archetype " + str((scenario, phase, family)))
        if not any(candidate["candidate_id"] in selected for candidate in eligible):
            best = max(eligible, key=lambda item: (item["scenario_mass"][scenario], item["candidate_id"]))
            selected.add(best["candidate_id"])
    return [candidate for candidate in candidates if candidate["candidate_id"] in selected]


def target_rows_from_extensions(selected: list[dict]) -> list[dict]:
    result = []
    for candidate in sorted(selected, key=lambda item: item["candidate_id"]):
        for number, target in enumerate(candidate["targets"], 1):
            result.append({
                "target_id": candidate["candidate_id"] + "_P" + str(number),
                "candidate_id": candidate["candidate_id"], "source_scenario": target["source_scenario"],
                "represented_scenarios": ";".join(sorted(candidate["scenario_mass"])),
                "scenario_mass_ns_nonadditive": ";".join(s + ":" + str(m) for s, m in sorted(candidate["scenario_mass"].items())),
                "meta_role": "SCENARIO_EXTENSION",
                "phase": candidate["phase"], "normalized_kernel_family": candidate["family"],
                "family_archetype": archetype(candidate["family"]),
                "implementation_family_key": candidate["function_key"],
                "recurrence_signature": candidate["recurrence_signature"],
                "exact_implementation_sha256": target["exact_implementation_sha256"],
                "grid": target["grid"], "block": target["block"],
                "decode_step": target["decode_step"],
                "group_total_native_mass_ns_nonadditive": candidate["total_mass_ns"],
                "group_mass_accounted_ns": candidate["total_mass_ns"] if number == 1 else 0,
                "asset_classification": "MISSING_SIM_TRACE_PLANNING",
                "capture_authorized": "NO", "selection_reason": candidate["selection_reason"],
            })
    return result


def s2_meta_targets(s2_targets: list[dict], cluster_status: list[dict], members: dict[str, list[dict]]) -> list[dict]:
    portable = Counter()
    for row in cluster_status:
        if row["scenario"] != "S2" and row["classification"] in {
            "PORTABLE_EXACT", "PORTABLE_IMPLEMENTATION_SHAPE_VARIANT", "HORIZON_EXTENSION_VARIANT"}:
            portable[row["s2_cluster_id"]] += 1
    result = []
    by_cluster_scenario = defaultdict(list)
    for status in cluster_status:
        if status["classification"] in {"PORTABLE_EXACT", "PORTABLE_IMPLEMENTATION_SHAPE_VARIANT", "HORIZON_EXTENSION_VARIANT"}:
            by_cluster_scenario[status["s2_cluster_id"]].append(status["scenario"])
    for row in s2_targets:
        role = "CORE_CROSS_CONTEXT" if portable[row["cluster_id"]] >= 2 or row["asset_status"] == "REUSABLE_NOW" else "S2_SCENARIO_EXTENSION"
        source_member = members[row["cluster_id"]][0]
        result.append({
            "target_id": row["target_id"], "candidate_id": row["cluster_id"], "source_scenario": "S2",
            "represented_scenarios": ";".join(sorted(set(by_cluster_scenario[row["cluster_id"]]))),
            "scenario_mass_ns_nonadditive": "SEE_CROSS_CONTEXT_CLUSTER_MAP",
            "meta_role": role, "phase": row["phase"],
            "normalized_kernel_family": row["normalized_kernel_family"],
            "family_archetype": archetype(row["normalized_kernel_family"]),
            "implementation_family_key": source_member["implementation_family_key"],
            "recurrence_signature": source_member["recurrence_signature"],
            "exact_implementation_sha256": row["exact_implementation_sha256"],
            "grid": row["grid"], "block": row["block"],
            "decode_step": row["decode_step_v2"],
            "group_total_native_mass_ns_nonadditive": row["cluster_total_represented_mass_ns"],
            "group_mass_accounted_ns": row["represented_mass_accounted_ns"],
            "asset_classification": row["asset_status"],
            "capture_authorized": "NO",
            "selection_reason": "ACCEPTED_S2_BALANCED_REUSE_" + str(portable[row["cluster_id"]]) + "_OTHER_SCENARIOS",
        })
    return result


def meta_identity(baseline: tuple[set, set, set], selected_ext: list[dict],
                  s2_rows: list[dict], all_rows: dict[str, list[dict]]) -> tuple[set, set, set]:
    exact, level2, level1 = (set(part) for part in baseline)
    for candidate in selected_ext:
        for scenario, row in candidate["member_rows"]:
            exact.add(row["level3"])
            level2.add(row["level2"])
            level1.add(row["level1"])
    return exact, level2, level1


def capture_priority(s2_clusters: list[dict], s2_targets: list[dict],
                     selected_ext: list[dict], all_rows: dict[str, list[dict]],
                     members: dict[str, list[dict]]) -> list[dict]:
    by_cluster = defaultdict(list)
    for row in s2_targets:
        by_cluster[row["cluster_id"]].append(row)
    groups: list[dict] = []
    for cluster in s2_clusters:
        targets = by_cluster[cluster["cluster_id"]]
        if not targets or targets[0]["asset_status"] != "MISSING_SIM_TRACE":
            continue
        exacts = {(cluster["phase"], cluster["exact_implementation_sha256"], grid, cluster["block"])
                  for grid in cluster["member_grids"].split(";")}
        mass_by_scenario = Counter()
        for scenario, rows in all_rows.items():
            for row in rows:
                if row["level3"] in exacts:
                    mass_by_scenario[scenario] += row["mass_ns"]
        groups.append({
            "capture_group_id": cluster["cluster_id"], "source_kind": "S2_BALANCED_MISSING",
            "phase": cluster["phase"], "family": cluster["normalized_kernel_family"],
            "function_key": members[cluster["cluster_id"]][0]["implementation_family_key"],
            "target_ids": ";".join(row["target_id"] for row in targets),
            "measurement_target_count": len(targets),
            "native_mass_across_scenarios_ns": sum(mass_by_scenario.values()),
            "scenario_mass": dict(mass_by_scenario),
            "grid_ctas": sum(int(row["representative_grid_ctas"]) for row in targets),
        })
    for candidate in selected_ext:
        groups.append({
            "capture_group_id": candidate["candidate_id"], "source_kind": candidate["candidate_type"],
            "phase": candidate["phase"], "family": candidate["family"],
            "function_key": candidate["function_key"],
            "target_ids": ";".join(candidate["candidate_id"] + "_P" + str(i)
                                   for i in range(1, len(candidate["targets"]) + 1)),
            "measurement_target_count": len(candidate["targets"]),
            "native_mass_across_scenarios_ns": candidate["total_mass_ns"],
            "scenario_mass": candidate["scenario_mass"],
            "grid_ctas": sum(math.prod(int(part) for part in target["grid"].split(","))
                             for target in candidate["targets"]),
        })
    implementation_presence = defaultdict(set)
    for scenario, rows in all_rows.items():
        for row in rows:
            implementation_presence[(row["phase"], row["implementation_family_key"])].add(scenario)
    output = []
    for group in groups:
        impl_scenarios = len(implementation_presence[(group["phase"], group["function_key"])])
        exact_scenarios = len(group["scenario_mass"])
        reuse_value = 1 + .5 * (impl_scenarios - 1) + (exact_scenarios - 1)
        diversity = exact_scenarios
        # Deterministic planning proxy: missing trace qualification plus
        # number and grid size of representative measurements.
        burden = 4 * group["measurement_target_count"] * (
            1 + math.log2(1 + group["grid_ctas"]) / 16)
        score = reuse_value * group["native_mass_across_scenarios_ns"] * diversity / burden
        output.append({
            "capture_group_id": group["capture_group_id"], "source_kind": group["source_kind"],
            "phase": group["phase"], "normalized_kernel_family": group["family"],
            "implementation_family_key": group["function_key"],
            "target_ids": group["target_ids"],
            "cross_context_reuse_value": reuse_value,
            "native_time_mass_across_scenarios_ns": group["native_mass_across_scenarios_ns"],
            "scenario_diversity": diversity,
            "scenario_mass_ns": ";".join(s + ":" + str(m) for s, m in sorted(group["scenario_mass"].items())),
            "actual_measurement_target_count": group["measurement_target_count"],
            "representative_grid_ctas": group["grid_ctas"],
            "estimated_capture_sim_burden_points": burden,
            "priority_score": score, "capture_authorized": "NO",
        })
    output.sort(key=lambda row: (-row["priority_score"], row["capture_group_id"]))
    for i, row in enumerate(output, 1):
        row["priority_rank"] = i
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--s2-catalog", required=True, type=Path)
    parser.add_argument("--s2-clusters", required=True, type=Path)
    parser.add_argument("--s2-targets", required=True, type=Path)
    parser.add_argument("--cross-dir", required=True, type=Path)
    parser.add_argument("--cross-receipt", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    all_rows, rec, clusters, s2_targets, receipt = load_inputs(args)
    base = selected_identity(clusters, all_rows["S2"])
    baseline_exact, baseline_l2, baseline_l1, members = base
    baseline = (baseline_exact, baseline_l2, baseline_l1)
    mapped = cluster_map(clusters, members, all_rows, rec)
    classified = [entry for scenario, rows in all_rows.items()
                  for entry in classify_strata(scenario, rows, *baseline)]
    candidate_groups = extension_candidates(all_rows, rec, baseline_exact)
    extensions = select_extensions(candidate_groups, all_rows)
    s2_meta = s2_meta_targets(s2_targets, mapped, members)
    extension_targets = target_rows_from_extensions(extensions)
    all_meta_targets = s2_meta + extension_targets
    meta = meta_identity(baseline, extensions, all_rows["S2"], all_rows)
    meta_exact, meta_level2, meta_level1 = meta
    for entry in classified:
        key3 = (entry["phase"], entry["exact_implementation_sha256"], entry["grid"], entry["block"])
        key2 = (entry["phase"], entry["normalized_kernel_family"],
                entry["implementation_family_key"], entry["recurrence_signature"])
        key1 = (entry["phase"], entry["family_archetype"])
        entry["meta_suite_relation"] = ("LEVEL3_EXACT" if key3 in meta_exact else
                                        "LEVEL2_IMPLEMENTATION_RECURRENCE" if key2 in meta_level2 else
                                        "LEVEL1_ARCHETYPE_ONLY" if key1 in meta_level1 else
                                        "UNCOVERED_ARCHETYPE")
        entry["remaining_high_mass_exact_gap"] = ("YES" if entry["meta_suite_relation"] != "LEVEL3_EXACT" and
                                                  float(entry["scenario_gpu_time_share"]) >= .01 and
                                                  entry["phase"] != "AUXILIARY" else "NO")
    covered = []
    for scenario in SCENARIOS:
        for name, identity in (("S2_BALANCED_ONLY", baseline), ("PROPOSED_META_SUITE", meta)):
            covered.append(coverage(scenario, all_rows[scenario], *identity,
                                    name, SCENARIOS[scenario][1]))
    if covered[0]["exact_covered_ns"] != 139333064:
        raise ValueError("S2 accepted BALANCED coverage changed")
    d128_traj = [row for row in mapped if row["scenario"] == "D128" and
                 row["s2_cluster_type"] == "DECODE_SHAPE_TRAJECTORY"]
    if len(d128_traj) != 1 or d128_traj[0]["classification"] != "HORIZON_EXTENSION_VARIANT" or \
       d128_traj[0]["new_horizon_shape_count"] != 96 or d128_traj[0]["new_horizon_mass_ns"] != 28654328:
        raise ValueError("D128 continuation evidence changed")
    t256_gemv = [row for row in mapped if row["scenario"] == "T256" and
                 row["normalized_kernel_family"] == "CUBLAS_GEMV"]
    if len(t256_gemv) != 5 or any(row["classification"] != "PORTABLE_EXACT" for row in t256_gemv):
        raise ValueError("T256 five-GEMV shared skeleton changed")
    b4_gemv = [row for row in mapped if row["scenario"] == "B4" and
               row["normalized_kernel_family"] == "CUBLAS_GEMV"]
    if len(b4_gemv) != 5 or any(row["classification"] != "SCENARIO_SPECIFIC_DISPATCH" for row in b4_gemv):
        raise ValueError("B4 GEMV dispatch shift changed")
    if len({row["target_id"] for row in all_meta_targets}) != len(all_meta_targets):
        raise ValueError("meta suite target identity duplicated")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    write(args.output_dir / "CROSS_CONTEXT_CLUSTER_MAP.tsv", mapped)
    write(args.output_dir / "CROSS_CONTEXT_COVERAGE.tsv", covered)
    write(args.output_dir / "SCENARIO_STRATA_CLASSIFICATION.tsv", classified)
    high_remaining = sorted((row for row in classified if row["remaining_high_mass_exact_gap"] == "YES"),
                            key=lambda row: (row["scenario"], -int(row["accumulated_gpu_duration_ns"]), row["grid"]))
    write(args.output_dir / "SCENARIO_HIGH_MASS_GAPS.tsv", high_remaining, list(classified[0]))
    write(args.output_dir / "META_SUITE_TARGETS.tsv", all_meta_targets)
    ext_rows = [row for row in all_meta_targets if row["meta_role"] != "CORE_CROSS_CONTEXT"]
    write(args.output_dir / "SCENARIO_EXTENSION_TARGETS.tsv", ext_rows)
    priority = capture_priority(clusters, s2_targets, extensions, all_rows, members)
    write(args.output_dir / "CAPTURE_PRIORITY.tsv", priority)
    candidate_review = []
    selected_ids = {candidate["candidate_id"] for candidate in extensions}
    for candidate in sorted(candidate_groups, key=lambda item: (-item["total_mass_ns"], item["candidate_id"])):
        candidate_review.append({
            "candidate_id": candidate["candidate_id"], "candidate_type": candidate["candidate_type"],
            "phase": candidate["phase"], "family": candidate["family"],
            "implementation_family_key": candidate["function_key"],
            "scenario_mass_ns": ";".join(s + ":" + str(m) for s, m in sorted(candidate["scenario_mass"].items())),
            "total_native_mass_ns": candidate["total_mass_ns"],
            "max_scenario_share": candidate["max_scenario_share"],
            "actual_target_count": len(candidate["targets"]),
            "selected": "YES" if candidate["candidate_id"] in selected_ids else "NO",
            "selection_reason": candidate["selection_reason"],
        })
    write(args.output_dir / "EXTENSION_CANDIDATES.tsv", candidate_review)
    input_hashes = {"s2_catalog": S2_CATALOG_SHA, "s2_clusters": S2_CLUSTER_SHA,
                    "s2_targets": S2_TARGET_SHA, "cross_receipt": sha(args.cross_receipt)}
    input_hashes.update({name: digest for name, digest in SOURCE_SHA.items()})
    output_receipt = {
        "stage": STAGE, "status": "META_SUITE_DESIGN_FOR_REVIEW",
        "parent_s2_sha": S2_SHA, "cross_authority_sha": CROSS_SHA,
        "input_sha256": input_hashes,
        "scenarios": {name: {"total_gpu_duration_ns": total, "evidence_class": klass}
                      for name, (_, total, klass) in SCENARIOS.items()},
        "s2_balanced_clusters": len(clusters), "s2_balanced_targets": len(s2_targets),
        "cross_context_core_targets": sum(row["meta_role"] == "CORE_CROSS_CONTEXT" for row in all_meta_targets),
        "s2_specific_extension_targets": sum(row["meta_role"] == "S2_SCENARIO_EXTENSION" for row in all_meta_targets),
        "new_scenario_extension_groups": len(extensions),
        "new_scenario_extension_targets": len(extension_targets),
        "meta_suite_total_targets": len(all_meta_targets),
        "candidate_groups_evaluated": len(candidate_groups),
        "capture_authorized": False, "gpu_run_performed": False,
        "selection_inputs": "Native source structure and time, accepted S2 target identities; no translation sensitivity, C1, simulation, or mechanism result",
    }
    (args.output_dir / "RUN_RECEIPT.json").write_text(json.dumps(output_receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"receipt": output_receipt,
                      "baseline_coverage": [row for row in covered if row["suite"] == "S2_BALANCED_ONLY"],
                      "meta_coverage": [row for row in covered if row["suite"] == "PROPOSED_META_SUITE"]},
                     indent=2))


if __name__ == "__main__":
    main()
