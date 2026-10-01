#!/usr/bin/env python3
"""CPU-only root-cause audit and source qualification for FFN two-stream V2."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path


FAILED_PRODUCER = "ef517d8e5a0e3659abe71b49beeba1559cd5f2ce"
FAILED_TREE = "12b002aeb3376a340ac15f848e1e97b3d52a5937"
AUTHORITY_COMMIT = "30b3016a7ad5b5ef86a3494c784e072938dee6c5"
CONTRACT_SHA = "4cc42ab8c36b191716e5dd41ec5eca49ab2d94d665a8960f76dcce8c07dece09"
RUNNER = "util/vm_tlb/c16/e1_operator_family_natural.py"
V1_RUNNER_SHA = "c57ca31cd86cf1575024661164ef2bb14a1656c9cac64a5820862b97b13f0ebb"
PATCH_SHA = "3bcc1971121b848659248a1c27951d67a5df489d4b4bcc89ba7628bf5a0dbe40"
V2_RUNNER_SHA = "0297e142457ea5ac4ed3d6c37889993fda4168bfcca8392b41d74ba4b698fc0b"
PACK_IN = "docs/vm_tlb/review_packs/C16_FFN_GATE_UP_CONCURRENCY_NATIVE_DIAGNOSTIC_109_V1"
PACK_OUT = "docs/vm_tlb/review_packs/C16_FFN_TWO_STREAM_CORRECTNESS_ROOT_CAUSE_AND_REPAIR_174NEW_V2"
PATCH_NAME = "V2_SOURCE_DIFF.patch"
AUTOAWQ_WHEEL_SHA = "02e09d71ca961ca131ac9963a2635fe8c34eb52d6b6a104b8574056aef8f2efe"
AUTOAWQ_GEMM_SHA = "7cdf8fb01dabbfcd7f8be8bb58dcaf68a76073f2f91fc0e7c96881094e6a2913"
AUTOAWQ_METADATA_SHA = "a1507a39c59e1e76d2d782d8ea9846c8c02cfbb6ad2818b8a23a6a1b4eb02f4d"
WHEEL_DEFAULT = Path("/tmp/c16_autoawq_wheel.0psIuQ/autoawq-0.2.7.post3-py3-none-any.whl")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_bytes(repo: Path, commit: str, path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{commit}:{path}"], cwd=repo)


def read_failed_json(repo: Path, name: str) -> dict:
    return json.loads(git_bytes(repo, FAILED_PRODUCER, f"{PACK_IN}/{name}"))


def functions(tree: ast.AST, name: str) -> list[ast.FunctionDef]:
    return [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == name]


def dump_nodes(nodes: list[ast.stmt]) -> str:
    return ast.dump(ast.Module(body=nodes, type_ignores=[]), include_attributes=False)


def qualify_source(repo: Path, patch_path: Path) -> dict:
    v1 = git_bytes(repo, FAILED_PRODUCER, RUNNER)
    if sha256(v1) != V1_RUNNER_SHA:
        raise AssertionError("V1 runner SHA mismatch")
    patch = patch_path.read_bytes()
    if sha256(patch) != PATCH_SHA:
        raise AssertionError("V2 patch SHA mismatch")
    with tempfile.TemporaryDirectory(prefix="c16_ffn_v2_source_") as temp_name:
        target = Path(temp_name) / "e1_operator_family_natural.py"
        target.write_bytes(v1)
        applied = subprocess.run(["patch", "-s", str(target)], input=patch, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        if applied.returncode != 0:
            raise AssertionError(applied.stderr.decode(errors="replace"))
        v2 = target.read_bytes()
    if sha256(v2) != V2_RUNNER_SHA:
        raise AssertionError("V2 runner SHA mismatch")
    compile(v2, RUNNER, "exec")
    v1_text, v2_text = v1.decode(), v2.decode()
    v1_tree, v2_tree = ast.parse(v1_text), ast.parse(v2_text)
    v1_outer = functions(v1_tree, "make_concurrent_mlp_forward")[0]
    v2_outer = functions(v2_tree, "make_concurrent_mlp_forward")[0]
    v1_inner = [node for node in v1_outer.body if isinstance(node, ast.FunctionDef) and node.name == "concurrent_forward"][0]
    v2_inner = [node for node in v2_outer.body if isinstance(node, ast.FunctionDef) and node.name == "concurrent_forward"][0]
    guard = v2_inner.body[0]
    if not isinstance(guard, ast.If) or len(guard.body) != 1 or not isinstance(guard.body[0], ast.Return):
        raise AssertionError("prefill guard is not first in concurrent_forward")
    if "active_decode" not in ast.dump(guard.test) or "original_forward" not in ast.dump(guard.body[0]):
        raise AssertionError("prefill guard does not call bound original forward")
    if dump_nodes(v2_inner.body[1:]) != dump_nodes(v1_inner.body):
        raise AssertionError("V1 event DAG changed beyond the prefill guard")
    if len(v2_outer.args.args) != len(v1_outer.args.args) + 1 or v2_outer.args.args[-1].arg != "original_forward":
        raise AssertionError("bound original forward was not explicitly captured")
    v1_seq = functions(v1_tree, "make_sequential_mlp_forward")[0]
    v2_seq = functions(v2_tree, "make_sequential_mlp_forward")[0]
    if ast.dump(v1_seq, include_attributes=False) != ast.dump(v2_seq, include_attributes=False):
        raise AssertionError("B0/sequential source changed")
    if v2_text.count("torch.cuda.Stream()") != 2:
        raise AssertionError("V2 does not construct exactly two producer streams")
    concurrent_source = ast.get_source_segment(v2_text, v2_inner) or ""
    if "synchronize" in concurrent_source:
        raise AssertionError("synchronize added inside concurrent forward")
    if v2_text.index('original_mlp_forwards[layer_index] = layer.mlp.forward') > v2_text.index('layer.mlp.forward = make_concurrent_mlp_forward('):
        raise AssertionError("original bound method is saved after replacement")
    if not (v2_text.index('active_decode["value"] = decode_index') < v2_text.index("result = model(input_ids=current")):
        raise AssertionError("decode activation guard is not set before model execution")
    import_dump_v1 = [ast.dump(node, include_attributes=False) for node in v1_tree.body if isinstance(node, (ast.Import, ast.ImportFrom))]
    import_dump_v2 = [ast.dump(node, include_attributes=False) for node in v2_tree.body if isinstance(node, (ast.Import, ast.ImportFrom))]
    if import_dump_v1 != import_dump_v2:
        raise AssertionError("new kernel/backend import introduced")
    return {
        "base_runner_sha256": V1_RUNNER_SHA,
        "patch_sha256": PATCH_SHA,
        "result_runner_sha256": V2_RUNNER_SHA,
        "application_tool": "GNU patch",
        "git_apply_authorized": False,
        "tool_version": subprocess.check_output(["patch", "--version"], text=True).splitlines()[0],
        "exact_command": f"patch -s {RUNNER} < {PACK_OUT}/{PATCH_NAME}",
        "checks": {
            "python_compile": True,
            "prefill_first_statement_returns_bound_original_forward": True,
            "decode_enables_concurrent_path_before_model_call": True,
            "exactly_two_producer_streams": True,
            "event_dag_byte_semantics_equal_after_guard": True,
            "no_synchronize": True,
            "no_new_kernel_or_backend_import": True,
            "original_forward_saved_before_replacement": True,
            "B0_sequential_function_ast_unchanged": True,
        },
    }


def validate_authority(repo: Path) -> dict:
    tree = subprocess.check_output(["git", "rev-parse", f"{FAILED_PRODUCER}^{{tree}}"], cwd=repo, text=True).strip()
    if tree != FAILED_TREE:
        raise AssertionError("failed producer tree mismatch")
    manifest = git_bytes(repo, FAILED_PRODUCER, f"{PACK_IN}/SHA256SUMS").decode()
    for line in manifest.splitlines():
        expected, name = line.split("  ", 1)
        if sha256(git_bytes(repo, FAILED_PRODUCER, f"{PACK_IN}/{name}")) != expected:
            raise AssertionError(f"V1 producer SHA mismatch: {name}")
    contract_path = repo / "docs/vm_tlb/review_packs/C16_FFN_TIMELINE_HEADROOM_QUALIFICATION_174NEW_V2/LANE7_FFN_GATE_UP_CONCURRENCY_NATIVE_CONTRACT.json"
    if sha256(contract_path.read_bytes()) != CONTRACT_SHA:
        raise AssertionError("qualified contract SHA mismatch")
    final = read_failed_json(repo, "FINAL_DECISION.json")
    failed = read_failed_json(repo, "FAILED_CANARY_AUDIT.json")
    b0 = read_failed_json(repo, "TIMELINE_CANARY_B0.json")
    b1 = read_failed_json(repo, "TIMELINE_CANARY_B1.json")
    if final["status"] != "CORRECTNESS_MISMATCH_STOP" or final["formal_timing_started"]:
        raise AssertionError("V1 failure quarantine/status drift")
    if b0["generated_tokens"] != [23578, 11, 323, 3950] or b1["observed_tokens"] != [143907, 11, 476, 304]:
        raise AssertionError("V1 token evidence drift")
    return {"manifest_sha256": sha256(manifest.encode()), "manifest_count": len(manifest.splitlines()), "final": final, "failed": failed, "b0": b0, "b1": b1}


def audit_autoawq(repo: Path, wheel: Path) -> dict:
    wheel_bytes = wheel.read_bytes()
    if sha256(wheel_bytes) != AUTOAWQ_WHEEL_SHA:
        raise AssertionError("AutoAWQ wheel SHA mismatch")
    with zipfile.ZipFile(wheel) as archive:
        gemm = archive.read("awq/modules/linear/gemm.py")
        metadata = archive.read("autoawq-0.2.7.post3.dist-info/METADATA")
    if sha256(gemm) != AUTOAWQ_GEMM_SHA or sha256(metadata) != AUTOAWQ_METADATA_SHA:
        raise AssertionError("AutoAWQ wheel source/metadata mismatch")
    text = gemm.decode()
    required = [
        'awq_ext, msg = try_import("awq_ext")',
        "FP16_MATMUL_HEURISTIC_CONDITION = x.shape[0] * x.shape[1] >= 1024",
        "out = awq_ext.dequantize_weights_cuda(",
        "out = torch.matmul(x, out)",
        "out = awq_ext.gemm_forward_cuda(",
    ]
    if any(marker not in text for marker in required):
        raise AssertionError("exact AutoAWQ GEMM source markers missing")
    wheel_manifest = repo / "docs/vm_tlb/review_packs/C16_MULTIMODEL_NATIVE/lane_g/WHEELHOUSE_MANIFEST.tsv"
    if AUTOAWQ_WHEEL_SHA not in wheel_manifest.read_text():
        raise AssertionError("accepted wheel manifest does not bind AutoAWQ wheel")
    return {
        "autoawq_version": "0.2.7.post3",
        "wheel_sha256": AUTOAWQ_WHEEL_SHA,
        "gemm_source_path": "awq/modules/linear/gemm.py",
        "gemm_source_sha256": AUTOAWQ_GEMM_SHA,
        "metadata_sha256": AUTOAWQ_METADATA_SHA,
        "python_source": {
            "decode_M1": "awq_ext.gemm_forward_cuda(..., split_k_iters=8)",
            "prefill_M2048": "awq_ext.dequantize_weights_cuda(...) then torch.matmul",
            "threshold": "x.shape[0] * x.shape[1] >= 1024",
            "explicit_stream_argument_to_awq_ext": False,
        },
        "actual_109_extension": {
            "awq_ext_presence": "INFERRED_FROM_ACCEPTED_KERNEL_IDENTITY",
            "autoawq_kernels_distribution_version": "UNKNOWN",
            "awq_ext_binary_path": "UNKNOWN",
            "awq_ext_binary_sha256": "UNKNOWN",
            "compiled_source_commit": "UNKNOWN",
            "dequantize_kernel_current_stream_binding": "UNKNOWN",
            "gemm_kernel_current_stream_binding": "UNKNOWN_AT_BINARY_LEVEL",
            "decode_reduction_stream_binding": "UNKNOWN_AT_BINARY_LEVEL",
            "torch_matmul_stream_binding": "PYTORCH_CURRENT_STREAM_CONTEXT_SOURCE_LEVEL",
            "default_stream_or_global_workspace_assumptions": "UNKNOWN",
            "explicit_concurrent_stream_support_statement": "NOT_FOUND_IN_HASH_CLOSED_PYTHON_WHEEL; COMPILED_EXTENSION_UNBOUND",
        },
    }


def build(repo: Path, wheel: Path, out: Path) -> None:
    authority = validate_authority(repo)
    patch_path = repo / PACK_OUT / PATCH_NAME
    source_qualification = qualify_source(repo, patch_path)
    autoawq = audit_autoawq(repo, wheel)
    out.mkdir(parents=True, exist_ok=True)
    if (out / PATCH_NAME).resolve() != patch_path.resolve():
        shutil.copyfile(patch_path, out / PATCH_NAME)

    receipt = {
        "schema_version": 1,
        "status": "PREFILL_SCOPE_CONTAMINATION_CONFIRMED",
        "failed_producer_commit": FAILED_PRODUCER,
        "failed_producer_tree": FAILED_TREE,
        "qualified_contract_commit": AUTHORITY_COMMIT,
        "qualified_contract_sha256": CONTRACT_SHA,
        "evidence": {
            "B1_wrapper_installed_before_prefill": True,
            "concurrent_forward_active_decode_guard_in_V1": False,
            "first_generated_token_source": "argmax(prefill.logits[:, -1, :]) before D0",
            "expected_first_token": 23578,
            "B1_observed_first_token": 143907,
            "prefill_output_drift_proven": True,
            "V1_formal_timing_started": False,
        },
        "classification_is_not_unique_low_level_cause": True,
        "possible_but_unproven_low_level_causes": ["opaque awq_ext dequantize stream binding", "default-stream interaction", "extension global workspace", "other concurrent-prefill backend assumption"],
        "V1_preservation": {"status": "CORRECTNESS_MISMATCH_STOP", "quarantined_overlap_count": authority["failed"]["b1_overlap_count"], "scientific_use": "NONE", "rewrite_as_engineering_pass": False},
    }
    (out / "V1_SCOPE_CONTAMINATION_RECEIPT.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")

    root_cause = f"""# FFN two-stream V1 correctness root cause and V2 repair

