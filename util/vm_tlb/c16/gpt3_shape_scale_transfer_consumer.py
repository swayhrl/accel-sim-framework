#!/usr/bin/env python3
"""CPU-only scaffold and old-Qwen recompute for GPT-3 public-shape scale transfer."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import statistics
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np


COORDINATION_COMMIT = "0583d359d67a4d70c6a70a6a2e80d30ede971aba"
OLD_AUTHORITY_COMMIT = "3aad5887b9b4c5bec801962bf8035fed9d485f47"
OLD_AB_COMMIT = "0e88faa28c9066b48e394dce657d7a16e6332a32"
PRODUCER_BRANCH = "hrl/c16-gpt3-public-shape-scale-transfer-109-v1"
STATE_PACK = "docs/vm_tlb/review_packs/C16_SPLITK_MEMORY_STATE_INTERACTION_109_V1"
AB_PACK = "docs/vm_tlb/review_packs/C16_LOWBIT_SPLITK_NATIVE_AB_109_V1"
L2_BYTES = 67_108_864
SEED = 20260928
BOOTSTRAPS = 1000

QWEN = {
    "UP_M1": {"role": "EXPAND-like", "M": 1, "K": 3584, "N": 18944, "split1_grid": 148, "split8_grid": 1184, "reduction_grid": 37, "split1_scratch": 37888, "split8_scratch": 303104, "ab_point": "up_proj_M1"},
    "UP_M256": {"role": "EXPAND-like", "M": 256, "K": 3584, "N": 18944, "split1_grid": 2368, "split8_grid": 18944, "reduction_grid": 9472, "split1_scratch": 9699328, "split8_scratch": 77594624, "state_operator": "up_proj"},
    "DOWN_M1": {"role": "CONTRACT-like", "M": 1, "K": 18944, "N": 3584, "split1_grid": 28, "split8_grid": 224, "reduction_grid": 7, "split1_scratch": 7168, "split8_scratch": 57344, "ab_point": "down_proj_M1"},
    "DOWN_M256": {"role": "CONTRACT-like", "M": 256, "K": 18944, "N": 3584, "split1_grid": 448, "split8_grid": 3584, "reduction_grid": 1792, "split1_scratch": 1835008, "split8_scratch": 14680064, "state_operator": "down_proj"},
}

GPT3 = {
    "EXPAND_M1": {"role": "EXPAND-like", "M": 1, "K": 12288, "N": 49152},
    "EXPAND_M256": {"role": "EXPAND-like", "M": 256, "K": 12288, "N": 49152},
    "CONTRACT_M1": {"role": "CONTRACT-like", "M": 1, "K": 49152, "N": 12288},
    "CONTRACT_M256": {"role": "CONTRACT-like", "M": 256, "K": 49152, "N": 12288},
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def git_blob(repo: Path, commit: str, path: str) -> bytes:
    return subprocess.run(["git", "show", f"{commit}:{path}"], cwd=repo, check=True, stdout=subprocess.PIPE).stdout


def git_json(repo: Path, commit: str, path: str) -> Any:
    return json.loads(git_blob(repo, commit, path))


def git_tsv(repo: Path, commit: str, path: str) -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO(git_blob(repo, commit, path).decode("utf-8")), delimiter="\t"))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def stats(values: list[float]) -> dict[str, float | int]:
    return {
        "n": len(values),
        "min_ms": min(values),
        "median_ms": statistics.median(values),
        "max_ms": max(values),
        "mean_ms": statistics.mean(values),
        "cv": statistics.pstdev(values) / statistics.mean(values),
    }


def bootstrap_interaction(samples: list[dict[str, Any]], operator: str) -> tuple[float, float, float]:
    cells = ("A_W", "B_W", "A_E", "B_E")
    by: dict[tuple[int, str], list[float]] = defaultdict(list)
    for row in samples:
        if row["operator"] == operator:
            by[(int(row["block"]), row["cell"])].append(float(row["ms"]))
    require(all(len(by[(block, cell)]) == 2 for block in range(25) for cell in cells), "incomplete old mirror blocks")
    rng = np.random.default_rng(SEED)
    interactions = []
    for _ in range(BOOTSTRAPS):
        chosen = rng.integers(0, 25, size=25)
        medians = {cell: float(np.median([value for block in chosen for value in by[(int(block), cell)]])) for cell in cells}
        gain_w = 1 - medians["B_W"] / medians["A_W"]
        gain_e = 1 - medians["B_E"] / medians["A_E"]
        interactions.append(gain_w - gain_e)
    try:
        values = np.quantile(interactions, [0.05, 0.5, 0.95], method="linear")
    except TypeError:
        values = np.quantile(interactions, [0.05, 0.5, 0.95], interpolation="linear")
    return tuple(float(value) for value in values)


def gpt3_static(point: dict[str, int | str]) -> dict[str, Any]:
    m, k, n = int(point["M"]), int(point["K"]), int(point["N"])
    require(n % 128 == 0 and k % 128 == 0, "GPT-3 shape incompatible with frozen layout")
    parameter_count = k * n
    qweight_bytes = k * (n // 8) * 4
    qzeros_bytes = (k // 128) * (n // 8) * 4
    scales_bytes = (k // 128) * n * 2
    split1_grid = math.ceil(m / 16) * math.ceil(n / 128)
    split8_grid = split1_grid * 8
    split1_scratch = m * n * 2
    split8_scratch = split1_scratch * 8
    return {
        **point,
        "parameter_count": parameter_count,
        "dense_fp16_bytes": parameter_count * 2,
        "qweight_bytes": qweight_bytes,
        "qzeros_bytes": qzeros_bytes,
        "scales_bytes": scales_bytes,
        "w4_total_bytes": qweight_bytes + qzeros_bytes + scales_bytes,
        "qweight_l2_ratio": qweight_bytes / L2_BYTES,
        "split1_gemm_grid": split1_grid,
        "split8_gemm_grid": split8_grid,
        "split8_reduction_grid": math.ceil(m * n / 512),
        "split1_scratch_bytes": split1_scratch,
        "split8_scratch_bytes": split8_scratch,
    }


def write_tsv(path: Path, fields: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: "NA" if row.get(field) is None else row.get(field) for field in fields})


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def write_text(path: Path, value: str) -> None:
    path.write_text(value, encoding="utf-8", newline="\n")


def validate_pack_sha(repo: Path, pack: str, selected: list[str]) -> dict[str, str]:
    sums = {}
    for line in git_blob(repo, OLD_AUTHORITY_COMMIT, f"{pack}/SHA256SUMS").decode("utf-8").splitlines():
        digest, name = line.split(maxsplit=1)
        sums[name.strip()] = digest
    result = {}
    for name in selected:
        data = git_blob(repo, OLD_AUTHORITY_COMMIT, f"{pack}/{name}")
        observed = sha256_bytes(data)
        require(sums[name] == observed, f"old pack SHA mismatch: {pack}/{name}")
        result[name] = observed
    return result


def recompute_old_qwen(repo: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    selected_state = ["SOURCE_AND_RUN_MANIFEST.json", "TIMING_SAMPLES.tsv", "CORRECTNESS_AND_LAUNCH.tsv", "NCU_SUMMARY.json"]
    selected_ab = ["EXPERIMENT_MANIFEST.json", "INPUT_AND_WEIGHT_BINDINGS.tsv", "LAUNCH_AUDIT.tsv", "TIMING_SAMPLES.tsv", "BUILD_AND_BINARY_RECEIPT.json"]
    state_shas = validate_pack_sha(repo, STATE_PACK, selected_state)
    ab_shas = validate_pack_sha(repo, AB_PACK, selected_ab)
    state_samples_raw = git_tsv(repo, OLD_AUTHORITY_COMMIT, f"{STATE_PACK}/TIMING_SAMPLES.tsv")
    state_samples = [{**row, "block": int(row["block"]), "position": int(row["position"]), "ms": float(row["ms"])} for row in state_samples_raw]
    ab_samples_raw = git_tsv(repo, OLD_AUTHORITY_COMMIT, f"{AB_PACK}/TIMING_SAMPLES.tsv")
    ab_samples = [{**row, "block": int(row["block"]), "position": int(row["position"]), "ms": float(row["ms"])} for row in ab_samples_raw]
    bindings = git_tsv(repo, OLD_AUTHORITY_COMMIT, f"{AB_PACK}/INPUT_AND_WEIGHT_BINDINGS.tsv")
    qweight_bytes = {row["operator"]: int(row["bytes"]) for row in bindings if row["tensor"] == "qweight"}
    require(qweight_bytes == {"up_proj": 33_947_648, "down_proj": 33_947_648}, "old qweight size mismatch")
    ncu = git_json(repo, OLD_AUTHORITY_COMMIT, f"{STATE_PACK}/NCU_SUMMARY.json")["operators"]
    rows = []
    for point_name, point in QWEN.items():
        row = {
            "authority_commit": OLD_AUTHORITY_COMMIT,
            "model_shape_class": "Qwen7B accepted",
            "point": point_name,
            "role": point["role"],
            "M": point["M"], "K": point["K"], "N": point["N"],
            "split1_gemm_grid": point["split1_grid"], "split8_gemm_grid": point["split8_grid"], "split8_reduction_grid": point["reduction_grid"],
            "split1_scratch_bytes": point["split1_scratch"], "split8_scratch_bytes": point["split8_scratch"],
            "qweight_bytes": 33_947_648, "l2_bytes": L2_BYTES, "qweight_l2_ratio": 33_947_648 / L2_BYTES,
        }
        if "ab_point" in point:
            values_a = [entry["ms"] for entry in ab_samples if entry["point"] == point["ab_point"] and entry["arm"] == "A"]
            values_b = [entry["ms"] for entry in ab_samples if entry["point"] == point["ab_point"] and entry["arm"] == "B"]
            sa, sb = stats(values_a), stats(values_b)
            for key, value in sa.items(): row[f"A_W_{key}"] = value
            for key, value in sb.items(): row[f"B_W_{key}"] = value
            row["gain_W"] = 1 - sb["median_ms"] / sa["median_ms"]
            row["state_protocol"] = "WARM_ONLY_ORIGINAL_ABBA; no disturbed M1 authority"
            row["source_timing_pack"] = AB_PACK
        else:
            operator = point["state_operator"]
            cell_stats = {}
            for cell in ("A_W", "B_W", "A_E", "B_E"):
                values = [entry["ms"] for entry in state_samples if entry["operator"] == operator and entry["cell"] == cell]
                cell_stats[cell] = stats(values)
                for key, value in cell_stats[cell].items(): row[f"{cell}_{key}"] = value
            row["gain_W"] = 1 - cell_stats["B_W"]["median_ms"] / cell_stats["A_W"]["median_ms"]
            row["gain_E"] = 1 - cell_stats["B_E"]["median_ms"] / cell_stats["A_E"]["median_ms"]
            row["state_interaction"] = row["gain_W"] - row["gain_E"]
            p05, p50, p95 = bootstrap_interaction(state_samples, operator)
            row.update({"bootstrap_interaction_p05": p05, "bootstrap_interaction_median": p50, "bootstrap_interaction_p95": p95})
            row["state_protocol"] = "WARM_SAME_ARM versus EVICT_CONDITIONED, 25 complete mirror blocks"
            row["source_timing_pack"] = STATE_PACK
            for cell in ("A_W", "B_W", "A_E", "B_E"):
                row[f"ncu_{cell}_dram_bytes"] = ncu[operator][cell]["dram_bytes_total"]
        rows.append(row)
    audit = {
        "old_authority_commit": OLD_AUTHORITY_COMMIT,
        "old_ab_authority_commit": OLD_AB_COMMIT,
        "state_pack_selected_file_sha256": state_shas,
        "ab_pack_selected_file_sha256": ab_shas,
        "accepted_binary_sha256": {
            "split8": "9e8d38a04c28770338fcef8ae0f9a90a984b7a8f95bcb98a407738594e1c08d7",
            "split1": "1aa8db13f5fd10651aa4241f58200e3a7075214d34cca4d70fbcbe7cbbc07887",
        },
        "timing_rows": {"state": len(state_samples), "ab": len(ab_samples)},
        "recompute_status": "PASS",
    }
    return rows, audit


OLD_FIELDS = [
    "authority_commit", "model_shape_class", "point", "role", "M", "K", "N", "split1_gemm_grid", "split8_gemm_grid", "split8_reduction_grid",
    "split1_scratch_bytes", "split8_scratch_bytes", "qweight_bytes", "l2_bytes", "qweight_l2_ratio", "state_protocol", "source_timing_pack",
    "A_W_n", "A_W_min_ms", "A_W_median_ms", "A_W_max_ms", "A_W_mean_ms", "A_W_cv",
    "B_W_n", "B_W_min_ms", "B_W_median_ms", "B_W_max_ms", "B_W_mean_ms", "B_W_cv", "gain_W",
    "A_E_n", "A_E_min_ms", "A_E_median_ms", "A_E_max_ms", "A_E_mean_ms", "A_E_cv",
    "B_E_n", "B_E_min_ms", "B_E_median_ms", "B_E_max_ms", "B_E_mean_ms", "B_E_cv", "gain_E", "state_interaction",
    "bootstrap_interaction_p05", "bootstrap_interaction_median", "bootstrap_interaction_p95",
    "ncu_A_W_dram_bytes", "ncu_B_W_dram_bytes", "ncu_A_E_dram_bytes", "ncu_B_E_dram_bytes",
]

DENSE_FIELDS = ["point", "M", "K", "N", "evidence_class", "raw_source", "n", "min_ms", "median_ms", "max_ms", "mean_ms", "cv", "kernel_inventory", "grid", "block", "correctness_status", "ncu_l1tex_bytes", "ncu_lts_bytes", "ncu_dram_bytes", "status"]
W4_FIELDS = ["point", "role", "M", "K", "N", "arm", "state", "raw_source", "n", "min_ms", "median_ms", "max_ms", "mean_ms", "cv", "correctness_status", "gemm_grid", "reduction_present", "reduction_grid", "scratch_bytes", "ncu_gemm_dram_bytes", "ncu_reduction_dram_bytes", "status"]
COMPARE_FIELDS = ["model_shape_class", "point", "role", "M", "K", "N", "split1_gemm_grid", "split8_gemm_grid", "qweight_bytes", "l2_bytes", "qweight_l2_ratio", "gain_W", "gain_E", "state_interaction", "bootstrap_interaction_p05", "bootstrap_interaction_median", "bootstrap_interaction_p95", "ncu_A_W_dram_bytes", "ncu_B_W_dram_bytes", "ncu_A_E_dram_bytes", "ncu_B_E_dram_bytes", "matched_old_point", "delta_gain_W", "delta_gain_E", "delta_state_interaction", "warm_direction_changed", "disturbed_direction_changed", "interaction_direction_changed", "status"]


def build(repo: Path, output: Path, producer_remote_head: str) -> None:
    output.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "merge-base", "--is-ancestor", COORDINATION_COMMIT, "HEAD"], cwd=repo, check=True)
    old_rows, old_audit = recompute_old_qwen(repo)
    write_tsv(output / "OLD_QWEN_RECOMPUTE.tsv", OLD_FIELDS, old_rows)
    write_tsv(output / "NEW_DENSE_RECOMPUTE.tsv", DENSE_FIELDS, [])
    write_tsv(output / "NEW_W4_RECOMPUTE.tsv", W4_FIELDS, [])
    write_tsv(output / "SCALE_TRANSFER_COMPARISON.tsv", COMPARE_FIELDS, [])

    static = {name: gpt3_static(point) for name, point in GPT3.items()}
    require(all(item["parameter_count"] == 603_979_776 for item in static.values()), "GPT-3 parameter count mismatch")
    require(all(item["dense_fp16_bytes"] == 1_207_959_552 for item in static.values()), "GPT-3 dense bytes mismatch")
    require(all(item["qweight_bytes"] == 301_989_888 for item in static.values()), "GPT-3 qweight mismatch")
    require(all(item["qzeros_bytes"] == 2_359_296 and item["scales_bytes"] == 9_437_184 for item in static.values()), "GPT-3 W4 metadata mismatch")
    require(static["EXPAND_M1"]["split1_gemm_grid"] == 384 and static["CONTRACT_M1"]["split1_gemm_grid"] == 96, "GPT-3 M1 grid mismatch")
    require(static["EXPAND_M256"]["split8_gemm_grid"] == 49152 and static["CONTRACT_M256"]["split8_gemm_grid"] == 12288, "GPT-3 M256 grid mismatch")

    formulas = {
        "schema_version": 1,
        "status": "FROZEN_BEFORE_PRODUCER_CONSUMPTION",
        "coordination_commit": COORDINATION_COMMIT,
        "old_authority_commit": OLD_AUTHORITY_COMMIT,
        "gpt3_public_shapes": static,
        "evidence_classes": {"dense": "GPT-3 public-shape synthetic FP16 Dense anchor", "w4": "GPT-3 public-shape mapped to accepted AutoAWQ W4 mechanism proxy"},
        "formulas": {
            "gain_W": "1 - median(B_W_ms) / median(A_W_ms)",
            "gain_E": "1 - median(B_E_ms) / median(A_E_ms)",
            "state_interaction": "gain_W - gain_E",
            "qweight_l2_ratio": "qweight_bytes / 67108864",
            "split1_grid": "ceil(M/16) * ceil(N/128)",
            "split8_grid": "8 * split1_grid",
            "split1_scratch_bytes": "M * N * 2",
            "split8_scratch_bytes": "8 * M * N * 2",
            "scale_delta_gain_W": "GPT3 gain_W - matched Qwen gain_W",
            "scale_delta_gain_E": "GPT3 gain_E - matched Qwen gain_E",
            "scale_delta_state_interaction": "GPT3 state_interaction - matched Qwen state_interaction",
            "direction_changed": "strict sign comparison; zero is reported separately, never forced positive/negative",
        },
        "bootstrap": {"unit": "complete mirror block", "seed": SEED, "resamples": BOOTSTRAPS, "quantiles": [0.05, 0.5, 0.95], "quantile_rule": "linear"},
        "matching": {"roles": {"EXPAND-like": "Qwen up_proj vs GPT3 expand", "CONTRACT-like": "Qwen down_proj vs GPT3 contract"}, "M": [1, 256], "warning": "shape-direction analogy only; not identical model semantics"},
        "output_schemas": {"dense": DENSE_FIELDS, "w4": W4_FIELDS, "scale_transfer": COMPARE_FIELDS},
        "consumer_rule": "final metrics must be recomputed from producer raw samples/rows; producer derived summaries are comparison-only",
    }
    write_json(output / "FORMULA_AND_SCHEMA_FREEZE.json", formulas)

    gate_open = bool(producer_remote_head)
    audit = {
        "schema_version": 1,
        "status": "PREPARED_AWAITING_PRODUCER" if not gate_open else "PRODUCER_BRANCH_SEEN_NOT_YET_ACCEPTED",
        "coordination": {"branch": "hrl/c16-gpt3-public-shape-scale-transfer-v1-coordination", "head": COORDINATION_COMMIT},
        "old_qwen": old_audit,
        "producer_gate": {
            "expected_branch": PRODUCER_BRANCH,
            "remote_head_observed": producer_remote_head or None,
            "formal_consumption_started": False,
            "required_before_consumption": ["final commit pushed", "review-pack SHA closure", "Lane8 PRE_GPU_READY binding", "GPU lock released", "correctness closed", "launch identity closed", "raw samples available"],
        },
        "gpu_used": False,
        "gpu_lock_requested": False,
        "lane4_partial_accessed": False,
    }
    write_json(output / "AUTHORITY_AUDIT.json", audit)
    write_json(output / "NCU_COMPARISON.json", {"schema_version": 1, "status": "WAITING_FOR_ACCEPTED_PRODUCER_RAW", "old_qwen_source": f"{OLD_AUTHORITY_COMMIT}:{STATE_PACK}/NCU_SUMMARY.json", "new_dense": None, "new_w4": None, "claim_boundary": "raw NCU rows only; GEMM/reduction separate; no tensor attribution"})

    write_text(output / "GRID_AND_WORKSET_INTERPRETATION.md", f"""# Grid 与工作集比较合同

