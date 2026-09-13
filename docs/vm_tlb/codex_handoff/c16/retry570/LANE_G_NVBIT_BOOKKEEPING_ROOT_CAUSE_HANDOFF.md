# C16 Lane G Retry570 — NVBit module/bookkeeping root-cause handoff

## 0. Purpose

This handoff is the authoritative next-step diagnostic plan for Lane G Retry570.

The goal is **not** to run longer timeouts. The goal is to close the remaining causal boundary around NVBit 1.8 host-side module/library bookkeeping and either:

1. prove the issue is in our callback/census implementation and fix it; or
2. prove it is in NVBit core module bookkeeping and establish a bounded engineering workaround (preferably EAGER/prewarm outside measurement); or
3. identify a concrete alternative root cause with source/stack evidence.

This document is docs-only. Do not reset or rewrite the active Lane G branch to this handoff branch.

### Remote anchors

- repository: `swayhrl/accel-sim-framework`
- active lane branch: `hrl/vm-c16-g-retry570-v0`
- active remote anchor when this handoff branch was created: `da36cf03c21c979184a3117ed12f1bdb3d5b0393`
- handoff branch: `hrl/vm-c16-g-retry570-chatgpt-handoff-v1`

Read this file from the handoff branch, then continue work on the existing Lane G worktree/branch. Do **not** merge or reset to the handoff branch merely to consume this document.

---

## 1. Facts already established — do not regress them

### 1.1 Environment/tool-startup failures are closed

- CUDA 12.4 is present.
- `nvdisasm` exists at `/usr/local/cuda-12.4/bin/nvdisasm`.
- Harness child `PATH` propagation was repaired and `NVDISASM=nvdisasm` was made explicit.
- NVBit official `instr_count_bb + vectoradd` smoke passes.
- The prior `nvdisasm not found on PATH` failure is CLOSED.

### 1.2 PyTorch/NVBit is not universally broken

Independent C0–C4 PyTorch/NVBit probes completed within 60 s.

The C4 GEMM reference showed:

- 89 related functions,
- 88 actually enumerated,
- 66,032 static instructions,
- cumulative `nvbit_get_instrs()` time ≈ 19.969523 s.

This proves related-function/static-instruction discovery can be expensive, but **must not be mapped causally onto the exact target**, because the exact target was later shown to stall before the target launch callback.

### 1.3 Exact-target boundary moved earlier than kernel instrumentation

For the exact `indexSelectLargeIndex` reproducer, the important LAZY timeline is:

```text
EXACT_TARGET_SUBMISSION_BEGIN
  -> ~tens of ms
cuLibraryLoadData completes
  ->
cuLibraryGetModule ENTRY
  -> no EXIT inside the short diagnostic window
  -> no launch API observed
  -> GPU utilization remains 0
  -> CPU remains busy (~100–150%)
  -> no nvdisasm child process
```

Therefore the exact-target problem is **not currently located in**:

- target kernel execution,
- target `nvbit_get_instrs()`,
- instruction insertion,
- `nvbit_enable_instrumented`,
- trace emission,
- GPU synchronization after target launch.

### 1.4 Native 2×2 controls rule out native CUDA/PyTorch first-use as the main cause

Exact reproducer controls:

- native + LAZY: completes (~3.28 s observed in prior diagnostic)
- native + EAGER: completes (~4.92 s observed in prior diagnostic)

Therefore a native CUDA/PyTorch `cuLibraryGetModule` path that inherently takes tens of seconds is not supported.

### 1.5 NVBit callback-only reproduces the high-CPU stall

2×2 callback-only results:

- C = callback-only + LAZY: reproduces high-CPU stall around `cuLibraryGetModule`; no launch API; GPU 0.
- D = callback-only + EAGER: the long delay moves earlier, before the exact marker / near initialization.

Interpretation: LAZY/EAGER changes **where** first-use module/library work happens; it does not by itself prove the root cause.

### 1.6 GDB moved the hot path into NVBit/module bookkeeping

Multiple successful GDB snapshots on the LAZY callback-only case showed the main thread spending time in the injected `.so` / statically linked NVBit core path around:

```text
Nvbit::module_loaded
  -> elfModuleHashMap::operator[]
  -> std::_Hash_bytes / std::unordered_map<..., std::vector<Function*>>::operator[]
```

The main thread was **not** primarily observed in:

