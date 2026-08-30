# EP-L2 final calibration convergence r1

Status: **FINAL_CALIBRATION_CONVERGENCE_REVIEW_READY — request independent ChatGPT review.**

This analysis-only pack does not change a simulator default or authorize
Unified, RO pending-tag, TVD, or headroom execution. The primary matrix has 80
provenance-bound rows: D256/D512 base have 26 rows each; four promoted Lane-C
cells have seven B0-Banked rows each. Lane-E is a supplemental sensitivity.

`lower_admission_byte_rate_norm` is not physical DRAM utilization. Native
physical utilization is the final complete 32-channel snapshot. Compact L1
review tables lack native distributions, so their field is explicitly
`NOT_RETAINED_IN_COMPACT_L1_REVIEW_TABLE`, never zero.

Reproduce derived CSVs with
`PYTHONDONTWRITEBYTECODE=1 python3 docs/ep_l2/analysis/final_calibration_convergence.py`.
