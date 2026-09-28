# Scientific interpretation

All four A outputs exactly reproduce the accepted SHA and all B outputs pass `rtol=1e-2, atol=5e-2`. The dynamic launch audit confirms the preregistered A/B grids, including A `down_proj_M256` grid 3584; every A point launches GEMM then reduction, while every B point launches only the same m16n128k32 GEMM family.

At `up_proj_M256`, B median module time is 0.501024 ms versus A 0.704512 ms, an improvement of 28.88%. The improvement exceeds the larger arm CV. The bounded NCU pair also lowers L2 and DRAM totals and removes the reduction row; the automatically exposed per-kernel duration does not contradict the module result. These totals are not tensor-level attribution.

At `down_proj_M256`, the median improvement is only 0.90%, below the 5% rule and below the larger arm CV. At M1, B regresses by 41.30% for up_proj and 413.32% for down_proj. Therefore the preregistered global H1 is not supported. The allowed decision is `OPERATOR_SPECIFIC_SPLIT_POLICY_ONLY`: the fixed split8 policy is materially costly for the tested up_proj M256 point, but split1 is not a generally superior policy across the four selected points.

The four points selected this diagnostic and are not an independent holdout. This result is not the unique cause of E1, is not a full-model decode speedup, is not a new split-K algorithm, and does not prove an L2 mechanism.
