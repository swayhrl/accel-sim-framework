# Round A14｜SM89平台物理资源轴与真实AI负载候选的可实现性筛选

**执行者：ChatGPT／AI-ARCH Discovery。日期：2026-10-13。**  
**工作范围：** GitHub固定科学证据 + NVIDIA官方CUDA/Ada/Green Context/Nsight Compute文档 + 作者官方模型/软件页的**source/design-only审计**。没有连接node109/174/164运行命令、下载权重/数据、安装CUDA/PyTorch、GPU profile、模拟器或Codex。  
**科学裁决：`SM89_RESOURCE_CONTROL_AVAILABLE_IN_DOCUMENTATION_WITH_QUALIFICATION_GAPS / TWO_CANDIDATES_SCREENED / ZERO_NATIVE_PROBES_ADMITTED / P13_HARDWARE_RESIDUAL_NOT_ESTABLISHED`。**

> 任务是核查“有没有真正可以单独控制的物理资源、真实AI输入和强软件基线”，而不是因为A13发现寄存器限制就立刻开发动态寄存器机制。保留[Round A13审查](AI_ARCH_ROUND_A13_ONCHIP_STATE_LIFETIME_STRONG_SOFTWARE_CAUSAL_AUDIT_2026-10-13_V1.md)结论：Hopper/B200作者外部kernel资源墙已证明特定条件下存在；**本地Ada SM89没有对应的原生已证瓶颈**。

## 0. 来源登记及本轮阅读深度