## Confirmed failure stage

V1 installs `make_concurrent_mlp_forward` on all 28 layers before the model prefill call. Its `concurrent_forward` has no `active_decode` guard, so B1 changes prefill as well as D0-D3. The first recorded generated token is computed directly as `argmax(prefill.logits[:, -1, :])` before the decode loop. B0 produces `23578`; B1 produces `143907`. Therefore prefill output drift is already proven and the classification is `PREFILL_SCOPE_CONTAMINATION_CONFIRMED`.

This does not uniquely identify the low-level defect. The exact AutoAWQ Python wheel chooses a different prefill backend (`dequantize_weights_cuda` plus `torch.matmul`) from the M=1 decode backend (`gemm_forward_cuda`). The compiled 109 `awq_ext` binary/version/source was not recorded, so default-stream, workspace, or concurrency assumptions remain possible rather than proven causes.

## Minimal repair

V2 adds one scope guard as the first statement of the bound concurrent wrapper:

```python
if active_decode["value"] is None:
    return original_forward(hidden_state)
```

`original_forward` is the bound method saved before replacement. During prefill it bypasses all gate/up concurrency. D0-D3 set `active_decode` before invoking the model and therefore retain the complete V1 two-stream/event DAG. The resulting runner SHA256 is `{V2_RUNNER_SHA}`.

