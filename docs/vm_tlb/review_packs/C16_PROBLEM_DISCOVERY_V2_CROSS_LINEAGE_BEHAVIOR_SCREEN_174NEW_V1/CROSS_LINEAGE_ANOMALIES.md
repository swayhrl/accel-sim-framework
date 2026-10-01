# Cross-lineage anomalies and admission

The accepted observations are three different natural routed expert `down_proj` invocations replayed in isolation, not a matched population across all three models. All 243 selected static paths per model were hash checked.

| Contrast | Q30 | DeepSeek | OLMoE | Reading |
|---|---:|---:|---:|---|
| Executed static paths | 41/243 | 169/243 | 129/243 | Coverage and static code differ |
| Warps per executed static path | 2447.6 | 2144.9 | 1024.0 | Static instruction work differs even after coverage normalization |
| Weight sector fill proxy | 0.0625 | 1.0000 | 1.0000 | Per warp/role geometry differs; cache traffic is unknown |

Weight and input each contribute about half of active lane events in all three, while sector proxy differs. Q30 full warps touch widely separated sectors; DeepSeek/OLMoE input warps repeat 16 BF16 starts over 32 lanes and weight warps are compact. This geometry was already characterized as familiar coalescing under different gemvx templates.

One additional within-shard contrast survives: DeepSeek has 2.000 warp-line visits per distinct weight line, Q30 1.200, OLMoE 1.000. DeepSeek has 2.000 logical weight lane bytes per logical weight byte, versus 1.000 and 1.000. These are repeated line touches within the same static shard replay, not measured cache misses or duplicate DRAM fetches. DeepSeek and OLMoE share a receipt-bound gemvx template-6 family but differ in K width and runtime shape; this screen does not assign causality to model lineage.

The role-conditioned executed-shard event Gini values are 0.1333 (Q30 weight), 0.0433 (DeepSeek), and 0 (OLMoE). All-selected-path Gini is much larger because many static paths have proven zero execution. No module/expert population concentration is available from one selected expert each. Nearly all WEIGHT/INPUT records have 32 active lanes; sparse OUTPUT stores explain the small difference in overall active-lane density.

No module or expert hotspot can be inferred from one selected module and one expert invocation per lineage. Static shard concentration is reported descriptively in `SPATIAL_CONCENTRATION.tsv`. The sum of per-shard unique lines is not a cross-replay address union. C16WARP1 does not supply comparable cross-shard time order or a matched token population; phase claims remain UNKNOWN.

Admission gate (A lineage contrast, B normalization persistence, C beyond coverage, D distinct from closed C16 directions, E architectural relevance):

- `Q30_EXECUTED_COVERAGE`: A--D-; 41/243 versus 169/243 and 129/243 is a static coverage contrast; different code and one selected module per lineage.
- `Q30_SCATTERED_REQUEST_GEOMETRY`: ABC-E; 32-sector sparse Q30 versus one/two-sector DeepSeek/OLMoE persists per warp and role, but C16 warp geometry already classified familiar gemvx template/coalescing behavior; no new residual opportunity.
- `DEEPSEEK_OLMOE_INPUT_BROADCAST`: -BC-E; DeepSeek and OLMoE share the two-lane input duplication; familiar within-warp broadcast and coupled template-6.
- `DEEPSEEK_WEIGHT_LINE_REVISIT`: ABCDE; within one shard, DeepSeek weight lines are touched by two warp records per unique line versus Q30 1.2 and OLMoE 1.0; survives role/warp/weight-byte normalization; different from the closed W4 cross-M mapping and from within-warp input broadcast, but exact cause and time value are unknown.
- `SHARD_EVENT_CONCENTRATION`: -B-D-; top shares arise from differing executed static counts and one isolated module; no module/expert concentration population.
- `PHASE_ROUTING`: ---D-; C16WARP1 has no cross-shard chronology; Q30 E3 balanced proxy already sufficient, OLMoE lag-11 posthoc origin unresolved.

One descriptive phenomenon passes all five gates for **oracle screening only**: `DEEPSEEK_WEIGHT_LINE_REVISIT`. Its closest known capabilities are CUDA warp coalescing and GEMV implementation choice, as described in the [NVIDIA CUDA Best Practices Guide](https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/index.html) and [cuBLAS GEMV documentation](https://docs.nvidia.com/cuda/cublas/). Existing C16 warp geometry explains the within-warp pattern but did not classify this within-shard cross-warp revisit contrast. A next CPU-only oracle would bound avoidable request/line service under the exact DeepSeek static path and compare a matched shape/backend control before any mechanism or native experiment. If the bound is small or software scheduling removes the revisit, stop. No independent lineage holdout exists. The accepted Q30 E3 result and OLMoE posthoc temporal audit remain scoped and do not establish cross-model routing skew.
