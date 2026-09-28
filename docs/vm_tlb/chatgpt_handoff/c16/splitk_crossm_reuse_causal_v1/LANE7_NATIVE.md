# Lane 7 — 跨M权重复用 Native 因果验证

执行节点：109  
Lane：7  
角色：RTX4080 native producer  
GPU：RTX4080 / SM89  
GPU lock：必须，仅正式CUDA阶段  
GPU lock path：`/data/c16/locks/c16_gpu_campaign.lock`  
允许并行：Lane4、Lane6、Lane8

任务：
`C16_SPLITK_CROSSM_REUSE_CAUSAL_NATIVE_109_V1`

## 1. 机会性CPU准备

现在可立即开始：
- 独立worktree
- 读取MASTER
- 核 accepted source/binary SHA
- 按Lane8设计准备新extension build脚本和runner
- tiny CPU formula tests
- review-pack skeleton

在Lane8 `EARLY_GATE.json`为：
`READY_FOR_NATIVE_CAUSAL_SCREEN`
之前：
- 禁止CUDA初始化
- 禁止import新CUDA extension
- 禁止GPU lock

Lane8预期branch：
`hrl/c16-splitk-crossm-reuse-causal-prep-174new-v1`

可每120秒fetch，最长90分钟。
若gate STOP/超时，发布CPU prep状态后STOP。

## 2. GPU矩阵

固定：
- M=256
- N=49152
- K={2560,3072}
- split={8,1}
- state={SHARED,PER_MTILE}

8 cells。

所有cell均分配16份bit-identical qweight/qzeros/scales。

state：
- SHARED：replica_mask=0
- PER_MTILE：replica_mask=15

同一patched binary/path。

## 3. Correctness gate

每K、每split：

- SHARED vs PER_MTILE：bitwise equal required
- A split8 vs B split1：原 `rtol=1e-2, atol=5e-2`
- shape/dtype/all finite
- replica 0..15的qweight/qzeros/scales semantic SHA各自相同
- input SHA与frozen synthetic contract一致

同一split state不bitwise equal则该K直接STOP，不time/profile。

## 4. Launch gate

每K必须与Lane8表一致：

split8：
- GEMM 49152
- reduction 24576
- scratch 201326592B
- block [32,2,1]

split1：
- GEMM 6144
- no reduction
- scratch 25165824B
- block [32,2,1]

还要验证：
- SHARED/PER_MTILE kernel name与function identity相同
- state只由runtime replica_mask区分

## 5. Timing

每K做25 complete mirror blocks：

`A_SHARED, B_SHARED, A_PER_M, B_PER_M, B_PER_M, A_PER_M, B_SHARED, A_SHARED`

每cell 50 samples。

每sample前：
- 同cell 2次untimed warmup
- 不使用conditioner
- CUDA event只包target module call

记录全部raw samples。

## 6. NCU

8 profiles：
2K × 2split × 2state。

metrics：
- `lts__t_sectors_srcunit_tex_op_read_lookup_hit.sum`
- `lts__t_sectors_srcunit_tex_op_read_lookup_miss.sum`
- `l1tex__t_bytes.sum`
- `lts__t_bytes.sum`
- `dram__bytes.sum`
- `gpu__time_duration.sum`

application replay，cache-control none。

A GEMM/reduction分列。
主因果解释只用GEMM read hit/miss + GEMM DRAM；
module timing用于端到端局部效果。

## 7. 主要derived量

对每K/split计算：

- shared_hit_fraction
- per_mtile_hit_fraction
- delta_hit_pp = shared - per_mtile
- shared_miss_sectors
- per_mtile_miss_sectors
- shared_dram
- per_mtile_dram
- dram_ratio
- shared_median
- per_mtile_median
- timing_ratio

并比较：

### K2560 split1
预测最关键：
SHARED有大量跨M reuse，PER_MTILE应显著破坏。

### K3072 split1
SHARED状态capacity已破坏大量reuse；PER_MTILE额外恶化可能较小。

### split8
如果高hit主要来自local-set跨M复用，PER_MTILE应显著降低hit并增加DRAM。

预测仅用于判读，结果不符合时不得修实验。

## 8. 一次GPU campaign

Gate支持后获取一次外层lock。

锁内：
1. GPU identity/free memory
2. build产物/file SHA复核
3. import extension
4. 生成16 replicas
5. correctness
6. launch audit
7. timing
8. NCU子进程仍由持锁wrapper串行
9. post receipt
10. release

CPU分析/Git全部锁外。

## 9. STOP边界

不新增：
- replica count 2/4/8 sweep
- 新K
- 新split
- 新M/N
- EVICT state
- SASS/NVBit
- Accel-Sim

若结果支持，再由后续review决定是否已经足够作为机制证据。

## 10. 输出

`docs/vm_tlb/review_packs/C16_SPLITK_CROSSM_REUSE_CAUSAL_NATIVE_109_V1/`

至少：
- SOURCE_AND_GATE.json
- BUILD_RECEIPT.json
- REPLICA_BINDINGS.tsv
- CORRECTNESS.tsv
- LAUNCH_AUDIT.tsv
- GPU_LOCK_RECEIPT.json
- TIMING_SAMPLES.tsv
- TIMING_SUMMARY.tsv
- NCU_KERNEL_ROWS.tsv
- REUSE_CAUSAL_SUMMARY.tsv
- SCIENTIFIC_INTERPRETATION.md
- NEXT_174_CONSUMER_CONTRACT.md
- SHA256SUMS

branch：
`hrl/c16-splitk-crossm-reuse-causal-native-109-v1`

最终push/fetch-back/clean/STOP。
