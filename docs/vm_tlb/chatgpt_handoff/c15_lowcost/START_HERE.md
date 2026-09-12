# C15 — START HERE

计划版本：`C15_LOWCOST_V1`。状态：`AUTHORIZED_FOR_BOUNDED_PARALLEL_IMPLEMENTATION`。

本阶段只研究AI推理负载的TLB/Cache特性，不包含Decoupled-L1。用户已审定《C15：低成本多模型TLB/Cache负载表征》设计；本包将其C15-0至C15-5拆成可执行、可验证的小阶段。这里的阈值和预算是工程起点，不是已测结果或文献保证。

## 三个并行Goal

| 窗口 | Goal | Framework分支 | 主要职责 |
|---|---|---|---|
| A | `C15_A_STATIC_FINGERPRINT_AND_INTEGRATION` | `hrl/vm-c15-static-v0` | 资产、8–12个配置的静态库、最终只读汇总 |
| B | `C15_B_NATIVE_CENSUS_AND_BOUNDED_CAPTURE` | `hrl/vm-c15-native-capture-v0` | 原生轻量目录、对象寿命、受限选择性采集 |
| C | `C15_C_SAMPLING_AND_RETROSPECTIVE_VALIDATION` | `hrl/vm-c15-sampling-validation-v0` | 分层选样、页/行指纹、既有C12/C13回测与误差 |

共同规划分支：`hrl/vm-c15-lowcost-plan-v0`，只读。三个执行分支从同一个handoff提交开始，底层代码基于正式C12 `a268aba0d01310294074ded5bb8017e2092394c0`。C13/C14/Operator-aware通过固定提交只读消费，不合并成新的模拟执行身份。

## 必读顺序

1. `C15_AUTHORITY_AND_SCOPE.md`
2. `C15_DATA_CONTRACT.md`
3. `C15_RESOURCE_AND_RECOVERY.md`
4. `C15_STAGE_ACCEPTANCE.tsv`
5. `C15_VALIDATION_TEST_CATALOG.md`
6. 自己的`C15_LANE_A_GOAL.md`、`C15_LANE_B_GOAL.md`或`C15_LANE_C_GOAL.md`
7. `C15_REFERENCE_ANCHORS.tsv`及`C15_BUDGET_MATRIX.tsv`

完整路径前缀：`docs/vm_tlb/chatgpt_handoff/c15_lowcost/`。

## 启动方式

在Goal模式发送`C15_LAUNCH_PROMPTS.md`中对应窗口指令。先找已有的`swayhrl/accel-sim-framework` clone，不假定固定主仓库路径。对自己的分支建立独立、非detached worktree。示例（变量须按窗口填入）：

```bash
git -C "$REPO" fetch origin "$BRANCH"
# 本地分支不存在时：
git -C "$REPO" worktree add --track -b "$BRANCH" "$WT" "origin/$BRANCH"
```

若分支/worktree已存在，先检查owner、branch、HEAD、dirty status，安全续用；不得reset、stash、切换别人的worktree或覆盖未提交文件。建议worktree为`/workspace/worktrees/accel-sim-vm-c15-{static,native,sampling}`。

启动后把本次规划commit记为`planning_sha`，读取阶段表，连续完成所有当前可执行的小阶段；不每阶段等待用户确认。所有后续计划变更需保留原版本和理由。

## 首轮授权范围

- C15-0至C15-4：资产/元数据读取、分析工具开发、合成fixture单测、既有数据离线回测。
- B可以在已经连接、获准使用的GPU上运行最多3个本地真实部署的短原生profiling，并在验证通过后执行预算内的选择性采集。
- C15-5：只授权已有/本轮低成本数据的跨模型汇总、抽样审核和升级计划。
- **新增Accel-Sim/GPGPU-Sim回放数=0；新增full-ROI模拟数=0；新增完整模型SASS采集数=0。**
- 不下载完整权重、不租机器、不接受新许可证、不执行未经审计的模型远程代码。无可用GPU或模型时继续完成工具、历史目录导入、回测和静态分析，真实动态结果单独标缺口。

## 并行不互等

A立即生成bootstrap资产/模型清单；B可先盘点本地能力并在既有锚点完成canary；C立刻用冻结C12/Operator-aware资料做选择器和回测。B首次少量选区可使用本包规定的bootstrap规则，不依赖C完成全部回测。跨窗口仅读取已提交且hash绑定的发布物，禁止读取/修改对方正在写的partial。

A完成自身工作后只读fetch B/C，按固定提交整合到A自己的`integration/`目录；不合并或改写B/C分支，不修改规划分支。

## 结果不冒进

工具正确、采样准确、跨模型规律得到验证是三种不同状态。准确性目标未达也要报告完整实验，不得调低阈值、改分母、剔除不利样本后宣称PASS。只有历史模拟来源完整时才保留其`FULL_ROI_VALIDATED`标签；C15派生估计不能升级成新的完整模拟。

各lane使用`READY_FOR_REVIEW`或有证据的`CAPABILITY_LIMITED_READY_FOR_REVIEW`；最终是否接受由独立审阅决定。不存在“模型越多越好”的硬凑数要求。
