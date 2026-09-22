# SG4A bounded logical-Tag closure (V1)

## Decision

SG4A is **closed**. The existing fixed-G4 evidence is sufficient for the
paper's bounded logical-Tag question; no FAST12 extension is triggered. This
is a predeclared efficiency closure, not a result-selected expansion or a
change to the preserved V3 execution plan.

## Numeric 16/32/64 KiB summary

`SG4A_BOUNDED_LOGICAL_TAG_CLOSURE_V1.tsv` gives cycles and the percentage
change from the frozen 16-KiB point. For the identity-matched Core95 rows:

| workload | mode | 32 KiB vs. 16 KiB | 64 KiB vs. 16 KiB |
|---|---:|---:|---:|
| BICG | IO | 0.000% | -0.261% |
| BICG | OO | -0.105% | -10.085% |
| GESUMMV | IO | +0.085% | -1.353% |
| GESUMMV | OO | -0.280% | -18.978% |
| Btree | IO | -3.594% | -4.257% |
| Btree | OO | -11.741% | -15.245% |

The added logical-tag capacity does not expose a new mechanism requiring
FAST12 coverage: IO is near-flat to modestly improved, while the larger OO
changes are already bounded by the G4 characterization. All logical32/
logical64 G4 attempts used for this closure passed row-local strict validation.

The 2DConvolution values are retained in the TSV as boundary context: IO is
-0.264%/-0.749% and OO is +0.406%/-0.606% at 32/64 KiB relative to frozen
16 KiB. Its frozen 16-KiB baseline is the documented narrow Core658
tag-identity exception, whereas the new 32/64-KiB rows ran on Core95. They
are therefore explicitly **not** a same-identity three-point performance curve
and cannot support cross-Core causal attribution. They corroborate only the
bounded/no-extra-sweep decision.

Sources: `fast64_6_logical_plot.tsv` for the Core95 BICG/GESUMMV/Btree
16/32/64 series; `SG4A_R0_VALIDATION.tsv` and
`SG4A_EXECUTION_DATA_SNAPSHOT_V3.tsv` for strict-passing SG4A rows; and
`fast64_4_cap_resolved_matrix_v1/fast64_4_speedup.tsv` for the frozen
2DConvolution 16-KiB exception.

## logical80 is a nonnumeric boundary

The four preserved logical80 attempts (BICG and GESUMMV, each IO/OO) exited
with source-model deadlock. GESUMMV deadlocked before final aggregate stats
were emitted. These are immutable, nonaccepted, **nonnumeric boundary**
evidence, not missing numeric cells and not evidence for a capacity trend.
They are recorded in `SG4A_FAILURE_REGISTRY.tsv` and
`SG4A_LOGICAL80_SOURCE_BOUNDARY_AUDIT.md`. No retry, alternate Core, or
logical80/FAST12 expansion is authorized by this closure.

## Scheduler disposition

SG4A has no remaining eligible rows. The rolling supervisor must not launch an
SG4A row or a FAST12 row on SG4A's behalf. SG1, SG3, and SG5 retain their
unchanged V3 rolling plans and row-local validation gates.
