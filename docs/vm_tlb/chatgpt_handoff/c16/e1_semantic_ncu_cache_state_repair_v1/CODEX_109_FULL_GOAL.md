# CODEX 109 — C16 E1 Semantic NCU Cache-State Repair Full Goal V1

## Mode

GOAL MODE / solve-and-continue

Suggested branch:

`hrl/c16-e1-semantic-ncu-cache-state-repair-109-v1`

## Read first

Fetch and verify:

`hrl/c16-e1-semantic-ncu-cache-state-repair-handoff-v1`

Read completely:

1. `docs/vm_tlb/chatgpt_handoff/c16/e1_semantic_ncu_cache_state_repair_v1/DESIGN.md`
2. accepted V1 producer:
   `hrl/c16-e1-semantic-ncu-109-v1@9ad003fff0d42b544d3a703eca4846364c13ccb6`
3. accepted clean E1 producer:
   `hrl/c16-e1-clean-baseline-109-v1@8988d6108ff8bdca180a14cec2fe769df45b09f1`

## Goal

Repair only the profiler cache/replay context.

Do not re-run the 18-point timing matrix.
Do not change role/points/backend/input authority.

Frozen points:

- up_proj M1 RAW_FP16
- up_proj M1 AWQ_FP16_INPUT
- up_proj M256 RAW_FP16
- up_proj M256 AWQ_FP16_INPUT

## Stage 1 — audit V1 profiler mode

From preserved V1 session CSVs independently confirm:

- V1 command did not specify application replay;
- V1 command did not specify cache-control none;
- profiler__replayer_passes for every selected V1 kernel;
- exact V1 raw traffic sums.

Record V1 as:

`COLD_CACHE_KERNEL_REPLAY_DIAGNOSTIC`

Do not alter its arithmetic.

## Stage 2 — inspect installed NCU syntax

Use installed NCU 2025.1.1 help/version.

Confirm exact supported syntax for:

- application replay
- cache control none
- NVTX include
- metric selection

Do not copy an unsupported command from external docs.

## Stage 3 — V2 application-context replay

Use the existing exact standalone semantic replay and accepted NVTX ranges.

Intent:

`--replay-mode application --cache-control none`

Keep both existing warmups outside the target NVTX range.

For each point:

- rebuild identical process/module state;
- execute 2 warmups;
- profile exactly one target semantic module invocation;
- preserve accepted input SHA;
- require accepted output SHA;
- preserve exact session command;
- preserve raw report/export.

Collect only:

- l1tex__t_bytes.sum
- lts__t_bytes.sum
- dram__bytes.sum

unless installed NCU requires dependent counters automatically.

No optional utilization metrics are required in this repair.

## Stage 4 — selector/kernel qualification

For all four V2 points prove:

- correct target range;
- no warmup selected;
- no other semantic invocation selected;
- RAW expected kernel set;
- AWQ complete GEMM + reduction kernel set;
- exact input/output identity.

If application replay cannot make this unambiguous:
STOP as PROFILER_CONTEXT_REPAIR_UNRESOLVED.
Do not fall back to V1.

## Stage 5 — independent raw arithmetic inside producer

From V2 raw base/session exports compute:

- per-kernel exact byte counters;
- semantic module sums;
- M1 AWQ/RAW ratios;
- M256 AWQ/RAW ratios;
- RAW M256/M1 scaling;
- AWQ M256/M1 scaling;
- traffic shape interaction.

Record replay-pass count and session command for every point.

## Stage 6 — V1/V2 comparison

Compare V2 warmed/application-context traffic against V1 cold kernel-replay traffic.

Classify:

- SAME_DIRECTION_SIMILAR_MAGNITUDE
- SAME_DIRECTION_DIFFERENT_MAGNITUDE
- QUALITATIVE_DIRECTION_CHANGED

per metric.

Also compare V2 traffic direction with accepted native timing direction.

Do not infer cache/TLB causality.

## Stage 7 — close

Create:

`docs/vm_tlb/review_packs/C16_E1_SEMANTIC_NCU_CACHE_STATE_REPAIR_109_V1/`

with all DESIGN-required artifacts.

Update:

`docs/vm_tlb/scientific_logs/C16_LOWBIT_SHAPE_EXPLORATION_LOG.md`

Then:

SHA256SUMS -> commit -> push -> remote verify -> clean worktree -> release GPU lock -> STOP.

Forbidden:
- NVBit
- full address trace
- TLB/cache mechanism
- new shape sweep
- role reselection

Routine NCU CLI/export/parser issues are solve-and-continue.

STOP early only for:
- accepted input/output SHA mismatch;
- application replay cannot preserve semantic range identity;
- backend/runtime identity changes;
- genuine GPU/runtime corruption;
- scientific contract change.
