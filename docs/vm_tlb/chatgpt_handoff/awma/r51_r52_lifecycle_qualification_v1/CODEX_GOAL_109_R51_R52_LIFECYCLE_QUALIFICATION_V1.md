# CODEX GOAL — AWMA R51/R52 Task-Lifecycle Handoff Qualification V1

## Purpose

Enter Goal mode and execute continuously to the scientific STOP boundary.

This round advances **one research group only**:

- **R51 (primary): safe resource handoff for an already-ready high-priority task**
- **R52 (special case): work that becomes invalid while an old task is still executing**

R52 shares R51's lifecycle/timeline machinery. Do not create a second independent platform or campaign.

The goal is **problem qualification**, not a preemption mechanism. Determine whether a strong software safe-point/decomposition baseline leaves a material latency-throughput tradeoff that justifies later architecture review.

Repository:
`swayhrl/accel-sim-framework`

Coordination branch:
`hrl/awma-r51-r52-lifecycle-qualification-handoff-v1`

Accepted execution base:
`ce5918d837b76e95ad4000c50bbe1465707a2ebd`

Stage:
`AWMA_R51_R52_TASK_LIFECYCLE_QUALIFICATION_V1`

Execution node:
**109 / RTX4080 / SM89**

Do not run Accel-Sim in this Goal.
Do not start a 174 task.
Do not download a new model.
Do not patch the NVIDIA driver.

Ordinary engineering issues are solve-and-continue. Stop only for a scientific identity/contract/claim change that cannot be resolved without changing the preregistered question.

---

# 0. Required reading / accepted inputs

Read:

1. Accepted P1/P2 closeout:
   `docs/vm_tlb/review_packs/AWMA_P1_P2_NATIVE_PROBLEM_QUALIFICATION_V1/`

2. ChatGPT literature branch at exact commit:
   `hrl/awma-chatgpt-literature-notes-v1 @ d6a10f0209a024edb4612b1f53edb61d6e39bd18`

   Required:
   `docs/vm_tlb/literature_notes/awma/rounds/2026-09-26_ROUND_05_PROBLEM_DISCOVERY.md`

3. Historical real-kernel census/selection authority:
   `hrl/awma-kernel-target-selection-109-v1 @ e90fd76d3704df4a367bb04de09aee42d0cab803`

Important accepted historical observation:
- Qwen2.5 S2 Decode contains an `internal::gemvx` subfamily with
  `grid=18992,1,1`, `block=8,8,1`,
  median about 409 us, 32 occurrences, about 10.7% of Decode GPU kernel time.
- This historical row has **operator_role=UNKNOWN**. It is only a target clue.
  Do not call it `lm_head` from duration/shape alone.

Foreground authority:
reuse the accepted model-derived Q/K/V and Flash-SDPA execution identity from the P1 stage when scientifically valid.

Preserve all prior negative conclusions. This Goal does not reopen translation, UVM, P1/P2, cache/MSHR scaling, or AWQ.

---

# 1. Scientific questions

## R51 primary question

With the foreground input already ready and submitted at high priority:

> How long until the foreground begins useful GPU work, and how much background-throughput cost is required by a strong software safe-point/decomposition baseline to reduce that delay?

Separate:
- input readiness,
- host/runtime submission,
- scheduler/resource availability,
- first foreground GPU kernel start.

Do not call all delay "preemption latency".

## R52 special-case question

Using the same lifecycle and background execution:

> If the background becomes known-invalid at the same lifecycle point, how much not-yet-useful work remains before the earliest legal software safe point?

R52 is **scientifically qualified only with a real online invalidation authority**.
Without such an accepted authority, emit only a capability diagnostic. A synthetic invalidation timestamp is not evidence that speculative inference exposes this opportunity.

---

# 2. Phase A — target identity and preregistration

Perform all CPU/source/asset audit before overlap timing.

## 2.1 Background target

Primary candidate:
a semantically closed Qwen2.5-0.5B **decode output projection / lm_head** replay derived from an accepted real model state.

