# C16 RTX4080 Formal Trace Campaign — Master Goal V1

Owner: ChatGPT coordination
Execution node: node109 / RTX4080
Execution mode: **Goal mode / unattended multi-hour execution**

## 0. Source anchors

The campaign must preserve the following already-accepted authorities and must not reinterpret them silently:

- Pipeline V1 integration: `3c4847d2da818013dca6422194af36966136ab31`
  - `PIPELINE_V1_END_TO_END_PASS_WITH_FILESYSTEM_LIMITATIONS`
  - canonical node164 root: `/root/share/mnt164/huangrulin/c16_ai_workload`
  - formal admission concurrency: one writer
- Analysis prep: `d07b7eb5d43b9a31474a6d298ec4e4f75292cc48`
  - Q2 Prefill/Decode parser regression exact PASS
  - actual R5 U5/U6/U7/U9 archive reconciled
- Pre-capture planning: `55d11e6829bc89189d1c3fadf695c31078485421`
  - frozen matrix commit: `a5ab72e99976abb9f4592176c280defe8f75f9af`
  - Qwen2.5-0.5B and Qwen2.5-7B-AWQ admitted on RTX4080
  - Qwen2.5-7B raw S2_TEXT currently `NOT_ADMITTED_MEMORY`
  - Qwen3-8B / DeepSeek-V2-Lite remain `NO_HISTORICAL_FROZEN_BINDING`

The pre-capture matrix is an **evidence-backed starting state**, not a permanent authorization list. A row marked `READY_FOR_NCU_ONLY`, `REJECT_WEAK_TARGET`, or blocked by missing object/static mapping is a recovery task for this Goal, not a reason to return immediately with zero formal traces.

## 1. Goal

Complete a high-quality, analysis-useful formal NVBit trace campaign on RTX4080, focusing first on:

1. `Qwen/Qwen2.5-0.5B-Instruct`
2. `Qwen/Qwen2.5-7B-Instruct-AWQ` using the actually observed unfused AutoAWQ backend
3. optional exact-resource retry of raw `Qwen/Qwen2.5-7B-Instruct`
4. high-quality Llama-3.2-1B S0 supplementary capture after the Qwen core set

The campaign must actively close missing readiness work (object maps, exact static MREF maps, launch selectors, bounded NCU evidence where useful, canary quality) and then continue directly into formal capture, Pipeline V1 publication, destination ACK closure, and post-capture index/report creation.

Do **not** stop simply because the pre-capture frozen matrix contains zero `READY_FOR_FORMAL_TRACE` rows.

## 2. Scientific invariants — never lower these to make progress

The following are hard scientific boundaries:

- exact model revision and asset receipt must remain bound;
- exact frozen Qwen input binding must be used; no re-tokenization;
- do not silently change batch, context length, decode count, dtype, attention backend, quantization mode, or model revision to avoid a failure;
- do not CPU-offload a deployment merely to make it run;
- do not substitute an arbitrary easy PC/instruction for a representative target;
- target identity must be exact enough to revalidate function + phase/step + launch shape/ordinal and RTX4080-local code/static MREF identity;
- representative NVBit traces should instrument **all relevant GLOBAL MREFs of the selected target launch/window**, not a single convenient memory instruction;
- raw scientific data must pass Pipeline V1 hash/manifest/ACK closure before node109 treats transfer as complete;
- source raw is never deleted by this campaign;
- failed, partial, diagnostic, control, and formal data must remain explicitly distinguished.

Unknown semantic/object attribution is allowed when honestly retained as `UNKNOWN_*`; inventing a label is not allowed.

## 3. Procedural gates that are recoverable inside this Goal

These are **not terminal blockers** and must be worked through as sub-goals:

- missing object map;
- semantic label still unresolved for an exact heavy GEMM;
- missing decode static map;
- missing attention/KV static map;
- missing NCU metrics for a candidate;
- address-bearing canary returns zero records on first attempt;
- one launch selector drifts between runs;
- NVBit bounded capture overflows or becomes too large;
- one scenario OOMs while other frozen scenarios remain admitted;
- Pipeline transfer temporarily fails;
- post-capture parser invocation fails while raw/ACK remain valid.

Use `READINESS_RECOVERY_PLAYBOOK_V1.md` before declaring any of these unresolved.

## 4. Required execution philosophy

This is Goal mode. The agent should behave as an engineer/researcher completing the campaign, not as a checklist executor that stops at the first red cell.

For every recoverable problem:

1. identify root cause from evidence;
2. attempt the highest-quality non-semantic-changing repair;
3. retry in a fresh process when runtime state may be involved;
4. if the original target is genuinely invalid, move only to a pre-frozen or newly evidence-ranked fallback in the **same semantic stratum**;
5. preserve failed evidence and reason;
6. continue with the remaining campaign.

Do not ask for approval at every local recovery step. Continue unless a hard scientific invariant would have to be violated.

## 5. Priority tiers

### Tier A — Qwen2.5-0.5B S2_TEXT core

