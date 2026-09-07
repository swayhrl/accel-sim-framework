# Resource and experiment-farm policy

Status: **MANDATORY FOR WINDOWS B/C; ADVISORY PROTECTION FOR A**.

## Purpose

Use the 512-logical-CPU host efficiently without starving the authoritative run, exhausting RAM, thrashing storage, or corrupting experiment provenance.

## 1. Hardware inventory before launching the farm

B must record:

- `lscpu -e=CPU,CORE,SOCKET,NODE,ONLINE`;
- unique physical core count;
- NUMA topology from `numactl -H` when available;
- `MemTotal`, `MemAvailable`, swap status;
- filesystem/device for immutable traces and scratch;
- available disk space and inode headroom;
- current A/C processes that must not be touched.

Do not assume 512 logical CPUs means 512 useful concurrent simulations.

## 2. Authoritative reservation

Window A has highest priority.

Before B/C launch a large farm, reserve resources for A and the OS. Default protection:

- at least 8 physical cores or one small CPU set not used by the farm;
- at least 20% of total RAM free, and never intentionally enter sustained swap;
- at least 15% filesystem free space on the scratch volume;
- B jobs use lower host priority (`nice` and/or best-effort `ionice`) when safe and available.

If A already has an active CPU affinity, B/C must not overlap it. Do not change A affinity while it is running.

## 3. Concurrency calibration

Before full fan-out, B runs a bounded representative benchmark at concurrency approximately:

`16 -> 32 -> 64 -> 128`

Stop increasing when any of the following is true:

- aggregate throughput gain from the next level is <20%;
- sustained CPU iowait is >15%;
- major faults or swap activity become material;
- scratch device becomes the obvious bottleneck;
- `MemAvailable` approaches the protected headroom;
- A's wall-clock progress degrades materially.

This is not a Goal hard-stop. Reduce concurrency and continue.

Record per level:

- jobs launched/completed;
- aggregate kernels/minute or simulated-instructions/hour;
- wall time;
- average and p95 RSS/job;
- CPU utilization and iowait;
- major faults/swap;
- read/write throughput;
- failures/retries.

Freeze a `FARM_CONCURRENCY_V1` limit before broad sweeps. It may be reduced dynamically when heavy prefill kernels raise RSS or I/O pressure.

## 4. Slot formula

Use a conservative cap equivalent to:

`slots = min(cpu_safe_slots, memory_safe_slots, io_safe_slots)`.

Recommended starting bounds:

- `cpu_safe_slots <= 0.75 × physical_core_count` until calibration proves more useful;
- `memory_safe_slots <= 0.70 × MemAvailable_at_start / measured_p95_RSS_per_job`;
- never schedule against logical SMT threads merely to make `%CPU=100` if aggregate throughput falls.

Prefer one CPU-bound simulator per physical core before using sibling SMT threads.

## 5. NUMA and affinity

If multiple NUMA nodes exist:

- group farm workers by node;
- keep CPU and memory placement local when practical;
- do not bind A after it has started;
- record the chosen placement policy in the farm manifest.

If `numactl`/affinity causes portability or correctness problems, fall back to OS scheduling and continue; provenance must record the fallback.

## 6. Immutable trace sharing

- All jobs may read the same immutable trace tree concurrently.
- Use symlinks/reflinks/read-only paths; do not copy the entire trace tree per job.
- Large memory should be allowed to serve as Linux page cache.
- Never modify/repack the accepted formal archives or trace files.
- Do not drop page cache during active experiments.

## 7. Stateful simulator rule

Never split one formal/speculative `config × ROI` into separate per-kernel simulators and sum them as if equivalent.

The continuous process must preserve:

- TLB residency;
- PWC state;
- cache state;
- replacement history;
- any other cross-kernel simulator state.

Per-kernel sharding is allowed only for offline immutable-trace analysis.

## 8. Scratch and logging

Each run gets a fresh directory with:

- unique run ID;
- immutable-input manifest;
- config/list/object-map hashes;
- source/binary/runtime hashes;
- pid/start/end/status;
- compact summary.

Raw logs stay outside Git. Rotate/compress completed logs asynchronously only after their hashes/terminal status are recorded.

## 9. Process ownership

Every launched job must be registered in a farm process table containing PID/PPID, window, run ID, branch/source, command, scratch dir, and start time.

Never kill an unregistered process merely because its command resembles Accel-Sim/GPGPU-Sim. If ownership is ambiguous, inspect and isolate rather than mass-kill.

## 10. Machine-safety response

On OOM risk, swap growth, filesystem exhaustion, runaway retry storm, or severe I/O collapse:

1. stop launching new speculative jobs;
2. preserve authoritative A;
3. allow healthy running jobs to finish if safe;
4. reduce farm concurrency;
5. repair scheduler/cleanup policy;
6. resume.

Do not terminate the Goal for an ordinary resource-management issue.
