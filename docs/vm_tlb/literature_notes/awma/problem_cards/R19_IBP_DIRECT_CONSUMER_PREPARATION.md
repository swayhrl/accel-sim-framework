# R19 IBP direct consumer：一次性准备卡

状态：`R19_IBP_DIRECT_CONSUMER_CANDIDATE_QUALIFIED`，只资格化下一次独立授权的 Native 证伪；不是执行 Goal、机制参数或论文结论。

## 精确问题与对象

- **Producer**：固定 `AKKamath/Legion-IBP@0b0695fd470695bc6326ac0d2d9d117d422089c5` 的 `StaticCache::transfer`。其 `compress_cpu_transfer_kernel2` 读取 pinned-host IBP 行前缀或 GPU compressed-cache slab，用 `ibp::decompress_fetch_cpu` / `decompress_and_write` 重构 FP32 特征，并把完整的所选节点特征写入 GPU `dst_float_buffer`。
- **Consumer**：同一 Legion GraphSAGE batch 的 `ipc_service.get_next(feat_len)` 返回该 dense `features` 后，训练进程的第一层 GraphSAGE `SAGEConv` 执行邻居聚合/线性变换。该边界在 sampler 与 trainer 两个进程之间；不能假定简单 kernel fusion 已可跨进程成立。
- **边界**：只讨论 sampled minibatch 的 dense feature materialization 与第一次模型读取，不声称整个 Reddit 数据集或所有 embedding 表必须展开。作者已融合缓存查询、fetch 和解压；该已有能力属于强基线。

源码锚点：[Legion transfer kernel](https://github.com/AKKamath/Legion-IBP/blob/0b0695fd470695bc6326ac0d2d9d117d422089c5/sampling_server/src/comp_cache/compress_cache_kernel.cuh#L475-L581)、[buffer 接线](https://github.com/AKKamath/Legion-IBP/blob/0b0695fd470695bc6326ac0d2d9d117d422089c5/sampling_server/src/cache/cache.cu#L781-L795)、[trainer](https://github.com/AKKamath/Legion-IBP/blob/0b0695fd470695bc6326ac0d2d9d117d422089c5/training_backend/legion_graphsage.py#L87-L108)。

## 真实公开输入及 critical-path 依据

使用未放大的 [`dgl.data.RedditDataset()`](https://github.com/AKKamath/Legion-IBP/blob/0b0695fd470695bc6326ac0d2d9d117d422089c5/dataset/prepare_reddit.py#L1-L48)：公开图拓扑、真实节点 FP32 特征与标签；保留作者 GraphSAGE 两跳采样 25/10 及单 GPU IBP(C/M) 路径。不得用随机特征或随机索引替换。作者论文 Figure 9 在 Reddit 的 IBP(C/M) 训练中仍展示非零的等待下一批数据时间，说明 producer 路径并未完全被上一批训练覆盖；源码使 `get_next` 与随后模型消费形成明确依赖。[IBP 原文](https://akkamath.github.io/files/EuroSys26_IBP.pdf)

这仅是继续证伪的必要线索。Figure 9 没有把 dense-buffer 写/重读从采样、PCIe、解码、IPC 中分离，尚不能声称存在 material speedup。

## 强软件基线与数值合同

强基线是作者的完整 Legion+IBP(C/M) 路径：同一 CPU in-place compressed rows、GPU compressed cache、bitmask/Mask/Bitval、真实样本顺序、缓存容量与命中/缺失、GPU 发起 PCIe fetch、异步解码、MPS/stream 配置和 GraphSAGE。另保留作者 Legion 未压缩路径作背景对照；不得只对比弱 CPU 行查找。若后续构造直接消费者诊断，它只能改变 dense-output→首次消费这一个边界，不能换格式、采样、缓存策略或模型。

**Lossless numerical contract**：每个被选中 FP32 feature 的 32-bit pattern 与原始 Reddit 特征逐位相同；节点/边 ID、两跳邻居与顺序、cache 决策、模型权重和计算精度保持一致。第一层输出需与固定 strong baseline 的确定性输出逐位相等；若当前聚合实现/调度无法保证逐位复现，必须先明确浮点求和顺序与容差合同并停止“lossless end-to-end”声称，不得把算法变化算作边界收益。

## 109 上唯一有界 Native 证伪（未来单独授权）

在 GPU lock 下，先固定一个真实 Reddit 训练迭代的实际 sampled IDs/edges 与 IBP cache snapshot，选择确有 host miss 的 batch；固定原始作者命令/配置与一个 batch，不扫 batch size、格式或 cache 容量。每次 replay 恢复同一模型权重、optimizer、RNG 与 cache snapshot；若无法恢复，则不得把反复训练 step 当作匹配响应。做 10 次 warmup、30 次匹配 replay：

1. 记录作者 IBP(C/M) 基线的 sampler `transfer`、`dst_float_buffer` 写入、trainer `get_next` 暴露等待、第一层 GraphSAGE 读取与整步时间；统计相同 batch 的字节与结果 hash。
2. 只对该 batch 做一个有限软件诊断：让首层消费者按原采样/缓存状态直接取得 IBP 解码的 feature tile/行，消除该 batch 在首消费者之前的完整 dense `dst_float_buffer` 写入与重读；保留缓存查找、真实 PCIe fetch、解码工作量、其余层及同样的有限资源。任何跨进程桥接成本计入该诊断，不作为免费服务。
3. 逐位检查重构特征和第一层输出，核对后续模型输出、cache/host miss 数、采样身份与有限资源。报告 matched `get_next` 暴露等待和整步 latency 分布，以及 global-memory traffic；诊断不是硬件速度预测。

预注册停止条件：若 matched 诊断没有缩短暴露等待与整步时间（整步中位数改善 `<5%`），或语义/成本不能匹配，则否定此边界作为值得后续架构研究的问题。若改善达到门槛，也只能说明一个软件实现下有 residual；需再核 closest-work、跨输入稳定性与硬件代价。若 109 的 RTX4080 无法运行固定作者路径或真实 Reddit 数据不合资格，记录 input/platform blocked，不用合成数据代替。

## 最近工作与剩余差别

- [IBP EuroSys 2026](https://akkamath.github.io/files/EuroSys26_IBP.pdf) 已实现 host in-place lossless format、GPU 取数/解压重叠、Legion cache/fetch/decode 合核；不能重新包装这些贡献。
- [DFloat11](https://arxiv.org/html/2504.11651) 提供 GPU 无损 BF16 解码，但先重构权重矩阵再 GEMM。
- [ZipServ](https://arxiv.org/html/2603.17435) 与 [Tan 等 tile-rANS/GEMM](https://arxiv.org/html/2606.15789) 已直接覆盖 GPU resident LLM 权重的解码+GEMM 融合；R19 不以 GEMM 作为新颖性主张。
- [nvCOMP Device API](https://docs.nvidia.com/cuda/nvcomp/device_api.html) / [nvCOMPDx](https://docs.nvidia.com/cuda/nvcompdx/index.html) 已提供 device 内解压构件；“可以在 device 函数中解压”本身不是新意。

尚未核实的差别是：在 IBP 的 pinned-host 行 fetch 与真实 GNN 首层消费之间，避免 dense sampled-feature 往返能否在有限资源和匹配语义下减少暴露等待。此卡只要求一次有界 Native 证伪，不授权实现体系结构机制。
