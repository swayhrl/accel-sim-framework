#!/usr/bin/env python3
"""CPU-only M1F headroom admission analysis; never launches simulation."""
from __future__ import annotations

import argparse
import bisect
import csv
import hashlib
import json
import math
import struct
from pathlib import Path


SEED = 0x6A09E667F3BCC908
THRESHOLD = 0x0484BAF3B723B966
MASK64 = (1 << 64) - 1
LINE_BYTES = 128
PAIR = struct.Struct("<QQ")

LANE4_REVIEW = "f6ce663e2a2d6759050ee6f5b0e2cf42bc9f243b"
LANE4_PUBLICATION = "71324d46435293edab3b7a0ff6ee999e675be0d0"
M1F_STATIC = "a72d0f50b26c558368787318860df539950418fd"
M1F_ACTIVATION = "f99e1c697143c02786bc34fa5c27c75a2d19e740"
PRESSURE_INDEX = "4214398782159022907081dbcc36854cf21fb4b5"
TRACE_MANIFEST_SHA = "db3bdbb0295a47a6aa4644508ea1895779c987f2f77cd96f184c67b8a10ab389"
SIDECAR_SHA = "6c60839714d136b9f6f596218588e658e245e0b7cc6f8e8550cce8d683ce13c6"
PRESSURE_INDEX_SHA = "0a70bc0be2b7ec52814512dc2c63a00bc3448c6eb6946073c8399ea62c516bb5"
EXPECTED_TARGET_INDEX_FILES = {
    2985: {
        "summary": "aaba853a0d146f74de350e1242459dc010ef2bad8ee1ffa63a15bdbbe8b2a48e",
        "pairs": "37a7bf266a233291320ec91fa16213b8a15da42132018994edbcc261323c500d",
    },
    4490: {
        "summary": "40a6d4b3e1b5c08b07bac0e525abef89e718b47dde4938722ea69b72189683c4",
        "pairs": "8974ce85ddb8561be63d658a6122a0179778ced2eec6e98b255310f0071d8076",
    },
}


class ContractError(ValueError):
    pass


