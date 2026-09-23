# AWMA AI translation representative suite design V1

Status: **PROVISIONAL_PRE_GATE**  
Stage: AWMA_AI_TRANSLATION_REPRESENTATIVE_SUITE_DESIGN_V1

This is the Window D review pack. It is a deterministic methodology and
provisional result, not a frozen final suite.

## Inputs and boundary

- V1 Native inventory: AWMA_QWEN25_S2_KERNEL_CENSUS_V1.
- Durable inventory SHA-256:
  7825697aa23647daee6a38ac4436029c5746fe29a468d303520d3884f2b4abef.
- No new Native capture, simulator run, mechanism exploration, Node109 work, or
  Lane B change was launched.

## Stratification contract

A stratum is phase / normalized family / exact implementation / grid / block /
Decode-step behavior. Required source fields are global launch index, phase,
decode step, duration, normalized family, exact or demangled implementation,
grid, block, and semantic category.

Exact implementations and grid/block variants are retained even when function
families match. UNKNOWN semantic fields remain UNKNOWN; operator semantics are
never guessed from a name. Decode behavior is a source-measured all-vs-partial
step-support plus stable/early-heavier/late-heavier duration descriptor.

## Selector

The stable script is util/vm_tlb/awma/representative_suite/
select_representative_suite.py. It accepts Window A V2 inventory without a
method redesign. It uses accumulated Native GPU duration and deterministic
family/behavior diversity bonuses. Forced inclusion covers material phase/family
strata, observed long and ordinary Decode GEMV, Prefill/Decode Flash, material
Prefill GEMM, and rare structurally distinct measured strata.

A SHA-256 identity-only split reserves holdouts before selection. The fixed seed
is AWMA_REPRESENTATIVE_SUITE_SELECTOR_V1_HOLDOUT_SPLIT. Holdout duration and
selection outcomes are not supplied to selection or tuning.

## Published provisional result

- SELECTED_SUITE.tsv: selected launch records.
- PROVISIONAL_COVERAGE.tsv: 68,482,853 / 126,743,918 selection-pool ns (54.03%).
  Decode coverage is 55.64%; Prefill is 52.07%; V1 UNKNOWN-phase is 46.23%.
- PROPOSED_HOLDOUTS.tsv: 6,902 independent validation records.
- UNCOVERED_LOW_CONFIDENCE_STRATA.tsv: omitted strata plus explicit unsupported
  splitkv/combine requirements.
- RUN_RECEIPT.json: input SHA and repeatable split receipt.

The nominal 24-member budget produces 52 forced inclusions under V1. This
budget/coverage conflict is exposed for review rather than silently dropping
structural variants.

## Pre-gate blockers

V1 phase attribution is superseded when Window A returns corrected launch
context. V1 has no source-supported splitkv/combine tag, so neither label is
inferred. Window C must provide per-target simulator-native payload/runner SHA,
qualification/replay status, and asset classification. Then rerun this script
on V2, join Window C, and freeze the final suite and holdouts.
