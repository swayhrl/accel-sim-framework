# CODEX_NEXT_STAGE — Track A

## Status

`M1_M3_VM_BASELINE_CLOSEOUT`: **PASS / ACCEPTED**.

Accepted final Core:

`5ba17a1ba88b8e8ec0f9505a7e684c81df8f0b7d`

Accepted Framework evidence:

`47dde5767af8d30b892c7d63d932455644b7cf3a`

Track A has completed G3-4A, G3-4B, G3-5A, G3-5B, G3-CLOSEOUT and the M1-M3 macro closeout.

## Current authorization

**STOP / HOLD.**

There is no additional Track-A implementation target at this time.

Track B is still executing `M4A_MERGE_PREP` on the frozen formal LLM traces. Wait for its ChatGPT review before any A/B integration or M4B work.

## Frozen integration anchor

Any future integrated VM/LLM branch must use this Core as its starting VM baseline:

`swayhrl/gpgpu-sim:hrl/vm-m1-m3-v0`

`5ba17a1ba88b8e8ec0f9505a7e684c81df8f0b7d`

Do not replace it with Track B's old frozen parser Core; that old Core exists only as trace-format compatibility evidence.

## Future target is prewritten but NOT authorized

The detailed post-B contracts have already been prepared:

1. `M4_INTEGRATION_GOAL_START_DRAFT.md`
2. `stage_specs/M4_INTEGRATION_TO_SEGMENTATION_MASTER.md`
3. `stage_specs/M4I_AB_INTEGRATION_AND_REPLAY.md`
4. `stage_specs/M4C_LLM_BASELINE_CHARACTERIZATION.md`
5. `stage_specs/M4B_SEGMENTATION_REPRODUCTION.md`

They define the planned continuous target:

```text
M4I A/B integration
 -> M4R final-Core formal trace replay compatibility
 -> M4C real LLM baseline translation characterization
 -> M4B-P paper paging/L2-sub-entry baseline
 -> M4B-S Weight Segmentation on formal prefill/decode1
 -> M4B-CLOSEOUT
 -> STOP before M5 synthetic KV
```

`M4_INTEGRATION_GOAL_START_DRAFT.md` is deliberately marked NOT AUTHORIZED and
contains placeholders for the final accepted B merge-prep SHA, semantic list
hashes/coverage evidence and integration manifest.

After Track B reports `M4A_MERGE_PREP_PASS_READY_FOR_INTEGRATION`, ChatGPT will:

- review B independently;
- fill those immutable placeholders;
- adjust the drafted contracts only where B's measured NCCL/address/object
  evidence requires it;
- issue a new explicit `AUTHORIZED` start file.

The intent is that Codex can then enter Goal mode immediately rather than wait
for another architecture-planning round.

## Do not execute now

Do not:

- merge Track B into Track A;
- create the final A/B integration branch unless explicitly authorized;
- execute the draft start file;
- start M4B;
- implement Segmentation;
- implement L2-TLB sub-entry/coalescing;
- inject synthetic KV;
- add page faults/migration/UVM/MCM;
- broaden to multi-ASID claims;
- retune the accepted generic M1-M3 baseline in anticipation of LLM results.

Until the explicit post-B authorization is published, remain stopped.
