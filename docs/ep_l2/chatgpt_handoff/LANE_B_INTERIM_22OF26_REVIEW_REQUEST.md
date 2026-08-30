# EP-L2 Lane B — Interim 22/26 Review Request

Status: **authorized immediately while the remaining four D512 simulator jobs continue untouched.**

Purpose: give ChatGPT an early, final-format review surface for the already-computed D512 calibration evidence. This is a review/analysis snapshot only. It must not delay, restart, kill, modify, or duplicate the four live D512 runs.

## 1. Non-interference boundary

Do not disturb any currently running D512 simulator process or its worktree/result directory.

In particular:

```text
- do not kill/restart/rebuild the four live jobs;
- do not move/rename their result roots;
- do not modify the frozen D512 Core/Framework/config candidate;
- do not relaunch rows that are already COMPLETE_VALID;
- do not wait for the remaining jobs before publishing this interim snapshot.
```

The automatic promotion monitor may continue running normally.

## 2. Snapshot status and maturity

Use a clearly non-final status such as:

```text
LANE_B_INTERIM_D512_22_OF_26
```

Do NOT declare:

```text
D512_MIRROR_COMPLETE
PRIMARY_BASELINE
BASELINE_DECISION
```

If `D512_READY` has not yet been reached because Banked `scan` preflight is still running, preserve that fact explicitly.

Each row must retain its actual maturity, e.g.:

```text
COMPLETE_VALID + SPECULATIVE_PENDING_GATE
```

or, if the relevant promotion gates have already passed for that exact candidate,

```text
COMPLETE_VALID + PROMOTED_VALID_CALIBRATION
```

Never rewrite maturity merely to make the interim pack look complete.

## 3. Required source/config identity

Record exact immutable identities used by the 22 completed rows:

```text
Core candidate SHA
Framework candidate SHA
runtime config composite SHA256
D512 overlays / hashes
trace identity
frequency = 850 MHz
descriptor capacity = 512
Line MSHR = 128
per-address cap = 32
L1 = frozen BASE
```

Verify all 22 completed rows use one intended candidate/source/config family. Any mismatch is `INVALID_FOR_CALIBRATION` and must be surfaced rather than normalized away.

## 4. D256 equivalence evidence

The interim pack must include the completed D256 backward-equivalence state:

```text
vectorAdd_4M
spmv
scan
```

For each, show at least:

```text
status
cycles
instructions
selected L1/L2/DRAM counters
terminal invariants
parsed-output equality / hashes
exact reference source/config
exact generalized-source/config
```

Since `scan` is now reported complete, include the machine-readable `D256_EQ_SCAN_GATE.json` and summarize whether the full B3 equivalence gate is PASS.

If B3 is now fully PASS, publish the exact equivalence evidence path that Lane D can later consume in its calibration lineage contract.

## 5. D512 preflight state

Report preflight status per required workload:

```text
vectorAdd_4M
scan
spmv
FWT_7_21
low-pressure control (sad or btree)
Legacy paired control as actually scheduled
```

For completed preflight rows show:

```text
COMPLETE_VALID / failure status
cycles D256 vs D512
descriptor need/block
descriptor avg/p95/max
Line-MSHR avg/p95/max/full
per-address cap
L1 pressure
WAD/payload/bank
L2->DRAM/scheduler
native physical DRAM bus metric where available
5K temporal pressure
```

Explicitly verify the >256 telemetry requirement on at least one completed natural D512 row if already available:

```text
descriptor_max > 256
and preferably descriptor_p95 > 256 where naturally expected
```

If Banked `scan` is still running and therefore `D512_PREFLIGHT_PASS` cannot yet be declared, mark preflight as `PENDING_RUNNING_SCAN`; do not block publication of this interim pack.

## 6. 22/26 mirror provenance audit

For all 22 completed D512 mirror rows verify:

```text
run_status == COMPLETE_VALID
normal exit
expected frozen Core SHA
expected frozen Framework SHA
expected runtime config hash
trace identity
parser success
terminal_clean = 1
payload consistency = 1
required C7e telemetry artifacts present
maturity / unresolved promotion gates explicitly recorded
```

