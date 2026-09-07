# FAST64.1 Progress Checkpoint

Status: **ACTIVE_TELEMETRY_RERUN_PENDING — REVIEW CHECKPOINT ONLY**

Snapshot: `2026-09-07T08:27:49Z`

This checkpoint makes the active FAST64.1 state reviewable.  It is not a
stage PASS artifact, changes no simulator/configuration/trace behavior, and
does not authorize FAST64.2.

## Immutable stage authority

| item | identity / status |
| --- | --- |
| Framework branch / HEAD | `hrl/decoupled-l1-fast64-v0` / `db5fbf84cd020012dc7702c72526df8aebbd3243` |
| original Core behavior anchor | `15cfa76ed3b041fa5b78161dfba02bae1e6d7fe9` |
| telemetry-only Core repair | `bbcbb5e7565417102087bc80b14c349b4e568c05` (`FAST64-1-TELE-001`) |
| formal r1 runtime | `/tmp/dtc-fast64-telemetry-build-sEWez4/accel-sim.out`, SHA-256 `6a8743b4d7adc7f56d40aafdf913718c9e0ad13641e962aa8ef5e3ee35d4f041` |
| observer | A1, runtime-stat `500000`, overlay SHA `2c2a6a272c129243626617e2b80ded798b30ccb09377d07a2ca453209074074e` |
| FAST12 payload freeze | 12 workloads, 629 ordered trace members, 9,162,136,500 bytes; `generated/FAST64_PAYLOAD_MANIFEST.tsv` and `generated/FAST64_PAYLOAD_MEMBERS.tsv` |
| config-diff check | 124 rows: one required DTC mode selector and 123 common entries; zero `ERROR_UNRELATED_DIFFERENCE` |

The frozen payload roots remain locally readable.  All 12 ordered-set hashes
and the C2P-canonical provenance label are present.  The resolved 64x1 shell
and DTC Base/IO/OO geometry remain the previously documented FAST64.1
candidate; no C2P L1/peer mechanism was imported.

## Original-Core anchor progress

These rows used old runtime
`/tmp/dtc-fast64-build-bnAg9w/accel-sim.out`, SHA-256
`75f37ef8deb36fdcba4ae2615ad9c0b229998f3527ef1a52a14b56a29ca3fc8d`.
They are preserved anchors, never formal r1 rows.

| row / external run namespace | terminal status | terminal UTC | cycles / instructions | accounting evidence | disposition |
| --- | --- | --- | ---: | --- | --- |
| `fast64_1_bicg_oo_cap8192_a1` | exit 0 | `2026-09-07T06:49:59Z` | 47,231,655 / 145,666,048 | OO lower created=issued=responses=17,814,913; dependencies 18,350,080=closed; inflight/PIB/active-refs/lower=0; credits acquired=released | `PRE_REPAIR_TELEMETRY_INCOMPLETE_ANCHOR` |
| `fast64_1_bicg_oo_cap1048576_a1` | exit 0 | `2026-09-07T06:58:30Z` | 47,231,655 / 145,666,048 | same closure values as 8192 row | `PRE_REPAIR_TELEMETRY_INCOMPLETE_ANCHOR` |

Both rows consumed BICG `kernelslist.g` SHA-256
`388740a7be05d5596ffb77ff3f4812ff93f41afa0ee5082c1e179745cf5e0a4b`.
Their config SHA-256 values are respectively
`546c68f96d47f4650703ccfbc925bd789f923501d5607a77e79ca4845f234caa`
and `b9c8716bffb4c35dad31f568fd9288e2bb6cbda995997a9912ff2b3ddab5b6d6`.
The error scan found no assertion, fatal, actual deadlock, trace error, or
output mismatch.  A configuration echo of `-gpgpu_deadlock_detect 1` is not a
deadlock event.

Do not use the matching cycles as a non-binding-cap result: the old runtime
does not expose the formally required OO `DTC_L1_lower_cap_full_events` field.
The new-Core r1 pair must independently strict-parse and compare it.

## Live original-Core rows — preserve without intervention

All rows below were `R` and their CPU time was advancing at the snapshot.  No
signal, debugger, restart, timeout, affinity change, rename, cleanup, or
output modification is authorized.

| PID | row / output namespace | elapsed / CPU | RSS | state |
| ---: | --- | --- | ---: | --- |
| 3258353 | `fast64_1_bicg_base_cap8192_a1` | 04:58:42 / 04:56:12 | 2,367,488 KiB | R |
| 3258366 | `fast64_1_bicg_io_cap1048576_a1` | 04:58:42 / 04:57:28 | 2,420,736 KiB | R |
| 3258367 | `fast64_1_bicg_io_cap8192_a1` | 04:58:42 / 04:57:28 | 2,420,736 KiB | R |
| 3258374 | `fast64_1_gesummv_io_cap1048576_a1` | 04:58:42 / 04:57:19 | 3,039,232 KiB | R |
| 3258378 | `fast64_1_gesummv_io_cap8192_a1` | 04:58:42 / 04:57:28 | 3,039,232 KiB | R |

## Formal r1 recovery state

The following live controllers are preserved:

| PID | role | state |
| ---: | --- | --- |
| 3261725 | original qualification collector | live, waiting for old rows |
| 3291777 | deferred new-Core telemetry-rerun dispatcher | live, fail-closed, waits all seven old rows to exit 0 |
| 3362160 | new-Core r1 collector | live, waiting for r1 rows |

At this snapshot no `fast64_1r1_*` namespace and no
`generated/qualification_r1/` result file exists.  This is expected: the
dispatcher verifies every old row's natural `exit=0`, the repaired Core/runtime
identity, and target absence before it dispatches the seven isolated r1 rows.
The r1 rows are the only rows eligible to close the BICG IO/OO and GESUMMV IO
8192-versus-1048576 qualification.

## HARD-gate ledger

| FAST64.1 requirement | current evidence | status |
| --- | --- | --- |
| resolved configs; 64x1 DTC geometry; no unrelated config difference | resolved diff, NN telemetry triplet, `FAST64_1_PLATFORM.md` | PASS |
| frozen FAST12 payload identity | generated manifests; this checkpoint | PASS |
| new-Core NN Base/IO/OO natural terminal and strict telemetry regression | `generated/telemetry_regression/` | PASS |
| BICG Base/IO/OO new-Core smoke and terminal strict accounting | r1 replacements not yet dispatched | PENDING |
| BICG IO/OO candidate-vs-high exact comparison, candidate cap-full zero | r1 replacements not yet dispatched | PENDING |
| GESUMMV IO candidate-vs-high exact comparison, candidate cap-full zero | r1 replacements not yet dispatched | PENDING |
| formal row runtime/Core/config/observer provenance | r1 replacements not yet dispatched | PENDING |

## Review conclusion and next action

There is no new HARD failure and no researcher-decision boundary.  The two
completed old OO rows are sound lifecycle anchors but deliberately cannot be
relabeled as formal telemetry qualification.  The only next action is to let
the five live old rows naturally terminate, allow the existing fail-closed
controller to dispatch r1 exactly once, then run the existing strict row
validator and non-binding-cap comparator.  No FAST64.2 work may start before
every pending FAST64.1 HARD item passes.
