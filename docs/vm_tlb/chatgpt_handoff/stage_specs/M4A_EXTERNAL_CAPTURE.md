# M4A-C — External Rented-GPU Capture and Import Validation

## Status

**PREPARED BUT NOT AUTHORIZED.**

This is the future rented-GPU execution stage. It begins only after:

1. `M4A_PRERENTAL_FINALIZE` closes out;
2. ChatGPT reviews that closeout as ready;
3. the user rents/selects a suitable Route-E host;
4. a new ChatGPT-owned handoff explicitly authorizes M4A-C.

## Selected formal candidate

Route E:

- one physical host;
- 4 same-model SM86 GPUs;
- real tensor parallelism TP=4;
- rank 0 only receives NVBit injection;
- raw rank-0 inference ROI trace is retained intact;
- self-captured trace is `PAPER_COMPATIBLE_SELF_CAPTURE`, never the authors' exact trace.

RTX 3080 Ti 12 GiB is an acceptable SM86 host class if runtime smoke passes. RTX 3090 24 GiB provides more headroom but is not required by policy.

## Objective

Execute the fully prepared package on the rented node, validate every hardware/runtime assumption cheaply before expensive tracing, collect separate short-context prefill and first-decode traces plus metadata, copy them back with integrity checks, and validate parser/simulator compatibility without modifying M1-M3 VM semantics.

## Entry prerequisites

Require all of the following before any formal tracing:

- M4A-PR closeout reviewed as `READY_TO_RENT`;
- selected host can allocate 4 GPUs in one instance;
- all 4 GPUs are same model, SM86, and meet the prepared VRAM requirement;
- expandable/free local storage satisfies the initial gate;
- capture-package SHA is frozen;
- environment/tool lock is frozen;
- model revision/dtype choice is frozen or an explicit token-gated resolution step is part of the prepared bootstrap;
- `M4A_C_AUTHORIZED` is set only after the new handoff authorizes this stage.

Do not substitute SM70/SM80/SM89/SM90/SM120 SASS for the RTX3070-class paper route.

# C0 — Cheap rental smoke gates before model tracing

The rental session must begin with cheap gates. Do not download/run the full formal workload until these pass.

## C0.1 Host-only preflight

Immediately record/validate:

- full `nvidia-smi` and `nvidia-smi -L`;
- exactly 4 visible GPUs;
- identical GPU model;
- compute capability 8.6 on every GPU;
- VRAM on every GPU;
- driver version;
- host CPU/RAM;
- OS/image;
- filesystem and free/expandable local disk;
- network access required by the prepared dependency/model path;
- cloned Framework branch/SHA.

This gate must not require an already-built tracer.

If hardware differs from the approved Route-E requirements, STOP before installs/model work.

## C0.2 Environment/bootstrap gate

Execute the prepared isolated bootstrap. Validate the exact lock:

- Python;
- PyTorch + CUDA runtime build;
- Transformers / Accelerate / Safetensors / HF Hub;
- selected CUDA toolkit / `nvcc` for tracer build;
- NVBit exact version + archive SHA256;
- tracer/postprocessor build.

Do not update the NVIDIA driver. Do not silently choose the rental page's CUDA label or `latest` packages.

Run the capture-ready preflight after bootstrap.

## C0.3 Generic NVBit tracer smoke

Before model download/LLM work, run one tiny known-good CUDA program through:

`NVBit injection -> trace -> postprocess -> kernelslist.g -> checksum/archive validation`.

Required evidence:

- command/exit status;
- non-empty raw trace;
- non-empty postprocessed kernels list;
- tool/tracer version identity;
- archive/checksum integrity;
- wall-clock.

Failure blocks all LLM work.

## C0.4 Rank0-only injection proof on real 4-GPU torchrun

Run the prepared tiny four-rank injection smoke. Prove on the actual node:

- smoke phase: no rank has NVBit injection;
- trace phase: rank 0 has injection;
- ranks 1–3 do not inherit `CUDA_INJECTION64_PATH`;
- all four ranks launch and synchronize correctly.

Failure blocks LLM tracing.

## C0.5 TP + contiguous-weight runtime smoke

Bring up the pinned Llama-3.2 1B TP=4 workload **without tracing first**.

Validate:

- exact immutable model revision;
- selected self-capture dtype/quantization provenance;
- B8 / S64 / G3 workload contract;
- real world size 4;
- correct rank/GPU mapping;
- model output sanity;
- runtime one-buffer weight bind succeeds on every participating rank as designed;
- rank0 flat-buffer base/size/tensor offsets are valid;
- a second forward/check confirms the framework did not silently replace/reallocate weight backing storage;
- no unexpected OOM on the selected VRAM class.

Do not call this evidence of GPU physical contiguity. Simulated physical contiguity remains a later VM mapping input.

## C0.6 ROI-control smoke

Before a large LLM trace, validate the prepared profiler-controlled tracing path:

- tracer loaded but inactive during model load/TP setup/flat binding when `ACTIVE_FROM_START=0`;
- instrumentation activates only for the selected ROI;
- a tiny prefill/decode-region test produces trace only from the intended region;
- initialization kernels are absent from the formal ROI trace.

Failure blocks formal trace.

## C0.7 Tiny LLM trace + NCCL inventory

Capture the smallest practical real TP4/rank0 ROI sample.

