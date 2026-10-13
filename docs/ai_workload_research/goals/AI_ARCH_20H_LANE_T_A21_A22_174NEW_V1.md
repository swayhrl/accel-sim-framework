# AI-ARCH｜20小时无人值守 Lane T：A21真实场景准入→A22状态寿命source地图

**执行者：Codex Lane T／174-new，复用现有Lane T窗口（CPU/source-only）；科研协调：ChatGPT／AI-ARCH Discovery。**  
**任务总纲：** [20小时无人值守总计划](../ops/AI_ARCH_UNATTENDED_20H_2026-10-14_V1.md)，在用户离开前一次投递本Goal，允许在**科学目标固定、没有GPU/模型或场景下载、时间资源已设上限**的前提下连续完成两个**独立Git身份**的source-only任务。  
**执行状态：`PREPARED_ONLY`，需要用户向174 Lane T发送启动指令。**

## 0. 历史状态与不可覆盖边界

- 历史Lane T A4`a1a70180736499687435b1e2d99984d4ebba4c53`及A10`859eb16a51c7bf085d6e39a9000de198c0f4e710`均完成STOP；**不得reset、checkout覆盖或提交到旧任务branch**。
- 当前已经备好的A21执行分支：`hrl/aiarch-a21-gsscale-real-scene-source-174-v1`，起点`d3d5e235db0822a2404e05dcdb705ffc942e70ec`，完整A21合同为[`AI_ARCH_A21_GSSCALE_REAL_SCENE_SOURCE_ADMISSION_174NEW_V1.md`](AI_ARCH_A21_GSSCALE_REAL_SCENE_SOURCE_ADMISSION_174NEW_V1.md)（blob `9c96a86847eddc810f1219be766ed666761ea39d`）。
- [A20三家族已有科研审查](../literature/AI_ARCH_A20_REAL_AI_WORKLOAD_REDISCOVERY_THREE_FAMILY_AUDIT_2026-10-14_V1.md)已经做过GS-Scale真实场景/CPU-only依赖以及HSTU/MLIP近邻，**不得再做一次宽泛文献调研**。
- 本次20小时的新批准范围只新增一个**完全独立CPU/source-only A22**阶段，不会把A21已规定的STOP提升为“可以继续它的GPU运行”；A21先按原合同**commit/push/STOP A21阶段**，然后仅按本文件授权转到命名A22，在新的worktree/branch操作。任何其它后续Goal均不获授权。

## 1. 统一预检，确保两个Codex不会互相挤爆174

- 先`df -h`、`free -h`、`git status`、`git worktree list`，不使用sudo，不清理旧worktree/cache/swap。根盘压力或swap不足→`RESOURCE_DEFERRED`，只读GitHub API写最小报告，不能挤坏其它项目。
- 这条Lane总资源硬预算：CPU≤4 workers，物理RSS≤8GiB，本次worktree/资料新增≤200MiB；**A21总wall≤3小时，A22≤4小时，整Lane≤7小时**。若source API访问被限流，可退回已有固定Git blob或官方HTML；两种确定性入口都不可用则`SOURCE_BLOCKED`，不触发无界重试。
- 网络仅限作者论文、官方GitHub固定文本及公开小metadata，不下载场景tgz、权重、3DGS模型、gsplat仓库全量副本、PDF大批量、Torch/IPEX/wheel和镜像。不要`import torch`、运行训练/渲染/数值CUDA或NVCC。
- 不ssh 109/164、不调用GPU锁；C16/AWMA/NequIP/GreenContext权威及缓存保持冻结。

## 2. 阶段A｜严格按照已冻结A21科学合同执行

**目标**：建立真实Mill-19 Building或Rubble输入的作者来源/处理/scene manifest可复现性；对比原始`gsplat GPU-only`、naive host仅消融和**完整GS-Scale优化**；对目标109未来完整训练的CPU/Intel IPEX门保持未核实，**不得通过源码自行推算机器fit**。

按原A21仅新增：
`docs/ai_workload_research/reviews/AI_ARCH_A21_GSSCALE_REAL_SCENE_SOURCE_ADMISSION_174NEW_V1.md`

需包括原8个固定源码blob/符号、自然图像/point cloud/camera处理身份缺口、训练动态Gaussian创建/删减/visibility ID限制、Adam epsilon不严格bitwise的对照、完整训练时间/峰值容量/达到PSNR质量时间三分母、强软件已解决能力和有范围结论。

