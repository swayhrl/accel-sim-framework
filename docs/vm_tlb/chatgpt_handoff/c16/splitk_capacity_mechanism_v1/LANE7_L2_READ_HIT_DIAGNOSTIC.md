# Lane 7 — Split-K 容量机制 L2 Read-Hit 机会性诊断

执行节点：109  
Lane：7  
角色：RTX4080 native diagnostic  
GPU：RTX4080 / SM89  
GPU lock：必须，仅正式profile阶段  
GPU lock path：`/data/c16/locks/c16_gpu_campaign.lock`  
允许并行：Lane4、Lane6、Lane8

任务：
`C16_SPLITK_L2_READ_HIT_DIAGNOSTIC_109_V1`

## 1. CPU-only第一阶段

先不碰GPU。

绑定：
- threshold producer final `b17193ff6b3786fd01d5bfe83b5c1a0a03859729`
- static audit `c72d28b17247f25d0c3613604ab6cab1737666e0`
- accepted A/B binaries
- exact synthetic formula

用本机ncu 2025.1.1.0查询可用metrics，找出**最小且语义明确**的L2 global/read sector：
- read requests/sectors
- read lookup hits
- read lookup misses
- 或等价read hit rate

不要预设具体metric名字。

必须把候选metric的ncu query输出和最终选择写入：
`METRIC_SELECTION.json`

若无法找到能明确解释为L2 read lookup hit/miss或read hit rate的指标：
- 不升级到更大section sweep；
- 写`METRIC_NOT_AVAILABLE_STOP`；
- 不碰GPU；
- push/STOP。

## 2. 正式profile范围

如果metric可用，只profile：

- K2048 A/B
- K2560 A/B
- K3072 A/B
- K4096 A/B

共8 profiles。

不重跑K12288。

固定：
- M=256
- N=49152
- warm same-arm
- 2次warmup在NVTX外
- target只包目标module call
- application replay
- cache-control none

原先bytes/duration metrics可一并保留用于交叉检查，但不得扩展到大量section。

## 3. GEMM优先解释

A含GEMM+reduction。
必须把两行分开。

工作集机制只用：
- A GEMM的L2 read hit/miss
- B GEMM的L2 read hit/miss

reduction只保留记录，不参与weight-locality hit-rate比较。

不得tensor级归因；只能称“目标GEMM的read-side L2行为”。

## 4. 关键比较

重点检查：

### K2560 -> K3072

已知：
- full footprint：62.34MiB -> 74.81MiB
- B DRAM：约180MB -> 729MB
- A total DRAM：约491MB -> 504MB

若B GEMM L2 read hit rate/lookup-hit fraction同步大幅下降，而A GEMM变化小：
可以报告“与capacity-knee解释一致”。

若B hit行为无明显变化：
必须降级capacity解释，不为匹配预期改变指标/范围。

### K2048 / K4096
只作为两侧anchor。

## 5. 资源与停止

GPU动作放在一次外层lock内。
如果lock 30分钟内不可合法获得，可机会性STOP，不偷锁。

不运行：
- SASS trace
- NVBit address trace
- Accel-Sim
- EVICT conditioner
- 新K/split/M/N

## 6. 输出

Review pack：
`docs/vm_tlb/review_packs/C16_SPLITK_L2_READ_HIT_DIAGNOSTIC_109_V1/`

至少：
- AUTHORITY.json
- METRIC_SELECTION.json
- GPU_LOCK_RECEIPT.json（若GPU执行）
- RAW_INDEX.tsv
- KERNEL_ROWS.tsv
- L2_READ_HIT_SUMMARY.tsv
- SCIENTIFIC_INTERPRETATION.md
- FINAL_DECISION.json
- SHA256SUMS

用户汇报用中文：
- K2560→3072的GEMM read-hit是否明显变化；
- A/B是否不同；
- 是否加强或削弱capacity机制解释。

branch建议：
`hrl/c16-splitk-l2-read-hit-diagnostic-109-v1`

普通工程问题solve-and-continue。
