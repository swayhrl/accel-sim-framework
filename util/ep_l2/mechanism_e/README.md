# Mechanism study E execution entry

Current authority: Framework `b2e5328aca825d6e9ebfe09e46fa208957834636` (V2 incremental amendment).
Original authority/T0 and all attempts remain historical, without reinitialization.
Campaign: `EPL2_MECHANISM_STUDY_20261019_V1`.
New branch/worktree: `hrl/ep-l2-ms20261019-e-eval-v1`,
`/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1`.

The original Lane5 branch and scientific acceptance pointer remain read-only.
The old51/72 and R19 are closed. This existing study now has40 cumulative actual full starts (32 planned +8 contingency),
including full canaries, failures and retries. No accepted point exists yet.

## One resource authority

All transactions use the existing permanent
`/workspace/ep_l2_ft20261016_shared/REGISTRY.lock` and original registry JSON.
`mechanism_study_20261019_v1` is the new canonical field; the handoff directory
of the same name contains a `RUN_LEDGER.json` projection, never a second lock.
Git receipts are evidence, not live permission. The original registry, runner,
closure validator and input/config identity helpers are pinned by exact SHA256.

A owns all formal builds. B/C/E directed tests and A builds must use this common
resource extension, with exact conservative CPU/RAM/output-growth reservations.
No caller may reinterpret a successful Python control test as native production
qualification or as a resource waiver. Global4sim/8CPU/32GiB,48GiB physical
workspace,40GiB Share,64GiB available RAM remain. Builds max-j2. The same
reservations include all in-progress builds/tests/apps and future output growth.
New results max6GiB, old+new max20GiB. Migration exceptions do not apply.

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -B util/ep_l2/mechanism_e/coordinator.py status
# Actual request only after a material resource recovery event; no empty retry loop:
PYTHONDONTWRITEBYTECODE=1 python3 -B util/ep_l2/mechanism_e/coordinator.py reserve-work \
  --role A --kind build --cpu 2 --memory-bytes 8589934592 \
  --growth-bytes DECLARED_CONSERVATIVE_BYTES --result-growth-bytes DECLARED_LOG_BYTES \
  --output-directory /workspace/build/EXACT_NEW_OUTPUT
# Bind actual child identity immediately; keep lease until its full tree exits:
PYTHONDONTWRITEBYTECODE=1 python3 -B util/ep_l2/mechanism_e/coordinator.py bind-work-process \
  --role A --lease EXACT_LEASE --pid ACTUAL_CHILD_PID
# Release refuses a still-live PID/start_ticks/boot_id. For OS spawn failure only,
# use --no-child-started and retain that failure record:
PYTHONDONTWRITEBYTECODE=1 python3 -B util/ep_l2/mechanism_e/coordinator.py release-work \
  --role A --lease EXACT_LEASE --detail 'Actual build child fully exited; receipt PATH'
```

The CLI refuses the current low-space environment; it never starts a compiler.
Native test outputs use `/workspace/ep_l2_ms20261019_e_results/` and count toward
new6GiB. A must specify the build reserve; it is not a guessed lower disk floor.
The caller owns process execution/monitoring and must not release a live child.
One A build lease can span configure/build/directed phases: rebind the next child
only after the previous child exits; prior PID/start_ticks/boot_id stays in history.
Build growth and new log growth are separate fields in the same atomic reservation.
A native-test lease cannot hide any of its reserved output from the new6GiB total.
The actual build/test owner retains its existing monitored execution entry;
a resource lease alone is not production qualification.

## New starts, input and version preparation

D's immutable, timestamped four input registrations are copied byte-for-byte into
the E control pack and recorded once. Current command lists/declared path closure
are checked, not full input bytes. Actual full trace hashing occurs before and
after a real qualified run, using the original `asset_manifest/content_hash`.
No new trace bytes are copied. Read-only remains unqualified until C's full-epoch
oracle and A/E production checks pass; historical total pressure is background.

A's exact build release is normalized by E into the version-specific envelope
used by `register_qualification`. It requires the producing Core/Framework,
pybind11 vendor, actual binary, build/release provenance, original11 gates and
changed-path production evidence, not old cycles or a producer label. Each
supported profile specifies exact feature/diagnostic vectors, final effective
options, allowed research-option differences and diagnostic/subset/oracle labels.
The E-reviewed terminal parser is bound to the qualification. Profile combinations
outside that list are rejected. No complete ready spec can be inferred before A
has a binary. Ordinary manifest/path normalization is E's engineering duty.

`runner.py` reuses original trace/config closure, process monitoring and strict
64slice/request/WB/descriptor/resource summary validation; new diagnostic parser
adaptation is conditional on the exact A telemetry and independent native gates.
It does not inherit old release qualification or mutate old acceptance pointers.
The code is preparation, not proof that an unbuilt candidate passes native tests.

## Only E dispatches full apps

`controller.py --once` is a bounded event-driven controller, default2 workers.
It holds a separate E singleton flock for its entire lifetime. This is not an
extra global quota lock. Three workers require a reviewed E target and enough
physical/output reservations, with public build finished. Three unknown2.125GiB
outputs do not fit6GiB; smaller declared hard output limits can be used when
supported by complete observability and are enforced by the monitor, never by
silently increasing the campaign quota.

The only queue is the new handoff `inbox/READY_QUEUE.json`, prepared by E with
content-pinned specs and comparison pairs. With no exact ready queue it exits
without leases, simulations or a new resource survey. It is not a permanent
watcher. No queue is installed while resource/production prerequisites are absent.

Under the original lock, each unique spec reserves one pending slot. Before
actual Popen, a durable START_INTENT is written; successful Popen increments actual
starts exactly once. A crash in that interval remains unknown and consumes a slot
until explicit process/evidence reconciliation. No unknown launch is replayed.
Failed OS spawn is retained but is not an actual application start. Every actual
failed/resource-limited simulation remains charged. Same-key retries need a named
old failed attempt, engineering reason, a fresh directory and remaining budget.
The V2 14+6+2+2+1+6+1 scientific buckets plus8 contingency protect necessary controls.
Historical charged attempts retain their rows and consume the total and contingency, never an additional40. Explicit reallocation
requires a pre-result scientific reason, not favorable-speedup selection.

New starts stop2026-10-21 18:00 Asia/Shanghai. Each run's timeout is fixed before
launch, cannot exceed the22:00 intake freeze, and is separate from the new-start
cutoff. In-flight tasks drain naturally unless their own declared safety/timeout
condition trips. Only their own process group can be terminated by the runner.

A complete endpoint needs normal native exit, exact full instructions, matching
raw/parser cycles, strict64slice closure and version-bound data correctness.
`accept_pair` checks same binary/source/vendor/input/termination/nonresearch
options, then publishes a small `events/E_TO_D_PAIR_*.json` immediately. Missing
or changed endpoints/qualification cannot be imputed. Negative/zero results and
RESOURCE_LIMIT records remain. No new application or pair has yet been accepted.

Short screens are separately limited to6 ×120s/2M retired instructions; no screen
was requested by D, and no screen runner is enabled. They cannot become full
application results or certify whole-epoch read-only. Do not use a directed test
as a long-app workaround.

Control-only tests:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover \
  -s util/ep_l2/mechanism_e -p 'test_*.py' -v
```

