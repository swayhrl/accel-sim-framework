# C16 G Retry570 — Fast Qualification Then Frozen-Target Retry

## Scope

This branch is a continuation of the terminal G checkpoint `73850d93a4c97537976d799759b9440112eadea9` and MUST NOT rewrite the prior 595-driver closeout. The prior node remains scientifically closed as:

- `G2_NCU_CAPABILITY_LIMITED_PERF_COUNTER_PERMISSION`
- `G3_CAPABILITY_LIMITED`
- `C16_AUTODL_FINAL_G2_G3_COMPLETE_SAFE_TO_POWER_OFF`

The purpose of this branch is to test a new RTX3090 / SM86 node expected to use driver `570.124.04`, first with a fast compatibility qualification, then—only if qualified—to retry the already-frozen C targets.

This is not a new selector run and does not authorize any target changes.

## Fixed scientific authority

- Frozen C target authority: `d55075b7752380d6bd22328547db21a5e24eeed2`
- Selector: `SELECTOR_R`
- Budget: `B48`
- Exact frozen NCU target plan and NVBit target plan from that C commit remain immutable.
- Qwen2.5-7B raw remains `RESOURCE_UNAVAILABLE_ON_RTX3090`.
- AWQ S3/S4 remain `SKIPPED_RESOURCE`.
- No target/shape/context/batch/dtype/backend/offload substitution is allowed.

## New-node identity gate

Do not trust marketplace screenshots. Record the actual node:

- GPU model / UUID / compute capability
- driver version
- CUDA runtime/toolkit
- CPU / RAM / disk
- image/container identity
- instance start timestamp
- torch / Python / transformers / AutoAWQ
- NVBit archive/tool SHA
- Nsight Compute version

Expected preferred identity is RTX3090 / SM86 / driver 570.124.04, but any mismatch must be recorded and evaluated before proceeding.

## Phase Q0 — Minimal environment replication

Replicate the prior scientific software environment as closely as possible:

- CPython 3.10
- accepted hash-closed wheelhouse / torch 2.5.1+cu124
- same G source lineage
- same NVBit 1.7.6 archive/tool SHA

Do not use the base image's Python 3.12 scientific environment merely for speed; that would confound the driver comparison.

Transfer only code/wheelhouse/small fixtures first. Do NOT transfer Qwen7-AWQ before the compatibility gates pass.

## Phase Q1 — Fast NCU permission gate

Use a tiny deterministic PyTorch GEMM or CUDA fixture.

1. `ncu --version`
2. query permissions / metrics as needed
3. run one tiny bounded NCU capture

If `ERR_NVGPUCTRPERM` or equivalent permission denial occurs:

- record `G2_RETRY570_CURRENT_INSTANCE_CAPABILITY_LIMITED_PERF_COUNTER_PERMISSION`
- do not retry multiple metrics/targets/root variants
- continue NVBit qualification

If the tiny NCU capture succeeds:

- freeze the same compact metric set already defined by C16 G2
- only after NVBit fast qualification, allow retry of the exact frozen C NCU target plan

## Phase Q2 — NVBit compatibility qualification

All Q2 rows are `COMPATIBILITY_DIAGNOSTIC_ONLY`, not scientific model captures.

### Q2-A direct CUDA fixture

Re-run the known tiny CUDA fixture under the same NVBit build.
Require:

- injection PASS
- terminal state PASS
- real trace > 0 bytes
- active-mask / width / memory-space parsing PASS
- manifest/hash closure

### Q2-B PyTorch elementwise

Use the same workload class that failed on the 595 node.
Run:

1. no-NVBit baseline
2. official NVBit `instr_count`
3. C16 memory tracer

Require normal process exit and actual workload-kernel observation for both NVBit tools.

### Q2-C PyTorch GEMM

Repeat the same A/B/C comparison for a fixed small GEMM.

### Decision

