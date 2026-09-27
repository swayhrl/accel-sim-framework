# Round12｜R101架构审查：先验证现有L2 lifetime control，再决定是否上174

日期：2026-09-27。维护：ChatGPT。

## 1. R101独立审查

Accepted execution:
- branch: `hrl/awma-r101-fixed-ns-intermediate-lifecycle-v1`
- commit: `cfbe6503585fa1b10d979db5d26fb9be3a80e563`
- remote compare: identical 0/0
- accepted problem state: `R101_INTERMEDIATE_RETENTION_READY_FOR_ARCH_REVIEW_V1`

该状态作为“进入架构审查”的资格成立，不等于硬件机制已成立。

关键证据：
- S128同输入、同五步多项式、同tile map，author fused F128 vs compiled three-kernel K128。
- CUDA Graph正式中位数0.493408/0.623488ms，F128快20.863%，effect/noise约50.26x。
- 独立layer12 holdout graph 0.499072/0.624512ms，方向与量级复现，快20.086%。
- L512 author graph standalone约1.666ms；完整选中optimizer graph约1.82ms discovery、2.01ms holdout；这些比例仅描述，不作为可实现加速。
- L512 3-kernel NS-family NCU DRAM write 344.716928MB，与源码推导的五轮A/B/C logical writes 346.030080MB接近；L2 requested约3556.57MB，DRAM read约122.13MB。
- 因此当前实现存在真实GPU-side intermediate materialization；但compute scheduling/occupancy/instruction差异与DRAM marginal contribution尚未完全分离。

## 2. 强软件近邻重新核查

### HiMuon自身已包含的能力

Pinned HiMuon的batched XXT和ba_plus_cAA并不是普通full GEMM：
- 都跳过对称矩阵的一半block计算；
- 都将结果镜像写回完整A/B；
- ba_plus_cAA把A@A与b*A融合；
- fused_bmm_add把B@X与a*X融合。

因此R101当前baseline已经利用了主要对称性和epilogue融合，不是弱torch baseline。

### Flash-Muon

`nil0x9/flash-muon@80ac87fb49afc792b84eccb393d051b1ed8eee32`：
- 相同(a,b,c)和5-step标准NS；
- 主要减少X@X^T和A@A的对称计算；
- 仍用global buf1/buf2/X承载跨算子状态；
- 公开Triton实现是2D，不是HiMuon 44个512x512 tile的batched retained-intermediate替代。

### fused-muon

`StarrickLiu/fused-muon@740a4d76253e7277da4fd7cf911bed7bd482b31f`：
- 相同(a,b,c) standard finite NS；
- GEMM1用CuTe SYRK/部分shape cuBLAS；
- GEMM2用SYRK+fused epilogue；
- GEMM3用cuBLAS；
- workspace仍有A、B，五步间X/X_new ping-pong；
- 文档明确将“GEMM2+GEMM3 fusion省m²访存”和“multi-step NS pipeline”列为未来方向；
- 其公开API为单2D矩阵，不是R101 batched tile map的直接强等价替代。

### Gram Newton-Schulz

`Dao-AILab/gram-newton-schulz@e45d0aca7083cb275c9a303220c05c4abecd9187`：
- 对矩形矩阵将迭代转入较小Gram对象，是代数计算图变化；
- 对正方形输入代码选择standard NS而不是Gram；
- R101 L512是512x512方形tile，因此Gram路线不直接消除该tile map；
- 官方专用kernel路径要求Hopper/Blackwell，不能当RTX4080已资格的软件替代。

结论：最近邻会削弱“只靠对称GEMM就需要新硬件”的说法，但没有已实现的、R101 exact HiMuon batched 512x512 five-step retained-intermediate软件替代。

## 3. 架构审查发现：现有PTX已经支持destructive L2 discard

NVIDIA PTX从ISA 7.4起提供：

`discard.global.L2 [ptr], 128;`

Target要求sm_80+，所以SM89在ISA范围内。

语义：对应128B L2数据可被destructively discarded，不写回memory；之后读该地址值未定义，直到重新写入。

CUDA/ISA也提供L2 eviction/persistence控制（Ampere+），可以影响producer-consumer数据在L2中的驻留。

这意味着一个自然的“短生命周期中间态最后一次使用后不写回HBM”方案，不能直接声称需要新增硬件。必须先测试现有ISA/软件能做到多少。

## 4. R101R1必须回答的问题

对accepted K128/L512 exact map做lifetime-aware control：

1. baseline保持accepted author path。
2. D1: 在stream/graph中，消费者完成后对已经dead且下一次只会被overwrite的A/B/old-X范围执行`discard.global.L2`。
3. D2（仅设备支持且D1因早期eviction不足时）：结合L2 persisting/access-policy，再在last-use后discard。
4. 所有算术kernel、输入、NS steps、coefficients、tile population不变。
5. primary timing仍用CUDA event/graph replay；NCU只验证DRAM/L2变化。

安全lifetime：
- XXT写A；
- ba_plus_cAA消费A、写B；其后A dead，下一轮只overwrite。
- fused_bmm_add消费B和current X、写next X；其后B与old X dead，下一轮只overwrite。
- 最终next X不能在optimizer消费前discard。

## 5. 决策边界

### SOFTWARE_EFFECTIVE
若现有discard/persist显著降低DRAM writes，并产生稳定material性能收益，则R101降级为software/ISA opportunity，不进入174。

### WRITEBACK_NOT_PRIMARY
若写流量显著下降但性能无material响应，则R101观察到的20%不能主要归因于HBM writeback，硬件“扩大片上容量”动机显著减弱。

### EXISTING_CONTROL_INSUFFICIENT
若现有控制因capacity/eviction、128B逐行discard开销或无法表达跨kernel lifetime而不能消除已证实material residual，且holdout复现，才进入174做bounded architecture mechanism exploration。

## 6. 潜在后续硬件问题（仅在R101R1后）

不是“把整个512x512矩阵塞进单SM”。更合理的候选是：
- compiler/runtime标注transient region/lifetime；
- L2对短生命周期dirty line提供更粗粒度dead/drop语义；
- admission/reservation保证producer-consumer窗口；
- 对提前evict的live transient line保留spill正确性；
- last-use后dirty line可直接drop，不产生DRAM writeback。

必须与现有`discard.global.L2`、L2 persistence、Hopper DSMEM/thread-block cluster、inter-kernel reuse-aware scheduling以及dead-product eviction工作区分。

本轮不启动174。
