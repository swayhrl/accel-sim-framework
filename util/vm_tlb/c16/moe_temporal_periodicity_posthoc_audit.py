#!/usr/bin/env python3
"""CPU-only post-hoc periodicity audit for accepted OLMoE V34 routing."""

from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
import math
import random
import subprocess
from pathlib import Path
from typing import Any, Iterable


V1_COMMIT = "0017527afba6861a4a0cfee95cce7b2a0397f284"
V34_COMMIT = "ab26365dc663268b0799818db6687ed466e8c925"
V40_COMMIT = "85563ec6f55a0ad743d21483aa49c24fdb5cf3bf"
V34_ROOT = "docs/vm_tlb/review_packs/C16_OLMOE_S2_PRODUCER_109_V34"
ROUTING_PATH = f"{V34_ROOT}/NATURAL_TOP8_ROUTING.json"
STATE_PATH = f"{V34_ROOT}/S2_STATE_RECEIPT.json"
INPUT_PATH = f"{V34_ROOT}/S2_INPUT_AUTHORITY.json"
RUNTIME_PATH = f"{V34_ROOT}/RUNTIME_CAPACITY_RECEIPT.json"
ASSET_PATH = f"{V34_ROOT}/ASSET_RUNTIME_RECEIPT.json"
DATAFLOW_PATH = f"{V34_ROOT}/MOE_RUNTIME_DATAFLOW.json"
SPEC_PATH = (
    "docs/vm_tlb/chatgpt_handoff/c16/olmoe_s2_producer_v34/"
    "CODEX_109_OLMOE_S2_PRODUCER_V34.md"
)
V40_REPLAY_PATH = "util/vm_tlb/c16/olmoe_v40_marked_replay.py"
EXPECTED_ROUTING_SHA256 = "d973b1f2915bb7d5bfd47f0b83b1a8c19106f51ecacfe89ba359ab3a6a3207c3"
SEED = 20260928
PERMUTATIONS = 1000
LAGS = range(1, 17)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob(repo: Path, commit: str, path: str) -> bytes:
    return subprocess.run(
        ["git", "show", f"{commit}:{path}"],
        cwd=repo,
        check=True,
        stdout=subprocess.PIPE,
    ).stdout


def git_json(repo: Path, commit: str, path: str) -> Any:
    return json.loads(git_blob(repo, commit, path))


def mean(values: Iterable[float]) -> float | None:
    values = list(values)
    return sum(values) / len(values) if values else None


def quantile(values: list[float], probability: float) -> float:
    require(bool(values), "quantile requires non-empty values")
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    fraction = position - lower
    return ordered[lower] * (1.0 - fraction) + ordered[upper] * fraction


def summary(values: list[float]) -> dict[str, Any]:
    if not values:
        return {"count": 0, "min": None, "p05": None, "median": None, "mean": None, "p95": None, "max": None}
    return {
        "count": len(values),
        "min": min(values),
        "p05": quantile(values, 0.05),
        "median": quantile(values, 0.50),
        "mean": mean(values),
        "p95": quantile(values, 0.95),
        "max": max(values),
    }


def lag_metrics(records: list[dict[str, Any]], lag: int) -> dict[str, Any]:
    pairs = list(zip(records, records[lag:]))
    overlaps: list[float] = []
    jaccards: list[float] = []
    retentions: list[float] = []
    for left, right in pairs:
        left_set = set(left["natural_top8_ids"])
        right_set = set(right["natural_top8_ids"])
        intersection = len(left_set & right_set)
        overlaps.append(float(intersection))
        jaccards.append(intersection / len(left_set | right_set))
        retentions.append(intersection / len(left_set))
    return {
        "lag": lag,
        "pair_count": len(pairs),
        "mean_overlap": mean(overlaps),
        "mean_jaccard": mean(jaccards),
        "mean_retention": mean(retentions),
    }


