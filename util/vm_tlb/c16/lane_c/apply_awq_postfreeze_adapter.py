#!/usr/bin/env python3
"""Apply the frozen C16 Selector-R/B48 to P's post-freeze AWQ catalog.

P's formal AWQ release is an outside-Git, SHA-256-closed catalog receipt,
rather than the earlier P1 checkpoint schema.  This adapter validates that
new transport without changing ``c16_sampling_v2.py``: its SHA was committed
before the AWQ unseal and is therefore the selector implementation used here.
It reads only P's authorized cheap catalog and release metadata; it never
opens an NCU, NVBit, trace, or other candidate-outcome payload.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
SELECTOR_PATH = HERE / "c16_sampling_v2.py"
P_BRANCH = "origin/hrl/vm-c16-p-native-postprocess-v0"
P_RELEASE_RECEIPT = "docs/vm_tlb/review_packs/C16_P_NATIVE_POSTPROCESS/P_AWQ_CHEAP_CATALOG_RECEIPT.json"
P_RELEASE_STATUS = "C16_P_AWQ_CHEAP_CATALOG_READY_POST_FREEZE"
P_RELEASE_SCHEMA = "C16_P_AWQ_CHEAP_CATALOG_POST_FREEZE_RECEIPT_V1"


def load_selector() -> Any:
    spec = importlib.util.spec_from_file_location("c16_sampling_v2_frozen", SELECTOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load frozen C16 selector implementation")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


m = load_selector()


def die(message: str) -> None:
    raise RuntimeError(message)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_external_path(root: Path, relative: str) -> Path:
    candidate = (root / relative).resolve()
    if root not in candidate.parents:
        die(f"external payload escapes its declared root: {relative}")
    return candidate


def external_sha(path: Path, expected_size: int, expected_sha: str) -> None:
    if not path.is_file() or path.stat().st_size != expected_size:
        die(f"external P payload missing or size-mismatched: {path}")
    if m.sha256_file(path) != expected_sha:
        die(f"external P payload SHA-256 mismatch: {path}")


def gzip_content_sha(path: Path) -> str:
    digest = hashlib.sha256()
    with gzip.open(path, "rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git_ok(args: list[str]) -> None:
    completed = subprocess.run(["git", "-C", str(m.ROOT), *args], text=True, capture_output=True)
    if completed.returncode:
        die(f"Git validation failed ({' '.join(args)}): {completed.stderr.strip()}")


def declared_payloads(receipt: dict[str, Any], artifact_root: Path) -> tuple[dict[str, dict[str, Any]], dict[str, Path]]:
    entries = receipt.get("catalog_payloads")
    if not isinstance(entries, list) or not entries:
        die("P AWQ release has no hash-closed catalog payload list")
    payloads: dict[str, dict[str, Any]] = {}
    locations: dict[str, Path] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            die("P AWQ release payload entry is malformed")
        kind = entry.get("kind")
        relative = entry.get("path")
        expected_sha = entry.get("sha256")
        expected_size = entry.get("size_bytes")
        if (not isinstance(kind, str) or kind in payloads or not isinstance(relative, str) or not relative
                or not isinstance(expected_size, int) or expected_size < 0
                or not isinstance(expected_sha, str) or len(expected_sha) != 64):
            die("P AWQ release payload lacks a unique path/size/SHA-256 closure")
        path = safe_external_path(artifact_root, relative)
        external_sha(path, expected_size, expected_sha)
        payloads[kind] = entry
        locations[kind] = path
    required = {"KERNEL_CATALOG", "KERNEL_CATALOG_GZIP", "PROFILE_REPORT_INDEX", "DEPLOYMENT_ROSTER",
                "RESOURCE_ADMISSION", "JOIN_AUDIT", "RELEASE_MANIFEST"}
    if set(payloads) != required:
        die("P AWQ release payload kinds differ from the required cheap-catalog closure")
    if gzip_content_sha(locations["KERNEL_CATALOG_GZIP"]) != payloads["KERNEL_CATALOG"]["sha256"]:
        die("P AWQ compressed catalog does not reconstruct the declared full catalog SHA-256")
    return payloads, locations


def validate_release(p_commit: str, artifact_root: Path) -> tuple[dict[str, Any], dict[str, Path], dict[str, Any], str]:
    if len(p_commit) != 40 or any(char not in "0123456789abcdef" for char in p_commit):
        die("P commit must be an exact lowercase 40-hex SHA")
    git_ok(["cat-file", "-e", f"{p_commit}^{{commit}}"])
    git_ok(["merge-base", "--is-ancestor", p_commit, P_BRANCH])
    receipt_text = m.git_text(p_commit, P_RELEASE_RECEIPT)
    receipt = json.loads(receipt_text)
    if receipt.get("schema_version") != P_RELEASE_SCHEMA or receipt.get("status") != P_RELEASE_STATUS:
        die("P commit does not contain the formal post-freeze AWQ release receipt")
    prohibited = ("awq_outcomes_read", "candidate_ncu_nvbit_outcome_used", "post_hoc_ranking_information_used",
                  "unauthorized_counter_result_used")
    if any(receipt.get(field) is not False for field in prohibited):
        die("P AWQ release receipt does not preserve the no-outcome/no-ranking boundary")
    if receipt.get("release_event") != "C16_P_AWQ_CHEAP_CATALOG_POST_FREEZE_RELEASE":
        die("P AWQ release event is not the authorized post-freeze event")
    if receipt.get("semantic_policy", {}).get("kernel_name_heuristic") != "FORBIDDEN":
        die("P AWQ release permits a forbidden kernel-name semantic heuristic")
    if receipt.get("semantic_policy", {}).get("operator_layer_unresolved") != "UNKNOWN":
        die("P AWQ release does not retain unresolved semantic fields as UNKNOWN")
    if receipt.get("selector_immutability") != {
        "budget": "B48", "modified_by_p": False, "sample_rules": "FROZEN", "seed": 16031,
        "selector": "SELECTOR_R", "strata": "FROZEN", "thresholds": "FROZEN",
    }:
        die("P AWQ release changes the frozen Selector-R/B48 rule")
    if receipt.get("post_publication_path_repair", {}).get("status") != "PASS_CONTENT_UNCHANGED":
        die("P AWQ release lacks a content-preserving final path closure")
    payloads, locations = declared_payloads(receipt, artifact_root)
    release_manifest = json.loads(locations["RELEASE_MANIFEST"].read_text())
    if (release_manifest.get("schema_version") != "C16_P_AWQ_CHEAP_CATALOG_EXTERNAL_MANIFEST_V1"
            or release_manifest.get("status") != P_RELEASE_STATUS
            or release_manifest.get("awq_outcomes_read") is not False
            or release_manifest.get("selector_apply_scope") != "FROZEN_SELECTOR_R_B48_ONLY_NO_POST_HOC_RANKING"):
        die("P AWQ external release manifest does not preserve the frozen-selector scope")
    release_entries = {entry.get("kind"): entry for entry in release_manifest.get("payloads", []) if isinstance(entry, dict)}
    expected_external = {kind: entry for kind, entry in payloads.items() if kind != "RELEASE_MANIFEST"}
    if set(release_entries) != set(expected_external):
        die("P AWQ external release manifest payload closure disagrees with its Git receipt")
    for kind, entry in expected_external.items():
        candidate = release_entries[kind]
        if any(candidate.get(field) != entry.get(field) for field in ("path", "sha256", "size_bytes")):
            die(f"P AWQ external release manifest disagrees for {kind}")
    if release_manifest.get("join_audit_sha256") != payloads["JOIN_AUDIT"]["sha256"]:
        die("P AWQ external release manifest does not bind its join audit")
    join_audit = json.loads(locations["JOIN_AUDIT"].read_text())
    if (join_audit.get("schema_version") != "C16_P_AWQ_CHEAP_CATALOG_JOIN_AUDIT_V1"
            or join_audit.get("status") != "PASS_NO_MULTIPLICATION"
            or join_audit.get("outcome_columns") != "NONE"
            or join_audit.get("operator_layer_policy") != "UNKNOWN_ONLY_NO_KERNEL_NAME_HEURISTIC"):
        die("P AWQ join audit is not a clean no-outcome, explicit-UNKNOWN catalog")
    return receipt, locations, join_audit, sha256_bytes(receipt_text.encode())


def validate_c_freeze(receipt: dict[str, Any]) -> dict[str, Any]:
    protocol = m.assert_p_train_freeze(m.OUT)
    source_path = m.OUT / "P_TRAIN_SELECTOR_SOURCE_FREEZE.json"
    source = json.loads(source_path.read_text())
    policy_path = m.OUT / "G_TARGET_SELECTION_POLICY_V1.json"
    policy = json.loads(policy_path.read_text())
    gate = receipt.get("release_gate", {}).get("freeze_validation", {})
    if gate.get("status") != "PASS":
        die("P AWQ release does not validate the C freeze")
    if (gate.get("freeze_json", {}).get("sha256") != m.sha256_file(source_path)
            or gate.get("selector_source", {}).get("sha256") != m.code_sha()
            or gate.get("g_target_selection_policy", {}).get("sha256") != m.sha256_file(policy_path)
            or gate.get("g_target_selection_policy", {}).get("selector") != "SELECTOR_R"
            or gate.get("g_target_selection_policy", {}).get("budget") != "B48"):
        die("P AWQ release does not bind this exact frozen C selector/policy")
    release_c_head = gate.get("current_c_head", {}).get("commit")
    if not isinstance(release_c_head, str) or len(release_c_head) != 40:
        die("P AWQ release does not name its exact C head")
    git_ok(["merge-base", "--is-ancestor", release_c_head, m.current_head()])
    if (source.get("selector_code_sha256") != m.code_sha()
            or policy.get("PRIMARY_G_TARGET_SELECTOR") != "SELECTOR_R"
            or policy.get("PRIMARY_G_TARGET_BUDGET") != "B48"):
        die("local C freeze no longer agrees with the frozen R/B48 policy")
    return protocol


def load_and_audit_catalog(locations: dict[str, Path], receipt: dict[str, Any], p_commit: str,
                           receipt_sha: str) -> tuple[list[dict[str, str]], dict[str, str], dict[str, Any], dict[str, Any]]:
    with gzip.open(locations["KERNEL_CATALOG_GZIP"], "rt", encoding="utf-8", newline="") as source:
        rows = list(csv.DictReader(source, delimiter="\t"))
    roster = m.tsv_rows(locations["DEPLOYMENT_ROSTER"].read_text())
    profile = m.tsv_rows(locations["PROFILE_REPORT_INDEX"].read_text())
    resource = m.tsv_rows(locations["RESOURCE_ADMISSION"].read_text())
    audit, roles = m.p_validate_catalog_and_roster(rows, roster, profile, resource, m.P_AWQ_COHORT)
    if set(roles.values()) != {"PROSPECTIVE_HOLDOUT"} or set(roles) != {"c16_qwen25_7b_awq"}:
        die("P AWQ catalog is not solely the direct prospective AWQ deployment")
    declared_count = next(entry["logical_row_count"] for entry in receipt["catalog_payloads"] if entry["kind"] == "KERNEL_CATALOG")
    if len(rows) != declared_count:
        die("P AWQ catalog logical row count differs from its hash-closed receipt")
    profile_by_run = {row["run_id"]: row["profile_report_id"] for row in profile}
    for row in rows:
        row["profile_report_id"] = profile_by_run[row["run_id"]]
    admissions = receipt.get("resource_admission", {})
    admitted = sorted({row["scenario_id"] for row in resource})
    if admitted != sorted(admissions.get("admitted_clean_scenarios", [])):
        die("P AWQ resource-admission table differs from its release receipt")
    for skipped in admissions.get("skipped_resource_scenarios", []):
        if (skipped.get("status") != "SKIPPED_RESOURCE" or skipped.get("native_rows_created") != 0
                or skipped.get("no_shape_context_batch_or_offload_substitution") is not True
                or skipped.get("scenario_id") in admitted):
            die("P AWQ skipped-resource receipt permits a forbidden substitution or catalog row")
    dependencies = []
    kind_to_location = locations
    for entry in receipt["catalog_payloads"]:
        dependencies.append({"kind": entry["kind"], "path": entry["path"], "sha256": entry["sha256"],
                             "size_bytes": entry["size_bytes"], "transport": entry["git_policy"]})
    c_receipt = {
        "schema_version": "C16_C_P_AWQ_HOLDOUT_APPLICATION_RECEIPT_V1",
        "producer_p_commit": p_commit,
        "producer_p_branch": P_BRANCH,
        "producer_status": P_RELEASE_STATUS,
        "p_release_receipt_path": P_RELEASE_RECEIPT,
        "p_release_receipt_blob": m.git_blob(p_commit, P_RELEASE_RECEIPT),
        "p_release_receipt_sha256": receipt_sha,
        "manifest_path": P_RELEASE_RECEIPT,
        "manifest_sha256": receipt_sha,
        "outside_git_transport": "HASH_CLOSED",
        "validated_dependencies": dependencies,
        "catalog_logical_row_count": len(rows),
        "resource_admitted_scenarios": admitted,
        "resource_skipped_scenarios": [item["scenario_id"] for item in admissions.get("skipped_resource_scenarios", [])],
        "cohort": m.P_AWQ_COHORT,
        "split_role": "PROSPECTIVE_HOLDOUT",
        "unavailable_deployment_ids": [m.QWEN7_RAW_DEPLOYMENT_ID],
        "capability_limited_train_roster_version": m.CAPABILITY_LIMITED_TRAIN_ROSTER_VERSION,
        "amendment_binding": "P_RELEASE_GATE_EXACT_C_FREEZE_AND_POLICY_WITH_LOCAL_COMMITTED_RESOURCE_ONLY_AMENDMENT",
        "selector_code_sha256": m.code_sha(),
        "primary_selector": "SELECTOR_R",
        "primary_budget": "B48",
        "seed": m.PRIMARY_SEED,
        "strata_version": m.STRATA_VERSION,
        "thresholds": m.THRESHOLDS,
        "awq_outcomes_read": False,
        "ncu_nvbit_outcomes_read": False,
        "post_hoc_sample_edit": False,
        "forbidden_inputs_confirmed": ["NCU", "NVBIT", "TRACE", "COUNTER", "SPEEDUP", "MISS", "CANDIDATE_OUTCOME"],
        "external_payload_root": str(next(iter(kind_to_location.values())).parents[0]),
    }
    audit.update({
        "p_release_commit": p_commit, "p_release_receipt_sha256": receipt_sha,
        "external_payload_hash_size_validation": "PASS", "compressed_to_full_catalog_reconstruction": "PASS",
        "p_join_audit_status": receipt["join_audit"]["status"], "awq_outcomes_read": "FALSE",
        "ncu_nvbit_outcomes_read": "FALSE", "unknown_policy": "EXPLICIT_STRATUM_NO_KERNEL_NAME_HEURISTIC",
    })
    return rows, roles, audit, c_receipt


def publish(p_commit: str, artifact_root: Path) -> None:
    m.require_out(m.OUT)
    receipt, locations, _join_audit, receipt_sha = validate_release(p_commit, artifact_root.resolve())
    protocol = validate_c_freeze(receipt)
    rows, roles, audit, c_receipt = load_and_audit_catalog(locations, receipt, p_commit, receipt_sha)
    units = m.annotate_certainty(m.canonicalize_catalog(rows, "NATIVE_PROFILED", historical_oracle=False))
    if not units:
        die("P AWQ hash-closed catalog is empty")
    m.write_json(m.OUT / "P_AWQ_CHEAP_CATALOG_RECEIPT.json", c_receipt)
    m.write_json(m.OUT / "P_AWQ_SCHEMA_JOIN_AUDIT.json", audit)
    plans = m.write_p_plan_bundle(m.OUT, "P_AWQ", units, roles, m.P_AWQ_COHORT, selectors=("R",))
    m.write_p_awq_target_plan(m.OUT, plans, units, c_receipt)
    m.atomic_text(m.OUT / "P_AWQ_G_TARGET_PLAN_README.md", "# Bounded G target plans\n\nThese are separate request-only, exact-identity `Selector-R` B48 NCU and NVBit plans from the already-frozen selector source SHA.  Each plan contains at most 48 units per deployment/scenario/phase universe and only direct `ADMITTED` AWQ S1/S2 identities.  `c16_qwen25_7b_raw_reference` remains excluded as `RESOURCE_UNAVAILABLE_ON_RTX3090`; AWQ S3/S4 are `SKIPPED_RESOURCE` and have not been substituted.  `Selector-M` is explicitly deferred in `P_AWQ_SELECTOR_M_DEFERRED.md` and was not recomputed.  No NCU/NVBit result, trace outcome, speedup, miss, or candidate mechanism metric was read by C.\n")
    for modality in ("NCU", "NVBIT"):
        target_rows = m.tsv_rows((m.OUT / f"P_AWQ_G_{modality}_TARGET_PLAN.tsv").read_text())
        if not target_rows or any(row["deployment_id"] != "c16_qwen25_7b_awq" or row["scenario_id"] not in {"S1", "S2"}
                                  or row["selector_kind"] != "SELECTOR_R" or row["budget"] != "48" for row in target_rows):
            die(f"{modality} target plan violates the frozen AWQ resource-admission scope")
    protocol["state"] = "P_AWQ_CHEAP_CATALOG_APPLIED_FROZEN_TARGET_PLAN_PUBLISHED"
    protocol["awq_cheap_catalog_receipt"] = c_receipt
    protocol["g_target_plans"] = ["P_AWQ_G_NCU_TARGET_PLAN.tsv", "P_AWQ_G_NVBIT_TARGET_PLAN.tsv"]
    protocol["ncu_nvbit_outcomes_consumed"] = False
    m.write_json(m.OUT / "PROSPECTIVE_PROTOCOL.json", protocol)
    m.write_preflight(m.OUT, "P_FORMAL_TRAIN_AND_AWQ_CHEAP_CATALOGS_CONSUMED_NO_OUTCOMES")
    m.write_manifest(m.OUT, "C16_C_P_AWQ_FROZEN_TARGET_PLAN_READY_FOR_G", native_catalog=True)
    print(f"PASS applied frozen Selector-R/B48 to {len(rows)} authorized AWQ cheap-catalog rows")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p-commit", required=True)
    parser.add_argument("--artifact-root", type=Path, required=True,
                        help="P worktree root containing the receipt-relative hash-closed artifacts")
    args = parser.parse_args()
    publish(args.p_commit, args.artifact_root)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"FAIL C16 post-freeze AWQ application: {exc}")
        raise
