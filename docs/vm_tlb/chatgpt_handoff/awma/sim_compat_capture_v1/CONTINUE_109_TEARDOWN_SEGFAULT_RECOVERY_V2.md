# CONTINUE node109 — V2 teardown-segfault recovery and bounded pivot

## Current checkpoint

The active V2 producer remains fail-closed. The latest operator report states that after migrating:

```text
NVBit 1.7.7.1 explicit tool-module load/find/launch
context-owned channel/receiver state
per-kernel sequence completion
ChannelHost-owned receiver registration
teardown callback suppression
```

the custom Accel-Sim tracer still segfaults during context/tool teardown even in a **no-selected-kernel control**.

No Q05 capture has been resumed and no COMPLETE/READY/SIM_INPUT was issued.

This is not a scientific-identity failure. The failure is now isolated to host-side tool lifecycle / ownership / teardown. Stay in terminal-recovery V2.

## Key interpretation

A no-selected-kernel control has no scientific payload and should require no per-kernel terminal proof. Its only required behavior is:

```text
context/tool initialization
-> channel/receiver initialization if the implementation requires it
-> zero selected-kernel trace activity
-> clean receiver shutdown
-> clean resource destruction
-> natural process exit
```

Therefore a segfault in this control path is evidence of lifecycle/ownership corruption independent of Q05, trace volume and most trace payload semantics.

NVBit 1.7.7 release notes explicitly include a fix for `mem_trace` when a context does not launch any kernel. Use the locally SHA-closed 1.7.7.1 official source as the engineering authority for exact lifecycle behavior.

## Efficiency rule

Do not split this into separate Codex rounds.

Execute continuously:

```text
teardown crash localization
-> bounded surgical lifecycle repair
-> no-selected control PASS
-> selected tiny terminal PASS
-> fresh-process repeat
-> grammar/semantics regression
-> Q05 canary
-> Q05 formal capture
-> READY/hash closure
```

If the surgical route remains unstable after the bounded attempts defined below, pivot automatically in the same Goal to the official-lifecycle scaffold route.

Only stop for a scientific/semantic blocker or an external dependency that prevents both routes.

# Route A — exact teardown crash localization

## A0 Freeze the current broken state

Before modifying code:

- commit or otherwise hash-close the current broken custom tracer source/build/binary;
- preserve the failing no-selected-kernel command line, environment, selector and logs;
- preserve the official 1.7.7.1 passing mem_trace receipts;
- do not overwrite previous V1/V2 diagnostic evidence.

## A1 Obtain the exact host crash site

Run the smallest no-selected-kernel control under host-side crash diagnostics.

Preferred evidence:

```text
core dump + gdb bt full
or
live gdb catch SIGSEGV + bt full
```

Use ASAN/UBSAN only if they can be enabled for the host/tool shared object without changing NVBit/CUDA behavior enough to invalidate the reproducer. Sanitizer failure is not a blocker if a deterministic gdb/core backtrace is available.

Record:

```text
faulting instruction/function
thread ID
callback/lifecycle phase
relevant object addresses
whether the receiver thread is still alive
whether the CUDA context is still valid
last successful lifecycle transition
```

Do not diagnose teardown by print order alone if a real backtrace can be obtained.

## A2 Build a single-ownership table

For every lifecycle object, identify exactly one creator, owner and destroyer:

```text
per-context state object
ChannelDev allocation
ChannelHost object
receiver pthread / ChannelHost-owned thread
tool-pthread registration
loaded tool module / flush CUfunction
per-kernel receive state
trace FILE*/xz pipe
kernelslist/stats handles
context-map entry
```

For each object record:

```text
created at
valid from
valid until
destroyed at
who owns destruction
whether destruction is conditional when zero kernels are selected
```

Explicitly look for:

```text
double pthread join
double ChannelHost destroy
double cudaFree/use-after-free
context-state delete before receiver termination
receiver touching state after map erase
CUDA API use after context teardown has advanced too far
writer close on never-opened handle
per-kernel completion teardown executed when no kernel was armed
callback suppression hiding required NVBit cleanup
```

## A3 Diff lifecycle only against official NVBit 1.7.7.1 mem_trace

Do a structural diff of these phases using the locally SHA-closed official source:

```text
nvbit_at_ctx_init
nvbit_tool_init
channel/receiver initialization
per-kernel receive arming
terminal handling
nvbit_at_ctx_term
receiver STOP/FINISHED transition
join/destroy/free ordering
zero-kernel / zero-selected-kernel behavior
```

Do not copy unrelated mem_trace instrumentation or output formatting.

The official implementation that already passed twice on this RTX4080 is the reference for lifecycle order.

## A4 Bounded surgical repair

Allow at most two evidence-driven surgical repair iterations after A1/A2.

Each candidate must first pass this control ladder:

