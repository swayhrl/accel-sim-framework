# C16 E1 residency-intervention interpretation

Final scoped label: `RESIDENCY_INTERVENTION_PARTIALLY_SUPPORTED`.

Actual module-state census places q_proj RAW_FP16 and AWQ below the accepted 64 MiB L2 capacity, while down_proj/up_proj RAW_FP16 exceed it and their AWQ packed states remain below it. A single initialized 256 MiB FP32 allocation supplied all native sparse/dense interventions; pressure work stayed outside target timing and semantic NVTX ranges. Independent pressure-range NCU shows DENSE requested materially more L1/TEX, L2, and DRAM bytes than SPARSE over the same allocation. SPARSE remains only a page-footprint-oriented control and does not exclude TLB effects.

For primary TEXT up_proj M1 AWQ, DENSE increased median target time materially and increased target DRAM traffic by more than the registered threshold, while SPARSE did not produce the same timing/traffic effect. RAW up_proj M1 and both M256 shape-control implementations changed little in native timing. The AWQ pressure-dose response rose through 64 MiB and then approximately plateaued; the bounded 64 MiB NCU point reproduced high AWQ target DRAM traffic. CODE down_proj M1 independently reproduced the dense AWQ timing/DRAM perturbation and recovered under WARM_B.

The primary up_proj M1 AWQ WARM_B/WARM_A timing ratio was outside the strict pre-registered recovery tolerance, so the primary REVERSIBLE gate is false even though down_proj and CODE controls recover. Three of four primary gates pass; the scoped conclusion is therefore partial rather than strong support.

The evidence is consistent with cache-line residency contributing to the M1 AWQ advantage, but it does not establish L2 as the unique cause, exclude TLB effects, or authorize any cache/TLB mechanism. No NVBit, full address trace, new model, arbitrary shape sweep, or mechanism experiment was started.
