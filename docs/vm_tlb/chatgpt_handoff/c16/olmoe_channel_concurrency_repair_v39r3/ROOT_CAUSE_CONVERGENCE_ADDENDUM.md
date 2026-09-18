# V39R3 root-cause convergence addendum — actual-A instrumentation

## Purpose

Do not treat the current actual-A hang as a generic "formal capture blocker".

The evidence already separates the problem from model/input/static identity:

- exact OLMoE expert58 replay closes
- actual JIT variant-A identity closes
- 1096 static instructions close
- complete 243 address-bearing selector closes
- official NVBit 1.7.7.1 static introspection works
- historical V36 official-style mem_trace obtained actual-A same-process dynamic evidence
- vectoradd G1/G2 prove the new C16WARP1 transport works on an ordinary kernel

Therefore the unresolved layer is:

`actual-A instrumented-image construction / injected-helper / Channel transport interaction`

The goal of this addendum is to converge on a working implementation by changing **one dimension at a time**, then immediately resume canary/formal capture.

## External supporting fact

NVBit's own recent changes/issues make this class of failure plausible:
- mem_trace/Channel lifecycle has had deadlock/hang fixes
- patch-function argument passing has had fixes
- NVBit issue #160 reports injected-function argument-count sensitivity
- Channel push has historically caused hangs in some instrumented workloads

These are engineering clues only; do not use them as scientific evidence.

## Critical policy

Do not preserve the current custom helper architecture for its own sake.

The formal scientific contract requires:
- exact selected static identity
- exact lane addresses
- active mask / CTA / warp identity
- independent producer/receiver accounting
- C16WARP1 serialization
- terminal closure

It does **not** require:
- the current helper function signature
- current custom launch gating
- device-side sequence ordering
- current packet layout
- current custom instrumentation subset construction

Prefer the smallest implementation built directly from the official 1.7.7.1 mem_trace path that is proven to execute actual-A.

---

# Stage A — freeze current failure before repair

Commit a diagnostic receipt for the current hang if not already pushed.

Record:
- tool source SHA/binary SHA
- exact actual-A fingerprint
- static 101 row
- exact replay/output hash before instrumentation
- exact env/argv
- timeout point
- whether function launch callback was seen
- whether injected helper entry was observed
- whether any Channel packet was received
- whether terminal occurred
- cleanup result

No partial output is formal.

---

# Stage B — reproduce the historical positive control

Run the exact isolated expert58 replay with the **official NVBit 1.7.7.1 mem_trace tool as shipped**, with only bounded output controls needed to avoid huge files.

Call this `P0_OFFICIAL_MEM_TRACE`.

Require:
- actual-A function observed
- process exits normally
- at least one dynamic memory event from actual-A
- no hang

If P0 fails:
1. compare exact NVBit root/version/build/runtime to V36
2. repair identity differences
3. retry

Do not proceed to custom code until P0 closes.

If P0 cannot be reproduced under the same closed runtime after bounded repair, stop: that would contradict the accepted V36 dynamic-path premise and is a real environment/tool regression.

---

# Stage C — binary-search the instrumentation delta from official mem_trace

Starting from a **copy of the working official mem_trace source**, create the following variants. Do not start from the current custom V39 tool.

Each step changes only one concept.

## P1 — function filter only

Keep official mem_trace's:
- tool module
- Channel lifecycle
- injected helper
- packet type
- instrumentation API usage

Add only the exact actual-A function-name/fingerprint filter.

Instrument all memory instructions in the target function exactly as official mem_trace would.

Require normal execution.

If P1 hangs while P0 passes:
- function filtering / function-enable / launch-selection plumbing is the culprit.
- avoid `nvbit_set_at_launch`/occurrence machinery if the isolated replay has a single relevant launch.
- use the isolated one-module replay and instrument the matching function directly.

## P2 — static identity field only

Starting from P1, add only a static instruction identifier (idx or PC offset) to the official packet/helper.

Do not yet change address-source semantics.

Require normal execution and recoverable per-static records.

If P2 hangs:
- reduce injected argument count and trampoline pressure.
- pass a single pointer to a device-resident immutable config/metadata struct instead of multiple capacity/CTA/channel arguments.
- keep helper argument count minimal.

## P3 — record only requested static, but preserve official full-image instrumentation

Do **not** change which memory instructions receive injected calls.

Keep the same instrumented image as P2, but add a runtime/device filter so only records for the requested static are pushed/accepted.

This is intentional:
- official full-function instrumentation is already the proven code-generation path
- one formal replay still records exactly one selected static
- extra injected calls that immediately return are instrumentation overhead, not scientific events

Require static101 to execute and terminate.

