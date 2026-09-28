# C16 MoE temporal routing authority screen V1

## Outcome

Primary decision: `TEMPORAL_AUTHORITY_INSUFFICIENT_CROSS_MODEL`.

The audit recovered Q30's explicit 4-step × 48-layer sequence from accepted node164 authority, confirmed DeepSeek remains single-state-only, and validated OLMoE's natural 32-step layer-1 sequence through the V34→V40 ancestry and checksum chain. Only explicit sequences were analyzed. No GPU work, cache simulation, or timing analysis was performed.

OLMoE's authority/integrity result is `OLMOE_SINGLE_LAYER_TEMPORAL_SCREEN_PASS`; “pass” means the bounded screen completed on valid authority, not that it found a positive signal. Its actual adjacent metrics lie within the shuffle p05–p95 intervals. It must not be generalized to full-model cache behavior. Q30 is explicitly `LOW_TEMPORAL_POWER`.

## Review order

1. `TEMPORAL_AUTHORITY_AUDIT.tsv`
2. `CROSS_LINEAGE_COMPARABILITY.md`
3. `SCIENTIFIC_INTERPRETATION.md`
4. `FINAL_DECISION.json`
5. Metric/control details in `EXPLICIT_SEQUENCE_INDEX.tsv`, `TEMPORAL_SET_METRICS.tsv`, and `MARGINAL_PRESERVING_SHUFFLE_CONTROL.json`
6. `MINIMAL_ROUTING_CAPTURE_PLAN.md` (plan only; not authorization)

## Metric definitions

- Object identity is `(layer_id, expert_id)`; expert IDs are never mixed across layers.
- Each decode step is an unordered exact top-k set. Route rank is not kernel-call order.
- Overlap is intersection cardinality; Jaccard is intersection/union; retention is intersection/k.
- Lag 1/2/4/8 uses pairs exactly that many decode steps apart and is reported only when the sequence is long enough.
- Top1/top4 frequency concentration is the share of all step selections held by the one/four most frequent experts in that layer.
- Exact-set repeats count occurrences after the first occurrence of the same unordered set.
- Per-expert reuse-within-W is the fraction of consecutive expert arrivals whose decode-step distance is at most W; experts selected once receive JSON `null`.
- Longest absence gap is the longest run of observed steps not selecting that expert, including leading/trailing boundaries.
- Shuffle quantiles use R-7 linear interpolation. Seed `20260928`, `1000` permutations per sequence.

## Provenance and validation

- Base/consumer commit: `08536be9940590be101c7f5bac2117ba82056db5`.
- Q30 producer: `28620a89d55fd9230103a31d31d14757b57e1e0f`; explicit source SHA `07b68ead81d9471c46b9fadc77077f80a192d74f109be41b8c17e03280ed58dd`.
- DeepSeek producer: `baf892ced6d66cbacabb995caf095e5280995097`; routing receipt SHA `85027da8c989d5d811d4c4a275d1ad03cf482a7d63f4f4edab43658e118c84fc`.
- OLMoE producer V34: `ab26365dc663268b0799818db6687ed466e8c925`; accepted V40: `85563ec6f55a0ad743d21483aa49c24fdb5cf3bf`; routing SHA `d973b1f2915bb7d5bfd47f0b83b1a8c19106f51ecacfe89ba359ab3a6a3207c3`.
- Generator: `util/vm_tlb/c16/moe_temporal_routing_screen.py`.
- `SHA256SUMS` covers every review-pack file except itself.

The generator hard-fails on source SHA, ancestry, step continuity, layer coverage, top-k legality, forced routing, token binding, and router hash invariants.

Authority search covered the three accepted producer commits/review packs, the Q30 accepted node164 replay-state archive, the DeepSeek accepted node164 raw bundle and catalog binding, and node164 durable provenance/catalog locations. No Lane 4 path or partial result was read.

## Change and validation summary

This branch contains one reproducible CPU-only generator plus this ten-file review pack; no model, simulator, cache/TLB, trace, configuration, accepted authority, or handoff file is modified. The branch starts at accepted consumer commit `08536be9940590be101c7f5bac2117ba82056db5`; the stage commit is the single commit immediately above that base.

Validation consists of Python bytecode compilation, structured JSON/TSV assertions, independent `sha256sum -c`, deterministic regeneration comparison, `git diff --check`, fetch-back commit equality, and final clean-worktree verification.

## Open authority gaps

- DeepSeek has no accepted/durable multi-step explicit routing sequence.
- Q30 has all 48 layers but only four decode steps, so temporal power is low.
- OLMoE has 32 steps but only layer 1, so it cannot support full-model cache/capacity conclusions.
- `MINIMAL_ROUTING_CAPTURE_PLAN.md` is a plan only and requires fresh user authorization before any GPU work.
