# M5.E1 — V100 trace-capture readiness

Status: **ACTIVE — PAPER10_CAPTURE_HAS_PRIORITY**

This is a per-row E1 scheduling inventory for the current rented V100. It does
not alter Extended-20 membership, inputs, dimensions, source identity, or the
M5.2 gate for E2 performance runs. A historical sm52 build is provenance only;
a row becomes TRACE_CAPTURE_READY only after its own clean CUDA-11.8 V100/sm70
build, real-V100 checker, input/reference freeze, and unsupported-feature
audit pass.

All size classes below are planning labels, not measured traces. UNKNOWN is
used where no source-backed trace-volume basis exists.

| workload | source | build evidence | input | checker | V100 build | trace eligibility | size class | state / blocker |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BlackScholes | CUDA SDK 4.2 b059fdae | sm52 provenance only | PENDING_FREEZE | QA_PASSED | PENDING_CUDA11_8_SM70 | STATIC_TRACE_CANDIDATE | UNKNOWN | SOURCE_READY; real-V100 build/input smoke and dynamic contract pending |
| convolutionSeparable | CUDA SDK 4.2 b059fdae | sm52 provenance only | PENDING_FREEZE | QA_PASSED | PENDING_CUDA11_8_SM70 | RUNTIME_AUDIT_CONSTANT | UNKNOWN | SOURCE_READY; real-V100 build/input smoke and semantic audit pending |
| fastWalshTransform_11_19 | CUDA SDK 4.2 b059fdae | sm52 provenance only | PENDING_FREEZE | QA_PASSED | PENDING_CUDA11_8_SM70 | STATIC_TRACE_CANDIDATE | UNKNOWN | SOURCE_READY; real-V100 build/input smoke and dynamic contract pending |
| scalarProd_13920 | CUDA SDK 4.2 b059fdae | sm52 provenance only | PENDING_FREEZE | QA_PASSED | PENDING_CUDA11_8_SM70 | STATIC_TRACE_CANDIDATE | UNKNOWN | SOURCE_READY; real-V100 build/input smoke and dynamic contract pending |
| scan | CUDA SDK 4.2 b059fdae | sm52 provenance only | PENDING_FREEZE | QA_PASSED | PENDING_CUDA11_8_SM70 | STATIC_TRACE_CANDIDATE | UNKNOWN | SOURCE_READY; real-V100 build/input smoke and dynamic contract pending |
| sortingNetworks | CUDA SDK 4.2 b059fdae | sm52 provenance only | PENDING_FREEZE | QA_PASSED | PENDING_CUDA11_8_SM70 | STATIC_TRACE_CANDIDATE | UNKNOWN | SOURCE_READY; real-V100 build/input smoke and dynamic contract pending |
| transpose | CUDA SDK 4.2 b059fdae | sm52 provenance only | PENDING_FREEZE | QA_PASSED | PENDING_CUDA11_8_SM70 | STATIC_TRACE_CANDIDATE | UNKNOWN | SOURCE_READY; real-V100 build/input smoke and dynamic contract pending |
| vectorAdd_6000000 | CUDA SDK 4.2 b059fdae | sm52 provenance only | PENDING_FREEZE | QA_PASSED | PENDING_CUDA11_8_SM70 | STATIC_TRACE_CANDIDATE | UNKNOWN | SOURCE_READY; real-V100 build/input smoke and dynamic contract pending |
| cfd_097k | Rodinia 3.1 dad09cb0 | Makefile located | HASHED | PENDING_FREEZE | PENDING_CUDA11_8_SM70 | RUNTIME_AUDIT_CONSTANT | UNKNOWN | SOURCE_READY, INPUT_READY; checker, semantic audit and V100 build pending |
| btree | Rodinia 3.1 dad09cb0 | Makefile located | HASHED | PENDING_FREEZE | PENDING_CUDA11_8_SM70 | STATIC_TRACE_CANDIDATE | UNKNOWN | SOURCE_READY, INPUT_READY; output reference/checker, dynamic contract and V100 build pending |
| dwt2d | Rodinia 3.1 dad09cb0 | Makefile located | HASHED | PENDING_FREEZE | PENDING_CUDA11_8_SM70 | STATIC_TRACE_CANDIDATE | UNKNOWN | SOURCE_READY, INPUT_READY; output reference/checker, dynamic contract and V100 build pending |
| gaussian | Rodinia 3.1 dad09cb0 | Makefile located | CANDIDATE_SET_HASHED | PENDING_FREEZE | PENDING_CUDA11_8_SM70 | STATIC_TRACE_CANDIDATE | UNKNOWN | SOURCE_READY; primary input/checker, dynamic contract and V100 build pending |
| hotspot1 | Rodinia 3.1 dad09cb0 | Makefile located | HASHED | PENDING_FREEZE | PENDING_CUDA11_8_SM70 | STATIC_TRACE_CANDIDATE | UNKNOWN | SOURCE_READY, INPUT_READY; output reference/checker, dynamic contract and V100 build pending |
| lud | Rodinia 3.1 dad09cb0 | Makefile located | SOURCE_GENERATED_CONTRACT | source -v verifier | PENDING_CUDA11_8_SM70 | STATIC_TRACE_CANDIDATE | UNKNOWN | SOURCE_READY, INPUT_READY; exact V100 verifier smoke and dynamic contract pending |
| bfs | Parboil 4e0fc548 | CUDA Makefile located | HASHED | Python3 predicate adapter PASS | PENDING_CUDA11_8_SM70 | RUNTIME_AUDIT_ATOMICS_TEXTURE_GLOBAL_BARRIER | UNKNOWN | SOURCE_READY, INPUT_READY, CHECKER_READY; semantic audit and V100 build pending |
| cutcp | Parboil 4e0fc548 | CUDA Makefile located | HASHED | Python3 predicate adapter PASS | PENDING_CUDA11_8_SM70 | RUNTIME_AUDIT_STREAM_CONSTANT | UNKNOWN | SOURCE_READY, INPUT_READY, CHECKER_READY; semantic audit and V100 build pending |
| histo | Parboil 4e0fc548 | CUDA Makefile located | HASHED | byte-exact checker adapter PASS | PENDING_CUDA11_8_SM70 | RUNTIME_AUDIT_ATOMICS | UNKNOWN | SOURCE_READY, INPUT_READY, CHECKER_READY; semantic audit and V100 build pending |
| mri-q | Parboil 4e0fc548 | CUDA Makefile located | HASHED | Python3 predicate adapter PASS | PENDING_CUDA11_8_SM70 | RUNTIME_AUDIT_CONSTANT | UNKNOWN | SOURCE_READY, INPUT_READY, CHECKER_READY; semantic audit and V100 build pending |
| sad | Parboil 4e0fc548 | CUDA Makefile located | HASHED | Python3 predicate adapter PASS | PENDING_CUDA11_8_SM70 | RUNTIME_AUDIT_TEXTURE | UNKNOWN | SOURCE_READY, INPUT_READY, CHECKER_READY; semantic audit and V100 build pending |
| stencil | Parboil 4e0fc548 | CUDA Makefile located | HASHED | Python3 predicate adapter PASS | PENDING_CUDA11_8_SM70 | STATIC_TRACE_CANDIDATE | UNKNOWN | SOURCE_READY, INPUT_READY, CHECKER_READY; V100 build/dynamic contract pending |

