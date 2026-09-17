# Wave-A coordination result index

This branch is coordination-only. Each execution lane owns its own immutable
attempt namespace and commits its own accepted evidence. This index records
only branch heads and live-stage facts; it does not merge unclosed lane
evidence or make a performance conclusion. Every pre-existing attempt is
preserved.

| Lane | Branch | Current state | Accepted artifact |
|---|---|---|---|
| SG0 | `hrl/iscas2027-dtc-sg0-audit-v0` | Direct-audit checkpoint `721a767`; Chapter 4 lower-request granularity is explicitly classified as unspecified | No scientific run |
| SG1 | `hrl/iscas2027-dtc-sg1-wholeline-controls-v0` at `13577a7` | Canonical D2B smoke is 5/6 strict PASS with B16-N/BICG live; canonical G6 (12) and FAST12 (24) matrices are predeclared but gated on smoke/G6 respectively. Historical mixed-Core rows remain nonfinal. | Immutable attempt evidence and plans on SG1 branch |
| SG4A | `hrl/iscas2027-dtc-sg4a-logical-tag-v0` at `705691f` | Static one-dimensional audit passes; 10 BICG/GESUMMV logical32/64/80 IO/OO attempts are live. BICG/logical80 UUIDs `8bd134e8` (OO) and `49262e70` (IO) naturally ended with Core95 deadlock exit 1 and are hash-recorded as preserved nonaccepted failures. The 72-cell FAST12 missing-point matrix is frozen; 16 KiB remains a frozen reference. | Immutable live attempts, failure registry, and plan on SG4A branch |
| SG5 | `hrl/iscas2027-dtc-sg5-lower-traffic-observer-v0` at `239dbb5` | Canonical C1 has 12 strict OFF/ON pairs. C2 GESUMMV/B16-S UUID `50e5c0da` is a preserved no-terminal transport failure; detached retry `c4ee4642` is live. The fixed 36-cell canonical G6 observer matrix remains diagnostic only. | Canonical observer evidence, transport registry, and plan on SG5 branch |
| SG3 | `hrl/iscas2027-dtc-sg3-downstream-localization-v0` at `1a2b513` | Source audit and IO/OO NN/Btree observer equivalence pass. Twelve V1 sweeps are live but preserved OFF-control only; 96 fresh observer-ON G4 cells are frozen for later diagnostic execution. | Downstream telemetry evidence and plan on SG3 branch |

At the 2026-09-17T05:36Z coordination snapshot, Wave-A has 24 live children
(SG1 1, SG4A 10, SG3 12, SG5 1). The current policy forbids new launches until
the actual live count is below 24; this snapshot therefore remains a hold. The
live TC80 CM5 campaign remains external and is not an input/output namespace
for this investigation.
