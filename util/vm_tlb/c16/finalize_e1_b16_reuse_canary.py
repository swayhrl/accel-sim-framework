#!/usr/bin/env python3
"""Fail-closed publication organizer for the C16 E1 B16 reuse canary.

This tool does not recompute scientific results.  It validates the complete set
of analyzer outputs and the controller receipt, then creates the small,
deterministic publication layer in the review pack.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import tempfile


class ContractError(ValueError):
    """The final publication contract is incomplete or internally inconsistent."""


ANALYZER_FILES = {
    "CORRECTNESS_COMPARISON.json": "C16_E1_B16_REUSE_CORRECTNESS_V1",
    "B16_REUSE_WINDOW_PERFORMANCE.json": "C16_E1_B16_REUSE_PERFORMANCE_V1",
    "REPRODUCIBILITY.json": "C16_E1_B16_REUSE_REPRODUCIBILITY_V1",
    "B16_MECHANISM_ACTIVATION.json": "C16_E1_B16_MECHANISM_ACTIVATION_V1",
    "RAW_OUTPUT_INDEX.json": "C16_E1_B16_REUSE_RAW_OUTPUT_INDEX_V1",
    "RUN_RECEIPTS.json": "C16_E1_B16_REUSE_RUN_RECEIPTS_V1",
    "FINAL_DECISION.json": "C16_E1_B16_REUSE_FINAL_DECISION_V1",
}
AUTHORITY_JSON_FILES = {
    "REUSE_WINDOW_SCOPE.json": ("C16_E1_B16_REUSE_WINDOW_SCOPE_V1", "PASS"),
    "RUN_MATRIX.json": ("C16_E1_B16_REUSE_RUN_MATRIX_V1", "PASS"),
    "HOST_SCALE_AND_TELEMETRY_QUALIFICATION.json": (
        "C16_E1_B16_REUSE_HOST_SCALE_AND_TELEMETRY_QUALIFICATION_V1", "PASS"),
    "BOUNDED_REPRODUCIBILITY_PREFIX_UID168.json": (
        "C16_E1_B16_BOUNDED_REPRODUCIBILITY_PREFIX_V1", "PASS"),
    "PRIMARY_DIAGNOSTIC_ADMISSION_GATE.json": (
        "C16_E1_B16_PRIMARY_DIAGNOSTIC_ADMISSION_GATE_V1", "PASS"),
    "M1_B16_DIAGNOSTIC_ADMISSION_STATUS.json": (
        "C16_E1_B16_DIAGNOSTIC_ADMISSION_STATUS_V1", "ADMITTED_PRIMARY_GATES_PASS"),
}
CONFIG_FILES = {
    "R0_BASELINE": "configs/R0_BASELINE.gpgpusim.config",
    "M1_B16": "configs/M1_B16.gpgpusim.config",
    "M1_B16_DIAGNOSTIC": "configs/M1_B16_DIAGNOSTIC.gpgpusim.config",
}
TRACE_CONFIG_FILE = "configs/SM89_RTX4080_AWMA_V1.trace.config"
SEQUENCE_FILE = "REUSE_WINDOW_SEQUENCE.tsv"
RAW_OUTPUT_MEMBERS = {
    "simulator.stdout", "simulator.stderr", "TIME.txt", "COMMAND.txt",
    "LAUNCH_AUTHORITY.json", "RUN_RECEIPT.json",
}
DIAGNOSTIC_FILE = "DIAGNOSTIC_COUNTERS.json"
FOLLOWUP_SCHEMA = "C16_E1_B16_REUSE_FOLLOWUP_RECEIPT_V2"
STAGE_LABEL = "C16_E1_ORACLE_ELASTIC_B16_REUSE_CANARY_COMPLETE_V1"
REPRODUCIBILITY_CLAIM = "BOUNDED_REPRODUCIBILITY_PREFIX_PASS_UID168"
METRICS = ("C_window", "C_D2_prefix", "C_L0_up_D2")
CONDITIONS = (
    "R0_BASELINE",
    "M1_B16",
    "M1_B16_DIAGNOSTIC",
    "R0_BASELINE_REPEAT_BOUNDED",
)


def require(value: bool, message: str) -> None:
    if not value:
        raise ContractError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path):
    require(path.is_file() and path.stat().st_size > 0, f"missing/nonempty JSON: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ContractError(f"invalid JSON: {path}: {error}") from error


def require_regular(path: Path, label: str, allow_empty: bool = False) -> None:
    require(not path.is_symlink(), f"{label} is a symlink: {path}")
    require(path.is_file(), f"missing {label}: {path}")
    require(allow_empty or path.stat().st_size > 0, f"empty {label}: {path}")


def prevalidate_pack(pack: Path, followup_path: Path, write_sums: bool) -> None:
    require(pack.is_dir() and not pack.is_symlink(), f"invalid review pack: {pack}")
    for path in pack.rglob("*"):
        require(not path.is_symlink(),
                f"review pack symlink is forbidden: {path.relative_to(pack).as_posix()}")
    required = set(ANALYZER_FILES) | set(AUTHORITY_JSON_FILES) | {
        DIAGNOSTIC_FILE, SEQUENCE_FILE, TRACE_CONFIG_FILE, "PREFLIGHT.json",
        *CONFIG_FILES.values(),
    }
    for relative in sorted(required):
        require_regular(pack / relative, f"required publication input {relative}")
    require_regular(followup_path, "source follow-up receipt")
    for relative in ("README.md", "VALIDATION_SUMMARY.json", "FOLLOWUP_RECEIPT.json"):
        path = pack / relative
        require(not path.exists() or path.is_file(), f"publication target is not a file: {path}")
    if write_sums:
        path = pack / "SHA256SUMS"
        require(not path.exists() or path.is_file(), f"SHA target is not a file: {path}")


def finite_number(value, label: str) -> float:
    require(isinstance(value, (int, float)) and not isinstance(value, bool),
            f"{label} is not numeric")
    require(math.isfinite(value), f"{label} is not finite")
    return float(value)


def validate_response(metric: str, row: dict) -> None:
    require(isinstance(row, dict), f"{metric} response is not an object")
    baseline = finite_number(row.get("R0_cycles"), f"{metric}.R0_cycles")
    candidate = finite_number(row.get("M1_cycles"), f"{metric}.M1_cycles")
    delta = finite_number(row.get("R0_minus_M1_cycles"), f"{metric}.delta")
    fraction = finite_number(row.get("response_fraction"), f"{metric}.fraction")
    percent = finite_number(row.get("response_percent"), f"{metric}.percent")
    require(baseline > 0, f"{metric} baseline is not positive")
    require(delta == baseline - candidate, f"{metric} cycle delta drift")
    expected = delta / baseline
    require(math.isclose(fraction, expected, rel_tol=1e-15, abs_tol=1e-15),
            f"{metric} response fraction drift")
    require(math.isclose(percent, expected * 100.0, rel_tol=1e-15, abs_tol=1e-13),
            f"{metric} response percent drift")


def validate_authorities(pack: Path) -> dict:
    authorities = {}
    for name, (schema, status) in AUTHORITY_JSON_FILES.items():
        document = load_json(pack / name)
        require(document.get("schema") == schema, f"{name} schema drift")
        require(document.get("status") == status, f"{name} status drift")
        authorities[name] = document
    preflight = load_json(pack / "PREFLIGHT.json")
    require(preflight.get("status") == "PASS", "PREFLIGHT.json is not PASS")
    authorities["PREFLIGHT.json"] = preflight

    scope = authorities["REUSE_WINDOW_SCOPE.json"]
    require(scope.get("total_kernel_count") == 1565 and scope.get("thread_blocks") == 1259187,
            "scope kernel/CTA authority drift")
    require(scope.get("D1_complete") is True and scope.get("D2_prefix_complete") is True,
            "scope reuse window is incomplete")
    require(sha256(pack / SEQUENCE_FILE) == scope.get("selected_sequence_sha256"),
            "reuse sequence SHA drift")

    matrix = authorities["RUN_MATRIX.json"]
    require(matrix.get("trace_scope_sha256") == sha256(pack / "REUSE_WINDOW_SCOPE.json"),
            "run matrix scope SHA drift")
    require(matrix.get("trace_config_sha256") == sha256(pack / TRACE_CONFIG_FILE),
            "trace config SHA drift")
    runs = matrix.get("runs")
    require(isinstance(runs, dict) and set(runs) == set(CONFIG_FILES),
            "run matrix condition drift")
    for condition, relative in CONFIG_FILES.items():
        row = runs[condition]
        require(row.get("condition") == condition, f"run matrix condition mismatch: {condition}")
        require(row.get("config_sha256") == sha256(pack / relative),
                f"{condition} config SHA drift")
        require(Path(str(row.get("config", ""))).name == Path(relative).name,
                f"{condition} config authority path drift")
    require(runs["R0_BASELINE"].get("primary_performance_authority") is True and
            runs["M1_B16"].get("primary_performance_authority") is True and
            runs["M1_B16_DIAGNOSTIC"].get("diagnostic_only") is True,
            "run matrix role drift")

    bounded = authorities["BOUNDED_REPRODUCIBILITY_PREFIX_UID168.json"]
    require(bounded.get("claim") == REPRODUCIBILITY_CLAIM and
            bounded.get("bounded_prefix_last_uid") == 168 and
            bounded.get("full_1565_kernel_repeat_claimed") is False,
            "bounded evidence authority drift")
    gate = authorities["PRIMARY_DIAGNOSTIC_ADMISSION_GATE.json"]
    for key in ("primary_terminal_PASS", "primary_launch_authority_PASS",
                "primary_full_window_kernel_identity_PASS",
                "primary_per_UID_instruction_CTA_identity_PASS",
                "primary_correctness_comparison_PASS"):
        require(gate.get(key) is True, f"primary admission gate failed: {key}")
    require(gate.get("kernel_count") == scope["total_kernel_count"],
            "primary gate/scope kernel count drift")
    admission = authorities["M1_B16_DIAGNOSTIC_ADMISSION_STATUS.json"]
    require(admission.get("scientific_admission") == "ADMITTED" and
            admission.get("primary_terminal_PASS") is True and
            admission.get("primary_workload_kernel_instruction_CTA_identity") is True and
            admission.get("primary_correctness_comparison") is True,
            "diagnostic scientific admission did not close")
    return authorities


def valid_sha(value) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value)


def validate_raw_evidence(raw_runs: dict, receipt_runs: dict, correctness_runs: dict,
                          performance: dict) -> None:
    for condition in CONDITIONS:
        raw = raw_runs[condition]
        receipt = receipt_runs[condition]
        require(isinstance(raw, dict) and raw.get("status") == "PASS" and
                raw.get("condition") == condition, f"empty/failed raw summary: {condition}")
        require(isinstance(receipt, dict) and receipt, f"empty receipt summary: {condition}")
        for field in ("run_dir", "receipt_sha256", "output_manifest_sha256",
                      "stdout_sha256", "stderr_sha256", "kernel_sequence_sha256"):
            require(raw.get(field), f"{condition} raw field missing: {field}")
        for field in ("receipt_sha256", "output_manifest_sha256", "stdout_sha256",
                      "stderr_sha256", "kernel_sequence_sha256"):
            require(valid_sha(raw[field]), f"{condition} invalid SHA: {field}")
        require(raw["receipt_sha256"] == receipt.get("receipt_sha256") and
                raw["output_manifest_sha256"] == receipt.get("output_manifest_sha256") and
                raw["run_dir"] == receipt.get("run_dir"),
                f"{condition} raw/receipt authority mismatch")
        verified = raw.get("verified_output_sha256")
        require(isinstance(verified, dict) and set(verified) == RAW_OUTPUT_MEMBERS and
                all(valid_sha(value) for value in verified.values()),
                f"{condition} verified raw output matrix drift")
        require(verified == receipt.get("verified_output_sha256"),
                f"{condition} raw/receipt verified hash mismatch")
        require(raw.get("stderr_bytes") == 0, f"{condition} stderr is nonempty")
        require(isinstance(raw.get("kernel_count"), int) and raw["kernel_count"] > 0 and
                isinstance(raw.get("instruction_count"), int) and raw["instruction_count"] > 0 and
                isinstance(raw.get("CTA_count"), int) and raw["CTA_count"] > 0,
                f"{condition} raw scientific evidence is empty")
        run_dir = Path(raw["run_dir"])
        require(run_dir.is_absolute() and run_dir.is_dir() and not run_dir.is_symlink(),
                f"{condition} durable raw directory unavailable")
        for filename, expected in (("RUN_RECEIPT.json", raw["receipt_sha256"]),
                                   ("OUTPUT_SHA256SUMS", raw["output_manifest_sha256"])):
            candidate = run_dir / filename
            require_regular(candidate, f"{condition} raw {filename}")
            require(sha256(candidate) == expected, f"{condition} durable raw {filename} SHA drift")
        for filename, expected in verified.items():
            candidate = run_dir / filename
            require_regular(candidate, f"{condition} raw output {filename}",
                            allow_empty=filename == "simulator.stderr")
            require(sha256(candidate) == expected,
                    f"{condition} durable raw output SHA drift: {filename}")

    for condition in CONDITIONS[:3]:
        raw = raw_runs[condition]
        identity = correctness_runs[condition]
        for field in ("kernel_count", "kernel_sequence_sha256", "instruction_count", "CTA_count"):
            require(raw.get(field) == identity.get(field),
                    f"{condition} raw/correctness mismatch: {field}")
    for metric in METRICS:
        require(raw_runs["R0_BASELINE"]["cycles"].get(metric) ==
                performance["metrics"][metric]["R0_cycles"],
                f"{metric} R0 raw/performance mismatch")
        require(raw_runs["M1_B16"]["cycles"].get(metric) ==
                performance["metrics"][metric]["M1_cycles"],
                f"{metric} M1 raw/performance mismatch")


def recompute_interpretation(performance: dict, activation: dict) -> tuple[str, bool]:
    metrics = performance["metrics"]
    local = metrics["C_L0_up_D2"]["response_fraction"]
    window = metrics["C_window"]["response_fraction"]
    prefix = metrics["C_D2_prefix"]["response_fraction"]
    post = activation.get("D1_L0_class1_occupancy_after_fill")
    retained = activation.get("D1_L0_class1_occupancy_retained_before_D2_reuse")
    before = activation.get("checkpoints", {}).get("immediately_before_D2_L0_up", {})
    counters = before.get("counters", {}).get("sum", {})
    require(isinstance(post, int) and post >= 0 and isinstance(retained, int) and retained >= 0,
            "class-1 occupancy evidence missing")
    for key in ("target_protection_admission_denied", "normal_fallback_protected_victims"):
        require(isinstance(counters.get(key), int) and counters[key] >= 0,
                f"pre-D2 diagnostic counter missing: {key}")
    case4 = post > 0 and retained == 0 and (
        counters["target_protection_admission_denied"] > 0 or
        counters["normal_fallback_protected_victims"] > 0)
    if case4:
        return "CASE_4_EXACT_ZERO_RETENTION_WITH_OBSERVED_CONSTRAINT_EVENTS", True
    if local > 0 and window >= 0 and prefix >= 0:
        return "CASE_1_SIGNED_FIRST_MECHANISM_SIGNAL_POSITIVE", False
    if local > 0:
        return "CASE_2_RESIDENCY_RETAINED_BUT_COLLATERAL_PERSISTS", False
    return "CASE_3_RESIDENCY_ACTIVITY_WITHOUT_TARGET_LOCAL_TIMING_BENEFIT", False


def validate_external_test(path: Path | None):
    if path is None:
        return None
    require_regular(path, "external test summary")
    document = load_json(path)
    require(document.get("status") == "PASS", "external tests are not PASS")
    if "exit_code" in document:
        require(document["exit_code"] == 0, "external test exit code is nonzero")
    if "tests_failed" in document:
        require(document["tests_failed"] == 0, "external test failures are nonzero")
    return {"source": str(path), "sha256": sha256(path), "reported": document}


def validate_inputs(pack: Path, followup_path: Path,
                    external_test_summary: Path | None = None) -> tuple[dict, dict, dict, object]:
    authorities = validate_authorities(pack)
    documents = {}
    for name, schema in ANALYZER_FILES.items():
        document = load_json(pack / name)
        require(document.get("schema") == schema, f"{name} schema drift")
        require(document.get("status") == "PASS", f"{name} is not PASS")
        documents[name] = document

    diagnostics = load_json(pack / DIAGNOSTIC_FILE)
    require(isinstance(diagnostics, dict) and diagnostics,
            "diagnostic checkpoint output is empty")
    documents[DIAGNOSTIC_FILE] = diagnostics

    followup = load_json(followup_path)
    require(followup.get("schema") == FOLLOWUP_SCHEMA, "follow-up receipt schema drift")
    require(followup.get("status") == "PASS", "follow-up controller is not PASS")
    for key in ("diagnostic_exit_code", "bounded_repeat_exit_code", "analysis_exit_code"):
        require(followup.get(key) == 0, f"follow-up {key} is not zero")
    require(followup.get("reproducibility_claim") == REPRODUCIBILITY_CLAIM,
            "follow-up reproducibility claim drift")

    correctness = documents["CORRECTNESS_COMPARISON.json"]
    require(correctness.get("R0_M1_equal") is True, "primary correctness did not close")
    require(correctness.get("primary_and_diagnostic_natural_termination") is True,
            "primary/diagnostic natural termination did not close")
    require(correctness.get("full_expected_kernel_sequence_and_completion_coverage") is True,
            "full completion coverage did not close")
    require(correctness.get("verified_simulator_stderr_empty") is True,
            "simulator stderr is not qualified empty")
    runs = correctness.get("runs")
    require(isinstance(runs, dict) and set(runs) == set(CONDITIONS[:3]),
            "correctness run matrix drift")
    reference = runs["R0_BASELINE"]
    for condition in CONDITIONS[1:3]:
        require(runs[condition] == reference, f"{condition} workload identity drift")

    performance = documents["B16_REUSE_WINDOW_PERFORMANCE.json"]
    require(performance.get("primary_authority") == ["R0_BASELINE", "M1_B16"],
            "performance authority drift")
    require(performance.get("diagnostic_excluded_from_primary_performance") is True,
            "diagnostic leaked into performance authority")
    metrics = performance.get("metrics")
    require(isinstance(metrics, dict) and set(metrics) == set(METRICS),
            "performance metric matrix drift")
    for metric in METRICS:
        validate_response(metric, metrics[metric])

    reproducibility = documents["REPRODUCIBILITY.json"]
    require(reproducibility.get("reproducibility_claim") == REPRODUCIBILITY_CLAIM,
            "analyzer reproducibility claim drift")
    require(reproducibility.get("bounded_prefix_last_uid") == 168,
            "bounded repeat endpoint drift")
    require(reproducibility.get("full_window_repeat_claimed") is False,
            "full-window repeat was incorrectly claimed")
    for key in ("exact_cycle_instruction_CTA_kernel_reproduction",
                "M1_diagnostics_real_trace_neutral",
                "M1_diagnostics_per_UID_cycle_instruction_CTA_exact",
                "M1_diagnostics_kernel_identity_exact"):
        require(reproducibility.get(key) is True, f"reproducibility gate failed: {key}")
    coverage = reproducibility.get("diagnostic_coverage", {})
    require(coverage.get("UID_count") == 1565 and
            coverage.get("instance_count_per_UID") == 16 and
            coverage.get("counter_row_count") == 25040 and
            coverage.get("class_row_count") == 25040 and
            coverage.get("counter_schema_exact") is True and
            coverage.get("class_schema_exact") is True and
            coverage.get("class_sum_equals_occupancy_all_UIDs") is True,
            "exact diagnostic coverage did not close")

    activation = documents["B16_MECHANISM_ACTIVATION.json"]
    for key in ("mechanism_activated", "target_accesses_nonzero", "protected_fills_nonzero"):
        require(activation.get(key) is True, f"mechanism activation gate failed: {key}")
    require(activation.get("checkpoints") == diagnostics,
            "diagnostic checkpoint copy drift")
    require(set(diagnostics) == {"after_D1_L0_up", "after_D1_complete",
                                 "immediately_before_D2_L0_up", "after_D2_L0_up"},
            "diagnostic checkpoint matrix drift")

    raw = documents["RAW_OUTPUT_INDEX.json"].get("runs")
    require(isinstance(raw, dict) and set(raw) == set(CONDITIONS),
            "raw output run matrix drift")
    receipts = documents["RUN_RECEIPTS.json"]
    require(set(receipts.get("runs", {})) == set(CONDITIONS),
            "receipt run matrix drift")
    require(receipts.get("primary_and_diagnostic_natural_terminal") is True,
            "natural terminal receipt gate failed")
    bounded = receipts.get("bounded_repeat_scope", {})
    require(bounded.get("claim") == REPRODUCIBILITY_CLAIM and
            bounded.get("intentional_exit_code") == 143 and
            bounded.get("terminal_exit_detected") is False and
            bounded.get("full_window_repeat_claimed") is False,
            "bounded repeat receipt semantics drift")
    validate_raw_evidence(raw, receipts["runs"], runs, performance)

    final = documents["FINAL_DECISION.json"]
    require(final.get("stage_label") == STAGE_LABEL, "final stage label drift")
    for key in ("mechanism_activated", "correctness_qualified",
                "reproducibility_qualified", "diagnostic_neutrality_qualified",
                "not_whole_model_or_system_speedup", "no_budget_matrix_or_promotion_decision"):
        require(final.get(key) is True, f"final decision gate failed: {key}")
    require(isinstance(final.get("interpretation"), str) and final["interpretation"].startswith("CASE_"),
            "final interpretation is missing")
    interpretation, case4 = recompute_interpretation(performance, activation)
    require(final["interpretation"] == interpretation, "final interpretation recomputation drift")
    require(final.get("case4_exact_zero_retention_subset_satisfied") is case4,
            "final Case4 exact-subset flag drift")
    require(final.get("case4_qualitative_threshold_not_invented") is True,
            "Case4 qualitative-threshold caveat missing")
    subset = activation.get("case4_exact_zero_retention_subset", {})
    require(subset.get("satisfied") is case4 and
            subset.get("not_a_numeric_definition_of_qualitative_almost_or_large") is True,
            "activation Case4 caveat drift")
    external = validate_external_test(external_test_summary)
    return documents, followup, authorities, external


def json_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def render_readme(documents: dict, external_test) -> bytes:
    final = documents["FINAL_DECISION.json"]
    metrics = documents["B16_REUSE_WINDOW_PERFORMANCE.json"]["metrics"]
    activation = documents["B16_MECHANISM_ACTIVATION.json"]
    lines = [
        "# C16 E1 Oracle-Elastic B16 Reuse Performance Canary",
        "",
        f"Status: `{final['stage_label']}`",
        "",
        f"Interpretation: `{final['interpretation']}`",
        "",
        "## Independently validated results",
        "",
        "| Metric | R0 cycles | M1 cycles | R0-M1 cycles | Response |",
        "|---|---:|---:|---:|---:|",
    ]
    for metric in METRICS:
        row = metrics[metric]
        lines.append(
            f"| `{metric}` | {row['R0_cycles']} | {row['M1_cycles']} | "
            f"{row['R0_minus_M1_cycles']} | {row['response_percent']:.9f}% |"
        )
    case4 = final["case4_exact_zero_retention_subset_satisfied"]
    lines.extend([
        "",
        "## Qualification",
        "",
        "- R0 and M1 workload identity and correctness: PASS.",
        "- Mechanism activation and full diagnostic coverage: PASS.",
        "- M1 diagnostic neutrality, including per-UID cycles/instructions/CTA: PASS.",
        f"- Reproducibility: `{REPRODUCIBILITY_CLAIM}`; this is not a full-window repeat.",
        f"- D1 L0 class-1 occupancy after fill: {activation['D1_L0_class1_occupancy_after_fill']}.",
        f"- D1 L0 class-1 occupancy retained immediately before D2 reuse: "
        f"{activation['D1_L0_class1_occupancy_retained_before_D2_reuse']}.",
        f"- Exact diagnostic coverage: 1,565 UIDs x 16 L2 instances = 25,040 counter "
        "rows and 25,040 class-occupancy rows.",
        f"- External test summary supplied to the publisher: {'yes (PASS)' if external_test else 'no'}.",
        "",
        "## Interpretation boundary",
        "",
        ("Case 4 is the exact zero-retention subset: class-1 occupancy was nonzero after the "
         "D1 fill, exactly zero immediately before D2 reuse, and a preregistered constraint "
         "counter was observed. This is not a numeric definition of qualitative words such as "
         "'almost' or 'large'." if case4 else
         "The Case 4 exact zero-retention subset was not satisfied. No post-hoc numeric "
         "definition of qualitative words such as 'almost' or 'large' is introduced."),
        "",
        "## Claim boundary",
        "",
        f"`{final['claim_boundary']}`. This pack does not claim whole-model/system speedup, "
        "does not provide a budget-matrix promotion decision, and does not begin a later mechanism stage.",
        "",
        "`VALIDATION_SUMMARY.json` records the fail-closed publication checks and input hashes. "
        "`FOLLOWUP_RECEIPT.json` is the byte-exact controller receipt.",
        "",
    ])
    return "\n".join(lines).encode("utf-8")


def build_summary(pack: Path, followup_path: Path, documents: dict,
                  authorities: dict, external_test) -> dict:
    final = documents["FINAL_DECISION.json"]
    performance = documents["B16_REUSE_WINDOW_PERFORMANCE.json"]
    inputs = {name: {"sha256": sha256(pack / name), "bytes": (pack / name).stat().st_size}
              for name in sorted(ANALYZER_FILES)}
    inputs[DIAGNOSTIC_FILE] = {
        "sha256": sha256(pack / DIAGNOSTIC_FILE),
        "bytes": (pack / DIAGNOSTIC_FILE).stat().st_size,
    }
    inputs["SOURCE_FOLLOWUP_RECEIPT.json"] = {
        "sha256": sha256(followup_path), "bytes": followup_path.stat().st_size,
    }
    for name in sorted(authorities):
        inputs[name] = {"sha256": sha256(pack / name), "bytes": (pack / name).stat().st_size}
    for relative in sorted((*CONFIG_FILES.values(), TRACE_CONFIG_FILE, SEQUENCE_FILE)):
        inputs[relative] = {
            "sha256": sha256(pack / relative), "bytes": (pack / relative).stat().st_size,
        }
    if external_test is not None:
        inputs["EXTERNAL_TEST_SUMMARY"] = {
            "source": external_test["source"], "sha256": external_test["sha256"],
            "reported": external_test["reported"],
        }
    return {
        "schema": "C16_E1_B16_REUSE_PUBLICATION_VALIDATION_V1",
        "status": "PASS",
        "stage_label": final["stage_label"],
        "interpretation": final["interpretation"],
        "claim_boundary": final["claim_boundary"],
        "performance_metrics": performance["metrics"],
        "validation": {
            "all_analyzer_outputs_present_nonempty_schema_exact_PASS": True,
            "followup_controller_PASS_all_exit_codes_zero": True,
            "primary_workload_and_correctness_identity_closed": True,
            "raw_output_and_receipt_condition_matrix_exact": True,
            "durable_raw_files_present_nonempty_and_SHA_verified": True,
            "required_source_authorities_configs_and_admission_gates_verified": True,
            "mechanism_activation_and_diagnostic_copy_closed": True,
            "diagnostic_coverage": {
                "UID_count": 1565, "instance_count_per_UID": 16,
                "counter_row_count": 25040, "class_row_count": 25040,
            },
            "diagnostic_neutrality_closed": True,
            "interpretation_recomputed_from_signed_metrics_and_diagnostics": True,
            "case4_qualitative_threshold_not_invented": True,
            "bounded_reproducibility_claim_only": REPRODUCIBILITY_CLAIM,
            "full_window_repeat_claimed": False,
            "external_test_summary_supplied": external_test is not None,
            "external_tests_claimed_PASS": external_test is not None,
        },
        "input_artifacts": dict(sorted(inputs.items())),
    }


def atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def recursive_sums(pack: Path, output_name: str = "SHA256SUMS") -> bytes:
    rows = []
    for path in sorted(pack.rglob("*"), key=lambda item: item.relative_to(pack).as_posix()):
        relative = path.relative_to(pack)
        require(not path.is_symlink(), f"review pack symlink is forbidden: {relative.as_posix()}")
        if not path.is_file() or relative.as_posix() == output_name:
            continue
        rows.append(f"{sha256(path)}  {relative.as_posix()}")
    require(rows, "cannot publish an empty SHA manifest")
    return ("\n".join(rows) + "\n").encode("utf-8")


def finalize(pack: Path, run_root: Path, write_sums: bool,
             external_test_summary: Path | None = None) -> dict:
    followup_path = run_root / "FOLLOWUP_RECEIPT.json"
    prevalidate_pack(pack, followup_path, write_sums)
    if external_test_summary is not None:
        require_regular(external_test_summary, "external test summary")
    documents, _, authorities, external = validate_inputs(
        pack, followup_path, external_test_summary)
    summary = build_summary(pack, followup_path, documents, authorities, external)
    readme = render_readme(documents, external)
    receipt = followup_path.read_bytes()

    # No publication file is touched before the entire input contract validates.
    atomic_write(pack / "README.md", readme)
    atomic_write(pack / "VALIDATION_SUMMARY.json", json_bytes(summary))
    atomic_write(pack / "FOLLOWUP_RECEIPT.json", receipt)
    require(sha256(pack / "FOLLOWUP_RECEIPT.json") == sha256(followup_path),
            "copied follow-up receipt SHA drift")
    if write_sums:
        atomic_write(pack / "SHA256SUMS", recursive_sums(pack))
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pack", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--write-sha256sums", action="store_true")
    parser.add_argument("--external-test-summary", type=Path,
                        help="optional JSON test receipt; must report PASS")
    args = parser.parse_args()
    summary = finalize(args.pack, args.run_root, args.write_sha256sums,
                       args.external_test_summary)
    print(json.dumps({
        "status": summary["status"],
        "stage_label": summary["stage_label"],
        "interpretation": summary["interpretation"],
        "sha256sums_written": args.write_sha256sums,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