本阶段只冻结数学，不包含新 GPU 结果。

- GPT-3 公开 FFN 两个方向均有 603,979,776 个参数，FP16 单矩阵 1,207,959,552 B。
- W4 proxy 的 qweight 为 301,989,888 B（288 MiB），约为 64 MiB L2 的 {static['EXPAND_M1']['qweight_l2_ratio']:.6f} 倍；旧 Qwen qweight 为 33,947,648 B，约为 L2 的 {33_947_648/L2_BYTES:.6f} 倍。
- M1 split1 grid 从旧 Qwen expand-like/contract-like 的 148/28 增至 GPT-3 proxy 的 384/96。
- M256 split1 grid 从 2368/448 增至 6144/1536；split8 始终是对应 split1 的8倍。
- 这些只定位并行供给、workspace/reduction 与工作集尺度；不能仅凭 grid 或 qweight/L2 宣布 timing 或 cache 因果。

未来正式比较只匹配同一 accepted split8/split1 implementation family、相同 WARM_SAME_ARM/EVICT_CONDITIONED protocol、相同 role 和 M。Qwen up/down 与 GPT-3 expand/contract 只是形状方向类比。
""")
    write_text(output / "SCIENTIFIC_INTERPRETATION.md", """# 科学解释（准备态）

当前只完成旧 Qwen authority 的独立复算和未来比较合同冻结。GPT-3 producer 尚未形成可接受 final/raw，因此现在不能回答规模变化是否改变 split 策略方向、驻留状态敏感性或是否值得后续机制/模拟。

