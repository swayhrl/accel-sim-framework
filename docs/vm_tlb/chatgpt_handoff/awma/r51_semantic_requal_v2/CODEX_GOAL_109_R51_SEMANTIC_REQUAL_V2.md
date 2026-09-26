# CODEX GOAL — AWMA R51 Semantic-Contract Requalification V2

## Purpose

Continue the accepted R51/R52 lifecycle study from:

- execution commit: `8d7ba9e99d9e80f7111c7832ff3f9595ddbc7f6d`
- prior final state: `R51_R52_NATIVE_QUALIFICATION_INCOMPLETE_V1`

This V2 does **not** erase or weaken the V1 result:
`R51_NOT_QUALIFIED_SOFTWARE_SAFEPOINT_NUMERIC_CONTRACT_NOT_CLOSED`
remains permanently true for the strict bitwise-output contract.

V2 asks a narrower application-semantic question:

> For the frozen Qwen greedy-decode workload, do the pre-registered B8/B32 software safe-point implementations preserve the exact application-visible decode decision strongly enough to qualify the already-designed overlap experiment?

If yes, finish the original 25%/50% R51 overlap timeline in this same Goal.
If no, close R51 without further implementation search.

R52 remains only a lifecycle special case.

Repository:
`swayhrl/accel-sim-framework`

Coordination branch:
`hrl/awma-r51-semantic-contract-requal-handoff-v2`

Accepted base:
`8d7ba9e99d9e80f7111c7832ff3f9595ddbc7f6d`

Stage:
`AWMA_R51_SEMANTIC_CONTRACT_REQUALIFICATION_V2`

Execution node:
**109 / RTX4080 / SM89**

Do not run Accel-Sim.
Do not start 174.
Do not download a model.
Do not patch the NVIDIA driver.
Do not invent new chunk counts.

---

# 0. Required reading / frozen assets

Read the full V1 review pack:

`docs/vm_tlb/review_packs/AWMA_R51_R52_TASK_LIFECYCLE_QUALIFICATION_V1/`

Required:
- `TARGET_IDENTITY_RECEIPT.json`
- `PREREGISTRATION.json`
- `BACKGROUND_CORRECTNESS.tsv`
- `BACKGROUND_STANDALONE_TIMING.tsv`
- `NUMERIC_ATTEMPT_AUDIT.json`
- `R51_DECISION.md`
- `R52_INVALIDATION_AUTHORITY_AUDIT.md`
- `FINAL_DECISION.md`

Also read Round05:
`hrl/awma-chatgpt-literature-notes-v1 @ d6a10f0209a024edb4612b1f53edb61d6e39bd18`

Do not rerun V1 standalone timing merely to refresh numbers.
Reuse accepted V1 raw/results if source, tensor, runtime, driver, and implementation hashes still match.

Frozen V1 facts:
- real Qwen lm_head background identity is closed;
- B0 median = 0.412544 ms;
- B8 median = 0.456416 ms, +10.635%;
- B32 median = 0.482016 ms, +16.840%;
- B8/B32 fail strict B0 bitwise logits;
- stream priorities low=0, high=-5 exist;
- foreground layer-12 Flash SDPA identity/output is closed;
- no real R52 online invalidation authority exists.

---

# 1. Scientific scope and claim boundary

The frozen workload uses greedy next-token selection.

For this V2, define the application-visible numerical contract:

`GREEDY_DECODE_SEMANTIC_EQUIVALENCE_V1`

This contract is **not**:
- bitwise-logit equivalence;
- general sampling-distribution equivalence;
- a claim for arbitrary temperature/top-p decoding;
- permission to ignore numerical changes.

It is explicitly scoped to the frozen greedy-decode workload.

V1 strict-logit failure remains documented and must be carried into every final report.

---

# 2. Phase A — freeze semantic contract before checking pass/fail

Create `SEMANTIC_PREREGISTRATION.json` before computing V2 pass/fail.

Bind:

Primary state:
- accepted S2_TEXT decode step 16 hidden state from V1.

Holdout states:
- exactly decode steps **8 and 24** from the same accepted Qwen S2_TEXT greedy trajectory.
- Capture only if not already present.
- Same model/revision/input/runtime identity.
- No alternative scenario/model if a holdout fails.

For each state compare B0/B8/B32.

Required application-semantic checks:

1. exact output shape/dtype;
2. finite logits;
3. **exact argmax token ID equality** B8==B0 and B32==B0;
4. exact top-8 token-ID set equality;
5. exact top-1/top-2 ordering;
6. record, but do not gate on:
   - different FP16 element count;
   - max abs;
   - mean abs;
   - FP16 ordered-code distance if implemented correctly.

Why these gates:
- argmax is the actual frozen greedy decoder decision;
- top-8 set and top-1/top-2 order are conservative stability guards;
- no post-hoc absolute-error tolerance is introduced.

Do not choose a numeric tolerance after reading the V1 max difference.

Semantic states:

- `SEMANTIC_EQUIVALENCE_PASS`
  only if B8 and B32 pass all required gates for primary + both holdouts.

- `SEMANTIC_EQUIVALENCE_FAIL`
  if either safe-point arm fails any required gate on any frozen state.

If FAIL:
- final R51 = `R51_APPLICATION_SEMANTIC_SAFEPOINT_NOT_QUALIFIED`
- no formal overlap run;
- STOP after closure.

No third implementation attempt is allowed.
Do not repair B8/B32 arithmetic in V2.

---

# 3. Phase B — formal overlap timeline, only if semantic PASS

Use the **exact accepted V1 B0/B8/B32 implementations**.

Use the original frozen arrival fractions:
- 0.25
- 0.50

Use original measurement contract:
- one canary;
- 2 warmups;
- 7 formal repetitions;
- one bounded retry for arrival miss;
- actual GPU measurements under
  `/data/c16/locks/c16_gpu_campaign.lock`.

