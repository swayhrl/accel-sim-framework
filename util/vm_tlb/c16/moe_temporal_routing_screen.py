#!/usr/bin/env python3
"""Build the C16 MoE temporal-routing authority screen review pack.

This is intentionally CPU-only.  It reads accepted/durable routing authority,
validates its shape and provenance, computes set-based temporal descriptors,
and performs a decode-step-order shuffle control.  It does not model caches,
transactions, kernel order, or timing.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import random
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


Q30_COMMIT = "28620a89d55fd9230103a31d31d14757b57e1e0f"
DEEPSEEK_COMMIT = "baf892ced6d66cbacabb995caf095e5280995097"
OLMOE_V34_COMMIT = "ab26365dc663268b0799818db6687ed466e8c925"
OLMOE_V40_COMMIT = "85563ec6f55a0ad743d21483aa49c24fdb5cf3bf"

DEEPSEEK_PATH = (
    "docs/vm_tlb/review_packs/"
    "C16_DEEPSEEK_V2_LITE_S2_PRODUCER_109_V23R1/MOE_ROUTING_RECEIPT.json"
)
OLMOE_PATH = (
    "docs/vm_tlb/review_packs/"
    "C16_OLMOE_S2_PRODUCER_109_V34/NATURAL_TOP8_ROUTING.json"
)
OLMOE_STATE_PATH = (
    "docs/vm_tlb/review_packs/"
    "C16_OLMOE_S2_PRODUCER_109_V34/S2_STATE_RECEIPT.json"
)

Q30_EXPECTED_SHA = "07b68ead81d9471c46b9fadc77077f80a192d74f109be41b8c17e03280ed58dd"
DEEPSEEK_EXPECTED_SHA = "85027da8c989d5d811d4c4a275d1ad03cf482a7d63f4f4edab43658e118c84fc"
OLMOE_EXPECTED_SHA = "d973b1f2915bb7d5bfd47f0b83b1a8c19106f51ecacfe89ba359ab3a6a3207c3"

SEED = 20260928
PERMUTATIONS = 1000


def compact_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def pretty_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob(repo: Path, commit: str, path: str) -> bytes:
    result = subprocess.run(
        ["git", "show", f"{commit}:{path}"],
        cwd=repo,
        check=True,
        stdout=subprocess.PIPE,
    )
    return result.stdout


def check_ancestor(repo: Path, ancestor: str, descendant: str) -> None:
    subprocess.run(
        ["git", "merge-base", "--is-ancestor", ancestor, descendant],
        cwd=repo,
        check=True,
    )


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def mean(values: Iterable[float]) -> float | None:
    values = list(values)
    return sum(values) / len(values) if values else None


def quantile(values: list[float], probability: float) -> float:
    """R-7/NumPy-style linear quantile over a non-empty list."""
    require(bool(values), "quantile requires values")
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    fraction = position - lower
    return ordered[lower] * (1.0 - fraction) + ordered[upper] * fraction


def fmt(value: Any) -> str:
    if value is None:
        return "NA"
    if isinstance(value, float):
        return f"{value:.9f}"
    return str(value)


def lag_stats(step_sets: list[set[int]], lag: int) -> dict[str, Any]:
    if len(step_sets) <= lag:
        return {
            "pairs": 0,
            "overlap_mean": None,
            "jaccard_mean": None,
            "retention_mean": None,
        }
    overlaps: list[float] = []
    jaccards: list[float] = []
    retentions: list[float] = []
    for left, right in zip(step_sets, step_sets[lag:]):
        intersection = len(left & right)
        union = len(left | right)
        overlaps.append(float(intersection))
        jaccards.append(intersection / union)
        retentions.append(intersection / len(left))
    return {
        "pairs": len(overlaps),
        "overlap_mean": mean(overlaps),
        "jaccard_mean": mean(jaccards),
        "retention_mean": mean(retentions),
    }


def per_expert_metrics(steps: list[int], sets: list[set[int]]) -> dict[str, Any]:
    appearances: dict[int, list[int]] = defaultdict(list)
    positions: dict[int, list[int]] = defaultdict(list)
    for position, (step, selected) in enumerate(zip(steps, sets)):
        for expert in selected:
            appearances[expert].append(step)
            positions[expert].append(position)

    selected_steps: dict[str, Any] = {}
    inter_arrivals: dict[str, Any] = {}
    within: dict[int, dict[str, Any]] = {window: {} for window in (1, 2, 4, 8)}
    longest_absence: dict[str, Any] = {}

    for expert in sorted(appearances):
        key = str(expert)
        expert_steps = appearances[expert]
        distances = [b - a for a, b in zip(expert_steps, expert_steps[1:])]
        selected_steps[key] = expert_steps
        inter_arrivals[key] = distances
        for window in within:
            within[window][key] = (
                sum(distance <= window for distance in distances) / len(distances)
                if distances
                else None
            )

        expert_positions = positions[expert]
        absent_runs = [expert_positions[0]]
        absent_runs.extend(
            right - left - 1
            for left, right in zip(expert_positions, expert_positions[1:])
        )
        absent_runs.append(len(sets) - 1 - expert_positions[-1])
        longest_absence[key] = max(absent_runs)

    return {
        "selected_steps": selected_steps,
        "inter_arrivals": inter_arrivals,
        "within": within,
        "longest_absence": longest_absence,
    }


def sequence_metrics(sequence: dict[str, Any]) -> dict[str, Any]:
    steps = sequence["steps"]
    ordered_ids = sequence["ids"]
    sets = [set(ids) for ids in ordered_ids]
    top_k = sequence["top_k"]
    require(all(len(ids) == top_k for ids in ordered_ids), "top-k size mismatch")
    require(all(len(selected) == top_k for selected in sets), "duplicate expert within step")

    frequency = Counter(expert for selected in sets for expert in selected)
    ranked_counts = sorted(frequency.values(), reverse=True)
    total = len(sets) * top_k
    cumulative: list[int] = []
    seen: set[int] = set()
    for selected in sets:
        seen.update(selected)
        cumulative.append(len(seen))

    exact_keys = [tuple(sorted(selected)) for selected in sets]
    expert_metrics = per_expert_metrics(steps, sets)
    result: dict[str, Any] = {
        "lineage": sequence["lineage"],
        "scenario": sequence["scenario"],
        "layer_id": sequence["layer_id"],
        "decode_steps": len(steps),
        "first_step": steps[0],
        "last_step": steps[-1],
        "top_k": top_k,
        "sequence_power": "LOW_TEMPORAL_POWER" if len(steps) <= 4 else "DESCRIPTIVE_SCREEN",
        "cumulative_distinct_experts": len(seen),
        "cumulative_distinct_by_step_json": compact_json(cumulative),
        "top1_frequency_concentration": ranked_counts[0] / total,
        "top4_frequency_concentration": sum(ranked_counts[:4]) / total,
        "exact_set_repeat_count": len(exact_keys) - len(set(exact_keys)),
        "step_topk_sizes_json": compact_json([len(ids) for ids in ordered_ids]),
        "exact_sets_by_step_json": compact_json(
            [{"decode_step": step, "expert_ids": ids} for step, ids in zip(steps, ordered_ids)]
        ),
        "per_expert_selected_steps_json": compact_json(expert_metrics["selected_steps"]),
        "per_expert_inter_arrivals_json": compact_json(expert_metrics["inter_arrivals"]),
        "per_expert_reused_within_1_fraction_json": compact_json(expert_metrics["within"][1]),
        "per_expert_reused_within_2_fraction_json": compact_json(expert_metrics["within"][2]),
        "per_expert_reused_within_4_fraction_json": compact_json(expert_metrics["within"][4]),
        "per_expert_reused_within_8_fraction_json": compact_json(expert_metrics["within"][8]),
        "per_expert_longest_absence_gap_json": compact_json(expert_metrics["longest_absence"]),
    }
    for lag in (1, 2, 4, 8):
        stats = lag_stats(sets, lag)
        result[f"lag{lag}_pairs"] = stats["pairs"]
        result[f"lag{lag}_overlap_mean"] = stats["overlap_mean"]
        result[f"lag{lag}_jaccard_mean"] = stats["jaccard_mean"]
        result[f"lag{lag}_retention_mean"] = stats["retention_mean"]
    result["adjacent_pair_count"] = result["lag1_pairs"]
    result["adjacent_overlap_mean"] = result["lag1_overlap_mean"]
    result["adjacent_jaccard_mean"] = result["lag1_jaccard_mean"]
    result["adjacent_retention_mean"] = result["lag1_retention_mean"]
    return result


def shuffle_control(sequence: dict[str, Any], rng: random.Random) -> dict[str, Any]:
    sets = [set(ids) for ids in sequence["ids"]]
    actual = lag_stats(sets, 1)
    overlap_samples: list[float] = []
    jaccard_samples: list[float] = []
    for _ in range(PERMUTATIONS):
        order = list(range(len(sets)))
        rng.shuffle(order)
        shuffled = [sets[index] for index in order]
        stats = lag_stats(shuffled, 1)
        overlap_samples.append(stats["overlap_mean"])
        jaccard_samples.append(stats["jaccard_mean"])

    def distribution(samples: list[float]) -> dict[str, float]:
        return {
            "median": quantile(samples, 0.50),
            "p05": quantile(samples, 0.05),
            "p95": quantile(samples, 0.95),
        }

    overlap_distribution = distribution(overlap_samples)
    jaccard_distribution = distribution(jaccard_samples)

    def interval_position(actual_value: float, dist: dict[str, float]) -> str:
        if actual_value < dist["p05"]:
            return "BELOW_SHUFFLE_P05"
        if actual_value > dist["p95"]:
            return "ABOVE_SHUFFLE_P95"
        return "WITHIN_SHUFFLE_P05_P95"

    return {
        "sequence_id": sequence["sequence_id"],
        "lineage": sequence["lineage"],
        "layer_id": sequence["layer_id"],
        "decode_steps": len(sequence["steps"]),
        "top_k": sequence["top_k"],
        "power_label": "LOW_TEMPORAL_POWER" if len(sequence["steps"]) <= 4 else "DESCRIPTIVE_SCREEN",
        "actual": {
            "mean_adjacent_overlap": actual["overlap_mean"],
            "mean_adjacent_jaccard": actual["jaccard_mean"],
        },
        "shuffle": {
            "mean_adjacent_overlap": overlap_distribution,
            "mean_adjacent_jaccard": jaccard_distribution,
        },
        "descriptive_interval_position": {
            "overlap": interval_position(actual["overlap_mean"], overlap_distribution),
            "jaccard": interval_position(actual["jaccard_mean"], jaccard_distribution),
        },
    }


def write_tsv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: fmt(row.get(field)) for field in fields})


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def build(repo: Path, q30_source: Path, output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    check_ancestor(repo, OLMOE_V34_COMMIT, OLMOE_V40_COMMIT)

    q30_bytes = q30_source.read_bytes()
    require(sha256_bytes(q30_bytes) == Q30_EXPECTED_SHA, "Q30 durable receipt SHA mismatch")
    q30 = json.loads(q30_bytes)
    require(q30["status"] == "Q30_S2_T2048_PREFIX_D4_STREAMING_PASS", "Q30 status mismatch")
    require(q30["decode_forwards"] == 4, "Q30 decode length mismatch")
    q30_decode = {record["decode_step"]: record for record in q30["decode"]}
    q30_router = [record for record in q30["router"] if record["phase"] == "DECODE"]
    require(len(q30_router) == 192, "Q30 requires 4 x 48 decode router records")

    q30_by_layer: dict[int, dict[int, list[int]]] = defaultdict(dict)
    for record in q30_router:
        ids = record["selected_expert_ids"]
        require(len(ids) == 1 and len(ids[0]) == 8, "Q30 decode record must contain one top-8")
        q30_by_layer[int(record["layer_id"])][int(record["decode_step"])] = [int(x) for x in ids[0]]
    require(sorted(q30_by_layer) == list(range(48)), "Q30 layer coverage mismatch")

    deepseek_bytes = git_blob(repo, DEEPSEEK_COMMIT, DEEPSEEK_PATH)
    require(sha256_bytes(deepseek_bytes) == DEEPSEEK_EXPECTED_SHA, "DeepSeek routing SHA mismatch")
    deepseek = json.loads(deepseek_bytes)
    deepseek_ids = deepseek["natural_topk_ids"]
    require(len(deepseek_ids) == 1 and len(deepseek_ids[0]) == 6, "DeepSeek top-6 mismatch")
    require(len(set(deepseek_ids[0])) == 6, "DeepSeek top-6 contains duplicates")

    olmoe_bytes = git_blob(repo, OLMOE_V34_COMMIT, OLMOE_PATH)
    require(sha256_bytes(olmoe_bytes) == OLMOE_EXPECTED_SHA, "OLMoE routing SHA mismatch")
    olmoe = json.loads(olmoe_bytes)
    olmoe_state = json.loads(git_blob(repo, OLMOE_V34_COMMIT, OLMOE_STATE_PATH))
    require(olmoe["forced_expert_id"] is False, "OLMoE must be natural, not forced")
    require(olmoe["status"] == "PASS_NATURAL_TOP8", "OLMoE routing status mismatch")
    require(olmoe_state["status"] == "PASS_NATIVE_S2_D32", "OLMoE state status mismatch")
    olmoe_records = olmoe["repeat_decode_records"]
    require(len(olmoe_records) == 32, "OLMoE requires 32 decode records")
    require([record["decode_step"] for record in olmoe_records] == list(range(1, 33)), "OLMoE steps must be 1..32")
    for record in olmoe_records:
        require(len(record["natural_top8_ids"]) == 8, "OLMoE top-8 size mismatch")
        require(len(set(record["natural_top8_ids"])) == 8, "OLMoE top-8 contains duplicates")
        require(len(record["route_weights"]) == 8, "OLMoE route-weight size mismatch")
        require(isinstance(record["next_token_id"], int), "OLMoE next-token binding missing")
        require(len(record["router_logits_sha256"]) == 64, "OLMoE router-logits SHA missing")
        require(len(record["mlp_router_input"]["sha256"]) == 64, "OLMoE router-input SHA missing")

    audit_rows = [
        {
            "lineage": "Q30",
            "producer_commit": Q30_COMMIT,
            "scenario": q30["scenario"],
            "decode_steps": "4 (0..3)",
            "layer_coverage": "48 layers (0..47)",
            "top_k": 8,
            "explicit_ids": "YES",
            "route_weights": "NO",
            "token_binding": "YES",
            "durable_authority": "YES",
            "classification": "FULL_MODEL_EXPLICIT_SEQUENCE",
            "source_path": str(q30_source),
            "sha256": Q30_EXPECTED_SHA,
            "limitations": "Only four decode steps; LOW_TEMPORAL_POWER; no route weights; committed summary alone is hash-only.",
        },
        {
            "lineage": "DEEPSEEK",
            "producer_commit": DEEPSEEK_COMMIT,
            "scenario": "S2_TEXT B1/T2048 single selected decode state",
            "decode_steps": "1",
            "layer_coverage": "layer 1 only",
            "top_k": 6,
            "explicit_ids": "YES",
            "route_weights": "YES",
            "token_binding": "NO",
            "durable_authority": "YES",
            "classification": "SINGLE_STATE_ONLY",
            "source_path": f"git:{DEEPSEEK_COMMIT}:{DEEPSEEK_PATH}",
            "sha256": DEEPSEEK_EXPECTED_SHA,
            "limitations": "One explicit selected decode state only; no durable multi-step routing sequence found; no token binding in routing receipt.",
        },
        {
            "lineage": "OLMOE",
            "producer_commit": OLMOE_V34_COMMIT,
            "scenario": olmoe_state["scenario"],
            "decode_steps": "32 (1..32)",
            "layer_coverage": "layer 1 only",
            "top_k": 8,
            "explicit_ids": "YES",
            "route_weights": "YES",
            "token_binding": "YES",
            "durable_authority": "YES (V34 ancestor of accepted V40)",
            "classification": "SINGLE_LAYER_EXPLICIT_SEQUENCE",
            "source_path": f"git:{OLMOE_V34_COMMIT}:{OLMOE_PATH}",
            "sha256": OLMOE_EXPECTED_SHA,
            "limitations": "Single layer only; cannot represent full-model traffic, cache capacity, L2 transactions, or timing.",
        },
    ]
    audit_fields = [
        "lineage", "producer_commit", "scenario", "decode_steps", "layer_coverage",
        "top_k", "explicit_ids", "route_weights", "token_binding", "durable_authority",
        "classification", "source_path", "sha256", "limitations",
    ]
    write_tsv(output / "TEMPORAL_AUTHORITY_AUDIT.tsv", audit_rows, audit_fields)

    sequences: list[dict[str, Any]] = []
    for layer in sorted(q30_by_layer):
        records = q30_by_layer[layer]
        require(sorted(records) == [0, 1, 2, 3], f"Q30 layer {layer} step coverage mismatch")
        sequences.append(
            {
                "sequence_id": f"Q30_LAYER_{layer}",
                "lineage": "Q30",
                "scenario": q30["scenario"],
                "layer_id": layer,
                "steps": sorted(records),
                "ids": [records[step] for step in sorted(records)],
                "top_k": 8,
                "authority_classification": "FULL_MODEL_EXPLICIT_SEQUENCE",
                "source_path": str(q30_source),
                "source_sha256": Q30_EXPECTED_SHA,
            }
        )
    sequences.append(
        {
            "sequence_id": "OLMOE_LAYER_1",
            "lineage": "OLMOE",
            "scenario": olmoe_state["scenario"],
            "layer_id": 1,
            "steps": [record["decode_step"] for record in olmoe_records],
            "ids": [record["natural_top8_ids"] for record in olmoe_records],
            "top_k": 8,
            "authority_classification": "SINGLE_LAYER_EXPLICIT_SEQUENCE",
            "source_path": f"git:{OLMOE_V34_COMMIT}:{OLMOE_PATH}",
            "source_sha256": OLMOE_EXPECTED_SHA,
        }
    )

    index_rows: list[dict[str, Any]] = []
    for sequence in sequences:
        canonical = compact_json(
            [
                {"decode_step": step, "expert_ids": ids}
                for step, ids in zip(sequence["steps"], sequence["ids"])
            ]
        ).encode("utf-8")
        index_rows.append(
            {
                "sequence_id": sequence["sequence_id"],
                "lineage": sequence["lineage"],
                "scenario": sequence["scenario"],
                "layer_id": sequence["layer_id"],
                "decode_steps": len(sequence["steps"]),
                "first_step": sequence["steps"][0],
                "last_step": sequence["steps"][-1],
                "top_k": sequence["top_k"],
                "authority_classification": sequence["authority_classification"],
                "analysis_status": "LOW_TEMPORAL_POWER" if len(sequence["steps"]) <= 4 else "ANALYZED",
                "canonical_sequence_sha256": sha256_bytes(canonical),
                "source_path": sequence["source_path"],
                "source_sha256": sequence["source_sha256"],
            }
        )
    index_fields = [
        "sequence_id", "lineage", "scenario", "layer_id", "decode_steps", "first_step",
        "last_step", "top_k", "authority_classification", "analysis_status",
        "canonical_sequence_sha256", "source_path", "source_sha256",
    ]
    write_tsv(output / "EXPLICIT_SEQUENCE_INDEX.tsv", index_rows, index_fields)

    metric_rows = [sequence_metrics(sequence) for sequence in sequences]
    metric_fields = [
        "lineage", "scenario", "layer_id", "decode_steps", "first_step", "last_step",
        "top_k", "sequence_power", "adjacent_pair_count", "adjacent_overlap_mean",
        "adjacent_jaccard_mean", "adjacent_retention_mean",
    ]
    for lag in (1, 2, 4, 8):
        metric_fields.extend(
            [
                f"lag{lag}_pairs", f"lag{lag}_overlap_mean", f"lag{lag}_jaccard_mean",
                f"lag{lag}_retention_mean",
            ]
        )
    metric_fields.extend(
        [
            "cumulative_distinct_experts", "cumulative_distinct_by_step_json",
            "top1_frequency_concentration", "top4_frequency_concentration",
            "exact_set_repeat_count", "step_topk_sizes_json", "exact_sets_by_step_json",
            "per_expert_selected_steps_json", "per_expert_inter_arrivals_json",
            "per_expert_reused_within_1_fraction_json",
            "per_expert_reused_within_2_fraction_json",
            "per_expert_reused_within_4_fraction_json",
            "per_expert_reused_within_8_fraction_json",
            "per_expert_longest_absence_gap_json",
        ]
    )
    write_tsv(output / "TEMPORAL_SET_METRICS.tsv", metric_rows, metric_fields)

    rng = random.Random(SEED)
    controls = [shuffle_control(sequence, rng) for sequence in sequences]
    control_document = {
        "schema_version": 1,
        "seed": SEED,
        "permutations_per_sequence": PERMUTATIONS,
        "null_construction": (
            "Randomly permute whole decode-step top-k sets; preserve each set, marginal expert "
            "frequency, and within-step co-selection; destroy only observed step ordering."
        ),
        "quantile_definition": "R-7 linear interpolation over 1000 permutation values",
        "interpretation_boundary": (
            "Descriptive control only; interval position is not a p-value, significance test, "
            "causal claim, cache claim, or timing claim."
        ),
        "sequences": controls,
    }
    write_text(output / "MARGINAL_PRESERVING_SHUFFLE_CONTROL.json", pretty_json(control_document))

    q30_metrics = [row for row in metric_rows if row["lineage"] == "Q30"]
    q30_controls = [row for row in controls if row["lineage"] == "Q30"]
    olmoe_metric = next(row for row in metric_rows if row["lineage"] == "OLMOE")
    olmoe_control = next(row for row in controls if row["lineage"] == "OLMOE")
    q30_above = sum(
        row["descriptive_interval_position"]["jaccard"] == "ABOVE_SHUFFLE_P95"
        for row in q30_controls
    )
    q30_within = sum(
        row["descriptive_interval_position"]["jaccard"] == "WITHIN_SHUFFLE_P05_P95"
        for row in q30_controls
    )
    q30_below = len(q30_controls) - q30_above - q30_within

    cross_md = f"""# Cross-lineage comparability

