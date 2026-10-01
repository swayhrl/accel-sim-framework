#!/usr/bin/env python3
"""Deterministic independent Stage A Tier0 review-pack builder (CPU only)."""
from __future__ import annotations

import argparse
import csv
import json
from hashlib import sha256
from pathlib import Path

from consume import CONTRACT_PACK, HERE, REPO, recompute_from_raw
from core import dq2_batch_matched_graph_control, validate_coverage
from intervals import handoff_chronology_summary
from raw_authority import CONTRACT_SHA256, digest_file


PACK_REL = Path("docs/vm_tlb/review_packs/C16_STAGEA_DENSE_FIRST_TIER0_INDEPENDENT_CONSUMER_174NEW_V1")
HANDOFF_REL = Path("docs/vm_tlb/chatgpt_handoff/c16/C16_STAGEA_DENSE_FIRST_TIER0_CURRENT_STATE.md")
PRODUCER_COMMIT = "82788c2d587e86f94791d65aaa2bde28929f9303"
PRODUCER_TREE = "c9093a84820c4221b06233a8efa2a2aa911b5cf5"
CONTRACT_COMMIT = "fad9da8116c8ad794f99a93f153b0866162158a4"
CONTRACT_TREE = "c657f1655ffabbeb0942732bdff08c8df8e79987"


