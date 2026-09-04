# M4A-PR — Finalize the Capture Package Before Renting GPU

## Status

**AUTHORIZED NOW.**

This is the final no-rental preparation stage for Track B. `M4A_PRECAPTURE_PREP` and `M4A_PRECAPTURE_FIXUP` are accepted preparation checkpoints. Route E remains the preferred formal self-capture candidate: **one node with 4 same-model SM86 GPUs, real TP=4, NVBit injected only into rank 0**.

Real external capture (`M4A-C`) remains **NOT AUTHORIZED**. This stage must finish everything practical on the existing server so that, after ChatGPT review, renting the GPU node is primarily an execution/validation task rather than an environment-design task.

## User-confirmed candidate rental snapshot

`USER_CONFIRMED`, mutable availability snapshot from 2026-09-02:

- AutoDL currently showed RTX 3080 Ti 12 GiB / SM86 hosts with at least four idle GPUs on one physical host;
- a preferred candidate had 6 / 8 GPUs idle and expandable local storage up to about 1.6 TB;
- another candidate had 5 / 8 idle and expandable storage up to about 2 TB;
- the displayed host stack used a recent NVIDIA driver and CUDA 13.x environment.

This snapshot proves only that a feasible host class exists. Do not hard-code a host ID as permanent truth. M4A-C must revalidate model, GPU count, SM86 capability, VRAM, driver/toolkit, host memory, and free disk immediately after rental.

## Objective

Close all known pre-rental gaps in the Route-E package:

1. prove rank-0-only injection semantics structurally and with no-GPU mock tests;
2. prevent model loading / flat-buffer rebinding from becoming part of the formal SASS trace;
3. define separate prefill and first-decode ROI capture paths;
4. freeze the software/model/tracer environment as far as possible without downloading model weights;
5. make NVBit acquisition/build provenance reproducible and checksummed;
6. split host-only preflight from post-build tracer preflight;
7. extend metadata preparation to include real KV-cache ranges/lifetimes where observable;
8. retain and classify NCCL/collective kernels without forcing a premature keep/drop policy;
9. create a dry-run-ready AutoDL rental checklist and one-command bootstrap/capture entry;
10. run all no-GPU syntax/unit/mock tests and produce a review pack.

## PR0 — Provenance / current-package audit

Before editing, verify:

- branch `hrl/llm-trace-prep-v0` is clean and at/after `9a02eecc9534726294c7e6ae2a5c8db3bbc05988`;
- M4A-C authorization guard still blocks execution by default;
- Route E scripts exist and no full-model single-GPU fallback has been added;
- current frozen tracer is the Accel-Sim 1.x NVBit tracer and `install_nvbit.sh` points to NVBit 1.7.6;
- `tracer_tool.cu` supports `ACTIVE_FROM_START=0` and profiler-controlled activation via `cuProfilerStart/cuProfilerStop` semantics.

Record exact source anchors in the review pack.

## PR1 — Fix rank-0-only NVBit injection contract

The current design has a structural hazard if a parent driver exports `CUDA_INJECTION64_PATH` before `torchrun`: child ranks may inherit injection even though `rank0_nvbit_exec.sh` intends to set it only for rank 0.

Required implementation:

- the top-level M4A driver must **not globally export** `CUDA_INJECTION64_PATH` for Route E;
- it may export only a neutral path variable such as `M4A_NVBIT_PATH`;
- before launching `torchrun`, explicitly unset inherited `CUDA_INJECTION64_PATH` unless a non-Route-E diagnostic explicitly requires otherwise;
- `rank0_nvbit_exec.sh` alone sets `CUDA_INJECTION64_PATH` when `M4A_PHASE=trace && RANK=0`;
- ranks 1–3 must execute with that variable absent;
- smoke phase: every rank executes without NVBit injection.

Add a no-GPU mock test that simulates ranks 0–3 and records the environment seen by the child command. Acceptance requires:

- smoke: injection absent on all four ranks;
- trace: injection present only on rank 0;
- failure if rank metadata is missing or inconsistent.

