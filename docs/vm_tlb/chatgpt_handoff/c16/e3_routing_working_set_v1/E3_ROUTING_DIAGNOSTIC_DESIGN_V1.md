# C16 E3 — Routing-Driven Active-Expert Working-Set Diagnostic V1

## Status

This is the next authorized C16 mainline **diagnostic design** after the accepted three-lineage MoE consumer and the scientific-log consolidation.

This stage is intentionally lightweight first.

It does **not** authorize:
- a new TLB/cache mechanism;
- full NVBit/NCU/NSYS capture for all four routing conditions;
- decode cross-step reuse claims;
- new model download;
- new expert/layer fishing.

The first goal is to determine whether routing organization materially changes the **whole MoE-region execution behavior** enough to justify deeper memory capture.

---

# 1. Scientific motivation

The accepted three-lineage consumer established that Q30, DeepSeek and OLMoE all show:

- weight/input event balance near 50/50;
- output events extremely small;
- OTHER = 0;
- 243 selected static paths for the accepted expert-down-proj anchors.

However, these common properties are better explained first by the shared `down_proj / GEMV` structure and the observed cuBLAS gemvx deployment family than by sparse routing itself.

Therefore the next question moves one level upward:

> **When model, layer, tensor shape, E, top-k, dtype, expert backend and timing boundary are held fixed, does changing the routing pattern change MoE-region fragmentation, dispatch/combine cost, active-expert weight working set, or execution structure?**

This is the first test aimed at a truly MoE-specific variable: **which experts become active and how assignments are distributed among them**.

---

# 2. Primary model and accepted starting asset

Primary model:

`Qwen3-30B-A3B`

Use the already accepted S2/T2048 exact-state/replay assets on node109.

Relevant accepted replay authority:

`hrl/c16-qwen3-30b-s2-state-replay-109-v1@ee67225edc8fc5868de585d38e0391cbeb755d9f`

Primary target region:

- S2/T2048 prefill
- Layer24 MoE block
- M = 2048 token rows
- E = 128 routed experts
- k = 8 experts/token
- total assignments = M × k = 16,384

Historical accepted routing census for this exact state reports Layer24 prefill:
- assignments = 16,384
- unique experts = 92

These historical values are expectations only. Recompute them in the E3 harness before using them.

The existing exact-state replay must be used. Do not regenerate a semantically different hidden-state pool merely because it is easier to instrument.

---

# 3. Experimental variable: four routing conditions

All four conditions use the same frozen hidden-state matrix, same model weights, same expert backend, same dtype/layout and same MoE-region code path wherever possible.

Every token must always select exactly k=8 **distinct** expert IDs.

The only intended variable is routing organization.

## N — Natural routing

Definition:

- run the accepted model router on the frozen hidden state;
- persist exact natural `selected_experts[M,k]` and `routing_weights[M,k]`;
- use these frozen natural outputs as the routing input to the MoE body.

For body timing, use the same boundary as the synthetic conditions:

`dispatch -> expert compute -> combine`

Router time is measured separately.

N is the reference for real model behavior.

## U — Balanced routing

Purpose:

> Test whether a commonly used balanced/uniform expert-load proxy adequately represents the natural route for this fixed region.

Requirements:

- same M=2048, E=128, k=8;
- total assignments = 16,384;
- every expert receives exactly 128 assignments;
- each token has 8 distinct expert IDs;
- preserve each token's natural routing-weight vector exactly; replace only the selected expert IDs;
- mark this condition `SYNTHETIC_ROUTING`.

Use a deterministic balanced construction and persist its exact route matrix and SHA.

A simple acceptable construction is any deterministic mapping that satisfies all invariants exactly; the implementation must record the algorithm rather than depending on an opaque random sampler.

Do not call U “real model inference”.

## H — Concentrated/hot-set routing

Purpose:

> Stress sensitivity to a very small active-expert set while keeping total assignment work fixed.