If P3 passes, use this pattern for formal shards instead of generating a different instrumented image for each static subset.

## P4 — C16 scientific payload

Starting from P3, replace/extend only the packet payload to carry:
- static_index
- active_mask
- cta_x/y/z
- warp
- addr[32]

Keep Channel/lifecycle/helper structure otherwise official.

No sequence-order spin.

Use order-independent receiver accounting.

Require normal execution.

## P5 — C16WARP1 serializer/accounting

Add:
- producer logical count
- receiver accepted count
- unique sequence IDs
- exact sequence-set closure
- overflow
- terminal
- unchanged C16WARP1 final serializer

Rerun G1/G2/G4.

Only after P5 passes move to OLMoE canary.

---

# Stage D — address-source decision for actual-A loads

Do not assume the V20 register-pair path is necessary for OLMoE actual-A simply because it was necessary/used for older kernels.

The V36 official-style mem_trace already produced meaningful actual-A addresses.

For representative actual-A load rows, compare in the **same process/instruction execution**:

1. official NVBit MREF address argument
2. source-register-pair reconstructed address

Require exact active-lane address equality, or an explicitly understood and typed difference.

### If MREF == register-pair

Use the official MREF address API for OLMoE formal capture.

This is preferred because it keeps the injected helper closest to the proven official mem_trace implementation.

Persist the equivalence receipt.

### If MREF differs

Keep the register-pair source, but minimize helper arguments:
- pred
- lo
- hi
- static id
- one device config/state pointer

Move Channel pointer/capacity/CTA range/counters into device state referenced by that pointer where technically valid.

Do not use a large argument list unless required.

Any address-source change must be validated against same-process semantic object ranges before formalization.

---

# Stage E — explicit no-op differential if needed

If P0/P1 execute but a later custom step hangs, use a true differential matrix:

- `N0`: injected call at static101, no arguments, **no Channel initialization at all**
- `N1`: same no-arg injected call, official Channel lifecycle initialized but no push
- `N2`: minimal official Channel fixed packet push
- `N3`: active-mask/address gather without Channel push
- `N4`: full payload + Channel push

This distinction is mandatory.

"no-op while the custom Channel-enabled tool is loaded" is **not** sufficient to conclude that the injected call itself is the problem.

Interpretation:
- N0 hangs -> injected-image/call-site/tool-patch problem
- N0 passes, N1 hangs -> Channel lifecycle interaction
- N1 passes, N2 hangs -> Channel push interaction
- N2 passes, N3 hangs -> warp/address helper logic
- N3 passes, N4 hangs -> packet/payload transport

Repair the exact failing layer and continue.

---

# Stage F — remove unsafe device progress dependencies

The V39 device ticket-spin serialization is forbidden for V39R3 formal use.

Do not replace it with another global GPU spinlock.

Device-side producer may assign a unique sequence with atomicAdd, but must not wait for sequence order.

Receiver validates exact set membership at closure:

`received_sequences == {0,1,...,producer_count-1}`

and:
- no duplicates
- no malformed packet
- producer==receiver==serialized
- overflow=0
- terminal exactly once

Arrival order is transport order only.

---

# Stage G — scientific canary and formal capture

As soon as one implementation path P5 is proven on actual-A:

1. rerun actual-A typed canaries:
   - input read
   - weight read
   - output write
   - GLOBAL_TO_SHARED if present
2. unchanged parser must accept each canary
3. same-process semantic object hits must close
4. replay output must remain bitwise equal

Then continue automatically:
- 243 independently replayed formal shards
- variant-A guard
- complete executed/zero partition
- failed attempts excluded
- formal analysis
- serial transfer/admission/positive ACK
- third-lineage handoff
- Git closure
- cleanup
- STOP

`FORMAL_ADMISSION_CONCURRENCY=1`

---

# Strong preference

The preferred final implementation is:

`official NVBit 1.7.7.1 mem_trace lifecycle + official instrumentation pattern + minimal C16 payload/serializer extensions`

rather than:

`custom V20-style tracer architecture ported forward`

because the official path is already known to execute actual-A.

---

# Stop boundary

Do not stop for:
- needing to rewrite the helper
- needing to abandon the current custom packet
- needing to remove per-static image specialization
- needing to reduce helper arguments
- needing to use official MREF addresses after proving equivalence
- needing to implement order-independent sequence accounting

Stop only if:
- official P0 actual-A dynamic instrumentation cannot be reproduced under closed identity
- no official-derived instrumentation can preserve exact selected-static + lane-address semantics
- MREF and register-pair addresses disagree in a way that cannot be scientifically resolved
- replay output changes
- formal evidence integrity cannot be closed after bounded repairs
