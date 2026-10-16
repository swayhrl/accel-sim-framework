# EP-L2 GitHub执行入口｜Lane 1–6

发布日期：2026-10-16。状态：`HANDOFF_READY / EXECUTION_NOT_STARTED_BY_PUBLICATION`。

本轮用户已同意功能实现、天花板诊断、实验与论文并行，并要求通过GitHub协调。本文将原任务包的当前Lane A–F依次命名为Lane 1–6；历史分支、历史review pack及历史LANE_D文件名不改。

## 先读什么

1. `COMMON_CONTRACT.md`：已同意的机制、预算、正确性与实验边界。
2. `COORDINATION_PROTOCOL.md`：工作树、分支、依赖、状态与证据发布方式。
3. 自己的`LANE_<N>_GOAL.md`：连续执行任务，不止于计划或复述。
4. `EVIDENCE_INDEX.md`：历史证据的准确仓库、提交和路径。按任务需要用`git show <SHA>:<path>`读取；不因当前分支缺文件就认为来源不存在。

## 六个窗口

| Lane | 任务文件 | 职责 | 可立即做的部分 |
|---|---|---|---|
| 1 | [LANE_1_GOAL.md](LANE_1_GOAL.md) | 公共Core、有限WBUF、统一WB池、最终集成 | 发布接口；旧模式等价；B16/U_WB16 |
| 2 | [LANE_2_GOAL.md](LANE_2_GOAL.md) | Clean/dirty TVD | 模块、状态表、生产驱动测试；接口就绪后接入 |
| 3 | [LANE_3_GOAL.md](LANE_3_GOAL.md) | RO oracle与Pending事务 | 输入认证、独立事务模块、测试；接口就绪后接入 |
| 4 | [LANE_4_GOAL.md](LANE_4_GOAL.md) | 理想化天花板与历史结果复用 | 立即核查旧结果，开发I_WB/I_META/I_READ_HIT |
| 5 | [LANE_5_GOAL.md](LANE_5_GOAL.md) | 独立验证、资源配额、运行去重、实验 | 先发布配额与registry位置，准备测试和runner |
| 6 | [LANE_6_GOAL.md](LANE_6_GOAL.md) | 论文、证据映射、PPA | 立即写正文与成本账，不等待完整结果 |

首个功能比较仍是`B16_BANKED vs U_WB16`。Lane 4不等Full EP-L2；Lane 2/3不空等Lane 1。新功能、诊断开关默认OFF；旧校准不重跑整套；16项WBUF主配置、8项敏感性分别等预算1168/1160项；RO oracle与TVD额外一拍保持已同意口径。

## GitHub入口与身份

- 协调仓库：`swayhrl/accel-sim-framework`。
- 协调分支：`hrl/ep-l2-ft20261016-coordination-v1`。
- 本目录：`docs/ep_l2/chatgpt_handoff/fast_track_2026_10_16_v1/`。
- Core仓库：`swayhrl/gpgpu-sim`；本次发布不修改Core。
- 六个执行分支：`hrl/ep-l2-ft20261016-lane1-v1`至`hrl/ep-l2-ft20261016-lane6-v1`，仅在相应lane实际开始时创建或继续；发布分支不等于已启动任务。
- 协调分支基于Framework `b7dbdecb94054f08aaf2e33bfef48e453747ceb5`，只作文档协调，不是新的模拟器runtime authority。
- 工程起点候选：Core `1fc248aa89abefbd1b417f7f4053cd2bf56d7a1e`，Framework集成归档`54fbc7869f4e40b6b48dc936b527fee85dd46406`；Lane 1验证匹配后发布实际source/binary/config合同。不得把协调提交填成运行源码SHA。

## 启动纪律

用户给每个窗口一个Lane编号与本次协调提交SHA。窗口只读fetch该提交，完整读上述文件，然后检查已有活动任务；没有重复任务才建立隔离工作树执行。不要checkout/reset/rebuild其他lane的工作树。

首次报告写入自己的执行分支，状态为真实的`IN_PROGRESS`或有具体原因的阻塞，不可仅凭本文件宣称`RUNNING`。各lane发布`READY_FOR_REVIEW`不等于ChatGPT已独立接受。

公共合同只保存一份；任务文件通过引用使用它。内容来源校验见`SOURCE_INPUTS.json`；本次发布只做任务编号、文件拆分和GitHub协调补充，不改变已同意的研究方案。历史STOP在本轮明确授权的功能范围内由本合同替代，未授权扩展仍保持禁止。
