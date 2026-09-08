# 单页PPT两张图验收标准

## 图A数据验收

| 检查项 | 期望值/条件 | 结果要求 |
|---|---|---|
| Prefill L1 TLB miss rate | 1.3267% | 必须由 1,246,241 / 93,933,006 复算 |
| Decode L1 TLB miss rate | 0.09161% | 必须由 69,483 / 75,844,615 复算 |
| Prefill L2 continued miss | 4.5310% | 必须由 56,467 / 1,246,241 复算 |
| Decode L2 continued miss | 34.2602% | 必须由 23,805 / 69,483 复算 |
| Prefill MSHR-full | 0 | full-ROI累计 |
| Decode MSHR-full | 2,301,691 | full-ROI累计 |
| Decode normalized MSHR-full | 30.35K events / 1M requests | 不能写成请求百分比 |
| 数据来源 | A/C4 `TRANSLATION_TOTALS.tsv` | 禁止混入 B/C speculative 数据 |

## 图A视觉验收

- 左右两列：Prefill / Decode。
- 自上而下三级路径：L1 TLB miss → L2 continued miss → MSHR-full。
- 不用三指标共轴柱状图。
- 第三级同时保留累计值和归一化值，且注明 event counter 语义。
- 图内主结论不超过一行。
- 中文标签优先。

## 图B数据验收

| 检查项 | 精确值 | PPT可显示 |
|---|---:|---:|
| Prefill Weight lane share | 15.9773% | 16% |
| Prefill Weight 64KB page share | 87.4066% | 87% |
| Decode Weight lane share | 7.8606% | 8% |
| Decode Weight 64KB page share | 98.9555% | 99% |
| Decode L2 TLB Weight→Weight replacement share | 97.1057% | 97.1% |

来源必须分别绑定：

- `C4_TRACE_LOCALITY_SUMMARY.tsv`
- `L2_TLB_REPLACEMENT_MATRIX.tsv`

## 图B视觉验收

- 分组柱状图，横轴仅 Prefill、Decode 两组。
- 每组两根柱：动态访问占比、64KB唯一页比例。
- 纵轴统一 0–100%。
- 柱顶显示百分比。
- Decode 上方标注 `97.1% 的 L2 TLB 替换为 Weight → Weight`。
- 注释不得遮挡柱或数据标签。

## 输出与工程验收

必须生成：

- SVG：用于 PPT 矢量插图。
- PNG：用于快速预览。
- `FIGURE_DATA_USED.tsv`：记录全部原始值、公式、显示值、来源文件。
- README：记录生成命令与依赖。

提交前：

1. 重新从权威 TSV 解析并计算全部指标；不得手工只抄最终百分比。
2. 若脚本中存在硬编码数据，必须同时实现 source assertion：解析到的原始值与预期完全一致，否则失败。
3. 打开 PNG/SVG 做视觉检查：无裁切、无重叠、中文字体可读、标注清晰。
4. `git diff --check` PASS。
5. 只显式 stage 本轮文件，禁止 `git add .` / `git add -A`。
6. commit 并 push 到 `hrl/vm-tlb-ppt-figures-v0`。

## Scope guard

以下任一行为直接判定不通过：

- 重跑模拟器；
- 修改任何正式 C3/C4 数值；
- 将 `MSHR-full events / requests` 表达成请求发生率；
- 把 UNKNOWN 归类成 Activation；
- 增加与本页无关的第三张图；
- 修改 Window C 功能代码或配置。

最终状态：`PPT_FIGURES_AB_READY_FOR_REVIEW`。