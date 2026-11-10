# AI-ARCH 远端既有论文研究基础（2026-11-10）

## 阅读范围与固定身份

- 仓库：`swayhrl/accel-sim-framework`。协调分支 `hrl/ai-workload-research-coordination` 的远端 HEAD 为 `b9e74381b3ca36d43d439a29a811c509af15bb8a`；最新本项目收口分支 `hrl/aiarch-q1-shn-cpu-closeout-109-v1` 的远端 HEAD 为 `ea670fcdab45aa91a0b692fd615c2fb1721a1741`。两者的 `docs/ai_workload_research/literature/` 无文件差异。
- 已逐份阅读该目录全部 **23 份 Git 跟踪文件**（22 份 Markdown、1 份 JSON 算术账本），并阅读较新的研究组合包 `f88e40123f4060328aa50a16d22fa328cee51cfe` 中 `RECENT_LITERATURE_AND_SOFTWARE_EXCLUSION.md`、`GS_PRIMARY_LITERATURE.md`、`KV_MOE_PRIMARY_LITERATURE.md`、对应两份结构化 `GS_PRIMARY_LITERATURE.json` / `KV_MOE_PRIMARY_LITERATURE.json`、`LITERATURE_REGISTRY.json` 和 `AI_ARCH_NEXT_STAGE_DECISION.md`。该包登记 9 篇重点论文和 33 条组织化实验组记录，其中 GSArch 仅摘要级；这不是 33 次独立复现。同时核对协调目录 README、CURRENT_STATE、authority 索引和统一问题图谱。
- 此处的“读完”指**读完项目远端已有的论文阅读记录及其结论**。没有在本轮重新逐页核验所引论文 PDF、作者代码和实验 raw；原记录中 `ABSTRACT_ONLY`、`PROGRAM_ONLY`、`SOURCE_ONLY`、作者实测、模拟与本机实测的等级不提升。

## 既有方法基础

主问题是 P01/P13：负载规模、输入、阶段及资源配比变化时，瓶颈如何迁移；强软件选优之后，哪些完整执行成本仍暴露。项目要求分别记录模型/输入/版本、自然工作量身份、数值与质量、阶段和完整应用分母、Host/GPU/通信重叠、共享资源，以及软件与硬件证据等级。局部算子更快、容量更大、SMEM或寄存器用量高、作者报告加速，都不能自动推出本机硬件收益。

早期 P01/P13、A2、A3、A4、A6、A10、A12–A15 已完成 NanoFlow、MPK、Bullet、Kitsune、VTC、Tawa/Twill 等近邻与资源模型的逐组审计；C16 Split-K 策略反转、NequIP 静态批量响应等有范围结果，不能推广为跨负载硬件因果。Green Context 接口资格也不是模型内资源切分收益。

## 按方向整理的既有结论

