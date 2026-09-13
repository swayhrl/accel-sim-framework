#!/usr/bin/env python3
"""No-GPU contract tests for C16 Sampling V2."""
import importlib.util
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SPEC = importlib.util.spec_from_file_location("c16_sampling_v2", ROOT / "util/vm_tlb/c16/lane_c/c16_sampling_v2.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def unit(unit_id, operator, implementation, shape, dtype, duration, variation=0):
    return {
        "deployment_id": "Qwen2.5-0.5B", "scenario_id": "S1", "phase": "prefill", "operator_class": operator,
        "implementation_key": implementation, "shape_key": shape, "dtype_key": dtype, "duration_ns": str(duration),
        "variation_proxy": str(variation), "unit_id": unit_id, "launch_ordinal": unit_id, "grid": "(4,1,1)", "block": "(128,1,1)",
    }


rows = [
    unit("a", "MATMUL", "CUTLASS", "[1,128,4096]", "bf16", 100),
    unit("b", "MATMUL", "CUTLASS", "[1,128,4096]", "bf16", 20),
    unit("c", "MATMUL", "CUTLASS", "[1,128,4096]", "bf16", 20),
    unit("d", "SOFTMAX", "FLASH", "[1,32,128,128]", "bf16", 10),
    unit("e", "SOFTMAX", "FLASH", "[1,32,128,128]", "bf16", 10),
    unit("f", "KV", "KV_WRITE", "[1,32,128]", "bf16", 1),
]
# A non-certainty stratum ensures Selector-R has an actual finite-population
# sample rather than a degenerate all-certainty fixture.
rows.extend(unit(f"ordinary-{index}", "OTHER", "FUSED", "[1,1]", "bf16", 0.1) for index in range(100))
units = MODULE.annotate_certainty(MODULE.canonicalize_catalog(rows, "NATIVE_PROFILED"))

assert MODULE.shape_bucket("[1,128,4096]") == "R3_P2_0xP2_7xP2_12"
assert all(len(item["stratum_id"].split("|")) == 5 for item in units)
assert any(item["unit_id"] == "a" and item["certainty"] for item in units)  # >=1% phase time
assert any(item["unit_id"] == "f" and "SPECIAL_KV_MANAGEMENT" in item["certainty_reason"] for item in units)

r_plan, r_budget, _ = MODULE.build_plan(units, 12, "R", 16031)
m_plan, _, _ = MODULE.build_plan(units, 12, "M", 16031)
assert all(row["selector_kind"] == "SELECTOR_R" for row in r_plan)
assert all(row["selector_kind"] == "SELECTOR_M" for row in m_plan)
assert all(row["inclusion_probability"] != "NA" for row in r_plan)
assert all(row["design_confidence"] == "NOT_APPLICABLE_MEDOID" for row in m_plan if row["selection_role"] == "MEDOID")
assert all(row["design_confidence"] == "CERTAINTY_SELF_REPRESENTING" for row in m_plan if row["selection_role"] == "CERTAINTY")
assert r_budget and all(row["estimated_capture_cost_ns"] >= 0 for row in r_budget)

# Full census must conserve exactly even with a mix of certainty and ordinary
# rows.  In particular, certainty unit a must never receive N/n amplification.
full = []
for item in units:
    full.append({"stratum_id": item["stratum_id"], "unit_id": item["unit_id"], "selection_role": "CERTAINTY" if item["certainty"] else "PROBABILITY"})
values = {item["unit_id"]: index + 1 for index, item in enumerate(units)}
estimate = MODULE.estimate_additive(units, full, values)
assert estimate["estimate"] == estimate["exact"] == sum(values.values())

# A rate is reconstructed from totals, not by averaging the per-unit rates.
numerator = {"a": 1, "b": 0, "c": 1, "d": 0, "e": 0, "f": 0}
denominator = {"a": 1, "b": 100, "c": 1, "d": 100, "e": 100, "f": 100}
ratio = MODULE.estimate_ratio(units, full, numerator, denominator)
assert ratio["estimate"] == ratio["exact"] == sum(numerator.values()) / sum(denominator.values())

# Candidate outcomes are not read by plan construction: changing them cannot
# change membership, inclusion probabilities, or the frozen allocation.
altered = [dict(row, candidate_speedup="999999", candidate_miss="0") for row in rows]
again = MODULE.annotate_certainty(MODULE.canonicalize_catalog(altered, "NATIVE_PROFILED"))
again_plan, _, _ = MODULE.build_plan(again, 12, "R", 16031)
assert [(row["unit_id"], row["inclusion_probability"]) for row in r_plan] == [(row["unit_id"], row["inclusion_probability"]) for row in again_plan]

assert MODULE.split_role("Qwen2.5-7B-Instruct-AWQ") == "PROSPECTIVE_HOLDOUT"
assert MODULE.split_role("Qwen3-30B-A3B-MoE") == "STRUCTURAL_HOLDOUT"
assert MODULE.split_role("unknown-deployment") == "UNASSIGNED_EXCLUDED"

amendment = MODULE.capability_limited_train_roster_payload()
assert amendment["schema_version"] == MODULE.CAPABILITY_LIMITED_TRAIN_ROSTER_VERSION
assert amendment["scientific_scope"] == "NOT_FULL_ORIGINAL_TRAIN_ROSTER_COMPLETION"
assert [row["model"] for row in amendment["effective_train_tune"]] == ["Llama3.2-1B", "Qwen2.5-0.5B"]
assert amendment["unavailable"][0]["reason"] == "RESOURCE_UNAVAILABLE_ON_RTX3090"
assert amendment["unavailable"][0]["timing_result_emitted"] is False
assert amendment["prospective_holdout"][0]["outcomes_read"] is False

# P admission has a direct deployment roster, not a model-name or kernel-name
# guess.  UNKNOWN semantic coverage remains an ordinary explicit stratum.
p_catalog = [{
    "run_id": "p-run", "deployment_id": "opaque-deployment-id", "scenario_id": "S1", "phase": "prefill",
    "device": "GPU-0", "context": "1", "stream": "7", "correlation_id": "8", "launch_ordinal": "9",
    "kernel_name": "looks_like_kv_router_but_is_not_semantic_evidence", "implementation_key": "opaque-impl",
    "grid": "(1,1,1)", "block": "(128,1,1)", "start_ns": "0", "end_ns": "10", "duration_ns": "10",
    "operator_class": "UNKNOWN", "layer_id": "UNKNOWN", "shape_key": "[1,128]", "dtype_key": "bf16",
    "semantic_evidence": "UNKNOWN", "mapping_status": "UNKNOWN",
}]
p_roster = [{"deployment_id": "opaque-deployment-id", "c16_cohort": "TRAIN_LLAMA", "c16_split_role": "TUNING"},
            {"deployment_id": "opaque-qwen05", "c16_cohort": "TRAIN_QWEN0_5", "c16_split_role": "TUNING"}]
p_catalog += [{**p_catalog[0], "run_id": "p-run-qwen05", "deployment_id": "opaque-qwen05", "correlation_id": "10"},
]
p_profiles = [{"run_id": "p-run", "profile_report_id": "sha256:report"},
              {"run_id": "p-run-qwen05", "profile_report_id": "sha256:report-qwen05"}]
p_resource = [{"deployment_id": "opaque-deployment-id", "scenario_id": "S1", "admission_status": "ADMITTED"},
              {"deployment_id": "opaque-qwen05", "scenario_id": "S1", "admission_status": "ADMITTED"}]
p_audit, p_roles = MODULE.p_validate_catalog_and_roster(p_catalog, p_roster, p_profiles, p_resource, MODULE.P_TRAIN_COHORT)
assert p_audit["unknown_semantic_rows"] == "2"
assert p_audit["unknown_policy"] == "EXPLICIT_STRATUM_NO_KERNEL_NAME_HEURISTIC"
assert p_audit["resource_admitted_deployment_scenarios"] == "2"
assert p_roles["opaque-deployment-id"] == "TUNING"
p_units = MODULE.annotate_certainty(MODULE.canonicalize_catalog(p_catalog, "NATIVE_PROFILED"))
assert p_units[0]["operator_class"] == "UNKNOWN_OPERATOR"
assert "SPECIAL_KV_MANAGEMENT" not in p_units[0]["certainty_reason"]
with tempfile.TemporaryDirectory() as temporary:
    temporary_path = Path(temporary)
    MODULE.write_g_target_selection_policy(temporary_path)
    policy = json.loads((temporary_path / "G_TARGET_SELECTION_POLICY_V1.json").read_text())
    assert policy["PRIMARY_G_TARGET_SELECTOR"] == "SELECTOR_R"
    assert policy["PRIMARY_G_TARGET_BUDGET"] == "B48"
    assert policy["SELECTOR_M_ROLE"] == "AUXILIARY_REPRESENTATIVE_PLAN_NONBLOCKING"
    r_only = MODULE.write_p_plan_bundle(temporary_path, "R_ONLY", p_units, p_roles, MODULE.P_TRAIN_COHORT, selectors=("R",))
    assert r_only and {row["selector_kind"] for row in r_only} == {"SELECTOR_R"}
    assert (temporary_path / "R_ONLY_SELECTOR_M_DEFERRED.md").is_file()
    assert not (temporary_path / "R_ONLY_SELECTOR_M_PLAN.tsv").exists()
try:
    MODULE.p_validate_catalog_and_roster([{**p_catalog[0], "candidate_speedup": "999"}], p_roster, p_profiles, p_resource, MODULE.P_TRAIN_COHORT)
    raise AssertionError("P outcome fields must be rejected before selection")
except RuntimeError as exc:
    assert "forbidden outcome" in str(exc)
try:
    MODULE.p_validate_catalog_and_roster(p_catalog, p_roster, p_profiles,
                                         [{**p_resource[0], "admission_status": "SKIPPED_RESOURCE"}], MODULE.P_TRAIN_COHORT)
    raise AssertionError("non-admitted resource identity must not enter a targetable catalog")
except RuntimeError as exc:
    assert "RESOURCE_ADMISSION" in str(exc)

p_manifest = {
    "schema_version": MODULE.P_MANIFEST_SCHEMA, "status": MODULE.P_READY_STATUS,
    "capability_limited_train_roster_version": MODULE.CAPABILITY_LIMITED_TRAIN_ROSTER_VERSION,
    "unavailable_deployment_ids": [MODULE.QWEN7_RAW_DEPLOYMENT_ID],
    "hash_closure": {"status": "HASH_CLOSED", "producer_commits": ["a" * 40], "raw_artifacts": [{"path": "raw/report.nsys-rep", "size_bytes": 1, "sha256": "b" * 64}]},
    "files": [{"cohort": MODULE.P_TRAIN_COHORT, "kind": kind, "path": f"train/{kind}.tsv", "sha256": "c" * 64}
              for kind in MODULE.P_REQUIRED_PAYLOAD_KINDS],
}
assert set(MODULE.p_manifest_entries(p_manifest, MODULE.P_TRAIN_COHORT)) == set(MODULE.P_REQUIRED_PAYLOAD_KINDS)
p_manifest["status"] = "P_ORDINARY_MILESTONE"
try:
    MODULE.p_manifest_entries(p_manifest, MODULE.P_TRAIN_COHORT)
    raise AssertionError("ordinary P milestone must not be admitted")
except RuntimeError as exc:
    assert MODULE.P_READY_STATUS in str(exc)

# Post-freeze holdout evaluation only considers a declared holdout deployment,
# keeps a rate's numerator and denominator separate, and does not promote a
# structural page metric into an additive population estimate.
holdout_catalog = [
    {**unit("h1", "MATMUL", "CUTLASS", "[1,128,4096]", "bf16", 10), "deployment_id": "Qwen2.5-7B-Instruct-AWQ"},
    {**unit("h2", "MATMUL", "CUTLASS", "[1,128,4096]", "bf16", 20), "deployment_id": "Qwen2.5-7B-Instruct-AWQ"},
]
holdout_units = MODULE.annotate_certainty(MODULE.canonicalize_catalog(holdout_catalog, "NATIVE_PROFILED"))
holdout_plan, _, _ = MODULE.build_plan(holdout_units, 12, "R", 16031)
for row in holdout_plan:
    row["split_role"] = MODULE.split_role(row["deployment_id"])
metric_rows = []
for unit_id, value, numerator, denominator in (("h1", 10, 1, 1), ("h2", 20, 0, 2)):
    common = {"deployment_id": "Qwen2.5-7B-Instruct-AWQ", "scenario_id": "S1", "phase": "prefill", "unit_id": unit_id,
              "evidence_tier": "NATIVE_PROFILED", "target_identity_status": "EXACT", "ground_truth_scope": "FULL_FROZEN_UNIVERSE"}
    metric_rows += [
        {**common, "metric": "native_duration_total", "metric_kind": "ADDITIVE", "value": str(value)},
        {**common, "metric": "counter_miss_rate", "metric_kind": "RATE", "numerator": str(numerator), "denominator": str(denominator)},
        {**common, "metric": "observed_page_union", "metric_kind": "STRUCTURAL"},
    ]
results, qualifications = MODULE.evaluate_holdout(holdout_units, holdout_plan, metric_rows, {"producer_commit": "fixture", "payload_sha256": "fixture"})
by_metric = {row["metric"]: row for row in results}
assert by_metric["native_duration_total"]["qualification_status"] == "QUALIFIED"
assert by_metric["counter_miss_rate"]["estimate"] == 1 / 3
assert by_metric["observed_page_union"]["qualification_status"] == "STRUCTURAL_ONLY"
assert {row["status"] for row in qualifications} >= {"QUALIFIED", "SCREENING_ONLY", "STRUCTURAL_ONLY"}
print("PASS C16 Lane C Sampling V2 no-GPU contract tests")