已知的静态差异是：GPT-3 W4 proxy qweight 从旧 Qwen 的约0.51×L2增至4.5×L2；M1 split1 grid 也由148/28增至384/96。这些是待新 raw timing/launch/NCU 检验的解释变量，不是结果。
""")
    write_json(output / "FINAL_DECISION.json", {"schema_version": 1, "status": "CONSUMER_SCAFFOLD_READY_AWAITING_ACCEPTED_PRODUCER", "old_qwen_recompute": "PASS", "formula_and_schema_freeze": "PASS", "new_producer_consumed": False, "scientific_decision": "尚无新数据，不能形成GPT-3规模转移结论", "gpu_used": False})
    write_text(output / "OPEN_ISSUES.md", f"""# Open issues

- Producer branch `{PRODUCER_BRANCH}` was not present at the bounded poll used for this scaffold.
- Formal consumption remains gated on final pack/SHA, Lane8 PRE_GPU_READY binding, released GPU lock, correctness, launch closure, and raw samples.
- `NEW_DENSE_RECOMPUTE.tsv`, `NEW_W4_RECOMPUTE.tsv`, and `SCALE_TRANSFER_COMPARISON.tsv` intentionally contain schema headers only.
""")
    write_text(output / "README.md", """# C16 GPT-3 public-shape scale-transfer consumer scaffold

CPU-only Lane 6 preparation. Start with `AUTHORITY_AUDIT.json`, `OLD_QWEN_RECOMPUTE.tsv`, and `FORMULA_AND_SCHEMA_FREEZE.json`.

The producer gate is closed. No future result has been prefilled; new result tables contain headers only. The old Qwen values are independently recomputed from committed raw timing samples rather than copied from derived summaries.

Generator: `util/vm_tlb/c16/gpt3_shape_scale_transfer_consumer.py`.
""")

    files = sorted(path for path in output.iterdir() if path.is_file() and path.name != "SHA256SUMS")
    write_text(output / "SHA256SUMS", "\n".join(f"{sha256_bytes(path.read_bytes())}  {path.name}" for path in files) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, default=Path("docs/vm_tlb/review_packs/C16_GPT3_PUBLIC_SHAPE_SCALE_TRANSFER_CONSUMER_174NEW_V1"))
    parser.add_argument("--producer-remote-head", default="")
    args = parser.parse_args()
    repo = args.repo_root.resolve()
    output = args.output if args.output.is_absolute() else repo / args.output
    build(repo, output, args.producer_remote_head)


if __name__ == "__main__":
    main()
