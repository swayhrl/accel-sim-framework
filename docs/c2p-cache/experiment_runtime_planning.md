# C2P replay runtime and resource planning

This is host-side scheduling metadata, not an architectural metric.  Keep it
separate from paper IPC/L2 figures: wall time and RSS vary with host load,
binary build, trace compression, and the number of concurrent replays.

## Per-run record

`scripts/run_c2p_cache_cases.sh` writes `host_profile.txt` beside every new
completed run:

```text
user_cpu_sec=...
sys_cpu_sec=...
cpu_percent=...
max_rss_kib=...
exit_status=...
wall_start_utc=...
wall_end_utc=...
wall_elapsed_sec=...
```

The wrapper is outside `accel-sim.out`: it leaves the copied simulator,
resolved configuration, trace, `run.out`, and `summary.txt` unchanged.  It
also writes a profile for a failed simulator invocation before propagating its
exit code, so failed runs remain useful for capacity diagnosis.

Historical run directories have no exact host profile.  They may be reported
as a **legacy file-mtime estimate** from copied `accel-sim.out` to
`summary.txt`; this is adequate for rough queue planning only.  Do not label
an absent RSS or a simulator's architectural `gpgpu_simulation_time` as a host
measurement.

## Summarize a campaign

```bash
python3 scripts/summarize_c2p_run_resources.py \
  hw_run/<campaign> --format csv --output hw_run/<campaign>/resource_summary.csv
python3 scripts/summarize_c2p_run_resources.py \
  hw_run/<campaign> --format markdown
```

The report retains case/mode, wall time and its source, peak RSS when
available, CPU time, simulator elapsed time, simulated work, trace payload
bytes, and the exact run directory.  It is safe to rerun after new jobs finish.

## Scheduling rule

Use `max_rss_kib` from matching trace/configuration families for bin packing;
sum only the candidate jobs, then reserve a fixed operating margin for the
host and filesystem cache.  Wall time is an ETA/priority signal, not an
admission signal.  For a legacy point with no RSS, start one representative
job and wait for a stable `VmHWM`/new `host_profile.txt` before launching a
large batch.

For the current C2P+ policy campaign, the completed ISPASS LPS legacy points
needed approximately 91--146 seconds each on this host and carried a 534,340
byte compressed trace payload.  The four Btree policy points started after the
new profiler was added and provide the first exact RSS/time records for this
diagnostic family.  The 2DConvolution legacy points had an observed
`VmHWM` of 356--365 MiB per job; their final elapsed time remains a legacy
estimate because they began before the recorder existed.

## First planning table: C2P+ policy campaign

Campaign root:
`hw_run/c2p-plus-probe-policy-v1-20260822/`.  Its generated
`resource_summary.csv` and `resource_summary.md` are the machine-readable and
human-readable source.  Values below are per replay, not total batch cost.

| Workload / policy | Wall time | Time source | Peak RSS | Trace payload | Scheduling use |
|---|---:|---|---:|---:|---|
| ISPASS LPS, all four policies | 91--146 s | legacy file-mtime estimate | unavailable | 0.51 MiB | small, fast smoke/negative-control family |
| 2DConvolution, four policies | 38.5--43.9 min | legacy file-mtime estimate | 356--365 MiB observed `VmHWM` | 802 MiB | long wall-time family; four were safe concurrently |
| Btree budget1 | 837 s | exact `host_profile` | 420 MiB | 772 MiB | longest Btree policy point in this batch |
| Btree budget2 | 653 s | exact `host_profile` | 416 MiB | 772 MiB | |
| Btree budget4 | 598 s | exact `host_profile` | 420 MiB | 772 MiB | |
| Btree Ideal | 695 s | exact `host_profile` | 420 MiB | 772 MiB | |

The Btree four-way batch ran with each process at approximately 95% CPU.  Its
in-simulator `gpgpu_simulation_time` (298--403 s) was not equal to measured
wall time (598--837 s), so it must not be used for host ETA.  This table is an
initial same-host reference rather than a promise for a future shared or
different machine.
