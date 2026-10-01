#!/usr/bin/env python3
"""CPU/source-only authority and asset preflight for the AWQ Observer V2 canary."""

import argparse
import ast
import hashlib
import json
import subprocess
from pathlib import Path


SOURCE_COMMIT = "f63d39c8d90ced038445c264fa8242c524a1aa6f"
SOURCE_TREE = "9855a156b7c13b7ab10c4747dcb0f5c5b05e3ac9"
RUNTIME_AUTHORITY = "3f62f909a474e4c56695ffacf36ddcb5d7b5f147"
RUNTIME_TREE = "4b9a1c07ee6b16997957d804f26ab57d0ca3853e"
BASE_SHA = "1f68c1117623cbc46f98f51f17ba798d8bf5ffb103f427b9d7b916ced0a35020"
PATCH_SHA = "7769e8b85480c2bfd3f178c77dcd3b66a6b8d5c7b8bf13c9f5002e9dc9b968c9"
V2_SHA = "7f2a76a375eaa4f652553fc523f785a753180ef1402291e54beb2256ed02bb22"
INPUT_SHA = "aeeadfecb7b95b140c902491ccc25ab1c0deffac3de6718acc567d2e307c414e"
MODEL = Path("/data/c16/stagea_runtime_qualification_v1/assets/qwen2.5-3b-instruct-awq/3559b226e8ce77211e2c1bd7ddfb7686fec4d6dd")
INPUT = Path("/data/c16/stagea_runtime_qualification_v1/inputs/QWEN_AWQ_TRAIN_A_DISCOVERY_00.json")
ENV_PYTHON = Path("/data/c16/envs/c16-vllm-v0.30.0-sm89-v1/bin/python")
RUNNER = Path("util/vm_tlb/c16/stagea_runtime_qualification/runner.py")
PACK = Path("docs/vm_tlb/review_packs/C16_STAGEA_LOW_OVERHEAD_OBSERVER_V2_SOURCE_QUALIFICATION_109_V1")
AUTH_PACK = Path("docs/vm_tlb/review_packs/C16_STAGEA_RUNTIME_QUALIFICATION_CANARY_109_V1")


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git(repo, *args):
    return subprocess.check_output(["git", *args], cwd=repo, text=True).strip()


