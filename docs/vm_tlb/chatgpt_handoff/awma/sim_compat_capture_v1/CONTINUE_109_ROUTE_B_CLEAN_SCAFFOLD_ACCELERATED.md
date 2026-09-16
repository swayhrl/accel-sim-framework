# CONTINUE node109 — Route B clean-scaffold accelerated closure

## Decision

Route A is closed for this V2 recovery. Do not spend more time patching the old Accel-Sim tracer lifecycle.

Accepted Route-A evidence:

```text
- gdb localized the control-path failure into Nvbit::load_tool_module / custom context lifecycle
- surgical repair #1 (defer explicit module load to tool-init) did not make C0 exit cleanly
- surgical repair #2 (context-owned state + teardown suppression) did not make C0 exit cleanly
- official NVBit 1.7.7.1 mem_trace has already terminal-closed vectoradd twice on the same RTX4080
```

The remaining work is Route B: use the locally frozen and already verified official NVBit 1.7.7.1 `mem_trace` lifecycle as the control-plane scaffold, then add only the Accel-Sim simulator-trace data plane.

This is still the same V2 scientific stage. Workload/target identity does not change.

## Core rule: scaffold owns lifecycle; Accel-Sim only contributes data semantics

Treat the official 1.7.7.1 lifecycle as the authority for:

```text
context creation/destruction
tool module load/find/launch
ChannelDev allocation/free
ChannelHost initialization/destruction
receiver-thread registration and lifecycle
callback-reentry suppression
context map ownership
STOP/FINISHED sequencing
zero-selected / zero-kernel teardown behavior
```

Do NOT port these old Accel-Sim lifecycle elements into Route B unless an explicit source-backed reason is documented:

```text
legacy global ChannelHost / ChannelDev ownership
legacy recv_thread_started / recv_thread_receiving protocol
manual pthread ownership when ChannelHost owns/registers the receiver
legacy implicit flush_channel<<<...>>> launch path
legacy context teardown ordering
legacy host-side terminal completion flags
legacy global writer lifecycle that is not context/kernel owned
```

Only migrate the minimum data-plane semantics required for the existing Accel-Sim trace grammar:

```text
inst_trace_t payload definition
instrument_inst semantics
PC/opcode/register src/dst fields
memory flag / width / addresses
warp/CTA IDs
active/predicate mask
immediate/control information
instruction order
data/address compression if grammar-compatible
trace header + kernelslist metadata
traceg-compatible text renderer
```

Do not convert official `mem_trace` memory-only output post hoc into traceg. Route B must directly emit the simulator-native instruction trace semantics required by the consumer.

## Frozen local official sources

The operator reports these locally frozen authorities; verify the full hashes and paths before use:

```text
official_mem_trace_1771.cu    SHA prefix 0ab05d...
official_inject_funcs_1771.cu SHA prefix 930e26...
official_common_1771.h        SHA prefix 48116d...
```

Record full SHA256 values in the V2 review pack.

## Accelerated continuous Goal

Do not stop at intermediate engineering milestones. Execute B0 -> B1 -> B2 -> B3 -> B4 -> B5 continuously unless a change would alter scientific trace semantics or workload identity.

### B0 — Clean scaffold equivalence / lifecycle isolation

Create a new Route-B tracer implementation in a clearly separate source path or files. Do not keep layering the old Route-A source.

Start from the official 1.7.7.1 lifecycle structure and preserve its ordering closely enough that lifecycle diffs are auditable.

Before adding `inst_trace_t`, validate controls:

```text
C0: process creates tool/context, selector selects no kernel -> natural exit
C1: vectoradd executes, selector selects no kernel -> natural exit
```

Run each from fresh processes multiple times (>=3 recommended because these are cheap).

Requirements:

```text
no segfault
no hang
no watchdog/kill
receiver reaches official terminal shutdown state
channel is destroyed only after receiver shutdown
managed device state is freed only after channel/receiver completion
no per-kernel COMPLETE is claimed when no kernel was armed
```

If B0 cannot match the already-working official scaffold behavior, diff Route-B lifecycle line-by-line against the frozen official source before changing anything else.

### B1 — Replace only the channel packet/payload

After B0 passes, change only the device/host packet from official mem-trace payload to the existing Accel-Sim `inst_trace_t` semantics, preserving official lifecycle and terminal mechanism.

Use a selected tiny vectoradd.

Prove separately:

```text
real instruction packets received
real memory-address packets received
terminal sentinel is a distinct protocol event and is observed by receiver
writer is not closed before terminal acknowledgement
process exits naturally
```

The terminal/control record must not be confused with a valid `inst_trace_t` data record. If the old `cta_id_x == -1` sentinel representation is reused, prove that it cannot collide with real records and that official channel flushing preserves it. A dedicated terminal packet/tag is allowed if it is an internal channel protocol detail and does not alter emitted traceg grammar.

Repeat selected tiny closure from fresh process >=2 times.

