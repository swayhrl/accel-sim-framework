# 单页PPT绘图窗口当前状态

状态：`PPT_FIGURES_AB_READY_TO_START`

分支：`hrl/vm-tlb-ppt-figures-v0`

权威数据基线：A closeout `74d5fbe6a5ca2411309674cf457baa1efa78f58d`。

本窗口仅绘制两张图：

- 图A：Prefill vs Decode TLB 压力三级路径图；
- 图B：Weight 动态访问占比 vs 64KB 翻译工作集分组柱状图。

执行前必须阅读：

- `FIGURES_AB_HANDOFF.md`
- `FIGURES_AB_ACCEPTANCE_MATRIX.md`
- `FIGURES_AB_REFERENCE_DATA.tsv`

禁止重跑模拟器、修改正式数据或触碰 Window C。完成图、数据复核、视觉检查、commit/push 后停止。