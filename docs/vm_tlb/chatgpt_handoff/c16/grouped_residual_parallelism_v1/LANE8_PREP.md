# Lane 8 — Grouped residual-parallelism prep

执行节点：174-new  
Lane：8  
角色：CPU-only source/contract auditor  
GPU：禁止  
GPU lock：禁止  
允许并行：Lane4、Lane6、Lane7

任务：
`C16_GROUPED_RESIDUAL_PARALLELISM_PREP_174NEW_V1`

## 1. 目标

准备一个capacity-safe的residual screen，验证在GROUP_FULL_M已经最大化cross-M locality以后，split8是否仍仅在CTA供给较低的M区间有价值。

第一优先级：
尽快发布`EARLY_GATE.json`，不要等完整pack。

## 2. 冻结矩阵

固定：
- K=4096
- N=12288
- group_size=128
- split={1,8}
- mapping=GROUP_FULL_M

M：
- 1
- 16
- 32
- 64

共8 cells。

禁止新增M/K/N/split/GROUP_M。

## 3. 精确footprint

独立复核：
- qweight = 25,165,824 B
- qzeros = 196,608 B
- scales = 786,432 B
- weight-side total = 26,148,864 B = 24.9375 MiB
- total/L2 = 0.38965×

对M1/16/32/64分别列：
- input bytes
- split1 scratch/output bytes
- split8 scratch bytes
- expected reduction output
- conservative live-memory peak

必须明确：weight-side < L2只是降低capacity压力，不证明常驻。

输出：
`FOOTPRINT_AND_MEMORY_BUDGET.tsv`

## 4. GROUP_FULL_M mapping

动态：
- m_tiles=ceil(M/16)
- n_tiles=96
- linear=blockIdx.x%(m_tiles*n_tiles)
- split_z=blockIdx.x/(m_tiles*n_tiles)
- Mtile=linear%m_tiles
- Ntile=linear/m_tiles

静态枚举每个M/split：
- 所有(Mtile,Ntile)覆盖一次
- output tile无重无漏
- address-set union闭合
- 同Ntile的Mtile在线性ID中连续

输出：
`MAPPING_BIJECTION.tsv`
`ADDRESS_SET_AUDIT.json`

## 5. Source patch

优先复用上一轮GROUP_M16 patch结构，泛化到dynamic m_tiles。

所有science cells必须：
- 同一个compiled target kernel
- 同一GROUP_FULL_M路径
- 无M-dependent branch改变GEMM主体

允许整数算术依赖m_tiles，但：
- K-loop
- load count
- dequant
- MMA
- shared layout
- tile
- block
- split/reduction
- data layout
必须保持。

输出：
`PATCH_SEMANTIC_DIFF.md`

## 6. Synthetic authority

先审查现有synthetic generator是否真正参数化支持K4096/N12288/M1/16/32/64。

若支持：
直接绑定原formula SHA。

若不支持：
建立`C16_GROUPED_RESIDUAL_SYNTH_V1`，要求：
- deterministic
- weight-side bytes对所有M完全相同
- M只改变input/output shape
- split1/8使用同一input/weight bytes
- tiny CPU reference + SHA闭合

## 7. Expected launch

独立计算并冻结：

Ntile=96。

split1 GEMM：
- M1/M16: 96 CTA
- M32: 192
- M64: 384

split8 GEMM：
- 768 / 768 / 1536 / 3072 CTA

block必须保持[32,2,1]。

split8 reduction grid、scratch bytes必须从真实host/kernel公式推导，不用手工猜测。

输出：
`EXPECTED_LAUNCH.tsv`

## 8. EARLY_GATE

Review pack：
`docs/vm_tlb/review_packs/C16_GROUPED_RESIDUAL_PARALLELISM_PREP_174NEW_V1/`

Gate三选一：
- `READY_FOR_RESIDUAL_PARALLELISM_NATIVE_SCREEN`
- `MAPPING_OR_SHAPE_NOT_ISOLATED_STOP`
- `SYNTHETIC_OR_MEMORY_BLOCKED_STOP`

READY至少绑定：
- source/patch SHA
- mapping proof SHA
- footprint table SHA
- expected launch SHA
- synthetic formula/version
- exact8-cell matrix
- no-GPU attestation

Gate发布后继续完整pack。

## 9. 完整输出

至少：
- AUTHORITY.json
- PATCH_SEMANTIC_DIFF.md
- MAPPING_BIJECTION.tsv
- ADDRESS_SET_AUDIT.json
- FOOTPRINT_AND_MEMORY_BUDGET.tsv
- EXPECTED_LAUNCH.tsv
- SYNTHETIC_CONTRACT.json
- EARLY_GATE.json
- SCIENTIFIC_BOUNDARY.md
- SHA256SUMS

branch：
`hrl/c16-grouped-residual-parallelism-prep-174new-v1`

最终push/fetch-back/clean/STOP。
