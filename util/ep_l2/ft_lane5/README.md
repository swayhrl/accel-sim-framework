# EP-L2 FT Lane 5 tools — V1

Production source parent is Framework `54fbc7869f4e40b6b48dc936b527fee85dd46406`,
Core `1fc248aa89abefbd1b417f7f4053cd2bf56d7a1e`. This tooling release does not
qualify B16/U_WB, TVD or RO. A passing Python harness test is not a passing Core
production-path test. No new performance result is supplied by the harness.

## Shared allocation for all lanes

Canonical authority on node `huangrulin-174`:
`/workspace/ep_l2_ft20261016_shared/{RUN_REGISTRY.json,REGISTRY.lock}`.
The permanent lock inode is flocked before atomically replacing registry JSON.
Snapshots committed to Git never authorize another host to launch. Only the
authority dispatcher can register run ownership on behalf of another host;
this initial client refuses execution on an unregistered/different host.

Use the Lane 5 worktree's frozen `registry.py` from other lanes. Do not copy a
registry to another worktree and start a new authority. Every long simulation
including Lane 4 diagnostics must claim its full identity first. The same
B16 binary/config/trace identity is shared; source- or binary-mismatched rows
are different runs and cannot be called a reused common baseline.

```bash
python3 util/ep_l2/ft_lane5/registry.py snapshot
python3 util/ep_l2/ft_lane5/registry.py key /path/to/canonical_identity.json
python3 util/ep_l2/ft_lane5/registry.py build-claim --owner lane1 --jobs 4
python3 util/ep_l2/ft_lane5/registry.py build-release --owner lane1 LEASE_ID
```

For a diagnostic runner, import `Registry`, `run_key`, `process_identity` from
this exact file. `claim(identity, owner, result_directory)` returns
`(fresh, allocation)`. When fresh is false, consume/report the existing owner
and state; never start a duplicate. Preserve `allocation['lease_id']`, and call
`update(key, lease_id, 'RUNNING', process=process_identity(actual_pid))` after
launch, then one of `COMPLETE_VALID/FAILED/TIMEOUT/RESOURCE_LIMIT/INCOMPLETE`.
`COMPLETE_VALID` requires that runner's diagnostic/implementation closure gates;
the registry alone is not a scientific validator. Failed and stale keys are
retained and are never automatically reclaimed. Keep scan exclusive.

Build leases cover -j4 at most and share the 8-CPU/32-GiB ceiling with simulations.
Release only your lease after your build exits. No automatic expiry or killing
of somebody else's process. Registry reserved resources are conservative
admission accounting; runner monitors its own process-tree RSS. This is not
a claim of kernel-enforced cgroup isolation from unrelated projects.

## Complete run identity

`registry.IDENTITY_FIELDS` is exhaustive. SHA256 is computed over sorted-key,
compact UTF-8 JSON, preserving all nested feature/ideal/termination dimensions.
The source SHA is the producing source, not the publishing evidence commit.
Owner, host, source path and output path are deliberately outside the identity.

Config digest is `content_hash({'ordered_configs': asset_manifest(configs,
ordered=True), 'auxiliary_assets': asset_manifest(auxiliary_assets),
'environment': explicit_environment})`; use [] for no auxiliary assets.
Config order is significant. Declare all file dependencies, including XML,
interconnect and parser-required assets; nested configs must be flattened.
Environment entries are explicit and included in config identity.

Trace digest is `content_hash(asset_manifest(trace_files))`. Entries contain
stable relative logical `name`, `sha256`, and byte size. Declare kernelslist.g
and every referenced kernel body. Trace closure checks actual resolved content
paths against the kernel list, including repeated kernels. Unsupported commands
fail rather than silently omitting scientific input. Alias paths with identical
logical names/content have the same identity. Full trace hashing is required
when an actual qualified runtime is admitted; roster list hashes alone do not
qualify trace-body reuse.

