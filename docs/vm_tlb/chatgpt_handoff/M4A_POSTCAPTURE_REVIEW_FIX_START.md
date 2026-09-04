# Track B current start override — M4A post-capture review fix

This file is the current Track-B authorization after `GOAL_PASS_READY_FOR_CHATGPT_REVIEW` and overrides stale pre-rental / blocked-Goal wording in older handoff snapshots.

## Reviewed data-acquisition result

The expensive GPU capture Goal is provisionally accepted as having produced two durable checksum-verified formal bundles on the main server:

- formal prefill SHA256 `f96b7ea91b798e2ce8eb8f4592b1ef6512a762870471d2dbb85ab4777c97f181`;
- fresh formal decode1 SHA256 `5bdd4b55ed0e1499cbfee756d289cbd8072f556db4f467a882a54e42cd32dcad`.

No new GPU capture is authorized or required by this start override.

## Why one short review-fix remains

Independent review found stale/inconsistent files in `M4A_EXTERNAL_CAPTURE` despite the successful final report: `SOURCE_ANCHORS.md`, `HOST_ENVIRONMENT.md`, `GOAL_GATE_RESULTS.md`, and `RAW_LOG_INDEX.tsv` still contain historical blocked/running state. `FORMAL_DECODE1.md` is also materially less complete than the prefill evidence.

There are also two scientific follow-ups that can be audited entirely from the copied archives: why real TP4/NCCL execution produced zero classifier-recognized NCCL entries, and whether trace addresses can be streamed offline against Weight/KV sidecar ranges.

## Active specification

Execute only:

`docs/vm_tlb/chatgpt_handoff/stage_specs/M4A_POSTCAPTURE_REVIEW_FIX.md`

Run on the main development server. Do not depend on the rented GPU host except for optional nonessential provenance lookup; all required acceptance evidence must come from the copied formal archives and Git history.

The user may power off the GPU host to save rental cost once Codex has independently reverified both main-server archives and confirms no non-regenerable remote-only evidence is needed. The final spec asks Codex to return an explicit `SAFE_TO_POWER_OFF` recommendation.

Do not recapture prefill/decode1, do not modify Core M1-M3 semantics, and do not start Segmentation/M4B/M5/synthetic KV.
