# CODEX NEXT STAGE — 174-new Q05 Context-Effect Decomposition V1

Date: 2026-09-18

Status: ACTIVE MAINLINE.

Stage:

`AWMA_Q05_CONTEXT_EFFECT_DECOMPOSITION_174NEW_V1`

Node:

`174-new / port 2239`

## 0. Scientific purpose

The accepted contextual replay has changed the interpretation of Q05.

Accepted natural results:

```text
row       cycles    L2-TLB miss   walks
isolated  885681    633           240
P1        895312    510           184
P2        848511    415           128
P4        872569    450           128
P8        835145    292            16
P16       862623    241            16
P34       871835    249            15
```

Key accepted observations:

- full real P34 history reduces walks from 240 to 15 (-93.75%);
- full real P34 reduces L2-TLB misses from 633 to 249 (-60.66%);
- but P34 cycles are only 1.56% below isolated;
- P8 reaches near-saturated translation-relevant page overlap and 16 walks;
- P16 has the same 16 walks as P8 and *fewer* L2-TLB misses, yet is 27,478 cycles slower;
- P34 has only 15 walks but is slower than P8 by 36,690 cycles.

Therefore real predecessor history removes most cold PTW activity, but total-cycle behavior contains a substantial non-translation context component.

This stage answers:

> Under realistic contextual state, how much target-Q05 performance sensitivity remains attributable to the modeled translation path itself?

Do not start a new mechanism in this stage.

## 1. Coordination and execution parent

Read coordination branch:

`hrl/awma-q05-context-effect-decomposition-handoff-v1`

Execution parent:

```text
hrl/awma-q05-contextual-warm-prefix-replay-174new-v1
2640c4368aea1dc44eb6c34fdc9bb5f738ec3fb2
```

Recommended branch:

`hrl/awma-q05-context-effect-decomposition-174new-v1`

Formal context bundle remains immutable:

```text
C16R_qwen-qwen2-5-0-5b-instruct_s2-text_prefill_awma-route-b-nvbit1771-sim-native-contiguous-prefix_q05-contiguous-prefix_20260918T022749Z_1fea2d955d1c
manifest = 5dc4f8d3fc802e6af66ab76f33adfeb31b335d44511ec792404c7210ca04d64e
```

Accepted framework/core/F0 anchors remain unchanged.

## 2. D0 — Existing-run causal counter audit first

Before adding any new simulator instrumentation, mine the already accepted isolated/P1/P2/P4/P8/P16/P34 run logs on node164.

For every source-defined cumulative counter that can be differenced at the Q05 boundary, determine whether it helps explain contextual cycle differences.

Audit at least, where available:

- L2 request/access/miss classes;
- DRAM request counts and traffic;
- DRAM row-buffer/locality counters;
- memory-partition queue/latency counters;
- interconnect injection/return pressure;
- L2 queue/reservation-fail counters;
- shader memory-pipeline stall categories;
- scheduler/issue/scoreboard stall counters;
- cache replacement/eviction counters;
- any target-boundary-safe native memory-system telemetry already emitted by the accepted binary.

Do not invent counters that are not present.

Prioritize these natural contrasts:

### P2 vs P4

```text
walks: 128 -> 128
PWC misses: 3 -> 3
PTE requests: 131 -> 131
cycles: 848511 -> 872569 (+24058)
```

### P8 vs P16

```text
walks: 16 -> 16
L2-TLB misses: 292 -> 241
translation requester latency total: 8466455 -> 8371120
L2 data misses: 1183770 -> 1181047
cycles: 835145 -> 862623 (+27478)
```

This pair is especially important because translation and aggregate L2-miss counters improve while total cycles worsen.

### P16 vs P34

```text
walks: 16 -> 15
cycles: 862623 -> 871835 (+9212)
L2 data misses: 1181047 -> 1190722
```

Output:

- `EXISTING_RUN_CONTEXT_COUNTER_MATRIX.tsv`
- `NATURAL_CONTRAST_AUDIT.md`

Allowed conclusion at this point:

