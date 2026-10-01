#!/usr/bin/env python3
"""Independent Stage A Tier0 raw consumer entry point (CPU-only).

This script deliberately does not import or call producer postprocessing. It
consumes only a frozen producer pack locator, its 164 durable byte copies, and
the separately frozen final contract/accepted input receipts.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from adapter import (
    read_contract_tsv, recompute_native_request_samples,
    verify_frozen_token_bindings, verify_point_identity,
)
from correctness import compare_raw_graph_tokens
from core import headroom_gate
from crosscheck import compare_handoff_boundaries, compare_headroom_summary, compare_launch_gaps, compare_native_summary
from intervals import handoff_chronology_summary, parse_observed_intervals
from raw_authority import POINT_ALLOWLIST, load_final_contract, load_producer_raw_authority


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CONTRACT_PACK = REPO / "docs/vm_tlb/review_packs/C16_STAGEA_DENSE_FIRST_TIER0_CONTRACT_FINALIZATION_174NEW_V1"
ASSET_PACK = REPO / "docs/vm_tlb/review_packs/C16_MEASUREMENT_CAMPAIGN_STAGEA_ASSET_INPUT_CLOSURE_174NEW_V1"
RESULT_SCHEMA_PATH = CONTRACT_PACK / "RESULT_SCHEMA.json"


def raw_table(artifact_paths: dict[str, str], schema: dict, name: str, *, optional: bool = False) -> list[dict[str, str]]:
    path = artifact_paths.get(name)
    if path is None:
        if optional:
            return []
        raise ValueError(f"missing required raw artifact: {name}")
    rule = schema["row_rules"][name]
    return read_contract_tsv(path, rule["columns"], rule["key"])


def complete_point_candidates(correctness_rows: list[dict[str, str]], native_rows: list[dict[str, str]], capture_rows: list[dict[str, str]], contract: dict) -> set[str]:
    """Structural eligibility only; independent detailed gates follow."""
    by_correctness = {}
    for row in correctness_rows:
        by_correctness.setdefault(row["point_id"], {})[row["arm"]] = row
    native_matrix = {}
    for row in native_rows:
        if row["sample_role"] == "MEASURED":
            native_matrix.setdefault(row["point_id"], {}).setdefault(row["arm"], set()).add(row["sample_index"])
    captures = {}
    for row in capture_rows:
        if row["arm"] == "GRAPH_OFF_OBSERVED" and row["structural_status"] == "PASS":
            captures.setdefault(row["point_id"], 0)
            captures[row["point_id"]] += 1
    selected = set()
    for point in contract["point_allowlist_in_order"]:
        modes = by_correctness.get(point, {})
        if set(modes) != {"GRAPH_ON_NATIVE", "GRAPH_OFF_NATIVE", "GRAPH_OFF_OBSERVED"}:
            continue
        if any(row["status"] != "PASS" for row in modes.values()):
            continue
        if native_matrix.get(point, {}).get("GRAPH_ON_NATIVE") != {"0", "1", "2"}:
            continue
        if native_matrix.get(point, {}).get("GRAPH_OFF_NATIVE") != {"0", "1", "2"}:
            continue
        if captures.get(point) != 1:
            continue
        selected.add(point)
    return selected


def recompute_from_raw(producer_pack: Path) -> dict:
    contract = load_final_contract(CONTRACT_PACK)
    schema = json.loads(RESULT_SCHEMA_PATH.read_text(encoding="utf-8"))
    raw = load_producer_raw_authority(producer_pack, contract)
    paths = raw["artifact_paths"]
    binding = read_contract_tsv(CONTRACT_PACK / "POINT_TOKEN_BINDINGS.tsv",
        ["point_id", "model_key", "source_text_id", "source_utf8_sha256", "tokenizer_revision",
         "prompt_token_count", "token_ids_sha256", "token_id_file_sha256", "token_ids_relative_path"],
        ["point_id", "source_text_id"])
    receipts = read_contract_tsv(ASSET_PACK / "TOKENIZATION_RECEIPTS.tsv",
        ["model_key", "source_text_id", "source_utf8_sha256", "tokenizer_revision",
         "prompt_token_count", "token_ids_sha256", "token_id_file_sha256", "token_ids_relative_path"],
        ["model_key", "source_text_id"])
    bindings_audit = verify_frozen_token_bindings(binding, receipts, contract)
    identity = raw_table(paths, schema, "POINT_IDENTITY.tsv")
    native = raw_table(paths, schema, "NATIVE_REQUEST_SAMPLES.tsv")
    correctness = raw_table(paths, schema, "GRAPH_MODE_CORRECTNESS.tsv")
    capture = raw_table(paths, schema, "NSYS_CAPTURE_INDEX.tsv")
    semantic = raw_table(paths, schema, "SEMANTIC_INTERVALS.tsv")
    cuda = raw_table(paths, schema, "CUDA_INTERVALS.tsv")
    token_comparisons = []
    for point in contract["point_allowlist_in_order"]:
        on_name = f"{point}/{point}_GRAPH_ON_NATIVE.json"
        off_name = f"{point}/{point}_GRAPH_OFF_NATIVE.json"
        if on_name in paths and off_name in paths:
            token_comparisons.extend(compare_raw_graph_tokens(paths[on_name], paths[off_name], point))
    complete = complete_point_candidates(correctness, native, capture, contract)
    if raw["decision"]["status"] == "STAGEA_TIER0_PRODUCER_COMPLETE" and complete != set(contract["point_allowlist_in_order"]):
        raise ValueError("producer COMPLETE but a required point fails structural gates")
    identity_audit = verify_point_identity([r for r in identity if r["point_id"] in complete], binding, contract, complete)
    native_recompute = recompute_native_request_samples([r for r in native if r["point_id"] in complete], complete, contract)
    interval_recompute = {}
    for point in sorted(complete):
        captures = [r for r in capture if r["point_id"] == point]
        if len(captures) != 1:
            raise ValueError("capture cardinality drift")
        request = captures[0]["target_request_id"]
        interval_recompute[point] = parse_observed_intervals(semantic, cuda, point, request)
    headroom = []
    for point, parsed in sorted(interval_recompute.items()):
        for row in parsed["all_phase_family_unions"]:
            screen = headroom_gate(row["cuda_union_ns"], row["parent_full_request_cuda_union_ns"])
            headroom.append({
                "point_id": point, "phase": row["phase"], "family": row["family"],
                "candidate_graph_off_union_ns": row["cuda_union_ns"],
                "parent_graph_off_cuda_union_ns": row["parent_full_request_cuda_union_ns"],
                "screen_scope": "DQ1_ELIGIBLE" if point in {"MP01", "MP02"} else "REPRESENTATION_CONTROL_SUPPORTING_ONLY",
                **screen,
            })
    # The producer summary is opened only *after* independent recomputation.
    producer_native_summary = raw_table(paths, schema, "NATIVE_REQUEST_SUMMARY.tsv")
    native_crosscheck = compare_native_summary(native_recompute, producer_native_summary, complete)
    producer_headroom_summary = raw_table(paths, schema, "POINT_HEADROOM_SCREEN.tsv")
    headroom_crosscheck = compare_headroom_summary(headroom, producer_headroom_summary, complete)
    producer_launch_gaps = raw_table(paths, schema, "LAUNCH_GAPS.tsv")
    launch_gap_crosscheck = compare_launch_gaps(interval_recompute, producer_launch_gaps, complete)
    producer_handoffs = read_contract_tsv(paths["PRODUCER_CONSUMER_CHRONOLOGY.tsv"],
        ["point_id", "producer_ordinal", "consumer_ordinal", "boundary_gap_ns", "boundary_gap_parent_cuda_union_fraction"],
        ["point_id", "producer_ordinal", "consumer_ordinal"])
    handoff_crosscheck = compare_handoff_boundaries(interval_recompute, producer_handoffs, complete)
    return {
        "producer_status": raw["decision"]["status"],
        "run_id": raw["run_id"],
        "raw_index_sha256": raw["raw_index_sha256"],
        "raw_payload_manifest_sha256": raw["raw_payload_manifest_sha256"],
        "review_payload_manifest_sha256": raw["review_payload_manifest_sha256"],
        "raw_audit": raw["raw_audit"],
        "binding_audit": bindings_audit,
        "identity_audit": identity_audit,
        "complete_points": sorted(complete),
        "raw_token_comparisons": token_comparisons,
        "native_recompute": native_recompute,
        "interval_recompute": interval_recompute,
        "headroom_screens": headroom,
        "native_crosscheck": native_crosscheck,
        "headroom_crosscheck": headroom_crosscheck,
        "launch_gap_crosscheck": launch_gap_crosscheck,
        "handoff_crosscheck": handoff_crosscheck,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--producer-pack", required=True, type=Path)
    parser.add_argument("--detail", action="store_true", help="print compact independent native/family aggregates")
    args = parser.parse_args()
    result = recompute_from_raw(args.producer_pack)
    overview = {
        "producer_status": result["producer_status"],
        "run_id": result["run_id"],
        "raw_index_sha256": result["raw_index_sha256"],
        "raw_files_verified": len(result["raw_audit"]),
        "complete_points": result["complete_points"],
        "native_rows": len(result["native_recompute"]),
        "interval_points": len(result["interval_recompute"]),
        "native_crosscheck_mismatches": sum(r["status"] != "MATCH" for r in result["native_crosscheck"]),
        "headroom_crosscheck_mismatches": sum(r["status"] != "MATCH" for r in result["headroom_crosscheck"]),
        "launch_gap_crosscheck_mismatches": sum(r["status"] != "MATCH" for r in result["launch_gap_crosscheck"]),
        "handoff_crosscheck_mismatches": sum(r["status"] != "MATCH" for r in result["handoff_crosscheck"]),
    }
    if args.detail:
        overview["native_recompute"] = result["native_recompute"]
        overview["headroom_screens"] = result["headroom_screens"]
        overview["raw_token_comparison_summary"] = {
            point: {
                "matched_rows": sum(r["status"] == "MATCH" for r in result["raw_token_comparisons"] if r["point_id"] == point),
                "mismatched_rows": sum(r["status"] != "MATCH" for r in result["raw_token_comparisons"] if r["point_id"] == point),
                "first_mismatch_index_or_NA": next((r["first_mismatch_index_or_NA"] for r in result["raw_token_comparisons"] if r["point_id"] == point and r["status"] != "MATCH"), "NA"),
            } for point in POINT_ALLOWLIST
        }
        overview["interval_recompute"] = {
            point: {
                "parent_cuda_union_ns": data["parent_cuda_union_ns"],
                "parent_cuda_span_ns": data["parent_cuda_span_ns"],
                "uncorrelated_cuda_intervals": data["uncorrelated_cuda_intervals"],
                "phase_family_unions": data["phase_family_unions"],
                "handoff_chronology": handoff_chronology_summary(data),
            } for point, data in result["interval_recompute"].items()
        }
    print(json.dumps(overview, sort_keys=True))


if __name__ == "__main__":
    main()