```text
C0: process loads tool, context exists, selector matches no kernel -> clean exit
C1: vectoradd executes but selector matches no kernel -> clean exit
C2: selected tiny vectoradd -> real records + device/channel terminal + clean exit
C3: fresh-process repeat C2 at least twice
```

For C0/C1:

- do not fabricate or require a per-kernel COMPLETE when no kernel was armed;
- require only safe receiver/context shutdown and natural process exit.

For C2/C3 require the existing terminal/completeness rules.

If Route A passes, continue directly to grammar regression and Q05 in this same Goal.

# Route B — automatic pivot if the hybrid tracer remains unstable

Trigger Route B automatically if either:

```text
- two evidence-driven Route-A repairs still leave teardown unstable; or
- ownership remains structurally ambiguous because old global lifecycle and new ChannelHost-owned lifecycle are interleaved.
```

Do not spend further rounds patching individual flags/destructors.

## B1 Official-lifecycle scaffold

Create a clean isolated tracer implementation whose lifecycle skeleton is derived from the locally verified NVBit 1.7.7.1 `mem_trace` implementation that terminal-closes on this host.

Preserve the official lifecycle essentially intact:

```text
context state
ChannelDev/ChannelHost ownership
receiver thread ownership
explicit tool-module load/find/launch
per-kernel terminal protocol
context shutdown
zero-kernel behavior
```

Then port only the minimum Accel-Sim-specific semantics required by the consumer:

```text
existing inst_trace_t-equivalent packet semantics
static instrumentation fields
PC/opcode/register fields
memory width/address fields
warp/CTA/mask fields
instruction ordering
sync/control semantics
kernelslist metadata
existing traceg text grammar / post-processing contract
```

Do not port the old tracer's lifecycle machinery into this scaffold.

This route creates a new producer tracer implementation/build identity, which is allowed. It does not change the frozen workload/input/target identity.

## B2 Grammar compatibility gate

Before Q05, prove on tiny vectoradd that the official-lifecycle scaffold emits the same admitted simulator grammar/semantics expected by the 174-new consumer.

Required:

```text
actual Accel-Sim parser smoke
field/ordering regression
kernel/list closure
terminal provenance
fresh-process repeat >= 2
```

Byte-for-byte equality with old diagnostic traces is not required; semantic/grammar compatibility is required.

# After either route succeeds

Proceed without stopping:

```text
no-selected control PASS
selected tiny PASS x2+
parser/grammar/semantics regression PASS
-> exact frozen Q05 target re-resolution
-> bounded Q05 canary
-> formal Q05 capture
-> COMPLETE / zero-drop-overflow or source-backed equivalent
-> parser/hash closure
-> accepted pipeline READY
-> review pack/report/commit/push
```

Frozen Q05 authority remains unchanged:

```text
Qwen/Qwen2.5-0.5B-Instruct
revision 7ae557604adf67be50417f59c2c2f167def9a775
S2_TEXT / PREFILL
B1 / T2048 / Decode32
FP16 / SDPA
Q05_PREFILL_ATTN_FLASH
occurrence 0
```

Previous numeric kernel ID 35 is diagnostic only; re-resolve semantic/function/occurrence binding in the successful process.

# Do not do

Do not:

```text
switch target/model/backend/dtype/context
resume Q05 before lifecycle controls pass
accept process exit as terminal proof
fake COMPLETE on host timeout
kill receiver and call the trace complete
reuse stale completion state
mix Native C16WARP1 into simulator input
run SIM_INPUT admission or 10k simulation on node109
```

# Evidence to add

Continue updating:

```text
docs/vm_tlb/review_packs/AWMA_SIM_COMPAT_TERMINAL_RECOVERY_109_V2/
docs/vm_tlb/codex_handoff/awma/SIM_COMPAT_TERMINAL_RECOVERY_109_V2_REPORT.md
```

Add at minimum:

```text
TEARDOWN_SEGFAULT_BACKTRACE.md
LIFECYCLE_OWNERSHIP_TABLE.md
OFFICIAL_1771_LIFECYCLE_DIFF.md
NO_SELECTED_CONTROL_MATRIX.tsv
SURGICAL_REPAIR_DECISION.md
```

If Route B is triggered also add:

```text
OFFICIAL_LIFECYCLE_SCAFFOLD.md
SCAFFOLD_SOURCE_BUILD_RECEIPT.md
SCAFFOLD_TRACE_SEMANTICS_REGRESSION.md
```

# Final states

Preferred:

```text
SIM_COMPAT_CAPTURE_V1_PRODUCER_PASS
TERMINAL_PROTOCOL_SM89_RECOVERED_V2
```

If both Route A and Route B are exhausted with evidence, then and only then use a non-pass state naming the exact remaining lifecycle/semantic blocker.
