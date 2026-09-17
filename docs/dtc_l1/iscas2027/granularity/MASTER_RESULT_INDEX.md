# Wave-A coordination result index

This branch is coordination-only. Each execution lane owns its own immutable
attempt namespace and commits its own accepted evidence. This index records
only branch heads and live-stage facts; it does not merge unclosed lane
evidence or make a performance conclusion. Every pre-existing attempt is
preserved.

| Lane | Branch | Current state | Accepted artifact |
|---|---|---|---|
| SG0 | `hrl/iscas2027-dtc-sg0-audit-v0` | Direct-audit checkpoint `721a767`; Chapter 4 lower-request granularity is explicitly classified as unspecified | No scientific run |
| SG1 | `hrl/iscas2027-dtc-sg1-wholeline-controls-v0` at `186181f` | Canonical D2B smoke is 5/6 strict PASS with B16-N/BICG live; canonical G6 (12) and FAST12 (24) matrices are predeclared but gated on smoke/G6 respectively. Historical mixed-Core rows remain nonfinal. | Immutable attempt evidence and plans on SG1 branch |
| SG4A | `hrl/iscas2027-dtc-sg4a-logical-tag-v0` at `741eca0` | Static one-dimensional audit passes; 12 BICG/GESUMMV logical32/64/80 IO/OO attempts are live. The 72-cell FAST12 missing-point matrix is frozen; 16 KiB remains a frozen reference. | Immutable live attempts and plan on SG4A branch |
| SG5 | `hrl/iscas2027-dtc-sg5-lower-traffic-observer-v0` at `f9c6c4d` | Canonical C1 has 12 strict OFF/ON pairs; the 36-cell canonical G6 observer matrix is frozen and resource-gated. Observer rows remain diagnostic only. | Canonical observer evidence and plan on SG5 branch |
| SG3 | `hrl/iscas2027-dtc-sg3-downstream-localization-v0` at `1a2b513` | Source audit and IO/OO NN/Btree observer equivalence pass. Twelve V1 sweeps are live but preserved OFF-control only; 96 fresh observer-ON G4 cells are frozen for later diagnostic execution. | Downstream telemetry evidence and plan on SG3 branch |

At the 2026-09-17T04:33Z coordination snapshot, Wave-A has 25 live children
(SG1 1, SG4A 12, SG3 12). The current policy forbids new launches until the
actual live count is below 24. The live TC80 CM5 campaign remains external and
is not an input/output namespace for this investigation.
