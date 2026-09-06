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
| BlackScholes | CUDA SDK 4.2 b059fdae | sm52 provenance only | PENDING_FREEZE | QA_PASSED | PENDING_CUDA11_8_SM70 | PENDING_UNSUPPORTED_AUDIT | UNKNOWN | SOURCE_READY; real-V100 build/input smoke pending |
| convolutionSeparable | CUDA SDK 4.2 b059fdae | sm52 provenance only | PENDING_FREEZE | QA_PASSED | PENDING_CUDA11_8_SM70 | PENDING_UNSUPPORTED_AUDIT | UNKNOWN | SOURCE_READY; real-V100 build/input smoke pending |
| fastWalshTransform_11_19 | CUDA SDK 4.2 b059fdae | sm52 provenance only | PENDING_FREEZE | QA_PASSED | PENDING_CUDA11_8_SM70 | PENDING_UNSUPPORTED_AUDIT | UNKNOWN | SOURCE_READY; real-V100 build/input smoke pending |
| scalarProd_13920 | CUDA SDK 4.2 b059fdae | sm52 provenance only | PENDING_FREEZE | QA_PASSED | PENDING_CUDA11_8_SM70 | PENDING_UNSUPPORTED_AUDIT | UNKNOWN | SOURCE_READY; real-V100 build/input smoke pending |
| scan | CUDA SDK 4.2 b059fdae | sm52 provenance only | PENDING_FREEZE | QA_PASSED | PENDING_CUDA11_8_SM70 | PENDING_UNSUPPORTED_AUDIT | UNKNOWN | SOURCE_READY; real-V100 build/input smoke pending |
| sortingNetworks | CUDA SDK 4.2 b059fdae | sm52 provenance only | PENDING_FREEZE | QA_PASSED | PENDING_CUDA11_8_SM70 | PENDING_UNSUPPORTED_AUDIT | UNKNOWN | SOURCE_READY; real-V100 build/input smoke pending |
| transpose | CUDA SDK 4.2 b059fdae | sm52 provenance only | PENDING_FREEZE | QA_PASSED | PENDING_CUDA11_8_SM70 | PENDING_UNSUPPORTED_AUDIT | UNKNOWN | SOURCE_READY; real-V100 build/input smoke pending |
| vectorAdd_6000000 | CUDA SDK 4.2 b059fdae | sm52 provenance only | PENDING_FREEZE | QA_PASSED | PENDING_CUDA11_8_SM70 | PENDING_UNSUPPORTED_AUDIT | UNKNOWN | SOURCE_READY; real-V100 build/input smoke pending |
| cfd_097k | Rodinia 3.1 dad09cb0 | Makefile located | PENDING_FREEZE | PENDING_FREEZE | PENDING_CUDA11_8_SM70 | PENDING_UNSUPPORTED_AUDIT | UNKNOWN | SOURCE_READY; deterministic input/checker missing |
| btree | Rodinia 3.1 dad09cb0 | Makefile located | PENDING_FREEZE | PENDING_FREEZE | PENDING_CUDA11_8_SM70 | PENDING_UNSUPPORTED_AUDIT | UNKNOWN | SOURCE_READY; output reference/checker missing |
| dwt2d | Rodinia 3.1 dad09cb0 | Makefile located | PENDING_FREEZE | PENDING_FREEZE | PENDING_CUDA11_8_SM70 | PENDING_UNSUPPORTED_AUDIT | UNKNOWN | SOURCE_READY; deterministic input/checker missing |
| gaussian | Rodinia 3.1 dad09cb0 | Makefile located | PENDING_FREEZE | PENDING_FREEZE | PENDING_CUDA11_8_SM70 | PENDING_UNSUPPORTED_AUDIT | UNKNOWN | SOURCE_READY; exact verification contract missing |
| hotspot1 | Rodinia 3.1 dad09cb0 | Makefile located | PENDING_FREEZE | PENDING_FREEZE | PENDING_CUDA11_8_SM70 | PENDING_UNSUPPORTED_AUDIT | UNKNOWN | SOURCE_READY; deterministic input/checker missing |
| lud | Rodinia 3.1 dad09cb0 | Makefile located | PENDING_FREEZE | source -v verifier | PENDING_CUDA11_8_SM70 | PENDING_UNSUPPORTED_AUDIT | UNKNOWN | SOURCE_READY; exact V100 verifier/input freeze pending |
| bfs | Parboil 4e0fc548 | CUDA Makefile located | HASHED | Python3 predicate adapter PASS | PENDING_CUDA11_8_SM70 | PENDING_UNSUPPORTED_AUDIT | UNKNOWN | SOURCE_READY, INPUT_READY, CHECKER_READY; V100 build pending |
| cutcp | Parboil 4e0fc548 | CUDA Makefile located | HASHED | Python3 predicate adapter PASS | PENDING_CUDA11_8_SM70 | PENDING_UNSUPPORTED_AUDIT | UNKNOWN | SOURCE_READY, INPUT_READY, CHECKER_READY; V100 build pending |
| histo | Parboil 4e0fc548 | CUDA Makefile located | HASHED | byte-exact checker adapter PASS | PENDING_CUDA11_8_SM70 | PENDING_UNSUPPORTED_AUDIT | UNKNOWN | SOURCE_READY, INPUT_READY, CHECKER_READY; V100 build pending |
| mri-q | Parboil 4e0fc548 | CUDA Makefile located | HASHED | Python3 predicate adapter PASS | PENDING_CUDA11_8_SM70 | PENDING_UNSUPPORTED_AUDIT | UNKNOWN | SOURCE_READY, INPUT_READY, CHECKER_READY; V100 build pending |
| sad | Parboil 4e0fc548 | CUDA Makefile located | HASHED | Python3 predicate adapter PASS | PENDING_CUDA11_8_SM70 | PENDING_UNSUPPORTED_AUDIT | UNKNOWN | SOURCE_READY, INPUT_READY, CHECKER_READY; V100 build pending |
| stencil | Parboil 4e0fc548 | CUDA Makefile located | HASHED | Python3 predicate adapter PASS | PENDING_CUDA11_8_SM70 | PENDING_UNSUPPORTED_AUDIT | UNKNOWN | SOURCE_READY, INPUT_READY, CHECKER_READY; V100 build pending |

## Capture queue rule

No Extended row is TRACE_CAPTURE_READY yet. Paper SYR2K, SpMV and 2MM retain
exclusive physical-capture priority. While that queue runs, E1 may advance rows
independently through deterministic source, V100 build, input/checker and
unsupported-feature evidence. As soon as a row reaches TRACE_CAPTURE_READY,
it joins the sequential V100 queue after Paper-10 2MM ARCHIVE_PASS; every
capture then follows archive, copyback, local immutable validation and
proof-bound streaming eviction before the next storage-constrained capture.
