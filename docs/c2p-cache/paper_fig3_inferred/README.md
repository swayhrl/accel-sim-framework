# C2P paper Figure 3: inferred per-workload reference points

`paper_fig3_inferred_points.csv` is the project's fixed per-workload `(R,S)`
reference transcribed from the C2P-Cache Figure 3 vector and its documented
Figure-10 mapping.  The peer-locality campaign must compare later measurements
to this same reference rather than re-infer or relabel points per experiment.

## Evidence level

The publisher did not release its raw CSV, so the provenance remains
``publisher vector + documented Fig.10 mapping`` rather than author-provided
CSV.  This does **not** make the project reference optional: the named points
below are the canonical basis for all subsequent numerical comparisons.  The
only exception is GS: the vector has four separable R0S1 markers although
Figure 10 lists five workloads, so GS is a deliberate visualization-only
locus and is excluded from numerical aggregates.

The source vector and reconstruction live at
`/workspace/worktrees/accel-sim-decoupled-l2/docs/c2p-cache/figures/0826/fig3-paper-inferred16/`.
The rendered labelled reference is
`fig3_paper_inferred16_labeled.pdf` in that same directory.
At import time their SHA-256 digests were:

| artifact | SHA-256 |
| --- | --- |
| `fig3_paper_original_vector.svg` | `300046ddd2a923b7576760f527e0a2b3dd6f07bbc0f60714b38b1883d720aac4` |
| `fig3_paper_inferred16_coordinates.csv` | `7db6a0e59d1eed350cf47fee46e6e59cbe1467e5cddb630bcb2f64966ccce2c9` |

## Intended comparison rule

Compare the audit's `issue_sector_redundant_ratio` only with
`paper_fig3_redundancy_ratio`, never with a C2P performance or filter-hit
statistic.  Join on `abbr`, retain `identity_confidence`, and separately flag
the conditional mapping.  A numerical mismatch can establish that the local
trace/configuration differs from the paper point; it cannot by itself prove a
model defect.
