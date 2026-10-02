# R26研究计划：统一软件实现与真实batch容量边界

日期：2026-10-02，Asia/Shanghai。

## 问题从哪里来

R25已经接受C1强软件基线与S2额外容量响应。C1相对B0在两点均更快、更省显存；
S2在C1上继续省显存，但速度方向不跨模型保持。因此下一步不挽救Llama的0.13%
计时方向，也不追加微基准，而是验证节省的梯度显存能否转化为实际训练能力。

本轮仅问：同一16GB RTX4080、同一Llama模型/context/optimizer和仅tied W可训练
语义，S2能否完成C1自然OOM的更大physical batch？

## 设计选择及其限度

复用accepted Llama-3.2-1B与ADOPTED_LLAMA_S0_T128_V1，避免新资产与新输入工程。
T=127保持，增加B时物化重复的同一序列。真实执行更大batch，但不增加数据多样性；
它是容量压力与数据流检查，不能用于训练质量、收敛或独立data holdout主张。

保持仅tied W训练，不同时引入全参数optimizer、LoRA或checkpointing。整条backbone
仍真实前向/反向；只有参数更新集合受限。Production-oriented指同一可复用组件、
明确API/状态保存恢复/两个policy，而不是已经可以部署于任意训练系统。

C1为新组件默认policy；S2容量模式显式opt-in；既有工作流的采用仍默认OFF。
两者共享compact reducer和AdamW语义。清理harness多余GPU副本与逐步冷清cache，
但不引入新的数学算法、CCE或性能调优。

## 冻结顺序

1. 闭合已有model/input/source authority。
2. 单组件C1/S2实现；B0只用于短数值anchor。
3. B1 one-step、4-step anchor、32-step C1/S2 trajectory、checkpoint resume及policy切换。
4. implementation与classifier freeze。
5. 唯一B轴的自然OOM搜索、3/3端点与同batch witness确认。
6. 在唯一B_common点做数值复核及30条formal计时。
7. 按完整合同收口与STOP。

32步重复batch只检查optimizer/dataflow一致性。数值界沿用rtol=atol=1e-2，不随
步数/B放宽。长轨迹数值失败是qualification STOP，不是容量/性能negative。

## 容量与时间的解释

容量主证据是同batch C1 OOM、S2连续完成训练步，三个干净进程重复成立。OOM阶段、
完整step peak、C1 FP32累积workspace、S2 tile、backbone activation和持久状态均记清。

目标区域省显存但共同forward/backbone峰值限制B，是合法的“本配置无batch扩展”。
B=512仍可运行属于右截断；不扩大预算找positive。禁止ballast/人为VRAM限制。

Formal只在最大共同确认可运行B比较两policy，计入全部必要工作；TARGET_REGION
与COMPLETE_TRAIN_STEP分别给时间方向。Positive容量可以伴随时间regression，继续
定位容量opt-in，不包装成统一加速。

## 精确发布

Handoff: `hrl/awma-r26-tied-weight-production-capacity-handoff-v1`
HEAD: `67bb4c00236e52657130dd91ddf44fb6a2e22c87`
Tree: `309903b65d4c0aaf13a4506efb5a9ce93d508608`
Execution to create: `hrl/awma-r26-tied-weight-production-capacity-109-v1`
Stage: `AWMA_R26_TIED_WEIGHT_PRODUCTION_CAPACITY_BOUNDARY_109_V1`

完整合同与machine-readable常量：
`docs/vm_tlb/chatgpt_handoff/awma/r26_tied_weight_production_capacity_v1/`。

当前状态：AUTHORIZED / HANDOFF_READY，尚无本轮节点执行报告。
F/E/174与已关闭旧Goal不恢复；无hardware/PPA。