def write_tsv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    def render(value: Any) -> Any:
        if value is None:
            return "UNKNOWN"
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, float):
            return f"{value:.9f}"
        return value

    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: render(row.get(field)) for field in fields})


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def pretty_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def pair_descriptor(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    left_ids = left["natural_top8_ids"]
    right_ids = right["natural_top8_ids"]
    left_set = set(left_ids)
    right_set = set(right_ids)
    intersection = len(left_set & right_set)
    unordered_equal = left_set == right_set
    return {
        "step_t": left["decode_step"],
        "step_t11": right["decode_step"],
        "intersection": intersection,
        "jaccard": intersection / len(left_set | right_set),
        "exact_set_equal": unordered_equal,
        "near_repeat": (not unordered_equal) and intersection >= 7,
        "next_token_id_t": left["next_token_id"],
        "next_token_id_t11": right["next_token_id"],
        "next_token_equal": left["next_token_id"] == right["next_token_id"],
        "router_input_sha_equal": left["mlp_router_input"]["sha256"] == right["mlp_router_input"]["sha256"],
        "router_logits_sha_equal": left["router_logits_sha256"] == right["router_logits_sha256"],
        "ordered_topk_equal": left_ids == right_ids,
        "unordered_set_equal": unordered_equal,
    }


def association_group(pairs: list[tuple[dict[str, Any], dict[str, Any]]]) -> dict[str, Any]:
    jaccards: list[float] = []
    overlaps: list[float] = []
    exact = 0
    ordered = 0
    for left, right in pairs:
        descriptor = pair_descriptor(left, right)
        jaccards.append(descriptor["jaccard"])
        overlaps.append(float(descriptor["intersection"]))
        exact += int(descriptor["unordered_set_equal"])
        ordered += int(descriptor["ordered_topk_equal"])
    return {
        "pair_count": len(pairs),
        "jaccard": summary(jaccards),
        "overlap": summary(overlaps),
        "unordered_exact_set_equal_count": exact,
        "ordered_topk_equal_count": ordered,
    }


def build(repo: Path, output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "merge-base", "--is-ancestor", V34_COMMIT, V40_COMMIT], cwd=repo, check=True)

    routing_bytes = git_blob(repo, V34_COMMIT, ROUTING_PATH)
    require(sha256(routing_bytes) == EXPECTED_ROUTING_SHA256, "V34 routing SHA mismatch")
    routing = json.loads(routing_bytes)
    state = git_json(repo, V34_COMMIT, STATE_PATH)
    input_authority = git_json(repo, V34_COMMIT, INPUT_PATH)
    runtime = git_json(repo, V34_COMMIT, RUNTIME_PATH)
    asset = git_json(repo, V34_COMMIT, ASSET_PATH)
    dataflow = git_json(repo, V34_COMMIT, DATAFLOW_PATH)
    spec_text = git_blob(repo, V34_COMMIT, SPEC_PATH).decode("utf-8")

    require(routing["forced_expert_id"] is False, "routing must be natural")
    require(routing["status"] == "PASS_NATURAL_TOP8", "routing status mismatch")
    require(state["status"] == "PASS_NATIVE_S2_D32", "state receipt status mismatch")
    records = routing["repeat_decode_records"]
    require(len(records) == 32, "expected 32 records")
    require([record["decode_step"] for record in records] == list(range(1, 33)), "steps must be 1..32")
    for record in records:
        ids = record["natural_top8_ids"]
        require(len(ids) == 8 and len(set(ids)) == 8, "invalid top-8")
        require(len(record["route_weights"]) == 8, "route-weight length mismatch")
        require(isinstance(record["next_token_id"], int), "next-token missing")
        require(len(record["mlp_router_input"]["sha256"]) == 64, "router-input SHA missing")
        require(len(record["router_logits_sha256"]) == 64, "router-logits SHA missing")

    spectrum = [lag_metrics(records, lag) for lag in LAGS]
    write_tsv(
        output / "LAG_SPECTRUM.tsv",
        spectrum,
        ["lag", "pair_count", "mean_overlap", "mean_jaccard", "mean_retention"],
    )

    shuffle_rows: list[dict[str, Any]] = []
    for actual in spectrum:
        lag = actual["lag"]
        rng = random.Random(SEED)
        overlap_values: list[float] = []
        jaccard_values: list[float] = []
        retention_values: list[float] = []
        for _ in range(PERMUTATIONS):
            shuffled = list(records)
            rng.shuffle(shuffled)
            metrics = lag_metrics(shuffled, lag)
            overlap_values.append(metrics["mean_overlap"])
            jaccard_values.append(metrics["mean_jaccard"])
            retention_values.append(metrics["mean_retention"])
        overlap_dist = summary(overlap_values)
        jaccard_dist = summary(jaccard_values)
        retention_dist = summary(retention_values)
        shuffle_rows.append(
            {
                "lag": lag,
                "pair_count": actual["pair_count"],
                "seed": SEED,
                "permutations": PERMUTATIONS,
                "actual_mean_overlap": actual["mean_overlap"],
                "shuffle_overlap_p05": overlap_dist["p05"],
                "shuffle_overlap_median": overlap_dist["median"],
                "shuffle_overlap_p95": overlap_dist["p95"],
                "actual_mean_jaccard": actual["mean_jaccard"],
                "shuffle_jaccard_p05": jaccard_dist["p05"],
                "shuffle_jaccard_median": jaccard_dist["median"],
                "shuffle_jaccard_p95": jaccard_dist["p95"],
                "actual_mean_retention": actual["mean_retention"],
                "shuffle_retention_p05": retention_dist["p05"],
                "shuffle_retention_median": retention_dist["median"],
                "shuffle_retention_p95": retention_dist["p95"],
                "jaccard_interval_position": (
                    "ABOVE_SHUFFLE_P95"
                    if actual["mean_jaccard"] > jaccard_dist["p95"]
                    else "BELOW_SHUFFLE_P05"
                    if actual["mean_jaccard"] < jaccard_dist["p05"]
                    else "WITHIN_SHUFFLE_P05_P95"
                ),
            }
        )
    shuffle_fields = [
        "lag", "pair_count", "seed", "permutations",
        "actual_mean_overlap", "shuffle_overlap_p05", "shuffle_overlap_median", "shuffle_overlap_p95",
        "actual_mean_jaccard", "shuffle_jaccard_p05", "shuffle_jaccard_median", "shuffle_jaccard_p95",
        "actual_mean_retention", "shuffle_retention_p05", "shuffle_retention_median", "shuffle_retention_p95",
        "jaccard_interval_position",
    ]
    write_tsv(output / "LAG_SHUFFLE_CONTROL.tsv", shuffle_rows, shuffle_fields)

    period11_rows = [pair_descriptor(records[index], records[index + 11]) for index in range(21)]
    period_fields = [
        "step_t", "step_t11", "intersection", "jaccard", "exact_set_equal", "near_repeat",
        "next_token_id_t", "next_token_id_t11", "next_token_equal", "router_input_sha_equal",
        "router_logits_sha_equal", "ordered_topk_equal", "unordered_set_equal",
    ]
    write_tsv(output / "PERIOD11_PAIR_AUDIT.tsv", period11_rows, period_fields)

    all_pairs = list(itertools.combinations(records, 2))
    same_token_pairs = [pair for pair in all_pairs if pair[0]["next_token_id"] == pair[1]["next_token_id"]]
    different_token_pairs = [pair for pair in all_pairs if pair[0]["next_token_id"] != pair[1]["next_token_id"]]
    lag11_pairs = [(records[index], records[index + 11]) for index in range(21)]
    lag11_same = [pair for pair in lag11_pairs if pair[0]["next_token_id"] == pair[1]["next_token_id"]]
    lag11_different = [pair for pair in lag11_pairs if pair[0]["next_token_id"] != pair[1]["next_token_id"]]
    token_association = {
        "schema_version": 1,
        "status": "POST_HOC_DIAGNOSTIC_ONLY",
        "conditioning_variable": "next_token_id from the same decode-step record",
        "causal_boundary": (
            "Routing occurs before the recorded next token is generated. next_token_id is an "
            "associated output variable, not a causal routing input label."
        ),
        "all_unordered_step_pairs": {
            "total_pair_count": len(all_pairs),
            "same_next_token": association_group(same_token_pairs),
            "different_next_token": association_group(different_token_pairs),
        },
        "lag11_pairs": {
            "total_pair_count": len(lag11_pairs),
            "same_next_token": association_group(lag11_same),
            "different_next_token": association_group(lag11_different),
        },
        "actual_input_token": {
            "status": "UNKNOWN",
            "reason": (
                "V34 routing records do not store current-step input_token_id and the accepted "
                "generation runner/KV-transition semantics are not archived. Predecessor next-token "
                "values are therefore not promoted to input-token authority."
            ),
        },
    }
    write_text(output / "TOKEN_ASSOCIATION.json", pretty_json(token_association))

    lag11 = next(row for row in shuffle_rows if row["lag"] == 11)
    exact_count = sum(row["unordered_set_equal"] for row in period11_rows)
    ordered_count = sum(row["ordered_topk_equal"] for row in period11_rows)
    near_count = sum(row["near_repeat"] for row in period11_rows)
    same_token_count = sum(row["next_token_equal"] for row in period11_rows)
    same_input_sha_count = sum(row["router_input_sha_equal"] for row in period11_rows)
    same_logits_sha_count = sum(row["router_logits_sha_equal"] for row in period11_rows)
    above_p95_lags = [row["lag"] for row in shuffle_rows if row["jaccard_interval_position"] == "ABOVE_SHUFFLE_P95"]

    changed_paths = subprocess.run(
        ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", V34_COMMIT],
        cwd=repo,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    ).stdout.splitlines()
    v34_runner_committed = any(path.startswith("util/") or path.endswith(".py") for path in changed_paths)
    require(not v34_runner_committed, "unexpected committed V34 runner found; update provenance audit")
    require("S2_TEXT = B1/T2048/D32" in spec_text, "V34 scenario requirement missing")
    require("Execute exact native S2 with the frozen IDs" in spec_text, "V34 execution requirement missing")
    v40_replay = git_blob(repo, V40_COMMIT, V40_REPLAY_PATH).decode("utf-8")
    require("experts[58].down_proj(value)" in v40_replay, "V40 replay identity changed")

    provenance_md = f"""# Generation provenance audit

Status: `POST_HOC_DIAGNOSTIC_ONLY`

## Evidence boundary

The accepted V34 commit `{V34_COMMIT}` contains the 18-file review pack but no producer runner/source file. Its commit delta contains no `util/` or Python runner. The exact 32-step generation command, loop, and cache transitions are not archived in the accepted commit. This negative finding prevents reconstruction by assumption.

The V34 specification requires `S2_TEXT = B1/T2048/D32` and says to execute exact native S2 with frozen IDs. The receipts establish:

- `S2_STATE_RECEIPT.json`: 32 decode steps, layer 1, `no_synthetic_state=true`, native S2 status PASS;
- `NATURAL_TOP8_ROUTING.json`: one 32-record array with unique consecutive steps 1–32, natural routing, per-step top-8/weights/router-input SHA/router-logits SHA/next token;
- `S2_INPUT_AUTHORITY.json`: 2,048 frozen prompt IDs, no retokenization after freeze;
- `ASSET_RUNTIME_RECEIPT.json` and `RUNTIME_CAPACITY_RECEIPT.json`: a hash-closed model replica and native BF16 runtime family;
- `MOE_RUNTIME_DATAFLOW.json`: observed per-expert native path, but not the generation loop.

The accepted V40 descendant's `olmoe_v40_marked_replay.py` is a later single-module replay: it loads `expert58_d32_input.pt` and calls only `experts[58].down_proj(value)`. It did not generate V34's 32 routing records and cannot fill the missing generation semantics.

## Question-by-question audit

| Question | Finding | Evidence / limitation |
|---|---|---|
| One continuous autoregressive generation? | `UNRESOLVED` | Required scenario and consecutive records are consistent with one run, but the actual runner/session receipt is absent. |
| Per-step model call or rematerialization? | `UNRESOLVED` | Runtime/model residency is recorded; per-step call/materialization behavior is not. |
| KV cache continuous? | `UNRESOLVED` | No cache object identity, length progression, or runner code is archived. |
| State reset between steps? | `UNRESOLVED` | No reset log or loop source exists in accepted authority. |
| Cyclic input or fixed-token injection? | `UNRESOLVED` | No input-token-per-step field or runner code. The next-token cycle is output association, not proof of injection. |
| Sampling vs greedy? | `UNRESOLVED` | No `do_sample`, argmax, temperature, or generation-config receipt. |
| Seed? | `UNRESOLVED` | No generation seed in V34 receipts. The audit shuffle seed is unrelated. |
| EOS handling? | `UNRESOLVED` | EOS ID/check/ignore behavior is not recorded. |
| `max_new_tokens`? | `EFFECTIVE_32_STEPS_ONLY` | Exactly 32 steps are recorded; the runner parameter and early-stop policy are absent. |
| Stopping criteria? | `UNRESOLVED` | No runner/config evidence. |
| Hook perturbation? | `UNRESOLVED` | Router values are recorded and state is labeled non-synthetic, but hook source and perturbation validation are absent. |
| One run or stitched states? | `CONSISTENT_WITH_SINGLE_RUN_NOT_PROVEN` | One artifact has consecutive steps 1–32, but lacks a run ID, timestamps, command, and cache/session binding per record. |

## Period-11 origin assessment

At lag 11, `{same_token_count}` of 21 pairs share the same recorded next token, while router-input SHA equality is `{same_input_sha_count}` and router-logits SHA equality is `{same_logits_sha_count}`. Thus this is not exact hidden/router-state replay. The strong routing-set repetition is associated with output-token repetition, but the missing runner prevents deciding whether the token cycle arose from genuine autoregressive content behavior or capture/replay methodology.

Origin classification: `POSTHOC_PERIOD11_ORIGIN_UNRESOLVED`.
"""
    write_text(output / "GENERATION_PROVENANCE_AUDIT.md", provenance_md)

    interpretation_md = f"""# Scientific interpretation

Status: `POST_HOC_DIAGNOSTIC_ONLY`. This addendum was motivated after inspection of V1 and is not a preregistered positive result. V1 remains unchanged with primary decision `TEMPORAL_AUTHORITY_INSUFFICIENT_CROSS_MODEL`.

## Exact recompute

The complete lag 1–16 spectrum is reported, not only lag 11. Lag 11 has mean overlap `{lag11['actual_mean_overlap']:.6f}`, mean Jaccard `{lag11['actual_mean_jaccard']:.6f}`, and mean retention `{lag11['actual_mean_retention']:.6f}` over 21 pairs. Its whole-step shuffle Jaccard p05/median/p95 is `{lag11['shuffle_jaccard_p05']:.6f}` / `{lag11['shuffle_jaccard_median']:.6f}` / `{lag11['shuffle_jaccard_p95']:.6f}`. The actual value is `ABOVE_SHUFFLE_P95`.

Across period-11 pairs, unordered exact-set repeats are `{exact_count}`, ordered top-k repeats are `{ordered_count}`, and non-exact near repeats (7-of-8 or better) are `{near_count}`. Same-next-token pairs are `{same_token_count}` of 21. Router-input and router-logits SHA equality counts are `{same_input_sha_count}` and `{same_logits_sha_count}`, respectively.

Lags whose actual mean Jaccard is above their own shuffle p95 are `{above_p95_lags}`. This full-spectrum disclosure prevents presenting lag 11 without its neighboring/control context. The permutation interval is descriptive; it is not a preregistered significance test or causal estimate.

## Token association and origin

Same-next-token pairs have a different expert-set Jaccard distribution from different-next-token pairs (see `TOKEN_ASSOCIATION.json`). Routing precedes next-token generation, so the recorded next token is an associated same-step output, not a causal input label. Current-step input tokens are `UNKNOWN` because the accepted runner/KV transition is absent; predecessor output tokens are not silently substituted.

The period-11 routing signal is confirmed in this accepted single-layer sequence and is associated with token repetition. Its origin remains unresolved between genuine generated-content repetition and capture/replay methodology. No source evidence supports labeling it a capture artifact.

## Scope boundary

Q30 has only four steps: `Q30_AUTHORITY_TOO_SHORT_FOR_PERIOD11_TEST`. DeepSeek is `SINGLE_STATE_ONLY`. Cross-model periodicity is `NOT_COMPARABLE`.

This result is not full-model temporal locality, cache opportunity, cache-line reuse distance, L2 ordering, hit rate, timing benefit, or justification for a period-11 cache policy.
"""
    write_text(output / "SCIENTIFIC_INTERPRETATION.md", interpretation_md)

    final_decision = {
        "schema_version": 1,
        "status": "POST_HOC_DIAGNOSTIC_ONLY",
        "primary_label": "POSTHOC_PERIOD11_SIGNAL_CONFIRMED",
        "qualifications": [
            "POSTHOC_PERIOD11_SIGNAL_ASSOCIATED_WITH_TOKEN_REPETITION",
            "POSTHOC_PERIOD11_ORIGIN_UNRESOLVED",
        ],
        "v1_primary_decision_unchanged": "TEMPORAL_AUTHORITY_INSUFFICIENT_CROSS_MODEL",
        "authority": {
            "producer_commit": V34_COMMIT,
            "accepted_descendant": V40_COMMIT,
            "source_path": ROUTING_PATH,
            "source_sha256": EXPECTED_ROUTING_SHA256,
            "layer": 1,
            "decode_steps": 32,
            "top_k": 8,
            "forced_routing": False,
        },
        "lag11": {
            "pair_count": 21,
            "actual_mean_overlap": lag11["actual_mean_overlap"],
            "actual_mean_jaccard": lag11["actual_mean_jaccard"],
            "actual_mean_retention": lag11["actual_mean_retention"],
            "shuffle_jaccard_p05": lag11["shuffle_jaccard_p05"],
            "shuffle_jaccard_median": lag11["shuffle_jaccard_median"],
            "shuffle_jaccard_p95": lag11["shuffle_jaccard_p95"],
            "interval_position": lag11["jaccard_interval_position"],
            "unordered_exact_set_repeat_count": exact_count,
            "ordered_topk_repeat_count": ordered_count,
            "near_repeat_count": near_count,
            "same_next_token_count": same_token_count,
            "same_router_input_sha_count": same_input_sha_count,
            "same_router_logits_sha_count": same_logits_sha_count,
        },
        "above_shuffle_p95_lags": above_p95_lags,
        "generation_origin": "UNRESOLVED",
        "cross_model_periodicity": {
            "Q30": "Q30_AUTHORITY_TOO_SHORT_FOR_PERIOD11_TEST",
            "DEEPSEEK": "SINGLE_STATE_ONLY",
            "classification": "NOT_COMPARABLE",
        },
        "claims_not_made": [
            "MOE_TEMPORAL_LOCALITY_PROVEN",
            "MOE_CACHE_OPPORTUNITY_PROVEN",
            "PERIOD11_CACHE_POLICY_JUSTIFIED",
        ],
        "gpu_work_performed": False,
        "new_capture_performed": False,
    }
    write_text(output / "FINAL_DECISION.json", pretty_json(final_decision))

    readme_md = f"""# C16 MoE temporal periodicity post-hoc audit V1

Status: `POST_HOC_DIAGNOSTIC_ONLY`

## Outcome

Primary label: `POSTHOC_PERIOD11_SIGNAL_CONFIRMED`.

Qualifications:

- `POSTHOC_PERIOD11_SIGNAL_ASSOCIATED_WITH_TOKEN_REPETITION`
- `POSTHOC_PERIOD11_ORIGIN_UNRESOLVED`

This addendum does not modify or reinterpret the V1 primary decision: `TEMPORAL_AUTHORITY_INSUFFICIENT_CROSS_MODEL`.

## Authority

- OLMoE V34 producer: `{V34_COMMIT}`
- accepted V40 descendant: `{V40_COMMIT}`
- source: `{ROUTING_PATH}`
- source SHA-256: `{EXPECTED_ROUTING_SHA256}`
- natural layer-1 top-8, 32 consecutive steps, no forced routing

No GPU, node109 access, profiler, cache simulation, new capture, new mechanism, Lane 4 result, or V1 edit was used.

## Review order

1. `LAG_SPECTRUM.tsv` — complete actual lag 1–16 spectrum
2. `LAG_SHUFFLE_CONTROL.tsv` — per-lag 1,000-permutation controls
3. `PERIOD11_PAIR_AUDIT.tsv` — all 21 `(t,t+11)` pairs
4. `TOKEN_ASSOCIATION.json`
5. `GENERATION_PROVENANCE_AUDIT.md`
6. `SCIENTIFIC_INTERPRETATION.md`
7. `FINAL_DECISION.json`
8. `SHA256SUMS`

## Definitions

- Expert objects are layer-qualified; this pack analyzes OLMoE layer 1 only.
- Top-k rank is not treated as kernel order.
- Overlap is intersection size, Jaccard is intersection/union, retention is intersection/8.
- `exact_set_equal` and `unordered_set_equal` both mean equality of unordered top-8 sets; `ordered_topk_equal` separately tests list equality.
- `near_repeat` means non-exact intersection ≥7 of 8.
- Each lag resets `Random({SEED})`, performs `{PERMUTATIONS}` whole-step permutations, and preserves every top-8 set and its marginal frequency/co-selection.
- Shuffle p05/median/p95 use R-7 linear quantiles and are descriptive, not preregistered significance thresholds.
- Token-conditioned summaries use all 496 unordered step pairs and separately report the 21 lag-11 pairs.

## Validation

The generator hard-fails on V34→V40 ancestry, source SHA, natural-routing flag, 32-step continuity, top-8 legality, route-weight length, token presence, and router SHA presence. Structured file counts, deterministic regeneration, `sha256sum -c`, `git diff --check`, fetch-back equality, and a clean final worktree are required.

Generator: `util/vm_tlb/c16/moe_temporal_periodicity_posthoc_audit.py`.
"""
    write_text(output / "README.md", readme_md)

    pack_files = sorted(path for path in output.iterdir() if path.is_file() and path.name != "SHA256SUMS")
    checksum_lines = [f"{sha256(path.read_bytes())}  {path.name}" for path in pack_files]
    write_text(output / "SHA256SUMS", "\n".join(checksum_lines) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("docs/vm_tlb/review_packs/C16_MOE_TEMPORAL_PERIODICITY_POSTHOC_AUDIT_V1"),
    )
    args = parser.parse_args()
    repo = args.repo_root.resolve()
    output = args.output if args.output.is_absolute() else repo / args.output
    build(repo, output)


if __name__ == "__main__":
    main()
