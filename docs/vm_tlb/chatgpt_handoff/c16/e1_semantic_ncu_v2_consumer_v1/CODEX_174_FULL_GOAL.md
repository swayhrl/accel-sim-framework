# CODEX 174-new — C16 E1 Semantic NCU V2 Independent Consumer Closure V1

## Mode

GOAL MODE / CPU-side independent verification

Suggested execution branch:

`hrl/c16-e1-semantic-ncu-v2-consumer-174new-v1`

No GPU work.
Do not modify node164 accepted authority.

## Read first

Fetch and verify:

`hrl/c16-e1-semantic-ncu-v2-consumer-handoff-v1`

Read completely:

1. this file
2. producer repair pack:
   `docs/vm_tlb/review_packs/C16_E1_SEMANTIC_NCU_CACHE_STATE_REPAIR_109_V1/`
3. hardened consumer authority:
   `hrl/c16-e1-semantic-ncu-consumer-hardening-v1@396233ca250c20be834aa0c50d2504e6017953bc`
4. prior consumer prep:
   `hrl/c16-e1-semantic-ncu-consumer-prep-174new-v1@92fa940cc7ca6e3e8eb7ca628e4d28634e05ac35`

Producer V2 authority:

`hrl/c16-e1-semantic-ncu-cache-state-repair-109-v1@8d1f62229cae15199793ba5569327cf1e83596f3`

## Goal

Independently verify the V2 application-replay/cache-control-none traffic evidence directly from producer-preserved raw NCU base/session exports.

Do **not** treat producer `TRAFFIC_SUMS.tsv`, `TRAFFIC_COMPARISON.json`, or normalized scientific summaries as calculation authority.

They are compare-only references.

## Stage 1 — raw provenance and profiler-mode audit

For each point:

- M1_RAW
- M1_AWQ
- M256_RAW
- M256_AWQ

Read directly:

- `RAW_<POINT>_BASE.csv`
- `RAW_<POINT>_SESSION.csv`
- `RAW_<POINT>_PROFILE.log`

Verify:

1. session command contains exact:
   - `--replay-mode application`
   - `--cache-control none`
   - correct `--nvtx-include <range>/`
   - exactly the three intended traffic metrics;
2. installed NCU version is 2025.1.1.0 build 35528883;
3. every selected base-CSV row reports `profiler__replayer_passes = 1`;
4. raw metric units for:
   - `l1tex__t_bytes.sum`
   - `lts__t_bytes.sum`
   - `dram__bytes.sum`
   are exactly `byte`;
5. raw NVTX push/pop column contains the expected semantic range;
6. selected kernel inventory is:
   - RAW: exactly one target kernel
   - AWQ: exactly GEMM + reduction;
7. profile PASS receipt matches accepted point input/output SHA.

Fail closed on any mismatch.

## Stage 2 — independently normalize raw NCU CSV

Build/extend a raw-NCU normalizer on 174-new.

The consumer must derive normalized semantic rows from the raw base CSV itself.

Do not copy producer `SELECTED_KERNELS.tsv` or `TRAFFIC_SUMS.tsv` into the consumer result.

For each raw selected kernel derive:

- semantic point
- range name
- range occurrence/process identity
- raw NCU ID/kernel launch identity
- kernel name
- grid/block
- exact metric name
- exact metric unit
- exact metric value

Preserve raw-row provenance:
- source filename
- source row/NCU ID
- source file SHA256

Use the hardened fail-closed behavior:
- duplicate headers -> FAIL
- NaN/Inf -> FAIL
- duplicate kernel/metric -> FAIL
- kernel-ID/name inconsistency -> FAIL
- missing additive metric on any selected kernel -> FAIL
- unit mismatch -> FAIL
- ambiguous/missing target range -> FAIL

## Stage 3 — resolve V2 metric policy from runtime evidence

For this V2 producer, independently resolve:

- `l1tex__t_bytes.sum` / byte / additive
- `lts__t_bytes.sum` / byte / additive
- `dram__bytes.sum` / byte / additive

Do not rely on the old preregistered aliases.

No non-additive utilization metrics are required in the V2 repair closure.

## Stage 4 — independent semantic-module sums

Sum additive counters over all kernels in the uniquely qualified semantic range.