`scientific_target_change = NONE`. `execution_scope_correction = PREFILL_RESTORED_TO_ACCEPTED_BASELINE`. Model, input, D0-D3 scenario, kernels, quantization, layout, two streams, event dependencies, ABBA protocol, oracle, and held-out target are unchanged.

## V1 preservation

Commit `{FAILED_PRODUCER}` remains `CORRECTNESS_MISMATCH_STOP`. Its 10 observed overlap windows remain quarantined and have no scientific performance use. V2 is canary-first; any remaining token/hash mismatch becomes `CORRECTNESS_MISMATCH_AFTER_PREFILL_REPAIR` and stops without a second on-site repair.
"""
    (out / "ROOT_CAUSE_ANALYSIS.md").write_text(root_cause)

    stream_audit = f"""# AutoAWQ stream semantics audit

## Exact Python authority

The accepted environment binds AutoAWQ 0.2.7.post3 wheel SHA256 `{AUTOAWQ_WHEEL_SHA}`. The exact wheel's `awq/modules/linear/gemm.py` SHA256 is `{AUTOAWQ_GEMM_SHA}`. It prefers `awq_ext` when importable.

For decode M=1, the heuristic is false and Python calls `awq_ext.gemm_forward_cuda(..., 8)`. For prefill M=2048, the heuristic is true and Python calls `awq_ext.dequantize_weights_cuda(...)` followed by `torch.matmul`. Neither extension call receives an explicit CUDA stream argument at the Python interface.