## Capture queue rule

No Extended row is TRACE_CAPTURE_READY yet. Paper SYR2K, SpMV and 2MM retain
exclusive physical-capture priority. While that queue runs, E1 may advance rows
independently through deterministic source, V100 build, input/checker and
unsupported-feature evidence. As soon as a row reaches TRACE_CAPTURE_READY,
it joins the sequential V100 queue after Paper-10 2MM ARCHIVE_PASS; every
capture then follows archive, copyback, local immutable validation and
proof-bound streaming eviction before the next storage-constrained capture.

## Live scheduling ledger (2026-09-06)

The following is an **exclusive highest-demonstrated-pre-build-state** count
for worker-pool scheduling.  It is not a formal-result classification and does
not relax the per-row requirements in the table above.  In particular, a
historical CUDA-11.8 `sm_52` provenance build is not `BUILD_READY`: every row
needs its own clean CUDA-11.8 `sm_70` V100 build and runtime checker smoke.

| exclusive state | count | members / evidence boundary |
| --- | ---: | --- |
| `NOT_READY` | 0 | Every approved member has a clean source anchor. |
| `SOURCE_READY` | 9 | Eight CUDA SDK 4.2 members plus Rodinia `gaussian`; each still lacks an accepted input/checker and/or V100 build boundary. |
| `INPUT_READY` | 5 | Rodinia `cfd_097k`, `btree`, `dwt2d`, `hotspot1`, `lud`; their source-backed input contracts are frozen, but output checker and V100 build/smoke remain pending. |
| `CHECKER_READY` | 6 | Parboil `bfs`, `cutcp`, `histo`, `mri-q`, `sad`, `stencil`; clean input hashes and the source-predicate Python-3 adapter fixture suite are revalidated. |
| `BUILD_READY` | 0 | No clean V100/sm70 build and real-device checker smoke has yet completed. |
| `TRACE_CAPTURE_READY` | 0 | Paper-10 physical capture retains priority; no Extended row may be queued as ready before the V100 build, checker and dynamic trace-semantic gates close. |

These counts total 20.  The clean Parboil source at `4e0fc548...`, clean
GPU-app-collection/Rodinia source at `dad09cb0...`, and the SDK 4.2 object at
`b059fdae...` were rechecked locally without modifying any source tree.  The
Parboil source-predicate adapter fixture suite remains six-for-six PASS.  This
is a low-cost E1 drift check only; it neither starts an Extended simulation nor
turns a static audit into a V100 trace claim.

BlackScholes additionally has a reproducible local CUDA-11.8 `sm_70` build
preflight (executable/PTX hashes and compatibility-input identities in
`extended20/CUDA_SDK_E1_SOURCE_AUDIT.md`). Because it was not built and
executed on the actual V100 with the source-defined output checker, it remains
`SOURCE_READY`; all exclusive readiness counts above are unchanged.
