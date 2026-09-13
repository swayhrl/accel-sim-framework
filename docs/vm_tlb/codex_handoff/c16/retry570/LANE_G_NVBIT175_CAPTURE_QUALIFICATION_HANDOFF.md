# C16 Lane G Retry570 — NVBit 1.7.5 capture qualification handoff

## 0. Mission

The root-cause phase is complete enough to stop debugging NVBit 1.8 for this lane.

The next goal is to **promote NVBit 1.7.5 from a working diagnostic candidate to a reproducible Lane G capture runtime**, while keeping prewarm/startup strictly outside the scientific measurement window.

This handoff is docs-only. Do not checkout/reset/merge this handoff branch into the active Lane G worktree merely to read it.

### Anchors

- repository: `swayhrl/accel-sim-framework`
- active Lane G branch: `hrl/vm-c16-g-retry570-v0`
- active remote head at handoff creation: `ac4f678a815954e4ddb22c15d9a8d3841fca86a3`
- prior root-cause handoff: `43c50becb8b3bc41673f77f5674bf15308954440`
- handoff branch: `hrl/vm-c16-g-retry570-chatgpt-handoff-v2`

The current Codex session may have local or not-yet-pushed work newer than the anchor above. Preserve it. Treat the current worktree as source of truth for code state, and this document as execution policy.

---

## 1. Facts now established

### 1.1 NVBit 1.8 is not the Lane G runtime candidate on this node

Under the observed RTX3090/SM86 + driver 570.124.04 + CUDA 12.4 + PyTorch 2.5.1+cu124 environment:

- NVBit 1.8 official tiny smoke can pass.
- But exact PyTorch first-use/module paths reproduce a high-CPU host-side core path in:

```text
std::_Hash_bytes
  -> elfModuleHashMap::operator[]
  -> Nvbit::module_loaded
  -> nvbitToolsCallbackFunc
```

- TRUE RAW callback census hangs.
- EMPTY callback also hangs.
- Therefore the callback/tool implementation is not the primary cause.
- Native LAZY/EAGER controls complete.
- The pathology is version-sensitive core behavior, not a general CUDA/PyTorch failure.

Status to retain:

```text
NVBIT_CORE_MODULE_BOOKKEEPING_PATHOLOGY_CONFIRMED
```

for NVBit 1.8 on the current validated matrix.

Do not spend more Lane G time reverse engineering the private vendor STL map unless a later task explicitly requires an NVBit upstream bug report.

### 1.2 NVBit 1.7.5 provides the current engineering path

Evidence already observed in the current Codex session:

1. Official NVBit 1.7.5 `instr_count_bb + vectoradd` PASS (~1.2 s).
2. Same EMPTY exact + LAZY reproducer that stalls under 1.8 completes under 1.7.5 (~5.77 s).
3. Original Lane G tracer rebuilt against NVBit 1.7.5, with EAGER loading, completes a minimal PyTorch first-kernel smoke (~6.76 s remote / ~7.18 s local SSH observed) with `trace_file_count=0`.

Before starting the next phase, Codex must finish hash/receipt/publication closure for these results and bind the exact source/tool/core SHA values. If any number above differs in the final authoritative receipt, use the receipt rather than this summary.

The working classification is:

```text
NVBIT_VERSION_SENSITIVE_CORE_PATH
NVBIT_1_7_5_LANE_G_FIRST_KERNEL_PATH_PASS
```

This does **not** yet mean full AI/model trace is qualified.

---

## 2. First action — close the 1.7.5 qualification evidence

Before introducing any new capture behavior:

1. Finish the current 1.7.5 version-differential/P3 publication.
2. Push the authoritative commit to the active Lane G branch.
3. Record and hash-close:
   - NVBit 1.7.5 archive/core/tool identity,
   - Lane G tracer source commit,
   - built tracer `.so` SHA256,
   - official smoke receipt,
   - exact EMPTY receipt,
   - first-kernel smoke receipt,
   - remote/local wall times,
   - `trace_file_count=0`,
   - cleanup state.
4. Update `LATEST_RUNTIME_STATUS.md` so the new 1.7.5 path supersedes the old “startup not qualified” interpretation for future work, without deleting historical evidence.

Do not start model work while this closure is incomplete.

---

