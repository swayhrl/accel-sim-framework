#!/usr/bin/env python3
"""CPU-only consistency checks for the Stage A dense-first scope revision."""

import csv
import json
import pathlib
import subprocess
import sys


ROOT = pathlib.Path(__file__).resolve().parent
AUTHORITIES = {
    "campaign_design_commit": "5f0335b5f991890348e60e1f23a546f393f86d8b",
    "asset_input_closure_commit": "c3f625e46adb8d5c4082ded8b61858c710e1f4e9",
    "runtime_qualification_commit": "3f62f909a474e4c56695ffacf36ddcb5d7b5f147",
    "olmoe_diagnostic_commit": "8b677cfa541877f559614f7bf22a40dd11cebd56",
    "observer_v2_source_commit": "f63d39c8d90ced038445c264fa8242c524a1aa6f",
}


def table(name):
    with (ROOT / name).open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    assert rows and all(None not in row for row in rows), name
    assert all(all(value != "" for value in row.values()) for row in rows), name
    return rows


def main():
    draft = json.loads((ROOT / "C16_STAGEA_DENSE_FIRST_TIER0_109_CONTRACT_DRAFT_V1.json").read_text())
    decision = json.loads((ROOT / "FINAL_DECISION.json").read_text())
    points = {row["point_id"]: row for row in table("POINT_STATUS.tsv")}
    questions = {row["question_id"]: row for row in table("QUESTION_STATUS.tsv")}
    stops = {row["rule_id"]: row for row in table("UPDATED_STOP_RULES.tsv")}
    assert set(points) == {f"MP{i:02d}" for i in range(1, 9)}
    assert set(questions) == {"DQ1", "DQ2", "DQ3", "DQ4a", "DQ4b", "SQ_TRANSLATION_AUTHORITY_ONLY"}
    assert draft["authority"] == AUTHORITIES
    assert draft["status"] == "DRAFT_PENDING_AWQ_OBSERVER_V2_RESULT"
    assert draft["authorized_for_execution"] is False and draft["automatic_109_start"] is False
    assert draft["holdout_execution"] is False and draft["olmoe_execution"] is False
    assert draft["budget_transfer_from_mp06"] is False
    expected = {
        "AWQ_OBSERVER_V2_PASS": (["MP01", "MP02", "MP03", "MP05"], 9),
        "AWQ_OBSERVER_V2_FAIL": (["MP01", "MP02", "MP03"], 6),
    }
    for branch, (ids, cap) in expected.items():
        choice = draft["static_branches"][branch]
        assert choice["point_allowlist"] == ids and choice["gpu_active_cap_minutes"] == cap
        assert sum(choice["per_point_cap_minutes"].values()) == cap
    assert draft["excluded_points"] == ["MP04", "MP06", "MP07", "MP08"]
    assert {point for point, row in points.items() if row["current_stage_a_status"] == "ACTIVE_CORE"} == {"MP01", "MP02", "MP03"}
    assert points["MP05"]["current_stage_a_status"] == "CONDITIONAL_ON_OBSERVER_V2_PASS"
    assert points["MP06"]["current_stage_a_status"] == "CAMPAIGN_QUESTION_NOT_EXECUTION_READY"
    assert points["MP07"]["current_stage_a_status"] == "DEFERRED_MOE_HOLDOUT"
    assert questions["DQ4b"]["current_status"] == "DEFERRED_NOT_EXECUTION_READY"
    assert questions["SQ_TRANSLATION_AUTHORITY_ONLY"]["current_status"] == "UNKNOWN_INACTIVE"
    assert "< 0.03" in stops["ST_LOCAL_WEIGHT"]["frozen_trigger"]
    assert "< 0.02" in stops["ST_ZERO_COST_CEILING"]["frozen_trigger"]
    assert ">= 0.85" in stops["ST_STRONG_GRAPH_CONTROL"]["frozen_trigger"]
    assert decision["status"] == "STAGEA_DENSE_FIRST_SCOPE_READY_PENDING_AWQ"
    assert decision["execution_authorized"] is False and decision["holdout_outputs_generated"] is False
    assert decision["olmoe_diagnostic_preserved"] == "OLMOE_GRAPH_MODE_EXPERT_SET_DIVERGENCE"
    assert decision["olmoe_original_canary_preserved"] == "CORRECTNESS_OR_BACKEND_IDENTITY_FAILED"
    for commit in AUTHORITIES.values():
        obj_type = subprocess.check_output(["git", "cat-file", "-t", commit], text=True).strip()
        assert obj_type == "commit", (commit, obj_type)
    def at(commit, path):
        return json.loads(subprocess.check_output(["git", "show", f"{commit}:{path}"], text=True))
    review = "docs/vm_tlb/review_packs/"
    runtime = at(AUTHORITIES["runtime_qualification_commit"], review + "C16_STAGEA_RUNTIME_QUALIFICATION_CANARY_109_V1/FINAL_DECISION.json")
    diagnostic = at(AUTHORITIES["olmoe_diagnostic_commit"], review + "C16_OLMOE_GRAPH_OFF_ON_CORRECTNESS_DIAGNOSTIC_174NEW_V1/FINAL_DECISION.json")
    observer = at(AUTHORITIES["observer_v2_source_commit"], review + "C16_STAGEA_LOW_OVERHEAD_OBSERVER_V2_SOURCE_QUALIFICATION_109_V1/FINAL_DECISION.json")
    assert runtime["target_readiness"]["QWEN_BF16"]["ready"] is True
    assert runtime["target_readiness"]["QWEN_AWQ"]["blocker"] == "INSTRUMENTATION_NON_NEUTRAL"
    assert runtime["target_readiness"]["OLMOE"]["blocker"] == "CORRECTNESS_OR_BACKEND_IDENTITY_FAILED"
    assert diagnostic["status"] == "OLMOE_GRAPH_MODE_EXPERT_SET_DIVERGENCE"
    assert diagnostic["order_only_swap_events"] == 1599 and diagnostic["expert_set_substitution_events"] == 616
    assert diagnostic["structure_shift_events"] == 0
    assert diagnostic["logprob_outside_original_tolerance_steps"] == ["D1", "D4", "D6", "D23", "D29"]
    assert observer["runtime_neutrality_proven"] is False
    print("PASS: authority objects, JSON/TSV schema, static branches, exclusions, thresholds, and non-execution")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"FAIL: {error}", file=sys.stderr)
        raise
