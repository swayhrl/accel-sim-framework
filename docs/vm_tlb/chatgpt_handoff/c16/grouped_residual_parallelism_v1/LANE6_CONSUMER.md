# Lane 6 — Grouped residual-parallelism independent consumer

执行节点：174-new  
Lane：6  
角色：CPU-only independent consumer  
GPU：禁止  
GPU lock：禁止  
允许并行：Lane4、Lane7、Lane8

任务：
`C16_GROUPED_RESIDUAL_PARALLELISM_CONSUMER_174NEW_V1`

## 1. 立即可做

绑定accepted authorities：
- grouped strong-baseline consumer：
  `e7855278076c7e0360d39b18424cc8f048f51da5`
- cross-M causal consumer：
  `2113422f7e6b7e5a851469511d26a9ddf7123d4e`
- threshold consumer：
  `6d226cd99946d3bd7b41c5ee005285183efbb915`
- LR09 literature：
  `38d4df40b615625c15d1843a69a23eb954ac0bef`

建立consumer scaffold与schema，不预填新结果。

## 2. 等待authority

Lane8：
`hrl/c16-grouped-residual-parallelism-prep-174new-v1`

要求：
- EARLY_GATE支持
- footprint
- mapping bijection
- expected launch
- synthetic authority闭合

Lane7：
`hrl/c16-grouped-residual-parallelism-native-109-v1`

正式消费要求：
- final commit/tree
- SHA closure
- GPU lock released
- correctness/launch闭合
- raw timing/NCU rows可读

合法STOP不当科学负结果。

## 3. 独立重算

不要以producer derived summary作为计算authority。

每M/split独立重算：
- n/min/median/max/mean/CV
- split1 relative gain = 1 - split1/split8
- complete-ABBA-block bootstrap，seed=20260929，1000次，q05/q50/q95
- GEMM duration
- split8 reduction duration/DRAM单列
- L2 read hit/miss sectors
- hit fraction
- GEMM DRAM
- launch CTA
- CTA/76SM launch-level proxy
- 若producer合法提供并行度NCU指标，独立重算/转录其raw rows

## 4. 必做比较

### M1 vs M16
两者split1/split8 grid完全相同：
- 96 vs768 CTA

只改变有效M行数和output规模。

判断：
- split8相对收益是否显著变化
- GEMM duration与module timing如何变化
- L2 hit是否保持高位

如果M1比M16更依赖split8，partial-tile利用率参与。

### M16 -> M32 -> M64
split1 launch CTA：
96 -> 192 -> 384

判断：
- split8 relative gain是否随split1 CTA供给增加而单调/总体衰减
- 是否出现crossover
- split1 L2 hit是否一直保持高位

## 5. 结论规则

### 情形A：只低供给点split8有价值
如果M1/M16 split8有优势，M32/M64优势消失或split1反超，且cache hit稳定：

可写：
> grouped locality已控制后，剩余split-K价值主要集中在CTA供给不足/partial-tile利用率较低的区域；随着split1 CTA供给提高，8路split的并行度收益被partial-output/reduction成本抵消。

这应定位为已有parallel decomposition / Stream-K问题，而不是新cache机制。

### 情形B：M64仍有显著split8优势
只有在：
- split1 hit仍高
- mapping/launch闭合
- grid=384
情况下，才建议后续研究低比特特有dequant/latency-hiding/resource机制。

### 情形C：split1全胜
关闭当前split-K支线，不再追加实验。

### 情形D：cache异常
如果split1 hit明显下降，不能把结果解释为parallelism residual；先报告cache仍是混杂变量。

## 6. 不允许的事后扩展

consumer不得建议：
- M128/M256追加点作为“确认”
- split2/4/16扫描
- GROUP_M扫描
除非当前冻结4M点本身出现科学歧义且无法判读；这种情况只记录OPEN_ISSUE，交项目review决定。

## 7. 文献定位

最终必须对照LR09：
- grouped/swizzled mapping是已有软件能力
- Stream-K类工作已经研究低并行度下K维工作划分
- 因此如果残余只来自CTA供给，不能包装成新的split思想

真正可能的新问题只能是：
已有grouped locality + 已有parallel decomposition之后，低比特数据流是否还有特有限制。

## 8. 输出

Review pack：
`docs/vm_tlb/review_packs/C16_GROUPED_RESIDUAL_PARALLELISM_CONSUMER_174NEW_V1/`

至少：
- AUTHORITY_AUDIT.json
- RAW_RECOMPUTE.tsv
- M_SWEEP_COMPARISON.tsv
- NCU_RECOMPUTE.json
- PARALLELISM_INTERPRETATION.md
- RELATED_WORK_POSITIONING.md
- FINAL_DECISION.json
- OPEN_ISSUES.md
- SHA256SUMS

最终中文汇报必须直接回答：
1. split8是否只在低CTA供给点有价值；
2. M1 vs M16是否显示partial-tile因素；
3. M32/M64是否已经由grouped split1解决；
4. 这条支线应关闭，还是还剩低比特特有机制值得继续。

branch：
`hrl/c16-grouped-residual-parallelism-consumer-174new-v1`

普通工程问题solve-and-continue。
最终push/fetch-back/clean/STOP。
