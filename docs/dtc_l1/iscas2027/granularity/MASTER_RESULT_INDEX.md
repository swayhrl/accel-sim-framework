# Wave-A coordination result index

This branch is coordination-only.  No Wave-A simulator has been launched and
no Wave-A scientific result is accepted.  The static checkpoints below passed
their own validators.  The current host gate continues to block new simulator
launches: the fresh resume snapshot has adequate workspace (71 GiB), but only
18.04% available memory and recurrent swap-in/out over `vmstat 1 10`.  Every
pre-existing attempt is preserved.

| Lane | Branch | Current state | Accepted artifact |
|---|---|---|---|
| SG0 | `hrl/iscas2027-dtc-sg0-audit-v0` | Source audit checkpoint `000901b2`; Chapter 4 direct-review gate blocked | No scientific run |
| SG1 | `hrl/iscas2027-dtc-sg1-wholeline-controls-v0` | Config checkpoint `d3c52a4`; smoke/G6/FAST12 host-gated | No scientific run |
| SG4A | `hrl/iscas2027-dtc-sg4a-logical-tag-v0` | Logical geometry checkpoint `6a069003`; FAST12 host-gated | No scientific run |
| SG5 | `hrl/iscas2027-dtc-sg5-lower-traffic-observer-v0` | Source-placement checkpoint `01a60366`; dedicated Core observer `afe978ea` is implemented but unbuilt; fixtures/G6 host-gated | No scientific run |

The live TC80 CM5 campaign is external and is not an input/output namespace
for this investigation.
