# 未闭合项

1. Figure 9 的 `Wait` 不是 dense materialization 的独立计时；尚不知道这段 write/read 是否有足够可回收的真实 critical-path 成本。
2. Legion sampler 与 trainer 分进程。直接消费者诊断须计入跨进程数据/同步成本，不允许将 on-chip handoff 视为免费。
3. 压缩输入和大部分其他开销可能受 PCIe 主导；作者 Figure 7 对 dense 数据报告接近理想压缩传输吞吐，提示可能无 material residual。
4. 109 RTX4080 与作者 A100 的环境/容量不同；公开 Reddit 数据、原模型/依赖和单 GPU IBP 路径在 109 尚未资格化。未取得 dataset bytes、运行 receipt 或 GPU 性能值。
5. 直接 GraphSAGE 消费必须保持采样、cache 命中/缺失及 FP32 聚合顺序。若改变浮点输出，不能称为 lossless 同一计算。
6. 最近邻调查为有界原始来源检查；尚未证明相对于所有可能 GNN/embedding 融合工作的全球新颖性。
