# CODEX_NEXT_STAGE — Track B

## Status

`M4A_PRECAPTURE_PREP` has been reviewed by ChatGPT: **CONDITIONAL_PASS ACCEPTED**.

Real rented-GPU capture (`M4A-C`) remains **NOT AUTHORIZED**.

A short pre-capture fixup is required before rental because the current capture driver depends on an unspecified workload command and the paper's `TP=4, simulate one partition` method is unavailable.

## Next authorized stage

Execute only:

`stage_specs/M4A_PRECAPTURE_FIXUP.md`

Do not repeat the completed legacy-asset audit except where needed to support the fixup.

## Core tasks

1. Analyze two real workload routes:
   - actual 4-GPU SM86 TP=4, trace one rank;
   - single-GPU one-rank TP emulation.
2. Do not use a full-model single-GPU trace as the formal paper workload.
3. Create at least one concrete pinned executable workload wrapper/template that enforces B8/S64/G3 and the selected TP interpretation.
4. Integrate runtime metadata-sidecar generation into the wrapper/hook path.
5. Prepare the contiguous-weight runtime hook/strategy to the strongest level possible without a GPU.
6. Revise the rental recommendation so `1 x RTX3090` is only recommended if the single-rank emulation route is explicitly selected/approved.
7. Keep M4A-C authorization guard intact.

## Reporting

Maintain:

`docs/vm_tlb/codex_handoff/m4a/LATEST_REPORT.md`

Create:

`docs/vm_tlb/review_packs/M4A_PRECAPTURE_FIXUP/`

Report clearly:

- preferred formal capture route;
- required GPU count/model class;
- executable wrapper path;
- exact software/model pins or recorded-version policy;
- unresolved paper exactness;
- estimated rental workflow/cost complexity (qualitative is sufficient; do not fabricate prices).

## STOP boundary

After the fixup:

- commit and push `hrl/llm-trace-prep-v0`;
- update Track-B report;
- provide review pack;
- STOP.

Do **not** start `M4A_EXTERNAL_CAPTURE.md`, rent a GPU, collect a formal trace, implement Segmentation, or inject synthetic KV traffic until the user/ChatGPT explicitly authorizes the chosen route.
