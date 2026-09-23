# CODEX 174-new — C16 E1 Targeted L2 Persistence Consumer Prep/Closure V1

## Mode

GOAL MODE / CPU-side parallel prep and one-shot consume-if-ready

Suggested branch:

`hrl/c16-e1-l2-persistence-intervention-consumer-174new-v1`

No GPU work.

## Read first

Fetch and verify:

`hrl/c16-e1-l2-persistence-intervention-handoff-v1`

Read completely:

1. `docs/vm_tlb/chatgpt_handoff/c16/e1_l2_persistence_intervention_v1/CURRENT_STATE.md`
2. `docs/vm_tlb/chatgpt_handoff/c16/e1_l2_persistence_intervention_v1/DESIGN.md`
3. this file

Accepted natural-reuse consumer:

`hrl/c16-e1-natural-reuse-residency-consumer-174new-v1@4f9242d177220721cb9e669aad5dd9e29f04407d`

## Stage 1 — contract audit

Freeze:

- CUDA capability fields
- exact qweight-only address interval policy
- five natural conditions
- target vs setaside-only vs unrelated controls
- timing/DRAM materiality
- conditional budget-sweep gate
- allowed final-state labels
- no mechanism implementation

Create:
`DESIGN_AUDIT.json`

## Stage 2 — policy receipt consumer

Implement a fail-closed policy-receipt parser.

Require:

- CUDA runtime/device identity
- L2/max-persist/max-window values
- qweight pointer/bytes/contiguity
- requested and accepted set-aside
- access window base/bytes
- hitRatio
- hit/miss properties
- stream identity
- reset receipt

Fail closed on:
- qweight/window mismatch
- window larger than target qweight for target-persist conditions
- budget > runtime max
- window > runtime max
- missing reset
- ambiguous target region
- wrong condition label.

SETASIDE_ONLY must prove no target persisting window is active.

BASELINE must prove persisting state is reset/disabled.

## Stage 3 — isolated qualification consumer

Build independent raw timing and NCU consumer for:

- ISO_BASELINE_DENSE
- ISO_QWEIGHT_PERSIST_DENSE

Timing:
- 9 reps each
- exact input/output identity
- median/min/max/CV
- persist/baseline ratio

NCU:
consume BASE+SESSION+PROFILE+policy receipt directly.

Verify:
- application replay
- cache-control none
- exact target range
- exact metrics/units
- kernel inventory
- replay pass count
- policy identity.

## Stage 4 — natural condition consumer

Expected conditions:

- BASELINE
- SETASIDE_ONLY
- PERSIST_L0_UP
- PERSIST_L14_UP
- PERSIST_L0_DOWN

For each:
- 7 fresh process runs
- exact accepted prefix
- token sequence
- 12 occurrence SHA sequence
- timing rows
- decode-step rows
- policy receipt.

Fail closed on any semantic identity change across conditions.

## Stage 5 — natural NCU consumer

Independently consume raw NCU evidence for the frozen 16-profile maximum matrix.

Do not use producer summary TSV as authority.

For each profile require:

- condition
- target/layer/role/decode index
- exact NVTX range
- BASE+SESSION+PROFILE
- policy receipt
- application replay/cache-control none
- exact three traffic metrics
- unit byte
- exact kernel inventory
- replay pass count.

Compute semantic sums directly.

## Stage 6 — comparison recompute

For each target compute independently:

### reservation
SETASIDE_ONLY vs BASELINE

### target persistence
PERSIST_TARGET vs SETASIDE_ONLY

### unrelated persistence
PERSIST_OTHER vs SETASIDE_ONLY

Timing benefit:
>=5% lower and greater than combined dispersion.

DRAM benefit:
>=20% lower and >=4MiB absolute.

TARGET_SPECIFIC:
target-persist effect materially exceeds matched unrelated effect.

Do not compare only PERSIST_TARGET to BASELINE.

## Stage 7 — budget sensitivity consumer

If producer correctly triggered budget sweep:

Expected budgets:
8,16,24,32 MiB,full-qweight.

Verify:
- same full qweight window
- tested set-aside
- hitRatio=min(1,budget/qweight_bytes)
- 7 fresh processes/budget
- natural L0 up D3 identity

Independently recompute:
- timing stats
- DRAM
- first TESTED material budget

No exact threshold claim.

If producer did not trigger sweep:
verify trigger condition was false.

## Stage 8 — independent final-state decision

Allowed:

- MECHANISM_REQUIREMENTS_READY_FOR_DESIGN_REVIEW
- TARGETED_PERSISTENCE_TRAFFIC_ONLY
- TARGETED_PERSISTENCE_MECHANISM_PRECONDITION_NOT_SUPPORTED
- CUDA_PERSISTENCE_POLICY_UNQUALIFIED

If requirements-ready:
independently verify the producer requirement document is supported by evidence.

Do not authorize:
- NVBit
- full trace
- simulator mechanism implementation
- cache/TLB mechanism simulation.

## Stage 9 — review pack

Prepare:

`docs/vm_tlb/review_packs/C16_E1_L2_PERSISTENCE_INTERVENTION_CONSUMER_174NEW_V1/`

At minimum:

- `DESIGN_AUDIT.json`
- `CONSUMER_TESTS.tsv`
- `POLICY_RECEIPT_CONTRACT.json`
- `ISOLATED_CONSUMER_CONTRACT.json`
- `NATURAL_CONDITION_CONTRACT.json`
- `PRODUCER_RAW_PROVENANCE_AUDIT.json`
- `INDEPENDENT_ISOLATED_ANALYSIS.json`
- `INDEPENDENT_NATURAL_TIMING.json`
- `INDEPENDENT_NATURAL_NCU.json`
- `INDEPENDENT_POLICY_EFFECTS.json`
- `INDEPENDENT_BUDGET_ANALYSIS.json`
- `MECHANISM_REQUIREMENT_CHECK.json`
- `PRODUCER_MATCH_CHECK.json`
- `SCIENTIFIC_INTERPRETATION.md`
- `FINAL_DECISION.json`
- `NEXT_STEP_AUTHORIZATION.json`
- `SHA256SUMS`

## Stage 10 — one-shot consume if ready

Expected producer:

`hrl/c16-e1-l2-persistence-intervention-109-v1`

After prep, fetch once.

If producer exists and is complete:
- consume raw evidence
- independently close
- update scientific log
- commit/push/verify/clean
- STOP.

If producer absent/incomplete:
- commit/push prep
- verify/clean
- STOP as:

`READY_FOR_E1_L2_PERSISTENCE_INTERVENTION_109`

No polling.

## Boundaries

No GPU.
No NVBit.
No full trace.
No mechanism simulation.
