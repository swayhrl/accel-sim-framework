# EPL2B0V1 interim analysis schema

This provisional package uses direct `EPL2B0V1` application-cumulative records
from completed runs only.  `samples` is a slice-cycle sample count.  `block_*`
are additive blocker events, not exclusive blocked cycles; matrices consequently
keep event density and mark blocked-cycle ratios unavailable.  Fields marked
`NOT_EMITTED_BY_EPL2B0V1` were not inferred from unrelated counters.

Raw simulator terminal summaries supply total L2 accesses/misses, DRAM reads/writes,
and total instructions.  All other occupancy and blocker values are derived from
`target_slice.csv` / `target_summary.csv`.