| ID | 来源 | 本次确认范围 / 证据类型 |
|---|---|---|
| H1 | [NVIDIA官方CUDA GPU Compute Capability设备列表](https://developer.nvidia.com/cuda/gpus)及[CUDA Guide 5.1 Table 29–32](https://docs.nvidia.com/cuda/cuda-programming-guide/05-appendices/compute-capabilities.html) | `SOURCE_SPEC`：RTX4080为CC8.9、每SM资源上限、8.x与9.0功能差异；并非本机cudaDeviceGetAttribute再次测量 |
| H2 | [NVIDIA Ada Tuning Guide](https://docs.nvidia.com/cuda/archive/13.0.0/ada-tuning-guide/index.html)和[CUDA Guide 3.2.6 L1/Shared配置](https://docs.nvidia.com/cuda/cuda-programming-guide/03-advanced/advanced-kernel-programming.html) | `SOURCE_SPEC`：Ada具有L1/shared物理共用与carveout偏好；驱动可以忽略偏好，不是孤立L1容量扩展 |
| H3 | [CUDA Green Contexts正式指南](https://docs.nvidia.com/cuda/cuda-programming-guide/04-special-topics/green-contexts.html)，[CUDA Driver API 12.4.1](https://docs.nvidia.com/cuda/archive/12.4.1/cuda-driver-api/group__CUDA__GREEN__CONTEXTS.html) | `SOURCE_API`：限制执行流可用SM集合；分区与workqueue语义及保留资源共享。该API可用于**少SM可访问预算**的敏感性试验，不改变硅片SM总数；真实109硬件/driver/PyTorch支持待门检 |
| H4 | [PyTorch CUDA Green Context文档](https://docs.pytorch.org/docs/stable/cuda)、[PyTorch GreenContext包装](https://docs.pytorch.org/docs/stable/generated/torch.cuda.green_contexts.GreenContext.html) | `SOURCE_API`：PyTorch封装标experimental、需`cuda.bindings`及PyTorch CUDA **>=12.8**；green context stream依赖需要显式同步。这**不匹配**Lane M已有`torch2.10.0+cu126`冻结执行环境；不得声称109该环境能无修改调用此封装 |
| H5 | [NVIDIA Nsight Compute官方Profiling Guide的Launch Metrics](https://docs.nvidia.com/nsight-compute/ProfilingGuide/) | `SOURCE_SPEC`：`launch__sm_count`、`launch__registers_per_thread_allocated`、`launch__shared_mem_config_size`、occupancy约束等可作为未来必要的配置/实际资源量佐证；本轮没有运行NCU，且任何NCU需新明确授权 |
| S1 | [Dao-AILab/flash-attention官方代码仓库](https://github.com/Dao-AILab/flash-attention)、[HuggingFace Qwen2模型后端文档](https://github.com/huggingface/transformers/blob/main/docs/source/en/model_doc/qwen2.md)、[Qwen官方部署说明](https://qwen.readthedocs.io/en/v2.5/inference/chat.html) | `SOFTWARE_SOURCE`：FlashAttention-2支持Ampere/Ada/Hopper的FP16/BF16；Qwen2类型已支持SDPA/FA2选择。**FlashAttention-3/4部分Hopper/Blackwell实现不能直接在SM89运行**；具体版本compatibility、JIT选择与kernel是否真正生效均未在109确认 |
| W1 | [Qwen/Qwen2.5-0.5B-Instruct模型页](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct)及[固定config快照`c89bee90d9f811437d9735454613c35b4a3c4dc8`](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct/blob/c89bee90d9f811437d9735454613c35b4a3c4dc8/config.json) | `OFFICIAL_MODEL_CARD/CONFIG_ONLY`：公开真实0.49B参数、24层、Q14/KV2、hidden896、head_dim=64、BF16配置及Apache2授权，属于**可继续验证的自然预训练模型候选**；本轮未核任何权重safetensors SHA、tokenizer文件hash、自然数据snapshot或本机实际工作集 |
| W2 | [A11独立接受的Lane M V1R1原生](../reviews/AI_ARCH_ROUND_A11_LANE_M_T_JOINT_INDEPENDENT_REVIEW_2026-10-13_V1.md)、[A12交叉复核](AI_ARCH_ROUND_A12_CROSS_WORKLOAD_GRAIN_RESOURCE_IDENTIFIABILITY_2026-10-13_V1.md) | `ACCEPTED_NATIVE_WITH_SCOPE`：OAM-S 32 Si结构、GPU C2/G2/G4/G8数值/完整wall有范围PASS；未取得SM资源受控干预。C16 Grouped Split-K已有软件反转，不应因新SM quota API重写其老STOP |

**没有下载并实际执行以上任何软件新版本**；文献/源码可用性不等于node109实机资格。RTX4080在先前Lane M原生执行收据中为SM89，driver 580.178.04，已装torch2.10+cu126；这些身份来自冻结执行报告，而不是本轮现场检查。

## 1. 先区分“SM89物理上有哪些资源”与“究竟能合法改变哪一种资源”

| SM89特征 | 由官方原始规范能确认的事实 | 可否用于当前P13严格单变量实验 |
|---|---|---|
| 通用寄存器 | **64K个32-bit register/SM**，单线程最大255，单CTA最多64K；SM89同时驻留上限48 warps、1536线程 | 说明register/occupancy约束存在，不提供“在同SM89上只增加总RF容量”的软件API；`maxrregcount`之类改变分配、spill与编译而非物理RF |
| 共享存储 | 每SM最高**100KiB**（100 KB按文档1024计），单CTA约99KiB；静态48KiB以上需要动态SMEM/opt-in | 改tile/blockSMEM会同时改变算法和占用；不可声称硬件容量变大 |
| L1/shared共用 | 统一data cache **128KiB**，可选共享存储配置`0/8/16/32/64/100KiB` | `cudaFuncAttributePreferredSharedMemoryCarveout`是**驱动提示**，真实结果与实际SMEM容量、可用L1会耦合；改变carveout不是仅扩L1或仅扩SMEM，若driver不调整配置则无有效干预 |
| 异步搬运/动态reg | SM89属于8.x，有支持的`memcpy_async`及barrier能力，但没有SM90的TMA/WGMMA与`setmaxnreg`软件目标 | 不能称SM89没有全部异步搬运；也不能把Tawa/Twill Hopper内核直接移植为同指令的Ada真实对照 |
| Green Contexts SM配额 | CUDA Driver API自12.4已有SM resource split/context功能；官方compute capability表把Green Context资源量列入现有架构能力。Green Context启动流只能访问获配SM | 是**改变“可用SM数量/访问配额”**的受控API，不是修改物理SM总数；被分走SM同时意味着关联register/SMEM/计算能力一起减少，L2/DRAM/CPU仍共用。不能从SM减少的时间比直接预测未来更多物理SM或某个单独寄存器容量 |
| 强PyTorch集成 | PyTorch GreenContext包装明确要求**CUDA>=12.8**、experimental与cuda.bindings；作者文档警告非自动跨stream依赖 | 109旧冻结torch **cu126不达这个包装入口的要求**；可研究CUDA Driver API低层合法性，但不能偷偷升级Lane M环境/驱动或修改已接收A9结果 |

**方法警告**：单CUDA设备上缩小SM供给同时缩小一组以SM为单位的硬件资源，严格地说是一个“SM配额轴”而非纯算力/寄存器/共享存储单轴。即使将来形成真实配额—时间曲线，也只能证明**同设备不同可用SM配额**的受控响应。共享L2/DRAM、worker分配/上下文调度、kernel选择及操作形状均需要检查；它既不是Silicon physical SM-scaling实验，也不自动是新GPU架构机制。

## 2. 候选一 C14-01｜现有OAM-S天然语义完整的SM配额敏感性（低成本、低论文headroom）

**动机**：选择已有被A11接受的真正原生模型、Si几何与数值、编译产物，比重新准备一个模型/自然token更省身份工程。科学对象依旧是B8完成固定32帧的`energy+forces+stress`，完整wall已在109报告**7.602ms**；事后instrumented model-event约2.383ms、GPU构图event约4.139ms，**不同诊断时钟/采样不可相加为关键路径**。

**有资格的部分**：

- 源码可用单GPU Ada，真实模型字节、输入几何、图多重边/数值基线及同compiled OEQ产物曾被接受；`alchemiops`及OEQ路径用GPU运行的能力已得到原生证明。
- 若一种**确实在该GPU上可用**的SM配额流接管全部必要GPU操作而不绕过图/数据/模型，保持同精度/工作量/输出/compiled model，只改变实际可用SM配额，就能形成**有条件的SM配额敏感性**。至少要返回actual provisioned SM count及正确性身份，不能只给请求百分比。

**无法借用前轮PASS的内容**：

- 当前`torch2.10+cu126`与PyTorch `green_contexts`要求不符；Driver API接管NequIP AOT、Warp/ALCHEMI自管GPU流、独立缓存/编译产物、tensor依赖能否合法一致**未核实**。不得复用旧runner并自行注入Context把该功能算成“已兼容”。
- 上次未测真实GPU SM/reg occupancy、warp ready/stall、DRAM和L1/L2压力，没有证明其受SM数量限制。很小的模型或大量构图/host链路开销可能导致SM缩额仍不改变完整wall；或只造成任意可工作的任务被资源削减后减速。
- 只减少已存SM，不提供“再增加SM会有多少收益”的上界。单个静态32帧重复样本不代表自然时序/多模型规律。

**分类**：`NATIVE_MODEL_INPUT_ALREADY_QUALIFIED / SM_QUOTA_API_COMPATIBILITY_UNKNOWN / HARDWARE_RESIDUAL_NOT_DEMONSTRATED / LOW_PAPER_PRIORITY / NO_GPU_PROBE_ADMITTED`。  
**STOP**：如需要修改OAM-S内部计算/语义、创建无法验证的自定义backend或绕过现有GPU锁才能切Context，则不执行；即使经合法配额产生减速也只能说明该执行对**减少SM**敏感，不足以晋升新SM扩容机制。

## 3. 候选二 C14-02｜公开Qwen2.5-0.5B真实Attention的SM配额／片上状态响应（高关联性、更高资格缺口）

**为什么选它（不是因为目前资产有它）**：用户研究目标为单卡边缘AI任务执行资源；选择原作者有公开真实权重模型、较小的0.49B并带真实GQA/长上下文注意力，减少相较未授权的352B分布式模型的模型/环境门槛。其主张是**候选软件可实现性**，而非RTX4080已运行或已测headroom。

- 固定模型源页有24层、hidden896、Q14/KV2、BF16、最大32,768上下文、Apache2；`head_dim=896/14=64`是配置导出的数学事实。所核snapshot只验证`config.json`，**没有锁定整库权重/Tokenizer hash或自然prompt/token序列，也没有获取授权下载**。
- 强软件：Qwen2已有Transformers内的`sdpa`与`flash_attention_2`，FA2官方声明Ampere/Ada/Hopper FP16/BF16合法。单GPU试验前必须固定PyTorch/Transformers/FA2具体版本和实际backend（包括是否发生fallback、Graph、JIT与共享缓存身份）；**不能用PyTorch eager手搓attention作为唯一强对照**。
- 因果对象：同模型、权重、自然已固定token IDs、KV/sequence长度、输出和数值约束下，比较每一强软件后端在**同一种资源配额**下的完整prefill或decode wall与attention子段；记录最佳合法`T_best(R)`和固定单策略`T(R,S)`两套前沿，**但它们只有在CUDA正确可控R及原生任务均合格后才有意义**。
- 不能把`SDPA`在所有形状上强行指定为不同算法：PyTorch SDPA可能本来就调用Flash Attention；需要真实kernel identity去重。也不因Qwen模型较小就凭参数量断言16GiB上的实际prefill/decode batch、KV、编译与缓存余量PASS。
- 若考虑L1/shared carveout，它会同时改变两个容量、驱动可能只给hint且FA2的kernel配置不一定允许外部设置；即使改变完整wall，也不是寄存器容量单变量。除非能证明实际`launch__shared_mem_config_size`变化且同数学算子、同数值/compiled kernel保持，否则不能纳入有效资源A/B。

**分类**：`PUBLIC_MODEL_AND_STRONG_ADA_SOFTWARE_SOURCE_SUPPORTED / RAW_TOKEN_AND_WEIGHT_IDENTITY_MISSING / 109_NATIVE_FIT_UNKNOWN / EFFECTIVE_SM_QUOTA_UNVERIFIED / CANDIDATE_FOR_FUTURE_CONTRACT_ONLY`。  
**STOP**：若完整固定自然token/权重身份或强FA2/SDPA在设备上不兼容、没有真正不同的合法软件方案、真实输出数值不闭合、SM配额改变带来额外kernel/stream切换，则不构造假对照。不要下载模型或实际执行来填补本source阶段缺口。

## 4. 负面控制：为什么不把原C16与“Carveout敏感”直接立项？

- C16 Grouped W4 Split-K：原生数据显示M1→M64时Split8优势从约2.27×缩小并反转；切换split同时改K分解、CTA、reduction和额外流量，其软件强对照已能解释部分现象。没有真实固定模型全请求与仅改变SM数量的同分母证据，故**不从其旧软件分解效果再生新hardware Goal**。
- M中实际G2慢于C2、G8快于G2：不能靠强制L1偏好改变来获得新的逻辑观测“调用次数减少”，更不能从图构图诊断推某个L1命中率头寸。
- 无NVIDIA提供的“仅放大RTX4080物理register file并保持其它系统完全不变”API。`cudaFuncSetAttribute(MaxDynamicSharedMemorySize)`、`maxrregcount`、SMEM carveout、SM partition都不满足该等价性。任何未来模拟`×2 RF`仅为冻结校准模型的反事实，需新模拟器资格，不能借当前Ada原生结果“免费”实现。

## 5. 科研裁决：当前平台**有文档层的SM配额旋钮，但没有科学已准入的物理资源候选**

| 资格门 | C14-01 OAM-S | C14-02 Qwen attention |
|---|---|---|
| 真实模型/输入字节identity +数值 | **已有范围内PASS** | 公共源码/配置已证，权重/token/数值**未取得** |
| 强软件与完整wall | **已有范围内PASS**，G8仅四臂最优 | SDPA/FA2源码支持，具体109路径**未执行** |
| GPU/driver可操作的单R | Driver GreenCtx可能，但PyTorch封装旧cu126不符，实际配额/stream尚未检查 | 同左，且backend融合路径更复杂 |
| 与现有软件不同的硬件剩余 | **没有证明** | **没有证明** |
| 跨family论文可推广性 | 仅固定Si32帧，静态非MD | 潜在自然LLM，但尚无独立token bank |
| **当前科学决策** | `PARKED_LOW_HEADROOM` | `PARKED_IDENTITY_AND_PLATFORM` |

**相对A13的新进展是方法可行性，而不是新headroom**：官方CUDA/GreenCtx提示，不必因RTX4080没有Hopper`setmaxnreg`就宣布本地**所有**P13资源分析不可做；可以研究**减少可用SM配额**的真实响应。但既有软件/模型必须全部正确迁移到受控Context，强软件基线选优且实际运行门需独立通过。因物理SM总数未变，任何“额外SM可加速多少”的外推也需另行校准，不能以缩减配额曲线直接线性外插。两个候选都**不获本轮新GPU或模拟器授权**。

**若要高质量论文问题，还需独立证明**：最强合法软件后有稳定、对完整应用可观的实际延迟残余；这一残余与物理资源的因果边界能够区分异步任务就绪、工作量几何、launch/JIT/Graph差异及共享L2/DRAM服务；且存在跨独立输入的真实负载族响应。当前证据缺这些门，无法宣称发现未解决硬件机制。

## 6. 后续最短路径（非执行授权）

### Round A15建议｜单旋钮硬件可辨识性的实现资格与模型任务收敛（执行者：ChatGPT／AI-ARCH Discovery）

不建议立刻扩SMED/FA2、下载Qwen或再对NequIP加B16。若继续同一source-only研究，先确认一次**不动109的低层CUDA Driver Green Context文档契约与PyTorch已安装cu126的接口断层**，并从作者代码查独立GPU stream对ALCHEMI/OEQ/FA2的兼容要求。执行资格若必须改动109的完整安装环境、依赖或旧A9缓存，则返回`PLATFORM_UNQUALIFIED`，不上GPU。**本轮资料已足以把运行门列清楚；进一步API与driver真实行为，最终仍需要新明确GPU授权的小型canary。**

若未来需发执行Goal，建议按以下固定门分层，而非立刻做144样本新campaign：

1. **SCIENTIFIC_IDENTITY**：选C14-01已有Si full outputs，或另行合法冻结Qwen权重/token/强backend；只选一个，冻结正确性和执行时间分母。
2. **PLATFORM_SM_QUOTA**：先非阻塞共享锁与低预算API查询确认设备实际GreenCtx可用/实际配额，再同stream输出数值与kernel身份；受影响与未受影响核要分开。不同架构或CUDA版本必须另作限定，不能顺手升级全局环境。
3. **SM_ONLY_LIMITED_SCOPE**：正式未插桩比较`T(W,R,S)`与重选优`T_best(W,R)`，同时记录共享L2/DRAM与CPU准备；若软件策略已吸收或响应仅在缩减SM的极端配额成立，就归档为`SCOPED_SM_BUDGET_SENSITIVITY`，不提出新的RF/Cache机制。
4. **PAPER_GATE**：需要跨负载和独立样本、面积功耗与实现成本、已存在GreenCtx/Bullet/MPK等强近邻对照。失败或不具真实可解释资源轴则`STOP`。

**允许的当前操作**：仅本ChatGPT继续做公开源码/文献核查与协调笔记更新。**未授权**109 GPU/新CUDA内核/依赖安装、174模拟器、NSYS/NCU/NVBit、C16/AWMA恢复、模型权重下载/holdout、新硬件或新Codex Goal。

**最终`ROUND_A14_TWO_WORKLOADS_SCREENED / API_LEVEL_SM_QUOTA_PATH_FOUND / NO_NATIVE_HARDWARE_ADMISSION`。**
