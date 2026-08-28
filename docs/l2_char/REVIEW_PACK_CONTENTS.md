# `review_pack.tar.gz` contents

The generated closeout archive is self-contained review evidence, not a
source-distribution tarball.  It contains:

- `core_patches/`: the split semantic patch series from official core baseline
  `03c1fe44`.
- `framework_patches/`: framework and documentation patches after framework
  baseline `3016c658`.
- `evidence/t1_t15.log`: the production-predicate regression result.
- `evidence/integrated_pressure/`: P1--P6 terminal logs, resolved overlays,
  SHA-256 trace manifests, and `summary.tsv`.
- `fixtures/`: the small external directed trace fixtures referenced by the
  harness, so every P case can be replayed without another worktree.
- `docs/`: corrected-baseline contract, provenance, postchecks, closeout, and
  this manifest.
- `source/`: the exact core regression and framework pressure harness source,
  including the local P5 writeback fixture.
- `metadata/`: immutable core/framework commit IDs, commit logs, and the
  commands used to build and run the evidence.

The archive intentionally excludes simulator build products and all large
workload traces.