## Result

`TEMPORAL_AUTHORITY_INSUFFICIENT_CROSS_MODEL`

| Pair / scope | Classification | Reason |
|---|---|---|
| Q30 per-layer vs OLMoE layer 1 | `PARTIAL_COMPARABLE` | Both have explicit top-k set sequences and identical set-metric definitions, but Q30 has 4 steps across 48 layers while OLMoE has 32 steps for one layer. Horizon and authority coverage differ, so no locality ranking is valid. |
| Q30 vs DeepSeek | `NOT_COMPARABLE` | DeepSeek has one explicit routing state and no temporal sequence. |
| OLMoE vs DeepSeek | `NOT_COMPARABLE` | DeepSeek has one explicit routing state and no temporal sequence. |
| Three-lineage temporal conclusion | `NOT_COMPARABLE` | The three lineages do not share a common multi-step authority level. |

No cross-lineage row qualifies as `SUPPORTED_COMPARABLE`. Q30 supplies a full-model explicit sequence but only four steps (`LOW_TEMPORAL_POWER`). OLMoE supplies a 32-step explicit sequence but only for layer 1. DeepSeek supplies only one state. These asymmetries are authority limitations, not evidence that one model has more or less temporal locality.

The screen therefore reports each supported scope separately and does not order the models by locality.
"""
    write_text(output / "CROSS_LINEAGE_COMPARABILITY.md", cross_md)

    plan_md = """# Minimal routing capture plan (not executed)