Construct the fixed hot set as:

- the k=8 most frequently selected experts under N;
- ties broken by ascending expert ID.

For every token:
- select exactly those same 8 distinct experts;
- preserve that token's natural 8 routing weights in slot order;
- total assignments remain 16,384;
- each hot expert receives 2,048 assignments;
- mark `SYNTHETIC_ROUTING`.

H is an extreme diagnostic only.

A large H effect by itself does **not** justify a claim that natural MoE execution suffers from severe hotspot behavior.

## P — Natural-histogram-preserving token/order permutation

Purpose:

> Test whether token/order/dispatch organization matters when the natural expert histogram and exact token/expert semantics are preserved.

Construct one deterministic permutation `perm[0:M]`.

Apply the same permutation jointly to:
- hidden states;
- natural selected expert IDs;
- natural routing weights.

Run the MoE body, then inverse-permute the output.

Required invariants:
- exact natural per-expert assignment histogram preserved;
- exact active expert set preserved;
- exact per-token route IDs/weights stay paired with the corresponding token hidden state;
- inverse-permuted output must reproduce the N-body output under the accepted deterministic/equivalence rule.

Persist:
- permutation algorithm/seed;
- permutation SHA;
- inverse-permutation SHA;
- equivalence receipt.

P is not a different routing distribution. It is an ordering/dispatch diagnostic.

---

# 4. Timing and semantic boundary

## 4.1 Compare the same body boundary

Primary comparison:

`dispatch -> expert compute -> combine`

For N/U/H/P, compare this same body boundary.

For N only, separately record:

`router`

Do not include router time in N while excluding it from U/H/P.

Report:
- router time
- body total time
- dispatch time if the implementation exposes a defensible boundary
- expert-compute time if defensibly separable
- combine time if defensibly separable

If the current implementation does not expose trustworthy sub-boundaries without intrusive changes, report only:
- router
- full body

and record the limitation. Do not invent fake sub-times.

## 4.2 First-round timing protocol

Use uninstrumented native execution.

Initial protocol:
- 2 warmup iterations;
- 5 measured iterations per condition;
- preserve all individual measurements;
- report median, min, max and coefficient of variation.

Use a deterministic interleaved/rotated condition order to reduce simple thermal/order drift.

Do not use NCU timing as the native execution time.

---

# 5. Required first-round observations

This first E3 round is deliberately **lightweight**.

For each N/U/H/P record:

## Routing structure
- total assignments
- active expert count
- per-expert assignment histogram
- histogram CV
- max / median / min assignments among active experts
- top-expert assignment fraction
- selected-expert matrix SHA
- routing-weight matrix SHA
- per-token distinct-ID validation

## Expert-call structure
From the actual runtime dispatch/expert path:
- number of expert calls / non-empty expert groups;
- token rows per expert call;
- distribution of expert batch sizes;
- exact expert IDs called;
- whether the backend/code path changes across conditions.

Do not infer GPU kernel equivalence from Python call count alone.

## Semantic active-weight capacity
Compute from the actual loaded expert parameters:
- bytes of expert weights per expert for the complete expert MLP region;
- active-expert weight capacity = union of weights for active experts;
- report gate/up/down components separately if present.

Label this clearly:

`SEMANTIC_ACTIVE_WEIGHT_CAPACITY`

This is **not observed memory traffic** and **not an actual page/line footprint**.

## Native timing
- router time (N only)
- body time N/U/H/P
- any trustworthy sub-stage timing
- raw repeats and variability

---

# 6. Qualification gates

Before trusting the matrix:

## Gate A — exact N replay

Require:
- accepted hidden-state/state identity closes;
- natural router result is deterministic under the frozen replay;
- N-body output matches the accepted/original MoE-region output under the existing exact replay contract.

## Gate B — P equivalence

Require:
- natural histogram preserved exactly;
- active expert set preserved exactly;
- inverse-permuted P output equals the N-body output under the accepted deterministic equivalence rule.