Include a machine-readable status table.

## 7. Interim pairwise analysis

For every D512 workload with a matching D256 formal baseline and complete D512 evidence, provide a conservative comparison containing at least:

```text
D256 cycles
D512 cycles
speedup/slowdown

descriptor block / need movement
descriptor occupancy movement
Line-MSHR pressure movement
per-address cap movement
L1 blocker movement
WAD movement
payload / true bank conflict movement
L2->DRAM pressure
scheduler pressure
native application DRAM bus utilization
5K sustained-vs-bursty descriptors/lower-path behavior
```

Classify only provisionally using the established vocabulary:

```text
DESCRIPTOR_CAUSAL_SENSITIVE
DESCRIPTOR_THROTTLE_MOVES_DOWNSTREAM
DESCRIPTOR_PRESSURE_LOW_PERF_SENSITIVITY
D512_STILL_DESCRIPTOR_LIMITED
INSUFFICIENT_EVIDENCE
```

Do not infer causality from occupancy alone.

Do not extrapolate the four unfinished rows.

## 8. Research questions to answer in the interim report

Use the completed data to answer, with evidence and caveats:

1. Does D512 materially reduce/eliminate the D256 shared-descriptor blocking observed in vectorAdd/scan/spmv/convolution/FWT workloads?
2. After descriptor relief, does Line MSHR occupancy/full pressure emerge naturally?
3. Does performance improve when descriptor pressure falls, or does pressure mainly move to L1 / L2->DRAM / scheduler / DRAM bus?
4. Is per-address cap=32 becoming material after D512?
5. Does D512 change WAD/payload/bank pressure materially?
6. Which workloads already support or weaken an MSHR-centric RO no-MSHR motivation?
7. Does D512 appear hardware-plausible given the already-reviewed 256->512 metadata cost estimate?

Treat every conclusion as `INTERIM_22_OF_26` until the full mirror and promotion gates finish.

## 9. Running-job snapshot

Record the four unfinished rows read-only:

```text
workload
variant
PID/job identifier if available
start time / elapsed wall time
result path
basic health / file-growth state
```

No repeated expensive scraping and no interaction with the simulator processes.

## 10. Required review pack

Create a directly browsable pack, suggested path:

```text
docs/ep_l2/review_packs/D512_CALIBRATION_INTERIM_22OF26_r1/
```

Suggested contents:

```text
README.md
INTERIM_STATUS.md
SOURCE_ANCHORS.md
D256_EQUIVALENCE.md
D256_EQUIVALENCE_STATUS.csv
D512_PREFLIGHT_INTERIM.md
D512_RUN_STATUS_22OF26.csv
D512_PROVENANCE_AUDIT_22OF26.csv
D512_INTERIM_COMPARISON.csv
D512_INTERIM_RESOURCE_PRESSURE.csv
D512_INTERIM_TEMPORAL.csv
D512_INTERIM_RESEARCH_FINDINGS.md
RUNNING_JOBS_SNAPSHOT.csv
OPEN_ISSUES.md
RAW_LOG_INDEX.tsv
SHA256SUMS
```

Reuse the same parser/analyzer semantics intended for final Lane-B closeout. Do not fork a separate contradictory interim analysis path.

## 11. Handoff

Publish/update:

```text
docs/ep_l2/codex_handoff/LANE_B_LATEST.md
```

with:

```text
Stage: Descriptor-512 Calibration — Interim 22/26
Status: LANE_B_INTERIM_D512_22_OF_26
Core / Framework / config identity
D256 equivalence gate PASS/PENDING/FAIL
D512 preflight PASS/PENDING/FAIL
Completed mirror rows: 22/26
Remaining rows: exact four
promotion maturity summary
main interim findings
known issues
running jobs healthy YES/NO
review-pack path
```

Then continue the existing Lane-B target mode and live simulator jobs. Do not stop after publishing the interim review snapshot.
