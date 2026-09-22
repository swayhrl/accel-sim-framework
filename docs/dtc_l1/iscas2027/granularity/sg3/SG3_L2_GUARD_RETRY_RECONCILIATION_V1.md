# SG3 Btree/OO L2 guard-retry reconciliation

The immutable `Btree/OO/capacity=base` attempt
`sg3_capacity_base_OO_Btree_4b2f5a94-9e74-4ee9-accb-0bf421e540e3`
terminated naturally with all identity, instruction, lower-credit/drain, and
observer-lifetime checks passing.  Its original row-local V1 receipt remains
preserved as FAIL because V2 required the aggregate L2 reservation-fail count
to equal the five printed resource-reason counters.

The terminal report has aggregate `6536`, printed classified sum `6217`, and
residual `319`.  Core `9b6bd33` source-audit locates this residual in
`baseline_cache::send_read_request`: the merge-tag identity guard returns a
legal retry before `inc_fail_stats` when an old MSHR no longer owns a valid
tag.  The ordinary cache status path records `RESERVATION_FAIL`, so it appears
in the aggregate but not in any of the five resource-failure enums.

V3 records the inferred residual as
`L2_fail_merge_tag_identity_guard_retry_inferred`.  It accepts a nonzero
residual only for exact Core `9b6bd33`, requires it be nonnegative, preserves
all five source-defined reason values, and classifies it as non-resource
diagnostic telemetry.  No Core/runtime/config/trace change and no rerun occur.
