# AI-trace / NVBit server bootstrap and failure-avoidance runbook

## Purpose

This runbook captures the lessons from C16 Lane G Retry570 so that a newly rented GPU server can be qualified quickly without repeating environment, NVBit-version, timeout, or measurement-window mistakes.

It is intentionally conservative: **do not run a model or start scientific capture until the infrastructure gates pass.**

---

## 1. Golden rule: latest is not automatically best

For the observed Lane G environment, NVBit 1.8 is a known bad runtime candidate even though its official tiny example can pass.

The validated working direction is NVBit 1.7.5 for the exact Lane G startup/first-kernel path.

Do not silently upgrade NVBit because a newer release exists. Treat NVBit as part of the experiment configuration and record its version and binary/core hashes just like CUDA/driver/tool source.

### Known-good minimal profile observed on Retry570

```text
GPU                RTX3090
compute capability SM86
driver             570.124.04
CUDA toolkit       12.4
nvcc               12.4.131
nvdisasm           12.4.127
PyTorch            2.5.1+cu124
NVBit              1.7.5
module loading     EAGER for Lane G qualification
```

### Known-bad-for-this-lane profile

Same node/software matrix with NVBit 1.8 reproduced a high-CPU NVBit core module-bookkeeping path:

```text
std::_Hash_bytes
 -> elfModuleHashMap::operator[]
 -> Nvbit::module_loaded
```

This is a scoped observation, not a universal claim that NVBit 1.8 is broken for all workloads.

---

## 2. New-server bootstrap sequence

Always qualify a new rental in this order.

### Gate A — hardware and driver identity

Record, do not merely inspect interactively:

```bash
nvidia-smi
nvidia-smi --query-gpu=name,uuid,driver_version,compute_cap --format=csv,noheader
```

Capture:

- GPU model,
- GPU UUID,
- driver version,
- compute capability,
- visible device count.

If the GPU/SM differs from the known-good profile, classify the machine as `UNVALIDATED_MATRIX`; continue only through tiny qualification gates before model use.

### Gate B — CUDA toolchain identity

Record:

```bash
nvcc --version
command -v nvdisasm || true
/usr/local/cuda-12.4/bin/nvdisasm --version 2>/dev/null || true
ls -l /usr/local/cuda /usr/local/cuda-* 2>/dev/null || true
```

Do not infer CUDA toolkit version from `nvidia-smi` alone.

### Gate C — child-process environment, not login-shell environment

A major historical failure was that `nvdisasm` existed but the **harness child PATH** did not contain its directory.

Before any NVBit run, the harness must verify the environment actually passed to the injected child.

Required contract:

```text
absolute nvdisasm path exists
CUDA bin directory is present in child PATH
NVDISASM=nvdisasm (or an explicitly supported equivalent) is set
```

Do not accept “`command -v nvdisasm` works in my shell” as proof that the runtime child can find it.

Prefer the harness to construct and record its child environment explicitly.

### Gate D — Python/PyTorch identity

Record:

```bash
python3 - <<'PY'
import torch
print('torch=', torch.__version__)
print('torch_cuda=', torch.version.cuda)
print('cuda_available=', torch.cuda.is_available())
if torch.cuda.is_available():
    print('device=', torch.cuda.get_device_name(0))
    print('capability=', torch.cuda.get_device_capability(0))
PY
```

Hash important runtime libraries when experiment reproducibility requires it, e.g. `libtorch_cuda.so`.

### Gate E — NVBit identity

Record:

- release/version,
- installation path,
- archive SHA256 if installed from an official archive,
- `core/libnvbit.a` SHA256,
- tool source commit,
- built tool `.so` SHA256.

For the Retry570 x86_64 NVBit 1.7.5 official archive, preserve the official release artifact checksum in the runtime profile rather than trusting a filename alone.

Never mix headers/core/library files from different NVBit releases in one tool build.

---

## 3. Mandatory smoke ladder before any model

