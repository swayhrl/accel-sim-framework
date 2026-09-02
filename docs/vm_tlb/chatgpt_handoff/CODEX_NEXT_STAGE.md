# CODEX_NEXT_STAGE — Track B

## Status

`M4A_PRECAPTURE_PREP` and `M4A_PRECAPTURE_FIXUP` have been reviewed by ChatGPT and accepted as preparation checkpoints.

Preferred formal self-capture route remains:

- **Route E**: one physical host with 4 same-model SM86 GPUs;
- real TP=4 execution;
- NVBit injected only into rank 0;
- raw rank-0 ROI trace retained intact;
- self-capture fidelity label, never author-exact.

Real rented-GPU capture (`M4A-C`) remains **NOT AUTHORIZED**.

Before rental, one final preparation round is authorized to eliminate avoidable runtime/setup ambiguity and to make the rental session execution-focused.

## Next authorized stage

Execute only:

`stage_specs/M4A_PRERENTAL_FINALIZE.md`

Do not repeat the completed route-selection work except where needed to implement/validate the final package.

## Mandatory read order

1. repository-root `AGENTS.md`
2. `docs/vm_tlb/chatgpt_handoff/CURRENT_STATE.md`
3. `docs/vm_tlb/chatgpt_handoff/DISCUSSION_REFERENCE.md`
4. this file
5. `stage_specs/M4A_PRERENTAL_FINALIZE.md`
6. `stage_specs/M4A_EXTERNAL_CAPTURE.md` as the future execution contract only
7. `docs/vm_tlb/paper_specs/SEGMENTATION_LLM_2026.md`
8. existing `docs/vm_tlb/llm/*`
9. existing `util/llm_trace_capture/*`
10. M4A-P / M4A-PF review packs

Do not modify `chatgpt_handoff/*`.

## Source anchor

Start from Framework branch:

`swayhrl/accel-sim-framework:hrl/llm-trace-prep-v0`

Expected prior closeout:

`9a02eecc9534726294c7e6ae2a5c8db3bbc05988`

or a descendant containing the latest ChatGPT handoff.

Verify branch/worktree cleanliness before editing.

## Core tasks

Follow every PR gate in `M4A_PRERENTAL_FINALIZE.md`. In particular:

1. fix the rank0-only injection environment contract so the parent driver never injects ranks 1–3;
2. use the frozen tracer's ROI control (`ACTIVE_FROM_START=0` plus profiler start/stop semantics) so model load, TP setup and flat-weight copies are not in formal traces;
3. prepare distinct `prefill` and `decode1` formal capture regions;
4. freeze/document Python, PyTorch/CUDA runtime, Transformers, Accelerate, NVBit archive/checksum, tracer CUDA toolkit, Framework SHA, wrapper SHA and model revision/dtype provenance;
5. prepare a checksum-verifying NVBit/bootstrap path without changing the host NVIDIA driver;
6. split host-only preflight from post-build capture-ready preflight;
7. extend runtime metadata preparation from weight-only to real KV-cache ranges/lifetimes where observable;
8. retain all raw rank0 ROI kernels and add reproducible NCCL/compute/other classification plus derived kernel lists without destructive filtering;
9. produce the AutoDL rental checklist for one 4xSM86 instance;
10. run all no-GPU unit/syntax/mock/dry-run tests.

## User-confirmed candidate host class

A 2026-09-02 AutoDL snapshot showed same-node RTX 3080 Ti / SM86 hosts with >=4 idle GPUs and expandable local storage. Treat this as `USER_CONFIRMED` mutable availability, not a permanent host guarantee.

Do not hard-code a specific host ID as required. M4A-C must re-check availability and hardware immediately after rental.

## Important known implementation hazards to close

### Rank injection

The parent Route-E driver must not globally export `CUDA_INJECTION64_PATH` before `torchrun`. Only the rank wrapper may set it for rank 0 during trace phase.

### Formal trace scope

Do not trace model download/load, TP initialization, flat weight rebinding, or unrelated initialization. Formal trace data should be selected inference ROI only.

### CUDA / driver / PyTorch

Do not assume the rental page's displayed CUDA 13.x stack is the project environment. Select and document an isolated, compatible CUDA/PyTorch/NVBit path from authoritative evidence. Do not alter the NVIDIA driver during the rental workflow.

### NCCL

The paper's collective-kernel treatment is unavailable. Preserve the raw trace and classify collectives; do not silently delete or permanently include them as a paper-exact choice.

## Reporting

Maintain:

`docs/vm_tlb/codex_handoff/m4a/LATEST_REPORT.md`

Create:

`docs/vm_tlb/review_packs/M4A_PRERENTAL_FINALIZE/`

The final report must state:

- final Route E host requirements;
- exact prepared bootstrap command(s);
- exact future M4A-C entry command(s);
- pinned/locked environment identities;
- rank0-only mock-test result;
- prefill/decode1 ROI design;
- Weight + KV metadata readiness;
- NCCL classification readiness;
- which remaining checks require the rented GPU;
- whether the package is `READY_TO_RENT` or `NOT_READY_TO_RENT`.

## STOP boundary

After M4A-PR:

- commit and push `hrl/llm-trace-prep-v0`;
- update Track-B report;
- provide review-pack entry;
- STOP.

Do **not**:

- rent a GPU;
- start `M4A_EXTERNAL_CAPTURE`;
- set the authorization variable for a real LLM capture;
- collect formal trace data;
- implement Segmentation;
- inject synthetic KV.

ChatGPT will review this closeout before the user rents the AutoDL node.
