#!/usr/bin/env python3
"""Build the hash-closed, outcome-free AWQ apply-selector catalog for Lane C.

This program is deliberately a one-way post-freeze materializer.  It verifies
the immutable C selector-freeze objects before it opens the four *clean* AWQ
native catalogs.  It has no input for the direct-semantic diagnostic, NCU,
NVBit, counters, traces, or target plans.  Its only semantic transformation is
to represent the existing phase/kernel-name-only evidence as explicit
``UNKNOWN``; it never infers an operator or layer from a kernel name.

The full launch population is retained outside Git with deterministic gzip and
SHA-256 indexes.  The compact JSON receipt is suitable for a later, explicit
Lane-C apply-selector import; this utility does not alter C's worktree or
execute C's selector.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


FREEZE_COMMIT = "dd70d5faafb81ac2b921b49bb0606bcf2d9972a7"
CURRENT_C_HEAD = "941229c6eacef28e4e782e37f87c738458071d39"
G_RESOURCE_COMMIT = "523efd2c3ef0c023d0b46061483213f34f5049a5"
C_ROOT = "docs/vm_tlb/review_packs/C16_MULTIMODEL_NATIVE/lane_c"
FREEZE_PATH = f"{C_ROOT}/P_TRAIN_SELECTOR_SOURCE_FREEZE.json"
POLICY_PATH = f"{C_ROOT}/G_TARGET_SELECTION_POLICY_V1.json"
PROTOCOL_PATH = f"{C_ROOT}/PROSPECTIVE_PROTOCOL.json"
SELECTOR_SOURCE_COMMIT = "ebb0a96ee8fe685406950ea2013c9d6423a17d75"
SELECTOR_SOURCE_PATH = "util/vm_tlb/c16/lane_c/c16_sampling_v2.py"
EXPECTED_SELECTOR_SHA = "acb30e322de5f77a8fb33c5d63666e23c9c0c8097322e9736e1038510af8c301"
EXPECTED_POLICY_SHA = "9f35e7b0809fdfb24352c46b7e43547238d9f0b1615dd39bbe3df934b2d2a3ad"
EXPECTED_FREEZE_SHA = "3096c9ea5d1d09e4935a8d765bc1dc36a8d4ff35f4174c7ef42846259aee95c7"
JOIN_CONTRACT = "docs/vm_tlb/review_packs/C16_P_NATIVE_POSTPROCESS/JOIN_KEY_CONTRACT.md"
EXPECTED_JOIN_SHA = "41a84737c2380e51c43e90d8915fd4aa2c462090a1238da22511efe22babfa54"

CATALOG_FIELDS = [
    "run_id", "deployment_id", "scenario_id", "phase", "device", "context", "stream",
    "correlation_id", "launch_ordinal", "kernel_name", "implementation_key", "grid", "block",
    "start_ns", "end_ns", "duration_ns", "operator_class", "layer_id", "shape_key", "dtype_key",
    "semantic_evidence", "mapping_status",
]
PROFILE_FIELDS = ["run_id", "profile_report_id"]

# The diagnostic directory is intentionally absent from this closed allow-list.
SOURCES = (
    {
        "label": "S1_CODE",
        "directory": "p3_awq_s1_g1_56a853d1-ef7f-4653-8cd8-cc7defde5689",
        "seal": "HOLDOUT_P3_AWQ_S1_G1_SEAL.json",
    },
    {
        "label": "S2_TEXT",
        "directory": "p3_awq_s2_text_g1_ee52fecb-7bff-4918-bfa4-f0c65838ed5f",
        "seal": "HOLDOUT_P3_AWQ_S2_TEXT_G1_SEAL.json",
    },
    {
        "label": "S2_CODE",
        "directory": "p3_awq_s2_code_g1_bedbd6bd-f51e-4246-89e9-c0e59c74e0e7",
        "seal": "HOLDOUT_P3_AWQ_S2_CODE_G1_SEAL.json",
    },
    {
        "label": "S2_STRUCTURED",
        "directory": "p3_awq_s2_structured_g1_0db40447-a201-452d-a48d-be8116d71aee",
        "seal": "HOLDOUT_P3_AWQ_S2_STRUCTURED_G1_SEAL.json",
    },
)

TRAIN_INPUTS = {
    "KERNEL_CATALOG": ("KERNEL_CATALOG.tsv.gz", "f31378a17c61bd0bd14708baebcfa687ce4e17428d5c0f4b0658cb1bf3e2b40f"),
    "KERNEL_SEMANTIC_MAP": ("KERNEL_SEMANTIC_MAP.tsv", "bdcc42cb60f60e2b9741ddd0fb723a8dcfe257019e05bcf98144601296f1f6a3"),
    "P1_CLOSURE_AUDIT": ("P1_CLOSURE_AUDIT.json", "fa7a16a4c919c2de4096bc549faf6c0a7a10c51e20b05118dace2ee1b920a2ca"),
    "POSTPROCESS_MANIFEST": ("POSTPROCESS_MANIFEST.json", "386ebb080a4a151603241b2ab819f5b6d33ed4bd5b33afdcdb65aaf309c84b3e"),
    "PROFILE_REPORT_INDEX": ("PROFILE_REPORT_INDEX.tsv", "61d7280e6e5c6c9ff9162a440bbf6f82119ee63037aa13d5534df59d6da870e6"),
    "RAW_INDEX": ("RAW_INDEX.tsv", "626cc8907fd643d099f1a0a4f5a9a270d8303b6fbc8250a087bb32a3fff7a43f"),
    "RUN_JOIN_AUDIT": ("RUN_JOIN_AUDIT.json", "22199df6ab5fcae3ba8cc75d186ea08be6768ed793bf206f0980d950dc77fdf6"),
    "SEMANTIC_COVERAGE": ("SEMANTIC_COVERAGE.tsv", "ecea9bb269dc8ee9d426be011ed72ba1c218d4d8c639e78641c51ac3f0673eb3"),
}


class ReleaseError(RuntimeError):
    """A pre-freeze or source closure invariant failed."""


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, prefix=f".{path.name}.", suffix=".tmp", delete=False) as handle:
        handle.write(json_bytes(value))
        temporary = Path(handle.name)
    os.replace(temporary, path)


def git(repo: Path, *args: str, binary: bool = False) -> str | bytes:
    result = subprocess.run(["git", "-C", str(repo), *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if result.returncode:
        raise ReleaseError(result.stderr.decode("utf-8", errors="replace").strip())
    return result.stdout if binary else result.stdout.decode("utf-8")


def git_bytes(repo: Path, commit: str, path: str) -> bytes:
    return git(repo, "show", f"{commit}:{path}", binary=True)  # type: ignore[return-value]


def git_json(repo: Path, commit: str, path: str) -> tuple[dict[str, Any], str]:
    payload = git_bytes(repo, commit, path)
    try:
        value = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise ReleaseError(f"invalid JSON {commit}:{path}") from exc
    if not isinstance(value, dict):
        raise ReleaseError(f"JSON root is not an object: {commit}:{path}")
    return value, sha256_bytes(payload)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ReleaseError(message)


def object_exists(repo: Path, commit: str) -> None:
    git(repo, "cat-file", "-e", f"{commit}^{{commit}}")


def commit_identity(repo: Path, commit: str) -> dict[str, str]:
    output = str(git(repo, "show", "-s", "--format=%H%x00%aI%x00%an <%ae>%x00%s", commit)).rstrip("\n")
    fields = output.split("\x00")
    require(len(fields) == 4, f"cannot parse commit identity: {commit}")
    return {"commit": fields[0], "author_time": fields[1], "author": fields[2], "subject": fields[3]}


def validate_freeze(repo: Path, p_root: Path) -> dict[str, Any]:
    for commit in (FREEZE_COMMIT, CURRENT_C_HEAD, SELECTOR_SOURCE_COMMIT, G_RESOURCE_COMMIT):
        object_exists(repo, commit)
    git(repo, "merge-base", "--is-ancestor", FREEZE_COMMIT, CURRENT_C_HEAD)
    freeze, freeze_sha = git_json(repo, FREEZE_COMMIT, FREEZE_PATH)
    policy, policy_sha = git_json(repo, FREEZE_COMMIT, POLICY_PATH)
    protocol, protocol_sha = git_json(repo, FREEZE_COMMIT, PROTOCOL_PATH)
    selector_payload = git_bytes(repo, SELECTOR_SOURCE_COMMIT, SELECTOR_SOURCE_PATH)
    selector_sha = sha256_bytes(selector_payload)
    require(freeze_sha == EXPECTED_FREEZE_SHA, "selector freeze JSON SHA differs from the published freeze")
    require(policy_sha == EXPECTED_POLICY_SHA, "G target-selection policy SHA differs from frozen policy")
    require(selector_sha == EXPECTED_SELECTOR_SHA, "frozen selector-source SHA differs")
    require(freeze.get("state") == "SOURCE_SHA_FROZEN_BEFORE_AWQ_UNSEAL", "C source is not frozen before AWQ unseal")
    require(freeze.get("selector_source_commit") == SELECTOR_SOURCE_COMMIT, "freeze does not bind expected selector source commit")
    require(freeze.get("selector_code_sha256") == EXPECTED_SELECTOR_SHA, "freeze does not bind selector source SHA")
    require(freeze.get("primary_g_target_selector") == "SELECTOR_R", "primary selector is not frozen SELECTOR_R")
    require(freeze.get("primary_g_target_budget") == "B48", "primary target budget is not frozen B48")
    require(freeze.get("g_target_selection_policy_sha256") == EXPECTED_POLICY_SHA, "freeze does not bind policy SHA")
    require(policy.get("schema_version") == "G_TARGET_SELECTION_POLICY_V1", "unexpected G policy schema")
    require(policy.get("PRIMARY_G_TARGET_SELECTOR") == "SELECTOR_R", "policy primary selector is not SELECTOR_R")
    require(policy.get("PRIMARY_G_TARGET_BUDGET") == "B48", "policy primary budget is not B48")
    forbidden = set(policy.get("forbidden_policy_inputs", []))
    require({"AWQ_OUTCOME", "NCU_OUTCOME", "NVBIT_OUTCOME", "CANDIDATE_PERFORMANCE", "CANDIDATE_COUNTER"}.issubset(forbidden), "policy does not forbid all outcome inputs")
    require(protocol.get("state") == "P_TRAIN_SELECTOR_RULES_AND_12_24_48_PLANS_FROZEN_AWAITING_AWQ_CHEAP_CATALOG", "C protocol is not awaiting post-freeze AWQ catalog")
    require(protocol.get("candidate_outcomes_used_for_selection") is False, "C protocol records candidate outcomes in selection")
    require(protocol.get("native_catalog_receipt", {}).get("awq_outcomes_read") is False, "C freeze does not declare AWQ outcome unread")
    require(protocol.get("read_holdout_target_metrics_after") == "selector SHA, strata, seed, budgets, deployment split and thresholds are committed", "C protocol does not order freeze before holdout metrics")
    require(freeze.get("manifest_declared_not_read_status", {}).get("AWQ_HOLDOUT") == "HOLDOUT_PENDING_FREEZE", "freeze did not mark AWQ as not-read holdout")
    observed_train_hashes = freeze.get("train_input_hashes")
    require(isinstance(observed_train_hashes, dict), "freeze lacks train-input hashes")
    train_root = p_root / "artifacts/c16_p_native_postprocess/p1_native_events_e3d49cea"
    checked_train: dict[str, str] = {}
    for kind, (relative, expected) in TRAIN_INPUTS.items():
        path = train_root / relative
        actual = sha256_file(path)
        require(actual == expected, f"P train input hash mismatch: {kind}")
        require(observed_train_hashes.get(kind) == expected, f"C freeze train input mismatch: {kind}")
        checked_train[kind] = actual
    join_path = p_root / JOIN_CONTRACT
    require(sha256_file(join_path) == EXPECTED_JOIN_SHA, "P JOIN_KEY_CONTRACT hash changed")
    freeze_identity = commit_identity(repo, FREEZE_COMMIT)
    selector_identity = commit_identity(repo, SELECTOR_SOURCE_COMMIT)
    current_identity = commit_identity(repo, CURRENT_C_HEAD)
    require(selector_identity["author_time"] < freeze_identity["author_time"], "selector source is not earlier than freeze commit")
    return {
        "status": "PASS",
        "freeze_commit": freeze_identity,
        "current_c_head": current_identity,
        "freeze_is_ancestor_of_current_head": True,
        "freeze_json": {"path": FREEZE_PATH, "sha256": freeze_sha},
        "selector_source": {"commit": selector_identity, "path": SELECTOR_SOURCE_PATH, "sha256": selector_sha},
        "g_target_selection_policy": {"path": POLICY_PATH, "sha256": policy_sha, "selector": "SELECTOR_R", "budget": "B48"},
        "prospective_protocol": {"path": PROTOCOL_PATH, "sha256": protocol_sha, "awq_outcomes_read_before_freeze": False, "candidate_outcomes_used_for_selection": False},
        "train_input_hashes": checked_train,
        "join_key_contract": {"path": JOIN_CONTRACT, "sha256": EXPECTED_JOIN_SHA},
    }


def validate_source(p_root: Path, source: dict[str, str]) -> dict[str, Any]:
    directory = p_root / "artifacts/c16_p_native_postprocess/event_driven" / source["directory"]
    catalog = directory / "KERNEL_CATALOG.tsv"
    profiles = directory / "PROFILE_REPORT_INDEX.tsv"
    seal_path = p_root / "docs/vm_tlb/review_packs/C16_P_NATIVE_POSTPROCESS" / source["seal"]
    require(catalog.is_file() and profiles.is_file() and seal_path.is_file(), f"sealed AWQ source missing: {source['label']}")
    seal = json.loads(seal_path.read_text(encoding="utf-8"))
    require(seal.get("schema_version") == "C16_P_HOLDOUT_SEAL_V1", f"unexpected seal schema: {source['label']}")
    identity = seal.get("identity")
    artifacts = seal.get("hash_closed_artifacts_outside_git")
    require(isinstance(identity, dict) and isinstance(artifacts, dict), f"sealed source lacks identity/artifacts: {source['label']}")
    require(identity.get("deployment_id") == "c16_qwen25_7b_awq", f"non-AWQ deployment in {source['label']}")
    require(identity.get("scenario_id") in {"S1", "S2"}, f"unexpected admitted scenario in {source['label']}")
    require(sha256_file(catalog) == artifacts.get("full_catalog_tsv_sha256"), f"catalog SHA mismatch: {source['label']}")
    require(sha256_file(profiles) == artifacts.get("profile_report_index_sha256"), f"profile index SHA mismatch: {source['label']}")
    with catalog.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        require(reader.fieldnames is not None and set(CATALOG_FIELDS).issubset(reader.fieldnames), f"catalog schema missing fields: {source['label']}")
        first = next(reader, None)
    require(first is not None and first.get("run_id") == identity.get("run_id"), f"catalog run identity mismatch: {source['label']}")
    with profiles.open("r", encoding="utf-8", newline="") as handle:
        profile_rows = list(csv.DictReader(handle, delimiter="\t"))
    require(len(profile_rows) == 1, f"ambiguous profile index: {source['label']}")
    profile = profile_rows[0]
    require(profile.get("run_id") == identity.get("run_id"), f"profile run identity mismatch: {source['label']}")
    require(profile.get("profile_report_id") == artifacts.get("raw_nsys_rep_sha256"), f"profile/raw report identity mismatch: {source['label']}")
    producer = seal.get("exact_g_producer")
    require(isinstance(producer, dict) and isinstance(producer.get("commit"), str), f"seal lacks exact G producer: {source['label']}")
    return {
        "label": source["label"], "directory": str(directory.relative_to(p_root)), "seal_path": str(seal_path.relative_to(p_root)),
        "seal_sha256": sha256_file(seal_path), "g_producer_commit": producer["commit"], "g_checkpoint_path": producer.get("checkpoint_path"),
        "g_checkpoint_sha256": producer.get("checkpoint_sha256"), "identity": identity,
        "source_catalog": {"path": str(catalog.relative_to(p_root)), "size_bytes": catalog.stat().st_size, "sha256": sha256_file(catalog)},
        "source_profile_index": {"path": str(profiles.relative_to(p_root)), "size_bytes": profiles.stat().st_size, "sha256": sha256_file(profiles)},
        "raw_nsys_rep_sha256": artifacts["raw_nsys_rep_sha256"],
        "source_catalog_path": catalog, "source_profile_path": profiles,
    }


def validate_skips(repo: Path) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for scenario in ("S3", "S4"):
        path = f"docs/vm_tlb/codex_handoff/c16/autodl_wave1/P3_AWQ_{scenario}_RESOURCE_ADMISSION.json"
        receipt, digest = git_json(repo, G_RESOURCE_COMMIT, path)
        identity = receipt.get("identity", {})
        require(receipt.get("status") == "SKIPPED_RESOURCE", f"AWQ {scenario} skip status changed")
        require(receipt.get("scientific_eligible") is False and receipt.get("timing_result_emitted") is False, f"AWQ {scenario} skip acquired outcomes")
        require(identity.get("deployment_id") == "c16_qwen25_7b_awq" and identity.get("scenario_id") == scenario, f"AWQ {scenario} identity mismatch")
        constraints = receipt.get("constraints", {})
        require(constraints.get("cpu_offload_forbidden") is True and constraints.get("frozen_context_batch_decode_unchanged") is True, f"AWQ {scenario} has unauthorized substitution")
        results.append({"scenario_id": scenario, "status": "SKIPPED_RESOURCE", "g_commit": G_RESOURCE_COMMIT, "receipt_path": path, "receipt_sha256": digest,
                        "identity": {key: identity[key] for key in ("deployment_id", "scenario_id", "run_id", "shape_key", "implementation_key", "dtype", "quantization")},
                        "no_shape_context_batch_or_offload_substitution": True, "native_rows_created": 0})
    return results


def write_tsv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n", extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)


def payload_record(p_root: Path, path: Path, kind: str, rows: int | None = None, *, published_path: Path | None = None) -> dict[str, Any]:
    """Hash a staging file while recording its eventual atomically-published path."""
    result: dict[str, Any] = {"kind": kind, "path": str((published_path or path).relative_to(p_root)), "size_bytes": path.stat().st_size, "sha256": sha256_file(path), "git_policy": "OUTSIDE_GIT_HASH_CLOSED"}
    if rows is not None:
        result["logical_row_count"] = rows
    return result


def materialize(p_root: Path, output: Path, sources: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if output.exists():
        raise ReleaseError(f"refusing to overwrite existing output: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f".{output.name}.", dir=output.parent))
    catalog_path = staging / "P_AWQ_CHEAP_KERNEL_CATALOG.tsv"
    profile_path = staging / "P_AWQ_PROFILE_REPORT_INDEX.tsv"
    roster_path = staging / "P_AWQ_DEPLOYMENT_ROSTER.tsv"
    admission_path = staging / "P_AWQ_RESOURCE_ADMISSION.tsv"
    seen_physical: set[tuple[str, str, str, str, str, str]] = set()
    profile_rows: list[dict[str, str]] = []
    admissions: set[tuple[str, str]] = set()
    rows = 0
    try:
        with catalog_path.open("w", encoding="utf-8", newline="") as out:
            writer = csv.DictWriter(out, fieldnames=CATALOG_FIELDS, delimiter="\t", lineterminator="\n", extrasaction="raise")
            writer.writeheader()
            for source in sources:
                with source["source_catalog_path"].open("r", encoding="utf-8", newline="") as handle:
                    reader = csv.DictReader(handle, delimiter="\t")
                    for source_row in reader:
                        require(source_row.get("semantic_evidence") == "NSYS_KERNEL_NAME_PLUS_NVTX_PHASE", f"unexpected semantic evidence in {source['label']}")
                        require(source_row.get("mapping_status") == "UNKNOWN_OPERATOR_LAYER_NO_DIRECT_EVIDENCE", f"unexpected semantic mapping in {source['label']}")
                        require(source_row.get("operator_class") == "UNKNOWN" and source_row.get("layer_id") == "UNKNOWN", f"non-UNKNOWN semantics in {source['label']}")
                        row = {field: source_row[field] for field in CATALOG_FIELDS}
                        # The source marker is not direct operator/layer evidence under the frozen P contract.
                        row["semantic_evidence"] = "UNKNOWN"
                        row["mapping_status"] = "UNKNOWN_OPERATOR_LAYER_NO_DIRECT_EVIDENCE"
                        require(all(row[field] != "" for field in CATALOG_FIELDS), f"empty structural key in {source['label']}")
                        physical = tuple(row[field] for field in ("run_id", "device", "context", "stream", "correlation_id", "launch_ordinal"))
                        require(physical not in seen_physical, "duplicate report-scoped physical launch identity")
                        seen_physical.add(physical)
                        writer.writerow(row)
                        rows += 1
                with source["source_profile_path"].open("r", encoding="utf-8", newline="") as handle:
                    profile_rows.extend({field: row[field] for field in PROFILE_FIELDS} for row in csv.DictReader(handle, delimiter="\t"))
                admissions.add((source["identity"]["deployment_id"], source["identity"]["scenario_id"]))
        require(len(profile_rows) == len({row["run_id"] for row in profile_rows}), "duplicate run/profile bridge")
        write_tsv(profile_path, PROFILE_FIELDS, sorted(profile_rows, key=lambda row: row["run_id"]))
        write_tsv(roster_path, ["deployment_id", "c16_cohort", "c16_split_role"], [{"deployment_id": "c16_qwen25_7b_awq", "c16_cohort": "PROSPECTIVE_QWEN7_AWQ", "c16_split_role": "PROSPECTIVE_HOLDOUT"}])
        write_tsv(admission_path, ["deployment_id", "scenario_id", "admission_status", "admission_basis"],
                  [{"deployment_id": deployment, "scenario_id": scenario, "admission_status": "ADMITTED", "admission_basis": "HASH_CLOSED_CLEAN_NATIVE_PROFILE"} for deployment, scenario in sorted(admissions)])
        gzip_path = staging / "P_AWQ_CHEAP_KERNEL_CATALOG.tsv.gz"
        with catalog_path.open("rb") as source_handle, gzip_path.open("wb") as destination:
            with gzip.GzipFile(filename="", mode="wb", fileobj=destination, mtime=0) as compressed:
                shutil.copyfileobj(source_handle, compressed, length=1024 * 1024)
        payloads = [
            payload_record(p_root, catalog_path, "KERNEL_CATALOG", rows, published_path=output / catalog_path.name),
            payload_record(p_root, gzip_path, "KERNEL_CATALOG_GZIP", rows, published_path=output / gzip_path.name),
            payload_record(p_root, profile_path, "PROFILE_REPORT_INDEX", len(profile_rows), published_path=output / profile_path.name),
            payload_record(p_root, roster_path, "DEPLOYMENT_ROSTER", 1, published_path=output / roster_path.name),
            payload_record(p_root, admission_path, "RESOURCE_ADMISSION", len(admissions), published_path=output / admission_path.name),
        ]
        join_audit = {
            "schema_version": "C16_P_AWQ_CHEAP_CATALOG_JOIN_AUDIT_V1", "status": "PASS_NO_MULTIPLICATION",
            "physical_launch_population": rows, "unique_report_scoped_physical_keys": len(seen_physical),
            "profile_run_bridges": len(profile_rows), "admitted_deployment_scenarios": len(admissions),
            "semantic_evidence": {"UNKNOWN": rows, "DIRECT": 0},
            "prohibited_join_operations": ["CROSS_RUN_ABSOLUTE_TIMESTAMP", "BARE_STREAM", "BARE_CORRELATION_ID"],
            "operator_layer_policy": "UNKNOWN_ONLY_NO_KERNEL_NAME_HEURISTIC", "outcome_columns": "NONE",
        }
        join_path = staging / "P_AWQ_CHEAP_CATALOG_JOIN_AUDIT.json"
        write_json(join_path, join_audit)
        payloads.append(payload_record(p_root, join_path, "JOIN_AUDIT", published_path=output / join_path.name))
        manifest = {
            "schema_version": "C16_P_AWQ_CHEAP_CATALOG_EXTERNAL_MANIFEST_V1",
            "status": "C16_P_AWQ_CHEAP_CATALOG_READY_POST_FREEZE",
            "transport": "OUTSIDE_GIT_HASH_CLOSED",
            "awq_outcomes_read": False,
            "selector_apply_scope": "FROZEN_SELECTOR_R_B48_ONLY_NO_POST_HOC_RANKING",
            "payloads": payloads,
            "join_audit_sha256": sha256_file(join_path),
        }
        manifest_path = staging / "P_AWQ_CHEAP_CATALOG_RELEASE_MANIFEST.json"
        write_json(manifest_path, manifest)
        payloads.append(payload_record(p_root, manifest_path, "RELEASE_MANIFEST", published_path=output / manifest_path.name))
        os.replace(staging, output)
        return payloads, join_audit
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True)
        raise


def verify_existing_output(p_root: Path, output: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Recheck a completed atomic output before refreshing its small receipt.

    This permits a receipt-only provenance update without rewriting the large
    launch population.  It never accepts a partial directory: every manifest
    entry is checked again by size and SHA-256.
    """
    manifest_path = output / "P_AWQ_CHEAP_CATALOG_RELEASE_MANIFEST.json"
    audit_path = output / "P_AWQ_CHEAP_CATALOG_JOIN_AUDIT.json"
    require(manifest_path.is_file() and audit_path.is_file(), "existing output lacks release manifest or join audit")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    require(manifest.get("schema_version") == "C16_P_AWQ_CHEAP_CATALOG_EXTERNAL_MANIFEST_V1", "existing output manifest schema differs")
    require(manifest.get("status") == "C16_P_AWQ_CHEAP_CATALOG_READY_POST_FREEZE", "existing output is not ready")
    payloads = manifest.get("payloads")
    require(isinstance(payloads, list) and payloads, "existing output manifest has no payloads")
    for payload in payloads:
        require(isinstance(payload, dict), "invalid existing payload entry")
        relative = payload.get("path")
        require(isinstance(relative, str), "existing payload lacks path")
        path = p_root / relative
        require(path.is_file(), f"existing payload absent: {relative}")
        require(path.stat().st_size == payload.get("size_bytes") and sha256_file(path) == payload.get("sha256"), f"existing payload closure failed: {relative}")
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    require(audit.get("status") == "PASS_NO_MULTIPLICATION", "existing join audit is not PASS")
    require(manifest.get("join_audit_sha256") == sha256_file(audit_path), "existing manifest/join-audit hash mismatch")
    complete = [dict(item) for item in payloads]
    complete.append(payload_record(p_root, manifest_path, "RELEASE_MANIFEST"))
    return complete, audit


