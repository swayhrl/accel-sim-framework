# Round A29｜3DGS硬件热度核验与非3DGS并行研究组合

**执行者：ChatGPT／AI-ARCH Discovery；日期：2026-10-14。**

**上下文起点：** `05cbf0f28843b942451417a6253c44acda14d73a`，A28、CURRENT_STATE、统一问题图谱和协调规则。写入前compare确认协调分支与该提交identical。

**范围：**公开会议/出版方/作者原文及官方文档的研究方向核验；没有运行论文代码，没有访问109/174/164或启动Codex，没有下载模型/场景、申请GPU锁、运行模拟器或新增机制。本轮仅新增研究笔记；原CURRENT_STATE的A28快照和所有执行合同保持不变。

**当前执行：**用户报告Lane M正在执行A26GR1，本窗口不做实时进程断言，不打断、重发、重启、扩预算或替换GS-Scale/真实Rubble输入。A29的候选与分工是研究建议，不是已启动的Lane任务。

## 0. 决策摘要

1. **3DGS确实是持续的硬件/体系结构研究热点。** 2024—2026正式论文已覆盖渲染、训练反向、SLAM、GPU光栅/光追单元扩展；不是只有视觉算法论文。
2. **热度不等于当前GS-Scale卸载方向已具备硬件创新性。** GS-Scale和CLM属于强软件/系统近邻；它们不能自动证明某个Gaussian Cache、预取或CPU更新机制仍有空间。
3. **保留3DGS为一个有界探索分支，不把AI-ARCH改成3DGS专线。** 总主问题继续是P01/P13：真实AI执行的瓶颈如何随工作粒度、阶段、强软件和资源配比迁移。
4. **优先并行两个非3DGS发现对象：完整MoE解码执行粒度、DiT的稀疏化/复用后资源配比。** CPU–GPU协同MoE作为与长期方向接近的第三储备，不立刻新增工程。
5. 本轮没有证明任何新机制的新颖性、性能headroom或本机可运行资格；也不要求先证明完整硬件因果，才允许以后申请小型发现实验。

## 1. 3DGS硬件论文证据：以正式来源判断热度

