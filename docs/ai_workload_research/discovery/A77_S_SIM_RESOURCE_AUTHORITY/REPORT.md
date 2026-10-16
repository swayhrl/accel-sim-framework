# Round A77 S77｜Ada 模拟器资源反事实资格审查

执行者：Codex S77 / node174-new；2026-10-16；CPU/source-only。

**裁决：`MODEL_AUTHORITY_NO_GO`，`PAIRING_NOT_ESTABLISHED`；0 个准入资源轴、0 个有效 pilot 点。** 保留两个源码层待验证轴，不推荐当前执行。AWMA 的有范围翻译资格成立；当前证据不足以把它升级为真实 Qwen 强后端上的 TC/L2/DRAM 资源曲线。这是模型/配对资格失败，不是 GPU 无硬件空间，也不是本轮运行了模拟器得到负性能结果。

## 1. 冻结与方法

固定 Goal HEAD `9902ead45ed61d54bd5eb0e2a998e2ccc4ba3285`，执行分支 `hrl/aiarch-a77s-simulator-resource-authority-174new-v1`。完整阅读共同 Goal 和科学设计 [S01/S02]；读取 CURRENT_STATE 的 A76、证据索引 E-C01/C03/C06/C08/C11/C14/E-A01/A02、图谱 P01/P02/P13 和协调协议冻结/发布规则。没有重做 A70–A76 文献综述。AWMA authority 固定 `29ce051f982f3854bd4392a94e4195c59340123b`，C16 terminal 固定 `ccd6928bfb420d1e4c554ec0e377bb8fbe377501`。

所有原实验数值均为已发布文本的范围事实，本轮仅核 Git 内容和重算元数据。未读取任何 trace、模型、数据集或外部现场 checkout；文中原 164 路径只是 Git manifest 的字面身份，未 stat/open/访问。未查询、等待或轮询 W77。本分支只新增 S77 四文件；其它项目、锁、配置、模拟器代码保持只读。

## 2. 平台资格不能跨级

| 已有证据 | 接受内容 | 本轮不能据此接受的内容 |
|---|---|---|
| 平台初审→后续 requalification [S10–S14] | 初审 held-out 不足后，后续用 matched-scale native 定时重新审查、冻结同一配置；保留后续 `RTX4080_ADA_PLATFORM_QUALIFIED` | 不能拿初审 NOT_QUALIFIED 覆盖后续，也不能把后续局部通过升级为全 AI timing |
| 后续 H_CACHE/H_STREAM/H_COMPUTE [S12] | Native 1.754112/2.845696/2.845696 us；sim 2.529341317/2.500998004/2.498203593 us；误差 44.195%/12.113%/12.211% | H_CACHE 是已知 outlier；后两者小且 launch-dominated，不验证持续流式带宽或 TC 执行 |
| 12 点 AI correctness [S05/S06] | T0/T1/T2 × Legacy/V1 × 10/80、0/80 共12行全部 PASS；instructions、CTA、UID、translation coverage、无重复/遗漏、controller quiescence | 没有 tensor 数值参考、完整模型输出或 TC/L2/DRAM 时间误差门，PASS 不能等同 BF16 功能/时序 fidelity |
| 交叉校准 [S08] | 工作集 M0→M1 方向一致，10/80 模拟 M1/M0=8.347872 | 精确并发 M1→M2：Native −4.5840%，sim +86.5202%；方向失配仍在，不能拟合 ns↔cycle 消掉 |
| 基准提升 [S03/S04] | `QUALIFIED_FOR_AWMA_MEMORY_TRANSLATION_STUDIES`，V1、10/80 overlay、Legacy selectable、V2R1 diagnostic、Segment F0 dormant | `BASE_CONCURRENCY_MODEL_RESIDUAL` 不被提升标签覆盖；10/80 不是 RTX4080 真实 TLB/PTW 周期 |

