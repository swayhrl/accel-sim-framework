# CONTINUE node109 — Solve B2 with the canonical Accel-Sim raw-trace -> traceg pipeline

## Decision

The current Route-B `blocked` state at B2 is **not accepted as a final blocker**.

B0 and B1 have already closed the hard lifecycle/channel problem:

```text
B0 official NVBit 1.7.7.1 lifecycle scaffold / zero-selected controls   PASS
B1 Route-B inst_trace_t packet path / fresh closure x3                  PASS
```

The missing piece is format production. The repository already contains the canonical Accel-Sim two-stage trace format pipeline, so Route B must reuse it instead of inventing a new direct traceg renderer.

This remains the same V2 scientific stage. Do not return to Route A and do not change the frozen Q05 workload/target.

## Core correction: there are two formats, not one

The canonical path is:

```text
Route-B NVBit receiver
  -> kernel-*.trace or kernel-*.trace.xz        # raw dynamic instruction stream
  -> existing post-traces-processing
  -> kernel-*.traceg or kernel-*.traceg.xz      # CTA/warp grouped simulator trace
  -> kernelslist.g
  -> authoritative gpu-simulator/trace-parser/trace_parser.cc
  -> AWMA strict traceg_grammar_smoke
```

Therefore **do not require Route B to directly emit final traceg structure inside the NVBit receiver**.

The standard post-processor already exists at:

```text
util/tracer_nvbit/tracer_tool/traces-processing/post-traces-processing.cpp
util/tracer_nvbit/tracer_tool/traces-processing/Makefile
```

It accepts raw `.trace` / `.trace.xz` members plus the raw kernelslist, groups instructions by CTA/warp, writes `#BEGIN_TB`, `thread block`, `warp`, `insts`, `#END_TB`, creates `*.traceg(.xz)`, and generates `kernelslist.g`.

This is standard simulator-native Accel-Sim post-processing. It is **not** C16WARP1/MREF conversion and does not cross the frozen Native/Simulation evidence boundary.

## Accepted consumer grammar authority

Consumer authority remains commit:

```text
25aa29862239a408099639ae9d5f1a0ea4fee1e1
```

The exact grammar gates are already executable:

```text
util/vm_tlb/awma/simulation/build_traceg_grammar_smoke.sh
util/vm_tlb/awma/simulation/traceg_grammar_smoke.cc
gpu-simulator/trace-parser/trace_parser.cc
util/vm_tlb/awma/simulation/test_simulation_foundation.py
```

Do not speculate about parser compatibility: build and run these exact gates on Route-B output.

The accepted consumer semantic encoding is:

```text
pc             = TRACE_RECORD
opcode         = TRACE_RECORD
access_kind    = OPCODE_CLASS
memory_space   = OPCODE_CLASS
byte_width     = TRACE_RECORD_AND_OPCODE
warp_id        = CTA_WARP_STREAM
cta_id         = CTA_STREAM
active_mask    = TRACE_RECORD
lane_addresses = TRACE_RECORD
event_order    = KERNEL_LIST_CTA_WARP_INSTRUCTION_STREAM
sync_control   = OPCODE_STREAM
```

Thus Route B does not need to invent new explicit fields for access-kind/memory-space/event-order. Preserve the canonical opcode/record/CTA-warp grammar and the consumer derives them exactly as frozen.

## B2-A — Restore only the legacy raw-line renderer

The Route-B lifecycle remains 100% official NVBit 1.7.7.1 scaffold-owned.

From the old Accel-Sim tracer, migrate only the pure formatting/data helpers necessary to turn an already-received `inst_trace_t` packet into the canonical **raw** instruction line.

For trace version 5, each raw line before post-processing must retain the legacy leading routing fields:

```text
cta_id_x cta_id_y cta_id_z warpid_tb
[optional lineinfo]
PC
active/predicate mask
destination count + destination registers
opcode
source count + source registers
memory width
[if memory: address mode + encoded addresses]
immediate
```

