# Lane 8 — 跨M权重复用因果对照准备

执行节点：174-new  
Lane：8  
角色：CPU-only source/contract auditor  
GPU：禁止  
GPU lock：禁止  
允许并行：Lane4、Lane6、Lane7

任务：
`C16_SPLITK_CROSSM_REUSE_CAUSAL_PREP_174NEW_V1`

## 1. 目标

把MASTER中的replica counterfactual实现成一个可审计、可在109直接执行的source contract。

第一优先级是尽快发布：
`EARLY_GATE.json`

只要证明：
- patch只改变weight-side base address选择；
- SHARED/PER_MTILE走同一patched binary/path；
- 16 replicas内存预算合法；
- K2560/K3072所有shape合法；
就可先push gate，让Lane7继续。

## 2. 精确source patch设计

基于：
- AutoAWQ kernels commit `c7b0e88c327694c715b0a758d9ce8fd414a1fa21`
- target source blob `98f49efac8626388039912e6aabc8a84d9f8303b`
- existing split1 patch authority `0e88faa28c9066b48e394dce657d7a16e6332a32`

构建一个新独立extension source，不替换accepted binaries。

在target GEMM里：
- Mtile = blockIdx_y / j_factors1
- replica_id = Mtile & replica_mask
- qweight/qzeros/scales base分别加replica_id * frozen stride

replica_mask runtime：
- 0 = SHARED
- 15 = PER_MTILE

要求：
- 两种state同一个compiled kernel；
- replica address arithmetic无branch；
- 除base offset外不改target GEMM kernel body；
- split1/split8数学与旧accepted保持；
- split1仍无reduction；
- split8仍sum(0)。

## 3. 静态证明

输出：
`PATCH_SEMANTIC_DIFF.md`

必须证明：
- A/input地址公式未改变；
- output/scratch公式未改变；
- qweight/qzeros/scales load数量/loop次数未改变；
- tile/grid/block未改变；
- dequant/mma未改变；
- 唯一新增语义是weight-side replica base选择。

如果无法证明，EARLY_GATE不得支持GPU。

## 4. Replica资产

固定M=256，所以Mtile=16。

每cell总是分配16份bit-identical：
- qweight
- qzeros
- scales

不管mask=0还是15，allocation完全相同。

input仅一份。
scratch/output按原split分配。

每份replica SHA必须与replica0一致。

内存预算：
- K2560 full W4 ≈62.34MiB ×16 ≈997.5MiB
- K3072 ≈74.81MiB ×16 ≈1197MiB
再加input/output/scratch/runtime reserve，必须<16GiB并保留充分headroom。

输出：
`MEMORY_BUDGET.tsv`

## 5. Expected launch

K2560/K3072都固定M256,N49152。

split8：
- GEMM grid 49152
- block [32,2,1]
- scratch 201326592B
- reduction grid 24576

split1：
- GEMM grid 6144
- block [32,2,1]
- scratch 25165824B
- no reduction

输出：
`EXPECTED_LAUNCH.tsv`

## 6. Correctness contract

同一split：
- SHARED vs PER_MTILE应bitwise equal。

A vs B：
- 保持既有 `rtol=1e-2, atol=5e-2`
- 若本synthetic在该K上自然bitwise equal，记录但不提高跨项目通用claim。

## 7. EARLY_GATE

文件：
`docs/vm_tlb/review_packs/C16_SPLITK_CROSSM_REUSE_CAUSAL_PREP_174NEW_V1/EARLY_GATE.json`

三选一：
- `READY_FOR_NATIVE_CAUSAL_SCREEN`
- `PATCH_NOT_ISOLATED_STOP`
- `MEMORY_OR_IDENTITY_BLOCKED_STOP`

READY必须绑定：
- patch source SHA
- old source SHA
- expected launch table SHA
- memory budget SHA
- replica tensor formula/version
- exact K/M/N/split/state matrix

发布EARLY_GATE后继续完成完整pack。

## 8. 输出

Review pack：
`docs/vm_tlb/review_packs/C16_SPLITK_CROSSM_REUSE_CAUSAL_PREP_174NEW_V1/`

至少：
- AUTHORITY.json
- PATCH_SEMANTIC_DIFF.md
- REPLICA_CONTRACT.json
- MEMORY_BUDGET.tsv
- EXPECTED_LAUNCH.tsv
- EARLY_GATE.json
- SCIENTIFIC_BOUNDARY.md
- SHA256SUMS

branch：
`hrl/c16-splitk-crossm-reuse-causal-prep-174new-v1`

最终push/fetch-back/clean/STOP。
