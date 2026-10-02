#!/usr/bin/env python3
"""CPU-only authority, pinned-source and status-boundary validation."""

import argparse
import csv
import io
import json
import pathlib
import subprocess


ROOT = pathlib.Path(__file__).resolve().parent
PACK = "docs/vm_tlb/review_packs/"
MODE_PASS = "9122fac5c50dbf19706636fc03978a356ffd800f"
V2_FAIL = "c48331a9ea5a3f381741aad4bae91dfb0eefc2c2"
OBSERVER = "eaaa2e66befa872ce7c8f47011e9fe7cdf8921d9"
PRODUCER = "82788c2d587e86f94791d65aaa2bde28929f9303"
CONSUMER = "9d82ff41132e7b1a1fdd18a287c13627fe62e5b7"
VLLM = "ced6857afa0ea7b2e3f0846a62e1394e90f15607"


def git(*args):
    return subprocess.check_output(["git", *args], text=True).strip()


def from_commit(commit, path):
    return subprocess.check_output(["git", "show", f"{commit}:{path}"], text=True)


def rows(name):
    with (ROOT / name).open(encoding="utf-8", newline="") as stream:
        result = list(csv.DictReader(stream, delimiter="\t"))
    assert result and all(None not in row and all(value != "" for value in row.values()) for row in result), name
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--vllm-repo", required=True, type=pathlib.Path)
    args = parser.parse_args()
    for commit in (MODE_PASS, V2_FAIL, OBSERVER, PRODUCER, CONSUMER):
        assert git("cat-file", "-t", commit) == "commit"
    assert subprocess.check_output(["git", "-C", str(args.vllm_repo), "rev-parse", VLLM], text=True).strip() == VLLM
    assert subprocess.check_output(["git", "-C", str(args.vllm_repo), "rev-parse", f"{VLLM}^{{tree}}"], text=True).strip() == "22fe534b15542997d37f97a9079b4a1ac7961a18"

    mode = json.loads(from_commit(MODE_PASS, PACK + "C16_QWEN_DECODE_MODE_DECONFLATION_CANARY_109_V1/FINAL_DECISION.json"))
    failed = json.loads(from_commit(V2_FAIL, PACK + "C16_QWEN_COMPILED_NO_CUDAGRAPH_OBSERVER_V2_CANARY_109_V1/FINAL_DECISION.json"))
    detail = json.loads(from_commit(V2_FAIL, PACK + "C16_QWEN_COMPILED_NO_CUDAGRAPH_OBSERVER_V2_CANARY_109_V1/MP02_IDENTITY_FAILURE_DETAIL.json"))
    old = json.loads(from_commit(PRODUCER, PACK + "C16_STAGEA_DENSE_FIRST_TIER0_PRODUCER_109_V1/CORRECTNESS_STOP_RECEIPT.json"))
    consumer = json.loads(from_commit(CONSUMER, PACK + "C16_STAGEA_DENSE_FIRST_TIER0_INDEPENDENT_CONSUMER_174NEW_V1/FINAL_DECISION.json"))
    assert mode["decision"] == "MODE_DECONFLATION_CORRECTNESS_PASS_FOR_OBSERVER_REVIEW_ONLY"
    assert mode["mp02_pass"] and mode["mp03_pass"]
    assert failed["decision"] == "COMPILED_NO_CUDAGRAPH_OBSERVER_V2_IDENTITY_FAIL"
    assert failed["semantic_observed"] == 0 and failed["semantic_expected"] == 4608
    assert failed["mp02_native_samples_completed"] == 0 and failed["mp03_executed"] is False
    assert failed["correctness_evaluated"] is failed["neutrality_evaluated"] is failed["kernel_inventory_evaluated"] is False
    assert detail["observer_on_compiled_call_path"] == "UNRESOLVED_AFTER_SEMANTIC_FAILURE"
    assert old["MP02"]["status"] == old["MP03"]["status"] == "STOP_POINT_CORRECTNESS"
    assert consumer["independent_tier0_survivor_count"] == 0
    assert set(consumer["question_final_status"].values()) == {"QUESTION_INCOMPLETE"}
    assert consumer["no_new_architectural_phenomenon_found_claim_allowed"] is False

    source = subprocess.check_output(["git", "-C", str(args.vllm_repo), "show", f"{VLLM}:vllm/v1/worker/gpu_model_runner.py"], text=True)
    decorators = subprocess.check_output(["git", "-C", str(args.vllm_repo), "show", f"{VLLM}:vllm/compilation/decorators.py"], text=True)
    wrapper = subprocess.check_output(["git", "-C", str(args.vllm_repo), "show", f"{VLLM}:vllm/compilation/wrapper.py"], text=True)
    assert "def _register_layerwise_nvtx_hooks(self)" in source
    assert "after the first dynamo tracing" in source
    assert "they will never" in source and "be called on the compiled model execution path" in source
    assert source.index("after the first dynamo tracing") < source.index("self._register_layerwise_nvtx_hooks()")
    assert "return self.aot_compiled_fn(self, *args, **kwargs)" in decorators
    assert "return TorchCompileWithNoGuardsWrapper.__call__(self, *args, **kwargs)" in decorators
    assert "self._compiled_callable = torch.compile(" in wrapper

    levels = {row["level"]: row for row in rows("ATTRIBUTION_AUTHORITY_LEVELS.tsv")}
    questions = {row["question"]: row for row in rows("DQ_OBSERVABILITY_REQUIREMENTS.tsv")}
    rule = json.loads((ROOT / "STAGEA_V2_ELIGIBILITY_RULE.json").read_text())
    final = json.loads((ROOT / "FINAL_DECISION.json").read_text())
    assert set(levels) == {"LEVEL_2_EXACT", "LEVEL_1_FAMILY_ONLY", "LEVEL_0_UNRESOLVED"}
    assert set(questions) == {"DQ1", "DQ2", "DQ3", "DQ4a"}
    assert questions["DQ1"]["minimum_authority"] == questions["DQ3"]["minimum_authority"] == "LEVEL_1_FAMILY_ONLY"
    assert questions["DQ4a"]["minimum_authority"] == "LEVEL_2_EXACT"
    assert questions["DQ2"]["minimum_authority"] == "NATIVE_MODE_A_B_TIMING_ONLY"
    assert rule["minimum_for_decode_semantic_stagea_v2_design"] == "LEVEL_1_FAMILY_ONLY"
    assert rule["level_0_action"]["stagea_v2_mp02_mp03_semantic_design"] == "STOP"
    assert rule["gpu_or_new_measurement_authorized_by_this_rule"] is False
    assert final["status"] == "COMPILER_NATIVE_ATTRIBUTION_DESIGN_READY_FOR_FEASIBILITY"
    assert final["mode_b_no_observer_execution_identity"] == "VALID_IN_9122fac5_ACCEPTED_CANARY"
    assert final["observer_v2_failed_canary_preserved"] == "COMPILED_NO_CUDAGRAPH_OBSERVER_V2_IDENTITY_FAIL"
    assert final["specific_observability_classification"] == "POST_COMPILE_PYTHON_MODULE_HOOK_OBSERVER_INCOMPATIBLE"
    assert final["stagea_v2_ready"] is False and final["gpu_used"] is False
    print("PASS: immutable outcomes, pinned compiled-hook source comment, level/DQ gates and CPU-only scope")


if __name__ == "__main__":
    main()
