# Padding CLI route V2: preserve concurrent EP prepend

**48 CPU checks PASS;0 models,0 signals,0 production changes.** V1 and B's five qualified source files, qualification and request metadata are untouched.

Main's earlier preflight correctly held because another EP Goal had prepended a route. V2 changes only the qualified router base:

| Item | Identity |
|---|---|
| Required current entry | `89927e66750b94f00579cf9728e8672b11386a699aa9d8eef39d1d833051b205` |
| Current body bytes | 4568, all preserved verbatim |
| Padding prefix | 1941 bytes, identical to publishedV1 |
| New complete candidate | `793f960016b33fa926d0c91fb09319d5b010b8aae506b3e354c80c9aab414598` |

The full89927e entry is the exact suffix of `native.candidate.sh`; its original79ad body remains intact farther down. The new EP route remains `experiment:EP_PERF_* → /root/data/ep_l2_full_workload_performance_20261027_v1/tools/ep_perf_frontend.py`, exporting `EP_FULL_PERF_NATIVE_ENTRY=1`.

The padding routing logic, frontend deployment path, exact flag/project checks and all fail-closed behavior are unchanged. Every no-opt-in command falls through to the complete current entry. V2 adds EP_PERF prepare/run-native/result argument-vector and environment checks, explicit prefix/suffix checks and the expected89927e source guard to the original41 checks.

Actual POSIX shell execution uses instrumented copies in an A-owned fixture: every original/private execution target becomes a CPU argument sink. The fixture experiment wrapper points only to the fixture native; the production absolute wrapper is never executed. No production frontend or run-native is invoked by these tests. Missing/inactive ACTIVE metadata is tested only at the fixture gate; B's real registered frontend qualification remains separate.

`sh -n` passes. Old legacy argv/exported flags/stdout/stderr/return codes remain identical. The real existing gaussian DH-E384 full strict control still passes740717 cycles. Native/experiment are absent from the frozen21 source pins, and their original identity/strict contracts remain unchanged. The real production entry stayed89927e throughout qualification.

`CPU_ROUTE_QUALIFICATION.json` contains all48 checks and source hashes. `V2_SOURCE_PINS.json` records the new router-only source set. `V1_PREFIX.bin` is the original1941-byte **plain shell text**, preserved as raw bytes solely for comparison; it is not a compiled binary.

Main should publish this separateV2 package and amend only the router execution request. Immediately before installing, require the current entry still hashes89927e; if another concurrent prepend occurs, hold and rebase again rather than overwriting it. B's five-source qualification and scientific request metadata need no change for this router-only rebase. Agent A did not install the route.
