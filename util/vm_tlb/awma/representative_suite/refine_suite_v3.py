#!/usr/bin/env python3
"""Build the AWMA Phase 3 representative suite from frozen Native evidence.

All selection inputs are Native launch durations, structural fields, and accepted
asset classifications. No simulator or mechanism result enters the selector.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import statistics
from collections import Counter, defaultdict
from pathlib import Path

V2_SHA = "222d5dfeeb1e7aaae3423f13873053c37c27f5c6290d8a58bd3186a0803ca77a"
CATALOG_SHA = "8af6142299a8699db56f69d3d15966ab6f7ad8de31070e4949abef7ee5235139"
ASSET_SHA = "7041c0aedc6e5c066530f4a412192fee9011c69301018b15e4e829c963cdeed0"
FULL_S2_NS = 154876910
PHASE_NS = {"PREFILL": 32229639, "DECODE": 122454407, "AUXILIARY": 192864}
STATUSES = {"REUSABLE_NOW", "REQUIRES_REQUALIFICATION", "MISSING_SIM_TRACE"}
SEED = "AWMA_PHASE3_SCIENTIFIC_CLUSTER_HOLDOUT_V1"
FIRST_LAST_MEDOID = 3


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict], columns: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, delimiter="\t", lineterminator="\n", extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)


def canonical_kind(name: str) -> str:
    """Use exactly the accepted Lane A catalog's narrow implementation rules."""
    lowered = name.lower()
    if "flash_fwd_splitkv_combine_kernel" in lowered:
        return "FLASH_FWD_SPLITKV_COMBINE"
    if "flash_fwd_splitkv_kernel" in lowered:
        return "FLASH_FWD_SPLITKV"
    if "flash_fwd_kernel" in lowered:
        return "FLASH_FWD"
    if "internal::gemvx" in lowered or "gemvx::kernel" in lowered:
        return "CUBLAS_GEMV"
    if "cutlass_80_tensorop_f16_s16816gemm_relu_f16_256x128_32x3_tn_align8" in lowered:
        return "CUTLASS_F16_GEMM_256X128_32X3_TN_ALIGN8"
    return "EXACT_IMPLEMENTATION_UNNORMALIZED"


def canonical_function_key(name: str) -> str:
    kind = canonical_kind(name)
    return kind if kind != "EXACT_IMPLEMENTATION_UNNORMALIZED" else "EXACT_SHA256_" + hashlib.sha256(name.encode()).hexdigest()


def canonical_stratum_key(phase: str, family: str, function: str, grid: str, block: str) -> str:
    fields = (phase, family, canonical_function_key(function), grid, block)
    return hashlib.sha256("\x1f".join(fields).encode()).hexdigest()


def structural_key(row: dict[str, str]) -> tuple[str, str, str, str, str]:
    return (row["phase"], row["normalized_kernel_family"], row["exact_implementation"], row["grid"], row["block"])


def launch_key(row: dict[str, str]) -> tuple[str, str, str, str, str]:
    return (row["phase"], row["normalized_kernel_family"], row["exact_kernel_function"], row["grid"], row["block"])


def stable_id(prefix: str, values: tuple[str, ...]) -> str:
    return prefix + hashlib.sha256("\x1f".join(values).encode()).hexdigest()[:12]


def grid_tuple(grid: str) -> tuple[int, int, int]:
    parts = tuple(int(item) for item in grid.split(","))
    if len(parts) != 3 or min(parts) < 1:
        raise ValueError(f"invalid grid: {grid}")
    return parts


def observed_step_runs(step_records: list[dict]) -> list[list[dict]]:
    """Split when grid reverses, recurrence changes, or duration changes >=25%."""
    result: list[list[dict]] = []
    current: list[dict] = []
    direction = 0
    for record in step_records:
        if current:
            prev = current[-1]
            prev_grid, next_grid = grid_tuple(prev["grid"]), grid_tuple(record["grid"])
            signs = {((b > a) - (b < a)) for a, b in zip(prev_grid, next_grid)} - {0}
            change = next(iter(signs)) if len(signs) == 1 else 0
            reversed_grid = len(signs) > 1 or (direction != 0 and change != 0 and change != direction)
            count_switch = record["recurrence"] != prev["recurrence"]
            # Sustained change requires two later steps, avoiding a single noisy point.
            i = step_records.index(record)
            regime = False
            if len(current) >= 3 and i + 1 < len(step_records):
                baseline = statistics.median(float(x["selection_pool_median_launch_duration_ns"]) for x in current[-3:])
                later = statistics.median(float(x["selection_pool_median_launch_duration_ns"]) for x in step_records[i:i + 2])
                regime = max(baseline, later) / max(1.0, min(baseline, later)) >= 1.25
            if reversed_grid or count_switch or regime:
                result.append(current)
                current = []
                direction = 0
            elif change:
                direction = change
        current.append(record)
    if current:
        result.append(current)
    return result


