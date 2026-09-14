#!/usr/bin/env python3
"""Parent-leased, bounded Llama Route-B Q2 dynamic-address qualification."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import uuid
from pathlib import Path
from typing import Any

from c16_native_common import ContractError, atomic_json, sha256_file
from execution_budget import MeasurementActive
from profiler_wrapper import write_parent_lease_closeout, write_parent_lease_start
from retry570_long_watch import nvdisasm_environment_contract
from retry570_recovery_v3_campaign_budget import RecoveryV3CampaignLease, initialize
from route_b_memory_event_host import parse_raw_jsonl, write_parse_manifest, write_verified_producer_manifest
from route_b_producer_q0 import ProducerBinding


def validate_events(raw: Path, producer: dict[str, Any], function: str) -> dict[str, Any]:
    parsed = parse_raw_jsonl(raw, producer)
    events = [json.loads(line) for line in raw.read_text(encoding="utf-8").splitlines()
              if json.loads(line).get("record_kind") == "LANE_EVENT"]
    if not events or any(event["function_mangled_name"] != function for event in events):
        raise ContractError("Q2 raw lacks only the closed exact-function lane events")
    if not any(int(event["gpu_va"]) != 0 for event in events):
        raise ContractError("Q2 raw has no nonzero GPU virtual address")
    return {"parse": parsed, "event_count": len(events),
            "nonzero_gpu_va_count": sum(int(event["gpu_va"]) != 0 for event in events),
            "static_mref_pairs": sorted({(int(event["static_index"]), int(event["mref_ordinal"])) for event in events})}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    for name in ("binding", "campaign_ledger", "historical_ledger", "tool", "static_map", "whitelist_json", "whitelist_tsv", "code_object", "receipt", "child_receipt", "parent_lease", "producer_manifest", "parse_manifest", "raw", "stdout", "stderr"):
        p.add_argument("--" + name.replace("_", "-"), type=Path, required=True)
    p.add_argument("--historical-sha256", required=True); p.add_argument("--tool-sha256", required=True)
    p.add_argument("--code-object-sha256", required=True); p.add_argument("--function", required=True)
    p.add_argument("--phase", choices=("PREFILL", "DECODE"), required=True); p.add_argument("--run-id", required=True)
    p.add_argument("--runtime-code-commit", required=True); p.add_argument("--expected-output-checksum", required=True)
    p.add_argument("--expected-attention-backend", required=True); p.add_argument("--budget-scope", required=True)
    p.add_argument("--nvdisasm", type=Path, required=True); p.add_argument("--event-capacity", type=int, default=262144)
    p.add_argument("--raw-cap-bytes", type=int, default=536870912); p.add_argument("--target-cap-seconds", type=int, default=120)
    a = p.parse_args()
    if str(uuid.UUID(a.run_id)) != a.run_id or a.event_capacity <= 0 or a.raw_cap_bytes <= 0:
        raise ContractError("Q2 run/capacity contract is invalid")
    if sha256_file(a.tool) != a.tool_sha256 or sha256_file(a.static_map) == "" or sha256_file(a.code_object) != a.code_object_sha256:
        raise ContractError("Q2 tool/static-map/code-object identity is not closed")
    if a.raw.exists() or a.receipt.exists() or a.child_receipt.exists():
        raise ContractError("Q2 refuses to overwrite retained evidence")
    # This must be byte-for-byte the identity recomputed by the child
    # ``nvbit_model_qualify`` wrapper.  Phase/function are capture metadata,
    # not lease identity: adding them would make a genuine parent lease look
    # like a budget bypass to the child verifier.
    identity = {"deployment_id": "c16_llama32_1b_frozen_compatible", "model_id": "meta-llama/Llama-3.2-1B",
                "model_revision": "4e20de362430cd3b72f300e6b0f18e50e7166e08", "tokenizer_revision": "4e20de362430cd3b72f300e6b0f18e50e7166e08",
                "implementation_key": "TRANSFORMERS_CAUSAL_LM", "dtype": "float16", "quantization": "NONE", "scenario_id": "S0",
                "input_hash": "bae0b908106146659663fa04f44bc03ec0da18cadb08c9ec357c140afc4d8208", "run_id": a.run_id, "code_commit": a.runtime_code_commit}
    initialize(ledger_path=a.campaign_ledger, historical_ledger=a.historical_ledger,
               expected_historical_sha256=a.historical_sha256, identity=identity, budget_scope=a.budget_scope)
    MeasurementActive.assert_available(a.campaign_ledger)
    a.raw.parent.mkdir(parents=True, exist_ok=True)
    binding = ProducerBinding(a.function, a.code_object, a.code_object_sha256, a.static_map,
                              sha256_file(a.static_map), "", a.raw_cap_bytes)
    # The host helper independently derives the whitelist SHA from the frozen JSON.
    from route_b_memory_event_host import load_whitelist
    from route_b_producer_q0 import whitelist_sha256
    binding = ProducerBinding(a.function, a.code_object, a.code_object_sha256, a.static_map,
                              sha256_file(a.static_map), whitelist_sha256(load_whitelist(a.whitelist_json)), a.raw_cap_bytes)
    producer = write_verified_producer_manifest(a.producer_manifest, binding, a.whitelist_json)
    started = time.monotonic(); terminal = "FAILED_OR_ABORTED"; cleanup: dict[str, Any] = {"required": False}
    with RecoveryV3CampaignLease(a.campaign_ledger, identity, "NVBIT", capture=True, budget_scope=a.budget_scope) as lease:
        if lease.max_elapsed_seconds < a.target_cap_seconds:
            raise ContractError("Q2 campaign lease cannot cover its cap")
        parent, token = write_parent_lease_start(a.parent_lease, {"identity": identity}, "route_b_q2", lease)
        env = os.environ.copy(); env.pop("LD_PRELOAD", None); env.update(nvdisasm_environment_contract(a.nvdisasm, env.get("PATH", "")))
        env.update({"CUDA_MODULE_LOADING": "EAGER", "CUDA_INJECTION64_PATH": str(a.tool), "C16_NVBIT_LD_PRELOAD_DECLARATION": str(a.tool),
                    "C16_G_PARENT_LEASE_RECEIPT": str(a.parent_lease), "C16_G_PARENT_LEASE_TOKEN": token,
                    "C16_G_MEASUREMENT_ACTIVE_MARKER": str(a.campaign_ledger.parent.parent / "control" / "MEASUREMENT_ACTIVE"),
                    "C16_ROUTE_B_VERIFIED_MANIFEST": str(a.producer_manifest), "C16_ROUTE_B_EXACT_FUNCTION_MANGLED": a.function,
                    "C16_ROUTE_B_WHITELIST_TSV": str(a.whitelist_tsv), "C16_ROUTE_B_RAW_JSONL": str(a.raw), "C16_ROUTE_B_RUN_ID": a.run_id,
                    "C16_ROUTE_B_DEPLOYMENT_ID": identity["deployment_id"], "C16_ROUTE_B_SCENARIO_ID": "S0", "C16_ROUTE_B_PHASE": a.phase,
                    "C16_ROUTE_B_DECODE_STEP": "ALL_CACHE_CORRECT_STEPS", "C16_ROUTE_B_EVENT_CAPACITY": str(a.event_capacity), "C16_ROUTE_B_HOST_OUTPUT_CAP_BYTES": str(a.raw_cap_bytes)})
        command = [sys.executable, str(Path(__file__).with_name("nvbit_model_qualify.py")), "--mode", "NVBIT_NOOP_CONTROL",
                   "--receipt", str(a.child_receipt), "--binding-receipt", str(a.binding), "--raw-dir", str(a.raw.parent),
                   "--budget-ledger", str(a.campaign_ledger), "--tool-path", str(a.tool), "--tool-sha256", a.tool_sha256,
                   "--adapter", "llama32_1b", "--implementation-key", "TRANSFORMERS_CAUSAL_LM", "--dtype", "float16", "--quantization", "NONE",
                   "--run-id", a.run_id, "--runtime-code-commit", a.runtime_code_commit, "--expected-output-checksum", a.expected_output_checksum,
                   "--expected-attention-backend", a.expected_attention_backend, "--parent-lease-receipt", str(a.parent_lease),
                   "--runtime-deployment-id", identity["deployment_id"], "--recovery-v3-generic", "--route-b-llama-s0"]
        with a.stdout.open("w", encoding="utf-8") as out, a.stderr.open("w", encoding="utf-8") as err:
            with MeasurementActive(a.campaign_ledger, identity, "ROUTE_B_Q2_DYNAMIC_CAPTURE"):
                child = subprocess.Popen(command, stdout=out, stderr=err, text=True, env=env, start_new_session=True)
                try: child.wait(timeout=a.target_cap_seconds)
                except subprocess.TimeoutExpired: child.kill(); child.wait(); cleanup = {"required": True, "kill_sent": True}
        if child.returncode != 0: raise ContractError("Q2 child failed; retained stdout/stderr are the exact boundary")
        result = validate_events(a.raw, producer, a.function); write_parse_manifest(a.parse_manifest, a.raw, producer)
        terminal = "COMPLETE"; elapsed = time.monotonic() - started
        lease.finish(elapsed_seconds=elapsed, raw_bytes=a.raw.stat().st_size, terminal_status=terminal,
                     evidence_classification="NON_SCIENTIFIC_DIAGNOSTIC", diagnostic_reason="ROUTE_B_Q2_DYNAMIC_ADDRESS_QUALIFICATION")
        close = write_parent_lease_closeout(a.parent_lease, lease, terminal_status=terminal, elapsed_seconds=elapsed, raw_bytes=a.raw.stat().st_size)
    atomic_json(a.receipt, {"schema_version": "C16_ROUTE_B_Q2_DYNAMIC_CAPTURE_V1", "status": terminal,
        "scientific_eligible_for_timing": False, "scientific_eligible_for_dynamic_address_evidence": terminal == "COMPLETE",
        "identity": identity, "producer_manifest": {"path": str(a.producer_manifest), "sha256": sha256_file(a.producer_manifest)},
        "static_map": {"path": str(a.static_map), "sha256": sha256_file(a.static_map)}, "whitelist": {"path": str(a.whitelist_json), "sha256": sha256_file(a.whitelist_json)},
        "raw": {"path": str(a.raw), "bytes": a.raw.stat().st_size, "sha256": sha256_file(a.raw)}, "parse_manifest": {"path": str(a.parse_manifest), "sha256": sha256_file(a.parse_manifest)},
        "result": result, "parent_lease_closeout": {"path": str(close), "sha256": sha256_file(close)}, "cleanup": cleanup})
    print(f"PASS Route-B Q2 dynamic capture: {a.receipt}")


if __name__ == "__main__":
    try: main()
    except ContractError as exc: print(f"FAIL Route-B Q2 dynamic capture: {exc}", file=sys.stderr); raise SystemExit(2)
