# Fair sub-entry profile implementation

The candidate remains `REFERENCE_APPROX_SUBENTRY_16`: 64KiB-only, 16 leaves
per base-tag group, with group allocation/replacement and selected-leaf
validity distinct from an exact-page entry.

The underlying `tlb_config` computes set count from `entries / assoc`; it does
not retain the historical 48-set shape. C10-A exposed `subentry_tlb::sets()`
solely for focused fair-profile validation and adds:

- `F1`: `G=96`, 16-way, six sets, 1,536 leaf capacity, 59,802 charged bits;
- `F8`: `G=32`, 16-way, two sets, 512 leaf capacity after charged Segment
  replicas, 57,734 charged bits;
- leaf invalidation; ASID flush; global flush; empty-group way release.

The test source fills sibling leaves, invalidates one while retaining the
group, invalidates the last leaf and verifies the group frees, then checks ASID
and global flush. Configuration validation remains 64KiB-only for sub-entry;
2MiB requires a separate exact diagnostic.

Historical 768 groups is preserved only as H0 with
`HISTORICAL_UNFAIR_SPECULATIVE_CANDIDATE_DO_NOT_SELECT`. The static validator
rejects it as an official arm. Captured-generation stale-fill discard remains
unimplemented and is deferred to C10-B.
