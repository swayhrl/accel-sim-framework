# C2P-Cache paper16 directional reproduction

## Scope and acceptance

This report evaluates the canonical local 16 complete replay traces; it is not a claim of cycle-identical reproduction of unpublished author traces or address hashes.  All numbers below are derived from `paper16_cases.csv` and `paper16_modes.csv`.

## Local workload classification

| Group | Cases |
|---|---|
| R0S0 | DW, GA, LU, NN, MR |
| R1S0 | HO, CU, SG, 2D, 3M, GE |
| R0S1 | AT, BI, GS |
| R1S1 | B+, ST |

## Paper group reference versus local reclassification

The Figure-10 group is retained as a paper reference only. The local group always comes from this campaign's independent oracle-redundancy and 50-cycle-L2 measurements; a mismatch is trace/input evidence, not a relabeling of the paper.

| Case | Paper label | Paper group | Local group | Local redundancy | Local L2 sensitivity |
|---|---|---|---|---:|---:|
| btree | B+ | R1S1 | R1S1 | 0.434 | 1.130 |
| dwt2d | DW | R0S0 | R0S0 | 0.091 | 1.045 |
| gaussian | GA | R1S0 | R0S0 | 0.079 | 1.070 |
| hotspot1 | HO | R1S0 | R1S0 | 0.300 | 1.004 |
| lud | LU | R1S1 | R0S0 | 0.252 | 1.041 |
| nn | NN | R0S0 | R0S0 | 0.000 | 1.044 |
| cutcp | CU | R1S0 | R1S0 | 0.913 | 1.014 |
| mri-q | MR | R0S0 | R0S0 | 0.000 | 1.003 |
| sgemm | SG | R1S1 | R1S0 | 0.410 | 1.084 |
| stencil | ST | R1S1 | R1S1 | 0.332 | 1.844 |
| 2DConvolution | 2D | R1S1 | R1S0 | 0.339 | 1.082 |
| 3mm | 3M | R1S1 | R1S0 | 0.357 | 1.037 |
| atax | AT | R0S1 | R0S1 | 0.002 | 1.249 |
| bicg | BI | R0S1 | R0S1 | 0.002 | 1.367 |
| gemm | GE | R1S1 | R1S0 | 0.368 | 1.017 |
| gesummv | GS | R0S1 | R0S1 | 0.002 | 1.270 |

## Figure-10-style normalized IPC aggregate

Arithmetic mean across locally complete seven-mode cases in each group; not a replacement for the paper's original workload-weighted set.

| Group | Baseline | ATA | CCD | RING | C2P-Cache |
|---|---:|---:|---:|---:|---:|
| R0S0 | 1.000 | 0.997 | 1.002 | 0.423 | 1.007 |
| R1S0 | 1.000 | 1.005 | 1.000 | 0.197 | 1.007 |
| R0S1 | 1.000 | 0.906 | 1.041 | 0.629 | 0.954 |
| R1S1 | 1.000 | 1.018 | 1.001 | 0.162 | 1.218 |

## Figure-11-style normalized L2 access aggregate

| Group | Baseline | ATA | CCD | RING | C2P-Cache |
|---|---:|---:|---:|---:|---:|
| R0S0 | 1.000 | 0.989 | 0.994 | 0.970 | 0.981 |
| R1S0 | 1.000 | 0.933 | 0.961 | 0.866 | 0.831 |
| R0S1 | 1.000 | 0.999 | 0.999 | 0.997 | 0.997 |
| R1S1 | 1.000 | 0.912 | 0.941 | 0.831 | 0.840 |

## Remote-opportunity retention diagnostic

The oracle measures a peer opportunity when a miss is accepted. The two retention columns show how much survives later exact probing; timeout is the fraction of accepted peer requests that fall back because a target-L1 probe remained blocked. This is a diagnostic for model/queue contention, not a paper performance metric.

| Group | Exact ideal retains oracle opportunity | C2P retains oracle opportunity | Ideal target-timeout rate | C2P target-timeout rate |
|---|---:|---:|---:|---:|
| R0S0 | 0.499 | 0.400 | 0.045 | 0.077 |
| R1S0 | 0.607 | 0.445 | 0.157 | 0.320 |
| R0S1 | 1.740 | 1.520 | 0.000 | 0.000 |
| R1S1 | 0.680 | 0.641 | 0.136 | 0.187 |

## Paper target versus local directional evidence

- paper target (R1S1): C2P IPC +23.5% average (up to +49.7%).
- paper target (R0S1): C2P about -2.0%; ATA -31.7%; RING -19.3%; CCD +0.4%.
- paper target (R1S0/R1S1): C2P normalized L2 access 53.4% / 69.8%.

- consistent: R1S1 C2P has positive IPC direction (observed 1.218)
- consistent: R0S1 C2P remains near neutral (observed 0.954)
- consistent: R0S1 ATA exposes sharing overhead (observed 0.906)
- consistent: R0S1 RING exposes sharing overhead (observed 0.629)
- consistent: R1S1 C2P reduces L2 accesses (observed 0.840)
- consistent: R1S0 C2P reduces L2 accesses (observed 0.831)

## Counter-direction outliers requiring explanation

Rows below are not silently averaged away: they reduce L2 access but slow down. The displayed C2P queue, candidate, false-positive, and target-timeout rates are evidence for diagnosis, not automatic proof of a single root cause.

| Case | Local group | C2P IPC | C2P L2 access | Candidates/query | Query bypass rate | Target-timeout rate | Snapshot FP rate |
|---|---|---:|---:|---:|---:|---:|---:|
| sgemm | R1S0 | 0.987 | 0.805 | 4.054 | 0.009 | 0.338 | 0.148 |
| 2DConvolution | R1S0 | 0.951 | 0.908 | 1.922 | 0.028 | 0.425 | 0.458 |

## Mechanism and provenance gates

- `analyze_c2p_paper16.py --strict` requires every seven-mode bundle and every 50-cycle baseline, oracle timing invariance, and one avoided L2 request per remote hit.
- Figure 12 uses independent CCD and C2P tag-time TP/FN/FP/TN classification.  Figure 13 is a distinct measured m/k sweep, not an interpolation of the default point.
- Figure 14 is built from the dynamic peer-access histograms, split into completed remote-hit and miss/fallback paths.

## Default C2P binary-equivalence audit

The parameterized Snapshot Matrix must preserve the default 5,120-row/four-encoding C2P point before pre-parameterization replays can enter this aggregate. The strict closeout requires a paired, field-by-field equivalence result for every local case.

- audit rows: 16; equivalent cases: 16.
- audit artifact: present.

## Rendered artifacts

- fig10_normalized_ipc: pdf, svg, png
- fig11_l2_access: pdf, svg, png
- fig12_filtering_accuracy: pdf, svg, png
- fig13_ipc_vs_fp_ratio: pdf, svg, png
- fig14_peer_probe_distribution: pdf, svg, png
- figure-style audit: present

## Separate V100 extension set

The ISPASS (BFS, LIB, LPS, RAY) and Pannotia (color_max, fw_block, mis, pagerank) traces are now available as a V100-generated extension set. They are deliberately excluded from this canonical 16-workload aggregate: their trace capture, inputs, hashes, compatibility, uncapped baseline, seven-mode, and L2=50 evidence are audited independently by the V100 extension closeout.