## Frozen runner and qualification adapter

`run.py --spec SPEC.json --check-only` verifies inputs without reserving/running.
Without `--check-only`, it uses an exclusive new result directory under
`/workspace/results/ep_l2_ft20261016/<run-key>/`, snapshots binary/configs,
rehashes inputs after execution and retains every failure. It monitors its own
process group, timeout/RSS/output/disk floors; only its own child group can be
terminated. It never rebuilds the producing worktree or alters input traces.

SPEC fields: `identity`, `owner`, `binary`, ordered `configs` list and
`auxiliary_assets` list (`{name,path}`), complete `trace_files` list,
`entry_trace_name`, `qualified_release`, `parser` (`{path,sha256}`),
`timeout_seconds`, and explicit `environment`. Parser adapter invocation:
`python3 PARSER --raw RAW_LOG --out terminal_summary.json`.

Feature vector fields: finite_wbuf, unified_wb, tvd, ro, adaptive_policy,
wbuf_entries, payload_capacity_per_slice, bank_count, ops_per_bank_cycle.
Ideal vector fields: wb, meta, read_hit, all false for implementation tables.
`epoch_range` must explicitly identify full_application/all. Diagnostic fragments
and ideal modes go to separate Lane 4 tables, never implementation averages.

Lane 5 will normalize published Lane 1 contracts into a
`status=INDEPENDENTLY_QUALIFIED`, `qualified_by=lane5`,
`evidence_kind=PRODUCTION_DRIVEN` release envelope bound to exact producing
Core/Framework/binary SHA and qualified feature vectors. Every `run.GATES` item
requires PASS, production_driven=true and an existing content-hashed evidence
artifact. TVD/RO combinations need additional version-specific production tests
before appearing in qualified_feature_vectors. This normalized adapter is a
consumer format, not a unilateral change to Lane 1's public interface contract.
No such production qualification envelope is published in the tooling stage.

`validate.SUMMARY_FIELDS` defines hardware terminal metrics. Cycles/instructions
must also match the native terminal counters. A normal software exit is necessary
but insufficient. A parser must source-map exact unique-request audit, hardware
drain, WB milestones and role conservation; it cannot fill absent counters with
zero or turn observation-only qualification into correctness evidence. Live
resident contents may remain; transient payload, descriptor, MSHR, WAD and return
obligations must be explicitly closed under the registered termination contract.
Current normalized V1 accepts full-application hardware-drained terminals only;
any alternative legitimate workload terminal needs an explicit reviewed adapter.

## Independent data/version test adapter

`validate.py --reference PROGRAM.json --events OBSERVATIONS.jsonl --out AUDIT.json`
checks independent ordered initialization/read/write stimulus against observed
production responses. PROGRAM is separate from producer observations; no implicit
initial-zero memory. Data is full 32-byte sector hex. Request identities are
epoch/slice/request_id, with explicit sector and line in the reference stimulus.
The current oracle covers ordinary read/write data. Atomic semantics, concurrent
ordering and synthetic write-allocation identity need dedicated production
adapters; they cannot be claimed covered by these ordinary-data fixtures.

Events cover requester admission/response; descriptor allocation/free;
payload allocation/role/free and generations; tag bind/unbind and stale/detached
fills; WAD and actual WB created/lower-accepted/completed; bank operations and
hardware terminal. Free events require pending_sectors=0 and read_refs=0. WB
payload free requires true lower data acceptance; WAD free requires true set_done.
Directed fixtures explicitly retire all payloads; normal performance terminals
use the separate summary validator allowing resident data to remain.

Run self-tests with:
`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s util/ep_l2/ft_lane5 -p 'test_*.py' -v`.
Coverage includes eight-process same-key race, cross-lane reuse, scan and quota,
content identity, malicious/missing evidence, data/version errors, stale fills,
early frees, incorrect WB boundaries and terminal resource leaks.
