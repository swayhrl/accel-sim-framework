# DTC-L1 / ISCAS2027 文献支线

更新日期：2026-09-26。维护者：ChatGPT。当前状态：**ROUND_2_UPLOADED_FULLTEXT_REVIEW_COMPLETE / NO_SIMULATION_AUTHORIZATION**。

## 最新入口

用户补齐了MiCache、DL-MSHR、CCWS和ICS2015旁路论文的PDF。本轮依据这四份上传版本通读正文，核对关键机制图、实验配置和结果口径；未进行代码复现，也未把参考文献中的二手介绍当作已读原文。

**先读：[第二轮结论、机制对照与论文修改建议](round2/ROUND2_SYNTHESIS_ZH.md)。**

| 文献 | 当前详细笔记 | 本轮状态变化 |
|---|---|---|
| MiCache，FPGA2024 | [P12](round2/P12_MICACHE_FULLTEXT_ZH.md) | 仅书目 → 正文、状态转换、双流水线、方法/代价核读 |
| DL-MSHR，ICS2019 | [P11](round2/P11_DL_MSHR_FULLTEXT_ZH.md) | 仅书目 → 正文、分配/合并/回收、方法/代价核读 |
| CCWS，MICRO2012 | [P10](round2/P10_CCWS_FULLTEXT_ZH.md) | 首页/摘要 → 正文、检测/发射规则、方法/代价核读 |
| Locality-Driven Dynamic GPU Cache Bypassing，ICS2015 | [P03](round2/P03_DECOUPLED_L1D_FULLTEXT_ZH.md) | 定向阅读 → 补核完整正文和生命周期表述边界 |

[来源版本与SHA-256](round2/UPLOADED_SOURCE_MANIFEST.tsv)；[四篇补齐的BibTeX](round2/references_fulltext_verified.bib)；[当前总索引](PAPER_INDEX.tsv)；[当前相关工作措辞](RELATED_WORK_AND_CLAIMS_ZH.md)。

## 当前最重要的更新

1. **DL-MSHR不是简单扩大传统MSHR。** 它重组固定entry/slot绑定，使用动态链接的slot-set池；必须与DTC正面比较等待状态由谁组织。
2. **MiCache与DTC的比较比上一轮更接近。** 它既复用cache/MSHR存储，又在子项溢出时保留不参加新请求匹配、但仍参加响应匹配的旧记录。不能再把“新查询可见性与旧请求状态保留分开”这个宽泛概念直接当作DTC独有。
3. **ICS2015已有GPU Tag/Data解耦，但目标是局部性过滤。** RC是复用频次，Position是组内数据位置；没有证据把它称为DTC的消费者引用计数，也不能从论文未详述的瞬态规则推出其实现一定不支持。
4. **CCWS限制的是部分load的发射资格。** 它不等价于全GPU在途请求cap；“优于Belady”的比较涉及不同调度产生的访问流，不能写成固定访问流上击败最优替换。

## 阅读台账与历史

仍登记14项：4篇本轮正文/关键图表核读、8篇上一轮全文定向核读、2项摘要筛查。不是14篇已复现，也不是相关工作已经查全。

第一轮提交：`9d1026d3c49d56c584e074a76071c90a456aebce`。第一轮原始记录保留在Git历史及[PAPER_NOTES_ZH.md](PAPER_NOTES_ZH.md)、[COMPARISON_MATRIX.tsv](COMPARISON_MATRIX.tsv)、[IDEAS_AND_NEXT_READS_ZH.md](IDEAS_AND_NEXT_READS_ZH.md)、[SEARCH_LOG_2026-09-26.md](SEARCH_LOG_2026-09-26.md)。**其中P03/P10/P11/P12的旧阅读等级、待取文事项及相关推断由round2取代**；不能把第一轮“未取得全文”当作当前状态。其他文献本轮未重新审核。

本轮只保存原创文字笔记、书目和来源哈希，不上传论文全文、原文图像或授权下载水印。论文事实、作者解释、我们的推断和原文未明确之处分开记录。

## 项目隔离

分支：`hrl/iscas2027-dtc-literature-review-v0`。DTC比较基础见[PROJECT_COMPARISON_BASIS.md](PROJECT_COMPARISON_BASIS.md)。本轮不改该设计基础、不改主线handoff、模拟器代码、配置或已接受结果；不授权复现或新实验。SG3冻结证据锚点仍为`6886930ab22d63701e58732cfde18ba019d1dfde`。
