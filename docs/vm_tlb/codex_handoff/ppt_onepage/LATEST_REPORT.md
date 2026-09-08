# 单页PPT绘图窗口当前状态

状态：`PPT_FIGURES_AB_ASSET_REFACTOR_AUTHORIZED`

分支：`hrl/vm-tlb-ppt-figures-v0`

权威数据基线：A closeout `74d5fbe6a5ca2411309674cf457baa1efa78f58d`。

第一版两张图已经完成并通过数据复核，但 review 发现其视觉层级更像两张独立“小型幻灯片”，不适合作为真正 PPT 页面中的 figure asset。

当前追加任务不是重做数据分析，而是进行“去 PPT 化”资产重构：

- 保留图A的 Prefill/Decode 两列三级 TLB 压力路径；
- 保留图B的 Weight 动态访问占比 vs 64KB 翻译工作集柱状图；
- 删除图内大标题、副标题、页脚、结论框、顶部横线、过大外围白边与大型说明卡片；
- 输出紧裁、透明背景优先的 SVG/PNG 图形资产。

执行：

- `docs/vm_tlb/codex_handoff/ppt_onepage/FIGURES_AB_ASSET_REFACTOR_ADDENDUM.md`
- `docs/vm_tlb/codex_handoff/ppt_onepage/FIGURES_AB_ASSET_REFACTOR_ACCEPTANCE.md`
- 原 `FIGURES_AB_REFERENCE_DATA.tsv` 与 `FIGURE_DATA_USED.tsv` 继续作为数据权威。

建议新输出：

- `FIG_A_PREFILL_DECODE_TLB_PRESSURE_ASSET.svg/png`
- `FIG_B_WEIGHT_ACCESS_VS_TRANSLATION_WORKING_SET_ASSET.svg/png`

原 review-ready 图保留作为历史版本，不覆盖。

禁止重跑 simulator、修改正式 C3/C4 数据或触碰 Window C。

最终状态：

`PPT_FIGURES_AB_ASSETS_READY_FOR_REVIEW`