This plan exists because current authority is insufficient for a three-lineage temporal comparison. It requires separate user authorization before any node109/GPU execution.

## Goal

Capture 32 continuous natural-routing decode steps for each lineage, preferably reusing its accepted S2 input, model revision, prompt/token authority, seed, and runtime environment. Capture all MoE layers when an all-layer router hook has negligible overhead; do not drop to one target layer merely to reduce storage.

For every `(decode_step, layer_id)` record, persist:

- ordered top-k expert IDs and route weights;
- router-input SHA-256 and router-logits SHA-256;
- next-token ID;
- model ID/revision, input authority, zero/one-based decode convention, and seed.

At run level, persist the exact input-token checksum, generated-token checksum, software/runtime identity, status, immutable destination path, file SHA-256 manifest, and positive catalog/transfer receipt.

## Validation gates

1. Exactly 32 unique consecutive decode steps.
2. Every expected MoE layer appears exactly once per step.
3. Every top-k has the configured size, legal IDs, no duplicates, and matching route-weight length.
4. Router-input/logit hashes and token bindings are present for every record.
5. Routing is natural: no forced expert and no model modification.
6. Two CPU-side parsers independently reproduce record counts and canonical sequence hashes before admission.

## Explicit non-goals

No NVBit, NCU, SASS trace, model download, weight copy, forced routing, cache/TLB mechanism, LRU simulation, or timing claim. NSYS is unnecessary unless a later authority review specifically requires launch identity. This document authorizes no capture by itself.
"""
    write_text(output / "MINIMAL_ROUTING_CAPTURE_PLAN.md", plan_md)

    olmoe_actual_overlap = olmoe_control["actual"]["mean_adjacent_overlap"]
    olmoe_actual_jaccard = olmoe_control["actual"]["mean_adjacent_jaccard"]
    olmoe_shuffle_overlap = olmoe_control["shuffle"]["mean_adjacent_overlap"]
    olmoe_shuffle_jaccard = olmoe_control["shuffle"]["mean_adjacent_jaccard"]
    interpretation_md = f"""# Scientific interpretation