def medoid_step(records: list[dict]) -> int:
    values = [grid_tuple(record["grid"])[0] for record in records]
    median = statistics.median(values)
    return min((int(record["step"]) for record in records), key=lambda step: (abs(values[step - int(records[0]["step"])] - median), step))


def representative_launch(rows: list[dict[str, str]]) -> dict[str, str]:
    median = statistics.median(int(row["duration_ns"]) for row in rows)
    return min(rows, key=lambda row: (abs(int(row["duration_ns"]) - median), int(row["global_launch_index"])))


def validate_catalog(catalog: list[dict[str, str]], launches: list[dict[str, str]]) -> tuple[list[dict[str, str]], dict]:
    strata = [row for row in catalog if row["catalog_row_type"] == "STRUCTURAL_STRATUM"]
    if len(strata) != 100 or len(launches) != 34677:
        raise ValueError("accepted source cardinality changed")
    launch_groups: dict[tuple, list[dict]] = defaultdict(list)
    for row in launches:
        launch_groups[launch_key(row)].append(row)
    catalog_keys = {structural_key(row) for row in strata}
    if set(launch_groups) != catalog_keys:
        raise ValueError("catalog/V2 structural keys differ")
    for row in strata:
        group = launch_groups[structural_key(row)]
        if len(group) != int(row["stratum_launch_count_s2"]):
            raise ValueError("catalog/V2 stratum launch count differs")
        if sum(int(item["duration_ns"]) for item in group) != int(row["stratum_accumulated_gpu_duration_ns"]):
            raise ValueError("catalog/V2 stratum duration differs")
        if canonical_kind(row["exact_implementation"]) != row["implementation_match_key"]:
            raise ValueError("catalog canonical implementation key differs")
        if row["lane_c_asset_status"] not in STATUSES:
            raise ValueError("unexpected simulator asset status")
    observed = Counter()
    for row in launches:
        observed[row["phase"]] += int(row["duration_ns"])
    if dict(observed) != PHASE_NS or sum(observed.values()) != FULL_S2_NS:
        raise ValueError("full-S2 denominator changed")
    return strata, launch_groups


def build_clusters(strata: list[dict[str, str]], launch_groups: dict, selection_launch_groups: dict) -> tuple[list[dict], list[dict]]:
    by_impl: dict[tuple, list[dict]] = defaultdict(list)
    for row in strata:
        if row["phase"] == "DECODE":
            by_impl[(row["normalized_kernel_family"], row["exact_implementation"], row["block"])].append(row)
    trajectory_members: dict[str, list[dict]] = {}
    trajectory_steps: list[dict] = []
    for identity, members in sorted(by_impl.items()):
        per_step: dict[int, list[dict]] = defaultdict(list)
        for member in members:
            for launch in launch_groups[structural_key(member)]:
                per_step[int(launch["decode_step"])].append(launch)
        if sorted(per_step) != list(range(1, 33)):
            continue
        # Concurrent multiple shapes are separate paths, not an evolving grid.
        if any(len({row["grid"] for row in per_step[step]}) != 1 for step in per_step):
            continue
        grids = {next(iter({row["grid"] for row in values})) for values in per_step.values()}
        if len(grids) <= 1:
            continue
        observations = []
        for step in sorted(per_step):
            values = per_step[step]
            selection_values = [row for row in values if row in selection_launch_groups[launch_key(row)]]
            if not selection_values:
                raise ValueError("trajectory step has no non-holdout selection records")
            observations.append({"step": step, "grid": values[0]["grid"], "recurrence": len(values),
                                 "accumulated_duration_ns": sum(int(x["duration_ns"]) for x in values),
                                 "median_launch_duration_ns": statistics.median(int(x["duration_ns"]) for x in values),
                                 "selection_pool_median_launch_duration_ns": statistics.median(int(x["duration_ns"]) for x in selection_values)})
        for run in observed_step_runs(observations):
            # A one-step run remains a structural stratum; no trajectory claim.
            if len(run) < 2:
                continue
            run_grids = {entry["grid"] for entry in run}
            if len(run_grids) < 2:
                continue
            ident = stable_id("TRJ_", (*identity, str(run[0]["step"]), str(run[-1]["step"])))
            run_members = [member for member in members if member["grid"] in run_grids]
            # A repeated grid in disjoint runs would overlap clusters: refuse it.
            if len(run_members) != len(run_grids):
                raise ValueError("trajectory grid repeats across segments; requires occurrence identity")
            trajectory_members[ident] = run_members
            chosen_steps = sorted({int(run[0]["step"]), medoid_step(run), int(run[-1]["step"])})
            for record in run:
                trajectory_steps.append({"trajectory_id": ident, "normalized_kernel_family": identity[0],
                                         "exact_implementation_sha256": hashlib.sha256(identity[1].encode()).hexdigest(),
                                         "block": identity[2], "step": record["step"], "grid": record["grid"],
                                         "recurrence": record["recurrence"],
                                         "accumulated_duration_ns": record["accumulated_duration_ns"],
                                         "median_launch_duration_ns": record["median_launch_duration_ns"],
                                         "selection_pool_median_launch_duration_ns": record["selection_pool_median_launch_duration_ns"],
                                         "selected_measurement_point": "YES" if record["step"] in chosen_steps else "NO"})
    assigned = {structural_key(member) for members in trajectory_members.values() for member in members}
    if len(assigned) != sum(len(group) for group in trajectory_members.values()):
        raise ValueError("trajectory structural overlap")
    clusters = []
    for ident, members in trajectory_members.items():
        clusters.append(make_cluster(ident, "DECODE_SHAPE_TRAJECTORY", members, selection_launch_groups,
                                     [record for record in trajectory_steps if record["trajectory_id"] == ident]))
    for member in strata:
        if structural_key(member) not in assigned:
            ident = stable_id("STR_", structural_key(member))
            clusters.append(make_cluster(ident, "STRUCTURAL_STRATUM", [member], selection_launch_groups, []))
    clusters.sort(key=lambda cluster: cluster["cluster_id"])
    if sum(cluster["represented_workload_mass_ns"] for cluster in clusters) != FULL_S2_NS:
        raise ValueError("cluster masses do not partition full S2")
    return clusters, trajectory_steps


