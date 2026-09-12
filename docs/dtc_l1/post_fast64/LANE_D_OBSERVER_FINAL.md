# Lane D observer telemetry: final evidence closeout

Status: `D_OBSERVER_EVIDENCE_READY`.

Lane D is a provenance-bound extension of frozen FAST64, not a replacement for
it.  Every retained D4/D5 row is classified
`POST_FAST64_EXPLORATORY_NOT_PRIMARY_RESULT`; none enters the accepted FAST64
matrix or GM-FAST12.

## Completed evidence package

- `generated/D1_OBSERVER_SOURCE_RUNTIME_MANIFEST.tsv` binds the observer source
  and runtime identities.  `D3B_OCCUPANCY_EXTENSION_EQUIVALENCE.md` proves NN
  and Btree IO/OO retain exact pre-existing simulated metrics after the added
  occupancy/in-flight telemetry.
- `generated/D4_OBSERVER_PHYSICAL_TELEMETRY.tsv` contains all 18 D4 rows:
  BICG, GESUMMV, Btree x 24/32/48 KiB x IO/OO.  It has raw counters and
  source-defined time-integrated occupancy, full exposure, inflight exposure,
  allocation-to-ready and pending/reclaim lifetime measures.
- `generated/D5_OO_DUPLICATE_FAST12.tsv` contains the twelve whole-line OO
  FAST12 rows (11 fresh natural terminals plus exact Btree D3B reuse).
  `generated/D5_IO_OO_DUPLICATE_COMPARISON.tsv` joins those rows to accepted
  Lane-C IO evidence and accepted Base/IO/OO speedups.
- `generated/D5_DUPLICATE_TRAFFIC_INFLATION.tsv` is the explicit 24-row IO/OO
  lower-request-payload inflation table.  Its 128-B payload quantities are
  neither total-link nor DRAM traffic.
- `generated/D4_D5_OBSERVER_RAW_RUN_INDEX.tsv` is the 30-row identity-only raw
  index; raw simulator output is outside Git.

The collector requires a natural exit 0, immutable attempt/runner/Core/runtime/
config/trace identity, exact equality of all pre-existing accepted FAST64
metrics, conservation checks, and terminal observer-live-record drain.  The
final full-wave collection passed all 29 launched rows and the D3B reuse.

The Lane-B source audit remains decisive on physical identity: physical-ID and
free-list identity do not directly select lower addresses, L2 sets/partitions,
or request order.  It is therefore source-proven downstream-inert, rather than
a candidate explanation for the measured D4 downstream traffic patterns.

## D4 findings

Btree is the control.  At every physical-pool point, its same-mode cycles,
lower requests, in-flight exposure, allocation-to-ready lifetime, and duplicate
count are invariant; its pool-full fraction is zero.  Its occupancy *fraction*
decreases only because physical capacity is the denominator.  This rejects a
universal simple pool-starvation account.

BICG and GESUMMV have local capacity-associated changes.  For BICG IO, average
allocated lines/inflight rise 186.94/59.85 -> 248.46/79.77 -> 355.06/148.05;
for OO they rise 186.37/72.55 -> 247.83/98.73 -> 303.77/133.97.  GESUMMV shows
the analogous IO 191.44/35.48 -> 255.49/56.29 -> 363.72/87.80 and OO
191.42/38.49 -> 255.39/58.41 -> 325.81/79.26 patterns.  These are measured
correlations, not causal arrows.

L2 pressure and allocation-to-ready lifetime also co-vary locally.  BICG IO
misses/lower and mean lifetime are 1.43/2018, 1.61/2802, 2.82/9400 across
24/32/48 KiB; GESUMMV IO is 1.48/1123, 1.94/2276, 2.65/5431.  The corresponding
OO data are retained in the D4 table.  Capacity changes, workload execution,
and several queues co-vary, so this does not establish that L2 pressure causes
lifetime or performance.

The previously proposed local pressure-transfer premise is not supported in
its stated no-free form.  Exact IO no-free events per instruction for BICG are
3.781 -> 3.977 -> 4.617 and for GESUMMV are 5.475 -> 7.059 -> 6.677.  They do
not fall with a larger pool.  Whole-line OO intentionally reports no compact
no-free field, so it is `NA_NOT_REPORTED_IN_WHOLE_LINE_OO_COMPACT`, never a
proxy.

## D5 duplicate findings

OO duplicate share is lower than accepted IO for seven workloads
(2DConvolution, ATAX, BICG, GEMM, GESUMMV, Hotspot1, LUD), higher for three
(Btree, DWT2D, Gaussian), and equal at zero for MRI-Q and NN.  Therefore OO
does not universally reduce duplicates.  The comparison includes exact
accepted IO speedups and OO speedups for context, but neither is attributed to
duplicates.

`duplicate_traffic_inflation = duplicate / (lower_created - duplicate)` means
extra duplicate lower-request payloads per nonduplicate lower request.  It is
descriptive, has explicit zero-denominator labels, and does not estimate
recoverable performance.  The exact duplicate counters exclude post-response
re-accesses by source semantics.

## Integrated causal classification

`generated/D6_INTEGRATED_ARROW_CLASSIFICATION.tsv` classifies every requested
physical and OO lifecycle arrow as `SOURCE_PROVEN`, `MEASURED_CORRELATION`,
`NOT_SUPPORTED`, or `INSUFFICIENT`.  The source-proven transition is pending
Tag eviction of a still-pending line to duplicate lower-request creation after
same-line reallocation.  The full downstream claim—L2 pressure is the primary
limiter and duplicates a secondary positive-feedback mechanism—remains
`INSUFFICIENT`: there is no duplicate-only or L2-only intervention that ranks
their causal contributions.

## 40-KiB decision

No 40-KiB point was launched.  The completed 24/32/48-KiB results already show
that a fourth observational capacity point cannot identify the disputed causal
directions, while the no-free premise is directly contradicted for the emitted
IO metric.  It would add rectangularity, not a source-backed causal
discriminator.
