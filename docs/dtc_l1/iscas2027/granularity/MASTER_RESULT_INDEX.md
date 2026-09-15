# Wave-A coordination result index

This branch is coordination-only. Each execution lane owns its own immutable
attempt namespace and commits its own accepted evidence. The static
checkpoints below passed their own validators. Under the latest resource
policy, Wave-A runs at a combined ceiling of four simulators; the documented
4-to-8 resource gate remains HOLD_AT_4. Every pre-existing attempt is
preserved.

| Lane | Branch | Current state | Accepted artifact |
|---|---|---|---|
| SG0 | `hrl/iscas2027-dtc-sg0-audit-v0` | Direct-audit checkpoint `721a767`; Chapter 4 lower-request granularity is explicitly classified as unspecified | No scientific run |
| SG1 | `hrl/iscas2027-dtc-sg1-wholeline-controls-v0` | Runner checkpoint `7d8d9b2`; five smoke rows strictly pass; B16-N/BICG is still active | Immutable attempt evidence on SG1 branch |
| SG4A | `hrl/iscas2027-dtc-sg4a-logical-tag-v0` | Logical geometry checkpoint `6a069003`; bulk runs await higher-priority SG1 G6 and SG5 qualification | No scientific run |
| SG5 | `hrl/iscas2027-dtc-sg5-lower-traffic-observer-v0` | Equivalence checkpoint `e7e4f59`; all eight frozen-mode NN/Btree OFF/ON pairs strictly pass; NORMAL waits for SG1 identity | Immutable attempt evidence on SG5 branch |

The live TC80 CM5 campaign is external and is not an input/output namespace
for this investigation.
