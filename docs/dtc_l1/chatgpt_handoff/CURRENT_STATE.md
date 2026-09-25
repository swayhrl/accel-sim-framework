# DTC-L1 / ISCAS 2027 Current State

Last coordination update: 2026-09-25

Status: **SIMULATOR DOWNSTREAM LOCALIZATION CLOSED; PAPER/RTL PHASE NEXT**

## 1. Accepted simulator authority

Current accepted SG3 authority:

`6886930ab22d63701e58732cfde18ba019d1dfde`

The following simulator evidence is accepted and frozen:

- FAST64 primary Base / IO / OO performance.
- Lane-E mechanism evidence.
- 80-KiB conventional-cache capacity control.
- transaction-granularity fairness controls.
- SG4A logical-Tag characterization.
- SG5 comparable-lower-traffic evidence.
- SG3 cap sensitivity and positive controls.
- L2-internal miss-queue 32->128 intervention.
- memory-side queue-chain A-F study.
- detailed-DRAM 2x time-domain service probe.
- GESUMMV E/F validation.
- BICG 20-MiB-L2 all-headroom ceiling.
- final ICNT->L2 ingress G/H check.

Do not rerun, rename, or replace these accepted rows.

## 2. Final downstream conclusions

### Queue-capacity interventions are not the dominant explanation

Across the tested path, enlarging explicit finite buffers does not materially recover BICG performance:

- L2-internal miss queue 32->128 eliminates `MISS_QUEUE_FULL` but does not improve performance.
- L2->DRAM queue headroom is neutral/slower.
- DRAM scheduler/admission headroom is slower.
- return-path buffering is neutral.
- full memory-side queue-chain headroom is neutral/slightly mixed.
- ICNT->L2 ingress 64->256 is also neutral:
  - G/IO 93,788,867 cycles vs default 93,942,704;
  - G/OO 48,040,165 vs default 47,231,655.
- adding ICNT->L2 headroom on top of accepted DRAM2x is also neutral:
  - H/IO 51,153,208 vs E/IO 50,713,356;
  - H/OO 29,821,617 vs E/OO 29,933,876.

Therefore large queue-full/stall counters are pressure indicators, but the tested FIFO capacities are not demonstrated dominant performance limiters.

### Detailed-DRAM service timing/rate is a strong dimension

The source-discriminating DRAM time-domain upper bound is strongly beneficial:

BICG:
- default IO 93,942,704 -> E/IO 50,713,356 cycles (-46.0% cycles)
- default OO 47,231,655 -> E/OO 29,933,876 (-36.6%)

GESUMMV:
- default IO 210,667,785 -> E/IO 107,119,606 (-49.2%)
- default OO 143,059,605 -> E/OO 79,382,011 (-44.5%)

The full queue-chain + DRAM2x configuration adds only modest gain over DRAM2x alone.

Paper-safe interpretation:

> DTC exposes additional memory-level parallelism, but for difficult workloads the usefulness of that concurrency is strongly sensitive to downstream DRAM service timing/rate. Merely enlarging the tested queue capacities does not recover the same headroom.

Do not claim a unique physical DRAM bottleneck or a physical 2x-frequency prediction.

### L2 capacity remains an approximately separate sensitivity dimension

The accepted BICG all-headroom ceiling with 20-MiB L2 gives:

- IO 47,347,123 cycles
- OO 22,204,820 cycles

This supports a residual L2-capacity effect in addition to the DRAM-service effect, but it is an idealized ceiling point, not a product configuration or broad capacity sweep.

## 3. Final R5 interpretation

R5 decision:

`ICNT_L2_INGRESS_PRESSURE_NOT_CAPACITY_LIMITED`

The source-defined `gpu_stall_icnt2mem` counter is an ICNT->L2 ingress-admission pressure metric despite the legacy printed label `gpu_stall_dramfull`.

Increasing the ingress FIFO 64->256 does not materially improve BICG either at default DRAM service or on top of DRAM2x.

Thus no further queue/NoC/ROP/DRAM-parameter cascade is authorized.

## 4. Simulator STOP boundary

The downstream-localization program is complete.

Do not launch new:

- queue sweeps;
- NoC/interconnect sweeps;
- ROP sweeps;
- DRAM frequency/timing/bus-width sweeps;
- L2 capacity/MSHR/logical-Tag sweeps;
- DTC cap sweeps;
- FAST12 sensitivity;
- adaptive-admission mechanisms.

Any future simulator work requires a new explicit scientific question, not continuation of SG3 localization.

## 5. Next project phase

Priority now moves to:

1. paper-facing synthesis of accepted evidence and figures;
2. final architecture description and claim-boundary cleanup;
3. RTL/DC area/timing/SRAM evidence;
4. manuscript v0.3 and page-budget compression.

The next stage should not use simulator time unless a paper/RTL review reveals a genuine missing scientific control.
