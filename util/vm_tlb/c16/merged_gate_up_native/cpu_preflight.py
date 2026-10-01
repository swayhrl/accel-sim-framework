#!/usr/bin/env python3
"""CPU-only identity, quantization, loader-mapping, and environment preflight."""

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
from contextlib import ExitStack
from pathlib import Path

import torch
from safetensors import safe_open


AUTH_COMMIT = "3c3f667bbab8f3ae227dc3bc8eaa6c642b97a453"
AUTH_TREE = "e4be7386c697b33e4f429b833216fdb0bd65f17d"
CONTRACT_SHA = "b843c11381b0451e958087aa825869da00f9624ebd8389673d02fa33a0a298c3"
VLLM_COMMIT = "df8fd42116f172b7a53bc10c8a680b05232edbed"
REVISION = "b25037543e9394b818fdfca67ab2a00ecc7dd641"
CONFIG_SHA = "ec0c1f5f875ad8bc1f78c5140c22dbdde1b55478442ad358e7a4d9ecf947a327"
CONTRACT_PATH = "docs/vm_tlb/review_packs/C16_MERGED_GATE_UP_STRONG_BASELINE_GUARD_174NEW_V1/LANE7_MERGED_GATE_UP_NATIVE_BASELINE_CONTRACT.json"
SOURCE_EXPECTED = {
    "vllm/model_executor/models/qwen2.py": "6684104ba6dc40325bb1f6e632ec90633fa83a7b95883bb2181e9dc0008c3e21",
    "vllm/model_executor/layers/linear.py": "7a9b90937865fa35d955ffc2017f23d3997bc4fba954e2667870b1b4854a38e0",
    "vllm/model_executor/layers/activation.py": "bebeddbd4997f49f54471ee31ac42b22c3c11dfe25244e55d20c36f390489c05",
    "vllm/model_executor/parameter.py": "1a4bbd7400fd1ba79e8e1e8d19666cd22881ec83c35e6e01b3fdc78faee23171",
    "vllm/model_executor/layers/quantization/auto_awq.py": "9ed2fd3d33b510e152a8826aab239e46c2a9c0d6cf718ba32a2d54e3d60e29fa",
    "vllm/model_executor/layers/quantization/utils/marlin_utils.py": "e60713c15080347b01425f90eaf03840ca80a1cd226ec57e526e8f6286eeeb22",
    "vllm/model_executor/layers/quantization/base_config.py": "17c17fcf0d20458a969213d6a2c04dbe6491b49ab41c38f1a2dc5d4b61c947f1",
}


