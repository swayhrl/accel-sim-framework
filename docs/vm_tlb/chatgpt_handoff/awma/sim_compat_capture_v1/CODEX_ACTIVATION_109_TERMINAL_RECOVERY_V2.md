# CODEX ACTIVATION — node109 SIM_COMPAT terminal recovery V2

## Why this stage exists

The first node109 producer attempt correctly stopped fail-closed at:

```text
SIM_COMPAT_CAPTURE_V1_NOT_QUALIFIED_TRACER_TERMINAL_PROTOCOL_SM89
```

Accepted diagnostic branch / commit:

```text
hrl/awma-sim-compat-capture-109-v1
7f38c063fa853525680effd8454d4899c7895ff5
```

Do not reinterpret that attempt as a simulator input. It emitted no READY bundle and must remain diagnostic evidence.

The failure is now narrow:

```text
exact Qwen workload authority       PASS
exact token authority               PASS
SM89 tracer build/injection          PASS
target occurrence discovery          PASS
Q05 target -> observed kernel ID 35  PASS
bounded output volume (~81 MB xz)    PASS/diagnostic
terminal channel closure              FAIL
```

The old receiver never observed/acknowledged the device terminal sentinel after the selected kernel finished. Therefore no COMPLETE / zero-drop-overflow / parser / hash / READY closure was legally issued.

This stage is a **terminal-protocol recovery**, not a redesign of the AWMA project and not a change of scientific target.

## Execution branch

Start from the accepted V1 diagnostic commit above. Create a fresh worktree and branch, for example:

```text
hrl/awma-sim-compat-terminal-recovery-109-v2
```

Preserve the V1 review pack as immutable historical evidence. Create a V2 pack rather than rewriting V1.

## Frozen upstream scientific identity

Nothing about the workload/target changes:

```text
model_id = Qwen/Qwen2.5-0.5B-Instruct
model_revision = 7ae557604adf67be50417f59c2c2f167def9a775
scenario_id = S2_TEXT
input_class = TEXT
phase = PREFILL
batch = 1
prefill_tokens = 2048
decode_tokens = 32
backend = sdpa
dtype = float16
python = 3.10.12
torch = 2.5.1+cu124
transformers = 4.46.3

target_id = Q05_PREFILL_ATTN_FLASH
target_function_occurrence = 0
observed diagnostic kernel id = 35
```

Frozen target function and authority hashes remain those in the accepted consumer contract / V1 producer Goal.

Do not retokenize, shorten context, change dtype/backend/model, change target occurrence, switch to GEMM, or silently define a narrower ROI.

## Accepted consumer checkpoint remains unchanged

```text
174NEW_SIM_CONSUMER_READY_FOR_INPUT_V1
consumer commit = 25aa29862239a408099639ae9d5f1a0ea4fee1e1
SIM_BASELINE_ID = SIM_BASELINE_6305c065f2c4913448b0cb61a85d5003030c5917cd37d6a346fd3f42939d5964
scope = HASH_BOUND_FIXED_WINDOW_10000
```

174-new remains stopped. Do not ask it to consume the V1 diagnostic traces.

## External engineering anchors to inspect

These are engineering clues, not scientific authorities. Verify them from the actual source/release artifacts before using them:

1. NVlabs/NVBit issue #147 documented hangs on SM86/SM89; the reporter later stated 1.7.5 appeared to fix that reproducer.
2. accel-sim/accel-sim-framework issue #374 documented tracer hangs on RTX4090/SM89 with NVBit 1.7.2/1.7.3 and success with older NVBit on that reproducer.
3. NVBit 1.7.7 release notes explicitly introduced:
   - `nvbit_load_tool_module()`
   - `nvbit_find_function_by_name()`
   - `nvbit_launch_kernel()`
   and state that explicit loading/launching of tool kernels such as `flush_channel()` avoids potential tool deadlocks.
