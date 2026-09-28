# Scientific interpretation

Decision: `STRONG_SUPPORT_CROSS_M_WEIGHT_SIDE_REUSE`.

The counterfactual preserved the compiled extension, target GEMM kernel,
grid/block, K-loop, split/reduction behavior, scratch, arithmetic inputs, and
total allocation.  All cells allocated sixteen bit-identical qweight, qzeros,
and scales replicas.  The only intended state change was runtime
`replica_mask`: zero made all M tiles read replica 0, while fifteen mapped the
sixteen M tiles to sixteen distinct but identical replica addresses.

All same-split SHARED/PER_MTILE outputs were bitwise identical.  K2560 A/B
passed the original tolerance with max absolute difference 6.103515625e-05;
K3072 A/B was bitwise identical.

GEMM-only NCU evidence:

| K | split | hit SHARED | hit PER_MTILE | hit loss | DRAM ratio PER/SHARED |
|---:|---:|---:|---:|---:|---:|
| 2560 | 8 | 95.86% | 28.17% | 67.69 pp | 5.51x |
| 2560 | 1 | 90.53% | 35.50% | 55.03 pp | 5.93x |
| 3072 | 8 | 95.89% | 28.48% | 67.41 pp | 6.11x |
| 3072 | 1 | 63.54% | 35.62% | 27.93 pp | 1.77x |

The preregistered pattern is present.  At K2560 split1, removing cross-M
address sharing sharply reduces hit rate, increases misses from 4,794,648 to
32,729,128 sectors, and increases DRAM from 181,183,232 to 1,075,074,000 bytes.
At K3072 split1, the direction remains the same but the additional hit loss and
DRAM multiplier are smaller, consistent with SHARED already losing reuse near
the capacity knee.  Both split8 points lose their high-hit behavior under
PER_MTILE, directly showing that their high hit rate depends strongly on
cross-M repeated physical addresses.

Median module timing worsens under PER_MTILE by 1.72x/3.39x at K2560 and
1.91x/2.59x at K3072 for split8/split1.  Split8 reduction kernels are recorded
separately; they are excluded from the GEMM hit/miss and DRAM interpretation.

The supported claim is limited to the combined weight-side address set
(qweight, qzeros, scales) in this artificial frozen proxy.  The experiment does
not attribute the effect to any one tensor, infer NVIDIA replacement details,
or claim universality across models or GEMMs.
