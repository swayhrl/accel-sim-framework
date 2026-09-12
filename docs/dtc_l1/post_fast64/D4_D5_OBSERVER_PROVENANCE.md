# D4/D5 observer diagnostic provenance

Status: `D4_D5_INTERIM_REVIEW_CHECKPOINT`.

Every retained row is classified
`POST_FAST64_EXPLORATORY_NOT_PRIMARY_RESULT`.  These diagnostics extend the
accepted FAST64 evidence; they do not alter its membership, artifacts, or
conclusions.

## Runtime and equivalence boundary

The observer source/runtime identities are recorded in
`generated/D1_OBSERVER_SOURCE_RUNTIME_MANIFEST.tsv`.  Core95 supplies all
non-2D rows and Core658 supplies only the accepted 2DConvolution OO row.
Before this wave, D3B exactly requalified NN and Btree in IO and OO with the
occupancy/in-flight extension.  Its compact package is
`D3B_OCCUPANCY_EXTENSION_EQUIVALENCE.md` and its generated TSVs.  D3B requires
all pre-existing simulated statistics to agree exactly and permits only the
new observer fields to be additional.

The D4/D5 collector applies that same row-level rule against the exact
accepted FAST64 compact summary named in each run's immutable manifest.  A
retained row must additionally have a natural terminal receipt, matching
attempt identity and core/config/trace hashes, and zero terminal observer live
records.  The final raw-run index records only paths, hashes and identities;
it intentionally contains no raw simulator output.

## D4 physical-pool wave

The interim package retains 16 natural-terminal rows from the intended 18-row
matrix: BICG and Btree at 24/32/48 KiB in IO and whole-line OO, plus GESUMMV at
24/32 KiB in IO and whole-line OO.  The GESUMMV 48-KiB IO/OO rows remain live
and are deliberately absent from numerical tables.  The interim raw and
derived outputs are `generated/D4_INTERIM_TERMINAL_ROWS.tsv` and
`generated/D4_INTERIM_ANALYSIS.tsv`.
It carries raw counters plus these descriptive normalizations:

- time-integrated physical occupancy per sampled active SM cycle, its fraction
  of the configured 128-B-line capacity, pool-full fraction and lower
  in-flight requests per sample;
- allocation-to-ready and pending-eviction/deferred-reclaim lifetimes;
- L2 miss and reservation-failure counts per lower request and per instruction;
- same-mode cycles divided by that workload/mode's 24-KiB cycles.

The source-defined sampling hook executes once per active SM simulation cycle;
the full counter definition and hook audit are in
`LANE_D_OBSERVER_COUNTER_SEMANTICS.md`.  These are time integrals, not
access-event samples.  D4 presents association only; it does not make an
automatic causal inference.

Whole-line OO has no compact emitted `no_free_physical_events` statistic in
this runtime.  Its table cell is therefore the explicit source-classified
boundary `NA_NOT_REPORTED_IN_WHOLE_LINE_OO_COMPACT`, never a proxy.  IO retains
the exact emitted event count.

## D5 OO duplicate FAST12 extension

The interim comparison has eleven whole-line OO primary rows.  Ten are natural
terminal fresh diagnostics and Btree is a D3B exact reuse with the same
source/runtime/config/trace identity, labelled `D3B_EXACT_REUSE` in the raw
index.  GESUMMV OO remains live and is deliberately absent.  The first retained
Core658 2DConvolution row also requires exact pre-existing agreement with its
accepted Core658 OO row.  The output is
`generated/D5_INTERIM_IO_OO_DUPLICATE.tsv`.

The table reports raw lower-created, pending-hit, Tag-eviction and exact
`DTC_L1_oo_duplicate_after_eviction` counts.  Its ratios are descriptive:

`duplicate_share_of_lower = duplicate / lower_created`

`duplicate_per_tag_eviction = duplicate / tag_evictions`

`duplicate_event_ratio = duplicate / (duplicate + pending_hits)`

The last is explicitly not called a probability.  All zero denominators are
rendered by an explicit `NA_*_DENOMINATOR` label.  The exact source definition,
including pending-hit, failed-allocation, stale-fill and post-response negative
cases, is in `OO_DUPLICATE_COUNTER_SEMANTICS.md`.

For this exact whole-line mode, one newly created lower request is source-proven
to have a 128-B logical-line payload.  Thus
`duplicate_payload_bytes_128B_lower_request_only = duplicate * 128` and
`duplicate_traffic_inflation = duplicate / (lower_created - duplicate)` are
reported as lower-request payload quantities only.  They are not DRAM traffic,
total interconnect traffic or an estimate of performance recoverable by
removing duplicates.

## 40-KiB decision rule

The 40-KiB observer point is not a rectangular-completeness requirement.  It
will be launched only if the completed 24/32/48-KiB time-integrated evidence
could distinguish H2 pressure transfer from H3 pending-lifetime/duplicate or
H4 reclaim-lifetime explanations.  A merely interpolating capacity point cannot
turn an observational correlation into an identified causal arrow and is not
sufficient reason to run it.  The final decision and its completed-data basis
are recorded in `LANE_D_OBSERVER_FINAL.md`.