def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha_file(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha_tensor(tensor):
    return sha_bytes(tensor.detach().contiguous().view(torch.uint8).numpy().tobytes())


def canonical_unpack_sha(tensor, reverse_awq=True, rows=32):
    h = hashlib.sha256()
    shifts = torch.arange(0, 32, 4, dtype=torch.int32)
    order = torch.tensor([0, 4, 1, 5, 2, 6, 3, 7], dtype=torch.long)
    for start in range(0, tensor.shape[0], rows):
        block = tensor[start:start + rows]
        unpacked = (block.unsqueeze(-1) >> shifts) & 15
        if reverse_awq:
            unpacked = unpacked[:, :, order]
        unpacked = unpacked.reshape(block.shape[0], -1).to(torch.uint8).contiguous()
        h.update(unpacked.numpy().tobytes())
    return h.hexdigest()


def git(repo, *args, binary=False):
    result = subprocess.check_output(["git", "-C", str(repo), *args])
    return result if binary else result.decode().strip()


def merged_loader(output_sizes, shape, dtype, packed):
    from vllm.model_executor.layers.linear import MergedColumnParallelLinear

    obj = object.__new__(MergedColumnParallelLinear)
    obj.output_sizes = output_sizes
    obj.tp_size = 1
    obj.tp_rank = 0
    param = torch.nn.Parameter(torch.empty(shape, dtype=dtype), requires_grad=False)
    param.output_dim = 1
    if packed:
        param.packed_dim = 1
        param.packed_factor = 8
    param.is_sharded_weight = False
    return obj, param


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--main-repo", type=Path, required=True)
    parser.add_argument("--vllm-source", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "":
        raise RuntimeError("CPU preflight requires CUDA_VISIBLE_DEVICES empty")
    if torch.cuda.is_initialized() or torch.cuda.is_available():
        raise RuntimeError("CUDA became visible or initialized during CPU preflight")

    authority_ref = "refs/remotes/origin/hrl/c16-merged-gate-up-strong-baseline-guard-174new-v1"
    contract_bytes = git(args.main_repo, "show", f"{AUTH_COMMIT}:{CONTRACT_PATH}", binary=True)
    contract = json.loads(contract_bytes)
    config_path = args.checkpoint / "config.json"
    index_path = args.checkpoint / "model.safetensors.index.json"
    config = json.loads(config_path.read_text())
    index = json.loads(index_path.read_text())["weight_map"]
    source_hashes = {path: sha_file(args.vllm_source / path) for path in SOURCE_EXPECTED}
    checks = {
        "authority_commit": git(args.main_repo, "rev-parse", authority_ref) == AUTH_COMMIT,
        "authority_tree": git(args.main_repo, "rev-parse", authority_ref + "^{tree}") == AUTH_TREE,
        "contract_sha": sha_bytes(contract_bytes) == CONTRACT_SHA,
        "contract_status": contract["status"] == "QUALIFIED_STRONG_BASELINE_NOT_STRICT_SINGLE_VARIABLE_AB",
        "vllm_commit": git(args.vllm_source, "rev-parse", "HEAD") == VLLM_COMMIT,
        "vllm_source_clean": git(args.vllm_source, "status", "--porcelain") == "",
        "source_anchor_hashes": source_hashes == SOURCE_EXPECTED,
        "checkpoint_revision_directory": args.checkpoint.name == REVISION,
        "checkpoint_config_sha": sha_file(config_path) == CONFIG_SHA,
        "checkpoint_architecture": config["architectures"] == ["Qwen2ForCausalLM"],
        "checkpoint_dimensions": (config["hidden_size"], config["intermediate_size"], config["num_hidden_layers"]) == (3584, 18944, 28),
        "checkpoint_dtype": config["torch_dtype"] == "float16",
        "quantization_exact": config["quantization_config"] == {"bits": 4, "group_size": 128, "modules_to_not_convert": None, "quant_method": "awq", "version": "gemm", "zero_point": True},
        "cuda_not_visible_or_initialized": not torch.cuda.is_available() and not torch.cuda.is_initialized(),
    }
    if not all(checks.values()):
        raise RuntimeError(f"identity preflight failed: {checks}")

    shard_paths = sorted({args.checkpoint / value for value in index.values()})
    rows = []
    with ExitStack() as stack:
        handles = {path.name: stack.enter_context(safe_open(path, framework="pt", device="cpu")) for path in shard_paths}
        for layer in range(28):
            tensors = {}
            for role in ("gate_proj", "up_proj"):
                for kind in ("qweight", "qzeros", "scales"):
                    name = f"model.layers.{layer}.mlp.{role}.{kind}"
                    tensors[(role, kind)] = handles[index[name]].get_tensor(name)
            expected_shapes = {
                "qweight": (3584, 2368), "qzeros": (28, 2368), "scales": (28, 18944)
            }
            for role in ("gate_proj", "up_proj"):
                for kind, shape in expected_shapes.items():
                    if tuple(tensors[(role, kind)].shape) != shape:
                        raise RuntimeError(f"shape mismatch L{layer} {role} {kind}")

            qw_loader, qw = merged_loader([18944, 18944], (3584, 4736), torch.int32, True)
            qz_loader, qz = merged_loader([18944, 18944], (28, 4736), torch.int32, True)
            sc_loader, scales = merged_loader([18944, 18944], (28, 37888), torch.float16, False)
            for shard, role in enumerate(("gate_proj", "up_proj")):
                qw_loader.weight_loader(qw, tensors[(role, "qweight")], shard)
                qz_loader.weight_loader(qz, tensors[(role, "qzeros")], shard)
                sc_loader.weight_loader(scales, tensors[(role, "scales")], shard)
            gate_qw, up_qw = qw[:, :2368], qw[:, 2368:]
            gate_qz, up_qz = qz[:, :2368], qz[:, 2368:]
            gate_sc, up_sc = scales[:, :18944], scales[:, 18944:]
            exact = {
                "gate_qweight_raw": torch.equal(gate_qw, tensors[("gate_proj", "qweight")]),
                "up_qweight_raw": torch.equal(up_qw, tensors[("up_proj", "qweight")]),
                "gate_qzeros_raw": torch.equal(gate_qz, tensors[("gate_proj", "qzeros")]),
                "up_qzeros_raw": torch.equal(up_qz, tensors[("up_proj", "qzeros")]),
                "gate_scales_bytes": torch.equal(gate_sc, tensors[("gate_proj", "scales")]),
                "up_scales_bytes": torch.equal(up_sc, tensors[("up_proj", "scales")]),
            }
            before = {
                "gate_qweight": canonical_unpack_sha(tensors[("gate_proj", "qweight")]),
                "up_qweight": canonical_unpack_sha(tensors[("up_proj", "qweight")]),
                "gate_qzeros": canonical_unpack_sha(tensors[("gate_proj", "qzeros")]),
                "up_qzeros": canonical_unpack_sha(tensors[("up_proj", "qzeros")]),
            }
            after = {
                "gate_qweight": canonical_unpack_sha(gate_qw),
                "up_qweight": canonical_unpack_sha(up_qw),
                "gate_qzeros": canonical_unpack_sha(gate_qz),
                "up_qzeros": canonical_unpack_sha(up_qz),
            }
            canonical_equal = before == after
            if not all(exact.values()) or not canonical_equal:
                raise RuntimeError(f"merged loader mismatch layer {layer}: {exact} canonical={canonical_equal}")
            rows.append({
                "layer": layer, "status": "PASS", "exact": exact,
                "canonical_before": before, "canonical_after": after,
                "merged_raw_sha256": {"qweight": sha_tensor(qw), "qzeros": sha_tensor(qz), "scales": sha_tensor(scales)},
                "source_raw_sha256": {
                    f"{role}.{kind}": sha_tensor(tensors[(role, kind)])
                    for role in ("gate_proj", "up_proj") for kind in ("qweight", "qzeros", "scales")
                },
                "merged_shapes": {"qweight": list(qw.shape), "qzeros": list(qz.shape), "scales": list(scales.shape)},
                "logical_quant_bytes": sum(t.numel() * t.element_size() for t in tensors.values()),
            })

    quant = {
        "status": "PASS", "layers": rows,
        "all_28_layers_exact": len(rows) == 28 and all(row["status"] == "PASS" for row in rows),
        "loader": "actual MergedColumnParallelLinear.weight_loader on CPU parameters",
        "canonical_unpack": "AWQ 4-bit reverse order [0,4,1,5,2,6,3,7]",
        "no_requantization": True, "physical_runtime_repack_allowed": True,
        "logical_total_bytes_per_layer_gate_plus_up": 70547456,
        "padding_required_for_tp1": False,
    }
    (args.output_dir / "CANONICAL_QUANT_IDENTITY.json").write_text(json.dumps(quant, indent=2, sort_keys=True) + "\n")
    shard_identity = [{"path": str(path), "bytes": path.stat().st_size, "sha256": sha_file(path)} for path in shard_paths]
    extensions = sorted((args.vllm_source / "vllm").glob("*.so"))
    environment = {
        "status": "PASS", "python": sys.version, "platform": platform.platform(),
        "python_executable": sys.executable, "torch_version": torch.__version__,
        "torch_cuda_version": torch.version.cuda, "vllm_source": str(args.vllm_source),
        "vllm_commit": git(args.vllm_source, "rev-parse", "HEAD"),
        "vllm_tree": git(args.vllm_source, "rev-parse", "HEAD^{tree}"),
        "source_hashes": source_hashes,
        "precompiled_extensions": [{"path": str(path), "bytes": path.stat().st_size, "sha256": sha_file(path)} for path in extensions],
        "install_class": "editable exact source + exact-commit cu130 precompiled extensions",
        "accepted_autoawq_environment_modified": False,
        "checkpoint_files": shard_identity,
        "checkpoint_index_sha256": sha_file(index_path),
    }
    (args.output_dir / "ENVIRONMENT_RECEIPT.json").write_text(json.dumps(environment, indent=2, sort_keys=True) + "\n")
    result = {
        "status": "PASS" if all(checks.values()) and quant["all_28_layers_exact"] else "STOP",
        "checks": checks, "authority_commit": AUTH_COMMIT, "authority_tree": AUTH_TREE,
        "contract_sha256": sha_bytes(contract_bytes), "vllm_commit": VLLM_COMMIT,
        "checkpoint_revision": REVISION, "checkpoint_config_sha256": sha_file(config_path),
        "all_28_layer_loader_and_canonical_identity": quant["all_28_layers_exact"],
        "no_requantization": True, "rtx4080_static_backend_support": {
            "compute_capability": "8.9", "minimum": "7.5", "group_size": 128,
            "source_supported": True, "runtime_canary_still_required": True,
        },
        "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
        "cuda_initialized": torch.cuda.is_initialized(),
    }
    (args.output_dir / "CPU_PREFLIGHT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))
    if result["status"] != "PASS":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
