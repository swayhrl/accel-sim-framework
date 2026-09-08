# 单页 PPT：LLM memory 两张图

状态：`PPT_FIGURES_AB_READY_FOR_REVIEW`。

本目录只包含两张可直接插入 PPT 的图及其数据清单；没有运行 simulator、生成
trace，或修改 A/C4 正式数据。权威输入是 A closeout
`74d5fbe6a5ca2411309674cf457baa1efa78f58d` 中的：

- `docs/vm_tlb/review_packs/M4C_C3_C4_FINAL_CLOSEOUT/TRANSLATION_TOTALS.tsv`
- `docs/vm_tlb/review_packs/M4C_C3_C4_FINAL_CLOSEOUT/C4_TRACE_LOCALITY_SUMMARY.tsv`
- `docs/vm_tlb/review_packs/M4C_C3_C4_FINAL_CLOSEOUT/L2_TLB_REPLACEMENT_MATRIX.tsv`

## 输出

- `FIG_A_PREFILL_DECODE_TLB_PRESSURE.svg/png`：左右两列、逐级向下的
  L1 miss → L2 continued miss → Translation MSHR-full 路径。MSHR-full 明确为
  event counter；Decode 同时列出 full-ROI `2.30M` 与 `30.35K events / 1M
  translation requests`，不把它解释为请求发生率。
- `FIG_B_WEIGHT_ACCESS_VS_TRANSLATION_WORKING_SET.svg/png`：Weight 动态 lane
  访问占比和 64KB 唯一页工作集占比的分组柱状图，并标记 Decode 的 `97.1%`
  Weight → Weight L2 TLB 替换。
- `FIGURE_DATA_USED.tsv`：全部原始分子、分母、公式、精确复算值、显示值、
  authority TSV SHA-256 和逐行 assertion 结果。

SVG 适用于 PPT 矢量插入；PNG 为 1920×1080 的快速预览。中文字体优先使用
`Noto Sans CJK SC`，并在 SVG 中给出 `Microsoft YaHei`/sans-serif fallback。

## 再生成与数据断言

```bash
python3 util/vm_tlb/plot_ppt_onepage_figures.py
```

脚本先从三个 authority TSV 解析 generic full-ROI 行，再计算全部 13 个图表值；
每个原始分子/分母和复算值都必须与
`docs/vm_tlb/codex_handoff/ppt_onepage/FIGURES_AB_REFERENCE_DATA.tsv` 一致。
它还断言 Decode replacement matrix 的 9 个单元之和等于 L2 TLB eviction 总数。
任一输入或数值漂移会以非零退出码停止出图。

## 视觉检查

已实际检查 Pillow 生成的两张 PNG，以及以 LibreOffice 渲染 SVG 后的 PNG：

- 图 A 去除了会与卡片相叠的层级标记，并将 MSHR 归一化文本上移，保持三级箭头
  路径、卡片、结论和 event-counter 注记彼此分离；
- 图 B 为接近 100% 的 Decode 页工作集标签预留顶部空间，并将柱顶标签改为居中
  定位，避免与柱体、100% 网格线和替换注释重叠；
- 两种渲染均确认没有裁切、中文缺字或重叠。

除这两张图外，本轮没有第三张图。
