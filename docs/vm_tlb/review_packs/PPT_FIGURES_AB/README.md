# PPT Figures A/B review pack

状态：`PPT_FIGURES_AB_READY_FOR_REVIEW`。

本包索引单页 PPT 的两张图，不包含任何 simulator 运行或新的研究数据。权威输入为
A C4 closeout `74d5fbe6a5ca2411309674cf457baa1efa78f58d` 的
`TRANSLATION_TOTALS.tsv`、`C4_TRACE_LOCALITY_SUMMARY.tsv` 与
`L2_TLB_REPLACEMENT_MATRIX.tsv`。

## 交付物与复现

- 图、README 和逐指标来源/公式/断言：
  `docs/vm_tlb/ppt_figures/llm_memory_onepage/`
- 生成器：`util/vm_tlb/plot_ppt_onepage_figures.py`
- 命令：`python3 util/vm_tlb/plot_ppt_onepage_figures.py`

生成器解析 generic full-ROI 的 A/C4 TSV 行，复算并断言 13 项数据与
`FIGURES_AB_REFERENCE_DATA.tsv` 对齐；Decode 的 L2 replacement matrix 还被断言为
9 格总和等于 L2 TLB eviction 总数。生成物为两张 1920×1080 SVG/PNG，且已实际检查
Pillow PNG 与 LibreOffice SVG 渲染，无文字裁切、中文缺字或标签重叠。

## 范围与已知边界

- 图 A 的 MSHR-full 是 event counter；`30.35K events / 1M translation requests`
  不是请求发生率。
- 图 B 的 `UNKNOWN` 保持 UNKNOWN，未改写为 Activation。
- 图 A/B 仅是 A/C4 full-ROI 权威数据的汇报表达，未使用 Window C speculative 数值。
- 没有原始运行日志：本阶段只执行了可复现的 TSV 解析、断言、SVG/PNG 出图与渲染检查。
