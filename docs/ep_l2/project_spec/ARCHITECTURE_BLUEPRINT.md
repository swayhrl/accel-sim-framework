# EP-L2 Architecture Blueprint

## Scope

This document records long-lived architectural intent and the current calibrated model boundary. Exact experiment provenance belongs in review packs; transient execution status belongs in the workboard/handoffs.

## Working architecture name

**Elastic Payload L2 (EP-L2)**

Core idea:

> Decouple resident tag state, requester/waiter metadata, transaction/pending state, and physical 128-B payload ownership so that one statically provisioned resource does not unnecessarily terminate useful L2 concurrency while other resources remain available.

## Frozen target geometry / baseline model

Current target model:

```text
L2 slices                     64
memory channels               32
subpartitions/channel         2
cache line                    128 B
sectors/line                  4 x 32 B
resident tags/slice           64 sets x 16 ways = 1024 tags
resident payload quota        1024 lines = 128 KiB/slice
bypass payload quota          128 lines = 16 KiB/slice
potential unified payload     1152 lines = 144 KiB/slice = 9 MiB/chip
physical payload banks        4 x 288 entries
bank mapping                  payload_id % 4
bank service model            one arbitrary 128-B operation/bank/cycle
Line MSHR                     128 entries/slice in the calibrated base
per-address merge cap         32
WAD                           128 line addresses/slice
L2->DRAM queue                128/slice
DRAM scheduler                FR-FCFS, 128/channel
DRAM internal ReturnQ         192/channel
DRAM->L2                      64/slice
primary DRAM clock            850 MHz
```

L1 is not part of the EP-L2 storage budget and is held fixed for the primary target baseline unless a sensitivity experiment explicitly says otherwise:

```text
L1D capacity                  64 KiB/core
sets x ways x line            4 x 128 x 128 B
banks                         4
latency                       20 cycles
L1 MSHR                       512
L1 merge cap                  8
L1 MissQ                      16
```

## Baseline payload organizations

### B0-Legacy

- 1024 resident payload slots and 128 bypass payload slots are separate logical/physical roles.
- Existing service behavior remains legacy/static.

### B0-Banked

- Same total physical organization: 4 x 288 payload entries.
- Roles remain statically partitioned as resident 1024 + bypass 128.
- No capacity borrowing.
- Idle bank grants same cycle.
- Oldest-ready pending request priority.
- One arbitrary operation per bank per cycle.
- True bank contention is measured separately from artificial staging.

B0-Legacy/B0-Banked are calibration/control organizations, not the final EP-L2 mechanism.

## Metadata / lifetime principles

### Resident tag

A resident tag identifies cache-line residency/state. Tag allocation and payload ownership need not always have identical lifetimes in later EP-L2 mechanisms.

### Request descriptor

Persistent requester/waiter metadata remains live until the corresponding requester response is successfully enqueued toward the interconnect. It is distinct from the Line-MSHR resource.

The project calibrated descriptor capacity separately because a cheap global metadata ceiling can otherwise hide pressure in later resources.

### Line MSHR

The Line MSHR is keyed by 128-B line address with sector masks. The baseline remains 128 entries unless a causal sensitivity explicitly changes it. MSHR capacity is not to be enlarged merely to create or remove a desired story.

### Payload identity

Physical payload state uses explicit `payload_id + generation` style ownership/lifecycle tracking so stale fills/reuses can be rejected correctly.

### WAD

The Writeback Address Directory allocates before destructive dirty-victim mutation and is released only at the true no-return writeback completion point (`memory_partition_unit::set_done()` in the simulator model).

## Current calibration conclusions that constrain future design

These are design constraints, not final opportunity-mechanism claims:

- Descriptor=256 is a real structural pressure point in several workloads, but increasing it to 512 generally removes descriptor-full blocking without material speedup.
- Descriptor relief naturally exposes higher Line-MSHR pressure; in convolution, exact Line-MSHR-full blocking appears at D512/M128.
- Raising convolution Line-MSHR 128->256 removes that exact full-blocking but yields only sub-1% speedup, indicating downstream-limited bottleneck substitution.
- Large native L1 retry/queue event counts do not by themselves imply a strong L1 performance bottleneck; broad L1 META/BANK headroom has shown low performance sensitivity so far.
- ReturnQ/DRAM->L2 return blocking has not been a broad primary bottleneck in the current target set.

## Future mechanism families — not yet frozen implementation

### 1. Unified payload borrowing

Allow resident and bypass/pending uses to draw from a shared physical payload pool rather than fixed 1024/128 quotas while preserving ownership/generation correctness and bank service limits.

### 2. Replaceable read-only pending tag / no-traditional-MSHR path

For certified read-only cases, investigate whether pending transaction/tag state can remain replaceable/flexible without consuming the traditional Line-MSHR resource for its entire lifetime. This must not be motivated solely by MSHR-full counts; the mechanism also needs a lifetime/flexibility/opportunity argument.

### 3. WAD-backed TVD / payload decoupling

Explore temporary victim/pending data state backed by existing writeback/pending metadata so dirty or in-flight payload lifetime is less tightly coupled to a resident cache way.

### 4. Cross-mechanism resource elasticity

Longer-term EP-L2 may allow tag/pending/payload resources to adapt to workload phase while preserving total storage/bank/timing constraints. This is a later mechanism, not a calibration shortcut.

## Hard architecture boundaries

Until a reviewed stage explicitly changes them:

- do not alter trace/workload semantics;
- do not silently change L1 geometry/timing in an L2 mechanism comparison;
- do not silently change DRAM frequency/scheduler/queues in the primary mechanism comparison;
- do not increase total L2 storage and call the result an EP-L2 storage-efficiency improvement;
- do not conflate simulator resources with undocumented physical NVIDIA structures.