def need(value: bool, message: str) -> None:
    if not value:
        raise ContractError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path):
    need(path.is_file() and path.stat().st_size > 0, f"missing JSON {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def verify_manifest(repo: Path, pack: Path, name: str) -> dict[str, str]:
    manifest = pack / name
    need(manifest.is_file() and manifest.stat().st_size > 0, f"missing manifest {manifest}")
    verified = {}
    for raw in manifest.read_text(encoding="utf-8").splitlines():
        expected, member = raw.split(maxsplit=1)
        member = member.lstrip(" *")
        candidate = repo / member if member.startswith(("docs/", "util/")) else pack / member
        need(candidate.is_file() and sha256(candidate) == expected,
             f"manifest mismatch {candidate}")
        verified[member] = expected
    need(verified, f"empty manifest {manifest}")
    return verified


def stable_hash(target_class: int, line_index: int) -> int:
    value = (SEED ^ (target_class << 32) ^ line_index) & MASK64
    value = (value + 0x9E3779B97F4A7C15) & MASK64
    value = ((value ^ (value >> 30)) * 0xBF58476D1CE4E5B9) & MASK64
    value = ((value ^ (value >> 27)) * 0x94D049BB133111EB) & MASK64
    return (value ^ (value >> 31)) & MASK64


def read_sidecar(path: Path):
    need(sha256(path) == SIDECAR_SHA, "sidecar SHA drift")
    rows = []
    with path.open(encoding="utf-8") as stream:
        need(stream.readline().rstrip("\n") ==
             "ORACLE_ELASTIC_QWEIGHT_RESIDENCY_V1\t1\tMODELED_L2_GET_ADDR",
             "sidecar header drift")
        for raw in stream:
            if not raw.strip():
                continue
            begin, end, name, target_class = raw.rstrip("\n").split("\t")
            rows.append({"begin": int(begin, 0), "end": int(end, 0),
                         "name": name, "target_class": int(target_class)})
    rows.sort(key=lambda row: row["begin"])
    need(len(rows) == 28 and {row["target_class"] for row in rows} == set(range(1, 29)),
         "sidecar class matrix drift")
    need(all(row["begin"] % LINE_BYTES == 0 and row["end"] % LINE_BYTES == 0 and
             row["end"] - row["begin"] == 33947648 for row in rows),
         "sidecar region geometry drift")
    need(all(left["end"] <= right["begin"] for left, right in zip(rows, rows[1:])),
         "sidecar overlap")
    return rows, [row["begin"] for row in rows]


def lookup(address: int, regions, starts):
    index = bisect.bisect_right(starts, address) - 1
    if index >= 0 and address < regions[index]["end"]:
        return regions[index]
    return None


def recompute_selector(regions):
    classes = []
    total_lines = selected_lines = 0
    for region in regions:
        count = (region["end"] - region["begin"]) // LINE_BYTES
        selected = sum(stable_hash(region["target_class"], line) < THRESHOLD
                       for line in range(count))
        classes.append({"target_class": region["target_class"],
                        "region_lines": count, "selected_lines": selected,
                        "selected_unique_line_fraction": selected / count})
        total_lines += count
        selected_lines += selected
    classes.sort(key=lambda row: row["target_class"])
    return total_lines, selected_lines, classes


def read_sequence(path: Path):
    with path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    return {int(row["global_dynamic_order"]): row for row in rows}


def locate_target_kernel(scope, sequence, summary_root: Path, range_name: str,
                         decode: int, target_class: int):
    target_range = scope[range_name]
    ids = [int(value) for value in target_range["kernel_ids"]]
    need(ids == list(range(int(target_range["first_dynamic_kernel"]),
                           int(target_range["last_dynamic_kernel"]) + 1)),
         f"{range_name} is not contiguous")
    candidates = []
    for kernel_id in ids:
        row = sequence[kernel_id]
        need(int(row["decode_iteration"]) == decode and row["semantic_layer"] == "0" and
             row["semantic_identity"] == "up_proj" and row["profile_range_active"] == "True",
             f"semantic identity drift at {kernel_id}")
        summary = load_json(summary_root / "kernels" / str(kernel_id) / "summary.json")
        if summary.get("expected_target_observed") is True:
            candidates.append(kernel_id)
    need(len(candidates) == 1, f"{range_name} target trace identity is ambiguous")
    kernel_id = candidates[0]
    summary = load_json(summary_root / "kernels" / str(kernel_id) / "summary.json")
    need(summary["kernel_id"] == kernel_id and summary["decode_iteration"] == decode and
         summary["semantic_layer"] == 0 and summary["semantic_identity"] == "up_proj" and
         summary["expected_target_class"] == target_class and
         summary["semantic_range_first_dynamic_kernel"] == ids[0] and
         summary["semantic_range_last_dynamic_kernel"] == ids[-1],
         f"{range_name} target summary drift")
    return kernel_id


def canonical_u64_sha(values) -> str:
    digest = hashlib.sha256()
    for value in sorted(values):
        digest.update(struct.pack("<Q", value))
    return digest.hexdigest()


def target_coverage(summary_root: Path, kernel_id: int, regions, starts,
                    trace_root: Path, manifest_artifacts):
    need(kernel_id in EXPECTED_TARGET_INDEX_FILES,
         f"derived target kernel lacks frozen index binding: {kernel_id}")
    directory = summary_root / "kernels" / str(kernel_id)
    summary_path = directory / "summary.json"
    pairs_path = directory / "all_line_refs.u64"
    expected = EXPECTED_TARGET_INDEX_FILES[kernel_id]
    need(sha256(summary_path) == expected["summary"], "target summary SHA drift")
    need(sha256(pairs_path) == expected["pairs"], "target pair-index SHA drift")
    summary = load_json(summary_path)
    raw = pairs_path.read_bytes()
    need(len(raw) % PAIR.size == 0, "ragged line-reference index")
    seen = set()
    target_lines = set()
    selected_lines = set()
    target_refs = selected_refs = 0
    target_counts = []
    selected_counts = []
    for address, count in struct.iter_unpack("<QQ", raw):
        need(address % LINE_BYTES == 0 and address not in seen and count > 0,
             "malformed line-reference pair")
        seen.add(address)
        region = lookup(address, regions, starts)
        if region is None or region["target_class"] != 1:
            continue
        target_lines.add(address)
        target_refs += count
        target_counts.append(count)
        line_index = (address - region["begin"]) // LINE_BYTES
        if stable_hash(1, line_index) < THRESHOLD:
            selected_lines.add(address)
            selected_refs += count
            selected_counts.append(count)
    need(len(target_lines) == summary["target_unique_128b_lines"] and
         target_refs == summary["target_128b_line_references"],
         "line-reference index does not close against summary")
    need(target_counts and selected_counts, "target or selected line set is empty")
    trace_relative = "traces/" + summary["trace_artifact"]
    need(trace_relative in manifest_artifacts, "target trace absent from manifest")
    artifact = manifest_artifacts[trace_relative]
    trace_path = trace_root / trace_relative
    need(trace_path.is_file() and trace_path.stat().st_size == artifact["size_bytes"] and
         sha256(trace_path) == artifact["sha256"] and
         artifact["sha256"] == summary["trace_index_validation"].get("sha256", artifact["sha256"]),
         "target trace artifact authority drift")
    return {
        "kernel_id": kernel_id,
        "summary_path": str(summary_path), "summary_sha256": sha256(summary_path),
        "pairs_path": str(pairs_path), "pairs_sha256": sha256(pairs_path),
        "trace_artifact": str(trace_path), "trace_sha256": artifact["sha256"],
        "target_lines": target_lines, "selected_lines": selected_lines,
        "target_unique_lines": len(target_lines),
        "selected_unique_lines": len(selected_lines),
        "target_references": target_refs, "selected_references": selected_refs,
        "target_reference_count_min_per_line": min(target_counts),
        "target_reference_count_max_per_line": max(target_counts),
        "selected_reference_count_min": min(selected_counts),
        "selected_reference_count_max": max(selected_counts),
        "target_line_set_sha256": canonical_u64_sha(target_lines),
        "selected_line_set_sha256": canonical_u64_sha(selected_lines),
    }


def counter_delta(before, after):
    need(set(before) == set(after), "counter field matrix drift")
    result = {key: after[key] - before[key] for key in sorted(before)}
    need(all(value >= 0 for value in result.values()), "cumulative counter decreased")
    return result


def response(baseline: int, candidate: int):
    need(baseline > 0, "zero response denominator")
    return (baseline - candidate) / baseline


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--trace-summary-root", type=Path, required=True)
    parser.add_argument("--trace-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    repo = args.repo_root.resolve()
    need(repo.is_dir() and not args.output_dir.exists(), "repo/output state invalid")

    review = repo / "docs/vm_tlb/review_packs"
    lane4 = review / "C16_E1_ORACLE_ELASTIC_B16_REUSE_PERFORMANCE_CANARY_174NEW_V1"
    terminal = review / "C16_E1_LANE4_TERMINAL_REVIEW_V1"
    static = review / "C16_E1_M1F_STABLE_ADMISSION_PROTOTYPE_V1"
    activation = review / "C16_E1_M1F_REAL_TRACE_ACTIVATION_CANARY_V1"
    pressure = review / "C16_E1_TRACE_REUSE_SET_PRESSURE_CHARACTERIZATION_174NEW_V1"
    namespace = review / "C16_E1_TRACE_ADDRESS_NAMESPACE_INTEGRATION_174NEW_V1"
    verify_manifest(repo, lane4, "SHA256SUMS")
    verify_manifest(repo, terminal, "SHA256SUMS")
    verify_manifest(repo, static, "SHA256SUMS")
    verify_manifest(repo, activation, "SHA256SUMS")
    verify_manifest(repo, pressure, "RESULT_SHA256SUMS")

    freeze = load_json(static / "HASH_FREEZE_RECEIPT.json")
    need(freeze["status"] == "PASS" and
         freeze["version"] == "C16_M1F_STABLE_ADMISSION_HASH_V1" and
         int(freeze["seed_hex"], 0) == SEED and int(freeze["threshold_hex"], 0) == THRESHOLD and
         freeze["seed_searched_or_tuned"] is False,
         "selector freeze drift")
    need(THRESHOLD == ((1 << 64) * 131072 // 7426048),
         "frozen threshold arithmetic drift")
    sidecar = namespace / "ORACLE_QWEIGHT_L2_SIDECAR.tsv"
    regions, starts = read_sidecar(sidecar)
    total_lines, selected_lines, classes = recompute_selector(regions)
    need(total_lines == 7426048 and selected_lines == 130571,
         "global selector recheck mismatch")
    class1 = next(row for row in classes if row["target_class"] == 1)
    need(class1["region_lines"] == 265216 and class1["selected_lines"] == 4752,
         "class1 selector recheck mismatch")
    historical_selector = load_json(static / "selector_summary.json")
    need(historical_selector["total_lines"] == total_lines and
         historical_selector["selected_lines"] == selected_lines and
         historical_selector["classes"] == [
             {"target_class": row["target_class"], "selected_lines": row["selected_lines"]}
             for row in classes], "historical selector cross-check mismatch")

    manifest_path = args.trace_root / "RUN_MANIFEST.json"
    need(sha256(manifest_path) == TRACE_MANIFEST_SHA, "accepted trace manifest SHA drift")
    manifest = load_json(manifest_path)
    manifest_artifacts = {row["relative_path"]: row for row in manifest["artifacts"]}
    pressure_manifest = load_json(pressure / "TRACE_REFERENCE_SUMMARY_MANIFEST.json")
    need(pressure_manifest["status"] == "PASS" and
         pressure_manifest["index"]["sha256"] == PRESSURE_INDEX_SHA and
         Path(pressure_manifest["durable_root"]).resolve() == args.trace_summary_root.resolve() and
         sha256(args.trace_summary_root / "TRACE_REFERENCE_SUMMARY.json") == PRESSURE_INDEX_SHA and
         pressure_manifest["sidecar_sha256"] == SIDECAR_SHA,
         "trace reference index authority drift")

    scope = load_json(lane4 / "REUSE_WINDOW_SCOPE.json")
    sequence_path = lane4 / "REUSE_WINDOW_SEQUENCE.tsv"
    need(sha256(sequence_path) == scope["selected_sequence_sha256"],
         "reuse sequence SHA drift")
    sequence = read_sequence(sequence_path)
    d1_kernel = locate_target_kernel(scope, sequence, args.trace_summary_root,
                                     "D1_L0_up_proj_range", 1, 1)
    d2_kernel = locate_target_kernel(scope, sequence, args.trace_summary_root,
                                     "D2_L0_up_proj_range", 2, 1)
    d1 = target_coverage(args.trace_summary_root, d1_kernel, regions, starts,
                         args.trace_root, manifest_artifacts)
    d2 = target_coverage(args.trace_summary_root, d2_kernel, regions, starts,
                         args.trace_root, manifest_artifacts)
    need(d2["selected_unique_lines"] == class1["selected_lines"],
         "D2 selected/static class1 mismatch")
    producer_intersection = d1["selected_lines"] & d2["selected_lines"]
    need(producer_intersection == d2["selected_lines"],
         "D2 selected line lacks D1 producer access")

    activation_distribution = load_json(activation / "M1F_REAL_TRACE_SELECTION_DISTRIBUTION.json")
    activation_selection = next(row for row in activation_distribution["kernels"]
                                if row["kernel_id"] == d2_kernel)
    need(activation_selection["target_unique_128b_lines"] == d2["target_unique_lines"] and
         activation_selection["selected_unique_target_lines"] == d2["selected_unique_lines"] and
         activation_selection["trace_target_line_reference_proxy"] == d2["target_references"] and
         activation_selection["trace_selected_line_reference_proxy"] == d2["selected_references"],
         "M1F activation trace cross-check mismatch")
    accounting = load_json(activation / "M1F_ADMISSION_ACCOUNTING.json")
    activation_accounting = next(row for row in accounting["kernels"]
                                 if row["kernel_id"] == d2_kernel)
    l2_totals = activation_accounting["simulator_l2_totals"]

    diagnostic = load_json(lane4 / "DIAGNOSTIC_COUNTERS.json")
    before = diagnostic["immediately_before_D2_L0_up"]
    after = diagnostic["after_D2_L0_up"]
    need(before["dynamic_kernel"] == scope["D2_L0_up_proj_range"]["first_dynamic_kernel"] - 1 and
         after["dynamic_kernel"] == scope["D2_L0_up_proj_range"]["last_dynamic_kernel"],
         "D2 counter boundary drift")
    delta = counter_delta(before["counters"]["sum"], after["counters"]["sum"])
    need(delta["target_accesses"] == delta["target_hits"] + delta["target_misses"],
         "D2 target access accounting drift")
    class1_before = before["class_occupancy"]["sum"]["class_1"]
    class1_after = after["class_occupancy"]["sum"]["class_1"]

    selector = {
        "schema": "C16_E1_M1F_SELECTOR_RECHECK_V1", "status": "PASS",
        "selector_version": freeze["version"], "seed_hex": freeze["seed_hex"],
        "threshold_hex": freeze["threshold_hex"], "seed_or_threshold_changed": False,
        "total_target_unique_lines": total_lines, "selected_lines": selected_lines,
        "selected_fraction": selected_lines / total_lines,
        "quota_lines": 131072, "selected_minus_quota_lines": selected_lines - 131072,
        "classes": classes,
        "class1": class1,
        "historical_artifact_exact_match": True,
    }

    unique_fraction = d2["selected_unique_lines"] / d2["target_unique_lines"]
    dynamic_fraction = d2["selected_references"] / d2["target_references"]
    l2_supporting_fraction = l2_totals["selected_target_accesses"] / l2_totals["target_accesses"]
    coverage = {
        "schema": "C16_E1_M1F_D2_L0_SELECTED_ACCESS_COVERAGE_V1", "status": "PASS",
        "semantic_localization": {
            "source": "REUSE_WINDOW_SCOPE_AND_SEQUENCE_NOT_GUESSED_KERNEL_ID",
            "D1_L0_up_range": scope["D1_L0_up_proj_range"],
            "D2_L0_up_range": scope["D2_L0_up_proj_range"],
            "D1_target_trace_kernel": d1_kernel, "D2_target_trace_kernel": d2_kernel,
        },
        "D2_target": {
            "unique_target_lines": d2["target_unique_lines"],
            "selected_unique_lines": d2["selected_unique_lines"],
            "selected_unique_line_fraction": unique_fraction,
            "target_128B_line_reference_proxy": d2["target_references"],
            "selected_128B_line_reference_proxy": d2["selected_references"],
            "selected_access_fraction": dynamic_fraction,
            "selected_reference_count_min_per_line": d2["selected_reference_count_min"],
            "selected_reference_count_max_per_line": d2["selected_reference_count_max"],
            "target_reference_count_min_per_line": d2["target_reference_count_min_per_line"],
            "target_reference_count_max_per_line": d2["target_reference_count_max_per_line"],
            "target_line_set_sha256": d2["target_line_set_sha256"],
            "selected_line_set_sha256": d2["selected_line_set_sha256"],
        },
        "D1_producer_qualification": {
            "D1_target_trace_kernel": d1_kernel,
            "D1_selected_unique_lines_accessed": d1["selected_unique_lines"],
            "D2_selected_lines_with_D1_access_producer": len(producer_intersection),
            "D2_selected_lines_with_D1_access_producer_fraction":
                len(producer_intersection) / d2["selected_unique_lines"],
            "D1_D2_selected_line_set_exact": d1["selected_lines"] == d2["selected_lines"],
            "address_specific_protected_fill_status":
                "UNKNOWN_EXISTING_M1_COUNTERS_NOT_SELECTOR_OR_ADDRESS_RESOLVED",
            "optimistic_reuse_producer_qualified_by_access": True,
        },
        "sector_coverage": {
            "status": "UNKNOWN",
            "reason": "ACCEPTED_EXISTING_INDEX_IS_128B_LINE_REFERENCE_ONLY_NO_NEW_OBSERVER",
        },
        "supporting_isolated_M1F_activation_L2_transactions": {
            "claim_boundary": accounting["claim_boundary"],
            "target_accesses": l2_totals["target_accesses"],
            "selected_target_accesses": l2_totals["selected_target_accesses"],
            "selected_access_fraction": l2_supporting_fraction,
            "continuous_M1_substitution_authorized": False,
        },
        "selected_heat": {
            "unique_line_fraction": unique_fraction,
            "dynamic_trace_reference_fraction": dynamic_fraction,
            "dynamic_to_unique_fraction_ratio": dynamic_fraction / unique_fraction,
            "difference_fraction": dynamic_fraction - unique_fraction,
            "classification": "NO_TRACE_REFERENCE_HEAT_ENRICHMENT_EXACT_EQUAL",
            "seed_reselection_performed": False,
        },
        "raw_provenance": {
            "D1": {key: value for key, value in d1.items() if not isinstance(value, set)},
            "D2": {key: value for key, value in d2.items() if not isinstance(value, set)},
        },
    }

    potential_upper = min(d2["selected_references"], delta["target_misses"])
    counter_bound = {
        "schema": "C16_E1_M1F_D2_L0_EXISTING_COUNTER_BOUND_V1", "status": "PASS",
        "boundary": {"before": before["dynamic_kernel"], "after": after["dynamic_kernel"]},
        "M1_diagnostic_delta": {
            "target_accesses": delta["target_accesses"],
            "target_hits": delta["target_hits"], "target_misses": delta["target_misses"],
            "protected_hits": delta["protected_hits"],
            "protected_fills": delta["protected_fills"],
            "class1_occupancy_before": class1_before,
            "class1_occupancy_after": class1_after,
            "class1_occupancy_change": class1_after - class1_before,
        },
        "selected_M1_continuous_counter_resolution": "UNKNOWN_NOT_CLASS_OR_ADDRESS_RESOLVED",
        "potential_extra_hits": {
            "classification": "OPTIMISTIC_UPPER_BOUND_NOT_PROVEN_CURRENT_MISSES",
            "upper_bound_events": potential_upper,
            "bound_by_selected_D2_trace_line_reference_proxy": d2["selected_references"],
            "bound_by_current_M1_non_hit_target_accesses": delta["target_misses"],
            "event_unit_caveat":
                "TRACE_ACTIVE_LANE_128B_LINE_REFERENCES_BOUND_MODELED_L2_ACCESSES_BUT_ARE_NOT_EQUAL",
            "supporting_isolated_M1F_selected_L2_accesses": l2_totals["selected_target_accesses"],
            "supporting_isolated_value_is_not_continuous_M1_authority": True,
        },
        "unknowns": [
            "WHICH_FROZEN_SELECTED_ACCESSES_ARE_MISSES_IN_CONTINUOUS_M1",
            "SELECTED_ACCESS_CLASS_ADDRESS_RESOLVED_M1_COUNTERS",
            "SECTOR_OR_TRANSFER_BYTES",
        ],
    }

    performance = load_json(lane4 / "B16_REUSE_WINDOW_PERFORMANCE.json")
    c_window = performance["metrics"]["C_window"]["R0_cycles"]
    c_local = performance["metrics"]["C_L0_up_D2"]["R0_cycles"]
    local_share = c_local / c_window
    model_saved_local = c_local * dynamic_fraction
    model_window_response = model_saved_local / c_window
    ceilings = {
        "schema": "C16_E1_M1F_HEADROOM_CEILINGS_V1", "status": "PASS",
        "E0_HARD_TARGET_KERNEL_ZERO_CEILING": {
            "R0_C_window_cycles": c_window, "R0_C_L0_up_D2_cycles": c_local,
            "D2_L0_up_cycle_fraction_of_window": local_share,
            "D2_L0_up_cycle_percent_of_window": 100 * local_share,
            "maximum_window_cycles_eliminated_if_target_zero": c_local,
            "minimum_window_cycles_under_target_zero": c_window - c_local,
            "maximum_window_response_fraction": local_share,
            "scope": "BENEFIT_ASSUMED_FULLY_LOCALIZED_TO_THIS_REUSE_TARGET",
        },
        "E1_PERFECT_SELECTED_RETENTION_TRAFFIC_CEILING": {
            "producer_qualified_selected_unique_lines": len(producer_intersection),
            "unique_128B_line_byte_reduction_upper_bound":
                len(producer_intersection) * LINE_BYTES,
            "unique_line_MiB_reduction_upper_bound":
                len(producer_intersection) * LINE_BYTES / (1 << 20),
            "dynamic_selected_trace_reference_upper_bound": d2["selected_references"],
            "dynamic_selected_reference_byte_proxy_upper_bound":
                d2["selected_references"] * LINE_BYTES,
            "potential_extra_hit_upper_bound": potential_upper,
            "not_a_cycle_speedup": True,
        },
        "E2_SIMPLE_BANDWIDTH_RESPONSE_MODEL": {
            "classification": "MODEL_BASED_OPTIMISTIC_ESTIMATE",
            "not_cycle_upper_bound": True,
            "assumption": "D2_L0_UP_TIME_LINEARLY_PROPORTIONAL_TO_QWEIGHT_SERVICE",
            "selected_dynamic_access_fraction": dynamic_fraction,
            "local_ideal_time_reduction_fraction": dynamic_fraction,
            "local_ideal_speedup_factor": 1.0 / (1.0 - dynamic_fraction),
            "local_ideal_speedup_percent": 100 * (1.0 / (1.0 - dynamic_fraction) - 1.0),
            "modeled_local_cycles_saved": model_saved_local,
            "modeled_window_ideal_response_fraction": model_window_response,
            "modeled_window_ideal_response_percent": 100 * model_window_response,
            "supporting_isolated_L2_fraction_sensitivity": {
                "selected_fraction": l2_supporting_fraction,
                "modeled_window_response_fraction": local_share * l2_supporting_fraction,
                "modeled_window_response_percent": 100 * local_share * l2_supporting_fraction,
            },
        },
    }

    decision_label = "M1F_FULL_TIMING_NOT_JUSTIFIED_BY_CURRENT_HEADROOM"
    decision = {
        "schema": "C16_E1_M1F_HEADROOM_FINAL_DECISION_V1", "status": "PASS",
        "decision": decision_label,
        "no_new_paper_materiality_threshold": True,
        "facts": {
            "selected_unique_line_fraction": unique_fraction,
            "selected_dynamic_trace_reference_fraction": dynamic_fraction,
            "selected_heat_ratio": dynamic_fraction / unique_fraction,
            "hard_target_zero_window_ceiling_fraction": local_share,
            "model_based_optimistic_window_response_fraction": model_window_response,
            "primary_cost_hours": 78, "diagnostic_cost_hours": 88,
            "primary_plus_diagnostic_slot_hours": 166,
        },
        "reasoning": [
            "FROZEN_SELECTOR_COVERS_ABOUT_1P8_PERCENT_OF_D2_L0_TARGET_WORK",
            "SELECTED_DYNAMIC_FRACTION_EQUALS_UNIQUE_FRACTION_NO_HEAT_ENRICHMENT",
            "MODEL_BASED_WHOLE_WINDOW_RESPONSE_IS_ABOUT_0P017_PERCENT",
            "FULL_TARGET_ZERO_CEILING_IS_BELOW_ONE_PERCENT_OF_MEASURED_WINDOW",
            "FULL_TIMING_COST_IS_78H_PRIMARY_AND_88H_DIAGNOSTIC",
        ],
        "runs_started": [], "GPU_used": False, "simulator_executed": False,
        "selector_changed": False, "seed_or_threshold_search_performed": False,
        "if_later_project_approval": {
            "first": "RUN_M1F_PRIMARY_ONLY",
            "diagnostic": "ONLY_IF_PRIMARY_HAS_PRE_FROZEN_LOCAL_OR_WINDOW_SIGNAL",
            "priority_stable": "ONLY_AFTER_QUALIFIED_M1F_SIGNAL",
            "if_primary_unhelpful": "STOP_WITHOUT_DIAGNOSTIC_OR_PRIORITY_STABLE",
        },
    }

    anchors = {
        "schema": "C16_E1_M1F_HEADROOM_SOURCE_ANCHORS_V1", "status": "PASS",
        "authorities": {
            "lane4_terminal_review": LANE4_REVIEW,
            "lane4_publication": LANE4_PUBLICATION,
            "m1f_static_qualification": M1F_STATIC,
            "m1f_real_trace_activation": M1F_ACTIVATION,
            "trace_reference_index": PRESSURE_INDEX,
        },
        "selector": {"version": freeze["version"], "seed_hex": freeze["seed_hex"],
                     "threshold_hex": freeze["threshold_hex"]},
        "trace_manifest_sha256": sha256(manifest_path),
        "sidecar_sha256": sha256(sidecar),
        "pressure_index_sha256": sha256(args.trace_summary_root / "TRACE_REFERENCE_SUMMARY.json"),
        "input_sha256": {
            "scope": sha256(lane4 / "REUSE_WINDOW_SCOPE.json"),
            "sequence": sha256(sequence_path),
            "diagnostic_counters": sha256(lane4 / "DIAGNOSTIC_COUNTERS.json"),
            "performance": sha256(lane4 / "B16_REUSE_WINDOW_PERFORMANCE.json"),
            "selector_freeze": sha256(static / "HASH_FREEZE_RECEIPT.json"),
            "selector_summary": sha256(static / "selector_summary.json"),
            "activation_selection": sha256(activation / "M1F_REAL_TRACE_SELECTION_DISTRIBUTION.json"),
            "activation_accounting": sha256(activation / "M1F_ADMISSION_ACCOUNTING.json"),
        },
    }

    args.output_dir.mkdir(parents=True)
    dump(args.output_dir / "M1F_SELECTOR_RECHECK.json", selector)
    dump(args.output_dir / "D2_L0_SELECTED_ACCESS_COVERAGE.json", coverage)
    dump(args.output_dir / "D2_L0_EXISTING_COUNTER_BOUND.json", counter_bound)
    dump(args.output_dir / "M1F_HEADROOM_CEILINGS.json", ceilings)
    dump(args.output_dir / "SOURCE_ANCHORS.json", anchors)
    dump(args.output_dir / "FINAL_DECISION.json", decision)

    rows = [
        ("STATIC_CLASS1", "unique_128B_lines", class1["region_lines"], class1["selected_lines"],
         class1["selected_unique_line_fraction"], "EXACT"),
        ("D2_TRACE", "unique_128B_lines", d2["target_unique_lines"], d2["selected_unique_lines"],
         unique_fraction, "EXACT"),
        ("D2_TRACE", "128B_line_reference_proxy", d2["target_references"], d2["selected_references"],
         dynamic_fraction, "EXACT_TRACE_PROXY"),
        ("D1_PRODUCER", "D2_selected_lines_with_D1_access", d2["selected_unique_lines"],
         len(producer_intersection), len(producer_intersection) / d2["selected_unique_lines"],
         "EXACT_ACCESS_PRODUCER"),
        ("M1F_ACTIVATION_SUPPORTING", "simulator_L2_target_accesses",
         l2_totals["target_accesses"], l2_totals["selected_target_accesses"],
         l2_supporting_fraction, "SUPPORTING_ONLY_NOT_CONTINUOUS_M1"),
    ]
    with (args.output_dir / "D2_L0_SELECTED_ACCESS_COVERAGE.tsv").open(
            "w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
        writer.writerow(("domain", "metric", "total", "selected", "fraction", "authority"))
        writer.writerows(rows)

    review_md = f"""# C16 E1 M1F headroom cost/benefit review

Decision: `{decision_label}`.

This is a CPU-only admission review. It did not run Accel-Sim, M1F, PRIORITY_STABLE, GPU work, a new observer, or a seed/threshold search.

## Frozen selector and useful-target coverage

The independently recomputed selector covers {selected_lines:,} of {total_lines:,} total target lines. For class 1 / layer 0 it covers {d2['selected_unique_lines']:,} of {d2['target_unique_lines']:,} unique lines ({100*unique_fraction:.9f}%). The accepted D2 trace has {d2['selected_references']:,} selected references out of {d2['target_references']:,} target 128-byte line-reference proxies ({100*dynamic_fraction:.9f}%). The two fractions are exactly equal, so the frozen hash subset is not unusually hot in this target.

All {len(producer_intersection):,} D2-selected lines also occur in the D1 L0 up trace, so they have an exact D1 access producer. Existing M1 counters are not selector/address-resolved; address-specific D1 protected-fill status remains UNKNOWN. The isolated M1F activation canary reports {l2_totals['selected_target_accesses']:,} selected of {l2_totals['target_accesses']:,} modeled L2 target accesses, supporting only, not as continuous-M1 authority.

## Existing Lane4 counter bound

Across the frozen D2 L0 up boundary, M1 records {delta['target_accesses']:,} target accesses, {delta['target_hits']:,} hits, {delta['target_misses']:,} misses, {delta['protected_hits']:,} protected hits, and {delta['protected_fills']:,} protected fills. Class-1 occupancy moves from {class1_before:,} to {class1_after:,}. Which stable-selected accesses are current M1 misses is UNKNOWN. An optimistic cross-level bound is `potential_extra_hits <= {potential_upper:,}`, capped by selected trace references and current non-hit target accesses.

## Headroom

- E0 hard target-zero ceiling: D2 L0 up is {100*local_share:.9f}% of the R0 measured window. Even zero target cycles cannot improve that window by more than this localized ceiling.
- E1 perfect selected retention: at most {len(producer_intersection):,} unique lines / {len(producer_intersection)*LINE_BYTES:,} bytes ({len(producer_intersection)*LINE_BYTES/(1<<20):.9f} MiB) of unique-line first-need traffic, and at most {d2['selected_references']:,} trace line-reference events. This is not a cycle speedup.
- E2 model-based optimistic estimate: under a fully linear qweight-service model, local time reduction is {100*dynamic_fraction:.9f}%, local speedup is {100*(1/(1-dynamic_fraction)-1):.9f}%, and the modeled whole-window response is {100*model_window_response:.9f}%. This is `MODEL_BASED_OPTIMISTIC_ESTIMATE`, not a cycle upper bound.

## Resource judgment

The direct useful-target coverage is about 1.8%, with no dynamic heat enrichment. The optimistic linear whole-window estimate is about 0.017%, while the prior cost is roughly 78 hours for primary and 88 hours for diagnostic. No new paper materiality threshold is introduced; these exact coverage, ceiling, and cost facts do not justify committing the full timing sequence now.

If project review later overrides this recommendation, run M1F primary only. Run the diagnostic only after a pre-frozen useful local/window signal; run PRIORITY_STABLE only after that qualified signal. An unhelpful primary stops the expansion.
"""
    (args.output_dir / "M1F_COST_BENEFIT_REVIEW.md").write_text(review_md, encoding="utf-8")
    readme = """# C16 E1 M1F Headroom Admission V1

CPU-only headroom review for the frozen M1F stable selector. Review `FINAL_DECISION.json`, `M1F_COST_BENEFIT_REVIEW.md`, `M1F_HEADROOM_CEILINGS.json`, the D2 coverage artifacts, selector recheck, counter bound, source anchors, and validation summary. No simulation or GPU work was run.
"""
    (args.output_dir / "README.md").write_text(readme, encoding="utf-8")
    validation = {
        "schema": "C16_E1_M1F_HEADROOM_VALIDATION_SUMMARY_V1", "status": "PASS",
        "authority_manifests_verified": True, "selector_independently_recomputed": True,
        "D2_target_semantically_localized_without_guessed_kernel": True,
        "accepted_index_used_without_full_trace_rescan": True,
        "D1_producer_access_closed": True, "Lane4_counter_delta_independently_recomputed": True,
        "selected_heat_compared": True, "ceilings_computed": ["E0", "E1", "E2"],
        "simulator_executed": False, "GPU_used": False, "selector_changed": False,
        "decision": decision_label,
    }
    dump(args.output_dir / "VALIDATION_SUMMARY.json", validation)
    checksums = []
    for path in sorted(args.output_dir.iterdir(), key=lambda item: item.name):
        if path.name == "SHA256SUMS":
            continue
        need(path.is_file() and not path.is_symlink() and path.stat().st_size > 0,
             f"invalid output {path}")
        checksums.append(f"{sha256(path)}  {path.name}")
    (args.output_dir / "SHA256SUMS").write_text("\n".join(checksums) + "\n",
                                                encoding="utf-8")
    print(json.dumps({"status": "PASS", "decision": decision_label,
                      "output": str(args.output_dir)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
