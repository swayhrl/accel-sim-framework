#!/usr/bin/env python3
"""CPU-only source guard for merged gate/up strong software baselines."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
from pathlib import Path


C16_AUTHORITY = "30b3016a7ad5b5ef86a3494c784e072938dee6c5"
VLLM_COMMIT = "df8fd42116f172b7a53bc10c8a680b05232edbed"
VLLM_COMMIT_DATE = "2026-10-01T01:06:24+00:00"
VLLM_DEFAULT = Path("/root/workspace/vllm-c16-merged-guard-source")
PACK = "docs/vm_tlb/review_packs/C16_MERGED_GATE_UP_STRONG_BASELINE_GUARD_174NEW_V1"
MODEL_ID = "Qwen/Qwen2.5-7B-Instruct-AWQ"
MODEL_REVISION = "b25037543e9394b818fdfca67ab2a00ecc7dd641"
MODEL_CONFIG_SHA = "ec0c1f5f875ad8bc1f78c5140c22dbdde1b55478442ad358e7a4d9ecf947a327"
FILES = {
    "vllm/model_executor/models/qwen2.py": ("6684104ba6dc40325bb1f6e632ec90633fa83a7b95883bb2181e9dc0008c3e21", "88600b3767c2199f1cb94c9a2007201fa337b0bf"),
    "vllm/model_executor/layers/linear.py": ("7a9b90937865fa35d955ffc2017f23d3997bc4fba954e2667870b1b4854a38e0", "65cda325a22188c83746121d54567f4f94a229a1"),
    "vllm/model_executor/layers/activation.py": ("bebeddbd4997f49f54471ee31ac42b22c3c11dfe25244e55d20c36f390489c05", "808d6e711277b4c7e975bec18db8eaf492008f94"),
    "vllm/model_executor/parameter.py": ("1a4bbd7400fd1ba79e8e1e8d19666cd22881ec83c35e6e01b3fdc78faee23171", "de1cc7d218884e4b37eedaa81f83f58e6b6f9ac9"),
    "vllm/model_executor/layers/quantization/auto_awq.py": ("9ed2fd3d33b510e152a8826aab239e46c2a9c0d6cf718ba32a2d54e3d60e29fa", "0c3e9805517a5f0b7cab3a15883b1482f6ff921f"),
    "vllm/model_executor/layers/quantization/utils/marlin_utils.py": ("e60713c15080347b01425f90eaf03840ca80a1cd226ec57e526e8f6286eeeb22", "1ee52a17802b2148a88be819ad0137755560e6a2"),
    "vllm/model_executor/layers/quantization/base_config.py": ("17c17fcf0d20458a969213d6a2c04dbe6491b49ab41c38f1a2dc5d4b61c947f1", "1b0457854eb173cfc964285b6848264817c029cf"),
    "docs/contributing/model/basic.md": ("71e1aaf7cab6243376c5a051523dfcb39590b73386eb9415e4b6e09fb5bbd3dd", "1db0981cf1890f4ce3ae76b49584647177ad498e"),
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def line_of(text: str, needle: str) -> int:
    for index, line in enumerate(text.splitlines(), 1):
        if needle in line:
            return index
    raise AssertionError(f"source anchor not found: {needle}")


def write_tsv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "NA") or "NA" for field in fields})


def validate(repo: Path, vllm: Path) -> dict:
    subprocess.run(["git", "merge-base", "--is-ancestor", C16_AUTHORITY, "HEAD"], cwd=repo, check=True)
    vllm_head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=vllm, text=True).strip()
    if vllm_head != VLLM_COMMIT:
        raise AssertionError(f"vLLM source commit drift: {vllm_head}")
    if subprocess.check_output(["git", "status", "--porcelain=v1"], cwd=vllm, text=True).strip():
        raise AssertionError("vLLM source worktree is dirty")
    texts = {}
    anchors = []
    for path, (expected_sha, expected_blob) in FILES.items():
        data = (vllm / path).read_bytes()
        actual_sha = sha256(data)
        actual_blob = subprocess.check_output(["git", "rev-parse", f"HEAD:{path}"], cwd=vllm, text=True).strip()
        if (actual_sha, actual_blob) != (expected_sha, expected_blob):
            raise AssertionError(f"source identity mismatch: {path}")
        texts[path] = data.decode("utf-8")
        anchors.append({
            "repository": "https://github.com/vllm-project/vllm",
            "commit": VLLM_COMMIT,
            "path": path,
            "sha256": actual_sha,
            "git_blob": actual_blob,
            "url": f"https://github.com/vllm-project/vllm/blob/{VLLM_COMMIT}/{path}",
        })

    qwen = texts["vllm/model_executor/models/qwen2.py"]
    linear = texts["vllm/model_executor/layers/linear.py"]
    activation = texts["vllm/model_executor/layers/activation.py"]
    awq = texts["vllm/model_executor/layers/quantization/auto_awq.py"]
    marlin = texts["vllm/model_executor/layers/quantization/utils/marlin_utils.py"]
    base_config = texts["vllm/model_executor/layers/quantization/base_config.py"]
    required = [
        (qwen, "self.gate_up_proj = MergedColumnParallelLinear("),
        (qwen, "[intermediate_size] * 2,"),
        (qwen, "self.act_fn = SiluAndMul()"),
        (qwen, '".gate_proj": (".gate_up_proj", 0)'),
        (qwen, '".up_proj": (".gate_up_proj", 1)'),
        (qwen, '"gate_up_proj": ["gate_proj", "up_proj"]'),
        (linear, "class MergedColumnParallelLinear(ColumnParallelLinear):"),
        (linear, "output_size=sum(output_sizes),"),
        (linear, "shard_size = round(shard_size // param.packed_factor)"),
        (activation, "class SiluAndMul(CustomOp):"),
        (activation, "return F.silu(x[..., :d]) * x[..., d:]"),
        (awq, "class AutoAWQConfig(QuantizationConfig):"),
        (awq, "self.group_size = group_size"),
        (awq, "self.zero_point = zero_point"),
        (awq, "output_size_per_partition = sum(output_partition_sizes)"),
        (awq, "packed_dim=1,"),
        (awq, "_convert_awq_to_standard_format("),
        (marlin, "MARLIN_SUPPORTED_GROUP_SIZES = [-1, 32, 64, 128]"),
        (marlin, "if device_capability < 75:"),
        (base_config, "self.packed_modules_mapping: dict[str, list[str]] = dict()"),
    ]
    for text, marker in required:
        line_of(text, marker)

    decision = json.loads((repo / "docs/vm_tlb/review_packs/C16_FFN_TIMELINE_HEADROOM_QUALIFICATION_174NEW_V2/FINAL_DECISION.json").read_text())
    if decision["F2A"] != "F2A_QUALIFIED_FOR_NATIVE_CONCURRENCY_DIAGNOSTIC":
        raise AssertionError("C16 headroom authority mismatch")
    deployment = json.loads((repo / "docs/vm_tlb/review_packs/C15_LOWCOST_MULTIMODEL/lane_a/DEPLOYMENT_MANIFEST.json").read_text())
    matched = [row for row in deployment["deployments"] if row["model_id"] == MODEL_ID]
    if len(matched) != 1 or matched[0]["revision"] != MODEL_REVISION or matched[0]["config_sha256"] != MODEL_CONFIG_SHA:
        raise AssertionError("accepted model/config identity mismatch")
    model_registry = (repo / "docs/vm_tlb/review_packs/C15_LOWCOST_MULTIMODEL/lane_a/MODEL_REGISTRY.tsv").read_text()
    if not any(MODEL_ID in line and "\tawq\t128\t" in line for line in model_registry.splitlines()):
        raise AssertionError("accepted AWQ group-size authority missing")

    semantic_anchors = [
        {"id": "QWEN2_MERGED_MLP", "path": "vllm/model_executor/models/qwen2.py", "line": line_of(qwen, "class Qwen2MLP"), "claim": "MergedColumnParallelLinear gate_up_proj followed by SiluAndMul and down_proj"},
        {"id": "QWEN2_SHARD_MAPPER", "path": "vllm/model_executor/models/qwen2.py", "line": line_of(qwen, '".gate_proj": (".gate_up_proj", 0)'), "claim": "separate checkpoint gate/up tensors map to logical merged shards 0/1"},
        {"id": "QWEN2_PACKED_MAPPING", "path": "vllm/model_executor/models/qwen2.py", "line": line_of(qwen, "packed_modules_mapping ="), "claim": "gate_up_proj advertises gate_proj/up_proj packed mapping"},
        {"id": "MERGED_LINEAR_LOADER", "path": "vllm/model_executor/layers/linear.py", "line": line_of(linear, "class MergedColumnParallelLinear"), "claim": "logical output sizes are concatenated and loaded shard-wise with packed offsets"},
        {"id": "AUTOAWQ_CONFIG", "path": "vllm/model_executor/layers/quantization/auto_awq.py", "line": line_of(awq, "class AutoAWQConfig"), "claim": "bits/group size/zero point are read from checkpoint quantization config"},
        {"id": "AUTOAWQ_MERGED_STORAGE", "path": "vllm/model_executor/layers/quantization/auto_awq.py", "line": line_of(awq, "class AutoAWQMarlinLinearMethod"), "claim": "merged qweight/qzeros/scales allocate over sum(output_partition_sizes)"},
        {"id": "AUTOAWQ_LOSSLESS_REPACK", "path": "vllm/model_executor/layers/quantization/auto_awq.py", "line": line_of(awq, "def _convert_awq_to_standard_format"), "claim": "AWQ packing is losslessly unpacked/repacked for MP/Marlin kernels, not requantized"},
        {"id": "SILU_AND_MUL", "path": "vllm/model_executor/layers/activation.py", "line": line_of(activation, "class SiluAndMul"), "claim": "one fused activation-and-multiply operator consumes the two logical output halves"},
        {"id": "MARLIN_PLATFORM", "path": "vllm/model_executor/layers/quantization/utils/marlin_utils.py", "line": line_of(marlin, "if device_capability < 75"), "claim": "CC >= 7.5 and group size 128 are source-supported"},
    ]
    return {"texts": texts, "files": anchors, "semantic_anchors": semantic_anchors}


def build(repo: Path, vllm: Path, out: Path) -> None:
    source = validate(repo, vllm)
    k = 3584
    n = 18944
    groups = k // 128
    qweight_one = k * n // 2
    qzeros_one = groups * n // 2
    scales_one = groups * n * 2
    total_two = 2 * (qweight_one + qzeros_one + scales_one)
    if (qweight_one, qzeros_one, scales_one, total_two) != (33_947_648, 265_216, 1_060_864, 70_547_456):
        raise AssertionError("quantized byte accounting drift")
    hidden_bytes = 3584 * 2
    d_bytes = 18944 * 2
    current_intermediate_writes = 4 * d_bytes
    merged_intermediate_writes = 2 * d_bytes + d_bytes
    current_handoff_traffic = 8 * d_bytes
    merged_handoff_traffic = 6 * d_bytes

    out.mkdir(parents=True, exist_ok=True)
    anchors = {
        "schema_version": 1,
        "status": "PASS",
        "as_of_date": "2026-10-01",
        "c16_authority_commit": C16_AUTHORITY,
        "vllm": {"repository": "https://github.com/vllm-project/vllm", "commit": VLLM_COMMIT, "commit_date": VLLM_COMMIT_DATE, "files": source["files"], "semantic_anchors": source["semantic_anchors"]},
        "checkpoint": {
            "model_id": MODEL_ID,
            "revision": MODEL_REVISION,
            "config_sha256": MODEL_CONFIG_SHA,
            "url": f"https://huggingface.co/{MODEL_ID}/blob/{MODEL_REVISION}/config.json",
            "quantization_config": {"quant_method": "awq", "bits": 4, "group_size": 128, "zero_point": True, "version": "gemm"},
            "dimensions": {"hidden_size": 3584, "intermediate_size": 18944, "layers": 28, "dtype": "float16"},
        },
        "scope_boundary": "Pinned current vLLM source and exact accepted checkpoint metadata; no GPU/runtime execution and no performance claim.",
    }
    (out / "SOURCE_ANCHORS.json").write_text(json.dumps(anchors, indent=2, sort_keys=True) + "\n")

    matrix = [
        {"capability": "scientific_semantics", "CURRENT_AUTOAWQ": "silu(gate(x))*up(x)->down", "TWO_STREAM_GATE_UP": "same DAG; explicit branch dependencies", "MERGED_GATE_UP_STRONG_BASELINE": "same DAG via merged [gate,up] output then SiluAndMul", "evidence_boundary": "source-closed"},
        {"capability": "quantization_semantics", "CURRENT_AUTOAWQ": "AWQ W4 group128 zero-point; separate qweight/qzeros/scales", "TWO_STREAM_GATE_UP": "identical tensors and quantization", "MERGED_GATE_UP_STRONG_BASELINE": "same logical 4-bit values/zero-points/scales loaded into two output shards; no requantization", "evidence_boundary": "logical quant semantics exact; Marlin may losslessly repack bytes"},
        {"capability": "kernel_count", "CURRENT_AUTOAWQ": "observed gate+up: 2 GEMM + 2 reduce; SiLU + Mul = 6 kernels", "TWO_STREAM_GATE_UP": "same six kernels; scheduling changes only", "MERGED_GATE_UP_STRONG_BASELINE": "one quantized-linear invocation + one SiluAndMul invocation; exact GPU kernel/reduce count backend-resolved", "evidence_boundary": "do not guess native kernel count before capture"},
        {"capability": "weight_bytes", "CURRENT_AUTOAWQ": f"gate+up logical quant bytes={total_two}", "TWO_STREAM_GATE_UP": f"same {total_two}", "MERGED_GATE_UP_STRONG_BASELINE": f"same logical {total_two}; shapes aligned so no Marlin tile padding required", "evidence_boundary": "metadata/workspace excluded"},
        {"capability": "input_reads", "CURRENT_AUTOAWQ": f"two logical hidden reads={2*hidden_bytes} B", "TWO_STREAM_GATE_UP": f"same {2*hidden_bytes} B, concurrent", "MERGED_GATE_UP_STRONG_BASELINE": f"one logical hidden input={hidden_bytes} B", "evidence_boundary": "logical interface reads, not measured DRAM transactions"},
        {"capability": "output_intermediate_bytes", "CURRENT_AUTOAWQ": f"writes={current_intermediate_writes} B; handoff write+read={current_handoff_traffic} B", "TWO_STREAM_GATE_UP": f"same writes={current_intermediate_writes} B and handoff={current_handoff_traffic} B", "MERGED_GATE_UP_STRONG_BASELINE": f"merged gate_up + fused product writes={merged_intermediate_writes} B; handoff={merged_handoff_traffic} B", "evidence_boundary": "logical FP16 bytes per layer/decode"},
        {"capability": "launch_count", "CURRENT_AUTOAWQ": "two linear calls + separate SiLU and Mul calls", "TWO_STREAM_GATE_UP": "same calls on two streams", "MERGED_GATE_UP_STRONG_BASELINE": "one linear call + one fused SiluAndMul call", "evidence_boundary": "CUDA launch count depends on selected backend"},
        {"capability": "parallelism", "CURRENT_AUTOAWQ": "gate->SiLU->up->Mul serialized on one stream", "TWO_STREAM_GATE_UP": "gate/SiLU branch overlaps up branch", "MERGED_GATE_UP_STRONG_BASELINE": "gate/up output-channel work co-scheduled inside one merged linear", "evidence_boundary": "no performance ranking inferred"},
        {"capability": "layout", "CURRENT_AUTOAWQ": "two AWQ output-packed modules", "TWO_STREAM_GATE_UP": "unchanged", "MERGED_GATE_UP_STRONG_BASELINE": "concatenate logical output N; direct AWQ slices or lossless GPTQ-like/MP repack", "evidence_boundary": "Marlin physical layout differs from C16"},
        {"capability": "numerical_equivalence", "CURRENT_AUTOAWQ": "accepted hash-closed reference", "TWO_STREAM_GATE_UP": "bitwise projection identity required", "MERGED_GATE_UP_STRONG_BASELINE": "same quantized weights and mathematical DAG; FP bitwise output not assumed across backend/reduction", "evidence_boundary": "native tolerance/token validation required"},
        {"capability": "platform_feasibility", "CURRENT_AUTOAWQ": "accepted RTX4080 CC8.9", "TWO_STREAM_GATE_UP": "source-feasible; diagnostic contracted", "MERGED_GATE_UP_STRONG_BASELINE": "source-qualified: AutoAWQ min CC7.5, uint4+zero-point+group128 supported, K/N aligned", "evidence_boundary": "isolated vLLM runtime still requires 109 canary"},
        {"capability": "W4_kernel", "CURRENT_AUTOAWQ": "AutoAWQ 0.2.7.post3 WQLinear_GEMM", "TWO_STREAM_GATE_UP": "unchanged WQLinear_GEMM", "MERGED_GATE_UP_STRONG_BASELINE": "vLLM AutoAWQLinear or AutoAWQMarlin MP kernel selected at runtime", "evidence_boundary": "not a same-kernel single-variable A/B"},
        {"capability": "reduction_path", "CURRENT_AUTOAWQ": "two observed GEMM+reduce pairs", "TWO_STREAM_GATE_UP": "same two pairs", "MERGED_GATE_UP_STRONG_BASELINE": "backend-specific merged reduction path", "evidence_boundary": "must record chosen backend and native kernel sequence"},
        {"capability": "Silu_Mul_fusion", "CURRENT_AUTOAWQ": "two distinct elementwise kernels", "TWO_STREAM_GATE_UP": "unchanged", "MERGED_GATE_UP_STRONG_BASELINE": "SiluAndMul fused custom op", "evidence_boundary": "mature vLLM source capability"},
    ]
    write_tsv(out / "MERGED_GATE_UP_CAPABILITY_MATRIX.tsv", matrix, ["capability", "CURRENT_AUTOAWQ", "TWO_STREAM_GATE_UP", "MERGED_GATE_UP_STRONG_BASELINE", "evidence_boundary"])

    audit = {
        "schema_version": 1,
        "status": "SEMANTICALLY_MATCHED_MERGED_BASELINE_EXISTS",
        "checkpoint": {"model_id": MODEL_ID, "revision": MODEL_REVISION, "bits": 4, "group_size": 128, "zero_point": True, "activation_dtype": "FP16"},
        "separate_projection": {
            "per_projection": {"qweight_packed_shape": [3584, 2368], "qweight_bytes": qweight_one, "qzeros_packed_shape": [28, 2368], "qzeros_bytes": qzeros_one, "scales_shape": [28, 18944], "scales_bytes": scales_one},
            "gate_plus_up_total_bytes": total_two,
        },
        "merged_projection": {
            "logical_output_features": 37888,
            "merge_axis": "logical output/N dimension; AWQ KxN packed tensors concatenate along packed output dimension 1",
            "qweight_packed_shape": [3584, 4736],
            "qzeros_packed_shape": [28, 4736],
            "scales_shape": [28, 37888],
            "total_logical_quant_bytes": total_two,
            "requires_requantization": False,
            "direct_loader": "gate_proj -> merged shard 0; up_proj -> merged shard 1; packed offsets divided by pack_factor",
            "group_size_preserved": True,
            "zero_point_preserved": True,
            "scale_bytes_preserved": True,
        },
        "marlin_or_mp_conversion": {
            "physical_packing_changes": True,
            "logical_quantized_values_change": False,
            "requantization": False,
            "description": "unpack/reorder/repack AWQ integers and zero-points into the selected MP kernel layout; scales are carried with the same groups",
            "shape_padding_required_for_tp1": False,
            "runtime_selected_kernel": "UNKNOWN_UNTIL_109_PREFLIGHT",
        },
        "floating_point_output": {"mathematical_equivalence": True, "bitwise_equivalence_across_backend": "NOT_ASSUMED", "reason": "merged and MP/Marlin kernels may use a different FP reduction schedule"},
        "strict_ab_classification": "SAME_CHECKPOINT_AND_QUANTIZATION_SEMANTICS_BUT_CROSS_RUNTIME_BACKEND; NOT_MERGE_ONLY",
    }
    (out / "QUANTIZATION_SEMANTICS_AUDIT.json").write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n")

    report = f"""# Merged gate/up strong-baseline guard

