# DTC-L1 / ISCAS 2027 Discussion Reference

Last update: 2026-09-25

## 1. Accepted result before the final check

The memory-side queue-chain study is closed at SG3 commit:

`c055d817b009cbe6a59c7f8ac7af1081f86ec6e8`

BICG A-D shows that enlarging the tested queues after L2 does not materially improve performance.

BICG/GESUMMV E/F shows that the idealized detailed-DRAM 2x time-domain service probe produces large speedups.

Thus the current paper-facing result is:

> explicit queue capacity tested so far is not the main limiter, while downstream DRAM service timing/rate is a strong performance dimension.

## 2. Why ICNT->L2 is different from A-D

The four-field partition queue config is:

`ICNT->L2 : L2->DRAM : DRAM->L2 : L2->ICNT`

Default:

`64:64:64:64`

A-D intentionally modified only the memory-side second/third entries plus L2 miss queue, scheduler queue, and DRAM return queue. The first ICNT->L2 ingress FIFO remained 64.

The source condition behind `gpu_stall_icnt2mem` is:

- on an L2-domain cycle,
- if `m_memory_sub_partition[i]->full(SECTOR_CHUNCK_SIZE)` is true,
- and the interconnect has a packet waiting for that subpartition,
- increment `gpu_stall_icnt2mem`.

The FIFO helper returns true when the finite queue cannot accommodate the requested number of entries. The check uses `SECTOR_CHUNCK_SIZE` because one incoming request can expand into up to four 32-B sectors.

Therefore this counter is evidence of **ingress admission pressure before L2**, not generic DRAM-full pressure despite the legacy terminal label `gpu_stall_dramfull`.

## 3. Existing source-directed evidence

Accepted BICG telemetry:

- IO default: `gpu_stall_icnt2mem` ≈ 545M
- IO cap512: ≈ 27M
- OO default: ≈ 269M
- OO cap512: ≈ 11M

This is a much stronger cap-sensitive signal than the already-tested downstream queues.

It does not prove causality, but it justifies one direct intervention.

## 4. Final 2x2-style comparison

For each BICG mode use existing rows plus two new rows:

| Ingress queue | DRAM service | Evidence |
|---|---|---|
| 64 | 850 | existing default |
| 256 | 850 | new G |
| 64 | 1700 | accepted E |
| 256 | 1700 | new H |

This isolates:

1. ingress-queue effect at default DRAM service: G vs default;
2. ingress-queue incremental effect under DRAM2x: H vs E;
3. combined upper-bound effect vs default: H vs default.

## 5. Interpretation boundaries

If G improves materially:

> ICNT->L2 ingress admission is an independently important pressure point.

If G is weak but H improves materially beyond E:

> ingress buffering matters only once deeper DRAM service is relieved; this is an interaction.

If both G and H are weak:

> the large ingress-stall counter is primarily a symptom of upstream/downstream timing pressure rather than a dominant queue-capacity limit.

No arbitrary new threshold is needed for the main interpretation, but report exact deltas. For paper significance, >=5% remains a useful descriptive marker, not a hidden launch gate.

## 6. No further automatic cascade

After G/H, do not test:

- ICNT->L2 512;
- L2->ICNT changes;
- interconnect buffer sizes;
- NoC bandwidth/routing;
- ROP;
- additional DRAM frequencies;
- DRAM timing sweeps;
- new L2 capacities;
- new DTC cap points.

Any such step would be a new scientific stage and requires review.