### B2 — Port renderer and exact existing trace grammar

Only after B1 is stable, add the Accel-Sim text trace renderer, trace header, kernelslist/stats metadata and xz writer.

Keep file/writer ownership per context/per selected kernel. Explicitly model:

```text
UNOPENED
OPEN
TERMINAL_ACKED
CLOSED
```

Never close an unopened handle and never let context teardown synthesize per-kernel closure.

Run tiny vectoradd and prove:

```text
kernelslist/list closure
trace member fully decompresses
actual Accel-Sim parser/grammar smoke passes
PC/opcode/register fields are present
memory width/address semantics are present
warp/CTA/mask semantics are present
instruction ordering is preserved
sync/control representation required by consumer is preserved
terminal provenance remains device/channel-derived
```

Run negative tests:

```text
suppress/corrupt terminal => no COMPLETE / no READY
missing trace member => admission helper rejects
malformed record => parser smoke fails
```

### B3 — Semantic regression / source-bound equivalence

Compare Route-B tiny output against the accepted existing Accel-Sim grammar/consumer expectations, not against official memory-only output.

Freeze a semantic field matrix showing where each consumer-required field originates in Route B:

```text
pc
opcode
access_kind
memory_space
byte_width
warp_id
cta_id
active_mask
lane_addresses
event_order
sync_control
```

Important: if the legacy tracer grammar itself does not directly encode a consumer-required semantic field, do not invent it silently. Identify whether it is derivable losslessly from opcode/record structure or requires a sidecar/grammar change. Any material grammar/semantic change is a scientific-contract checkpoint.

If parser + semantic matrix close without changing the consumer contract, continue immediately.

### B4 — Exact Q05 target canary

Only after B0-B3 pass, restore the frozen workload:

```text
Qwen/Qwen2.5-0.5B-Instruct
revision 7ae557604adf67be50417f59c2c2f167def9a775
S2_TEXT
PREFILL
B1 / T2048 / Decode32
FP16 / SDPA
Q05_PREFILL_ATTN_FLASH
occurrence 0
```

Re-resolve exact function/occurrence in the new process. Previous kernel ID 35 is diagnostic only.

Run a bounded Q05 canary and require:

```text
exact selector binding
real instruction trace
real terminal acknowledgement
natural writer close
natural process exit
full trace read/decompression
actual parser smoke
no drop/overflow or exact source-backed equivalent
```

If Q05 canary passes, continue directly to formal capture. Do not stop to report canary success.

### B5 — Formal producer closure

Capture the exact Q05 target and close:

```text
kernelslist(.g as consumer contract expects)
*.traceg.xz / admitted native trace members
producer manifest
address/context sidecars
terminal/completeness receipt
source/archive/build/binary/environment receipts
trace-member manifest
stable repeated SHA256/hash roots
READY through accepted 109 -> 174/node164 pipeline
```

Formal success remains:

```text
SIM_COMPAT_CAPTURE_V1_PRODUCER_PASS
TERMINAL_PROTOCOL_SM89_RECOVERED_V2
```

Then STOP node109. Consumer admission/SIM_INPUT/10k replay remain 174-new work.

## Efficiency rules

- Do not rerun already accepted official 1.7.7.1 canaries unless a Route-B change touches the official scaffold itself.
- Do not re-download NVBit artifacts already hash-closed.
- Do not rerun Qwen discovery until B0-B3 pass.
- Build/test C0/C1/C2 in one scripted matrix so every candidate patch runs the same controls automatically.
- Add ASAN/UBSAN for host-only/scaffold unit paths when feasible, but do not require sanitizer-compatible NVBit injection if it changes runtime behavior; gdb/core evidence is sufficient for GPU callback faults.
- Preserve failed Route-B candidates as DIAGNOSTIC receipts, but do not create a new review pack per candidate.
- Continue using the same V2 review pack/report.

## Required implementation boundary report

Before formal Q05, add a short `ROUTE_B_IMPLEMENTATION_BOUNDARY.md` documenting:

```text
FROM_OFFICIAL_1771_LIFECYCLE:
  exact functions/state structures retained/adapted

FROM_ACCEL_SIM_DATA_PLANE:
  exact packet/instrumentation/renderer pieces migrated

INTENTIONALLY_NOT_MIGRATED:
  old lifecycle/global/thread/teardown pieces

GRAMMAR_CHANGE:
  NONE
or exact justified change + consumer compatibility proof
```

This file is part of the formal review evidence and prevents future ambiguity about which lifecycle owns the producer.

## Stop discipline

Do not call the stage permanently blocked merely because one Route-B integration attempt fails. The official 1.7.7.1 scaffold has already proved the host/GPU can close correctly.

A final NOT_QUALIFIED is allowed only if the clean official lifecycle plus Accel-Sim data plane cannot preserve the required simulator semantics after bounded, source-backed attempts, or if the required grammar itself cannot represent the frozen consumer contract without a scientific change.
