# V40 deterministic hang localization + minimal version-matrix addendum

## Purpose

The current V40 state is not a scientific blocker. The immediate problem is that the launcher did not provide a durable target PID and the marker stream stopped at M0, so the hang phase is still unknown.

Do **not** run more background-shell probes with ambiguous PID ownership.

Implement one deterministic supervisor, localize the phase, then run the smallest useful official-NVBit matrix.

## Stage A — deterministic supervisor

Implement a small Python supervisor, e.g.

`util/vm_tlb/c16/olmoe_v40/run_nvbit_supervised.py`

Requirements:

1. launch the target directly with `subprocess.Popen(argv, env=..., start_new_session=True)`
2. do not wrap the target in shell backgrounding or external `timeout`
3. the returned `Popen.pid` is the authoritative target PID
4. redirect stdout/stderr to durable files
5. write a launcher receipt immediately with:
   - target PID
   - process-group ID
   - argv
   - relevant env
   - start time
   - NVBit root/version/tool SHA
6. poll the target and marker file
7. on timeout, collect diagnostics **before** killing
8. terminate the whole process group:
   - SIGTERM
   - bounded wait
   - SIGKILL if still alive
9. verify no residual target/NVBit/Python process remains

Do not call a timed-out run "rc=124" without also recording the actual child process state.

## Stage B — make marker writes durable and more granular

Every marker write must:
- append one line
- flush
- `os.fsync()`

Keep M0–M6, and add setup markers so M0-only is no longer ambiguous:

- `M0_PROCESS_START`
- `M0A_IMPORTS_BEGIN`
- `M0B_IMPORTS_DONE`
- `M0C_CUDA_INIT_BEGIN`
- `M0D_CUDA_INIT_DONE`
- `M0E_REPLAY_STATE_LOAD_BEGIN`
- `M0F_REPLAY_STATE_LOAD_DONE`
- `M0G_TARGET_READY`
- `M1_BEFORE_EXPERT58_CALL`
- `M2_AFTER_EXPERT58_CALL_RETURN`
- `M3_BEFORE_TORCH_CUDA_SYNCHRONIZE`
- `M4_AFTER_TORCH_CUDA_SYNCHRONIZE`
- `M5_OUTPUT_HASH_CLOSED`
- `M6_BEFORE_NORMAL_PROCESS_EXIT`

Do not change model/replay semantics merely to add markers.

## Stage C — mandatory timeout diagnostics

When a run exceeds the bounded timeout, collect all possible diagnostics before kill.

At minimum:

### host process/thread state
- `ps -o pid,ppid,pgid,stat,etime,wchan:32,cmd -p <PID>`
- `ps -L -p <PID> -o pid,tid,stat,wchan:32,comm`
- `/proc/<PID>/status`
- for every `/proc/<PID>/task/<TID>`:
  - `status`
  - `wchan`
  - `stack` if permitted

### debugger stack
If attach is permitted, after the run is already classified as hung:
- bounded `gdb -batch -ex "set pagination off" -ex "thread apply all bt" -p <PID>`
- apply a short timeout to gdb itself
- failure to attach is recorded, not treated as absence of a hang

### GPU state
- `nvidia-smi`
- compute-process query with PID, memory
- utilization snapshot
- any available per-process monitoring that does not materially perturb the run

### fd/thread evidence
If useful:
- `ls -l /proc/<PID>/fd`
- count receiver/tool threads

Persist all diagnostic files under the V40 run root.

## Stage D — precise hang classification

Use the furthest durable marker plus stacks/GPU state.

Classify exactly one primary phase:

### PRE_TARGET_INIT_HANG
M1 is never reached.

Subtype using M0A–M0G:
- import
- CUDA init
- replay-state load
- target preparation

### TARGET_CALL_HANG
M1 reached, M2 not reached.

### CUDA_SYNC_HANG
M2 and M3 reached, M4 not reached.

### TEARDOWN_HANG
M4/M5/M6 reached but process remains alive.

### CLEAN_EXIT
M6 reached and rc=0 with no residual process.

Do not proceed with a generic "official mem_trace timed out" classification after this addendum.

## Stage E — minimal official-tool matrix

Do **not** test many NVBit versions before the phase is known.

First run exactly these four cells under the deterministic supervisor:

1. NVBit 1.7.7.1 official `opcode_hist`
2. NVBit 1.7.7.1 official `mem_trace`
3. NVBit 1.7.5 official `opcode_hist`
4. NVBit 1.7.5 official `mem_trace`

Use the exact same isolated expert58 replay and runtime.

Run each cell at least twice if the first result is not CLEAN_EXIT.

Record:
- actual-A observed
- nonzero dynamic events where applicable
- furthest marker
- hang phase
- rc
- stack signature
- GPU state
- residual-process state
- tool/version/hash

Only after this 2-version matrix decide whether 1.7.7.3/1.8 adds information.

## Stage F — decisive route selection

### F1 — 1.7.5 mem_trace CLEAN_EXIT

If official NVBit 1.7.5:
- sees actual-A
- produces nonzero dynamic memory events
- reaches M6
- exits rc=0
- leaves no residual process

then stop debugging 1.7.7.1.

Use NVBit 1.7.5 self-consistently for:
- actual-JIT static enumeration
- selector generation
- tracer
- canary
- formal capture

Re-establish all static/selector identities under 1.7.5. Do not reuse 1.7.7.1 static indices without revalidation.

Continue automatically to OLMoE formal capture.

### F2 — both 1.7.5 and 1.7.7.1 mem_trace hang in the same phase on R580

If:
- official opcode_hist is clean or materially healthier, and
- official mem_trace in both versions hangs in the same sync/teardown class, and
- driver remains R580.178.04,

classify:
`NODE109_R580_SM89_NVBIT_MEMTRACE_COMPATIBILITY_BLOCKER`

Do **not** spend another round patching custom C16 tracer code.

Then perform only supported-driver preflight:
- verify whether R575 package/module is already installed or cached
- determine exact downgrade/reboot requirement
- produce rollback plan
- confirm CUDA 12.6/12.8 compatibility
- preserve repo/data/model
- define post-reboot qualification:
  - driver identity
  - torch CUDA smoke
  - official opcode_hist
  - official mem_trace exact replay
  - C16 G1/G2/G4

Stop for human authorization only if a host driver change/reboot is required.

### F3 — version-specific behavior

If one official version cleanly exits and another hangs:
- use the clean version
- continue formal work
- type the NVBit version as deployment identity

Do not keep fixing the failing version.

### F4 — opcode_hist and mem_trace both hang before target

If both tool families stop before M1, investigate injection/runtime initialization rather than Channel/formal logic.

Use the setup-marker subtype and stacks to repair that layer first.

## Stage G — commit evidence before route transition

Before moving to formal capture or driver-preflight, commit/push:

- `SUPERVISOR_RECEIPT.json`
- `HANG_MARKER_TIMELINE.tsv`
- `HANG_STACK_SUMMARY.md`
- `GPU_TIMEOUT_SNAPSHOT.txt`
- `NVBIT_MINIMAL_MATRIX.tsv`
- `ROUTE_SELECTION.json`

Do not leave the decisive compatibility evidence only in transient scratch.

## Important scope

This Goal is allowed to solve ordinary launcher/PID/marker/gdb collection issues itself.

Do not stop because:
- the first supervisor implementation needs repair
- gdb attach needs a different invocation
- marker granularity needs adjustment
- a tool path must be found
- a bounded matrix cell needs rerun

Stop only at:
- a required host driver change/reboot, or
- a genuine scientific identity change.

After a clean NVBit route is found, continue automatically through the original V40 formal-capture path.
