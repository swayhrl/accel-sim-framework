# M4 compute bring-up review pack

Result: **PASS — READY_FOR_M5_REVIEW** for the authorized frozen-source M4 domain. M5 remains forbidden.

- Core implementation: `cdeec769fd0c1be12b45d58536ecb81074d4b415`.
- Framework evidence baseline: `49f6943c7f166e28a417a99b8400eb8d235a9771`.
- Workload checkout provenance: `gpgpu-workloads` `de9cf4293f...`.

Read `VALIDATION_SUMMARY.md`, `COUNTER_SANITY.md`, and `SOURCE_ANCHORS.md`, then use `RAW_LOG_INDEX.tsv` and `generated/*.json` for reproduction. Raw logs stay external; every listed artifact has a path, byte count, and SHA-256.

The frozen GPGPU-Sim PTX frontend cannot generate the existing dynamic proxy-fence path. End-to-end F01--F03 are `SOURCE_UNREACHABLE_NA` after source audit. No fence semantics were invented or substituted. M4 correctness claims apply to the source-reachable Load/Store/Atomic/bypass domain used by the accepted workloads.
