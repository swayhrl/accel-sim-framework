# C16文献阅读笔记｜ChatGPT独立支线

维护者：ChatGPT。更新时间：2026-10-01。分支：`hrl/c16-chatgpt-literature-notes-v1`。

本支线记录原文核读、相关工作比较和待验证问题，不修改实验/Core/raw，不消费Lane4 partial。文献笔记不是实验完成证据。AWMA与C16文献分开维护。

## 当前入口：LR12

[LR12：literature-first problem map 与 C16 候选准入审查](rounds/2026-10-01_LR12_LITERATURE_FIRST_PROBLEM_MAP.md)

本轮从2025–26原始论文的实验组和反例出发，先构造问题分类，再对照C16终态八条关闭方向。审查包位于`docs/vm_tlb/review_packs/C16_PROBLEM_DISCOVERY_V2_LITERATURE_PROBLEM_MAP/`，记录来源阅读等级、实验组条件、strong software边界与问题→机制准入链。结果为`NO_NEW_LITERATURE_DRIVEN_PROBLEM_QUALIFIED`，零正式候选；异构tile-handoff仍只在future-only parking lot。所有作者artifact均未运行；本轮不授权GPU、trace、模拟或机制实验。LR11及此前轮次原文保留。

## 历史入口：LR11

[LR11：并发强基线、共享缓存上界与下一轮并行机会筛选](rounds/2026-10-01_LR11_CONCURRENCY_CACHE_BOUNDS_AND_STRONG_BASELINES.md)

本轮在FFN natural timeline与M1F headroom gate之后重新筛方向。新增关键边界：vLLM当前Qwen2已使用merged gate_up + SiluAndMul类强软件路径，因此plain gate/up merge/concurrency不能直接作为新颖性；NanoFlow/Bullet/Resonator已把intra-GPU并发调度推进到成熟systems能力。PASCAL共享缓存模型从摘要升级到正文，首次可把policy-independent residency/traffic bound作为本项目cache机制的前置oracle gate。另纳入IISWC 2026 Hopper利用率分解方法，建议在Ada W4上用既有NCU/launch证据做multi-view screen。

本轮建议并行三个CPU-only窗口：merged gate/up strong-baseline guard、PASCAL policy-independent cache-headroom screen、Ada W4 decode utilization multi-view screen。generic KV/L2 prefetch、generic concurrency、MoE expert-locality/cache、generic fusion/megakernel均因2025–2026近邻过强而不优先。没有新GPU/SASS/模拟授权。

## 历史入口：LR10

[LR10：强软件基线之后的表示转换复用与跨算子交接成本](rounds/2026-09-29_LR10_REPRESENTATION_REUSE_AND_HANDOFF_COSTS.md)

本轮重点核对Kitsune、VTC、ComFuse、StreamDQ、Multi-Scale Dequant的相关正文，以及NVIDIA Rubin官方tile级依赖触发说明。不是完整逐页复现，不运行作者artifact。PASCAL、ATLAS和Leeway全文仍未取得，不升级阅读等级。

研究判断：优先核查固定量化语义和强kernel基线后，转换结果的有限复用能否超过表示展开、带宽、同步和容量成本；异构tile交接作为第二候选。两者均是待证假设，不是已成立机制。VTC强基线反例提醒“少搬一次”可能令计算路径变慢；Rubin说明“tile-ready就启动consumer”本身已非新能力。不要重开已被grouped强基线关闭的split/cache故事。

本轮仅更新文献与问题设计。Lane6消费继续，Lane4不动，M1F full timing未授权，不启动新GPU/SASS/模拟矩阵。远端本轮研究记录提交：`89590088efe52c0a3b23fecf9c7be858f0227f01`。

## 历史入口：LR09

[LR09：Split-K、跨CTA复用、执行顺序与强基线](rounds/2026-09-29_LR09_SPLITK_LOCALITY_SCHEDULING_AND_STRONG_BASELINES.md)

[同轮补充：Tile级缓存模型、并发进度偏移与更近的研究边界](rounds/2026-09-29_LR09B_TILE_LEVEL_MODELS_AND_PHASE_DIVERGENCE.md)

两份文件合计7篇工作的相关正文：Stream-K从摘要升级；MARLIN复读；新增Stream-K++、SwizzlePerf、GPIR、TileSight及多chiplet GEMM轻量局部性模拟。另核Triton/CUTLASS官方文档、作者说明；PASCAL共享缓存模型与PPoPP2019协调tiling/batching仅摘要，不算全文。

主笔记的5篇与补充的2篇是同一轮分阶段记录，不重复计数。均未运行作者artifact。