def make_cluster(ident: str, kind: str, members: list[dict], launch_groups: dict, steps: list[dict]) -> dict:
    phase = members[0]["phase"]
    family = members[0]["normalized_kernel_family"]
    exact = members[0]["exact_implementation"]
    block = members[0]["block"]
    if any((row["phase"], row["normalized_kernel_family"], row["exact_implementation"], row["block"]) != (phase, family, exact, block) for row in members):
        raise ValueError("incompatible trajectory members")
    mass = sum(int(row["stratum_accumulated_gpu_duration_ns"]) for row in members)
    if kind == "DECODE_SHAPE_TRAJECTORY":
        chosen_steps = sorted(int(row["step"]) for row in steps if row["selected_measurement_point"] == "YES")
        targets = []
        for step in chosen_steps:
            record = next(row for row in steps if int(row["step"]) == step)
            member = next(row for row in members if row["grid"] == record["grid"])
            group = [row for row in launch_groups[structural_key(member)] if int(row["decode_step"]) == step]
            targets.append((member, representative_launch(group)))
    else:
        member = members[0]
        available = launch_groups[structural_key(member)]
        targets = [(member, representative_launch(available))] if available else []
    return {"cluster_id": ident, "cluster_type": kind, "phase": phase, "normalized_kernel_family": family,
            "exact_implementation": exact, "implementation_match_key": members[0]["implementation_match_key"],
            "block": block, "member_strata": members, "member_strata_count": len(members),
            "member_grids": sorted({member["grid"] for member in members}),
            "launch_count": sum(int(row["stratum_launch_count_s2"]) for row in members),
            "represented_workload_mass_ns": mass, "targets": targets,
            "target_count": len(targets)}


def matched_asset(member: dict, assets: list[dict], launch_by_index: dict[str, dict]) -> tuple[dict, dict] | None:
    names = set(member["lane_c_candidate_ids"].split(";")) - {""}
    candidates = [asset for asset in assets if asset["candidate"] in names and asset["phase"] == member["phase"]
                  and asset["kind"] == "SIMULATOR_NATIVE" and "FORMAL" in asset["producer_identity"]
                  and asset["grid"] == member["grid"] and asset["block"] == member["block"]
                  and canonical_function_key(asset["exact_function"]) == canonical_function_key(member["exact_implementation"])
                  and asset["classification"] == member["lane_c_asset_status"]
                  and len(asset["payload_sha256"]) == 64 and len(asset["runner_index_sha256"]) == 64]
    matched = []
    for asset in candidates:
        payload = re.search(r"kernel-([0-9]+)-", asset["payload_rel"])
        if not payload or payload.group(1) not in launch_by_index:
            continue
        launch = launch_by_index[payload.group(1)]
        if launch_key(launch) != structural_key(member):
            continue
        if asset["decode_step"].isdigit() and int(asset["decode_step"]) != int(launch["decode_step"]):
            continue
        matched.append((asset, launch))
    if not matched:
        return None
    # Prefer accepted T0/T1/T2, then step closest to 16, then stable candidate ID.
    return min(matched, key=lambda pair: (0 if pair[0]["accepted_target"] in {"T0", "T1", "T2"} else 1,
                                           abs(int(pair[0]["decode_step"]) - 16) if pair[0]["decode_step"].isdigit() else 0,
                                           pair[0]["candidate"], pair[0]["payload_sha256"]))


