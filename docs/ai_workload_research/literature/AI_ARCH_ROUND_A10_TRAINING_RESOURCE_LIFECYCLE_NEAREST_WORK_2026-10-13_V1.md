# Round A10｜训练激活生命周期中的资源迁移：最近邻原文证据与P13资格

**执行者：ChatGPT／AI-ARCH Discovery（原始来源、因果归纳）；并行预备：Codex Lane P／174-new CPU-source-only。**  
**日期：2026-10-13。类型：PAPER_AUTHOR / SOURCE_CODE / OUR_INFERENCE；无本机GPU、模拟器、训练、下载或新机制。**

## 0. 当前发现

1. 训练中激活的保存、重计算和CPU卸载已经有**成熟图编译器和带有现实模型的多GPU native测试**，因此不能把“按tensor动态选择卸载”直接当新架构创新。
2. 新的[SlackSwap 2026-10-09 arXiv 2610.13003v1](https://arxiv.org/abs/2610.13003)明确把host-link的可重叠时间作为有限预算；其摘要提到A100 **trace-driven模拟**的1.10–1.11×，与TorchTitan **8×H100真实训练**属于不同证据等级、不同模型/硬件/软件对照。**本轮无法获取SlackSwap的全文PDF/HTML，仅核作者原始arXiv摘要；未按Table/Figure把它算作“全文实验组精读”。**
3. 当前[TorchTitan源码快照`8a75afd90773fe410340e0709b0b1af427c4af58`](https://github.com/pytorch/torchtitan/tree/8a75afd90773fe410340e0709b0b1af427c4af58)除了`sac_and_offload`，还有**MoE`sac_and_paged_stash`**（原代码说是移植自Megatron-Core 0.19.0）；后者针对静态capacity-padded activations/动态live rows和pipeline寿命，**默认CPU spill factor=0**，不能混成普通CPU卸载，也不能当无人提出的新机制。
4. P13值得继续考察的是“**同一软件策略固定时的资源响应**”与“**各硬件条件下强软件重新选优后的资源响应**”的区别，而非只换batch/预算就声称物理SM、PCIe带宽或者HBM容量已单变量放大。本轮保留问题卡，**0项新109 native授权**。

## 1. 固定来源登记（严格区分阅读深度）

| ID | 原始固定源 | 本轮真正阅读范围 | 证据级别与限制 |
|---|---|---|---|
| T10-D | [PyTorch Graph-based CPU Offloading作者DevLog](https://docs.pytorch.org/devlogs/distributed/2026-06-23-cpu-offloading/)，2026-06-23；[固定Markdown源码`pytorch/devlogs@74462e4bd312dbd9763358dc528968754b7bc536`](https://github.com/pytorch/devlogs/blob/74462e4bd312dbd9763358dc528968754b7bc536/content/distributed/2026-06-23-cpu-offloading.md)，blob `223b3655bb695767d46bdf3014426ee86f6c9b36` | 全文文本、图题及文字结果；未按图像像素反算全部曲线，也没有下载训练artifact | `AUTHOR_TECH_REPORT_NATIVE_8_H100`；不是论文正式camera-ready，不是本地109 |
| T10-S | [SlackSwap `arXiv:2610.13003v1`](https://arxiv.org/abs/2610.13003)，Hui Feng、Xun Zhou、Yuxin Wang，2026-10-09 | **原始arXiv摘要**，无可访问PDF/HTML；未核各图、参数、输入bank或对照代码 | `PAPER_AUTHOR_ABSTRACT / TRACE_DRIVEN_SIMULATION`；全文所有未看字段为`未核实`，不把摘要结果当1080/4080原生测量 |
| T10-C | [pytorch/torchtitan@`8a75afd90773fe410340e0709b0b1af427c4af58`](https://github.com/pytorch/torchtitan/tree/8a75afd90773fe410340e0709b0b1af427c4af58) | 固定源码`experiments/graph_trainer/{README.md,configs.py,memory_policy.py,cpu_offload.py,paged_stash_memory_policy.py}`的关键说明与符号；核部分路径/注释 | `SOURCE_CODE`，是2026-10-13选定公开快照；**不能宣称等同T10-D于6月跑实验的具体commit**，没有执行 |
| T10-A6 | [TorchTitan v3／SimpleFSDP v2已审原始论文组](AI_ARCH_ROUND_A6_NEQUIP_PATH_AND_PUBLIC_TRAINING_2026-10-13_V1.md) | 仅复用A6已经核的T1–T4控制表、不重复深读 | `PREVIOUS_SCOPED_AUDIT`；分布式H100不能投射单4080 |
| T10-BASE | [PyTorch 2025 activation checkpointing官方方法综述](https://pytorch.org/blog/activation-checkpointing-techniques/) | 只读官方已提供的SAC与memory-budget接口背景 | `OFFICIAL_TECH_GUIDANCE`；**无本机资源响应** |

上述英文`native`表示作者的外部机器真实系统实验，非AI-ARCH独立运行。网页源文章/图表未披露或未从源码精确核对的字段直接标`未披露/未核实`。

## 2. T10-D：按原始实验组，不混淆分母

作者声明：所有以下运行在**8×H100、单GPU 96GB**环境；工作围绕TorchTitan graph_trainer traced joint forward/backward。文中的吞吐为训练TPS，不是单个offload CUDA kernel加速，也不是训练至收敛时间；文章没有逐实验列出可复现的数据集snapshot、sample IDs和token bank。

| 组/位置 | 实际对象/控制变量 | 作者报告的可用结果 | 不能推出 |
|---|---|---|---|
| D1，总览与tradeoff | Llama3 8B、Qwen3 14B；同族模型的activation offload budget变化 | dense模型可用近10% GPU peak-memory节省换不到1%的吞吐下降；更激进时Llama3约33%、Qwen3约38%节省对应约20%吞吐牺牲 | 两模型点不一定同batch/shape；不能当单变量计算资源或PCIe带宽扩展 |
| D2，Llama3 8B budget/defer | 作者给defer=8、bs=1、seq=8192；改变offload budget | 约10→12GB预算区间，多省约0.46GiB peak memory，同时TPS低约60–70（作者文字给数）；出现局部cliff | 未从图读取误差棒/独立seed；不证明“GPU内存带宽耗尽”或普遍12GB阈值 |
| D3，Qwen3 14B预算 | bs=4、seq=4096；改变budget | 所核范围未出现Llama式cliff；已卸载273/351个tensor、28.8GB数据；图展示不同time/memory前沿 | 不能把D2/D3之间差异唯一归到模型结构；bs、seq也不同 |
| D4，DeepSeek V3（DSv3） | 作者称使用8-way expert parallel；调defer；MoE更少可被offload的激活 | 129/335个tensor、6.8GB；defer>=3时24%+ overhead或NCCL timeout；作者未绘budget曲线（称变化很小） | 是否完整671B模型或训练数据token身份**未核实**；timeout不是硬件带宽服务“负例” |
| D5，view replay消融 | 同一Llama8B，offload view-base与不处理view | 最大peak memory savings由约4%增至33% | 是软件数据别名合法化能力，不是硬件cache加速 |
| D6，pinned pool消融 | 复用host pinned buffers vs逐tensor分配 | 作者说开销约50%→22%，此前155 tensors的cudaHostAlloc累积代价可观 | 该比例是特定环境/配置，不是“所有PCIe传输都能免费被隐藏” |
| D7，seq长度对照 | 作者报告seq8192 vs4096时overhead 20.3% vs23.9% | 更长序列可以提供不同计算/拷贝重叠窗口 | 同时改变计算量、激活字节及kernel形状；不能只归到slack增加 |

作者说明通过具体数值检查验证transformation bitwise identical，但本文没有公开逐步checkpoint/完整梯度reference，因此`PAPER_AUTHOR_NUMERIC_CLAIM`不等于本研究已有可执行numerical contract。

**主机链路口径的特殊警示：** 博客在段落中称“PCIe 300GB/s”，但现有固定TorchTitan`cpu_offload.py`源码的NUMA注释明确以**GB200 NVLink-C2C**为例（local约350GB/s、cross-NUMA约120GB/s）；作者所指设备互连的精确归属尚未由本轮实机资产核实。不能将300GB/s改写为一般PCIe带宽，更**不能继承为node109 RTX4080**的host-link指标。

## 3. T10-S：SlackSwap是直接最近邻，但全文未核

- **作者在摘要中明确提出的难题**：compute扩展相对host-link增速更快，传统无link-time预算的swap容易在PCIe上阻塞；checkpointing保守时主机链路可能闲置。
- **作者方法（摘要级）**：用一次profile估计每tensor重算成本与可重叠传输预算，先把host-link预算分给重算最昂贵的激活；剩余容量短缺用重算解决；FIFO offload＋EDF prefetch，减少同步屏障。
- **实验组S-ABS**：BERT-Large、GPT-2 XL、Llama-7B-style，A100，**trace-driven simulation**。作者摘要给“激活内存一半时保持unlimited-memory吞吐的96–100%”及“相对选定最优baseline 1.10–1.11×”；6,600–14,000组候选计划的genetic search差<0.5%，计划生成<0.4s。这些数字**来自摘要**；具体训练token、optimizer、profile原始数据、baseline实现、GPU时间/图表现、统计显著性和artifact均`未核实`。
- **不可合并**：SlackSwap的模拟器时间/基线不等于T10-D作者H100系统的wall；二者比较只支持“同一科学问题已有强最近邻”，不支持“某一方案本机优于另一个”。

如后续取得SlackSwap全文/代码，应对照真实实验组补证据，而不是用摘要内容填Table图。此方向不需要现在就获取作者所有训练数据或运行代码。

## 4. 源码新近邻：保存/重算/CPU卸载与MoE paged stash不是同一个对象

T10-C固定源码中`GraphTrainerCompileConfig.memory_policy`有`none/default/full/eager/min_cut/sac_and_offload/sac_and_paged_stash`，并有显式`cpu_offload_budget_gb`、`cpu_offload_defer_n_layers`和`cpu_offload_prefetch_n_layers`。

- **普通SAC**：按node内的算子种类和跨layer依赖做`MUST_SAVE`或重算，已能按tensor而非整block选择。
- **SAC+CPU offload**：`MUST_SAVE`中选部分tensor经`ao::offload/reload/wait_tensor`，带事件依赖和视图合法化。这里的关键预算有HBM减少、host pinned memory、link字节、额外forward等待和backward就绪；不再是“没有异步offload软件”。
- **SAC+MoE paged stash**：当前代码说明来自**Megatron-Core 0.19.0**。对**有静态capacity factor的MoE token dispatch**中allocated worst-case padded activation，仅保存实际live rows到共享page pool，避免层数×capacity padding；默认`buffer_size_factor_cpu=0.0`，**不是普通host offload**。其使用示例为round-robin debug routing，不是自然输入路由的代表实测。
- **overflow和算法身份**：`paged_stash.overflow_check=deferred`在overrun时异步标志、保留参数/优化器状态，但让数据step和LR进度继续；blocking模式可同步检测并重新跑一轮。两种属于明确的运行与数值/收敛契约，不可把它们假定成透明零开销优化，也不能用debug合成路由得到自然MoE容量结论。

因此，“为MoE容量填充做shared pages”“对激活做async offload和prefetch”都已有代码/论文强近邻。硬件方向若重新提出，必须先说明**相对于这些现成实现仍有何可消除的资源服务或时间残余**。

## 5. 科学推导：如何真正辨识P01/P13而不是调软件参数

记同一训练步的`B_copy`为host-link实际双向字节，`W_overlap`为可覆盖拷贝的计算/调度窗口，`R_host`为目标硬件/部署下有效拷贝服务率。条件量`B_copy/R_host <= W_overlap`**只是乐观的隐藏可行性必要条件之一**，实际还受传输发起延迟、拓扑/NUMA、D2H/H2D双向争用、kernel同步、pin内存预算、CUDA Graph和动态ready限制；不是硬件预测值。

两个不同的对照不得混合：

1. **固定软件策略的资源响应**：保持相同训练语义、模型输入、memory policy、tensor selection和prefetch/defer不变，改变真正可验证的硬件资源（有可靠instrumentation的物理设备/受校准的资源模型），测wall/peak/time-to-valid-step变化，才接近P13硬件响应。
2. **给每一资源配置重新找最佳强软件策略后的响应**：不同硬件条件下允许policy重优化，记录其参数、容量约束与完整时间。这个上包络/最优前沿与1不同，更接近“软件已调优后的剩余硬件价值”。

直接在同一GPU改`offload_budget_gb`或seq/B而看到cliff，是**P01软件策略/负载响应**，而不是直接测得“扩SM/扩PCIe”的物理反事实。更换GPU型号会同时改变算力、HBM/PCIe/NVLink、容量、软件最优kernel及导出产物，也不是单变量干预。

**优先科研假设Q-T10-R（待资格）：** 经过强SAC+graph offload以及动态prefetch，随合法训练工作量/资源的变化，剩余时间损失是否由**host-link饱和**、**依赖ready窗口不足**还是**GPU算术重算成本**主导？三个解释需要分别的传输字节与time、实际recompute FLOPs/time、完整train-step wall和HBM峰值；缺任一不可归因。近邻已覆盖一般算法，**不晋升新硬件机制**。

**最低成本反证（不执行GPU）：** 若源码发现配置已支持所需数据流/时间窗，且作者在最接近的真实模式已消除对应成本，则只做科学去重；若没有合法自然输入/小规模可执行的单GPU同语义model+policy pair，记`NO_VALID_TRAINING_PAIR`并STOP。不能靠用debug model/随机fake tokens替代真实学习负载来制造收益。

## 6. 并行任务与审查顺序

- **ChatGPT本轮已经完成**：T10-D原文按7组审查，T10-S原始摘要（全文不可得）和T10-C固定源码的最低限度因果对照，并写入此报告。它**不是**174工作的预先结果，也不代表新GPU任务资格。
- **Codex Lane P／174-new**：依据[单独源审Goal](../goals/AI_ARCH_A10_TRAINING_LIFECYCLE_SOURCE_AUDIT_174NEW_V1.md)，只核具体GraphTrainer成熟源码、公开训练对象与小规模自然输入的可行性，产出一份**独立branch**的source-only审查，不同于ChatGPT本轮的跨作者论文因果对照。需要在真实174 Codex新窗口由用户发送指令才能启动，本ChatGPT只有GitHub准备权限；不得称自动后台运行。
- **Codex Lane M／109**：用户表示V1R1正在执行中；不干预其GPU进程、锁、cache、模型身份、数值门或改变Goal。Lane P不在109运行任何任务，也不以此文献分析触发其追加诊断。
- **回收点**：Lane P若发布固定commit，本窗口独立对照其source级资格再收口Q-T10-R；Lane M完成后独立按原V1R1合同审科学。两条可能有独立结果，**不必互相等待或互相授权**。

**本轮裁决：`TRAINING_LIFECYCLE_STRONG_SOFTWARE_EVIDENCE_GROUNDED / NO_NEW_GPU_ADMISSION / NO_MECHANISM_PROMOTION`**。

## 7. 后续最短路径

1. 在174启动Lane P（仅CPU源码≤10文件），等待其唯一报告并审其自然输入/数值合法性，**不扩大为数十篇论文综述**。
2. Lane M 109结果自然返回后另起独立审查。不能因为它在运行就发状态询问/重启命令。
3. 如果Lane P给出真正同语义、强软件、资源可测的训练pair，才另写单独GPU discovery候选及预算、征求许可；如无，则`PARKED_NEAR_NEIGHBOR`，保留作者有范围的瓶颈，不重复搭offload框架。

本次不是AWMA R27R3、C16 Stage A、DTC-L1的一部分；原STOP、持久raw与共享GPU资源锁保持。
