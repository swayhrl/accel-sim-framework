# Current state — Track B

## Review result

Track B pre-rental preparation is **PASS / READY_TO_RENT** after independent ChatGPT review.

Accepted stages:

- `M4A_PRECAPTURE_PREP`: PASS/accepted;
- `M4A_PRECAPTURE_FIXUP`: PASS/accepted;
- `M4A_PRERENTAL_FINALIZE`: accepted after review-fix;
- `M4A_PRERENTAL_REVIEW_FIX`: **PASS / READY_TO_RENT_REVIEW_FIX_PASS**.

Reviewed Framework branch:
`hrl/llm-trace-prep-v0`

Accepted Route-E implementation commit:
`524cb20785ec4632b434a0786181ff814ad7eaba`

Final provenance/report descendant:
`11b4fc33fe3b9e95ad470bccedc306182c5122b5`

## Approved formal self-capture route

Route E is approved:

- one physical host with four same-model SM86 GPUs;
- real TP=4 execution;
- NVBit injected only into rank 0;
- B8 / S64 / G3 workload contract;
- separate profiler-controlled `prefill` and `decode1` formal ROI captures;
- raw rank-0 ROI trace retained intact;
- contiguous rank-local weight buffer + runtime sidecar;
- observable real KV-cache events/ranges where the pinned framework exposes them;
- resulting trace is `PAPER_COMPATIBLE_SELF_CAPTURE`, never author-exact.

A full-model single-GPU trace remains rejected as the formal paper workload. Route A remains an approval-only `DOCUMENTED_APPROX` fallback.

## Accepted review-fix results

The final two engineering blockers are closed:

- selected `--cuda-home` now controls the actual NVBit `nvcc` and `ptxas` paths; contaminating host PATH toolkits cannot silently take over the build;
- capture-ready preflight records selected compiler realpaths/versions, host-PATH compiler values, PyTorch runtime CUDA, tracer/postprocessor existence, NVBit checksum marker, and locked artifact digests;
- with `ACTIVE_FROM_START=0`, ROI-inactive `cuMemcpyHtoD_v2` events no longer enter the formal replay list, while active-ROI memcpy remains eligible;
- kernel classification now separates `COMPUTE`, `NCCL_COLLECTIVE`, `MEMCPY`, and `UNKNOWN_OTHER`; the compute-only derivative excludes non-compute entries without altering raw evidence;
- rank0-only injection, TP/ROI, Weight/KV metadata, checksum/bootstrap, host/capture preflights, model metadata lock, and M4A-C authorization guard all retain passing no-GPU tests.

Review entry:
`docs/vm_tlb/review_packs/M4A_PRERENTAL_REVIEW_FIX/README.md`

## Rental hardware requirements

At rental time require:

- one physical host row with at least four currently idle GPUs;
- allocate all four GPUs in the same instance;
- all four GPUs same model and compute capability 8.6 (SM86);
- RTX 3080 Ti 12 GiB is accepted; RTX 3090 24 GiB provides more headroom but is not required;
- host RAM target >=64 GiB;
- at least 500 GiB free/immediately expandable local storage before formal trace; more is preferred when inexpensive;
- SSH and checksum-verified copy-back capability;
- do not rely on the rental page's CUDA 13.x label as the project toolchain.

The 2026-09-02 AutoDL availability screenshot is a mutable `USER_CONFIRMED` snapshot only. Recheck availability when paying.

Prefer an instance/image where an explicit CUDA 12.6 toolkit is already available at a known path. If it is not, stop after host preflight and establish the approved local CUDA-12.6 toolkit path before any NVBit build/model download; never change the host NVIDIA driver.

## Current authorization boundary

The **user may now rent** a qualifying Route-E host.

`M4A-C` formal capture is still **NOT YET AUTHORIZED**. Immediately after rental, only the host-suitability gate should run first; no model download or formal tracing is needed for that gate.

Future first command is `host_preflight.py` using the actual large local-data mount as `--work-root`.

After host-preflight PASS, report the generated `host-preflight.json` / host summary back for the M4A-C authorization handoff. Then the sequence will be:

`isolated env -> checksum NVBit bootstrap with explicit CUDA 12.6 -> generic NVBit smoke -> capture-ready preflight -> real TP4 smoke -> tiny LLM ROI trace -> measured disk projection -> formal prefill/decode1 capture -> archive/copy-back -> parser/simulator compatibility`.

## Remaining host-only gates

The following are intentionally unresolved until the rented host exists:

- real driver/NVBit compatibility;
- actual four-GPU `torchrun`/NCCL TP behavior;
- profiler ROI behavior under the real CUDA runtime;
- flat-weight rebinding stability and numerical sanity on real TP4;
- real KV VA/lifetime coverage;
- real trace growth/disk projection;
- NCCL kernel inventory and parser/simulator compatibility;
- final raw/full/compute-only replay policy;
- imported trace parser/simulator smoke.

These are M4A-C execution gates, not pre-rental blockers.

## STOP boundary

Until a qualifying host is rented and host preflight is reviewed, do not set `M4A_C_AUTHORIZED=1`, bootstrap a real capture environment, download formal model weights, collect trace data, implement Segmentation, or inject synthetic KV.