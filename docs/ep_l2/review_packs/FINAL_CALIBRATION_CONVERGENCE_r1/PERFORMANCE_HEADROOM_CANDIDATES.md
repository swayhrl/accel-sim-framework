# Performance-headroom candidates — not executed

| Candidate | Workloads | Evidence |
| --- | --- | --- |
| H-SCHED 128→256 | scan, vectorAdd_4M, convolutionSeparable, FWT_7_21 | scheduler/lower-path pressure |
| H-L2D 128→256 | scan, vectorAdd_4M, convolutionSeparable, spmv | L2→DRAM-full pressure |
| H-BW 850MHz→1GHz | scan, vectorAdd_4M, spmv | high final-snapshot native physical DRAM utilization |

These are later sensitivities, not baseline edits. `sad` is the low-pressure
control. No headroom simulation was run. A later masking claim requires an
L2-local effect at H0 and a measured mechanism×headroom interaction.
