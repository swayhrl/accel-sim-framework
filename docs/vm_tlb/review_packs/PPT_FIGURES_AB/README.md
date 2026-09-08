# PPT Figures A/B review pack

状态：`PPT_FIGURES_AB_ASSETS_READY_FOR_REVIEW`。

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

本次 asset 重构新增（不覆盖原 first-pass 图）：

- `FIG_A_PREFILL_DECODE_TLB_PRESSURE_ASSET.svg/png`：透明、紧裁的两列三级路径；
  移除图内标题、结论框、脚注和大面积卡片。
- `FIG_B_WEIGHT_ACCESS_VS_TRANSLATION_WORKING_SET_ASSET.svg/png`：透明、紧裁的柱图；
  指标直接标在柱下，`97.1% L2 TLB 替换：Weight → Weight` 为无框短注释。

`--asset-only` 会在不覆盖第一版图的前提下重跑解析/assertion 并生成 asset。PNG 为
3600×1300 和 3200×1440 的透明高分辨率输出；SVG root 不含背景矩形。二者均经实际
PNG 及 LibreOffice SVG 渲染检查，不呈现“PPT 中嵌 PPT”的视觉层级。

## 范围与已知边界

- 图 A 的 MSHR-full 是 event counter；`30.35K events / 1M translation requests`
  不是请求发生率。
- 图 B 的 `UNKNOWN` 保持 UNKNOWN，未改写为 Activation。
- 图 A/B 仅是 A/C4 full-ROI 权威数据的汇报表达，未使用 Window C speculative 数值。
- 没有原始运行日志：本阶段只执行了可复现的 TSV 解析、断言、SVG/PNG 出图与渲染检查。
