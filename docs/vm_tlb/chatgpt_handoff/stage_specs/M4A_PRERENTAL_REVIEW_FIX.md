# M4A-PR2 — Final Review Fix Before Renting GPU

## Status

**AUTHORIZED NOW.**

M4A-P, M4A-PF, and the first M4A-PR preparation round are accepted as preparation checkpoints. Route E remains the approved formal self-capture route: one physical host with four same-model SM86 GPUs, real TP=4, rank0-only NVBit injection.

However, ChatGPT review found two concrete pre-rental engineering hazards and one related classifier gap that must be fixed before the package is promoted to final `READY_TO_RENT`.

Real external capture (`M4A-C`) remains **NOT AUTHORIZED**.

## Objective

Close the final pre-rental issues without accessing/renting a GPU:

1. make the frozen CUDA toolkit path truly control the NVBit tracer build;
2. make capture-ready validation prove the actual `nvcc` / `ptxas` provenance;
3. ensure ROI-inactive memcpy activity cannot pollute the formal replay list;
4. classify memcpy separately from compute/NCCL;
5. rerun all no-GPU package tests and return either `READY_TO_RENT_REVIEW_FIX_PASS` or `NOT_READY_TO_RENT`.

Do not redesign TP, weight/KV metadata, ROI selection, rank0 injection, or the paper workload unless a regression proves those existing mechanisms are broken.

## RF0 — Freeze source / provenance

Start from Framework branch:

`swayhrl/accel-sim-framework:hrl/llm-trace-prep-v0`

Required prior Codex closeout:

`f74b08f867d5bcb781caa0c319acf03148fb2630`

or a descendant containing the latest ChatGPT handoff.

Record:

- exact starting SHA;
- clean worktree;
- current digests of capture wrappers;
- current `CAPTURE_ENV_LOCK.md` values;
- current NVBit tracer Makefile behavior.

Do not edit `chatgpt_handoff/*`.

## RF1 — Force explicit CUDA toolkit provenance for NVBit build

### Problem

`bootstrap_route_e_nvbit.sh` accepts `--cuda-home` and invokes make with `CUDA_HOME=...`, but the frozen tracer Makefile currently resolves `nvcc` / `ptxas` by command name. On a rental host whose system PATH exposes CUDA 13.x, this could silently build the tracer with the wrong toolkit despite the project lock requiring CUDA 12.6.x.

### Required behavior

The Route-E bootstrap must make the selected toolkit authoritative.

Acceptable implementation patterns include either:

- pass explicit `NVCC="$CUDA_HOME/bin/nvcc ..."` and `PTXAS="$CUDA_HOME/bin/ptxas"` into the build; or
- prepend/replace PATH in a tightly-scoped subprocess and independently verify resolved binaries; or
- make a small project-local Makefile adjustment that cleanly supports explicit tool paths.

Requirements:

- tracer build must use exactly the selected `--cuda-home` toolkit;
- postprocessor build provenance must be recorded too;
- no driver installation/change;
- no implicit fallback to another toolkit;
- if `$CUDA_HOME/bin/nvcc` or `$CUDA_HOME/bin/ptxas` is absent, fail;
- record exact resolved realpaths and versions in bootstrap logs/manifest.

Prefer project-local changes over unnecessary generic upstream rewrites.

### No-GPU test

Add a mock/fake-toolchain test that provides two fake toolkits:

- selected toolkit A;
- contaminating PATH toolkit B.

The test must prove the bootstrap/build command selects toolkit A and never B.

## RF2 — Strengthen capture-ready preflight compiler/toolchain validation

`capture_ready_preflight.py` must not merely test that some `nvcc` exists.

Require an explicit approved CUDA toolkit path, either as a command-line argument or a frozen environment variable with clear provenance.

Validate and record:

- requested CUDA_HOME;
- `realpath $CUDA_HOME/bin/nvcc`;
- `nvcc --version`;
- `realpath $CUDA_HOME/bin/ptxas`;
- `ptxas --version`;
- whether `which nvcc`/`which ptxas` disagree with the selected toolkit;
- PyTorch `torch.version.cuda` separately from the compiler toolkit;
- built tracer/postprocessor existence;
- NVBit checksum marker;
- wrapper digests.

A PATH mismatch may be reported as information if the build/run scripts still use the explicit approved toolkit, but the selected explicit path/version must be exact and must match the environment lock. Silent fallback is a failure.

Add static/unit tests for:

- correct 12.6-style selected toolkit;
- absent selected toolkit;
- contaminating PATH toolkit;
- version mismatch.

Do not hardcode the rental page's CUDA 13.x label as the project toolchain.

## RF3 — Enforce formal ROI semantics for memcpy records

### Problem

The frozen tracer gates kernel instrumentation on `active_region`, but its `API_CUDA_cuMemcpyHtoD_v2` callback can append `MemcpyHtoD` records to the kernel list without checking whether profiler-controlled ROI tracing is active. The postprocessor retains memcpy records in `kernelslist.g`.