## Scoped correctness failures and later review

A real native/terminal validation failure retains its attempt and places a
REVIEW_REQUIRED hold on that exact E qualification. New starts and new pair
acceptance for that version stop; independent other qualified versions remain
eligible. Already admitted siblings finish under their original safety/timeout
rules. Previously accepted affected pair declarations become
WITHDRAWN_SCIENTIFIC_HOLD with their prior status preserved in history, and D
receives a hold event. This never edits an old raw log or historical campaign.

Resource-limit termination alone does not revoke scientific qualification. A
parser or tool compatibility problem can be reviewed as engineering: E records
content-pinned resolution evidence tied to the exact active hold. Clearing that
hold does not silently restore a withdrawn pair; explicit endpoint/pair review
is still required. No real failure/withdrawal has occurred in this new campaign;
these paths have only isolated control-fixture coverage so far.

## Initial local-service terminal adapter and input-oracle review

`parse_terminal.py` adapts the actual A066c60b1 output and the44c940b7 correction
that prints disabled observations as DISABLED_NOT_OBSERVED. It reuses the original
structure decoder and strict summary validator, requires exact64slice final
native-clock scope, closed bank/descriptor/WAD state and independently bound
production data gates. Five initial profiles are explicit; RO/victim/old ideals
are not silently added. Copy exemptions, paid physical grants, lower packet bytes
and overlapping request-wait histograms remain distinct. Synthetic decoder checks
are control tests; this adapter has not yet passed new native production replay.

`review_ro_input.py` reads a completed D/C oracle candidate and its SQLite/export
artifacts without modifying them or rescanning large trace bodies. It independently
checks read/no-write/no-atomic eligibility, exact line/range exports, full command
order, post-activation host updates, artifact hashes and the preregistered trace
identity of D's completed scan. The initial HtoD prefix is drained before oracle
activation; every selected kernel and intervening command remains in scope. Model
assumptions remain explicit. An input-artifact review does not grant runtime T/M,
data-value, performance or resource qualification. Actual input bytes must be
rebound before an eventual qualified RO application.


## Full-system V2 increment

`policy_v2.py` amends the canonical field in place, validates the D32-condition
matrix, and requires E production-driven combination gates in addition to the
original11. It checks full dirty victim scope, finite common resources and real
F-minus-W semantics. F_DATA_FREE and fixed-victim require their own native gates.
These Python checks are intake controls, not proof of native implementation.
The initial terminal parser still rejects full F until an actual A combined
producer format and native qualification are available; do not relax it blindly.

Queue priority is Conv/FWT S/F, the other five S/F, then leave-one-out and
W-only, RO factorization/fixed-victim, local diagnostics/static64. The immutable
old FIRST14 file remains PREPARED_SUPERSEDED_ORDER through a separate annotation;
it is not installed as READY_QUEUE. A final source/binary identity must be
explicitly frozen in the ledger before V2 full conditions can reserve a start.
Current new starts and accepted points remain zero.

The E CLIENT_CONTRACT binds every runtime Python helper by SHA256 to one exact
published Git source commit. A caller cannot fix an edited helper by merely
replacing its checksum: published blob bytes must also agree. Publication is
source commit/push/readback first, then exact client update and receipt publish.
The original old CLIENT_CONTRACT and scientific pointer remain unchanged.

All active host leases count toward one global4sim/8CPU/32GiB. Local build/test
leases now explicitly record execution host/boot, central dispatcher, environment,
A build ownership and actual executor. Foreign hosts cannot lock a copied
registry. `review_environment` accepts only an E-independent, content-bound,
fresh observation including actual physical backing, all write filesystem
quotas/peaks, input/compiler/vendor/libraries, relevant I/O and an authorized
execution entry. Its result is ENVIRONMENT_REVIEW_PASS_NOT_A_LEASE.

Remote deployment is currently disabled: F228c0bf4 reports authentication denied,
not an inadequate target disk. No target candidate or remote lease is admitted.
Once that entry works, E independently measures it, binds the real central
remote execution/monitor/retirement transport and its affected compatibility
checks, then A publishes the exact named build. A file/Git receipt is never a
cross-host lock or an automatically usable remote dispatcher. No password, mount,
new credentials, native command or watcher is created by these controls.
