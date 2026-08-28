# C2P paper Figure 3: inferred per-workload reference points

`paper_fig3_inferred_points.csv` records the best available *graphically
inferred* per-workload R/S reference for the C2P-Cache paper.  It is preserved
here so that the peer-locality campaign can compare a later measured point to
the same reference without silently changing either identity or coordinate.

## Evidence level

This is **not author-provided raw data** and must not be reported as such.
The publisher's vector Figure 3 exposes 23 marker coordinates but neither its
underlying CSV nor the mapping from every marker to a workload.  The mapping
uses Figure 10's within-group drawing order, and is therefore marked
`conditional`.  The vector has four separable R0S1 markers although Figure 10
lists five workloads; GS is a deliberately synthetic visualization-only
locus and is excluded from all numerical aggregates.

The source vector and reconstruction live at
`/workspace/worktrees/accel-sim-decoupled-l2/docs/c2p-cache/figures/0826/fig3-paper-inferred16/`.
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