`NON_TRANSLATION_CONTEXT_EFFECT_PRESENT`

if the source-backed counters support it.

Do not claim an exact L2/DRAM causal mechanism unless the available counters actually support it.

## 3. D1 — Target-only ideal-translation counterfactual

This is the central experiment.

### Required semantics

All predecessor kernels in a row execute under the accepted natural F0/R0 translation path.

Only member 34 / Q05 changes.

At Q05 entry, for Q05 memory requests that would normally enter VM translation:

- bypass L1/L2 TLB, MSHR, PTW, PWC and PTE traffic;
- use the already accepted ideal-identity SimVA->SimPA semantics;
- preserve the same lower data-cache/memory-system path after translation;
- do not flush/reset L1/L2 data cache;
- do not alter predecessor execution;
- do not reconstruct or preload translation state;
- do not mutate the formal context bundle.

This is a **Q05-only translation counterfactual**, not a new architecture mechanism.

### Source-contract gate

Before implementation, prove from the accepted source/config that the natural R0 mapping for this admitted Q05/context is identity-compatible with the accepted mode-1 identity mapping.

If the target's accepted mapping can differ from identity in a way that changes lower-memory addresses, STOP_FOR_SCIENTIFIC_REVIEW rather than silently substituting addresses.

### Implementation policy

Prefer a minimal disabled-by-default diagnostic switch bound to exact target member/Q05 identity.

Do not globally set the whole prefix to I0.

Do not run predecessors under ideal translation.

Record a new diagnostic binary SHA; historical accepted binary remains unchanged.

## 4. D2 — Neutrality gate

With the new diagnostic source present but target-only ideal translation **disabled**, rerun at minimum:

```text
P8_R0_CONTROL
P34_R0_CONTROL
```

Require the accepted Q05 scientific metrics to reproduce exactly or to an already source-justified deterministic equivalence:

- Q05 cycles;
- completed active thread-instructions;
- CTA count;
- L1/L2 TLB accesses/hits/misses;
- walks;
- PWC/PTE;
- translation requester-latency composition;
- L2 data-cache accesses/misses.

If neutrality fails, repair the diagnostic plumbing before continuing.

No mechanism sweep.

## 5. D3 — Contextual Q05-only ideal-translation matrix

After neutrality passes, run from fresh simulator processes:

```text
P2_Q05_I0
P8_Q05_I0
P34_Q05_I0
```

Prefixes remain natural R0/F0.

For each, report Q05-only:

- cycles;
- active-thread instructions;
- CTA;
- ideal/bypass translation counters;
- L1/L2 TLB/PTW/PWC/PTE deltas, expected to be zero/bypassed according to exact diagnostic semantics;
- L2 data-cache accesses/misses;
- DRAM/memory-system counters available from D0.

Also run:

`ISOLATED_Q05_I0_FULL`

if it can be produced with the same target-only path without extra semantic ambiguity. This provides a full-kernel counterpart to the historical fixed-window I0 sensitivity.

Do not substitute historical 10k/50k progress numbers for full-kernel cycles.

## 6. D4 — Required comparisons

Create a table:

```text
context     R0 cycles   Q05-I0 cycles   delta cycles   relative sensitivity
isolated    ...
P2          ...
P8          ...
P34         ...
```

Answer quantitatively:

1. How much full-kernel Q05 cycle sensitivity to translation remains in the full real P34 context?
2. How much did the isolated condition overstate or understate this target-only translation sensitivity?
3. Does P8 and P34 show similar translation sensitivity even though their natural total cycles differ?
4. If P8/P34 target-only translation sensitivity is similar, can P8 be treated as a **screening-prefix candidate** for translation mechanism development while P34 remains the final realism reference?
5. If the P34 target-only ideal gain is small, which historical opportunity is specifically downgraded:
   - PTW/walk reduction;
   - L2-TLB miss handling;
   - total translation-path elimination?
6. If a substantial P34 ideal gap remains despite only 15 walks, does the remaining sensitivity point more toward lookup/service latency than PTW frequency?

Do not claim a concrete mechanism from these observations.

