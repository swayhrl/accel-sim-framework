# DTC-L1 / ISCAS2027 文献支线

最新更新：2026-10-16。维护者：ChatGPT。状态：**ROUND_3_LATEX_REFERENCE_AUDIT_AND_TARGETED_EXPANSION / NO_SIMULATION_AUTHORIZATION**。

## 最新入口：英文LaTeX v0.1文献核查

**[R3逐条核查、针对性补充与论文含义](round3/ROUND3_AUDIT_ZH.md)**。

本轮核查原九条参考文献及正文引用用途，登记七条有明确位置的新增候选：NuRAPID、Scalable Cache Miss Handling、MSHR-rich、MeDiC、PolyBench GPU/ACC、Rodinia、Parboil。数量不是目标，阅读深度分别说明。

最重要更新是已有Accel-Sim论文中的streaming L1及reservation-bottleneck case study不能忽略。它限定本文reserve-on-miss基线的适用范围，不自动否定DTC，也不自动授权新实验。

- [精简候选BibTeX](round3/references_curated.bib)
- [本轮阅读等级及未纳入候选](round3/READING_REGISTER.tsv)

原v0.1论文与实验数值不覆盖。未取得正文的MSHR-rich、Parboil及其他候选不记为全文精读；原始页码冲突和输入溯源缺口不以新增引用掩盖。

## 第二轮入口（2026-09-26，保留）

用户补齐了MiCache、DL-MSHR、CCWS和ICS2015旁路论文的PDF。本轮依据这四份上传版本通读正文，核对关键机制图、实验配置和结果口径；未进行代码复现，也未把参考文献中的二手介绍当作已读原文。

**[第二轮结论、机制对照与论文修改建议](round2/ROUND2_SYNTHESIS_ZH.md)。**

| 文献 | 当前详细笔记 | 第二轮状态变化 |
|---|---|---|
| MiCache，FPGA2024 | [P12](round2/P12_MICACHE_FULLTEXT_ZH.md) | 仅书目 → 正文、状态转换、双流水线、方法/代价核读 |
| DL-MSHR，ICS2019 | [P11](round2/P11_DL_MSHR_FULLTEXT_ZH.md) | 仅书目 → 正文、分配/合并/回收、方法/代价核读 |
| CCWS，MICRO2012 | [P10](round2/P10_CCWS_FULLTEXT_ZH.md) | 首页/摘要 → 正文、检测/发射规则、方法/代价核读 |
| Locality-Driven Dynamic GPU Cache Bypassing，ICS2015 | [P03](round2/P03_DECOUPLED_L1D_FULLTEXT_ZH.md) | 定向阅读 → 补核完整正文和生命周期表述边界 |

[来源版本与SHA-256](round2/UPLOADED_SOURCE_MANIFEST.tsv)；[四篇补齐的BibTeX](round2/references_fulltext_verified.bib)；[此前总索引](PAPER_INDEX.tsv)；[此前相关工作措辞](RELATED_WORK_AND_CLAIMS_ZH.md)。

第二轮的重要结论仍保留：DL-MSHR不是简单扩大固定MSHR；MiCache存在新请求不可见、响应仍处理的旧记录；ICS2015的RC是复用频率；CCWS控制load发射资格，不能把不同调度产生的访问流当作固定流上的Belady比较。

## 阅读台账与历史

第一轮提交：`9d1026d3c49d56c584e074a76071c90a456aebce`。第二轮提交：`606f62813c479525a1bac420b4f14d8ebb0b5261`。此前14项索引不代表R3累计条目，也不代表14项已经复现。

第一轮原始记录保留在Git历史及[PAPER_NOTES_ZH.md](PAPER_NOTES_ZH.md)、[COMPARISON_MATRIX.tsv](COMPARISON_MATRIX.tsv)、[IDEAS_AND_NEXT_READS_ZH.md](IDEAS_AND_NEXT_READS_ZH.md)、[SEARCH_LOG_2026-09-26.md](SEARCH_LOG_2026-09-26.md)。P03/P10/P11/P12的旧待取文状态由round2取代；R3新增核查与限定见round3，未重读条目保留原状态。

只保存原创文字笔记、书目和来源索引，不上传第三方论文全文、原文图像、字体或授权下载水印。论文事实、作者解释、我们的推断和未取得的证据分别记录。

## 项目隔离

分支：`hrl/iscas2027-dtc-literature-review-v0`。DTC比较基础见[PROJECT_COMPARISON_BASIS.md](PROJECT_COMPARISON_BASIS.md)。文献补充不修改科学执行合同、主线handoff、Core、配置或已接受结果，不自动授权复现、重新计时或新机制。SG3既有冻结锚点仍为`6886930ab22d63701e58732cfde18ba019d1dfde`。
