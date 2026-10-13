# 20小时无人值守｜Lane N A23：3DGS硬件最近邻与剩余空间反证

**执行者：174-new既有Codex Lane N，CPU/source/paper-only；用户离开前一次启动。** 科研总控：[20小时无人值守计划](../ops/AI_ARCH_UNATTENDED_20H_2026-10-14_V1.md)。只有这个Goal的明确CPU任务获准，禁止GPU/模拟器/环境安装/下载大型数据。**执行前核固定Git起点、原有STOP和资源；本文件存在不表示已运行。**

## 目标与绝对隔离

**Q-N23：** 3D Gaussian Splatting完整训练中，GS-Scale已解决host卸载/优化器更新，HPCA2025 GSArch已研究Gaussian冷热缓冲/原子冲突；从作者原始实验中还有没有**可以区分软件组织与硬件资源**的未解决时间/容量限制？

仅独立审**硬件最近邻与创新冲突**；Lane T承担真实Mill-19场景与训练源码/数据时间线，双方互不等待、互不merge。旧Lane N A4 `e355f096eeac44328d7463ef3256cc649ec9cb03` STOP，其原V1报告曾发生中文字符损坏；**新输出必须严格UTF-8校验，不能覆盖旧A4工作区或伪称旧问题已修复**。

## 固定原始文献（最多4篇）

- **GSArch，HPCA2025**：优先原会议论文/作者公开全文，核真实GPU还是架构模拟、真实/合成scene、热度定义、cache/bank/atomic机制、强baseline、质量与训练完整时间；若仅IEEE摘要能合法取得则**ABSTRACT_ONLY**，绝不编造图表数值。
- **GS-Scale，ASPLOS2026**：原arXiv [2509.15645](https://arxiv.org/html/2509.15645) §3/§5，强调真正GPU-only、naive-offload、optimized-GSScale三个不同分母；作者RTX4080 Super不是本机RTX4080。已审[A20](../literature/AI_ARCH_A20_REAL_AI_WORKLOAD_REDISCOVERY_THREE_FAMILY_AUDIT_2026-10-14_V1.md)为起点，不重复大规模综述。
- **GS-Cache** [2502.14938](https://arxiv.org/abs/2502.14938)，尤其渲染**inference vs training**，不能把帧缓存当Adam状态可复用证明。
- 仅必要时再选一篇与训练硬件有关的强近邻（如Grendel/CityGaussian），固定具体版本、逐组审；不为凑篇数搜论文。

**核查矩阵**：source/paper真实平台与输入；是否独立Gaussian ID跨step复用、densification失效；CPU↔GPU状态与未重叠服务时间；GPU renderer/gradient atomics与强gsplat；参数/优化器ε数值语义；场景质量PSNR/LPIPS；是否有真正**单因子物理资源**测试。将`PAPER_NATIVE`、`PAPER_SIM`、`CODE_ONLY`、`ABSTRACT_ONLY`、`OUR_INFERENCE`严格区分。平均每步8.28%可见Gaussian**不是**时间reuse率或cache收益。

## 单一独立交付

仅在新分支`hrl/aiarch-a23-gsarch-hardware-nearest-174-v1`，新worktree，写一份
`docs/ai_workload_research/reviews/AI_ARCH_A23_3DGS_HARDWARE_PRIOR_AND_RESIDUAL_SCOPE_174NEW_V1.md`：

1. 原论文确切来源/图表组，实验对象、基线、受控变量、质量/时间/容量分母、证据等级；
2. `NOVELTY_COLLISION_MATRIX`：热Gaussian cache、梯度atomics、host state、CPU Adam、动态可见集、跨frame复用，哪些已被谁解决，哪些尚未测；
3. 一张可证伪`Q-N23`或明确`NO_HARDWARE_HEADROOM_QUALIFIED`；给出独立于Lane T的最小反例和STOP；不生成硬件机制方案；
4. `UNATTENDED_20H_CLOSEOUT`：branch/commit/tree/blob、实际源证据、未核字段、资源与UTF-8校验结果。

资源：174 CPU≤2 workers，RAM≤4GiB，新增≤100MiB，文献下载≤40MiB、单PDF≤20MiB，6小时内STOP。174根盘/swap压力高时只读API优先；不得清理旧用户数据。小型URL/ref/metadata包装问题最多2次确定性修复，自行完成readback，失败标`SOURCE_BLOCKED`而不是自动换论文。任何GPU、C16/AWMA恢复、模型/场景下载、训练/编译、跨节点访问或超预算一律STOP。

完成仅提交/push本分支，远端fetch-back核对commit/tree/blob并STOP；**没有获得自动启动其它任务或新GPU的权限**。
