# Causality Analysis

## D256 accepted screen

All fourteen D256 rows are `COMPLETE_VALID`. META-HR speedup is +0.36%
(vectorAdd), +0.32% (scan), -1.21% (spmv), +0.07% (convolution), +2.17%
(btree), +0.79% (sad), and -1.09% (FWT). BANK-HR speedup is -0.32%, -0.12%,
-0.41%, -0.81%, +1.91%, +0.90%, and -0.64%, respectively.

No META-HR workload crosses the required roughly 5% material-response
threshold or shows the required strong downstream-pressure movement. C9
therefore does not require MSHR-only, merge-only, or MissQ-only decomposition.
The heuristic classifications are predominantly `L1_NOT_CAUSAL`; btree's
+2.17% META-HR response is `L1_LOCAL_BOTTLENECK`, below the decomposition
trigger. The complete machine-readable comparisons and 5K temporal summaries
are in `/workspace/results/ep_l2_l1_causality_d256/analysis_final/`.

## D512 promoted screen

All fourteen D512 descendants are locally `COMPLETE_VALID`. Against the
exact Lane-B D512 B0-Banked base, META-HR / BANK-HR speedups are: vectorAdd
+0.60% / +0.46%; scan +0.64% / -0.10%; spmv +0.22% / +0.49%; convolution
+0.67% / -0.53%; btree +2.17% / +1.91%; sad +0.79% / +0.90%; FWT -0.15% /
+0.36%. The exact matching rows have been promoted to
`PROMOTED_VALID_CALIBRATION`; compact review copies are
`D512_L1_CAUSALITY_COMPARISON.csv`, `D512_TEMPORAL_SUMMARY.csv`, and
`D512_CAUSAL_CLASSIFICATION.csv` in this pack.
