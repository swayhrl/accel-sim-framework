# Lane 7 — Grouped CTA Strong Baseline Native

执行节点：109  
Lane：7  
角色：RTX4080 native producer  
GPU：RTX4080 / SM89  
GPU lock：必须，仅正式CUDA阶段  
GPU lock path：`/data/c16/locks/c16_gpu_campaign.lock`  
允许并行：Lane4、Lane6、Lane8

任务：
`C16_SPLITK_GROUPED_CTA_BASELINE_NATIVE_109_V1`

## 1. 机会性CPU准备

现在立即做：
- 独立worktree
- 读取MASTER
- 核old source/binary SHA
- 准备新extension build
- runner/static tests
- review-pack skeleton

Lane8 branch预期：
`hrl/c16-splitk-grouped-cta-baseline-prep-174new-v1`

在`EARLY_GATE.json`明确为
`READY_FOR_GROUPED_CTA_NATIVE_BASELINE`
前：
- 禁止CUDA初始化
- 禁止import新CUDA extension
- 禁止GPU lock

每120秒fetch，最长90分钟。
gate STOP/超时则保留CPU prep后STOP。

## 2. Matrix

固定：
- M=256
- N=49152
- K={3072,4096}
- split={8,1}
- mapping={ROW,GROUP_M16}

8 cells。

所有cell使用同一patched binary。
mapping_mode：
- ROW=0
- GROUP_M16=1

不扫GROUP_M。

## 3. Correctness

每K、每split：
- ROW vs GROUP_M16必须bitwise equal
- all finite / shape/dtype一致

split8 vs split1：
- 原`rtol=1e-2, atol=5e-2`

如果同一split不bitwise equal，相关K直接STOP，不time/profile。

## 4. Launch / coverage dynamic gate

必须验证：
- split8 GEMM grid 49152，block[32,2,1]
- split1 GEMM grid 6144，block[32,2,1]
- split8 reduction 24576
- scratch不变
- ROW/GROUP kernel function identity相同

另外保存mapping-mode invocation receipt，确保每cell使用正确mode。

## 5. ROW calibration

用本轮ROW cell对照accepted历史K3072/K4096：

- output闭合
- median方向一致
- 若patched ROW median相对accepted偏差>5%且大于两边CV，标记`ROW_PATCH_OVERHEAD_MATERIAL`并STOP科学解释。

不要为了通过校准调整timing协议。

## 6. Timing

每K 25 complete mirror blocks：

`A_ROW, B_ROW, A_GROUP, B_GROUP, B_GROUP, A_GROUP, B_ROW, A_ROW`

A=split8，B=split1。

每cell 50 samples。
每sample前同cell 2次untimed warmup。
不使用conditioner。

## 7. NCU

8 profiles：
2K × 2split × 2mapping。

metrics：
- `lts__t_sectors_srcunit_tex_op_read_lookup_hit.sum`
- `lts__t_sectors_srcunit_tex_op_read_lookup_miss.sum`
- `l1tex__t_bytes.sum`
- `lts__t_bytes.sum`
- `dram__bytes.sum`
- `gpu__time_duration.sum`

application replay，cache-control none。

split8 reduction单列；locality解释只用GEMM。

## 8. 主要derived

每K/split：
- row_hit_fraction
- grouped_hit_fraction
- grouped_minus_row_hit_pp
- row/grouped miss sectors
- row/grouped GEMM DRAM
- DRAM ratio grouped/row
- row/grouped median module time
- timing ratio grouped/row

并计算GROUP_M16下：
- split1 vs split8 timing gain
- split1 vs split8 GEMM DRAM
- split1 vs split8 hit fraction

## 9. 判读

### Strong baseline solves most of problem
若GROUP_M16让split1：
- L2 hit大幅恢复
- DRAM显著下降
- 在K4096重新明显优于split8 GROUP

则说明原split8优势主要补偿ROW mapping局部性不足。
停止设计新split机制，优先把结果定位为software mapping改进/分析。

### Residual split value remains
若GROUP_M16改善split1但在相同GROUP mapping下split8仍明显更好：
说明强mapping后仍存在local working-set / parallelism / reduction tradeoff。
这才保留进一步机制空间。

### No material mapping effect
若grouped几乎不改变hit/DRAM：
需重新审视“逻辑邻近能转化为真实调度局部性”的假设，不追加GROUP_M参数扫描。

## 10. GPU campaign

Gate支持后一次外层GPU lock完成：
correctness -> launch -> timing -> NCU -> release。

锁外CPU分析/Git。

禁止：
- 新K/split/M/N
- GROUP_M sweep
- replica experiment
- EVICT
- SASS/NVBit
- Accel-Sim

## 11. Output

Review pack：
`docs/vm_tlb/review_packs/C16_SPLITK_GROUPED_CTA_BASELINE_NATIVE_109_V1/`

至少：
- SOURCE_AND_GATE.json
- BUILD_RECEIPT.json
- CORRECTNESS.tsv
- LAUNCH_AUDIT.tsv
- ROW_CALIBRATION.tsv
- GPU_LOCK_RECEIPT.json
- TIMING_SAMPLES.tsv
- TIMING_SUMMARY.tsv
- NCU_KERNEL_ROWS.tsv
- GROUPED_BASELINE_SUMMARY.tsv
- SCIENTIFIC_INTERPRETATION.md
- NEXT_174_CONSUMER_CONTRACT.md
- SHA256SUMS

branch：
`hrl/c16-splitk-grouped-cta-baseline-native-109-v1`

最终push/fetch-back/clean/STOP。
