# SG0 source audit reproduction

This is a read-only, simulation-free audit:

```sh
python3 util/dtc_l1/validate_sg0_static.py \
  --core-repo /workspace/repos/gpgpu-sim_distribution
```

The Chapter-4 primary source is pinned in `SG0_DISSERTATION_PROVENANCE.tsv`.
Its direct-review anchors are machine-checked without inferring a transaction
rule from the word “cacheline”:

```sh
python3 util/dtc_l1/validate_sg0_dissertation.py \
  --pdf '/workspace/worktrees/accel-sim-decoupled-l2/docs/reference/赵皓宇 博士论文.pdf'
```

The direct result is that Chapter 4 specifies duplicate-miss behavior and a
128-B cacheline context, but does **not** specify whole-line or sector lower
transactions. The local RTL audit remains separate and is not used to fill
that primary-source gap.
