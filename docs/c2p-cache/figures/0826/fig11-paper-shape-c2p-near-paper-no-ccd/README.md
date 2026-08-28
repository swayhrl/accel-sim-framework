# Fig. 11 paper-shape / local-average / no-CCD note

> **Non-evidentiary 0826 visual sensitivity.** This chart is a synthetic
> construction, not simulation output. It begins by preserving each visible
> design's measured local group average while imposing the displayed paper
> Fig. 11 workload ordering and above/below-baseline direction. CCD is
> deliberately omitted from rendering only.

## Construction

For a paper displayed value `p`, local measured group mean `m`, and
paper subset mean `p_bar`, the rendered value is:

`1 + ((m - 1) / (p_bar - 1)) * (p - 1)`.

Thus each rendered group/design arithmetic mean is exactly its measured
local mean before any explicit C2P-only factor. The local measurements
come from `/workspace/worktrees/accel-sim-c2p-cache/hw_run/c2p-paper16-analysis-final-v7-20260821/paper16_modes.csv`.
The paper values in `paper_displayed_shape_reference.csv` are approximate
bar-height reconstructions from the publisher PDF, not raw paper data.

## Requested post-shape C2P factors

| Paper group | C2P multiplier |
|---|---:|
| R1S0 | 0.7359 |
| R1S1 | 0.8657 |

## Measured versus rendered averages

| Paper R/S group | Workloads | ATA measured/rendered | RING measured/rendered | 本结构 measured/rendered | CCD measured (hidden) |
|---|---|---:|---:|---:|---:|
| R1S0 | CU, HO, GA | 0.926 / 0.926 | 0.782 / 0.782 | 0.798 / 0.587 | 0.935 |
| R1S1 | LU, SG, 3M, GE, B+, 2D, ST | 0.944 / 0.944 | 0.912 / 0.912 | 0.887 / 0.768 | 0.975 |

## Paper-reported C2P average contrast

| Paper group | Paper reported C2P average | Local measured subset | Rendered C2P average | Rendered - paper |
|---|---:|---:|---:|---:|
| R1S0 | 0.534 | 0.798 | 0.587 | +0.053 |
| R1S1 | 0.698 | 0.887 | 0.768 | +0.070 |

## Shape-scale audit

| Paper group | Design | Paper subset mean | Local measured mean | Alpha |
|---|---|---:|---:|---:|
| R1S0 | ata | 0.625 | 0.926 | 0.196 |
| R1S0 | ring | 0.573 | 0.782 | 0.511 |
| R1S0 | c2p | 0.453 | 0.798 | 0.370 |
| R1S1 | ata | 0.870 | 0.944 | 0.435 |
| R1S1 | ring | 0.856 | 0.912 | 0.610 |
| R1S1 | c2p | 0.685 | 0.887 | 0.360 |

## Rebuild

```bash
python3 rebuild_fig11_paper_shape_local_avg_no_ccd.py --analysis-dir <final-analysis-dir>
```
