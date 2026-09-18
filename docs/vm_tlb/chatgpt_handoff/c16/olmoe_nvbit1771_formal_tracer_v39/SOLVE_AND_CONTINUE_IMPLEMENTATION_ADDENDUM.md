# V39 solve-and-continue producer/receiver implementation contract

## Status

The current V39 blocker is reclassified as an **engineering implementation task**, not a scientific/evidence-authority blocker.

The absence of an already-written NVBit 1.7.7.1 C16WARP1 producer/receiver implementation does not justify stopping. V39 is explicitly authorized to implement that producer/receiver from the already-closed authorities below, validate it against independent consumers/golden artifacts, and continue through formal capture.

Do not fabricate unsupported fields. Do not relax existing consumers. Do not change the scientific target.

## Closed authorities

### A. Lifecycle authority
Use the exact official NVBit 1.7.7.1 `mem_trace` context-owned/channel/receiver lifecycle already proven by V39 C0/C1.

This authority defines:
- context-owned state
- device/host channel initialization
- receiver thread lifecycle
- instrumentation enablement
- channel flush/termination mechanism
- receiver join
- context teardown ordering

### B. C16WARP1 semantic/wire authority
Use the exact historical V20 sources at:

`hrl/c16-qwen3-s3-kv-scaling-109-v20@c94825dab9b114e468a83cdad009181f23add608`

Files:
- `util/vm_tlb/c16/campaign/v20_warp_common.h`
- `util/vm_tlb/c16/campaign/v20_warp_inject.cu`
- `util/vm_tlb/c16/campaign/v20_warp_tool.cu`

These define:
- WRec scientific fields
- active-mask semantics
- CTA/warp semantics
- source-register address semantics
- selected static/occurrence semantics
- C16WARP1 binary header/record layout
- capacity/overflow semantics
- terminal text semantics

### C. Independent consumer authority
Use without relaxation:
- `util/vm_tlb/c16/analysis/c16_warp_container.py`
- `util/vm_tlb/c16/q30_v3_audit_static_shards.py`

These define the formal acceptance conditions.

## Engineering objective

Implement a new producer/receiver:

`warp_regsource_1771_c16warp1`

that uses:

`NVBit 1.7.7.1 lifecycle/channel/receiver`

internally, but emits finalized shard artifacts that are accepted unchanged by the existing C16WARP1 consumer.

This is a new implementation of an existing audited contract, not a new scientific schema.

## Internal transport packet

The internal NVBit Channel packet is an implementation detail and does not need to equal the final C16WARP1 record layout byte-for-byte.

Recommended design:

- one DATA packet corresponds to one historical WRec
- include a monotonic producer sequence number in the internal packet
- include the complete WRec scientific payload:
  - static_index
  - active_mask
  - cta_x/y/z
  - warp
  - addr[32]
- include packet type/version only if required for the receiver lifecycle
- use the exact official 1.7.7.1 channel push/receive APIs from the working mem_trace scaffold; do not invent unsupported API calls

A monotonic sequence number is strongly preferred because it makes receiver loss detectable independently of the final binary contract.

## Device producer semantics

Port the scientific behavior from V20:

1. evaluate the selected instruction guard predicate
2. form the active warp mask
3. apply CTA filter if configured
4. derive the exact lane address from:
   - source register pair for register-addressed loads when required, or
   - MREF address API for paths where that is the audited address source
5. gather 32 lane addresses under the active mask
6. emit exactly one logical WRec per active warp execution
7. increment an independent producer-emitted counter exactly once per logical WRec
8. if configured formal capacity is exceeded:
   - increment overflow
   - do not silently overwrite
   - formal shard must later fail/recapture

The producer counter must count logical records before receiver transport accounting.

Do not count inactive lanes as records.

## Receiver semantics

Use the already-working official 1.7.7.1 receiver thread and channel lifecycle.

For each DATA packet:
- verify packet version/type if applicable
- verify sequence number continuity
- append/write exactly one WRec scientific record
- increment receiver-accepted counter

Do not silently discard malformed/out-of-order packets.

Any transport inconsistency must make the shard non-formal.

At lifecycle termination:
- use the exact proven official channel flush/terminal mechanism
- wait for receiver terminal
- join receiver cleanly
- finalize only after no more packets can arrive

## Accounting closure

For each shard persist a sidecar accounting receipt with at least:

- producer_logical_records
- producer_overflow
- receiver_packets_accepted
- receiver_first_sequence
- receiver_last_sequence
- receiver_sequence_gap_count
- receiver_duplicate_sequence_count
- receiver_terminal_seen
- receiver_terminal_count
- finalized_c16warp1_records_written

Formal closure requires:

`producer_logical_records == receiver_packets_accepted == finalized_c16warp1_records_written`

and:

`producer_overflow == 0`

`receiver_sequence_gap_count == 0`

`receiver_duplicate_sequence_count == 0`

