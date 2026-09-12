# C14 dual-path exploration — START HERE

状态：`C14_DUAL_PATH_EXPLORATION_AUTHORIZED`

本窗口与正在收口的 C13 effective-config audit **并行但完全隔离**。C13 D 窗口继续负责 EQ1→EQ2、repaired exact-mode replay 和最终 H1/H2/H3 closure；C14 不写 C13 worktree、C13 output dirs、C13 review pack，也不修改 C12 正式资产。

C14 的目标是利用当前共享主机的大量空闲 CPU/内存，在 C13 最终结论出来前，提前把两种相反结果下都值得做的下一步准备到可评审状态：

1. **Path P — Segment-positive continuation**：若 corrected C13 证明 Segment 在正确 exact-mode 下仍有稳定收益，重点研究 Segment 与 conventional exact translation path 的交互、冗余工作和 latency 暴露，准备一个低风险的 Segment-aware path-gating / scheduling 候选机制。
2. **Path N — Segment-fragile / negative-result pivot**：若 corrected C13 表明 Segment 收益脆弱、依赖极低 lookup latency、或 capacity/object 假设不成立，则转向“translation criticality / exposure”问题：不是继续减少所有 miss，而是识别哪些 translation 真正暴露到 GPU 执行关键路径，并为 criticality-aware translation 准备观测基础和候选机制。

Framework branch：

`hrl/vm-m4b-c14-dual-path-explore-v0`

本分支起点：C13 repaired Decode checkpoint

`889704ff6e8e7ed52c8aad8c5f414bc9fd743af3`

建议独立 Framework worktree：

`/workspace/worktrees/accel-sim-vm-m4b-c14-dual-path`

两个独立 Core branches 已建立，均从正式 C12 Core `57bb71ecd015b6ec0ab32e45b0815e5beaf69172` 起步：

- Positive：`hrl/vm-m4b-c14-segment-positive-v0`
- Negative/Pivot：`hrl/vm-m4b-c14-criticality-v0`

建议 Core worktrees：

- `/workspace/worktrees/gpgpu-sim-vm-m4b-c14-segment-positive`
- `/workspace/worktrees/gpgpu-sim-vm-m4b-c14-criticality`

必须依次阅读：

1. `C14_DUAL_PATH_EXPLORATION_GOAL.md`
2. `C14_PATH_P_SEGMENT_POSITIVE.md`
3. `C14_PATH_N_CRITICALITY_PIVOT.md`
4. `C14_MICRODIAGNOSTIC_MATRIX.tsv`
5. `C14_ACCEPTANCE_AND_HANDOFF.md`

C13 只读输入：

- branch `hrl/vm-m4b-c13-diagnostics-v0`
- 当前至少已到 `889704ff...`
- 允许在阶段边界 `git fetch` 获取更新后的 C13 checkpoint / final report，但禁止向该分支写入。

## 当前证据边界

- C12 正式 22-arm 结果仍是主科学锚点。
- C13 原始 9 个 mode=1 结果已经 superseded，不能作为下一阶段机制事实。
- repaired Decode 三点已经 mode=0、terminal/conservation PASS，但仍在 `PASS_PENDING_EQ_GATE`；只能作为条件性信号，直到 C13 EQ1→EQ2 晋升。
- C14 microdiagnostics 只用于机制定位和代码验证，统一标为 `EXPLORATORY_MICRODIAGNOSTIC`，不得冒充 full-ROI paper result。

## 成功状态

`C14_DUAL_PATH_EXPLORATION_COMPLETE_READY_FOR_REVIEW`

C14 不负责自动选择最终论文主线；最终由 C13 repaired evidence + C14 两条路线的可行性一起决定。