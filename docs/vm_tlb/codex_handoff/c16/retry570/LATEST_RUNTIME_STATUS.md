# C16-G Retry570 runtime status

Status: `NVBIT_RETRY570_LLAMA_MODEL_CANARY_INCONCLUSIVE_FILTERING_NOT_DISAMBIGUATED`.

## Current bounded PyTorch/NVBit first-kernel isolation

The current non-scientific diagnostic checkpoint is
[`lane_g_retry570_pytorch_stage_diagnostic`](../../../review_packs/C16_MULTIMODEL_NATIVE/lane_g_retry570_pytorch_stage_diagnostic/),
with fixed `PUBLISH_MANIFEST.json` SHA256
`7b803deecea24e273f3c368081174a27910e7bfd94f503232c8e61cd4129a553`.
Its status is `NVBIT_PYTORCH_FIRST_KERNEL_STAGE_DIAGNOSTIC_COMPLETE`; its
runtime producer source is
`982135c3a7d946f4d4be8705239d4b332802330b` and the diagnostic-only NVBit
timing-probe tool is hash-closed at
`07ba183f1f27f231af249ad6f2329a70b84d3de75e0bff8974696e5b8c59b845`.

It ran C0 CUDA initialization, C1 allocation, C2 tensor fill, C3 elementwise
add, and C4 small GEMM as ten independent native/NVBit processes. All completed
under their fixed 60-second limits, produced no trace, and are not scientific
timing or C-target evidence. C2/C3 had one related function and about 0.23 s
of `nvbit_get_instrs()` discovery. C4's first CUTLASS GEMM launch expanded to
89 related functions (88 enumerated), 66,032 total static instructions and
19.969523 s of instruction discovery; insertion/enable/synchronization then
completed, with the full C4 probe ending at 20.041227 s and child completion
at 23.064094 s. The retained five-second snapshots show advancing discovery
markers and `do_wait`/futex wait states, not a fixed mutex deadlock; node policy
denied symbolized `/proc/.../stack` reads.

This localizes the minimal-PyTorch boundary to related-function/static-
instruction discovery expansion (B), rather than establishing A, C, or D. It
does not reopen the already-closed 300-second watch and does not authorize
Llama, Qwen, a trace, or any C frozen target. A separately authorized future
longer diagnostic could be technically useful only with an exact bounded
function/related-function scope. All 75 retained payloads (772,515 bytes) have
remote-to-local size/SHA closure, tree SHA256
`d411d972d08fe9d5f255e2dec84251cfd74c9a70da6bb29faa90f7ea5b73aaaa`;
`REMOTE_ONLY_REQUIRED_ARTIFACT_COUNT=0` and `ACTIVE_GPU_PROCESS_COUNT=0`.

## NVBit nvdisasm path-repair gate

The new closeout is
[`retry570_nvdisasm_path_repair`](../../../review_packs/C16_MULTIMODEL_NATIVE/lane_g_retry570_nvdisasm_path_repair/),
with fixed `PUBLISH_MANIFEST.json` SHA256
`c9b4daf8a2f8bd2a8c54d2ddd27c3ec2ed6ca625c3c8d2393436e9aec2665f59`.
Its result is
`NVBIT_NVDISASM_PATH_CONTRACT_FIXED_RUNTIME_SMOKE_NOT_QUALIFIED`.

This was a harness configuration defect, not a missing CUDA component:
`/usr/local/cuda-12.4/bin/nvdisasm` exists and is version 12.4.127, while
the original child PATH omitted `/usr/local/cuda-12.4/bin`. NVBit 1.8 requires
`nvdisasm` to be discoverable through PATH. The fixed source contract verifies
the absolute path, prefixes that exact directory into every injected child
PATH, records the absolute provenance, and sets `NVDISASM=nvdisasm`; it does
not depend on a transient shell export. The repair source is
`b76fb566144bb7ca4f7c4356337b36bc0fa65903`; the fixed smoke runtime is
`26a24b07f922df259dcc6823d1915c69b6f0f02a`.

Gate A (`nvdisasm --version`) and Gate B (NVBit 1.8 official
`instr_count_bb` plus vectoradd) passed. Gate C, the Lane G PyTorch
first-kernel smoke with the same environment contract and official tool,
passed the old `nvdisasm not found on PATH` boundary and reached
`FIRST_CUDA_KERNEL_SUBMISSION_BEGIN`, but did not complete a first CUDA kernel
or emit the official kernel marker within its fixed 60 seconds. It produced no
trace or scientific data. Its raw historic `EXTREME_STARTUP_OVERHEAD` label is
retained but normalized by `c9b0be4435b31f389d34854a937a6dff2e42eb1d` as a
60-second path-smoke timeout—not a 300-second long-watch diagnosis.

Accordingly, formal long-watch reapplication is **not qualified**. No
long-watch, model, C target, trace, scientific capture, or 6+6-window rerun
is authorized from this checkpoint. The remote has no active GPU process or
measurement marker, and all retained smoke payloads are locally SHA-closed.

## One-shot NVBit long-watch closeout

The retained microreproducer closeout remains valid and its existing 6+6
bounded NVBit windows were not rerun. The new compact checkpoint is
[`retry570_long_watch_diagnostic`](../../../review_packs/C16_MULTIMODEL_NATIVE/lane_g_retry570_long_watch_diagnostic/),
whose `PUBLISH_MANIFEST.json` SHA256 is
`e5a2488994a1abd82b1ebb87792ad6b662a28b23aa34fa87547708c19cccac9d`.
The runtime harness actually used is fixed at
`d8021532adfd94b4196785475f5c3914a3f51c2e`; its existing NVBit1.8 map-only
tool remains fixed at source `f08af62e4bb77559617bd14d5df9a13d2e236873`
and SHA256
`ae4e4e632a4afad0d5dda4b7f7aac2b460135784676765350945137a722cb5c0`.

The no-NVBit control completed the same finite index-select microreproducer
and observed first CUDA-kernel completion at `2.820031002163887` seconds.
It was followed by exactly one NVBit map-only long-watch, durably reserved at
300 seconds with 5-second sampling. That process reached
`FIRST_CUDA_KERNEL_SUBMISSION_BEGIN` but ended after about 2.87 seconds,
before a first completed CUDA kernel, because the NVBit-side resolver emitted
`ERROR: /usr/local/cuda-12.4/bin/nvdisasm not found on PATH!!!`. The executable
was independently observed on the node; this evidence establishes only a
tool-startup/path-resolution configuration failure. It did not reach the
300-second discriminator. Accordingly the closeout state is
`NVBIT_LONG_WATCH_DIAGNOSTIC_INCONCLUSIVE_TOOL_STARTUP_CONFIGURATION_FAILURE`:
it does **not** establish either
`NVBIT_PYTORCH_PRE_FIRST_KERNEL_STALL_CONFIRMED` or
`NVBIT_PYTORCH_EXTREME_STARTUP_OVERHEAD`.

The one-shot authorization is closed, so a second long-watch is forbidden.
No trace, static map, model, Qwen, Llama, frozen C target, timing result, or
scientific capture was produced. All small retained payloads and the ledger
are SHA-closed locally; `REMOTE_ONLY_REQUIRED_ARTIFACT_COUNT=0` and
`ACTIVE_GPU_PROCESS_COUNT=0`.

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