def relocate_existing_output(p_root: Path, source: Path, destination: Path, receipt_path: Path) -> tuple[list[dict[str, Any]], str]:
    """Atomically relocate an already-verified output and repair path metadata.

    This is deliberately *not* a materialization path: it neither opens the
    four source catalogs nor rewrites the launch TSV.  It performs the one
    requested final existence/size/SHA closure check on the destination files.
    """
    require(source.is_dir(), f"relocation source is absent: {source}")
    require(not destination.exists(), f"relocation destination already exists: {destination}")
    require(receipt_path.is_file(), "existing compact receipt is absent")
    source_relative = source.relative_to(p_root)
    destination_relative = destination.relative_to(p_root)
    manifest_name = "P_AWQ_CHEAP_CATALOG_RELEASE_MANIFEST.json"
    manifest_path = source / manifest_name
    require(manifest_path.is_file(), "relocation source lacks release manifest")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    require(manifest.get("schema_version") == "C16_P_AWQ_CHEAP_CATALOG_EXTERNAL_MANIFEST_V1", "relocation source manifest schema differs")
    entries = manifest.get("payloads")
    require(isinstance(entries, list) and entries, "relocation source has no payload entries")
    destination.parent.mkdir(parents=True, exist_ok=True)
    os.replace(source, destination)
    try:
        for entry in entries:
            require(isinstance(entry, dict) and isinstance(entry.get("path"), str), "invalid payload during relocation")
            old = Path(entry["path"])
            require(old.is_relative_to(source_relative), "manifest payload is outside relocation source")
            new = destination_relative / old.relative_to(source_relative)
            entry["path"] = str(new)
            actual = p_root / new
            require(actual.is_file(), f"relocated payload absent: {new}")
            require(actual.stat().st_size == entry.get("size_bytes"), f"relocated payload size changed: {new}")
            require(sha256_file(actual) == entry.get("sha256"), f"relocated payload SHA changed: {new}")
        audit_path = destination / "P_AWQ_CHEAP_CATALOG_JOIN_AUDIT.json"
        require(manifest.get("join_audit_sha256") == sha256_file(audit_path), "relocated join-audit SHA changed")
        write_json(destination / manifest_name, manifest)
        manifest_record = payload_record(p_root, destination / manifest_name, "RELEASE_MANIFEST")
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        require(receipt.get("status") == "C16_P_AWQ_CHEAP_CATALOG_READY_POST_FREEZE", "existing receipt is not ready")
        require(receipt.get("awq_outcomes_read") is False, "existing receipt no longer protects AWQ outcomes")
        require(receipt.get("selector_immutability", {}).get("selector") == "SELECTOR_R" and receipt.get("selector_immutability", {}).get("budget") == "B48", "existing receipt does not bind frozen selector")
        require(len(receipt.get("p_awq_seal_producers", [])) == 4, "existing receipt does not bind four AWQ clean sources")
        receipt["catalog_payloads"] = [dict(entry) for entry in entries] + [manifest_record]
        receipt["post_publication_path_repair"] = {
            "status": "PASS_CONTENT_UNCHANGED",
            "source_path": str(source_relative),
            "final_path": str(destination_relative),
            "launch_population_reconstructed": False,
            "source_catalogs_rescanned": False,
            "semantic_inference_performed": False,
            "final_payload_existence_size_sha256": "PASS",
            "performed_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }
        write_json(receipt_path, receipt)
        return [dict(entry) for entry in entries] + [manifest_record], sha256_file(receipt_path)
    except BaseException:
        # The directory is already safely at its final path.  Leave it there
        # for an explicit repair rather than risking a second rename.
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--reuse-output", action="store_true", help="revalidate an existing atomic output instead of recreating it")
    parser.add_argument("--relocate-from", type=Path, help="atomically move an existing verified output and repair only path metadata")
    parser.add_argument("--materializer-commit", default="WORKTREE_UNCOMMITTED", help="exact P commit containing the materializer")
    args = parser.parse_args()
    repo = args.repo.resolve()
    try:
        if args.relocate_from is not None:
            payloads, receipt_sha = relocate_existing_output(repo, args.relocate_from.resolve(), args.output.resolve(), args.receipt.resolve())
            print(json.dumps({"status": "C16_P_AWQ_CHEAP_CATALOG_READY_POST_FREEZE", "receipt": str(args.receipt.resolve()), "receipt_sha256": receipt_sha, "output": str(args.output.resolve()), "payloads": len(payloads), "mode": "PATH_REPAIR_ONLY"}, sort_keys=True))
            return 0
        freeze = validate_freeze(repo, repo)
        sources = [validate_source(repo, dict(source)) for source in SOURCES]
        skips = validate_skips(repo)
        output = args.output.resolve()
        payloads, join_audit = (verify_existing_output(repo, output) if args.reuse_output else materialize(repo, output, sources))
        receipt = {
            "schema_version": "C16_P_AWQ_CHEAP_CATALOG_POST_FREEZE_RECEIPT_V1",
            "status": "C16_P_AWQ_CHEAP_CATALOG_READY_POST_FREEZE",
            "release_event": "C16_P_AWQ_CHEAP_CATALOG_POST_FREEZE_RELEASE",
            "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "release_gate": {"selector_freeze_happened_first": True, "freeze_validation": freeze},
            "p_awq_seal_producers": [{key: value for key, value in source.items() if key not in {"source_catalog_path", "source_profile_path"}} for source in sources],
            "catalog_payloads": payloads,
            "resource_admission": {"admitted_clean_scenarios": ["S1", "S2"], "skipped_resource_scenarios": skips, "no_shape_context_batch_or_offload_substitution": True},
            "validated_dependencies": [
                {"kind": "C_SELECTOR_FREEZE", "commit": FREEZE_COMMIT, "path": FREEZE_PATH, "sha256": EXPECTED_FREEZE_SHA},
                {"kind": "C_SELECTOR_SOURCE", "commit": SELECTOR_SOURCE_COMMIT, "path": SELECTOR_SOURCE_PATH, "sha256": EXPECTED_SELECTOR_SHA},
                {"kind": "G_TARGET_SELECTION_POLICY_V1", "commit": FREEZE_COMMIT, "path": POLICY_PATH, "sha256": EXPECTED_POLICY_SHA},
                {"kind": "P_JOIN_KEY_CONTRACT", "path": JOIN_CONTRACT, "sha256": EXPECTED_JOIN_SHA},
            ],
            "awq_outcomes_read": False,
            "candidate_ncu_nvbit_outcome_used": False,
            "unauthorized_counter_result_used": False,
            "post_hoc_ranking_information_used": False,
            "semantic_policy": {"source_direct_semantic_diagnostic_read": False, "operator_layer_unresolved": "UNKNOWN", "kernel_name_heuristic": "FORBIDDEN"},
            "selector_immutability": {"selector": "SELECTOR_R", "budget": "B48", "strata": "FROZEN", "seed": 16031, "thresholds": "FROZEN", "sample_rules": "FROZEN", "modified_by_p": False},
            "join_audit": join_audit,
            "p_payload_materializer": {"commit": args.materializer_commit, "path": "util/vm_tlb/c16/lane_p/awq_post_freeze_release.py", "code_sha256": sha256_file(Path(__file__)), "existing_output_revalidated": args.reuse_output},
        }
        write_json(args.receipt.resolve(), receipt)
        print(json.dumps({"status": receipt["status"], "receipt": str(args.receipt.resolve()), "receipt_sha256": sha256_file(args.receipt.resolve()), "output": str(args.output.resolve())}, sort_keys=True))
        return 0
    except ReleaseError as exc:
        print(f"C16-P AWQ post-freeze release blocked: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
