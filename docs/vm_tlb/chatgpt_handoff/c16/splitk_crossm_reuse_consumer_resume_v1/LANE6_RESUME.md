# Lane 6 Resume — Cross-M weight-side reuse formal consumption

Date: 2026-09-29

执行节点：174-new  
Lane：6  
角色：CPU-only independent consumer  
GPU：禁止  
GPU lock：禁止  
允许并行：Lane4；Lane7/Lane8已停止

任务：继续 `C16_SPLITK_CROSSM_REUSE_CAUSAL_CONSUMER_174NEW_V1`，**不要重做scaffold阶段**。

## 1. 已完成的consumer scaffold

Branch：
`hrl/c16-splitk-crossm-reuse-causal-consumer-174new-v1`

Current scaffold HEAD：
`d6982c872633bc73047a51dde37105e5719d5c84`

当前pack已明确：
- status = `CONSUMER_SCAFFOLD_READY_WAITING_PRODUCER`
- 未预填新结果
- 既有static footprint / threshold / L2-read-hit authorities已绑定
- no GPU / no Lane4 partial

直接在现有worktree/branch继续正式消费。

## 2. Lane8 prep authority

Branch：
`hrl/c16-splitk-crossm-reuse-causal-prep-174new-v1`

Early gate commit：
`bc82d767c27e55c8bc06f5bf8830ccf752838d24`

Final commit：
`bcc3a7082ffb66ab85d8ef8c62439ada97090d16`

Gate：
`READY_FOR_NATIVE_CAUSAL_SCREEN`

Gate闭合：
- SHARED / PER_MTILE同一patched kernel与同一指令路径
- 唯一state-dependent memory semantic是qweight/qzeros/scales replica base
- input、K-loop、load count、dequant、MMA、scratch/output、grid/block不变
- 所有cell都分配16份bit-identical replicas
- 最坏预算远低于16GB

## 3. Lane7 producer authority

Branch：
`hrl/c16-splitk-crossm-reuse-causal-native-109-v1`

Final HEAD：
`2f8338408b2b9a39f5a6fc1bab9db015a019ea62`

Final tree：
`60d7199da7ba608be078923f42c1f1a451e30a1c`

Review pack：
`docs/vm_tlb/review_packs/C16_SPLITK_CROSSM_REUSE_CAUSAL_NATIVE_109_V1/`

Producer已闭合：
- 8 cells
- 400 timing samples
- 8 NCU profiles
- same-split SHARED/PER_MTILE outputs bitwise equal
- A/B correctness PASS
- launch identity PASS
- GPU lock合法释放
- no Lane4 partial
- no SASS / simulation

## 4. 正式消费只能从raw/base rows重算

禁止把producer `REUSE_CAUSAL_SUMMARY.tsv` 或 `SCIENTIFIC_INTERPRETATION.md` 当计算authority。

优先读取：
- SOURCE_AND_GATE.json
- REPLICA_BINDINGS.tsv
- CORRECTNESS.tsv
- LAUNCH_AUDIT.tsv
- TIMING_SAMPLES.tsv
- NCU_KERNEL_ROWS.tsv
- GPU_LOCK_RECEIPT.json
- SHA256SUMS

独立重算每个K/split/state：
- n/min/median/max/mean/CV
- SHARED vs PER_MTILE timing ratio
- complete-mirror-block bootstrap，seed=20260928，1000次，q05/q50/q95
- L2 read hit/miss sectors
- hit fraction
- delta hit pp
- GEMM DRAM
- DRAM ratio
- split8 reduction单列

## 5. 必做的数值一致性检查

### K2560 split1
验证：
- SHARED hit约90.5%
- PER_MTILE hit约35.5%
- hit loss约55pp
- DRAM约181MB -> 1.075GB
- timing约0.844ms -> 2.863ms

进一步检查：
`(PER miss sectors - SHARED miss sectors) * 32B`
与
`PER GEMM DRAM - SHARED GEMM DRAM`
是否数量级/数值高度一致。

### K3072 split1
验证：
- SHARED hit约63.5%
- PER_MTILE约35.6%
- hit loss约28pp
- DRAM约727MB -> 1.285GB
- timing约1.348ms -> 3.496ms

检查：
K3072额外损失是否明显小于K2560，支持“SHARED状态下capacity已经提前破坏部分cross-M reuse”。

### split8
验证：
- K2560 SHARED≈95.9% -> PER_MTILE≈28.2%
- K3072 SHARED≈95.9% -> PER_MTILE≈28.5%
- 两个K都发生约67pp hit loss
- DRAM都约增加5.5–6.1倍

这项结果若独立成立，是判断“split8高hit是否真的依赖跨M物理地址复用”的核心证据。

## 6. 允许的科学结论

若raw重算确认producer：

可写：

> 在保持计算、M/N/K、split、grid、scratch、总分配量和kernel指令路径不变时，仅把不同M tile访问的weight-side物理地址从共享改为各自独立，就会显著降低目标GEMM的L2读命中并增加DRAM与局部时间。因此，跨M weight-side地址复用是当前高L2命中的重要来源；split-K通过缩小每个split的局部工作集，提高了这类复用在cache中存活的机会。

同时必须保留：
- weight-side = qweight + qzeros + scales，不能再细分tensor归因
- 16×不同VA会同时扩大页面/TLB足迹，因此“timing全部来自L2”不能成立
- 但L2 read-hit与miss/DRAM的直接变化可作为明确的cache-side因果证据
- 不推断NVIDIA replacement细节
- 不推广到所有GEMM/LLM
- 不是GPT-3 checkpoint行为

## 7. 与文献强基线的连接

若机制成立，下一步不应继续做更多replica/split sweep。

优先建议一个独立强基线：

> 保持split1与同一AWQ数学/数据布局，只改变CTA到(Mtile,Ntile)的逻辑映射，采用经典grouped/block-swizzled ordering，让共享同一weight-side地址的M tiles在逻辑顺序上更靠近。

目的：
判断不增加split/reduction，仅通过已有CTA locality scheduling能力能恢复多少reuse。

这一步只作为最终建议，不在本consumer自动执行。

## 8. 输出

继续更新现有：
`docs/vm_tlb/review_packs/C16_SPLITK_CROSSM_REUSE_CAUSAL_CONSUMER_174NEW_V1/`

至少完成：
- AUTHORITY_AUDIT.json
- RAW_RECOMPUTE.tsv
- REUSE_CAUSAL_COMPARISON.tsv
- NCU_RECOMPUTE.json
- MECHANISM_INTERPRETATION.md
- FINAL_DECISION.json
- OPEN_ISSUES.md
- SHA256SUMS

最终：
tests -> deterministic rerun -> diff-check -> commit -> push -> fetch-back exact commit/tree -> clean -> STOP。

最终汇报用中文说明：
1. cross-M地址共享是不是高L2 hit的重要来源；
2. K2560与K3072是否符合capacity决定reuse存活程度；
3. split8高hit是否依赖cross-M sharing；
4. 下一步是否应转向grouped/swizzled CTA strong baseline。
