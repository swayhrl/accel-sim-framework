#!/usr/bin/env python3
"""Run every C16-G offline contract check without importing CUDA/torch or raw data."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from c16_native_common import ContractError, atomic_json, repo_root
from prepare_gpu_package import DEFAULT_HANDOFF, DEFAULT_OUT, prepare, record_offline_dry_run, refresh_manifest, validate
from run_schema import validate_receipt


ROOT = repo_root()
LANE = ROOT / "util/vm_tlb/c16/lane_g"


def target() -> dict[str, object]:
    return {
        "run_id": "C16_G_OFFLINE_FIXTURE_RUN",
        "deployment_id": "C16_G_OFFLINE_FIXTURE_DEPLOYMENT",
        "scenario_id": "S0",
        "phase": "decode",
        "decode_step_bin": "1-4",
        "device": "MOCK_NO_GPU",
        "context": "fixture-context",
        "stream": "fixture-stream",
        "correlation_id": "fixture-correlation",
        "kernel_name": "fixture_kernel",
        "implementation_key": "fixture-implementation",
        "grid": "1,1,1",
        "block": "32,1,1",
        "operator_class": "UNKNOWN_OFFLINE_FIXTURE",
        "layer_id": "UNKNOWN",
        "shape_key": "fixture-shape",
        "dtype_key": "float16",
        "semantic_evidence": "OFFLINE_FIXTURE_NONSCIENTIFIC",
        "launch_ordinal": 7,
        "identity": {
            "model_id": "fixture/mock-model", "model_revision": "fixture-immutable-revision",
            "tokenizer_revision": "fixture-immutable-tokenizer", "deployment_id": "C16_G_OFFLINE_FIXTURE_DEPLOYMENT",
            "implementation_key": "fixture-implementation", "dtype": "float16", "quantization": "NONE",
            "scenario_id": "S0", "input_hash": "0" * 64, "run_id": "C16_G_OFFLINE_FIXTURE_RUN",
            "code_commit": "offline-fixture-only",
        },
        "runtime": {"device": "MOCK_NO_GPU", "profiler_mode": "MOCK_NO_GPU"},
    }


def execute(command: list[str]) -> None:
    completed = subprocess.run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if completed.returncode != 0:
        raise ContractError(f"offline command failed ({completed.returncode}): {' '.join(command)}\n{completed.stderr}")


def run(out: Path) -> None:
    prepare(out, DEFAULT_HANDOFF if out == DEFAULT_OUT else None)
    receipts: dict[str, object] = {}
    with tempfile.TemporaryDirectory(prefix="c16-g-offline-") as temporary:
        temp = Path(temporary)
        requested = temp / "requested.json"
        observed = temp / "observed.json"
        atomic_json(requested, target())
        atomic_json(observed, target())
        metrics = temp / "ncu_metrics.txt"
        metrics.write_text("l1tex__t_sectors_pipe_lsu_mem_global_op_ld.sum\nlts__t_sectors_op_read.sum\ndram__bytes_read.sum\n", encoding="utf-8")
        instance = temp / "instance.json"
        execute([sys.executable, str(LANE / "autodl_instance_receipt.py"), "--dry-run", "--work-root", str(temp / "autodl-work"), "--receipt", str(instance)])
        receipts["instance_receipt"] = {"status": "PASS", "mode": "DRY_RUN", "scientific_eligible": False}
        transfer = temp / "transfer.json"
        execute([sys.executable, str(LANE / "transfer_verify.py"), "--dry-run", "--expected-hashes", str(out / "EXPECTED_HASHES.tsv"), "--transfer-root", str(temp / "transfer"), "--receipt", str(transfer)])
        transfer_status = json.loads(transfer.read_text(encoding="utf-8"))["status"]
        if transfer_status != "BLOCKED_UPSTREAM_HASH_CLOSURE":
            raise ContractError("offline transfer preflight must expose, not hide, the A hash-closure gap")
        receipts["transfer_verify"] = {"status": "PASS", "mode": "DRY_RUN", "reported_gap": transfer_status}
        execute(["bash", str(LANE / "bootstrap_autodl.sh"), "--dry-run", "--wheelhouse", str(temp / "wheelhouse")])
        receipts["bootstrap"] = {"status": "PASS", "mode": "DRY_RUN", "no_gpu_query_download_or_install": True}
        runner = temp / "runner.json"
        execute([sys.executable, str(LANE / "run_model.py"), "--mode", "canary", "--mock", "--receipt", str(runner)])
        receipts["runner"] = {"status": "PASS", "mode": "MOCK", "scientific_eligible": False}
        validate_receipt(json.loads(runner.read_text(encoding="utf-8")), require_native=False)
        scenario = temp / "scenario.json"
        execute([sys.executable, str(LANE / "scenario_driver.py"), "--fixture", "--canary", "--receipt", str(scenario)])
        receipts["scenario_driver"] = {"status": "PASS", "mode": "OFFLINE_FIXTURE", "scientific_eligible": False}
        guard = temp / "guard.json"
        execute([sys.executable, str(LANE / "identity_guard.py"), "--requested", str(requested), "--observed", str(observed), "--receipt", str(guard)])
        receipts["identity_guard"] = {"status": "PASS", "naked_launch_ordinal_join_forbidden": True}
        for tool, wrapper in (("nsys", "nsys_wrapper.py"), ("ncu", "ncu_wrapper.py"), ("nvbit", "nvbit_wrapper.py")):
            receipt = temp / f"{tool}.json"
            command = [sys.executable, str(LANE / wrapper), "--receipt", str(receipt), "--target-json", str(requested), "--output", str(temp / f"{tool}.out"), "--dry-run"]
            if tool == "ncu":
                command += ["--metrics-file", str(metrics)]
            if tool == "nvbit":
                command += ["--nvbit-tool", str(temp / "nvbit_tool"), "--raw-dir", str(temp / "raw")]
            command += ["--", sys.executable, "-c", "print('offline fixture only')"]
            execute(command)
            receipts[tool] = {"status": "PASS", "mode": "DRY_RUN", "scientific_eligible": False}
            validate_receipt(json.loads(receipt.read_text(encoding="utf-8")), require_native=False)
    atomic_json(out / "OFFLINE_DRY_RUN_RECEIPTS.json", {"scientific_eligible": False, "mode": "OFFLINE_DRY_RUN", "receipts": receipts})
    record_offline_dry_run(out)
    refresh_manifest(out)
    validate(out)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    run(args.output_dir)
    print(f"PASS C16 G full offline dry-run suite: {args.output_dir}")


if __name__ == "__main__":
    try:
        main()
    except ContractError as exc:
        print(f"FAIL C16 G offline dry-run: {exc}", file=sys.stderr)
        raise SystemExit(2)
