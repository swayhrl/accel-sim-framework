# SG4A R0 validation reconciliation

The initial R0 validation invocation correctly preserved FAIL receipts for the
four IO attempts.  Its validator, however, required
`DTC_L1_io_pending_tag_evictions`, which frozen Core95 (`95ccdb7a`) never
emits.  Core95 does emit `DTC_L1_io_physical_allocations`,
`DTC_L1_io_tag_evictions`, duplicate-after-eviction, lower-create/response,
and lower-credit counters.

The validator now requires only emitted IO fields and retains UUID, natural
exit, workload/mode/geometry, authority trace/instruction, error scan,
lower-drain, and credit-drain checks.  The four original FAIL JSON files are
immutable preserved evidence; each corresponding
`VALIDATION_RECONCILIATION_V1.json` is a named revalidation receipt.  No
simulator was relaunched.
