# DQ2 — B1→B4 and representation control

`QUESTION_INCOMPLETE`. The frozen B1/B4 pair requires MP02 and MP03. Direct raw generated-token comparisons show MP02: 3/3 mismatched measured rows (first index 9); MP03: 9/12 mismatched batch rows (first index 3). Their Graph-OFF correctness STOPs and missing observed/NSYS captures invalidate their native medians, effective-M/shape comparison and the 85% matched estimator. Frozen nominal B1/B4 inputs cannot substitute for a qualified observed execution. No B1→B4 utilization claim is made.

MP05 AWQ B1 is a legal *representation control only*: native Graph ON median 167.931198120 ms and Graph OFF median 275.276397705 ms, each from three instrumentation-OFF request CUDA events; observed decode gate/up input shape `[1,2048]` gives effective M=1 in its own graph-OFF semantic row. Its Marlin path and BF16 path differ in representation/runtime, so no strict BF16-vs-AWQ causal ratio is admitted. The MP05 ON/OFF difference is not the contract's MP02/MP03 matched absorption estimator.

Graph control: `GRAPH_CONTROL_GAP_NOT_IDENTIFIABLE`. No alternate denominator was invented.