`receiver_terminal_seen == true`

`receiver_terminal_count == 1`

If official NVBit exposes an independent channel-drop counter, record and require it to be zero.

If it does not, do not invent one. Use producer/receiver/sequence equality as:

`NO_UNACCOUNTED_RECORDS_PROVEN`

Any legacy receipt field called `drop=0` must be explicitly derived from this closure, not represented as a raw wire field.

## Final C16WARP1 serialization

After receiver closure, serialize exactly:

Header:
`<8sIIQQQ`

- magic = `C16WARP1`
- selected static index
- selected function occurrence
- callback_records = producer_logical_records
- overflow = producer_overflow
- records_written = receiver_packets_accepted

Then write all WRec records in receiver order as:

`<6I32Q`

The accepted parser must accept this file unchanged.

Also print exactly one terminal line:

`C16_WARP_TERMINAL static=<static> occurrence=<occ> records=<records_written> overflow=<overflow>`

Do not add extra lines that match the same terminal regex.

## True zero-execution semantics

A zero-event formal shard is valid only when all of the following are true:

- target actual-JIT variant-A fingerprint guard passed
- selected function identity passed
- selected occurrence identity passed
- selected static instruction exists in the complete selector
- tracer lifecycle completed
- receiver terminal completed exactly once
- producer_logical_records = 0
- receiver_packets_accepted = 0
- producer_overflow = 0
- valid C16WARP1 binary exists with zero records
- exact terminal line exists
- existing consumer parser accepts it unchanged

Missing file / missing terminal / receiver not closed is never zero execution.

## Required implementation tests

Continue from existing V39 G0/G3.

### G1 new 1.7.7.1 nonzero fixture
Use the new producer/receiver on a bounded known-executed selected memory instruction.

Require:
- producer count > 0
- receiver count == producer count
- contiguous sequences
- terminal exactly once
- overflow 0
- valid C16WARP1 file
- existing parser accepts without code modification

### G2 new 1.7.7.1 zero fixture
Use a bounded control that preserves valid selected function/static identity but guarantees no accepted WRec after the scientific filter.

A clean non-overlapping CTA filter is acceptable for this **engineering fixture only** if it preserves valid instrumentation and selected launch identity.

Require:
- valid binary exists
- producer=receiver=records_written=0
- terminal exactly once
- overflow 0
- parser accepts as ZERO_EXECUTION_PROVEN

Do not use this artificial zero fixture as scientific evidence.

### G4 accounting fault injection
In addition to existing parser-negative G3, add at least one producer/receiver accounting negative test:
- synthetic sequence gap, or
- synthetic receiver count mismatch

Require V39 accounting validator to reject it.

## Independent validation rule

Do not validate the new implementation only with code that shares its serializer logic.

At least two independent checks are required:

1. existing C16WARP1 consumer parser unchanged
2. separate V39 accounting validator that compares producer/receiver counters and sequence closure

Historical accepted artifact regression remains G0.

## After G1/G2/G4 PASS

The previous V39 block is cleared.

Continue automatically with the existing scientific pipeline:

1. re-enumerate actual variant-A 1096 instructions
2. regenerate full 243-row selector
3. close:
   - all-static SHA `089d264460999f54f9279ccced4b4bab72483d0572e1d08d6797338ef76a9aa3`
   - selector SHA `9d2d414999e417200167664dc0b4c716f1dcfb72aaf505d89736e14dbedbcb33`
4. formal-protocol A probes
5. typed OLMoE canaries
6. complete 243-shard formal capture
7. clean executed/zero partition using the new terminal/accounting closure
8. formal analysis
9. serial transfer/admission/positive ACK
10. third-lineage handoff
11. review pack/hash/Git closure

Do not stop after merely implementing G1/G2.

## Stop boundary

Valid reasons to stop for review:
- implementing the channel producer/receiver would require changing scientific WRec fields/count semantics
- existing unchanged C16WARP1 parser cannot be satisfied without semantic relaxation
- actual variant-A identity materially changes
- source-register/address semantics cannot be closed
- formal integrity cannot be established after bounded engineering repairs

Not valid reasons to stop:
- "there is no existing 1.7.7.1 C16WARP1 implementation"
- receiver code needs to be written
- packet structure needs to be defined from the closed WRec contract
- a build/channel/callback/flush bug occurs
- output serializer needs implementation
- accounting validator needs implementation

Those are the engineering work of this Goal.

## Review-pack additions

Add:
- `C16WARP1_1771_IMPLEMENTATION_RECEIPT.json`
- `C16WARP1_INTERNAL_PACKET_CONTRACT.md`
- `C16WARP1_ACCOUNTING_CONTRACT.md`
- `G1_NONZERO_FIXTURE.json`
- `G2_ZERO_FIXTURE.json`
- `G4_ACCOUNTING_NEGATIVE.json`

Bind source SHA256 for all new producer/receiver/inject/serializer/accounting-validator files.