def call_name(call):
    value = call.func
    parts = []
    while isinstance(value, ast.Attribute):
        parts.append(value.attr)
        value = value.value
    if isinstance(value, ast.Name):
        parts.append(value.id)
    return ".".join(reversed(parts))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    repo = args.repo.resolve()
    checks = {}

    checks["source_commit_exact"] = git(repo, "rev-parse", "HEAD") == SOURCE_COMMIT
    checks["source_tree_exact"] = git(repo, "rev-parse", "HEAD^{tree}") == SOURCE_TREE
    base = subprocess.check_output(["git", "show", f"{RUNTIME_AUTHORITY}:{RUNNER}"], cwd=repo)
    checks["runtime_authority_tree_exact"] = git(repo, "rev-parse", f"{RUNTIME_AUTHORITY}^{{tree}}") == RUNTIME_TREE
    checks["base_runner_sha_exact"] = hashlib.sha256(base).hexdigest() == BASE_SHA
    checks["patch_sha_exact"] = sha(repo / PACK / "OBSERVER_V2_SOURCE_DIFF.patch") == PATCH_SHA
    checks["v2_runner_sha_exact"] = sha(repo / RUNNER) == V2_SHA

    draft = json.loads((repo / PACK / "C16_AWQ_OBSERVER_V2_REQUAL_CANARY_DRAFT.json").read_text())
    checks["draft_goal_exact"] = draft["goal"] == "C16_AWQ_OBSERVER_V2_REQUAL_CANARY_109_V1"
    checks["draft_scope_exact"] = draft["scope"]["targets"] == ["QWEN_AWQ"] and draft["scope"]["graph_modes"] == ["GRAPH_OFF"]
    checks["draft_cap_exact"] = draft["protocol"]["gpu_active_seconds_cap"] == 60
    checks["draft_order_exact"] = draft["protocol"]["native_arm_order"] == ["OFF", "ON", "ON", "OFF", "OFF", "ON"]
    checks["draft_gate_exact"] = draft["acceptance"]["neutrality_expression"] == "abs(median_on_ms - median_off_ms) <= max(5.0, 0.10 * median_off_ms)"

    tree = ast.parse((repo / RUNNER).read_text())
    hook = next(node for node in ast.walk(tree) if isinstance(node, ast.ClassDef) and node.name == "HookSession")
    generate = next(node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == "generate")
    hook_calls = [call_name(node) for node in ast.walk(hook) if isinstance(node, ast.Call)]
    generate_calls = [call_name(node) for node in ast.walk(generate) if isinstance(node, ast.Call)]
    checks["per_occurrence_cuda_event_zero"] = hook_calls.count("torch.cuda.Event") == 0
    checks["request_cuda_event_pair_only"] = generate_calls.count("torch.cuda.Event") == 2
    checks["semantic_nvtx_push_pop"] = hook_calls.count("torch.cuda.nvtx.range_push") == 1 and hook_calls.count("torch.cuda.nvtx.range_pop") == 1
    hook_source = ast.get_source_segment((repo / RUNNER).read_text(), hook)
    checks["semantic_metadata_present"] = all(term in hook_source for term in ("ordinal", "module", "input_shape", "output_shape"))

    asset = json.loads((repo / AUTH_PACK / "ASSET_VISIBILITY_AND_SHA.json").read_text())
    awq = asset["models"]["QWEN_AWQ"]
    checks["model_path_exact"] = Path(awq["path"]) == MODEL
    checks["model_revision_exact"] = awq["revision"] == MODEL.name
    checks["quantization_exact"] = awq["quantization"] == {"bits": 4, "group_size": 128, "modules_to_not_convert": None, "quant_method": "awq", "version": "gemm", "zero_point": True}
    checks["no_requantization"] = awq["no_requantization"] is True
    model_rows = [row for row in asset["rows"] if row["model_key"] == "QWEN_AWQ"]
    asset_rows = []
    for row in model_rows:
        path = MODEL / row["path"]
        actual = sha(path)
        ok = path.stat().st_size == row["expected_bytes"] and actual == row["expected_sha256"]
        asset_rows.append({"path": row["path"], "bytes": path.stat().st_size, "sha256": actual, "pass": ok})
    checks["all_model_asset_hashes_exact"] = all(row["pass"] for row in asset_rows)
    checks["input_sha_exact"] = sha(INPUT) == INPUT_SHA
    tokens = json.loads(INPUT.read_text())
    checks["input_token_count_512"] = len(tokens) == 512

    package_text = subprocess.check_output([
        str(ENV_PYTHON), "-c",
        "import json,importlib.metadata as m; print(json.dumps({'python_package_vllm':m.version('vllm'),'python_package_torch':m.version('torch')},sort_keys=True))",
    ], text=True).strip()
    packages = json.loads(package_text)
    checks["runtime_python_exists"] = ENV_PYTHON.is_file()
    checks["vllm_version_exact"] = packages["python_package_vllm"] == "0.30.0"
    nsys_version = subprocess.check_output(["nsys", "--version"], text=True).strip()
    checks["nsys_available"] = "Nsight Systems" in nsys_version

    result = {
        "goal": "C16_AWQ_OBSERVER_V2_REQUAL_CANARY_109_V1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "source": {"commit": SOURCE_COMMIT, "tree": SOURCE_TREE, "base_runner_sha256": BASE_SHA,
                   "patch_sha256": PATCH_SHA, "v2_runner_sha256": V2_SHA},
        "runtime_authority": {"commit": RUNTIME_AUTHORITY, "tree": RUNTIME_TREE},
        "runtime": {"python": str(ENV_PYTHON), **packages, "nsys_version": nsys_version},
        "model": {"path": str(MODEL), "revision": MODEL.name, "asset_rows": asset_rows,
                  "no_requantization": True},
        "input": {"path": str(INPUT), "sha256": INPUT_SHA, "token_count": len(tokens)},
        "cuda_initialized": False,
        "gpu_lock_acquired": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": result["status"], "checks": checks}, sort_keys=True))
    if result["status"] != "PASS":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
