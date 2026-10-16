# Lane 5 shared host budget — v1

Coordination: `6c136e2a56a008695f8c8b815723bf8f1a760db9`.
Authority node: `huangrulin-174`. Shared canonical directory:
`/workspace/ep_l2_ft20261016_shared/`.

- Live registry: `RUN_REGISTRY.json`; permanent advisory lock: `REGISTRY.lock`.
- Discovery: `HOST_DISCOVERY_INITIAL.json` (full process and resource inventory).
- New results: `/workspace/results/ep_l2_ft20261016/` only.
- Owner/dispatcher: Lane 5. Lane 4 and Lane 5 share baseline run keys.
- This JSON snapshot in Git is descriptive, never a lock. On this node every
  read-modify-write must hold exclusive `flock(REGISTRY.lock)` and atomically
  replace the JSON. Never lock the replaceable JSON inode itself.
- Other hosts cannot create a separate registry and claim global exclusivity.
  They need a unique assignment in this central registry first. No remote-host
  execution is admitted until host identity/resources and allocation are registered.

## Measured initial resources

512 logical CPUs / 256 physical cores; cgroup CPU quota 384 CPU equivalents;
cgroup memory limit 256 GiB, initial current usage about 43 GiB. Host available
memory about 286 GiB. Host swap is full (2 GiB); cgroup swap about 114 MiB and
historical cgroup oom_kill=17 (cumulative history, not a current failure).
Workspace initial free space 63.74 GiB, load average about 185. Other
projects have active simulator runs; none were stopped, restarted, reprioritized,
or rebuilt. These resources are shared, not EP-L2-owned.

## Initial shared EP-L2 quota

Across ALL six lanes on this host: at most 2 simultaneous long simulations,
8 CPU units including registered builds, 32 GiB reserved memory. Pilot reservation
8 GiB/run; initial combined EP-L2 result ceiling 8 GiB and 2 GiB/run output.
Build at most -j4 and obtain a shared resource lease. Keep at least 64 GiB
available cgroup/host memory and 48 GiB free workspace; refuse new work below
these floors. These are conservative operational limits, not architecture knobs.
Re-measure at each admission. Scan is a separate exclusive long-run slot and
cannot overlap another admitted EP-L2 simulation. Existing external tasks are
recorded as observation only, never adopted, killed, or counted as our results.

## Run-key identity v1

SHA256 of canonical UTF-8 JSON with sorted keys and compact separators, containing:
`core_source_commit`, `framework_source_commit`, `binary_sha256`,
`runtime_config_sha256`, `trace_content_sha256`, `workload`, `epoch_range`,
`feature_vector`, `ideal_vector`, `termination_contract`.
Config identity covers ordered exact config/auxiliary asset bytes after resolution;
trace identity covers kernelslist plus every referenced trace content, not its path.
Epoch range distinguishes full application from diagnostic fragments. Feature and
ideal vectors must be complete, including OFF fields. Paths, lane owner and host
are excluded so Lane 4/5 and alternate paths deduplicate the same work.

Record canonical identity, unique run owner, host/boot ID, source/receipt references,
result directory and attempt state under the lock BEFORE starting a process.
A duplicate key returns the existing owner/state, including failures; it never
implicitly relaunches. Stale owners are not automatically reclaimed. Lane 5 must
check original process identity and preserve evidence before an explicit retry.
No Git snapshot authorizes a launch. The registry client and runner are now
published under util/ep_l2/ft_lane5/; producing commit
`de8fe21d9598660e40da8486e48f2d46acee4582`. The shared CLIENT_CONTRACT.json
binds its path/hash. All lanes must obtain a shared claim before a long run.
Diagnostic runners may use Registry directly and keep their separate evidence
gates; the implementation runner additionally requires independent qualification.

## Dependency gate

Formal performance launches require Lane 1's qualified baseline/source/binary/
config contract and independent all-OFF/finite-WBUF validation. Historical
1152-payload/shadow results cannot fill B16/U_WB16 cells. Quota is not model
qualification. Lane 2/3 versions enter the matrix only after independent checks.

## review_r3 resource audit

Authority a41bfb55934303a4d4a342762f74a16d137d0316. RESOURCE_HOLD; audit45,436,243,968 workspace free bytes, deficit6,103,367,680 bytes before any build growth. Results resolve to a different /root/share filesystem with47,704,883,200 free bytes, also below48GiB. No own inactive workspace build/tmp candidates; probe objects on results FS cannot repair workspace. Physical bytes released0, no files deleted/moved. Full measured before/after/device/path/hash evidence in FT20261016_LANE5_REVIEW_R3_RESOURCE_r1. No floor change or admission retry. Lane1 is sole official builder; reserve measured compile growth above floor before starting. Scientific current authority V2 is an additional mandatory gate, separately from resource claim and original immutable terminal/certificate.

## review_r5 bounded evidence, no policy amendment

Authority77a9fbe937ea23465cf0d0076d2df1909f52d055.48GiB applies to formal production admission; source/static/preparation work proceeds. Current resource evidence and user-review-only alternatives: docs/ep_l2/review_packs/FT20261016_LANE5_REVIEW_R5_r1/BUILD_ADMISSION_ALTERNATIVES.md and RESOURCE_EVIDENCE.json. No floor, production path, quota or host changed. Workspace snapshot38,342,262,784B; no EP-L2 run/build leases. Lane1 alone uses the formal build entry after exact source fix and adequate growth headroom. No Storage-Ops or DTC cleanup/transport delegated to Lane5.
