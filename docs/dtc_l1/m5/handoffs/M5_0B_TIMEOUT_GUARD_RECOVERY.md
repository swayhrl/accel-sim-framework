# M5.0B progressing-job timeout-guard recovery

Status: **CLOSED — external guard removed; live simulations preserved**

## Trigger and scope

At `2026-09-05T09:12:04+08:00`, the five remaining ratio-zero `PAPER_BASE`
simulations had source-backed simulator progress but were still beneath old
GNU `timeout 86400` supervisors created at `2026-09-04T10:12:09+08:00`.
The guard would have expired near `10:12:09+08:00`; elapsed duration is not a
simulator failure.  No workload, input, PTX, runtime, config, Core source, or
parser behavior was changed.

## Exact production topology before recovery

| workload | timeout PID | runner PID | simulator PID | PGID / session | remaining external allowance |
| --- | ---: | ---: | ---: | --- | ---: |
| ATAX | 3572144 | 3572154 | 3572276 | `3572144 / 3572132` | about 3,605 s |
| MVT | 3572147 | 3572157 | 3572277 | `3572147 / 3572132` | about 3,605 s |
| SYR2K | 3572149 | 3572155 | 3572296 | `3572149 / 3572132` | about 3,605 s |
| 2MM | 3572150 | 3572159 | 3572310 | `3572150 / 3572132` | about 3,605 s |
| SYRK | 3572148 | 3572158 | 3572311 | `3572148 / 3572132` | about 3,605 s |

Each topology was `timeout 86400 -> run_m5_cuda_app.sh -> simulator` in the
timeout-owned process group.  The terminal checker (PID 3606752) and strict
observers (PIDs 3854883 and 3860251) are independent path-polling shells; they
are not children of, and do not depend on, a production timeout supervisor.

## Disposable proof before production action

The preserved disposable proof directory is
`/tmp/dtc-l1-timeout-detach-proof.b6rnDY`.  It recreated
`timeout 120 -> bash -> sleep` with stdout/stderr redirected to its launcher
log and a separate path-polling observer.  `SIGKILL` was sent **only** to the
disposable timeout PID 3410176.

- The shell (3410180) and child (3410181) survived, were reparented to PID 1,
  and retained the original timeout-owned PGID.
- The child stdout/stderr file descriptors both continued to reference the
  original `launcher.log` before and after detachment.
- The child naturally wrote `child-natural-completion`; the independent
  observer wrote `observer-recovered-terminal-path`.
- Therefore supervisor removal neither killed nor paused the child, corrupted
  its output stream, changed its process group, nor prevented an independent
  result-closeout path.

## Applied least-invasive recovery

After exact command-line guards confirmed all five production supervisors,
`SIGKILL` was sent only to timeout PIDs 3572144, 3572147, 3572148, 3572149,
and 3572150.  No runner or simulator PID was signalled.  Each runner became a
PID-1 child while preserving its original PGID/session; each simulator retained
its original runner parent and `m5_run.log` stdout/stderr descriptors.  All
old timeout PIDs were absent in the post-action check, so no automatic
24-hour guard remains armed.

At `2026-09-05T09:14:24+08:00`, a 60-second post-detach read-only sample
confirmed continued simulator-level progress:

| workload | `gpu_sim_cycle` delta | `gpu_sim_insn` delta | state |
| --- | ---: | ---: | --- |
| ATAX | +47,000 | +379,104 | `Sl`, live |
| MVT | +41,500 | +333,984 | `Sl`, live |
| SYR2K | +14,500 | +127,776 | `Sl`, live |
| 2MM | +18,000 | +1,272,320 | `Sl`, live |
| SYRK | +14,500 | +147,328 | `Sl`, live |

The detached runners, simulators, and all three observer/checker shells were
still live at that sample.  This resolves only the obsolete external deadline;
it does not claim any live workload result.  M5.0B remains ACTIVE and M5.0C
remains gated on all five natural terminal validations.
