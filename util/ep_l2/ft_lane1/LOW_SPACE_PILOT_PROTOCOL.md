# Lane1 / Lane5 r8 handshake, proposed adapter API v1

This is a request-side interface, not a Lane5 authorization or a disk policy
change. Frozen Framework3ab150b3 / Corec9481845 / pybind11f90c430c are checked
out into **new exact engineering source worktrees**: Core CMake writes an ignored
`setup` file in its source directory. The frozen official source roots are not
writable pilot inputs. The original driver and Registry remain untouched.

Lane1 publishes `lane1/LOW_SPACE_PILOT_REQUEST.json`, exact raw-file sha256 and
driver code commit. Lane5 independently samples actual resources and publishes
`lane5/LOW_SPACE_PILOT_AUTHORIZATION.json` on its own branch. A denial uses
`status=NO_SAFE_PILOT_ENVELOPE`; it does not authorize compilation. An approval
uses `status=AUTHORIZED_ENGINEERING_ONLY` and binds:

- `pilot_id`, `request_sha256`, `host`, `boot_id`, exact complete `identity` from
  the request, `publication_path` (the authorization's own repository path),
  `not_before_unix`, `expires_at_unix`, `max_wall_seconds` (<=3600),
  `monitor_interval_seconds` (<=1), `cpu_units=2`, `memory_bytes=8589934592`,
  `formal_runtime_ready=false`.
- `filesystems.workspace` and `filesystems.results`: positive integer
  `entry_free_bytes` (minimum launch threshold), `hard_stop_free_bytes`,
  `max_pilot_allocated_growth_bytes`, `external_write_reserve_bytes`,
  `monitor_and_kill_overshoot_bytes`, `minimum_untouched_emergency_bytes`.
  Entry >= the sum of the latter four budgets; hard stop >= emergency+overshoot.
  Actual measured free belongs separately in the independent resource gate.
  Max own growth cannot exceed the request cap; stop margin cannot be reduced.
- `registry_adapter`: the exact `CLIENT_CONTRACT.json.engineering_pilot`
  dictionary, containing `api_version=ENGINEERING_PILOT_V1`, `module_path`,
  `module_sha256`, `source_commit`, `repository_path`. The module must be a
  committed Lane5 file; both authorization and module commit must be ancestors
  of the freshly fetched Lane5 branch. Lane1 checks their actual Git bytes.

The **Lane5-owned** module exports `PilotRegistry(shared_root)`:

```python
claim(request, authorization, observed_resources) -> {
    "lease_id": str, "owner": "lane1", "pilot_id": str, ...
}
record_process(lease_id, pilot_id, process_identity) -> None
heartbeat(lease_id, pilot_id, observed_resources) -> None
finish(lease_id, pilot_id, engineering_receipt) -> None
```

Lane5 alone registers authorization/token with the central permanent
`REGISTRY.lock`. `claim` atomically checks its registered request/auth hashes,
single-use pilot id (including across restart), exact host/boot/source/driver,
TTL, resources and policy; refuses all other active runs/builds for this sole
pilot, preserving CPU/memory/scan protections. It records an ordinary active
`resource_leases` row with explicit ENGINEERING_PILOT metadata, leaving all
formal callers/floors unchanged. `heartbeat` verifies sole ownership, boot,
TTL, caps and current global constraints; `record_process` binds the real owned
PID/start ticks/boot. `finish` releases even on failed/stopped builds and leaves
the pilot token permanently consumed. Exceptions mean stop, never fall back to
direct CMake or unregistered execution. No Lane1 live authorization registration.

The adapter must honor the request's permanent cancellation marker. Lane1's
single GateWaiter and pilot runner share `LANE1_BUILD_EXECUTION.lock`. If formal
50GiB admission is reached first, the waiter writes the marker and invokes only
the frozen official entry after two samples >=60s apart. During an active pilot
it waits without starting a second build or reserving a lease.

Runner default is dry-run. Actual launch requires `--execute-once`,
`--pilot-id`, `--authorization` and `--authorization-publication`, plus independent
Git proof and the central adapter. It uses the frozen driver's `repair_commands`
for21 executions, exactly its five targets and Release/assertion CMake flags.
Its child launcher limits affinity to2 CPUs, nice10, zero core dumps, and256MiB
maximum single file. Disk/own blocks/RAM/process/IO/TTL are sampled every<=1s,
with a2s stalled-monitor watchdog and own-group TERM→KILL only. A net external
space contraction is a stop trigger, not a claim to measure gross external IO.

The request proposes explicit conservative **caps**, not measured compiler
peaks. Lane5 must independently accept reliable numeric bounds or deny. The
initial runner makes one configure/build/test pass and never auto-clean/retry.
Any ordinary repair must keep original identities/results, use a new frozen
engineering revision and independent Lane5 audit within the same campaign
limits; it cannot silently obtain a second claim or broaden science. A future
continuation interface must be reviewed before use. No engineering output may
set formal runtime_ready, issue a scientific certificate or launch applications.

Before live registration, Lane5 tests its real adapter: valid under-floor pilot,
forged/expired permits, replay after restart, CPU/memory/active-lease/scan/host/
boot/source failures, unchanged formal floors, failed-owner release. Lane1's
tests cover runner refusal/monitor/owned-child isolation; fake adapters do not
constitute a test of Lane5's not-yet-published central implementation.
