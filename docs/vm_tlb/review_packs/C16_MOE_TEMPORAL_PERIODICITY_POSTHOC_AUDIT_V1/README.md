# C16 MoE temporal periodicity post-hoc audit V1

Status: `POST_HOC_DIAGNOSTIC_ONLY`

## Outcome

Primary label: `POSTHOC_PERIOD11_SIGNAL_CONFIRMED`.

Qualifications:

- `POSTHOC_PERIOD11_SIGNAL_ASSOCIATED_WITH_TOKEN_REPETITION`
- `POSTHOC_PERIOD11_ORIGIN_UNRESOLVED`

This addendum does not modify or reinterpret the V1 primary decision: `TEMPORAL_AUTHORITY_INSUFFICIENT_CROSS_MODEL`.

## Authority

- OLMoE V34 producer: `ab26365dc663268b0799818db6687ed466e8c925`
- accepted V40 descendant: `85563ec6f55a0ad743d21483aa49c24fdb5cf3bf`
- source: `docs/vm_tlb/review_packs/C16_OLMOE_S2_PRODUCER_109_V34/NATURAL_TOP8_ROUTING.json`
- source SHA-256: `d973b1f2915bb7d5bfd47f0b83b1a8c19106f51ecacfe89ba359ab3a6a3207c3`
- natural layer-1 top-8, 32 consecutive steps, no forced routing

No GPU, node109 access, profiler, cache simulation, new capture, new mechanism, Lane 4 result, or V1 edit was used.

## Review order

1. `LAG_SPECTRUM.tsv` — complete actual lag 1–16 spectrum
2. `LAG_SHUFFLE_CONTROL.tsv` — per-lag 1,000-permutation controls
3. `PERIOD11_PAIR_AUDIT.tsv` — all 21 `(t,t+11)` pairs
4. `TOKEN_ASSOCIATION.json`
5. `GENERATION_PROVENANCE_AUDIT.md`
6. `SCIENTIFIC_INTERPRETATION.md`
7. `FINAL_DECISION.json`
8. `SHA256SUMS`

## Definitions

- Expert objects are layer-qualified; this pack analyzes OLMoE layer 1 only.
- Top-k rank is not treated as kernel order.
- Overlap is intersection size, Jaccard is intersection/union, retention is intersection/8.
- `exact_set_equal` and `unordered_set_equal` both mean equality of unordered top-8 sets; `ordered_topk_equal` separately tests list equality.
- `near_repeat` means non-exact intersection ≥7 of 8.
- Each lag resets `Random(20260928)`, performs `1000` whole-step permutations, and preserves every top-8 set and its marginal frequency/co-selection.
- Shuffle p05/median/p95 use R-7 linear quantiles and are descriptive, not preregistered significance thresholds.
- Token-conditioned summaries use all 496 unordered step pairs and separately report the 21 lag-11 pairs.

## Validation

The generator hard-fails on V34→V40 ancestry, source SHA, natural-routing flag, 32-step continuity, top-8 legality, route-weight length, token presence, and router SHA presence. Structured file counts, deterministic regeneration, `sha256sum -c`, `git diff --check`, fetch-back equality, and a clean final worktree are required.

Generator: `util/vm_tlb/c16/moe_temporal_periodicity_posthoc_audit.py`.
