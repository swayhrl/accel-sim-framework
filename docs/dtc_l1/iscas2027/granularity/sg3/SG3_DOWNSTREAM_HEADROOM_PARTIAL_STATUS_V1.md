# SG3 downstream-headroom partial status V1

Snapshot time: `2026-09-24T00:21:11Z`.

This is an interim review snapshot for the committed Phase-B queue=128
intervention.  It preserves the single completed immutable attempt and does
not change the Phase-A trigger or Phase-B definition.

## Completed receipt

`BICG/OO/queue=128` (`88908b04`) naturally exits and strict-PASSes with the
default DTC cap=8192, the queue=128 resolved L2 config echo, exact Core/runtime
and trace/config-chain identity, terminal drain, and observer closure.  The
data row is in `SG3_DOWNSTREAM_HEADROOM_PARTIAL_SNAPSHOT_V1.tsv`.

Compared with its accepted BICG/OO default row, its source-defined
`MISS_QUEUE_FULL` count falls from 43,594,150 to zero, but cycles change from
47,231,655 to 47,588,121 (+0.75%) and average lower lifetime changes from
5,612.70 to 5,692.26 cycles.  This is a measured one-row observation only;
it is not evidence that queue headroom is sufficient or insufficient for the
four-row intervention family.

## Active immutable attempts

The following rows remain active and are deliberately absent from the data
snapshot until they have terminal and strict-validation receipts:

- `BICG/IO` — `82949efb-c7b6-494a-83e4-f615605bb106`
- `GESUMMV/IO` — `e44f570d-16de-4550-bb61-52792caebfb2`
- `GESUMMV/OO` — `959a227a-8ed5-4b5c-9277-313cd947eabb`

No port, combined queue+port, capacity, MSHR, or other expansion is
authorized from this partial result.  The final decision remains deferred to
the predeclared four-row queue family and review-pack closure.
