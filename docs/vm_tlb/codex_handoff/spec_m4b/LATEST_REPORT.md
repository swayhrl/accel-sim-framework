# Window C — SPECULATIVE M4B DEVELOPMENT 交接报告

结论：`C0 → C4 PASS；C5 SKIPPED_POLICY；C6 closeout 完成；C7 analysis-only 完成`。实现和数据均为
`SPECULATIVE_CANDIDATE`，sub-entry 采用冻结的
`REFERENCE_APPROX_SUBENTRY_16`，绝不作为 target 论文精确复现或正式 M4B 性能结论。

## 隔离与分支

| 项目 | SHA / 状态 |
| --- | --- |
| Framework branch | `hrl/vm-m4b-speculative-v0` |
| Framework C4 tested runtime anchor | `5dd4501a51720a959129860b72988a6961b07477` |
| Framework C7 evidence HEAD | `ea07cb0ec6fb3212c18f3435637f055e1296d737` |
| Core frozen functional SHA | `c21137bcb86010215c008292f272aacefac175d3` |
| Framework original branch point | `eb18c43c516bdcd52c164969df10d97b895f45f1` |
| Core original branch point | `0d92e6aa8fd8bc885ffdf081a559bc616aaa85fd` |

两者均为 `hrl/vm-m4b-speculative-v0`。使用的 worktree 是
`/workspace/worktrees/accel-sim-vm-m4b-speculative` 与
`/workspace/worktrees/gpgpu-sim-vm-m4b-speculative`，所有运行 scratch 位于
`/workspace/vm-m4b-speculative/`。没有合并到 Window A，也没有实现任何被明确禁止的
后续机制。两个隔离分支均已推送到各自的 `origin`。

## 已实现的内容

- C0 恢复 completed-delivery 不阻塞 quiescent completion 的既有 invariant；M1--M3 与
  M4C 标准基线通过。
- C1 审计后冻结 `REFERENCE_APPROX_SUBENTRY_16`：仅 64KiB、每 group 16 leaf、group
  LRU/replacement；标准 L2 exact-page 路径不变。
- C2 增加分离的 speculative `subentry_tlb` 和运行 profile；标准模式与 2MiB 标准行为
  保持回归兼容。
- C3 增加 immutable Weight Segment descriptor 和显式 parallel Segment + L1 状态机。
  Segment hit 不触及 conventional L2/MSHR/PWQ/walker/PWC/PTE 且不填充 conventional
  TLB；Segment miss 只复用已经完成的 L1；KV/Unknown 保持普通 paging；PTW retry 不会
  二次 Segment probe。

完整语义和证据限制见 `C1_SUBENTRY_SEMANTICS_AUDIT.md`、
`C2_SUBENTRY_VALIDATION.md`、`C3_WEIGHT_SEGMENTATION_STATE_MACHINE.md`。

## 验证

已通过 M1、全部 M2/M3、M4C、sub-entry、Weight Segmentation 共 18 个定向测试；全量
构建成功。提交后二进制/本地 runtime SHA-256 分别为：

```
6a40636e76b33f7f3622e175144379febf8d018b9e3e93d1e62d7c8383fb74fd
20d1c446391c2f6da4f764ab3904b2b236f7571ad8511f4bf0c68a5607297b7e
```

提交后的受限真实 Llama decode1 三连续 kernel 回放，paper、sub-entry、sub-entry +
Weight Segment 和 ideal 均退出码 0。四种 profile 的前端 data/store/atomic telemetry
哈希完全一致；Segment profile 显示 512 次 Weight hit 和 512 次下游 L2 语义抑制。详情见
`C4_BOUNDED_REPLAY.md`。

## C5 决策

完整 speculative prefill/decode1 replay 没有启动：scratch 仅约 2% 可用，swap 仅剩
216 KiB，违反资源 farm policy。此为有意的 `SKIPPED_POLICY`，不代表候选失败；详细
快照在 `C5_RESOURCE_DECISION.md`。

## C7 analysis-only（实现冻结）

没有启动 C5 或任何新的 simulator workload。离线 opportunity 审计位于
`docs/vm_tlb/review_packs/M4B_SPECULATIVE_DEVELOPMENT/C7_SPECULATIVE_CANDIDATE_OPPORTUNITY_ANALYSIS.md`；
它维持 `REFERENCE_APPROX_SUBENTRY_16` / `SPECULATIVE_CANDIDATE` 标签，并将 Weight
Segment 评为 HIGH、sub-entry 评为 MEDIUM 的**分析机会**，不是性能结论。

## C8 authorized next stage

下一阶段为 analysis-only：`C8_HARDWARE_COST_AND_MODEL_RISK_AUDIT`。

C8 只读审计当前冻结 Core `c21137bc...` 与 C1/C3/C4/C7 证据，目标是回答 Weight Segment/Sub-entry 是否对应合理可实现的硬件、当前 simulator shortcut/assumption 有哪些风险、以及 C5 full replay 前是否必须先修正模型。

C8 禁止修改 Core、build、启动 simulator/C5、生成 trace 或扫描完整大 ROI。完整要求见：

- `docs/vm_tlb/codex_handoff/spec_m4b/C8_HARDWARE_COST_AND_MODEL_RISK_AUDIT.md`
- `docs/vm_tlb/codex_handoff/spec_m4b/C8_ACCEPTANCE_MATRIX.md`

C8 最终必须从规定的 C5 gate conclusion 中选择一个，commit/push 后 STOP；不得自动启动 C5 或继续实现 KV segmentation/12K/M5。

## 边界

保持 `REFERENCE_APPROX_SUBENTRY_16` / `SPECULATIVE_CANDIDATE`。不要进入 synthetic 12K KV、KV segmentation、M5，或将此分支并入 Window A。