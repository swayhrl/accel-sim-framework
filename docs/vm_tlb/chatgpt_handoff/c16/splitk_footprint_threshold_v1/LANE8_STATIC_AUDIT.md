# Lane 8 — Split-K工作集静态机制审计

执行节点：174-new  
Lane：8  
角色：CPU-only static mechanism auditor  
GPU：禁止  
GPU lock：禁止  
允许并行：Lane4、Lane6、Lane7

任务：
`C16_SPLITK_FOOTPRINT_STATIC_AUDIT_174NEW_V1`

## 1. 目标

回答一个非常具体的问题：

> AutoAWQ split8是否真的把不同M tile之间反复消费的weight+metadata静态唯一集合，从完整矩阵规模缩小到一个显著小于64MiB L2的集合？

只做源码和算术，不运行GPU。

## 2. 精确源码authority

必须核：
- repo `casper-hansen/AutoAWQ_kernels`
- commit `c7b0e88c327694c715b0a758d9ce8fd414a1fa21`
- `awq_ext/quantization/gemm_cuda_gen.cu`
- expected blob `98f49efac8626388039912e6aabc8a84d9f8303b`

同时核本项目accepted：
- split8 binary/source lineage；
- split1 direct-output patch；
- GPT3 proxy synthetic formula；
- K=12288 W4 shape/metadata。

## 3. 尽快发布STATIC_GATE

不要等完整pack。

第一阶段独立证明/否证：

1. blockIdx.x → split/Mtile/Ntile映射；
2. qweight B地址是否与M tile无关；
3. qzeros/scales地址是否与M tile无关；
4. split8 K tile是否为mod8 interleave；
5. 对固定split z、固定N tile，不同M tile是否重复访问同一weight地址集合；
6. 对线性block ID，从M tile m到m+1同N tile之间，是否经过一个N-tile sweep；
7. 每split唯一qweight/qzeros/scales byte集合精确值。

必须写：

`docs/vm_tlb/review_packs/C16_SPLITK_FOOTPRINT_STATIC_AUDIT_174NEW_V1/STATIC_GATE.json`

并立即push一个中间commit。

Gate三选一：

- `SUPPORTED_PROCEED_NATIVE_THRESHOLD_SCREEN`
- `NOT_SUPPORTED_STOP_NATIVE`
- `AMBIGUOUS_STOP_FOR_REVIEW`

SUPPORTED要求全部核心映射闭合；任何关键地址依赖不明则不能放行。

## 4. 精确集合算法

不要只做总bytes/8。

对每个K：
- 2048
- 2560
- 3072
- 4096
- 12288

以及旧Qwen K=3584,N=18944：

枚举/解析kernel公式，计算每个split z：
- unique qweight byte intervals；
- unique qzeros byte intervals；
- unique scales byte intervals；
- 128B line数；
- 总unique bytes；
- /64MiB；
- split间metadata overlap；
- split间qweight overlap；
- 对同一N tile跨M tile的地址集合Jaccard（理论应为1则验证）。

输出：
`PER_SPLIT_FOOTPRINT.tsv`

特别检查：
- GPT3 K12288 split8单split是否约41.625MiB；
- 旧Qwen split1完整W4是否约33.64MiB；
- 2560完整W4约62.344MiB；
- 3072完整W4约74.813MiB。

如果精确枚举与这些预估不一致，使用源码结果并在gate说明，不能为了匹配预估修改算法。

## 5. 线性block-ID复用距离proxy

静态生成：
`BLOCK_ID_REUSE_MODEL.tsv`

对M=256,N=49152：
- Mtile count=16
- Ntile count=384

对split1和split8，记录：
- 同一N tile从Mtile m到m+1的block-ID距离；
- 两次使用之间涉及多少其他N tiles；
- 这些intervening N tiles联合覆盖的weight+metadata unique bytes。

明确：
这是**线性block-ID proxy**，不是实际CTA调度顺序、cache replacement或hit率。

## 6. K-threshold新点合法性

验证K=2048/2560/3072/4096：
- divisible by32；
- group_size=128合法；
- qweight/qzeros/scales shape满足kernel；
- N=49152满足OC约束；
- split1/8 k_bound没有非法空split；
- A/B output/scratch/reduction shapes与K无关；
- A/B grid与K无关。

输出：
`K_THRESHOLD_POINT_CONTRACT.tsv`

## 7. 完整报告

Gate push后继续CPU-only完成：
- `SOURCE_BINDING.json`
- `ADDRESS_MAPPING.md`
- `PER_SPLIT_FOOTPRINT.tsv`
- `BLOCK_ID_REUSE_MODEL.tsv`
- `K_THRESHOLD_POINT_CONTRACT.tsv`
- `SCIENTIFIC_INTERPRETATION.md`
- `FINAL_DECISION.json`
- `SHA256SUMS`

最终中文解释必须区分：
- 源码证明的地址复用关系；
- 线性block-ID推导；
- 真实GPU调度/命中尚未证明。

## 8. branch

从coordination HEAD建立：

`hrl/c16-splitk-footprint-static-audit-174new-v1`

普通工程问题solve-and-continue。

最终push/fetch-back/clean/STOP。
