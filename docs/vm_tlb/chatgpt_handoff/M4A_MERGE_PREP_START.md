# Track-B start override — M4A MERGE PREP

This file is the current Track-B authorization and overrides stale pre-rental/capture wording in older handoff snapshots.

## Authorized now

Execute only:

`docs/vm_tlb/chatgpt_handoff/stage_specs/M4A_MERGE_PREP.md`

as one continuous Goal:

`MP0 -> MP1 -> MP2 -> MP3 -> MP4 -> MP5 -> MP6 -> MP7 -> MP8 -> STOP`.

## Accepted input state

- expensive Route-E capture is complete and accepted;
- formal prefill/decode1 archives are checksum-verified on the main server;
- GPU host is no longer required;
- no recapture is authorized;
- capture executable source is `c79f4469c6a2befa59e4c4efcd3c885dc2259a81`;
- current reviewed post-capture evidence descendant is `f000a8284ee3dc224f89ee3fca6f38c8d8202785` or a descendant containing this authorization.

## Purpose

Prepare immutable LLM artifacts for later Track-A integration by:

1. replacing filename-only kernel classification with embedded-header semantic classification;
2. producing real NCCL inventory plus non-destructive full/compute-only/NCCL-only derivatives;
3. replacing the regex-only address analyzer with exact list/base-stride/base-delta warp-address decoding;
4. running full prefill/decode1 Weight/KV/UNKNOWN coverage and 64KB/2MB page-footprint analysis;
5. performing representative compute/NCCL parser compatibility checks;
6. repairing stale B-owned post-capture documentation and creating a merge/integration manifest.

## Boundaries

Do not touch Track A or Core. Do not merge branches. Do not implement M4B/Segmentation. Do not inject synthetic KV. Do not choose the permanent NCCL keep/drop policy. Do not modify formal archives.

After MP8, push the Track-B Framework branch and STOP for ChatGPT review.
