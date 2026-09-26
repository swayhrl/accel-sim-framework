# R53 source and closest-work audit

Pinned `NVlabs/Fast-dLLM@a9b81e4c...`; `v2/generation_functions.py` blob is `76fc22d1...`. Official A0 output matches the instrumented A0 exactly in both discovery domains. Fast-dLLM v2 already removes finished requests at block boundaries and uses cohort-wide refresh decisions. dInfer, dLLM-Serve, BlockServe, Sangam, BiCache and FluxServe already cover broad packing/batching/cache/graph ideas.

The direct A1 packing attempt reduced executed token rows by about 12.3% on GSM8K and 21.6% on HumanEval, but changed forced commits, complete discrete trajectories, and final tokens. The one allowed safe-bucket repair preserved the trajectory exactly but restored A0's forward/token-row work. Thus the apparent reduction is an algorithm-visible numerical/trajectory change, not a legal mapping gain. No hardware capability claim follows.
