# C16 Three-Lineage MoE Consumer — Analysis Contract V1

## Research question

For three accepted natural-routed MoE expert `down_proj` anchors from independent model lineages:

- Qwen3-30B-A3B
- DeepSeek-V2-Lite
- OLMoE-1B-7B

determine which observed memory-access properties are:

1. shared across all three model lineages;
2. shared by only two lineages;
3. specific to one model/deployment;
4. plausibly coupled to the common cuBLAS gemvx implementation family rather than MoE semantics.

This is descriptive characterization, not a causal MoE experiment.

---

## Required methodology

### A. Re-audit authority before analysis

For each lineage independently verify from node164 authority:
- raw RUN_ID exists;
- manifest identity matches the accepted target;
- positive ACK/catalog bindings exist;
- accepted producer commit exists remotely;
- raw bundle is immutable accepted authority.

Do not modify accepted raw/catalog.

### B. Recompute all three using one consumer definition

Do not build the three-lineage table by copying:
- V25 comparison table;
- producer summary JSON;
- OLMoE receiver final summary.

Those are comparison references only.

Read the accepted raw shard evidence and recompute a common metric set.

It is acceptable to have lineage-specific adapters for old bundle layouts, but the final metric definitions must be identical.

### C. Reproduce historical accepted results first

Before drawing a three-lineage conclusion:

- Q30 recompute must reproduce the accepted V25 Q30 scope/results.
- DeepSeek recompute must reproduce the accepted V25 DeepSeek scope/results.
- OLMoE recompute must reproduce the accepted V40 authority results.

If a historical comparison field cannot be reproduced because the old authority lacks required durable data, mark it `NOT_RECOMPUTABLE_FROM_CURRENT_AUTHORITY`; do not fill it from memory.

A mismatch blocks scientific synthesis until explained.

---

## Common metric schema

For every lineage report:

### 1. Semantic scope

- model/revision
- scenario
- layer
- decode position/state
- selected natural expert
- routing topology
- input width
- output width
- weight shape
- weight bytes
- dtype
- function/kernel family evidence
- grid/block only if directly supported

### 2. Static/dynamic scope

- selected static path count
- executed static count
- proven-zero static count
- failed/excluded count
- executed fraction = executed / selected
- dynamic warp records
- active-lane events

Never compare static indices across models as if index N means the same instruction.

### 3. Typed object composition

Use common output names:

- `WEIGHT`
- `INPUT`
- `OUTPUT`
- `OTHER`

Map lineage-specific historical names such as:
- `EXPERT_DOWN_WEIGHT`
- `EXPERT_WEIGHT`
- `ROUTED_EXPERT_DOWN_INPUT`

into the common names only after preserving the original role in a lineage-specific sidecar.

Report:
- role event counts
- role fractions
- `weight_input_fraction_delta = abs(weight_fraction - input_fraction)`
- output fraction
- other fraction

Do not convert address-event counts to bytes unless exact per-event access width is available and validated consistently across all three lineages.

### 4. Per-executed-shard distributions

For each lineage, from executed shards only, report:

active-lane events:
- min
- p25
- median
- p75
- p90
- max

unique 128B lines:
- min
- p25
- median
- p75
- p90
- max

unique 4K pages:
- same quantiles

unique 64K pages:
- same quantiles

unique 2M pages:
- same quantiles

Use a deterministic quantile definition and record it in the review pack.

Also report the full per-shard table for audit.

### 5. Safe normalized locality descriptors

For each executed shard compute, when denominator > 0:

- `unique_128B_lines / active_lane_events`
- `unique_4K_pages / active_lane_events`
- `unique_64K_pages / active_lane_events`
- `unique_2M_pages / active_lane_events`

Then report the same distribution quantiles per lineage.

These are per-shard spatial-density descriptors only. They are not cache miss rates, TLB miss rates, or reuse metrics.

### 6. Role-conditioned shard behavior

Where an executed shard has a clear dominant/only semantic object role, classify it as:
- WEIGHT
- INPUT
- OUTPUT
- MIXED
- OTHER

Report counts and per-role distributions of:
- active-lane events
- unique 128B lines
- unique 4K pages

Do not force a role classification if the raw evidence is mixed or ambiguous.

### 7. Static implementation structure

For each lineage summarize, from durable static selector/function evidence:
- kernel/function family
- template/variant evidence
- selected path-class counts if reproducible
- load/store counts if reproducible
- opcode-family counts if reproducible

Do not align static indices across models.

Explicitly determine:
- whether DeepSeek and OLMoE use the same exact/near-exact gemvx template variant;
- whether Q30 differs only by template/shape specialization;
- which observed common properties may therefore be implementation-coupled.

---

## Three-lineage comparison logic

