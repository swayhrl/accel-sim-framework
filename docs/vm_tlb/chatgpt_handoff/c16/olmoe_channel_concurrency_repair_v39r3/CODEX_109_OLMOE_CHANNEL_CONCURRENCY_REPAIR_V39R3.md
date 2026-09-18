# C16 OLMoE NVBit 1.7.7.1 Channel concurrency repair + formal closure — node109 V39R3

## Goal mode

Execute in **GOAL MODE** on node109.

This is an engineering continuation of V39/V39R2, not a new scientific target.

Suggested implementation branch:

`hrl/c16-olmoe-channel-concurrency-repair-109-v39r3`

Base:
`hrl/c16-olmoe-nvbit1771-formal-capture-109-v39r2@e300be3cbf21c12f9f7908d9058c1dc2fd6970ce`

## Accepted facts

Do not reopen:
- OLMoE model/input authority
- natural expert58 target
- variant-A policy
- actual-A 1096 static instructions
- complete 243 selected address-bearing instructions
- V38 static/selector SHA identities
- C16WARP1 wire semantics
- G1/G2/G4 producer/receiver fixture closure
- V39R2 C0/C1/G0/G3 regressions

Current blocker:
- actual-A selected static 101 hangs under the custom C16WARP1 Channel-enabled instrumented image
- bounded no-op/V20-ABI/CTA-prefilter repairs did not close it
- failed attempts were not formalized
- official non-Channel opcode_hist executes
- historical V36 `mem_trace_2` using official NVBit 1.7.7.1 mem_trace obtained actual-A same-process dynamic evidence

## First action — persist the current blocker evidence

Before modifying the implementation, reproduce or recover the current bounded differential evidence and commit a small diagnostic receipt containing:
- exact tool/source SHA
- actual function fingerprint
- static 101 identity
- exact command/env
- timeout/termination behavior
- whether helper entered
- whether Channel push occurred
- GPU/process cleanup result

Do not admit any hung/partial output as scientific data.

## Primary root-cause hypothesis

The current producer contains a device-side global ticket serialization:

`sequence = atomicAdd(producer_records,1)`

followed by:

`while (producer_next_to_push != sequence) { spin }`

before `ChannelDev::push`.

This is **not required by the C16 scientific contract** and is unsafe as a global GPU progress mechanism. Later-ticket warps can occupy execution resources while waiting for an earlier-ticket warp that has not been scheduled, producing a scheduler-dependent deadlock/livelock.

Treat this as the first engineering hypothesis to test.

## Scientific ordering boundary

C16WARP1 event order is not a claim of:
- hardware-global memory arrival order
- warp-global chronology
- reuse-distance chronology

Therefore V39R3 is authorized to remove device-side sequence-order serialization.

Sequence numbers may be used **only for integrity/accounting**.

Do not introduce any analysis that interprets sequence order as a hardware timing order.

## Repair A — remove device-side ticket spin

Modify the 1.7.7.1 producer so that:

1. every logical WRec obtains a unique monotonic sequence via atomicAdd
2. capacity/overflow behavior remains fail-closed
3. packet is pushed directly through the official Channel mechanism
4. no warp waits for `producer_next_to_push`
5. remove `producer_next_to_push` from the formal progress condition

Follow the official mem_trace Channel push pattern as closely as possible.

Do not add a GPU global lock/spinlock to replace the ticket spin.

## Repair B — receiver accounting becomes order-independent

Because concurrent Channel pushes need not arrive in sequence-number order, do not use stream-order sequence-gap logic.

Receiver must retain every accepted sequence ID and, at closure, independently validate:

- received packet count == producer logical count
- every sequence is in range `[0, producer_count)`
- no duplicate sequence
- exact received sequence set == `{0,1,...,producer_count-1}`
- malformed packet count == 0
- overflow == 0
- receiver terminal exactly once
- finalized C16WARP1 records == receiver accepted count

Implementation may use:
- vector of sequence IDs + sort, or
- bitmap/set

for bounded formal shard sizes.

Do not infer missing records from arrival order.

Accounting status:
`NO_UNACCOUNTED_RECORDS_PROVEN`

remains valid only after exact set closure.

## Final binary ordering

The final C16WARP1 parser does not define scientific chronology from record order.

Either:
- serialize records in receiver arrival order, or
- sort by transport sequence for deterministic packaging

is acceptable **only if explicitly labeled as transport/serialization order, not hardware chronology**.

Prefer receiver arrival order unless deterministic packaging provides a concrete engineering benefit.

## Differential matrix before OLMoE canary

Use actual-A static 101 and the exact isolated expert58 replay.