Goal portfolio, not a rigid target count:

- Prefill compute-heavy/GEMM representative;
- Prefill attention-core representative;
- Decode compute-heavy representative at an early decode step;
- Decode memory/KV/attention-relevant representative at early and late decode steps when the runtime exposes a meaningful distinction.

A semantically unresolved but exact heavy GEMM may remain named `GEMM_HEAVY_UNRESOLVED`; this does not block capture.

### Tier B — Qwen2.5-7B-AWQ S2_TEXT core

Treat the measured deployment as:

`qwen25_7b_awq_autoawq_unfused`

Do not claim fused backend equivalence.

Goal portfolio:

- dominant quantized GEMM / weight-heavy target;
- quant/dequant or quant-metadata-related target when runtime evidence supports a distinct stratum;
- attention-core target;
- decode compute-heavy target;
- decode KV/attention-memory target, preferably early + late when meaningful.

### Tier C — controlled scenario scaling

Only after the S2 core portfolio is healthy, use lightweight native/NSYS checks to decide whether additional formal traces are scientifically useful:

- context: S1 vs S2 vs S3;
- batch: S4 vs S2 structured;
- content: S2_CODE / S2_STRUCTURED / S2_TEXT.

Do not capture all seven bindings blindly. If kernel population/target identity is materially unchanged, keep the scenario as a control/smoke result. If new kernels, launch shapes, long-context behavior, KV behavior, or memory-relevant dominant populations appear, capture a bounded representative control.

### Tier D — Llama S0 high-quality supplement

After Qwen core work, capture a small high-quality S0 portfolio to replace/supplement the historically weak single-PC style evidence. It is single-scenario evidence only; do not generalize it to context/batch scaling.

### Tier E — raw Qwen2.5-7B opportunistic exact retry

Because the previous S2_TEXT OOM was close to the device limit, perform a bounded resource re-admission trial in a **fresh, otherwise idle process** with the exact same scientific configuration.

Allowed recovery:

- ensure no unrelated GPU process is consuming memory;
- finish/exit previous model processes;
- rerun from a clean process with identical model/input/dtype/backend/scenario.

Not allowed:

- reducing context/batch/decode;
- changing dtype/backend;
- CPU offload;
- allocator changes that would alter the formal memory-layout experiment without a separately bound deployment identity.

If exact clean-process admission still fails, record `NOT_ADMITTED_MEMORY_CONFIRMED` and continue; do not let this block Qwen0/AWQ/Llama.

## 6. Qwen3 / DeepSeek boundary

Qwen3-8B and DeepSeek-V2-Lite remain outside this RTX4080 formal campaign unless a separately explicit prospective input authority and resource admission are created. Do not invent historical bindings and do not let these models block completion of the admitted campaign.

## 7. Campaign persistence / resumability

Maintain a machine-readable campaign state under node109, e.g.:

`/data/c16/results/C16_FORMAL_CAMPAIGN_V1/CAMPAIGN_STATE.json`

Every target/scenario must have one state among:

- `PLANNED`
- `READINESS_RECOVERY`
- `CANARY_PASS`
- `FORMAL_CAPTURE_RUNNING`
- `LOCAL_CLOSED`
- `TRANSFER_ACKED`
- `FORMAL_ACCEPTED`
- `CONTROL_ONLY`
- `BOUNDED_DIAGNOSTIC`
- `DEFER_RESOURCE`
- `REJECTED_WITH_EVIDENCE`

Checkpoint after every meaningful transition. After interruption, resume from the state file; do not re-run an already `TRANSFER_ACKED` formal bundle merely because the process restarted.

## 8. When the campaign may stop

Do not stop on a local missing map, NCU failure, first OOM, first canary failure, or a single target failure.

A premature hard stop is justified only when continuing would require violating a scientific invariant, or a global infrastructure failure remains unresolved after reasonable recovery, for example:

- RTX4080 or driver is globally unusable across fresh-process canaries;
- exact model/input authority fails hash validation and cannot be recovered from known authority;
- NVBit 1.7.5 cannot produce any valid address-bearing canary even after known-good tool regression/rebuild;
- Pipeline V1 repeatedly produces source/destination hash disagreement;
- node164 storage is unavailable and node109 lacks safe local capacity for continued bounded capture;
- all candidates for an entire required semantic stratum fail exact identity/static-map closure after exhaustive local mapping.

Even then, preserve all completed formal bundles and finish a root-cause report rather than discarding the campaign.

## 9. Final outcome classes

Preferred final result:

`FORMAL_CAMPAIGN_PASS`

A scientifically useful partial campaign may finish as:

`FORMAL_CAMPAIGN_PASS_WITH_DEFERRED_CONTROLS`

or, if a core deployment has a demonstrated irreducible blocker:

`FORMAL_CAMPAIGN_PARTIAL_WITH_ROOT_CAUSE`

`FAIL` is reserved for the case where no usable core formal trace set can be produced or the data integrity/authority contract cannot be trusted.