12点原始终止覆盖再核：T0 instructions=368696302 / CTA=224 / unique UID=3090304；T1=369131520 /384 /7159808；T2=43357696 /1216 /411008。admissions 可因重试大于 unique，不能把 admissions 当不重复的 DRAM 事务。V1 10/80 完成周期分别 527896、665802、93079 [S06]，保留为这三条 trace 的模拟事实，未转为完整请求时间。

Q05 的 10k/50k 固定周期理想翻译进度 +56.55%/+76.55% [S22 E-A01] 既非完整 kernel 加速，也非 TC/DRAM 校准。AWMA 原范围不变，不恢复 R23G 或旧机制。

## 3. 精确 ISA/config/trace 与外部性能模型

配置 [S18] 本轮按 Git bytes 重算 SHA256 `de9ee8f30325c033e0de624640ffa8803f0eae40633eebaa0b3144f549f5ccb8`；trace config [S19] 为 `a46fe47a14f3ca4116a35c5bf1dc156f4e861484b91278e8b3f6e09519bd7e5b`，均与基准 manifest 相同。基准 binary 的**已发布** SHA256 为 `a866c219b7d71a3075e032c9179bcd679074d6f2e9f1750b435170aabb413b24`，未读取该二进制、未本轮重建/验证其现场存在。

源码 [S15/S16] 在 AWMA SHA 定义 binary version 89 并映射 Ampere opcode table；HMMA/BMMA/IMMA 映射 `SPECIALIZED_UNIT_3_OP`。`trace_driven.cc:193–201` 按点号前 opcode 归类，`:468–505` 对 specialized category 用相应 latency/initiation；这不是逐种 HMMA shape/dtype 的数学正确性证明。[S17] 解析 kernel/grid/block/register/shmem/stream/binary version、active masks 和地址；trace replay 没有因此成为模型数值执行。

**启动树与执行 authority 不同：** Goal HEAD 对比 AWMA 的两个源码差异恰为新增 `ADA_RTX_BINART_VERSION 89` 与 SM89→Ampere 分派；Goal 树没有这一分派，也没有上述 Ada 配置路径。不能把 CPU 文档分支当 AWMA 可执行 baseline，更不能为让它运行而自行补代码/配置。

**外部实际核心：`EXTERNAL_SOURCE_NOT_INSPECTED`。** [S20] setup 默认克隆 `accel-sim/gpgpu-sim_distribution` 的可变 `dev`，接受既有 `GPGPUSIM_ROOT`，不是 pinned submodule；树中无对应 gitlink。 [S09/S13] 记录 reconstructed V1+V2R1、framework authority 及若干 shader/vm_translation 文件 hash，但没有闭合到基准 binary 的公开完整 performance-core commit/tree 和全部修改集。框架 SHA 或 binary SHA 不能代替该链。

有界公开读取了 [S14] 明确引用的 **engineering scaffold** `dzwduan/gpgpu-sim_distribution@dc56ca74fa51d333cacb6a8aac91bce804301ae1` 的六个文本源码及 tree。它不是已冻结 AWMA core；未将其替换成执行 authority。其 shader.cc SHA256 `786d230cd00784c4b0dcaabbbf08dd8acbe640c97c63e04125b1bf0f2da23e65` 与 [S09] reconstructed shader.cc 的 `c72fc5919587ace925639ebae74cc3a8bc200d44455f6e00d42ae387bd964f66` 不同；这仅证明这两个文件不同，不重建最终基准来源。PR #548 本次公开页面仍显示 open；贡献者关于“共享 ISA”的描述不作为精确 SM89 qualification。scaffold 的具体风险用于说明为什么不能只看参数名。

