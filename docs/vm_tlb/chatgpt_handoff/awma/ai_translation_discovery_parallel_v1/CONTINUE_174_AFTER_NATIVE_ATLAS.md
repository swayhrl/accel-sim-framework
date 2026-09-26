# Continue 174 after Native Atlas — V1

Date: 2026-09-26

Resume the SAME Lane E / 174-new window.

Previous preparation:
- branch `hrl/awma-ai-translation-path-and-residual-174new-v1`
- commit `a3756e1f3896c2ab292e2576c6271849c22eaf61`
- status `PREP_COMPLETE_AWAITING_NATIVE_ATLAS`

Native atlas is now ready:
- branch `hrl/awma-ai-translation-native-atlas-capture-109-v1`
- commit `39548abdd83bf5058abc5ffedd9513286ddab271`
- status `READY_FOR_AI_TRANSLATION_RESIDUAL_174NEW`

Create continuation branch:
`hrl/awma-ai-translation-native-residual-174new-v1`

Do NOT repeat the access-path source audit or existing T0/T1/T2/A2 path matrix.
Consume them as accepted authority.

## 1. Consume Native handoff exactly once

Read:
`docs/vm_tlb/review_packs/AWMA_AI_TRANSLATION_NATIVE_ATLAS_CAPTURE_109_V1/NATIVE_ATLAS_CONSUMER_HANDOFF.json`

Qualified simulator inputs:
- L1: Llama-3.2-1B GEMV, QUALIFIED
- M1: OLMoE GEMV, QUALIFIED
- M2: OLMoE reduction, QUALIFIED

Native-only / blocked:
- L2: Llama attention, TRACE_GRAMMAR_BLOCKED due to LDC.U8 width.

No replacement target selection.

## 2. Interpretation of Native evidence before simulator runs

Freeze these facts before seeing simulator output:

### L1 vs M1
Same exact function SHA:
`e52f28ddc664202dcf583dfef5266a7d06e21d90dcaf3c98eb3b6c993036ea9d`

L1 grid = 2048x1x1
M1 grid = 256x1x1

Per CTA both have:
- 514 dynamic memory instructions
- 16,388 active-lane refs
- exactly 258 one-page instructions
- exactly 256 two-page instructions

Thus L1/M1 are a useful scale/aggregate-working-set comparison, NOT evidence that MoE changes local GEMV page behavior.

### M2
One CTA, 2 dynamic memory instructions, 9 active-lane refs, 2 virtual 4KB pages.
Treat as LOW_TRANSLATION_DEMAND_CONTROL.
Do not generalize from it to MoE.

### L2
Distinct attention-like structure, Native page behavior retained, but no simulator claim until grammar-qualified.

Record this preregistered interpretation in:
`NATIVE_INTERPRETATION_FREEZE.md`.

## 3. Qualify L1/M1/M2 under strong baseline

For each:
- verify trace SHA/grammar/identity;
- run `WARP_VPN_DEDUP_REFERENCE` 10/80;
- correctness/coverage/exactly-once/terminal/quiescence;
- instructions/CTA/UID;
- untranslated/unobserved/duplicate=0.

If any qualification fails, stop only that target; continue the others.

Collect:
- cycles
- L1 TLB launches/hits/misses
- L2 launches
- MSHR alloc/merge/full
- PWQ/walker/PTW/PTE
- L1D accesses/hits/misses/reservation failures
- translation-not-ready exposure
- scheduler/memory Observatory Level1 only where needed.

## 4. Adaptive path/residual diagnostics

### L1 and M1
Because they are exact-function scale controls:
1. compare normalized-per-CTA and normalized-per-memory-instruction service counts;
2. compare aggregate working-set/capacity effects;
3. if hit-dominated with low miss-side pressure, run the accepted B1-equivalent 0/80 diagnostic;
4. if 0/80 removes most response, classify as access-path-sensitive rather than a new translation problem.

Do not call cross-model raw runtime comparable.

### M2
Do strong-baseline qualification only by default.
Run no extra diagnostic unless an unexpected material translation bottleneck appears.

