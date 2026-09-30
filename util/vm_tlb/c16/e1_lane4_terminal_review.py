#!/usr/bin/env python3
"""CPU-only, read-only terminal review of a committed Lane 4 publication packet.

This module never opens simulator run directories and never publishes a paper
result row. Numeric A/B/C/D thresholds are intentionally absent from V1.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PACK_ROOT = Path("docs/vm_tlb/review_packs")
PACKET_NAME = "TERMINAL_REVIEW_PACKET.json"
INPUT_SCHEMA = "C16_LANE4_TERMINAL_GATE_INPUT_V1"
OUTPUT_SCHEMA = "C16_LANE4_TERMINAL_GATE_REVIEW_V1"

AUTHORITY = {
    "lane3_commit": "a402828860ced26124ddbf3c9d87baa6f6774d55",
    "literature_commit": "350e4a0d364d65812f379ebc69412696e2a4d82a",
    "lane4_framework_snapshot": "8dfd9c0fdc98314c2aa11710da9b89f59e4c7a66",
    "core_commit": "0271de82432db004beed43280ed01057246a0f2c",
}
IDENTITY = {
    "run_matrix_sha256": "b1d0610a79cecea552502b9c3f8e06ba679cdd965170e39b3068ac12848e0d20",
    "binary_sha256": "6be0986958ffbb8a128ce19e8a88b53a4c4838f97202c2f3d1c9dec6e9a02186",
    "r0_config_sha256": "a8918f1407fc2a9146808625b55a5120f64bb2cf4ce8b6a5b399ac4654d36d96",
    "m1_b16_config_sha256": "15e06af19200e7fb40af93c6a21b19290b581c327f420dd3fdefc3f4b3af3bdd",
    "diagnostic_config_sha256": "12434fee397093b2ac13cf65e1b2644b8f7a98ad97e3824a2cbfae5aba5daee7",
    "kernelslist_sha256": "f9a952e2d52420a850dc28554be208a2dd1d7894260d8bff87153637740a5ae8",
    "platform_sha256": "de9ee8f30325c033e0de624640ffa8803f0eae40633eebaa0b3144f549f5ccb8",
    "sidecar_sha256": "6c60839714d136b9f6f596218588e658e245e0b7cc6f8e8550cce8d683ce13c6",
    "trace_scope_sha256": "3861e58b45851e1aa94660d2473df2ee475a9135d9c475724d07010ed529ce31",
    "reuse_sequence_sha256": "c3bb16d8f40eabdd09c165c7ff7c31ad2ce7aac2f5b7548a639d87dec493a6be",
    "source_manifest_sha256": "db3bdbb0295a47a6aa4644508ea1895779c987f2f77cd96f184c67b8a10ab389",
    "total_kernels": 1565,
}
SCOPE = {
    "first_dynamic_kernel": 2926,
    "D1_last_kernel": 4430,
    "D2_prefix_last_kernel": 4490,
    "last_dynamic_kernel": 4490,
    "D1_kernel_count": 1505,
    "D2_prefix_kernel_count": 60,
    "total_kernel_count": 1565,
    "thread_blocks": 1259187,
}
WINDOWS = ("C_window", "C_D2_prefix", "C_L0_up_D2")
CASES = ("A", "B", "C", "D")


class ReviewError(ValueError):
    def __init__(self, code: str, detail: str):
        super().__init__(f"{code}: {detail}")
        self.code = code


def obj(parent: dict, key: str) -> dict:
    value = parent.get(key)
    if not isinstance(value, dict):
        raise ReviewError("PARTIAL_PACKET", f"missing object {key}")
    return value


def keys(value: dict, required: set[str], optional: set[str] | None = None) -> None:
    optional = optional or set()
    if not required.issubset(value) or not set(value).issubset(required | optional):
        raise ReviewError("SCHEMA_DRIFT", "missing or unrecognized packet fields")


def integer(parent: dict, key: str, *, positive: bool = False) -> int:
    value = parent.get(key)
    if type(value) is not int or value < (1 if positive else 0):
        raise ReviewError("INVALID_METRIC", f"{key} must be a nonnegative integer" if not positive
                          else f"{key} must be a positive integer")
    return value


def sha(parent: dict, key: str) -> str:
    value = parent.get(key)
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
        raise ReviewError("MISSING_SOURCE_SHA", key)
    return value


def exact(parent: dict, expected: dict, code: str) -> None:
    for key, value in expected.items():
        if parent.get(key) != value:
            raise ReviewError(code, f"{key}: expected frozen authority")


def receipt(receipts: dict, name: str) -> dict:
    value = receipts.get(name)
    if not isinstance(value, dict):
        raise ReviewError("MISSING_TERMINAL_RECEIPT", name)
    keys(value, {"status", "exit_code", "terminal_marker", "receipt_sha256"})
    sha(value, "receipt_sha256")
    if value.get("status") not in ("PASS", "FAIL") or type(value.get("exit_code")) is not int or type(value.get("terminal_marker")) is not bool:
        raise ReviewError("INVALID_TERMINAL_RECEIPT", name)
    return value


def pending_cases() -> dict[str, str]:
    return {case: "REQUIRES_PROJECT_REVIEW" for case in CASES}


def failed(stage: str, reason: str) -> dict:
    return {"schema": OUTPUT_SCHEMA, "status": "PRIMARY_FAILED", "failed_stage": stage,
            "reason": reason, "diagnostic_admission": "QUARANTINE_DIAGNOSTIC",
            "normalized_metrics": {}, "candidate_interpretation": [],
            "ABCD": pending_cases(), "project_level_interpretation": "NO_SCIENTIFIC_DECISION",
            "scientific_result_row_generated": False}


def normalize_counters(counters: dict) -> dict:
    names = ("target_accesses", "protected_fills", "protected_protected_evictions",
             "protected_victim_evictions", "eligible_target_fills",
             "quota_denials_invalid_priority", "quota_denials_no_local_protected_victim",
             "D1_class1_after_fill", "D1_class1_before_D2")
    keys(counters, set(names), {"old_address_survivors", "old_address_population"})
    values = {name: integer(counters, name) for name in names}
    if values["protected_protected_evictions"] > values["protected_victim_evictions"]:
        raise ReviewError("INVALID_METRIC", "protected churn exceeds protected victims")
    if values["protected_fills"] > values["eligible_target_fills"]:
        raise ReviewError("INVALID_METRIC", "protected fills exceed eligible fills")
    for name in ("old_address_survivors", "old_address_population"):
        value = counters.get(name)
        if value is not None and (type(value) is not int or value < 0):
            raise ReviewError("INVALID_METRIC", name)
        values[name] = value
    if (values["old_address_survivors"] is None) != (values["old_address_population"] is None):
        raise ReviewError("INVALID_METRIC", "old-address fields must be present together")
    if values["old_address_survivors"] is not None and values["old_address_survivors"] > values["old_address_population"]:
        raise ReviewError("INVALID_METRIC", "old-address survivors exceed population")

    def fraction(numerator: int | None, denominator: int | None):
        return numerator / denominator if numerator is not None and denominator else None

    return {
        "raw_counters": values,
        "protected_to_protected_churn_fraction": fraction(values["protected_protected_evictions"], values["protected_victim_evictions"]),
        "class1_occupancy_retention_fraction": fraction(values["D1_class1_before_D2"], values["D1_class1_after_fill"]),
        "old_address_survival_fraction": fraction(values["old_address_survivors"], values["old_address_population"]),
        "protected_admission_fraction": fraction(values["protected_fills"], values["eligible_target_fills"]),
        "invalid_priority_denial_fraction": fraction(values["quota_denials_invalid_priority"], values["eligible_target_fills"]),
        "no_local_protected_victim_denial_fraction": fraction(values["quota_denials_no_local_protected_victim"], values["eligible_target_fills"]),
    }


def classify_synthetic_signals(signals: dict[str, bool]) -> str:
    """Exercise preregistered routing with already classified *synthetic* signals.

    Production evaluation does not call this function: no frozen numeric high/low
    thresholds exist in the inspected Lane 4 design snapshot.
    """
    expected = {"high_churn", "low_old_survival", "good_old_survival",
                "local_positive", "window_positive", "denial_dominant",
                "target_protection_low"}
    if set(signals) != expected or any(type(v) is not bool for v in signals.values()):
        raise ReviewError("INVALID_SYNTHETIC_SIGNALS", "exact boolean signal set required")
    if signals["low_old_survival"] and signals["good_old_survival"]:
        raise ReviewError("INVALID_SYNTHETIC_SIGNALS", "survival signals conflict")
    matches = []
    if signals["denial_dominant"] and signals["target_protection_low"]:
        matches.append("D")
    if signals["high_churn"] and signals["low_old_survival"]:
        matches.append("A")
    if signals["good_old_survival"] and signals["local_positive"] and signals["window_positive"]:
        matches.append("C")
    if (not signals["high_churn"] and signals["good_old_survival"] and
            not signals["local_positive"] and not signals["window_positive"]):
        matches.append("B")
    return matches[0] if len(matches) == 1 else "REQUIRES_PROJECT_REVIEW"


def evaluate(packet: dict) -> dict:
    if not isinstance(packet, dict) or packet.get("schema") != INPUT_SCHEMA or packet.get("publication_status") != "TERMINAL_REVIEW_READY":
        raise ReviewError("PARTIAL_REJECTED", "packet lacks final publication schema/status")
    keys(packet, {"schema", "publication_status", "authority", "identity", "terminal_receipts"},
         {"reuse_window_scope", "workload_identity", "primary_correctness",
          "primary_timing", "diagnostic"})
    authority = obj(packet, "authority")
    keys(authority, set(AUTHORITY))
    exact(authority, AUTHORITY, "SOURCE_AUTHORITY_MISMATCH")
    identity = obj(packet, "identity")
    keys(identity, set(IDENTITY))
    exact(identity, IDENTITY, "IDENTITY_MISMATCH")

    receipts = obj(packet, "terminal_receipts")
    for primary in ("R0_BASELINE", "M1_B16"):
        if primary not in receipts:
            raise ReviewError("MISSING_TERMINAL_RECEIPT", primary)
    keys(receipts, {"R0_BASELINE", "M1_B16"}, {"M1_B16_DIAGNOSTIC"})
    r0 = receipt(receipts, "R0_BASELINE")
    m1 = receipt(receipts, "M1_B16")
    if any(r["status"] != "PASS" or r["exit_code"] != 0 or r["terminal_marker"] is not True for r in (r0, m1)):
        return failed("primary terminal receipt", "R0/M1 did not both terminate PASS")

    scope = obj(packet, "reuse_window_scope")
    keys(scope, set(SCOPE) | {"status", "no_kernel_filtering_or_reordering",
                             "selected_sequence_sha256"})
    exact(scope, SCOPE, "SCOPE_MISMATCH")
    if scope.get("status") != "PASS" or scope.get("no_kernel_filtering_or_reordering") is not True or scope.get("selected_sequence_sha256") != IDENTITY["reuse_sequence_sha256"]:
        raise ReviewError("SCOPE_MISMATCH", "reuse window not exactly closed")

    workload = obj(packet, "workload_identity")
    keys(workload, {"R0_BASELINE", "M1_B16"})
    r0_workload = obj(workload, "R0_BASELINE")
    m1_workload = obj(workload, "M1_B16")
    for row in (r0_workload, m1_workload):
        keys(row, {"kernel_count", "kernel_sequence_sha256", "instruction_count", "CTA_count"})
        if integer(row, "kernel_count") != IDENTITY["total_kernels"] or integer(row, "CTA_count") != SCOPE["thread_blocks"]:
            return failed("primary workload identity", "kernel/CTA count mismatch")
        integer(row, "instruction_count", positive=True)
        sha(row, "kernel_sequence_sha256")
    if any(r0_workload[key] != m1_workload[key] for key in
           ("kernel_count", "kernel_sequence_sha256", "instruction_count", "CTA_count")):
        return failed("primary workload identity", "R0/M1 workload fields differ")

    correctness = obj(packet, "primary_correctness")
    keys(correctness, {"status", "R0_M1_equal", "comparison_sha256"})
    sha(correctness, "comparison_sha256")
    if correctness.get("status") != "PASS" or correctness.get("R0_M1_equal") is not True:
        return failed("primary correctness", "R0/M1 comparison not PASS")

    timing = obj(packet, "primary_timing")
    keys(timing, {"status", "performance_sha256", "cycles"})
    sha(timing, "performance_sha256")
    if timing.get("status") != "PASS":
        raise ReviewError("PARTIAL_PRIMARY_TIMING", "primary timing lacks accepted status")
    cycles = obj(timing, "cycles")
    keys(cycles, set(WINDOWS))
    normalized = {}
    for window in WINDOWS:
        pair = obj(cycles, window)
        keys(pair, {"R0_cycles", "M1_cycles"})
        baseline = integer(pair, "R0_cycles", positive=True)
        candidate = integer(pair, "M1_cycles", positive=True)
        normalized[window] = {"R0_cycles": baseline, "M1_cycles": candidate,
                              "R0_minus_M1_cycles": baseline - candidate,
                              "response_fraction": (baseline - candidate) / baseline}

    result = {"schema": OUTPUT_SCHEMA, "status": "PRIMARY_REVIEW_READY",
              "review_order_completed": ["Git/source authority", "binary/config/trace identity",
                                         "terminal receipt", "exact reuse-window scope closure",
                                         "R0/M1 workload identity", "primary correctness",
                                         "primary timing interpretation"],
              "normalized_metrics": {"primary_timing": normalized},
              "diagnostic_admission": "PENDING_DIAGNOSTIC_TERMINAL",
              "candidate_interpretation": [], "ABCD": pending_cases(),
              "project_level_interpretation": "REQUIRES_PROJECT_REVIEW",
              "scientific_result_row_generated": False}

    diagnostic = packet.get("diagnostic")
    if diagnostic is None:
        return result
    if not isinstance(diagnostic, dict) or diagnostic.get("pre_gate_status") != "SPECULATIVE_PRE_GATE":
        raise ReviewError("INVALID_DIAGNOSTIC", "expected speculative pre-gate source")
    keys(diagnostic, {"pre_gate_status", "neutrality_status", "counters_status",
                      "diagnostic_sha256"}, {"counters"})
    diag_receipt = receipt(receipts, "M1_B16_DIAGNOSTIC")
    if (diag_receipt["status"] != "PASS" or diag_receipt["exit_code"] != 0 or
            diag_receipt["terminal_marker"] is not True or
            diagnostic.get("neutrality_status") != "PASS" or
            diagnostic.get("counters_status") != "PASS"):
        result["diagnostic_admission"] = "QUARANTINE_DIAGNOSTIC"
        return result
    sha(diagnostic, "diagnostic_sha256")
    result["diagnostic_admission"] = "ADMITTED_FOR_REVIEW"
    result["review_order_completed"].extend(["diagnostic admission", "diagnostic counters",
                                              "project-level interpretation"])
    diag_metrics = normalize_counters(obj(diagnostic, "counters"))
    result["normalized_metrics"]["diagnostic"] = diag_metrics
    local = normalized["C_L0_up_D2"]["response_fraction"]
    window = normalized["C_window"]["response_fraction"]
    if local > 0 and window > 0:
        result["candidate_interpretation"].append("RAW_LOCAL_AND_WINDOW_POSITIVE_REVIEW_C")
    elif local > 0:
        result["candidate_interpretation"].append("RAW_LOCAL_POSITIVE_WINDOW_NONPOSITIVE_REVIEW_B")
    else:
        result["candidate_interpretation"].append("RAW_LOCAL_NONPOSITIVE_REVIEW_SURVIVAL_VALUE")
    if diag_metrics["raw_counters"]["protected_protected_evictions"]:
        result["candidate_interpretation"].append("CHURN_PRESENT_REVIEW_A")
    if (diag_metrics["raw_counters"]["quota_denials_invalid_priority"] +
            diag_metrics["raw_counters"]["quota_denials_no_local_protected_victim"]):
        result["candidate_interpretation"].append("DENIAL_PRESENT_REVIEW_D")
    if diag_metrics["old_address_survival_fraction"] is None:
        result["candidate_interpretation"].append("OLD_ADDRESS_SURVIVAL_UNOBSERVED")
    return result


def committed_packet(path: Path) -> dict:
    resolved = path.resolve(strict=True)
    root = ROOT.resolve()
    try:
        relative = resolved.relative_to(root)
    except ValueError as exc:
        raise ReviewError("ACTIVE_OUTPUT_FORBIDDEN", "packet is outside this repository") from exc
    if relative.name != PACKET_NAME or not relative.as_posix().startswith(PACK_ROOT.as_posix() + "/C16_E1_"):
        raise ReviewError("ACTIVE_OUTPUT_FORBIDDEN", "only committed C16 E1 review-pack packets are readable")
    raw = resolved.read_bytes()
    try:
        committed = subprocess.check_output(["git", "-C", str(root), "show",
                                            f"HEAD:{relative.as_posix()}"], stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as exc:
        raise ReviewError("UNCOMMITTED_PACKET", "packet absent from HEAD") from exc
    if raw != committed:
        raise ReviewError("UNCOMMITTED_PACKET", "packet differs from HEAD")
    try:
        return json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ReviewError("INVALID_PACKET_JSON", "committed packet cannot be parsed") from exc


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", required=True, type=Path,
                        help="committed C16 E1 review-pack TERMINAL_REVIEW_PACKET.json; no run dirs")
    args = parser.parse_args()
    result = evaluate(committed_packet(args.packet))
    relative = args.packet.resolve().relative_to(ROOT.resolve()).as_posix()
    result["packet_git_commit"] = subprocess.check_output(
        ["git", "-C", str(ROOT), "log", "-1", "--format=%H", "--", relative],
        stderr=subprocess.PIPE).decode().strip()
    result["packet_sha256"] = hashlib.sha256(args.packet.resolve().read_bytes()).hexdigest()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