- `libcuda` loader frames,
- ATen/libtorch,
- futex wait as the active main-thread state,
- `waitpid` / subprocess wait,
- `nvdisasm` child execution.

This makes **NVBit host-side module/function bookkeeping** the current primary suspect.

However, do not yet state “NVBit core bug confirmed” until RAW and EMPTY controls below separate our diagnostic callback code from NVBit core behavior.

---

## 2. Current causal question

We need to distinguish three layers:

```text
A. diagnostic/census code artifact
B. Lane G tool-side bookkeeping artifact
C. NVBit core module/library bookkeeping pathology
```

The decisive sequence is:

```text
old callback census
    -> RAW census (fixed POD only)
        -> EMPTY callback
            -> if still reproduced: NVBit core path confirmed
```

Do not widen the workload matrix before completing this sequence.

---

## 3. P0 — one final source/provenance pass only

### Goal

Map the observed hot path to the most precise reliable symbol/source ownership possible, without spending repeated runs guessing the layout of an untyped vendor STL object.

### Required outputs

Report:

- `.so` / archive/object containing the observed PC,
- symbolized call chain,
- whether `Nvbit::module_loaded` and `elfModuleHashMap::operator[]` are from NVBit 1.8 vendor/core code or from Lane G-added code,
- exact source/commit provenance if available.

Use `addr2line`, `nm`, `objdump`, archive member inspection, and `git blame/log/diff` where source exists.

### Important restriction

The vendor archive lacks sufficient DWARF for reliable interpretation of the real STL map object. Do **not** infer root cause from an ABI-guessed cast that merely prints plausible values.

A locally compiled same-template sentinel may help GDB parse a type expression, but it does **not** validate that an arbitrary vendor global can be safely reinterpreted as that type/layout.

Allow at most **one more** attempt to extract map size/bucket data. If type/layout remains uncertain, stop this path.

### Prefer sampling over unsafe object introspection

If `perf` is available and attach overhead is acceptable, take a short (~5 s) sample during the reproduced stall:

```bash
perf record -F 99 -g -p <PID> -- sleep 5
perf report --stdio
```

Classify the hottest STL operation if possible:

- `_Hash_bytes` dominant -> repeated/heavy hashing,
- `_M_find_before_node` / bucket traversal dominant -> lookup/collision path,
- `_M_rehash` dominant -> growth/rehash path,
- `_M_insert_unique_node` dominant -> insertion path.

Sampling is diagnostic only, not a performance measurement.

---

## 4. P1 — true RAW callback census

### Goal

Remove every dynamic container and every NVBit introspection action from our callback implementation.

Add a dedicated mode such as:

```text
CALLBACK_CENSUS_RAW=1
```

### Callback contract

Inside `nvbit_at_cuda_event`, RAW mode may only record a fixed POD event into a preallocated fixed-capacity buffer:

```text
sequence
timestamp / monotonic tick
tid
cbid
is_exit
```

### Strictly forbidden in RAW callback path

- `std::string`
- `std::vector`
- `std::unordered_map`
- dynamic `new/delete`
- explicit `malloc/free`
- iostream formatting
- callback-name lookup
- `Function*` metadata bookkeeping
- any `nvbit_get_*` API
- CUDA API calls
- instruction discovery
- insertion
- enable
- synchronization
- trace emission

Prefer a preallocated ring/fixed buffer and dump/translate callback names **after** the process leaves the sensitive callback path.

### Workload

Run only the exact `indexSelectLargeIndex` reproducer under LAZY.

Use the short bounded diagnostic supervisor described in Section 8.

### Decision

- If RAW completes while old census stalls: classify as `TOOL_OR_CENSUS_BOOKKEEPING_ROOT_CAUSE` and debug our implementation. Do not blame NVBit core.
- If RAW reproduces the same `Nvbit::module_loaded -> elfModuleHashMap` CPU path: proceed immediately to EMPTY.

---

## 5. P2 — EMPTY callback control

### Goal

Determine whether merely entering the NVBit CUDA-event machinery is sufficient to reproduce the problem.

Build the smallest possible callback tool:

```cpp
void nvbit_at_cuda_event(...) {
    return;
}
```

No logging, no counters, no STL, no introspection, no synchronization.

If feasible without changing the NVBit load contract, add an even stricter control that loads the minimum tool/runtime but does not register/use event bookkeeping beyond what NVBit core necessarily performs.

Run the same exact reproducer under LAZY.

### Decision table

