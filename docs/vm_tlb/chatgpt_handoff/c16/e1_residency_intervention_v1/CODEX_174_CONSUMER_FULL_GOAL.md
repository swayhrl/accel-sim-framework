# CODEX 174-new — C16 E1 Residency Intervention Consumer Prep/Closure V1

## Mode

GOAL MODE / CPU-side parallel preparation and one-shot consume-if-ready

Suggested branch:

`hrl/c16-e1-residency-intervention-consumer-174new-v1`

No GPU work.
Do not modify node164 accepted authority.

## Read first

Fetch and verify:

`hrl/c16-e1-residency-intervention-handoff-v1`

Read completely:

1. `docs/vm_tlb/chatgpt_handoff/c16/e1_residency_intervention_v1/CURRENT_STATE.md`
2. `docs/vm_tlb/chatgpt_handoff/c16/e1_residency_intervention_v1/DESIGN.md`
3. this file

Accepted independent semantic-NCU consumer:
`hrl/c16-e1-semantic-ncu-v2-consumer-174new-v1@cdd3ec7afbb1611cc52a4b74d32b38a3edabd131`

Hardened raw-NCU consumer:
`hrl/c16-e1-semantic-ncu-consumer-hardening-v1@396233ca250c20be834aa0c50d2504e6017953bc`

## Stage 1 — independent contract audit

Audit the intervention design and freeze:

- target semantic input/backend is invariant;
- pressure runs outside target timing/NVTX;
- WARM/SPARSE/DENSE/WARM_B state definitions;
- SPARSE is a page-footprint-oriented control, not a TLB-only control;
- DENSE is memory/cache pressure, not a guaranteed cache flush;
- same 256 MiB allocation is reused;
- no mechanism claim is allowed.

Create:
`INTERVENTION_DESIGN_AUDIT.json`

## Stage 2 — pre-register capacity and prediction logic

Implement independent capacity census logic from accepted receipts/module metadata.

Required outputs:

- exact RAW FP16 parameter bytes per q/down/up;
- exact AWQ state_dict bytes per q/down/up;
- device L2 bytes;
- relation of each to L2.

Freeze P1–P4 and materiality/recovery logic from DESIGN in machine-readable form.

Create:
- `CAPACITY_CONTRACT.json`
- `PREDICTION_CONTRACT.json`

## Stage 3 — build independent timing comparator

Implement parser for producer native timing rows.

It must independently compute for each point:

- median/min/max/CV
- SPARSE/WARM_A
- DENSE/WARM_A
- WARM_B/WARM_A
- combined dispersion
- materiality
- recovery

Fail closed on:
- missing state;
- duplicate point/state/rep;
- input/output SHA mismatch within target point;
- non-finite timing;
- sample-count mismatch.

Synthetic tests must cover:
- material dense effect;
- no effect;
- sparse≈dense;
- warm recovery;
- failed recovery;
- duplicate/missing samples.

## Stage 4 — extend hardened raw-NCU normalizer

Extend the hardened raw-NCU consumer to include intervention state in the semantic point identity.

For every producer raw NCU profile later verify directly from raw BASE/SESSION evidence:

- exact target range
- point/role/M/implementation/state
- application replay
- cache-control none
- exact metric names/units
- replay pass count
- RAW vs AWQ kernel inventory
- pressure operation outside target semantic range

Compute independent semantic sums and state ratios.

Do not trust producer-normalized NCU TSV as authority.

Synthetic tests:
- WARM/SPARSE/DENSE unique identities
- duplicate state range fails
- pressure kernel accidentally inside target range fails
- missing metric fails
- unit mismatch fails.

## Stage 5 — pressure-dose comparator

Implement independent dose parser:

- 0,16,32,64,128,256 MiB
- RAW/AWQ
- 7 reps/dose

Compute:
- median/CV
- ratio to 0MiB
- monotonicity diagnostics

Do not require strict monotonicity as a PASS gate.

## Stage 6 — decision recompute

Implement producer-independent recompute of:

- MATERIAL_TIMING_PERTURBATION
- MATERIAL_DRAM_PERTURBATION
- REVERSIBLE
- DENSE_SPECIFIC

Then recompute scoped label:

- RESIDENCY_INTERVENTION_STRONGLY_SUPPORTED
- RESIDENCY_INTERVENTION_PARTIALLY_SUPPORTED
- RESIDENCY_INTERVENTION_NOT_SUPPORTED

Use DESIGN exactly.

Do not broaden label to universal cache causality.

## Stage 7 — prepare review pack

Prepare:

`docs/vm_tlb/review_packs/C16_E1_RESIDENCY_INTERVENTION_CONSUMER_174NEW_V1/`

At minimum:

- `INTERVENTION_DESIGN_AUDIT.json`
- `CAPACITY_CONTRACT.json`
- `PREDICTION_CONTRACT.json`
- `CONSUMER_TESTS.tsv`
- `PRODUCER_RAW_PROVENANCE_AUDIT.json`
- `INDEPENDENT_CAPACITY_CENSUS.tsv`
- `INDEPENDENT_TIMING_ANALYSIS.json`
- `INDEPENDENT_NCU_SUMS.tsv`
- `INDEPENDENT_INTERVENTION_ANALYSIS.json`
- `INDEPENDENT_DOSE_ANALYSIS.json`
- `CODE_HOLDOUT_CHECK.json`
- `PRODUCER_MATCH_CHECK.json`
- `SCIENTIFIC_INTERPRETATION.md`
- `FINAL_DECISION.json`
- `NEXT_STEP_AUTHORIZATION.json`
- `SHA256SUMS`

Producer-dependent files may remain absent before producer exists.

## Stage 8 — consume producer once if ready

Expected producer branch:

`hrl/c16-e1-residency-intervention-109-v1`

After prep is complete, fetch remote once.

If producer is complete:
- independently consume raw timing/NCU evidence;
- verify all calculations and labels;
- update living scientific log;
- complete review pack;
- commit/push/verify/clean;
- STOP.

If producer is absent/incomplete:
- commit/push prep;
- verify/clean;
- STOP with:
  `READY_FOR_E1_RESIDENCY_INTERVENTION_109`

Do not poll/idle for hours.

## Scientific boundaries

Even if strong:

Allowed:
> controlled memory-state intervention supports a cache-line residency contribution under the tested points.

Not allowed:
- TLB fully excluded;
- L2 is the sole cause;
- mechanism design is already authorized.

No GPU/NVBit/full trace/mechanism work.
