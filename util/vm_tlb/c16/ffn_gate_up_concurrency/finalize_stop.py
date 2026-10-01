#!/usr/bin/env python3
"""Create the review pack for the contract-mandated correctness STOP."""

import argparse
import csv
import hashlib
import json
import os
import platform
import shutil
import subprocess
from pathlib import Path


BASE = "071297ae7f4aa772a27fae0cf31ad47ab7d967be"
BASE_TREE = "1e6a4f5ed19dfc76f91795524a29ac652156c653"
AUTH = "30b3016a7ad5b5ef86a3494c784e072938dee6c5"
AUTH_TREE = "b111d2147d2aa4d8656695aa321b7c31517e1927"
CONTRACT_SHA = "4cc42ab8c36b191716e5dd41ec5eca49ab2d94d665a8960f76dcce8c07dece09"
SCIENTIFIC_IDENTITY = "08f38d7163da95e895aaba10d72231a6d350dfe2"


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def write_tsv(path, fields, rows):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--pack", type=Path, required=True)
    parser.add_argument("--remote-path", required=True)
    args = parser.parse_args()
    args.pack.mkdir(parents=True, exist_ok=True)
    preflight = json.loads((args.pack / "SOURCE_PREFLIGHT.json").read_text())
    failed = json.loads((args.pack / "FAILED_CANARY_AUDIT.json").read_text())
    contract = args.pack / "LANE7_FFN_GATE_UP_CONCURRENCY_NATIVE_CONTRACT.json"
    runner = args.repo / "util/vm_tlb/c16/e1_operator_family_natural.py"
    tools = args.repo / "util/vm_tlb/c16/ffn_gate_up_concurrency"
    source_contract = {
        "status": "PASS_AUTHORITY_AND_SOURCE_PREFLIGHT_THEN_CORRECTNESS_STOP",
        "task": "C16_FFN_GATE_UP_CONCURRENCY_NATIVE_DIAGNOSTIC_V1",
        "node": 109, "gpu": "RTX4080 / SM89", "condition": "CONTROL_GUD84",
        "lane6_branch": "hrl/c16-ffn-timeline-headroom-qualification-174new-v2",
        "lane6_commit": AUTH, "lane6_tree": AUTH_TREE,
        "contract_sha256": sha256(contract), "expected_contract_sha256": CONTRACT_SHA,
        "accepted_timeline_producer_commit": BASE, "accepted_timeline_producer_tree": BASE_TREE,
        "accepted_scientific_identity_commit": SCIENTIFIC_IDENTITY,
        "base_runner_sha256": preflight["base_runner_sha256"],
        "diagnostic_runner_sha256": sha256(runner),
        "raw_path_node109": str(args.raw), "raw_path_node164": args.remote_path,
        "matrix": {"B0": "CURRENT_SINGLE_STREAM_STRONG_RUNTIME",
                   "B1": "TWO_STREAM_GATE_UP_STRONG_BASELINE"},
        "scientific_expansion": False,
    }
    dump(args.pack / "SOURCE_AND_CONTRACT.json", source_contract)
    build = {
        "status": "PASS", "build_kind": "Python source / py_compile only",
        "same_runner_for_b0_b1": True, "binary_build": "NONE",
        "python_executable_for_gpu_runs": "/data/c16/env/c16-awq-v6/bin/python",
        "runner_sha256": sha256(runner),
        "tool_sha256": {path.name: sha256(path) for path in sorted(tools.glob("*")) if path.is_file()},
        "host_python": platform.python_version(),
    }
    dump(args.pack / "BUILD_RECEIPT.json", build)
    dependency = {
        "status": "STATIC_DEPENDENCY_CLOSURE_PASS_RUNTIME_CORRECTNESS_FAILED",
        "original_stream": ["record hidden_ready", "wait gate_done", "wait up_done", "multiply", "down_proj"],
        "gate_stream": ["wait hidden_ready", "gate_proj", "SiLU", "record gate_done"],
        "up_stream": ["wait hidden_ready", "up_proj", "record up_done"],
        "event_timing_enabled": False, "device_or_layer_synchronize_added": False,
        "policy_hook_execution": "inside actual gate/up stream contexts; down remains original stream",
        "runtime_acceptance": "REJECTED_BY_TOKEN_IDENTITY_STOP",
    }
    dump(args.pack / "STREAM_DEPENDENCY_RECEIPT.json", dependency)
    lifetime = {
        "status": "STATIC_RECORD_STREAM_PLAN_PRESENT_RUNTIME_SAFETY_NOT_ESTABLISHED",
        "hidden_state": {"producer": "original", "consumers": ["gate_stream", "up_stream"],
                         "handling": ["record_stream(gate_stream)", "record_stream(up_stream)", "hidden_ready waits"]},
        "activated": {"producer": "gate_stream", "consumer": "original",
                      "handling": ["gate_done wait", "record_stream(original_stream)"]},
        "up": {"producer": "up_stream", "consumer": "original",
               "handling": ["up_done wait", "record_stream(original_stream)"]},
        "use_after_free_claim": "NOT_MADE",
        "reason": "B1 token mismatch prevents runtime lifetime/race acceptance",
    }
    dump(args.pack / "LIFETIME_SAFETY_RECEIPT.json", lifetime)
    audit = f"""# B0/B1 implementation audit\n\nStatus: **CORRECTNESS_MISMATCH_STOP**.\n\n- Authority and contract SHA: exact PASS.\n- Accepted producer: `{BASE}` / tree `{BASE_TREE}`.\n- Base runner SHA256: `{preflight['base_runner_sha256']}`.\n- Diagnostic runner SHA256: `{sha256(runner)}`.\n- B0: opt-in is off; no producer stream or dependency-event construction occurs.\n- B1: exactly two producer streams and three non-timing dependency events per MLP call.\n- DAG: gate projection plus SiLU and up projection branch independently; original stream joins before multiply/down.\n- Lifetime: hidden is registered on both producers; activated/up are registered on original consumer.\n- No layer/device synchronize, busy-wait, priority change, kernel change, NCU, NVBit, SASS, or Accel-Sim was added.\n- Canary B0 passed frozen tokens. B1 produced `{failed['b1_tokens']}` instead of `{failed['expected_tokens']}`.\n- Per contract, formal timing was not started. Static lifetime intent is documented but runtime safety is not claimed.\n"""
    (args.pack / "B0_B1_IMPLEMENTATION_AUDIT.md").write_text(audit)
    not_run = {
        "status": "NOT_RUN_CORRECTNESS_MISMATCH_STOP", "reason": "B1 canary token mismatch",
        "formal_samples_b0": 0, "formal_samples_b1": 0,
        "primary_endpoint": "NOT_MEASURED", "bootstrap": "NOT_COMPUTED",
    }
    dump(args.pack / "BOOTSTRAP_RESULT.json", not_run)
    dump(args.pack / "ORACLE_REALIZATION.json", {**not_run, "oracle_reference_saving_ms": 7.732849,
                                                  "realization_fraction": None})
    dump(args.pack / "HELDOUT_VALIDATION.json", {**not_run, "d3": "NOT_RUN", "layers_14_27": "NOT_RUN"})
    final = {
        "status": "CORRECTNESS_MISMATCH_STOP", "formal_timing_started": False,
        "b1_overlap_structurally_observed_but_quarantined": failed["b1_overlap_count"] > 0,
        "b1_overlap_count_quarantined": failed["b1_overlap_count"],
        "correctness": {"expected": failed["expected_tokens"], "b0": failed["b0_tokens"], "b1": failed["b1_tokens"]},
        "kernel_identity_trace_only": {"global_inventory_equal": failed["global_kernel_name_grid_block_multiset_equal"],
                                       "per_semantic_inventory_equal": failed["per_semantic_kernel_inventory_equal"]},
        "classification": "NO_PERFORMANCE_CLASSIFICATION_CORRECTNESS_STOP",
        "next_step_qualified": False, "automatic_next_experiment": False,
    }
    dump(args.pack / "FINAL_DECISION.json", final)
    write_tsv(args.pack / "NATIVE_TIMING_RAW.tsv",
              ("status", "reason", "b0_samples", "b1_samples"),
              [{"status": not_run["status"], "reason": not_run["reason"], "b0_samples": 0, "b1_samples": 0}])
    write_tsv(args.pack / "ABBA_BLOCK_SUMMARY.tsv",
              ("status", "reason", "completed_blocks"),
              [{"status": not_run["status"], "reason": not_run["reason"], "completed_blocks": 0}])
    shutil.copyfile(args.raw / "GPU_LOCK_RECEIPT.json", args.pack / "GPU_LOCK_RECEIPT.json")
    tests = {
        "status": "PASS_STOP_BEHAVIOR",
        "source_preflight": preflight["status"], "python_compile": "PASS", "shell_syntax": "PASS",
        "b0_canary": "PASS", "b1_canary": "CORRECTNESS_MISMATCH_STOP",
        "formal_launch_guard": "PASS_ZERO_FORMAL_SAMPLES", "gpu_lock_released": True,
        "forbidden_tool_use": {"NCU": False, "NVBit": False, "SASS": False, "Accel-Sim": False},
    }
    dump(args.pack / "TESTS.json", tests)
    readme = """# C16 FFN gate/up concurrency native diagnostic — Lane 7\n\nThe CPU/source preflight passed, but the B1 timeline canary violated the frozen token identity. The contract therefore required an immediate correctness STOP. No formal timing samples, bootstrap inference, oracle realization, held-out validation, or performance classification were produced.\n\nThe two NSYS traces are retained only as quarantined structural/debug evidence. Their apparent overlap and kernel inventory cannot support a performance claim while correctness is false. Large raw artifacts are published to the node164 provenance path recorded in `SOURCE_AND_CONTRACT.json`.\n"""
    (args.pack / "README.md").write_text(readme)
    stop = {"status": "CORRECTNESS_MISMATCH_STOP", "expected_tokens": failed["expected_tokens"],
            "observed_b1_tokens": failed["b1_tokens"], "formal_timing_started": False,
            "gpu_lock_released": True, "review_pack": str(args.pack)}
    dump(args.raw / "CORRECTNESS_MISMATCH_STOP.json", stop)
    print(json.dumps(final, sort_keys=True))


if __name__ == "__main__":
    main()
