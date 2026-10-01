# AWMA R19 IBP consumer scout — Lane E / 174-new

结论：`R19_IBP_DIRECT_CONSUMER_CANDIDATE_QUALIFIED`。

唯一准备对象是公开 Reddit 数据上的 Legion+IBP(C/M) sampled-feature buffer 到首层 GraphSAGE 消费者。固定 IBP 源码仍物化完整的 **所选 minibatch** dense 特征；作者已将缓存查询、host fetch 与解压融合，因此剩余边界更窄。作者 Figure 9 的 Reddit 路径有暴露的下一批数据等待，但未量化 dense materialization 的独立代价。准备卡给出一次有界 Native 证伪，需另行授权。

阅读顺序：

1. [`DECISION.md`](DECISION.md)
2. [`SOURCE_PATH_AUDIT.md`](SOURCE_PATH_AUDIT.md)
3. [`CLOSEST_WORK.md`](CLOSEST_WORK.md)
4. [`SOURCE_REGISTER.tsv`](SOURCE_REGISTER.tsv)
5. [`VALIDATION_SUMMARY.md`](VALIDATION_SUMMARY.md)、[`OPEN_ISSUES.md`](OPEN_ISSUES.md)
6. [`RAW_DATA_INDEX.tsv`](RAW_DATA_INDEX.tsv)、`SHA256SUMS`

完整中文文献记录：[`2026-10-01_R19_IBP_CONSUMER_SCOUT.md`](../../literature_notes/awma/rounds/2026-10-01_R19_IBP_CONSUMER_SCOUT.md)。准备卡：[`R19_IBP_DIRECT_CONSUMER_PREPARATION.md`](../../literature_notes/awma/problem_cards/R19_IBP_DIRECT_CONSUMER_PREPARATION.md)。

本阶段 CPU/source only；未启动 109、CUDA、GPU lock、Accel-Sim 或新的 execution Goal。
