# CODEX_NEXT_STAGE

Status: **ACTIVE MAINLINE — M3R; M4 WAITING**

Stage:

`AWMA_Q05_PREFIX_LDC_U8_SEMANTIC_RECOVERY_V1`

Coordination branch:

`hrl/awma-q05-prefix-ldc-recovery-handoff-v1`

## M3R — node109 — ACTIVE MAINLINE

Read:

```text
docs/vm_tlb/chatgpt_handoff/awma/CURRENT_STATE.md
docs/vm_tlb/chatgpt_handoff/awma/DISCUSSION_REFERENCE.md
docs/vm_tlb/chatgpt_handoff/awma/Q05_CONTIGUOUS_PREFIX_CAPTURE_CONTRACT_V1.md
docs/vm_tlb/chatgpt_handoff/awma/CODEX_RESUME_109_Q05_PREFIX_LDC_U8_RECOVERY_V1.md
```

Execution parent:

```text
hrl/awma-q05-contiguous-prefix-capture-109-v1
78f153eb8da6e8e54467382d655f2a55d3eb43fa
```

Recommended branch:

`hrl/awma-q05-prefix-ldc-recovery-109-v1`

Priority:

1. audit the real member-2 LDC.U8 record and accepted producer/parser/trace-driven semantics;
2. make only a narrow strict-validator repair for exact LDC when source-backed;
3. run compiled regression fixtures/full tests;
4. reuse the existing 35/35 raw P34 execution and validate all members offline;
5. only if all members pass, derive page-overlap tables and publish the immutable context bundle to node164 with ACK;
6. GPU recapture only if existing raw cannot be provenance/integrity-closed.

Do not fabricate width=1 or constant addresses.

Routine source/build/test/postprocess/storage issues are solve-and-continue. A later new opcode may be handled without another ChatGPT round only when accepted source unambiguously proves the same implicit/non-address-bearing representation and the repair remains exact-opcode/narrow with compiled fixtures. Otherwise STOP.

Success marker:

`AWMA_Q05_PREFIX_LDC_U8_SEMANTIC_RECOVERY_V1_COMPLETE_WITH_SCOPE`

## M4 — node174-new — WAITING

Current accepted waiting execution:

```text
hrl/awma-q05-warm-prefix-replay-174new-v1
5b9d708087e8ff485f03fd561a15e08baea8ad3a
AWMA_Q05_WARM_PREFIX_REPLAY_174NEW_V1_WAITING_FOR_CONTEXT_BUNDLE
```

Do not dispatch 174 again until M3R publishes a formal 35-member context bundle.

The known small F0 wording/state-matrix cleanup will be folded into that substantive resume.

## Mainline priority

No side task may delay M3R.

Do not auto-start Decode Flash, Qwen3/DeepSeek, NCU side work, complementary GEMM/GEMV replay, cleanup, or mechanism sweeps.

No TLB/PTW/cache mechanism experiment is authorized in this stage.

After M3R closes, return its report to ChatGPT before resuming 174.
