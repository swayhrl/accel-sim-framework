# C16 OLMoE 多轮路由独立 consumer（174-new）

这是 CPU-only 独立重算。未使用 GPU、未申请 GPU lock、未读取 Lane4 partial，也未修改 producer 或旧 Lane6 结果。

## 主结论

采集可用，历史 TEXT 专家集合和输出序列在显式 cached-greedy runner 下得到复现；但主周期随输入族改变。PROSE 的 lag11 只是相对单cell描述性 p95 的弱超线，且不是主峰，因此不能据 producer 机械分类声称强11步周期跨输入成立。

请按以下顺序审阅：

1. `AUTHORITY_AND_SEQUENCE_CHECKS.json`
2. `SCIENTIFIC_INTERPRETATION.md`
3. `FINAL_DECISION.json`
4. `RECOMPUTED_LAG_METRICS.tsv` 与 `RECOMPUTED_TOKEN_METRICS.tsv`
5. `ROBUSTNESS_DIAGNOSTICS.tsv` 与 `TOKEN_CONDITIONAL_CHECK.json`
6. `PRODUCER_COMPARISON.tsv` 与 `HISTORICAL_COMPARISON.tsv`
7. `SHA256SUMS`

主指标按 producer 的 NumPy `default_rng(20260928)`、每个 session/layer/lag 重置 seed、1000 次 whole-step permutation 和线性 quantile 独立实现。结果可见后的检查单独标记，不修改原门槛。

生成器：`util/vm_tlb/c16/olmoe_multiround_independent_consumer.py`；最小测试：`tests/vm_tlb/c16/test_olmoe_multiround_independent_consumer.py`。
