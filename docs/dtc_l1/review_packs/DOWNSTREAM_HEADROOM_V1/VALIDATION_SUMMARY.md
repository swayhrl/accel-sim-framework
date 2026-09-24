# Validation and result summary

Every row below has a fresh immutable UUID (unless marked exact reuse), natural exit zero, instruction identity, mode/config echo, DTC/lower drain, observer closure, and source-audited L2 terminal consistency.  `cycles` are `gpu_tot_sim_cycle`.

| Workload | Mode | Cell | cycles | relative to comparator | disposition |
|---|---:|---|---:|---:|---|
| BICG | IO | Q0M0 exact reuse | 93,942,704 | baseline | accepted reference |
| BICG | IO | Q1M0 exact reuse | 94,719,567 | +0.83% vs Q0M0 | queue alone; queue-full 145,882,748 -> 0 |
| BICG | IO | Q0M1 | 97,104,810 | +3.37% vs Q0M0 | strict PASS; Gate M false |
| BICG | IO | Q1M1 | 95,272,616 | +0.58% vs Q1M0 | strict PASS; Gate I false |
| BICG | OO | Q0M0 exact reuse | 47,231,655 | baseline | accepted reference |
| BICG | OO | Q1M0 exact reuse | 47,588,121 | +0.75% vs Q0M0 | queue alone; queue-full 43,594,150 -> 0 |
| BICG | OO | Q0M1 | 47,522,785 | +0.62% vs Q0M0 | strict PASS; Gate M false |
| BICG | OO | Q1M1 | 47,844,044 | +0.54% vs Q1M0 | strict PASS; Gate I false |
| GESUMMV | IO | Q0M0 exact reuse | 210,667,785 | baseline | accepted reference |
| GESUMMV | IO | Q1M0 | 210,761,147 | +0.04% vs Q0M0 | strict PASS; queue-full 217,938,332 -> 0 |
| GESUMMV | OO | Q0M0 exact reuse | 143,059,605 | baseline | accepted reference |
| GESUMMV | OO | Q1M0 | 144,046,358 | +0.69% vs Q0M0 | strict PASS; queue-full 214,486,650 -> 0 |

`Q` is L2 miss queue entries (0=32 default, 1=128); `M` is selected detailed-DRAM data-bus width (0=16 B default, 1=32 B).  Default DTC lower outstanding cap is 8192 in all rows.  The BICG Q1M1 controls are valid because the prerequisite Q1M0 rows had already strict-PASSed.

## Gate decision

Gate M requires at least one BICG Q0M1 row to be >=5% faster than Q0M0 with coherent service telemetry.  Gate I requires at least one BICG Q1M1 row to be >=5% faster than the better of Q0M1/Q1M0 with coherent telemetry.  All four C1 deltas are non-positive.  Therefore Gate M and Gate I are both false; the four conditional GESUMMV C2 cells are correctly `NOT_LAUNCHED_BY_PREDECLARED_GATE`.

## Claims and forbidden claims

Allowed: queue fullness can be eliminated in these rows without material end-to-end improvement; the selected 2x detailed-DRAM service-width upper bound did not unlock the BICG performance headroom under cap=8192.

Forbidden: that L2 queues never matter; that no downstream/memory bottleneck exists; that 32-B bus width models a particular physical GPU; any generalization beyond BICG/GESUMMV, this Core/runtime/trace identity, or the one selected counterfactual.