## Position

Pinned vLLM `{VLLM_COMMIT}` implements Qwen2 MLP as `MergedColumnParallelLinear(hidden, [intermediate, intermediate])`, followed by `SiluAndMul` and `down_proj`. Its mapper loads the checkpoint's separate `gate_proj` and `up_proj` tensors into logical merged shards 0 and 1. This is a mature standard software capability, not a speculative C16 mechanism.

The exact accepted Qwen2.5 AWQ checkpoint is compatible without re-quantization. For each original projection, qweight/qzeros/scales occupy `{qweight_one}`, `{qzeros_one}`, and `{scales_one}` bytes. Concatenating along logical output N gives the same `{total_two}` total quantized bytes. `group_size=128`, zero-point and scale semantics remain unchanged. A selected MP/Marlin backend may losslessly repack the physical bytes; that is not requantization, but it does make the comparison cross-backend.

## What the merged path changes

It structurally replaces two quantized-linear calls with one, presents hidden once at the operator interface, doubles logical N from 18944 to 37888, and replaces separate SiLU and multiply with `SiluAndMul`. Therefore it can also change W4 tiling and reduction. Exact CUDA kernel count, input memory transactions, and performance are deliberately left to native validation.

Two-stream B1 changes none of those properties: it retains both WQLinear_GEMM calls, both reduction paths, both hidden consumers, and both elementwise kernels. It only permits the sibling branches to overlap. A positive B1 result can support “recoverable scheduling headroom in the current separated AutoAWQ backend”; it cannot support first/novel gate-up fusion, first avoidance of the duplicate hidden input, best software baseline, or a need for new hardware.

