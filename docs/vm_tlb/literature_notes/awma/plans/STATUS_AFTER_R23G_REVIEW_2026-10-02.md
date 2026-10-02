# Status after R23G review

Date: 2026-10-02.

This current-state record supersedes the G-running state in `STATUS_AFTER_R22F1_AND_R23G_AUTHORIZATION_2026-10-02.md` and the R23G-active main handoff snapshot. It does not change any historical experiment contract or decision.

## Accepted R23G result

Lane / node: G / node109.
Execution branch: `hrl/awma-r23g-r81-live-dispatch-109-v1`.
Starting contract: `f981039d9289368cc32f761d6e5a79f91a775266`.
Result commit: `99d05f0ad221a1d44dd11bac0ed83965bb2c0942`.
Result tree: `b3bcf21e81e1bc34a3281d41b570d6021d8a1edd`.

Accepted under the unchanged frozen Goal:
`R23G_R81_LIVE_DISPATCH_LOCAL_RESPONSE_PRESENT`.

中文结论：固定RULE_U01在本轮冻结的三个公开来源B4批次中，计入CPU union、分派与真实A0/A3切换后，仍保留稳定的净LIVE_HEAD收益。原完整生成安全退化门通过。这是有范围的软件结果，不是稳定普遍端到端加速，也不是硬件结果。

- V0 net LIVE_HEAD reductions across three groups: 24.16%, 24.48%, 23.98%.
- V1: 31.32%, 30.91%, 33.80%.
- V2: 15.72%, 15.52%, 15.52%.
- All nine groups pass their original 3x larger-arm MAD noise rule; all three batches are stable local positives.
- All published semantic qualifications and 90 formal runs report exact token/schema qualification.
- No stable complete-generation regression above 2%; complete-generation gains remain variable and not uniformly noise-stable across groups.

## Coverage and claim limits

Public dataset: `korotkov/glaive-function-calling-v2-parsed`, test revision `b5b1a23f1a88b180d512789ab0a77bf0764dc774`.
The fixed 24-row pool all passed B0 qualification; its first 12 were frozen and grouped consecutively.

Review adds a mandatory descriptive qualification: these are 12 distinct source-row identities but only 9 distinct prompt/schema combinations and 8 schema hashes. Ranks 1, 2, 4, 5 repeat the same prompt/schema. This does not violate the original selection rule; do not retroactively deduplicate, regroup or rerun. Do not present the cohort as 12 independent tasks or as a production distribution.

Non-target kernel neutrality and task accuracy are not established. No local positive automatically authorizes hardware. No whole-application 5% veto is introduced.

## Review / software-result authority

Detailed review was published at `3af156d8f9a217289909c694f269665ef88c8db2`:
`docs/vm_tlb/literature_notes/awma/empirical/R23G_LIVE_DISPATCH_REVIEW_2026-10-02.md`.

ChatGPT read the exact original Goal, current GitHub execution commit/tree, code and review pack, and locally recomputed all formal timing median/MAD groups. Node process release, old-fixture canary and node164 publication remain execution-receipt evidence, not a claimed ChatGPT SSH/raw re-execution.

## Current lane / resource disposition

- Lane G / node109: R23G COMPLETED; accepted scoped software result; STOP per original Goal closure.
- Lane F / node109: R22F1 STOP at `bb5c66c674007cc6c9a77549fb0f81528be30056`; no OEQ Donline, old holdout, profile or model/frame rescue.
- Lane E / 174-new: R22E STOP at `4fbef16c342fb409918aef7a3922c4f5334761ac`.
- R20 CLOSED; R21A/OEQ target-family line STOP.
- No new AWMA GPU, node174/Accel-Sim or hardware execution is authorized by this record.
- F/G remain two node109 windows; E remains on 174-new. Lane names are unchanged.
- CUDA/JIT/generation/profile activities still share `/data/c16/locks/c16_gpu_campaign.lock`.
- Node164 remains durable large-data authority. No large-trace staging requirement on 174.

No restart command, reset, merge, new node Goal, expanded timing matrix, threshold/union sweep or new hardware work was issued during this review.

## Next interpretation boundary, not execution authorization

Preserve R81 conditional sparse-state results and add R23G's cost-inclusive online software policy result. R22G's historical unknown-cost audit remains unchanged. Any later integration or broader independent validation needs a separately explicit question and authorization; this review does not launch it.
