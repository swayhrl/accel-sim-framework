# AI-ARCH｜当前科研协调状态

**快照日期：2026-10-14（A44审查后）。维护者：ChatGPT／AI-ARCH Discovery。**

本页是研究导航，不是节点监控或GPU执行授权。AI-ARCH负责Discovery及总体协调；AWMA由原独立窗口管理；C16为冻结历史证据。遵循[协调协议](COORDINATION_PROTOCOL.md)、[问题图谱](AI_WORKLOAD_ARCHITECTURE_PROBLEM_ATLAS_V1.md)与[证据索引](AI_WORKLOAD_C16_AWMA_EVIDENCE_INDEX_V1.md)。

历史导航：[A30及更早@15d20bb0](https://github.com/swayhrl/accel-sim-framework/blob/15d20bb0bbf045e9dc05f2d51eecb70c9b0cfd5f/docs/ai_workload_research/CURRENT_STATE.md)、[A32收口@80c4362f](https://github.com/swayhrl/accel-sim-framework/blob/80c4362fbe79fc92fb82c786513153a4f7231bb7/docs/ai_workload_research/CURRENT_STATE.md)、[A33状态@c2dc0642](https://github.com/swayhrl/accel-sim-framework/blob/c2dc064265dafcb4f5cebfe9d0f75f150d10aeb1/docs/ai_workload_research/CURRENT_STATE.md)。原报告、Goal、commit及scientific authority均不改写。

## 0. 执行状态：A26GR1已真实STOP并完成A44审查；T/N仍STOP

| Lane | 当前已知状态 | 不变边界 |
|---|---|---|
| M／109，A26GR1 | 真实从零连续训练到15200步，最终commit `cf80f6ec07a31eccdaff264c3bce64e0511179f8`，**SOURCE/NATIVE SCOPED COMPLETE / STOP**；已被A44独立审查 | 执行合同已结束；历史raw/预算不改写；没有下一项GPU或新机制自动授权 |
| T／174-new，A30T | 源审完成STOP，提交`1a8b9317de4c16e3dd19018f7f42cae1ebf5750e`，已由A32独立审查 | H200/SM90a条件性发现卡，非109可执行任务；不自动恢复 |
| N／174-new，A30N | 源审完成STOP，提交`6f78a2e1e9a2fdb04bc9468f4b2d5594bc3229a6`，已由A32独立审查 | DiT当前具体候选证据不足；不移植DiSC、不自动恢复 |

A44审查由本窗口通过GitHub只读执行，未新开Codex，未登录109/174/164、未下载新资产至节点、未执行GPU/模拟器。M执行终态是用户提供且有固定Git收据，核验不等于本窗口实机复跑。

## 1. 最新独立审查：Round A44｜真实3DGS训练PASS及线程归因纠偏

[**A44独立科学审查**](reviews/AI_ARCH_A44_A26GR1_NATIVE_THREAD_ATTRIBUTION_REVIEW_2026-10-14_V1.md)。M报告与固定Git、原始15,200条逐步raw、150步CUDA事件、执行代码和冻结作者源码核验完成。R0/R1/R2/R4 PASS，R3为有边界原生PASS；后期未插桩均值132.480/133.810ms，两次连续运行相机顺序一致，但Gaussian状态不逐bit相同；200k收敛和晚期GPU-only未证。

**独立发现的必要修正：** 原`30.871/32.128ms`是GPU工作子线程＋主线程的跨线程同步、join与D2H区间并集，不是全部主线程暴露等待；仅主线程并集`14.084/14.746ms`。GPU worker约17ms同步大多与CPUAdam重叠；45/49、50/50个正常CPUAdam步骤里，GPU工作子线程先于CPUAdam结束。当前更具体的问题是OMP16下CPU处理/数据交接与软件分工，**不是已证明Cache、CPU带宽或PCIe硬件headroom**。两条结果均保持历史raw，纠偏只作为协调独立附注。

**权限：** Lane M原Goal正式STOP，不重跑15k、不自动新建A26GR2、不同步未审新实验到AWMA/C16。下一步先让软件已覆盖能力与线程策略/准备阶段反证；只有存在新的、具体的完整时间剩余，才另行讨论有界CPU/GPU原生实验。A43稀疏卷积、A33 ANNS仍为独立候选。

## 2. 最近Discovery：A34—A43十轮已完成

用户要求连续十轮研究，执行者为ChatGPT／AI-ARCH Discovery，起点`c2dc064265dafcb4f5cebfe9d0f75f150d10aeb1`。

[**十轮完整Git研究日志**](literature/AI_ARCH_A34_A43_TEN_ROUND_DISCOVERY_JOURNAL_2026-10-14_V1.md)；[**纯算术推导记录**](literature/AI_ARCH_A34_A43_DERIVED_LEDGER_2026-10-14_V1.json)。本会话另提供扩展报告、十份逐轮笔记、来源登记、算术脚本和校验包。不是十项新硬件创新或十个待执行Goal。

| 轮次 | 科学推进 | 决策 |
|---|---|---|
| A34 | ANNS算法质量前沿与固定资源诊断分离 | A33三条hash路径不是纯物理资源干预；保留小发现 |
| A35 | FROG过滤/compaction后再查hash | 直观lazy-hash新机制被覆盖，过滤型ANNS降级 |
| A36 | GrAND更新/删除/延迟维护与active-set真值 | 不能漏计修图债务；不扩动态图系统 |
| A37 | TorchSparse++/Minuet/PCEngine映射与特征计算 | 新增直接神经网络稀疏卷积候选 |
| A38 | Spira提前全网映射、真实计时与缓存reset | 撤回无证据的eager映射内存爆炸动机 |
| A39 | Insum/WarpConvNet的格式准备、复用寿命与前后向布局 | 保留完整结构有效期问题；条件摊销不冒称实测 |
| A40 | SpGEMM累加器与结构复用 | 数值partial sum不能照搬visited遗忘规则 |
| A41 | FBTriton训练metadata前移与optimizer提交 | 相对强软件的额外代价未知，TBE留储备 |
| A42 | Spira固定loader/runner输入与计时源审 | 真实坐标+随机特征是结构型执行，非任务精度验证 |
| A43 | 两项最小反证设计和候选收敛 | Q-S神经网络相关性优先；Q-A增量成本优先；不新开任务 |

**关键新增源码证据：** `SPIN-Research-Group/Spira@aee69c61f3e001f72828a6d5a70f6a1200166f65`，直接读四文件。端到端脚本在每个输入前reset，并把排序/映射/model计入；loader随机生成特征。不能把它当漏计准备的弱基线，也不能把结构型实验称训练好模型的真实分割质量。未运行该代码。

**关键反证：** Spira正式论文的约40MB映射与渐进缓存方案最终空间相近；FROG已有晚查hash；TBE的前向开销增加必须从反向收益扣除。全部是作者/源码或独立算术，不是109新测量。

## 3. 现有候选排序：只到发现层

**Q-S：点云稀疏卷积的结构准备—布局—消费有效期。** 直接神经网络相关性优先。一个真实坐标对象、一个实际层组、最多两条强可实现后端；完整计入准备/变换和合法复用。Spira及适用TorchSparse++/Minuet优先，不能强制重复build造问题。尚无本机ABI/数值/性能资格；坐标型结构研究不必先有整模型任务精度，但不能扩大claim。

**Q-A：ANNS每查询状态与并发。** A33继续作为较小部署规模备选。真实图/query、同recall强参照、AUTO与显式配置；12格仍是未批准草案。若差距只来自已知hash/reset策略或质量变化，停止硬件问题。

**Q-E：TBE训练状态储备。** 强CUDA/Triton、真实ID/run分布及完整forward/backward/update边界先成立；不把GB200作者结果移到4080，不为广泛已覆盖的hoist/split再做机制。

优先级不是已经证明的研究收益。没有新硬件headroom或PPA、没有执行许可。下一项必须实际测的问题不宜无限重复源审；选中后另定一个有界连续canary→小矩阵合同，普通工程问题自行闭环，科学身份/预算变化才停。

## 4. A33及更早结果继续保留

[A33 ANNS](literature/AI_ARCH_A33_GPU_ANNS_SEARCH_STATE_RESOURCE_DISCOVERY_2026-10-14_V1.md)的固定cuVS源、条件字节表及GloVe候选仍是source-level证据，不是本机实验。

[A32 T/N独立审查](reviews/AI_ARCH_A32_A30T_A30N_INDEPENDENT_SCIENTIFIC_CLOSEOUT_2026-10-14_V1.md)保持。MonoMoE的软件加速不是强Mono之后硬件headroom；DiSC专用硬件模型不等于强GPU稀疏路径。两条STOP不否定整个MoE/DiT领域。

[A31 CPU–GPU MoE](literature/AI_ARCH_A31_CPU_GPU_MOE_COEXECUTION_RESOURCE_FRONTIER_2026-10-14_V1.md)共享主存与策略排序问题留储备，无本机策略反转或新GPU任务。[A29组合](literature/AI_ARCH_A29_3DGS_HARDWARE_HOTSPOT_AND_PARALLEL_NON3DGS_PORTFOLIO_2026-10-14_V1.md)及[A28 Rubble/CLM](literature/AI_ARCH_A28_RUBBLE_CLM_AND_GSSCALE_TRANSFER_SOURCE_AUDIT_2026-10-14_V1.md)不变。原A26G STOP与单独授权A26GR1不能混成一次执行。

## 5. 科学与权限边界

发现允许合理强对照下的小预算观察，不要求预先完成全部oracle。硬件贡献需强软件后的因果与有限成本证据；目标family、应用加权和end-to-end分层，不用全应用5%统一判死。

固定软件资源响应与允许软件重新选优后的收益不同。真图/真坐标、真实训练好数值与任务质量也不同。不得以维持并行为由填充空闲窗口；不恢复C16 Stage A、NequIP/Green Context或AWMA旧任务。M已完成A44限定范围独立审查，当前没有新的已授权M实验。
