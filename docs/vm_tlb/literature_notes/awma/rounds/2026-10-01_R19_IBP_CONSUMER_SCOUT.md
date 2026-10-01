# R19 Lane E: IBP 解压到真实消费者的边界

日期：2026-10-01。审查方式：174-new CPU/source only；未运行 CUDA、GPU 或 Accel-Sim。

结论：`R19_IBP_DIRECT_CONSUMER_CANDIDATE_QUALIFIED`，仅限公开 Reddit / Legion GraphSAGE 的准备与一次有界 Native 证伪。它不是机制实现、性能结果或创新性结论。LLM 权重 GEMM 的“解码即计算”概念已有直接近邻，不能作为这张卡的新颖性依据。

## 固定源码核对

主仓库是 [`AKKamath/InvariantBitPacking@b2f71003113defb4e387caf18843b241f6280ba9`](https://github.com/AKKamath/InvariantBitPacking/tree/b2f71003113defb4e387caf18843b241f6280ba9)。作者仓库在此提交固定的四个相关子模块分别是 InfiniGen-IBP `529e2e31335aa65791d0ef17d718d593691591f7`、DGL-IBP `eafc5b39176c50cd8a979179ffd7ec9f7c864cfb`、Legion-IBP `0b0695fd470695bc6326ac0d2d9d117d422089c5`、ColossalAI `151938279a63d5901a46bd997145342116d1267e`。路径、blob 与行锚点详见 review pack 的 `SOURCE_REGISTER.tsv`。

1. **压缩字节位置。** [`compress_inplace`](https://github.com/AKKamath/InvariantBitPacking/blob/b2f71003113defb4e387caf18843b241f6280ba9/src/compress.cu#L176-L235) 接受 CUDA 或 pinned-host tensor，并将同一个 `dataset_data` 同时作为输入与输出。CPU 行槽仍按未压缩大小分配，只有压缩前缀需经 PCIe 读取；压缩参与 bitmask 在 GPU，Mask/Bitval 元数据供设备解码。作者论文 §5 明说 in-place CPU 布局保留原容量以维持固定行索引。[IBP 原文](https://akkamath.github.io/files/EuroSys26_IBP.pdf)
2. **重构字节位置。** [`src/decompress.cu`](https://github.com/AKKamath/InvariantBitPacking/blob/b2f71003113defb4e387caf18843b241f6280ba9/src/decompress.cu#L110-L155) 选取调用者的完整形状 `output_tensor`，否则分配 `{num_vecs, vec_size}` 的张量；随后将其指针传给独立解压 kernel。[warp 与 TB kernel](https://github.com/AKKamath/InvariantBitPacking/blob/b2f71003113defb4e387caf18843b241f6280ba9/include/decompress/ibp_decompress_kernel.cuh#L16-L111) 向 `output[...]` 写每个重构向量；[device helper](https://github.com/AKKamath/InvariantBitPacking/blob/b2f71003113defb4e387caf18843b241f6280ba9/include/decompress/ibp_decompress_dev.cuh#L130-L335) 最终执行 `dest[i] = temp_dest`。GPU 输出是完整的所选向量集合，不必是整个原始数据集。
3. **作者真实集成。** FlexGen 的 [CPU→GPU copy hook](https://github.com/AKKamath/InfiniGen-IBP/blob/529e2e31335aa65791d0ef17d718d593691591f7/speedup/flexgen/original/pytorch_backend.py#L1143-L1162) 把权重写入预分配 `dst_tensor`，之后 [Gemma 的 `F.linear`](https://github.com/AKKamath/InfiniGen-IBP/blob/529e2e31335aa65791d0ef17d718d593691591f7/speedup/flexgen/original/flex_gemma.py#L854-L867) 读取 dense 权重。InfiniGen 的 [KV selection](https://github.com/AKKamath/InfiniGen-IBP/blob/529e2e31335aa65791d0ef17d718d593691591f7/speedup/infinigen/infinigen/kv_selection_controller.py#L29-L74) 返回完整的 `selected_k/v` GPU tensor，后续 attention 是另一操作。DGL 的 [feature storage `fetch`](https://github.com/AKKamath/DGL-IBP/blob/eafc5b39176c50cd8a979179ffd7ec9f7c864cfb/python/dgl/storages/pytorch_tensor.py#L28-L97) 返回所选行的 dense GPU tensor。ColossalAI [cache manager](https://github.com/AKKamath/ColossalAI/blob/151938279a63d5901a46bd997145342116d1267e/colossalai/legacy/nn/parallel/layers/cache_embedding/cache_mgr.py#L519-L559) 先解压缺失行到 GPU 临时 tensor，再 `index_copy_` 入 dense cache；[`CachedEmbeddingBag.forward`](https://github.com/AKKamath/ColossalAI/blob/151938279a63d5901a46bd997145342116d1267e/colossalai/legacy/nn/parallel/layers/cache_embedding/cached_embedding.py#L123-L143) 随后调用 `F.embedding_bag`。这里不能说“整个表在每批都展开”；只展开缺失行。
4. **device helper 不等于 compute fusion。** IBP 有 `__device__` 解压函数。Legion 的 [压缩缓存/CPU 取特征 kernel](https://github.com/AKKamath/Legion-IBP/blob/0b0695fd470695bc6326ac0d2d9d117d422089c5/sampling_server/src/comp_cache/compress_cache_kernel.cuh#L475-L581) 已把缓存查询、PCIe fetch 和解压合到一个 transfer kernel；它仍把所选节点的所有特征写到 `output_features`。[`cache.cu`](https://github.com/AKKamath/Legion-IBP/blob/0b0695fd470695bc6326ac0d2d9d117d422089c5/sampling_server/src/cache/cache.cu#L781-L795) 把它接到 `dst_float_buffer`；训练进程 [`get_next` 后调用 GraphSAGE](https://github.com/AKKamath/Legion-IBP/blob/0b0695fd470695bc6326ac0d2d9d117d422089c5/training_backend/legion_graphsage.py#L87-L108)。固定子模块中未找到同一 kernel 的 IBP 解压+GraphSAGE 聚合、解压+`F.embedding_bag` 或解压+GEMM；这是对这些固定源码路径的有界检查，不是对所有可能实现的否定。

## 真实 critical-path 线索及其限制

作者的 [Legion Reddit 数据准备](https://github.com/AKKamath/Legion-IBP/blob/0b0695fd470695bc6326ac0d2d9d117d422089c5/dataset/prepare_reddit.py#L1-L48) 直接使用 `dgl.data.RedditDataset()` 的图、标签及 FP32 节点特征；Reddit 不是论文中 Pubmed/Citeseer/Cora 的放大版本。作者论文 Figure 9 将 Legion 训练与等待下一批数据的时间分开；Reddit 的 IBP(C/M) 仍有可见等待。源码中 `ipc_service.get_next` 必须先返回完整 `features`，GraphSAGE 才能处理该 batch。因而这是有真实输入和暴露等待的 producer→consumer 依赖链。[论文 Figure 9 与 §6.2](https://akkamath.github.io/files/EuroSys26_IBP.pdf)

**尚未证明的是** dense buffer 的写入与首消费者重读占该等待的多少；等待还含采样、PCIe、解码和 IPC。作者 Figure 7 对 dense 数据报告接近 ideal compressed-transfer throughput，提示解码开销常被传输隐藏。必须先用同一 batch、同一 cache 状态的有界 Native 干预证伪，而不能把整段 `Wait` 归因给 materialization。

DLRM 作者实验使用公开的 NVIDIA/Criteo 预训练表，但 [`tests/dlrm_comp_merged.py`](https://github.com/AKKamath/InvariantBitPacking/blob/b2f71003113defb4e387caf18843b241f6280ba9/tests/dlrm_comp_merged.py#L109-L121) 为查找生成 `torch.randint` 索引；这些索引不是公开真实查询流，故本轮不用它替代 Reddit 的真实训练 batch。FlexGen 的 dense 权重路径是真实的，但 GEMM 融合近邻已很强。

## 最近原始工作与四种能力

| 工作 | 压缩格式 | 传输重叠 | 设备解压 | 直接压缩执行 |
| --- | --- | --- | --- | --- |
| [IBP EuroSys 2026](https://akkamath.github.io/files/EuroSys26_IBP.pdf) | invariant-bit lossless，CPU 原行槽 in-place，另有 GPU compressed cache | GPU 发起 zero-copy/异步 PCIe fetch 与解码 | 是；warp/TB kernel 与可复用 device helper | 缓存查找+取特征+解压已融合；仍写 dense minibatch；未见 GraphSAGE/GEMM/embedding 直接消费压缩数据 |
| [DFloat11](https://arxiv.org/html/2504.11651) | BF16 指数动态长度无损编码 | 主要是 GPU resident 权重，不是 IBP 的 pinned-CPU fetch | 两阶段、Transformer-block 粒度 | 解压 BF16 矩阵后执行计算；非 fused GEMM |
| [ZipServ](https://arxiv.org/html/2603.17435) | 固定长 TCA-TBE BF16 无损权重格式 | 其重点是 GPU resident serving | 是 | decode 用 ZipGEMM 将解码结果直接送 Tensor Core；prefill 则先展开到 global memory。已直接覆盖“LLM 权重解压+GEMM”概念 |
| [Tan 等 2026 ANS/GEMM](https://arxiv.org/html/2606.15789) | tile 对齐 rANS 无损权重流 | GPU resident tile 流水 | 是 | decoded tile 直接进入 shared memory 并供 GEMM 消费；再次强化 GEMM 近邻 |
| [NVIDIA nvCOMP Device API](https://docs.nvidia.com/cuda/nvcomp/device_api.html) / [nvCOMPDx](https://docs.nvidia.com/cuda/nvcompdx/index.html) | 多种通用 codec | API 本身不证明应用的 PCIe 重叠 | 可在 `__device__` 调用 | 提供构件，不是已核实的 IBP+GraphSAGE consumer 实现 |

格式创新、PCIe 重叠、设备端解压和真实 compute consumer fusion 是不同事实。ZipServ/Tan 已否定将“直接解码进 GEMM”作为 R19 的新颖性陈述。Reddit GraphSAGE 边界只获准进入准备卡，closest-work 差别与性能价值均等待证伪。

R53 更正已存在于 [`2026-10-01_ROUND18_ERRATUM_R53_EXECUTION.md`](2026-10-01_ROUND18_ERRATUM_R53_EXECUTION.md) 并由文献 README 链接；最终 `R53_ALGORITHM_CHANGE_NOT_MAPPING_GAIN_V1`。本轮核对后没有重复改写该更正，也未复跑 R53。
