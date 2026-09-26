# DTC-L1 / ISCAS2027 文献支线

记录日期：2026-09-26。维护者：ChatGPT。状态：**ROUND_1_RECORDED / NOT_AN_EXPERIMENT_AUTHORIZATION**。

本目录记录已做过的检索、原文核读范围、与DTC的技术联系和未解决问题。目的有三项：减少重复阅读；约束创新点表述；为论文相关工作和后续研究提供可追溯素材。它不是一份已经证明DTC新颖性的报告，也不是新模拟器任务。

## 入口

| 文件 | 内容 |
|---|---|
| [PAPER_INDEX.tsv](PAPER_INDEX.tsv) | 14项登记：题目、年份、来源、阅读状态和笔记位置 |
| [PAPER_NOTES_ZH.md](PAPER_NOTES_ZH.md) | 12篇核心候选的逐篇记录；两篇2026年外围线索的筛查说明 |
| [COMPARISON_MATRIX.tsv](COMPARISON_MATRIX.tsv) | 按控制对象、状态组织及DTC对照问题比较；未知项不填成“没有” |
| [RELATED_WORK_AND_CLAIMS_ZH.md](RELATED_WORK_AND_CLAIMS_ZH.md) | 技术脉络、不能声称的新颖性、可用于改稿的相关工作段落 |
| [IDEAS_AND_NEXT_READS_ZH.md](IDEAS_AND_NEXT_READS_ZH.md) | 待验证启发、优先补读原文、下一轮停止条件 |
| [SEARCH_LOG_2026-09-26.md](SEARCH_LOG_2026-09-26.md) | 检索范围、来源路线、取文失败、书目信息纠正 |
| [references_verified.bib](references_verified.bib) | 已核对主要书目信息的10篇文献；未核实的DOI/页码不猜填 |
| [PROJECT_COMPARISON_BASIS.md](PROJECT_COMPARISON_BASIS.md) | DTC自身来源、当前比较对象和冻结边界 |

## 本轮覆盖与阅读等级

共登记14项，不应表述为“精读14篇”：

- **9篇 FULLTEXT_TARGETED**：已取得原文，定向核读机制、方法或相关实验段落；并不表示每一节、每一张图都读完或已经复现。
- **1篇 PRIMARY_FRONTMATTER**：CCWS核到原文首页/摘要，详细机制和实验待补读。
- **2篇 METADATA_ONLY**：DL-MSHR、MiCache。已定位文献信息，未获得足够原文，不能据此判断机制差异已经清楚。
- **2篇 ABSTRACT_SCREEN**：2026年的TTP、TileLens，作为外围线索；没有当作当前DTC最接近对手。

原文事实、作者声称、ChatGPT比较推断和未核实事项在笔记中分栏处理。对未读内容使用“本轮未核读/未取得”，不混同于“原文未披露”。本目录只保存书目、链接和原创笔记，不上传外部论文全文或图像。

## 本轮最重要的三个判断

1. **直接对照不能遗漏Li等的ICS2015工作。** 它本身已经使用分离的GPU L1 Tag/Data存储。需比较它的局部性过滤与DTC的物理行生命周期，而不是把所有前人归为“仍然紧耦合”。见P03。
2. **并发与缓存/内存承载能力需要平衡，不是本项目新发现的一般规律。** MRPB、CCWS、SACAT、Poise等已从不同控制位置研究此问题。当前DTC受控实验的价值是解释本设计，而非重新命名一条普遍规律。见P04、P06、P07、P10。
3. **现阶段不能完成miss-state方向的新颖性排查。** DL-MSHR和MiCache是优先缺口，不能因为全文未取到而略过；2025年的LLaMCAT也使“利用MSHR命中和节流改善访存”成为必须比较的方向。见P08、P11、P12。

## 与主线的隔离

本支线从协调提交 `d0f8e72b370271b7432c3785c0687e79ca3e0f4b` 建立。只增加本目录，不改 `chatgpt_handoff/CODEX_NEXT_STAGE.md`、运行配置、模拟器代码或既有结果。SG3冻结证据锚点为 `6886930ab22d63701e58732cfde18ba019d1dfde`。

**这些笔记不授权任何仿真、复现或新机制。** 下一轮阅读可以继续补充本目录；实验必须另有明确论文问题和执行授权。
