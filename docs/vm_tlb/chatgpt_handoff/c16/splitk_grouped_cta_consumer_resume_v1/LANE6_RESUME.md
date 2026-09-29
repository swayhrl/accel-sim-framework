# Lane 6 Resume — Grouped CTA strong-baseline formal consumption

日期：2026-09-29

执行节点：174-new  
Lane：6  
角色：CPU-only independent consumer  
GPU：禁止  
GPU lock：禁止  
允许并行：Lane4；Lane7/Lane8已STOP

任务：继续 `C16_SPLITK_GROUPED_CTA_BASELINE_CONSUMER_174NEW_V1`，不要重做scaffold。

## 1. 已完成scaffold

Branch：
`hrl/c16-splitk-grouped-cta-baseline-consumer-174new-v1`

Scaffold commit：
`73dd063dbe35a4eadbba233e678498a87052f57e`

Tree：
`c7e8b1f7121a08c2189a70110cad237262064c3c`

现有pack已绑定：
- static footprint `c72d28b...`
- threshold consumer `6d226cd9...`
- L2 read-hit diagnostic `91570734...`
- cross-M causal consumer `2113422f...`
- LR09 `38d4df40...`

状态仍为：
`CONSUMER_SCAFFOLD_READY_WAITING_PRODUCER`

直接从现有worktree继续，不重新生成schema/旧authority。

## 2. Lane8 prep authority

Branch：
`hrl/c16-splitk-grouped-cta-baseline-prep-174new-v1`

Final commit：
`0b37b84cf8fbcaaeb90c36fc28dcbb8ec3764ae1`

Final tree：
`bbf6f448369dcbee866a6dbf6f0b0a9afdd29615`

Early gate：
`READY_FOR_GROUPED_CTA_NATIVE_BASELINE`

关键闭合：
- ROW/GROUP_M16均为6144 CTA严格双射
- 12582912 output elements完整覆盖，无重无漏
- 同Ntile相邻Mtile逻辑距离ROW=384、GROUP_M16=1
- input/qweight/qzeros/scales/scratch-output静态地址集合完全相同
- 只改变访问顺序
- 同一patched kernel、branch-free runtime mapping select
- AWQ数学、K-loop、split/reduction、grid/block、数据布局不变

## 3. Lane7 producer authority

Branch：
`hrl/c16-splitk-grouped-cta-baseline-native-109-v1`

Final HEAD：
`a75379674116fc94e57ccc88eff9359fc1f4114c`

Final tree：
`681262652c2fce136b8eeaabc342f46dd92f4ec4`

Review pack：
`docs/vm_tlb/review_packs/C16_SPLITK_GROUPED_CTA_BASELINE_NATIVE_109_V1/`

Producer闭合：
- 8 cells
- 400 timing samples
- 8 NCU profiles
- ROW/GROUP同split输出bitwise equal
- ROW output SHA与accepted authority一致
- ROW calibration全部PASS
- GPU lock合法释放
- no Lane4 partial

## 4. 正式消费必须从raw/base rows重算

不要使用producer `GROUPED_BASELINE_SUMMARY.tsv` 或 `SCIENTIFIC_INTERPRETATION.md` 作为计算authority。

优先读取：
- SOURCE_AND_GATE.json
- CORRECTNESS.tsv
- LAUNCH_AUDIT.tsv
- ROW_CALIBRATION.tsv
- TIMING_SAMPLES.tsv
- NCU_KERNEL_ROWS.tsv
- GPU_LOCK_RECEIPT.json
- SHA256SUMS

独立重算每个K/split/mapping：
- n/min/median/max/mean/CV
- L2 read hit/miss sectors
- hit fraction
- GEMM DRAM
- split8 reduction独立记录
- GROUP/ROW timing ratio
- GROUP-ROW hit pp
- GROUP/ROW DRAM ratio
- complete-mirror-block bootstrap，seed=20260929，1000次，q05/q50/q95

## 5. 必做强基线比较

### K3072 split1
独立确认：
- ROW hit约63.56%
- GROUP约95.95%
- hit恢复约+32.39pp
- DRAM GROUP/ROW约0.145
- timing GROUP/ROW约0.724

### K4096 split1
独立确认：
- ROW hit约63.26%
- GROUP约95.95%
- hit恢复约+32.69pp
- DRAM GROUP/ROW约0.135
- timing GROUP/ROW约0.669

### split8自身
独立确认GROUP相对ROW：
- hit变化<0.07pp
- DRAM约1.00x
- timing只改善约1.4%/2.6%

## 6. 同等mapping能力下的核心对比

必须直接比较GROUP_M16状态下split1 vs split8。

独立计算：

### K3072
- split1 GROUP median
- split8 GROUP median
- split1 relative gain = 1 - split1/split8
- GEMM DRAM ratio split1/split8
- hit fraction difference

### K4096
同上。

若raw确认producer，应得到：
- split1比split8快约38.7% / 30.9%
- 两者GEMM hit都约95.95%
- split1 GEMM DRAM仅为split8约40%–46%

这里必须把split8 reduction成本单列，不能混成GEMM locality结论。

## 7. 项目级结论门槛

若独立重算确认上述结果：

应明确写：

> 对K3072/K4096这两个冻结点，经典GROUP_M16软件映射已经恢复split1的大部分L2复用；在给split1和split8相同的locality mapping能力后，split8不再保留独立优势，split1反而因为避免8路partial/reduction而明显更快。因此，先前split8在ROW mapping下的优势主要是在补偿原始CTA映射造成的局部性损失，而不是split8本身提供了不可替代的缓存机制。

必须同时说明：
- GROUP_M16属于已有经典软件优化能力，不是新贡献；
- 仅限当前AutoAWQ kernel family、M256/N49152/K3072/K4096 synthetic proxy；
- logical block-ID adjacency不等于严格物理issue order；
- 不能推广到所有M/N/K/GROUP_M；
- 不代表GPT-3 checkpoint。

## 8. 对后续研究空间的判断

若强基线成立：
- 停止当前“cache-aware split8/new split mechanism”主张；
- 不做GROUP_M sweep；
- 不做split sweep；
- 不再围绕这两个点设计硬件机制。

后续若要继续，只允许把问题重新定义为：

> 在经典grouped/swizzled CTA locality scheduling之后，是否仍存在其他shape/M值/并行度条件下无法同时满足CTA供给、局部工作集和reduction成本的残余区间？

这需要新的独立实验设计，不能从本轮两点直接外推。

## 9. 输出

继续更新现有：
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

完成：
tests -> deterministic rerun -> diff-check -> commit -> push -> fetch-back exact commit/tree -> clean -> STOP。

最终汇报用中文明确：
1. grouped mapping恢复了多少split1 reuse；
2. 相同mapping下split8还剩多少优势；
3. 当前“新split机制”故事是否应关闭；
4. 若继续，剩余科学问题应如何重新定义。
