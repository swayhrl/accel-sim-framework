# POST-FAST64 Lane C — duplicate-miss quantification handoff

Status: **C_DUPLICATE_MISS_READY**

Scope: accepted FAST64 IO evidence only; no FAST12 IO workload was rerun. The
frozen authority remains framework commit
`18a68dcccd795f1b6cda75504e9450d00c9cee02` and terminal state
`FAST64_COMPLETE_READY_FOR_REVIEW`.

Evidence disposition:

| Item | Evidence class |
| --- | --- |
| IO counter semantics and 128-B request-payload granularity | `SOURCE_PROVEN` |
| FAST12 and Stage6 extracted/normalized tables | `EXISTING_DATA_DERIVED_ANALYSIS` from `ACCEPTED_FAST64_EVIDENCE` |
| Stage6 association coefficients | `MEASURED_CORRELATION` |
| Exact accepted OO duplicate count | `INSUFFICIENT` |

## C1 — accepted FAST12 IO extraction

The reproducible extractor is
`util/dtc_l1/generate_post_fast64_duplicate_miss.py`. It verifies that the
primary IO registry is exactly the 12 FAST12 workloads, validates every
selected compact JSON hash, and requires terminal
`lower_created = lower_issued = lower_responses`. The raw source counts,
traffic counters, evidence paths, evidence hashes, all three requested ratios,
and explicit zero-denominator states are in:

- `generated/post_fast64/duplicate_miss_fast12_io.tsv`
- `generated/post_fast64/duplicate_miss_input_manifest.tsv`

`duplicate_share_of_lower = duplicate_after_eviction / io_lower_created`;
`duplicate_escape_fraction = duplicate_after_eviction /
(duplicate_after_eviction + io_pending_hits)`; and
`duplicate_per_tag_eviction = duplicate_after_eviction / io_tag_evictions`.
They are descriptive event ratios, never called probabilities. NN has zero Tag
evictions, so its third ratio is undefined; MRI-Q has zero duplicates and zero
pending hits, so its escape ratio is undefined.

| Workload | Duplicate / lower created | Share of lower | Escape fraction | Per Tag eviction | Presentation bin |
| --- | ---: | ---: | ---: | ---: | --- |
| ATAX | 356,940 / 17,821,540 | 2.003% | 94.807% | 2.003% | 1–5% |
| BICG | 279,251 / 17,821,394 | 1.567% | 93.817% | 1.567% | 1–5% |
| GESUMMV | 605,076 / 34,595,564 | 1.749% | 95.497% | 1.749% | 1–5% |
| GEMM | 440,128 / 4,256,815 | 10.339% | 16.606% | 10.359% | >5% |
| 2DConvolution | 1,425,269 / 3,375,831 | 42.220% | 24.300% | 42.322% | >5% |
| Btree | 8 / 507,779 | 0.0016% | 0.0011% | 0.0016% | <0.1% |
| DWT2D | 1,520 / 232,115 | 0.655% | 8.508% | 0.679% | 0.1–1% |
| Gaussian | 713,979 / 1,422,278 | 50.200% | 16.483% | 50.490% | >5% |
| Hotspot1 | 4,567 / 351,857 | 1.298% | 82.437% | 1.329% | 1–5% |
| LUD | 31,436 / 517,232 | 6.078% | 87.844% | 6.176% | >5% |
| NN | 0 / 2,673 | 0.000% | 0.000% | undefined (0 evictions) | <0.1% |
| MRI-Q | 0 / 15,517 | 0.000% | undefined (0 + 0) | 0.000% | <0.1% |

The bins `<0.1%`, `0.1–1%`, `1–5%`, and `>5%` are presentation bins only;
they are not a scientific definition of “rare.” The 3,858,174 observed
duplicate events correspond to 493,846,272 B of source-proven *lower-request
payload* across FAST12, not total request/reply/link traffic.

## C2 — adjudication of the dissertation claim

**The unqualified claim that locality makes duplicate requests rare is not
supported across FAST12.** Eight of 12 workloads are below the presentation
bin boundary of 5%, but only four are below 1% and only three are below 0.1%.
Without an a-priori scientific threshold for “rare,” the most defensible result
is the full distribution above rather than a binary conclusion.

The exceptions are retained in full: LUD (6.078%), GEMM (10.339%),
2DConvolution (42.220%), and Gaussian (50.200%). The worst case is Gaussian:
713,979 duplicate lower requests, or just over half of its lower-created
count. 2DConvolution is also far from negligible at 1,425,269 duplicates and
42.220% of lower-created requests.

An average hides important workload behavior. The unweighted mean share is
9.676%, the median is 1.658%, and the count-weighted FAST12 share is 4.768%.
None is an adequate substitute for the four >5% cases, especially the two
42–50% cases.

The data give only descriptive co-occurrences, not a causal explanation:

- Tag evictions are high in absolute count for most IO workloads, including
  Btree (499,587) and MRI-Q (13,325), where duplicate shares are effectively
  zero. Tag eviction alone is therefore not sufficient.
- The two largest-share exceptions also have millions of pending hits
  (2DConvolution: 4,439,927; Gaussian: 3,617,506), but Btree has 735,684
  pending hits and only eight duplicates. Pending-hit totals alone are also
  insufficient.
- The `duplicate_escape_fraction` contrasts the observed duplicate events with
  observed pending-hit events; it is not the chance that a pending request
  escapes. High escape fractions for ATAX/BICG/GESUMMV coexist with only
  1.6–2.0% lower-request shares, while the two largest shares have 16–24%
  escape fractions.
