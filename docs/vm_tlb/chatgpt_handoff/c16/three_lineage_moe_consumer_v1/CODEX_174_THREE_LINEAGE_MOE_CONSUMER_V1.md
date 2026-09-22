# CODEX 174-new — C16 Three-Lineage MoE Consumer V1

## Goal mode

Execute this as one CPU-side Goal on 174-new.

This is a **consumer analysis only**. Do not launch GPU work, do not contact node109 for new capture, do not modify node164 accepted raw/catalog, and do not start a TLB/cache mechanism experiment.

Suggested execution branch:

`hrl/c16-three-lineage-moe-consumer-174new-v1`

---

## Mandatory first reads

Fetch and verify the ChatGPT handoff branch:

`hrl/c16-three-lineage-moe-consumer-handoff-v1`

Read completely:

1. `docs/vm_tlb/chatgpt_handoff/c16/three_lineage_moe_consumer_v1/CURRENT_STATE.md`
2. `docs/vm_tlb/chatgpt_handoff/c16/three_lineage_moe_consumer_v1/ANALYSIS_CONTRACT_V1.md`
3. this file

Then read as historical/reference evidence:

- V25 two-lineage review pack:
  `docs/vm_tlb/review_packs/C16_Q30_DEEPSEEK_TWO_LINEAGE_MOE_174NEW_V25/`
- Q30 producer V3 review pack:
  `docs/vm_tlb/review_packs/C16_QWEN3_30B_S2_FORMAL_CAPTURE_109_V3/`
- DeepSeek V23R1 review pack:
  `docs/vm_tlb/review_packs/C16_DEEPSEEK_V2_LITE_S2_PRODUCER_109_V23R1/`
- OLMoE V40 authority review pack:
  `docs/vm_tlb/review_packs/C16_OLMOE_V40_FORMAL_ADMISSION_174NEW_V1/corrected_fc0f3cf67edf/`

Historical summaries are references only. Recompute scientific metrics from accepted raw authority.

---

## Stage 0 — resource and authority preflight

Check:
- node164 mount health
- free storage
- CPU/RAM
- current I/O load
- Git status/worktree

Do not copy the three raw bundles to local 174 storage unless a small temporary index is necessary.

Verify the three accepted raw roots and their authority bindings exactly as listed in `CURRENT_STATE.md`.

Create `AUTHORITY_AUDIT.json`.

If any raw/catalog/ACK identity is missing or inconsistent, fail closed before scientific synthesis.

---

## Stage 1 — build/reuse one common consumer

Prefer reusing the accepted V25 analysis semantics and existing C16 readers rather than inventing a new incompatible interpretation.

Implement the minimum common adapter needed to read:
- Q30 accepted raw bundle
- DeepSeek accepted raw bundle
- OLMoE accepted raw bundle

The final common metric definitions must follow `ANALYSIS_CONTRACT_V1.md`.

Do not align static indices across models.

Do not read old summary numbers as inputs to the recompute.

---

## Stage 2 — recompute the three lineages

The three lineage recomputes are independent after Stage 0.

Before launching, inspect CPU/RAM/I/O. If resources are safe, run Q30, DeepSeek, and OLMoE recomputes in parallel. If node164 I/O is the bottleneck, use the highest safe concurrency rather than mechanically forcing 3.

Each recompute must produce:
- semantic scope
- selected/executed/zero/failed
- dynamic warp records
- active-lane events
- typed role event counts/fractions
- per-executed-shard event distribution
- per-executed-shard 128B/4K/64K/2M footprint distributions
- normalized per-shard spatial-density descriptors
- role-conditioned shard behavior where evidence is unambiguous
- static implementation summary from durable evidence

Write:
- `Q30_RECOMPUTE.json`
- `DEEPSEEK_RECOMPUTE.json`
- `OLMOE_RECOMPUTE.json`
- one full per-shard TSV for each

---

## Stage 3 — reproduce accepted historical results before extending them

After recompute finishes, compare against historical accepted references.

Q30 and DeepSeek must reproduce V25 within identical metric definitions.

OLMoE must reproduce V40 authority closure.

Create:
`HISTORICAL_REPRODUCTION_CHECK.json`

For every compared field record:
- recomputed value
- historical value
- equal / explained schema difference / mismatch

Do not continue to a three-lineage scientific claim on an unexplained mismatch.

Routine parser/layout mistakes are solve-and-continue.

---

## Stage 4 — scope and implementation alignment

Create:
- `SCOPE_ALIGNMENT.json`
- `IMPLEMENTATION_RELATION.json`

Explicitly record:

### Model-semantic commonality
All three are accepted natural-routed BF16 expert `down_proj` anchors.