### Miss/walker path
Only if a qualified target shows material MSHR/PWQ/PTW pressure that survives B1:
use one bounded source-supported causal diagnostic at the actual bottleneck level.
Do not implement MPW/LATPC as mechanisms.

Max new full-kernel diagnostic replays for L1/M1/M2 after strong baseline: 6 total.

## 5. Bounded L2 LDC.U8 grammar-repair audit

Do this OFFLINE; no node109 GPU use by default.

Goal: determine whether the missing/zero width can be reconstructed deterministically from accepted SASS/producer semantics, not guessed.

Allowed path:
- identify exact producer/postprocessor grammar representation for `LDC.U8`;
- verify opcode semantics and existing accepted traces/canaries;
- if width is a deterministic function of the opcode/operand form, implement a narrowly scoped normalization in a NEW diagnostic/consumer path with provenance;
- prove no change to instruction count, opcode, addresses, CTA/UID ordering, or non-LDC records;
- validate against at least one known-good instruction-width canary where applicable;
- preserve original blocked artifact unchanged.

If and only if all gates pass:
create a new derived input authority:
`L2_GRAMMAR_REPAIRED_DETERMINISTIC`
and then run the same strong-baseline/path residual flow on L2.

If any semantic ambiguity remains:
keep:
`L2_TRACE_GRAMMAR_BLOCKED`
and do not weaken the validator.

This grammar audit is engineering enablement, not a scientific mechanism.

## 6. Novel-problem gate

For every simulated target, classify:

A. `NO_MATERIAL_TRANSLATION_RESIDUAL`

B. `ACCESS_PATH_MODEL_SENSITIVE_ONLY`
- material under sequential strong baseline
- largely explained by B1/VIPT-like overlap
- no distinct miss-side bottleneck

C. `KNOWN_MISS_SIDE_PROBLEM`
- material MSHR/PTW/walker pressure
- closest work already covers the capability (ISCA2018 / Neighborhood / LATPC / MPW / Avatar etc.)

D. `DIFFERENTIATED_RESIDUAL_PROBLEM`
Only if:
- material under strong baseline;
- survives appropriate path diagnostic;
- localized to a finite resource/service;
- not already covered by closest work;
- online information exists for a future solution.

At most TWO problem cards.
Do not create a mechanism unless D exists.

## 7. Optional one prototype only

Only if D exists:
- preregister max 3 development targets;
- implement ONE primary prototype;
- baseline = WARP_VPN_DEDUP_REFERENCE + appropriate realistic path model;
- max 3 main + 3 matched controls;
- no sweep and no automatic repair loop.

Otherwise candidate runs = 0.

## 8. Deliverables

- README.md
- NATIVE_INTERPRETATION_FREEZE.md
- NEW_TRACE_QUALIFICATION.tsv
- L1_M1_SCALE_COMPARISON.tsv
- NEW_AI_RESIDUAL_MATRIX.tsv
- DIAGNOSTIC_DECISION_LOG.tsv
- L2_GRAMMAR_AUDIT.md
- L2_DERIVED_INPUT_AUTHORITY.tsv if repaired
- CLOSEST_WORK_SCREEN.md
- PROBLEM_CARD_1.md / PROBLEM_CARD_2.md if any
- PROTOTYPE_DECISION.md
- REPORT.md
- RAW_DATA_INDEX.tsv
- SHA256SUMS

Final status exactly one of:
- `NO_NEW_AI_TRANSLATION_PROBLEM_IDENTIFIED_V1`
- `NOVEL_AI_TRANSLATION_PROBLEM_IDENTIFIED_READY_FOR_FORMAL_DEVELOPMENT`
- `AI_TRANSLATION_PROTOTYPE_SUPPORTED_DEVELOPMENT`
- `AI_TRANSLATION_PROTOTYPE_NOT_SUPPORTED`

Commit/push/fetch-back/remote HEAD+tree/hash/clean and STOP.

Do not start node109 in this continuation unless the L2 grammar audit proves a recapture is strictly necessary; if so, STOP and report rather than silently using GPU.
