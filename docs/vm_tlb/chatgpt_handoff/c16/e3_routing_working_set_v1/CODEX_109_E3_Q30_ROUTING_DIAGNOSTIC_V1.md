# CODEX 109 — C16 E3 Q30 Routing Diagnostic V1

## Goal

Run the first **lightweight** E3 routing diagnostic on node109 using the accepted Qwen3-30B-A3B S2/T2048 exact-state/replay.

Do not start deep tracing or mechanism work.

Suggested execution branch:

`hrl/c16-e3-q30-routing-diagnostic-109-v1`

## Mandatory first reads

Fetch and verify:

`hrl/c16-e3-routing-working-set-handoff-v1`

Read:

1. `docs/vm_tlb/chatgpt_handoff/c16/e3_routing_working_set_v1/E3_ROUTING_DIAGNOSTIC_DESIGN_V1.md`
2. `docs/vm_tlb/scientific_logs/C16_MOE_EXPLORATION_LOG.md`
3. this file

Use accepted upstream Q30 replay authority:

`hrl/c16-qwen3-30b-s2-state-replay-109-v1@ee67225edc8fc5868de585d38e0391cbeb755d9f`

## Execution target

Primary region:

- Qwen3-30B-A3B
- accepted S2/T2048 prefill state
- Layer24 MoE block
- M=2048
- E=128
- k=8
- 16,384 assignments

Recompute the natural routing census from the actual frozen state before proceeding.

Historical expectation:
- 16,384 assignments
- 92 unique experts

Do not use the historical value as the runtime input truth.

## Implement one bounded route-injection harness

Keep the original model weights, hidden states, dtype/layout and expert backend.

Freeze natural router outputs once:
- selected expert IDs
- routing weights

Use the same body boundary for all conditions:

`dispatch -> experts -> combine`

Measure router separately for N.

Implement exactly the N/U/H/P contracts in the design document.

Critical invariants:

- every token has exactly 8 distinct expert IDs;
- 16,384 total assignments in every condition;
- U: all 128 experts receive exactly 128 assignments;
- H: fixed natural top-8 experts only, each receives 2,048 assignments;
- U/H preserve each token's natural route-weight vector;
- P preserves exact natural histogram/active set and inverse-permuted output reproduces N.

Mark U/H as `SYNTHETIC_ROUTING`.

## First-round measurements only

No NVBit, NCU, NSYS, or full address trace.

Run:
- 2 warmups;
- 5 measured iterations per condition;
- deterministic interleaved/rotated N/U/H/P order.

Record raw repeats.

Produce:
- routing histograms / CV / active expert counts;
- top-expert fraction;
- expert call/group count and per-expert token batch sizes;
- actual loaded full-expert MLP weight bytes per expert;
- `SEMANTIC_ACTIVE_WEIGHT_CAPACITY` per condition;
- router time;
- common MoE-body time;
- trustworthy dispatch/expert/combine sub-times only if the implementation exposes defensible boundaries without intrusive redesign;
- min/median/max/CV timing.

Do not call semantic active-weight capacity observed traffic.

## Gates

Require:
- exact accepted N state/replay closure;
- natural router determinism;
- N-body output equivalence to accepted/original region;
- P inverse-permutation equivalence;
- U/H exact routing invariants;
- unchanged expert backend/dtype/layout.

Ordinary harness/timing/route-generation issues are solve-and-continue.

Stop for scientific review only if accepted state identity cannot close or the required controlled route injection would materially change expert math/backend.

## Output

Create:

`docs/vm_tlb/review_packs/C16_E3_Q30_ROUTING_DIAGNOSTIC_109_V1/`

with the artifacts required by the design document.

Update:

`docs/vm_tlb/scientific_logs/C16_MOE_EXPLORATION_LOG.md`

with:
Question / Evidence / Result / Interpretation / Superseded / Next question / Stop condition.

Commit, push, remote verify, clean worktree, STOP.

Do not automatically start:
- deep memory capture;
- OLMoE validation;
- CODE holdout;
- decode cross-step reuse experiment;
- TLB/cache mechanism work.
