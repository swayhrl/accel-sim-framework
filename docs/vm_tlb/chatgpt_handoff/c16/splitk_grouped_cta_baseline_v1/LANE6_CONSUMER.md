# Lane 6 — Grouped CTA Strong Baseline Independent Consumer

执行节点：174-new  
Lane：6  
角色：CPU-only independent consumer  
GPU：禁止  
GPU lock：禁止  
允许并行：Lane4、Lane7、Lane8

任务：
`C16_SPLITK_GROUPED_CTA_BASELINE_CONSUMER_174NEW_V1`

## 1. 可立即准备

绑定accepted机制authority：
- static footprint `c72d28b17247f25d0c3613604ab6cab1737666e0`
- threshold consumer `6d226cd99946d3bd7b41c5ee005285183efbb915`
- L2 read-hit diagnostic `915707348617f7a8f432bad7a434a98d78b487c8`
- cross-M causal consumer `2113422f7e6b7e5a851469511d26a9ddf7123d4e`

读取LR09：
`hrl/c16-chatgpt-literature-notes-v1@38d4df40b615625c15d1843a69a23eb954ac0bef`

建立consumer scaffold与输出schema，不预填新结果。

## 2. 等待

Lane8：
`hrl/c16-splitk-grouped-cta-baseline-prep-174new-v1`

要求EARLY_GATE支持执行、mapping bijection/address-set invariance闭合。

Lane7：
`hrl/c16-splitk-grouped-cta-baseline-native-109-v1`

正式消费要求：
- final commit/tree
- pack SHA
- GPU lock released
- correctness
- launch
- ROW calibration
- raw timing/NCU rows

若producer合法STOP，仅记录停止原因，不当负科学结果。

## 3. 独立重算

不要用producer derived summary作为计算authority。

每K/split/mapping：
- n/min/median/max/mean/CV
- L2 hit/miss sectors
- hit fraction
- GEMM DRAM
- split8 reduction单列
- complete-mirror-block bootstrap，seed=20260929，1000次

对每K/split计算：
- GROUP/ROW timing ratio
- GROUP-ROW hit pp
- GROUP/ROW DRAM ratio

在GROUP_M16下独立计算：
- split1相对split8 timing gain
- GEMM DRAM ratio
- hit fraction difference

## 4. 主要判断

### A. split1 mapping recovery
K3072、K4096分别判断：
- GROUP_M16是否显著提高split1 L2 hit
- 是否降低miss/DRAM
- 是否改善module timing

### B. 同等mapping能力后的split1 vs split8
这是最重要的强基线。

如果GROUP_M16下split1重新明显优于split8：
说明先前split8收益主要是在补偿原ROW mapping未利用跨M局部性。

如果GROUP_M16下split8仍明显优于split1：
说明即便采用经典locality mapping，split缩小local working set / 并行度等仍有独立价值。

### C. split8自身
A_ROW vs A_GROUP：
判断split8高hit是否已经基本饱和，还是原ROW mapping同样限制它。

## 5. 结论边界

grouped/swizzled ordering属于已有软件优化能力，不作为项目新颖性。

本consumer最终要回答：
- 现有强基线能解决多少问题；
- 强基线之后还剩什么问题；
- 是否仍值得设计新机制。

不得因为已有机制结论成立就预设新机制一定有空间。

## 6. 输出

Review pack：
`docs/vm_tlb/review_packs/C16_SPLITK_GROUPED_CTA_BASELINE_CONSUMER_174NEW_V1/`

至少：
- AUTHORITY_AUDIT.json
- RAW_RECOMPUTE.tsv
- GROUPED_STRONG_BASELINE_COMPARISON.tsv
- NCU_RECOMPUTE.json
- RELATED_WORK_POSITIONING.md
- SCIENTIFIC_INTERPRETATION.md
- FINAL_DECISION.json
- OPEN_ISSUES.md
- SHA256SUMS

最终中文汇报必须明确：
1. grouped mapping能恢复多少split1 reuse；
2. 相同mapping下split8还剩多少优势；
3. 当前故事应该收敛成软件映射改进，还是仍有新机制空间。

branch：
`hrl/c16-splitk-grouped-cta-baseline-consumer-174new-v1`

普通工程问题solve-and-continue。
最终push/fetch-back/clean/STOP。