- 正常闭合即`SOURCE_INPUT_CONTRACT_FEASIBLE_PENDING_ASSETS`、`SOFTWARE_ABSORBED`、`INPUT_IDENTITY_BLOCKED`或`PLATFORM_UNQUALIFIED`；**blocked也是有效结束**，不可盲下载弥补。
- `git add`仅A21单报告，commit/push并远端fetch-back校验commit/tree/blob；A21独立STOP后才进入B。
- 如果A21卡在合法的`SOURCE_BLOCKED`，先保留能够审查的部分交付。A22属于静态source分析，不依赖A21 input hash闭合，因此可继续A22，但**不能在A22里用缺失的真实场景原始ID**。

## 3. 阶段B｜新A22：训练step状态与依赖/时间原理图（不可运行）

**A22独立合同**：[A22状态寿命CPU-only合同](AI_ARCH_A22_GSSCALE_STEP_LIFETIME_SOURCE_ONLY_174NEW_V1.md)，必须与本总控一并阅读；其中规定相同的独立输入/正确性/资源限制。

**A22独立分支**：`hrl/aiarch-a22-gsscale-step-state-lifetime-174-v1`，从20小时总计划的固定Git协调commit创建单独worktree（如远端预建该分支，则核对HEAD并使用）；**不得基于A21实验branch merge或复制其代码产物**。可引用A21提交链接作为外部冻结输入，不重写A21。

**唯一交付**：
`docs/ai_workload_research/reviews/AI_ARCH_A22_GSSCALE_STEP_STATE_LIFETIME_SOURCE_MAP_174NEW_V1.md`

科学问题：**已优化GS-Scale如何为每一训练步选择活跃Gaussian、在CPU与GPU之间移动参数/梯度和状态、完成CPU优化器更新并发布到下一step？哪些源代码同步是真正必要，哪些已通过软件重叠，哪些还只是作者宣称？**

只读固定作者实现：
[`SNU-ARC/GS-Scale@6471e958f7e318f4870234d8107e0aa91c2d6932`](https://github.com/SNU-ARC/GS-Scale/tree/6471e958f7e318f4870234d8107e0aa91c2d6932)。
重点不超过5份实现文件：
`examples/simple_trainer_hybrid_optimized.py`、`examples/simple_trainer.py`、`examples/simple_trainer_hybrid_baseline.py`、`cpu_adam/src/cpu_adam.cpp`、必要时`examples/simple_trainer_hybrid_optimized_split.py`。每份只查调用入口/持有的state/发布屏障，不复制完整代码。

**必须具体交付**：
1. 一张`producer→state→consumer`的per-step流程图/表，包含camera selection、frustum culling、活动Gaussian ID、GPU gather、forward render/backward、gradient transfer、CPU Adam & deferred counter、下一轮模型状态可见性；用`file:function:line`逐项给source锚点。
2. `DATA_IDENTITY / STATE_LIFETIME / TIMING_WALL`三种观测的最小必要字段（例如相机ID、稳定Gaussian ID+densification epoch、实际copy bytes、CPU更新序列号、CUDA event/host monotonic时间以及必要barrier）；不允许从源码推每步真实ms或reuse率。
3. 对`GPU-only`、`naive host`、`GS-Scale strong host`做**同语义前提**对照；指出deferred Adam忽略ε/形态增密等位置可能使比对不完全等价。源代码不同且没有数值门时不许给性能排序。
4. 一个`minimum future observability instrumentation`草案（写**观测目标与not-timed probes**，不写可启动GPU任务），明确预期反例：如果CPU等待已经完全被隐藏或真实ID没有跨步稳定复用，则停掉硬件cache构想。
5. 输出结论仅限`SOURCE_LIFETIME_MAP_COMPLETE_WITH_INPUT_GAPS`、`SOFTWARE_ABSORBED_BY_STRONG_GSSCALE`、`SOURCE_IDENTITY_BLOCKED`；**不会自动升格为本机原生实验或硬件机制**。

完成后只在A22 branch新增这一份source mapping审查，commit/push/readback SHA并STOP。没有A23/Lane N报告也不阻塞A22：双方并行、不能未经用户许可自动把结果合并。

## 4. 唯一允许的连续性

此处的新指令**特定批准**“A21 source-only完成后自主继续A22 source-only”，不等于一般性重新启动被STOP的科研项目。两个阶段均可提前合法负面结论，且本轮不得转入GPU、CPU训练、软件构建或大数据采样。

最终答复输出A21、A22各自commit/tree/文件SHA/状态与缺口，旧Lane T工作区干净的证据，20小时期间没有触碰GPU/164/109，以及`UNATTENDED_20H_CLOSEOUT`。如超过7h或机器资源门不符则带已完成证据STOP；不耗尽剩余时长为目标。
