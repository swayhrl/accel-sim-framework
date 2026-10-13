# A22｜GS-Scale每步动态状态寿命与CPU-GPU交接（CPU-only）

**执行者：174-new既有Lane T；来源授权：[20小时无人值守计划](../ops/AI_ARCH_UNATTENDED_20H_2026-10-14_V1.md)和[Lane T双阶段Goal](AI_ARCH_20H_LANE_T_A21_A22_174NEW_V1.md)。** A21提交并停止后，用户本次明确允许仅这一项A22 CPU-only在另一个分支/worktree继续。新研究不是A21旧分支的恢复，更不是GPU授权。

**源码身份：** `SNU-ARC/GS-Scale@6471e958f7e318f4870234d8107e0aa91c2d6932`，限`simple_trainer_hybrid_optimized.py`、`simple_trainer.py`、`simple_trainer_hybrid_baseline.py`、`cpu_adam/src/cpu_adam.cpp`及按需`optimized_split.py`。以固定A21的实际commit作为只读来源，A21自然场景身份未锁不影响source-only研究，但不能从静态代码编出运行时ms、复用率或数值PASS。

## 逐门要做

1. 用`file:function:line`画一张**单个训练step**的producer/consumer图：camera及Gaussians ID、visibility、GPU gather、render、backward、gradient transfer、CPU Adam moments/counter、deferred update、densification及下一步可见性。
2. 区分**确切同步/真实依赖**与源代码允许但**未原生实测**的overlap；记录资源分母`complete_step_wall / epoch_wall / time_to_PSNR`，GPU/CPU峰值、H2D/D2H有效字节和实际可见集稳定ID（若无则UNKNOWN）。
3. 强基线至少`GPU-only gsplat`与`GS-Scale optimized host`，naive offload只是消融；定位deferred Adam epsilon/像素拆分/densification的非同语义边界，不能做虚假bitwise比较。
4. 只给一张未来**可证伪**剩余问题卡或明确`SOFTWARE_ABSORBED`：若host服务已隐藏、稳定跨步reuse不成立或完整训练wall没有可观的未消除代价，则STOP硬件cache研究。

## 交付和保护

分支`hrl/aiarch-a22-gsscale-step-state-lifetime-174-v1`；仅新增`docs/ai_workload_research/reviews/AI_ARCH_A22_GSSCALE_STEP_STATE_LIFETIME_SOURCE_MAP_174NEW_V1.md`，≤320行，`CODE_ONLY`/`PAPER_AUTHOR`/`INFERENCE`/`UNKNOWN`分层。提交、push、远端commit/tree/blob SHA回读并STOP，输出`UNATTENDED_20H_CLOSEOUT`。

最多4 CPU workers、8GiB RAM、A21+A22累计新增≤200MiB，本阶段≤4小时、两阶段总≤7小时。禁止下载自然scene、模型/依赖、CPUAdam编译、Torch/CUDA运行、109/164 SSH、AWMA/C16恢复、额外GPU实验、跨分支merge及自动再开A23/A24。工程路径/manifest问题可在同一Goal有界修复；语义/预算变化停止。
