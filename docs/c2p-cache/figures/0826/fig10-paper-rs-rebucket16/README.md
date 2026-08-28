# Fig. 10 paper-R/S rebucketed local-16 note

> **Non-evidentiary 0826 diagnostic.** The plot rebuckets existing local
> Fig. 10 values by the paper's R/S labels. It is not a new experiment,
> a formal paper figure, or a basis for a performance claim.

## Local group averages after paper-R/S rebucketing

| Paper R/S group | Workloads | ATA | CCD | RING | 本文提到的结构 |
|---|---|---:|---:|---:|---:|
| R0S0 | MR, NN, DW | 0.998 | 1.001 | 0.756 | 1.004 |
| R1S0 | CU, HO, GA | 1.000 | 1.000 | 0.794 | 1.003 |
| R0S1 | AT, BI, GS | 0.962 | 1.016 | 0.851 | 0.982 |
| R1S1 | LU, SG, 3M, GE, B+, 2D, ST | 1.004 | 1.000 | 0.657 | 1.026 |

## C2P group-average contrast with the paper vector

This comparison uses the same local-16 subset in both columns. The
paper column is decoded from displayed Fig. 10 vector geometry, not
from author-provided raw data.

| Paper R/S group | Paper displayed C2P | Local C2P | Local - paper |
|---|---:|---:|---:|
| R0S0 | 1.009 | 1.004 | -0.005 |
| R1S0 | 1.034 | 1.003 | -0.031 |
| R0S1 | 0.968 | 0.982 | +0.014 |
| R1S1 | 1.263 | 1.026 | -0.236 |

## Classification differences

| Workload | Paper group | Local 64KiB group | R | S = IPC(50)/IPC(200) |
|---|---|---|---:|---:|
| GA | R1S0 | R0S0 | 0.079 | 1.070 |
| LU | R1S1 | R0S0 | 0.252 | 1.041 |
| SG | R1S1 | R1S0 | 0.410 | 1.084 |
| 3M | R1S1 | R1S0 | 0.357 | 1.037 |
| GE | R1S1 | R1S0 | 0.368 | 1.017 |
| 2D | R1S1 | R1S0 | 0.339 | 1.082 |

## Paper-figure vector comparison (C2P bar only)

The following is a direct extraction of displayed bar geometry from the
publisher vector Fig. 10, rounded to 0.001. It is suitable for locating
large visual deltas, but is **not** the authors' raw dataset.

| Workload | Paper displayed C2P | Local C2P | Local - paper | Observation |
|---|---:|---:|---:|---|
| MR | 1.003 | 1.000 | -0.003 | close |
| NN | 1.001 | 0.999 | -0.002 | close |
| DW | 1.025 | 1.014 | -0.011 | close |
| CU | 1.023 | 1.001 | -0.023 | close |
| HO | 1.005 | 1.008 | +0.003 | close |
| GA | 1.074 | 1.000 | -0.074 | close |
| AT | 0.998 | 0.980 | -0.019 | close |
| BI | 0.978 | 0.987 | +0.010 | close |
| GS | 0.928 | 0.978 | +0.050 | close |
| LU | 1.134 | 1.002 | -0.133 | large |
| SG | 1.412 | 0.995 | -0.417 | large |
| 3M | 1.163 | 1.024 | -0.140 | large |
| GE | 1.498 | 1.009 | -0.489 | large |
| B+ | 1.197 | 1.010 | -0.187 | large |
| 2D | 1.350 | 0.980 | -0.370 | large |
| ST | 1.085 | 1.164 | +0.079 | close |

## Interpretation

- The largest negative local-vs-paper C2P gaps are `GE`, `SG`, `2D`,
  `B+`, `LU`, and `3M`; these are also the main reason the local data
  does not reproduce the paper's strong R1S1 aggregate benefit.
- `LU` crosses both local R and S thresholds, while `GA` loses the R1
  label. `SG`, `3M`, `GE`, and `2D` retain R1 locally but fall below
  the S1 threshold. `SG` and `2D` are near the 1.10 S threshold; `3M`
  and `GE` are materially below it.
- `ST` is the one clear inverse case: local C2P is above the displayed
  paper C2P bar. Therefore the mismatch is not a uniform scale factor;
  it is workload-dependent and should be traced to configuration, trace
  shape, and protocol-model differences before drawing any conclusion.

## Rebuild

The figure is rebuilt from the reviewed local Fig. 10 SVG and the
local Fig. 3 point table. Supply an SVG exported from the publisher's
Fig. 10 PDF only when regenerating the diagnostic comparison table:

```bash
env -u PYTHONHOME -u PYTHONPATH -u PYTHONNOUSERSITE /usr/bin/python3 \
  rebuild_fig10_paper_rs_rebucket16.py --paper-svg path/to/ipc.svg \
  --r1s1-mismatch-c2p-uplift 0.00
```