## Authority result

- Q30: `FULL_MODEL_EXPLICIT_SEQUENCE`, 48 layers × 4 decode steps, top-8. The node164 semantic receipt contains explicit IDs and token bindings; its committed summary is hash-only. Four steps are labeled `LOW_TEMPORAL_POWER`.
- DeepSeek: `SINGLE_STATE_ONLY`, layer 1, one top-6 state. No multi-step accepted/durable routing sequence was found, so no temporal metric is computed.
- OLMoE: `SINGLE_LAYER_EXPLICIT_SEQUENCE`, layer 1 × 32 consecutive decode steps, natural top-8 with weights, router input/logit hashes, and token bindings. V34 is an ancestor of accepted V40 and its routing SHA matches the V34 checksum manifest.

## Descriptive temporal result

For OLMoE layer 1, actual mean adjacent overlap is `{olmoe_actual_overlap:.6f}` and mean adjacent Jaccard is `{olmoe_actual_jaccard:.6f}`. The 1,000-permutation marginal-preserving shuffle distributions are:

- overlap: median `{olmoe_shuffle_overlap['median']:.6f}`, p05 `{olmoe_shuffle_overlap['p05']:.6f}`, p95 `{olmoe_shuffle_overlap['p95']:.6f}`;
- Jaccard: median `{olmoe_shuffle_jaccard['median']:.6f}`, p05 `{olmoe_shuffle_jaccard['p05']:.6f}`, p95 `{olmoe_shuffle_jaccard['p95']:.6f}`.

