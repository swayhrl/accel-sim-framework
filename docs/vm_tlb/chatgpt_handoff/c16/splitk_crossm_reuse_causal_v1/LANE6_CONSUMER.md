# Lane 6 — Cross-M reuse independent consumer

执行节点：174-new
Lane：6
角色：CPU-only independent consumer
GPU：禁止
GPU lock：禁止

任务：C16_SPLITK_CROSSM_REUSE_CAUSAL_CONSUMER_174NEW_V1

先绑定已有authority：
- static footprint: c72d28b17247f25d0c3613604ab6cab1737666e0
- threshold native: b17193ff6b3786fd01d5bfe83b5c1a0a03859729
- threshold consumer: 6d226cd99946d3bd7b41c5ee005285183efbb915
- L2 read-hit diagnostic: 915707348617f7a8f432bad7a434a98d78b487c8

现在可先准备consumer scaffold与输出schema，不预填新结果。

等待：
- Lane8 branch hrl/c16-splitk-crossm-reuse-causal-prep-174new-v1
- Lane7 branch hrl/c16-splitk-crossm-reuse-causal-native-109-v1

正式消费要求：
- Lane8 EARLY_GATE支持执行；
- Lane7 final commit/tree、SHA、GPU lock、correctness、launch和raw rows闭合。

从raw timing/NCU独立重算每个K/split/state：
- median/min/max/mean/CV
- SHARED vs PER_MTILE timing ratio
- L2 read hit/miss sectors与hit fraction
- GEMM DRAM
- split8 reduction单列
- 1000次complete-mirror-block bootstrap，seed 20260928

重点：
1. K2560 split1：破坏跨M weight-side地址共享后，hit是否显著下降、DRAM/timing是否上升。
2. K3072 split1：额外损失是否比K2560小。
3. split8：PER_MTILE是否显著破坏约95.9%的高read-hit。

若成立，可说明：
保持计算、grid、scratch、split和总分配量不变时，仅改变不同M tile是否访问相同weight-side地址，就能显著改变L2 read-hit、DRAM和局部性能。跨M weight-side地址复用因此是当前高L2命中的重要来源，而split-K缩小局部工作集有助于让这种复用在cache中存活。

仍不得声称：
- 只有qweight起作用；
- 已知NVIDIA replacement细节；
- 对所有GEMM/LLM普遍成立；
- 这是GPT-3 checkpoint行为。

若SHARED→PER_MTILE基本不改变hit/DRAM，则降级该机制解释，不追加replica count扫描。

输出：
docs/vm_tlb/review_packs/C16_SPLITK_CROSSM_REUSE_CAUSAL_CONSUMER_174NEW_V1/

至少：
AUTHORITY_AUDIT.json
RAW_RECOMPUTE.tsv
REUSE_CAUSAL_COMPARISON.tsv
NCU_RECOMPUTE.json
MECHANISM_INTERPRETATION.md
FINAL_DECISION.json
OPEN_ISSUES.md
SHA256SUMS

branch:
hrl/c16-splitk-crossm-reuse-causal-consumer-174new-v1

完成后push、fetch-back、clean、STOP。
