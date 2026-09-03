# M5 Extended-20 Selection Report

## Decision

This is a pre-performance, selection-only proposal for **20** supplemental GPU-compute workloads and **5 ranked alternates**.  It is intentionally separate from the Paper-10 M5 campaign and authorizes **no** Base/IO/OO runs.

## Authoritative local evidence and reconciliation

The authoritative local population is exactly 52 `(suite, workload, retained input)` entries in `/workspace/worktrees/accel-sim-decoupled-l2/docs/decoupled_l2_workload_roster_under_5h.md` (SHA-256 `4def39e4426e7a3ed912bc88ff0b8f4f15f19db4ab84b9450809233dce23f1ca`, commit `d3c41ad839afe37300e3054e8f80500140e790b4`).  Its 52/52 machine-readable reconciliation is `/workspace/worktrees/accel-sim-ep-l2-l1-causality/docs/l2_char_v1/ROUND1_WAVE1_COST_ROSTER.tsv` (SHA-256 `335348e84edce46f9bf5f8a54e2edd4d4302f09f8e3f75382e3e4629aefbac98`, commit `286e9fc09cd8898a6e8137669194ab3ac1182677`).

The roster records prior successful/full evidence where stated, plus bounded and V100-special cohorts.  It is not an M5 result registry and no active M5 worktree or GPGPU-Sim Core file was read or changed for selection.  The inventory preserves all 52 and distinguishes the 6 microbenchmarks, one trimmed derivation, five bounded-only items, five V100-special rehydration cases, and six direct Paper-10 algorithm duplicates.

`input_hash` is the frozen `kernelslist.g` SHA-256 and notes contain the reconciled trace-tree SHA-256.  This is adequate prior-run identity evidence, but not a substitute for the later M5 source/binary/input hash lock; that re-freeze is a launch precondition.

## Selected portfolio

The selected table is `EXTENDED20_SELECTED.tsv`.  Suite counts: {'CUDA SDK': 8, 'Rodinia': 5, 'Parboil': 6, 'PolyBench': 1}.  Domain counts: {'MONTE_CARLO_STATISTICAL': 1, 'IMAGE_SIGNAL_PROCESSING': 5, 'SEARCH_SORT_SCAN_REDUCTION': 5, 'DENSE_LINEAR_ALGEBRA': 3, 'OTHER_SOURCE_BACKED_COMPUTE': 2, 'STENCIL_STRUCTURED_GRID': 2, 'GRAPH_TRAVERSAL': 1, 'PARTICLE_PHYSICS_NBODY': 1}.  Cost counts: {'COST_Q1': 7, 'COST_Q3': 3, 'COST_Q2': 4, 'COST_Q4': 4, 'COST_UNKNOWN_OR_BOUNDED': 2}.  Cost tiers are empirical over the 39 rows with recorded numeric historical time: Q1 <=7m, Q2 <=20m, Q3 <=66m, Q4 >66m; unknown/bounded remains non-quartiled.  The selection has four Q4 items (scan, cutcp, histo, 3mm), and ten Q1/Q2 items.

## Eligibility and duplicate handling

Paper-10 direct duplicates excluded: PolyBench atax, bicg, mvt, gesummv, 2DConvolution; Parboil spmv.  The mapping follows `M5_COMPUTE_WORKLOAD_MANIFEST.md`: Paper-10 also includes gemver/gemv, syrk, syr2k, 2mm and conv2d, none of which is silently substituted here.  Same-family variants are not co-selected: one vectorAdd, one scalarProd, one fastWalshTransform and one BFS implementation.  The full per-row gate/disposition evidence is in the inventory and not-selected table.

For every selected row, the inventory records: E1 compute application; E2 suite/app/version plus historical trace-runner path; E3 retained input plus frozen trace-list and trace-tree identity; E4 historical full/natural-drain completion evidence; E5 nontrivial work amount; E6 Paper-10 non-duplicate; E7 portfolio dedup; E8 prior GPGPU-Sim natural-drain fidelity.  The later M5 source/input/PTX re-freeze is a reproducibility lock for a new formal campaign, not a relaxed replacement for these gates.

## P1-P6 check

| Constraint | Result |
| --- | --- |
| P1 suites | PASS: CUDA SDK 8, Rodinia 5, Parboil 6, PolyBench 1; four suites and none >10. |
| P2 domains | PASS: 8 primary classes; maximum image/signal count is 5. |
| P3 access/operation coverage | PASS: irregular/graph >=3 (cfd, btree, BFS); structured/streaming >=3; reuse-heavy >=3; update-heavy >=2 (histo, scan/BFS/hotspot); compute-heavy controls >=2 (BlackScholes, Gaussian/3mm); reduction/sort/scan >=3. |
| P4 Base/source pressure | PASS target: 7 high (cfd, btree, BFS, cutcp, histo, mri-q, scan), 7 medium/mixed, 6 low/compute controls.  Tags are source/static only. |
| P5 cost | PASS: Q4=4; Q1+Q2=11.  Two unknown-cost selections are retained for unique domain/access coverage. |
| P6 no speedup cherry-picking | PASS: no PAPER_IO/PAPER_OO/DTC cycles, speedup, miss gain, or DTC-benefit field was opened or used. |

## Adversarial self-review (S4)

1. No suite dominates; CUDA SDK has 8/20, below 50%.
2. Same-family crowding was removed (parameter variants and duplicate BFS/GEMM/stencil families are alternates or excluded).
3. Long/irregular cases remain (scan, cutcp, histo, stencil, cfd, btree, BFS); runtime convenience did not remove them.
4. Selection data contains no DTC performance value.  The score is coverage/provenance/correctness/Base-source-interest/runtime/suite only.
5. Both plausible memory-pressure cases and low-pressure/compute controls are present by source inference, not observed benefit.
6. Load-dominant, balanced read/write, store-heavy and atomic-present/heavy operations are represented.
7. Common pool members are either selected, a ranked alternate, a Paper-10 duplicate, a near-duplicate, microbenchmark, bounded-only, or rehydration-incomplete; each has a stated reason.
8. The resulting set is therefore auditable as a broad portfolio rather than a DTC-speedup-cherry-picked list.

## Remaining launch gates / do not infer

Before any later M5 formal runner is authorized, freeze the exact selected source revision, CUDA wrapper/build command, binary/PTX SHA-256, canonical input byte SHA-256, output checker/reference hash, and M5 formal config/parser identity.  Do not reuse an L2 trace result as an M5 DTC result; do not substitute an alternate without rerunning P1-P6; do not launch the 60 runs from this branch.
