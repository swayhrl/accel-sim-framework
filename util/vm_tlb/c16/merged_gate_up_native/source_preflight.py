#!/usr/bin/env python3
"""Source-only guard for the independent merged gate/up native goal."""

import argparse
import ast
import hashlib
import json
import py_compile
import subprocess
from pathlib import Path


BASE = "071297ae7f4aa772a27fae0cf31ad47ab7d967be"
FAILED_TWO_STREAM = "ef517d8e5a0e3659abe71b49beeba1559cd5f2ce"
CONTRACT_SHA = "b843c11381b0451e958087aa825869da00f9624ebd8389673d02fa33a0a298c3"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(repo, *args, check=True):
    result = subprocess.run(["git", "-C", str(repo), *args], text=True, capture_output=True)
    if check and result.returncode:
        raise RuntimeError(result.stderr)
    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--repo", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    b0 = args.repo / "util/vm_tlb/c16/e1_operator_family_natural.py"
    tools = args.repo / "util/vm_tlb/c16/merged_gate_up_native"
    b2 = tools / "b2_runner.py"
    lock = tools / "run_locked.sh"
    contract = args.repo / "docs/vm_tlb/review_packs/C16_MERGED_GATE_UP_NATIVE_STRONG_BASELINE_109_V1/AUTHORITY_CONTRACT.json"
    cpu = args.repo / "docs/vm_tlb/review_packs/C16_MERGED_GATE_UP_NATIVE_STRONG_BASELINE_109_V1/CPU_PREFLIGHT.json"
    for path in [b0, b2, tools / "compare_canary.py", tools / "timeline_audit.py", tools / "postprocess.py", tools / "cpu_preflight.py"]:
        ast.parse(path.read_text())
        py_compile.compile(str(path), doraise=True)
    base_bytes = subprocess.check_output(["git", "-C", str(args.repo), "show", f"{BASE}:util/vm_tlb/c16/e1_operator_family_natural.py"])
    b0_text, b2_text, lock_text = b0.read_text(), b2.read_text(), lock.read_text()
    failed_ancestor = git(args.repo, "merge-base", "--is-ancestor", FAILED_TWO_STREAM, "HEAD", check=False).returncode == 0
    checks = {
        "head_is_accepted_timeline_producer": git(args.repo, "rev-parse", "HEAD").stdout.strip() == BASE,
        "failed_two_stream_commit_not_ancestor": not failed_ancestor,
        "base_runner_sha": hashlib.sha256(base_bytes).hexdigest() == "ad922629a9898c01400a165b2f6565659f1c6e422784c10bc1d013265c45b5fb",
        "contract_sha": sha(contract) == CONTRACT_SHA,
        "cpu_preflight_pass": json.loads(cpu.read_text())["status"] == "PASS",
        "all_python_compile": True,
        "b0_has_no_two_stream_toggle": "gate-up-concurrency" not in b0_text and "torch.cuda.Stream" not in b0_text,
        "b0_changes_observational_only": "ffn-baseline-measurement" in b0_text and "decode_wall_start" in b0_text,
        "b2_uses_pinned_local_checkpoint": "b25037543e9394b818fdfca67ab2a00ecc7dd641" in b2_text,
        "b2_uses_merged_qwen2_mlp": "Qwen2MLP" in b2_text and "gate_up_proj" in b2_text and "silu_and_mul" in b2_text,
        "b2_inproc_exact_step_control": 'VLLM_ENABLE_V1_MULTIPROCESSING", "0"' in b2_text and "engine.step()" in b2_text,
        "b2_no_requantization_code": "quantize" not in b2_text.lower() and "requant" not in b2_text.lower().replace("no_requantization", ""),
        "single_outer_lock": lock_text.count("flock -w 2700") == 1,
        "gpu_budget_480_seconds": "TOTAL_MAX_GPU_WALL_SECONDS=480" in lock_text and "PRIOR_GPU_WALL_SECONDS" in lock_text,
        "formal_abba_fixed": "for block in $(seq 0 11)" in lock_text,
        "forbidden_tools_absent": all(token not in lock_text for token in ("ncu", "nvbit", "sass", "accel-sim")),
    }
    result = {"status": "PASS" if all(checks.values()) else "SOURCE_PREFLIGHT_FAILED",
              "checks": checks, "base_commit": BASE,
              "base_runner_sha256": hashlib.sha256(base_bytes).hexdigest(),
              "b0_runner_sha256": sha(b0), "b2_runner_sha256": sha(b2),
              "contract_sha256": sha(contract),
              "comparison_class": "same checkpoint and logical AWQ semantics; cross-runtime strong baseline",
              "failed_two_stream_frozen": not failed_ancestor}
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))
    if result["status"] != "PASS":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