Its descriptive interval position is `{olmoe_control['descriptive_interval_position']['jaccard']}`. The observed ordering therefore does not resolve extra adjacent-set correlation beyond this marginal-preserving control. This is a bounded descriptive non-detection, not proof that the generating process has no temporal dependence, and it does not establish causality or statistical significance.

Across Q30's 48 four-step layer sequences, Jaccard interval positions are: above p95 `{q30_above}`, within p05–p95 `{q30_within}`, below p05 `{q30_below}`. Because each sequence has only three adjacent pairs, these are low-power diagnostics and are not promoted into a Q30 temporal-locality conclusion. The mean actual Q30 adjacent Jaccard across layers is `{mean(row['adjacent_jaccard_mean'] for row in q30_metrics):.6f}`.

## Boundaries

Frequency locality is not temporal locality. Temporal set overlap is not a full-model cache opportunity. A single-layer expert-ID sequence is not cache-line reuse distance, L2 transaction order, hit rate, or timing benefit. Expert IDs are always interpreted as `(layer_id, expert_id)`; IDs are never mixed across layers. Route rank is not treated as kernel call order.

No LRU/cache simulator or expert-object reuse-distance proxy was run. Although Q30 has full-layer IDs, its four-step horizon is too short for a capacity conclusion; OLMoE lacks the other layers and ordinary traffic. No 4 MiB L2 mapping or performance claim is made.

