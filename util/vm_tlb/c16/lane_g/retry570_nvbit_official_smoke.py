#!/usr/bin/env python3
"""Accounted, non-capture NVBit 1.8 official vectoradd smoke gate.

This is intentionally a fixed, minimal vendor test-app gate.  It neither
loads a model nor accepts a C target, trace, or arbitrary user command.  The
same closed ``nvdisasm`` child-environment contract as the Lane G runtime
harness is used, so a successful result proves more than an interactive-shell
``export PATH`` workaround.
"""
from __future__ import annotations

import argparse
import os
import signal
import subprocess
import sys
import time
import uuid
from pathlib import Path
from typing import Any

from c16_native_common import ContractError, atomic_json, sha256_file, valid_sha256
from execution_budget import BudgetLease, MeasurementActive
from nvbit_indexselect_microreproducer import git_head
from retry570_long_watch import nvdisasm_environment_contract


SCHEMA = "C16_G_RETRY570_NVBIT_OFFICIAL_VECTORADD_SMOKE_V1"
WALL_LIMIT_SECONDS = 60
DEPLOYMENT = "c16_retry570_nvbit_official_vectoradd_smoke"
REQUIRED_MARKERS = ("NVBit (NVidia Binary Instrumentation Tool", "kernel 0 -", "Final sum =")
ALLOWED_NVBIT_VERSIONS = frozenset({"1.8", "1.7.5", "1.7.7.3"})


def official_evidence(stdout: str) -> dict[str, bool]:
    return {marker: marker in stdout for marker in REQUIRED_MARKERS}


