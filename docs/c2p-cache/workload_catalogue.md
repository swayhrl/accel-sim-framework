# C2P-Cache workload catalogue

This catalogue records the **retained trace**, semantic role and practical
replay cost for C2P work.  It deliberately separates complete comparison
evidence from a workload that merely has a trace or an early diagnostic point.
Wall time is a historical single-process host measurement, not a simulator
performance metric; it changes by mode, trace, filesystem cache and host load.

The canonical inventory is `configs/c2p-cache/paper16_workloads.tsv`.  The
main closeout contract is seven modes
`baseline/oracle/ideal/c2p/ata/ccd/ring`, a separate 50-cycle-L2 sensitivity
baseline, C2P m/k points and a fresh-training CCD replay.

## Retained paper16 inventory

| Workload | Suite, retained input | Program meaning / expected traffic character | Historical C2P-like point | Evidence state |
|---|---|---|---:|---|
| `btree` | Rodinia 3.1, B+ tree file+command | Tree index traversal: pointer chasing and irregular reads; a high peer-sharing/target-pressure case. | **8–14 min**, ~**0.41 GiB** RSS (policy and adaptive points). | Full seven-mode/L2-50/fresh-CCD evidence; primary positive C2P case. |
| `dwt2d` | Rodinia 3.1, 1024×1024 | 2-D discrete wavelet transform; tiled image transform with multi-stage locality. | No comparable host profile retained. | Full evidence; modest positive remote-sharing case. |
| `gaussian` | Rodinia 3.1, s=256 | Dense Gaussian elimination; row updates and pivoting. | **19–21 min**, ~**0.38 GiB** RSS. | Full evidence; local zero/near-zero-opportunity control. |
| `hotspot1` | Rodinia 3.1, 1024×1024, 2 iterations | Thermal stencil simulation; regular grid neighbourhood traffic. | No comparable host profile retained. | Full evidence. |
| `lud` | Rodinia 3.1, matrix-512 | Dense LU decomposition; block/row-column updates. | No comparable host profile retained. | Full evidence; remote reuse exists but retained result is near neutral. |
| `nn` | Rodinia 3.1, filelist-4 | Nearest-neighbour search over geo records; short irregular query workload. | **3–4 s**, ~**0.37 GiB** RSS. | Full evidence; strict no-sharing negative control. |
| `cutcp` | Parboil, watbox-sl40 full trace | Coulombic potential calculation over a spatial box; regular/irregular particle-grid access mix. | No comparable host profile retained. | Full evidence. |
| `mri-q` | Parboil, 32×32×32 full trace | MRI-Q reconstruction; many independent voxel/sample computations. | No comparable host profile retained. | Full evidence; retained R0/provisional `mri` point. |
| `sgemm` | Parboil, medium full trace | Single-precision dense GEMM. | **19–22 min**, ~**7.8 GiB** RSS. | Full evidence; key outlier—C2P reduces L2 accesses but finite target/FIFO costs can still slow IPC. |
| `stencil` | Parboil, 128×128×32 full trace | 3-D stencil / iterative grid update. | No comparable host profile retained. | Full evidence. |
| `2DConvolution` | PolyBench, `NO_ARGS` | Dense 2-D convolution; regular sliding-window accesses. | **34–46 min**, ~**0.35 GiB** RSS (policy/adaptive points); trace ~802 MiB. | Full evidence; important policy-sensitive case. |
| `3mm` | PolyBench, `NO_ARGS` | Three chained matrix multiplications; dense intermediate reuse. | No reliable completed point. | Has trace, but the seven-mode contract still has missing items; exclude from aggregate. |
| `atax` | PolyBench, `NO_ARGS` | Matrix transpose times vector; streaming matrix and vector reuse. | No reliable completed point. | Has trace, incomplete contract; exclude from aggregate. |
| `bicg` | PolyBench, `NO_ARGS` | Bi-conjugate gradient kernels (`Aq` and `Aᵀp`); streaming matrix-vector traffic. | No reliable completed point. | Has trace, incomplete contract; exclude from aggregate. |
| `gemm` | PolyBench, `NO_ARGS` | Dense matrix multiply. | No comparable host profile retained. | Full evidence; different executable/trace from Parboil `sgemm`. |
| `gesummv` | PolyBench, `NO_ARGS` | Sum of two matrix-vector products; streaming matrix/vector reads. | No reliable completed point. | Has trace, incomplete contract; exclude from aggregate. |