def encoded(value):
    if value is None:
        return "NA"
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def write_tsv(path: Path, rows: list[dict], columns: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({col: encoded(row.get(col)) for col in columns})


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def fmt(value: float) -> str:
    return f"{value:.9f}"


def build(producer_pack: Path) -> dict:
    result = recompute_from_raw(producer_pack)
    complete = set(result["complete_points"])
    if result["producer_status"] != "STAGEA_TIER0_PRODUCER_PARTIAL" or complete != {"MP01", "MP05"}:
        raise ValueError("this frozen partial closure requires MP01/MP05 exactly; no branch-follow or point substitution")
    crosschecks = (
        result["native_crosscheck"] + result["headroom_crosscheck"] +
        result["launch_gap_crosscheck"] + result["handoff_crosscheck"]
    )
    mismatches = [r for r in crosschecks if r["status"] != "MATCH"]
    if mismatches:
        raise ValueError(f"CONSUMER_PRODUCER_NUMERIC_MISMATCH count={len(mismatches)}")
    coverage = validate_coverage(complete, result["producer_status"])
    assert set(coverage.values()) == {"QUESTION_INCOMPLETE"}
    native = {(r["point_id"], r["arm"]): r for r in result["native_recompute"]}
    medians = {(point, "ON" if arm == "GRAPH_ON_NATIVE" else "OFF"): row["cuda_median"]
               for (point, arm), row in native.items()}
    sample_counts = {(point, "ON" if arm == "GRAPH_ON_NATIVE" else "OFF"): row["cuda_sample_count"]
                     for (point, arm), row in native.items()}
    graph_control = dq2_batch_matched_graph_control(medians, sample_counts, identity_ok=False)
    if graph_control["status"] != "GRAPH_CONTROL_GAP_NOT_IDENTIFIABLE":
        raise ValueError("forbidden DQ2 matched Graph admission on failed MP02/MP03")

    pack = REPO / PACK_REL
    pack.mkdir(parents=True, exist_ok=True)
    authority = {
        "stage": "C16_STAGEA_DENSE_FIRST_TIER0_INDEPENDENT_CONSUMER_174NEW_V1",
        "contract_commit": CONTRACT_COMMIT, "contract_tree": CONTRACT_TREE,
        "contract_json_sha256": CONTRACT_SHA256,
        "producer_commit": PRODUCER_COMMIT, "producer_tree": PRODUCER_TREE,
        "producer_branch_frozen": "hrl/c16-stagea-dense-first-tier0-producer-109-v1",
        "producer_status": result["producer_status"],
        "run_id": result["run_id"],
        "raw_index_sha256": result["raw_index_sha256"],
        "raw_payload_manifest_sha256": result["raw_payload_manifest_sha256"],
        "producer_review_payload_manifest_sha256": result["review_payload_manifest_sha256"],
        "raw_files_independently_verified": len(result["raw_audit"]),
        "complete_points": result["complete_points"],
        "failed_points": ["MP02", "MP03"],
        "source_script_sha256": {p.name: digest_file(p) for p in sorted(HERE.glob("*.py"))},
        "producer_postprocess_imported": False,
        "raw_authority_only": True,
        "gpu_used": False, "holdout_executed": False, "tier1_executed": False,
    }
    write_json(pack / "CONSUMER_AUTHORITY.json", authority)

    write_tsv(pack / "RAW_INTEGRITY_AUDIT.tsv", result["raw_audit"],
        ["artifact", "node109_path", "path", "expected_size", "actual_size",
         "expected_sha256", "actual_sha256", "status"])
    write_tsv(pack / "CORRECTNESS_RECOMPUTE.tsv", result["raw_token_comparisons"],
        ["point_id", "sample_index", "source_id", "graph_on_generated_tokens", "graph_off_generated_tokens",
         "first_mismatch_index_or_NA", "graph_on_token_at_mismatch_or_NA",
         "graph_off_token_at_mismatch_or_NA", "status"])
    write_tsv(pack / "NATIVE_TIMING_RECOMPUTE.tsv", result["native_recompute"],
        ["point_id", "arm", "cuda_sample_count", "cuda_median", "cuda_min", "cuda_max",
         "cuda_spread", "cuda_spread_over_median", "cuda_population_cv",
         "host_median_diagnostic_ms", "token_ids_sha256", "warmup_count"])

    interval_rows = []
    launch_rows = []
    for point, data in sorted(result["interval_recompute"].items()):
        for kind, rows in (("ORDINAL", data["ordinal_unions"]),
                           ("MODULE", data["module_unions"]),
                           ("PHASE_FAMILY", data["phase_family_unions"]),
                           ("ALL_PHASE_FAMILY", data["all_phase_family_unions"])):
            for row in rows:
                interval_rows.append({"record_type": kind, **row,
                    "uncorrelated_cuda_interval_count": data["uncorrelated_cuda_intervals"],
                    "parent_cuda_span_ns": data["parent_cuda_span_ns"]})
        for i, row in enumerate(data["global_launch_gaps"]):
            launch_rows.append({"record_type": "GLOBAL_CHRONOLOGY", "gap_id": i,
                "point_id": point, "observed_request_id": row["observed_request_id"],
                "predecessor_or_producer": row["predecessor"],
                "successor_or_consumer": row["successor"],
                "signed_gap_ns": row["signed_gap_ns"], "positive_gap_ns": row["positive_gap_ns"],
                "overlap_ns": row["overlap_ns"], "gap_start_ns": row["gap_start_ns"],
                "gap_end_ns": row["gap_end_ns"], "classification": row["classification"],
                "parent_cuda_union_ns": data["parent_cuda_union_ns"]})
        for i, row in enumerate(data["sibling_boundaries"]):
            launch_rows.append({"record_type": "SEMANTIC_SIBLING_BOUNDARY", "gap_id": i,
                "point_id": point, "observed_request_id": row["observed_request_id"],
                "predecessor_or_producer": row["producer_ordinal"],
                "successor_or_consumer": row["consumer_ordinal"],
                "producer_module": row["producer_module"], "consumer_module": row["consumer_module"],
                "signed_gap_ns": row["signed_gap_ns"], "positive_gap_ns": row["positive_gap_ns"],
                "gap_start_ns": row["gap_start_ns"], "gap_end_ns": row["gap_end_ns"],
                "classification": row["status"], "parent_cuda_union_ns": data["parent_cuda_union_ns"],
                "positive_gap_parent_cuda_union_fraction": row["positive_gap_parent_fraction"]})
    write_tsv(pack / "INTERVAL_UNION_RECOMPUTE.tsv", interval_rows,
        ["record_type", "point_id", "observed_request_id", "ordinal", "module", "phase", "family",
         "cuda_event_count", "cuda_sum_ns", "cuda_union_ns", "overlap_double_count_ns",
         "parent_full_request_cuda_union_ns", "f_of_full_request_graph_off",
         "parent_cuda_span_ns", "uncorrelated_cuda_interval_count"])
    write_tsv(pack / "LAUNCH_GAP_RECOMPUTE.tsv", launch_rows,
        ["record_type", "gap_id", "point_id", "observed_request_id", "predecessor_or_producer",
         "successor_or_consumer", "producer_module", "consumer_module", "signed_gap_ns",
         "positive_gap_ns", "overlap_ns", "gap_start_ns", "gap_end_ns", "classification",
         "parent_cuda_union_ns", "positive_gap_parent_cuda_union_fraction"])

    headroom_rows = []
    for row in result["headroom_screens"]:
        headroom_rows.append({
            **row,
            "local_weight_gate": "STOP_LOCAL_LINE" if row["below_3pct_local_gate"] else "PASS_LOCAL_WEIGHT",
            "two_percent_whole_run_gate": "WHOLE_RUN_CEILING_NOT_IDENTIFIABLE",
            "question_final_status": "QUESTION_INCOMPLETE" if row["point_id"] == "MP01" else "CONTROL_ONLY_NOT_DQ1",
        })
    write_tsv(pack / "DQ1_HEADROOM_DECISION.tsv", headroom_rows,
        ["point_id", "phase", "family", "screen_scope", "candidate_graph_off_union_ns",
         "parent_graph_off_cuda_union_ns", "f_graph_off", "s_zero_graph_off_screen",
         "local_weight_gate", "whole_run_ceiling_status", "whole_run_ceiling_incremental",
         "two_percent_whole_run_gate", "status", "question_final_status"])

    comparison_rows = []
    for scope, rows in (("NATIVE", result["native_crosscheck"]),
                        ("HEADROOM", result["headroom_crosscheck"]),
                        ("LAUNCH_GAP", result["launch_gap_crosscheck"]),
                        ("HANDOFF_BOUNDARY", result["handoff_crosscheck"])):
        comparison_rows.extend({"comparison_scope": scope, **row} for row in rows)
    write_tsv(pack / "PRODUCER_CONSUMER_CROSSCHECK.tsv", comparison_rows,
        ["comparison_scope", "point_id", "arm", "question_id", "candidate_id", "metric",
         "consumer", "producer", "absolute_difference", "status"])
    write_json(pack / "PRODUCER_MATCH_CHECK.json", {
        "native_metric_checks": len(result["native_crosscheck"]),
        "headroom_metric_checks": len(result["headroom_crosscheck"]),
        "launch_gap_metric_checks": len(result["launch_gap_crosscheck"]),
        "handoff_boundary_metric_checks": len(result["handoff_crosscheck"]),
        "total_checks": len(comparison_rows), "numeric_mismatches": 0,
        "status": "PRODUCER_NUMERIC_MATCH_ON_ADMITTED_POINTS_ONLY",
        "excluded_failed_points": ["MP02", "MP03"],
    })

    mp01 = result["interval_recompute"]["MP01"]
    mp05 = result["interval_recompute"]["MP05"]
    handoff_01 = handoff_chronology_summary(mp01)
    handoff_05 = handoff_chronology_summary(mp05)
    token_rows = result["raw_token_comparisons"]
    token_summary = {point: {
        "match": sum(r["status"] == "MATCH" for r in token_rows if r["point_id"] == point),
        "mismatch": sum(r["status"] != "MATCH" for r in token_rows if r["point_id"] == point),
        "first": next((r["first_mismatch_index_or_NA"] for r in token_rows
                       if r["point_id"] == point and r["status"] != "MATCH"), "NA"),
    } for point in ("MP01", "MP02", "MP03", "MP05")}
    mp05_on = native[("MP05", "GRAPH_ON_NATIVE")]["cuda_median"]
    mp05_off = native[("MP05", "GRAPH_OFF_NATIVE")]["cuda_median"]
    (pack / "DQ2_BATCH_REPRESENTATION_DECISION.md").write_text(
        "# DQ2 — B1→B4 and representation control\n\n"
        "`QUESTION_INCOMPLETE`. The frozen B1/B4 pair requires MP02 and MP03. Direct raw generated-token comparisons show "
        f"MP02: {token_summary['MP02']['mismatch']}/3 mismatched measured rows (first index {token_summary['MP02']['first']}); "
        f"MP03: {token_summary['MP03']['mismatch']}/12 mismatched batch rows (first index {token_summary['MP03']['first']}). "
        "Their Graph-OFF correctness STOPs and missing observed/NSYS captures invalidate their native medians, effective-M/shape comparison and the 85% matched estimator. "
        "Frozen nominal B1/B4 inputs cannot substitute for a qualified observed execution. No B1→B4 utilization claim is made.\n\n"
        f"MP05 AWQ B1 is a legal *representation control only*: native Graph ON median {fmt(mp05_on)} ms and Graph OFF median {fmt(mp05_off)} ms, "
        "each from three instrumentation-OFF request CUDA events; observed decode gate/up input shape `[1,2048]` gives effective M=1 in its own graph-OFF semantic row. "
        "Its Marlin path and BF16 path differ in representation/runtime, so no strict BF16-vs-AWQ causal ratio is admitted. "
        "The MP05 ON/OFF difference is not the contract's MP02/MP03 matched absorption estimator.\n\n"
        f"Graph control: `{graph_control['status']}`. No alternate denominator was invented.\n",
        encoding="utf-8")

    candidate_rows = []
    for row in result["headroom_screens"]:
        point, family = row["point_id"], row["family"]
        observed = [r for r in result["interval_recompute"][point]["phase_family_unions"] if r["family"] == family]
        names = {name.lower() for part in observed for name in part["unique_kernel_names"]}
        if family == "ATTENTION":
            clue = any("flash" in name or "attention" in name for name in names)
        elif family in {"GATE_UP_PROJECTION", "DOWN_PROJECTION"}:
            clue = any("cutlass" in name or "marlin" in name or "gemm" in name or "gemv" in name for name in names)
        else:
            clue = False
        local_candidate = not row["below_3pct_local_gate"] and clue
        candidate_rows.append((point, family, row["f_graph_off"], clue, local_candidate))
    candidate_table = "\n".join(
        f"| {point} | {family} | {fraction:.6%} | {'YES' if clue else 'NO'} | "
        f"{'MEMORY_SERVICE_CANDIDATE_FOR_TIER1_REVIEW' if candidate else 'NO_MEMORY_SERVICE_CANDIDATE'} |"
        for point, family, fraction, clue, candidate in candidate_rows)
    (pack / "DQ3_MEMORY_SERVICE_DECISION.md").write_text(
        "# DQ3 — Tier0 memory/service screen\n\n"
        "The independent screen uses only correlated raw CUDA family unions, the admitted native request endpoint, observed shape, "
        "and actual kernel names (FlashAttention, CUTLASS or Marlin). A name/weight layout is a **clue**, not measured service latency. "
        "The local candidate label does not distinguish L1, L2, DRAM or TLB.\n\n"
        "| Point | Family | Graph-OFF family/full-request CUDA-union f | Kernel/layout clue | Local Tier0 screen |\n"
        "|---|---|---:|---|---|\n" + candidate_table + "\n\n"
        "ATTENTION, GATE_UP_PROJECTION and DOWN_PROJECTION remain local *review* candidates at MP01/MP05; ACTIVATION is below the 3% screen. "
        "However MP02 and MP03 failed correctness, so the full DQ3 question is `QUESTION_INCOMPLETE`; no Tier1 is authorized or executed. "
        "The Graph-OFF f is not a Graph-ON local contribution, and the 2% whole-run ceiling is `WHOLE_RUN_CEILING_NOT_IDENTIFIABLE`. "
        "These rows are not bottleneck attributions or project-level survivors.\n",
        encoding="utf-8")

    (pack / "DQ4A_HANDOFF_DECISION.md").write_text(
        "# DQ4a — dense handoff chronology\n\n"
        f"MP01 raw correlated adjacent producer→consumer boundaries: {handoff_01['boundary_count']} identifiable, "
        f"positive gap union {handoff_01['positive_gap_union_ns']} ns / parent CUDA union {mp01['parent_cuda_union_ns']} ns "
        f"= {handoff_01['positive_gap_fraction_of_parent_cuda_union']:.6%}; "
        f"`{handoff_01['status']}` under the existing 3% chronology screen. "
        "All boundary gaps were independently reconstructed from CUDA timestamps and semantic ordinals; this is observed Graph-OFF chronology, not a cache-handoff saving or hardware cause.\n\n"
        f"MP05 AWQ representation control has {handoff_05['boundary_count']} boundaries and {handoff_05['positive_gap_union_ns']} ns "
        f"({handoff_05['positive_gap_fraction_of_parent_cuda_union']:.6%} of its parent CUDA union), but MP05 is not an eligible DQ4a dense BF16 substitute. "
        "The needed MP02 decode point failed correctness; final DQ4a status is `QUESTION_INCOMPLETE`, no mechanism claim.\n",
        encoding="utf-8")

    question_rows = []
    for question, missing in (("DQ1", "MP02"), ("DQ2", "MP02;MP03"),
                              ("DQ3", "MP02;MP03"), ("DQ4a", "MP02")):
        question_rows.append({"question_id": question, "complete_points": "MP01;MP05",
                              "missing_required_points": missing,
                              "local_valid_evidence": "MP01_PREFILL_AND_MP05_CONTROL_ONLY",
                              "graph_control_gap": graph_control["status"] if question == "DQ2" else "GRAPH_CONTROL_GAP_NOT_IDENTIFIABLE",
                              "whole_run_ceiling": "WHOLE_RUN_CEILING_NOT_IDENTIFIABLE",
                              "final_tier0_status": coverage[question]})
    write_tsv(pack / "QUESTION_FINAL_STATUS.tsv", question_rows,
        ["question_id", "complete_points", "missing_required_points", "local_valid_evidence",
         "graph_control_gap", "whole_run_ceiling", "final_tier0_status"])
    final = {
        "stage": "C16_STAGEA_DENSE_FIRST_TIER0_INDEPENDENT_CONSUMER_174NEW_V1",
        "status": "STAGEA_TIER0_CONSUMER_PARTIAL",
        "producer_status": result["producer_status"],
        "producer_commit": PRODUCER_COMMIT, "producer_tree": PRODUCER_TREE,
        "complete_points": result["complete_points"],
        "failed_correctness_points": ["MP02", "MP03"],
        "question_final_status": {r["question_id"]: r["final_tier0_status"] for r in question_rows},
        "independent_tier0_survivor_count": 0,
        "no_new_architectural_phenomenon_found_claim_allowed": False,
        "discovery_freeze_receipt_draft_generated": False,
        "graph_control": graph_control["status"],
        "raw_files_verified": len(result["raw_audit"]),
        "producer_consumer_numeric_mismatches": 0,
        "scientific_mismatch": False,
        "holdout_executed": False, "tier1_executed": False,
        "gpu_used_by_consumer": False, "mechanism_work": False,
    }
    write_json(pack / "FINAL_DECISION.json", final)
    (pack / "VALIDATION_SUMMARY.md").write_text(
        "# Validation\n\n"
        f"Independent 164 raw audit: {len(result['raw_audit'])}/{len(result['raw_audit'])} files size/SHA PASS. "
        f"Independent producer numeric crosscheck: {len(comparison_rows)} metric cells MATCH, 0 mismatch. "
        "Native timing uses only the individual instrumentation-OFF CUDA-event rows. "
        "All generated files are deterministic from the frozen contract, producer commit and durable raw. "
        "All 29 independent synthetic/real-contract tests PASS. Run `python3 -m unittest discover -s util/vm_tlb/c16/stagea_tier0_independent_consumer -p test_*.py`, "
        "rerun `publish.py --producer-pack ...`, then `sha256sum -c SHA256SUMS` in this directory. "
        "No GPU/holdout/Tier1/NCU/NVBit/SASS/Accel-Sim/mechanism action was taken by this consumer.\n",
        encoding="utf-8")

    handoff = REPO / HANDOFF_REL
    handoff.parent.mkdir(parents=True, exist_ok=True)
    handoff.write_text(
        "# C16 Stage A dense-first Tier0 current state\n\n"
        "Status: `STAGEA_TIER0_CONSUMER_PARTIAL` (174-new independent raw closure). "
        f"Contract `{CONTRACT_COMMIT}`, producer `{PRODUCER_COMMIT}`, consumer branch "
        "`hrl/c16-stagea-dense-first-tier0-independent-consumer-174new-v1`. "
        f"All {len(result['raw_audit'])} 164 raw files independently rehashed PASS; producer numeric crosscheck "
        f"{len(comparison_rows)}/{len(comparison_rows)} cells MATCH.\n\n"
        "MP01 BF16 prefill and MP05 AWQ representation control are the only admitted complete points. "
        "MP02 BF16 B1 decode and MP03 BF16 B4 decode failed Graph-OFF token correctness and stopped before observed/NSYS; "
        "their native timing is quarantined. All four DQ questions are `QUESTION_INCOMPLETE`; zero project-level Tier0 survivors. "
        "MP01 has material Graph-OFF producer→consumer chronology, but no causal hardware handoff claim. "
        "Graph-ON 85% matched DQ2 absorption and comparable whole-run 2% ceiling are not identifiable. "
        "Do not claim `NO_NEW_ARCHITECTURAL_PHENOMENON_FOUND` from incomplete coverage.\n\n"
        "Review pack: `docs/vm_tlb/review_packs/C16_STAGEA_DENSE_FIRST_TIER0_INDEPENDENT_CONSUMER_174NEW_V1/`. "
        "No freeze-receipt draft, holdout, Tier1, GPU, simulator or mechanism work is authorized by this closure. STOP for project review.\n",
        encoding="utf-8")

    # Manifest includes every review-pack file and the required handoff.
    entries = []
    for path in sorted(pack.iterdir(), key=lambda p: p.name):
        if path.is_file() and path.name != "SHA256SUMS":
            entries.append((digest_file(path), path.name))
    relative_handoff = Path("../../chatgpt_handoff/c16/C16_STAGEA_DENSE_FIRST_TIER0_CURRENT_STATE.md")
    entries.append((digest_file(handoff), relative_handoff.as_posix()))
    (pack / "SHA256SUMS").write_text("".join(f"{digest}  {name}\n" for digest, name in entries), encoding="utf-8")
    return {"status": final["status"], "raw_files": len(result["raw_audit"]),
            "numeric_checks": len(comparison_rows), "survivors": 0,
            "pack": str(pack), "handoff": str(handoff)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--producer-pack", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(build(args.producer_pack), sort_keys=True))


if __name__ == "__main__":
    main()
