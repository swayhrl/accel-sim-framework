# AI-ARCH｜当前科研协调状态

**最新快照：2026-10-16 / Round A74-C已完成并STOP。** 继A73的W/H结果与A74独立审查之后，原A74-C“SM100非矩阵资源与TensorCore固定预算取舍”CPU/source-only资格任务已由**ChatGPT本窗口通过GitHub与公开网页直接完成**。本对话无SSH/109 Codex启动入口，因此**没有启动node109的Codex进程，也没有109设备资源或GPU性能测量**。该任务实际科研结果为`PARKED_FOR_PPA_OR_SIM_MODEL / STOP`，不是被批准的B200探针。

历史导航：[A74-C准备期@54d2e153](https://github.com/swayhrl/accel-sim-framework/blob/54d2e153ca927c5dd990714cd772ae3593543fb4/docs/ai_workload_research/CURRENT_STATE.md)；[A74 W/H独立科学审查](reviews/AI_ARCH_A74_A73_W_H_INDEPENDENT_SCIENTIFIC_REVIEW_2026-10-16_V1.md)。旧执行分支、报告、数据、Stop/冻结范围不修改。

## 1. A74-C科研结果：SOURCE_ONLY，不是SM100实测

**原A74-C固定Goal：** [CPU-only审查合同](goals/AI_ARCH_A74_C_ISO_PPA_RESOURCE_ADMISSION_CPU_SOURCE_109_V1.md)，预备Goal HEAD `f5ac43b4eb6adc29d040bdf65993cbd7de063db5`。独立交付分支`hrl/aiarch-a74c-iso-resource-admission-109-v1`，最终commit `d2530b3bb8a2743b716ec58e6a3113d18b66c71f`，tree `7effe7d22591998bfbef4a6f627d02be8bf09d1b`。Goal→final ahead4，只有新目录四个文件；final→该分支HEAD identical，四blob独立回读正确。通过GitHub contents API逐文件原子提交，不宣称本地git push或worktree clean。

**交付入口：**
- [完整REPORT.md](https://github.com/swayhrl/accel-sim-framework/blob/d2530b3bb8a2743b716ec58e6a3113d18b66c71f/docs/ai_workload_research/discovery/A74_C_ISO_RESOURCE_ADMISSION/REPORT.md)
- [18条原始来源与资格证据](https://github.com/swayhrl/accel-sim-framework/blob/d2530b3bb8a2743b716ec58e6a3113d18b66c71f/docs/ai_workload_research/discovery/A74_C_ISO_RESOURCE_ADMISSION/PRIOR_AND_FEASIBILITY.tsv)
- [机读DECISION.json](https://github.com/swayhrl/accel-sim-framework/blob/d2530b3bb8a2743b716ec58e6a3113d18b66c71f/docs/ai_workload_research/discovery/A74_C_ISO_RESOURCE_ADMISSION/DECISION.json)
- [诚实资源/验证RECEIPT.json](https://github.com/swayhrl/accel-sim-framework/blob/d2530b3bb8a2743b716ec58e6a3113d18b66c71f/docs/ai_workload_research/discovery/A74_C_ISO_RESOURCE_ADMISSION/RECEIPT.json)

| 资格 | 独立裁决 | 科学边界 |
|---|---|---|
| G0软硬件近邻 | `DIRECT_PRIOR_EXISTS / FORMAL_DETAIL_PARTIAL` | FA4确实MLSys2026正式版，arXiv v1有BF16 B200软件指数模拟和SM100式roofline；NVIDIA Blackwell Ultra/GB300已实际约2倍指数SFU、特定FP8 GQA约1.35倍FPROP；RISC-V VEXP等也为硬件近邻。**“更多SFU加速softmax”不是原创机制**。FA4正式PDF完整图表因抓取限制未核，不能假称其附录版本冲突已消除。 |
| G1主流模型与强软件 | `BACKEND_RUNTIME_UNQUALIFIED / WHOLE_PREFILL_WALL_UNKNOWN` | Qwen3-8B固定BF16模型配置与完整数学分母可算；强FA4/cuDNN要逐资源点重新调优。真实合法自然输入、GPU后端、数值和完整Prefill wall未获资格。4K/8K/16K理想因果QK/PV矩阵MAC占比约8.00/14.82/25.81%，**非真实Attention wall份额**。 |
| G2同面积/同功耗反事实 | `SIM_AND_PPA_NOT_QUALIFIED` | 已检查Git固定Accel-Sim源的tested-cfgs仅到SM86，ISA映射没有可认定的SM100 tcgen05/TMEM异步模型；GPGPU-Sim性能核由外部checkout加载，未审109/174本机扩展。AccelWattch文档是GV100功耗校准，**没有可信的TC↔SFU同工艺边际面积/功耗函数**。不能把B200与GB300跨代当iso-PPA。 |
| G3未来机会 | `PARKED_FOR_PPA_OR_SIM_MODEL` | SM100原生FA4 profiling仅是机会门，不允许替代真实物理资源交换。只有被独立校准的SM100模型＋单位成本＋完整模型强基线和合法输入闭合后再重审GPU/模拟器/PPA预算。 |

**H73-Q1保留为限定科研假说但暂时搁置**，不是负硬件测量，也不是当前要求申请B200的任务。A73-W的TraceLab缓存统计不能恢复原生Qwen prompt，WQ01仍为`SOURCE_INCOMPLETE / PARKED`。没有新增GPU、Simulator或Codex运行指令。

## 2. 其余冻结证据与当前Lane分工

A70 M/N/O/P四线此前均`SOURCE_SCOPE_NO_SURVIVOR`而非native负结果，固定综合见[A72](reviews/AI_ARCH_A72_A70_M_AND_FOUR_LANE_DISCOVERY_SYNTHESIS_2026-10-16_V1.md)。A73 W原结果`e7f2438aec9ee5c3ab677027c48a08dcd40c75b0`、H原结果`06b17a72f683316a4088292a4b424c9d97c7437c`，经[A74](reviews/AI_ARCH_A74_A73_W_H_INDEPENDENT_SCIENTIFIC_REVIEW_2026-10-16_V1.md)接受范围。A61/A65/A67 GNN STOP、A69 ScanNet/Q-S储备、A62/A63稀疏训练储备、C16/AWMA/ISCAS所有已有科学authority和资源边界原样冻结，不恢复任何旧Goal。

- **109/174-new/164**：本轮没有实际新模型、GPU、模拟器、权重/数据下载、外部配置更改、许可接受或资产清理；不对其它项目抢占CPU/GPU/共享锁。109 Codex在本对话没有运行回执。
- **ChatGPT**：本轮A74-C源码审查已完成。后续如继续大模型Discovery，需要转换科学入口或真正取得符合模型/质量合同的输入与资源模型，不为保持并行而重复同一“SFU更多就是新机制”的研究。
- **下个行动**：没有自动下一步作业；是否进一步投资SM100/PPA由用户基于新增模型/成本权威再审，不能用缺实测直接推定硬件加速。

**当前A74-C终态：PARKED_FOR_PPA_OR_SIM_MODEL / STOP；发布协调记录不产生109执行授权。**