## Guard decision

`PLAIN_GATE_UP_CONCURRENCY_NOT_NOVEL_MECHANISM`. The two-stream diagnostic remains useful as a characterization/control. The merged vLLM path is a semantically matched strong baseline, but not a strict one-variable A/B against C16 because current vLLM selects a different AWQ/MP kernel and fused activation path. QUICK/FLUTE are not needed to establish this guard; they remain alternate low-bit kernel neighbors rather than substitutes for this exact pinned Qwen2 loader path.
"""
    (out / "MERGED_GATE_UP_STRONG_BASELINE_GUARD.md").write_text(report, encoding="utf-8")

    final = {
        "schema_version": 1,
        "status": "PASS",
        "decision": "PLAIN_GATE_UP_CONCURRENCY_NOT_NOVEL_MECHANISM",
        "merged_same_checkpoint_available": True,
        "requantization_required": False,
        "quantization_semantics_preserved": True,
        "physical_packing_may_change": True,
        "strict_single_variable_ab_available": False,
        "strict_ab_reason": "pinned mature vLLM path changes runtime W4/MP backend, reduction path, merged N tiling, and SiluAndMul in addition to merging",
        "two_stream_diagnostic_still_valid": True,
        "two_stream_allowed_claim": "recoverable sibling scheduling headroom for the current separated AutoAWQ WQLinear_GEMM runtime",
        "claims_blocked": ["novel plain gate/up concurrency", "first merged gate/up projection", "first removal of duplicate hidden input", "best software baseline", "hardware mechanism necessity"],
        "lane7_merged_contract_emitted": True,
        "gpu_used": False,
        "cuda_initialized": False,
        "gpu_lock_used": False,
    }
    (out / "FINAL_DECISION.json").write_text(json.dumps(final, indent=2, sort_keys=True) + "\n")

    contract = {
        "schema_version": 1,
        "status": "QUALIFIED_STRONG_BASELINE_NOT_STRICT_SINGLE_VARIABLE_AB",
        "execution": "NOT_EXECUTED_BY_LANE6",
        "purpose": "MERGED_GATE_UP_NATIVE_STRONG_BASELINE",
        "scientific_identity": {"model_id": MODEL_ID, "revision": MODEL_REVISION, "input_and_D0_D3_scenario": "exact accepted C16 authority from 30b3016a7ad5b5ef86a3494c784e072938dee6c5", "quantization": {"method": "AWQ", "bits": 4, "group_size": 128, "zero_point": True}, "no_requantization": True},
        "source": {"vllm_commit": VLLM_COMMIT, "qwen2_path": "vllm/model_executor/models/qwen2.py", "quantization_path": "vllm/model_executor/layers/quantization/auto_awq.py", "source_anchors": f"{PACK}/SOURCE_ANCHORS.json"},
        "B0": {"name": "CURRENT_AUTOAWQ", "runtime": "AutoAWQ 0.2.7.post3 WQLinear_GEMM", "gate_up": "separate", "activation_multiply": "separate"},
        "B2": {"name": "MERGED_GATE_UP_STRONG_BASELINE", "runtime": f"vLLM {VLLM_COMMIT}", "gate_up": "MergedColumnParallelLinear", "activation_multiply": "SiluAndMul", "kernel_backend": "record exact AutoAWQ MP kernel selected at runtime", "comparison_class": "same checkpoint/quant semantics; cross-runtime strong baseline"},
        "cpu_preflight_before_gpu": ["build an isolated vLLM environment without altering the accepted C16 environment", "load config and verify Qwen2ForCausalLM merged mapping", "canonical-unpack gate/up qweight and qzeros before/after loading and require exact integer digests", "require scales byte equality and group/zero-point equality", "record selected MP kernel and prove no requantization"],
        "correctness_gate": {"generated_tokens": [23578, 11, 323, 3950], "all_outputs_finite": True, "gate_and_up_slice_shapes": [1, 1, 18944], "down_shape": [1, 1, 3584], "canonical_quant_params_exact": True, "fp16_comparison": {"rtol": 0.01, "atol": 0.05, "report_max_abs_mean_abs_relative_l2": True}, "performance_admission_requires_correctness": True},
        "measurement": {"primary": "complete natural D0-D3 CUDA-event wall", "order": "12 complete ABBA blocks B0,B2,B2,B0", "fresh_process_per_sample": True, "samples": {"B0": 24, "B2": 24, "total": 48}, "bootstrap": {"unit": "complete ABBA block", "resamples": 1000, "seed": 20261001}, "timeline_canaries": "one lightweight NSYS cuda,nvtx B0 and one B2; excluded from timing inference", "gpu_wall_budget_minutes": 8},
        "required_native_facts": ["exact selected vLLM W4 kernel", "gate_up GPU kernel and reduction count", "SiluAndMul kernel count", "logical gate/up slice correctness", "complete D0-D3 wall", "weight padding/workspace if any"],
        "forbidden": ["model re-quantization", "different checkpoint", "synthetic-only operator timing", "calling B0/B2 a merge-only A/B", "NCU as first step", "NVBit", "SASS", "Accel-Sim", "automatic hardware follow-up"],
        "gpu_lock": {"required": True, "path": "/data/c16/locks/c16_gpu_campaign.lock", "single_outer_lock": True, "release_receipt_required": True},
        "stop_conditions": ["canonical qweight/qzeros/scales mismatch", "requantization occurs", "exact checkpoint/scenario cannot load", "RTX4080 runtime/backend unsupported", "correctness tolerance or token identity fails", "GPU lock unavailable for 45 minutes", "8-minute GPU budget exceeded"],
    }
    (out / "LANE7_MERGED_GATE_UP_NATIVE_BASELINE_CONTRACT.json").write_text(json.dumps(contract, indent=2, sort_keys=True) + "\n")
    (out / "README.md").write_text("# C16 merged gate/up strong-baseline guard\n\nCPU-only source audit. Plain gate/up merge is a mature standard capability; the current two-stream diagnostic remains a characterization of the separated AutoAWQ path, not a novel mechanism claim.\n")

    names = sorted(path.name for path in out.iterdir() if path.is_file() and path.name != "SHA256SUMS")
    (out / "SHA256SUMS").write_text("".join(f"{sha256((out / name).read_bytes())}  {name}\n" for name in names))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--vllm-root", type=Path, default=VLLM_DEFAULT)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[3]
    if args.check:
        validate(repo, args.vllm_root)
        return
    build(repo, args.vllm_root, args.output_dir or repo / PACK)


if __name__ == "__main__":
    main()
