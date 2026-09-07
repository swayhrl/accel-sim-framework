# Window C — SPECULATIVE M4B DEVELOPMENT 当前交接

结论：`C0-C4 PASS；C5 SKIPPED_POLICY；C6 closeout；C7/C8 analysis-only 完成；C9 design-only 完成；C10-A partial implementation 完成`。历史实现与结果继续标记 `SPECULATIVE_CANDIDATE`，sub-entry 保持 `REFERENCE_APPROX_SUBENTRY_16`，不得作为 target paper 精确复现或正式性能结论。

## 冻结身份

| 项目 | SHA / 状态 |
|---|---|
| Framework branch | `hrl/vm-m4b-speculative-v0` |
| C10-A evidence HEAD | `47840049d6c0ea41748674d4284e7d51d11aad56` |
| C10-A Core HEAD | `c27bf0e2fc5e24c54966426840bd56748ef92028` |
| C10-A Core parent | `c21137bcb86010215c008292f272aacefac175d3` |
| C9 architecture SHA | `04be2899a19b1fe756956dbe5e459494ae1da8df` |
| C4 tested runtime anchor | `5dd4501a51720a959129860b72988a6961b07477` |

## External A evidence context

Window A progress checkpoint：`73d25ebbdd96833ee1ddb8ea42b9017cefbceb75`。

Window A early C4 analysis：`2e491abec2afb0c745ca26aae0d86f8f35ad096b`。它只作为方法学/observability 参考，不是 C candidate 的参数校准输入。

A early C4 显示：decode paper 相比 generic 的 L1/L2 miss 与 MSHR-full 更少但 cycles 更高，同时 PTE memory-wait、requester-MSHR-wait 与部分 memory-hierarchy queue occupancy 更高。因此未来 C 模型/报告必须保留 queue/backpressure/latency/stall 和 cross-layer memory outcome；A/C 数值不得合并或用于调参匹配。

## C9 architecture decision（完成）

C9 唯一结论：`ARCHITECTURE_READY_FOR_MODEL_IMPLEMENTATION`。

冻结 v1：privileged runtime/driver registration、real `PA_base + (VA-VA_base)`、N=8 local replicated Segment table、single provisioned ASID、`HIT_FIRST / MISS_JOIN`、5/10/20 Segment latency sensitivity、pinned immutable epoch；object map telemetry-only。Fair sub-entry standalone G96，charged combined G32；历史 768-group 永不作为 equal-cost arm。

## C10-A implementation（完成但 partial）

Framework：`47840049d6c0ea41748674d4284e7d51d11aad56`。
Core：`c27bf0e2fc5e24c54966426840bd56748ef92028`，严格从 `c21137bc...` 开始两段 functional delta。

最终状态：

`C10A_IMPLEMENTATION_PARTIAL_WITH_NAMED_BLOCKERS`

已落地：real-PA V2 registered mapping、registration-based eligibility、logical N=8 local replicas、`HIT_FIRST / MISS_JOIN`、Segment/order/fallback telemetry、G96/G32 geometry 和 F0-F9/H0 static fairness contract。

但最终 Core **未编译、未链接、未运行**，因为 closeout 时 SwapFree 仅约 76 kB。任何 candidate replay 仍被禁止。

关键 named blockers：
- semantic registration rejection 仍可能 assert 而非原子 conventional fallback；
- runtime install/revoke/replica-ack lifecycle 未闭合；
- production translation callers 仍可能依赖 READ default，store/atomic 尚未端到端接入；
- F0-F9 主要是 static contract，尚非完整 runtime-selectable profiles；
- sub-entry fill 尚未绑定 ASID generation，stale-fill race 未闭合；
- F5 physical PWC model 未实现；
- final compile/regression/post-delta telemetry inspection 未运行。

完整证据：
`docs/vm_tlb/review_packs/M4B_SPECULATIVE_DEVELOPMENT/C10A_ARCHITECTURE_MODEL_IMPLEMENTATION_LOW_RESOURCE/`。

## C10-A2 authorized next stage

现授权：

`C10A2_NAMED_BLOCKER_STATIC_CLOSURE`

执行文档：
- `docs/vm_tlb/codex_handoff/spec_m4b/C10A2_NAMED_BLOCKER_STATIC_CLOSURE.md`
- `docs/vm_tlb/codex_handoff/spec_m4b/C10A2_ACCEPTANCE_MATRIX.md`

C10-A2 允许继续修改 Framework/Core source，但仍严格 **NO BUILD / NO SIMULATOR / NO C5 / NO LARGE TRACE**。目标是在 Window A 仍运行期间关闭可由 source/static 工作解决的 B2-B7 blockers：atomic registration fallback、install/revoke+replica acknowledgements、production access-class wiring、fair-arm runtime plumbing、sub-entry generation/stale-fill race。F5 只有在前述 blocker 闭合后且 source-only 风险可控时才尝试；否则继续硬阻塞。

即使 C10-A2 达到 `C10A2_STATIC_BLOCKERS_CLOSED_COMPILE_AND_RUNTIME_DEFERRED`，也不代表候选可运行。最终 compile/link、standard regression、candidate focused runtime tests、cross-layer output inspection 和 C5 都必须等后续独立 C10-B 授权。

C10-A2 完成后 commit/push 并 STOP；不得自动进入 C10-B/C5/KV segmentation/12K/M5。