## Decision

The OLMoE authority/integrity screen and bounded analysis complete as `OLMOE_SINGLE_LAYER_TEMPORAL_SCREEN_PASS`; “pass” means the sequence is valid and the screen ran, not that a positive temporal signal was found. The observed OLMoE result lies within the shuffle p05–p95 interval. The requested cross-model answer is `TEMPORAL_AUTHORITY_INSUFFICIENT_CROSS_MODEL` because DeepSeek lacks a sequence and Q30 has only four steps.
"""
    write_text(output / "SCIENTIFIC_INTERPRETATION.md", interpretation_md)

    final_decision = {
        "schema_version": 1,
        "decision_label": "TEMPORAL_AUTHORITY_INSUFFICIENT_CROSS_MODEL",
        "bounded_screen_label": "OLMOE_SINGLE_LAYER_TEMPORAL_SCREEN_PASS",
        "bounded_signal_assessment": "NO_EXTRA_ORDERING_SIGNAL_RESOLVED_BY_DESCRIPTIVE_CONTROL",
        "question_answer": (
            "The available OLMoE layer-1 ordering does not resolve extra adjacent-set correlation "
            "beyond a marginal-preserving shuffle; Q30 is low-power and DeepSeek has no sequence, "
            "so current authority cannot support a three-lineage conclusion."
        ),
        "authority": {
            "Q30": {
                "classification": "FULL_MODEL_EXPLICIT_SEQUENCE",
                "decode_steps": 4,
                "layers": 48,
                "power": "LOW_TEMPORAL_POWER",
            },
            "DEEPSEEK": {
                "classification": "SINGLE_STATE_ONLY",
                "decode_steps": 1,
                "layers": 1,
                "temporal_analysis": "NOT_ALLOWED",
            },
            "OLMOE": {
                "classification": "SINGLE_LAYER_EXPLICIT_SEQUENCE",
                "decode_steps": 32,
                "layers": 1,
                "temporal_analysis": "DESCRIPTIVE_SCREEN_COMPLETE",
            },
        },
        "olmoe_layer1": {
            "actual_mean_adjacent_overlap": olmoe_actual_overlap,
            "actual_mean_adjacent_jaccard": olmoe_actual_jaccard,
            "shuffle_overlap": olmoe_shuffle_overlap,
            "shuffle_jaccard": olmoe_shuffle_jaccard,
            "descriptive_interval_position": olmoe_control["descriptive_interval_position"],
            "cumulative_distinct_experts": olmoe_metric["cumulative_distinct_experts"],
            "exact_set_repeat_count": olmoe_metric["exact_set_repeat_count"],
        },
        "cross_lineage_comparability": {
            "Q30_vs_OLMOE": "PARTIAL_COMPARABLE",
            "Q30_vs_DEEPSEEK": "NOT_COMPARABLE",
            "DEEPSEEK_vs_OLMOE": "NOT_COMPARABLE",
            "three_lineage": "NOT_COMPARABLE",
        },
        "claims_not_made": [
            "MOE_CACHE_OPPORTUNITY_PROVEN",
            "MOE_L2_OPTIMIZATION_JUSTIFIED",
            "UNIVERSAL_MOE_TEMPORAL_LOCALITY",
            "cache_line_reuse_distance",
            "L2_hit_rate_or_timing_benefit",
        ],
        "gpu_work_performed": False,
        "capture_plan_executed": False,
    }
    write_text(output / "FINAL_DECISION.json", pretty_json(final_decision))

    readme_md = f"""# C16 MoE temporal routing authority screen V1

