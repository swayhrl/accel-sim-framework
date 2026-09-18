# C16 OLMoE NVBit runtime compatibility qualification and formal-route closure — node109 V40

## Goal mode

Execute in **GOAL MODE** on node109.

This Goal supersedes further blind repair of the V39 custom tracer.

The current scientific target is unchanged. The immediate objective is to determine whether the actual-A non-exit is:
1. a target-kernel execution hang,
2. an NVBit synchronization/Channel/teardown hang,
3. an NVBit-version-specific regression,
4. or a host-driver compatibility failure.

Then automatically choose the first evidence-clean route to formal capture.

Suggested implementation branch:

`hrl/c16-olmoe-nvbit-runtime-compat-109-v40`

## Accepted upstream facts

Accepted from V34–V39R3:
- OLMoE model/input/replay authority closed
- natural expert58 down_proj target closed
- actual JIT variant-A identity closed
- 1096 static instructions closed
- complete 243 address-bearing selector closed
- V38 all-static and selector SHA identities closed
- NVBit 1.7.7.1 C0/C1 and C16WARP1 G0/G1/G2/G3/G4 engineering controls closed
- official NVBit 1.7.7.1 mem_trace on exact actual-A produces nonzero memory-address events
- three injection identity modes were tried:
  - LD_PRELOAD
  - CUDA_INJECTION64_PATH
  - CUDA_INJECTION64_PATH + NO_EAGER_LOAD=0
- all produced actual-A events but did not return normally; one timed out at 90 seconds
- no hung/partial attempt is formal evidence

Do not reopen the scientific target.

## External compatibility evidence to record locally

Record and hash/snapshot authoritative references or exact text receipts sufficient to establish:

1. NVBit official current requirement:
   `CUDA driver version <= 575.xx`

2. NVBit issue #147 documents hangs at cudaDeviceSynchronize on SM86/SM89, including reports for RTX4090.

3. NVBit 1.7.7 release changed mem_trace synchronization/Channel/tool-module behavior specifically to avoid deadlocks and removed kernel execution serialization.

These are engineering compatibility clues, not scientific workload results.

## Stage 0 — preserve current P0 evidence

Before new experiments, commit a receipt for the current official-mem_trace P0 attempts.

For each injection identity record:
- NVBit version/root/hash
- exact official tool binary hash
- exact replay commit/input/output hash
- actual-A function/fingerprint
- first/last observed dynamic event time if available
- timeout
- rc
- stdout/stderr tail
- cleanup result

No partial output enters formal data.

## Stage 1 — establish exact host/runtime compatibility identity

Record:
- GPU model
- compute capability
- NVIDIA driver version
- kernel module version
- libcuda path/hash
- CUDA runtime visible to torch
- torch/transformers/cublas package versions
- CUDA toolkit used to build NVBit tools
- current NVBit versions available on node

If driver version is greater than 575.xx, classify:

`NVBIT_VENDOR_SUPPORT_MATRIX_MISMATCH`

This classification alone is not yet proof that it caused the hang, but it prevents endless unsupported-environment patching.

Do not change the host driver in this Goal without an already-installed safe alternative and explicit non-disruptive activation path. Do not reboot silently.

## Stage 2 — localize the hang: target execution vs tool teardown

Instrument the exact replay script with host-side durable markers written/flushed to a file:

- `M0_PROCESS_START`
- `M1_BEFORE_EXPERT58_CALL`
- `M2_AFTER_EXPERT58_CALL_RETURN`
- `M3_BEFORE_TORCH_CUDA_SYNCHRONIZE`
- `M4_AFTER_TORCH_CUDA_SYNCHRONIZE`
- `M5_OUTPUT_HASH_CLOSED`
- `M6_BEFORE_NORMAL_PROCESS_EXIT`

Run under official mem_trace.

At timeout, collect before kill:
- marker file
- `nvidia-smi` process/utilization/memory
- host process/thread stacks using gdb/pstack if permitted
- receiver-thread stack if visible
- child threads
- open fds/pipes as useful
- process state

Classify:

### EXECUTION_HANG
if M2/M4 cannot be reached and GPU remains inside/saturated by the instrumented kernel/synchronize.

### TEARDOWN_HANG
if M4/M5/M6 are reached but process remains alive.

### TOOL_SYNC_HANG
if call returns but explicit CUDA synchronize does not.

This stage is mandatory. Do not use generic "timeout" after this point.

## Stage 3 — bounded official NVBit version matrix on current driver

Use only official tools first. No C16 custom tracer.

Test exact actual-A replay under available/reasonably obtainable versions, in this priority:

1. NVBit 1.7.5 — high priority because C16 previously used 1.7.5 successfully on this node for other accepted anchors
2. NVBit 1.7.7.1 — current failing reference
3. NVBit 1.7.7.3 — if easily obtainable from official release
4. NVBit 1.8 — optional only if its official binary can run with the installed toolkit/driver without unrelated environment surgery

For each version run:
- official opcode_hist
- official mem_trace
- exact same OLMoE replay

Record:
- static/function identity visibility
- nonzero actual-A events
- M0–M6 markers
- rc
- timeout
- hang phase
- tool/driver identity

Do not compare event totals across versions as scientific workload results.

### Clean-version gate

A version is usable for formal route only if:
- actual-A is observed
- nonzero dynamic memory events are obtained
- replay output hash is correct
- M6 is reached
- process rc=0
- no stale receiver/tool process remains
- repeated fresh runs close consistently

## Stage 4 — route selection

### Route A — a clean NVBit version exists on current driver

