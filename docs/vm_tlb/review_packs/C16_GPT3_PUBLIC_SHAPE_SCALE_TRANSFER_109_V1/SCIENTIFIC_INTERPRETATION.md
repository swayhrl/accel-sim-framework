# 科学解释（producer侧描述性）

本结果只使用GPT-3公开FFN尺寸；Dense是合成FP16 shape anchor，W4是既有AutoAWQ内核的机制代理。它们都不是GPT-3原始权重、自然激活或完整模型性能。

- `EXPAND_M1`：gain_W=24.103%，gain_E=24.939%，state interaction=-0.836个百分点；Dense median=1.802240 ms。
- `EXPAND_M256`：gain_W=-71.014%，gain_E=-73.630%，state interaction=2.615个百分点；Dense median=3.098624 ms。
- `CONTRACT_M1`：gain_W=-63.915%，gain_E=-51.518%，state interaction=-12.397个百分点；Dense median=1.806640 ms。
- `CONTRACT_M256`：gain_W=-36.023%，gain_E=-35.057%，state interaction=-0.967个百分点；Dense median=3.019776 ms。

M1是否因更大N而减少对split8额外CTA的依赖、M256方向是否延续旧7B结果、以及>4×L2 qweight下W/E交互如何变化，以上仅作为producer观察列示；最终scale-transfer判断留给Lane6独立consumer。EXPAND与CONTRACT的grid、workspace和reduction差异共同变化，producer不建立通用预测器。NCU计数按kernel保留，不归因到具体tensor，也不证明唯一L2/cache/TLB机制。
