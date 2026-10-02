# Main handoff index — R23G reviewed

## Current-state override — 2026-10-02

R23G now has a completed execution result, reviewed under its original frozen Goal:

- execution commit: `99d05f0ad221a1d44dd11bac0ed83965bb2c0942`
- execution tree: `b3bcf21e81e1bc34a3281d41b570d6021d8a1edd`
- accepted result: `R23G_R81_LIVE_DISPATCH_LOCAL_RESPONSE_PRESENT`
- Lane G: completed and STOP per Goal closure; scoped software result, not a hardware claim.

Read the current state at commit `8df5946f118bd7debb597a72dab7b93d80c882ef`:
`docs/vm_tlb/literature_notes/awma/plans/STATUS_AFTER_R23G_REVIEW_2026-10-02.md`

Detailed review / software result, first published at `3af156d8f9a217289909c694f269665ef88c8db2`:
`docs/vm_tlb/literature_notes/awma/empirical/R23G_LIVE_DISPATCH_REVIEW_2026-10-02.md`

The original main handoff below remains useful for goals, frozen contracts, history and node workflow, but its G-running state is superseded. F/E remain STOP; R20 CLOSED; no new node/GPU/Accel-Sim/hardware task is authorized. Do not restart G, regroup/de-duplicate the frozen cohort, or treat complete-generation safety as proof of uniform end-to-end acceleration. The 12 source records include only 9 distinct prompt/schema combinations; this coverage qualification is recorded in the review without changing the original contract.

---

## Historical active snapshot (retained)

# Latest main handoff — R23G active snapshot

Date: 2026-10-02.
Purpose: transfer the ChatGPT research/review context only. No new experiment is authorized.

## Read this first

The complete self-contained Chinese project handoff is on the dedicated documentation branch:

- branch: `hrl/awma-main-context-r23g-active-20261002-v1`
- commit: `2b96d94ed79f0fb2a3360aa55c3f0184a590c523`
- tree: `f8e7e4339c38c61a273a388c81a09eb8dffad1eb`
- path: `docs/vm_tlb/chatgpt_handoff/awma/context_2026_10_02_r23g_active/AWMA_PROJECT_HANDOFF_CONTEXT_2026-10-02_R23G_ACTIVE.md`
- file Git blob: `0e7d2481440d5e8a465bf67764e4dafdf5e4eb4d`
- file SHA256: `b388832ba8a434ec30de3568a44669ef19e22ca4f9390159e907f10086299b36`
- UTF-8 file bytes: 62616
- Sections 0–4 cover current authority, lane state, R23G contract and the next review checklist; sections 5–17 retain history, positive/negative/unknown boundaries, methodology, literature, node workflow, source index and a next-ChatGPT prompt.

The local downloadable main file and remote Git blob have matching content identity. No large raw was copied or rehashed by ChatGPT.

## Current scientific task state

- Lane G / node109: user confirms R23G is running; it is the only authorized GPU task.
- R23G execution branch: `hrl/awma-r23g-r81-live-dispatch-109-v1`.
- At this handoff's remote check, execution ref still equals starting commit `f981039d9289368cc32f761d6e5a79f91a775266`, tree `8008841642b207cdf5258f1aea534aa2c1519d0d`. No completion report was present at that ref. Do not claim a specific live phase or repeat the start command.
- R23G Goal: `docs/vm_tlb/chatgpt_handoff/awma/r23g_r81_live_dispatch_v1/LANE_G_R23G_R81_LIVE_DISPATCH_109_GOAL.md`.
- Lane F / R22F1: accepted STOP at `bb5c66c674007cc6c9a77549fb0f81528be30056`.
- Lane E / R22E: accepted STOP at `4fbef16c342fb409918aef7a3922c4f5334761ac`.
- R20 remains CLOSED; R21A/OEQ target-family line STOP. No Donline/old holdout/profile rescue, new 174/Accel-Sim work or hardware task.

Current execution authorization is `STATUS_AFTER_R22F1_AND_R23G_AUTHORIZATION_2026-10-02.md` at `a5f069109ff3b72fd9754ded48ebdddc145cd89c`.

The main literature README still contains a Round22 historical statement saying no lanes have new authorization. That old statement is not the current dispatch state. Use this index, the above authorization and the latest execution receipt instead. Historical README snapshots and experiment labels are not rewritten.

## Handoff safety

Do not restart Lane G because the ChatGPT window changes. Read the exact existing Goal and wait for an actual result or user update. When a new result arrives, first check input selection, exact union, same A0/A3 implementation, greedy/schema semantics, cost-inclusive LIVE_HEAD and complete-generation safety. Kernel-family value is not vetoed merely by whole-model <5%, and unknown/mixed is not a performance negative.
