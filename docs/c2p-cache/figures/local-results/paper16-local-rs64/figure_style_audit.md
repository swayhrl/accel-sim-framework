# C2P paper-figure style and data audit

All figures use the manuscript's compact Times-style typography, closed axes,
black bar outlines, dashed workload-group separators, and the same stable
mechanism vocabulary: ATA light blue with forward hatching, CCD blue-gray,
RING pale salmon with back hatching, and C2P-Cache salmon with cross-hatching.
Published formats: pdf, svg, png.

| Local artifact | Paper counterpart | Data source | Required visual convention |
|---|---|---|---|
| `fig10_normalized_ipc` | Fig. 10 | `paper16_modes.csv: ipc_normalized` | Full-width grouped four-bar strip; ATA/CCD/RING/C2P order; C2P cross-hatch; R0S0/R1S0/R0S1/R1S1 separators and in-strip labels. |
| `fig11_l2_access` | Fig. 11 | `paper16_modes.csv: l2_access_normalized` | Compact R1S0/R1S1 four-bar strip using the same mechanism colors, order, hatch, and group separators. |
| `fig12_filtering_accuracy` | Fig. 12 | `paper16_cases.csv: ccd_*_rate`, `snapshot_*_rate` | Full-width stacked CCD/C2P pair per case; eight-entry TP/FN/FP/TN legend; blue-gray CCD and salmon C2P families with the manuscript's hatch distinction. |
| `fig13_ipc_vs_fp_ratio` | Fig. 13 | `fp_sweep_binned.csv` | Compact four-group FP-ratio strip; median IPC line and P25--P75 band; manuscript group colors, markers and line styles.  Only measured, populated bins are drawn. |
| `fig14_peer_probe_distribution` | Fig. 14 | `paper16_modes.csv: c2p_peer_access_{hit,miss}_{p90,p95,p99,max}` | Two compact `(a) Hit` / `(b) Miss` panels; P90/P95/P99/MAX x-axis; four manuscript group line/marker styles, shared 8-access-referenced scale, and no cropping of a measured local MAX. |

The local traces are not the authors' unpublished trace inputs; visual
matching does not imply numerical identity.  The strict analyzer and final
report provide the corresponding mechanism/provenance audit.
