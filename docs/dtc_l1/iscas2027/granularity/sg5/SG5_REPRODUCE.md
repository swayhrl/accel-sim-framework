# SG5 design-gate reproduction

```sh
python3 util/dtc_l1/validate_sg5_design.py \
  --core-repo /workspace/repos/gpgpu-sim_distribution
```

This command checks only frozen Core95 source anchors.  It does not build or
run a simulator.  Runtime fixtures, equivalence, and G6 remain forbidden until
the host admission gate is truly met and an isolated observer Core descendant
can be created without touching a frozen Core/runtime.
