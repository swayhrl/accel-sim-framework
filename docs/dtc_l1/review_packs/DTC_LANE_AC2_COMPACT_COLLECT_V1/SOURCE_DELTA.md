# AC2 test-only source delta

Fixed parent:83aca449135703c176cfab29ae43e1245d00a557. It descends from
X2e32afdcf44be3374ff36d22568ed01a075459b6f; X2's direct parent is
c0a5e2c31e407c57e3a4af3ce529c921e8059a05. Exact input SHAs were fetched/read back
before AC2 worktree creation; no moving AG integration branch is used.

Allowlist: CMakeLists.txt adds only one CPU test target/CTest and matching runtime
path; tests/dtc_l1_ac2_capacity_probe.cc reuses the unchanged parent fixture and
adds source-coalescer capacity, manual fullpool, small-bank bound/negative and
unavailable-option witnesses. **Every production file is identical to parent AC.**
Removing the one AC2 CMake block recovers parent's entire CMake byte-for-byte.
The old tests are unchanged. No compact production option is registered, no state
machine or performance change is made after the resource STOP.

SOURCE_DELTA.json binds exact changed paths/blobs and production identity;
SOURCE_DELTA.patch is the complete Core diff (ordinary-context patch). K0 to X2
reuses and reruns the parent's exact source-recovery audit after removing only
AC2 test wiring from an in-memory/archive audit copy. All source/config/parser,
service quotas, K1 events/linearity, ordinary pending commit, physical generation,
waiters, inflight/return, Ref/PIB lifetime, sidecars, cache/public statistics,
clocks/ports/lower traffic are untouched. Only tests execute source methods.
