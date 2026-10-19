# A first source candidate: single finite execution entry

Current state: source and55 finite commands prepared; C++ NOT_COMPILED_NOT_RUN.
No executable runtime is released. Public source is Core17e7e224954e44a968a0447bcdfea91e3b2e5a96.

Runtime Framework197741be9be9b8e390a557d639503b416d8e95f0 is in the NEW isolated
`/workspace/worktrees/accel-sim-ep-l2-ms20261019-a-runtime-v1` worktree. Its exact
vendorf90c430 is a separate new worktree borrowing existing Git objects; old
Framework/vendor and builds are unchanged. Control Framework is this A branch.

Entry: `util/ep_l2/mechanism_study/build_a.py`. The entry defaults to preparation
only and never runs an application. One future explicit invocation after E's
exact current resource approval is:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 util/ep_l2/mechanism_study/build_a.py \
  --out /workspace/ep_l2_ms20261019_e_results/A_BUILD_AND_DIRECTED_r1 \
  --build /workspace/build/ep-l2-ms20261019-a-r1 \
  --admission /workspace/ep_l2_ms20261019_shared/E_ADMISSION_A_BUILD_r1.json \
  --execute
```

The example JSON in this directory is deliberately NOT APPROVED and expired;
it is a schema/identity handoff, not authorization. E supplies a fresh file with
approved=true, PASS result-budget reservation>=128MiB and valid_until_unix,
only after its current resource assessment. The file binds exact Core/runtime/
driver hashes and original174. No 174-new or migration exception is implied.
E's small file can be delivered while A/B/C/D continue independent source work.

The entry rechecks48GiB workspace +2GiB build reserve, Share40GiB, canonical
MemAvailable64GiB with8GiB reservation and central2CPU lease. All stages are
serial except CMake-j2; output is bounded128MiB for logs/control, original build
entry uses a2GiB growth reserve and continuously enforces48GiB. E must also
account remaining new6GiB/old+new20GiB allocations before authorizing. The published E coordinator API reserves build growth and new result
growth atomically in the original registry with owner mechanism_A. There is
no separate legacy lane2 lease. Both source/output paths and current E API
SHA256 are bound by the admission. A_BUILD.lock is unique
and no resident wait/automatic retry is created. Floor/expiry changes stop only
the owned process group. Neither frozen results nor other projects are removed.

Build uses unchanged Framework CMake source, exact current Core source and
vendor; new native targets are EXCLUDE_FROM_ALL. Actual command/log/assertion/
source/executable/config identities will be recorded ONLY when run. The entry
reuses immutable Framework197741b's `build_r0_1.run_owned` process supervisor,
without invoking its old main, source selection, Goal, tests or release logic.

First suite:55 native processes, including exact observer0/1 cycle/semantic
comparison and preserved default-OFF/host/clock/atomic paths. DIRECTED_PLAN_r1
is a preparation record, not evidence of executable existence. Every actual
attempt gets a fresh output directory; resource/compile/test failures remain
frozen and do not count as PASS. E must independently validate an actual producer
PASS, then alone run the full OFF canary and D-preregistered application groups.
The canary counts toward24; old equal cycles never qualify a different binary.

Control checks actually performed: Python parse/plan generation and deliberate
missing-E-file rejection. That rejection created0 leases,0 native commands and
no build directory; the central registry bytes were unchanged. This is a TOOL
control result, not simulator/native qualification. No optional syntax-only
C++ compilation was used to bypass the resource gate.

E compatibility: published1b93f33b2169b88f50eec49033e259966c153ea3
A_BUILD_ENTRY_SHARED_RESOURCE_COMPAT.patch applied and AST parsed. The new
E API digest must match CLIENT_CONTRACT and admission; no integrity bypass.
Child PID/start_ticks/boot_id is rebound to the ONE lease for every serial
phase and may be released only after all owned children exit. Actual process
RSS<=8GiB, owned build<2GiB and owned result<128MiB are monitored.

Bounded readonly build-budget evidence: existing microopt source84359d4 build
allocated1,611,059,200 bytes; earlier7-target producer allocated1,080,152,064
bytes (`du -s --block-size=1` on only those two known retained build roots).
Our10-target first release excludes three larger old candidates and adds a
small observer unit. Reserve2,147,483,648 build bytes leaves536,424,448 above
the larger measured final tree, plus134,217,728 separately reserved log bytes.
This is a conservative finite budget, not a measured new peak; crossing it
stops and preserves the attempt. E's atomic admission must cover48GiB floor
+2GiB build+128MiB logs+all pending reservations (at least50.125GiB before
other reservations). No build was attempted from these budget observations.
