# Lane 6 — Split-K容量阈值 Independent Consumer

执行节点：174-new  
Lane：6  
角色：CPU-only independent consumer  
GPU：禁止  
GPU lock：禁止  
允许并行：Lane4、Lane7、Lane8

任务：
`C16_SPLITK_FOOTPRINT_THRESHOLD_CONSUMER_174NEW_V1`

## 1. 可以立即并行做的准备

无需等Lane7：

- 读取MASTER和Lane8合同；
- 绑定旧Qwen UP_M256：
  `3aad5887b9b4c5bec801962bf8035fed9d485f47`
- 绑定GPT3 proxy EXPAND_M256 K=12288：
  `3ea7c5401d185cb4eab237041464911d5b2b2482`
- 独立复算accepted endpoint timing/NCU；
- 实现K-series consumer和bootstrap；
- 冻结输出schema；
- 不预填未来K结果。

## 2. 等待两项authority

### Lane8
branch：
`hrl/c16-splitk-footprint-static-audit-174new-v1`

必须至少看到：
- STATIC_GATE=SUPPORTED；
- source binding；
- per-split footprint结果。

### Lane7
branch：
`hrl/c16-splitk-footprint-threshold-native-109-v1`

正式消费要求：
- final commit/tree；
- pack SHA closure；
- static gate binding；
- GPU lock released；
- correctness/launch closed；
- raw timing和NCU rows可读取。

如果Lane7因gate negative/ambiguous或GPU unavailable合法STOP，本consumer不把“没有新GPU数据”当实验负结果；只记录停止原因。

## 3. 独立重算

不要使用producer derived summary作为计算authority。

对每个合法K：
- raw timing A/B各n=50；
- median/min/max/mean/CV；
- split1 gain = 1-B/A；
- ABBA block delta；
- block bootstrap 1000次，seed=20260928；
- correctness；
- grid/scratch/reduction；
- NCU A/B GEMM与reduction；
- total DRAM和B/A DRAM ratio。

加入accepted K=12288 endpoint，但注明来自前一正式campaign，不伪装成本轮同一campaign样本。

## 4. footprint binding

从Lane8读取每K：
- full W4 weight+metadata；
- /L2；
- split8 per-split unique qweight；
- unique metadata；
- total per-split；
- /L2。

不自己用“/8”近似覆盖Lane8源码结果。

构造：

`CAPACITY_THRESHOLD_COMPARISON.tsv`

至少字段：
- K
- full_bytes
- full_over_l2
- split8_local_bytes
- split8_local_over_l2
- split1_gain
- bootstrap q05/q50/q95
- A_DRAM
- B_DRAM
- B_over_A_DRAM
- source_campaign
- status

## 5. 主要判读

### 支持工作集容量机制

需要联合看到：

1. 2560以下full footprint在L2容量范围时，split1相对表现明显好于3072/4096/12288；
2. full footprint跨过L2范围后，split1 DRAM相对split8显著增加；
3. M/N/grid/scratch固定，不能用CTA数量变化解释K-series内部变化；
4. split8 local footprint在这些K点都保持明显低于L2；
5. K=12288 endpoint延续同一趋势。

注意：
- 不是要求2560→3072一步精确跳变；
- 真实有效容量可能低于64MiB；
- 这仍不能单独证明具体replacement/hit序列。

### 不支持

如果split1性能/DRAM与full footprint跨容量无系统关系：
- 当前“split-K通过缩小weight working set跨L2容量线”假设降级；
- 不建议继续SASS/Accel-Sim围绕该解释。

### 部分支持

若DRAM趋势清晰但timing不跟随，或反之：
- 分开报告；
- 不强行合成因果。

## 6. 与并行度解释的关系

本K-series内部M/N固定，所以：
- split1 grid固定6144；
- split8 grid固定49152；
- output/scratch/reduction shape固定。

因此K-series比旧Qwen↔GPT3跨shape比较更能隔离工作集变量。

但K增加也会增加每CTA K-loop计算量，因此不能把所有timing变化都归因cache；DRAM趋势是关键辅助证据。

## 7. 后续门槛

本consumer只能建议，不自动执行。

若容量机制得到清晰支持：
优先下一步二选一，而不是同时做：

A. **paired Accel-Sim容量counterfactual**
- GPT3 proxy EXPAND_M256
- split1 vs split8
- 少量L2容量点
- 目标：看crossover是否随容量移动

或

B. **qweight-targeted bounded trace**
- 仅在模拟器无法直接回答或需要验证真实调度时使用。

由项目review决定。

## 8. 输出

`docs/vm_tlb/review_packs/C16_SPLITK_FOOTPRINT_THRESHOLD_CONSUMER_174NEW_V1/`

至少：
- `AUTHORITY_AUDIT.json`
- `ACCEPTED_ENDPOINT_RECOMPUTE.tsv`
- `NEW_K_RECOMPUTE.tsv`
- `CAPACITY_THRESHOLD_COMPARISON.tsv`
- `NCU_RECOMPUTE.json`
- `MECHANISM_INTERPRETATION.md`
- `FINAL_DECISION.json`
- `OPEN_ISSUES.md`
- `SHA256SUMS`

用户汇报用中文，直接说：
- 是否看到容量阈值趋势；
- 哪些证据支持/不支持；
- 下一步是模拟还是停止。

## 9. branch

建议：
`hrl/c16-splitk-footprint-threshold-consumer-174new-v1`

普通工程问题solve-and-continue。
最终push/fetch-back/clean/STOP。
