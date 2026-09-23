# CODEX 174-new — C16 E1 Semantic NCU Consumer Prep V1

## Mode

GOAL MODE / CPU-side parallel preparation

Suggested branch:

`hrl/c16-e1-semantic-ncu-consumer-prep-174new-v1`

No GPU work.
Do not modify node164 accepted raw/catalog data.

## Read first

Fetch and verify:

`hrl/c16-e1-semantic-ncu-handoff-v1`

Read completely:

1. `docs/vm_tlb/chatgpt_handoff/c16/e1_semantic_ncu_v1/CURRENT_STATE.md`
2. `docs/vm_tlb/chatgpt_handoff/c16/e1_semantic_ncu_v1/E1_SEMANTIC_NCU_DESIGN_V1.md`
3. this file

Accepted E1 consumer:
`hrl/c16-e1-clean-baseline-consumer-prep-174new-v1@59ddb8ba2a33ef12b73bfc859f3a994e0b4ef4ca`

## Stage 1 — independent semantic-selector contract audit

Audit and freeze the consumer interpretation:

- scientific unit = exact semantic `up_proj` module invocation;
- AWQ may launch multiple GPU kernels;
- all kernels inside a uniquely qualified semantic range belong to the module-level traffic total;
- warmup/other invocations must be excluded;
- additive byte/event metrics may be summed;
- percentages/utilization are not blindly summed;
- no cache/TLB causality is inferred.

Create:
`SEMANTIC_SELECTOR_DESIGN_AUDIT.json`

## Stage 2 — build NCU parser/aggregator

Build a CPU-side parser for expected NCU CSV/raw exports.

Requirements:

- preserve exact metric names and units;
- group by semantic point / range / kernel;
- fail closed on missing/ambiguous range identity;
- sum only metrics explicitly classified additive;
- keep non-additive metrics per kernel;
- compute semantic-module traffic totals;
- compute normalization by input/output elements and weight-storage bytes when supplied.

Create an explicit metric aggregation policy:
`METRIC_AGGREGATION_CONTRACT.json`

Do not hardcode producer scientific values.

## Stage 3 — synthetic tests

Create fixtures covering:

- one RAW kernel in one semantic range;
- multi-kernel AWQ range;
- warmup kernel outside range;
- duplicate/ambiguous target range -> FAIL;
- unit mismatch for same metric -> FAIL;
- additive bytes aggregation;
- non-additive utilization not summed.

Persist:
`CONSUMER_TESTS.tsv`

## Stage 4 — pre-register comparisons

Independent consumer must later compute:

- M1 AWQ/RAW traffic ratios
- M256 AWQ/RAW traffic ratios
- M256/M1 traffic scaling by implementation
- timing-vs-traffic directional comparison

It must not reinterpret timing values as profiler traffic.

Prepare expected review pack:

`docs/vm_tlb/review_packs/C16_E1_SEMANTIC_NCU_CONSUMER_174NEW_V1/`

## Stage 5 — consume producer once if available

Expected producer:

`hrl/c16-e1-semantic-ncu-109-v1`

After prep is complete, fetch remote once.

If producer is complete:

- verify producer HEAD/review pack;
- independently audit standalone replay identity/output SHA;
- independently verify selector qualification;
- independently recompute semantic-module additive sums;
- verify exact metric names/units;
- verify normalizations and traffic ratios;
- confirm no unsupported cache/TLB causal claim;
- write final consumer review pack;
- commit/push/remote verify/clean;
- STOP.

If producer is not complete:

- commit/push prep;
- remote verify/clean;
- STOP with:
  `READY_FOR_E1_SEMANTIC_NCU_109`

Do not idle/poll.

## Producer-unresolved case

If producer closes as:
`SEMANTIC_NCU_SELECTOR_UNRESOLVED_V2`

then consumer should independently verify that the failure is genuine and that no traffic was fabricated. Do not invent a workaround on 174-new.

## Solve-and-continue

Routine parser/schema/Git issues:
solve and continue.

STOP early only for a genuine contradiction in the semantic selector/aggregation contract.
