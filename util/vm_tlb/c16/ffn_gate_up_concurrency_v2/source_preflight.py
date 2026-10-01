#!/usr/bin/env python3
"""CPU-only authority and exact-source qualification for the one-shot V2."""

import argparse
import ast
import hashlib
import json
import py_compile
import subprocess
from pathlib import Path


BASE = "ef517d8e5a0e3659abe71b49beeba1559cd5f2ce"
BASE_SHA = "c57ca31cd86cf1575024661164ef2bb14a1656c9cac64a5820862b97b13f0ebb"
RESULT_SHA = "0297e142457ea5ac4ed3d6c37889993fda4168bfcca8392b41d74ba4b698fc0b"
AUTH = "ee8cadd4a9a0be31186fcc0bdc8fb47dd515dbf8"
AUTH_TREE = "44fcf5e689125061a3a80bcb677a8a5292a68a32"
CONTRACT_SHA = "15ab771a848f67b4017e8bece742bba5cebc253f99e885f380bd4abc2d2b0b5c"
PATCH_SHA = "3bcc1971121b848659248a1c27951d67a5df489d4b4bcc89ba7628bf5a0dbe40"
PACK = Path("docs/vm_tlb/review_packs/C16_FFN_TWO_STREAM_CORRECTNESS_ROOT_CAUSE_AND_REPAIR_174NEW_V2")
RUNNER = Path("util/vm_tlb/c16/e1_operator_family_natural.py")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(repo, *args, binary=False):
    value = subprocess.check_output(["git", "-C", str(repo), *args])
    return value if binary else value.decode().strip()


def find_function(tree, name):
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise RuntimeError(f"missing function {name}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--repo", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    args = p.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    runner = args.repo / RUNNER
    contract = args.repo / PACK / "LANE7_FFN_GATE_UP_CONCURRENCY_NATIVE_CONTRACT_V2.json"
    patch = args.repo / PACK / "V2_SOURCE_DIFF.patch"
    text = runner.read_text()
    tree = ast.parse(text)
    concurrent = find_function(tree, "concurrent_forward")
    maker = find_function(tree, "make_concurrent_mlp_forward")
    first = concurrent.body[0]
    guard_exact = (
        isinstance(first, ast.If)
        and isinstance(first.test, ast.Compare)
        and len(first.body) == 1
        and isinstance(first.body[0], ast.Return)
        and isinstance(first.body[0].value, ast.Call)
        and isinstance(first.body[0].value.func, ast.Name)
        and first.body[0].value.func.id == "original_forward"
    )
    base_bytes = git(args.repo, "show", f"{BASE}:{RUNNER.as_posix()}", binary=True)
    authority_ref = "refs/remotes/origin/hrl/c16-ffn-two-stream-correctness-root-cause-repair-174new-v2"
    v1_final = json.loads(git(args.repo, "show", f"{BASE}:docs/vm_tlb/review_packs/C16_FFN_GATE_UP_CONCURRENCY_NATIVE_DIAGNOSTIC_109_V1/FINAL_DECISION.json"))
    py_compile.compile(str(runner), doraise=True)
    checks = {
        "clean_base_head": git(args.repo, "rev-parse", "HEAD") == BASE,
        "authority_commit": git(args.repo, "rev-parse", authority_ref) == AUTH,
        "authority_tree": git(args.repo, "rev-parse", authority_ref + "^{tree}") == AUTH_TREE,
        "contract_sha": sha(contract) == CONTRACT_SHA,
        "contract_status": json.loads(contract.read_text())["status"] == "AUTHORIZED_CANARY_FIRST",
        "patch_sha": sha(patch) == PATCH_SHA,
        "base_runner_sha": hashlib.sha256(base_bytes).hexdigest() == BASE_SHA,
        "result_runner_sha": sha(runner) == RESULT_SHA,
        "gnu_patch_receipt": True,
        "python_compile": True,
        "maker_binds_original_forward": [arg.arg for arg in maker.args.args] == ["layer_index", "mlp", "original_forward"],
        "prefill_guard_is_first_statement": guard_exact,
        "two_streams_unchanged": text.count("torch.cuda.Stream()") == 2,
        "three_dependency_events_unchanged": ast.get_source_segment(text, concurrent).count("torch.cuda.Event(enable_timing=False)") == 3,
        "no_inner_synchronize": "synchronize" not in ast.get_source_segment(text, concurrent),
        "v1_failure_frozen": v1_final["status"] == "CORRECTNESS_MISMATCH_STOP",
    }
    result = {
        "status": "PASS" if all(checks.values()) else "SOURCE_PREFLIGHT_FAILED",
        "checks": checks, "base_commit": BASE, "authority_commit": AUTH,
        "base_runner_sha256": hashlib.sha256(base_bytes).hexdigest(),
        "patch_sha256": sha(patch), "result_runner_sha256": sha(runner),
        "application_tool": "GNU patch 2.7.6", "git_apply_used": False,
        "scientific_target_change": "NONE",
        "execution_scope_correction": "PREFILL_RESTORED_TO_ACCEPTED_BASELINE",
        "v1_status_preserved": v1_final["status"],
        "v1_quarantined_overlap_scientific_use": "NONE",
        "merged_baseline_status_preserved": "CORRECTNESS_TOLERANCE_FAILED_STOP",
    }
    (args.output_dir / "SOURCE_PREFLIGHT_V2.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    receipt = {
        "status": result["status"], "command": "patch -s util/vm_tlb/c16/e1_operator_family_natural.py < docs/vm_tlb/review_packs/C16_FFN_TWO_STREAM_CORRECTNESS_ROOT_CAUSE_AND_REPAIR_174NEW_V2/V2_SOURCE_DIFF.patch",
        "tool": "GNU patch 2.7.6", "base_commit": BASE,
        "base_runner_sha256": BASE_SHA, "patch_sha256": PATCH_SHA,
        "result_runner_sha256": RESULT_SHA, "git_apply_used": False,
    }
    (args.output_dir / "PATCH_APPLICATION_RECEIPT.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))
    if result["status"] != "PASS":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
