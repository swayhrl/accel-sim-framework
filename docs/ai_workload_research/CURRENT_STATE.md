# AI-ARCH｜当前科研协调状态

**最新快照：2026-10-16 / Round A73已准备、未启动。** A70的M/N/O/P四个主流大模型源/论文Discovery全部完成并独审，都是`NO_SURVIVOR_IN_SEARCH_SCOPE / STOP`，合计0主0备、**非任何领域的GPU性能负证据**。A72已接受M且完成四线综合。鉴于单纯筛“现有软件没有实现的新功能”的方法过于容易得到4×0，A73改为**真实工作量与GPU体系结构反事实并行发现**，两条独立CPU/source Codex任务已准备，等待用户分别派发。

历史导航：[Round A72四线完全收口](https://github.com/swayhrl/accel-sim-framework/blob/adf6ab9467887f74b0b509c105977128663707a5/docs/ai_workload_research/CURRENT_STATE.md)；[Round A71三线收口](https://github.com/swayhrl/accel-sim-framework/blob/0c891b59e28177bfbff1ce6a6744a26fa6d30ad2/docs/ai_workload_research/CURRENT_STATE.md)。旧原始Goal/branch/REPORT/raw/候选不覆盖、不合并旧实验执行HEAD。

## 1. 已独立完成的A70科学证据

| Lane | 真实固定Git final/tree | 结论 |
|---|---|---|
| M／109 常规Qwen3长KV混合推理 | `f2d6324da298be26f39cda427f3e7db1a7e7031d` / `5cbb8f8eaa4fb00efcd51bc963bf68c6b3263d52` | DuetServe、Nexus、Sarathi、NanoFlow已有直接近邻，真实最新强runtime剩余wall未知，0候选 |
| N／174-new Qwen3.5混合KV/GDN | `5076223db5db0256fd0ccacec50b5347a0cab8c5` / `592e12903c8fa029fb5108a967f8a00bb9cb9458` | 混合分配和checkpoint、ReplaySSM写回已有软件反证，0候选 |
| O／109 Qwen3.5 MoE | `94ca01df352cf4cf707cd35e5f9f63d4eff014c6` / `b5b3d7f8f925c50aa845cebec2cb3057fe91b261` | MonoMoE/融合分组成熟；旧E3是Q30 Prefill expert-loop非当前fused Decode，0候选 |
| P／174-new Qwen3-VL | `f2399777a30f4fdafa26858b3cd418e497538db2` / `811616c50e4594e1884d4ee4e4c622a72fb953d1` | 视觉Graph/缓存/分离已有；公开单图局部基线不证明8B多视频端到端，0候选 |

四线固定共同Goal `8f24af162ba37b4fa37f7a18d89b0fdb62697942`；每条独立ahead1、远端HEAD identical、只增自身4文件；83条TSV/11字段各自ID唯一，CANDIDATES.json全部空，CPU/source-only、无GPU训练/模型权重下载。[A71 N/O/P独立审查](reviews/AI_ARCH_A71_A70_N_O_P_PARALLEL_DISCOVERY_INDEPENDENT_REVIEW_2026-10-16_V1.md)与**[A72 M和四线综合](reviews/AI_ARCH_A72_A70_M_AND_FOUR_LANE_DISCOVERY_SYNTHESIS_2026-10-16_V1.md)**为协调已接受范围。

M附注：Qwen3-8B BF16 2×32K逻辑KV+权重内容24.256GiB超过109的16GiB，不是可用实际峰值；首次Git fetch配置2线程实际并发未测，后收口已修正，属于初始工程资源观测缺口而非科学否决。DuetServe的H100、旧vLLM/SGLang、mean TTFT/TBT和请求吞吐与当前109实测不能互换。

## 2. A73两个独立轻量Codex任务：READY_FOR_USER_DISPATCH

**完整合同：[A73工作量与体系结构并行Goal包](goals/AI_ARCH_A73_WORKLOAD_AND_ARCHITECTURE_PARALLEL_DISCOVERY_GOAL_PACK_2026-10-16_V1.md)。两分支固定Goal启动HEAD `9afcdf6faa5b8351b56c9cbbefd3530c19c89537`，均已与远端精确回读为identical。**

| A73 Lane | 默认宿主 | 执行分支 | 主线科研交付 | 状态 |
|---|---|---|---|---|
| **W-A73** | node109新窗口 | `hrl/aiarch-a73w-mainstream-real-workload-109-v1` | 真正的主流模型真实任务、自然请求/状态/阶段分布与高质量最小对照，区分合成到达及实际prompt语义 | `READY_FOR_USER_DISPATCH` |
| **H-A73** | 174-new新窗口 | `hrl/aiarch-a73h-gpu-architecture-counterfactual-174new-v1` | ISCA/MICRO/HPCA/ASPLOS/MLSys/OSDI已发表GPU研究的具体实验组、资源反事实/强软件/应用范围与新架构问题 | `READY_FOR_USER_DISPATCH` |

- 首轮仅两条互补研究并行，不要求四窗口全部占满；每Lane单CPU worker、RSS≤2GiB、新盘≤128MiB、公开文本/PDF≤64MiB、90分钟收口，**GPU/CUDA/模型运行/模拟器/权重或数据集下载/安装/清理全部禁止**。独立worktree/output/branch，不能改协调branch或别的Lane文件。
- W交`REPORT.md`/`WORKLOAD_EVIDENCE.tsv`/`QUESTION_CARDS.json`/`RECEIPT.json`，H交`REPORT.md`/`PAPER_GROUPS.tsv`/`ARCH_QUESTION_CARDS.json`/`RECEIPT.json`。每线允许0，不强行制造机制；要求一个真实区别变量、公平成熟软件对照、最小可证伪诊断与停止条件。完毕即发布精确commit/tree/blob并STOP，不等另Lane。
- 第三个Measurement-first（暂称C-A73）仅在W或H提出具体值得回答的自然变量后，才由ChatGPT单独准备CPU静态实验资格Goal；**并非已获许可的Lane、109 GPU任务或大模型权重下载**。
- 准备/发布本Goal和创建branch**不是**已在109/174启动Codex进程。只有用户向各窗口发送明确指令并提供真实回执，状态才可从READY进入RUNNING。

## 3. 冻结、资源与审查

A61/A65/A67 GNN及A68软件反证、A69 ScanNet/Q-S低优先级、A62/A63稀疏训练储备、C16/AWMA/ISCAS各独立STOP与资源边界不变，不因A73启动恢复任何旧任务。109共享GPU `/data/c16/locks/c16_gpu_campaign.lock`沿用，但本轮不触GPU。164没有新操作授权。

协调窗口收到任何A73 Lane结果即独立抽核原文实验组与源码、核固定commit/tree、挑战软件/硬件竞争解释并更新本导航。不能将作者H100/H200/GB200结果或结构估算转成RTX4080 GPU stall/wall；不能将论文软件功能存在当成普遍零成本。

**当前A70已全部STOP；A73 W/H只已准备、未收到真实运行回执；当前本项目新增GPU执行授权为0。**