4. Current upstream Accel-Sim dev installs a newer NVBit line (currently 1.8), so testing a later NVBit in an **isolated build** is legitimate engineering recovery if trace semantics remain unchanged.
5. Accel-Sim's newer spinlock tool uses a more explicit per-context channel/receiver lifecycle (`ChannelHost.init(..., recv_thread_fun, ctx)` and NVBit tool-thread registration). Treat this as a candidate lifecycle reference, not something to copy blindly.

## Important interpretation of the V1 atomic patch

V1 changed the host flag from volatile bool to `std::atomic<bool>`. Keep or revert it only based on evidence, but understand its scope:

```text
atomic host flag
!=
proof that the device sentinel reached ChannelHost
```

The receiver only finishes when it actually sees the terminal record. Do not solve this stage by simply clearing the flag on the host after a timeout. That would fabricate COMPLETE.

## Goal

Preferred final state remains:

```text
SIM_COMPAT_CAPTURE_V1_PRODUCER_PASS
```

but now with a separately documented terminal recovery:

```text
TERMINAL_PROTOCOL_SM89_RECOVERED_V2
```

The stage ends only after the same formal Q05 target has a genuine simulator-native COMPLETE bundle and is published through the accepted pipeline.

## Goal-mode policy

Use solve-and-continue mode. Recoverable tracer/build/channel problems are engineering work and should be diagnosed and repaired inline.

STOP only if bounded evidence shows that preserving simulator-native trace semantics is impossible with the available supported toolchain, or if an unavoidable external dependency blocks all semantics-preserving recovery paths.

Do not stop at the first failed candidate version or first failed micro-canary.

## GPU safety

Before any GPU test, inspect and acquire:

```text
/data/c16/locks/c16_gpu_campaign.lock
```

Never delete/steal/bypass a live lock and never kill another owner.

Do CPU-only source archaeology and build preparation before holding the GPU lock when practical.

# Recovery ladder

## R0 — Reproduce and freeze the V1 failure evidence

Read completely:

```text
docs/vm_tlb/review_packs/AWMA_SIM_COMPAT_CAPTURE_109_V1/
docs/vm_tlb/codex_handoff/awma/SIM_COMPAT_CAPTURE_109_REPORT.md
util/tracer_nvbit/tracer_tool/tracer_tool.cu
```

Record the exact V1 source/build/binary hashes and the diagnostic trace locations. Do not modify/delete the diagnostic raw traces.

Confirm from source that the legacy protocol is:

```text
user kernel completes
-> launch flush_channel tool kernel
-> push sentinel record
-> channel_dev.flush()
-> receiver sees sentinel
-> receiver clears kernel-receiving flag
-> leave_kernel_launch continues
```

## R1 — CPU-only protocol archaeology

Before another Qwen run, inspect the actual local NVBit 1.7.5 `channel.hpp` plus later official NVBit release artifacts/source examples if available.

Compare at minimum:

```text
NVBit 1.7.5 current local channel/tool-kernel lifecycle
NVBit 1.7.7.x official mem_trace terminal/tool-kernel launch pattern
current NVBit 1.8 pattern if needed
Accel-Sim newer spinlock-tool receiver/channel lifecycle
```

Freeze hashes for every release archive/source file actually used.

Answer with evidence:

```text
Does ChannelDev::flush return only after publication or merely issue publication?
Does ChannelHost::recv require a specific tool pthread registration/lifecycle?
Is implicit CUDA launch of a tool kernel still supported/recommended?
Is ASYNC_COPY_STREAM behavior involved in this local channel.hpp?
Can the terminal record be lost/delayed while payload records were already consumed?
```

Do not guess these answers.

## R2 — Add terminal observability without changing trace semantics

Add diagnostic-only observability sufficient to distinguish the following states:

```text
flush kernel launch attempted
flush kernel entered
sentinel push attempted
channel_dev.flush returned on device path (if observable safely)
flush kernel launch completed on host
host total recv calls / bytes / records
host saw sentinel
trace writer/pclose completed
```