If 1.7.5 or another version cleanly exits:

Use that version **self-consistently** for the entire formal stack:
- actual-JIT static enumeration
- selector generation
- tracer build
- canary
- formal capture

Do not mix static identity from 1.7.7.1 with runtime tracer from another version.

Re-establish:
- actual function identity
- all-static instruction count/hash
- complete selected set/hash
- exact load address-source semantics

The old V38 hashes are comparison anchors only; exact equality is welcome but not required after an NVBit-version deployment change. If they differ, type the new deployment; do not silently reuse old selectors.

Before formal:
- regenerate C0/C1
- G1/G2/G4 under selected version
- typed input/weight/output canaries
- bitwise replay output

Then automatically continue to the complete formal capture/admission stages below.

### Route B — every official NVBit version shows the same non-exit class on current R580 driver

If:
- driver >575.xx, and
- multiple official NVBit versions reproduce the same SM89 execution/sync/teardown hang,

close:

`NODE109_R580_NVBIT_SM89_RUNTIME_COMPATIBILITY_BLOCKER`

At this point:
- STOP all user-space tracer patching on R580
- do not attempt P1–P5/custom helper hacks
- prepare a supported-driver migration receipt and exact continuation plan

The required supported host condition is:
- same RTX4080/SM89 if possible
- NVIDIA driver <=575.xx
- driver new enough for CUDA 12.x/CUDA 12.8 runtime compatibility
- preferably R575

Do not perform system-wide driver downgrade/reboot without explicit host-change authorization.

### Route C — version-specific official-tool behavior identifies a narrower NVBit regression

If one version has a distinct hang phase and another cleanly exits, use the clean version and proceed via Route A.

Do not continue debugging the failing version merely to preserve 1.7.7.1.

## Stage 5 — supported-driver preflight if Route B

Without changing the driver, inspect whether node109 already has:
- an installed R575 package/module
- cached package artifacts
- a second boot entry/kernel/module combination
- sudo privileges
- a documented maintenance/reboot mechanism

Also check for any project-authorized alternate GPU host with:
- SM89 or compatible GPU
- NVIDIA driver <=575.xx
- enough VRAM for OLMoE

Do not use an alternate GPU architecture as if it were the same deployment without typing the change.

Produce:
- exact driver migration commands/options
- rollback plan
- expected reboot requirement
- expected CUDA 12.6/12.8 compatibility
- data/model preservation statement
- post-boot qualification checklist

Then STOP for host-change authorization only if a reboot/driver replacement is actually required.

This is the one valid human checkpoint in Route B.

## Stage 6 — formal capture after Route A or post-supported-driver qualification

Once a clean self-consistent NVBit/runtime route is established:

1. exact actual-A/natural target replay
2. static map
3. complete selected address-bearing set
4. same-process input/weight/output address contexts
5. typed canaries
6. one independently replayed shard per selected static instruction
7. clean executed/zero partition
8. overflow/accounting/terminal closure
9. per-shard line/page/event distributions
10. typed object fractions
11. serial node164 admission
12. positive ACK

`FORMAL_ADMISSION_CONCURRENCY=1`

No cross-shard VA union/chronology/reuse-distance/cache-TLB causality.

## Stage 7 — third-lineage handoff

After positive ACK authorize:

`OLMOE_FORMAL_ANCHOR_CLOSED_FOR_THREE_LINEAGE_MOE_CONSUMER`

The handoff must type:
- driver
- NVBit version
- actual JIT function/fingerprint
- semantic target
- variant condition
- static selected set
- executed/zero
- events/page/line distributions
- object fractions
- admission/ACK identities

If a driver or NVBit version changed from V38/V39, explicitly state that deployment change.

## Review pack

Create/finalize:

`docs/vm_tlb/review_packs/C16_OLMOE_NVBIT_RUNTIME_COMPAT_109_V40/`

At least:
- `UPSTREAM_V39R3_AUTHORITY.json`
- `P0_OFFICIAL_MEMTRACE_BASELINE.tsv`
- `HOST_DRIVER_RUNTIME_IDENTITY.json`
- `NVBIT_SUPPORT_MATRIX_RECEIPT.json`
- `HANG_PHASE_LOCALIZATION.json`
- `NVBIT_VERSION_MATRIX.tsv`
- `ROUTE_SELECTION.json`
- Route A formal evidence OR Route B supported-driver migration preflight
- `FINAL_DECISION.json`
- `OPEN_ISSUES.md`
- `SHA256SUMS`

## Preferred final outcomes

If a clean version works:
`C16_OLMOE_NVBIT_RUNTIME_COMPAT_109_V40_PASS_CLEAN_NVBIT_ROUTE_AND_FORMAL_ANCHOR`

If R580 is the confirmed common blocker:
`C16_OLMOE_NVBIT_RUNTIME_COMPAT_109_V40_BLOCKED_HOST_DRIVER_OUTSIDE_SUPPORTED_NVBIT_MATRIX`

The latter is a real environment blocker, not a tracer-engineering blocker.

## Engineering guidance

Routine version build, official-tool setup, phase-marker plumbing, stack collection, and retry issues are solve-and-continue.

Do not spend another long round modifying custom C16 tracer code until the official-tool/runtime matrix is closed.

## Git / cleanup

Use existing node109 Git transport.

Commit/push each major compatibility receipt so evidence is not lost.

At end:
- canonical remote verification
- clean worktree
- release GPU lock
- no stale CUDA/NVBit process
- GPU baseline restored
- retain OLMoE replica
- retain useful NVBit versions/tools