本轮主要判断：
- Stream-K §5.2已经明确处理负载均衡与跨CTA cache复用冲突，不能将“split影响cache”本身当作新颖性。
- 当前AutoAWQ的M/Ntile映射应与经典grouped ordering对照；先看不增加split/reduction也能恢复多少复用，再判断新机制空间。
- MARLIN提示L2的有效用途取决于数据流，不一定是保留完整qweight；数值/格式不匹配的W4实现不能直接当同语义基线。
- TileSight明确建模跨M的B-tile复用，并披露deep-K下SM进度不齐导致高估命中的反例。轻量模型不能自动替代本项目平台资格。
- PASCAL: A Phase-Aware Shared-Cache Model for Parallel Scans（arXiv:2609.10515）非常接近，当前仅原始摘要；正文取得失败，优先补全文。它不同于此前推理调度Pascal。
- 本轮不改当前跨M replica实验，不授权新GPU、SASS或模拟。建议是在当前任务结束后另行冻结的研究方向。

固定代码入口：
- Triton教程：commit `ef633a550d8565a8c4cd89edce63213c8b173e2b`，`python/tutorials/03-matrix-multiplication.py`，blob `526934c1d7c60ccbb8119b1bca0e807f6fc602e8`。
- TileSight公开README：blob `803cf28984f1d1f0eaecaf2aae9822f172690343`；只核代码入口，未安装/运行，不声称RTX4080已支持或合格。
- MARLIN作者README：blob `ae24af61fed1ede9f06ca8f3b3b2985a1d93f12a`。

## 历史入口：LR08

[LR08：GPT-3的论文使用含义、权重可获取性与单卡层级研究](rounds/2026-09-28_LR08_GPT3_WORKLOAD_ACCESS_AND_SINGLE_GPU_FEASIBILITY.md)

本轮回答：GPT-3是否仍是重要研究对象；原始权重与公开结构、独立训练checkpoint、OPT代理之间怎样区分；RTX4080是否能研究175B尺寸的关键层。

新增核查：原GPT-3论文Table2.1/§2.1、LLMCompass相关正文与作者随机operand代码、NeuPIMs§8.1/Table3、MLCommons定制GPT3训练checkpoint及2025年基准替换说明、官方权重入口；FlashInfer/SpecMD只用于具体研究对象对照，不构造全领域使用率排名。

核心判断：
- 没有找到OpenAI原始GPT-3训练权重的官方公开下载；但这不妨碍构造公开尺寸的合成算子。MLPerf独立训练checkpoint、OPT与gpt-oss不是原版GPT-3。
- 175B单block主矩阵以2B/参数推算约3.375GiB，单FFN矩阵1.125GiB。完整175B则远超16GB；单层可行性与全模型可行性分开。
- 原论文包含dense/local sparse attention交替。全dense代理、修改context、TP切片都须注明，不冒充完整原模型。
- 随机张量可服务规则dense算子结构研究，不替代量化质量、真实数值分布或自然生成证据。单层自重复不代表96层不同权重的跨模型驻留。
- LR08当轮只做研究与容量推导，没有新GPU/模拟/下载。后继实验已另行派发，不能把本历史状态当作当前运行状态。

## 历史入口：LR07

[LR07：warp请求结构、临时工作区与并行度交互](rounds/2026-09-28_LR07_WARP_GEOMETRY_WORKSPACE_AND_RESOURCE_BALANCE.md)

当轮新增cuThermo、FlashDecoding++、FlashInfer、QServe的相关正文阅读；Stream-K当时仅原始摘要/作者页面，正文获取未成功（LR09已升级相关正文）。复核NVIDIA coalescing与Nsight请求层级定义；未运行作者artifact。

当轮新增问题：
- active-lane事件数量相同，不保证同warp地址合并后的sector覆盖相同。旧三lineage consumer仅做role事件和per-shard footprint；已有C16WARP1可用于新请求结构分析，不重抓trace。
- accepted split8→split1差异不仅来自删除reduction：GEMM自身的计数也改变。74MiB/14MiB等scratch allocation不是cache占用证明；下一诊断固定A/B实现，仅比较两种执行前访存状态。
- 形状适配、work-centric partition、CTA预算化workspace已有直接前例，不把通用split-K调参称为新机制。

协调位置：`hrl/c16-lr07-exploration-coordination-v1`。LR07发布时的队列状态保留于该轮正文及README历史commit `b0533583a6207a48cd4fa309e8dc4d925f20adce`；不把旧READY/QUEUED文字当成当前运行状态。

