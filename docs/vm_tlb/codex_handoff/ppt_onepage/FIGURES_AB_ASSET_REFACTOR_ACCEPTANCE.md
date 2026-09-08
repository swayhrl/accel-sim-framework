# 单页PPT图A/B 资产重构验收标准

本文件只验收呈现层级，不重新验收科学数据定义。

必须全部满足：

- [ ] 两张图均已生成新的 `*_ASSET.svg` 与 `*_ASSET.png`。
- [ ] 数据与 `FIGURES_AB_REFERENCE_DATA.tsv` 完全一致。
- [ ] 图A保留 Prefill/Decode 两列三级翻译压力路径。
- [ ] 图A没有大标题、副标题、顶部横线、底部结论框、页脚脚注。
- [ ] 图A Decode 同时显示 full-ROI `~2.30M` 与 `30.35K events / 1M translation requests`，且没有写成请求比例。
- [ ] 图B保留 15.98/87.41、7.86/98.96 四个权威值。
- [ ] 图B明确标注 `97.1% L2 TLB 替换：Weight → Weight`。
- [ ] 图B没有大型标题/副标题/callout/页脚和过大的 legend。
- [ ] SVG 优先为透明背景；PNG 紧裁且外围留白少。
- [ ] 实际视觉检查确认无裁切、重叠、异常字体。
- [ ] 两图作为单独 figure asset 插入 PPT 后不呈现“PPT 中嵌 PPT”的观感。
- [ ] 未重跑 simulator，未修改 C3/C4 正式数据，未触碰 Window C。
- [ ] `git diff --check` PASS；仅显式路径 staging；已 commit/push。

最终只能报告：

`PPT_FIGURES_AB_ASSETS_READY_FOR_REVIEW`

或有证据的 hard blocker。
