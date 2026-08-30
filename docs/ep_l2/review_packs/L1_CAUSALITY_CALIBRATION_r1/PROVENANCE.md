# Provenance and Config Contract

## D256

- Framework: `hrl/ep-l2-l1-causality-v0` @ `dc30e67`.
- Core: `ece1a3a77c5628763e0a4605bfd1c639ee6a1495`.
- Formal base semantics: Framework `f08d2ce857972fad73c4e1ab7162ba94c6336507`.
- Result root: `/workspace/results/ep_l2_l1_causality_d256/`.

The frozen L1 geometry is 64 KiB, 4 sets, 128 ways, 128-B lines and
20-cycle latency. META-HR changes only MSHR `512→1024`, merge `8→32`, and
MissQ `16→64`; BANK-HR changes only banks `4→8`.

## D512 candidate and descendants

- Lane-B Core: `878f80869ce212e779df20b6421e4dc7f987825d`.
- Lane-B Framework: `aae62b66685f15437cecf0193934f628e6fac6ae`.
- Isolated Lane-C Framework descendant: `hrl/ep-l2-l1-causality-d512-v0`
  @ `8e9693c71df072004089b2ac483313fa08f36158`.
- Isolated Lane-C Core: exact candidate `878f80869ce212e779df20b6421e4dc7f987825d`.
- Result root: `/workspace/results/ep_l2_l1_causality_d512_speculative/`.

The D512 base overlay SHA256 is
`492269014ee869f9023cc7ec4fb3ac8dd7da04bf96d34e2e55ffb74d040007b3`.
The D512 descendants add only the matching META-HR or BANK-HR delta above.
Lane A and Lane B active worktrees were not modified.

## Validation

The C7e D256 base reproduction was exact for vectorAdd_4M, spmv and FWT_7_21.
Release build, C3--C7 closeout, runner config audits, parser/invariant checks
and `git diff --check` passed. The analyzer default-D256 regression reproduced
its prior CSV output byte-for-byte after D512 layout support was added.