| 资源 | config 存在性与已知来源 | 真实目标 fidelity |
|---|---|---|
| TC/issue | specialized unit3=1,4,32,4,4,TENSOR，spec_op_3=32,32；pipeline topology/latencies 来自 Ada scaffold | `UNVERIFIED`；非 matched BF16 HMMA shape/并发/完整 wall 校准 |
| L2 | 64MiB 容量映射、16 subpartitions、32B data port；容量有 public-spec 来源；ROP latency=0 是 pointer-anchor calibration | `UNVERIFIED`；容量身份和 pointer latency 不等于服务吞吐/队列/并发准确 |
| DRAM | 8×32-bit controllers、GDDR6X 带宽级别；latency=190 为 pointer-anchor calibration；timing tuple 保持 scaffold | `UNVERIFIED`；不是 BF16 Qwen sustained DRAM bandwidth/并发资格。DRAM 不作为第三候选轴 |

## 4. 两个待验证控制轴（均未准入）

**A：SASS HMMA specialized initiation service。** 真正候选为 `-trace_opcode_latency_initiation_spec_op_3` 的 initiation 32→64（0.5×）或16（2×），latency 固定32；不是只改 `-gpgpu_num_tensor_core_units` 或 generic `trace_opcode_latency_initiation_tensor`。后者可能不控制 HMMA 实际路径。保留 specialized unit 数量4、ID/OC宽度4、四scheduler、RF、operand collector、writeback、SM count/clock、cache/DRAM、VM overlay、同 trace 全部不变。scaffold shader.cc 的 specialized FU 构造/issue 和 sub-core per-scheduler 端口断言表明，直接增减 unit/宽度还会牵连调度绑定，不能声称纯 TC 数量轴。修改 initiation 是否在**实际核心**形成预期服务与 pipeline 容量效应未核实；缺参数路径到 frozen binary 链与 native matched evidence，`UNVERIFIED`。

假响应：改错 generic 参数得到0响应；依赖链 latency 不变而吞吐翻倍无效；RF/issue/写回成为限制；更改 max-latency 使 pipeline 容量也变。需记录同 kernel 完成 cycles、实际 HMMA issued/retired与specialized service/stall分母，而非只读 generic TC utilization；精确 counter 名称须由 frozen core 核实，当前 `UNKNOWN`。未来 native matched control须为**相同 BF16 强kernel**的原始目标 input + 预冻结合法形状/并发压力对，输出符合原 numerical contract；只测可比较局部 kernel wall并保留完整请求wall，不用改 GPU clock 冒充纯 TC 扩展。不同 shape 的独立 trace 不能复用。

**B：L2 data/fill-port service。** 候选 `-gpgpu_cache:dl2` 最后 data_port_width 从32→16/64 B/cache-cycle，固定 sets2048、line128、assoc16、sector32、hash X、subpartitions16、MSHR192/merge4、miss queue32、容量64MiB、L2 clock、DRAM/ICNT/VM/其它轴。它同时控制 data 和 fill（以及 writeback 计费），所以只能称二者联合服务，不能称纯 hit bandwidth 或容量轴。

scaffold `gpu-cache.h:574–578,684,745–749` 解析该参数，`abstract_hardware_model.h:767–768` 定义 sector=32B、每line四sector，sector atom因此为32B；`gpu-cache.cc:1153–1188` 的 hit cycles 用ceil(data/width)，fill却用整数 `atom/width`。由此32→64使32B fill从1变0，writeback也可能截断；32B hit仍至少1cycle，不能表示两笔同cycle服务。**因此字面 B×2 在这个公开模型里不是合法2倍服务。** 这不是已证 AWMA core bug；实际 core 未审，不能替它诊断或修复。即使延迟下降也可能是假响应。仅缩成16/32的单侧试验仍不能解决校准和配对缺口，所以本轮0点。

未来 native 对照须保相同强后端/精度/算法，通过预冻结合法输入大小/真实cache冷热或并发压力控制识别L2服务与DRAM混淆；必须披露cache初态，不把修改逻辑footprint当实际流量。计数需要 L2 data/fill occupied/available cycles、hit/miss/sector访问和DRAM bytes及整kernel cycles 的同一窗口；scaffold 对应 cache stats 存在，不代表 AWMA binary 的准确分母已闭合。更改 n_mem/subpartitions 会改分区/容量/地址映射和DRAM并发；改DRAM clock会改延迟/clock比例，均不能作为B的“简单替代”。