def target_records(cluster: dict, assets: list[dict], launch_by_index: dict[str, dict]) -> list[dict]:
    result = []
    for index, (member, launch) in enumerate(cluster["targets"], 1):
        status = member["lane_c_asset_status"]
        match = matched_asset(member, assets, launch_by_index) if status != "MISSING_SIM_TRACE" else None
        if status != "MISSING_SIM_TRACE" and match is None:
            raise ValueError(f"accepted asset identity failed to close: {cluster['cluster_id']}")
        asset = match[0] if match else None
        if match:
            launch = match[1]
        if asset is not None and asset["kind"] != "SIMULATOR_NATIVE":
            raise ValueError("Native-only input cannot satisfy simulator target")
        target_id = cluster["cluster_id"] + "_P" + str(index)
        result.append({"target_id": target_id, "cluster_id": cluster["cluster_id"], "phase": cluster["phase"],
                       "normalized_kernel_family": cluster["normalized_kernel_family"],
                       "exact_implementation_sha256": hashlib.sha256(cluster["exact_implementation"].encode()).hexdigest(),
                       "implementation_match_key": cluster["implementation_match_key"],
                       "canonical_exact_function_key": canonical_function_key(cluster["exact_implementation"]),
                       "canonical_stratum_key": canonical_stratum_key(cluster["phase"], cluster["normalized_kernel_family"],
                                                                     cluster["exact_implementation"], launch["grid"], launch["block"]),
                       "global_launch_index_v2": launch["global_launch_index"],
                       "decode_step_v2": launch["decode_step"] or "N/A", "grid": launch["grid"], "block": launch["block"],
                       "representative_launch_native_duration_ns": int(launch["duration_ns"]),
                       "representative_grid_ctas": grid_tuple(launch["grid"])[0] * grid_tuple(launch["grid"])[1] * grid_tuple(launch["grid"])[2],
                       "asset_status": status, "asset_candidate": asset["candidate"] if asset else "NONE",
                       "accepted_target": asset["accepted_target"] if asset else "NONE",
                       "payload_sha256": asset["payload_sha256"] if asset else "NONE",
                       "runner_index_sha256": asset["runner_index_sha256"] if asset else "NONE",
                       "new_capture_authorized": "NO"})
    return result


def cluster_public(cluster: dict) -> dict:
    return {"cluster_id": cluster["cluster_id"], "cluster_type": cluster["cluster_type"], "phase": cluster["phase"],
            "normalized_kernel_family": cluster["normalized_kernel_family"],
            "exact_implementation_sha256": hashlib.sha256(cluster["exact_implementation"].encode()).hexdigest(),
            "implementation_match_key": cluster["implementation_match_key"],
            "canonical_exact_function_key": canonical_function_key(cluster["exact_implementation"]), "block": cluster["block"],
            "member_strata_count": cluster["member_strata_count"], "member_grids": ";".join(cluster["member_grids"]),
            "launch_count": cluster["launch_count"], "represented_workload_mass_ns": cluster["represented_workload_mass_ns"],
            "measurement_target_count": cluster["target_count"],
            "asset_statuses": ";".join(sorted({m["lane_c_asset_status"] for m in cluster["member_strata"]}))}


def mandatory_clusters(clusters: list[dict], selection_pool_mass: dict[str, int]) -> set[str]:
    required_gemv = {("1216,1,1", "16,4,1"), ("18992,1,1", "8,8,1"), ("224,1,1", "16,4,1"),
                     ("224,1,1", "32,4,1"), ("32,1,1", "32,4,1")}
    ids = set()
    gemv_found = set()
    for cluster in clusters:
        phase, family = cluster["phase"], cluster["normalized_kernel_family"]
        if cluster["cluster_type"] == "DECODE_SHAPE_TRAJECTORY":
            ids.add(cluster["cluster_id"])
        if phase == "DECODE" and family == "CUBLAS_GEMV":
            shape = (cluster["member_grids"][0], cluster["block"])
            if shape in required_gemv:
                ids.add(cluster["cluster_id"])
                gemv_found.add(shape)
        if family == "PYTORCH_FLASH_FWD" and phase in {"PREFILL", "DECODE"}:
            ids.add(cluster["cluster_id"])
    if gemv_found != required_gemv:
        raise ValueError("five required Decode GEMV variants are not distinct and present")
    prefill_gemms = sorted((cluster for cluster in clusters if cluster["phase"] == "PREFILL" and cluster["normalized_kernel_family"] == "CUBLAS_GEMM"),
                          key=lambda cluster: (-selection_pool_mass[cluster["cluster_id"]], cluster["cluster_id"]))
    ids.update(cluster["cluster_id"] for cluster in prefill_gemms[:3])
    return ids


