# AI负载体系结构研究｜科研协调入口

**角色：研究规划与证据导航分支。不是C16/AWMA的统一实验代码主干，不是任何执行Goal的授权源。**

研究范围：AI训练与推理；LLM、MoE、多模态、推荐、GNN、科学计算/3DGS等非LLM应用；单GPU、多GPU、CPU–GPU协同；计算、调度、数据就绪、片上资源、Cache/TLB、通信、存储、状态生命周期与可靠性。

## 从这里开始

- [统一问题图谱 V1](AI_WORKLOAD_ARCHITECTURE_PROBLEM_ATLAS_V1.md)：按负载/约束组织问题、已知现象、未知前提和潜在架构研究方向。
- [C16 × AWMA跨项目证据索引 V1](AI_WORKLOAD_C16_AWMA_EVIDENCE_INDEX_V1.md)：每条证据的实验范围、实际结论、测量层级和固定来源。
- [当前项目状态](CURRENT_STATE.md)：最新可核对的科研入口与待审结果，供两个ChatGPT协调窗口使用。
- [协调与变更规则](COORDINATION_PROTOCOL.md)：如何更新、如何避免干扰独立实验及已有结果。

## 本分支与两个项目的关系

- 本分支只收录跨项目科研底稿、固定Git证据入口、文献调研和研究决策；**不会把C16与AWMA实验分支直接合并到一起**。
- C16的历史结果仍以各自accepted commit及review pack为科学依据；AWMA已有机制、软件实验和正在进行的任务仍以各自合同及review pack为依据。
- 研究图谱中的科学状态不覆盖原实验`PASS/FAIL/STOP`；新的上层研究优先级也不改变任何已冻结模型、输入、容差、源码或模拟器参数。
- 两个项目可只`git fetch`并阅读此分支的Markdown，无需人工转发文件或切换现有执行worktree。

## 固定状态入口（2026-10-13）

- C16最新Problem Discovery Reset：[`635b2f22cbe1bed5ac45de04b258a5f5e9bc6d4f`](https://github.com/swayhrl/accel-sim-framework/commit/635b2f22cbe1bed5ac45de04b258a5f5e9bc6d4f)，目前无获准的C16 native任务。
- C16 Stage A收口：[`ccd6928bfb420d1e4c554ec0e377bb8fbe377501`](https://github.com/swayhrl/accel-sim-framework/commit/ccd6928bfb420d1e4c554ec0e377bb8fbe377501)，`TERMINAL_PARTIAL`，不得解释为AI没有新瓶颈。
- AWMA R27R3事前交接：[`29ce051f982f3854bd4392a94e4195c59340123b`](https://github.com/swayhrl/accel-sim-framework/commit/29ce051f982f3854bd4392a94e4195c59340123b)，原Goal/STOP规则不变。
- AWMA R27R3现有执行提交：[`7bd31fae4c54e121d54743a803d978ee02a64959`](https://github.com/swayhrl/accel-sim-framework/commit/7bd31fae4c54e121d54743a803d978ee02a64959)，`B0_REFERENCE_NOT_REPEATABLE`为**已提交的执行结论，尚待AWMA独立科研审查**。
- AWMA研究笔记：[`0b8310ee4afe8429b3ed2de381594794ee12ae31`](https://github.com/swayhrl/accel-sim-framework/commit/0b8310ee4afe8429b3ed2de381594794ee12ae31)；其中授权状态为发布时快照，不代替最新执行分支结果。

## 一条重要边界

本协调分支的提交、合并、标签更新或文件维护，都**不自动批准GPU执行、模型下载、重编译、Profiler、模拟器、硬件实验、holdout、重启/修改运行中的Goal**。具体执行必须由对应项目单独审核并形成冻结合同。