Required procedure:
1. Use an accepted frozen Qwen S2 model/input/revision.
2. Capture the exact tensor presented to `model.get_output_embeddings()` / `lm_head` at one declared decode step without altering model output.
3. Replay exactly that linear operation with the model's real weight.
4. NSYS-audit the exact function/grid/block.
5. Independently compare against the historical `grid=18992,1,1` long-GEMV row.

Only if exact semantic binding and runtime identity close may it be called `LM_HEAD_BACKGROUND`.

Historical equality is useful but not required for semantic qualification; a semantically bound real lm_head replay is acceptable even if current library selection differs.

Background eligibility:
- real model-derived input and real model weight;
- output correctness closed against the model invocation;
- optimized library/native baseline;
- median standalone GPU time **>=150 us**.

If lm_head does not qualify, one fallback is allowed:
select the first semantically-qualified real Qwen S2 linear/GEMM operator with standalone median >=150 us, using a preregistered deterministic selection rule based on accepted phase-time order.

If no real operator qualifies:
`R51_NOT_QUALIFIED_NO_LONG_REAL_BACKGROUND`
and STOP the stage. Do not manufacture a long synthetic AI kernel.

## 2.2 Foreground target

Primary foreground:
the accepted P1 model-derived layer-12 Flash SDPA B1 operator/input if reusable without contract drift.

Requirements:
- independent from background result;
- all input tensors device-resident before `t_ready`;
- exact output hash/reference;
- standalone median target time recorded;
- exact NSYS function/grid/block closed.

If that exact P1 input cannot be legally reused, recapture the same declared semantic target from the accepted model/input. Do not replace it with a tiny synthetic vector-add foreground.

## 2.3 Stream capability

Audit:
- CUDA stream priority range;
- PyTorch/CUDA ability to create highest- and lowest-priority streams;
- actual stream IDs in NSYS.

If the device/runtime exposes no distinct stream-priority levels, record that fact and use separate streams only as a diagnostic; do not claim high-priority scheduling.

## 2.4 Freeze before formal overlap

Create `PREREGISTRATION.json` before formal overlap results.

Bind:
- model/revision/input/decode-step;
- background semantic identity and hashes;
- foreground semantic identity and hashes;
- exact software versions/GPU/driver;
- standalone medians;
- safe-point chunk counts: exactly **8 and 32**;
- arrival fractions: exactly **0.25 and 0.50** of the accepted monolithic standalone median;
- warmups=2;
- measured repetitions=7;
- one canary per formal point;
- retry tolerance for arrival timing;
- decision thresholds below.

No parameter sweep after timing.

---

# 3. Phase B — background software baselines

All arms compute the same complete background output.

## B0 — MONOLITHIC

Run the original optimized full output projection/linear operator as one library operation.

## B8 — CHUNKED_GRAPH_8

Partition **only the output-row dimension** into 8 deterministic contiguous chunks.

For each chunk:
- execute the same mathematical linear rows;
- concatenate in original row order;
- no row may be duplicated or skipped.

Capture the 8 chunks into a CUDA Graph on the low-priority/background stream when graph capture is legal.

## B32 — CHUNKED_GRAPH_32

Same, with exactly 32 chunks.

The split counts are frozen diagnostic points, not a tuning search.

## Strong-baseline correctness gate

For B8/B32:
- full output shape must match B0;
- require bitwise equality to B0 if the actual per-row arithmetic is unchanged;
- if library kernel selection changes and bitwise equality fails, make at most **two surgical implementation attempts** to preserve the same row arithmetic/decomposition.
- If bitwise equality still cannot be preserved, fail that arm closed as
  `SOFTWARE_SAFEPOINT_NUMERIC_CONTRACT_NOT_CLOSED`.
  Do not silently relax to an arbitrary tolerance.

Graph liveness:
mutate the frozen hidden input in a bounded canary and prove graph replay recomputes output, then restore original input/output hash.

## Standalone throughput cost

Before foreground overlap, measure B0/B8/B32 standalone background completion.

Compute:
`background_overhead = (T_arm - T_B0) / T_B0`.

Do not use profiler timing as the primary throughput number; use CUDA-event operator timing with NSYS as identity/timeline evidence.