A newly rented server is not model-ready merely because CUDA works.

Run these gates in order.

### Smoke 1 — native CUDA/PyTorch

Run a tiny native PyTorch CUDA operation and synchronize.

Expected: fast completion and normal process exit.

### Smoke 2 — official NVBit example

Use the exact installed NVBit release's official `instr_count_bb + vectoradd` or equivalent tiny example.

PASS requires:

- NVBit banner,
- kernel/instrumentation marker,
- application terminal output,
- normal exit.

If this fails, stop. Do not debug the Lane G tracer yet.

### Smoke 3 — exact minimal PyTorch reproducer with EMPTY/no-op NVBit tool

Use the smallest frozen PyTorch operation known to exercise the problematic path, e.g. the exact `indexSelectLargeIndex` reproducer retained by Lane G.

Purpose: validate NVBit core + PyTorch + CUDA module/library loading before tracer logic is involved.

### Smoke 4 — original Lane G tracer, first-kernel only, no trace

Build the real tracer against the candidate NVBit version.

Use:

```text
CUDA_MODULE_LOADING=EAGER
```

for the current qualified Lane G path unless later evidence supersedes it.

PASS requires:

- first kernel completes,
- process exits,
- `trace_file_count=0`,
- no measurement marker was armed,
- no stale GPU process remains.

Only after all four smokes pass may capture qualification start.

---

## 4. Measurement-window hygiene

Never mix NVBit startup/prewarm with scientific measurement.

Correct lifecycle:

```text
process start
 -> NVBit/CUDA initialization
 -> EAGER module loading / prewarm
 -> runtime ready checks
 -> confirm trace count == 0
 -> create/arm MEASUREMENT_ACTIVE
 -> CAPTURE_BEGIN
 -> target workload
 -> CAPTURE_END
 -> disarm measurement
 -> validate trace
 -> cleanup
```

Rules:

- prewarm time is not scientific runtime;
- prewarm must not create trace files;
- trace files must not pre-exist the measurement window;
- measurement marker must be absent after cleanup;
- a startup timeout is not a trace failure;
- a trace failure must be localized after `CAPTURE_BEGIN`.

---

## 5. Timeout architecture

A historical source of wasted time was a “25 s run” that took minutes end-to-end because only one child sub-step had a 25 s cap.

Use an **external monotonic supervisor**.

Keep three separate budgets:

```text
target process budget
remote transaction budget
local SSH/orchestration budget
```

For example, for a 25 s diagnostic:

```text
target     25 s
remote     ~32 s
local SSH  ~40 s
```

At deadline:

1. TERM the whole target process group;
2. wait a short fixed grace period;
3. KILL the whole process group if needed;
4. reap children;
5. verify no GPU/diagnostic process remains.

GDB/ptrace can suspend the target process and therefore must never be the owner of the only watchdog.

Every receipt should record:

```text
target_wall_s
remote_transaction_wall_s
local_ssh_wall_s
term_sent
kill_sent
cleanup_result
```

---

## 6. If a future server hangs: fastest diagnostic tree

Do not start with a 300 s timeout.

### Step 1 — determine the boundary

Use stage markers and a minimal reproducer to distinguish:

```text
before CUDA operation
CUDA/library API entry
kernel launch callback
instruction discovery
insertion/enable
kernel completion
```

### Step 2 — strip the tool progressively

If the hang is before target kernel instrumentation:

```text
normal diagnostic callback
 -> TRUE RAW callback (preallocated POD only)
 -> EMPTY callback { return; }
```

If EMPTY still reproduces, the problem is below the tracer logic.

### Step 3 — collect CPU-side evidence

Use short GDB/perf snapshots. Classify the active main thread rather than merely noting that some background thread waits on a futex.

Useful classes:

```text
libcuda/module loader
libnvbit/NVBit core
libtorch/ATen
nvdisasm child
waitpid/process wait
mutex/futex main-thread wait
```

