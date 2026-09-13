# C16-G Retry570 runtime status

Status: `NVBIT_RETRY570_LLAMA_MODEL_CANARY_INCONCLUSIVE_FILTERING_NOT_DISAMBIGUATED`.

## Current microreproducer closeout

The newest Retry570 checkpoint is
[`retry570_microreproducer_discriminator`](../../../review_packs/C16_MULTIMODEL_NATIVE/lane_g_retry570_microreproducer_discriminator/).
Its fixed `PUBLISH_MANIFEST.json` SHA256 is
`87ed9580ebad311a6bd553cd07fec8ed53d462b783d6728aa61815cf8736efb0`.
The publication-generator source commit is
`c1325a324ef94f2b5dcc0399ff507dce86f60c2a`; the actual final NVBit
diagnostic producer is distinctly anchored at
`f08af62e4bb77559617bd14d5df9a13d2e236873`.

It used no full Llama model to discover a static map. A finite exact
`torch.index_select` microreproducer matched the observed RTX3090,
driver `570.124.04`, PyTorch `2.5.1+cu124`, and
`libtorch_cuda.so` SHA256
`761b14acafb8b02011e32d11bd437b63cca3fe882b9c4a02c89fd01d738ccb6a`.
The complete Llama candidate mangled identity was required, never a short
name. Under correct `CUDA_INJECTION64_PATH`, both the optimized mapper and a
final lifecycle-free exact-map tool bounded out before the first micro CUDA
kernel. The latter had no context/tool-init hook, CUDA allocation,
instrumentation, or mapper cache. Consequently neither a static map nor an
authoritative NVBit instruction index exists. This is a narrow
NVBit/PyTorch callback-path limitation for the setup, not a causal driver or
model-incompatibility claim.

Both the P0 Llama deployment and the isolated microreproducer have exactly
six accounted NVBit windows; no additional NVBit diagnostic, Llama, Qwen, C16
tracer, or C frozen-target operation is authorized on this node. The retained
raw/ledger/marker evidence is locally SHA-closed:
`REMOTE_ONLY_REQUIRED_ARTIFACT_COUNT=0`,
`ACTIVE_GPU_PROCESS_COUNT=0`. The state remains `INCONCLUSIVE`, not NO-GO.

The NVBit-native static-index pass is closed in
[`retry570_nvbit_native_static_map`](../../../review_packs/C16_MULTIMODEL_NATIVE/lane_g_retry570_nvbit_native_static_map/).
It does **not** establish an index: `348` remains only
`HISTORICAL_CANDIDATE_ORDINAL`, and `34` only `SASS_TEXT_LINE_COUNTER`.
The direct `nvbit_get_instrs()` map-only Llama S0 run reached model load but
timed out at 180 seconds without forward completion, target-function launch,
or `LLAMA_INDEXSELECT_NVBIT_STATIC_MAP.tsv`. Thus no authoritative NVBit
static index or memory-instruction target exists; exact-memory/C16 tracing,
Qwen, and C frozen targets remain forbidden. This is not a zero-record NO-GO
or a model/NVBit incompatibility claim. All retained diagnostic artifacts are
locally hash-closed and `REMOTE_ONLY_REQUIRED_ARTIFACT_COUNT=0`.

The post-resize node consumed the exact minimal immutable P0/Llama
package subset.  P0 commit
`20fb38e6ca629f1a93db7939248bd1a03790724c` and package manifest SHA256
`ac59f0d2aca95021c686948d7244ce50375530bbe983c8508ca5f6954e80230f`
are closed in [`retry570_p0_llama`](../../../review_packs/C16_MULTIMODEL_NATIVE/lane_g_retry570_p0_llama/).
The frozen M1 S0/TEXT binding is exact B1/T128/decode4 and has no tokenizer
execution or context resize. The disambiguation run binds runtime source
commit `48c330fbda219db12146ea96ed2d08230c3e8b08`; its historical producer
code anchor is `c4597507d50d4ebce67ef0efc6ea50dcdea1183c`.

The `48c330fb` no-go package remains a valid historical publication/provenance
checkpoint, but its scientific inference is superseded: its valid official
intervals `[0,1)` and `[0,8)` did not prove that a memory instruction was
covered. The new hash-closed package is
[`retry570_llama_model_disambiguation`](../../../review_packs/C16_MULTIMODEL_NATIVE/lane_g_retry570_llama_model_disambiguation/).
It used the identical Llama identity to obtain a real NVTX-contained kernel:
`indexSelectLargeIndex`, nsys grid ID `1`. The required frozen contract is
`LDG.E` at static ordinal `348`, `INSTR_BEGIN=348`, `INSTR_END=351`. An
already-completed historical attempt instead bound `[34,35)` because `34` was
an SM86 SASS-text instruction-line counter. There is no established
equivalence between `34` and the authoritative `348`; that attempt is retained
only as `UNQUALIFIED_ORDINAL_34_ATTEMPT`, not as a test of the frozen contract.
It also timed out at its 180 s guard before proving a target launch, memory
record, or model-forward completion. Therefore this is
`MODEL_NVBIT_QUALIFICATION_DIAGNOSTIC` only, never native timing or a C target
result; it is neither a disambiguated zero-record NO-GO nor a model-NVBit
incompatibility claim. The C16 tracer was not run.

No Qwen0.5, Qwen7-AWQ, or raw-Qwen payload has been transferred, and no C
`SELECTOR_R/B48` frozen target has been read or executed. No target/shape/
context/dtype/backend/offload or kernel-name substitution occurred.
`NVBIT_STORAGE_ESTIMATE.json` remains `NOT_APPLICABLE_NO_REAL_MODEL_TRACE`;
both local receiver mounts remain below the 100 GiB formal-campaign gate.

The new-node observed identity is bound by
[`C16_RETRY570_NODE_IDENTITY_RECEIPT.json`](../../../review_packs/C16_MULTIMODEL_NATIVE/lane_g_retry570/C16_RETRY570_NODE_IDENTITY_RECEIPT.json).
It is an RTX3090 / SM86 node with actual driver `570.124.04`; this is an
observed receipt, not a marketplace claim.  Following resize/restart, the
remote disk is 200 GiB total with 198,796,951,552 bytes available, passing the
100 GiB formal-capture storage gate.  The new GPU UUID is recorded in the
post-resize receipt.  No C target has been read as an execution choice,
altered, or substituted.

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
target, or G3 target was launched.  Exactly one post-resize PyTorch
elementwise+C16-NVBit1.8 sanity exited normally and produced nonzero trace;
the complete prior 1.7.6/1.8 matrix was deliberately not repeated.

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

The current post-resize checkpoint is
[`lane_g_retry570_post_resize`](../../../review_packs/C16_MULTIMODEL_NATIVE/lane_g_retry570_post_resize/),
manifest SHA256 `c262464c9ee9757905b295bb177d5da6f1ce3ab8b2bb9c4a550e7b9dde0349a2`.
The next permitted stage is M1 Llama model-level NVBit qualification.

The only eventual G2/G3 authority was immutable C commit
`d55075b7752380d6bd22328547db21a5e24eeed2`, `SELECTOR_R/B48`.  Qwen7 raw,
AWQ S3/S4, changed shapes/context/batch/dtype/backend, CPU offload, and
target substitution remain forbidden.
