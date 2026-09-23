# C16 E1 Semantic NCU Cache-State Repair V1

## Why this repair is required

Producer V1:

`hrl/c16-e1-semantic-ncu-109-v1@9ad003fff0d42b544d3a703eca4846364c13ccb6`

correctly closed:
- standalone replay identity;
- exact NVTX semantic range selection;
- RAW 1-kernel and AWQ 2-kernel composition;
- raw NCU CSV preservation;
- arithmetic aggregation of additive metrics.

However, the preserved session command line shows that V1 did **not** specify:
- `--replay-mode application`
- `--cache-control none`

Therefore Nsight Compute used its default kernel-replay/cache-control behavior.

The raw V1 CSV additionally records:

`profiler__replayer_passes = 7`

for every selected kernel.

Under Nsight Compute default behavior, GPU caches are flushed before kernel replay passes. This makes V1 traffic a valid **cold/isolated kernel-replay diagnostic**, but not a faithful measurement of the cache state seen by one naturally executed warmed semantic module invocation.

This matters especially for AWQ:
- one semantic up_proj call launches GEMM + reduction;
- under kernel replay/cache flush, the reduction kernel may not observe the cache state produced by the immediately preceding GEMM;
- summing the two cold-replay kernel counters can therefore misrepresent the native semantic-module L1/L2/DRAM traffic.

## V1 status

Do not discard V1.

Relabel its traffic evidence:

`COLD_CACHE_KERNEL_REPLAY_DIAGNOSTIC`

The arithmetic values are independently confirmed from raw CSV:

- M1 AWQ/RAW:
  - L1/TEX = 0.1737193764
  - L2 = 0.3038159794
  - DRAM = 0.2587944202
- M256 AWQ/RAW:
  - L1/TEX = 3.3837209302
  - L2 = 3.0267706296
  - DRAM = 1.1065566466

These values are correct for the V1 profiler configuration.

They must not yet be called native/warmed semantic-module traffic.

## Repair question

> Under application-managed warmup/cache state, does the accepted timing interaction still have the same L1/L2/DRAM traffic interaction?

## Required V2 profiling contract

Selected role/points remain frozen:

- up_proj M1 RAW_FP16
- up_proj M1 AWQ_FP16_INPUT
- up_proj M256 RAW_FP16
- up_proj M256 AWQ_FP16_INPUT

Use the exact same:
- canonical activation SHAs;
- standalone replay;
- accepted RAW_FP16/AWQ backends;
- NVTX semantic range names;
- output SHA gates.

### Main profiling mode

Use installed-NCU-supported application replay with application-managed cache state.

Target intent:

`--replay-mode application --cache-control none`

Keep the two existing warmup module calls outside the NVTX target range.

Thus each application replay pass rebuilds the same runtime/module state, executes the same warmups, then executes exactly one selected semantic invocation.

Before running, inspect installed NCU help and record the exact supported command syntax.

### Metrics

The repair requires only the three additive traffic metrics:

- `l1tex__t_bytes.sum`
- `lts__t_bytes.sum`
- `dram__bytes.sum`

Use exact metric names/units returned by the installed NCU.

Do not collect optional utilization metrics in the main repair unless doing so does not increase replay complexity. They are not needed for the traffic repair.

### Qualification

For every point:

1. exact input SHA matches accepted E1;
2. output SHA matches accepted E1;
3. exactly the intended semantic NVTX range is selected;
4. RAW contains the expected dense kernel;
5. AWQ contains the complete GEMM + reduction sequence;
6. raw NCU report/session/base export is preserved;
7. session command explicitly proves application replay + cache-control none;
8. replay-pass count is recorded, not assumed.

If application replay cannot preserve the exact semantic selection, STOP rather than silently falling back to V1.

## Analysis

Compute from V2 raw exports:

- M1 AWQ/RAW:
  - L1/TEX
  - L2
  - DRAM
- M256 AWQ/RAW
- RAW M256/M1
- AWQ M256/M1
- traffic shape-interaction ratio

Compare V2 with:
- accepted native timing interaction;
- V1 cold-kernel-replay traffic.

Required interpretation categories:

1. V2 preserves V1 direction/magnitude reasonably;
2. V2 preserves direction but materially changes magnitude;
3. V2 changes one or more qualitative traffic directions.

Any of these is a valid scientific result.

## Claim boundary

V2 may support:

> warmed/application-context semantic-module traffic is associated with the observed implementation/shape timing interaction.

It still does not establish:
- cache causality;
- TLB causality;
- a specific mechanism opportunity.

## Deliverables

Review pack:

`docs/vm_tlb/review_packs/C16_E1_SEMANTIC_NCU_CACHE_STATE_REPAIR_109_V1/`

At minimum:

- `UPSTREAM_V1_AUDIT.json`
- `PROFILER_MODE_CONTRACT.json`
- `REPLAY_POINT_BINDINGS.tsv`
- `RAW_*_SESSION.csv`
- `RAW_*_BASE.csv`
- `SELECTED_KERNELS.tsv`
- `TRAFFIC_SUMS.tsv`
- `TRAFFIC_COMPARISON.json`
- `V1_V2_COMPARISON.json`
- `SCIENTIFIC_INTERPRETATION.md`
- `NEXT_STEP_DECISION.json`
- `SHA256SUMS`

Update the living scientific log.

## Stop boundary

This repair is one complete node109 Goal.

Do not start:
- NVBit;
- full address trace;
- TLB/cache mechanism.

After V2 closure:
commit -> push -> remote verify -> clean -> release GPU lock -> STOP.
