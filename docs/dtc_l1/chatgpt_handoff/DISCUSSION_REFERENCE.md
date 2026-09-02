# DTC-L1 Discussion Reference

## Research question

Reproduce the thesis Decoupled-Tag L1 design in Accel-Sim with enough fidelity to explain its performance mechanisms, then use the infrastructure for controlled extensions and modern-GPU studies.

## Short conclusion

The reproduction should be **mechanism-faithful rather than gate-faithful**. We preserve the resource relationships that determine MLP, blocking, allocation pressure, and IO/OO completion, while parameterizing implementation details that are not themselves the research contribution.

## Why an explicit PIB matters

The thesis motivation attributes a large fraction of conventional L1 stalls to the small pending-instruction structure, with Tag/cacheline allocation and MSHR capacity as additional limits. Therefore an Accel-Sim reproduction cannot substitute an unrelated dispatch register and still claim the same mechanism. The simulator needs a bounded pending-instruction admission point that can propagate backpressure to the memory-instruction entrance.

## Why Tag and Physical Data stay decoupled

The logical Tag Array is a 16KB, 4-way, 32-set structure, while the physical Cacheline Array is 80KB. A valid logical Tag stores a physical-line identity. Tag-bank location does not imply Data-bank location.

For the first model, Tag-bank throughput is explicit because it is a visible pipeline resource; detailed Data-bank conflicts are not required. Physical allocation remains finite at four lines/cycle and retirement remains one instruction/cycle, preserving the dominant resource bounds without reintroducing an artificial Tag↔Data bank coupling.

## Why partial allocation/no rollback is frozen

A top-level memory instruction can contain many divergent line requests. Allocation occurs over multiple cycles. If physical space runs out after some lines have already been allocated, those allocations remain held while the instruction waits for the rest.

Under IO FIFO retirement this can form a circular resource dependency: the stalled instruction holds newly allocated lines, cannot complete, and the ordering/resource state can prevent the releases required to make further progress. We intentionally allow this behavior to emerge instead of adding an all-or-nothing allocator that would change the mechanism.

## Why simulator coalescer width is 32 by default

The original RTL processed only 16 threads/cycle largely for area/port constraints. The research simulator may process the full 32-thread warp/cycle as long as Baseline/IO/OO share the same front-end rule. A 16-thread/cycle knob remains available for fidelity/sensitivity.

## IO vs OO distinction

IO-DTC uses a FIFO pending-instruction queue and in-order retirement. Old physical lines displaced from the logical Tag space can be held and released safely according to FIFO progress.

OO-DTC allows a ready younger entry to retire before an older stalled entry. That requires explicit physical-line lifetime tracking plus pending-dependency wakeup state. A physical line is reclaimable only when it is no longer visible through a logical Tag and no live reference remains.

## Ref Count interpretation

Frozen simulator semantics use **per-coalesced-128B-cacheline-reference** counting.

Multiple lanes that coalesce into one 128B line request contribute one reference. A fully divergent 32-thread warp may produce up to 32 distinct line references; with 128 OO PIB entries, a conservative upper bound is 4096 and a 13-bit counter matches the thesis sizing convention.

This interpretation is preferable to per-thread counting because the functional pipeline operates on coalesced cacheline requests. It is also more faithful to the thesis examples in which a coalesced request increments the counter once.

## Sector extension decision

The primary paper reproduction remains whole-line 128B DTC.

The modern extension does **not** change the renaming granularity:

- one 128B logical line still maps to one 128B physical line;
- line-level Tag visibility and Ref Count remain line-granular;
- data readiness is split into 4×32B sectors;
- sector INVALID/PENDING/VALID state and OO merge/wakeup are sector-granular;
- `wait_cnt` counts not-ready sector dependencies.

This keeps the original DTC concept intact while making it compatible with a sector-cache execution model.

## Store, Atomic, Fence, and bypass

They are not required to prove the read-path Tag-decoupling mechanism, so the first implementation can isolate reads. They are required before complete compute results are considered formal because Stores/Atomics participate in long-latency instruction lifecycles and therefore influence IO head-of-line blocking versus OO completion.

Existing architectural L1 bypass behavior must remain correct from the beginning. Thesis policy-driven DTC bypass is a separate later optimization and should not be conflated with architectural bypass.

## Whole-line paper mode vs modern mode

Keep two evidence categories:

1. **PAPER-WHOLE-LINE** — 128B line state/requests, intended to reproduce thesis mechanisms/figures.
2. **MODERN-SECTOR** — 128B Tag/Physical mapping with 4×32B readiness, intended to evaluate the design on modern sector-cache assumptions.

Do not silently combine them into a single average.

## Baseline fairness

The baseline must have explicit 8-entry PIB behavior and 32-entry traditional MSHR behavior for the paper-style mechanism comparison. DTC defaults are IO PIB 256 and OO PIB 128.

A later publication-quality evaluation should also include equal-resource/equal-area comparisons so performance is not attributed solely to a larger physical storage budget.

## Graphics scope

Stock Accel-Sim is not a direct glmark2 graphics-pipeline simulator. Any graphics result without original LGPU/request traces should be labeled a calibrated graphics-memory proxy or shader-memory-stage study, not direct glmark2 FPS reproduction.

Calibration should target request/traffic/coalescing/miss/stall signatures, not target speedup.

## Rejected shortcuts

- making Tag Array globally fully associative;
- binding a Tag bank to a Data bank;
- unlimited/zero-cycle physical allocation;
- unlimited OO retirement;
- all-or-nothing allocation rollback that removes the IO resource cycle;
- using traditional MSHR capacity as the DTC merge mechanism;
- identifying fills only by a current logical Tag lookup after Tag eviction;
- hard-coding paper default sizes into IO/OO implementation;
- treating temporary Store/Atomic bypass bring-up as formal IO/OO evidence;
- directly claiming glmark2 execution in stock Accel-Sim.

## Expected research outcome

The infrastructure should let us separately answer:

- whether larger PIB alone explains the gain;
- how much comes from Tag→Physical renaming;
- how much traditional MSHR capacity ceases to matter;
- how much OO completion removes IO head-of-line blocking;
- when physical capacity becomes the new bottleneck;
- where the bottleneck moves after DTC raises L1 MLP;
- how the mechanism changes under modern sector behavior and different memory-system latency/bandwidth.
