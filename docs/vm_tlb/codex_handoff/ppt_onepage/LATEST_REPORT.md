# 单页PPT绘图窗口当前状态

状态：`PPT_FIGURES_AB_ASSETS_READY_FOR_REVIEW`

分支：`hrl/vm-tlb-ppt-figures-v0`

权威数据基线：A closeout `74d5fbe6a5ca2411309674cf457baa1efa78f58d`。

第一版两张图已经完成并通过数据复核，但 review 发现其视觉层级更像两张独立“小型幻灯片”，不适合作为真正 PPT 页面中的 figure asset。

追加的“去 PPT 化”资产重构已经完成：

- 保留图A的 Prefill/Decode 两列三级 TLB 压力路径；
- 保留图B的 Weight 动态访问占比 vs 64KB 翻译工作集柱状图；
- 删除图内大标题、副标题、页脚、结论框、顶部横线、过大外围白边与大型说明卡片；
- 输出紧裁、透明背景优先的 SVG/PNG 图形资产。

新的可插入资产：

- `docs/vm_tlb/ppt_figures/llm_memory_onepage/FIG_A_PREFILL_DECODE_TLB_PRESSURE_ASSET.svg/png`
- `docs/vm_tlb/ppt_figures/llm_memory_onepage/FIG_B_WEIGHT_ACCESS_VS_TRANSLATION_WORKING_SET_ASSET.svg/png`

两张 SVG 均为透明背景；PNG 分别为 3600×1300 与 3200×1440。原 first-pass 图保留为
历史版本，未被覆盖。数据仍由同一 authority TSV 重新解析并逐项断言；新 asset 已实际
检查 PNG 和 LibreOffice SVG 渲染，无裁切、重叠或“PPT 中嵌 PPT”观感。

执行依据：

- `docs/vm_tlb/codex_handoff/ppt_onepage/FIGURES_AB_ASSET_REFACTOR_ADDENDUM.md`
- `docs/vm_tlb/codex_handoff/ppt_onepage/FIGURES_AB_ASSET_REFACTOR_ACCEPTANCE.md`
- 原 `FIGURES_AB_REFERENCE_DATA.tsv` 与 `FIGURE_DATA_USED.tsv` 继续作为数据权威。

禁止重跑 simulator、修改正式 C3/C4 数据或触碰 Window C。

最终状态：

`PPT_FIGURES_AB_ASSETS_READY_FOR_REVIEW`
