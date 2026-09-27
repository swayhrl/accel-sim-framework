# AWMA论文阅读笔记｜ChatGPT支线

维护者ChatGPT；更新：Round09，2026-09-27。文献笔记不是执行receipt；是否启动和完成实验，以独立Goal和review pack为准。

## 最新问题发现

- [Round10：R81/R82横向审查与下一轮并行候选](rounds/2026-09-27_ROUND_10_HORIZONTAL_REVIEW_AND_NEXT.md)：独立接受R81软件机会/R82当前软件充分，关闭其架构推进；Round09后备中提升R101固定Newton–Schulz中间态生命周期，条件提升R102低精度权重变化检测/压缩，Q92/Q93暂缓。下一轮建议Lane H/Lane I并行，109 GPU仍统一加锁。\n- [Round09：宽范围支线——执行组织、表示生命周期与训练新成本](rounds/2026-09-27_ROUND_09_BROAD_SIDE_RESEARCH.md)：27项核心工作，19项正文关键章节、1项部分正文、6项原始摘要、1项作者artifact/元数据；本轮扩展证据表53条。覆盖编译、通信、稀疏、优化器、RL同步、TT embedding、可靠性、CPU/FPGA与模拟方法。保留三个后备问题卡，未启动新GPU任务、不改Lane F/R81或Lane G/R82。明确Celty/Coruscant公开代码范围及Syncopate AE版本标注差异。
- [Round08：能力比较与两窗口并行探索](rounds/2026-09-27_ROUND_08_PARALLEL_PROBLEM_DISCOVERY.md)：核心13篇，7篇正文关键章节、6篇原始摘要，另核官方源码。保留R81异构合法词表批处理、R82片上layout转换两个小型探索，非已证明的硬件创新。Kestrel已有indexed LM-head，Triton已有多级转换优化，均进入强基线。协调入口：`hrl/awma-round08-parallel-exploration-handoff-v1`，`docs/vm_tlb/chatgpt_handoff/awma/round08_parallel_v1/START_HERE.md`。发布不等于已运行。
- [Round07：R54 checkpoint生命周期选择](rounds/2026-09-27_ROUND_07_R54_LONG_HORIZON_SELECTION.md)：原长时资格设计。后续R54已完成于`d6ef29505de75985181afc74dffc3cf1b652afc2`，后端greedy资格通过；科学状态`R54_HOST_RUNTIME_COST_NOT_ARCH_LOCALIZED_V1`。不要用原设计状态代替最新结果。
- [Round06：R53扩散推理合法工作集](rounds/2026-09-27_ROUND_06_R53_RESEARCH_AND_DESIGN.md)：9篇核心，8篇正文关键章节、1篇摘要及源码；原设计状态不是后续执行状态。
- [Round05：工作有效性与安全资源交接](rounds/2026-09-26_ROUND_05_PROBLEM_DISCOVERY.md)：15篇核心，13篇正文关键章节、2篇摘要；R51/R52候选及边界。
- [Round04：负结果之后的问题重选](rounds/2026-09-26_ROUND_04_PROBLEM_DISCOVERY.md)：数值合同、在线稀疏选择、MoE、SSM与执行组织；随后P1/P2已有独立native结果。

不同轮次可能重复阅读同一论文/版本，阅读计数不能相加为去重论文数。KEY_SECTIONS不代表全文逐段阅读，摘要与artifact记录不升级为已核实实验结果。

## 基础机制阅读状态（截至Round03）

11篇有正文依据，其中4篇用户提供会议版全文已读；7篇原文关键章节阅读（NeuMMU实际读2019预印本）。不声称全部全文精读、代码复现或覆盖所有前人工作。

| ID | 论文 | 深度 |
|---|---|---|
| [L001](papers/L001_ISCA2018_SIMT_Page_Walk_Scheduling.md) | ISCA2018 Page Walk Scheduling | 正文关键章节 |
| [L002](papers/L002_MICRO2018_Neighborhood_Translation.md) | MICRO2018 Neighborhood | 正文关键章节/图表 |
| [L003](papers/L003_ASPLOS2018_MASK.md) | ASPLOS2018 MASK | 正文关键章节 |
| [L004](papers/L004_ASPLOS2018_Virtual_Caching.md) | ASPLOS2018 Virtual Caching | 正文关键章节 |
| [L005](papers/L005_HPCA2023_Core_Partitioning.md) | HPCA2023 Core Partitioning | 正文关键章节/图表 |
| [L006](papers/L006_ISCA2024_Memento.md) | ISCA2024 Memento | 用户全文已读 |
| [L007](papers/L007_MICRO2025_LATPC.md) | MICRO2025 LATPC | 用户全文已读 |
| [L008](papers/L008_HPCA2025_Marching_Page_Walks.md) | HPCA2025 MPW | 用户会议版全文已读 |
| [L009](papers/L009_MICRO2024_Avatar.md) | MICRO2024 Avatar | 用户会议版全文已读 |
| [L010](papers/L010_PACT2020_Valkyrie.md) | PACT2020 Valkyrie | 正文关键章节，未估读图柱 |
| [L011](papers/L011_ASPLOS2020_NeuMMU_PREPRINT_REVIEW.md) | ASPLOS2020 NeuMMU | 2019arXiv v1关键章节，最终版差异未核 |

旧L008/L009 PRELIMINARY路径为历史跳转。

## 历史轮次与经验账本

- [Round03](rounds/2026-09-26_ROUND_03.md)：12上下文、40条workload、40条观察。
- [Round02](rounds/2026-09-26_ROUND_02.md)：6上下文、34条workload、17条观察。
- [Round01](rounds/2026-09-26_ROUND_01.md)：初始机制/近邻笔记。
- [实验账本说明](empirical/README.md)、[Round03数据](empirical/ROUND03_DATA.json)、[Round02数据](empirical/ROUND02_DATA.json)。
- [基础来源登记](SOURCE_REGISTER.json)、[相关工作关系](RELATED_WORK_MAP.md)、[阅读队列](READING_QUEUE.md)、[维护记录](CHANGELOG.md)、[模板](NOTE_TEMPLATE.md)。后续问题发现来源见各轮笔记。

截至Round03的74条workload记录/57条观察不是74个独立程序或复现实验。正文数值、作者均值、图上明确数字和定性信息分开；null不等于0。

## 使用边界

作者结论、源码事实、比较判断、待验证想法分开。版本、输入、实现、初始状态和统计分母不一致时不能直接合并结果。存储比例不是布局面积；模拟器不是实机内部结构；统计改善不等于性能改善；独立分段时间不天然可加成critical path。缺失证据保持未知。

分支：`hrl/awma-chatgpt-literature-notes-v1`；目录：`docs/vm_tlb/literature_notes/awma/`。
Round03基于`c9e16ce0857be4562570fae79dbd861b6ae5a8e2`；Round04正文`082dd8b36b199e135585c0ba61cab587d6814e60`；Round05正文`ecef0bfd80a62a60cae9e4a0df478b3acfa15567`；Round06正文`8dac519298eb16709c88c37a28f02f360360c507`；Round07正文`5afae5b18922333130a0c6b253eea9cc9ebf3d85`；Round08正文`214b30039cc579c28457cb17bfbd7e9d88d00fcd`；Round09正文`e14378a293ce0a031e2a88b1ce8b7b912a3ecadd`。
原论文PDF不提交仓库，accepted实验和raw不改动。
