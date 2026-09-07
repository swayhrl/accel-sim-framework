# Window C — SPECULATIVE M4B DEVELOPMENT 当前交接

结论：`C0-C4 PASS；C5 SKIPPED_POLICY；C6 closeout；C7/C8 analysis-only 完成`。历史实现与结果继续标记 `SPECULATIVE_CANDIDATE`，sub-entry 保持 `REFERENCE_APPROX_SUBENTRY_16`，不得作为 target paper 精确复现或正式性能结论。

## 冻结身份

| 项目 | SHA / 状态 |
|---|---|
| Framework branch | `hrl/vm-m4b-speculative-v0` |
| C8 evidence SHA | `468fe62ddc1c4d1786133072b540e52e0d8bdc23` |
| C4 tested runtime anchor | `5dd4501a51720a959129860b72988a6961b07477` |
| Core frozen functional SHA | `c21137bcb86010215c008292f272aacefac175d3` |
| original Framework branch point | `eb18c43c516bdcd52c164969df10d97b895f45f1` |
| original Core branch point | `0d92e6aa8fd8bc885ffdf081a559bc616aaa85fd` |

C0-C4 已有 18 个定向测试、bounded real replay 和 Weight Segment C4 telemetry。C7 将 Weight Segment 评为 HIGH analytical opportunity、Sub-entry MEDIUM；均不是性能结论。

## C8 architecture gate

C8 的唯一 C5 gate：

`ARCHITECTURE_DECISION_REQUIRED`

原因：
- current Segment hit 使用 identity-like `ppn=vpn`，没有真实 PA mapping；
- `OBJECT_WEIGHT` 是 simulator metadata，不是可信硬件安装来源；
- Segment table port/bank/queue/latency 及 parallel-L1 ordering 未定义；
- descriptor context/lifecycle/migration/shootdown 未定义；
- current 768-group sub-entry 最多可容纳 12,288 leaves，对 768 exact entries 不是同预算比较。

因此不得在资源恢复后直接重启 C5。

## External A checkpoint context

A progress checkpoint：`73d25ebbdd96833ee1ddb8ea42b9017cefbceb75`。

七个 C3 arms 已 terminal，prefill-paper 在 checkpoint 时仍 RUNNING。A decode evidence 显示 ideal/disabled 相同，而 generic/paper 有显著 translation overhead；paper 虽有更低部分 miss/MSHR-full counters，cycles 仍高于 generic。这只作为 motivation：未来 C architecture/reporting 必须保留 queue/backpressure/latency/stall observables，不能只靠 hit/miss rate。A/C 数值不得合并，也不得据此调参匹配比例。

## C9 authorized next stage

下一阶段：

`C9_SEGMENT_SUBENTRY_ARCHITECTURE_DECISION`

模式：`DESIGN_ONLY`。

目标是把 C8 的开放问题收敛成 future C10 可直接实现的 architecture specification：
- real VA->PA Segment descriptor；
- trusted runtime/driver installation；
- descriptor topology/capacity/throughput；
- parallel L1/Segment completion ordering；
- pinned inference epoch / context / invalidate lifecycle；
- parameterized Segment latency；
- Sub-entry equal-bit budget `G_equal_bit`；
- exact/PWC/2MiB/leaf-capacity/combined candidate 的公平 baseline policy。

严格执行：
- `docs/vm_tlb/codex_handoff/spec_m4b/C9_SEGMENT_SUBENTRY_ARCHITECTURE_DECISION.md`
- `docs/vm_tlb/codex_handoff/spec_m4b/C9_ACCEPTANCE_MATRIX.md`
- `docs/vm_tlb/paper_specs/SEGMENTATION_LLM_2026.md`

Core `c21137bc...` 必须保持完全冻结。本轮禁止 build、simulator、C5、trace/full-scan 或实现修改。

C9 最终只能选择：
- `ARCHITECTURE_READY_FOR_MODEL_IMPLEMENTATION`
- `ARCHITECTURE_DECISION_STILL_OPEN`

完成后 commit/push 并 STOP，不自动启动 C10/C5/KV segmentation/12K/M5。