Therefore model load / flat-buffer initialization can remain outside kernel tracing but still pollute the formal replay list.

### Required semantics

For Route-E formal runs using:

`ACTIVE_FROM_START=0`

with profiler-controlled ROI:

- memcpy events observed while `active_region == false` must **not appear in the formal ROI replay list**;
- memcpy events during an active ROI may be retained if they genuinely occur in that ROI;
- raw/provenance information should remain recoverable where useful, but the formal list must be unambiguous.

Preferred implementation:

- gate tracer-side memcpy kernel-list insertion using the same ROI state when `ACTIVE_FROM_START=0`;
- if preserving an auxiliary raw event log is useful, write it separately rather than contaminating the formal list.

A derived postprocessing-only filter is acceptable only if it can prove which memcpy occurred inside vs outside ROI. Do not infer ROI membership from filename/order when the tracer can record it explicitly.

### Required no-GPU/source-level tests

Add a source/static or unit/mocked callback test proving the intended policy:

- ROI inactive HtoD memcpy -> absent from formal list;
- ROI active HtoD memcpy -> retained/classified as memcpy;
- prefill/decode1 formal list excludes initialization copies;
- kernel ROI behavior remains unchanged.

Do not broaden the formal ROI to include model load just to avoid the problem.

## RF4 — Add explicit MEMCPY kernel-list classification

Update the non-destructive classifier so formal/raw manifests distinguish at least:

- `COMPUTE`;
- `NCCL_COLLECTIVE`;
- `MEMCPY`;
- `UNKNOWN_OTHER`.

Requirements:

- `MemcpyHtoD,...` must never be classified as `COMPUTE`;
- future known memcpy list-record forms should be handled conservatively;
- raw ordering/content remains retained;
- compute-only derived list excludes NCCL, MEMCPY, and UNKNOWN_OTHER unless a later approved policy says otherwise;
- full manifest records every retained raw-list entry and its classification;
- classifier self-test includes compute/NCCL/memcpy/unknown examples.

Do not make a paper-exact keep/drop decision for NCCL here.

## RF5 — Recompute wrapper/tool digests and environment lock

Any approved changes to:

- bootstrap scripts;
- preflights;
- tracer source;
- classifier;
- capture driver/wrappers

must update the appropriate lock/provenance documents and any digest validation tables.

Do not leave `capture_ready_preflight.py` expecting stale wrapper SHA256 values.

If the frozen tracer source changes only for ROI memcpy gating, record the exact Framework SHA and reason. Continue to identify it as the project capture tracer, not an author-provided artifact.

## RF6 — Full no-GPU regression

Rerun at minimum:

- `py_compile util/llm_trace_capture/*.py`;
- `bash -n util/llm_trace_capture/*.sh`;
- existing contiguous-weight planner self-test;
- metadata validator self-test;
- Llama TP wrapper/KV fake-tensor self-test;
- rank0 injection four-rank mock;
- ROI contract test;
- classifier self-test including `MEMCPY`;
- host-preflight self-test;
- capture-ready preflight self-tests including toolchain provenance cases;
- bootstrap dry run / fake-toolchain provenance test;
- generic NVBit smoke dry run;
- model metadata resolver dry run;
- unauthorized M4A-C guard.

No GPU or model-weight download is authorized.

## RF7 — Review pack and final readiness statement

Create:

`docs/vm_tlb/review_packs/M4A_PRERENTAL_REVIEW_FIX/`

At minimum include:

- `README.md`;
- `CHANGED_FILES.md`;
- `SOURCE_ANCHORS.md`;
- `VALIDATION_SUMMARY.md`;
- `OPEN_ISSUES.md`;
- `RAW_LOG_INDEX.tsv` where applicable.

Update:

`docs/vm_tlb/codex_handoff/m4a/LATEST_REPORT.md`

Final report must state exactly one:

- `READY_TO_RENT_REVIEW_FIX_PASS`; or
- `NOT_READY_TO_RENT`.

`READY_TO_RENT_REVIEW_FIX_PASS` requires all of:

1. explicit CUDA toolkit build provenance cannot be bypassed by PATH contamination;
2. capture-ready preflight validates the selected toolkit and records compiler/runtime distinction;
3. formal ROI replay lists exclude ROI-inactive initialization memcpy;
4. memcpy is separately classified;
5. existing rank0/TP/ROI/Weight/KV/NCCL preparation tests still pass;
6. M4A-C authorization guard remains blocked;
7. worktree clean and branch pushed.

## STOP boundary

After RF7:

- commit/push `hrl/llm-trace-prep-v0`;
- report final SHA and review-pack entry;
- STOP.

Do not:

- rent or access a GPU;
- start M4A-C;
- download formal Llama weights;
- collect a formal trace;
- implement Segmentation;
- generate/inject synthetic KV.

ChatGPT will perform one final review. Only after that review may the user rent the 4xSM86 AutoDL host.