## 历史轮次

| 轮次 | 笔记 | 当轮核心增量与阅读边界 |
|---|---|---|
| LR06 | [低比特数据流与MoE时间结构](rounds/2026-09-28_LR06_LOWBIT_DATAFLOW_AND_MOE_EXPLORATION.md) | MARLIN由README升级正文；QUICK、FLUTE、SpecMD正文；MonoNN相关正文；ATLAS仅摘要。Lane5/6探索设计保留当时状态，后继结果查总账。 |
| LR05 | [五篇原文核读](rounds/2026-09-27_LR05_FIVE_PAPERS_FULLTEXT_AUDIT.md) | GPU eviction hints、DIP、RRIP、SHiP、PIPP。3/12条是特定干扰下可靠保留量，不是绝对容量；RRIP sector false-locality；PIPP参数冲突未擅自修正。 |
| LR04 | [机会成本、对象分类与全文请求](rounds/2026-09-27_LR04_OPPORTUNITY_COST_CLASSIFICATION_AND_FULLTEXT_REQUESTS.md) | Whirlpool/EVA相关正文；MLP-aware作者技术报告，不冒充最终会议稿。Leeway仅摘要。 |
| LR03 | [近邻、故事、最小强基线](rounds/2026-09-27_LR03_NEIGHBORS_STORY_STRONG_BASELINES.md) | P_all/P_stable与M1/M1F能力对照；AutoScratch functional replay与完整timing分开；APCM及cache-resident LLM相关正文。 |
| LR02 | [容量、公平、跨轮存活与效用](rounds/2026-09-27_LR02_REUSE_SURVIVAL_AND_UTILITY.md) | Talus/Vantage/AutoScratch/PRESERVE等；容量占用、旧地址存活和周期价值不是同一问题。部分工作当轮仅摘要，后续升级在对应轮次注明。 |

LR02接续历史聊天中的调研，不声称仓库存在同结构的LR01。复读、补全文、文档版本升级不重复计成新的研究工作。此前更完整的README与来源初始阅读等级保留在commit `dc41de767b55f3ba1532627f1cb5dc176ea539ee`。

## 原始来源的维护原则

原文陈述、项目事实和我们的推断分别标注。队列中的论文不计作已读；读相关章节不冒充完整逐页复核；不将技术报告冒充会议定稿；作者artifact未运行就直接注明。原论文PDF不提交仓库。

SHiP、AutoScratch-style比较和当前C16_SHIP_SW_STYLE_V1不同，必须保留具体signature/训练时点/软件region范围。CUDA官方文档不保证本项目要求的跨token地址稳定性，也没有证明真实硬件每次独立抽签。自定义对照不得冒称真实NVIDIA内部实现。

当前未闭合阅读队列：PASCAL共享缓存模型全文、Leeway全文、ATLAS全文、必要时PIPP代码/勘误。Stream-K已在LR09升级相关正文。读取论文并不自动授权实现。

## 配套数学反例

[LR02类内循环扫描反例](examples/toy_scan_counterexample.py)

这是CPU构造例子：相同边界占用不代表相同旧行存活。它不是C16 trace、CUDA实测、Talus复现或系统加速证据。

## 项目锚点与后继结果

- 早期Lane1：`4214398782159022907081dbcc36854cf21fb4b5`。
- 冻结Lane3 V1 / 本文献分支基点：`a402828860ced26124ddbf3c9d87baa6f6774d55`。
- LR07的three-lineage原始consumer：`08536be9940590be101c7f5bac2117ba82056db5`。
- LR07的split-K数据来源：`0e88faa28c9066b48e394dce657d7a16e6332a32`。
- 工作总账分支：`hrl/c16-work-history-audit-20260928-v1`；后继状态以最新已发布结果和用户派发说明为准。
- OLMoE多轮producer的协调合同：`378df585cba4c21ac5864c374976e271ae44e9a3`；其后已有独立分析，不因新文献重开旧采集。
- LR08阅读基点：`b0533583a6207a48cd4fa309e8dc4d925f20adce`。
- LR09阅读基点：`139135231fb30b4981eedb031da9c7e182269652`。
- LR09只读静态地址映射：`c72d28b17247f25d0c3613604ab6cab1737666e0`。
- LR10阅读基点：`38d4df40b615625c15d1843a69a23eb954ac0bef`。

历史笔记中的planned状态不回写成当时已经执行。所有“首次”“系统收益”“优于现有机制”主张仍需要实际比较，不由阅读数量或代码资格替代。Lane4不变；本支线不授权M1F或新的full timing simulation。