Every proposed pattern must be classified into one of:

### T3 — three-lineage observed pattern

All three independently recomputed anchors show the same qualitative property/direction.

This supports:
`THREE_INDEPENDENT_MODEL_LINEAGES_OBSERVED`

It does **not** automatically support implementation independence.

### T2 — two-lineage-only pattern

Exactly two lineages show the property, or the third materially differs.

This downgrades any former two-lineage “common” interpretation.

### L1 — lineage-specific pattern

Only one anchor shows it.

Treat as model/deployment/implementation-specific until further evidence.

### U — unresolved

Evidence definitions/layouts are not sufficiently comparable or one lineage lacks the required durable data.

Do not force a conclusion.

---

## Patterns that must be explicitly tested

At minimum test:

1. **Weight/input balance**
   - are weight and input each approximately half of active-lane address events in all three?
   - quantify exact fractions/deltas.

2. **Output-smallness**
   - is output a consistently tiny fraction in all three?
   - report exact output fraction.

3. **Other/unclassified**
   - is OTHER exactly zero in all three under accepted object maps?

4. **Static execution coverage**
   - selected count is 243 in all three, but executed fraction differs strongly.
   - quantify and treat this as implementation behavior, not semantic equivalence.

5. **Per-shard event-scale shape**
   - compare median/tails of active-lane events.

6. **Per-shard spatial footprint**
   - compare 128B/4K/64K/2M distributions and normalized density descriptors.

7. **Role-conditioned footprint**
   - compare WEIGHT shards vs INPUT shards within each lineage and across lineages.

8. **Implementation coupling**
   - determine whether DeepSeek/OLMoE commonality is partly explained by shared gemvx variant.
   - report Q30 relation separately.

---

## Historical expected values for sanity only

Do not use these as computed inputs.

Q30:
- selected 243
- executed 41
- zero 202
- active-lane events 3,147,776
- historical typed fractions:
  weight 0.4996746909564086
  input 0.4996746909564086
  output 0.0006506180871828237

DeepSeek:
- selected 243
- executed 169
- zero 74
- active-lane events 11,538,432
- historical typed fractions:
  weight 0.4998225062122826
  input 0.4998225062122826
  output 0.0003549875754348598

OLMoE:
- selected 243
- executed 129
- zero 114
- active-lane events 4,196,352
- typed fractions:
  weight 0.4997559785261103
  input 0.4997559785261103
  output 0.0004880429477794046

---

## Required outputs

Create a review pack, suggested path:

`docs/vm_tlb/review_packs/C16_THREE_LINEAGE_MOE_CONSUMER_174NEW_V1/`

At minimum:

- `AUTHORITY_AUDIT.json`
- `SCOPE_ALIGNMENT.json`
- `Q30_RECOMPUTE.json`
- `DEEPSEEK_RECOMPUTE.json`
- `OLMOE_RECOMPUTE.json`
- `Q30_PER_SHARD.tsv`
- `DEEPSEEK_PER_SHARD.tsv`
- `OLMOE_PER_SHARD.tsv`
- `HISTORICAL_REPRODUCTION_CHECK.json`
- `THREE_LINEAGE_COMPARISON.tsv`
- `OBJECT_COMPOSITION_COMPARISON.json`
- `STATIC_EXECUTION_COMPARISON.json`
- `LOCALITY_DISTRIBUTION_COMPARISON.json`
- `ROLE_CONDITIONED_COMPARISON.json`
- `IMPLEMENTATION_RELATION.json`
- `PATTERN_CLASSIFICATION.json`
- `SCIENTIFIC_INTERPRETATION.md`
- `FINAL_DECISION.json`
- `NEXT_STEP_AUTHORIZATION.json`
- `SHA256SUMS`

---

## Scientific interpretation requirements

`SCIENTIFIC_INTERPRETATION.md` must have four sections:

1. **What is common across all three accepted model lineages**
2. **What differs materially**
3. **What may be caused by shared kernel implementation rather than MoE semantics**
4. **What this does and does not justify studying next**

Do not state “MoE universally does X”.

Preferred strongest wording, if evidence supports it:

> Across the three accepted independent model lineages, the natural-routed expert `down_proj` anchors show a shared descriptive pattern under the observed cuBLAS gemvx deployments: ...

Then immediately state the implementation-coupling caveat.

---

## Next-step boundary

This Goal does not start a new experiment.

`NEXT_STEP_AUTHORIZATION.json` should normally state:

- no new capture automatically authorized;
- no new TLB/cache mechanism automatically authorized;
- consumer results are ready for ChatGPT/user review;
- candidate follow-up questions may be listed, but execution waits for review.

The point of this consumer is to decide what evidence is actually worth collecting next.
