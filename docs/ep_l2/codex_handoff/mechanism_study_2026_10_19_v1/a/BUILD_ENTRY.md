# A first source candidate: single finite execution entry

Current state: source and55 finite commands prepared; C++ NOT_COMPILED_NOT_RUN.
No executable runtime is released. Public source is Core44c940b748fceaec8f21fa2b443907d5afd2756b.

Runtime Framework197741be9be9b8e390a557d639503b416d8e95f0 is in the NEW isolated
`/workspace/worktrees/accel-sim-ep-l2-ms20261019-a-runtime-v1` worktree. Its exact
vendorf90c430 is a separate new worktree borrowing existing Git objects; old
Framework/vendor and builds are unchanged. Control Framework is this A branch.

Entry: `util/ep_l2/mechanism_study/build_a.py`. The entry defaults to preparation
only and never runs an application. One future explicit invocation after E's
exact current resource approval is:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 util/ep_l2/mechanism_study/build_a.py \
  --out /workspace/ep_l2_ms20261019_a_common_v1/A_BUILD_AND_DIRECTED_r1 \
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
account remaining new6GiB/old+new20GiB allocations before authorizing. The legacy
registry only accepts lane1..6, so this original Lane2 window uses resource owner
lane2 for the NEW A campaign, not a restarted old Goal. A_BUILD.lock is unique
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
