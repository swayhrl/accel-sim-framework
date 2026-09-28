# 后续实现上下文

仅作后来实现背景，不替代V26/V27 authority。审计固定于Transformers commit `07338b6c74a578868368e6e549dea83414e4b8cb`（2026-09-27）及`modeling_deepseek_v2.py` blob `a51ac0266263945af68fa6b84cf5a71d84198c79`、`modular_deepseek_v2.py` blob `9717b12b17d4aba970e1dc6d3f64a46f840181be`。

该实现把`k_nope`整理为`[B,1,T,512]`、`k_pe`为`[B,1,T,64]`，先调用cache update，再执行`expand_kv`生成每头K/V。这说明公开实现后来已经能够避免V26/V27的展开persistent cache。源码结构不能单独证明性能更好。
