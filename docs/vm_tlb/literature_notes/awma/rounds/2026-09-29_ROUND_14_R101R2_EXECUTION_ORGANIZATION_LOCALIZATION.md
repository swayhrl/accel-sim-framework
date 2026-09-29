# Round14｜R101R2 Execution-Organization Localization

日期：2026-09-29。维护：ChatGPT。

本轮采用新的分级实验制度：L1 directed/micro，L2 CONTEXT2默认screen，L3 FULL5只给survivor。R101 FULL5不再作为日常筛选输入。

## 1. 已接受前序结论

### R101 Native

`R101_INTERMEDIATE_RETENTION_READY_FOR_ARCH_REVIEW_V1`

同map S128：
- F128 graph: ~0.4934 ms
- K128 graph: ~0.6235 ms
- fused improvement: 20.86%
- layer12 holdout: 20.09%

### R101R1 Native L2 control

`R101R1_EXISTING_L2_CONTROL_INSUFFICIENT_READY_FOR_ARCH_REVIEW`

L512:
- discard-only writeback -26.26%，runtime -3.39% performance；
- 44 MiB A+B persistence+discard没有降低writeback，runtime -2.60%。

### Transient-L2 simulator first pass

`R101_TRANSIENT_L2_TRAFFIC_RESPONSE_NO_CYCLE_GAIN`

FULL5 B0/O1/M1：
- B0 writeback 323.968 MB；
- O1 writeback -92.1033%，cycles +0.9145%；
- M1 writeback -92.0887%，DRAM reads -70.936%，L2 misses -19.387%，cycles +0.5027%。

B0 writeback与Native/source约344.7-346.9 MB同数量级且只低约6%，未调平台参数。

因此当前性能假设收缩为：

> HBM/L2 miss/writeback service并不是R101同map20% fused response的主要解释。

## 2. 新问题

F128与K128的区别不只是HBM traffic。

K128仍执行：
- global store/load instructions；
- L1/L2 access path；
- 15个NS arithmetic kernels；
- producer/consumer kernel decomposition；
- global-memory dependency/issue；
- 不同的register/shared/occupancy与instruction organization。

Transient-L2 M1显著减少lower-memory service，但没有减少L2 accesses本身：
B0 L2 accesses 151,984,336；M1 151,984,338，几乎完全不变。

这提示下一步应区分：

1. **memory service cost**：global access指令仍存在，但如果数据服务变成近片上/理想，最多能省多少cycle？
2. **execution work / organization cost**：即使memory service接近免费，global指令、kernel decomposition、instruction scheduling、occupancy等是否仍主导？

## 3. R101R2双节点并行设计

### Lane F / 109 Native profile

复用accepted discovery S128 payload和F128/K128同map实现。

不再重新证明20% timing。

做一次小型profile：
- exact same input；
- exact source；
- F128与K128正确性gate；
- compact NCU各1次（必要时最多2次/arm，仅为counter replay）；
- 静态SASS/cubin分类；
- 复用已有NSYS kernel-count/timeline authority，只有缺口才补canary。

目标比较：
- executed instruction work；
- global load/store instruction count（使用109实际支持的NCU metric，不硬编码不存在的名字）；
- L1/TEX/L2/DRAM traffic；
- tensor/math-pipe activity；
- active cycles；
- warp activity/occupancy；
- registers/shared；
- kernel launch decomposition。

不把NCU replay duration当primary timing。

### Lane E / 174 CONTEXT2 O2

从已接受FULL5 `SIM_INPUT_R101_L512_TRANSIENT_V1`确定性派生：

`R101_L512_NS_CONTEXT2_EXECORG_V1`

只引用原node164 trace members，不复制大trace。

固定scope：
- kernel 3-5：NS iteration 0，context；
- kernel 6-8：NS iteration 1，measured ROI；
- 44个L512 tile全部保留；
- A/B/X0/X1真实地址保留；
- 原sidecar的region/generation语义确定性重编号/裁剪；
- 不包含normalization，不改变trace bytes；
- 第一轮仅用于建立真实cache/context，第二轮为报告ROI。

先跑matched B0_CONTEXT2。

### O2_TRANSIENT_1C_SERVICE_ORACLE

这不是硬件方案，而是memory-service upper bound。

对合法live transient region的global-memory transaction：
- 保留原global memory instruction；
- 保留warp/CTA/issue/coalescing与kernel decomposition；
- 保留地址与producer-consumer顺序；
- 在memory hierarchy service入口处短路为固定最小1-cycle完成；
- 不访问正常L1/L2/DRAM；
- read/write/atomic语义必须只用于本trace中合法的A/B/X ping-pong transient accesses；
- 非transient access完全不变；
- 不能删除memory instruction；
- 不能修改compute instruction、kernel launch、CTA schedule；
- 不使用future per-line last-use。

O2是一个上界诊断：
它回答“如果这些temporary global accesses的数据服务几乎免费，而global指令本身仍存在，cycles最多能改善多少”。

## 4. 为什么只做一个O2

M1已证明：
- DRAM writeback几乎可全部移除；
- DRAM read大幅下降；
- L2 miss大幅下降；
- cycle仍基本不动。

所以无需再做更多cache机制。

O2进一步去掉L1/L2/DRAM service本身，是更强的memory-service上界。

若O2仍无material cycle response，cache/memory-service方向应关闭，不再设计scratchpad/cache机制来“减少latency”而没有证据。

## 5. 预注册判定

### O2 >=5% cycle improvement

分类：
`R101R2_MEMORY_SERVICE_HEADROOM_PRESENT`

说明lower-level traffic本身不是主因，但更完整的global-memory service path仍有material headroom。

下一步才值得研究：
- cross-kernel transient operand handoff；
- bounded on-chip producer-consumer buffer；
- cluster/DSMEM式local handoff；
- 与persistent scratchpad / locality scheduling最近邻做机制边界。

仍不能直接把O2当硬件速度。

### O2 <5%

结合109 profile。

若F128相对K128显著减少executed instructions/global memory instructions/kernel work，且memory hierarchy counters变化不足以解释20%：

`R101R2_EXECUTION_ORGANIZATION_DOMINANT`

停止cache/lifetime architecture方向。
后续转向：
- software/kernel fusion；
- multi-step NS pipeline；
- compute/dataflow scheduling；
- 或以R101作为software-execution opportunity收口。

若Native profile也不能形成清晰解释：

`R101R2_MIXED_EXECUTION_RESIDUAL`

只保留最小缺口，不扩大机制。

## 6. 分级制度

本轮：
- 109 profile = L1/diagnostic；
- 174 CONTEXT2 B0/O2 = L2 screen；
- 不跑FULL5；
- 不跑holdout；
- 不设计正式M2。

只有O2 >=5%才允许下一轮L3/机制设计。

## 7. 存储约束

174本地硬盘不足，保持node164共享挂载作为trace/raw authority。

不要求local staging。

效率通过：
- derived kernelslist/view；
- CONTEXT2减少模拟量；
- B0只跑matched CONTEXT2一次；
- 文档/accounting与sim并行；
- 不重复FULL5。

## 8. 当前最近邻边界

需要继续保留：
- HiMuon small-tile single-CTA fused NS；
- Flash-Muon symmetry；
- fused-muon SYRK/fused epilogue，其文档把multi-step NS pipeline列为未来方向；
- Gram Newton-Schulz rectangular algebraic transform；
- persistent scratchpad / inter-kernel reuse scheduling / Locality Descriptor；
- Hopper DSMEM/thread-block cluster。

R101R2只做定位，不提出novelty。
