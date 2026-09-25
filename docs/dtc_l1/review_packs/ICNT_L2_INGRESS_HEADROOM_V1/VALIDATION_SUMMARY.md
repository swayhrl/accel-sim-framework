# R5 validation and result summary

All four fresh immutable attempts natural-exited and strict-PASSed: UUID,
workload/mode, trace, config echo, default cap echo, instruction identity,
terminal drain, observer closure, and L2 consistency all pass.

| Family/mode | cycles | versus default | versus E | ingress stall | mem->ICNT stall | avg ICNT->mem | avg MRQ |
|---|---:|---:|---:|---:|---:|---:|---:|
| G IO | 93,788,867 | +0.16% | — | 506,963,103 | 1,391,547 | 963 | 783 |
| G OO | 48,040,165 | -1.71% | — | 247,783,693 | 139,392 | 560 | 788 |
| H IO | 51,153,208 | +45.54% | -0.87% | 286,763,252 | 540,331 | 584 | 422 |
| H OO | 29,821,617 | +36.87% | +0.38% | 149,696,457 | 168,600 | 308 | 406 |

Default comparators are IO 93,942,704 and OO 47,231,655 cycles.  E comparators
are IO 50,713,356 and OO 29,933,876.  `ingress stall` is the source-defined
`gpu_stall_icnt2mem` counter printed under legacy label `gpu_stall_dramfull`;
`mem->ICNT stall` is printed under legacy label `gpu_stall_icnt2sh`.

Resolved G queue/clock: `256:64:64:64`, `1410:1410:1410:850`; H: the same
queue tuple with `1410:1410:1410:1700`.  Each DRAM `mrqq` reports max 64;
the raw stdout index preserves all per-partition avg samples.  DTC lower
outstanding averages (integral/core ticks) are G IO 1962.1, G OO 2043.3,
H IO 2167.7, H OO 2013.2.  L2 miss-queue average pressure
(integral/L2-bank ticks) is G IO 1.05, G OO 1.10, H IO 0.93, H OO 0.59.
