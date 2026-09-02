# Current state — Track B

## Review result

`M4A_PRECAPTURE_PREP` has been reviewed by ChatGPT and is accepted as **CONDITIONAL_PASS**.

Reviewed Framework branch:
`hrl/llm-trace-prep-v0`

Reviewed closeout HEAD:
`27bdeeb947dc1f84b6dc8ec400480fbc2048e264`

Review entry:
`docs/vm_tlb/review_packs/M4A_PRECAPTURE_PREP/README.md`

Accepted evidence:

- previous AutoDL/V100 campaign recovered at `3bed497023c7ee52e2b7ea0393628f34997ea974`;
- reusable preflight, disk-guard, postprocess verification, archive/checksum/offload patterns identified;
- current branch contains static contiguous-weight planning, metadata validation, preflight, and a gated external-capture driver;
- no Core VM/TLB semantics were changed;
- external capture remains blocked by authorization guard;
- exact public paper artifact/trace, TP=4 capture method, dtype, contiguous loader, sub-entry/PTW details, and synthetic-KV distribution remain unavailable.

## Why M4A-C is still not authorized

The current `run_m4a_c.sh` deliberately requires an externally supplied executable LLM workload command. The repository does not yet contain a concrete pinned workload wrapper that resolves the paper's `TP=4, simulate one partition` requirement.

This creates a material ambiguity:

- a **real TP=4 run traced on one rank** likely requires a 4-GPU SM86 node;
- a **single RTX3090** can support a single-rank emulation route, but that is not automatically paper-exact;
- a full-model single-GPU trace is not an acceptable substitute for the paper workload.

Therefore the previous blanket recommendation `1 x RTX3090` is not yet sufficient to authorize rental/capture.

## Next authorized Track B work

Execute:

`docs/vm_tlb/chatgpt_handoff/stage_specs/M4A_PRECAPTURE_FIXUP.md`

The fixup must:

- compare real 4-GPU TP=4/rank0 capture against a single-GPU one-rank emulation;
- create at least one concrete pinned executable workload wrapper candidate;
- connect runtime metadata generation into that wrapper/hook path;
- prepare the runtime contiguous-weight hook to the strongest non-GPU-verifiable level;
- revise the rental hardware recommendation based on the selected TP route.

## Prepared but still not authorized

`docs/vm_tlb/chatgpt_handoff/stage_specs/M4A_EXTERNAL_CAPTURE.md`

Do not rent/capture yet from this branch solely on the basis of the prior `1 x RTX3090` recommendation.

## STOP boundary

After `M4A_PRECAPTURE_FIXUP`, push the Track-B report/review pack and STOP. The user/ChatGPT will then select the actual rental route and explicitly authorize M4A-C.
