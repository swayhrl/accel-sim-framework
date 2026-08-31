# EP-L2 Motivation Figures r1

This is the final independent Motivation-lane review pack. It contains only
formal results from the single frozen candidate below; earlier pilot output is
retained outside this pack as `PRE_WBUF_LIFECYCLE_FIX_DIAGNOSTIC` evidence and
is not used by any table or figure here.

| Item | Value |
|---|---|
| Core | `2a6a31591bc42023e5997cca969e4b672efe0405` |
| Framework runtime | `02f36816f60afcff55e910cdef2b60937e691cdc` |
| Branch | `hrl/ep-l2-motivation-v0` |
| Scope | default-OFF observation-only EPL2MOTV1 telemetry |
| Formal broad rows | `scan`, `vectorAdd_4M`, `convolutionSeparable`, `spmv`, `FWT_7_21`, `cfd_097k`, `dwt2d`, `sad`, `btree`, `gemm` |

`VALIDATION_SUMMARY.md` records the stage gates. The CSVs are the exact
machine-readable inputs for the six files in `figures/`; `RAW_LOG_INDEX.tsv`
binds every row to a raw-log checksum and frozen provenance.
