# Lane1 / Lane5 review_r8 handshake r2 — published Lane5 API

The r1 caller-side proposal is preserved in commit65500bb9 and its review pack.
This revision consumes actual Lane5 Framework300c1010161b270ae73414b8146d238c961f0cd0,
API source205782b9745a7189b9bf858486648930b08b8a81 and registry compatibility
source02440185c5cc349f1569f5d11e682902939b0ee3. Lane5 owns these modules.
Its39 new pilot and10 affected registry tests are evidence of tools, not a live
authorization. Lane5's first NO_SAFE_PILOT_ENVELOPE used old Lane1 ref85534de2
before the present request existed. New request revisions must be independently
reviewed; the refusal is never treated as approval or silently rewritten.

## Exact shared request fields

Lane1 publishes raw LOW_SPACE_PILOT_REQUEST.json and its immutable SHA256.
Alongside source/audit/cap/command evidence it supplies Lane5's required fields:

- pilot_id, host, boot_id, cpu_units=2, memory_bytes=8589934592,
  max_duration_seconds<=3600.
- execution_identity: exact core_source_commit, framework_source_commit,
  vendor_commit, driver_sha256, build_entry_sha256 and repair_commands_sha256.
  The last hash is SHA256 of ast.get_source_segment of the unique top-level
  repair_commands function, UTF-8 with no appended newline.
- execution_locations: absolute core_repo, framework_repo, vendor_repo,
  driver_path, build_entry_path and repair_commands_path. Actual clean producing
  identities and bytes are measured, not merely accepted from caller strings.
- output_roots: fresh disjoint build, result and small control-journal roots,
  with path/resolved_path/filesystem. TMPDIR is nested in build, not double-counted.
  Existing exact engineering source worktrees are separate input roots. Core
  CMake's ignored setup write is declared and counted by Lane1's local growth
  monitor; any difference from backend output-root accounting is conservatively
  charged to whole-filesystem contraction, never treated as zero external IO.

Original Corec9481845 / Framework3ab150b3 / vendorf90c430c are unchanged.
New exact engineering source worktrees protect frozen production roots from
CMake's source/setup output. No old getter patch is reapplied. The frozen
repair_commands supplies all21 executions and the same five CMake targets,
Release/assertion flags and-j2. No applications or scientific promotion.

## Only Lane5 authorizes and registers

Use the owner's ENGINEERING_PILOT_API.md as authoritative API documentation.
An authorization must be schema EPL2_ENGINEERING_PILOT_AUTHORIZATION_V1,
status APPROVED_ENGINEERING_ONLY, issuer lane5, r8 authority56a0517d, exact
request publication/hash/token, actual source/driver/vendor/locations/output
roots, host/boot/mount/protected inventory, TTL and all positive justified
per-filesystem budgets. scientific_use is FORBIDDEN_ENGINEERING_EVIDENCE_ONLY.
Requested emergency/external/kill reserves cannot be reduced by the caller.
Lane5 independently accepts reliable numbers or emits NO_SAFE_PILOT_ENVELOPE.

Lane1 verifies the fetched Lane5 authorization Git bytes and central
CLIENT_CONTRACT's engineering_pilot_module/source/hash plus dependencies before
import. It uses a thin bridge to actual PilotRegistry:

```
claim(auth, exact_request_bytes, measure_execution_identity(locations)) -> key
monitor(key, auth) -> stop/reasons/independent live observation
attach_process(key, auth, actual_owned_Popen_child)
release(key, auth, terminal, exact_pre_release_receipt_sha256)
```

Only Lane5 calls register on the real authority. Lane1 has no register/fallback
or direct central JSON mutation path. The pre-release journal is immutable in
its own new control root; the final receipt binds that hash after release. Token
replay remains rejected across process restart, STOP stays latched, and original
formal admission is preserved. Monitoring runs more frequently than the2s API
ceiling and keeps an independent2s stalled-watchdog for its own child group.

## Bounded waiting and result publication

Only one Lane1 disk GateWaiter runs, at600s cadence and within its original48h
deadline. API alignment can replace an idle own control process, preserving its
old records and original deadline; it cannot restart the science Goal, run a
second waiter or consume/reuse a pilot token. Formal50GiB admission wins first
with two>=60s-spaced observations and the original formal driver. All paths
share the central lease and execution mutex. A separate kernel pidfd completion
publisher does not poll disk/Git/registry and cannot start/retry any build.

Runner default is dry-run; execution requires exact current authorization,
registered one-use token and explicit --execute-once. All engineering outcomes
remain ENGINEERING_ONLY. Ordinary repairs need a new isolated frozen source
revision and independent amendment within the original campaign bounds; this
first owner API forbids implicit rebinding or a second claim. No auto-clean or
infinite retry. Formal producer events still require normal release audit and
Lane5 independent11gate before performance evidence.

Seventeen caller safety tests plus three integrations against the actual
published owner implementation use PRIVATE temporary ledgers only. Real central
register/claim and CMake/compilation executions remain0 before Lane5 approval.
The private tests verify real one-use/replay, latched STOP/release/journal hash
and actual direct-child attachment. The owner's unchanged39 tests are retained,
not replayed or represented as scientific qualification.
