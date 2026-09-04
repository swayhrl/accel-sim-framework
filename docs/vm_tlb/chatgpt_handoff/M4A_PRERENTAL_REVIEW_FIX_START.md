# Track-B Start Override — M4A-PR2

This file is the current ChatGPT authorization for Track B and resolves any stale wording in older `CODEX_NEXT_STAGE.md` / `CURRENT_STATE.md` snapshots that still point to `M4A_PRERENTAL_FINALIZE`.

Execute only:

`docs/vm_tlb/chatgpt_handoff/stage_specs/M4A_PRERENTAL_REVIEW_FIX.md`

Source branch:

`swayhrl/accel-sim-framework:hrl/llm-trace-prep-v0`

Prior Codex closeout:

`f74b08f867d5bcb781caa0c319acf03148fb2630`

Required result:

- `READY_TO_RENT_REVIEW_FIX_PASS`, or
- `NOT_READY_TO_RENT`.

M4A-C remains unauthorized. Do not rent/access a GPU, download formal Llama weights, collect formal traces, implement Segmentation, or inject synthetic KV.

The repair scope is limited to:

1. explicit CUDA toolkit / nvcc / ptxas provenance;
2. capture-ready preflight validation of that explicit toolchain;
3. formal ROI exclusion of ROI-inactive HtoD memcpy records;
4. separate MEMCPY classification;
5. digest/lock updates and full no-GPU regression.

After push/report, STOP for ChatGPT review.
