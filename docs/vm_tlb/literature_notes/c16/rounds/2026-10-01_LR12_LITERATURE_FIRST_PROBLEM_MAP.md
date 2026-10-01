# LR12：literature-first problem map 与 C16 候选准入审查

日期：2026-10-01。状态：`RESEARCH_ONLY_NO_EXPERIMENT_AUTHORITY`。本轮在终态项目账本之后，**先由2025–26文献构造问题分类，再做C16映射**。审查包：`docs/vm_tlb/review_packs/C16_PROBLEM_DISCOVERY_V2_LITERATURE_PROBLEM_MAP/`。这是LR12，不覆盖LR11。

## 阅读与证据层次

原文相关章节核读并按实验组登记：NanoFlow（OSDI25）、Bullet（ASPLOS26/arXiv版本）、MPK（OSDI26）、Kitsune、VTC（OSDI26）、ComFuse、StreamDQ、TileSight、PASCAL v1、Hopper utilization、BOOST、reverse address translation。ReMoE仅本轮PMLR正式摘要；Patterns Behind Chaos仅ISCA官方题名/奖项及LR11已有摘要线索，不写成正文实验核读。全部作者artifact `NOT_RUN`。每篇版本、链接、章节、缺失字段见`SOURCE_READING_LEVEL.tsv`与以`(source_id, group_id)`联结的`LITERATURE_EXPERIMENT_AUDIT.tsv`/`LITERATURE_EXPERIMENT_CONTEXT.tsv`。未披露就是未披露；论文的最佳性能数不作为C16预测。

问题不是先选机制。文献形成七类：资源重叠与干扰；跨算子数据交接；低比特表示转换；progress divergence下共享cache；小batch利用率假象；tiered-memory/translation；MoE专家移动。每类按`现象→诊断→oracle/headroom→强软件基线→候选机制`记录。尤其四个反例改变了问题筛法：Bullet的naive overlap产生干扰；Kitsune的LL-TOK较高fusion coverage只带来0.07% traffic reduction；TileSight deep-K的lockstep预测82%而实测43%；BOOST的31%吞吐收益主要是容量，独立并发带宽约4%。这些是各论文自身实验点，不外推C16。PASCAL v1 Theorem 4的policy-independent *traffic* bound也不提供cycle speedup。来源分别为[BULLET §4](https://arxiv.org/html/2504.19516)、[Kitsune §6](https://arxiv.org/html/2502.18403v1)、[TileSight §5.3](https://arxiv.org/html/2607.22432v1)、[BOOST §5](https://arxiv.org/html/2609.13592)、[PASCAL v1 §3–5](https://arxiv.org/html/2609.10515v1)。

StreamDQ有必要单独分开：§6.3–6.4针对定制HBM基底die的机制采用改造Accel-Sim和实机校准；并非实机装有该机制。其AWQ-v2在batch≤4略优于StreamDQ是已披露反例。把其高batch modeled result转成RTX4080/AWQ小batch事实不合法。[原文](https://arxiv.org/html/2607.08993v1)。VTC与ComFuse明确把TensorRT/编译器作为强基线；VTC的部分移动优化即使减少内存占用，也需独立看时延，[VTC §7](https://www.usenix.org/system/files/osdi26-hu-muyan.pdf)、[ComFuse §VI](https://arxiv.org/html/2608.03537v1)。

## C16对照与冲突保留

终态authority `hrl/c16-ai-workload-exploration-wave-terminal-synthesis-174new-v1@ca6c33ae0431d91aa7c6a43cbb79522402dd7580`已关闭八条具体方向、保留零promotion candidate；唯一异构tile-handoff是future-only parking lot。本轮没有把文献中的普遍机会倒灌成既有C16身份的正headroom。具体八条逐项匹配见`C16_LITERATURE_GAP_MAP.tsv`。结论`NO_NEW_LITERATURE_DRIVEN_PROBLEM_QUALIFIED`，candidate count=0；这不是“领域问题不存在”。三条筛选性问题（tile handoff、新身份Ada W4 multi-view、新平台host-tier/scale-up）均因当前缺准入证据而不是正式候选，更不构成实验授权。

版本/来源冲突须保留：PASCAL此处按2026-09的v1公式/题名，不与后续改题版本合并；Bullet会议题名和arXiv页面题名不同，读的是后者正文；StreamDQ HTML含模板式venue/DOI占位，不宣称会议录用；既有LR05的PIPP参数正文/表格冲突仍未由本轮解决。MoE正式摘要不能支撑实验组精确设置。

## 边界

不运行GPU、NCU、NVBit、SASS、Accel-Sim、GPGPU-Sim、作者artifact，不下载大模型、不抓新trace、不实现机制。论文结果保留作者/版本/平台/精度/指标归属；C16结论保留终态证据归属。若未来另派研究，必须先冻结新target并证明headroom、相同语义强基线和合法scope，不能从LR12直接开启旧方向。
