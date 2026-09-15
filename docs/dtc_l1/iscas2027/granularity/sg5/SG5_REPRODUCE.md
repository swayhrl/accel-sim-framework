# SG5 design-gate reproduction

```sh
python3 util/dtc_l1/validate_sg5_design.py \
  --core-repo /workspace/repos/gpgpu-sim_distribution

python3 util/dtc_l1/validate_sg5_implementation.py \
  --observer-core /workspace/worktrees/gpgpu-sim-iscas2027-sg5-observer
```

These commands check frozen Core95 anchors and the dedicated observer source
placement only.  They do not build or run a simulator.  Runtime fixtures,
equivalence, and G6 remain forbidden until the host admission gate is truly
met.  The observer Core descendant is `afe978ea` on
`hrl/iscas2027-dtc-sg5-lower-traffic-v0`; no frozen Core/runtime is touched.