## 3. Freeze a known-good runtime profile

Create a machine-readable profile, or equivalent frozen config, for the currently validated matrix. Suggested location:

```text
docs/vm_tlb/runtime_profiles/NVBIT_LANE_G_RTX3090_CUDA124_KNOWN_GOOD.json
```

Required fields:

```text
profile_status: KNOWN_GOOD_FOR_MINIMAL_LANE_G_FIRST_KERNEL
GPU: RTX3090
compute_capability: SM86
driver: 570.124.04
CUDA toolkit: 12.4
nvcc: 12.4.131
nvdisasm: 12.4.127
PyTorch: 2.5.1+cu124
NVBit: 1.7.5
CUDA_MODULE_LOADING: EAGER
absolute nvdisasm path
NVBit archive/core SHA256
Lane G tracer source commit
Lane G tracer binary SHA256
validation receipt references
```

Also record a `KNOWN_BAD_FOR_THIS_LANE` entry for NVBit 1.8 on the same matrix, with the root-cause publication reference. This prevents a future operator from “upgrading to latest” and silently reintroducing the failure.

Do not claim that 1.7.5 is universally better than 1.8. The claim is scoped to this Lane G workload/environment.

---

## 4. Capture qualification ladder

Do not jump from first-kernel smoke directly to Llama/Qwen.

### Q0 — runtime/prewarm gate

Use NVBit 1.7.5 and the **original Lane G tracer**, with:

```text
CUDA_MODULE_LOADING=EAGER
```

Prewarm/startup happens before `MEASUREMENT_ACTIVE` exists.

Required assertions before arming capture:

- correct GPU/driver/CUDA/PyTorch/NVBit profile recorded,
- `nvdisasm` absolute path exists,
- child PATH contains the CUDA bin directory,
- `NVDISASM=nvdisasm` or equivalent frozen contract is effective,
- official tiny smoke has passed for this installation,
- Lane G first-kernel smoke has passed,
- `trace_file_count=0` before capture arm,
- no stale measurement marker,
- no stale GPU/diagnostic process.

Emit an explicit:

```text
LANE_G_RUNTIME_READY
```

only after all checks pass.

### Q1 — minimal deterministic capture canary

Use a tiny deterministic PyTorch reproducer, preferably the already frozen exact `indexSelectLargeIndex` microreproducer because its identity is known.

Do **not** use a full model.

The capture must be deliberately small and bounded. The important purpose is to prove:

1. capture can be armed after prewarm;
2. at least one intended target event/record is emitted;
3. the output parses successfully;
4. no startup/prewarm event contaminates the capture;
5. the capture terminates and cleans up;
6. the result is reproducible in a second independent process.

Required timeline:

```text
PROCESS_START
  -> EAGER/NVBit initialization
  -> prewarm
  -> LANE_G_RUNTIME_READY
  -> verify trace_file_count == 0
  -> create/arm MEASUREMENT_ACTIVE
  -> CAPTURE_BEGIN
  -> execute one tiny deterministic target operation
  -> CAPTURE_END
  -> disarm/remove MEASUREMENT_ACTIVE
  -> parse/validate trace
  -> cleanup
```

Do not retroactively treat prewarm time as scientific runtime.

### Q1 acceptance criteria

PASS only if all are true:

- process exits normally;
- no timeout/forced kill;
- capture output exists;
- output is non-empty if the tracer contract says the target should emit records;
- records are parseable;
- target/kernel/function identity matches the intended tiny reproducer;
- no record timestamp/sequence precedes `CAPTURE_BEGIN`;
- no trace file existed before arming capture;
- second independent run reproduces the same qualitative target identity and record schema;
- all retained artifacts are hash-closed;
- active GPU process count returns to zero;
- measurement marker is absent after cleanup.

If the tracer is designed to emit zero records for this exact operation, stop and explain why from the tracer contract; do not fake a positive canary by changing the workload ad hoc.

### Q2 — tracer correctness, not performance

Only after Q1 PASS, validate the smallest correctness invariants required by the Lane G trace format, for example:

- required header/version fields,
- kernel/function identity,
- instruction/memory-operation fields required by downstream analysis,
- monotonically valid sequence/event ordering,
- no truncated final record,
- no duplicate file append from prewarm,
- parser round-trip or schema validation.

