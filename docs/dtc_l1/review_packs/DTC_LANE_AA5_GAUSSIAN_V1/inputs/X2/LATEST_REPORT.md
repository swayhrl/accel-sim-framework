# X2 K1 normal-terminal export V1

2026-10-18, original `huangrulin-174` container/root account.

**PASS_PRINT_ONLY_NORMAL_EXPORT_CPU_QUALIFICATION**. The user-authorized single
production repair is implemented and qualified through the actual normal
statistics entrypoint. Full/canary simulator starts = **0**. This is no workload,
K1 performance, full-ISA/value/coherence or PPA acceptance, and no AA4 execution
continuation is authorized by this delivery.

## Concrete change

AA4 `2b69f5ec8fae85c0ee1bbfe95ac93eb524bb172e` found that normal `gpu_print_stat()`
called the public DTC aggregate but did not reach the observer summary. X2 adds
30 lines to `shader.cc` and 3 const declarations to `shader.h`: a K1-only framed
snapshot in the existing aggregate entrypoint, then read-only cluster/core/LDST
delegation to the original `source_invalidation_observer::print()`.

Core: `e32afdcf44be3374ff36d22568ed01a075459b6f`, branch
`hrl/iscas2027-dtc-lane-x2-terminal-export-core-174-v1`, based exactly on
`c0a5e2c31e407c57e3a4af3ce529c921e8059a05`.
Framework review branch: `hrl/iscas2027-dtc-lane-x2-export-review-174-v1`.
The fresh trace binary's Framework **build source** is
`ccc3e553b89c2cfe2578c2b70abe147cf98fee2a`; later document/publication SHAs are
recorded separately, not presented as that binary's build source.

The other changes are the new CPU test and its six-line build wiring. Exact
fragment removal recovers the original shader implementation/header and CMake;
all other tracked paths are unchanged. The observer/counters/formatter,
invalidation sources and guards, linearization, physical/generation/Ref/PIB/
waiter/inflight/return ownership, ordinary pending retirement, finite quotas,
clocks and old public statistics are unchanged. No legacy L1 printer is restored,
no new observer/counter is created, and runtime_stat500000/debuglimit0 stay fixed.

## Evidence

| Check | Result and boundary |
| --- | --- |
| Original Core CTest | 7/7 passed; original tests unchanged |
| Actual normal-entrypoint CPU processes | 10: five new/five freshly built c0; real GPU/cluster/core/LDST objects; `gpu_print_stat()` called directly, never private print |
| K0 omission/0 | No K1 section/summary; omitted = explicit0; absence stays UNAVAILABLE |
| K1 complete population | Three cumulative snapshots per process, 64 unique SMs each; 64x1 and 8x8 topologies |
| Events and sentinels | Real no-event zero/sentinel rows; nonzero source, changed/retained/reclaimed; repeated requests and ordinary commit coalescing |
| Snapshot semantics | Last whole frame selected; cumulative frames never summed or mixed |
| Fail-closed parser | 15 negative checks reject missing/duplicate/truncated/unframed/private/malformed/K0-unexpected export |
| Public output | 15 corresponding new/c0 normal boundaries byte-identical after removing only the new frame; CPU fixture scope, not full-run numerical equivalence |
| Print is read-only | Observer byte state, finite service/occupancy edges, Ref/allocation counts and clock unchanged around every normal call |
| Actual ELF | All four normal-to-LDST call/tail-call links present; old legacy route absent from normal GPU printer |
| Binary/source identity | Fresh clean e32 release; independently fresh c0 baseline; per-ELF/library/probe/trace SHA and build IDs; actual CPU dladdr/exe/maps binding; source hashes stable |

The event fixture prepares frontend metadata through production APIs, supplies a
controlled ordinary owner, injects source requests and calls one CPU LDST cycle.
It launches no instruction/kernel, trace replay, GPU `cycle()` or runtime
simulation thread. Its timestamps and counts are CPU witnesses, not Gaussian
measurements. The old c0 library's missing K1 normal export is reproduced by the
same fixture, rather than inferred from Y2's private-printer witness.

The separately compiled trace executable was **not run**. Its actual ELF
interpreter was invoked only with `--list`, binding all resolved dependencies to
the new library without entering trace main. Trace runtime process maps remain
UNAVAILABLE_NOT_RUN. Actual process maps in this pack belong to the CPU probes.
A future authorized run must pin and recheck the published library identity.

## Contract and prior accepted scopes

Each normal aggregate call can print one version1 section with all configured
SMs, explicit global cycle and UINT64_MAX no-event-cycle sentinel, retaining the
original per-SM summary format. Values remain lifetime cumulative; multiple
statistics boundaries are snapshots, not additive measurements. A completed
frame alone does not replace a future runner's full normal-terminal strict test.

AA4's STOP and its 0/4 starts remain historical facts. V's eager request contract,
Y2 `d085f98c` bounded OO model/ABI acceptance and gaps, AA3's K1-only noncomparative
observer contract, and X's IO/modern/value limits are preserved. All requested
AA4 materials and accepted scopes were fetched/read via immutable Git objects,
with file/blob/SHA identities in ACCEPTED_INPUT_READBACK.json. No other Lane
source/raw or old execution lock was used or modified.

The atomic directory sweep's zero added simulated-cycle cost remains an explicit
pre-existing model assumption. Additional K1 host output proves no GPU-cycle,
hardware-area, bandwidth or physical-timing claim. Host throughput/wall time is
not GPU performance. No performance result or source-event count for Gaussian
is supplied, and K0 absent telemetry is never converted to measured zero.

## Files and publication

- SOURCE_DELTA_ALLOWLIST.json and CORE_DELTA.patch: strict four-path delta;
  zero-context patch applies with `git apply --unidiff-zero`.
- NORMAL_EXPORT_CONTRACT.md: normal route, population, cumulative/sentinel rules,
  parser scope and model limits.
- CPU_NORMAL_ENTRYPOINT_TESTS.json and 7_CTEST.json: scoped checks and exact logs.
- BINARY_IDENTITY.json and ELF_NORMAL_PATH_AUDIT.json: fresh identities, actual
  loading/call path and loader-only trace binding.
- SOURCE_SHA256.tsv and SHA256SUMS: per-file source and package identities.
- PUBLICATION_RECEIPT.json: push/fetch-back receipt; final receipt commit and clean
  final-tree verification are bound externally to avoid a self-referential SHA.

Raw builds/logs remain exclusively under the new X2 paths. The initial CPU
fixture compile used vector iteration on the production raw-pointer core arrays;
that test-only engineering error was corrected before release and its failed log
was preserved. It caused no production mechanism change or simulator start.