Use sequence/counter markers or managed diagnostic state only if they do not change the scientific trace payload/order.

A bounded watchdog may terminate a diagnostic hang, but timeout must produce FAIL/DIAGNOSTIC, never COMPLETE.

Do not use host-side `recv_thread_receiving=false` as success evidence.

## R3 — Tiny terminal canary before Qwen

Build a minimal reproduction that exercises the same channel terminal path with very small output.

Preferred ladder:

```text
A. flush-only / tiny kernel canary
B. vectoradd or another repository micro-canary with actual traced records
C. repeat A/B at least twice after a candidate fix
```

For each run prove:

```text
sentinel observed by receiver
receiver exits kernel state
writer closes normally
no timeout
trace/list can be fully read
```

If V1's exact legacy path already closes on tiny kernels, record that fact: it indicates a volume/kernel/tool-kernel interaction rather than a universally broken channel.

Do not proceed directly to the 81 MB Qwen target without this ladder.

## R4 — Candidate fixes, in evidence-driven priority order

### Candidate A — Official explicit tool-kernel launch path

Strongly prefer testing the NVBit >=1.7.7 official mechanism that explicitly loads/finds/launches tool kernels instead of relying on the implicit `flush_channel<<<...>>>` path, because the NVBit release notes explicitly associate the new API with avoiding potential tool deadlocks.

Use an isolated NVBit build/install. Do not overwrite the accepted Native-characterization NVBit installation.

A later NVBit version is allowed for Simulation producer qualification because tracer version/build/binary identity is a producer field, not a frozen workload field. However it must receive a new tracer/build identity and pass all trace-semantic regression gates.

Prefer the narrowest compatible later release that contains the terminal-launch fix. If a candidate cannot build/run with node109's CUDA 12.8 / driver 580.178.04, record the exact incompatibility and continue to the next bounded candidate rather than changing the scientific workload.

### Candidate B — Official receiver-thread/channel lifecycle

If Candidate A alone is insufficient, test the documented/working `ChannelHost.init(..., recv_thread_fun, ctx)` / `nvbit_set_tool_pthread(...)` style and, if required, per-context `ChannelDev` lifecycle as used by newer NVBit/Accel-Sim tools.

Do not migrate unrelated tracer functionality. Preserve the existing inst_trace_t payload and output grammar.

### Candidate C — Minimal channel-protocol repair

Only if official lifecycle paths do not solve the issue, make the smallest source-level channel synchronization repair justified by R1/R2 evidence.

Forbidden fixes include:

```text
host fabricates sentinel
host clears receiving flag after arbitrary delay
silently drops tail records
kills receiver and labels file COMPLETE
closes xz pipe without terminal proof
truncates Q05 while keeping the same target identity
```

## R5 — Trace-semantic regression after any version/lifecycle change

Before Qwen formal capture, prove the candidate tracer still produces simulator-compatible semantics.

At minimum:

```text
actual parser/grammar smoke
kernel/list closure
PC/opcode/register/memory fields preserved
memory width/access semantics preserved
warp/CTA/active mask/address semantics preserved
instruction order preserved
sync/control semantics preserved
terminal is device/channel-derived, not host-invented
```

If a later NVBit produces a materially different tracer grammar, do not silently adapt it. Either demonstrate a formally lossless consumer path and update the producer identity/contracts, or stop for scientific review.

## R6 — Exact Q05 target canary

After tiny canaries close reliably, rerun the exact frozen workload/selector.

Re-verify:

```text
frozen model revision
frozen token hashes
S2_TEXT / B1 / T2048 / Decode32
FP16 / SDPA
Q05_PREFILL_ATTN_FLASH
occurrence 0
exact mangled function
observed launch relation (kernel ID may be recorded but target authority remains semantic/function based)
```

Require a bounded target canary to terminal-close cleanly before the formal run.

Prefer at least two successful terminal closures with the candidate protocol before issuing FORMAL evidence.

