# AWMA论文阅读笔记｜ChatGPT支线

维护者ChatGPT；更新：Round07，2026-09-27。仅文献与条件化实验观察，不是执行Goal，不授权修改模拟器或启动109。

## 最新问题发现

- [Round06：R53扩散推理的合法工作集与在线组织](rounds/2026-09-27_ROUND_06_R53_RESEARCH_AND_DESIGN.md)：9篇核心文献，8篇正文关键章节、1篇原始摘要；补官方batch源码、模型配置和runtime/API能力。状态`R53_DESIGN_READY_NATIVE_NOT_AUTHORIZED`；仅形成一组有界实验设计，未下载模型、未启动109/174。R51在已测范围冻结，R52无真实失效证据而休眠。
- [Round05：动态AI执行、工作有效性与安全资源交接](rounds/2026-09-26_ROUND_05_PROBLEM_DISCOVERY.md)：15篇核心文献，13篇正文关键章节、2篇原始摘要，另2份官方文档。该轮优先核查R51/R52，未启动实验；随后项目结果见相应独立review pack，不把有限资格结果扩大成领域否定。
- [Round04：负结果之后的问题重选](rounds/2026-09-26_ROUND_04_PROBLEM_DISCOVERY.md)：数值合同、在线稀疏选择、MoE、SSM与执行组织。其P1/P2随后已有native资格结果；Round05注明引用边界。

Round04/05/06/07与下列机制阅读可能有交叉，不直接相加为去重论文数。

## 基础机制阅读状态（截至Round03）

11篇有正文依据，其中4篇用户提供会议版全文已读；7篇为原文关键章节阅读（NeuMMU实际读2019预印本）。不声称11篇全都全文精读、代码复现或覆盖所有前人工作。

| ID | 论文 | 当前深度 |
|---|---|---|
| [L001](papers/L001_ISCA2018_SIMT_Page_Walk_Scheduling.md) | ISCA2018 Page Walk Scheduling | 正文关键章节 |
| [L002](papers/L002_MICRO2018_Neighborhood_Translation.md) | MICRO2018 Neighborhood | 正文关键章节/图表 |
| [L003](papers/L003_ASPLOS2018_MASK.md) | ASPLOS2018 MASK | 正文关键章节 |
| [L004](papers/L004_ASPLOS2018_Virtual_Caching.md) | ASPLOS2018 Virtual Caching | 正文关键章节 |
| [L005](papers/L005_HPCA2023_Core_Partitioning.md) | HPCA2023 Core Partitioning | 正文关键章节/图表 |
| [L006](papers/L006_ISCA2024_Memento.md) | ISCA2024 Memento | 用户全文已读 |
| [L007](papers/L007_MICRO2025_LATPC.md) | MICRO2025 LATPC | 用户全文已读 |
| [L008](papers/L008_HPCA2025_Marching_Page_Walks.md) | HPCA2025 MPW | Round03升级，用户会议版全文已读 |
| [L009](papers/L009_MICRO2024_Avatar.md) | MICRO2024 Avatar | Round03升级，用户会议版全文已读 |
| [L010](papers/L010_PACT2020_Valkyrie.md) | PACT2020 Valkyrie | 正文关键章节，未估读图柱 |
| [L011](papers/L011_ASPLOS2020_NeuMMU_PREPRINT_REVIEW.md) | ASPLOS2020 NeuMMU | 2019arXiv v1关键章节，最终版差异未核 |

旧L008/L009 PRELIMINARY路径是历史跳转；其UNKNOWN不再代表最新状态。

## 历史轮次与经验账本

- [第3轮全文总结](rounds/2026-09-26_ROUND_03.md)：两篇补全文，新增12上下文、40条workload、40条观察。
- [第2轮](rounds/2026-09-26_ROUND_02.md)：6上下文、34条workload、17条观察。
- [第1轮](rounds/2026-09-26_ROUND_01.md)：初始机制/近邻笔记。
- [实验账本说明](empirical/README.md)；[Round03数据](empirical/ROUND03_DATA.json)；[Round02数据](empirical/ROUND02_DATA.json)。
- [来源及基础机制阅读历史](SOURCE_REGISTER.json)；[相关工作关系](RELATED_WORK_MAP.md)；[后续队列](READING_QUEUE.md)；[维护记录](CHANGELOG.md)；[模板](NOTE_TEMPLATE.md)。Round04/05/06/07的问题发现来源另见各轮笔记。

截至Round03的74条workload记录和57条观察不是74个不同程序，更不是74个已复现实验。原表、正文数值、作者均值、图上明确标注、定性信息分别标记；不从未标数字的柱高生成精确值。null不是零。

## 使用边界

作者结论、我的比较判断与待验证想法分开。先核版本、输入、实现、页大小、TLB/cache路径、统计分母，再比较数字。存储比例不是布局面积，模型不是真实GPU内部实现，数据可压缩率不是推测准确率，服务节省不是普遍加速。没有原文证据的实现细节保持未知。

分支：`hrl/awma-chatgpt-literature-notes-v1`；目录：`docs/vm_tlb/literature_notes/awma/`。Round03基于`c9e16ce0857be4562570fae79dbd861b6ae5a8e2`；Round04为`082dd8b36b199e135585c0ba61cab587d6814e60`；Round05正文为`ecef0bfd80a62a60cae9e4a0df478b3acfa15567`；Round06正文为`8dac519298eb16709c88c37a28f02f360360c507`；Round07正文为`5afae5b18922333130a0c6b253eea9cc9ebf3d85`。原论文PDF不提交仓库，执行分支不改动。
