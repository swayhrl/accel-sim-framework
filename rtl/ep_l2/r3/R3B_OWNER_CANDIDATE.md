# R3B isolated forward-fill ownership candidate

Inherited R3A two GEN ports and transaction phase sharing are unchanged.
Invariant preparation passed using actual role/owner/map transition under the
explicit legal event premises in R3_PORT_AND_STATE_CONTRACT. R3B replaces only
fill ownership with roleRESIDENT + GEN + tag_live[fill_tag] + forward map PID
+ unchanged nonzero/pending sector guards. The new full1024x11 map read is
real standard-cell logic. Payload owner output no longer drives functional
logic, so its10 FF/word are removed, not moved outside the cost cut.

All payload pins/ready/pending/dirty, roles/GEN32, WAD state and1024 Tag map
remain. Static B16/S64 use the same identity rule with proved constant maps;
all relevant lookup/live/compare gates are charged. No capacity, service,
pipeline or II change. No effect is inferred for official SIM/Lane5 results.

This source is NOT YET QUALIFIED. It requires actual bounded controller R2/B
comparison, full production suites, ten Lane3 byte vectors, highest bank3 slot,
all simultaneous GEN cases, stale fill/rebind/pin/rollback and same-library
three-mode mapping/two-period STA. An owner abstract proof is insufficient.
Tag-index sector/pin organization remains an explicit separate port-ledger
exploration; inverse external-pin lookup is not a free implementation.

The added fill lookup uses the same actual variable Tag-map selection idiom
as the existing frontend old_pid read. All1024x11 input bits and its mapped
selection gates are real cost. It supports the small symbolic Tag count
without the R2 helper BLOCK/IW limitation; full map capacity remains1024.

Final static specialization: B16/S64 use the already-proved resident PID==Tag
invariant directly. Their fill guard needs no new Tag-live read or dynamic
Tag-map. Unified retains the charged forward map+live lookup. This is a fair
common MODE specialization, not an intentionally weaker static baseline. B0
partial production runs remain archived at their exact old source and are not
claimed as validation of this new source; the final candidate gets new runs.
