# SG5 runtime-equivalence receipts

`SG5_EQUIVALENCE.tsv` is a compact index to sixteen immutable, natural-exit
attempts under `/workspace/wave-a-sg5-runs`. It records eight accepted SG5.3
pairs: B16-S NN/Btree, TC80-S NN/Btree, IO NN/Btree, and OO NN/Btree. The TC80-S
receipt binds the ordered `FAST64_BASE.config` plus frozen
`TC80_CAPACITY_MATCHED_OVERLAY.config` chain as one SHA-256 identity.

For each row, OFF has no `SG5_l1_lower_traffic_observer` output and ON emits
`SG5_l1_lower_traffic_observer = 1`.  The strict validator requires both
natural exit statuses to be zero, the same workload/variant/runtime/config/
trace identities, cycles and instructions, the complete pre-existing
scientific metric key set, and equal values for every such metric.  It passed
163 metrics for NN and 167 for Btree.

The validator deliberately excludes only six output fields which are
source-classified as host/debug reporting rather than architectural counters:
`Bank_Level_Parallism_Col`, `gpgpu_silicon_slowdown`,
`gpu_total_sim_rate`, `gpgpu_simulation_rate`,
`gpgpu_simulation_time`, and `n_ref`.  This is implemented in
`util/dtc_l1/sg5_equivalence.py`; every other numeric pre-existing output
metric participates in the equality check.  The immutable Btree runner is
the version with this classification (`581caa...`); the current runner adds
ordered multi-`-config` chain binding for future TC80 use (`085afaf2`) and
was regression-checked against the accepted NN pair.

The exact Btree check was:

```sh
python3 util/dtc_l1/sg5_equivalence.py validate \
  --off-dir /workspace/wave-a-sg5-runs/sg5_equivalence_B16-S_Btree_OFF_88d7a040-44d3-4b2c-bf05-c88fd2115cde \
  --on-dir /workspace/wave-a-sg5-runs/sg5_equivalence_B16-S_Btree_ON_0f9fc7ec-5be0-41ee-b594-9c0e23a07e23
```

The eight listed rows prove the frozen B16-S/TC80-S/IO/OO subset but do **not**
prove SG5.3 for every supported mode or authorize SG5.4. B16-N and TC80-N
remain gated on SG1 normal identities. No G6 observer row is represented by
this file.