- official tool FAIL + C16 tracer FAIL => `NVBIT_PYTORCH_RUNTIME_OR_DRIVER_COMPATIBILITY_NOT_RESOLVED`; stop before model transfer.
- official tool PASS + C16 tracer FAIL => bounded custom-tracer debug allowed for at most 10 minutes; do not blame driver.
- official tool PASS + C16 tracer PASS for elementwise and GEMM => `NVBIT_PYTORCH_COMPATIBILITY_GATE_PASS`; proceed.

Do not infer causality from driver version alone. A successful 570 node is strong comparative evidence, not proof that 595 was the sole cause.

## Phase Q3 — Progressive model canaries

Only after Q2 PASS.

Transfer models incrementally:

1. Llama3.2-1B first
2. Qwen2.5-0.5B second if needed
3. Qwen2.5-7B-AWQ only after the smaller model path is qualified

For each level:

- no-NVBit baseline sanity
- official/simple NVBit tool
- C16 memory tracer
- record exact failure boundary

If Llama/Qwen0.5 work but AWQ fails, classify the problem at the AutoAWQ/model-runtime boundary rather than as generic NVBit failure.

## Storage gate before formal model capture

Before the first formal C target capture, check both remote and local storage.

Remote:
- target working disk should have at least 100 GiB available; 150–200 GiB total data-disk capacity is recommended.

Local trace receiver:
- require at least 100 GiB available before a formal multi-window campaign.

If local free space is below 100 GiB, allow at most one bounded model canary for sizing, then stop with `LOCAL_TRACE_STORAGE_EXPANSION_REQUIRED`.

After the first real model trace, publish `NVBIT_STORAGE_ESTIMATE.json` with:

- raw bytes
- compressed bytes if compressed
- capture duration
- estimated selected-window count
- estimated campaign bytes
- local/remote free bytes

Do not launch the full campaign if the estimate crosses the safe storage margin.

## Phase Q4 — Retry exact frozen C targets

Only after Q2/Q3 qualification.

### NCU

If NCU tiny permission gate passed, retry ONLY the exact C NCU rows from `d55075b...`.
If permission gate failed, leave NCU as current-node capability-limited and do not spend further time.

### NVBit

Use the exact frozen C NVBit plan.

1. first row canary
2. prove unique structural/ordinal reproduction
3. no kernel-name-only or nearest/adjacent substitution
4. canary PASS => execute remaining bounded rows, grouped by scenario/phase where identity preservation is proven

Per window guards remain:

- <= 4 GiB raw
- <= 20 minutes
- <= 6 windows/deployment
- <= 64 GiB first-wave raw unless a newer explicit authorization exists

Every raw artifact:

remote size/SHA -> transfer local -> local size/SHA -> receipt -> optional compression -> next target.

Do not wait for Lane H analysis before executing the next already-authorized target.

## Publication / checkpoint policy

Push at these milestones:

1. new-node identity/environment closure
2. NCU tiny gate disposition
3. NVBit PyTorch compatibility gate PASS/FAIL
4. first real model NVBit canary PASS/FAIL
5. first frozen C target PASS/FAIL
6. each formal capture batch closeout
7. final remote/local raw closure

Large raw traces remain outside Git. Git stores path/size/SHA/run/target/tool identity only.

## Stop conditions

Stop rather than improvising on:

- package/revision/hash mismatch
- dtype/backend fallback
- CPU offload
- target ambiguity
- local trace storage below safe margin
- budget exhaustion
- NCU counter permission denial after one bounded tiny gate
- NVBit official-tool failure on minimal PyTorch after bounded verification

Ordinary path/tool/build/transfer issues may be actively solved within bounded time.

## Final states

If 570 node fails the same minimal PyTorch NVBit gate:

`C16_RETRY570_NVBIT_COMPATIBILITY_NOT_RESOLVED_SAFE_TO_POWER_OFF`

If NVBit succeeds but formal capture is storage-blocked:

`C16_RETRY570_NVBIT_QUALIFIED_WAITING_LOCAL_STORAGE`

If frozen NCU/NVBit retries finish or are explicitly capability-limited and all required raw is locally hash-closed:

`C16_RETRY570_FIXED_TARGET_COMPLETE_SAFE_TO_POWER_OFF`