Expected values below are compare-only references; calculate from raw first:

M1_RAW:
- L1 = 272187392
- L2 = 137167040
- DRAM = 138156416

M1_AWQ:
- L1 = 47284224
- L2 = 41898912
- DRAM = 640

M256_RAW:
- L1 = 417071104
- L2 = 417723360
- DRAM = 156380160

M256_AWQ:
- L1 = 1411252224
- L2 = 1266170592
- DRAM = 178195840

If independent raw recompute differs, STOP and report the mismatch.

## Stage 5 — independent ratios/interactions

From independent sums compute:

For each metric:
- M1 AWQ/RAW
- M256 AWQ/RAW
- RAW M256/M1
- AWQ M256/M1
- shape interaction ratio =
  (M256 AWQ/RAW) / (M1 AWQ/RAW)

Compare with producer only after computing independently.

Expected compare references:

L1:
- M1 = 0.17371937639198218
- M256 = 3.383720930232558
- interaction = 19.478085867620752

L2:
- M1 = 0.3054590373897403
- M256 = 3.031122300653715
- interaction = 9.923171128134786

DRAM:
- M1 = 4.6324305343879215e-06
- M256 = 1.139504141701863
- interaction = 245984.07536669614

## Stage 6 — V1/V2 independent comparison

Independently read V1 raw base/session evidence from:

`docs/vm_tlb/review_packs/C16_E1_SEMANTIC_NCU_109_V1/`

Verify:
- V1 default kernel replay;
- no explicit cache-control none;
- seven replay passes per selected kernel.

Recompute V1 traffic from raw.

Then independently classify V1 -> V2 per metric:

- SAME_DIRECTION_SIMILAR_MAGNITUDE
- SAME_DIRECTION_DIFFERENT_MAGNITUDE
- QUALITATIVE_DIRECTION_CHANGED

Use the frozen 25% similar-magnitude rule.

## Stage 7 — capacity/residency consistency check

This is a descriptive consistency check only, not a causal proof.

From accepted authority verify:

- AWQ up_proj packed state bytes =
  `35273728`
- RAW FP16 up_proj dense weight bytes =
  `3584 * 18944 * 2 = 135790592`
- device L2 size from raw NCU device attributes =
  `67108864` bytes

Record whether:
- AWQ packed state < L2 capacity
- RAW FP16 dense weight > L2 capacity

Then state only:

> the M1 V2 DRAM observation is consistent or inconsistent with a warm-cache capacity/residency hypothesis.

Do **not** upgrade this to cache causality.

## Stage 8 — scientific closure

Create:

`docs/vm_tlb/review_packs/C16_E1_SEMANTIC_NCU_V2_CONSUMER_174NEW_V1/`

At minimum:

- `RAW_PROVENANCE_AUDIT.json`
- `PROFILER_MODE_AUDIT.json`
- `RUNTIME_METRIC_POLICY.json`
- `RAW_NORMALIZED_ROWS.tsv`
- `INDEPENDENT_TRAFFIC_SUMS.tsv`
- `INDEPENDENT_TRAFFIC_COMPARISON.json`
- `V1_V2_INDEPENDENT_COMPARISON.json`
- `CAPACITY_RESIDENCY_CONSISTENCY.json`
- `PRODUCER_MATCH_CHECK.json`
- `SCIENTIFIC_INTERPRETATION.md`
- `FINAL_DECISION.json`
- `NEXT_STEP_AUTHORIZATION.json`
- `SHA256SUMS`

Update the living low-bit/shape scientific log with the independently verified V2 result.

## Claim boundary

Allowed if independently verified:

- application-replay/cache-control-none semantic traffic has a strong operator/shape association with accepted timing;
- M1 AWQ DRAM traffic is extremely small after warmup relative to RAW;
- the observation is consistent with, but does not prove, a cache-capacity/residency explanation.

Not allowed:

- cache causally explains the timing;
- TLB causes the timing;
- a specific cache mechanism is already justified;
- full trace is automatically required.

## Stop boundary

Complete all CPU-side independent verification in this one Goal.

Then:
SHA256SUMS -> commit -> push -> remote verify -> clean worktree -> STOP.

Do not start any GPU/NVBit/full-trace/mechanism work.
