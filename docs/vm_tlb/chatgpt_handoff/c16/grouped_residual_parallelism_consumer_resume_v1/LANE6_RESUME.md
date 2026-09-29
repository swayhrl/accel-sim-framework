# Lane 6 Resume — Grouped residual-parallelism formal consumption

日期：2026-09-29

执行节点：174-new  
Lane：6  
角色：CPU-only independent consumer  
GPU：禁止  
GPU lock：禁止  
允许并行：Lane4；Lane7/Lane8已STOP

任务：继续 `C16_GROUPED_RESIDUAL_PARALLELISM_CONSUMER_174NEW_V1`，不要重做scaffold。

## 1. 已完成scaffold

Branch：
`hrl/c16-grouped-residual-parallelism-consumer-174new-v1`

Scaffold HEAD：
`911bca13be88ba14ecdf2698b2f3499659644811`

Tree：
`2367b5d501f940fc7bfe8af64e69d1f265151a84`

当前pack状态：
`CONSUMER_SCAFFOLD_READY_WAITING_PRODUCER`

现有authority/schema已经冻结，直接继续正式消费。

## 2. Lane8 prep authority

Branch：
`hrl/c16-grouped-residual-parallelism-prep-174new-v1`

Early gate：
`f6bad36a0ee49e718df268421e96593c94756b77`

Final commit：
`493250b11302344c1f445465da8c58e6275545bd`

Final tree：
`f8893515af454aaff442f3598912dbf89bb22608`

Gate：
`READY_FOR_RESIDUAL_PARALLELISM_NATIVE_SCREEN`

已闭合：
- K=4096, N=12288, M={1,16,32,64}, split={1,8}
- GROUP_FULL_M mapping
- weight-side 24.9375MiB = 0.38965×64MiB
- 8 cells mapping/coverage/address-set PASS
- all science cells同一patched kernel与mapping_mode=1路径
- no M-dependent GEMM-body branch
- synthetic authority `C16_GROUPED_RESIDUAL_SYNTH_V1`
- expected launch冻结

## 3. Lane7 producer authority

Branch：
`hrl/c16-grouped-residual-parallelism-native-109-v1`

Final HEAD：
`ab84399012c89fce2c21fabac8d6f9fa8688d164`

Final tree：
`dd7b4a5dfa7082c54057584177c2b864f197e88e`

Review pack：
`docs/vm_tlb/review_packs/C16_GROUPED_RESIDUAL_PARALLELISM_NATIVE_109_V1/`

Producer闭合：
- 4 M × 2 split = 8 cells
- 400 timing samples
- 8 NCU profiles
- all A/B outputs bitwise equal
- launch PASS
- GPU lock合法释放
- no Lane4 partial
- no experiment expansion

## 4. 正式消费必须从raw/base rows重算

禁止使用producer `RESIDUAL_PARALLELISM_SUMMARY.tsv` / `SCIENTIFIC_INTERPRETATION.md` 作为计算authority。

优先读取：
- SOURCE_AND_GATE.json
- BUILD_RECEIPT.json
- METRIC_SELECTION.json
- CORRECTNESS.tsv
- LAUNCH_AUDIT.tsv
- TIMING_SAMPLES.tsv
- NCU_KERNEL_ROWS.tsv
- GPU_LOCK_RECEIPT.json
- SHA256SUMS

每M/split独立重算：
- n/min/median/max/mean/CV
- split8 relative gain = 1 - split8/split1
- split1 relative gain = 1 - split1/split8
- complete-ABBA-block bootstrap，seed=20260929，1000次，q05/q50/q95
- GEMM duration
- split8 reduction duration
- split8 reduction DRAM
- L2 read hit/miss sectors
- hit fraction
- GEMM DRAM
- launch CTA
- CTA/76SM proxy
- launch__waves_per_multiprocessor
- sm__warps_active.avg.pct_of_peak_sustained_elapsed

## 5. 必做的趋势检查

### M1 vs M16
两点：
- split1 CTA=96
- split8 CTA=768

