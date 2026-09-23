# CODEX 174-new — C16 E1 Natural-Reuse / Residency Consumer Prep/Closure V1

## Mode

GOAL MODE / CPU-side parallel preparation and one-shot consume-if-ready

Suggested branch:

`hrl/c16-e1-natural-reuse-residency-consumer-174new-v1`

No GPU work.
Do not modify node164 accepted authority.

## Read first

Fetch and verify:

`hrl/c16-e1-natural-reuse-residency-handoff-v1`

Read completely:

1. `docs/vm_tlb/chatgpt_handoff/c16/e1_natural_reuse_residency_v1/CURRENT_STATE.md`
2. `docs/vm_tlb/chatgpt_handoff/c16/e1_natural_reuse_residency_v1/DESIGN.md`
3. this file

Accepted consumer authorities:
- residency consumer:
  `hrl/c16-e1-residency-intervention-consumer-174new-v1@5b11dd41e98044fcad76da4a906c7ba8609eb828`
- residency raw-consumer hardening:
  `hrl/c16-e1-residency-consumer-hardening-v2@66f14280eb69cc6332b928c3ec045ac9074509b8`

## Stage 1 — contract audit

Freeze and audit:

- refill-sequence K1..K6 identity
- capacity-knee dose sets
- natural full-model decode token/occurrence identity
- layer0/layer14 target roles
- application replay/cache-control-none requirement
- optional RAW natural control boundary
- no mechanism claim

Create:
`DESIGN_AUDIT.json`

## Stage 2 — refill consumer

Implement raw native timing consumer for:

`role × implementation × K1..K6 × repetition`

Fail closed on:
- missing/duplicate K
- missing/duplicate rep
- target input SHA drift
- target output SHA drift
- non-finite timing
- wrong point matrix

Compute:
- median/min/max/CV per Ki
- Ki/K1 timing ratios
- K1→K6 fractional recovery
- monotonicity diagnostic, not pass gate

Extend raw NCU consumer identity with:
- refill_call_index

Directly consume:
BASE + SESSION + PROFILE

Compute:
- L1/L2/DRAM per K1/K2/K4
- K2/K1 and K4/K1 ratios
- RAW/AWQ refill comparisons

Synthetic tests required.

## Stage 3 — capacity-knee consumer

Freeze exact dose sets from DESIGN.

Implement timing + raw NCU dose consumer.

Independently compute:
- nominal residual-L2 budget from accepted L2/state bytes
- DRAM/timing at every dose
- first dose where DRAM >1 MiB and >10% packed state
- first material timing dose
- observed DRAM-knee minus nominal residual-L2 MiB

Fail closed on:
- missing dose
- duplicate dose/rep
- wrong role/implementation
- wrong pressure prefix
- wrong metric/unit
- identity drift

No forced pass/fail for exact knee equality.

## Stage 4 — natural decode consumer

Implement raw authority consumer for full-model natural decode.

Authority fields:
- accepted prefix token SHA
- generated token IDs D0..D3
- fresh-process token-sequence replay
- layer index
- role
- decode index
- input SHA
- output SHA
- NVTX range

Fail closed on:
- token sequence mismatch
- duplicate/missing occurrence
- SHA mismatch
- wrong layer/role/index
- non-M1 decode target shape
- NCU range mismatch

Native:
- independently recompute per-occurrence timing stats from raw full-run timing rows.

NCU:
- consume BASE+SESSION+PROFILE directly
- application replay/cache-control none
- exact metric names/units
- exact kernel inventory

## Stage 5 — isolated-reference comparator

Use accepted isolated WARM/DENSE evidence from previous closed stages.

Do not read producer-computed natural-vs-isolated summary as authority.

For every natural target with matching isolated reference compute:

`warm_fraction = abs(natural-warm)/abs(dense-warm)`

for:
- DRAM
- timing

If denominator = 0:
report undefined.

Do not clamp values.

## Stage 6 — integrated case recompute

Independently classify evidence using DESIGN Case A/B/C/D framing.

This is descriptive; no hidden scoring.

Explicitly preserve:
- capacity effect
- role/access-policy effect
- natural inter-module interference effect
as separable observations.

No mechanism authorization is derived automatically.

## Stage 7 — prepare review pack

Prepare:

`docs/vm_tlb/review_packs/C16_E1_NATURAL_REUSE_RESIDENCY_CONSUMER_174NEW_V1/`

At minimum:

- `DESIGN_AUDIT.json`
- `CONSUMER_TESTS.tsv`
- `REFILL_CONSUMER_CONTRACT.json`
- `KNEE_CONSUMER_CONTRACT.json`
- `NATURAL_SEQUENCE_CONSUMER_CONTRACT.json`
- `PRODUCER_RAW_PROVENANCE_AUDIT.json`
- `INDEPENDENT_REFILL_ANALYSIS.json`
- `INDEPENDENT_KNEE_ANALYSIS.json`
- `INDEPENDENT_NATURAL_TIMING.json`
- `INDEPENDENT_NATURAL_NCU.json`
- `INDEPENDENT_NATURAL_VS_ISOLATED.json`
- `OPTIONAL_RAW_CONTROL_CHECK.json`
- `PRODUCER_MATCH_CHECK.json`
- `SCIENTIFIC_INTERPRETATION.md`
- `FINAL_DECISION.json`
- `NEXT_STEP_AUTHORIZATION.json`
- `SHA256SUMS`

Producer-dependent files may remain absent before producer exists.

## Stage 8 — consume once if ready

Expected producer:

`hrl/c16-e1-natural-reuse-residency-109-v1`

After prep, fetch remote once.

If complete:
- consume raw timing and raw NCU evidence directly
- independently close all analyses
- update scientific log
- commit/push/verify/clean
- STOP

If absent/incomplete:
- commit/push prep
- verify/clean
- STOP as:

`READY_FOR_E1_NATURAL_REUSE_RESIDENCY_109`

No polling loop.

## Boundary

No GPU.
No NVBit.
No full address trace.
No cache/TLB mechanism.
No mechanism simulation.