def scientific_holdout(clusters: list[dict], mandatory: set[str]) -> dict:
    # Stable per-step shape paths qualify; identity hash is independent of time and outcomes.
    eligible = [cluster for cluster in clusters if cluster["phase"] == "DECODE" and cluster["cluster_type"] == "STRUCTURAL_STRATUM"
                and cluster["cluster_id"] not in mandatory and cluster["launch_count"] >= 32
                and cluster["member_strata"][0]["count_stable_across_32_decode_steps"] == "YES"
                and cluster["member_strata"][0]["shape_stable_across_32_decode_steps"] == "YES"
                and cluster["member_strata"][0]["decode_step_count"] == "32"]
    if not eligible:
        raise ValueError("no separate scientific holdout trajectory exists")
    chosen = min(eligible, key=lambda cluster: hashlib.sha256((SEED + "|" + cluster["cluster_id"]).encode()).hexdigest())
    return chosen


def ranked_optional(clusters: list[dict], excluded: set[str], selection_pool_mass: dict[str, int]) -> list[dict]:
    # After mandatory anchors, all optional clusters cost one missing trace/target.
    options = [cluster for cluster in clusters if cluster["cluster_id"] not in excluded
               and cluster["phase"] != "AUXILIARY" and cluster["target_count"] > 0]
    if any(cluster["target_count"] != 1 or cluster["member_strata"][0]["lane_c_asset_status"] != "MISSING_SIM_TRACE" for cluster in options):
        raise ValueError("optional frontier cost assumption changed")
    return sorted(options, key=lambda cluster: (-selection_pool_mass[cluster["cluster_id"]], cluster["cluster_id"]))


def find_tier_indices(options: list[dict], selection_pool_mass: dict[str, int], selection_pool_ns: int) -> tuple[int, int]:
    # Marginal selection-pool mass thresholds; no fixed K or holdout-weight tuning.
    balanced = sum(selection_pool_mass[cluster["cluster_id"]] / selection_pool_ns >= 0.01 for cluster in options)
    broad = sum(selection_pool_mass[cluster["cluster_id"]] / selection_pool_ns >= 0.0025 for cluster in options)
    if not 0 < balanced < broad:
        raise ValueError("no three distinct data-driven frontier tiers")
    return balanced, broad


