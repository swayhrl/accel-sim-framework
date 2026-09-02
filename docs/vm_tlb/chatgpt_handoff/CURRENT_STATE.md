# Current state — Track B

## Review result

`M4A_PRECAPTURE_PREP` and `M4A_PRECAPTURE_FIXUP` have been reviewed by ChatGPT and accepted as preparation checkpoints.

Reviewed Framework branch:
`hrl/llm-trace-prep-v0`

Latest completed Codex closeout before this handoff:
`9a02eecc9534726294c7e6ae2a5c8db3bbc05988`

Accepted Track-B state:

- previous AutoDL/V100 campaign recovery and reusable capture-safety patterns are accepted;
- formal preferred self-capture route is Route E: one 4x same-model SM86 node, real TP=4, trace rank0 only;
- Route A remains an approval-only `DOCUMENTED_APPROX` fallback;
- full-model single-GPU trace is rejected as the formal paper workload;
- concrete TP4 wrapper, runtime flat-weight binder, sidecar/manifest path, and rank wrapper exist;
- no external GPU has been rented and M4A-C has not started;
- paper-exact trace, TP implementation, dtype, contiguous loader, sub-entry/PTW details, synthetic-KV distribution, and collective treatment remain unavailable.

## User-confirmed rental availability snapshot

`USER_CONFIRMED`, snapshot date 2026-09-02:

- AutoDL showed RTX 3080 Ti 12 GiB / SM86 physical hosts with at least four idle GPUs on one host;
- one candidate showed 6 / 8 idle GPUs and expandable local storage up to about 1.6 TB;
- another showed 5 / 8 idle GPUs and expandable local storage up to about 2 TB;
- the displayed host environment used a recent NVIDIA driver and CUDA 13.x label.

This is evidence that the required host class can exist, not a reservation. Availability and all host details must be revalidated after rental. Do not hard-code a host ID as a project requirement.

## Why M4A-C is still not authorized

Before spending rental time, the package still needs several avoidable pre-rental gaps closed:

1. parent-level `CUDA_INJECTION64_PATH` must not leak NVBit injection to ranks 1–3;
2. formal trace ROI must exclude model loading, TP setup and flat-weight copy/rebind work;
3. prefill and first-decode traces need explicit, independent ROI/provenance paths;
4. driver / CUDA toolkit / PyTorch runtime / NVBit version/checksum and model revision/dtype provenance need a frozen environment contract;
5. host suitability preflight must be separated from post-build tracer readiness;
6. runtime metadata should record real KV-cache ranges/lifetimes where observable, not only Weight;
7. raw NCCL/collective kernels must be retained and classified so later replay policy does not require recapture.

These are preparation tasks and should be completed without renting a GPU.

## Next authorized Track B work

Execute:

`docs/vm_tlb/chatgpt_handoff/stage_specs/M4A_PRERENTAL_FINALIZE.md`

Goal: close all practical no-GPU setup gaps and return a package explicitly classified as `READY_TO_RENT` or `NOT_READY_TO_RENT`.

## Prepared but not authorized

Future execution specification:

`docs/vm_tlb/chatgpt_handoff/stage_specs/M4A_EXTERNAL_CAPTURE.md`

M4A-C remains blocked until ChatGPT reviews M4A-PR and the user then rents a selected 4xSM86 node.

## STOP boundary

After M4A-PR, push/report and STOP. Do not rent a GPU, run formal external capture, implement Segmentation, or inject synthetic KV traffic until a new ChatGPT-owned handoff explicitly authorizes M4A-C.