Measure/record:

- kernel sequence;
- compute vs NCCL/collective vs unknown classification;
- whether raw NCCL kernels postprocess correctly;
- whether full and derived compute-only kernel lists can be generated reproducibly;
- trace-size growth metric and disk projection;
- metadata Weight/KV coverage;
- parser compatibility smoke with the frozen paper-reproduction parser/config path when practical.

The raw trace must be retained intact. Do not decide a permanent paper-exact NCCL keep/drop policy by deleting files.

If parser/ISA/NCCL behavior creates a material ambiguity, STOP for review before formal trace.

# C1 — Formal workload validation

After every C0 gate passes, run the frozen workload normally once more and record:

- model / immutable revision;
- package/environment lock;
- B8/S64/G3;
- TP=4 Route E;
- deterministic input IDs;
- self-capture dtype;
- rank mapping;
- output sanity;
- Weight and real KV metadata sidecar generation.

# C2 — Formal separate ROI trace captures

Do not capture full 12K context. Long-context pressure remains a later synthetic translation mechanism.

Collect at minimum two separate, provenance-distinct rank0 traces:

## C2.1 Prefill

- initialization / TP setup / flat binding executed with tracing inactive;
- trace only B8/S64 prefill ROI;
- save raw trace, postprocessed list, metadata, kernel classification, manifest, checksums.

## C2.2 First decode

- initialization and required prefill executed with tracing inactive;
- trace only first decode step;
- save raw trace, postprocessed list, metadata, kernel classification, manifest, checksums.

Optional:

- one later decode/reuse trace for validating stable weight addresses/reuse, clearly diagnostic.

# C3 — Metadata runtime validation

For the formal runs validate:

- Weight range/tensor offsets stable;
- all known Weight tensors fall in the flat rank0 region;
- real KV cache ranges are recorded where observable;
- KV reallocation/growth/lifetime behavior is recorded across prefill/decode;
- unknowns remain `UNKNOWN`;
- no `SYNTHETIC_KV` entries exist;
- no unjustified active-range overlap;
- address classification provenance is recorded;
- trace-address coverage is quantified.

# C4 — NCCL / kernel-list decision evidence

Retain raw rank0 traces regardless of policy.

Produce:

- raw/full kernels list;
- classified kernel manifest;
- derived compute-only list;
- parser/simulator result for each relevant list when feasible.

If the paper's single-partition interpretation still leaves collective treatment ambiguous, report both and STOP before declaring one `PAPER_EXACT`. A later paper-reproduction handoff may select the formal replay policy without recapturing the raw trace.

# C5 — Trace size / archive / copy-back

Using the measured tiny trace, recompute disk projection and require safety margin before completing formal capture.

For each trace bundle:

- generate SHA256 manifest;
- package with the approved archive format;
- integrity-test the archive;
- copy to the main project server / persistent destination;
- verify destination checksum;
- record local and destination paths.

Do not release/delete the rental instance until required trace bundles are safely copied and verified when operationally practical.

# C6 — Frozen parser/simulator compatibility

After import to the main server, validate:

- trace parser accepts the selected raw/derived lists;
- ISA/config compatibility is explicit;
- a minimal simulator smoke starts/completes where feasible;
- trace addresses correspond to sidecar ranges as expected;
- no M1-M3 simulator modification is made merely to accept an incompatible trace.

Classify resulting traces as:

- `PAPER_COMPATIBLE_SELF_CAPTURE`, or
- `DOCUMENTED_APPROX_CAPTURE` only if later explicitly approved.

Never call a self-captured trace the authors' exact trace.

## Required deliverables

Review pack:

`docs/vm_tlb/review_packs/M4A_EXTERNAL_CAPTURE/`

Include at minimum:

- rental host provenance;
- environment/tool lock realization;
- C0 gate summary;
- rank0-only injection proof;
- TP/flat-weight runtime validation;
- ROI-control proof;
- tiny-trace/NCCL inventory;
- prefill trace manifest;
- decode1 trace manifest;
- Weight/KV metadata validation;
- raw/full and compute-only kernel-list identities;
- parser/simulator compatibility;
- archive/copy-back checksums;
- exactness classification;
- raw artifact index (not payloads in Git).

## Acceptance criteria

M4A-C PASS requires:

1. approved 4x same-model SM86 host used;
2. host and capture-ready preflights PASS;
3. generic NVBit smoke PASS;
4. actual four-rank rank0-only injection proof PASS;
5. TP=4 workload and flat-weight runtime smoke PASS without OOM/semantic fallback;
6. ROI control proves model load/setup are outside formal trace;
7. tiny LLM trace and NCCL classification/parser smoke are explainable;
8. separate prefill and first-decode traces collected;
9. Weight + real KV metadata collected/validated to the available evidence level;
10. trace-size/disk/archive/copy-back integrity PASS;
11. parser/config compatibility validated or any residual ambiguity explicitly blocks later formal replay selection;
12. provenance/exactness classification complete;
13. no Core VM semantic changes; no Segmentation/sub-entry/synthetic-KV mechanism started.

## STOP boundary

After closeout, push report/review evidence and STOP before:

- paper L2-TLB sub-entry implementation;
- Segment Table implementation;
- synthetic-KV simulator injection;
- M4B/M5 performance reproduction.
