# r19 downstream storage / service account — authorized targets, not PPA

Q4/D4 are not equal-downstream-cost competitors to H0. Targets below follow
coordination28e8fce027046643b909c58469e9c7697522a3df; producer actual-value dumps
and independent condition qualification are still required before reception.

| Structure | H0 | Q4/D4 | Added entries across chip |
|---|---:|---:|---:|
| L2→DRAM FIFO, per64 slices |128|512|24576|
| DRAM→L2 FIFO, per64 slices |64|256|12288|
| FR-FCFS scheduler, per32 channels |128|512|12288|
| DRAM return queue, per32 channels |192|768|18432|
| Derived shared credit limit, per partition |319|1279|+960 per partition, bookkeeping tied to queues |

The other two partition FIFOs remain64/64. Credit is derived from scheduler+
return-(subpartitions-1):128+192-1=319 versus512+768-1=1279. Do not count credit
as an independent extra payload RAM or label Q4 a single-FIFO change.
FIFO/carrier widths, packet storage, arbitration, comparators and physical
timing are not mapped here; entry counts are not silicon area. No sizeof,
power or measured RTL benefit is inferred. Both modes get the same headroom.

Both retain1024 tags,1168×128B primary slots,4 banks/292 slots,1 modeled
operation/bank/physical GPU cycle, D512,128 WAD and common128B latch. D4 adds
DRAM850→3400MHz while core/ICNT/L2 stay1132MHz; unchanged integer DRAM timing
parameters have a different physical duration and partition-service frequency.
The100-GPU-cycle dram_latency remains. No pure-bandwidth, product-frequency,
free implementation or global DRAM nonbinding claim follows.

LOWER_CEILING would use a different path/statistical scope and requires its
own independent functional qualification. Its absent counters must not become
zeros or be compared directly with detailed DRAM utilization. It is not
qualified or executed in this Lane6 revision. Strong static repartition,
TVD/RO/Ideal and real RTL/STA/power remain separate evidence gaps.