| Old census | RAW | EMPTY | Interpretation |
|---|---|---|---|
| stall | pass | n/a | our old census/tool bookkeeping artifact |
| stall | stall | pass | RAW logging/recording path still perturbs/re-enters |
| stall | stall | stall with same NVBit stack | NVBit core module/library bookkeeping pathology strongly confirmed |

Only the third row justifies a root-cause status equivalent to:

```text
NVBIT_CORE_MODULE_BOOKKEEPING_PATHOLOGY_CONFIRMED
```

Prefer evidence language over “bug” unless duplicated/incorrect behavior is demonstrated.

---

## 6. P3 — if NVBit core is confirmed, characterize “bounded first-use cost” vs “persistent pathology”

Do this **only after** EMPTY reproduces the issue or equivalent evidence proves the core path.

The next scientific/engineering question is not “can we make startup 2 s?” It is:

> Is the cost finite, one-time, cacheable, and safely movable before `MEASUREMENT_ACTIVE`?

### 6.1 EAGER/prewarm characterization

Use `CUDA_MODULE_LOADING=EAGER` only as a differential/engineering tool.

If an EAGER initialization can complete under a separately authorized bounded diagnostic, then in the same process run the identical small operation twice and compare:

```text
ROUND1_BEGIN/END
ROUND2_BEGIN/END
```

Record:

- first-use wall time,
- second-use wall time,
- whether the second operation re-enters the same high-CPU bookkeeping path,
- whether the module/library work is repeated.

### 6.2 Interpretation

If first use is slow but second use is fast:

```text
ONE_TIME_FIRST_USE_BOOKKEEPING_COST
```

This is potentially acceptable if it can be moved before the measurement gate.

If every identical operation repeats the cost:

```text
PERSISTENT_OR_DUPLICATED_BOOKKEEPING_PATHOLOGY
```

This requires version/tool/core remediation rather than simple prewarm.

### 6.3 Do not read private STL state if external counts suffice

Prefer externally observable counts:

- number of `cuLibraryLoadData` events,
- number of `cuLibraryGetModule` events,
- unique library/module handles if safely available,
- callback/event counts,
- first-use vs second-use timing.

If one library/module event induces tens of seconds of repeated core hashing, that is much more suspicious than a workload that legitimately loads a huge number of unique modules/functions.

---

## 7. P4 — engineering unblock policy after root cause is known

### Case A: our census/tool code is responsible

Fix the code, then rerun only:

1. RAW/normal callback exact reproducer,
2. one minimal first-kernel smoke.

Typical fixes to consider only if supported by evidence:

- remove callback-time dynamic containers,
- replace accidental `operator[]` lookup with non-mutating lookup where semantically correct,
- deduplicate function/module entries,
- protect concurrent mutation,
- avoid callback reentrancy,
- preallocate metadata,
- cache already processed handles.

Do not apply these speculatively before proving ownership of the path.

### Case B: NVBit core cost is finite and one-time

Prefer an engineering workaround before attempting invasive vendor-core modification:

```text
process start
  -> CUDA_MODULE_LOADING=EAGER (if required)
  -> bounded NVBit/module warm-up
  -> verify READY
  -> only then create/enable MEASUREMENT_ACTIVE
  -> launch real model/capture
```

This workaround is acceptable only if:

- initialization terminates reliably,
- warm-up does not contaminate captured trace,
- the formal measurement window begins afterward,
- repeated operations do not re-pay the same large cost,
- results remain reproducible.

### Case C: NVBit core cost repeats or is pathological

Then test the smallest compatible version/configuration matrix **only on the exact tiny reproducer**, not on models:

- current NVBit 1.8 baseline,
- one known-compatible alternative NVBit release if available,
- keep CUDA/driver changes out of the first comparison unless required by documented compatibility.

Do not upgrade/downgrade CUDA or driver first; change one variable at a time.

If a version change removes the pathology, document the exact compatibility matrix and then re-run official NVBit smoke + exact reproducer before any model work.

---

## 8. Diagnostic runtime budget — fix the current “25 s means several minutes” problem

The phrase “25 s cap” must refer to a clearly defined scope.

A single Codex action can legitimately take longer than 25 s because it includes edit/build/test/SSH/copy/analyze. But a **single remote diagnostic transaction** must not silently exceed its declared wall-clock budget by minutes.

### Required external supervisor model

Do not depend on a watchdog inside the target process, because GDB/ptrace stops may suspend the target and its watchdog threads.

