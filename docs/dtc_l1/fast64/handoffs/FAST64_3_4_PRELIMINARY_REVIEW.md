# FAST64.3/4 preliminary terminal-evidence review

Status: **PRELIMINARY, NONPROMOTING — FAST64.3 ACTIVE; FAST64.4 PHYSICAL
PRECOMPUTATION ONLY**

This record is a review-time audit of already terminal evidence.  It neither
creates a stage PASS nor turns a physical precompute into a primary result.
In particular, it does not compute a FAST12 geometric mean.

## Strict re-audit

At `2026-09-10` the current strict parser was rerun over every discovered
terminal `PAPER_BASE`, `PAPER_IO`, and `PAPER_OO` compact record, using the
exact config and trace-list paths recorded in that attempt's
`RUN_MANIFEST.tsv`.  The audit also checked the START/TERMINAL receipt,
current config/trace/stdout SHA-256 against the manifest/compact record, and
the standard assertion/fatal/deadlock/checker-mismatch scan.

| record class | count | parser/config/trace/stdout | immutable terminal receipt | disposition |
| --- | ---: | --- | --- | --- |
| formal/precomputed terminal rows | 44 | PASS | PRESENT | available only under their recorded pending/reuse authority |
| early NN smoke/telemetry anchors | 6 | PASS | absent by design | supporting instrumentation only; excluded from formal candidates |

The audit is retained outside the repository as
`/tmp/fast64-terminal-preaudit-v2-oXUg35/summary.tsv`; it contains no raw
simulator output.  A passed row still requires its identity/reuse and stage
acceptance gates.  In particular, historical `bbcbb5e...` IO/OO evidence is
not silently promoted to repaired-Core evidence.

### ATAX historical IO reconciliation (2026-09-11)

`fast64_4_atax_io_cap8192_a1_v3` is a natural-exit-zero historical-Core IO
attempt, not an unobserved placeholder.  The strict validator was rerun in an
isolated output namespace using its exact immutable receipt, config, payload,
Core `bbcbb5e...`, runtime `6a8743b4...`, A1 and Framework identity; its
compact result was byte-identical to
`generated/fast64_4_precomputed_rows_v1/fast64_4_atax_io_cap8192_a1_v3.json`.
The zero-access transition map permits this successful literal IO observation
only under its recorded historical provenance.  The provisional triplet table
now records one IO candidate, but it has no matching same-identity Base/OO
triple and is therefore explicitly incomplete and nonpromoting.

## Current provisional aggregates

The mechanically regenerated, checked-in, nonpromoting tables are:

- `generated/provisional_stage3_structural.tsv`
- `generated/provisional_stage4_triplets.tsv`
- `generated/provisional_stage4_speedup.tsv`

The only common repaired-Core triplet candidates presently represented are
`Btree`, `Hotspot1`, and `MRI-Q`.  Their preliminary cycle observations are:

| workload | Base | IO | OO | Base/IO | Base/OO |
| --- | ---: | ---: | ---: | ---: | ---: |
| Btree | 369,977 | 244,231 | 172,795 | 1.514865 | 2.141133 |
| Hotspot1 | 160,486 | 85,206 | 83,439 | 1.883506 | 1.923393 |
| MRI-Q | 366,667 | 360,536 | 361,415 | 1.017005 | 1.014532 |

These observations are hypotheses for FAST64.5, not causal claims: Btree
combines substantial baseline PIB and traditional-MSHR pressure with the
largest currently observed incremental OO change; Hotspot1 has high PIB
pressure but little IO-to-OO incremental change; MRI-Q is near neutral.  The
future causal review must cross-check those observations with its explicit
HOL, merge, retirement/reclaim, traffic, and live-miss evidence.

## 2DConvolution/Base remains an implementation incident

`fast64_3_2DConvolution_base_cap8192_a1_v2` is a preserved failed attempt,
not a terminal evidence row.  The deadlock dump has all of the following on
SMs 3, 29, and 51:

- `L1_latency_queue` stage zero repeatedly returns `RESERVATION_FAIL`;
- the relevant four conventional-L1 ways are `RESERVED`;
- the displayed MSHR, miss queue, response FIFO, and immediate lower-level
  queue are empty; and
- 129 latency-queue `MEM_FETCH_INITIALIZED` objects remain in the dump.

The configuration fixes `-gpgpu_dtc_l1_lower_outstanding_cap 8192`; this
incident is therefore not evidence that the cap is binding.  It is also not
the earlier dirty-only-victim condition: the frozen config has
`-gpgpu_l1_cache_write_ratio 0`, while this dump shows actual reservation
ownership rather than an unreplaceable dirty victim.

The conventional Base source path reserves a line in `tag_array::access`,
adds its MSHR/extra-field record and miss-queue request in
`baseline_cache::send_read_request`, then clears the reservation only through
the conventional `baseline_cache::fill` response path.  The snapshot proves a
lost/unobservable completion relationship, but does not yet identify which
transition lost ownership.  The next directed diagnostic must separately
account for reserve, MSHR/extra-field insertion, lower injection, and
response/fill/credit release before any functional repair or replacement
namespace is authorized.
