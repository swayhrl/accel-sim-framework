# C16文献阅读笔记｜ChatGPT独立支线

维护者：ChatGPT。更新时间：2026-09-28。分支：`hrl/c16-chatgpt-literature-notes-v1`。

本支线记录原文核读、相关工作比较和待验证问题，不修改实验/Core/raw，不消费Lane4 partial。文献笔记不是实验完成证据。AWMA与C16文献分开维护。

## 当前入口：LR07

[LR07：warp请求结构、临时工作区与并行度交互](rounds/2026-09-28_LR07_WARP_GEOMETRY_WORKSPACE_AND_RESOURCE_BALANCE.md)

本轮新增cuThermo、FlashDecoding++、FlashInfer、QServe的**相关正文阅读**；Stream-K仅原始摘要/作者页面，正文获取未成功。复核NVIDIA coalescing与Nsight请求层级定义；未运行任何作者artifact。

新增问题：

- active-lane事件数量相同，不保证同warp地址合并后的sector覆盖相同。旧三lineage consumer仅做role事件和per-shard footprint；已有C16WARP1可用于新请求结构分析，不重抓trace。
- accepted split8→split1差异不仅来自删除reduction：GEMM自身的计数也改变。74MiB/14MiB等scratch allocation不是cache占用证明；下一诊断固定A/B实现，仅比较两种执行前访存状态。
- 形状适配、work-centric partition、CTA预算化workspace已有直接前例，不把通用split-K调参称为新机制。

下发位置：`hrl/c16-lr07-exploration-coordination-v1`。

| 任务 | 节点/窗口 | 当前记录状态 |
|---|---|---|
| Warp request geometry screen | 174-new / 新Lane8，CPU-only | READY_TO_DISPATCH；没有新结果 |
| Split-K × cache-state diagnostic | 109 / Lane7，必须GPU锁 | QUEUED_NOT_STARTED；只能在当前OLMoE任务完成并释放锁后执行 |

Lane4不变；本轮没有授权M1F或新的full timing simulation。

## 历史轮次

| 轮次 | 笔记 | 当轮核心增量与阅读边界 |
|---|---|---|
| LR06 | [低比特数据流与MoE时间结构](rounds/2026-09-28_LR06_LOWBIT_DATAFLOW_AND_MOE_EXPLORATION.md) | MARLIN由README升级正文；QUICK、FLUTE、SpecMD正文；MonoNN相关正文；ATLAS仅摘要。Lane5/6探索设计保留当时状态，后继结果查总账。 |
| LR05 | [五篇原文核读](rounds/2026-09-27_LR05_FIVE_PAPERS_FULLTEXT_AUDIT.md) | GPU eviction hints、DIP、RRIP、SHiP、PIPP。3/12条是特定干扰下可靠保留量，不是绝对容量；RRIP sector false-locality；PIPP参数冲突未擅自修正。 |
| LR04 | [机会成本、对象分类与全文请求](rounds/2026-09-27_LR04_OPPORTUNITY_COST_CLASSIFICATION_AND_FULLTEXT_REQUESTS.md) | Whirlpool/EVA相关正文；MLP-aware作者技术报告，不冒充最终会议稿。Leeway仅摘要。 |
| LR03 | [近邻、故事、最小强基线](rounds/2026-09-27_LR03_NEIGHBORS_STORY_STRONG_BASELINES.md) | P_all/P_stable与M1/M1F能力对照；AutoScratch functional replay与完整timing分开；APCM及cache-resident LLM相关正文。 |
| LR02 | [容量、公平、跨轮存活与效用](rounds/2026-09-27_LR02_REUSE_SURVIVAL_AND_UTILITY.md) | Talus/Vantage/AutoScratch/PRESERVE等；容量占用、旧地址存活和周期价值不是同一问题。部分工作当轮仅摘要，后续升级在对应轮次注明。 |

LR02接续历史聊天中的调研，不声称仓库存在同结构的LR01。复读、补全文、文档版本升级不重复计成新的研究工作。

本次仅重整README入口；LR02–LR06正文没有改写。此前完整README及来源初始阅读等级保留在commit `dc41de767b55f3ba1532627f1cb5dc176ea539ee`的同一路径，可用`git show`查看。

## 原始来源的维护原则

原文陈述、项目事实和我们的推断分别标注。队列中的论文不计作已读；读相关章节不冒充完整逐页复核；不将技术报告冒充会议定稿；作者artifact未运行就直接注明。原论文PDF不提交仓库。

SHiP、AutoScratch-style比较和当前C16_SHIP_SW_STYLE_V1不同，必须保留具体signature/训练时点/软件region范围。CUDA官方文档不保证本项目要求的跨token地址稳定性，也没有证明真实硬件每次独立抽签。自定义对照不得冒称真实NVIDIA内部实现。

当前未闭合阅读队列：Leeway全文、ATLAS全文、Stream-K全文、必要时PIPP代码/勘误。读取论文并不自动授权实现。

## 配套数学反例

[LR02类内循环扫描反例](examples/toy_scan_counterexample.py)

这是CPU构造例子：相同边界占用不代表相同旧行存活。它不是C16 trace、CUDA实测、Talus复现或系统加速证据。

## 项目锚点与后继结果

- 早期Lane1：`4214398782159022907081dbcc36854cf21fb4b5`。
- 冻结Lane3 V1 / 本文献分支基点：`a402828860ced26124ddbf3c9d87baa6f6774d55`。
- LR07的three-lineage原始consumer：`08536be9940590be101c7f5bac2117ba82056db5`。
- LR07的split-K数据来源：`0e88faa28c9066b48e394dce657d7a16e6332a32`。
- 工作总账分支：`hrl/c16-work-history-audit-20260928-v1`；最新已审period11更新为`1f999e62000178feb7e657a79cdf9e5a64db182f`。
- 当前OLMoE多轮producer的协调合同：`378df585cba4c21ac5864c374976e271ae44e9a3`。本轮队列不得修改/抢占它。

历史笔记中的planned状态不回写成当时已经执行；实际后继结果以原producer/consumer及总账为准。所有“首次”“系统收益”“优于现有机制”主张仍需要实际比较，不由阅读数量或代码资格替代。
