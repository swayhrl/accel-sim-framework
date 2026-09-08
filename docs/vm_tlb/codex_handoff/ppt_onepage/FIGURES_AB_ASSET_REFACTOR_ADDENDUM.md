# 单页PPT图A/B 去PPT化资产重构追加指令

状态：`AUTHORIZED_ASSET_REFACTOR`

分支：`hrl/vm-tlb-ppt-figures-v0`

权威数据基线保持不变：A closeout `74d5fbe6a5ca2411309674cf457baa1efa78f58d`。

本追加指令只改变图形资产的呈现层级，不改变任何数据、公式、科学结论或正式 C3/C4 证据。

## 1. 目标

把现有两张图从“独立小型幻灯片”重构为“可直接嵌入真正 PPT 页面中的图形资产”。

当前两图的技术结构和数据逻辑保留，但必须删除由 PPT 页面本身承担的元素：大标题、副标题、页脚说明、结论框、顶部横线、过大的外围白边和不必要的说明性装饰。

输出应像科研论文/PPT中的 figure asset，而不是一张已经完成排版的 slide。

## 2. 图A要求

保留：

- 左列：预填充（Prefill）；
- 右列：解码（Decode）；
- 自上而下三级路径：
  1. 一级 TLB 未命中率；
  2. 进入二级 TLB 后继续未命中比例；
  3. Translation MSHR-full；
- Prefill/Decode 可继续用当前蓝/橙阶段色；
- Decode MSHR-full 同时保留：`full-ROI 累计约 2.30M` 和 `30.35K events / 1M translation requests`。

删除：

- 图内大标题；
- 图内副标题；
- 顶部装饰横线；
- 底部大结论框；
- 底部脚注；
- 模拟整张幻灯片的外围白色画布/留白。

建议进一步简化三级节点：节点只保留“大数字 + 短标签 + 必要分母/原始计数”，不再使用大面积卡片。可以使用细竖线、轻量圆角框或直接文字布局，但应保证两列对齐、三级路径一眼可读。

不要把图A称为严格比例漏斗；三个层级分母不同，视觉上是“地址翻译压力路径对比”，不是面积有数学比例意义的 funnel chart。

## 3. 图B要求

保留：

- 横轴：Prefill / Decode；
- 每组两根柱：Weight 动态 lane 访问占比、Weight 占 64KB 唯一页工作集比例；
- 数据：Prefill 15.98% / 87.41%，Decode 7.86% / 98.96%；
- Decode 附近标注：`97.1% L2 TLB 替换：Weight → Weight`。

删除：

- 图内大标题；
- 图内副标题；
- 顶部横线；
- 大型 callout 卡片；
- 页脚注释；
- 过大的 legend 与外围白边。

优先直接在柱上或柱下使用短标签表达两种指标，减少读者在柱与 legend 之间来回寻找。若保留 legend，必须极简且不占据明显垂直空间。

`97.1%` 标注必须明确写 `L2 TLB`，不得只写 `L2`，避免被误解为 L2 Data Cache replacement。

## 4. 输出规格

对两张图均要求：

- 优先透明背景 SVG；
- 同时输出高分辨率 PNG；
- 紧裁边界，尽量少外围留白；
- 中文优先；
- 数字、轴、短标签清晰；
- 无 3D、复杂渐变、装饰性大边框；
- 适合插入 16:9 技术汇报 PPT 后由页面标题、结论文字统一组织。

建议输出新文件，不覆盖当前 review-ready 原图：

- `FIG_A_PREFILL_DECODE_TLB_PRESSURE_ASSET.svg/png`
- `FIG_B_WEIGHT_ACCESS_VS_TRANSLATION_WORKING_SET_ASSET.svg/png`

当前原图继续保留作为历史版本。

## 5. 数据不允许变化

必须继续从权威 TSV 重新解析，并与现有 `FIGURE_DATA_USED.tsv` / `FIGURES_AB_REFERENCE_DATA.tsv` 逐项一致。

禁止：

- 重跑 simulator；
- 修改任何原始 C3/C4 数据；
- 修改百分比计算口径；
- 把 `UNKNOWN` 重命名为 Activation；
- 接触 Window C 功能/性能实验。

## 6. 视觉验收

必须实际查看最终 PNG/SVG 渲染，检查：

- 无文字裁切；
- 无重叠；
- 中文字体正常；
- 插入 PPT 后无需再次裁去大量白边；
- 图 A 左右两列和三级路径清楚；
- 图 B 两组柱和 97.1% 注释可快速理解；
- 图自身不再像完整 PPT 页面。

如果现有脚本结构导致难以去掉 slide 元素，可以对绘图脚本做小型重构，但不重新设计数据。

## 7. 结束条件

完成数据 assertion、视觉检查、显式路径 staging、commit/push 后停止。

最终状态：

- `PPT_FIGURES_AB_ASSETS_READY_FOR_REVIEW`
- 或真正不可安全解决时 `PPT_FIGURES_AB_ASSET_REFACTOR_BLOCKED_WITH_EVIDENCE`