Run bounded variants in fresh processes:

### D0 — official opcode_hist control
No Channel. Must execute.

### D1 — official mem_trace control
Use official NVBit 1.7.7.1 mem_trace on the exact actual-A replay with bounded output.
This is expected to execute based on V36 history; reproduce if inexpensive.

### D2 — custom instrumented helper, no Channel push
Use the custom injected helper path but do not push a Channel packet.
Do only the minimum safe per-warp computation/counter needed to prove the injected image executes.

### D3 — custom Channel push, no ticket spin
Push a minimal fixed packet through the official Channel path without source-register gathering complexity.

### D4 — full WRec path, no ticket spin
Use the actual C16WARP1 packet with source-address gathering and order-independent accounting.

Interpretation:
- D2 fails while D0/D1 pass -> injected helper/tool-patch or helper ABI/image issue
- D2 passes, D3 fails -> Channel integration/packet push issue
- D3 passes, D4 fails -> WRec/helper address-gather path issue
- D4 passes -> proceed directly to scientific canary

Routine failures in D2-D4 are engineering problems: repair and continue.

Do not stop after identifying a layer unless repair requires scientific-contract change.

## If D2 itself hangs

Use the official 1.7.7.1 opcode_hist/mem_trace injection structure as the implementation base and transplant only the minimal C16 WRec semantics into that proven helper/tool-patch path.

Do not keep an independently structured custom device callback if the official helper structure is required for actual-JIT cuBLAS compatibility.

Preserve:
- same C16WARP1 scientific record
- same address-source semantics
- same accounting/terminal contract

## If official mem_trace D1 hangs now

Compare exact runtime/tool identity to V36 `mem_trace_2`.

Do not assume V36 was wrong. Check:
- NVBit root/version/hash
- CUDA/driver/runtime
- replay source/state
- variant-A fingerprint
- environment variables
- tool build flags

Fail closed only if the previously observed official dynamic path cannot be reproduced after bounded identity repair.

## Re-run engineering fixtures after transport repair

After any producer/receiver transport change rerun:
- G1 nonzero
- G2 true-zero
- G4 accounting negative
- current parser unchanged

All must remain PASS.

## Then scientific canary

Once D4 + G1/G2/G4 pass:

Use the already-closed 243 selector.

Choose canaries covering:
- expert input read
- expert weight read
- expert output write
- GLOBAL_TO_SHARED/LDGSTS if present

Every canary requires:
- variant-A fingerprint
- exact static row/source register
- valid C16WARP1
- exact terminal
- producer/receiver/set accounting closure
- overflow 0
- unchanged parser PASS
- expected same-process object hits

## Formal capture

After canary PASS, continue automatically through the existing V39R2 contract:

- complete 243 independently replayed static shards
- clean executed/zero partition
- no failed attempt admitted
- per-shard descriptive analysis
- serial transfer/admission/positive ACK
- third-lineage handoff
- review pack
- Git closure
- cleanup
- STOP

`FORMAL_ADMISSION_CONCURRENCY=1`

## Do not re-run unnecessary science

Do not:
- chase variant B
- change cuBLAS algorithm/backend/workspace policy
- change OLMoE target
- change source/input
- use old NVBit 1.7.5 tracer
- interpret transport sequence as hardware chronology

## Required review evidence

Add/finalize:
- `ACTUAL_A_CHANNEL_HANG_BASELINE.json`
- `CHANNEL_CONCURRENCY_ROOT_CAUSE.json`
- `ACTUAL_A_INSTRUMENTATION_DIFFERENTIAL.tsv`
- `ORDER_INDEPENDENT_ACCOUNTING_CONTRACT.md`
- `TRANSPORT_REPAIR_BUILD_RECEIPT.json`
- refreshed G1/G2/G4
- scientific canary/formal files required by V39R2

Preferred engineering classification if ticket-spin removal fixes actual-A:
`PASS_DEVICE_TICKET_SERIALIZATION_REMOVED_ACTUAL_A_CHANNEL_PROGRESS_RESTORED`

Preferred final scientific decision remains:
`C16_OLMOE_NVBIT1771_FORMAL_TRACER_109_V39_PASS_WITH_FORMAL_VARIANT_A_ANCHOR`

## Stop boundary

Stop only if:
- official 1.7.7.1 dynamic instrumentation that previously worked on actual-A cannot be reproduced under closed identity
- actual-A can execute only by changing scientific WRec/address semantics
- same-process object attribution fails
- complete formal evidence cannot close after bounded engineering repair

A custom helper deadlock, Channel push bug, packet accounting bug, helper ABI bug, or tool-patch bug is engineering work: solve and continue.
