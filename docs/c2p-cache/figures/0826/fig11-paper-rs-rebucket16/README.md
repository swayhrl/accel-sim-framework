# Fig. 11 paper-R/S rebucketed local-16 note

> **Non-evidentiary 0826 diagnostic.** This reuses the final local
> `l2_access_normalized` measurements but groups the same 16 workloads
> with the C2P paper's R/S labels. It is not a new experiment, a formal
> paper figure, or a basis for a performance claim.

## Definition and provenance

Each value is `mode l2_total_cache_accesses / baseline l2_total_cache_accesses`
for the same workload. The source is the retained final analysis CSV:
`/workspace/worktrees/accel-sim-c2p-cache/hw_run/c2p-paper16-analysis-final-v7-20260821/paper16_modes.csv`.
The baseline is therefore 1.000 for every workload and is used only as
the normalization reference; its redundant bars are not plotted.

## Paper-R/S group averages

| Paper R/S group | Workloads | ATA | CCD | RING | 本文提到的结构 |
|---|---|---:|---:|---:|---:|
| R1S0 | CU, HO, GA | 0.926 | 0.935 | 0.782 | 0.798 |
| R1S1 | LU, SG, 3M, GE, B+, 2D, ST | 0.944 | 0.975 | 0.912 | 0.887 |

## Per-workload measured values

| Paper group | Workload | Local group | ATA | CCD | RING | 本文提到的结构 |
|---|---|---|---:|---:|---:|---:|
| R1S0 | CU | R1S0 | 0.801 | 0.812 | 0.493 | 0.488 |
| R1S0 | HO | R1S0 | 0.979 | 0.995 | 0.855 | 0.909 |
| R1S0 | GA | R0S0 | 0.999 | 1.000 | 0.996 | 0.997 |
| R1S1 | LU | R0S0 | 0.964 | 0.978 | 0.877 | 0.936 |
| R1S1 | SG | R1S0 | 0.920 | 0.980 | 0.873 | 0.805 |
| R1S1 | 3M | R1S0 | 0.965 | 0.993 | 1.069 | 0.939 |
| R1S1 | GE | R1S0 | 0.954 | 0.992 | 1.042 | 0.939 |
| R1S1 | B+ | R1S1 | 0.945 | 0.959 | 0.825 | 0.886 |
| R1S1 | 2D | R1S0 | 0.979 | 0.997 | 0.864 | 0.908 |
| R1S1 | ST | R1S1 | 0.878 | 0.924 | 0.837 | 0.794 |

## Rebuild

```bash
python3 rebuild_fig11_paper_rs_rebucket16.py --analysis-dir <final-analysis-dir>
```
