# 判定

`R19_IBP_DIRECT_CONSUMER_CANDIDATE_QUALIFIED`

**资格范围。** Legion / Reddit 的真实 sampled FP32 节点特征在作者 IBP(C/M) producer 中完整写入 GPU `dst_float_buffer`，trainer 从 `ipc_service.get_next` 接收 dense `features`，然后执行第一层 GraphSAGE。作者论文 Figure 9 对未经放大的 Reddit 显示 IBP 后仍有非零的 exposed sampler wait。这满足“真实公开输入 + 可处于 critical path 的独立 producer→consumer 边界”准备门槛。

**未被证明。** Figure 9 的等待包含采样、缓存、PCIe、解压和 IPC；没有单独测量 dense buffer 写/重读的时间，也没有在 109 上验证直接消费会更快。准备卡只预注册一次匹配 Native 证伪。当前没有机制、参数、硬件收益或论文新颖性结论。

**排除的宽泛声称。** FlexGen 的权重确实先写完整 dense GPU tensor 再由 `F.linear` 使用，但 ZipServ 与 tile-rANS/GEMM 已公开直接解码+GEMM；不能把此概念作为 R19 的创新。IBP 自身已有 device 解压 helper 及 Legion cache lookup/fetch/decode 合核；也不能把“设备端解压”或“解压与 PCIe 重叠”重新作为空白。

**另一路未升级。** ColossalAI 的 DLRM 路径解压 miss rows 到 GPU 临时 tensor，再写 dense cache，`F.embedding_bag` 从 cache 读；作者 benchmark 使用公开预训练表，但查找索引由 `torch.randint` 生成。本轮不把随机查询称为真实公开 query stream。

R53 纠正已在 Round18 erratum 与 literature README 中存在：`R53_ALGORITHM_CHANGE_NOT_MAPPING_GAIN_V1`；本轮仅核对，无复跑。