独立确认：
- M1 split8 relative gain约55.9%
- M16约46.6%

因为CTA数相同而收益不同，允许表述：
“partial-M tile utilization/effective work参与选择，CTA count alone不足。”

不得直接把差异唯一归因为partial tile；M也同时改变output/reduction规模。

### M16 -> M32 -> M64

split1 CTA：
96 -> 192 -> 384

独立确认split8 relative gain总体持续衰减：
- M16 ~46.6%
- M32 ~21.4%
- M64翻转为split1快约4.93%

bootstrap必须检查各点方向稳定，特别是M64 crossover。

## 6. Cache control check

必须独立确认：
- split1 GEMM L2 read miss sectors = 0 at all four M
- split8 GEMM L2 read miss sectors = 0 at all four M
- hit fraction = 1.0

因此旧capacity knee未重现。

注意：
`dram__bytes.sum`仍非零，可能含write/其他流量；不能因read miss=0而声称“完全没有DRAM”。

## 7. 并行度证据

独立读取/报告：

split1 GEMM：
- waves/SM: 0.14, 0.14, 0.28, 0.56
- active warps %: ~5.0, 5.0, 9.5, 17.8

split8 GEMM：
- waves/SM: 1.12, 1.12, 2.25, 4.49
- active warps %: ~24.2,24.3,30.2,33.6

这些指标支持“实际并行活跃度随CTA供给变化”，但不要把waves/SM等同resident occupancy。

## 8. GEMM vs reduction

独立重算split8 GEMM duration / split1 GEMM duration：
约：
- M1 0.399x
- M16 0.473x
- M32 0.707x
- M64 0.961x

split8 reduction kernel time占profile-local GEMM+reduction kernel time约：
- 11.4%
- 11.7%
- 9.6%
- 8.1%

需要说明：
module timing不等于简单NCU kernel duration相加，profile与timing campaign不同；这里只做方向性分解。

## 9. 项目级结论门槛

如果raw独立重算确认producer：

正式写：

> 在GROUP_FULL_M locality和capacity-safe weight-side条件下，split8的残余收益随split1 CTA供给增加持续衰减，并在M64/384-CTA处翻转；M1与M16拥有相同CTA数但split8收益不同，说明partial-tile/effective-work也参与选择。当前残余应定位为低CTA供给、tile利用率与partial-output/reduction之间的经典parallel-decomposition权衡，而不是新的cache机制。

并明确：
- 属于Stream-K/parallel decomposition已研究的问题空间；
- 不把“低CTA时split-K有帮助”包装成新贡献；
- 不建议继续当前split-K支线的M/split/GROUP扫描；
- 当前支线应关闭。

## 10. 是否还剩低比特特有机制

只有producer raw显示M64在：
- high L2 hit
- 384 split1 CTA
- GROUP_FULL_M
条件下split8仍显著优于split1，才允许建议继续。

当前producer相反：M64已由split1反超，因此若独立确认，应回答：
**没有足够证据继续追低比特特有split机制。**

## 11. 输出

继续更新现有：
`docs/vm_tlb/review_packs/C16_GROUPED_RESIDUAL_PARALLELISM_CONSUMER_174NEW_V1/`

至少完成：
- AUTHORITY_AUDIT.json
- RAW_RECOMPUTE.tsv
- M_SWEEP_COMPARISON.tsv
- NCU_RECOMPUTE.json
- PARALLELISM_INTERPRETATION.md
- RELATED_WORK_POSITIONING.md
- FINAL_DECISION.json
- OPEN_ISSUES.md
- SHA256SUMS

完成：
tests -> deterministic rerun -> diff-check -> commit -> push -> fetch-back exact -> clean -> STOP。

最终中文汇报必须直接回答：
1. split8是否只在低CTA供给点有价值；
2. M1/M16能否说明partial-tile/effective-work参与；
3. M32/M64是否显示随着split1供给提高发生crossover；
4. 当前split-K支线是否应正式关闭。
