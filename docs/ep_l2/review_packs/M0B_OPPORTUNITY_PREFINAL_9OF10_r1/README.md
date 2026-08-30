# M0b Opportunity Pre-final — 9 of 10

Status: `M0B_PREFINAL_9OF10_REVIEW_READY`.

This is an observation-only, data-review checkpoint on the promoted M0a+M1
parent.  Nine required units are `COMPLETE_VALID`; the isolated `scan` ON row
is still running and is deliberately excluded from every aggregate in this
pack.  No simulator mechanism is enabled: Unified Payload, RO pending-state,
TVD, adaptive policy, and performance headroom remain OFF/unimplemented.

The exact M0b Core producer is `9907b7e617ea0ee6580fb8156e985838720f08fa`.
The runtime-framework candidate frozen for the first ON evidence is
`8a0299cab19a658d34b7a2dc0b6d91e8373c121b`; later
`63084e5117640bc6fa4c729280517b25820e328d` changes only campaign/parser/
review helpers and is the runner-reported Framework SHA for the later rows.
It contains no M0b runtime producer change.  The executable used by every row
was built from the frozen runtime candidate before those helper commits.

The remaining scan is a breadth/temporal validation row, not a reason to
rerun any completed unit.  Its exact live state is frozen in
`RUNNING_SCAN_SNAPSHOT.csv`.

Evidence interpretation is intentionally narrow:

- RO: `UNCERTIFIED_CANDIDATE_ONLY`; no source-proven `SAFE_RO_ELIGIBLE` class
  exists in this producer.
- TVD: completed dirty-victim rows show no old resident payload handle live
  after reassignment; this is a current-model payload-identity observation.
- Shared payload: completed rows have no production non-resident allocation;
  final breadth remains pending scan.

All pre-final telemetry is non-functional observation evidence.  It must not
be construed as a performance result or authorization to implement M3/M4.