详见 `SIMULATOR_RESOURCE_AXES.tsv`。两个参数在配置层可分别命名，**有效控制语义、彼此独立性和native fidelity未通过**；不产出可制造/同面积收益。

## 5. 单 family 配对与条件矩阵

只保留一个未来诊断对象：已有 **T1 PREFILL_GEMM_PRIMARY_OCC0** 的 kernel-family 候选，不将三条目标拼成完整请求。 [S07] producer `8f49ba3b9228b5f8a9163e961225ffd415107734`，trace `kernel-45-ctx_0x60d38cb72530.traceg.xz`，SHA256 `e36178f9a92033cd91f3c1ff4b165321b7958157c7deed2a9aaa4696e7c73e8c`，runner index `c9dd68f84606deceb8d7dcece6e35c93750b16bf507ac3666c3adb2a0e0cdc41`。路径文本标识 Qwen2.5-0.5B-Instruct s2-text prefill；具体 checkpoint/tokenizer/token IDs、natural prompt、dtype/math flags、exact强软件/backend与 Stage A MP01/MP02 的等价性**未由已读 manifest 闭合**，标 `UNKNOWN/ASSET_NOT_INSPECTED`。未重新 hash payload；SM89 admission 来自 published source/subset receipts，未读取 trace header。

[S21] Stage A MP02 B1 Graph ON/OFF 354.598206/361.456543ms 是各5正式32token request，不是这个 T1 occurrence 的 native kernel wall。B4 Mode B formal=0；compiled hooks=0/4608、runtime names只1/96直接映射，因此不能从静态FX或名字恢复 T1 对应 family 时间/coverage。强软件负对照保留 [S22] GROUP_M16 M64 split1优于split8约4.93%、L2 hit约95.95%；FFN双流74.216→81.434ms变慢9.73%。如果模型给出与这些同范围软件观察不相容的巨大收益，先排查身份/计时/模型，不能拿不同对象硬校准。

SASS reuse仅在输入/地址/active mask/控制流、同SM89 ISA与同编译kernel、launch/stream/依赖/数值程序不变且被改硬件不改变动态指令序列时条件成立。换数学kernel、compiler/backend、算法、dtype、shape、GPU ISA，或需要动态调度反馈，就要新trace和授权；不能跨架构沿用旧trace证明硬件正确。单kernel trace不能恢复未抓取的完整host/Graph/并发关键路径。

条件模板最多6点，非当前执行清单：R0=(1,1)、Ahalf=(0.5,1)、Adouble=(2,1)、Bhalf=(1,0.5)、Bdouble=(1,2)、ABdouble=(2,2)。**有效列表为空**；Bdouble控制语义不成立、实际core与matched-native链不闭合，故baseline也不启动。JSON明确区分 conditional_template 和 admitted_points，所有模板点 blocked。

## 6. 可证伪门、未来最小合同与 STOP

未来如重新授权，只考虑上述一个family，先提供完整冻结core Git tree+patch+binary identity及T1的native/input/backend/numeric对应；其后审查实际代码与合法控制，不先跑6点再补资格。资源建议仅为待审批上界：静态闭链CPU 1worker/RSS2GiB/新盘128MiB/30min；任何后续native、trace或sim运行均本轮**零授权、零执行预算**，必须由新Goal明确device/锁、sample数、数值阈值、计时边界、sim时长/磁盘和终止预算，未定不得执行。没有此材料时停止该paired项目；协调可独立考虑native-only characterization，不由S77自动派发。

最小科学反证：在同family冻结边界，baseline order/完成时间分母以及一对真实资源压力native变化不能与sim方向一致，则拒绝该轴的real-GPU counterfactual；不拟合并发负例或以10/80补救。两轴合法后才允许至多6点，记录S_A=(T0−TA)/T0、S_B及联合点非加性；kernel cycles不能除以完整请求ms，重叠kernel不能相加。预冻结 holdout/negative且不用于选参。性能容差、数值tol和统计置信必须在新实验合同按对应原生参考制定，本轮不编造通过阈值。