---

# 4. Phase C — formal foreground-arrival experiment

Actual GPU measurements must hold:
`/data/c16/locks/c16_gpu_campaign.lock`.

For each background arm B0/B8/B32 and each frozen arrival fraction 0.25/0.50:

1. inputs are already resident;
2. launch background on the low-priority stream;
3. schedule foreground submission near the target fraction using a CPU helper/spin strategy that does not execute GPU work;
4. at foreground readiness/submission, emit an exact NVTX marker/range;
5. launch foreground on the highest-priority stream;
6. allow the background to complete;
7. verify both outputs.

Formal timing authority:
NSYS/CUPTI unified timeline.

For each repetition derive:
- `t_bg_start`
- `t_ready` (host NVTX readiness/submission point)
- `t_submit_end` (foreground CUDA launch/API completion if recoverable)
- `t_fg_first_kernel_start`
- `t_fg_last_kernel_end`
- `t_bg_end`
- current background chunk/kernel at `t_fg_first_kernel_start`
- whether foreground and background overlap in GPU time.

Primary metrics:
- `ready_to_fg_start = t_fg_first_kernel_start - t_ready`
- `submit_to_fg_start = t_fg_first_kernel_start - t_submit_end`
- foreground completion latency from `t_ready`
- background total completion extension relative to standalone.

Do not infer a hidden scheduler event that telemetry does not expose.

## Arrival acceptance

The actual arrival point is measured, not assumed.

A formal repetition is valid if the measured `t_ready` occurs within:
- target fraction ±0.10 of the B0 standalone median,
- and while background work is demonstrably active.

One bounded retry is allowed for a point if host scheduling misses this envelope.
Preserve failed-arrival attempts in the raw index.

---

# 5. R51 decision logic

First determine if B0 exposes a material ready-to-start delay.

Define the software handoff benefit using the best **pre-registered** of B8/B32; do not invent a new split count.

A handoff improvement is material only if:
1. median `ready_to_fg_start` falls by at least **10 us** versus B0 at a matched arrival fraction;
2. the improvement exceeds **3x** the larger relative CV/jitter envelope converted to the same latency metric;
3. output contracts remain closed.

Then classify software cost:

### `R51_NO_MATERIAL_HANDOFF_DELAY`
B0 itself has no material foreground delay, or B8/B32 do not materially improve it.

### `R51_SOFTWARE_SAFEPOINT_CLOSES_GAP`
A pre-registered chunked graph materially improves foreground handoff and its standalone background overhead is **<=5%**.

### `R51_SAFEPOINT_LATENCY_THROUGHPUT_TRADEOFF_SUPPORTED`
A pre-registered chunked graph materially improves handoff, but obtaining the improvement costs **>5%** standalone background throughput, or a meaningful residual remains even at B32.

This is the only R51 state that may become an architecture-review candidate.

### `R51_NOT_QUALIFIED_*`
Identity, output, stream, or timing contract cannot be closed.

Do not add chunk counts to turn a negative result positive.

---

# 6. Phase D — R52 as lifecycle special case

Execute this phase using the already-collected R51 timeline.

## 6.1 First search for real invalidation authority

Audit accepted local assets for an existing real online speculative/cancellation trace with:
- task creation,
- earliest online invalidation time,
- task completion,
- valid-consumer dependency.

Do not download or build a new speculative model.

If none exists:
`R52_NO_REAL_INVALIDATION_AUTHORITY`.

## 6.2 Capability diagnostic

Even without real authority, compute a clearly labeled diagnostic from R51:

At each matched arrival point, treat `t_ready` as a hypothetical invalidation instant and report:
- monolithic remaining background GPU time;
- time to the next B8/B32 chunk boundary;
- fraction of total background work after that boundary.

Label:
`R52_SYNTHETIC_CANCEL_WINDOW_DIAGNOSTIC_ONLY`.

This is not an AI workload result and cannot authorize a mechanism.

## 6.3 If real invalidation authority exists

Only then join actual invalidation times to the lifecycle model.

