#!/usr/bin/env python3
"""CPU-only source and immutable-authority preflight."""

import argparse
import ast
import hashlib
import json
import py_compile
import subprocess
from pathlib import Path


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def find_function(tree, name):
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return node
    raise RuntimeError(f"function missing: {name}")


def source_segment(text, node):
    lines = text.splitlines()
    return "\n".join(lines[node.lineno - 1:node.end_lineno])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--base-commit", required=True)
    parser.add_argument("--authority-ref", required=True)
    parser.add_argument("--authority-commit", required=True)
    parser.add_argument("--authority-tree", required=True)
    parser.add_argument("--contract-sha", required=True)
    parser.add_argument("--base-runner-sha", required=True)
    args = parser.parse_args()
    runner_rel = "util/vm_tlb/c16/e1_operator_family_natural.py"
    runner = args.repo / runner_rel
    text = runner.read_text()
    tree = ast.parse(text)
    main_node = find_function(tree, "main")
    concurrent = find_function(tree, "concurrent_forward")
    concurrent_text = source_segment(text, concurrent)
    py_compile.compile(str(runner), doraise=True)
    base_bytes = subprocess.check_output(["git", "-C", str(args.repo), "show", f"{args.base_commit}:{runner_rel}"])
    base_sha = hashlib.sha256(base_bytes).hexdigest()
    contract = json.loads(args.contract.read_text())
    checks = {
        "worktree_head_is_accepted_timeline_producer": git(args.repo, "rev-parse", "HEAD") == args.base_commit,
        "authority_commit_exact": git(args.repo, "rev-parse", args.authority_ref) == args.authority_commit,
        "authority_tree_exact": git(args.repo, "rev-parse", args.authority_ref + "^{tree}") == args.authority_tree,
        "contract_sha_exact": sha256(args.contract) == args.contract_sha,
        "contract_status_qualified": contract["status"] == "QUALIFIED_FOR_NATIVE_CONCURRENCY_DIAGNOSTIC",
        "contract_binds_timeline_producer": contract["authority"]["timeline_producer_commit"] == args.base_commit,
        "base_runner_sha_exact": base_sha == args.base_runner_sha,
        "python_compile_pass": True,
        "toggle_default_off": 'parser.add_argument("--gate-up-concurrency", choices=("off", "on"), default="off")' in text,
        "exactly_two_producer_stream_constructors": text.count("torch.cuda.Stream()") == 2,
        "three_non_timing_dependency_events": concurrent_text.count("torch.cuda.Event(enable_timing=False)") == 3,
        "four_explicit_event_waits": concurrent_text.count("wait_event(") == 4,
        "hidden_lifetime_registered_on_both_producers": concurrent_text.count("hidden_state.record_stream(") == 2,
        "producer_outputs_registered_on_consumer": "activated.record_stream(original_stream)" in concurrent_text and "up.record_stream(original_stream)" in concurrent_text,
        "producer_policy_hooks_run_inside_stream_contexts": (concurrent_text.index("with torch.cuda.stream(gate_stream):") < concurrent_text.index("self.gate_proj(hidden_state)") and concurrent_text.index("with torch.cuda.stream(up_stream):") < concurrent_text.index("self.up_proj(hidden_state)")),
        "multiply_after_both_original_stream_waits": concurrent_text.index("original_stream.wait_event(gate_done)") < concurrent_text.index("lambda: activated * up") and concurrent_text.index("original_stream.wait_event(up_done)") < concurrent_text.index("lambda: activated * up"),
        "down_after_multiply_on_original_stream": concurrent_text.index("lambda: activated * up") < concurrent_text.index("self.down_proj(product)"),
        "no_synchronize_inside_concurrent_forward": "synchronize" not in concurrent_text,
        "no_stream_priority_sweep": "priority=" not in text,
        "same_runner_contains_b0_and_b1": 'if args.gate_up_concurrency == "on":' in source_segment(text, main_node) and 'elif args.timeline_nvtx == "on":' in source_segment(text, main_node),
        "outer_decode_wall_events_present": "decode_wall_start" in text and "decode_wall_stop" in text,
    }
    result = {
        "status": "PASS" if all(checks.values()) else "SOURCE_PREFLIGHT_FAILED",
        "checks": checks,
        "repo_head": git(args.repo, "rev-parse", "HEAD"),
        "repo_tree_before_scientific_commit": git(args.repo, "rev-parse", "HEAD^{tree}"),
        "base_commit": args.base_commit,
        "base_runner_sha256": base_sha,
        "patched_runner_sha256": sha256(runner),
        "contract_sha256": sha256(args.contract),
        "contract_status": contract["status"],
        "compile_mode": "py_compile CPU/source-only; no runner import",
        "off_path_statement": "toggle default is off; concurrency streams/events are constructed only in the explicit on branch",
    }
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))
    if result["status"] != "PASS":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
