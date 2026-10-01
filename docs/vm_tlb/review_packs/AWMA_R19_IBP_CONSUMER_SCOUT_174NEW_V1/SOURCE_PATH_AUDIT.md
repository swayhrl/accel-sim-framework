# 固定源码路径审计

Authority：`AKKamath/InvariantBitPacking@b2f71003113defb4e387caf18843b241f6280ba9`；四个作者子模块 SHA 与文件 blob 见 `SOURCE_REGISTER.tsv`。所有判断为源码静态检查，未编译、未运行。

| 问题 | 有界源码结论 |
| --- | --- |
| compressed bytes 在哪里？ | `compress_inplace` 对 CUDA 或 pinned-host dataset 原位改写。CPU offload 案例仍保留每行原长度槽位，只读压缩前缀；GPU bitmask 和 Mask/Bitval 指示压缩状态。Legion 还可把压缩行放入 GPU cache slab。 |
| reconstructed bytes 写到哪里？ | `decompress_fetch` 接受完整 `{num_vecs,vec_size}` `output_tensor`，或创建该形状的新 tensor。device helper 对 `dest[i]` 写每个重构元素；未压缩行也复制到同一输出。FlexGen 写整块权重目的 tensor；DGL/InfiniGen 生成所选行 dense tensor；Legion 写所选 minibatch 的 `output_features`。 |
| consumer 是否必须读取完整 dense buffer？ | 在**作者已发布集成路径**中，FlexGen `F.linear` 使用解压完成的 dense 权重；Legion `get_next` 交付完整 sampled-feature tensor 后 GraphSAGE 才开始该 batch；DGL 返回 dense 所选行；ColossalAI 对 miss rows 先建临时 dense tensor、更新 dense cache，后由 `F.embedding_bag` 读取。这里的“完整”指各路径的目标张量/所选 minibatch 或 miss rows，绝非每批展开整个数据集。源码不证明每个元素都在同一 kernel 中被读取。 |
| 已有 decompress-inside-consumer/device-function 路径？ | `ibp_decompress_dev.cuh` 和 `ibp_dev_func.cuh` 提供 `__device__` 解压函数。Legion 已在**特征 transfer/cache kernel** 内调用设备 helper，同时完成缓存查找和 fetch。若把 transfer/cache 本身称作 consumer，已有融合；若 consumer 指 GraphSAGE、GEMM、attention 或 embedding 算子，则固定源码未见其内部调用解压 helper。 |
| 已有真正 fused decompress+GEMM/embedding/message-passing？ | 对固定主仓库和所审四个 pinned 子模块，未找到这些计算消费者的融合实现。ZipServ 与另一 tile-rANS/GEMM 原始工作已公开 GEMM 方向的直接融合，见 `CLOSEST_WORK.md`。 |

## 精确路径

```text
pinned host IBP row slots / compressed GPU cache slab
  -> Legion StaticCache::transfer
  -> compress_cpu_transfer_kernel2 / cache decode helper
  -> full sampled-feature dst_float_buffer in GPU global memory
  -> IPC get_next delivers dense features
  -> first GraphSAGE SAGEConv on that sampled graph block
```

对应关键源码：[IBP compress](https://github.com/AKKamath/InvariantBitPacking/blob/b2f71003113defb4e387caf18843b241f6280ba9/src/compress.cu#L176-L235)、[IBP fetch output](https://github.com/AKKamath/InvariantBitPacking/blob/b2f71003113defb4e387caf18843b241f6280ba9/src/decompress.cu#L110-L155)、[Legion transfer](https://github.com/AKKamath/Legion-IBP/blob/0b0695fd470695bc6326ac0d2d9d117d422089c5/sampling_server/src/comp_cache/compress_cache_kernel.cuh#L475-L581)、[cache buffer](https://github.com/AKKamath/Legion-IBP/blob/0b0695fd470695bc6326ac0d2d9d117d422089c5/sampling_server/src/cache/cache.cu#L781-L795)、[trainer](https://github.com/AKKamath/Legion-IBP/blob/0b0695fd470695bc6326ac0d2d9d117d422089c5/training_backend/legion_graphsage.py#L87-L108)。