## R7 — Formal simulator-native capture

Capture the exact same Q05 target. Do not expand to GEMM in this Goal.

Required raw/formal artifacts remain:

```text
kernelslist / kernelslist.g
trace payload(s) / *.traceg.xz as admitted by existing consumer grammar
producer manifest
address/context sidecars
terminal/completeness receipt
source/build/binary/environment receipts
trace-member manifest
SHA256 closure
```

The existing ~81 MB diagnostic size suggests volume is manageable, but recompute actual formal size/headroom.

## R8 — Terminal/completeness proof

PASS requires positive evidence, not absence of a hang:

```text
terminal marker observed through the channel protocol
trace writer closed successfully
all bytes/members readable
terminal_status = COMPLETE
no timeout / forced termination
```

For `drop_count=0` / `overflow_count=0` or native equivalents, derive the claim from the actual channel/tracer implementation and explicit counters/evidence. If the native channel has no explicit drop/overflow counters, document the exact source-backed equivalent and test it. Do not infer zero merely because the process exited.

Add a negative regression proving that suppressing/corrupting the terminal path cannot emit READY.

## R9 — Post-process, parser and hash closure

Only after R8:

```text
post-process to simulator input grammar
actual traceg parser smoke
all kernelslist members exist
full decompression/read
stable repeated hashes
sidecar/source/build/binary/environment closure
```

Then and only then emit READY.

## R10 — Publish and STOP

Use the accepted 109 -> 174/node164 pipeline.

At producer PASS report:

```text
capture/run ID
READY path
WORKLOAD_ID / TARGET relation
tracer version + release/archive hash
tracer source SHA
tracer build SHA
tracer binary SHA
terminal protocol version/receipt SHA
kernelslist SHA
trace-member hash root
sidecar hash root
bundle hash root
address/context fields required by consumer
```

After successful publication:

```text
SIM_COMPAT_CAPTURE_V1_PRODUCER_PASS
TERMINAL_PROTOCOL_SM89_RECOVERED_V2
```

then STOP node109.

Do not create `SIM_INPUT_ID` on 109. Do not run the 10k Accel-Sim replay or mechanism experiments. Those remain 174-new work after independent consumer admission.

# Required V2 evidence

Create:

```text
docs/vm_tlb/review_packs/AWMA_SIM_COMPAT_TERMINAL_RECOVERY_109_V2/
```

Minimum useful contents:

```text
README.md
V1_FAILURE_ANCHOR.md
UPSTREAM_TERMINAL_PROTOCOL_ARCHEOLOGY.md
NVBIT_VERSION_MATRIX.md
TERMINAL_STATE_MACHINE.md
TERMINAL_OBSERVABILITY.md
MICRO_CANARY_MATRIX.tsv
SM89_RECOVERY_DECISION.md
TRACE_SEMANTICS_REGRESSION.md
FORMAL_TARGET_BINDING.json
FORMAL_TERMINAL_AND_COMPLETENESS.md
SIM_COMPAT_CAPTURE_MANIFEST.json
TRACE_MEMBER_MANIFEST.tsv
TRANSFER_RECEIPT.md
CLAIM_BOUNDARY.md
OPEN_ISSUES.md
SHA256SUMS
```

Codex report:

```text
docs/vm_tlb/codex_handoff/awma/SIM_COMPAT_TERMINAL_RECOVERY_109_V2_REPORT.md
```

# Final-state discipline

Allowed success:

```text
SIM_COMPAT_CAPTURE_V1_PRODUCER_PASS
TERMINAL_PROTOCOL_SM89_RECOVERED_V2
```

Allowed non-pass only after bounded recovery:

```text
SIM_COMPAT_CAPTURE_V1_NOT_QUALIFIED_<EXACT_TERMINAL_REASON>
```

Do not use a generic BLOCKED state. Preserve every failed candidate as DIAGNOSTIC with exact source/build/toolchain identity.
