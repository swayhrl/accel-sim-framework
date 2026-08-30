# 13-workload archetype checkpoint

Status: **checkpoint complete; evidence labels are per dimension in
`WORKLOAD_ARCHETYPES.csv`.** Inputs are only the promoted D256/D512
calibration, promoted Lane-C sensitivities, and the separate Lane-E probe.

## Representative development set

| Role | Workload | Why |
| --- | --- | --- |
| Structural/substitution probe | `convolutionSeparable` | D256 descriptor relief exposes exact Line-MSHR-full; MSHR256 control shows downstream-limited conversion. |
| Sustained lower-path control | `scan` | Sustained descriptor pressure with high native DRAM utilization and lower/scheduler pressure. |
| Sustained throughput control | `vectorAdd_4M` | Clean sustained descriptor/lower-path/high-BW regime. |
| Address/near-MSHR control | `spmv` | Per-address pressure with near-capacity but not exact Line-MSHR-full; MSHR256 negative control. |
| Phase-local case | `FWT_7_21` | Bursty descriptor/WAD/lower-path behavior. |
| Bank-service case | `cfd_097k` | Measured true payload-bank conflict, without a payload-capacity claim. |
| Victim-lifetime candidate | `dwt2d` | WAD-active; dirty-victim lifetime itself remains unmeasured. |
| Low-pressure negative control | `sad` | Very low structural and downstream pressure. |

## Boundaries

`UNKNOWN_NEEDS_TELEMETRY` for Unified payload is intentional: current evidence
does not time-align resident and bypass-role slack. The same label applies to
read-only pending-tag eligibility and TVD-releasable dirty-victim payload
lifetime. No mechanism opportunity is inferred from a nonzero counter.

Application cycles are Level-3 evidence; structural counters/temporal windows
are Level-1; useful-service/lifetime movement is not upgraded beyond what the
current telemetry directly measures.