## 7. D5 — Optional non-translation state ablation only if source-safe

This subsection is optional and must not block D0-D4.

Only if D0 leaves the P8-vs-P34 non-translation cycle gap scientifically unresolved **and** the accepted source exposes a safe one-shot target-boundary L2-data-cache invalidate/flush operation that:

- does not alter translation hierarchy state;
- does not require fabricating data values;
- does not violate dirty-line correctness;
- can be disabled by default;
- has an obvious neutrality control;

then perform a bounded diagnostic on only P8 and P34:

```text
P8_L2COLD_Q05
P34_L2COLD_Q05
```

Q05 translation remains natural R0 in this optional pair.

The purpose is only to test whether inherited L2-data-cache state materially explains the P8/P34 natural cycle gap.

If the source-safe operation is not available, write:

`L2_TARGET_BOUNDARY_ABLATION_NOT_SAFE_OR_NOT_NEEDED`

and continue. Do not STOP the whole stage for this optional diagnostic.

Do not change global F0 `flush_l2` policy and call that equivalent to a one-shot target-boundary ablation.

## 8. Baseline policy after this stage

Until reviewed by ChatGPT:

- `P34` is the **realism reference** because it contains the complete available real predecessor history;
- `P8` is only a **screening-prefix candidate**;
- do not promote P8 merely because it has the lowest cycles;
- do not use isolated Q05 as the sole mechanism baseline after this contextual result.

No final screening/final-validation policy is frozen until D3/D4 is reviewed.

## 9. Existing result scope update to carry forward

Accepted contextual result:

```text
P34 vs isolated:
cycles      885681 -> 871835  (-1.56%)
walks       240    -> 15      (-93.75%)
L2-TLB miss 633    -> 249     (-60.66%)
PWC misses  70     -> 3
PTE req     310    -> 18
```

This supports:

- isolated cold replay substantially inflates PTW/walk activity;
- real-context translation state is mostly warm by Q05;
- total performance sensitivity cannot be inferred from walk reduction alone.

It does not yet establish the remaining causal cost of the whole translation path; D3 is designed to measure that.

## 10. No mechanism experiments

Forbidden in this stage:

- L2-TLB latency 80->40;
- TLB capacity/ports/walker sweeps;
- PTW fixed-latency mechanisms;
- page-size changes;
- segmentation;
- new PWC designs;
- speculative translation;
- translation prefetch;
- cache architecture changes.

This stage is causal decomposition only.

## 11. Durable output

Large new raw goes to:

`/root/share/mnt164/huangrulin/awma_q05_context_effect_decomposition_v1/`

174 local disk remains source/worktree/small scratch only.

## 12. Deliverables

Report:

`docs/vm_tlb/codex_handoff/awma/Q05_CONTEXT_EFFECT_DECOMPOSITION_174NEW_V1_REPORT.md`

Review pack:

`docs/vm_tlb/review_packs/AWMA_Q05_CONTEXT_EFFECT_DECOMPOSITION_174NEW_V1/`

At minimum:

```text
README.md
SOURCE_ANCHORS.md
EXISTING_RUN_CONTEXT_COUNTER_MATRIX.tsv
NATURAL_CONTRAST_AUDIT.md
TARGET_ONLY_I0_SEMANTIC_CONTRACT.md
DIAGNOSTIC_BINARY_RECEIPT.md
NEUTRALITY_RESULTS.tsv
CONTEXTUAL_TARGET_I0_RESULTS.tsv
TRANSLATION_SENSITIVITY_SUMMARY.tsv
P8_VS_P34_SCREENING_REFERENCE_AUDIT.md
L2_TARGET_BOUNDARY_ABLATION.md          # if attempted or explicitly skipped
RUN_RECEIPTS.json
RAW_DATA_INDEX.tsv
SHA256SUMS
```

Success marker:

`AWMA_Q05_CONTEXT_EFFECT_DECOMPOSITION_174NEW_V1_COMPLETE_WITH_SCOPE`

Then commit -> push -> remote verify -> clean worktree -> STOP.
