# M1F implementation semantics

`oracle_target`, `protection_eligible`, and `protected_admitted` are distinct.
Every qweight target remains a target for target-access/hit/miss statistics.
Only the frozen stable address subset enters M1 protected admission and
replacement; filtered targets use the ordinary M1 path. Existing hard quota,
pending accounting, ordinary borrowing, set-local victims, quota-full denial,
no-promotion behavior, and sector metadata remain authoritative.

The selector is deterministic by target class plus region-relative 128-byte
line index. Sectors, retries, repeated fills, and decode repetitions therefore
have the same eligibility. It does not use access count, kernel identity,
decode iteration, time, or mutable random state.