Use an external monotonic supervisor and a dedicated process group.

Recommended budgets:

```text
TARGET_HARD_BUDGET      = 25 s
REMOTE_TRANSACTION_CAP  = ~32 s
LOCAL_SSH_CAP           = ~40 s
```

At target deadline:

1. send `SIGTERM` to the whole target process group,
2. allow ~1–2 s grace,
3. send `SIGKILL` to the whole process group if any member remains,
4. reap children,
5. verify no GPU process / diagnostic child remains.

Each GDB snapshot should itself have a small external cap (for example <=3 s).

### Every run must report three wall times

```text
target_wall_s=
remote_transaction_wall_s=
local_ssh_wall_s=
```

Also report whether timeout cleanup required TERM or KILL.

Do not call a run “25 s” if only the target sub-step was limited while SSH/attach/cleanup spent additional minutes without reporting their wall time.

---

## 9. Efficiency rules

The objective is rapid convergence. Do not execute every branch of the diagnostic tree once a decisive result is obtained.

Priority order:

```text
P0 one final reliable provenance/sample pass
 -> P1 RAW census
    -> if RAW stalls: P2 EMPTY callback
       -> if EMPTY stalls: core confirmed
          -> characterize one-time vs repeated cost
```

Do not:

- run the full model,
- run Llama/Qwen,
- run C target,
- run trace/scientific capture,
- reopen the old 300 s one-shot long-watch,
- rerun historical 6+6 windows,
- increase timeout merely to see whether it “eventually finishes”,
- repeatedly probe unsafe vendor STL layouts.

Short diagnostic repetitions are allowed when they answer a different causal question.

---

## 10. Required stop statuses

Do not close with another generic `INCONCLUSIVE_PRE_LAUNCH...` if concrete evidence exists.

Preferred terminal classifications for this round:

```text
CENSUS_DIAGNOSTIC_ARTIFACT_CONFIRMED
LANE_G_TOOL_BOOKKEEPING_ROOT_CAUSE_CONFIRMED
RAW_LOGGING_INTERFERENCE_CONFIRMED
NVBIT_CORE_MODULE_BOOKKEEPING_PATHOLOGY_CONFIRMED
NVBIT_ONE_TIME_FIRST_USE_BOOKKEEPING_CONFIRMED
NVBIT_PERSISTENT_DUPLICATED_BOOKKEEPING_CONFIRMED
```

If still unresolved, the closeout must name the **last concrete active function/symbol and thread state**, e.g.:

```text
UNRESOLVED_AT_NVBIT_MODULE_LOADED_ELFMODULEHASHMAP_HASH_PATH
```

not merely “submission begin -> no callback”.

---

## 11. Required final report for the next Codex round

The report must answer, in this order:

1. Did RAW census pass or reproduce?
2. Did EMPTY callback pass or reproduce?
3. What exact stack/symbol is hot in the reproducing case?
4. Is the hot `unordered_map`/hash path ours, Lane G's, or NVBit core's?
5. Did `perf`/symbol evidence indicate hashing, lookup/bucket traversal, rehash, or insertion?
6. Is the behavior finite/one-time or repeated after first use?
7. Can the cost be safely moved before `MEASUREMENT_ACTIVE`?
8. What is the smallest unblock path for Lane G?
9. What remains forbidden before the next authorization?
10. Exact wall times: target / remote transaction / local SSH.
11. Cleanup proof: active GPU process count, diagnostic process count, measurement marker state.
12. Git commit(s), branch, tests, artifact hashes/receipts as required by the existing retry570 publication discipline.

---

## 12. Current working hypothesis ranking

As of this handoff:

1. **NVBit core first-use module/function bookkeeping scalability/pathology** — highest priority, supported by repeated GDB stacks in `Nvbit::module_loaded -> elfModuleHashMap -> unordered_map/hash` plus native controls.
2. **Residual callback/census bookkeeping artifact** — must be excluded by RAW/EMPTY before declaring core responsibility.
3. **Callback reentrancy / concurrency interaction** — secondary; investigate if RAW or our tool remains responsible.
4. **Native CUDA/PyTorch module loading itself** — substantially downgraded by native LAZY/EAGER completion.
5. **`nvdisasm`, target kernel discovery, insertion, GPU execution** — not the current causal boundary.

The shortest path to unblock is therefore **RAW -> EMPTY -> one-time-vs-repeated characterization**, not another long timeout.