Preserve the legacy address encodings exactly:

```text
0 = list_all
1 = base_stride
2 = base_delta
```

Preserve the existing pure helpers/semantics for:

```text
opcode-id -> opcode string
get_datawidth_from_opcode
base_stride_compress
base_delta_compress
active_mask & predicate_mask
register formatting
immediate formatting
```

Important: the consumer strict grammar checks memory width against opcode width when encoded. Do not blindly print an unverified NVBit width if the accepted legacy renderer derives/corrects the width from the opcode.

Do **not** migrate from the old tracer:

```text
ChannelHost / ChannelDev lifecycle
receiver thread ownership
terminal state
context map lifecycle
flush launch
callback suppression
teardown
```

Those remain Route-B official-scaffold responsibilities.

## B2-B — Restore raw kernel header + raw kernelslist only

For each selected kernel, emit the canonical legacy headers required by post-processing/parser:

```text
-kernel name = ...
-kernel id = ...
-grid dim = (x,y,z)
-block dim = (x,y,z)
-shmem = ...
-nregs = ...
-binary version = ...
-cuda stream id = ...
-shmem base_addr = ...
-local mem base_addr = ...
-nvbit version = ...
-accelsim tracer version = 5
-enable lineinfo = 0|1

#traces format = ...
```

The raw kernelslist should reference the raw `kernel-*.trace.xz` members in the form expected by `post-traces-processing`.

Writer ownership must stay Route-B per-context/per-kernel. Close/pclose the raw writer only **after the B1 device/channel-derived terminal acknowledgement**. The renderer itself owns no lifecycle state.

## B2-C — Use the existing post-processor unchanged first

Build the accepted repository post-processor:

```bash
cd util/tracer_nvbit/tracer_tool/traces-processing
make clean
make
sha256sum post-traces-processing post-traces-processing.cpp
```

Do not modify it initially.

Run it on the selected tiny Route-B raw kernelslist/directory. Expected result:

```text
kernel-*.trace.xz
  -> kernel-*.traceg.xz

raw kernelslist
  -> kernelslist.g
```

The post-processor is responsible for removing the raw leading CTA/warp routing fields from instruction records and reorganizing them into:

```text
#BEGIN_TB
thread block = x,y,z
warp = w
insts = N
<trace-version-5 instruction records without legacy CTA/warp prefix>
#END_TB
```

Do not reimplement this grouping in the NVBit callback/receiver.

## B2-D — Compile and run the exact accepted consumer parser gate

Build the AWMA grammar smoke exactly from the accepted consumer code:

```bash
util/vm_tlb/awma/simulation/build_traceg_grammar_smoke.sh
```

Then run the resulting `traceg_grammar_smoke` on every generated `kernel-*.traceg.xz`.

The strict gate requires, among other things:

```text
required kernel headers
nonzero grid/block dimensions
exact #BEGIN_TB/#END_TB structure
thread-block count == grid_x * grid_y * grid_z
warp records + exact declared instruction counts
nonempty instruction stream
PC + active mask
register counts and R<n> syntax
opcode
memory width semantics
address mode 0/1/2
active-mask-consistent address arity
one immediate field
no trailing tokens
```

It then passes the same file through the repository's authoritative `trace_parser.cc` and requires instruction-count agreement.

Use the accepted `VALID_TRACE` in `test_simulation_foundation.py` as a minimal golden grammar fixture, not as producer data.

## B2-E — Differential/golden regression

Before Q05, add a small CPU-only or tiny-GPU regression proving that the new Route-B raw renderer is format-equivalent to the legacy renderer for the same synthetic/known packet cases.

Cover at least:

```text
non-memory instruction
READ global memory instruction
WRITE global memory instruction
list_all address encoding
base_stride address encoding
base_delta address encoding
partial active mask
register src/dst
immediate/control opcode
```