def summarize(name: str, chosen: list[dict], targets: list[dict], all_clusters: list[dict],
              selection_pool_ns: int, selection_pool_mass_by_cluster: dict[str, int]) -> dict:
    ids = {cluster["cluster_id"] for cluster in chosen}
    if len(ids) != len(chosen):
        raise ValueError("cluster counted more than once")
    members = [target for target in targets if target["cluster_id"] in ids]
    mass = sum(cluster["represented_workload_mass_ns"] for cluster in chosen)
    selection_mass = sum(selection_pool_mass_by_cluster[cluster["cluster_id"]] for cluster in chosen)
    phase_mass = {phase: sum(cluster["represented_workload_mass_ns"] for cluster in chosen if cluster["phase"] == phase)
                  for phase in PHASE_NS}
    all_families = {(cluster["phase"], cluster["normalized_kernel_family"]) for cluster in all_clusters}
    covered_families = {(cluster["phase"], cluster["normalized_kernel_family"]) for cluster in chosen}
    all_impl = {(cluster["phase"], cluster["normalized_kernel_family"], cluster["exact_implementation"]) for cluster in all_clusters}
    covered_impl = {(cluster["phase"], cluster["normalized_kernel_family"], cluster["exact_implementation"]) for cluster in chosen}
    trajectory_total = sum(cluster["cluster_type"] == "DECODE_SHAPE_TRAJECTORY" for cluster in all_clusters)
    trajectory_covered = sum(cluster["cluster_type"] == "DECODE_SHAPE_TRAJECTORY" for cluster in chosen)
    status_counts = Counter(target["asset_status"] for target in members)
    # Point estimate is a planning index, never predicted simulator seconds.
    burden_points = sum({"REUSABLE_NOW": 1, "REQUIRES_REQUALIFICATION": 2, "MISSING_SIM_TRACE": 4}[target["asset_status"]]
                        for target in members)
    return {"suite": name, "cluster_count": len(chosen), "actual_simulator_targets": len(members),
            "represented_workload_mass_ns": mass, "full_s2_gpu_duration_ns": FULL_S2_NS,
            "full_s2_coverage": mass / FULL_S2_NS, "selection_pool_duration_ns": selection_pool_ns,
            "represented_selection_pool_mass_ns": selection_mass,
            "selection_pool_coverage": selection_mass / selection_pool_ns,
            "prefill_represented_ns": phase_mass["PREFILL"], "prefill_full_workload_coverage": phase_mass["PREFILL"] / PHASE_NS["PREFILL"],
            "decode_represented_ns": phase_mass["DECODE"], "decode_full_workload_coverage": phase_mass["DECODE"] / PHASE_NS["DECODE"],
            "auxiliary_represented_ns": phase_mass["AUXILIARY"], "phase_family_coverage": f"{len(covered_families)}/{len(all_families)}",
            "covered_phase_families": ";".join(f"{phase}:{family}" for phase, family in sorted(covered_families)),
            "structural_cluster_coverage": f"{len(chosen)}/{len(all_clusters)}",
            "exact_implementation_coverage": f"{len(covered_impl)}/{len(all_impl)}",
            "exact_implementation_shape_coverage": f"{sum(cluster['member_strata_count'] for cluster in chosen)}/{sum(cluster['member_strata_count'] for cluster in all_clusters)}",
            "measured_exact_implementation_shape_count": len({target["canonical_stratum_key"] for target in members}),
            "trajectory_coverage": f"{trajectory_covered}/{trajectory_total}",
            "reusable_now_targets": status_counts["REUSABLE_NOW"], "requires_requalification_targets": status_counts["REQUIRES_REQUALIFICATION"],
            "missing_sim_trace_targets": status_counts["MISSING_SIM_TRACE"],
            "estimated_measurement_burden_points": burden_points,
            "representative_native_duration_sum_ns": sum(target["representative_launch_native_duration_ns"] for target in members),
            "representative_grid_ctas_sum": sum(target["representative_grid_ctas"] for target in members)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--v2-inventory", type=Path, required=True)
    parser.add_argument("--structural-catalog", type=Path, required=True)
    parser.add_argument("--asset-inventory", type=Path, required=True)
    parser.add_argument("--statistical-holdout", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    for path, expected in ((args.v2_inventory, V2_SHA), (args.structural_catalog, CATALOG_SHA), (args.asset_inventory, ASSET_SHA)):
        if digest(path) != expected:
            raise ValueError(f"source SHA mismatch: {path}")
    launches, catalog, assets = read_tsv(args.v2_inventory), read_tsv(args.structural_catalog), read_tsv(args.asset_inventory)
    strata, launch_groups = validate_catalog(catalog, launches)
    holdout_launch_ids = {row["global_launch_index"] for row in read_tsv(args.statistical_holdout)}
    if len(holdout_launch_ids) != 6897:
        raise ValueError("statistical holdout identity changed")
    selection_launch_groups: dict[tuple, list[dict]] = defaultdict(list)
    for row in launches:
        if row["global_launch_index"] not in holdout_launch_ids:
            selection_launch_groups[launch_key(row)].append(row)
    clusters, trajectory_steps = build_clusters(strata, launch_groups, selection_launch_groups)
    selection_pool_ns = sum(int(row["duration_ns"]) for row in launches if row["global_launch_index"] not in holdout_launch_ids)
    if selection_pool_ns != 126440396:
        raise ValueError("V2 statistical selection pool weight changed")
    cluster_by_structural_key = {structural_key(member): cluster["cluster_id"] for cluster in clusters for member in cluster["member_strata"]}
    selection_pool_mass_by_cluster = Counter()
    for row in launches:
        if row["global_launch_index"] not in holdout_launch_ids:
            selection_pool_mass_by_cluster[cluster_by_structural_key[launch_key(row)]] += int(row["duration_ns"])
    if sum(selection_pool_mass_by_cluster.values()) != selection_pool_ns:
        raise ValueError("selection pool cluster weights do not partition pool")
    mandatory = mandatory_clusters(clusters, selection_pool_mass_by_cluster)
    holdout = scientific_holdout(clusters, mandatory)
    options = ranked_optional(clusters, mandatory | {holdout["cluster_id"]}, selection_pool_mass_by_cluster)
    balanced_count, broad_count = find_tier_indices(options, selection_pool_mass_by_cluster, selection_pool_ns)
    by_id = {cluster["cluster_id"]: cluster for cluster in clusters}
    tiers = {"CORE_MINIMAL": [by_id[ident] for ident in sorted(mandatory)],
             "BALANCED": [by_id[ident] for ident in sorted(mandatory)] + options[:balanced_count],
             "BROAD": [by_id[ident] for ident in sorted(mandatory)] + options[:broad_count]}
    launch_by_index = {row["global_launch_index"]: row for row in launches}
    all_targets = [target for cluster in clusters for target in target_records(cluster, assets, launch_by_index)]
    if any(target["global_launch_index_v2"] in holdout_launch_ids for target in all_targets):
        raise ValueError("statistical holdout launch became a measurement target")
    target_by_cluster: dict[str, list[dict]] = defaultdict(list)
    for target in all_targets:
        target_by_cluster[target["cluster_id"]].append(target)
    # Accepted asset classifications close only if each catalog match has an asset.
    identity_rows = []
    for cluster in clusters:
        for member in cluster["member_strata"]:
            if member["lane_c_asset_status"] in {"REUSABLE_NOW", "REQUIRES_REQUALIFICATION"}:
                match = matched_asset(member, assets, launch_by_index)
                if match is None:
                    raise ValueError("accepted asset join missing")
                asset, matched_launch = match
                identity_rows.append({"phase": member["phase"], "normalized_kernel_family": member["normalized_kernel_family"],
                                      "implementation_match_key": member["implementation_match_key"], "grid": member["grid"], "block": member["block"],
                                      "canonical_exact_function_key": canonical_function_key(member["exact_implementation"]),
                                      "canonical_stratum_key": canonical_stratum_key(member["phase"], member["normalized_kernel_family"],
                                                                                    member["exact_implementation"], member["grid"], member["block"]),
                                      "asset_canonical_stratum_key": canonical_stratum_key(asset["phase"], member["normalized_kernel_family"],
                                                                                           asset["exact_function"], asset["grid"], asset["block"]),
                                      "catalog_exact_function_sha256": hashlib.sha256(member["exact_implementation"].encode()).hexdigest(),
                                      "asset_exact_function_sha256": hashlib.sha256(asset["exact_function"].encode()).hexdigest(),
                                      "asset_candidate": asset["candidate"], "asset_classification": asset["classification"],
                                      "accepted_target": asset["accepted_target"], "payload_sha256": asset["payload_sha256"],
                                      "runner_index_sha256": asset["runner_index_sha256"],
                                      "v2_global_launch_index_from_payload": matched_launch["global_launch_index"],
                                      "v2_decode_step_from_payload": matched_launch["decode_step"] or "N/A",
                                      "join_basis": "PHASE_FAMILY_CANONICAL_KIND_GRID_BLOCK_PLUS_ACCEPTED_PRODUCER_CANDIDATE"})
    if holdout["cluster_id"] in {cluster["cluster_id"] for cluster in tiers["BROAD"]}:
        raise ValueError("scientific holdout entered candidate suite")
    frontier = [summarize(name, tiers[name], all_targets, clusters, selection_pool_ns, selection_pool_mass_by_cluster)
                for name in ("CORE_MINIMAL", "BALANCED", "BROAD")]
    # All optional clusters have one target and one missing trace; descending
    # mass is globally optimal at each optional K under those burden axes.
    for prev, next_ in zip(frontier, frontier[1:]):
        if not (prev["represented_workload_mass_ns"] < next_["represented_workload_mass_ns"] and
                prev["actual_simulator_targets"] < next_["actual_simulator_targets"] and
                prev["missing_sim_trace_targets"] < next_["missing_sim_trace_targets"]):
            raise ValueError("tiers are not nondominated in workload/burden axes")
    output = args.output_dir
    output.mkdir(parents=True, exist_ok=True)
    cluster_rows = [cluster_public(cluster) for cluster in clusters]
    write_tsv(output / "CLUSTER_CATALOG.tsv", cluster_rows, list(cluster_rows[0]))
    write_tsv(output / "DECODE_SHAPE_TRAJECTORY_STEPS.tsv", trajectory_steps, list(trajectory_steps[0]))
    write_tsv(output / "IDENTITY_RECONCILIATION.tsv", identity_rows, list(identity_rows[0]))
    write_tsv(output / "PARETO_FRONTIER.tsv", frontier, list(frontier[0]))
    suite_rows = []
    for name in ("CORE_MINIMAL", "BALANCED", "BROAD"):
        for cluster in tiers[name]:
            for ordinal, target in enumerate(target_by_cluster[cluster["cluster_id"]]):
                suite_rows.append({"suite": name, "cluster_type": cluster["cluster_type"],
                                   "cluster_total_represented_mass_ns": cluster["represented_workload_mass_ns"],
                                   "represented_mass_accounted_ns": cluster["represented_workload_mass_ns"] if ordinal == 0 else 0,
                                   **target})
    write_tsv(output / "SUITE_TARGETS.tsv", suite_rows, list(suite_rows[0]))
    for row in frontier:
        members = [entry for entry in suite_rows if entry["suite"] == row["suite"]]
        if len(members) != row["actual_simulator_targets"]:
            raise ValueError("frontier target burden does not match target manifest")
        if sum(entry["represented_mass_accounted_ns"] for entry in members) != row["represented_workload_mass_ns"]:
            raise ValueError("trajectory represented mass counted more than once")
    optional_rows = [{"rank": i + 1, "cluster_id": cluster["cluster_id"], "phase": cluster["phase"],
                      "family": cluster["normalized_kernel_family"], "grid": ";".join(cluster["member_grids"]),
                      "marginal_represented_ns": cluster["represented_workload_mass_ns"],
                      "marginal_full_s2_share": cluster["represented_workload_mass_ns"] / FULL_S2_NS,
                      "selection_pool_mass_ns_used_for_ranking": selection_pool_mass_by_cluster[cluster["cluster_id"]],
                      "incremental_targets": 1, "incremental_missing_trace_targets": 1,
                      "included_in": "BALANCED+BROAD" if i < balanced_count else ("BROAD" if i < broad_count else "OPTIONAL")}
                     for i, cluster in enumerate(options)]
    write_tsv(output / "MARGINAL_GAIN_ORDER.tsv", optional_rows, list(optional_rows[0]))
    heldout = cluster_public(holdout)
    holdout_target = target_by_cluster[holdout["cluster_id"]][0]
    heldout.update({"holdout_type": "SCIENTIFIC_HOLDOUT_REQUIREMENT", "selection_rule": "IDENTITY_HASH_BEFORE_MASS_RANKING",
                    "reserved_v2_global_launch_index": holdout_target["global_launch_index_v2"],
                    "reserved_decode_step": holdout_target["decode_step_v2"],
                    "reserved_grid": holdout_target["grid"], "reserved_block": holdout_target["block"],
                    "discovery_target_overlap": "NONE_IN_PHASE3_SUITES", "future_context_requirement": "CROSS_CONTEXT_AND_OTHER_MODEL_FAMILY"})
    write_tsv(output / "SCIENTIFIC_HOLDOUT.tsv", [heldout], list(heldout))
    heldout_member = holdout["member_strata"][0]
    holdout_by_step: dict[int, list[dict]] = defaultdict(list)
    for launch in launch_groups[structural_key(heldout_member)]:
        holdout_by_step[int(launch["decode_step"])].append(launch)
    if sorted(holdout_by_step) != list(range(1, 33)):
        raise ValueError("scientific stable-shape trajectory lacks full step evidence")
    holdout_steps = [{"holdout_cluster_id": holdout["cluster_id"], "step": step, "grid": heldout_member["grid"],
                      "block": heldout_member["block"], "recurrence": len(holdout_by_step[step]),
                      "accumulated_duration_ns": sum(int(row["duration_ns"]) for row in holdout_by_step[step])}
                     for step in sorted(holdout_by_step)]
    write_tsv(output / "SCIENTIFIC_HOLDOUT_STEP_EVIDENCE.tsv", holdout_steps, list(holdout_steps[0]))
    receipt = {"stage": "AWMA_AI_TRANSLATION_REPRESENTATIVE_SUITE_REFINEMENT_V3", "status": "RECOMMENDED_CORE_SUITE_FOR_REVIEW",
               "parent_sha": "ac9a6f95922e31c62b8ce0ad79510aaaf1a82758",
               "lane_a_structural_authority_sha": "2e8680dc4cc25e2409c2ef37a15ae8c2fc29ae9f",
               "lane_c_asset_authority_sha": "03924689da9c9691501d93567365c9265178b8a5",
               "input_sha256": {"v2_inventory": V2_SHA, "structural_catalog": CATALOG_SHA, "asset_inventory": ASSET_SHA,
                                "statistical_holdout": digest(args.statistical_holdout)},
               "full_s2_duration_ns": FULL_S2_NS, "phase_duration_ns": PHASE_NS,
               "source_strata": len(strata), "clusters": len(clusters), "trajectory_count": len([c for c in clusters if c["cluster_type"] == "DECODE_SHAPE_TRAJECTORY"]),
               "trajectory_step_rows": len(trajectory_steps), "identity_closed_asset_strata": len(identity_rows),
               "scientific_holdout_cluster_id": holdout["cluster_id"], "statistical_holdout_launch_count": len(holdout_launch_ids),
               "selection_pool_duration_ns": selection_pool_ns, "balanced_optional_count": balanced_count,
               "broad_optional_count": broad_count, "recommended_core_suite": "BALANCED",
               "burden_index_definition": "REUSABLE_NOW=1;REQUIRES_REQUALIFICATION=2;MISSING_SIM_TRACE=4; planning units only",
               "capture_authorized": False, "simulator_run_performed": False}
    (output / "RUN_RECEIPT.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"frontier": frontier, "receipt": receipt}, indent=2))


if __name__ == "__main__":
    main()
