# C13 diagnostic window — START HERE

状态：`C13_DIAGNOSTICS_AUTHORIZED_TO_START_AFTER_PREFLIGHT`

本窗口不是新的 paper-primary 公平矩阵，而是 C12 + Operator-aware Deep Dive 之后的**最小受控诊断实验**。目标是用尽量少的新 full-ROI replay，区分三个仍未闭合的问题：

1. Prefill 的 Segment 退化是否主要来自 Embedding/Output Weight，是否值得做 object-selective Segment eligibility；
2. Prefill 中 Segment 大量 suppress L2 lookup、但传统 walk/PTE-DRAM 反而增加，是否主要由 fair-budget 下 exact L2-TLB remainder 从 768 缩到 320 引起；
3. 当前 F7 并发查询微架构的真实正收益区间是否位于 Deep Dive 推出的经验 break-even 附近，而不是仅由 5/10/20 三个稀疏点造成。

Framework diagnostic branch：

`hrl/vm-m4b-c13-diagnostics-v0`

分支基于正式 C12 closeout：

`a268aba0d01310294074ded5bb8017e2092394c0`

建议独立 worktree：

`/workspace/worktrees/accel-sim-vm-m4b-c13-diagnostics`

必须按顺序阅读：

1. `C13_DIAGNOSTIC_REFERENCE_ANCHORS.md`
2. `C13_DIAGNOSTIC_GOAL.md`
3. `C13_DIAGNOSTIC_EXPERIMENT_MATRIX.tsv`
4. `C13_SELECTIVE_SEGMENT_CONTRACT.md`
5. `C13_DIAGNOSTIC_ACCEPTANCE.md`
6. `C13_DIAGNOSTIC_RESULT_SCHEMA.tsv`

Deep Dive 动机来源（只读参考，不属于本分支执行身份）：

- branch `hrl/vm-m4b-operator-aware-v0`
- accepted deep-dive commit `8801f2e9fea4e0df1d79853a5e4440c4da463486`
- review-pack commit `484663a46b3810df24b31d8f97cd9cdb671ed91b`

本轮 primary diagnostic 新点固定为 **7 个 full-ROI arms**。其中 5 个 Prefill、2 个 Decode1。若 selective eligibility 必须修改 Core/binary，则额外增加 2 个 same-new-binary controls；这两个只在该条件成立时执行。

禁止把 C13 diagnostic 结果包装成 equal-budget final architecture comparison。C12 仍是正式公平基线，C13 只用于因果诊断和下一阶段机制选择。

成功状态：

`C13_MINIMAL_DIAGNOSTICS_COMPLETE_READY_FOR_REVIEW`

真正无法继续：

`C13_MINIMAL_DIAGNOSTICS_HARD_BLOCKER_WITH_EVIDENCE`
