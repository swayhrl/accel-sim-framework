# Lane 7 — Grouped residual-parallelism native screen

执行节点：109  
Lane：7  
角色：RTX4080 native producer  
GPU：RTX4080 / SM89  
GPU lock：必须，仅正式CUDA阶段  
GPU lock path：`/data/c16/locks/c16_gpu_campaign.lock`  
允许并行：Lane4、Lane6、Lane8

任务：
`C16_GROUPED_RESIDUAL_PARALLELISM_NATIVE_109_V1`

## 1. 机会性CPU准备

现在立即开始：
- 独立worktree
- 读取MASTER
- 核accepted grouped source lineage
- 准备extension build/runner
- review-pack skeleton
- CPU-only查询最小并行度NCU指标

在Lane8 `EARLY_GATE.json`明确为
`READY_FOR_RESIDUAL_PARALLELISM_NATIVE_SCREEN`
之前：
- 禁止CUDA初始化
- 禁止import新CUDA extension
- 禁止GPU lock

Lane8预期branch：
`hrl/c16-grouped-residual-parallelism-prep-174new-v1`

每120秒fetch，最长90分钟。
gate STOP/超时则保存CPU prep并STOP。

## 2. 冻结matrix

K=4096
N=12288
M={1,16,32,64}
split={8,1}
mapping=GROUP_FULL_M

8 cells。

A=split8
B=split1

不运行ROW。

## 3. Correctness

每M：
- A/B使用完全相同input/qweight/qzeros/scales
- shape/dtype/all finite
- A vs B：`rtol=1e-2, atol=5e-2`
- output hash记录
- 若自然bitwise equal则记录

如果某M correctness失败：
该M不进入timing/NCU；其他M可继续资格检查。

## 4. Launch gate

必须严格匹配Lane8 expected table。

至少：
- split1 GEMM CTA = 96/96/192/384
- split8 GEMM CTA = 768/768/1536/3072
- block [32,2,1]
- split1无reduction
- split8 reduction存在
- scratch/reduction grid按Lane8冻结值

function identity必须相同kernel family。

## 5. Timing

每M做25个ABBA mirror blocks：
`A8,B1,B1,A8`

每cell50 samples。
每sample前2次same-cell untimed warmup。
CUDA event只包module call。
不同M的执行顺序按固定轮转表交错，避免所有小M/大M被时间漂移系统分开。

不用conditioner。

## 6. NCU

每cell1份，共8 profiles。

冻结已有：
- L2 read hit sectors
- L2 read miss sectors
- L1/TEX bytes
- L2 bytes
- DRAM bytes
- duration

CPU-only metric query再尝试选择最小并行度指标：
优先
- launch-level waves per SM
- active warps / SM
- SM throughput

只有语义明确、chip支持的指标才加入。
找不到则不扩大section sweep，核心screen继续。

输出`METRIC_SELECTION.json`。

split8必须分开：
- GEMM row
- reduction row

主timing保留module total，同时报告：
- GEMM duration
- reduction duration
- reduction DRAM

## 7. 关键derived

对每M：
- split1/split8 module median
- split1 relative gain = 1 - split1/split8
- GEMM duration ratio
- split8 reduction fraction of module time（用可合法比较口径）
- L2 hit fractions
- GEMM DRAM ratio
- launch CTA/SM proxy
- 若有NCU并行度指标，报告对应值

特别比较：

### M1 vs M16
grid相同96 vs768。
判断M tile有效行数提高后split收益是否变化。

### M16 -> M32 -> M64
split1 CTA供给96→192→384。
判断split8收益是否随供给提高而衰减/翻转。

## 8. 科学判读

### 低CTA供给残余
若split8只在M1/M16更快，M32/M64 split1追平/反超，同时split1 L2 hit维持高位：
报告为low-CTA-supply / tile-utilization / reduction tradeoff。

这是已有parallel-decomposition问题，不升级cache机制。

### 高供给仍有split8优势
只有M64时同时满足：
- split1 hit高
- grouped mapping闭合
- split1 grid384
- split8仍显著更快
才建议下一轮诊断低比特特有dequant/latency-hiding/resource原因。

### split1全胜
直接关闭该split支线。

### cache异常
若split1 L2 hit明显掉到旧ROW水平，先停止parallelism解释。

## 9. GPU campaign

Gate支持后一次外层GPU lock：
1. GPU identity/free memory
2. source/build SHA
3. correctness
4. launch
5. timing
6. NCU
7. post receipt
8. release

锁外做CPU分析/Git。

若GPU lock连续45分钟不可合法获得：
发布机会性STOP，不偷锁。

## 10. 禁止扩展

禁止：
- GROUP_M sweep
- split sweep
- 新K/N/M
- replica
- EVICT
- SASS/NVBit
- Accel-Sim

## 11. 输出

Review pack：
`docs/vm_tlb/review_packs/C16_GROUPED_RESIDUAL_PARALLELISM_NATIVE_109_V1/`

至少：
- SOURCE_AND_GATE.json
- BUILD_RECEIPT.json
- METRIC_SELECTION.json
- CORRECTNESS.tsv
- LAUNCH_AUDIT.tsv
- GPU_LOCK_RECEIPT.json
- TIMING_SAMPLES.tsv
- TIMING_SUMMARY.tsv
- NCU_KERNEL_ROWS.tsv
- RESIDUAL_PARALLELISM_SUMMARY.tsv
- SCIENTIFIC_INTERPRETATION.md
- NEXT_174_CONSUMER_CONTRACT.md
- SHA256SUMS

branch：
`hrl/c16-grouped-residual-parallelism-native-109-v1`

最终push/fetch-back/clean/STOP。