## Outcome

Primary decision: `TEMPORAL_AUTHORITY_INSUFFICIENT_CROSS_MODEL`.

The audit recovered Q30's explicit 4-step × 48-layer sequence from accepted node164 authority, confirmed DeepSeek remains single-state-only, and validated OLMoE's natural 32-step layer-1 sequence through the V34→V40 ancestry and checksum chain. Only explicit sequences were analyzed. No GPU work, cache simulation, or timing analysis was performed.

OLMoE's authority/integrity result is `OLMOE_SINGLE_LAYER_TEMPORAL_SCREEN_PASS`; “pass” means the bounded screen completed on valid authority, not that it found a positive signal. Its actual adjacent metrics lie within the shuffle p05–p95 intervals. It must not be generalized to full-model cache behavior. Q30 is explicitly `LOW_TEMPORAL_POWER`.

## Review order

1. `TEMPORAL_AUTHORITY_AUDIT.tsv`
2. `CROSS_LINEAGE_COMPARABILITY.md`
3. `SCIENTIFIC_INTERPRETATION.md`
4. `FINAL_DECISION.json`
5. Metric/control details in `EXPLICIT_SEQUENCE_INDEX.tsv`, `TEMPORAL_SET_METRICS.tsv`, and `MARGINAL_PRESERVING_SHUFFLE_CONTROL.json`
6. `MINIMAL_ROUTING_CAPTURE_PLAN.md` (plan only; not authorization)