## What is and is not established

`torch.matmul` is issued inside the active PyTorch stream context selected by the wrapper. However, correctness also requires the preceding dequantize output to be produced on a compatible stream with valid lifetime/workspace semantics. Decode contains the accepted GEMM plus reduction sequence, but both are behind the opaque extension call; their exact binary-level stream acquisition cannot be recovered from the Python wheel. The exact installed 109 `autoawq-kernels` distribution version, `awq_ext` path/SHA, compiled source commit, and C++ stream acquisition are absent from the accepted receipts and durable raw. They remain `UNKNOWN`; public upstream source is not substituted for the 109 binary.

The accepted M=1 trace observed some gate/up overlap, so at least part of the decode path can execute on different streams. That evidence is quarantined by correctness failure and does not establish prefill safety. No hash-closed source explicitly promises or forbids concurrent-stream use. Consequently the only confirmed root cause is accidental prefill scope expansion, not a unique `awq_ext` defect.

## Bound fields

```json
{json.dumps(autoawq, indent=2, sort_keys=True)}
```
"""
    (out / "AUTOAWQ_STREAM_SEMANTICS_AUDIT.md").write_text(stream_audit)

    qualification = {
        "schema_version": 2,
        "status": "PASS_CPU_SOURCE_QUALIFICATION_CANARY_ONLY",
        "scientific_target_change": "NONE",
        "execution_scope_correction": "PREFILL_RESTORED_TO_ACCEPTED_BASELINE",
        **source_qualification,
        "unchanged": ["model", "input", "D0-D3 scenario", "gate/up kernels", "quantization", "tensor layout", "event dependency design", "stream count", "formal ABBA protocol", "oracle", "validation target"],
        "V1_failure_preserved": True,
    }
    (out / "V2_SOURCE_QUALIFICATION.json").write_text(json.dumps(qualification, indent=2, sort_keys=True) + "\n")

    contract = {
        "schema_version": 2,
        "status": "AUTHORIZED_CANARY_FIRST",
        "scientific_target_change": "NONE",
        "execution_scope_correction": "PREFILL_RESTORED_TO_ACCEPTED_BASELINE",
        "authority": {"qualified_contract_commit": AUTHORITY_COMMIT, "qualified_contract_sha256": CONTRACT_SHA, "failed_V1_commit": FAILED_PRODUCER, "V1_status": "CORRECTNESS_MISMATCH_STOP"},
        "source": {"base_commit": FAILED_PRODUCER, "base_runner_sha256": V1_RUNNER_SHA, "patch_path": f"{PACK_OUT}/{PATCH_NAME}", "patch_sha256": PATCH_SHA, "application_tool": "GNU patch", "git_apply_forbidden": True, "exact_command": source_qualification["exact_command"], "expected_runner_sha256": V2_RUNNER_SHA},
        "B0": "accepted single-stream path unchanged",
        "B1_V2": {"prefill": "call bound original_forward; no gate/up concurrent execution", "D0_D3": "execute unchanged V1 concurrent gate/SiLU and up branches", "producer_stream_count": 2, "event_DAG": "unchanged from V1"},
        "stage_1_canary_only": {
            "runs": ["1 x B0 lightweight NSYS cuda,nvtx", "1 x B1_V2 lightweight NSYS cuda,nvtx"],
            "checks": {"B0_tokens": [23578, 11, 323, 3950], "B1_tokens": [23578, 11, 323, 3950], "call_order_count_each": 420, "projection_occurrences_each": 336, "projection_hash_shape_identity": True, "kernel_identity": True, "B1_real_overlap_required": True},
            "formal_timing_before_pass": False,
        },
        "automatic_stage_2_only_if_all_canary_checks_pass": {
            "protocol": "original frozen 12 complete ABBA blocks B0,B1,B1,B0",
            "samples": {"B0": 24, "B1": 24, "total": 48},
            "bootstrap": {"unit": "complete ABBA block", "resamples": 1000, "seed": 20261001},
            "oracle": "unchanged 7.732849 ms / 7.893066891889022% gap-preserving no-contention reference",
            "validation_target": "unchanged D3 whole-step plus layers 14-27 overlap/duration response",
        },
        "failure_after_repair": {"classification": "CORRECTNESS_MISMATCH_AFTER_PREFILL_REPAIR", "action": "STOP", "second_live_repair_allowed": False},
        "forbidden_changes": ["model/input", "prefill backend on B0/B1", "D0-D3 kernels", "quantization", "tensor layout", "stream count", "event DAG", "ABBA protocol", "oracle", "validation target", "NCU", "NVBit", "SASS", "Accel-Sim"],
        "gpu_lock": {"required_on_109": True, "path": "/data/c16/locks/c16_gpu_campaign.lock", "release_receipt_required": True},
    }
    (out / "LANE7_FFN_GATE_UP_CONCURRENCY_NATIVE_CONTRACT_V2.json").write_text(json.dumps(contract, indent=2, sort_keys=True) + "\n")

    final = {
        "schema_version": 2,
        "status": "V2_SOURCE_QUALIFIED_CANARY_ONLY",
        "root_cause_classification": "PREFILL_SCOPE_CONTAMINATION_CONFIRMED",
        "unique_low_level_cause": "NOT_PROVEN",
        "autoawq_binary_stream_semantics": "PARTIALLY_UNKNOWN",
        "scientific_target_change": "NONE",
        "execution_scope_correction": "PREFILL_RESTORED_TO_ACCEPTED_BASELINE",
        "V1_failure_preserved": "CORRECTNESS_MISMATCH_STOP",
        "V1_quarantined_overlap_preserved": True,
        "V2_contract_emitted": True,
        "gpu_used": False,
        "cuda_initialized": False,
        "gpu_lock_used": False,
    }
    (out / "FINAL_DECISION.json").write_text(json.dumps(final, indent=2, sort_keys=True) + "\n")

    anchors = {
        "schema_version": 1,
        "failed_producer": {"commit": FAILED_PRODUCER, "tree": FAILED_TREE, "runner_sha256": V1_RUNNER_SHA, "manifest_sha256": authority["manifest_sha256"], "manifest_file_count": authority["manifest_count"]},
        "qualified_contract": {"commit": AUTHORITY_COMMIT, "sha256": CONTRACT_SHA},
        "autoawq": autoawq,
        "durable_raw": "/root/share/mnt164/huangrulin/c16_ai_workload/provenance/c16_ffn_gate_up_concurrency_native_v1/C16R_ffn-gate-up-concurrency-native-v1_20261001T014701Z",
    }
    (out / "SOURCE_ANCHORS.json").write_text(json.dumps(anchors, indent=2, sort_keys=True) + "\n")

    names = sorted(path.name for path in out.iterdir() if path.is_file() and path.name != "SHA256SUMS")
    (out / "SHA256SUMS").write_text("".join(f"{sha256((out / name).read_bytes())}  {name}\n" for name in names))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wheel", type=Path, default=WHEEL_DEFAULT)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[3]
    if args.check:
        validate_authority(repo)
        qualify_source(repo, repo / PACK_OUT / PATCH_NAME)
        audit_autoawq(repo, args.wheel)
        return
    build(repo, args.wheel, args.output_dir or repo / PACK_OUT)


if __name__ == "__main__":
    main()
