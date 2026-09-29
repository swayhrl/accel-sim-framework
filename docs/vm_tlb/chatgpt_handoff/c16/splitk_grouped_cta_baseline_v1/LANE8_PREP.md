# Lane 8 — Grouped CTA Strong Baseline Prep

执行节点：174-new  
Lane：8  
角色：CPU-only source/contract auditor  
GPU：禁止  
GPU lock：禁止  
允许并行：Lane4、Lane6、Lane7

任务：
`C16_SPLITK_GROUPED_CTA_BASELINE_PREP_174NEW_V1`

## 1. 目标

把`GROUP_M16_FULL_M`映射做成可审计的强基线，不改变AWQ数学、K-loop、split/reduction、tile、grid或数据布局。

第一优先级：尽快发布
`EARLY_GATE.json`
让Lane7可以继续。

## 2. Source authority

基于：
- AutoAWQ kernel commit `c7b0e88c327694c715b0a758d9ce8fd414a1fa21`
- generator blob `98f49efac8626388039912e6aabc8a84d9f8303b`
- existing split1 direct-output authority `0e88faa28c9066b48e394dce657d7a16e6332a32`

新独立extension，不覆盖accepted binaries。

## 3. Mapping patch

固定M=256，因此m_tiles=16；固定N=49152，因此n_tiles=384。

原：
- linear = blockIdx.x % (16*384)
- split_z = blockIdx.x / (16*384)
- row_m = linear / 384
- row_n = linear % 384

grouped：
- group_m = linear % 16
- group_n = linear / 16

runtime `mapping_mode`：
- 0 ROW
- 1 GROUP_M16

要求branch-free：
- 同时算row/grouped坐标；
- 用整数select组合；
- 重构`blockIdx_y = Mtile*384 + Ntile`；
- split_z保持原公式。

两种mapping必须同一compiled target kernel与同一新增地址映射指令路径。

## 4. Static bijection / coverage proof

对每个split和mapping枚举全部6144逻辑CTA：
- (Mtile,Ntile)覆盖16×384恰好一次；
- 无重复、无遗漏；
- output tile范围覆盖一致；
- 同Ntile的Mtile线性ID距离：
  - ROW = 384
  - GROUP_M16 = 1
- qweight/qzeros/scales静态地址集合总union不变；
- 只改变访问顺序，不改变集合。

输出：
`MAPPING_BIJECTION.tsv`
`ADDRESS_SET_INVARIANCE.json`

如果union或coverage不同，STOP。

## 5. Kernel semantic isolation

输出：
`PATCH_SEMANTIC_DIFF.md`

必须证明：
- A/input pointer最终由重映射后的Mtile驱动，但同一输出tile读取的A行范围与原来一致；
- weight-side最终由重映射后的Ntile驱动，同一输出tile使用同一权重；
- output/scratch地址对应同一逻辑输出tile；
- K-loop、dequant、MMA、load数量、barrier、writeback公式不变；
- grid/block/reduction不变。

## 6. Experiment points

只：
- K3072
- K4096

× split1/8
× ROW/GROUP_M16

8 cells。

expected launch同accepted：
split8 GEMM 49152 / reduction24576 / scratch201326592B
split1 GEMM 6144 / no reduction / scratch25165824B
block [32,2,1]

## 7. Correctness contract

同一split：
ROW vs GROUP_M16必须bitwise equal。

split8 vs split1继续原容差。

## 8. EARLY_GATE

Review pack：
`docs/vm_tlb/review_packs/C16_SPLITK_GROUPED_CTA_BASELINE_PREP_174NEW_V1/`

Gate三选一：
- `READY_FOR_GROUPED_CTA_NATIVE_BASELINE`
- `MAPPING_NOT_ISOLATED_STOP`
- `COVERAGE_OR_IDENTITY_BLOCKED_STOP`

READY至少绑定：
- patch/source SHA
- mapping proof SHA
- expected launch SHA
- exact 8-cell matrix
- no GPU attestation

先push gate，再继续完整pack。

## 9. Full output

至少：
- AUTHORITY.json
- PATCH_SEMANTIC_DIFF.md
- MAPPING_BIJECTION.tsv
- ADDRESS_SET_INVARIANCE.json
- EXPECTED_LAUNCH.tsv
- EARLY_GATE.json
- SCIENTIFIC_BOUNDARY.md
- SHA256SUMS

branch：
`hrl/c16-splitk-grouped-cta-baseline-prep-174new-v1`

最终push/fetch-back/clean/STOP。
