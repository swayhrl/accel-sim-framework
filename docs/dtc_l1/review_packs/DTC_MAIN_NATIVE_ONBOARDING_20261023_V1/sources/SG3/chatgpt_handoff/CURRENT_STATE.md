# DTC-L1 / ISCAS 2027 Current State

Last coordination update: 2026-09-25

Status: **SIMULATOR MAINLINE ACCEPTED; FINAL ICNT->L2 INGRESS-QUEUE CHECK AUTHORIZED**

## 1. Accepted scientific state

The following simulator evidence is now accepted and frozen:

- FAST64 primary Base / IO / OO performance.
- Lane-E mechanism evidence.
- 80-KiB conventional-cache capacity control.
- transaction-granularity fairness controls.
- SG4A logical-Tag characterization.
- SG5 comparable-lower-traffic evidence.
- SG3 cap sensitivity and positive controls.
- L2-internal miss-queue 32->128 intervention.
- memory-side queue-chain study A-F.
- detailed-DRAM 2x time-domain service probe.
- GESUMMV validation of E/F.
- BICG all-headroom 20-MiB L2 ceiling.

Current SG3 authority:

`c055d817b009cbe6a59c7f8ac7af1081f86ec6e8`

Do not rerun or relabel these accepted rows.

## 2. Current downstream conclusions

### L2/internal and memory-side queue capacity

Enlarging explicit queues does not materially recover BICG performance:

- L2-internal miss queue 32->128 eliminates `MISS_QUEUE_FULL` but does not improve BICG/GESUMMV.
- L2->DRAM queue headroom is neutral/slower.
- scheduler/admission headroom is slower.
- return-path buffering is neutral.
- full memory-side queue-chain headroom is neutral/slightly mixed.

Therefore explicit downstream buffering capacity tested so far is not the dominant explanation.

### Detailed-DRAM service rate

The source-discriminating DRAM time-domain probe is strongly beneficial.

BICG:
- default IO 93,942,704 -> E/IO 50,713,356 cycles (-46.0%)
- default OO 47,231,655 -> E/OO 29,933,876 cycles (-36.6%)

GESUMMV:
- default IO 210,667,785 -> E/IO 107,119,606 cycles
- default OO 143,059,605 -> E/OO 79,382,011 cycles

Full queue-chain + DRAM2x adds only modest improvement over DRAM2x alone.

Paper-safe interpretation:

> For the tested difficult workloads, DTC exposes concurrency whose usefulness is strongly sensitive to downstream DRAM service timing/rate; simply enlarging the tested L2/memory-side queues is insufficient.

Do not convert this simulator upper bound into a physical-frequency claim.

### Residual L2-capacity effect

The accepted R4 ceiling combines 20-MiB L2, full queue-chain headroom, and DRAM2x:

- BICG IO: 47,347,123 cycles
- BICG OO: 22,204,820 cycles

This is a bounded ceiling result, not a realistic product configuration or capacity sweep.

## 3. Why one final ingress check remains

The accepted BICG telemetry shows a very large source-defined `gpu_stall_icnt2mem` counter at default cap=8192 that falls by roughly an order of magnitude under cap=512.

Source review shows that this counter increments when:

- an ICNT packet is waiting for a memory subpartition, and
- the subpartition's **ICNT->L2 ingress FIFO** lacks room for the worst-case sector expansion.

The terminal text label `gpu_stall_dramfull` is legacy/misleading; the actual source condition is the ICNT->L2 ingress-buffer admission check.

This queue is the **first** entry of:

`gpgpu_dram_partition_queues = 64:64:64:64`

and was intentionally held at 64 during the accepted A-F memory-side queue-chain study.

Therefore one final bounded experiment is scientifically justified.

## 4. Final authorized question

> Does enlarging the ICNT->L2 ingress queue recover BICG performance by itself, or provide additional benefit when combined with the already-supported DRAM2x service headroom?

Only four BICG rows are authorized:

- G/IO: ICNT->L2 64->256
- G/OO: ICNT->L2 64->256
- H/IO: ICNT->L2 64->256 + DRAM 850->1700 MHz
- H/OO: ICNT->L2 64->256 + DRAM 850->1700 MHz

No other queue, NoC, ROP, DRAM timing, capacity, or cap sweep is authorized.

## 5. STOP boundary

After these four rows:

- strict-validate;
- compare G to default;
- compare H to accepted E/DRAM2x and default;
- update the SG3 review pack / Codex report;
- STOP.

If G/H are neutral, freeze downstream localization completely.

If G/H are materially beneficial, report the bounded result and STOP for scientific review before any cross-workload extension.
