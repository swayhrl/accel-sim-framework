# Fig. 3 paper-position-inferred local-16 subset

This is a **non-evidentiary diagnostic illustration**, not a formal local
result and not a claim of recovered author data.  It starts from the
publisher's vector Fig. 3 and removes the eight extension-suite workloads by
the inferred within-group plotting order obtained from Fig. 10 and Table 2.
Its y-axis is deliberately relabeled as `Normalized IPC (L2=50 / L2=200)` to
make the local R/S definition explicit; this annotation is not text recovered
from the publisher vector.

The retained logical workload set is the local 16: `MR`, `NN`, `DW`, `CU`,
`HO`, `GA`, `AT`, `BI`, `GS`, `LU`, `SG`, `3M`, `GE`, `B+`, `2D`, and `ST`.
The published Fig. 3 vector exposes only 23 separable marker paths for its
24-workload corpus.  Its R0S1 series exposes four paths although Fig. 10 lists
five items.  For this diagnostic-only illustration, `GS` is **guessed as an
R0S1 marker** and drawn at a synthetic vector coordinate within the retained
R0S1 cluster.  It is not a recovered paper data point.  The image therefore shows
16 visible marker loci, but the `GS` locus has no evidentiary value.

Do not use this illustration for numerical claims, R/S reclassification, or
paper comparison.  Use `local-results/paper16-local-rs64/fig3_local_rs64.*`
for the measured local 16-workload figure.

## Inference map

The mapping is machine-readable in `fig3_paper_inferred16_mapping.csv`.
Marker removal follows the published within-group order:

- R0S0: remove `RA`, `CO`, `MI`.
- R1S0: remove `FW`.
- R0S1: remove `PA`, `LI`.
- R1S1: remove `BV`, `LP`.

`GS` is added as a guessed R0S1 diamond at vector coordinate `(42.10, 13.00)`.
That coordinate is intentionally not convertible to or usable as a reported
R/S measurement.

The rebuild script requires the publisher vector `mov.pdf` exported from the
paper's public source package:

```bash
python3 rebuild_fig3_paper_inferred16.py \
  --source-pdf path/to/mov.pdf --out-dir .
```
