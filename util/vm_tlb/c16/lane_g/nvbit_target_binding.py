#!/usr/bin/env python3
"""Bind one frozen C16 NVBit plan row to one exact structural replay target.

This is deliberately a *binder*, not a target selector.  It consumes the
file-order row already frozen by Lane C, closes its report-scoped composite
identity against the P kernel catalog, and produces the single global
NVBit ordinal-plus-regex filter.  A later trace must still prove the full
kernel name and launch geometry; this program never treats a name match or
an ordinal alone as sufficient identity evidence.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
import uuid
from pathlib import Path
from typing import Any

from c16_native_common import ContractError, atomic_json, sha256_file
from identity_guard import TARGET_FIELDS


PLAN_FIELDS = (
    "capture_modality", "target_plan_id", "selector_kind", "selector_code_sha256", "budget",
    "deployment_id", "scenario_id", "phase", "stratum_id", "unit_id", "run_id",
    "profile_report_id", "device", "context", "stream", "correlation_id", "launch_ordinal",
    "semantic_key_json", "selection_role", "selection_reason", "estimated_capture_cost_ns",
    "target_status", "capture_cap_per_universe", "identity_validation_required",
    "p_manifest_sha256", "p_catalog_sha256", "forbidden_input_confirmation",
)
CATALOG_FIELDS = (
    "run_id", "deployment_id", "scenario_id", "phase", "device", "context", "stream",
    "correlation_id", "launch_ordinal", "kernel_name", "implementation_key", "grid", "block",
    "start_ns", "end_ns", "duration_ns", "operator_class", "layer_id", "shape_key", "dtype_key",
    "semantic_evidence", "mapping_status",
)
COMPOSITE_FIELDS = (
    "run_id", "deployment_id", "scenario_id", "phase", "device", "context", "stream",
    "correlation_id", "launch_ordinal",
)


def read_tsv(path: Path, fields: tuple[str, ...], label: str) -> list[dict[str, str]]:
    try:
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle, delimiter="\t")
            if tuple(reader.fieldnames or ()) != fields:
                raise ContractError(f"{label} header differs from its frozen contract")
            rows = list(reader)
    except OSError as exc:
        raise ContractError(f"cannot read {label}: {exc}") from exc
    if not rows or any(set(row) != set(fields) for row in rows):
        raise ContractError(f"{label} is empty or malformed")
    return rows


def git_head() -> str:
    try:
        value = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ContractError("NVBit binder requires a hash-addressable source checkout") from exc
    if not re.fullmatch(r"[0-9a-f]{40}", value):
        raise ContractError("NVBit binder could not resolve a full source commit")
    return value


def read_binding(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read frozen binding: {exc}") from exc
    required = (
        "schema_version", "status", "deployment_id", "model_id", "model_revision", "tokenizer_revision",
        "scenario", "input", "package_id", "package_fixed_commit", "package_manifest_sha256",
    )
    if not isinstance(value, dict) or any(key not in value for key in required):
        raise ContractError("frozen binding lacks identity/package fields")
    if value["schema_version"] != "C16_G_RUNTIME_FROZEN_BINDING_V1" or value["status"] != "FROZEN_RUNTIME_BINDING_READY":
        raise ContractError("frozen binding is not a C16 immutable runtime binding")
    if not isinstance(value["scenario"], dict) or not isinstance(value["input"], dict):
        raise ContractError("frozen binding has malformed scenario/input")
    return value


def exact_source_row(plan_row: dict[str, str], catalog_rows: list[dict[str, str]]) -> dict[str, str]:
    matches = [
        row for row in catalog_rows
        if all(row[field] == plan_row[field] for field in COMPOSITE_FIELDS)
    ]
    if len(matches) != 1:
        raise ContractError(f"frozen plan composite identity matched {len(matches)} catalog rows, not exactly one")
    source = matches[0]
    expected_unit = "launch:" + ":".join(plan_row[field] for field in (
        "run_id", "device", "context", "stream", "correlation_id", "launch_ordinal",
    ))
    if plan_row["unit_id"] != expected_unit:
        raise ContractError("frozen C unit_id does not reproduce its full composite identity")
    return source


def narrow_regex(kernel_name: str) -> str:
    """Return the fixed implementation-family guard accepted by NVBit parser.

    The tool splits alternatives on commas, so the exact C++ template name is
    unsuitable as an input regex.  Its exact text is retained for post-trace
    validation; this family guard combines with the frozen global ordinal and
    is never accepted as identity by itself.
    """
    prefix = "void at::native::vectorized_elementwise_kernel"
    if not kernel_name.startswith(prefix):
        raise ContractError("first frozen NVBit target has no supported non-comma implementation-family filter")
    return prefix + ".*"


def bind(arguments: argparse.Namespace) -> dict[str, Any]:
    if arguments.row_index != 0:
        raise ContractError("C16 G3 canary must consume the file-order first frozen target row")
    if arguments.target_json.exists() or arguments.receipt.exists():
        raise ContractError("refusing to overwrite an immutable NVBit target/receipt")
    try:
        if str(uuid.UUID(arguments.run_id)) != arguments.run_id:
            raise ValueError
    except ValueError as exc:
        raise ContractError("new NVBit run_id must be canonical UUID") from exc
    plan_rows = read_tsv(arguments.plan, PLAN_FIELDS, "frozen NVBit plan")
    plan_row = plan_rows[arguments.row_index]
    if plan_row["capture_modality"] != "NVBIT" or plan_row["deployment_id"] != "c16_qwen25_7b_awq":
        raise ContractError("file-order first row is not the C-authorized AWQ NVBit target")
    if sha256_file(arguments.plan) != arguments.expected_plan_sha256:
        raise ContractError("frozen NVBit plan SHA256 differs from C publication")
    catalog_rows = read_tsv(arguments.catalog, CATALOG_FIELDS, "P AWQ kernel catalog")
    catalog_sha = sha256_file(arguments.catalog)
    if catalog_sha != arguments.expected_catalog_sha256 or catalog_sha != plan_row["p_catalog_sha256"]:
        raise ContractError("P catalog hash differs from frozen C target row")
    source = exact_source_row(plan_row, catalog_rows)
    binding = read_binding(arguments.binding_receipt)
    scenario, input_data = binding["scenario"], binding["input"]
    if (
        binding["deployment_id"] != plan_row["deployment_id"]
        or scenario.get("scenario_id") != plan_row["scenario_id"]
        or binding["package_manifest_sha256"] != arguments.expected_package_manifest_sha256
        or binding["package_fixed_commit"] != arguments.expected_package_commit
    ):
        raise ContractError("frozen binding does not match the C-authorized deployment/scenario/package")
    source_commit = git_head()
    identity = {
        "model_id": binding["model_id"], "model_revision": binding["model_revision"],
        "tokenizer_revision": binding["tokenizer_revision"], "deployment_id": binding["deployment_id"],
        "implementation_key": source["implementation_key"], "dtype": source["dtype_key"],
        "quantization": arguments.quantization, "scenario_id": scenario["scenario_id"],
        "input_hash": input_data["raw_input_sha256"], "run_id": arguments.run_id, "code_commit": source_commit,
    }
    if set(identity) != {
        "model_id", "model_revision", "tokenizer_revision", "deployment_id", "implementation_key", "dtype",
        "quantization", "scenario_id", "input_hash", "run_id", "code_commit",
    }:
        raise ContractError("generated NVBit identity is incomplete")
    family_regex = narrow_regex(source["kernel_name"])
    filter_value = f"{source['launch_ordinal']}@{family_regex}"
    runtime = {
        "device": "cuda:0", "gpu_uuid": arguments.gpu_uuid, "driver_version": arguments.driver_version,
        "cuda_version": arguments.cuda_version, "torch_version": arguments.torch_version,
        "attention_backend": arguments.attention_backend, "compile_state": "EAGER_UNCOMPILED",
        "profiler_mode": "NVBIT_C16_R_B48_STRUCTURAL_ORDINAL_REPLAY_NOT_FOR_TIMING",
    }
    target = {
        "deployment_id": identity["deployment_id"], "scenario_id": identity["scenario_id"], "run_id": arguments.run_id,
        "device": "cuda:0", "context": "NVBIT_RUNTIME_CONTEXT_PENDING_ACTUAL_TRACE",
        "stream": "NVBIT_RUNTIME_STREAM_PENDING_ACTUAL_TRACE", "correlation_id": "NVBIT_STRUCTURAL_REPLAY_NO_CROSS_RUN_TIMESTAMP_JOIN",
        "kernel_name": source["kernel_name"], "implementation_key": source["implementation_key"],
        "dtype_key": source["dtype_key"], "shape_key": source["shape_key"], "phase": plan_row["phase"],
        "decode_step_bin": "ALL_DECODE_STEPS", "grid": source["grid"], "block": source["block"],
        "operator_class": source["operator_class"], "layer_id": source["layer_id"],
        "semantic_evidence": "C_FIXED_SELECTOR_R_B48_STRUCTURAL_ORDINAL_REPLAY_PENDING_ACTUAL_NVBIT_TRACE",
        "identity": identity, "runtime": runtime,
    }
    if tuple(target) != TARGET_FIELDS:
        raise ContractError("generated target does not satisfy frozen target field order")
    receipt = {
        "schema_version": "C16_G3_NVBIT_TARGET_BINDING_V1",
        "status": "TARGET_IDENTITY_STRUCTURAL_ORDINAL_REPLAY_PENDING_ACTUAL_NVBIT_TRACE",
        "scientific_eligible_for_timing": False,
        "c_plan": {"path": str(arguments.plan), "sha256": sha256_file(arguments.plan), "row_index": arguments.row_index, "row": plan_row},
        "p_catalog": {"path": str(arguments.catalog), "sha256": catalog_sha, "exact_source_row": source},
        "binding": {
            "path": str(arguments.binding_receipt), "sha256": sha256_file(arguments.binding_receipt),
            "package_id": binding["package_id"], "package_fixed_commit": binding["package_fixed_commit"],
            "package_manifest_sha256": binding["package_manifest_sha256"],
        },
        "runtime_source_commit": source_commit,
        "target_json": str(arguments.target_json),
        "target_json_sha256": "PENDING_WRITE",
        "filter": {
            "dynamic_kernel_range": filter_value, "active_from_start": 1,
            "ordinal_basis": "C_P_CATALOG_REPORT_SCOPED_GLOBAL_LAUNCH_ORDINAL_ONE_BASED_NVBIT_CONTEXT_COUNTER",
            "kernel_name_only_matching_forbidden": True,
            "post_trace_must_exactly_verify": ["kernel_id", "full_kernel_name", "grid", "block", "single_trace"],
        },
    }
    atomic_json(arguments.target_json, target)
    receipt["target_json_sha256"] = sha256_file(arguments.target_json)
    atomic_json(arguments.receipt, receipt)
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--expected-plan-sha256", required=True)
    parser.add_argument("--catalog", type=Path, required=True)
    parser.add_argument("--expected-catalog-sha256", required=True)
    parser.add_argument("--binding-receipt", type=Path, required=True)
    parser.add_argument("--expected-package-commit", required=True)
    parser.add_argument("--expected-package-manifest-sha256", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--target-json", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--row-index", type=int, default=0)
    parser.add_argument("--quantization", default="AWQ")
    parser.add_argument("--gpu-uuid", required=True)
    parser.add_argument("--driver-version", required=True)
    parser.add_argument("--cuda-version", required=True)
    parser.add_argument("--torch-version", required=True)
    parser.add_argument("--attention-backend", required=True)
    arguments = parser.parse_args()
    try:
        receipt = bind(arguments)
    except ContractError as exc:
        parser.error(str(exc))
    print(f"PASS C16 G3 fixed NVBit target binder: {receipt['target_json']}")


if __name__ == "__main__":
    main()
