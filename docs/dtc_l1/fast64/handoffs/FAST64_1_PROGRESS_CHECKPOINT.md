# FAST64.1 Progress Checkpoint

Status: **ACTIVE_R1_QUALIFICATION_RUNNING — REVIEW CHECKPOINT ONLY**

Snapshot: `2026-09-07T08:27:49Z`

This checkpoint makes the active FAST64.1 state reviewable.  It is not a
stage PASS artifact, changes no simulator/configuration/trace behavior, and
does not authorize FAST64.2.

## Immutable stage authority

| item | identity / status |
| --- | --- |
| execution snapshot source HEAD | Framework `hrl/decoupled-l1-fast64-v0` at `db5fbf84cd020012dc7702c72526df8aebbd3243` |
| review/checkpoint commit | `e0e4debdad5dfc0404a8f5695e94b48a45b45fa7` |
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
| 3291777 | deferred new-Core telemetry-rerun dispatcher | live, preserved historical controller that waits all seven old rows; it is not the immediate r1 scheduler |
| 3657888 | new-Core r1 collector | live, restarted before r1 launch with exact execution-source provenance handling |

## Review-authorized r1 immediate dispatch

Dispatch occurred at `2026-09-07T08:49:18Z` after a fresh resource gate:
cpuset `0-511`, CPU quota 384 cores, a 60-second cgroup sample with zero CFS
throttling, `MemAvailable` about 120 GiB, zero `vmstat si/so`, no iowait, and
69 GiB output free space. Seven one-core rows are safe under that measured
envelope; their bindings do not change any original-Core row.

This is the required provenance distinction:

| identity kind | value |
| --- | --- |
| execution snapshot source HEAD | `037f008b330eb230353b60edf126d6be9f45afdc` |
| review/checkpoint commit | the commit containing this checkpoint update; it must never be substituted for the execution source HEAD |
| formal Core source | `bbcbb5e7565417102087bc80b14c349b4e568c05` |
| formal runtime SHA-256 | `6a8743b4d7adc7f56d40aafdf913718c9e0ad13641e962aa8ef5e3ee35d4f041` |
| observer overlay SHA-256 | `2c2a6a272c129243626617e2b80ded798b30ccb09377d07a2ca453209074074e` |

All target namespaces were absent in a dry preflight. The original deferred
dispatcher remains untouched; when its historical wait completes, pre-existing
r1 namespaces make it fail closed rather than duplicate a row. Its role is not
the active r1 scheduler. The stale idle r1 evidence collector was replaced
before launch only because it carried an old Framework SHA; no simulator or
original-Core row was signalled, restarted, renamed, or otherwise modified.

| r1 row | simulator PID | CPU | namespace | launch state |
| --- | ---: | ---: | --- | --- |
| BICG Base 8192 | 3658012 | 74 | `fast64_1r1_bicg_base_cap8192_a1` | `R`, live |
| BICG IO 8192 | 3658027 | 75 | `fast64_1r1_bicg_io_cap8192_a1` | `R`, live |
| BICG OO 8192 | 3658034 | 76 | `fast64_1r1_bicg_oo_cap8192_a1` | `R`, live |
| BICG IO 1048576 | 3658057 | 77 | `fast64_1r1_bicg_io_cap1048576_a1` | `R`, live |
| BICG OO 1048576 | 3658048 | 78 | `fast64_1r1_bicg_oo_cap1048576_a1` | `R`, live |
| GESUMMV IO 8192 | 3658060 | 79 | `fast64_1r1_gesummv_io_cap8192_a1` | `R`, live |
| GESUMMV IO 1048576 | 3658062 | 80 | `fast64_1r1_gesummv_io_cap1048576_a1` | `R`, live |

At the non-invasive start observation each simulator had advanced roughly two
minutes of CPU time, remained runnable, and had the expected runtime/config/
trace command identity. The only `deadlock` scan hit was the configuration echo
`-gpgpu_deadlock_detect 1`; no assertion, fatal, output mismatch, or actual
deadlock is currently observed. CPU-time alone is startup evidence, not a
claim of simulator-level completion or cap qualification.

The r1 rows are the only rows eligible to close BICG IO/OO and GESUMMV IO
8192-versus-1048576 qualification. They must naturally terminate, strict-parse
and satisfy every FAST64.1 HARD comparison before FAST64.2 can begin.

## HARD-gate ledger

| FAST64.1 requirement | current evidence | status |
| --- | --- | --- |
| resolved configs; 64x1 DTC geometry; no unrelated config difference | resolved diff, NN telemetry triplet, `FAST64_1_PLATFORM.md` | PASS |
| frozen FAST12 payload identity | generated manifests; this checkpoint | PASS |
| new-Core NN Base/IO/OO natural terminal and strict telemetry regression | `generated/telemetry_regression/` | PASS |
| BICG Base/IO/OO new-Core smoke and terminal strict accounting; BICG Base 8192 global cap-full zero | seven r1 rows live; natural terminal pending | PENDING |
| BICG IO/OO candidate-vs-high exact comparison; each 8192 candidate global cap-full zero | r1 BICG comparison pairs live | PENDING |
| GESUMMV IO candidate-vs-high exact comparison; 8192 candidate global cap-full zero | r1 GESUMMV comparison pair live | PENDING |
| formal row runtime/Core/config/observer/payload provenance and exact execution source `037f008b…` | launch manifests recorded; terminal strict validation pending | PENDING |

## Review conclusion and next action

There is no new HARD failure and no researcher-decision boundary. The two
completed old OO rows are sound lifecycle anchors but deliberately cannot be
relabeled as formal telemetry qualification. The seven isolated r1 rows are
running under the formal instrumented Core; after their natural terminal
states, the collector performs strict validation and the non-binding-cap
comparators. No FAST64.2 work may start before every pending FAST64.1 HARD
item passes.
