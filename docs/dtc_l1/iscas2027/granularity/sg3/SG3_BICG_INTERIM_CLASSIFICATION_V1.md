# SG3 BICG interim downstream classification (V1)

This classification is limited to the accepted BICG IO/OO coarse screen in
`SG3_EXECUTION_DATA_SNAPSHOT_V4.tsv`; it is not generalized to GESUMMV,
Btree, or 2DConvolution.

- **Strong DTC injection sensitivity / oversubscription.** Reducing DTC cap
  to 512 improves IO from 93,942,704 to 24,422,555 cycles and OO from
  47,231,655 to 18,938,635 cycles.
- **Secondary L2-capacity sensitivity.** The 0.5x/2x capacity perturbations
  move both modes, but the cap=512 positive signal is substantially larger.
- **No material benefit from 4x L2 MSHR.** Relative to base, IO at 4x is
  94,837,064 cycles and OO is 46,808,797 cycles, insufficient to support an
  MSHR-expansion mechanism claim.

The Btree/2D cap=512 positive controls and the independently retried GESUMMV
baselines remain necessary before any cross-workload bounded conclusion.