Do not weaken the M4A-C authorization guard.

## PR2 — Formal ROI tracing policy: do not trace model load

The formal trace must represent inference regions, not the large amount of framework/model initialization and flat-buffer copy work.

Use the existing frozen tracer capability rather than inventing a second tracer if practical:

- `ACTIVE_FROM_START=0` for formal LLM trace runs;
- activate instrumentation with CUDA profiler start/stop calls only around the selected inference region;
- perform model load, TP sharding, flat-weight rebinding, warmup needed for stable execution, and static metadata preparation while tracing is inactive.

Prepare an explicit region control abstraction in the workload wrapper. It must fail if the requested formal trace region cannot be enabled/disabled deterministically.

### Required formal trace regions

Prepare at least these independent routes:

- `prefill`: run initialization with tracing inactive, trace only B8/S64 prefill;
- `decode1`: run initialization and the required prefill with tracing inactive, then trace only the first decode step;
- optional `decode_reuse`: a small diagnostic later-decode region for weight-address reuse validation, never a replacement for the formal prefill/decode1 traces.

Prefer separate capture runs/directories for `prefill` and `decode1` so each has unambiguous provenance and trace size. If the implementation instead supports multiple profiler regions in one process, prove that the frozen tracer handles this correctly before choosing it.

Add no-GPU/static tests for region selection and manifest naming. Actual CUDA profiler behavior remains an M4A-C smoke gate.

## PR3 — Freeze environment and model metadata without renting

Prepare a versioned environment lock / bootstrap contract. It must distinguish:

- host NVIDIA driver;
- CUDA toolkit used to compile the NVBit tracer;
- CUDA runtime bundled with the selected PyTorch distribution;
- Python version;
- PyTorch build/version;
- Transformers;
- Accelerate;
- Safetensors;
- Hugging Face Hub;
- NVBit version + archive URL + SHA256;
- Framework commit;
- workload-wrapper commit;
- model ID and immutable model revision.

### Host CUDA policy

Do not assume a rental page showing CUDA 13.x means the project should build/run against CUDA 13.x.

Research authoritative compatibility information and select a **documented, explicit CUDA/PyTorch/NVBit path** suitable for the pinned Route-E workload. Prefer an isolated venv/conda/container/local-toolkit path that does not modify the NVIDIA driver.

If more than one capture environment is viable, select one primary environment and one fallback. Record evidence and exact commands; do not use `latest` package versions.

### Model revision / dtype

Attempt a metadata-only resolution of `meta-llama/Llama-3.2-1B` to an immutable 40-hex revision without downloading weights. If model access requires an accepted license/token, prepare a script/checklist that consumes `HF_TOKEN` from the environment and never writes the token into Git/logs.

Inspect the immutable model config when accessible and record its declared dtype. Do not silently claim the paper used that dtype: the paper dtype remains `PAPER_DETAIL_UNAVAILABLE`. The self-capture dtype must be an explicit workload choice with provenance.

### Tensor-parallel API proof

Against the pinned Transformers source/version, verify by source/API inspection that the selected Llama class / `tp_plan` path supports the intended real TP=4 route. This is a source-level readiness check, not a substitute for the real four-GPU smoke.

## PR4 — NVBit reproducibility and bootstrap scripts

The generic `install_nvbit.sh` downloads NVBit 1.7.6 without a checksum. Do not silently mutate generic upstream behavior if a project-specific wrapper is cleaner.

Prepare a Route-E bootstrap/install path that:

- uses an exact NVBit version and asset URL;
- verifies SHA256 before extraction;
- records the archive digest in the environment lock;
- builds the frozen tracer and postprocessor with an explicit CUDA toolkit path;
- records build command/log location/toolchain versions;
- never changes the host NVIDIA driver;
- fails rather than falling back to another NVBit version.

Prepare a tiny generic CUDA/NVBit tracer smoke script for M4A-C. It must be runnable before model download/LLM work and validate:

- injection works;
- one tiny CUDA kernel produces trace files;
- postprocessing produces a non-empty `kernelslist.g`;
- checksum/archive logic works.

No-GPU syntax/dry-run checks are required now; actual execution is deferred.

## PR5 — Split preflight into rental-host and capture-ready gates

The current `preflight.py` requires an already-built tracer/postprocessor, which conflates host suitability with capture readiness.

Prepare a two-step contract, for example:

### Host preflight

Runs immediately after rental and before installs/builds. It should validate/record:

- exactly four visible GPUs for Route E;
- same GPU model;
- every GPU compute capability = 8.6;
- per-GPU VRAM >= 12 GiB;
- host driver;
- host CPU/RAM;
- filesystem/free disk;
- network reachability needed for approved dependencies;
- Framework commit/branch after clone;
- no assumption that `nvcc` already exists.

### Capture-ready preflight

Runs after environment/bootstrap and validates:

- selected Python/package lock;
- selected CUDA toolkit/nvcc;
- built tracer;
- built postprocessor;
- exact NVBit digest/version;
- enough free disk (initial conservative gate may remain 500 GiB);
- four-GPU NCCL visibility / `torchrun` prerequisites;
- M4A model revision variable and external HF token availability status without printing secrets.

M4A-C formal tracing must not begin until both gates pass.

## PR6 — Complete real-allocation metadata path for Weight + KV

Existing flat-weight sidecar preparation is useful but weight-only metadata is insufficient for later object-aware translation analysis.

Extend the workload metadata path so the Route-E runtime can record the real KV cache returned/maintained by the pinned framework where observable.

At minimum prepare code capable of recording for each rank-0 KV tensor/buffer:

- object kind `KV_CACHE`;
- layer / K-or-V identity when available;
- data pointer / SimVA-labelled input range;
- size bytes;
- prefill/decode step at which it becomes active;
- whether a later step reuses, grows, or replaces the buffer;
- lifetime/end when determinable;
- classification provenance.

Do not invent activation/workspace classification. Unknown allocations remain `UNKNOWN`.

`SYNTHETIC_KV` remains prohibited in M4A; later synthetic pressure is a separate simulator mechanism.

Add CPU/fake-tensor unit tests for dynamic KV metadata and range/lifetime validation. Actual CUDA VA coverage remains M4A-C.

## PR7 — NCCL / collective capture preservation and classification

The exact paper treatment of TP collectives is unavailable. Do not force a keep/drop policy before seeing the real trace.

Prepare the capture/postprocess path so that:

- raw rank-0 ROI trace is retained intact;
- kernels are classified at least as `COMPUTE`, `NCCL_COLLECTIVE`, or `UNKNOWN/OTHER` using recorded kernel names and explicit rules;
- original raw ordering and files are never destroyed;
- a derived compute-only kernels list may be generated for parser/simulator diagnostic use;
- a derived full-list manifest remains available;
- every filtering/classification action is reproducible and logged.

M4A-C will use a tiny real trace to decide whether NCCL kernels are parser-compatible and whether the formal paper replay should retain them, exclude them, or report both. That later decision must not require recapturing the raw rank-0 ROI.

## PR8 — Trace-size / disk / archive / offload plan

Retain the proven V100-campaign safety pattern, adapted to Route E:

- tiny generic tracer smoke before model work;
- tiny LLM ROI trace before formal trace;
- measure actual trace bytes / kernel or another documented local metric;
- recompute projected formal trace size;
- require a safety margin before formal capture;
- keep 500 GiB only as a conservative initial rental gate, not a paper-derived size claim;
- support local expandable NVMe and checksum-verified copy-back;
- do not release the rented instance until the archive and destination checksums match when operationally practical.

Prepare separate manifests/archives or clearly separable subdirectories for `prefill` and `decode1`.

## PR9 — AutoDL rental checklist

Create/update a concise `AUTODL_RENTAL_CHECKLIST.md` that lets the user choose a host without architecture knowledge.

For Route E require at rental time:

