# SG3 GESUMMV A2 Dispatch Incident V1

Date: 2026-09-23  
Scope: SG3 scheduler bookkeeping; not scientific evidence

## Event

At 2026-09-23T12:02:07Z, immediately after strict validation of the fresh
GESUMMV/OO baseline retry, the row-local supervisor launched
`sg3_mshr_quad_OO_GESUMMV_acbe7c94-6782-4cee-88b7-817c6da7e5d4` through the
legacy broad `sg3_a2()` loop.  That MSHR=4x point was not authorized by the V4
necessity refinement: GESUMMV is limited to the baseline retries and the
predeclared `cap=512`/`cap=2048` IO/OO validation cells.

## Disposition

The runner process group was sent SIGTERM as soon as the dispatch was found.
The preserved attempt directory contains `RUN_MANIFEST.tsv`, `RUN_START.tsv`,
and simulator stdout/stderr, but no `RUN_TERMINAL.tsv` and no validation JSON.
It is an incomplete, non-scientific dispatch diagnostic and is excluded from
all resource-bottleneck attribution, ranking, trigger, table, and claim use.
No accepted or frozen evidence was modified or deleted.

## Corrective guard

The supervisor now limits `sg3_a2()` to BICG.  GESUMMV can be scheduled only
by the V4-specific `sg3_ges_cap_v4()` gate, which enumerates solely
`cap=512` and `cap=2048` for IO and OO.  The V3/V4 prohibition on automatic
GESUMMV capacity or MSHR expansion therefore remains enforced.