| 论文与发表 | 本轮来源/阅读层级 | 已有硬件方向 | 能与不能说明的事 |
|---|---|---|---|
| GSCore，ASPLOS 2024 | [会议正式摘要](https://www.asplos-conference.org/asplos2024/main-program/abstracts/index.html)、[作者机构出版记录](https://snu.elsevierpure.com/en/publications/gscore-efficient-radiance-field-rendering-via-architectural-suppo/) | Gaussian形状相交测试、分层排序、subtile skipping及专用渲染硬件；作者报告28nm综合 | 能确认体系结构论文身份；本轮未重做全文/RTL性能审计，不能转成本机结果 |
| GSArch，HPCA 2025 | [IEEE正式摘要](https://ieeexplore.ieee.org/document/10946749/) | 面向训练、反向传播和存储障碍的架构支持 | 延续A28近邻边界；本轮仍不声称取得完整原文细节 |
| GauRast，DAC 2025 | [NVIDIA作者研究页](https://research.nvidia.com/publication/2025-06_gaurast-enhancing-gpu-triangle-rasterizers-accelerate-3d-gaussian-splatting) | 扩展现有GPU triangle rasterizer支持3DGS，而非另造完全独立加速器 | 明确存在GPU集成式硬件路线；作者的SoC面积/速度结果不是RTX4080测量 |
| Cambricon-GS，HPCA 2026 | [会议正式摘要](https://2026.hpca-conf.org/details/hpca-2026-main-conference/29/Cambricon-GS-An-Accelerator-for-3D-Gaussian-Splatting-Training-with-Gaussian-Pixel-H) | Gaussian–pixel混合并行；alpha计算和混合使用不同单元并通过NoC连接 | 表明2026仍有训练专用架构工作；摘要中的加速比不跨baseline横向合并 |
| GRTX，HPCA 2026 | [会议正式摘要](https://2026.hpca-conf.org/details/hpca-2026-main-conference/106/GRTX-Efficient-Ray-Tracing-for-3D-Gaussian-Based-Rendering) | Gaussian的BVH表示与ray tracing unit遍历检查点 | 说明研究已扩到光追结构；不等于当前Accel-Sim可直接模拟RT单元 |
| Splatonic，HPCA 2026 | [会议正式摘要](https://2026.hpca-conf.org/details/hpca-2026-main-conference/24/Splatonic-Architecture-Support-for-3D-Gaussian-Splatting-SLAM-via-Sparse-Processing) | 稀疏像素采样、Gaussian并行pipeline和专用projection/aggregation架构 | 软件GPU结果与后续硬件评估是不同层；保持作者质量条件，不能当exact同工作量硬件比 |

**本轮归纳：**跨三个年份、多个独立团队与不同硬件问题，足以支持“活跃的体系结构细分热点”。这不是全领域计量统计，不推断它比LLM更热，不推断产业部署份额或投稿成功率。

## 2. 为什么选择3DGS不等于跑偏，但当前组织方式需要调整

3DGS的显式Gaussian表示、可见集合、排序/混合、训练梯度和动态状态，可作为GPU非规则工作量的合法研究对象；它不必具有Transformer或Tensor Core占主导，才属于AI-ARCH覆盖范围。[GS-Scale原文§2–4](https://arxiv.org/html/2509.15645)也说明其表示和训练过程。

必须分开三条线：

- **渲染硬件**：排序、剔除、混合、光栅/光追支持。
- **训练硬件**：反向聚合、原子访问、状态更新与片上资源。
- **训练系统**：GPU容量、host offload、CPU optimizer、通信重叠和视角调度。

**Lane M目前属于第三条的强软件后有限原生发现，不是前两条新硬件原型。** 不得把GSCore/GRTX的发表记录当作GS-Scale后“新Gaussian Cache”已有动机的证明。

[A28](AI_ARCH_A28_RUBBLE_CLM_AND_GSSCALE_TRANSFER_SOURCE_AUDIT_2026-10-14_V1.md)已经核到[CLM原文](https://arxiv.org/html/2511.04951)：CPU外观状态、camera交集复用、双缓冲、CPU Adam重叠与视角重排均有直接软件近邻。GS-Scale自己的parameter forwarding与deferred update也不是待发明机制。

因此：当前A26GR1按原边界完成一次真实应用发现；若只有软件扫描/传输冗余或没有明显目标族成本，归档即可。若发现剩余等待，再核它相对强软件的差别；不为保住3DGS方向而自动换scene、换系统、开启新训练或续Goal。

## 3. 主线重新居中：P01/P13的资源配比与瓶颈迁移

**统一研究问题：**同一AI任务在不同执行规模/阶段下，强软件选优之后，算术吞吐、寄存器/共享存储、任务供给、存储服务和CPU–GPU交接中，什么首先限制性能？是否存在可以迁移的规律和值得改变的资源组织？

至少区分两种研究：

- **固定软件的资源响应**：固定输入与实现S0，研究T(W,R,S0)。有利于定位一个明确干预的因果响应。
- **允许软件重选后的资源收益**：研究min_{S属于已评估合法候选集} T(W,R,S)。这是有限强软件集合中的最优，不是全体可能程序的数学最优。它防止新硬件只在旧映射上看起来有效。

不能把改batch、改grid、改clock或改Green Context配额全部统称为同一种物理资源扩展。涉及RF/SMEM/Tensor细节的硬件假说，需要适合的原生证据或明确范围的模型；当前不重新开启Green Context或先为工具再做若干轮资格。

[NanoFlow／OSDI2025](https://www.usenix.org/conference/osdi25/presentation/zhu-kan)已经研究同设备计算/访存/通信重叠，MPK/Tawa/Twill等也在旧轮次核过。因此“存在异构阶段”“多流可以重叠”“做持久kernel”不能作为新意。我们要找的是这些已有能力之后的具体成本。

## 4. 非3DGS候选一：完整MoE解码的有效工作粒度

### 问题

**固定自然route、精度和输出要求后，每个expert少量token的完整MoE区域，经过强软件优化仍损失多少有效执行能力？损失来自必读权重、tile浪费、阶段准备、片上状态还是任务供给？**

研究边界是router→dispatch/准备→两次expert投影与激活→combine，或者明确排除router但保留完整routed-MoE边界；不能只测一个selected expert GEMV。

### 最近邻与事实边界

[MonoMoE作者原始摘要](https://arxiv.org/abs/2609.04244)提出weight-major persistent megakernel，融合routing、top-k、量化、两次投影、激活与归约，并用H200评估。**本轮HTML正文未成功取得，机制细节限定于作者摘要。**

[FlashInfer官方fused_moe文档](https://docs.flashinfer.ai/api/fused_moe.html)的MonoMoE接口明确标SM90a/特定block-FP8形状；作者论文的模型覆盖不能自动等同当前公开接口覆盖，也不能宣称本地SM89/RTX4080已经可执行。

结论：不能从“每expert token少”直接命名新融合器，不能退回naive逐expert基线。C16旧E3自然/均匀接近的结果保持，它没有回答完整低batch routed-MoE的上述资源问题。

### 最小发现方案（尚未执行）

先从一个公开模型与最强适用后端构造一个完整operator边界，固定权重、真实激活和自然route；最多三个预选token规模。区分有用MAC、实际tile工作、准备/重排字节、完整operator时间与应用覆盖。诊断可用受控route，但自然route承担应用验证。

第一轮不做全模型formal trace、不移植Hopper专属软件到Ada、不设计dequant cache。目标族已有明显损失时，才选最有区分力的资源/软件对照；尚无完整硬件因果不阻止申请小预算发现性probe。

**停止/降级：**强合法后端已吸收现象；所谓机会只来自改route/精度；剩下仅是必读权重带宽而没有可论证的新组织；或关键平台缺失且当前不值得申请资源。

## 5. 非3DGS候选二：DiT在稀疏化/复用后的GPU资源配比

### 问题

**在固定的质量与加速策略下，DiT不同step/层的有效工作量变化，是否导致固定tile、驻留资源和矩阵/非矩阵执行组织失配？已有强kernel重选后，是否仍有值得硬件处理的成本？**

重点不是再发明跨步缓存。应研究“已有优化改变了工作量之后，硬件资源是否仍按原dense规模组织”。不同step同shape不代表必然不同瓶颈；若普通dense路径相同且稳定，这就是有效负例，不为得到正面而人为制造稀疏。

### 原文支持与直接反证

- [Cambricon-D／ISCA2024，IEEE摘要](https://ieeexplore.ieee.org/abstract/document/10609724/)已有full-network differential computing与sign-mask dataflow。
- [DiSC原文HTML](https://arxiv.org/html/2605.25798)已有cached-token reuse、attention sparsity mask reuse及针对混合dense/sparse工作的bank分配硬件；实验对象为DiT和PixArt-Sigma。**本轮读取机制与评估段；未独立复算图表或执行代码。**
- [DiTPA／ISCA2026，作者机构出版记录](https://researchportal.hkust.edu.hk/en/publications/ditpa-a-dit-based-action-planner-accelerator-exploiting-action-de/)已经将动作/去噪/多模态冗余与硬件协同，说明动作生成也有正式架构论文，但其闭环成功率和硬件评估不能等同单kernel延迟。

**本轮假说并未证明超出这些近邻；源码/全文对照要找具体遗漏能力，而不是改一个名称。**

### 最小发现方案（尚未执行）

先选择DiSC等原文中一个可追溯的DiT部署，固定checkpoint、scheduler、步数、条件和seed，选择真实去噪过程的少量step/层，比较已有强dense路径与一个固定质量约束的已有优化路径。记录完整block、表示准备/索引/重排、片上状态需求和完整sample覆盖，不把稀疏比例直接变成speedup。

正常扩散生成以随机噪声为初始输入；固定seed与真实条件是合法的生成workload。它不同于用任意随机张量替代未经验证的模型状态。分辨率变化必须处于模型合法范围；不靠复制token冒充真实高分辨率生成。

第一轮优先图像DiT；VLA动作规划仅作后续迁移方向，不同时搭建机器人闭环或新视频平台。若采用VLA，单次网络输出验证与闭环任务成功率必须分开。

**停止/降级：**收益仅来自降低质量/减少工作；现有可合法使用的kernel/算法已覆盖；剩余没有稳定的目标族成本；或可运行路径需要大规模新平台而没有明确问题支撑。

## 6. 第三储备：CPU–GPU协同MoE的资源分界

**问题：**在固定同一组expert计算和数值要求下，搬权重到GPU，与保留权重在CPU并搬激活/结果，两条路径的性能分界由哪些资源决定？强化CPU矩阵计算、host内存服务、互连或GPU驻留容量时，哪项资源先失去收益？

这与“prefill一定GPU、decode一定CPU”的静态口号不同，也不是只问如何预取专家。

[CoX-MoE原文HTML／DAC2026](https://arxiv.org/html/2605.17889)已有AMX协同、coalesced expert execution、attention/expert放置与静态热门专家分层。其动机profile使用Qwen3-30B-A3B、RTX6000 Ada、Xeon8452Y、B128/256/512、prompt512；**不能当成RTX4080低并发解码数据。**

[HiNa-MoE作者预印本摘要](https://arxiv.org/abs/2610.05123)为2026-10-04的新CPU MoE原文入口，已有AMX、NUMA和标准weight layout优化；本轮仅摘要级核验，不能据此填写未知的完整实验矩阵。

优先级：与长期CPU–GPU方向贴近，但基线/平台覆盖成本高。本轮由ChatGPT保留文献卡，不给109增加CPU/GPU任务；后续有单一可区分问题再申请小型协同实验。

## 7. 本轮拟定的并行分工：不是执行状态

| 执行者 | 科学问题与本轮交付 | 权限与依赖 |
|---|---|---|
| Lane M／109 | 原A26GR1真实Rubble/GS-Scale发现，独立完成与STOP | 用户已报告运行；完全按原合同，不接入A29新变量 |
| 拟复用Lane T／174-new | 候选一：固定完整MoE边界、核MonoMoE/适用强后端的真实能力与平台，形成一张有用工作—资源账与一个最小probe提案 | 新任务尚未启动；CPU/source-only，不等Lane M，不依赖Lane N |
| 拟复用Lane N／174-new | 候选二：选一个DiT部署，核Cambricon-D/DiSC/必要DiTPA最近邻，定位已有优化之后的一个具体资源成本，形成一张最小probe提案 | 新任务尚未启动；CPU/source-only，不做执行/模型下载 |
| ChatGPT／AI-ARCH Discovery | 保持P01/P13统一分母与独立审查，核CPU–GPU第三储备，不为所有候选同时搭工程 | 公开原文与Git只读；协调笔记不授予节点执行 |

**建议的T/N源审预算（未生效）：**每Lane最多2 CPU线程/4GiB RAM，新文本与文献≤100MiB；独立worktree/output；不import Torch、不编译GPU模块、不安装环境、不访问109/164、不运行任何GPU/模拟器/模型。当前节点资源不允许则延后，不挤占现有任务。最多一个候选、一个最小probe或明确否定结论，不再产出没有实验出口的大paper catalog。

两线同批汇报、独立裁决。一线被最近邻覆盖即可停止，不等待另一线。真正需要GPU的候选再按收益证据、执行可行性和资源增量统一排序；“研究并行”不等于同一4080并发测时。

## 8. 防止继续耗在工具和假门槛上的方法修正

1. **把论文热度、问题真实性、硬件增量分开。** 前者用公开发表证明，后两者必须用具体基线和实验回答。
2. **发现实验不要求提前完成全部oracle或单资源因果。** 先允许有真实身份、强但不必完美软件对照、有限范围的观察；资源归因是后续定位工作，不再把科学证据缺失写成必然STOP代码。
3. **评价保持三层：target kernel family、应用覆盖加权、实际end-to-end。** 不能用统一完整应用5%门槛否掉有明确目标族价值的机制；也不能只报目标kernel、不报非目标退化与开销。
4. **硬件价值不要求证明任何软件永远无法解决。** 需要证明相对强可实现软件，硬件提供有意义的性能/能耗/面积/容量或更低组织成本，并说明必要软件与硬件协同。
5. **现有平台是证据能力，不是研究空间上限。** 不能把H200新能力套到4080，也不因它不能本机直接运行就宣布方向不存在。若关键问题需要新平台，先把需求讲清楚，再决定预算；不先做漫长兼容移植。
6. **既有STOP保持。** 不重启C16选定expert访存、Split-K/dequant cache、原FFN双流、AWMA翻译、NequIP静态batch或Green Context，仅允许新的明确科学对象按独立合同进入发现。

## 9. 下一步真正应交付什么

本轮已交付公开证据核验与研究组合。下一阶段T/N各只需交付：**一个真实完整执行对象、最接近强软件/硬件能力、一个可区分解释的观察、最小输入与平台需求、否定条件**。不用等Lane M收口才开展这些互不依赖的CPU侧研究。

最终目标不是积累3DGS、MoE、DiT三个模型目录，而是选出能支撑P01/P13或另一清晰硬件问题的证据。3DGS保留探索价值，AI-ARCH主线不随当前哪项最容易下载/运行而改名。