- Physical-pool behavior is examined separately below with the controlled
  accepted Stage6 sweep. Its three workloads are BICG, GESUMMV, and Btree,
  not the four >5% exceptions; it therefore cannot establish a physical-pool
  explanation for LUD, GEMM, 2DConvolution, or Gaussian. It shows
  workload-specific patterns, not one universal anomaly signature.

Thus, high Tag-eviction counts do not distinguish the exceptions; high
pending-hit totals co-occur with 2DConvolution/Gaussian but are not sufficient;
and the accepted physical sweep is insufficient to attribute the four primary
exceptions to a physical-pool anomaly. These are bounded descriptive findings,
not causal conclusions.

No performance improvement is estimated from hypothetically eliminating these
events.

## C3 — Stage6 physical-sweep association

The accepted numeric Stage6 IO physical points are preserved in
`generated/post_fast64/duplicate_miss_stage6_io_physical.tsv`: BICG (24, 32,
40, 48 KiB), GESUMMV (24, 32, 40, 48 KiB), and Btree (16.5, 24, 32, 40,
48 KiB). The 16.5-KiB BICG/GESUMMV resource-deadlock boundaries have no
numeric performance row and are not included; Btree's retained 16.5-KiB
terminal row is included.

Each row retains raw duplicates, pending hits, Tag evictions, L2 misses,
L2 reservation failures, lower requests, and cycles. Event quantities are
normalized per lower request or per million instructions; time is expressed as
cycles per instruction. This avoids interpreting accumulated global counters
without exposure.

| Workload | Physical pool (KiB) | Duplicate share of lower, in point order | Descriptive pattern |
| --- | --- | --- | --- |
| BICG | 24, 32, 40, 48 | 0.708%, 1.992%, 2.178%, 2.002% | Rises through 40 KiB, then falls slightly; L2 misses, reservation failures, and cycles still rise across all four points. |
| GESUMMV | 24, 32, 40, 48 | 0.435%, 1.054%, 1.683%, 1.823% | Rises at every retained point, alongside larger normalized lower/L2 pressure and cycles per instruction; pending hits per lower fall. |
| Btree | 16.5, 24, 32, 40, 48 | 0.00020%, 0.00158%, 0.00158%, 0.00158%, 0.00158% | Duplicate behavior remains negligible despite the 16.5-KiB timing anomaly; 24–48 KiB are identical in this data. |

`generated/post_fast64/duplicate_miss_stage6_io_correlations.tsv` reports
Pearson descriptive associations against `duplicate_share_of_lower` for the
13 points, each workload separately, and a workload-demeaned 13-point view.
The latter correlations are: pool size 0.618, pending hits per lower -0.020,
Tag evictions per lower 0.385, L2 misses per lower 0.737, L2 reservation
failures per lower 0.719, lower requests per million instructions 0.921, and
cycles per instruction 0.736.

These are **not causal estimates**: there are only 4/4/5 points per workload,
the sweeps contain plateaus/non-monotonic points, and the counters share
exposure and mechanism paths. In particular, the opposite pending-hit patterns
in BICG/GESUMMV versus Btree rule out a simple claim that pending-hit volume
alone explains duplicate behavior.

## C4 — accepted OO semantic gap

Accepted OO does **not** contain an exactly equivalent duplicate counter. The
machine-readable audit is
`generated/post_fast64/duplicate_miss_oo_semantic_gap.tsv`; it verifies the
absence of `DTC_L1_oo_duplicate_after_eviction` in all 12 accepted OO compact
rows and explicitly rejects `DTC_L1_oo_new_misses` as a proxy.

The source agrees. `oo_frontend::access` in
`src/gpgpu-sim/dtc-l1-common.h:458–512` counts Tag evictions and
immediate/deferred reclaim, but has no IO-style map of pending evicted lines
and no duplicate counter. `complete()` at lines 523–539 wakes waiters but has
no such cleanup state. `paper_frontend_stats` exposes OO new misses, pending
hits, and Tag evictions (`dtc-l1-common.h:1394–1414`), while the accepted
printer has no OO duplicate field. Hence new misses, pending hits, Tag
evictions, reclaims, and lower-created counts cannot be used to infer OO
duplicates.

The minimum observer-only Lane-D counter, if an IO-vs-OO comparison is later
required, is `DTC_L1_oo_duplicate_after_eviction` with this predeclared
semantics:

1. In the OO successful Tag-victim path, record `(line, physical_identity)` in
   observer state only when the victim is valid and its physical line is
   pending (`!ready`) at Tag eviction.
2. On completion of that exact id-and-generation, erase its observer record.
3. On a later successful same-line `NEW_MISS`, erase a matching observer
   record and increment once. Require the normal integration to enqueue the
   one lower candidate for that `NEW_MISS`; do not count post-response
   re-accesses or pending Tag hits.
4. Export/reset/aggregate the counter like existing OO event counters, and
   add directed positive, pending-hit-negative, and post-response-negative
   tests. Observer state must not affect lookup, victim choice, allocation,
   lower scheduling, completion, retirement, or reclaim.

Lane D would implement this only on observer descendants rooted at accepted
Core95 for non-2D and Core658 for 2D, then demonstrate observer equivalence
before retaining new telemetry. Lane C does not alter the formal Core and does
not require that rerun: the IO evidence already quantifies and source-backs
the dissertation's no-MSHR duplicate-request claim.