## Metric definitions

- Object identity is `(layer_id, expert_id)`; expert IDs are never mixed across layers.
- Each decode step is an unordered exact top-k set. Route rank is not kernel-call order.
- Overlap is intersection cardinality; Jaccard is intersection/union; retention is intersection/k.
- Lag 1/2/4/8 uses pairs exactly that many decode steps apart and is reported only when the sequence is long enough.
- Top1/top4 frequency concentration is the share of all step selections held by the one/four most frequent experts in that layer.
- Exact-set repeats count occurrences after the first occurrence of the same unordered set.
- Per-expert reuse-within-W is the fraction of consecutive expert arrivals whose decode-step distance is at most W; experts selected once receive JSON `null`.
- Longest absence gap is the longest run of observed steps not selecting that expert, including leading/trailing boundaries.
- Shuffle quantiles use R-7 linear interpolation. Seed `{SEED}`, `{PERMUTATIONS}` permutations per sequence.

## Provenance and validation

- Base/consumer commit: `08536be9940590be101c7f5bac2117ba82056db5`.
- Q30 producer: `{Q30_COMMIT}`; explicit source SHA `{Q30_EXPECTED_SHA}`.
- DeepSeek producer: `{DEEPSEEK_COMMIT}`; routing receipt SHA `{DEEPSEEK_EXPECTED_SHA}`.
- OLMoE producer V34: `{OLMOE_V34_COMMIT}`; accepted V40: `{OLMOE_V40_COMMIT}`; routing SHA `{OLMOE_EXPECTED_SHA}`.
- Generator: `util/vm_tlb/c16/moe_temporal_routing_screen.py`.
- `SHA256SUMS` covers every review-pack file except itself.

The generator hard-fails on source SHA, ancestry, step continuity, layer coverage, top-k legality, forced routing, token binding, and router hash invariants.

Authority search covered the three accepted producer commits/review packs, the Q30 accepted node164 replay-state archive, the DeepSeek accepted node164 raw bundle and catalog binding, and node164 durable provenance/catalog locations. No Lane 4 path or partial result was read.

## Change and validation summary

This branch contains one reproducible CPU-only generator plus this ten-file review pack; no model, simulator, cache/TLB, trace, configuration, accepted authority, or handoff file is modified. The branch starts at accepted consumer commit `08536be9940590be101c7f5bac2117ba82056db5`; the stage commit is the single commit immediately above that base.

Validation consists of Python bytecode compilation, structured JSON/TSV assertions, independent `sha256sum -c`, deterministic regeneration comparison, `git diff --check`, fetch-back commit equality, and final clean-worktree verification.

## Open authority gaps

- DeepSeek has no accepted/durable multi-step explicit routing sequence.
- Q30 has all 48 layers but only four decode steps, so temporal power is low.
- OLMoE has 32 steps but only layer 1, so it cannot support full-model cache/capacity conclusions.
- `MINIMAL_ROUTING_CAPTURE_PLAN.md` is a plan only and requires fresh user authorization before any GPU work.
"""
    write_text(output / "README.md", readme_md)

    sum_files = sorted(path for path in output.iterdir() if path.is_file() and path.name != "SHA256SUMS")
    checksum_lines = [f"{sha256_bytes(path.read_bytes())}  {path.name}" for path in sum_files]
    write_text(output / "SHA256SUMS", "\n".join(checksum_lines) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--q30-source",
        type=Path,
        default=Path(
            "/root/share/mnt164/huangrulin/c16_ai_workload/provenance/"
            "qwen3_30b_replay_states/ad44e777bcd18fa416d9da3bd8f70d33ebb85d39/"
            "Q30_S2_STREAM_V1_20260917T001000Z/semantic/SEMANTIC_RUN_RECEIPT.json"
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "docs/vm_tlb/review_packs/C16_MOE_TEMPORAL_ROUTING_AUTHORITY_SCREEN_V1"
        ),
    )
    args = parser.parse_args()
    repo = args.repo_root.resolve()
    output = args.output if args.output.is_absolute() else repo / args.output
    build(repo, args.q30_source, output)


if __name__ == "__main__":
    main()