No model yet.

### Q3 — stop for review before model canary

After Q1/Q2 PASS, publish a compact capture-qualification pack and stop for user/ChatGPT review.

Do not run Llama/Qwen in this phase unless a new instruction explicitly authorizes the model canary.

---

## 5. Failure handling during Q0–Q2

Use short, information-producing failures.

If NVBit 1.7.5 startup fails:

1. verify profile/path first;
2. rerun official tiny smoke;
3. rerun minimal first-kernel smoke;
4. only then inspect tracer-specific code.

If capture arm succeeds but produces no target records:

1. verify target/filter identity;
2. verify capture window ordering;
3. verify target operation actually executed;
4. inspect tracer filter semantics;
5. do not immediately increase wall time or switch to a model.

If the process stalls before capture begins, classify it as startup/runtime and do not treat it as a trace failure.

If the process stalls after capture begins, record the last completed capture-stage marker and only then inspect trace/instrumentation paths.

---

## 6. Runtime budget contract

Keep the externally supervised process-group design introduced during root-cause debugging.

For tiny Q0/Q1 diagnostics, choose a bounded budget based on observed ~7 s first-kernel completion, e.g. a conservative 30 s target cap unless existing lane policy specifies a tighter one.

Always report separately:

```text
target_wall_s
remote_transaction_wall_s
local_ssh_wall_s
```

Timeout owner must be outside the target process. On deadline:

```text
TERM whole process group
-> short grace
-> KILL whole process group if required
-> reap
-> verify GPU/process/measurement cleanup
```

Never label a several-minute orchestration as a “25 s run” merely because one child had a 25 s internal cap.

---

## 7. Prohibited actions for this phase

Until Q1/Q2 closeout is reviewed:

- no Llama/Qwen/full model,
- no C frozen target,
- no long 300 s watch,
- no historical 6+6 rerun,
- no CUDA/driver upgrade or downgrade,
- no NVBit 1.8 re-debugging,
- no broad trace capture,
- no scientific performance claims from prewarm/startup time.

Do not change multiple variables at once.

---

## 8. Required reusable infrastructure

As part of this phase, implement or consolidate a **server bootstrap/preflight path** so a future rented server can be qualified without repeating this incident.

At minimum provide:

1. a human runbook: `docs/vm_tlb/runbooks/AI_TRACE_NVBIT_SERVER_BOOTSTRAP.md`;
2. a machine-readable known-good profile;
3. a preflight command/script that prints a single structured result such as:

```text
PROFILE_MATCH=KNOWN_GOOD
NVDISASM_PATH=PASS
CHILD_PATH=PASS
OFFICIAL_NVBIT_SMOKE=PASS
PYTORCH_FIRST_KERNEL_SMOKE=PASS
CAPTURE_ALLOWED=NO|YES
```

4. focused tests for profile parsing/path propagation/fail-closed behavior.

The preflight must **not** silently install or upgrade CUDA/driver/NVBit. It diagnoses and reports; installation/remediation is a separate explicit action.

---

## 9. Required next report

The next Codex report must lead with:

```text
NVBIT_175_EVIDENCE_CLOSEOUT_COMMIT=
KNOWN_GOOD_PROFILE=
Q0_RUNTIME_READY=PASS/FAIL
Q1_MINIMAL_CAPTURE=PASS/FAIL
Q1_RUN1_RECORD_COUNT=
Q1_RUN2_RECORD_COUNT=
PREWARM_TRACE_COUNT=
TRACE_SCHEMA_VALIDATION=PASS/FAIL
MEASUREMENT_WINDOW_CLEAN=PASS/FAIL
TARGET_WALL_S=
REMOTE_WALL_S=
LOCAL_SSH_WALL_S=
ACTIVE_GPU_PROCESS_COUNT=
MEASUREMENT_ACTIVE_AFTER_RUN=ABSENT/PRESENT
BOOTSTRAP_RUNBOOK_COMMIT=
```

Then provide tests, hashes, manifests and publication references.

The success criterion for this phase is **not** “a model was traced.” It is:

> NVBit 1.7.5 is frozen as a reproducible runtime candidate, startup/prewarm is isolated from measurement, and a tiny deterministic Lane G capture is produced and validated twice with clean lifecycle semantics.
