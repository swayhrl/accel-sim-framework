# C16-G Retry570 runtime status

Status: `NVBIT_RETRY570_MEMORY_TRACE_PATH_QUALIFIED_WAITING_USER_STORAGE_DECISION`.

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
archive.  After bounded `libbz2-dev` and `libffi-dev` build-dependency repair,
the 66-wheel CP310/cu124 wheelhouse passed no-index resolver dry-run,
installation, `pip check`, and import closure.  The base Python 3.12
environment was not a scientific runtime substitute.  NVBit 1.7.6 archive and
both tools were hash-closed.

The original Q2 closeout correctly recorded that NVBit 1.7.6 `instr_count`
and the C16 tracer timed out at `ELEMENTWISE_PREPARE`; it remains a retained,
non-scientific diagnostic record.  A subsequent bounded V2 discriminator
held all node and PyTorch inputs fixed, then established a narrower boundary:
NVBit 1.7.6 `instr_count_bb` and `mem_trace` also time out before the workload
kernel, while NVBit 1.8 `instr_count_bb`, `instr_count`, and `mem_trace` pass
both elementwise and GEMM.  NVBit 1.8 official `mem_trace` emits real memory
records, and the C16 tracer rebuilt against NVBit 1.8 emits real traces for
both workloads.  The resulting state is
`NVBIT_RETRY570_MEMORY_TRACE_PATH_QUALIFIED`, not a claim about model or C
target compatibility.

No model payload was transferred, and no Llama, Qwen0.5, Qwen7-AWQ, G2
target, or G3 target was launched.  The node must remain idle pending an
explicit user decision to expand storage: 37,780,586,496 available remote
bytes remains below the 100 GiB frozen-target gate.

The full compact evidence and dual-endpoint diagnostic raw closure are in
[`retry570_q2_closeout`](../../../review_packs/C16_MULTIMODEL_NATIVE/lane_g_retry570_q2_closeout/).
`REMOTE_ONLY_REQUIRED_ARTIFACT_COUNT=0` and `ACTIVE_GPU_PROCESS_COUNT=0`.
Its fixed closeout manifest is `PUBLISH_MANIFEST.json`, SHA256
`56aa8adfe81e259ff358d6d06341444136481bf7bfb2ff6e7878c27a48735804`;
the independent payload validation receipt is `PUBLISH_VALIDATION_RECEIPT.json`.
The direct-fixture producer anchor is `d67d2aea7b6e4e17b2e095633700720da13135ce`;
the existing PyTorch workload producer anchor is
`d1a87532ac71de796b48c622743bb1826eb2ecec`.  This closeout publication
commit is deliberately distinct from both runtime-code anchors.

The current discriminator evidence is in
[`lane_g_retry570_nvbit_v2`](../../../review_packs/C16_MULTIMODEL_NATIVE/lane_g_retry570_nvbit_v2/).
Its dual-endpoint transfer closure is
`NVBIT_COMPATIBILITY_TRANSFER_RECEIPT.json`; it has no remote-only required
artifact and the node has no active GPU process.  Its fixed publish manifest
SHA256 is `46189eb85b716ba39c73406613d88852d33bda461965d9dc77f02abe904fc8fa`.

The only eventual G2/G3 authority was immutable C commit
`d55075b7752380d6bd22328547db21a5e24eeed2`, `SELECTOR_R/B48`.  Qwen7 raw,
AWQ S3/S4, changed shapes/context/batch/dtype/backend, CPU offload, and
target substitution remain forbidden.
