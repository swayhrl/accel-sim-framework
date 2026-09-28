# Lane 7 — Split-K容量阈值机会性Native验证

执行节点：109  
Lane：7  
角色：RTX4080 native producer  
GPU：RTX4080 / SM89  
GPU lock：必须，仅在正式CUDA阶段使用  
GPU lock path：`/data/c16/locks/c16_gpu_campaign.lock`  
允许并行：Lane8静态审计、Lane6 consumer prep、Lane4

任务：
`C16_SPLITK_FOOTPRINT_THRESHOLD_NATIVE_109_V1`

## 1. 机会性执行原则

本Lane可以立即和Lane8并行，但先做CPU-only准备。

在Lane8的`STATIC_GATE.json`明确为：

`SUPPORTED_PROCEED_NATIVE_THRESHOLD_SCREEN`

之前：
- 禁止CUDA初始化；
- 禁止import会加载CUDA extension的模块；
- 禁止GPU lock；
- 禁止生成GPU大tensor。

如果gate为NOT_SUPPORTED或AMBIGUOUS：
- 发布CPU prep receipt；
- 不碰GPU；
- STOP。

如果gate在90分钟内未出现：
- 状态写`WAITING_FOR_STATIC_GATE`；
- push当前CPU prep；
- STOP，不自行猜测机制。

## 2. Lane8 gate来源

预期branch：

`hrl/c16-splitk-footprint-static-audit-174new-v1`

预期文件：

`docs/vm_tlb/review_packs/C16_SPLITK_FOOTPRINT_STATIC_AUDIT_174NEW_V1/STATIC_GATE.json`

可每120秒fetch一次，最长90分钟。

必须记录：
- gate commit/tree；
- source blob；
- K contract SHA；
- footprint table SHA（如果gate已绑定）。

## 3. CPU-only并行准备

现在就做：

- 独立worktree；
- 核A/B binaries：
  - split8 `9e8d38a04c28770338fcef8ae0f9a90a984b7a8f95bcb98a407738594e1c08d7`
  - split1 `1aa8db13f5fd10651aa4241f58200e3a7075214d34cca4d70fbcbe7cbbc07887`
- 核GPT3 synthetic formula `GPT3_SHAPE_SYNTH_V1`及SHA；
- 从accepted GPT3 K=12288 producer绑定N=49152、M=256和合成模式；
- 生成K-parametric runner；
- tiny CPU formula tests；
- 预期grid/scratch验证；
- review-pack skeleton。

CPU prep不得依赖未来结果。

## 4. 正式新点

固定：

- M=256
- N=49152
- group_size=128
- synthetic W4 formula与accepted GPT3 proxy完全同族
- A split8
- B split1

只新增：

- K=2048
- K=2560
- K=3072
- K=4096

K=12288直接使用：
`1544018d967003c2825eb69f56440f641f5f5581`
中的accepted EXPAND_M256 warm endpoint，不自动重跑。

## 5. 为什么不做EVICT状态

本轮专门隔离“weight footprint跨容量范围”：

- M/N固定；
- CTA grid固定；
- output/scratch固定；
- 只改变K和weight footprint。

只做`WARM_SAME_ARM`，避免再加入conditioner这个变量。

每个sample前：
- 2次same-arm untimed warmup；
- 然后CUDA event测目标一次。

## 6. correctness gate

每K：

A/B使用完全相同的：
- input
- qweight
- qzeros
- scales

要求：
- output shape/dtype一致；
- all finite；
- `rtol=1e-2, atol=5e-2`；
- 记录SHA/max_abs/mean_abs/relative_l2/changed count。

不得因某K失败而放宽容差。

失败K：
- 不timing；
- 不NCU；
- 其他独立K可以继续资格检查。

## 7. launch gate

动态验证每K：

M=256,N=49152，因此预期不随K变化：

B split1：
- GEMM grid 6144
- scratch 25,165,824B
- no reduction

A split8：
- GEMM grid 49,152
- scratch 201,326,592B
- reduction present
- reduction grid 24,576

block/function identity需与accepted GPT3 K=12288一致。

任何不一致的K不进入科学比较。

## 8. timing

每个合法K：

- 10 global warmups/arm；
- 25 ABBA blocks：
  `A,B,B,A`
- 50 samples/arm；
- CUDA event；
- sample边界同步。

总新样本：
4 K × 2 arms × 50 = 400。

保留raw samples和block pairing。

## 9. NCU

每个合法K：
- A_W一份
- B_W一份

最多8 profiles。

配置：
- application replay
- cache-control none
- 2 same-arm warmups在NVTX外
- target NVTX只包目标call

冻结：
- `l1tex__t_bytes.sum`
- `lts__t_bytes.sum`
- `dram__bytes.sum`
- `gpu__time_duration.sum`

A GEMM与reduction分列。
B只有GEMM。

不做tensor-level attribution。

## 10. 一次GPU campaign

Gate支持后才获取一次外层GPU lock。

锁内：
1. GPU/L2/free-memory identity；
2. import A/B；
3. 按K从小到大做correctness/launch/timing；
4. NCU子进程仍由持锁wrapper串行；
5. GPU post receipt；
6. release。

所有CPU分析、bootstrap、Git操作在释放锁后做。

如果GPU lock连续45分钟不能合法获得：
- 不偷锁；
- 发布`GPU_NOT_AVAILABLE_OPPORTUNISTIC_STOP`；
- STOP。

## 11. producer分析

计算每K：
- full W4 weight+metadata bytes；
- /L2；
- split8静态集合（从Lane8 gate读，不自行覆盖）；
- A/B median/CV；
- split1 gain；
- A/B DRAM；
- DRAM ratio；
- A reduction DRAM。

附上K=12288 accepted endpoint。

只做描述性趋势，不决定最终因果。

重点看：
- K2560（full footprint <64MiB）
- K3072（full footprint >64MiB）
之间是否出现明显timing/DRAM变化。

不能要求在64MiB精确跳变。

## 12. review pack

`docs/vm_tlb/review_packs/C16_SPLITK_FOOTPRINT_THRESHOLD_NATIVE_109_V1/`

至少：
- `CPU_PREP_RECEIPT.json`
- `STATIC_GATE_BINDING.json`
- `SOURCE_AND_RUN_MANIFEST.json`
- `GPU_LOCK_RECEIPT.json`
- `CORRECTNESS.tsv`
- `LAUNCH_AUDIT.tsv`
- `TIMING_SAMPLES.tsv`
- `TIMING_SUMMARY.tsv`
- `NCU_KERNEL_ROWS.tsv`
- `NCU_SUMMARY.json`
- `K_THRESHOLD_SERIES.tsv`
- `SCIENTIFIC_INTERPRETATION.md`
- `NEXT_174_CONSUMER_CONTRACT.md`
- `SHA256SUMS`

## 13. branch / STOP

建议branch：

`hrl/c16-splitk-footprint-threshold-native-109-v1`

普通工程问题solve-and-continue，但不得改变K列表、M/N、split、dtype、state或profile范围。

结束：
validate -> commit -> push -> fetch-back exact -> clean -> STOP。

禁止自动抓SASS或跑Accel-Sim。
