# C16 E1 semantic-NCU cache-state repair interpretation

V1 selector identity and raw arithmetic remain valid and unchanged. Its seven-pass default kernel replay is now explicitly interpreted as `COLD_CACHE_KERNEL_REPLAY_DIAGNOSTIC`.

V2 used Nsight Compute 2025.1.1 application replay with `--cache-control none`. Each selected kernel reports one application replay pass; every application run rebuilt the accepted module state, performed two warmups outside the target range, and reproduced the accepted output SHA for its single in-range semantic invocation. RAW retained one complete target kernel and AWQ retained its GEMM plus reduction sequence.

L1/TEX and L2 AWQ/RAW ratios preserve V1 direction and similar magnitude. DRAM preserves the qualitative directions but changes magnitude materially at M1: the V2 AWQ semantic-module DRAM request is 640 bytes versus 138,156,416 bytes for RAW. M256 AWQ remains above RAW for all three traffic metrics. All V2 traffic interactions retain the accepted native timing interaction direction.

These results describe profiler-context-sensitive semantic-module traffic. They do not establish cache causality, TLB causality, or a mechanism opportunity. No NVBit, full address trace, shape sweep, role reselection, or cache/TLB mechanism experiment was started.
