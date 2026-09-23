# CODEX 174-new — C16 E1 Clean Baseline Consumer/Prep V1

## Mode

GOAL MODE / CPU-side parallel preparation

Suggested branch:

`hrl/c16-e1-clean-baseline-consumer-prep-174new-v1`

No GPU work.
Do not modify node164 accepted raw/catalog objects.

## Read first

Fetch and verify:

`hrl/c16-e1-clean-baseline-handoff-v1`

Read completely:

0. `docs/vm_tlb/chatgpt_handoff/c16/e1_clean_baseline_v1/FP16_CAST_BRIDGE_CONTRACT_V2.md`

1. `docs/vm_tlb/chatgpt_handoff/c16/e1_clean_baseline_v1/CURRENT_STATE.md`
2. `docs/vm_tlb/chatgpt_handoff/c16/e1_clean_baseline_v1/E1_CLEAN_BASELINE_DESIGN_V1.md`
3. this file

Historical references:

- old E1 recovery failure:
  `hrl/c16-e1-qwen25-shape-lowbit-109-v1@5563c7bc9320f6699f351307b2895093d0658d97`
- old historical eight-point matrix:
  `hrl/awma-e1-shape-oracle-moe-harness-109-v2@56096d32bd5cd783286e1b5e5e612b6019f926d0`
- C16 RAW/AWQ pair closure:
  `hrl/c16-qwen25-7b-pair-closure-109-v10@57ca798c851a3b9d4a2c787c01f4e2b3a16fcdea`

## Stage 1 — independent contract audit

Audit the new clean-baseline design for internal consistency.

Confirm:
- old historical eight-point values are separated from new primary clean data;
- canonical source is RAW natural Layer0 S2_TEXT M2048 module input;
- M1/M256 slicing is deterministic;
- RAW_FP16 and AWQ use identical FP16 activation bytes;
- comparison remains implementation-level, not pure quantization causality.

Create:
`DESIGN_AUDIT.json`

If a scientific contradiction exists, STOP immediately and report it.

Routine wording/schema issues: solve-and-continue.

## Stage 2 — node164/local asset discovery

Search available node164 C16 assets and Git authority for:

### CODE holdout
Determine whether a durable common Qwen2.5 CODE token/input authority already exists.

Return exact:
- path
- SHA/receipt
- model/revision binding
- whether it can be used by the new RAW-canonical same-input contract.

### Optional Llama sanity
Determine whether Llama-3.2-1B assets/receipts are already available in node164/Git sufficiently for a cheap RAW-only M1/M256 linear sanity run.

Do not download or create assets.

Create:
- `AUXILIARY_ASSET_AUDIT.json`

## Stage 3 — prebuild independent consumer

Implement a CPU-side consumer/comparator for the expected 109 review pack schema.

It must compute independently from the producer timing TSV/receipts:

For each role × M:
- median/min/max/CV
- `R_dtype = RAW_FP16 / RAW_BF16`
- `R_awq = AWQ / RAW_FP16`

For each role:
- shape ratios
- `I = log(R_awq_M256) - log(R_awq_M1)`

Also:
- check exact same FP16 activation SHA between RAW_FP16 and AWQ rows;
- check authority regeneration PASS;
- check dtype/path identity;
- keep historical eight-point values in a separate namespace/table.

No formal p-values.

Materiality:
- >=5% median effect
- and larger than ordinary pair dispersion

Implement a deterministic NCU-selection recompute:
- choose role maximizing abs(I) among roles passing materiality;
- verify producer NCU selection, if any, matches this rule.

Create tests using synthetic fixture data only.

Do not populate final scientific values before producer evidence exists.

## Stage 4 — prepare output schema

Prepare expected consumer review pack:

`docs/vm_tlb/review_packs/C16_E1_CLEAN_BASELINE_CONSUMER_174NEW_V1/`

At minimum:
- `DESIGN_AUDIT.json`
- `AUXILIARY_ASSET_AUDIT.json`
- `CONSUMER_CONTRACT.json`
- `CONSUMER_TESTS.tsv`
- `PRODUCER_AUTHORITY_AUDIT.json`
- `INDEPENDENT_RECOMPUTE.json`
- `INTERACTION_COMPARISON.tsv`
- `NCU_SELECTION_CHECK.json`
- `SCIENTIFIC_INTERPRETATION.md`
- `FINAL_DECISION.json`
- `NEXT_STEP_AUTHORIZATION.json`
- `SHA256SUMS`

Before producer results, files depending on producer data may remain absent rather than filled with placeholders.

## Stage 5 — consume producer if available

Producer expected branch:

`hrl/c16-e1-clean-baseline-109-v1`

After prep is complete, fetch remote once.

If a completed producer review pack is already present:
- verify remote HEAD;
- independently audit its new canonical authority;
- independently recompute all timing ratios/interactions;
- verify CODE/Llama status;
- verify conditional NCU entry gate and selected points;
- write full consumer review pack;
- commit/push/remote verify/clean;
- STOP with final consumer decision.

If producer is not yet complete:
- commit/push the prep artifacts;
- remote verify/clean;
- STOP with:
  `READY_FOR_109_CLEAN_BASELINE`

Do not idle/poll for hours.

## Scientific boundaries

Do not infer:
- quantization-only causality;
- cache/TLB causality from timing or NCU traffic;
- end-to-end model speedup;
- generality beyond the tested model/operator/shape.

If NCU traffic differs, describe it as deployment/kernel traffic evidence only.

## Solve-and-continue

Routine parser/schema/Git/node164 search issues:
solve and continue.

STOP early only for a genuine scientific contradiction in the clean-baseline contract.
