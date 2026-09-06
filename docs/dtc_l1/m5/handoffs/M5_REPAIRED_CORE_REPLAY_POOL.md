# M5 repaired-Core replay-pool admission

Status: **ACTIVE acquisition; no stage PASS claim**.

Timestamp: 2026-09-06T10:33+08:00

## Measured admission basis

| Item | Observation | Decision relevance |
| --- | --- | --- |
| Host topology | 512 logical CPUs; two NUMA nodes | independent simulations use distinct non-SMT sibling CPUs |
| Existing pool | 15 live M5 simulators, including four stats-light A/B diagnostics | all have isolated output namespaces |
| Per-job RSS | light 0.55--3.3 GiB; heavy approximately 8.9 GiB | use a mixed workload/mode pool |
| MemAvailable | approximately 110 GiB before dispatch; approximately 101 GiB after | permits three additional light BICG jobs with substantial headroom |
| Swap / vmstat | swap occupied historically, `si=0`, `so=0` | no current swap pressure; do not treat occupancy as usable capacity |
| CPU / I/O | each worker near one CPU; iowait approximately 5% | no CPU or trace-store saturation observed |
| Output filesystem | approximately 32 GiB free | current simulation outputs are MB-scale; continue low-frequency space checks |

## Active limit and dispatch

Set the current dynamic **N_safe = 18** workers, with no more than five
approximately 9-GiB heavy workers.  The pre-dispatch 15 jobs include four
stats-light A/B diagnostics and five known-heavy ATAX/MVT/recovery rows.  The
three added workers are BICG Base/IO/OO, historically lighter than the heavy
rows.  At 18 workers MemAvailable remained approximately 101 GiB and swap I/O
remained zero; do not dispatch a nineteenth worker without a new calibration.
This is a host scheduling choice only: configs, traces, payloads and simulator
semantics are unchanged.

The BICG triplet uses its one immutable bundle, the repaired Core
`15cfa76ed3b041fa5b78161dfba02bae1e6d7fe9`, Framework
`dc7836c484544b78d143837bbbb40ecbabb15aee`, the frozen ratio-zero 80-SM/
cap-10240 configs, and distinct output directories.  ATAX uses the same
repaired Core but the earlier Framework `2bb015a812ad4ec5245d396a2a9cbe469ef9b41b`;
the two ATAX modes and Base all share that exact identity.  The source-level
Framework difference is documentation/parser only, not an unrecorded runtime
substitution; the complete per-job identity is in the companion manifest.
The BICG triplet's purpose is to re-establish T2 under the post-repair identity;
the older BICG T2 remains a diagnostic anchor only.

Recalibrate before any further dispatch or if MemAvailable, swap activity,
iowait, trace-store throughput or output-space headroom becomes adverse.

## Pipeline scheduling clarification (2026-09-06T10:44+08:00)

The active researcher scheduling authority permits a V100-captured workload to
enter the SIM_HOST dynamic replay queue immediately after all of the following
are PASS: hardware checker, immutable bundle, archive SHA, copyback, and local
bundle validation.  This acquisition rule does not wait for T3, a different
workload replay, the remaining capture queue, or the stats-light A/B study.
Rows completed before their predecessor logical gate are explicitly
`PRECOMPUTED_PENDING_STAGE_ACCEPTANCE`; they are not a stage PASS claim.

The current measurement still holds the M5 admission limit at **N_safe = 18**:
there are 18 live M5 workers, 512 logical CPUs across two NUMA nodes, per-M5
worker RSS p50 about 2.4 GiB and p95 about 8.5 GiB, and current workers retain
near-one-core CPU progress with zero `si`/`so`.  However, the host also has
substantial unrelated load, swap is historically occupied, and the shared
filesystem has only about 58 GiB free.  Therefore no nineteenth M5 worker is
admitted until a worker naturally exits and the resource sample is repeated.
This is a conservative dynamic-pool decision, not a serialization rule:
ready repaired-Core triplets (including GEMVER and MVT) are next eligible when
a safely calibrated slot exists.  All formal rows continue to use the frozen
statistics/configuration identity until the isolated stats-light equivalence
study is accepted; no stats-light result is a formal result.

