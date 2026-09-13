# C16-G Retry570 runtime status

Status: `G2_RETRY570_CURRENT_INSTANCE_CAPABILITY_LIMITED_PERF_COUNTER_PERMISSION`.

The new-node observed identity is bound by
[`C16_RETRY570_NODE_IDENTITY_RECEIPT.json`](../../../review_packs/C16_MULTIMODEL_NATIVE/lane_g_retry570/C16_RETRY570_NODE_IDENTITY_RECEIPT.json).
It is an RTX3090 / SM86 node with actual driver `570.124.04`; this is an
observed receipt, not a marketplace claim.  Its 50 GiB remote data disk is
below the 100 GiB formal-capture storage gate, so exact frozen C targets remain
blocked regardless of qualification outcome.  No C target has been read as an
execution choice, altered, or substituted.

Q1's sole tiny NCU permission canary reached the diagnostic CUDA fixture as
root but returned `ERR_NVGPUCTRPERM`, emitted no counter result and produced no
`.ncu-rep`.  G2 is therefore current-instance capability-limited; it will not
retry metrics, targets, or privilege variants.  See
[`G2_RETRY570_NCU_CAPABILITY_LIMITED_RECEIPT.json`](../../../review_packs/C16_MULTIMODEL_NATIVE/lane_g_retry570/G2_RETRY570_NCU_CAPABILITY_LIMITED_RECEIPT.json).
This does not block Q2 NVBit compatibility qualification.

CPython 3.10.12 was built in an isolated remote prefix from the official source
archive.  The accepted 66-wheel hash-closed CP310/cu124 wheelhouse is still
being transferred and has not been installed or used yet; the base Python 3.12
environment is not a scientific runtime substitute.  NVBit 1.7.6 bootstrap is
in progress from the fixed source/archival hash.  No model payload has been
transferred.

The only eventual G4 authority is immutable C commit
`d55075b7752380d6bd22328547db21a5e24eeed2`, `SELECTOR_R/B48`.  Qwen7 raw,
AWQ S3/S4, changed shapes/context/batch/dtype/backend, CPU offload, and
target substitution remain forbidden.
