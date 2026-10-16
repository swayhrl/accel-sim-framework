# AI-ARCH｜当前科研协调状态

**最新快照：2026-10-16 / Round A77，主流AI GPU资源饱和与协同扩展Characterization已完成科学设计，两个CPU-only Codex审查Goal已准备、尚未收到启动回执。** 本轮没有109/174/164上的新GPU、模拟器或Codex进程运行记录。**未来任何native／simulator执行都不从本准备文档自动获准。**

历史固定导航：[A76 R/D全部STOP、提出方法调整](https://github.com/swayhrl/accel-sim-framework/blob/c442936bf45c9070dc6058c0397b8aa6ca8681a2/docs/ai_workload_research/CURRENT_STATE.md)；[A76独立审查](reviews/AI_ARCH_A76_A75_R_D_INDEPENDENT_REVIEW_AND_DISCOVERY_METHOD_PIVOT_2026-10-16_V1.md)。A70四线、A73 W/H、A74-C、A75 R/D与其它项目的执行HEAD、原始raw及STOP全部保留，不合并旧分支。

## 1. 科研目标从“新软件遗漏”转向真实资源上限

**[A77科学设计V1](plans/AI_ARCH_A77_MAINSTREAM_GPU_RESOURCE_SATURATION_CHARACTERIZATION_DESIGN_2026-10-16_V1.md)**，首次发布commit `6c9059138168198add4682c9d9a493315901c099`，提出：从合法真实主流模型输入＋最强软件执行出发，分辨Prefill/Decode、低M/大M及完整请求的真实时间和资源限制，再基于**同输入、同ISA、已校准**的模型研究计算/issue、片上与外存服务的资源饱和规律与交互。这是研究设计，不是接受了“GPU缓存/TC必然存在增益”。

### 已有主证据与明确禁止拼接的地方

- **C16 Qwen MP01/MP02**：[Stage A terminal](https://github.com/swayhrl/accel-sim-framework/blob/ccd6928bfb420d1e4c554ec0e377bb8fbe377501/docs/vm_tlb/review_packs/C16_STAGEA_TERMINAL_INDEPENDENT_CONSUMER_174NEW_V1/STAGEA_TERMINAL_SYNTHESIS.md)证实局部BF16 Prefill组成，以及MP02 B1 compiled+Graph ON 354.598206ms/OFF 361.456543ms（各5正式请求）这一范围内native结果；但**B4 Mode B formal=0、四DQ仍INCOMPLETE、compiled family hook观测0/4608**。不可由该B1子结果补造跨batch曲线、compiler语义时间或C16 Tier1权限。
- **C16 W4/FFN软件反证**：[统一证据索引](AI_WORKLOAD_C16_AWMA_EVIDENCE_INDEX_V1.md)中的E-C06/E-C08/E-C16保留先前GROUP_M16和双流负结果；它们可作为极端trace或弱kernel性能归因的负控制，但不是完整Qwen自然请求收益。
- **AWMA RTX4080 Ada simulator**：[已接收限制](https://github.com/swayhrl/accel-sim-framework/blob/29ce051f982f3854bd4392a94e4195c59340123b/docs/vm_tlb/review_packs/AWMA_RTX4080_V1_BASELINE_PROMOTION_V1/KNOWN_LIMITATIONS.md)仅为`QUALIFIED_FOR_AWMA_MEMORY_TRANSLATION_STUDIES`，存在并发残差、small H_STREAM/H_COMPUTE launch dominance；[Native↔Simulator校准](https://github.com/swayhrl/accel-sim-framework/blob/29ce051f982f3854bd4392a94e4195c59340123b/docs/vm_tlb/review_packs/AWMA_NATIVE_SIMULATOR_CROSS_CALIBRATION_V1/README.md)结论为MIXED/PARTIAL，**不是对当前Qwen的TC/L2/DRAM资源扫描的自动合格模拟器**。两个已有证据家族必须单独核科学身份及配对。
- 不继承GNN A67全GPU驻留负结果作为LLM输入，不接管C16/AWMA的旧GPU、数据、root或配置，A74-C SM100 SFU iso-PPA模型缺口仍PARKED。

## 2. A77两个并行待派发Codex Goal

**[A77双线CPU-only Goal包](goals/AI_ARCH_A77_RESOURCE_CHARACTERIZATION_PARALLEL_CPU_ADMISSION_GOAL_PACK_2026-10-16_V1.md)**，统一固定启动HEAD **`9902ead45ed61d54bd5eb0e2a998e2ccc4ba3285`**。两独立Git分支已从该精确commit创建，启动前远端回读检查；当前`READY_FOR_USER_DISPATCH`，不是RUNNING。

| Lane / 节点 | branch | 任务及交付 |
|---|---|---|
| **W77 / 109** | `hrl/aiarch-a77w-native-workload-authority-109-v1` | 固定C16接受的Qwen原生输入、真实/shape代理、数值、软件编译身份、完整请求/局部family时间与自然coverage。最多两个可用于下一阶段资源characterization的`BASELINE_CARDS`；可0，输入/强后端不闭合STOP。输出REPORT、NATIVE_WORKLOAD_AUTHORITY.tsv、BASELINE_CARDS.json、RECEIPT。 |
| **S77 / 174-new** | `hrl/aiarch-a77s-simulator-resource-authority-174new-v1` | 固定AWMA Ada模拟器资格、Accel-Sim ISA/性能源、trace/配置与原生校准；按真实代码审能否独立控制两轴及一个合法的最多6点pilot；**模型无资格可输出0轴/0点STOP**。输出REPORT、SIMULATOR_RESOURCE_AXES.tsv、PAIRING_AND_PILOT.json、RECEIPT。 |

两条Lane互不等待、不读取其它Lane正在写的分支、不修改协调文件及旧项目；谁先报告先审。每LaneCPU工具worker≤1、进程树RSS≤2GiB、新增盘≤128MiB、公开资料下载≤64MiB、≤90分钟。**GPU/CUDA/JIT、模型import/推理、simulator执行与修改、tracer/Profiler、权重/数据集下载、安装、164访问、清理全部禁止。** 普通工程问题同一个Goal有界solve-and-continue；科学输入/精度/模型/后台权限变化STOP。

## 3. 下一阶段门槛（还没有用户授权）

只有W/S独立收口并确认**同一工作量、同一数值与强软件、同一ISA trace和模型准确性**之后才可提出新GPU/native＋simulator最小实验：

- 自然原生完整wall与有效family时间分开，不用compiled语义不可见点反推出模块服务。先两轴，经合法接口准入后最多`BASE、A0.5×、A2×、B0.5×、B2×、A2×B2×`这6点；必要时缩到零，不为凑图伪造资源轴。
- 任何TC/FMA/SMEM/L1/L2/DRAM/warp/issue变化都须对应被校准的源码/配置语义和实际工作负载；不同GPU ISA/数学kernel不能不加判断重用同一SASS trace。
- 保存无加速、方向不符、输入/编译数值/模型不合格结果。理想无限资源必须标UNPHYSICAL_ORACLE，不能用作芯片PPA结果。完整业务效果需要独立自然输入及有效时间权重，不用模拟器固定周期或逻辑流量直接称端到端。
- 即使有Native-only真实表征，也不能将模拟器未配对而获取的资源响应说成实机硬件机制。若只有Sim-only，需保留`SIM_ONLY_UNCALIBRATED`负边界。

没有新资源预算审批前，不启动109 GPU、不启动174模拟器、不触碰164模型盘。原AWMA/C16/ISCAS各自的项目任务和STOP仍冻结。

**当前实际状态：A77科学设计和两份CPU Codex任务包已经形成并固化Git；两个窗口待用户派发、0 GPU/模拟器权限。**