| 方向 | 已有强近邻与原记录的贡献 | 仍未获证明的事 |
| --- | --- | --- |
| 3DGS 训练 | GS-Scale 已有 GPU 几何、CPU Adam、parameter forwarding、deferred update；CLM 已有相机交集复用、选择性外观传输、双缓冲与 CPU 更新重叠；TideGS 已有 SSD/CPU/GPU working set、差分传输和轨迹调度。GSArch 是训练硬件近邻，但原 primary 全文方法仍缺。A20/A28 给出真实 Rubble、不同论文的容量/吞吐/质量分母及 GS-Scale 标称字节账。 | 不能跨 GS-Scale、CLM、TideGS 的场景、批量、训练语义和数值求直接速度排名。旧“热点 Gaussian cache / 相机重排 / 重叠 CPU Adam”不是新颖性。Q1 晚期窗口有有限接受，`shN` 驻留 V1 描述性退化；机制归因和长程质量未闭合。 |
| MoE 与 CPU–GPU 协同 | MonoMoE 已覆盖 H200/SM90a 上低 token 的融合与权重主序执行；Patterns 已研究自然路由、预测与放置；Not All Models 揭示路由局部性依模型/域而变。MoE-Lightning、DALI、CoX-MoE、HiNa-MoE 和 OSDI26 混合系统已有放置、预取、CPU AMX、NUMA 和共享主存争用。A31 的 9 MiB/专家权重是有条件逻辑字节例子。 | 随机 router/合成热点不是自然 route；H200 结果不能搬到 109 SM89。独立成本预测与并发成本之间是否存在强软件后策略反转、是否有硬件剩余，未实测。 |
| 长上下文、KV 与 Hybrid State | Strata 已覆盖分层 KV、传输布局和调度；HybridKV ACL26 是有损多模态 KV 压缩，不能替代 exact hybrid/GDN 状态管理。A70N 后续 source 审查未产生可执行幸存问题。 | 真实模型与自然会话、兼容运行时、状态端点、完整请求和质量资格仍缺；协调状态为 SECONDARY，不自动成为 GPU 任务。 |
| ANNS 检索 | CAGRA 有 visited 表遗忘及单/多 CTA；Jasper 有减状态策略；IVF-RaBitQ 有算术/片上存储折中；FROG 已实现过滤后再查 hash。A33 和 A34–A43 给出状态大小与清表寿命的条件账，以及同图同 recall 的最小诊断草案。 | 更大 hash 表同时改变重算、block 与资源占用，不能称单一硬件容量干预。GloVe 是真实向量但非现代生产 RAG；本机完整质量/性能资格及强软件后收益未建立。 |
| 点云稀疏卷积与稀疏训练 | TorchSparse++、Minuet、Spira、WarpConvNet 已处理映射、布局、正反向选择及部分缓存。A69 落到 ScanNet/OpenScene→MinkUNet34 `block1` 四个自然卷积的完整训练路径；Spira 公开端到端入口只可作前向结构反证。SNACK、SLoPe、BLaST、torchao、HASTE、FlashSchNet 提醒前向、dX、dW、结构更新与任务质量必须分账。 | ScanNet 许可/场景实体、109 ABI、自然梯度与数值尚未资格化。随机特征的结构测试不是已训练模型质量；稠密梯度可能是 STE/重新生长的算法要求，删除它不是等价优化。 |
| GNN、推荐、JEPA、VLA | GraphBolt/SDGraph 已有采样、图/特征缓存与异步供数；IGB-small 后续 FULL GPU 驻留在有界 eager 窗口形成强软件反证。FBTriton/TBE 已有元数据 hoist 与融合更新；HSTU 作者组中 DynamicEmb cache 曾使吞吐下降。M-JEPA 已处理 mask 共享/路由。SmolVLA 已有 prefix KV；vla.cpp 公开 server 串行，合成 bench 不代表多机器人共 GPU。 | 供数/cache 命中不能当完整训练收益；TBE 要先核真实 ID 和 exact optimizer；VLA 多客户端不等于并发 GPU 请求，真实 episode、模型同语义和期限证据缺。后续状态多为 PARKED/SOURCE_ONLY。 |
| RL 后训练、推测验证、视频 DiT | NeMo RL、RolloutPipe、AReaL/Libra 已有 rollout、推测和跨阶段流水；vLLM 自适应验证覆盖一般动态验证预算；Wan2.2、TeaCache、Sliding Tile Attention、CacheDit 等覆盖阶段切换、跨步复用、局部注意力及 offload。A75 严格区分作者真实训练、模拟投影、不同 GPU pool 和生成质量。 | 不能把作者 GB200 多卡步时拆分当本机资源比例，不能以跳步/降画质声称等价硬件加速。109 16GB 不具备官方 Wan2.2 720p 5B 的原设置容量资格；后续 R/D source review 已 STOP。 |

## 逐份阅读索引

远端原路径均以 `docs/ai_workload_research/literature/` 为前缀。以下列出全部 23 份，避免把多轮研究误数成同样多的获准实验。

