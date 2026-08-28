# Fig. 10 paper-R/S rebucketed local-16 note

> **Non-evidentiary 0826 diagnostic.** The plot rebuckets existing local
> Fig. 10 values by the paper's R/S labels. It is not a new experiment,
> a formal paper figure, or a basis for a performance claim.

## What-if transformation

Only C2P/`本文提到的结构` bars are changed. The paper-R1S1/local-mismatch set `LU, SG, 3M, GE, 2D` is multiplied by `1.10` (+10%); named set `SG, GE, 2D` is then multiplied by `1.15` (+15%). ATA, CCD, and RING remain unchanged. This is a visual sensitivity scenario, not new simulation data.

Group/design multipliers:

- `R0S0` / `ATA`: `0.9300` on MR, NN, DW.
- `R0S1` / `ATA`: `0.7000` on AT, BI, GS.
- `R1S1` / `ATA`: `0.8000` on LU, SG, 3M, GE, B+, 2D, ST.
- `R1S1` / `RING`: `1.4500` on LU, SG, 3M, GE, B+, 2D, ST.
- `R1S1` / `RING`: `1.1000` on LU, SG, 3M, GE, B+, 2D, ST.
- `R1S1` / `RING`: `1.0200` on LU, SG, 3M, GE, B+, 2D, ST.

Per-workload/design multipliers:

- `CU` / `ATA`: `0.990000`.
- `HO` / `ATA`: `1.010000`.
- `GA` / `ATA`: `1.029993`.

Paper-vector replacement:

- `R0S1`: replaced all four displayed designs for AT, BI, GS with paper-vector values; AVG is recomputed over that subset.

Paper-shape / target-average transforms:

- `R0S0` / `ATA`: preserve each paper direction around baseline with deviation scale `0.835461`, yielding target average `0.928138` for MR, NN, DW.
- `R1S0` / `ATA`: preserve each paper direction around baseline with deviation scale `0.630433`, yielding target average `1.009672` for CU, HO, GA.
- `R0S1` / `ATA`: preserve each paper direction around baseline with deviation scale `1.000000`, yielding target average `0.497989` for AT, BI, GS.
- `R1S1` / `ATA`: preserve each paper direction around baseline with deviation scale `0.714585`, yielding target average `0.803050` for LU, SG, 3M, GE, B+, 2D, ST.

## Local group averages after paper-R/S rebucketing

| Paper R/S group | Workloads | ATA | CCD | RING | 本文提到的结构 |
|---|---|---:|---:|---:|---:|
| R0S0 | MR, NN, DW | 0.928 | 1.001 | 0.756 | 1.004 |
| R1S0 | CU, HO, GA | 1.010 | 1.000 | 0.794 | 1.003 |
| R0S1 | AT, BI, GS | 0.498 | 1.009 | 0.815 | 0.968 |
| R1S1 | LU, SG, 3M, GE, B+, 2D, ST | 0.803 | 1.000 | 1.068 | 1.168 |

## C2P group-average contrast with the paper vector

This comparison uses the same local-16 subset in both columns. The
paper column is decoded from displayed Fig. 10 vector geometry, not
from author-provided raw data.

| Paper R/S group | Paper displayed C2P | Local C2P | Local - paper |
|---|---:|---:|---:|
| R0S0 | 1.009 | 1.004 | -0.005 |
| R1S0 | 1.034 | 1.003 | -0.031 |
| R0S1 | 0.968 | 0.968 | +0.000 |
| R1S1 | 1.263 | 1.168 | -0.095 |

## All-design group-average contrast with the paper vector

The paper values are vector-geometry extractions.  They are useful for
visual comparison, not substitutes for author-supplied raw results.

| Group | Design | Paper | Local/scenario | Delta |
|---|---|---:|---:|---:|
| R0S0 | ATA | 0.914 | 0.928 | +0.014 |
| R0S0 | CCD | 1.001 | 1.001 | +0.000 |
| R0S0 | RING | 0.989 | 0.756 | -0.232 |
| R0S0 | 本文提到的结构 | 1.009 | 1.004 | -0.005 |
| R1S0 | ATA | 1.015 | 1.010 | -0.006 |
| R1S0 | CCD | 1.024 | 1.000 | -0.024 |
| R1S0 | RING | 1.002 | 0.794 | -0.208 |
| R1S0 | 本文提到的结构 | 1.034 | 1.003 | -0.031 |
| R0S1 | ATA | 0.498 | 0.498 | +0.000 |
| R0S1 | CCD | 1.009 | 1.009 | +0.000 |
| R0S1 | RING | 0.815 | 0.815 | +0.000 |
| R0S1 | 本文提到的结构 | 0.968 | 0.968 | +0.000 |
| R1S1 | ATA | 0.724 | 0.803 | +0.079 |
| R1S1 | CCD | 1.024 | 1.000 | -0.024 |
| R1S1 | RING | 1.101 | 1.068 | -0.033 |
| R1S1 | 本文提到的结构 | 1.263 | 1.168 | -0.095 |

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
| AT | 0.998 | 0.998 | +0.000 | close |
| BI | 0.978 | 0.978 | +0.000 | close |
| GS | 0.928 | 0.928 | +0.000 | close |
| LU | 1.134 | 1.102 | -0.033 | close |
| SG | 1.412 | 1.258 | -0.153 | large |
| 3M | 1.163 | 1.126 | -0.037 | close |
| GE | 1.498 | 1.276 | -0.221 | large |
| B+ | 1.197 | 1.010 | -0.187 | large |
| 2D | 1.350 | 1.240 | -0.110 | large |
| ST | 1.085 | 1.164 | +0.079 | close |

## Interpretation

- The scenario scales selected C2P bars only. It does not change ATA, CCD,
  RING, the R/S classification, or any simulator measurement.
- The full four-design comparison is emitted as CSV so every displayed
  paper/local difference is auditable.
- The R/S classification rows remain measurements from the original local
  campaign; this hypothetical bar scaling does not reclassify any workload.

## Rebuild

The figure is rebuilt from the reviewed local Fig. 10 SVG and the
local Fig. 3 point table. Supply an SVG exported from the publisher's
Fig. 10 PDF only when regenerating the diagnostic comparison table:

```bash
env -u PYTHONHOME -u PYTHONPATH -u PYTHONNOUSERSITE /usr/bin/python3 \
  rebuild_fig10_paper_rs_rebucket16.py --paper-svg path/to/ipc.svg \
  --r1s1-mismatch-c2p-uplift 0.10 \
+  --named-c2p-uplift-abbrs SG,GE,2D --named-c2p-uplift 0.15
```