## Throughput recalibration and protected capacity (2026-09-06)

The container has all CPUs `0-511` in its effective cpuset, but
`/sys/fs/cgroup/cpu.max` is `38400000 100000`: its hard aggregate CPU quota is
384 cores, not 512.  The relevant resource sample found about 19% system idle
while the M5 workers each retained near-one-core progress.  Thus the prior
18-worker value is a conservative scheduling limit, not a cpuset or quota
ceiling.  It is not raised solely from nominal topology because shared-host
unrelated demand remains material and several active rows are approximately
9-GiB heavy.

Five researcher-authorized superseded/non-candidate workers were gracefully
retired after evidence snapshot: stats-light A2/A3 and the old-Core GESUMMV
Base/IO/OO diagnostic triplet.  The three GESUMMV rows are explicitly
`RESEARCHER_ABORTED_SUPERSEDED_DIAGNOSTIC`: their runtime predates the
lower-create repair and they can never be repaired-identity formal rows.
Their preserved namespace is
`/workspace/m5-t3-gesu-80sm-cap10240-r3-20260906/{base,io,oo}`; each had about
2:30 CPU time, empty stderr, and no fatal/assertion/deadlock/output-mismatch
signature at retirement.  `SIGTERM` was sent only to their distinct PGIDs
`480579`, `480592`, and `480604`; all exited without escalation.

Two released slots are now occupied by the required repaired-Core BICG
PAPER_IO/PAPER_OO A1 natural-terminal confirmations (CPUs 46/47).  Three
slots remain intentionally unfilled: ATAX repair rows have exceeded the old
failure window but have not yet naturally terminated, strict-parsed, or closed
drain/accounting.  Therefore the broad repaired-runtime gate required before
MVT replacement and repaired GESUMMV T3 dispatch is not yet established.
This is a source/correctness gate, not a stage-number serialization.  Refill
those slots immediately after that gate and a fresh resource sample permit it;
priority remains MVT IO/OO, repaired GESUMMV Base/IO/OO, then other locally
immutable Paper rows.

## Live-pool checkpoint (2026-09-06T12:19+08:00)

The repaired-Core BICG `PAPER_OO` A0 row naturally terminated (exit status
zero) in its existing isolated namespace
`/workspace/m5-repaired-core-replays-80sm-cap10240-20260906/bicg/oo`.
Its strict parser summary is retained beside that output only; it is not
registered and does not by itself re-close T2.  The exact terminal values are
`gpu_tot_sim_cycle=8764792`, `gpu_tot_sim_insn=158601216`, and
`DTC_L1_oo_lower_created/issued/responses=17827090/17827090/17827090`.
Dependencies close `18350080/18350080`; final OO PIB, inflight, active refs,
and lower outstanding are all zero.  The only `deadlock` text in stdout is
the echoed enabled configuration option; stderr reports exit status zero and
no assertion/fatal/output-mismatch signature was found.  It remains
`POST_REPAIR_T2_REPLAY_CANDIDATE` until the corresponding BICG Base and IO
rows naturally terminate and the same-bundle triplet is reconciled.

At this checkpoint 14 M5 simulator processes remain live: A0/A1 Base,
precomputed ATAX Base, repaired ATAX Base/IO/OO, repaired BICG Base/IO,
BICG IO/OO A1 confirmations, GEMVER Base/IO/OO, and MVT Base.  Every live
row has isolated output and approximately one advancing host CPU.  The
dynamic limit remains **N_safe=18**, not a permission to dispatch four new
rows: the remaining capacity is protected by the unresolved ATAX
post-repair natural-terminal/parser/drain gate.  The current cgroup exposes
`0-511` but has `cpu.max=38400000 100000` (384-core aggregate quota); it has
not throttled.  Host load is nevertheless about 440 on this shared machine
and the output filesystem has about 102 GiB free, so neither nominal 512-way
topology nor the lack of cgroup throttling justifies raising the limit.
