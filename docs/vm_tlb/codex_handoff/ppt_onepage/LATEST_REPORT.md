# 单页PPT绘图窗口当前状态

状态：`PPT_FIGURES_AB_READY_FOR_REVIEW`

分支：`hrl/vm-tlb-ppt-figures-v0`

权威数据基线：A closeout `74d5fbe6a5ca2411309674cf457baa1efa78f58d`。

本窗口已完成且仅绘制两张图：

- 图A：Prefill vs Decode TLB 压力三级路径图；
- 图B：Weight 动态访问占比 vs 64KB 翻译工作集分组柱状图。

输出目录：

`docs/vm_tlb/ppt_figures/llm_memory_onepage/`

- `FIG_A_PREFILL_DECODE_TLB_PRESSURE.svg/png`：左右两列、三级向下的
  L1 TLB miss → L2 continued miss → Translation MSHR-full 路径；Decode 清晰
  区分 full-ROI `2.30M` event counter 和 `30.35K events / 1M translation requests`。
- `FIG_B_WEIGHT_ACCESS_VS_TRANSLATION_WORKING_SET.svg/png`：Weight 动态 lane
  访问占比与 64KB 唯一页工作集的分组柱状图；Decode 标明 `97.1%` 的
  Weight → Weight L2 TLB 替换。
- `FIGURE_DATA_USED.tsv`：从权威 TSV 重算的 13 项指标、公式、输入 SHA-256 与
  对 `FIGURES_AB_REFERENCE_DATA.tsv` 的逐项 assertion。

生成器是：

`util/vm_tlb/plot_ppt_onepage_figures.py`

已通过数据 assertion、SVG XML/PNG 尺寸检查，以及 PNG 和 LibreOffice SVG 渲染的
实际视觉检查；没有重跑 simulator、改写正式 C3/C4 数据或触碰 Window C。

本窗口执行依据：

- `FIGURES_AB_HANDOFF.md`
- `FIGURES_AB_ACCEPTANCE_MATRIX.md`
- `FIGURES_AB_REFERENCE_DATA.tsv`

禁止重跑模拟器、修改正式数据或触碰 Window C。C11 前后的其他 VM 工作不属于本 PPT
图窗口范围。
