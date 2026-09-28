# Lane 8 — K4096 Capacity Counterfactual 设计准备

执行节点：174-new  
Lane：8  
角色：CPU-only simulator/trace design auditor  
GPU：禁止  
GPU lock：禁止  
允许并行：Lane4、Lane6、Lane7

任务：
`C16_SPLITK_K4096_CAPACITY_COUNTERFACTUAL_PREP_174NEW_V1`

本任务只准备，不抓trace、不跑长模拟。

## 1. 绑定authority

### 当前机制证据
- static audit：
  `c72d28b17247f25d0c3613604ab6cab1737666e0`
- threshold native：
  `b17193ff6b3786fd01d5bfe83b5c1a0a03859729`

### simulator platform
- branch：
  `hrl/awma-174-rtx4080-v1-baseline-promotion-v1`
- HEAD：
  `8d1f14a32f5538660d74da86ccb03a2c504c5735`
- config：
  `configs/rtx4080_ada/SM89_RTX4080_AWMA_V1/gpgpusim.config`
- expected blob：
  `3306caa589baa07c046e16fddd3066351ba10d2c`

baseline dl2：
`S:2048:128:16,...`

平台：
- 8 memory channels
- 2 subpartitions/channel
- 16 subpartitions total
- 128B line
- 16-way
- 2048 sets/subpartition
- total 64MiB

不要改变AWMA platform authority本身；新config必须isolated copy。

## 2. 目标只选K4096

固定：
- M=256
- K=4096
- N=49152
- W4 synthetic
- A split8
- B split1

原因：
- B full footprint = 99.75MiB
- A per-split static local = 13.875MiB
- native A/B timing近持平
- native B/A DRAM≈1.83
- 比K12288 trace小约3倍

不要再加入K2560/3072/12288到sim矩阵。

## 3. Trace方案审计

设计一个最小Accel-Sim SASS capture contract。

优先：
- 只capture目标GEMM kernel；
- A的reduction不进入capacity mechanism trace；
- B同样只GEMM；
- A/B使用同一个K4096 synthetic tensor authority；
- 记录input/qweight/qzeros/scales/output/scratch VA ranges和hash；
- exact launch identity：
  - A GEMM grid 49152
  - B GEMM grid 6144
  - block [32,2,1]
  - same kernel family

目的：
只比较GEMM内部weight reuse，不把A reduction的固定额外流量混进L2 capacity counterfactual。

需要审查：
- 现有Accel-Sim tracer是否可按kernel name/range只抓该GEMM；
- SM89 trace encoding/parser兼容；
- address width/namespace；
- trace capture是否会包含必要memory operands；
- trace-to-simulator object range是否可绑定qweight。

如果当前tracer无法可靠只捕获目标GEMM，设计退化方案，但不得自动扩大到完整模型。

## 4. Trace成本预估

不要直接让109试大trace。

基于：
- grid
- K loop iterations
- kernel SASS/static instruction count
- 现有trace编码经验

给A/B估算：
- dynamic warp-instruction order
- expected raw/compressed size区间
- capture时间区间

若无法静态可信估算，可设计一个**M=16只用于trace-size pilot**：
- 同K/N/split
- 不用于科学结论
- 仅估算bytes/CTA和runtime，再外推M256。

是否需要pilot由本prep决定并写入trace contract。

设置合理停止界限：
- 单arm预计trace过大或capture耗时明显不经济时，优先考虑缩小机制proxy，而不是硬抓。

## 5. Simulator L2容量配置

候选只改dl2 sets，保持：
- 128B line
- 16-way
- 16 subpartitions
- replacement/write/allocation policy不变
- 其他平台参数不变

建议：
- 64MiB：sets=2048，baseline
- 128MiB：sets=4096
- 256MiB：sets=8192

32MiB不是默认点；除非成本很低且能增加解释力才列为optional。

必须注明：
改变sets也改变set-index范围，因此这是“L2容量配置counterfactual”，不是纯物理容量隔离。

## 6. 模拟指标

只预注册GEMM级：
- cycles / instructions / CTA identity
- L2 read requests/hits/misses if telemetry supports
- DRAM read/request bytes/count
- qweight address-range hit/miss/DRAM if现有object telemetry可合法绑定
- completion/quiescence

目标判读：

如果capacity解释成立：
- B split1从64→128/256时L2 miss/DRAM应显著下降；
- B性能应改善；
- A split8相对更不敏感，因为13.875MiB local set已远低于64MiB。

不要求cycle-perfect native match。

## 7. 平台与claim边界

必须继承现有RTX4080 simulator资格边界：
- 用于方向/机制counterfactual；
- 不宣称cycle-perfect Ada；
- 不把模拟absolute cycles当native预测。

需要核对AWMA baseline promotion的scope与当前trace是否兼容；若不兼容则STOP。

## 8. Gate

输出：

`SIM_TRACE_PREP_GATE.json`

允许：
- `READY_FOR_K4096_GEMM_TRACE_CAPTURE`
- `TRACE_CAPTURE_TOO_EXPENSIVE_USE_REDUCED_PROXY`
- `SIM_PLATFORM_NOT_ADMITTED_STOP`
- `BLOCKED_NEEDS_REVIEW`

READY仅授权后续Lane7 capture，不授权本Lane运行长模拟。

## 9. 输出

Review pack：
`docs/vm_tlb/review_packs/C16_SPLITK_K4096_CAPACITY_COUNTERFACTUAL_PREP_174NEW_V1/`

至少：
- AUTHORITY_AUDIT.json
- PLATFORM_BINDING.json
- TRACE_CAPTURE_CONTRACT.md
- TRACE_SIZE_ESTIMATE.json
- L2_CONFIG_MATRIX.tsv
- SIM_METRIC_CONTRACT.md
- SIM_TRACE_PREP_GATE.json
- OPEN_ISSUES.md
- SHA256SUMS

branch建议：
`hrl/c16-splitk-k4096-capacity-counterfactual-prep-174new-v1`

最终push/fetch-back/clean/STOP。
