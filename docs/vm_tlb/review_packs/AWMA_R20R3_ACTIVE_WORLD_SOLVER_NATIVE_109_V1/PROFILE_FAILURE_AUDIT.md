# Sole NSYS job: workload qualified, profiler payload absent

The pre-timing eligible-stage audit was written before the NSYS result was inspected. A single NSYS command was run under the GPU campaign lock with `--trace=cuda,nvtx --cuda-graph-trace=node --capture-range=nvtx --nvtx-capture=R20R3_PROFILE --capture-range-end=stop --export=sqlite`. The Python workload used the exact OFF overlay and emitted nested NVTX ranges in fixed order `R20R3_T128_OFF_B0`, `T136`, `T144`, `T152`; all four complete-solver replays and their numerical checks completed successfully (`PROFILE_SUMMARY.json`).

The NSYS process returned code 0, but its stdout ends in `Processing events... Generated:` without a report path. The designated output prefix has no `.nsys-rep`, `.sqlite`, or `.qdstrm`; a search of the isolated campaign and worktree found none. Therefore CUDA graph child-kernel/phase durations are unavailable. The exact cause of the absent collection trigger/report is **not established** from this evidence; no zero-time interpretation is made.

The Goal permits at most one new NSYS job. It is consumed. No retry, alternate profiler, historical-profile substitution, inferred stage ranking, or S1 implementation followed. This is an evidence-admission stop, not a measured software negative.
