# Wave-A coordination result index

This branch is coordination-only. Each execution lane owns its own immutable
attempt namespace and commits its own accepted evidence. The static
checkpoints below passed their own validators. The latest five-minute
controlled-ramp snapshot passes the 4-to-8 gate, so Wave-A now runs at a
combined ceiling of eight simulators. Every pre-existing attempt is preserved.

| Lane | Branch | Current state | Accepted artifact |
|---|---|---|---|
| SG0 | `hrl/iscas2027-dtc-sg0-audit-v0` | Direct-audit checkpoint `721a767`; Chapter 4 lower-request granularity is explicitly classified as unspecified | No scientific run |
| SG1 | `hrl/iscas2027-dtc-sg1-wholeline-controls-v0` | Smoke 6/6 passes; BICG/Btree are exact-identity G6 reuse; Gaussian B16-N/TC80-N strictly pass; six G6 rows remain active | Immutable attempt evidence on SG1 branch |
| SG4A | `hrl/iscas2027-dtc-sg4a-logical-tag-v0` | Logical geometry checkpoint `6a069003`; bulk runs await higher-priority SG1 G6 and SG5 qualification | No scientific run |
| SG5 | `hrl/iscas2027-dtc-sg5-lower-traffic-observer-v0` | All 12 supported NN/Btree OFF/ON pairs pass; B16-S/TC80-S GESUMMV observer diagnostics are active | Immutable attempt evidence on SG5 branch |

The live TC80 CM5 campaign is external and is not an input/output namespace
for this investigation.
