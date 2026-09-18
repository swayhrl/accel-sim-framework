# C16WARP1 accounting closure

Formal closure requires all of the following:

- `producer_logical_records == receiver_packets_accepted == finalized_c16warp1_records_written`
- `producer_overflow == 0`
- no sequence gap, duplicate, or malformed packet
- `receiver_terminal_seen == true` and `receiver_terminal_count == 1`

No raw legacy drop field is invented.  A passing receipt is reported as
`NO_UNACCOUNTED_RECORDS_PROVEN`; it is derived from the independent counters and
sequence closure.