| 文件简称 | 核心阅读结果 |
| --- | --- |
| `AI_ARCH_P01_P13_EXPERIMENT_GROUP_AUDIT_2026-10-13_V1.md` | 代表论文实验组、输入、平台和分母的证据等级。 |
| `AI_ARCH_P01_P13_RESOURCE_MODEL_CAUSAL_READING_2026-10-13_V1.md` | 资源扩展响应与软件重选、观测量和因果归因的边界。 |
| `AI_ARCH_P01_P13_ROUND_A2_EXECUTION_RESOURCE_BOUNDARIES_2026-10-13_V1.md` | 执行粒度、寄存器/SM 配额、完成时间与资源模型的限制。 |
| `AI_ARCH_ROUND_A3_HISTORICAL_EVIDENCE_CLOSURE_AND_CANDIDATE_ADMISSION_2026-10-13_V1.md` | 历史正负证据与候选准入。 |
| `AI_ARCH_ROUND_A4_NATURAL_WORKLOAD_PARALLEL_DISCOVERY_2026-10-13_V1.md` | 自然输入与并行负载候选。 |
| `AI_ARCH_ROUND_A6_NEQUIP_PATH_AND_PUBLIC_TRAINING_2026-10-13_V1.md` | NequIP 实际执行路径与静态数据边界。 |
| `AI_ARCH_ROUND_A10_TRAINING_RESOURCE_LIFECYCLE_NEAREST_WORK_2026-10-13_V1.md` | 训练状态寿命和已有近邻。 |
| `AI_ARCH_ROUND_A12_CROSS_WORKLOAD_GRAIN_RESOURCE_IDENTIFIABILITY_2026-10-13_V1.md` | 跨负载粒度与资源可辨识性。 |
| `AI_ARCH_ROUND_A13_ONCHIP_STATE_LIFETIME_STRONG_SOFTWARE_CAUSAL_AUDIT_2026-10-13_V1.md` | 片上状态寿命与强软件后因果。 |
| `AI_ARCH_ROUND_A14_SM89_RESOURCE_AXIS_AND_WORKLOAD_FEASIBILITY_2026-10-13_V1.md` | SM89 可观测资源轴与工作量可行性。 |
| `AI_ARCH_ROUND_A15_GREEN_CONTEXT_CU126_SOURCE_INTERFACE_CLOSURE_2026-10-13_V1.md` | Green Context 接口资格边界。 |
| `AI_ARCH_A20_REAL_AI_WORKLOAD_REDISCOVERY_THREE_FAMILY_AUDIT_2026-10-14_V1.md` | 3DGS、MLIP/MD、HSTU 三类真实状态生命周期筛选。 |
| `AI_ARCH_A28_RUBBLE_CLM_AND_GSSCALE_TRANSFER_SOURCE_AUDIT_2026-10-14_V1.md` | Rubble 来源、CLM 强近邻及 GS-Scale 条件字节账。 |
| `AI_ARCH_A29_3DGS_HARDWARE_HOTSPOT_AND_PARALLEL_NON3DGS_PORTFOLIO_2026-10-14_V1.md` | 3DGS 硬件论文热度与 MoE/DiT 储备。 |
| `AI_ARCH_A31_CPU_GPU_MOE_COEXECUTION_RESOURCE_FRONTIER_2026-10-14_V1.md` | CPU–GPU MoE 的三条执行路径和共享主存约束。 |
| `AI_ARCH_A33_GPU_ANNS_SEARCH_STATE_RESOURCE_DISCOVERY_2026-10-14_V1.md` | CAGRA/Jasper 强近邻、搜索状态与召回合同。 |
| `AI_ARCH_A34_A43_TEN_ROUND_DISCOVERY_JOURNAL_2026-10-14_V1.md` | 十轮候选收敛与反证，不是十个执行 Goal。 |
| `AI_ARCH_A34_A43_DERIVED_LEDGER_2026-10-14_V1.json` | 准备摊销、FBTriton 前后向净时间及梯度合并算术。 |
| `AI_ARCH_A51_A55_CROSS_DOMAIN_AI_WORKLOAD_DISCOVERY_2026-10-15_V1.md` | GNN、稀疏融合、JEPA、VLA 的真实输入与强软件筛选。 |
| `AI_ARCH_A62_SPARSE_TRAINING_DIRECTIONAL_BASELINES_DISCOVERY_2026-10-16_V1.md` | 稀疏训练三方向及 SNACK 计时边界。 |
| `AI_ARCH_A63_SPARSE_TRAINING_SEMANTICS_AND_ARTIFACT_ADMISSION_DISCOVERY_2026-10-16_V1.md` | 梯度支持集合、算法语义、结构与值寿命。 |
| `AI_ARCH_A69_QS_SCANNET_MINKUNET34_SOURCE_ADMISSION_2026-10-16_V1.md` | 真实点云训练入口与自然层组。 |
| `AI_ARCH_A75_MAINSTREAM_POSTTRAIN_SPEC_VERIFY_AND_VIDEO_DIT_DISCOVERY_2026-10-16_V1.md` | RL、推测验证、视频 DiT 的作者分母和软件排除。 |

## 阅读后的研究边界

后续论文调研应从上述已审近邻出发，优先核**新论文真正新增的工作量、平台、版本和强软件能力**；已有目录中的旧优先级须受 2026-11-09 协调状态与更晚的 shN V1 收口约束。当前 3DGS 为 PRIMARY，但本轮没有新 GPU 授权；Hybrid/KV SECONDARY、MoE H200 CONDITIONAL、Qwen PARKED，其他 SOURCE_ONLY/STOP/PARKED 不自动重开。旧负结果和数值失败仍是有效边界。

本次为远端只读阅读与本机知识整理：未下载论文/模型/数据，未启动实验或改动远端 Git。
