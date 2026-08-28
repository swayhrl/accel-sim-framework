# Fig. 10 paper-R/S rebucketed local-16 note

> **Non-evidentiary 0826 diagnostic.** The plot rebuckets existing local
> Fig. 10 values by the paper's R/S labels. It is not a new experiment,
> a formal paper figure, or a basis for a performance claim.

## What-if transformation

Only the C2P/`本文提到的结构` bar is multiplied by `1.10` (+10%) for `LU, SG, 3M, GE, 2D`. ATA, CCD, RING, `B+`, and `ST` remain unchanged. This is a visual sensitivity scenario, not new simulation data.

## Local group averages after paper-R/S rebucketing

| Paper R/S group | Workloads | ATA | CCD | RING | 本文提到的结构 |
|---|---|---:|---:|---:|---:|
| R0S0 | MR, NN, DW | 0.998 | 1.001 | 0.756 | 1.004 |
| R1S0 | CU, HO, GA | 1.000 | 1.000 | 0.794 | 1.003 |
| R0S1 | AT, BI, GS | 0.962 | 1.016 | 0.851 | 0.982 |
| R1S1 | LU, SG, 3M, GE, B+, 2D, ST | 1.004 | 1.000 | 0.657 | 1.098 |

## C2P group-average contrast with the paper vector

This comparison uses the same local-16 subset in both columns. The
paper column is decoded from displayed Fig. 10 vector geometry, not
from author-provided raw data.

| Paper R/S group | Paper displayed C2P | Local C2P | Local - paper |
|---|---:|---:|---:|
| R0S0 | 1.009 | 1.004 | -0.005 |
| R1S0 | 1.034 | 1.003 | -0.031 |
| R0S1 | 0.968 | 0.982 | +0.014 |
| R1S1 | 1.263 | 1.098 | -0.165 |

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
| LU | 1.134 | 1.102 | -0.033 | close |
| SG | 1.412 | 1.094 | -0.317 | large |
| 3M | 1.163 | 1.126 | -0.037 | close |
| GE | 1.498 | 1.110 | -0.388 | large |
| B+ | 1.197 | 1.010 | -0.187 | large |
| 2D | 1.350 | 1.078 | -0.272 | large |
| ST | 1.085 | 1.164 | +0.079 | close |

## Interpretation

- The +10% scenario narrows the local-16 R1S1 C2P gap from `-0.236`
  to `-0.165`, but it does not reproduce the paper R1S1 aggregate.
  `GE`, `SG`, `2D`, and unchanged `B+` remain the largest deficits.
- This isolates a useful target: a uniform gain on the five locally
  reclassified cases helps, but cannot explain the whole paper/local
  difference. Workload-specific opportunity/protocol effects still dominate.
- The R/S classification rows remain measurements from the original local
  campaign; this hypothetical bar scaling does not reclassify any workload.

## Rebuild

The figure is rebuilt from the reviewed local Fig. 10 SVG and the
local Fig. 3 point table. Supply an SVG exported from the publisher's
Fig. 10 PDF only when regenerating the diagnostic comparison table:

```bash
env -u PYTHONHOME -u PYTHONPATH -u PYTHONNOUSERSITE /usr/bin/python3 \
  rebuild_fig10_paper_rs_rebucket16.py --paper-svg path/to/ipc.svg \
  --r1s1-mismatch-c2p-uplift 0.10
```