def _kill_group(process: subprocess.Popen[str]) -> None:
    if process.poll() is not None:
        return
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        process.wait(timeout=10)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vectoradd", type=Path, required=True)
    parser.add_argument("--tool", type=Path, required=True)
    parser.add_argument("--tool-sha256", required=True)
    parser.add_argument("--nvdisasm", type=Path, required=True)
    parser.add_argument("--budget-ledger", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--stdout", type=Path, required=True)
    parser.add_argument("--stderr", type=Path, required=True)
    parser.add_argument("--runtime-code-commit", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--nvbit-version", default="1.8")
    args = parser.parse_args()
    if args.runtime_code_commit != git_head():
        raise ContractError("declared runtime code commit differs from this source checkout")
    if args.nvbit_version not in ALLOWED_NVBIT_VERSIONS:
        raise ContractError("NVBit version is outside the frozen version-differential matrix")
    if not args.vectoradd.is_file() or not os.access(args.vectoradd, os.X_OK):
        raise ContractError("official NVBit smoke requires a built executable vectoradd test app")
    if not args.tool.is_file() or not valid_sha256(args.tool_sha256) or sha256_file(args.tool) != args.tool_sha256:
        raise ContractError("official NVBit smoke tool path/SHA is not closed")
    try:
        if str(uuid.UUID(args.run_id)) != args.run_id:
            raise ValueError
    except ValueError as exc:
        raise ContractError("official NVBit smoke run ID must be a canonical UUID") from exc
    for path in (args.receipt, args.stdout, args.stderr):
        if path.exists():
            raise ContractError(f"official NVBit smoke refuses to overwrite payload: {path}")
        path.parent.mkdir(parents=True, exist_ok=True)
    identity = {
        "deployment_id": DEPLOYMENT,
        "run_id": args.run_id,
        "scenario_id": f"NVBIT_{args.nvbit_version}_OFFICIAL_VECTORADD",
        "implementation_key": f"NVBIT_{args.nvbit_version}_OFFICIAL_INSTR_COUNT_BB",
    }
    MeasurementActive.assert_available(args.budget_ledger)
    started = time.monotonic()
    process: subprocess.Popen[str] | None = None
    timed_out = False
    try:
        with BudgetLease(args.budget_ledger, identity, "NVBIT_OFFICIAL_VECTORADD_SMOKE_DIAGNOSTIC", capture=False) as lease:
            with MeasurementActive(args.budget_ledger, identity, "NVBIT_OFFICIAL_VECTORADD_SMOKE_DIAGNOSTIC"):
                environment = os.environ.copy()
                environment.pop("LD_PRELOAD", None)
                environment.pop("CUDA_INJECTION64_PATH", None)
                for name in tuple(environment):
                    if name.startswith("C16_NVBIT_"):
                        environment.pop(name)
                contract = nvdisasm_environment_contract(args.nvdisasm, environment.get("PATH", ""))
                environment.update(contract)
                environment.update({
                    "CUDA_INJECTION64_PATH": str(args.tool),
                    "C16_NVBIT_LD_PRELOAD_DECLARATION": str(args.tool),
                })
                with args.stdout.open("w", encoding="utf-8") as stdout, args.stderr.open("w", encoding="utf-8") as stderr:
                    process = subprocess.Popen([str(args.vectoradd)], stdout=stdout, stderr=stderr, text=True, env=environment, start_new_session=True)
                    try:
                        process.wait(timeout=WALL_LIMIT_SECONDS)
                    except subprocess.TimeoutExpired:
                        timed_out = True
                        _kill_group(process)
            elapsed = time.monotonic() - started
            returncode = process.returncode if process is not None else None
            output = args.stdout.read_text(encoding="utf-8", errors="replace")
            evidence = official_evidence(output)
            passed = not timed_out and returncode == 0 and all(evidence.values())
            terminal_status = "COMPLETE" if passed else ("BOUNDED_TIMEOUT" if timed_out else "FAILED_OR_ABORTED")
            lease.finish(
                elapsed_seconds=elapsed, raw_bytes=0, terminal_status=terminal_status,
                evidence_classification="NON_SCIENTIFIC_DIAGNOSTIC",
                diagnostic_reason=f"NVBIT_{args.nvbit_version}_OFFICIAL_VECTORADD_INSTRUMENTATION_SMOKE_NO_TRACE_CAPTURE",
            )
        receipt: dict[str, Any] = {
            "schema_version": SCHEMA,
            "status": "NVBIT_OFFICIAL_VECTORADD_SMOKE_PASS" if passed else "NVBIT_OFFICIAL_VECTORADD_SMOKE_FAIL",
            "scientific_eligible": False,
            "diagnostic_only": True,
            "not_for_trace": True,
            "not_for_c_target": True,
            "runtime_code_commit": args.runtime_code_commit,
            "nvbit_version": args.nvbit_version,
            "run_id": args.run_id,
            "wall_limit_seconds": WALL_LIMIT_SECONDS,
            "tool": {"path": str(args.tool), "sha256": args.tool_sha256, "kind": f"NVBIT_{args.nvbit_version}_OFFICIAL_INSTR_COUNT_BB"},
            "nvdisasm_environment_contract": contract,
            "vectoradd": str(args.vectoradd),
            "returncode": returncode,
            "terminal_status": terminal_status,
            "elapsed_seconds": elapsed,
            "official_instrumentation_evidence": evidence,
            "stdout": {"path": str(args.stdout), "sha256": sha256_file(args.stdout)},
            "stderr": {"path": str(args.stderr), "sha256": sha256_file(args.stderr)},
            "trace_generated": False,
            "raw_trace_bytes": 0,
        }
        atomic_json(args.receipt, receipt)
        if not passed:
            raise ContractError("official NVBit vectoradd smoke did not reach all instrumentation evidence markers")
        print(f"PASS official NVBit vectoradd smoke: {args.receipt}")
    except Exception:
        if process is not None:
            _kill_group(process)
        raise


if __name__ == "__main__":
    try:
        main()
    except ContractError as exc:
        print(f"FAIL official NVBit vectoradd smoke: {exc}", file=sys.stderr)
        raise SystemExit(2)
