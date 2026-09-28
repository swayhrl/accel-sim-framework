# Grid 与工作集比较合同

本阶段只冻结数学，不包含新 GPU 结果。

- GPT-3 公开 FFN 两个方向均有 603,979,776 个参数，FP16 单矩阵 1,207,959,552 B。
- W4 proxy 的 qweight 为 301,989,888 B（288 MiB），约为 64 MiB L2 的 4.500000 倍；旧 Qwen qweight 为 33,947,648 B，约为 L2 的 0.505859 倍。
- M1 split1 grid 从旧 Qwen expand-like/contract-like 的 148/28 增至 GPT-3 proxy 的 384/96。
- M256 split1 grid 从 2368/448 增至 6144/1536；split8 始终是对应 split1 的8倍。
- 这些只定位并行供给、workspace/reduction 与工作集尺度；不能仅凭 grid 或 qweight/L2 宣布 timing 或 cache 因果。

未来正式比较只匹配同一 accepted split8/split1 implementation family、相同 WARM_SAME_ARM/EVICT_CONDITIONED protocol、相同 role 和 M。Qwen up/down 与 GPT-3 expand/contract 只是形状方向类比。
