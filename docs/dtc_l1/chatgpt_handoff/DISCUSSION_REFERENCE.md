# DTC-L1 / ISCAS 2027 Discussion Reference

Last update: 2026-09-24

## 1. Research question

DTC removes L1-side miss-concurrency constraints and exposes substantially more memory-level parallelism. BICG and GESUMMV improve dramatically when the GPU-wide DTC lower-outstanding cap is reduced.

The L2-internal miss-queue=128 intervention now shows that simply providing more buffering at that one stage is not sufficient.

The current question is:

> Does backpressure migrate through later finite queues on the L2->memory path, and must buffering headroom and detailed-DRAM service-rate headroom be improved together before DTC's exposed MLP becomes useful?

## 2. Accepted queue result

The L2-internal miss queue was increased 32->128 entries/bank.

Across BICG/GESUMMV and IO/OO:

- source-defined `MISS_QUEUE_FULL` is eliminated;
- end-to-end cycles are unchanged or slightly worse.

This supports:

> **INTERVENTION_SUPPORTED:** L2-internal miss-queue capacity alone is insufficient.

It does not support:

> “queues do not matter.”

A serial queueing system can simply move the blocking point downstream when one buffer is enlarged.

## 3. Why the previous busW probe is diagnostic-only for this question

The accepted detailed-DRAM `busW 16->32 B` probe was source-clean but not discriminating for the dominant 32-B sector-read path.

Relevant source semantics:

- L2 sector atom = 32 B.
- A sector request reaches DRAM with `nbytes = 32 B`.
- default `dram_atom_size = BL(2) * busW(16 B) * chips(1) = 32 B`.
- each DRAM data step increments `dqbytes` by `dram_atom_size`.
- a 32-B request therefore already completes in one data step at the default.
- busW=32 raises the atom to 64 B, but the same 32-B request still completes in one step.

Thus the observed null result cannot be used as evidence that a true 2x detailed-DRAM service-rate headroom would be ineffective.

The busW attempts remain valid diagnostic runs and must not be deleted.

## 4. Why later memory-side queues are plausible

The source contains multiple finite stages after the L2 miss queue:

1. L2->DRAM queue: 64 entries/subpartition.
2. FR-FCFS scheduler pending queue: 64 entries/channel.
3. DRAM return queue: 192 entries/channel.
4. DRAM->L2 queue: 64 entries/subpartition.

The L2 cache explicitly records `L2_dram_queue_full` when it cannot push a miss to the L2->DRAM FIFO.

The FR-FCFS `dram_t::full()` path blocks further admission when pending requests reach the scheduler queue limit.

The memory-partition arbitration credit budget is coupled to scheduler-queue and return-queue capacities, so changing those resources also changes how many requests may remain outstanding in that downstream partition path. This must be stated explicitly; scheduler/return tests are admission-buffering upper bounds, not perfectly isolated microarchitectural queues.

The DRAM->L2 queue and DRAM return queue form a serial return path. Increasing only one can simply move the backpressure to the other, so the bounded return-path test intentionally enlarges both together.

## 5. Existing telemetry to preserve and compare

Before launching, extract from accepted BICG default/cap rows where available:

- `L2_dram_queue_full`;
- DRAM scheduler pending-request max and average (`mrqq`);
- `gpu_stall_icnt2mem`;
- `gpu_stall_mem2icnt`;
- mean memory-fetch latency;
- mean ICNT->memory latency;
- mean MRQ latency;
- DRAM bandwidth/utilization and bank/command statistics.

Do not invent counters for stages that are not directly observed.

The purpose is not to gate launch; it is to make the later intervention interpretation source-grounded.

## 6. Six predeclared BICG intervention families

Keep DTC cap=8192, SM count, channel count, mapping, trace, L2 MSHR, and all unrelated parameters fixed.

### A. L2->DRAM queue headroom

Change only:

- `gpgpu_dram_partition_queues: 64:64:64:64 -> 64:256:64:64`

Question:

> Does the first queue after L2 constitute the next backpressure point?

### B. DRAM scheduler/admission headroom

Change only:

- FR-FCFS scheduler queue 64 -> 256.

Important:

- this also increases the source-defined shared credit budget;
- report it as scheduler/admission headroom, not a pure scheduler-storage-only effect.

