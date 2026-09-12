# Lane D live-run background-safety audit

Snapshot: `2026-09-12T23:57:35+08:00`.  This is an ownership audit only; it
does not send a signal, change affinity/priority, or write into any live run
directory.

## Result

All three live GESUMMV simulations are **NOT_SAFE_FOR_BACKGROUND**.  They share
the process group and session of controller PID `3732696`, whose direct parent
is Codex app-server PID `1219985`.  The controller was launched as a child of
that app-server; there is no independent `setsid`/`nohup`, `tmux`/`screen`,
systemd, supervisor, or detached persistent controller in the observed
ancestry.  Shell backgrounding therefore is not proof of survival if the
interactive Codex process tree ends.

Goal Mode must remain alive while any of these rows is live.

## Exact observed ownership chain

```
1219985  Codex app-server
  3732696  bash run_post_fast64_observer_diagnostic_wave_v1.sh  (PGID=3732696 SID=3732696)
    3733515  immutable runner (D4 GESUMMV physical48 IO)
      3733567  /usr/bin/time + taskset
        3733568  accel-sim.out
    3733559  immutable runner (D4 GESUMMV physical48 OO)
      3733613  /usr/bin/time + taskset
        3733614  accel-sim.out
    3733697  immutable runner (D5 GESUMMV primary OO)
      3733747  /usr/bin/time + taskset
        3733749  accel-sim.out
```

Every listed runner, `/usr/bin/time` wrapper, and simulator has
`PGID=3732696` and `SID=3732696`.  In particular, they are not in an
independent session from the controller.

| D5 role / D4 physical point | workload / mode | simulator PID (PPID) | PGID / SID | run directory | attempt UUID | immutable runner SHA-256 | CPU time at snapshot | stdout bytes / latest progress | safety |
|---|---|---:|---|---|---|---|---|---|---|
| D4 physical 48 KiB | GESUMMV / IO | `3733568` (`3733567`) | `3732696` / `3732696` | `/workspace/post-fast64-observer-d4d5-v1.20260912T045713Z.3732696/d4_gesummv_physical48_io` | `23830907-53c7-450f-b235-8411ad161004` | `43ad754a87191107fb00f2b9d3ffa1b9183521d38b8ed323aa190c78f138eb24` | `10:55:03` | `33805`; `thread block = 15,0,0` | `NOT_SAFE_FOR_BACKGROUND` |
| D4 physical 48 KiB | GESUMMV / OO | `3733614` (`3733613`) | `3732696` / `3732696` | `/workspace/post-fast64-observer-d4d5-v1.20260912T045713Z.3732696/d4_gesummv_physical48_oo` | `7d1eed9f-9c3e-4fb6-af25-c1fecabc49cb` | `43ad754a87191107fb00f2b9d3ffa1b9183521d38b8ed323aa190c78f138eb24` | `10:54:40` | `33805`; `thread block = 15,0,0` | `NOT_SAFE_FOR_BACKGROUND` |
| D5 primary | GESUMMV / OO | `3733749` (`3733747`) | `3732696` / `3732696` | `/workspace/post-fast64-observer-d4d5-v1.20260912T045713Z.3732696/d5_gesummv_primaryprimary_oo` | `a15aa3fc-f455-4e21-a1a3-721d1fb0bbb0` | `43ad754a87191107fb00f2b9d3ffa1b9183521d38b8ed323aa190c78f138eb24` | `10:55:33` | `33805`; `thread block = 15,0,0` | `NOT_SAFE_FOR_BACKGROUND` |

The output sizes and progress lines are a snapshot, not a claim that the
simulators are stalled.  Each simulator was observed runnable and consuming
CPU at the snapshot.

## Resumption after natural terminal

Leave the controller and its children unchanged.  After each natural terminal
receipt appears, run the same fail-closed collector against its immutable
manifest and accepted FAST64 summary; it requires exit 0, identity equality,
exact pre-existing metric equality, lifecycle/dependency conservation, and
zero terminal observer-live records.  Only then may the final Lane-D
materializer include that row.  No partial live output is analyzable evidence.