### Important differences
- Q30: Layer24 Decode3, Expert21, 768 -> 2048, top-8/128
- DeepSeek: Layer1 selected decode state, Expert4, 1408 -> 2048, top-6/64 routed + 2 shared
- OLMoE: Layer1 decode32, Expert58, 1024 -> 2048, top-8/64, actual-JIT variant A conditioned

### Runtime implementation relation
Audit exact durable function/template evidence.

Expected historical relation:
- Q30: internal gemvx template specialization with `...,7,...`
- DeepSeek: internal gemvx specialization with `...,6,...`
- OLMoE variant A: internal gemvx specialization with `...,6,...`

Do not assume this expectation is correct without checking durable evidence.

If DeepSeek and OLMoE are the same/near-identical gemvx specialization, say explicitly:

> independent model lineages, but coupled runtime implementation family

This caveat is mandatory in final interpretation.

---

## Stage 5 — three-lineage comparison

Generate the common comparison outputs required by the analysis contract.

At minimum evaluate:

### A. Object composition
For WEIGHT / INPUT / OUTPUT / OTHER:
- event counts
- fractions
- weight-input fraction delta
- output fraction

### B. Static execution coverage
For each lineage:
- selected count
- executed count/fraction
- zero count/fraction

Do not treat equal selected count 243 as proof of equivalent static code.

### C. Event scale
Compare per-executed-shard active-lane-event distributions:
- min
- p25
- median
- p75
- p90
- max

### D. Spatial footprint
Compare per-executed-shard:
- unique 128B lines
- 4K pages
- 64K pages
- 2M pages

Report same quantiles.

### E. Normalized spatial density
Per shard:
- lines / active-lane events
- pages / active-lane events

Compare distributions.

These are descriptive density metrics only, not cache/TLB metrics.

### F. Role-conditioned behavior
Where possible compare:
- WEIGHT shards
- INPUT shards
- OUTPUT shards

Do not force MIXED/ambiguous shards into a pure role.

### G. Static implementation structure
Compare path/load/store/opcode-family counts only when the same definitions can be recomputed from durable evidence.

No static-index cross-model mapping.

---

## Stage 6 — classify every scientific observation

Use the categories from the analysis contract:

- `T3` = observed in all three model lineages
- `T2` = only two-lineage
- `L1` = lineage-specific
- `U` = unresolved/not comparable

Create:
`PATTERN_CLASSIFICATION.json`

At minimum classify:
- weight/input approximately balanced
- output fraction small
- other/unclassified zero or nonzero
- static execution coverage behavior
- event-distribution shape
- line/page footprint behavior
- normalized spatial-density behavior
- implementation coupling

Do not use an arbitrary numerical threshold silently. If “approximately balanced” or “small” is used, define the descriptive threshold or simply report exact values and classify directionally.

---

## Stage 7 — scientific interpretation

Write:

`SCIENTIFIC_INTERPRETATION.md`

Required sections:

1. What is common across all three accepted model lineages
2. What differs materially
3. What may be explained by shared kernel implementation rather than MoE semantics
4. What this does and does not justify studying next

The strongest allowed wording, if supported, is:

> Across the three accepted independent model lineages, the natural-routed expert down_proj anchors show a shared descriptive pattern under the observed cuBLAS gemvx deployments: ...

Then state the implementation-coupling limitation immediately.

Do not write:
- “all MoE models”
- “universal MoE law”
- “MoE causes X”
- “routing causes X”
- “TLB/cache bottleneck” from these traces alone

---

## Stage 8 — final decision and next-step boundary

Create:
- `FINAL_DECISION.json`
- `NEXT_STEP_AUTHORIZATION.json`

This Goal should **not automatically authorize**:
- new GPU capture
- new model
- new expert/layer
- E3 routing manipulation
- TLB/cache mechanism work

It may list a small number of evidence-driven candidate questions for ChatGPT/user review.

Preferred final state if all evidence closes:

`C16_THREE_INDEPENDENT_MODEL_LINEAGE_MOE_CONSUMER_V1_PASS`

with explicit implementation-coupling caveat.

---

## Review pack and Git closure

Create:

`docs/vm_tlb/review_packs/C16_THREE_LINEAGE_MOE_CONSUMER_174NEW_V1/`

Include every output required by `ANALYSIS_CONTRACT_V1.md`.

Generate `SHA256SUMS`.

Then:
- commit
- push
- canonical remote verify
- clean worktree
- STOP

Do not modify accepted node164 raw/catalog data.

---

## Solve-and-continue

Solve ordinary engineering issues yourself:
- old bundle layout differences
- parser adapters
- field naming
- quantile implementation
- TSV/JSON output
- CPU parallelism
- Git

Stop for review only if:
- an accepted authority identity is actually inconsistent
- Q30/DeepSeek/OLMoE raw recompute cannot reproduce accepted historical evidence
- the three datasets are not semantically comparable under the stated scope
- claim boundaries need to change materially
