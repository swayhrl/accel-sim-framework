# 单页PPT两张图绘制任务

状态：`READY_TO_START`

本窗口只负责生成两张用于单页汇报PPT的图，不修改模拟器、配置语义、实验结果或 Window C。

权威数据基线：Framework `74d5fbe6a5ca2411309674cf457baa1efa78f58d`，即 A 的 `C4_COMPLETE_READY_FOR_REVIEW` closeout。

## 目标

只生成两张图：

1. 图A：Prefill 与 Decode 的 TLB 压力路径对比。
2. 图B：Weight 动态访问占比 vs 64KB 翻译工作集占比。

优先复用仓库现有绘图脚本、字体、字号、配色和导出流程；如现有脚本不能表达该布局，可增加小型专用脚本，但不得改研究数据。

输出至少提供 SVG 和 PNG，适合直接插入 PPT；若现有流程自然支持 PDF，可一并导出。

建议输出目录：

`docs/vm_tlb/ppt_figures/llm_memory_onepage/`

建议文件：

- `FIG_A_PREFILL_DECODE_TLB_PRESSURE.svg/png`
- `FIG_B_WEIGHT_ACCESS_VS_TRANSLATION_WORKING_SET.svg/png`
- `FIGURE_DATA_USED.tsv`
- `README.md`

## 图A：Prefill vs Decode TLB 压力

不要做三指标普通柱状图。做成左右两列、三级自上而下的路径/漏斗结构。

标题建议：

`预填充与解码阶段的 TLB 压力来源不同`

列标题：

- `预填充（Prefill）`
- `解码（Decode）`

三级内容：

### 第一级：一级 TLB 未命中率

Prefill：`1.3267%`

计算：`1,246,241 / 93,933,006`

Decode：`0.09161%`

计算：`69,483 / 75,844,615`

### 第二级：进入二级 TLB 后继续未命中的比例

Prefill：`4.5310%`

计算：`56,467 / 1,246,241`

Decode：`34.2602%`

计算：`23,805 / 69,483`

### 第三级：Translation MSHR 满事件

Prefill：

- full-ROI 累计：`0`
- 归一化：`0 events / 1M translation requests`

Decode：

- full-ROI 累计：`2,301,691`
- 归一化：`30.35K events / 1M translation requests`

计算：`2,301,691 / 75,844,615 * 1,000,000 = 30,347.45`

注意：MSHR-full 是 event counter，不能标成“3.03% 的请求”。图中必须显式写 `events / 1M translation requests`。

图A页内结论可放一行短句：

`Prefill 更偏翻译覆盖范围/容量压力；Decode 更偏高代价未命中、并发与长尾压力。`

数据来源：

`docs/vm_tlb/review_packs/M4C_C3_C4_FINAL_CLOSEOUT/TRANSLATION_TOTALS.tsv`

## 图B：Weight 访问量 vs 翻译工作集

采用普通分组柱状图。

标题建议：

`Weight 动态访问占比低，但主导页级翻译工作集`

横轴：

- `预填充（Prefill）`
- `解码（Decode）`

每组两根柱：

- `Weight 动态 lane 访问占比`
- `Weight 占 64KB 唯一页比例`

精确数据：

- Prefill：`15.9773%` vs `87.4066%`
- Decode：`7.8606%` vs `98.9555%`

PPT 数字标签可四舍五入为：

- Prefill：`16%` vs `87%`
- Decode：`8%` vs `99%`

计算来源：

Prefill lane share：
`410255360 / (410255360 + 54935552 + 2102553796)`

Decode lane share：
`63799296 / (63799296 + 25915264 + 721919901)`

Prefill 64KB page share：
`15443 / (15443 + 64 + 2161)`

Decode 64KB page share：
`15443 / (15443 + 82 + 81)`

数据来源：

`docs/vm_tlb/review_packs/M4C_C3_C4_FINAL_CLOSEOUT/C4_TRACE_LOCALITY_SUMMARY.tsv`

在 Decode 组上方增加一条不遮挡柱子的注释：

`97.1% 的 L2 TLB 替换为 Weight → Weight`

计算：`14,494 / 14,926 = 97.1057%`

来源：

`docs/vm_tlb/review_packs/M4C_C3_C4_FINAL_CLOSEOUT/L2_TLB_REPLACEMENT_MATRIX.tsv`

## 视觉与语言要求

- 以中文为主；Prefill、Decode、TLB、MSHR、Weight 等必要术语可保留英文并配中文。
- 图A强调“路径/层级”，不要让三个不同量纲看起来可直接比较大小。
- 图B纵轴为百分比，0–100%；数字直接标在柱顶。
- 不使用 3D、渐变、阴影堆叠等装饰。
- 风格要适合技术领导汇报：简洁、信息密度适中、黑白打印也能区分。
- 如果仓库已有统一科研配色，优先复用；不要为本轮重做整套主题。
- 不要把 `UNKNOWN` 改写成 Activation。

## 禁止事项

- 不重跑任何 simulator。
- 不修改 A 的正式结果。
- 不从 B/C speculative evidence 替换 A 的 full-ROI 数值。
- 不增加第三张图。
- 不把 event counter 误解释成独立请求比例。

## Goal 结束条件

完成两张图、数据复核、视觉自检、提交并推送后停止，最终状态仅允许：

- `PPT_FIGURES_AB_READY_FOR_REVIEW`
- `PPT_FIGURES_AB_HARD_BLOCKER_WITH_EVIDENCE`
