# Lane X: OO eager source-request invalidation V1

2026-10-18, Asia/Shanghai. Goal: `DTC_LANE_X_OPTIN_INVALIDATION_IMPLEMENTATION_174_V1`.

**IMPLEMENTED_OO_DEFAULT_OFF_LOCAL_CPU_CHECKS_PASSED_LANE_Y_PENDING**.
No independent K1 correctness PASS, architectural value correctness PASS,
all-ISA support, physical timing/PPA claim, or formal performance result is made.

## Authority and scope

The user explicitly lifted `SOURCE_EVENT_CONTRACT_MISMATCH` and selected eager
source-request semantics. Lane V authority is Framework branch
`hrl/iscas2027-dtc-lane-v-semantic-audit-174-v1` at
`26abd496417d9392245052e54fbd9ba27c6ffd96`; both `K1_SEMANTIC_CONTRACT.md` and
`SOURCE_EVENT_MAP.md` were read completely through immutable Git objects.
Their content hashes are recorded in `SOURCE_EVENT_AUDIT.json`.
The earlier STOP/build report remains historical at Lane X Framework
`0c8fcb571977303f3e87ecb0cac6cf7bd25d3cfc` and Core
`f8b34dd7a738caddf4f23dd417e34c0b63c206d9`.

Current Core: `c0a5e2c31e407c57e3a4af3ce529c921e8059a05`, on the original
`hrl/iscas2027-dtc-lane-x-invalidate-optin-core-174-v1` branch, descended from
frozen `6fba0136f8465b59fe5858a950fa39efb265f654`.
Framework review branch remains `hrl/iscas2027-dtc-lane-x-implementation-174-v1`.

`-gpgpu_dtc_l1_invalidate_on_source_event` uses the production `OPT_BOOL` parser,
with default `0`. Omitted/0 takes the original ordinary invalidate/cycle paths;
no DTC lookup map is changed by source requests. Value `1` supports PAPER_OO
only, with either existing finite-service setting. IO fails explicitly with
`IO_K1_UNIMPLEMENTED_STOP`; modern and Base/LEGACY are rejected for K1. K0 retains
all existing modes. Disabled L1D and the external-cache constructor are not K1
support claims and fail explicitly.

## Implemented behavior and time model

The linearization point is the existing `ldst_unit::invalidate()` request.
Idle-cluster, MEMBAR and cache-config-change predicates and selected SM sets
are preserved. Caller arguments now carry source labels through the existing
chain. There is no new kernel completion event or idle-request deduplication.
`flush()`, stores, atomics, bypass and PROXY_FENCE acquire no new invalidations.

For each visible OO Tag, K1 clears lookup visibility and physical `tag_valid`.
A live Ref retains the original allocation, generation and every consumer;
no inflight/sector/waiter/PIB/return ownership is cleared or rebound. Ref0 ready
lines can reclaim immediately; pending/service ownership in that state is a
hard assertion. Repeated requests without new mappings are no-ops. Map-loss
uses one timestamp per newly hidden generation; final release uses the existing
lifecycle. Same-address old and new allocations may coexist and finish by their
original physical identities.

The directory sweep is atomic at this host call and adds **zero simulated
cycles or new quota**. This is an explicitly idealized logical visibility
operation, not a hardware zero-cost/PPA result. It does not advance service,
metadata wakeup, collection, allocation or retirement ports. An explicit event
cycle is used for immediate map-loss accounting. Occupancy observation samples
before a source-event free, using a separate observation edge; existing service
advance sites, quotas and delays are preserved.

Ordinary cache files `gpu-cache.cc` and `gpu-cache.h` are byte-identical to the
frozen anchor. A K1-only inherited read-only observer sees its pending bit;
ordinary invalidate/cycle methods run once in the original order. Source request
and ordinary commit are counted separately, with source labels, phase/order,
cycles, effective DTC map changes and retained/reclaimed counts. A pending-to-clear
observation is a conventional commit invocation, including an unused Tag-array
no-op; it does not claim ordinary Tag contents changed. Detailed records use the
existing debug-event limit; summary counts and first/last timestamps remain
available when detailed logging is disabled or truncated.

## Validation and limitations

Independent Core build and seven CTest targets passed: the four existing
regressions, OO K1 lifecycle checks, production-parser/real-ordinary-cache
integration, and deterministic K0 mechanism trace. A separately compiled frozen
header produces byte-identical K0 trace output. These are CPU checks, not a
full-simulation K0 equivalence proof. See `CORNER_CASE_CHECKS.json` for coverage,
especially tests using the unchanged sector predicate and withheld retirement
rather than a full LD/ST/operand-collector fixture. Source selection and unchanged
response/retire paths also have immutable-source comparison evidence.

The real ordinary-cache test records requests at cycles 2,2,3 with a held
ordinary fill owner, DTC visibility change at the first request, deferred
ordinary commit at cycle 4, and a separate immediate config-request commit.
Old DTC Ref/identity remains live across that ordinary commit. This directly
separates source request from conventional retirement in a CPU fixture.

Bring-up failures are preserved in raw logs: a fixture omitted a service edge
before a later-cycle access; its ordering was corrected. A shared-library test
initially inherited an incompatible LD_LIBRARY_PATH and failed before test
execution; CTest now pins the new library directory. The existing CMake generator
also refreshed its build-string file without recompiling its consumer on an
incremental build. That candidate was excluded from released identities; the
published build is a fresh directory from clean committed source, with an
embedded SHA checked against that source. No mechanism assertion was weakened.

## Delivery and gates

All requested named artifacts are in this directory. `CORE_DELTA.patch` is the
complete delta from the frozen Core, including tests and the superseded STOP
note. It uses zero context (`git diff --binary --unified=0`), so literal blank
context spaces are not misreported as whitespace in the containing review diff;
apply it using `git apply --unidiff-zero`. Reverse applicability to the exact
published Core was checked without modifying that worktree. `SOURCE_AND_BINARY_IDENTITY.json` identifies the fresh build, actual library
resolution and before/after source hashes. `GIT_DELIVERY.json` records publication
receipts. Raw logs/builds remain solely in the new Lane X directories and are
not committed. The trace build recipe independently compiled `accel-sim.out` from unchanged
Framework source against this new Core library; the executable was not run on
a kernel or workload. Its build source is Framework
`0c8fcb571977303f3e87ecb0cac6cf7bd25d3cfc`, whose simulator/util code trees remain
unchanged in this review branch; the later review SHA is not mislabeled as that
build source. A future authorized invocation must pin and verify the actual
shared library as recorded in the identity file.

Lane V source contract has been consumed; **Lane Y independent validation is
still required before any complete performance simulation**. Lane Y must review
the new Core SHA, event scopes/order, actual LD/ST return and WB integration,
conservation and the bounded K0 evidence. IO remains `IO_K1_UNIMPLEMENTED_STOP`;
modern retains its prior boundary. `VALUE_CORRECTNESS_UNPROVEN` remains in force.
Any eventual full performance matrix is OO-only. This window dispatches zero
complete Gaussian/GEMM simulations and changes no frozen source, old binary,
other Lane source/results, workload/input/trace, capacity, clock or global cap.