### C. Return-path buffering headroom

Change together:

- DRAM->L2 queue 64 -> 256;
- DRAM return queue 192 -> 768.

Question:

> Is response-side buffering/backpressure constraining progress?

This is intentionally a bundled serial-return-path upper bound.

### D. Full memory-side queue-chain headroom

Increase:

- L2-internal miss queue 32 -> 128;
- L2->DRAM queue 64 -> 256;
- DRAM scheduler queue 64 -> 256;
- DRAM return queue 192 -> 768;
- DRAM->L2 queue 64 -> 256.

Keep ICNT->L2 and L2->ICNT at 64; they are interconnect-facing queues and are outside the current memory-side queue-chain factor.

Question:

> If the major finite memory-side buffering limits are jointly relaxed, does the DTC headroom emerge?

### E. Detailed-DRAM service-rate headroom

Change only the DRAM clock:

- 850 MHz -> 1700 MHz.

Keep:

- core / ICNT / L2 clocks at 1410 MHz;
- DRAM timing cycle counts unchanged;
- bus width at 16 B;
- channel count at 20;
- all queues at default;
- mapping and cache resources unchanged.

This makes `dram_cycle()` execute approximately twice as often per unit core time and is therefore an idealized **2x detailed-DRAM service-rate upper bound**.

It is not a physical V100 frequency claim.

### F. Full queue-chain + detailed-DRAM service headroom

Combine D and E.

Question:

> Do buffering and sustained memory service need to be relieved together?

## 7. Why these six can be batch-launched

These are not result-selected points. They form one predeclared diagnostic set that decomposes:

- first downstream request buffering;
- DRAM scheduler/admission buffering;
- response-side buffering;
- all memory-side buffering together;
- service rate alone;
- all buffering + service together.

Because the server is currently underutilized, all BICG IO/OO rows may be placed into the rolling worker pool once their overlays and identities are statically validated.

Do not wait for one result before starting another family.

## 8. GESUMMV independent validation

GESUMMV is used only to validate the most informative result(s), not to duplicate the full BICG diagnostic matrix.

After all BICG rows close, a configuration is eligible for GESUMMV only if:

- it improves BICG cycles by >=5% in at least one mode versus the exact default;
- its telemetry moves coherently;
- it uses no parameter outside the predeclared six families.

Validate at most two configurations, with this fixed priority if multiple qualify:

1. full queue-chain + DRAM2x;
2. full queue-chain;
3. DRAM2x alone;
4. L2->DRAM queue;
5. scheduler/admission;
6. return-path buffering.

For each selected configuration run GESUMMV IO and OO.

## 9. Conditional all-headroom ceiling with L2 capacity

The existing BICG L2-capacity=2x result is already accepted and shows partial benefit.

Only if **full queue-chain + DRAM2x** improves BICG by >=5% in either IO or OO, authorize two additional BICG ceiling rows:

- L2 capacity 20 MiB
- full queue-chain headroom
- DRAM 1700 MHz
- IO and OO

This is an idealized all-headroom ceiling, not a realistic product configuration and not a new factorial sweep.

Do not add new L2-capacity levels.

## 10. Paper interpretation

Possible strong result:

> DTC exposes useful MLP that a fixed downstream hierarchy cannot absorb; coordinated buffering and service-rate headroom converts that concurrency into performance.

Possible partial result:

> A specific later queue/admission stage is important, while other buffers are symptoms.

Possible null result:

> Even broad memory-side queue-chain relief plus a genuine detailed-DRAM service-rate upper bound is insufficient; the remaining effect lies elsewhere in the downstream path or request-timing interaction.

Any of these outcomes is valid.

## 11. Forbidden expansion

Do not run:

- queue sizes beyond the predeclared 256/768 upper bounds;
- L2 miss queue beyond 128;
- new L2 MSHR points;
- cap=1024/4096;
- additional DRAM frequencies;
- busW as the formal service-rate dimension;
- memory-channel-count changes;
- L2-bank-count changes;
- address-mapping changes;
- NoC or ROP sweeps;
- DRAM timing-string sweeps;
- perfect/infinite memory;
- adaptive admission mechanisms;
- FAST12 sensitivity;
- new logical-Tag experiments.
