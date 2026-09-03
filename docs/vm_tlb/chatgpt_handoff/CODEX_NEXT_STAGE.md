# CODEX_NEXT_STAGE — Track B

## Status

Route-E capture and post-capture audit are complete.

Current accepted state:

- real TP=4 / rank0-only NVBit / BF16 / B8/S64/G3 capture completed;
- formal prefill and decode1 archives are checksum-verified on the main server;
- capture executable source is `c79f4469c6a2befa59e4c4efcd3c885dc2259a81`;
- post-capture audit reached `POSTCAPTURE_REVIEW_PASS_SAFE_TO_POWER_OFF`;
- GPU host is no longer required;
- no recapture is authorized.

Two offline-analysis issues remain before A/B integration:

1. formal kernel classification must use embedded trace-header semantic names rather than `kernelslist.g` filenames;
2. formal address coverage must decode every active-lane reference for list-all/base-stride/base-delta trace formats and apply ROI-aware Weight/KV matching.

## Next authorized target

Execute only:

`M4A_MERGE_PREP`

Specification:

`docs/vm_tlb/chatgpt_handoff/stage_specs/M4A_MERGE_PREP.md`

Current start override:

`docs/vm_tlb/chatgpt_handoff/M4A_MERGE_PREP_START.md`

Run as one continuous internal Goal:

`MP0 -> MP1 -> MP2 -> MP3 -> MP4 -> MP5 -> MP6 -> MP7 -> MP8`.

Continue automatically after passing internal gates. Stop only on stage-spec hard blockers. After MP8 commit/push and STOP for ChatGPT review.

## Mandatory read order

1. repository-root `AGENTS.md`
2. `docs/vm_tlb/chatgpt_handoff/M4A_MERGE_PREP_START.md`
3. `docs/vm_tlb/chatgpt_handoff/CURRENT_STATE.md`
4. `docs/vm_tlb/chatgpt_handoff/DISCUSSION_REFERENCE.md`
5. this file
6. `docs/vm_tlb/chatgpt_handoff/stage_specs/M4A_MERGE_PREP.md`
7. `docs/vm_tlb/chatgpt_handoff/stage_specs/M4A_POSTCAPTURE_REVIEW_FIX.md`
8. `docs/vm_tlb/review_packs/M4A_EXTERNAL_CAPTURE/*`
9. `docs/vm_tlb/llm/*`
10. `util/llm_trace_capture/*`
11. `util/tracer_nvbit/tracer_tool/tracer_tool.cu`
12. `util/tracer_nvbit/tracer_tool/traces-processing/post-traces-processing.cpp`

`chatgpt_handoff/*` is ChatGPT-owned. Read it; do not modify it.

## Source and artifact anchors

Framework branch:

`swayhrl/accel-sim-framework:hrl/llm-trace-prep-v0`

Required authorization handoff:

use the latest descendant containing `M4A_MERGE_PREP_START.md` and `stage_specs/M4A_MERGE_PREP.md`.

Frozen capture source:

`c79f4469c6a2befa59e4c4efcd3c885dc2259a81`

Formal prefill:

`/workspace/m4a-rented-host-pilot/formal-prefill/m4a-llama-prefill-20260902T182016Z.tar.zst`

SHA256:

`f96b7ea91b798e2ce8eb8f4592b1ef6512a762870471d2dbb85ab4777c97f181`

Formal decode1:

`/workspace/m4a-rented-host-pilot/formal-decode1/m4a-llama-decode1-20260903T004138Z.tar.zst`

SHA256:

`5bdd4b55ed0e1499cbfee756d289cbd8072f556db4f467a882a54e42cd32dcad`

Frozen parser compatibility Core:

`73774727e25fadf89df6f30ef5cf014091115db7`

This Core is only the old parser/simulator compatibility anchor. Do not modify it and do not treat it as the future integrated VM Core.

## Required work summary

Follow the stage spec exactly. Core requirements are:

1. independently reverify both immutable formal archives before analysis;
2. implement semantic kernel-name extraction from each trace header;
3. regenerate non-destructive full semantic manifest, true compute-only list and NCCL-only diagnostic list for prefill/decode1;
4. quantify real semantic NCCL inventory and supersede the historical filename-only `0 NCCL` counts;
5. replace the regex-only coverage path with an exact streaming trace-address decoder for `list_all`, `base_stride`, and `base_delta`;
6. assert every decoded memory instruction reconstructs exactly `popcount(active_mask)` addresses;
7. make Weight/KV matching ROI-aware and conservative;
8. run full formal prefill/decode1 coverage plus 64KB/2MB object page-footprint analysis without fully decompressing trace text to disk;
9. perform representative semantic COMPUTE and NCCL parser/simulator compatibility checks;
10. repair stale B-owned post-capture docs and create a frozen integration manifest/review pack.

## Scientific boundaries

The following are not yet decided and must remain explicit:

- whether final M4B formal replay uses FULL_RANK0, COMPUTE_ONLY_TP_PARTITION, or reports both;
- whether NCCL kernels are representable/performance-meaningful in the one-partition Accel-Sim reproduction;
- exact per-instruction KV lifetime identity;
- Segmentation implementation details unavailable from the paper;
- synthetic long-context KV distribution.

Raw/full trace evidence must remain immutable regardless of later policy.

## Track-A coexistence

Track A is independently executing final M1–M3 VM closeout.

Do not fetch/merge/cherry-pick Track-A source into this Goal. Do not modify `hrl/vm-m1-m3-v0` or `swayhrl/gpgpu-sim`.

The future A/B merge will happen only after both independent closeouts pass. At that point Core will come from final Track A and Framework integration will occur on a new branch with a rewritten unified handoff.

## Reporting

Create:

`docs/vm_tlb/review_packs/M4A_MERGE_PREP/`

Maintain:

- `docs/vm_tlb/codex_handoff/m4a/LATEST_REPORT.md`
- `docs/vm_tlb/codex_handoff/m4a/GOAL_PROGRESS.md` if present.

Final report must state exactly one:

- `M4A_MERGE_PREP_PASS_READY_FOR_INTEGRATION`
- `M4A_MERGE_PREP_BLOCKED`

It must include actual formal semantic kernel counts, corrected coverage/page-footprint summary, parser compatibility status, artifact/output hashes, remaining NCCL-policy ambiguity and changed-file/source anchors.

## STOP boundary

After MP8:

- run required validation;
- commit only explicit paths;
- push `hrl/llm-trace-prep-v0`;
- STOP for ChatGPT review.

Do not:

- access/rent a GPU;
- recapture data;
- modify frozen formal archives;
- modify Track A or Core;
- merge branches;
- implement Segmentation/M4B;
- implement L2-TLB sub-entry/coalescing;
- inject synthetic KV;
- add page faults/migration/UVM/MCM;
- make a permanent NCCL keep/drop choice.
