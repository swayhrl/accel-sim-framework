# M5 E0 — Extended-20 Selection Handoff

- **Status:** `M5_EXTENDED20_SELECTION_READY_FOR_REVIEW`
- **Branch:** `hrl/decoupled-l1-exp-m5-extended20-select-v0`
- **Scope:** selection metadata only; no Extended-20 Base/IO/OO formal run was launched.

## Proposal

Selected 20: CUDA SDK/BlackScholes, CUDA SDK/convolutionSeparable, CUDA SDK/fastWalshTransform_11_19, CUDA SDK/scalarProd_13920, CUDA SDK/scan, CUDA SDK/sortingNetworks, CUDA SDK/transpose, CUDA SDK/vectorAdd_6000000, Rodinia/cfd_097k, Rodinia/btree, Rodinia/dwt2d, Rodinia/gaussian, Rodinia/hotspot1, Parboil/bfs, Parboil/cutcp, Parboil/histo, Parboil/mri-q, Parboil/sad, Parboil/stencil, PolyBench/3mm.

Alternates in order: ALT01 Parboil/sgemm, ALT02 Rodinia/lud, ALT03 CUDA SDK/fastWalshTransform_7_21, ALT04 CUDA SDK/scalarProd_8192, ALT05 CUDA SDK/vectorAdd_4000000.

Read `extended20/EXTENDED20_SELECTED.tsv` for reasons/scores and `extended20/EXTENDED20_ALTERNATES.tsv` for substitution rules.

## Evidence anchors

* 52-row source of truth: Decoupled-L2 under-five-hour roster, commit `d3c41ad839afe37300e3054e8f80500140e790b4`, SHA-256 `4def39e4426e7a3ed912bc88ff0b8f4f15f19db4ab84b9450809233dce23f1ca`.
* 52/52 trace-asset reconciliation: Round1 cost roster, commit `286e9fc09cd8898a6e8137669194ab3ac1182677`, SHA-256 `335348e84edce46f9bf5f8a54e2edd4d4302f09f8e3e4629aefbac98`.
* Local source recovery anchor where available: `gpu-app-collection-decoupled-l2` commit `dad09cb0487845edc7524ded814c6cde9f0ef6a1`; existing GPGPU workload wrapper commit `de9cf4293f418877aa9cdb6a2395338ca06674a6`.
* The committed inventory gives exact trace-list and trace-tree hashes for every candidate.  It does **not** claim those are later M5 binary/input hashes.

## Paper-10 proof and guardrails

The direct Paper-10 algorithm duplicates are excluded in `EXTENDED20_NOT_SELECTED.tsv`: atax, bicg, mvt, gesummv, 2DConvolution/conv2d, and spmv.  No `PAPER_IO`, `PAPER_OO`, DTC speedup, DTC-benefit or DTC live-miss result was used for selection/ranking/tie-breaking.

## Required later formal-runner re-freeze

For each selected row, record source commit/path, wrapper, canonical input byte hash, output checker/reference hash, executable/PTX hash, launch geometry, M5 Core/Framework/config hash and parser schema.  Recheck E1-E8 and P1-P6 if source/input identity differs from this trace-anchored proposal.

## Do not redo / do not do here

Do not alter GPGPU-Sim Core, active M5 worktree, M5.0B/R5DV jobs, DTC semantics, or this portfolio based on DTC results.  Do not start the 60 Base/IO/OO formal runs until researcher review authorizes the formal track.
