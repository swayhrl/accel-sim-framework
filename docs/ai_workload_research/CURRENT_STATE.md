# AI-ARCH｜当前科研协调状态

**最新快照：2026-10-16 / Round A75。** A74-C完成并以`PARKED_FOR_PPA_OR_SIM_MODEL / STOP`保留、未启动109 Codex/GPU；新一轮主流生成AI Discovery已由ChatGPT完成原始研究，识别两个**不同于A70/A74已有问题**的CPU/source候选：真实Qwen3 GRPO后训练各阶段和Wan2.2跨去噪step的视频DiT。两条独立Codex目标及分支已经准备，尚未由用户分别派发；不因科研笔记发布而自动启动节点任务。

固定历史导航：[A74-C完成快照](https://github.com/swayhrl/accel-sim-framework/blob/05c1722066bda6a079d92fdfca34bdd28249a72f/docs/ai_workload_research/CURRENT_STATE.md)。原A70四线0候选、A73 W source-incomplete/H source-only、A74 SFU固定面积假说Parked与所有独立项目STOP均未变。

## 1. A75已完成的ChatGPT文献／源码发现

**[A75完整研究笔记](literature/AI_ARCH_A75_MAINSTREAM_POSTTRAIN_SPEC_VERIFY_AND_VIDEO_DIT_DISCOVERY_2026-10-16_V1.md)**，首次研究提交`fe65befc648bc938856b9a06dd1175a4a836a638`；其后只修正文中“本地平台”文字错误，具体report以本协调branch最新文件为准。

| 方向 | 已有真实作者证据／成熟实现 | 当前科学选择 |
|---|---|---|
| **R：主流Qwen3 RL后训练** | NeMo RL Qwen3-8B GRPO实测训练步：无spec/有EAGLE3的Generation RL-Zero100.0→56.6s，总步151.2→107.5s；RL-Think133.6→87.0s，总步185.3→137.4s；32×GB200原生范围。RolloutPipe Qwen3-1.7B/8×4090训练+2×A100 rollout合法complete-group流水已减少作者训练端等待；Libra/HetRL/AReaL已有其它重叠/弹性路径。 | `SOURCE_QUESTION_FOR_STAGE_CENSUS`：核心是成熟优化后是否仍有GPU本质资源限制，不是“先重叠Rollout与训练”新机制。235B/GB200跨规模加速来自作者模拟，非完整原生。 |
| **V：Speculative Decode验证** | SpecDecode-Bench vLLM H100执行分解报告验证为42–95%区间；**当前2026-10-14 vLLM已经发布不用confidence head的在线自适应验证**，固定代码包含OnlineAcceptanceEstimator。 | `SOFTWARE_NEARBY_DIRECT / PARKED`：通用“裁剪不易接受token、动态分配验证长度”有强软件近邻，不新开一个重复Codex或GPU实验。 |
| **D：主流Wan2.2视频扩散Transformer** | 官方Wan2.2 TI2V-5B完整文/图生成视频；单卡官方720P入口需≥24GiB显存。A14B高/低噪声专家随step切换，非token top-k MoE。TeaCache/CVPR2025、Sliding Tile Attention/ICML2025、Cache-DiT及官方offload是直接软件反证。 | `SOURCE_QUESTION_FOR_NATURAL_STEP_LIFETIME`：核完整自然去噪／视频质量／阶段数据流与已有软件，尚无本机input/numeric/GPU结果。 |

**本轮不能声称两个硬件问题已确认。** 真实作者任务不是本机合格的数据；不能从接受长度、去噪跳步、视频tile局部、逻辑buffer或作者不同GPU加速倍数制造可实现硬件收益。R与D是需要严审的不同工作量，不是两张立即执行的GPU实验单。

固定原始源：NeMo-RL`540d2568c9cd184e01964c7de0a42026334f0a38`，vLLM`9a16d43ef0413b0a2a222e7f5baa4498c291ae5b`，Wan2.2`1ea34ff48f87168174e12956e200b1d908b1c5ff`；对应作者论文/实验组和软件限制均载于A75研究笔记。没有下载权重、接受数据许可或访问164。

## 2. 两条待分别派发的Codex SOURCE任务

**[完整A75 R/D并行Goal包](goals/AI_ARCH_A75_RL_AND_VIDEO_DIT_PARALLEL_DISCOVERY_GOAL_PACK_2026-10-16_V1.md)**，统一固定启动HEAD`1eb14b0395bc898c3707ba850c36f17a9ec07b4e`；两branch从该SHA创建并经过远端回读。

| Lane/宿主 | 独立执行分支 | 研究交付／状态 |
|---|---|---|
| **R-A75／109** | `hrl/aiarch-a75r-rl-posttraining-discovery-109-v1` | 真实GRPO step五阶段、weights及K-group正确性、强NeMo/RolloutPipe/Libra等后若有独立硬件资源限制。只提交自己的REPORT/STAGE_EXPERIMENT_GROUPS/QUESTION_CARDS/RECEIPT，状态`READY_FOR_USER_DISPATCH`。 |
| **D-A75／174-new** | `hrl/aiarch-a75d-wan22-video-dit-discovery-174new-v1` | 官方Wan2.2自然step/latent/高低噪声切换、完整生成质量与STA/TeaCache/BWCache/CacheDit强对照；四份独立文本证据/问题卡，状态`READY_FOR_USER_DISPATCH`。 |

每线工具CPU worker≤1、RSS≤2GiB、新增盘≤128MiB、公开文本/PDF≤64MiB、90分钟收口；**GPU/CUDA/JIT、模型import/加载、权重/真实数据或视频下载、依赖安装、Profiler、模拟器执行、清理及164访问全禁止**。独立分支/worktree/output，不能修改协调CURRENT_STATE或其它Lane、C16/AWMA/ISCAS。允许0主0备，若软件已经充分解释或输入/质量不闭合则如实STOP。完成一次push/fetch-back精确Git/tree/blob，向用户回执STOP，不自动做原生GPU资格。

两个分支是Git准备，不是已实际发给109/174 Codex的任务。**本窗口没有node109/174运行回执**。收到任一报告即由ChatGPT独立审查该Lane；不等待另外一条，也不通过合并两分支产生新的执行authority。

## 3. 原冻结边界

- A70 M/N/O/P `SOURCE_SCOPE_NO_SURVIVOR`但非native否决；A73 W`SOURCE_INCOMPLETE`、H`SOURCE_HYPOTHESIS`；A74-C固定SM100 SFU/TC面积互换因模拟器/PPA缺口`PARKED`，不申请B200、开启SM100工程或新机制。
- GNN A61/A65/A67、Q-S/ScanNet A69、3DGS/A26、C16、AWMA、ISCAS及所有已有STOP不改变。109 GPU共享锁继续独占，但A75不使用GPU。164无新资产任务。
- 同一个模型名不使不同模型precision/权重、训练step版本、专家路由与真实输入自动等价；paper原生、paper模拟器、源码能力、CPU公式和本机原生必须分开。

**当前AI-ARCH：A75研究笔记已完成，R/D各有一条未启动Codex Goal；新GPU授权为0。**