If P equivalence does not close, stop using P as an ordering diagnostic until the discrepancy is explained.

## Gate C — U/H invariants

Require:
- every token has exactly 8 distinct expert IDs;
- total assignments exactly 16,384;
- U: every one of 128 experts has exactly 128 assignments;
- H: only the fixed 8 experts are active and each has exactly 2,048 assignments;
- route weights retain the frozen per-token natural values;
- same expert backend/layout/dtype remains in use.

U/H outputs are expected to differ from N. Do not require semantic output equality.

---

# 7. What this first round does NOT measure

No full-address capture is required yet.

Do not claim from this round:
- actual 128B/4K/64K/2M touched footprint;
- cache hit/miss behavior;
- TLB hit/miss behavior;
- cross-step expert reuse;
- reuse distance;
- L2 arrival order;
- end-to-end model accuracy for U/H synthetic routes.

In particular:

> Decode cross-step expert reuse is a separate future question and is not mixed into this M=2048 four-condition experiment.

---

# 8. Decision after the lightweight matrix

The first round should stop and produce evidence for review.

## Case A — N and U are close

If N and U have similar body timing/expert-call structure within observed run-to-run variability:

Interpretation:

> For this model/shape/backend and these metrics, balanced routing is an adequate proxy.

Do not deepen E3 merely to force a difference.

## Case B — N and U differ reproducibly

If N and U differ beyond ordinary repeat variability in body timing, expert fragmentation or backend structure:

Authorize a **separate reviewed deep-capture stage**, not automatically in this Goal.

Preferred detailed pair:
- N
- U

The next capture may then measure actual object/line/page behavior.

## Case C — only H differs strongly

Interpretation:

> The implementation is sensitive to an extreme hot-set route.

Do not convert this into a natural-routing bottleneck claim.

## Case D — P differs from N after equivalence closes

Interpretation:

> Ordering/dispatch organization matters even with the natural expert histogram and semantics preserved.

This would justify a focused dispatch/order investigation before any memory mechanism.

---

# 9. Independent validation policy

Do not consume all validation assets in the first round.

If the primary Q30 TEXT result is scientifically interesting, the next reviewed validation should be:

1. a held-out Q30 CODE input if an already-qualified exact state is available without inventing a new capture; and/or
2. a predeclared OLMoE N/U comparison as an independent model family.

DeepSeek is not required in the first E3 validation because it adds additional MoE/shared-expert/runtime complexity that is not necessary for the first controlled-routing test.

---

# 10. Required review pack

Suggested:

`docs/vm_tlb/review_packs/C16_E3_Q30_ROUTING_DIAGNOSTIC_109_V1/`

At minimum:
- `UPSTREAM_AUTHORITY.json`
- `TARGET_REGION_QUALIFICATION.json`
- `NATURAL_ROUTING.json`
- `ROUTING_CONDITIONS.json`
- `ROUTE_INVARIANTS.json`
- `P_EQUIVALENCE.json`
- `EXPERT_CALL_STRUCTURE.json`
- `SEMANTIC_ACTIVE_WEIGHT_CAPACITY.json`
- `NATIVE_TIMING.tsv`
- `TIMING_SUMMARY.json`
- `SCIENTIFIC_INTERPRETATION.md`
- `NEXT_STEP_DECISION.json`
- `SHA256SUMS`

Also update:

`docs/vm_tlb/scientific_logs/C16_MOE_EXPLORATION_LOG.md`

with:
- Question
- Evidence
- Result
- Interpretation
- Superseded
- Next question
- Stop condition

---

# 11. Stop boundary

This Goal ends after the lightweight N/U/H/P diagnostic and Git closure.

Do not automatically launch:
- NVBit
- NCU
- NSYS
- full memory trace
- OLMoE validation
- CODE holdout
- decode cross-step routing sequence
- new TLB/cache mechanism

Those are chosen only after reviewing the first-round result.