Foreground:
accepted P1 layer-12 Flash SDPA B1.

Background:
accepted lm_head B0/B8/B32.

No new split count, no new arrival point.

## Timeline authority

Use NSYS/CUPTI unified timeline.

For each valid repetition derive:
- `t_bg_start`
- `t_ready`
- `t_submit_end`
- `t_fg_first_kernel_start`
- `t_fg_last_kernel_end`
- `t_bg_end`
- background kernel/chunk at foreground start
- whether foreground/background GPU intervals overlap.

Metrics:
- ready→foreground-start
- submit-end→foreground-start
- ready→foreground-complete
- background completion extension
- foreground standalone-vs-overlap duration.

Do not infer an unobserved internal scheduler event.

## Arrival validity

Keep the V1 envelope:
- target fraction ±0.10 of B0 standalone median;
- background demonstrably active at `t_ready`.

Preserve invalid attempts in raw index.

---

# 4. R51 decision logic

Carry V1 background overheads as accepted unless exact source/runtime identity changed.

For each arrival fraction compare B0/B8/B32.

A handoff improvement is material only if:
1. median ready→foreground-start improves by >=10 us versus B0;
2. improvement exceeds 3x the larger measured latency-jitter envelope;
3. foreground correctness remains exact;
4. V2 semantic contract remains PASS.

Final R51 state must be one:

### `R51_NO_MATERIAL_HANDOFF_DELAY_V2`
B0 itself exposes no material delay or chunking does not materially improve it.

### `R51_SOFTWARE_SAFEPOINT_CLOSES_GAP_V2`
A preregistered B8/B32 arm materially improves handoff and accepted standalone overhead is <=5%.

### `R51_SAFEPOINT_LATENCY_THROUGHPUT_TRADEOFF_SUPPORTED_V2`
A preregistered B8/B32 arm materially improves handoff, but:
- its accepted standalone overhead is >5%, or
- a meaningful handoff residual remains at B32.

### `R51_APPLICATION_SEMANTIC_SAFEPOINT_NOT_QUALIFIED`
semantic gate failed.

Only
`R51_SAFEPOINT_LATENCY_THROUGHPUT_TRADEOFF_SUPPORTED_V2`
may be marked ready for architecture review.

Do not interpret B8/B32's 10.635%/16.840% overhead alone as a positive result; overlap benefit must first be measured.

---

# 5. R52 special case

Do not search for or build a new speculative model.

Carry:
`R52_NO_REAL_INVALIDATION_AUTHORITY`
unless an already-accepted local authority unexpectedly exists.

If R51 formal timeline is completed, compute the previously planned:

`R52_SYNTHETIC_CANCEL_WINDOW_DIAGNOSTIC_ONLY`

At each valid arrival:
- hypothetical invalidation = `t_ready`;
- remaining B0 background GPU time;
- time to next B8/B32 boundary;
- fraction after boundary.

This is only a lifecycle capability diagnostic.
It is not evidence of real speculative-inference opportunity.
It cannot authorize a mechanism.

---

# 6. Conditional diagnostics

No NCU by default.

Only if R51 reaches the latency-throughput-tradeoff-supported state:
allow at most two standalone resource diagnostics to distinguish whether the cost comes from:
- launch/graph overhead,
- altered kernel occupancy/resource usage,
- extra memory traffic/materialization.

No NCU replay timing for overlap latency.
No NVBit full trace.
No TLB/UVM inference.

---

# 7. Efficiency rules

- Reuse V1 accepted tensors, outputs, timings, NSYS helpers, and code.
- Do not rerun expensive source/identity work already closed.
- Capture only the two fixed holdout hidden states if absent.
- CPU semantic checks may run before GPU timing.
- All GPU timing remains serialized under the lock.
- Ordinary engineering problems solve-and-continue.
- Missing derived wrapper/index files may be deterministically reconstructed.
- Missing scientific tensor identity fails closed.
- No parameter sweep.
- No new model.
- No auto merge.

---

# 8. Final stage state

Exactly one:

- `R51_R52_LIFECYCLE_QUALIFICATION_NO_RESIDUAL_V2`
- `R51_SAFE_HANDOFF_PROBLEM_READY_FOR_ARCH_REVIEW_V2`
- `R51_APPLICATION_SEMANTIC_SAFEPOINT_NOT_QUALIFIED_V2`
- `R51_R52_NATIVE_QUALIFICATION_INCOMPLETE_V2`

R52 alone cannot become architecture-ready in this V2 because no real invalidation authority is available.

---

# 9. Deliverables

Durable root:

`/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/r51_semantic_requal_v2_20260926/`

Review pack:

`docs/vm_tlb/review_packs/AWMA_R51_SEMANTIC_CONTRACT_REQUALIFICATION_V2/`

Required:
- `README.md`
- `V1_INHERITANCE.md`
- `SEMANTIC_PREREGISTRATION.json`
- `SEMANTIC_EQUIVALENCE_RESULTS.tsv`
- `SEMANTIC_DECISION.md`
- conditional `R51_TIMELINE_RESULTS.tsv`
- conditional `R51_MATCHED_COMPARISON.tsv`
- conditional `R52_CANCEL_WINDOW_DIAGNOSTIC.tsv`
- `R51_DECISION.md`
- `R51_R52_DECISION_MATRIX.tsv`
- `FINAL_DECISION.md`
- `RAW_DATA_INDEX.tsv`
- `SHA256SUMS`

Closure:
`science/engineering -> node164 -> review pack -> hashes -> commit -> push -> fetch-back -> exact remote SHA/tree verify -> clean worktree -> STOP`

Git transport failure is publication failure only; preserve science and exact commit.
