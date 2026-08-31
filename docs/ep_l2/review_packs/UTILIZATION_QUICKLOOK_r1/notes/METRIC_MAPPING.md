# Metric mapping and limits

All utilization panels are generated from `EPL2B0V1` `target_slice.csv` records.
For each workload, the plotted number is the maximum across its 64 application
slices: P95 occupancy when emitted, otherwise AVG occupancy.  That hotspot-slice
aggregation is intentional: it exposes pressure hidden by a whole-chip average.

| Figure resource | CSV field | Statistic | Capacity | Interpretation |
|---|---|---:|---:|---|
| Set-reservation | `c7d_reserved_p95` | P95 | 128 entries | C7D reserved-entry pressure per slice |
| MSHR-entry | `line_mshr_p95` | P95 | 128 entries | line-MSHR occupancy per slice |
| MissQ | `missq_avg` | AVG | 128 entries | P95 is not emitted by this schema |
| WB-path proxy (WAD) | `wad_p95` | P95 | 128 entries | live WAD occupancy; a proxy for the broader WB path |

`WB-path proxy (WAD)` is not a claim that the baseline has a physical WBUF.  The
accepted WB-path category includes WAD/order restrictions and a timing-neutral
shadow dirty-WB staging pressure; this quicklook uses the directly exported live
WAD occupancy as the closest frozen occupancy proxy.

Figure B is different: it is a WBUF=8 **exclusive primary blocker** breakdown.
Every stack segment and its printed total uses `eligible_miss_admission_cycles`
as the denominator, not a percentage of already-blocked cycles.  Its category
closure is verified before rendering.
