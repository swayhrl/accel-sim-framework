# Qualification decision

Decision: `RTX4080_ADA_PLATFORM_NOT_QUALIFIED`

The best defensible config was frozen after exactly two tuning passes. Calibration-anchor occurrence1 errors are P_L1 4.50%, P_L2 21.78%, and P_DRAM 18.74%, with the correct L1 < L2 < DRAM direction.

The predeclared held-out gate cannot pass:

- H_CACHE is the only scale-comparable held-out point. Native is 1.762880 us/launch and simulator is 2.529341 us/launch, absolute error `43.48%`, above the 35% scoped ceiling.
- H_STREAM changes from 67,108,864 elements x100 Native to 4,096 elements x1 in the trace.
- H_COMPUTE changes from 1,048,576 elements x100 Native to 1,024 elements x1 in the trace.
- The latter two are parser-valid but not valid runtime-error points; treating their raw runtimes as comparable would fabricate evidence.

Therefore there are not three valid held-out points and even the sole comparable point exceeds the scoped threshold. No `RTX4080_ADA_ACCELSIM_BASE_V1` authority is promoted. No third tuning pass, held-out-driven tuning, VM/TLB tuning, M0-M3 tuning, or mechanism study was performed.

Required recovery is external evidence, not more simulator tuning: publish workload-scale-matched held-out traces or a predeclared, defensible scale-normalized observable, then rerun the frozen config without changing it.