### Step 4 — do version differential early

If the EMPTY tool implicates NVBit core, test another known-compatible NVBit release on the same tiny reproducer **before** changing CUDA, driver, PyTorch, or GPU image.

Change one variable at a time.

This would have found the Retry570 1.7.5 path much earlier.

---

## 7. Anti-patterns to avoid

Do not repeat these mistakes:

1. **Assuming latest NVBit is best.** Version is an experimental variable.
2. **Checking PATH only in the login shell.** Validate the actual child environment.
3. **Using long timeout hunting as diagnosis.** Add stage markers and CPU-side evidence first.
4. **Calling callback-only “no-op” while it still uses STL/introspection.** TRUE RAW means fixed POD only; EMPTY means `return;`.
5. **Attributing a stall to a target kernel before the target launch callback exists.** Keep API boundary semantics precise.
6. **Mapping a proxy kernel's `nvbit_get_instrs()` cost onto another kernel without evidence.** Proxy characterization is not target causality.
7. **Treating GDB-perturbed runs as performance data.** They are diagnostic evidence only.
8. **Guessing private vendor STL layout without DWARF.** Prefer symbol/perf/external counts.
9. **Running a model before tiny smokes pass.** Model runs are expensive and low-information during infrastructure debugging.
10. **Mixing startup/prewarm into measurement.** READY must precede `MEASUREMENT_ACTIVE`.
11. **Changing CUDA/driver/NVBit/PyTorch together.** One-variable differential only.
12. **Leaving remote-only evidence.** Hash-close required artifacts locally and record cleanup state.

---

## 8. Suggested automated preflight contract

Provide one command that emits structured, machine-readable status.

Example output:

```text
GPU_IDENTITY=PASS
PROFILE_MATCH=KNOWN_GOOD|UNVALIDATED_MATRIX|KNOWN_BAD
CUDA_TOOLKIT=12.4
DRIVER=570.124.04
PYTORCH=2.5.1+cu124
NVBIT=1.7.5
NVDISASM_PATH=PASS
CHILD_PATH=PASS
CUDA_MODULE_LOADING=EAGER
OFFICIAL_NVBIT_SMOKE=PASS
EXACT_EMPTY_SMOKE=PASS
LANE_G_FIRST_KERNEL_SMOKE=PASS
PREWARM_TRACE_COUNT=0
STALE_GPU_PROCESS=ABSENT
MEASUREMENT_ACTIVE=ABSENT
CAPTURE_ALLOWED=YES|NO
```

Fail closed: `CAPTURE_ALLOWED=YES` only when the required gates for that runtime profile pass.

The preflight tool must diagnose; it must not silently install/upgrade system components.

---

## 9. Re-rental quick-start checklist

On a fresh server, the operator should be able to follow this sequence without rediscovering history:

```text
1. clone/fetch repository and required Lane G commit
2. run environment inventory/preflight
3. materialize the pinned NVBit release
4. verify archive/core/tool hashes
5. verify nvdisasm and child PATH
6. set explicit CUDA_MODULE_LOADING policy
7. run native PyTorch smoke
8. run official NVBit smoke
9. run exact EMPTY PyTorch smoke
10. run Lane G first-kernel no-trace smoke
11. confirm READY + trace_count=0 + cleanup
12. only then run minimal capture qualification
13. only after capture qualification, consider model canary
```

If any step fails, stop at that layer. Do not skip forward.

---

## 10. What must remain durable in the repository

Keep these items versioned:

- known-good/known-bad runtime profiles,
- preflight code and tests,
- the Lane G startup/capture state-machine contract,
- official-smoke and exact-smoke harnesses,
- child PATH / nvdisasm validation,
- external timeout/process-group cleanup utilities,
- receipt schemas,
- this runbook,
- compact root-cause and capture-qualification publications.

The goal is that a new rental should require **qualification, not rediscovery**.
