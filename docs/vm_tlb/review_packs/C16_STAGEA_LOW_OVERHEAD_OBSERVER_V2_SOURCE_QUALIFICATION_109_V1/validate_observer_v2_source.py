#!/usr/bin/env python3
"""Static, import-free qualification checks for the Stage A V2 observer."""

import argparse
import ast
import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path


EXPECTED_BASE_SHA256 = "1f68c1117623cbc46f98f51f17ba798d8bf5ffb103f427b9d7b916ced0a35020"
EXPECTED_GATE = "abs(median_on-median_off) <= max(5.0 ms, 0.10*median_off)"
RUNNER_PATH = "util/vm_tlb/c16/stagea_runtime_qualification/runner.py"


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def parse(data):
    return ast.parse(data.decode("utf-8"))


def find_named(tree, kind, name):
    nodes = [node for node in ast.walk(tree) if isinstance(node, kind) and node.name == name]
    if len(nodes) != 1:
        raise AssertionError(f"expected one {kind.__name__} named {name}, got {len(nodes)}")
    return nodes[0]


def call_name(node):
    parts = []
    value = node.func
    while isinstance(value, ast.Attribute):
        parts.append(value.attr)
        value = value.value
    if isinstance(value, ast.Name):
        parts.append(value.id)
    return ".".join(reversed(parts))


def calls(node, name):
    return [item for item in ast.walk(node) if isinstance(item, ast.Call) and call_name(item) == name]


def normalized_named(tree, kind, name):
    return ast.dump(find_named(tree, kind, name), include_attributes=False)


def normalized_assignment(tree, name):
    nodes = [node for node in tree.body if isinstance(node, ast.Assign)
             and any(isinstance(target, ast.Name) and target.id == name for target in node.targets)]
    if len(nodes) != 1:
        raise AssertionError(f"expected one assignment named {name}, got {len(nodes)}")
    return ast.dump(nodes[0], include_attributes=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--base-commit", default="3f62f909a474e4c56695ffacf36ddcb5d7b5f147")
    parser.add_argument("--patch", type=Path, required=True)
    parser.add_argument("--thresholds", type=Path, required=True)
    args = parser.parse_args()

    repo = args.repo.resolve()
    candidate_path = repo / RUNNER_PATH
    candidate = candidate_path.read_bytes()
    base = subprocess.check_output(["git", "show", f"{args.base_commit}:{RUNNER_PATH}"], cwd=repo)
    assert sha256(base) == EXPECTED_BASE_SHA256

    compile(candidate, str(candidate_path), "exec")
    base_tree = parse(base)
    candidate_tree = parse(candidate)
    hook = find_named(candidate_tree, ast.ClassDef, "HookSession")
    generate = find_named(candidate_tree, ast.FunctionDef, "generate")

    assert len(calls(hook, "torch.cuda.Event")) == 0
    assert len(calls(hook, "torch.cuda.nvtx.range_push")) == 1
    assert len(calls(hook, "torch.cuda.nvtx.range_pop")) == 1
    assert len(calls(generate, "torch.cuda.Event")) == 2
    assert normalized_named(base_tree, ast.FunctionDef, "generate") == normalized_named(candidate_tree, ast.FunctionDef, "generate")
    assert normalized_named(base_tree, ast.FunctionDef, "select_semantic_modules") == normalized_named(candidate_tree, ast.FunctionDef, "select_semantic_modules")
    assert normalized_named(base_tree, ast.FunctionDef, "profiler_inventory") == normalized_named(candidate_tree, ast.FunctionDef, "profiler_inventory")
    assert normalized_assignment(base_tree, "TARGETS") == normalized_assignment(candidate_tree, "TARGETS")

    hook_text = ast.get_source_segment(candidate.decode("utf-8"), hook)
    for required in ("ordinal", "module", "input_shape", "output_shape", "semantic_order_sha256", "semantic_ranges_sha256"):
        assert required in hook_text
    assert "event_timings_ms" not in hook_text

    threshold = json.loads(args.thresholds.read_text())
    assert threshold["instrumentation_neutrality"]["samples_per_arm"] == 3
    assert threshold["instrumentation_neutrality"]["wall_gate"] == EXPECTED_GATE
    assert threshold["correctness"]["generated_token_ids"] == "exact equality"
    assert threshold["correctness"]["shapes_and_semantic_order"] == "exact equality"

    with tempfile.TemporaryDirectory(prefix="c16_observer_v2_replay_") as temp_name:
        root = Path(temp_name)
        replay_path = root / RUNNER_PATH
        replay_path.parent.mkdir(parents=True)
        replay_path.write_bytes(base)
        subprocess.run(["patch", "-s", "-p1", "-i", str(args.patch.resolve())],
                       cwd=root, check=True)
        assert replay_path.read_bytes() == candidate

    report = {
        "status": "PASS",
        "base_runner_sha256": sha256(base),
        "candidate_runner_sha256": sha256(candidate),
        "patch_sha256": sha256(args.patch.read_bytes()),
        "hooksession_cuda_event_constructors": 0,
        "request_level_cuda_event_constructors": 2,
        "selector_unchanged": True,
        "target_configuration_unchanged": True,
        "profiler_inventory_unchanged": True,
        "outer_request_timing_unchanged": True,
        "neutrality_gate_unchanged": True,
        "clean_base_patch_replay_exact": True,
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