Preferred check:

```text
same logical inst_trace_t input
-> legacy pure formatter result
vs
-> Route-B pure formatter result
== byte-identical raw instruction text
```

Normalize only documented nondeterministic kernel-header values; do not normalize instruction fields.

Then pass the Route-B raw output through the unchanged canonical post-processor and exact AWMA parser smoke.

## B3 — Consumer semantic contract, no invention

After B2 parser PASS, populate the frozen manifest semantic mapping **exactly** from `simulation_foundation.py` rather than defining a new mapping.

For the formal Q05 bundle, `required_control_opcodes` must be a nonempty list of control/synchronization opcodes actually present in the selected target trace/static authority. Derive it from actual Q05 opcode evidence; do not insert a control opcode that is absent merely to satisfy the contract.

The strict grammar derives:

```text
READ / WRITE / ATOMIC from opcode class
memory space from opcode class
byte width from trace record + opcode
CTA/warp identity from grouped stream
sync/control from opcode stream
event order from kernelslist -> CTA -> warp -> instruction order
```

If actual Q05 emits an opcode whose access/space semantics are not recognized by the accepted consumer gate, stop only at that exact opcode/semantic mismatch and fix/extend the contract with evidence. Do not call a missing direct renderer a blocker.

## B2/B3 acceptance gate

B2/B3 PASS requires:

```text
Route-B selected tiny closes through real B1 terminal protocol
raw .trace.xz readable
canonical post-processor exits 0
.traceg.xz generated
kernelslist.g generated
xz -t PASS
AWMA strict traceg_grammar_smoke PASS
authoritative trace_parser.cc PASS
instruction counts agree
negative malformed/missing-terminal/member tests remain fail-closed
semantic mapping matches frozen consumer contract
```

Repeat the tiny pipeline from a fresh process at least twice after the final renderer integration.

## Then continue immediately — do not report an intermediate B2 success

Once B2/B3 pass, execute in the same Goal:

```text
B4 exact Q05 canary
-> exact workload/function/occurrence re-resolution
-> raw simulator-native capture
-> canonical post-processing
-> parser/semantic checks
-> real terminal closure

if PASS:
B5 formal Q05 capture
-> COMPLETE + zero drop/overflow or exact source-backed equivalent
-> kernelslist/member/sidecar/source/build/binary hashes
-> READY through accepted 109 -> 174/node164 pipeline
-> V2 review pack/report
-> commit + push + clean status
```

Frozen Q05 identity is unchanged:

```text
Qwen/Qwen2.5-0.5B-Instruct
revision 7ae557604adf67be50417f59c2c2f167def9a775
S2_TEXT / PREFILL
B1 / T2048 / Decode32
FP16 / SDPA
Q05_PREFILL_ATTN_FLASH
occurrence 0
```

The historical diagnostic numeric kernel ID 35 is not the authority; re-resolve semantic/function/occurrence binding.

## Final success

```text
SIM_COMPAT_CAPTURE_V1_PRODUCER_PASS
TERMINAL_PROTOCOL_SM89_RECOVERED_V2
```

Then STOP node109.

Do not generate `SIM_INPUT_ID`, run the 10k replay, or perform mechanism experiments on 109.

## Stop discipline

`MISSING_ROUTE_B_TRACEG_RENDERER` is no longer an allowed final blocker because the accepted repository already contains the canonical raw-trace -> traceg formatter and exact parser gate.

A new non-PASS stop is allowed only for a newly demonstrated exact incompatibility such as:

```text
Route-B packet lacks information required to reproduce the canonical raw instruction record
canonical post-processor rejects a correctly formed Route-B raw trace for a specific source-backed reason
accepted strict parser exposes an exact unsupported Q05 opcode/semantic contract
scientific identity/semantics would have to change
```

For ordinary formatter/build/path/post-processing issues: solve -> regress -> continue.