立即失败/STOP：core source缺失、T1自然输入/强后端无法闭链、数值或terminal失败、方向/分母失配、参数耦合或rounding造成伪服务、资源冲突/预算耗尽。需要修ISA/timing/新增统计、换输入/后端或扩大预算，均属新科学合同。当前已经命中core/配对/轴语义门，故 `MODEL_AUTHORITY_NO_GO / STOP`。没有修模拟器、没有GPU/模型/Profiler/模拟器运行、没有安装/清理、没有下一自动native。旧 SM100 结论不重开。

## 7. 可复核来源

以下固定Git来源身份已从对象库读取；hash是Git文本身份，不是现场资产存在性。公开scaffold仅供源码风险分析，层级 `ACCEPTED_SOURCE_REFERENCE_NOT_EXECUTION_AUTHORITY`。私有tmp保留下载manifest和源码SHA，提交收据同时嵌入其元数据。

- S01 [docs/ai_workload_research/goals/AI_ARCH_A77_RESOURCE_CHARACTERIZATION_PARALLEL_CPU_ADMISSION_GOAL_PACK_2026-10-16_V1.md](https://github.com/swayhrl/accel-sim-framework/blob/9902ead45ed61d54bd5eb0e2a998e2ccc4ba3285/docs/ai_workload_research/goals/AI_ARCH_A77_RESOURCE_CHARACTERIZATION_PARALLEL_CPU_ADMISSION_GOAL_PACK_2026-10-16_V1.md)；blob `9002c2679cca2415f182c647b652919debdee00e`。
- S02 [docs/ai_workload_research/plans/AI_ARCH_A77_MAINSTREAM_GPU_RESOURCE_SATURATION_CHARACTERIZATION_DESIGN_2026-10-16_V1.md](https://github.com/swayhrl/accel-sim-framework/blob/9902ead45ed61d54bd5eb0e2a998e2ccc4ba3285/docs/ai_workload_research/plans/AI_ARCH_A77_MAINSTREAM_GPU_RESOURCE_SATURATION_CHARACTERIZATION_DESIGN_2026-10-16_V1.md)；blob `c48a019bef43f9c53b7640db7055da04e682917b`。
- S03 [docs/vm_tlb/review_packs/AWMA_RTX4080_V1_BASELINE_PROMOTION_V1/KNOWN_LIMITATIONS.md](https://github.com/swayhrl/accel-sim-framework/blob/29ce051f982f3854bd4392a94e4195c59340123b/docs/vm_tlb/review_packs/AWMA_RTX4080_V1_BASELINE_PROMOTION_V1/KNOWN_LIMITATIONS.md)；blob `4041d42e33c1317a4006ffd8672b05fa714afede`。
- S04 [docs/vm_tlb/review_packs/AWMA_RTX4080_V1_BASELINE_PROMOTION_V1/AWMA_RTX4080_SIM_BASELINE_V1.json](https://github.com/swayhrl/accel-sim-framework/blob/29ce051f982f3854bd4392a94e4195c59340123b/docs/vm_tlb/review_packs/AWMA_RTX4080_V1_BASELINE_PROMOTION_V1/AWMA_RTX4080_SIM_BASELINE_V1.json)；blob `06eae005a41a29710c8fc0a4e45aa94e9c9d7653`。
- S05 [docs/vm_tlb/review_packs/AWMA_RTX4080_V1_BASELINE_PROMOTION_V1/AI_CORRECTNESS_GATES.tsv](https://github.com/swayhrl/accel-sim-framework/blob/29ce051f982f3854bd4392a94e4195c59340123b/docs/vm_tlb/review_packs/AWMA_RTX4080_V1_BASELINE_PROMOTION_V1/AI_CORRECTNESS_GATES.tsv)；blob `4e259f38e0fa1c6409caffaa34baeb8c9f515715`。
- S06 [docs/vm_tlb/review_packs/AWMA_RTX4080_V1_BASELINE_PROMOTION_V1/AI_PROMOTION_MATRIX.tsv](https://github.com/swayhrl/accel-sim-framework/blob/29ce051f982f3854bd4392a94e4195c59340123b/docs/vm_tlb/review_packs/AWMA_RTX4080_V1_BASELINE_PROMOTION_V1/AI_PROMOTION_MATRIX.tsv)；blob `c5159a78869d8d7fee76acbd2c5d62d1ee54e1ba`。
- S07 [docs/vm_tlb/review_packs/AWMA_RTX4080_V1_BASELINE_PROMOTION_V1/AI_TRACE_AUTHORITY.tsv](https://github.com/swayhrl/accel-sim-framework/blob/29ce051f982f3854bd4392a94e4195c59340123b/docs/vm_tlb/review_packs/AWMA_RTX4080_V1_BASELINE_PROMOTION_V1/AI_TRACE_AUTHORITY.tsv)；blob `9d8fd031eea7a154ae2a3ae88d0d561c297c1588`。
- S08 [docs/vm_tlb/review_packs/AWMA_NATIVE_SIMULATOR_CROSS_CALIBRATION_V1/CROSS_CALIBRATION_ANALYSIS.md](https://github.com/swayhrl/accel-sim-framework/blob/29ce051f982f3854bd4392a94e4195c59340123b/docs/vm_tlb/review_packs/AWMA_NATIVE_SIMULATOR_CROSS_CALIBRATION_V1/CROSS_CALIBRATION_ANALYSIS.md)；blob `6783495da4917bf2c93f60f5f83d4716ae809a6c`。
- S09 [docs/vm_tlb/review_packs/AWMA_NATIVE_SIMULATOR_CROSS_CALIBRATION_V1/RECONSTRUCTED_SIMULATOR_AUTHORITY.json](https://github.com/swayhrl/accel-sim-framework/blob/29ce051f982f3854bd4392a94e4195c59340123b/docs/vm_tlb/review_packs/AWMA_NATIVE_SIMULATOR_CROSS_CALIBRATION_V1/RECONSTRUCTED_SIMULATOR_AUTHORITY.json)；blob `b0d84ab5dd2f8802297151c22e84acc54f924da5`。
- S10 [docs/vm_tlb/review_packs/AWMA_RTX4080_ADA_ACCELSIM_PLATFORM_QUALIFICATION_V1/PARAMETER_PROVENANCE.tsv](https://github.com/swayhrl/accel-sim-framework/blob/29ce051f982f3854bd4392a94e4195c59340123b/docs/vm_tlb/review_packs/AWMA_RTX4080_ADA_ACCELSIM_PLATFORM_QUALIFICATION_V1/PARAMETER_PROVENANCE.tsv)；blob `7e7b856d9bd19e1f87e45a56835a3148d9e2d787`。
- S11 [docs/vm_tlb/review_packs/AWMA_RTX4080_PLATFORM_REQUAL_AND_MECHANISM_VALIDATION_V1/PLATFORM_REQUALIFICATION_DECISION.md](https://github.com/swayhrl/accel-sim-framework/blob/29ce051f982f3854bd4392a94e4195c59340123b/docs/vm_tlb/review_packs/AWMA_RTX4080_PLATFORM_REQUAL_AND_MECHANISM_VALIDATION_V1/PLATFORM_REQUALIFICATION_DECISION.md)；blob `243a1b8c603e2319963db507a99b321cbbdde42a`。
- S12 [docs/vm_tlb/review_packs/AWMA_RTX4080_PLATFORM_REQUAL_AND_MECHANISM_VALIDATION_V1/HELDOUT_REQUALIFICATION.tsv](https://github.com/swayhrl/accel-sim-framework/blob/29ce051f982f3854bd4392a94e4195c59340123b/docs/vm_tlb/review_packs/AWMA_RTX4080_PLATFORM_REQUAL_AND_MECHANISM_VALIDATION_V1/HELDOUT_REQUALIFICATION.tsv)；blob `1ee138c15d07d7d3dc6508f583fd194a4925d804`。
- S13 [docs/vm_tlb/review_packs/AWMA_RTX4080_ADA_ACCELSIM_PLATFORM_QUALIFICATION_V1/SOURCE_ANCHORS.md](https://github.com/swayhrl/accel-sim-framework/blob/29ce051f982f3854bd4392a94e4195c59340123b/docs/vm_tlb/review_packs/AWMA_RTX4080_ADA_ACCELSIM_PLATFORM_QUALIFICATION_V1/SOURCE_ANCHORS.md)；blob `1e5b4657a2f45a579c323c490492ae9c6ea3c0fd`。
- S14 [docs/vm_tlb/review_packs/AWMA_RTX4080_ADA_ACCELSIM_PLATFORM_QUALIFICATION_V1/UPSTREAM_ADA_REFERENCE.md](https://github.com/swayhrl/accel-sim-framework/blob/29ce051f982f3854bd4392a94e4195c59340123b/docs/vm_tlb/review_packs/AWMA_RTX4080_ADA_ACCELSIM_PLATFORM_QUALIFICATION_V1/UPSTREAM_ADA_REFERENCE.md)；blob `9432b816612b9d76d866d101b5267ab669708cc2`。
- S15 [gpu-simulator/ISA_Def/ampere_opcode.h](https://github.com/swayhrl/accel-sim-framework/blob/29ce051f982f3854bd4392a94e4195c59340123b/gpu-simulator/ISA_Def/ampere_opcode.h)；blob `7ca60db1b2aafd7b61e2fd4307a74256f2aa10e5`。
- S16 [gpu-simulator/trace-driven/trace_driven.cc](https://github.com/swayhrl/accel-sim-framework/blob/29ce051f982f3854bd4392a94e4195c59340123b/gpu-simulator/trace-driven/trace_driven.cc)；blob `3c08d869014ed6054c14e60f4193ab6fd29572a7`。
- S17 [gpu-simulator/trace-parser/trace_parser.cc](https://github.com/swayhrl/accel-sim-framework/blob/29ce051f982f3854bd4392a94e4195c59340123b/gpu-simulator/trace-parser/trace_parser.cc)；blob `36b2d5ee4153c0b1821920016af8315dfb110450`。
- S18 [configs/rtx4080_ada/SM89_RTX4080_AWMA_V1/gpgpusim.config](https://github.com/swayhrl/accel-sim-framework/blob/29ce051f982f3854bd4392a94e4195c59340123b/configs/rtx4080_ada/SM89_RTX4080_AWMA_V1/gpgpusim.config)；blob `3306caa589baa07c046e16fddd3066351ba10d2c`。
- S19 [gpu-simulator/configs/tested-cfgs/SM89_RTX4080_AWMA_V1/trace.config](https://github.com/swayhrl/accel-sim-framework/blob/29ce051f982f3854bd4392a94e4195c59340123b/gpu-simulator/configs/tested-cfgs/SM89_RTX4080_AWMA_V1/trace.config)；blob `07bfd7760f9073fc31d5535535c8e8707d23a625`。
- S20 [gpu-simulator/setup_environment.sh](https://github.com/swayhrl/accel-sim-framework/blob/29ce051f982f3854bd4392a94e4195c59340123b/gpu-simulator/setup_environment.sh)；blob `4f93a70c38094060bd95a1397e37e31a19fbc58b`。
- S21 [docs/vm_tlb/review_packs/C16_STAGEA_TERMINAL_INDEPENDENT_CONSUMER_174NEW_V1/STAGEA_TERMINAL_SYNTHESIS.md](https://github.com/swayhrl/accel-sim-framework/blob/ccd6928bfb420d1e4c554ec0e377bb8fbe377501/docs/vm_tlb/review_packs/C16_STAGEA_TERMINAL_INDEPENDENT_CONSUMER_174NEW_V1/STAGEA_TERMINAL_SYNTHESIS.md)；blob `810e755873fcf9d92e2c706f3894cee65618f786`。
- S22 [docs/ai_workload_research/AI_WORKLOAD_C16_AWMA_EVIDENCE_INDEX_V1.md](https://github.com/swayhrl/accel-sim-framework/blob/9902ead45ed61d54bd5eb0e2a998e2ccc4ba3285/docs/ai_workload_research/AI_WORKLOAD_C16_AWMA_EVIDENCE_INDEX_V1.md)；blob `6e1ac84ab2fe874cd815c3c6c9a6d0a7857ad19d`。

公开参考：[PR548](https://github.com/accel-sim/accel-sim-framework/pull/548)；固定 core scaffold `dc56ca74fa51d333cacb6a8aac91bce804301ae1`：

- [src/gpgpu-sim/shader.cc](https://github.com/dzwduan/gpgpu-sim_distribution/blob/dc56ca74fa51d333cacb6a8aac91bce804301ae1/src/gpgpu-sim/shader.cc)；blob `7a4ff3757c21ceace165217edbcf9b51af791b41`，SHA256 `786d230cd00784c4b0dcaabbbf08dd8acbe640c97c63e04125b1bf0f2da23e65`。
- [src/gpgpu-sim/shader.h](https://github.com/dzwduan/gpgpu-sim_distribution/blob/dc56ca74fa51d333cacb6a8aac91bce804301ae1/src/gpgpu-sim/shader.h)；blob `5922d2461eff2e099b6be44ef50aa729a1f4299f`，SHA256 `6772ea82db86bbcaf504f46df1fd49d7e4b9d7b3c5e0c484eaf938d338463c89`。
- [src/gpgpu-sim/gpu-cache.cc](https://github.com/dzwduan/gpgpu-sim_distribution/blob/dc56ca74fa51d333cacb6a8aac91bce804301ae1/src/gpgpu-sim/gpu-cache.cc)；blob `0ea9ff63d0d3b71cad82662066ce41ed722c5215`，SHA256 `40af83049fc8935b5ed97660928ac0e115487f6c3d3194d59eb77804bcd2c33f`。
- [src/gpgpu-sim/dram.cc](https://github.com/dzwduan/gpgpu-sim_distribution/blob/dc56ca74fa51d333cacb6a8aac91bce804301ae1/src/gpgpu-sim/dram.cc)；blob `80e20d795d72fe5c9068680c4f387eb034d77c43`，SHA256 `8ab6ce77309338ef12babf275feb854d9c4b6cbc56f820382fe8791c0fe4cbad`。
- [src/gpgpu-sim/gpu-cache.h](https://github.com/dzwduan/gpgpu-sim_distribution/blob/dc56ca74fa51d333cacb6a8aac91bce804301ae1/src/gpgpu-sim/gpu-cache.h)；blob `c07695fa8b7279321dff4e3da6b30290b101cc71`，SHA256 `4cf6bbdaa670594c3cd1e7cf6cbbea5d3b82b71dd731413ad761ac997ce4541c`。
- [src/abstract_hardware_model.h](https://github.com/dzwduan/gpgpu-sim_distribution/blob/dc56ca74fa51d333cacb6a8aac91bce804301ae1/src/abstract_hardware_model.h)；blob `06c3082c2cbc25e4a32a232dcb44f83c8866673f`，SHA256 `ad014e48553657441de7d0091ccacf2104846589fc2eec837ddcdebc042d4a88`。

本轮结构/元数据验证：JSON可解析、TSV固定字段与唯一axis ID、12点correctness全PASS、两配置SHA匹配、两处SM89源码差异、四文件白名单及git diff --check。未以执行测试补足source审查。发布后的精确commit/tree/四blob与SHA、远端fetch-back及clean以最终回执为准；不可把本文件自身commit递归写进其blob。
