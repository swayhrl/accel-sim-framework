# Lane 6 Resume — Split-K容量阈值独立消费

日期：2026-09-28

执行节点：174-new  
Lane：6  
角色：CPU-only independent consumer  
GPU：禁止  
GPU lock：禁止  
允许并行：Lane4、Lane7、Lane8

任务：`C16_SPLITK_FOOTPRINT_THRESHOLD_CONSUMER_174NEW_V1`

## 1. Static authority

Lane8 final branch：
`hrl/c16-splitk-footprint-static-audit-174new-v1`

Final commit：
`c72d28b17247f25d0c3613604ab6cab1737666e0`

Final tree：
`b7d8654f47023e80389e7dd8e78b907c41983bf9`

Gate commit：
`2f6029bfce65f7dcedb39ef9ec46860d349aa211`

核心源码闭合：
- split/Mtile/Ntile映射；
- qweight/qzeros/scales地址不依赖Mtile；
- split8为mod8 K32 tile交织；
- 固定split/Ntile跨Mtile静态地址集合Jaccard=1；
- K点合法；
- 每split精确footprint。

精确footprint：
- K2048：split1 49.875MiB；split8 local 6.9375MiB
- K2560：62.34375MiB；8.671875MiB
- K3072：74.8125MiB；10.40625MiB
- K4096：99.75MiB；13.875MiB
- K12288：299.25MiB；41.625MiB

这些是静态地址集合，不是实际L2 hit/replacement证明。

## 2. Native authority

Lane7 final branch：
`hrl/c16-splitk-footprint-threshold-native-109-v1`

Final HEAD：
`b17193ff6b3786fd01d5bfe83b5c1a0a03859729`

Final tree：
`2a6e42fab5cd8b03c01d900d59f0abd5df355c1f`

Science result commit：
`a46ba3183fb4c526c752a8a8d46dca119bd41a33`

RUN_ID：
`C16R_splitk-footprint-threshold-native-v1_20260928T150645Z`

GPU lock：
`2026-09-28T15:33:58Z -> 15:34:26Z`
已正常释放。

新K：
- 2048
- 2560
- 3072
- 4096

K12288引用accepted endpoint：
`1544018d967003c2825eb69f56440f641f5f5581`

Correctness / launch均闭合。

## 3. 正式重算要求

不要读取producer derived summary作为计算authority。

从：
- `TIMING_SAMPLES.tsv`
- `NCU_KERNEL_ROWS.tsv`
- `CORRECTNESS.tsv`
- `LAUNCH_AUDIT.tsv`
- Lane8 `PER_SPLIT_FOOTPRINT.tsv`

独立重算：

每K：
- A/B timing min/median/max/mean/CV
- split1 gain
- ABBA block deltas
- block bootstrap，seed=20260928，1000次，q05/q50/q95
- A/B total DRAM
- A GEMM DRAM
- A reduction DRAM
- B GEMM DRAM
- B/A total DRAM
- B/A GEMM-only DRAM（A用total-reduction）
- full footprint / L2
- split8 local footprint / L2

加入K12288 accepted endpoint，但明确来自旧campaign，不纳入本轮ABBA bootstrap。

## 4. 重点科学检查

### 4.1 容量附近的knee

重点比较K2560→K3072：

静态：
- 62.34MiB → 74.81MiB
- 从略低于64MiB到略高于64MiB

producer观察：
- split1 gain：+44.3% → +17.4%
- split1 DRAM：约180MB → 729MB
- split8总DRAM：约491MB → 504MB

独立判断：
- split1 DRAM增幅是否远超K本身20%的增长；
- split8是否没有相同幅度突变；
- timing是否同步恶化。

不能称“精确64MiB硬阈值”；有效容量受其他数据和映射影响。

### 4.2 跨更大K的连续趋势

检查：
- K2048、2560、3072、4096、12288
- split1 gain是否单调/近单调恶化；
- B/A DRAM是否持续增大；
- K4096附近是否接近timing crossover；
- K12288是否延续而非孤立异常。

### 4.3 归一化辅助指标

可新增post-hoc描述：
- B DRAM / full footprint
- A GEMM DRAM / full footprint
- timing per K-tile
- DRAM per K-tile

这些是结果可见后的解释指标，不能伪装成预注册门槛。

尤其检查split1在K>=3072后是否出现“每次target调用多轮重取完整weight set”的量级特征。

## 5. 结论层级

若独立重算确认：

- K2560→3072出现split1 DRAM明显非线性上升；
- split8没有对应突变；
- 固定M/N/grid/scratch条件闭合；
- 更大K继续沿相同方向；

则项目层可写：

> 在固定M/N和固定split实现下，当split1需要反复访问的完整W4权重集合从L2容量附近以下增长到以上时，其DRAM访问和相对性能出现明显恶化；split8因把每个split的静态权重集合保持在更小范围，未出现同样的恶化。这个结果强烈支持“工作集容量是split-K策略翻转的重要因素”，但尚不能证明真实CTA调度、替换策略或唯一L2因果。

不要写成：
- “64MiB就是硬阈值”
- “已经证明所有miss都是qweight”
- “split8缓存命中率已被直接测得”
- “这是GPT-3模型固有行为”

## 6. 下一步推荐门槛

如果上述机制得到强支持：

优先推荐：
**K4096 M256 N49152，split1 vs split8的最小paired capacity counterfactual。**

原因：
- full footprint 99.75MiB > 64MiB
- split8 local 13.875MiB < 64MiB
- native timing接近crossover
- 动态规模远小于K12288
- 若模拟L2从64提升到128MiB，split1完整集合进入容量范围，最适合观察方向是否随容量移动

但consumer只提出建议，不自动抓SASS/运行Accel-Sim。

## 7. 输出

建立/更新：

`docs/vm_tlb/review_packs/C16_SPLITK_FOOTPRINT_THRESHOLD_CONSUMER_174NEW_V1/`

至少：
- AUTHORITY_AUDIT.json
- ACCEPTED_ENDPOINT_RECOMPUTE.tsv
- NEW_K_RECOMPUTE.tsv
- CAPACITY_THRESHOLD_COMPARISON.tsv
- NCU_RECOMPUTE.json
- MECHANISM_INTERPRETATION.md
- FINAL_DECISION.json
- OPEN_ISSUES.md
- SHA256SUMS

完成：
tests -> deterministic rerun -> diff-check -> commit -> push -> fetch-back -> clean -> STOP。

最终汇报必须使用中文清楚说明，不用内部英文标签代替主结论。
