# DTC-L1 / ISCAS2027 文献支线

最新更新：2026-10-16。维护者：ChatGPT。状态：**ROUND_4_TARGETED_REVIEW_AND_LATEX_V02_INTEGRATED / NO_SIMULATION_AUTHORIZATION**。

## 最新入口：R4补齐并整合到英文v0.2

**[R4完成报告、关键来源与论文修改](round4/ROUND4_COMPLETION_REPORT_ZH.md)**。

20条已经实际进入英文LaTeX的引言、方法及Related Work，不只是候选列表：13篇独立技术工作、DTC学位论文、Accel-Sim、3套件来源、Volta白皮书和项目记录。保持4页技术内容＋第5页参考文献，原数据与TBD不改。源码与PDF由当前对话交付，本分支只持久化文献资料。

- [最接近工作的状态对照](round4/CLOSEST_WORK_COMPARISON_ZH.md)
- [实际使用的20条及读取深度](round4/READING_REGISTER.tsv)
- [整合后的BibTeX](round4/references_verified.bib)

Kroft重印正文进一步表明稳定返回身份已有先例；Hierarchical MHA的LSQ讨论补足消费者存放比较；Volta／Accel-Sim限定现代GPU背景；Poise及GPU带宽研究支撑并发/服务区分。MSHR-rich及Parboil正文缺口保留，Farkas/Jouppi 1994仅摘要未加入；没有把20条称为20篇全文精读。

## 第三轮（保留）

**[R3逐条核查、针对性补充与论文含义](round3/ROUND3_AUDIT_ZH.md)**。

R3核查原九条参考文献及正文引用用途，登记七条新增候选：NuRAPID、Scalable Cache Miss Handling、MSHR-rich、MeDiC、PolyBench GPU/ACC、Rodinia、Parboil。数量不是目标，读取深度分别说明。已有Accel-Sim论文的streaming L1限定reserve-on-miss基线范围，不自动否定DTC或授权实验。

- [R3候选BibTeX](round3/references_curated.bib)
- [R3读取等级及未纳入候选](round3/READING_REGISTER.tsv)

## 第二轮（2026-09-26，保留）

用户补齐MiCache、DL-MSHR、CCWS和ICS2015旁路论文PDF。此前依据四份上传版本通读正文、核对关键机制与方法；不把二手介绍作为原文。

**[第二轮结论、机制对照与论文修改建议](round2/ROUND2_SYNTHESIS_ZH.md)**。

| 文献 | 详细笔记 |
|---|---|
| MiCache，FPGA2024 | [P12](round2/P12_MICACHE_FULLTEXT_ZH.md) |
| DL-MSHR，ICS2019 | [P11](round2/P11_DL_MSHR_FULLTEXT_ZH.md) |
| CCWS，MICRO2012 | [P10](round2/P10_CCWS_FULLTEXT_ZH.md) |
| Locality-Driven Dynamic GPU Cache Bypassing，ICS2015 | [P03](round2/P03_DECOUPLED_L1D_FULLTEXT_ZH.md) |

[来源SHA-256](round2/UPLOADED_SOURCE_MANIFEST.tsv)；[四篇BibTeX](round2/references_fulltext_verified.bib)；[此前总索引](PAPER_INDEX.tsv)；[此前相关工作措辞](RELATED_WORK_AND_CLAIMS_ZH.md)。

第二轮结论保留：DL-MSHR不是简单扩容；MiCache有新请求不匹配而响应仍处理的特定旧记录；ICS2015 RC是复用频率；CCWS控制load资格而非全局在途cap。R4进一步限定具体比较，不改已有证据。

## 阅读台账与历史

第一轮：`9d1026d3c49d56c584e074a76071c90a456aebce`。第二轮：`606f62813c479525a1bac420b4f14d8ebb0b5261`。第三轮：`692fc0164546e76ff8c91f04dbf0509dcae1dbd9`。此前14项索引不是当前全部实际引用，也不是复现完成数。

原笔记保留：[PAPER_NOTES_ZH.md](PAPER_NOTES_ZH.md)、[COMPARISON_MATRIX.tsv](COMPARISON_MATRIX.tsv)、[IDEAS_AND_NEXT_READS_ZH.md](IDEAS_AND_NEXT_READS_ZH.md)、[SEARCH_LOG_2026-09-26.md](SEARCH_LOG_2026-09-26.md)。各轮的读取等级只按对应材料更新，不把未重读工作升级为精读。

## 项目隔离

分支：`hrl/iscas2027-dtc-literature-review-v0`。仅保存原创笔记、书目和来源，不上传第三方全文、原图、字体或工艺资料。论文事实、我们的推断、读取缺口分开。

[DTC比较基础](PROJECT_COMPARISON_BASIS.md)与冻结实验不修改。本轮不改变科学执行合同、主线handoff、Core、配置或已接受结果，不自动授权复现、重新计时或新机制。SG3既有冻结锚点仍为`6886930ab22d63701e58732cfde18ba019d1dfde`。
