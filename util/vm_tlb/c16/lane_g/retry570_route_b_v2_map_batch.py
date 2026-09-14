#!/usr/bin/env python3
"""Run the bounded V2 Route-B map-only batch without pre-assigning owners."""
from __future__ import annotations

import argparse
import csv
import json
import subprocess
import time
import uuid
from hashlib import sha256
from pathlib import Path
from typing import Any

from c16_native_common import atomic_json, sha256_file


def code_object_manifest(path: Path, roots: list[Path]) -> dict[str, str]:
    """Hash only actual candidate DSOs; the injected tool chooses the owner."""
    files = sorted({item.resolve() for root in roots if root.is_dir()
                    for item in root.rglob("*.so*") if item.is_file()})
    if not files:
        raise ValueError("no candidate code objects")
    closed = {str(item): sha256_file(item) for item in files}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(f"{name}\t{digest}\n" for name, digest in closed.items()), encoding="utf-8")
    return closed


def inventory_functions(path: Path) -> list[str]:
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    functions = sorted({row["function_mangled_name"] for row in rows if row.get("function_mangled_name")})
    if not functions:
        raise ValueError("launch inventory contains no exact mangled functions")
    return functions


def state(path: Path, *, active: str, remaining: int, next_job: str) -> None:
    atomic_json(path, {"schema_version": "C16_GPU_PIPELINE_STATE_V1", "timestamp_unix": time.time(),
                       "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
                       "gpu_active_job": active, "gpu_ready_queue_count": remaining,
                       "next_gpu_job": next_job, "measurement_active": active != "none",
                       "active_gpu_process_count": 1 if active != "none" else 0,
                       "transfer_slot_granted": True})


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    for name in ("python", "runner", "binding", "campaign_ledger", "historical_ledger", "tool", "nvdisasm", "inventory", "output_root", "control_state"):
        p.add_argument("--" + name.replace("_", "-"), type=Path, required=True)
    p.add_argument("--historical-ledger-sha256", required=True)
    p.add_argument("--tool-sha256", required=True)
    p.add_argument("--runtime-code-commit", required=True)
    p.add_argument("--expected-output-checksum", required=True)
    p.add_argument("--expected-attention-backend", required=True)
    p.add_argument("--candidate-root", type=Path, action="append", required=True)
    p.add_argument("--skip-function", action="append", default=[],
                   help="exact mangled function with an already V2 owner-closed map")
    p.add_argument("--max-functions", type=int, default=0)
    args = p.parse_args()
    functions = inventory_functions(args.inventory)
    functions = [item for item in functions if item not in set(args.skip_function)]
    if args.max_functions:
        functions = functions[:args.max_functions]
    manifest = args.output_root / "CODE_OBJECT_MANIFEST.tsv"
    code_object_manifest(manifest, args.candidate_root)
    summary: list[dict[str, Any]] = []
    for ordinal, function in enumerate(functions):
        run_id = str(uuid.uuid4()); run = args.output_root / "runs" / run_id
        digest = sha256(function.encode()).hexdigest()[:16]
        state(args.control_state, active=f"Route-B/V2_MAP/{digest}", remaining=len(functions) - ordinal,
              next_job=function)
        command = [str(args.python), str(args.runner), "--mode", "NVBIT_STATIC_MAP_V2", "--phase", "PREFILL",
                   "--binding", str(args.binding), "--campaign-ledger", str(args.campaign_ledger),
                   "--historical-ledger", str(args.historical_ledger), "--historical-ledger-sha256", args.historical_ledger_sha256,
                   "--tool", str(args.tool), "--tool-sha256", args.tool_sha256, "--nvdisasm", str(args.nvdisasm),
                   "--receipt", str(run / "PARENT_RECEIPT.json"), "--child-receipt", str(run / "CHILD_RECEIPT.json"),
                   "--parent-lease-receipt", str(run / "PARENT_LEASE.json"), "--stdout", str(run / "stdout.log"),
                   "--stderr", str(run / "stderr.log"), "--raw-dir", str(run / "raw"),
                   "--budget-scope", f"c16_llama32_1b_frozen_compatible/S0/ROUTE_B_V2_MAP_{digest}",
                   "--recovery-deployment-id", "c16_llama32_1b_frozen_compatible", "--adapter", "llama32_1b",
                   "--implementation-key", "TRANSFORMERS_CAUSAL_LM", "--dtype", "float16", "--quantization", "NONE",
                   "--run-id", run_id, "--runtime-code-commit", args.runtime_code_commit,
                   "--expected-output-checksum", args.expected_output_checksum,
                   "--expected-attention-backend", args.expected_attention_backend,
                   "--target-function", function, "--code-object-manifest", str(manifest),
                   "--route-b-llama-s0", "--target-cap-seconds", "120"]
        run.mkdir(parents=True, exist_ok=False)
        completed = subprocess.run(command, text=True, capture_output=True, check=False)
        receipt = run / "PARENT_RECEIPT.json"
        payload: dict[str, Any] = {"function_mangled_name": function, "run_id": run_id,
                                   "returncode": completed.returncode, "run_root": str(run),
                                   "stdout_sha256": sha256_file(run / "stdout.log") if (run / "stdout.log").is_file() else None,
                                   "stderr_sha256": sha256_file(run / "stderr.log") if (run / "stderr.log").is_file() else None}
        if receipt.is_file():
            payload["receipt"] = json.loads(receipt.read_text(encoding="utf-8"))
        summary.append(payload)
        atomic_json(args.output_root / "ROUTE_B_V2_MAP_BATCH_PROGRESS.json", {"functions": summary})
    state(args.control_state, active="none", remaining=0, next_job="Route-B/V2_RESULT_PUBLICATION")


if __name__ == "__main__":
    main()