Count as potentially avoidable only work that:
- begins/continues after invalidation is online-known,
- is not required by a still-valid consumer,
- has not already completed.

Do not count total rejection ratio.

Possible states:
- `R52_NO_KNOWN_INVALID_REMAINDER`
- `R52_SOFTWARE_CANCEL_BOUNDARY_SUFFICIENT`
- `R52_REAL_CANCEL_RESIDUAL_SUPPORTED`

The last state requires real invalidation authority and a material residual beyond a software safe point.

---

# 7. Conditional deep diagnostics

No NCU/NVBit full trace by default.

Only if R51 reaches
`R51_SAFEPOINT_LATENCY_THROUGHPUT_TRADEOFF_SUPPORTED`:

allow at most two bounded extra diagnostics to identify why:
- kernel occupancy/resource residency metadata;
- one source-correct NCU resource profile per relevant background arm, run standalone.

Do not use NCU replay to measure overlap handoff latency.
Do not infer TLB/UVM behavior.

No Accel-Sim in this Goal.

---

# 8. Final decision

Create `R51_R52_DECISION_MATRIX.tsv`.

Final stage state must be exactly one:

- `R51_R52_LIFECYCLE_QUALIFICATION_NO_RESIDUAL_V1`
- `R51_SAFE_HANDOFF_PROBLEM_READY_FOR_ARCH_REVIEW_V1`
- `R52_REAL_CANCEL_PROBLEM_READY_FOR_ARCH_REVIEW_V1`
- `R51_R52_BOTH_READY_FOR_ARCH_REVIEW_V1`
- `R51_R52_NATIVE_QUALIFICATION_INCOMPLETE_V1`

`READY_FOR_ARCH_REVIEW` does not authorize a hardware mechanism or 174 modification.
It only asks ChatGPT to review whether a distinct capability remains versus LithOS, GPREEMPT, ExpertPlex, MPK, and PipeThreader.

If negative, stop. Do not move to R53 inside this Goal.

---

# 9. Efficiency rules

- CPU/source audits and harness unit tests may run in parallel.
- All actual GPU measurements are serialized under the existing GPU lock.
- Reuse P1/P2 timing/NSYS/data-plane helpers where possible.
- Small engineering repairs remain on the same execution branch.
- Missing deterministic wrapper/index files follow the current reconstruction policy.
- Missing scientific input/semantic identity is a fail-closed blocker for that arm.
- No broad parameter sweep.
- No model download.
- No new general scheduling framework.
- No driver patch.
- No PPA.
- No automatic merge.

---

# 10. Authority and deliverables

Durable root:

`/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/r51_r52_lifecycle_qualification_20260926/`

Review pack:

`docs/vm_tlb/review_packs/AWMA_R51_R52_TASK_LIFECYCLE_QUALIFICATION_V1/`

Minimum:
- `README.md`
- `SOURCE_AND_CLOSEST_WORK_AUDIT.md`
- `TARGET_IDENTITY_RECEIPT.json`
- `PREREGISTRATION.json`
- `BACKGROUND_CORRECTNESS.tsv`
- `BACKGROUND_STANDALONE_TIMING.tsv`
- `STREAM_PRIORITY_RECEIPT.json`
- `R51_TIMELINE_RESULTS.tsv`
- `R51_MATCHED_COMPARISON.tsv`
- `R51_DECISION.md`
- `R52_INVALIDATION_AUTHORITY_AUDIT.md`
- `R52_CANCEL_WINDOW_DIAGNOSTIC.tsv`
- real R52 result only if qualified
- conditional diagnostic files only if triggered
- `R51_R52_DECISION_MATRIX.tsv`
- `FINAL_DECISION.md`
- `RAW_DATA_INDEX.tsv`
- `SHA256SUMS`

Closure:

`science/engineering -> node164 -> review pack -> hashes -> commit -> push -> fetch-back -> exact remote SHA/tree verification -> clean worktree -> STOP`

Git transport failure is publication failure only. Preserve the exact local commit and use the configured HTTPS -> HTTP/1.1 -> SSH -> gh/API fallback sequence. Never rerun science because push transport fails.