As of the retained audit, **12/16** workloads have the complete seven-mode,
L2-50 and fresh-CCD evidence: Btree, DWT2D, Gaussian, Hotspot1, LUD, NN,
CUTCP, MRI-Q, SGEMM, Stencil, 2DConvolution and GEMM.  `3mm`, `atax`, `bicg`
and `gesummv` must remain outside any aggregate until their missing contract
points are rerun.  Historical Ring points with the old queue-full bypass
semantics are likewise not closeout evidence; the backpressure-corrected Ring
root is required.

## Supplemental C2P+ diagnostic workloads

These are valuable mechanism discriminators but are **not replacements** for
the paper16 set.

| Workload | Source | Semantic purpose | Historical time / RSS | Correct use |
|---|---|---|---:|---|
| ISPASS `BFS` | V100 ISPASS trace | Broad graph-frontier sharing and high candidate pressure. | No stable host profile retained. | Distinguishes candidate quality and target-side FIFO/port contention from Btree-specific behaviour. |
| ISPASS `LPS` | V100 ISPASS trace | Low candidate-count case; useful protocol-overhead counterexample. | **91–146 s**, ~**0.69–0.72 GiB** RSS; trace 0.51 MiB. | Fast smoke/negative-control family; C2P may find peers yet not improve IPC. |
| ISPASS `RAY` | V100 ISPASS trace | Ray-tracing style traversal. | No stable host profile retained. | Compatibility/no-sharing control in available result. |
| ISPASS `LIB` | V100 ISPASS trace | Library-style workload retained by ISPASS archive. | No stable host profile retained. | Compatibility/no-sharing control in available result. |
| `fw_block` | Pannotia | Blocked Floyd–Warshall all-pairs shortest paths; repeated dense dynamic-programming updates. | No stable host profile retained. | Supplementary graph/DP locality case. |

## Scheduling and reporting guidance

- A single `nn` point is ideal for strict regression and invariant checks.
- Use **Btree + ISPASS BFS/LPS** to expose candidate pruning, remote reuse and
  target-port pressure; neither alone establishes generality.
- Use **SGEMM + 2DConvolution** for the important counterexample: lower L2
  traffic is insufficient if the peer discovery/target path adds critical
  delay.  SGEMM requires roughly 8 GiB RSS; reserve it as a high-memory job.
- Use `gaussian` and `mri-q` as clean low/no-opportunity controls.  A change in
  their C2P counters or timing is a reason to inspect the mechanism before
  scaling up.
- Do not call a workload a paper result merely because a trace exists.  Keep
  the qualified 12-workload set, supplemental ISPASS/Pannotia tests and
  incomplete four-workload tail separate in tables and geomeans.

## Sources and limits

The suite/input mapping comes from `configs/c2p-cache/paper16_workloads.tsv`.
The qualification boundary and result caveats are maintained in
`docs/c2p-cache/current_mechanism_and_experiment_audit_2026-08-21.md` and
`docs/c2p-cache/validation_results.md`.  Exact `host_profile.txt` records and
the resource collection protocol are described in
`docs/c2p-cache/experiment_runtime_planning.md`.

The recorded times are deliberately rounded to useful planning ranges and
identify the measured policy/adaptive point where relevant.  They are not
comparable across different configurations and must never be used in place of
simulated cycle/IPC results.
