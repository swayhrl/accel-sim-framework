# P2 selector contract

Implementation label: `QUEST_STYLE_SELECTOR_DIAGNOSTIC_V1`; this is not a full Quest reproduction and does not claim that the dense Qwen model naturally deploys sparse attention.

For layer-12 Qwen2.5-0.5B decode-step1 Q and the first 8,192 historical K/V tokens:

- page size: 16 tokens; 512 pages;
- per physical KV head and channel, precompute page `K_min` and `K_max` outside the query-time chain;
- score in FP32: `sum_i max(q_i*K_min_i, q_i*K_max_i)`;
- rank score descending with `torch.argsort(..., stable=True)`; exact ties retain ascending page ID;
- discovery configurations frozen before timing: Top-256 (50%) and Top-128 (25%);
- gather in exact ranked-page order and token offset 0..15, map each of 14 Q heads to its model-defined GQA KV head, then use the same Flash SDPA consumer;
- ONLINE, paired READY-INDEX and strong CUDA-Graph ONLINE arms must have identical ordered indices and output bytes.

The paired READY-INDEX arm is `DIAGNOSTIC_NOT_IMPLEMENTABLE_BASELINE`, not a strict upper bound. Primary source semantics: Tang et al., QUEST, ICML 2024, https://proceedings.mlr.press/v235/tang24l.html.
