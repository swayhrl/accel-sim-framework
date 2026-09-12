# Whole-line OO duplicate-after-eviction counter

Status: `D2_SOURCE_SEMANTICS_AUDITED`.

`DTC_L1_oo_duplicate_after_eviction` is new diagnostic telemetry, not a proxy
for `DTC_L1_oo_new_misses`.  All values produced with it are
`POST_FAST64_EXPLORATORY_NOT_PRIMARY_RESULT`.

## Exact definition

This applies only to the whole-line `dtc_l1::oo_frontend`, not sector OO.
`kLogicalLineBytes` is 128, and this frontend aligns each address to that
logical line.  At an OO Tag eviction, it inserts `victim->line` into the
observer-only `m_evicted_pending_lines` map only when telemetry is enabled and
the evicted physical line is not ready.  The map value is the original
physical id and generation.

On a later Tag miss for the same aligned line, the counter increments only at
the point where allocation has succeeded and `access()` will return
`NEW_MISS`: the code erases that line from the pending-eviction map and
increments only when the erase succeeds.  The integration queues exactly one
whole-line lower candidate for that `NEW_MISS`; its issue path constructs a
128-byte `GLOBAL_ACC_R` request and increments `DTC_L1_oo_lower_created` when
the request is created.  Thus the counter denotes a reallocation event whose
original pending line had been Tag-evicted and which enters the new-miss lower
request path; it is not a count of all OO new misses or of all Tag evictions.

When a response completes, the frontend removes every pending-eviction map
entry with the completing physical id and generation before returning.  A
re-access after that cleanup cannot erase the map entry and is therefore not
counted.  This is the source-level exclusion of post-response re-access.

## Observer-only and interpretation boundary

The OO pending map and counter mutation are gated by
`post_fast64_telemetry`; telemetry-off outputs remain zero and D3B proved
that enabling the guard does not change pre-existing stat sequences for NN or
Btree.  The map is never consulted for frontend allocation, victim selection,
reference tracking, lower scheduling, response routing, or retirement.

It follows from source control flow—not from a probabilistic model—that a
positive value is an exact count under this observer definition.  A ratio to
`oo_lower_created` is a descriptive share of created whole-line lower
requests; it is not called a probability, and this document makes no causal
claim about the effect of these events on cycles.

## Source anchors

On Core95 observer commit `2fcde3eb3fce1502cc0f910cad6f807e530018c5`:

- `src/gpgpu-sim/dtc-l1-common.h`: `oo_frontend::access()` records a pending
  Tag eviction, invalidates the Tag, and increments after successful
  reallocation; `oo_frontend::complete()` generation-matches and clears the
  pending map.
- `src/gpgpu-sim/shader.cc`: whole-line OO `NEW_MISS` enqueues one candidate;
  `dtc_l1_oo_issue_lower_requests()` uses `kLogicalLineBytes` (128) unless
  the separate sector OO mode is active and then increments
  `m_dtc_l1_oo_lower_created`.

The same changes are mirrored on Core658 observer commit
`857671dde39b5f34ca03f2be973aae15ead5aca1`; D5 uses that lineage only for
the accepted 2DConvolution OO row.
