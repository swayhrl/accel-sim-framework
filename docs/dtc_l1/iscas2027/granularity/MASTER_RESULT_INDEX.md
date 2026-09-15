# Wave-A coordination result index

This branch is coordination-only.  At bootstrap no Wave-A lane has accepted
scientific results, and no Wave-A simulator has been launched.  The host gate
recorded in `host/HOST_SNAPSHOT_WAVE_A_BOOTSTRAP_20260915T075111Z.tsv` blocks
new simulator launches while preserving every pre-existing attempt.

| Lane | Branch | Current state | Accepted artifact |
|---|---|---|---|
| SG0 | `hrl/iscas2027-dtc-sg0-audit-v0` | Static audit running | None yet |
| SG1 | `hrl/iscas2027-dtc-sg1-wholeline-controls-v0` | Static config audit running; execution gated | None yet |
| SG4A | `hrl/iscas2027-dtc-sg4a-logical-tag-v0` | Static reuse/config audit running; execution gated | None yet |
| SG5 | `hrl/iscas2027-dtc-sg5-lower-traffic-observer-v0` | Observer design running; execution gated | None yet |

The live TC80 CM5 campaign is external and is not an input/output namespace
for this investigation.
