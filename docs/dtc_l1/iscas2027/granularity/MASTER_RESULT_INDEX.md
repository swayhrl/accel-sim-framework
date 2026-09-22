# Wave-A coordination result index

This branch is coordination-only. Each execution lane owns its own immutable
attempt namespace and commits its own accepted evidence. This index records
only branch heads and live-stage facts; it does not merge unclosed lane
evidence or make a performance conclusion. Every pre-existing attempt is
preserved.

| Lane | Branch | Current state | Accepted artifact |
|---|---|---|---|
| SG0 | `hrl/iscas2027-dtc-sg0-audit-v0` | Direct-audit checkpoint `721a767`; Chapter 4 lower-request granularity is explicitly classified as unspecified | No scientific run |
| SG1 | `hrl/iscas2027-dtc-sg1-wholeline-controls-v0` at `a3271e7` | Canonical D2B smoke is 5/6 strict PASS. B16-N/BICG `e7fb57a0` naturally exited 0, but is pending strict validation and therefore not accepted. Canonical G6 (12) and FAST12 (24) remain gated; historical mixed-Core rows remain nonfinal. | Immutable attempts, source-closure validator, and plans on SG1 branch |
| SG4A | `hrl/iscas2027-dtc-sg4a-logical-tag-v0` at `705691f` | All 12 launched rows have terminal receipts: eight exit 0 pending strict validation; four exit 1 are preserved without numeric interpretation. BICG/logical80 IO/OO remain registry-recorded deadlocks; GESUMMV/logical80 IO/OO await registry audit. The 72-cell plan remains frozen. | Immutable attempts, failure registry, and plan on SG4A branch |
| SG5 | `hrl/iscas2027-dtc-sg5-lower-traffic-observer-v0` at `239dbb5` | Canonical C1 has 12 strict OFF/ON pairs. C2 GESUMMV/B16-S retry `c4ee4642` naturally exited 0 but is pending strict validation; UUID `50e5c0da` remains a preserved no-terminal transport failure. The fixed 36-cell canonical G6 observer matrix remains diagnostic only. | Canonical observer evidence, transport registry, and plan on SG5 branch |
| SG3 | `hrl/iscas2027-dtc-sg3-downstream-localization-v0` at `f0b0e3a` | Source audit and IO/OO NN/Btree observer equivalence pass. Twelve V1 sweeps naturally exited 0 but are unvalidated OFF controls; the frozen 96 observer-ON G4 cells remain the final diagnostic path. | Downstream telemetry evidence, field-map validator, and plan on SG3 branch |

At this execution checkpoint, Wave-A has no live children. This does not make
any terminal row accepted: strict validation remains mandatory. New launches
are hard-stopped because `/workspace` has 7.7 GiB free, below the 35 GiB
contract minimum. The TC80 CM5 campaign remains external and is not an
input/output namespace for this investigation.
