# Causal interpretation

Classification: `MSHR_ADMISSION_THROTTLE_DOWNSTREAM_LIMITED`.

For convolution under D512, increasing Line-MSHRs from 128 to 256 eliminates
the exact Line-MSHR-full count (`931,416 -> 0`) but changes cycles only from
`292,211 -> 291,108` (0.38% improvement, below the 2% sensitivity screen).
The D256 control is exactly unchanged at 290,308 cycles because it had no
Line-MSHR-full blocks. The D512 spmv negative control is also exactly unchanged
at 23,560 cycles and had no MSHR-full blocks at 128.

The 256-entry D512 run moves pressure rather than producing a material speedup:
L2-to-DRAM-full falls `2,455,970 -> 2,144,141`, while MissQ-full rises
`1,723,839 -> 2,329,422` and WAD-full events rise `3,407 -> 20,834`; scheduler
full remains substantial (`2,450,677 -> 2,405,303`) and DRAM traffic/bus use is
nearly unchanged. Thus MSHR128 is a real admission ceiling exposed after
descriptor relief, but not the final performance ceiling for this workload.

This sensitivity result does not promote MSHR256 as a baseline and does not
justify an RO no-MSHR, TVD, or Unified mechanism claim.
