# M2-D runtime-memory diagnosis

Result: `PASS`; original `G2-4` runtime replay is also `PASS`.

This pack is the review entry for the temporary M2-D blocker.  It establishes
that the observed 32–65 GiB pre-replay allocation was not an M2 TLB/PTW
footprint.  A stale Framework trace object had retained the old
`shader_core_config` layout after Core headers changed.  It read an invalid
`n_simt_clusters`, producing a 32 GiB `new[]` request during SIMT-cluster
creation.  The fixed dependency generation rebuilds Framework objects when
Core headers change.

The replay path then exposed a second concrete M2 integration defect: the
translation-pending early return set `COAL_STALL` but left the stall access-type
uninitialized.  The one-line classification completion fixes only statistics
indexing and preserves translation timing/resource semantics.

Source anchors:

- Core runtime-fix commit: `e7999554200760b31b4efe16d98e050370e1ea71`.
- Framework dependency-fix commit: `4012be3606c300d11e7b34826ee1cb22b0852b93`.
- Diagnosis started from Core `c1431e01f593719f9201d4ad4d7666bebead8a4f`
  and Framework `341d33311efb5725d19b94bd1d93df3c21d831b8`.

Read `VALIDATION_SUMMARY.md` after this file.  Raw logs remain under
`/tmp/m2d-runtime-memory/`; their index is committed, not the large logs.
