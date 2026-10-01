#!/usr/bin/env python3
"""CPU-only authority and schema assertions for the finalized Tier0 contract."""

import csv
import io
import json
import pathlib
import statistics
import subprocess


ROOT = pathlib.Path(__file__).resolve().parent
PACK = "docs/vm_tlb/review_packs/"


def git_bytes(commit, path):
    return subprocess.check_output(["git", "show", f"{commit}:{path}"])


def authority_json(commit, path):
    return json.loads(git_bytes(commit, path))


def authority_tsv(commit, path):
    return list(csv.DictReader(io.StringIO(git_bytes(commit, path).decode()), delimiter="\t"))


def local_json(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def local_tsv(name):
    with (ROOT / name).open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def assert_near(actual, expected, tolerance=0.000001):
    assert abs(actual - expected) <= tolerance, (actual, expected)


def main():
    contract = local_json("C16_STAGEA_DENSE_FIRST_TIER0_109_CONTRACT_V1.json")
    schema = local_json("RESULT_SCHEMA.json")
    verified = local_json("AUTHORITY_VERIFICATION.json")
    decision = local_json("FINAL_DECISION.json")
    binds = local_tsv("POINT_TOKEN_BINDINGS.tsv")
    auth = contract["authority"]
    for commit in auth.values():
        assert subprocess.check_output(["git", "cat-file", "-t", commit], text=True).strip() == "commit"

    old = authority_json(auth["scope_revision_commit"], PACK + "C16_MEASUREMENT_CAMPAIGN_STAGEA_DENSE_FIRST_SCOPE_REVISION_174NEW_V1/C16_STAGEA_DENSE_FIRST_TIER0_109_CONTRACT_DRAFT_V1.json")
    assert old["status"] == "DRAFT_PENDING_AWQ_OBSERVER_V2_RESULT"
    selected = old["static_branches"]["AWQ_OBSERVER_V2_PASS"]
    assert contract["activated_draft_branch"] == "AWQ_OBSERVER_V2_PASS"
    assert contract["point_allowlist_in_order"] == selected["point_allowlist"] == ["MP01", "MP02", "MP03", "MP05"]
    assert contract["gpu_budget"]["total_gpu_active_seconds_cap"] == 60 * selected["gpu_active_cap_minutes"] == 540
    assert contract["gpu_budget"]["per_point_seconds"] == {k: v * 60 for k, v in selected["per_point_cap_minutes"].items()}
    assert set(contract["points"]) == set(contract["point_allowlist_in_order"])
    assert set(contract["point_denylist"]) == {"MP04", "MP06", "MP07", "MP08"}
    assert set(contract["question_allowlist"]) == {"DQ1", "DQ2", "DQ3", "DQ4a"}
    assert contract["question_status"] == {"DQ4b": "DEFERRED_NOT_EXECUTION_READY", "translation": "UNKNOWN_INACTIVE"}
    assert contract["gpu_budget"]["unused_time_transfer_between_points"] is False
    assert contract["gpu_budget"]["budget_from_mp06"] is False

    awq_path = PACK + "C16_AWQ_OBSERVER_V2_REQUAL_CANARY_109_V1/"
    awq_commit = auth["awq_observer_v2_runtime_pass_commit"]
    awq_final = authority_json(awq_commit, awq_path + "FINAL_DECISION.json")
    neutral = authority_json(awq_commit, awq_path + "NEUTRALITY_RESULT.json")
    inventory = authority_json(awq_commit, awq_path + "KERNEL_INVENTORY_RECEIPT.json")
    runtime = authority_json(awq_commit, awq_path + "OBSERVER_V2_RUNTIME_RECEIPT.json")
    build = authority_json(awq_commit, awq_path + "SOURCE_AND_BUILD_RECEIPT.json")
    samples = authority_tsv(awq_commit, awq_path + "NATIVE_SAMPLES.tsv")
    assert awq_final["status"] == "OBSERVER_V2_NEUTRALITY_PASS"
    assert awq_final["mp05_runtime_status"] == "RUNTIME_READY_WITH_OBSERVER_V2"
    assert awq_final["tier0_authorized"] is False
    assert neutral["status"] == "OBSERVER_V2_NEUTRALITY_PASS" and all(neutral["checks"].values())
    assert len(samples) == 6 and [row["arm"] for row in samples] == ["OFF", "ON", "ON", "OFF", "OFF", "ON"]
    off = statistics.median(float(row["host_wall_ms"]) for row in samples if row["arm"] == "OFF")
    on = statistics.median(float(row["host_wall_ms"]) for row in samples if row["arm"] == "ON")
    assert_near(off, 54.955816)
    assert_near(on, 57.840243)
    assert_near(neutral["host_off_median_ms"], off)
    assert_near(neutral["host_on_median_ms"], on)
    assert_near(neutral["host_abs_delta_ms"], abs(on - off))
    assert_near(neutral["host_limit_ms"], max(5.0, 0.1 * off))
    assert neutral["host_abs_delta_ms"] < neutral["host_limit_ms"]
    for field, actual in [("host_off_median_ms", off), ("host_on_median_ms", on), ("host_abs_delta_ms", abs(on-off)), ("host_limit_ms", max(5.0, 0.1*off))]:
        assert_near(verified[field], actual)
    assert inventory["status"] == "PASS" and all(inventory["checks"].values())
    assert inventory["off_kernel_count"] == inventory["on_kernel_count"] == 1850
    expected_sha = "2212bbf7bb4d8cfdc7c8ba0a3e310594d33882ac868646f6f3a6f11b3a45e8fe"
    assert inventory["off_inventory_sha256"] == inventory["on_inventory_sha256"] == expected_sha
    assert contract["observer"]["awq_accepted_inventory_sha256"] == verified["kernel_inventory_sha256"] == expected_sha
    assert runtime["backend"] == {"kernel": "MarlinLinearKernel", "no_requantization": True, "quant_method": "AutoAWQMarlinLinearMethod"}
    assert build["observer_structure"]["per_occurrence_cuda_events"] == 0
    assert build["source_authority"]["commit"] == auth["observer_v2_source_commit"]
    assert contract["observer"]["bf16_v1_runner_sha256"] == build["source_authority"]["base_runner_sha256"]
    assert contract["observer"]["awq_v2_runner_sha256"] == build["source_authority"]["v2_runner_sha256"]
    assert runtime["performance_use"] == "OBSERVER_NEUTRALITY_REQUALIFICATION_ONLY_NO_TIER0"

    asset = auth["asset_input_closure_commit"]
    asset_path = PACK + "C16_MEASUREMENT_CAMPAIGN_STAGEA_ASSET_INPUT_CLOSURE_174NEW_V1/"
    token_rows = authority_tsv(asset, asset_path + "TOKENIZATION_RECEIPTS.tsv")
    lookup = {(r["model_key"], r["source_text_id"]): r for r in token_rows}
    assert len(binds) == 7
    assert len({(r["point_id"], r["source_text_id"]) for r in binds}) == 7
    fields = ["source_utf8_sha256", "tokenizer_revision", "prompt_token_count", "token_ids_sha256", "token_id_file_sha256", "token_ids_relative_path"]
    for bind in binds:
        source = lookup[(bind["model_key"], bind["source_text_id"])]
        assert all(bind[field] == source[field] for field in fields)
        assert source["model_output_generated"] == "false" and bind["prompt_token_count"] == "512"
        point = contract["points"][bind["point_id"]]
        assert bind["model_key"] == point["target"] and bind["source_text_id"] in point["source_ids"]
    for point_id, point in contract["points"].items():
        assert [r["source_text_id"] for r in binds if r["point_id"] == point_id] == point["source_ids"]
    awq_asset = authority_json(asset, asset_path + "QWEN_AWQ_ASSET_RECEIPT.json")
    bf16_asset = authority_json(asset, asset_path + "QWEN_BF16_ASSET_RECEIPT.json")
    assert awq_asset["quantization_config"]["bits"] == 4
    assert awq_asset["quantization_config"]["group_size"] == 128
    assert awq_asset["quantization_config"]["zero_point"] is True
    assert awq_asset["no_requantization"] is True
    assert bf16_asset["revision"] == contract["model_runtime_identity"]["QWEN_BF16"]["revision"]
    assert awq_asset["revision"] == contract["model_runtime_identity"]["QWEN_AWQ"]["revision"]

    graph = authority_tsv(auth["runtime_qualification_commit"], PACK + "C16_STAGEA_RUNTIME_QUALIFICATION_CANARY_109_V1/GRAPH_OFF_ON_CORRECTNESS.tsv")
    assert all(row["status"] == "PASS" for row in graph if row["target"] in ("QWEN_BF16", "QWEN_AWQ"))
    olmoe = authority_json(auth["olmoe_diagnostic_commit"], PACK + "C16_OLMOE_GRAPH_OFF_ON_CORRECTNESS_DIAGNOSTIC_174NEW_V1/FINAL_DECISION.json")
    assert olmoe["status"] == "OLMOE_GRAPH_MODE_EXPERT_SET_DIVERGENCE"
    assert olmoe["expert_set_substitution_events"] == 616

    assert set(contract["arms"]) == {"GRAPH_ON_NATIVE", "GRAPH_OFF_NATIVE", "GRAPH_OFF_OBSERVED"}
    for arm in ("GRAPH_ON_NATIVE", "GRAPH_OFF_NATIVE"):
        assert contract["arms"][arm]["instrumentation"] == "OFF"
        assert contract["arms"][arm]["warmup_requests"] == 1
        assert contract["arms"][arm]["measured_requests"] == 3
    assert contract["native_protocol"]["primary_field"] == "request_cuda_event_ms"
    assert contract["nsys"]["max_captures_per_point"] == 1
    assert contract["nsys"]["domains"] == ["cuda", "nvtx"]
    assert contract["nsys"]["native_timing_estimator_input"] is False
    assert contract["arms"]["GRAPH_OFF_OBSERVED"]["observed_requests"] == 1
    assert "does not recompute its median gate" in contract["correctness_gate"]["neutrality_rule"]
    assert contract["matched_graph_control_gap"]["only_predefined_pair"] == ["MP02", "MP03"]
    assert contract["matched_graph_control_gap"]["normalizer"] == "generated_tokens = batch_size * 32; MP02 = 32, MP03 = 128"
    assert contract["stop_rules"]["local_wall_fraction_lt"] == 0.03
    assert contract["stop_rules"]["zero_cost_whole_run_incremental_ceiling_lt"] == 0.02
    assert contract["stop_rules"]["graph_control_absorption_gte"] == 0.85
    assert set(contract["tool_denylist"]) == {"NCU", "NVBit", "SASS", "Accel-Sim"}
    assert contract["holdout_execution_authorized"] is False and contract["tier1_authorized"] is False
    assert contract["mechanism_design_authorized"] is False
    required = {"POINT_IDENTITY.tsv", "NATIVE_REQUEST_SAMPLES.tsv", "NATIVE_REQUEST_SUMMARY.tsv", "GRAPH_MODE_CORRECTNESS.tsv", "BACKEND_KERNEL_IDENTITY.tsv", "SEMANTIC_INTERVALS.tsv", "CUDA_INTERVALS.tsv", "LAUNCH_GAPS.tsv", "NSYS_CAPTURE_INDEX.tsv", "POINT_HEADROOM_SCREEN.tsv", "QUESTION_GATE_STATUS.tsv", "GPU_ACTIVE_BUDGET.json", "FINAL_DECISION.json"}
    assert set(schema["row_rules"]) == required
    for name, record in schema["row_rules"].items():
        assert record["rule"] and (record.get("columns") or record.get("required_keys")), name
        if "columns" in record:
            assert len(record["columns"]) == len(set(record["columns"]))
            assert set(record["key"]).issubset(record["columns"])
    assert decision["status"] == "STAGEA_DENSE_FIRST_TIER0_CONTRACT_FINALIZED"
    assert decision["execution_authorized"] is True and decision["gpu_used_in_this_goal"] is False
    print("PASS: authority, independent AWQ median, token identities, scope, budget, arms, estimators, stops, schema")


if __name__ == "__main__":
    main()