- one physical host row with >=4 currently idle GPUs;
- choose 4 GPUs in one instance;
- all selected GPUs same model and SM86;
- RTX 3080 Ti 12 GiB is acceptable; RTX 3090 24 GiB provides more headroom but is not required;
- enough host RAM for four-rank Python/TP execution;
- >=500 GiB free/expandable local storage before formal trace, preferably substantially more if inexpensive;
- SSH / copy-back access;
- no formal reliance on the web page's displayed CUDA version until host/capture preflight validates the chosen isolated environment.

Include the 2026-09-02 AutoDL multi-3080Ti availability only as a `USER_CONFIRMED` snapshot that must be rechecked.

## PR10 — No-GPU closeout tests

Before closeout run at minimum:

- Python compile/static tests for all project capture utilities;
- shell syntax tests;
- existing flat-weight planner self-test;
- metadata validator self-test;
- new KV metadata fake-tensor tests;
- rank0-only injection mock test for all four ranks;
- ROI region-selection/static test;
- M4A-C authorization guard test;
- environment-lock/bootstrap dry-run or non-destructive validation;
- kernel-classifier unit test with synthetic kernel names;
- `git diff --check`;
- clean status after commits.

No GPU, model weights, or formal trace is required or authorized in this stage.

## Required deliverables

Update/create stable files as appropriate:

- `docs/vm_tlb/llm/AUTODL_RENTAL_CHECKLIST.md`
- `docs/vm_tlb/llm/CAPTURE_ENV_LOCK.md`
- `docs/vm_tlb/llm/TRACE_ACQUISITION.md`
- `docs/vm_tlb/llm/ROI_TRACE_POLICY.md`
- `docs/vm_tlb/llm/METADATA_SCHEMA.md`
- `docs/vm_tlb/llm/NCCL_KERNEL_POLICY.md`
- `docs/vm_tlb/llm/WORKLOAD_CONTRACT.md`
- project-specific bootstrap/preflight/smoke/classification utilities under `util/llm_trace_capture/`

Review pack:

`docs/vm_tlb/review_packs/M4A_PRERENTAL_FINALIZE/`

Track-B report:

`docs/vm_tlb/codex_handoff/m4a/LATEST_REPORT.md`

## Acceptance criteria

M4A-PR PASS requires all of the following:

1. Route E remains the only selected formal self-capture route; no full-model fallback exists.
2. Rank0-only NVBit injection is structurally fixed and mock-proven.
3. Formal ROI tracing excludes model load/flat-buffer initialization and provides distinct prefill/decode1 capture routes.
4. Environment/tool/model lock is explicit, reproducible, and contains no `latest` dependency.
5. NVBit artifact is versioned and checksum-verified by the prepared bootstrap path.
6. Host preflight and capture-ready preflight are separate and testable.
7. Weight metadata remains valid and real KV-cache metadata collection is implemented/tested to the strongest no-GPU level.
8. Raw NCCL/collective trace information will be retained and classified so the later keep/drop policy does not require recapture.
9. AutoDL rental checklist is precise enough for the user to select a 4xSM86 host.
10. All no-GPU unit/syntax/mock tests pass.
11. M4A-C authorization guard still blocks external capture.
12. No GPU was rented, no model weights were downloaded as part of formal capture, no formal trace was collected, and no Core VM semantics were changed.

`CONDITIONAL_PASS` is allowed only for checks that genuinely require the rented four-GPU host (NVBit execution, TP/NCCL runtime, real CUDA profiler ROI control, actual VA stability/coverage, real trace size, parser compatibility).

## STOP boundary

After M4A-PR closeout:

- commit and push `hrl/llm-trace-prep-v0`;
- update Track-B report and review pack;
- report the exact recommended AutoDL host requirements and the prepared bootstrap/capture commands;
- STOP.

Do **not** rent a GPU, set `M4A_C_AUTHORIZED=1` for a real workload, download the formal model weights for capture, collect a formal trace, implement Segmentation, or inject synthetic KV traffic.

ChatGPT will review M4A-PR. Only after that review will the user rent a host and a new handoff authorize M4A-C.
