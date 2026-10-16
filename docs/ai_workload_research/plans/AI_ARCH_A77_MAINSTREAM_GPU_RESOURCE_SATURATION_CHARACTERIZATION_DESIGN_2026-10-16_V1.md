# Round A77｜主流大模型GPU资源饱和与协同扩展：Characterization科学设计V1

**日期：2026-10-16；准备者：ChatGPT／AI-ARCH科研协调。状态：CPU_SOURCE_DESIGN_ONLY / NO_EXECUTION_AUTHORIZED。**

## 0. 科学目的与上一轮方法纠偏

研究对象是**真实的主流通用模型及其自然训练／推理阶段**，先问“GPU资源限制是否随工作量形状与阶段迁移、哪一项或哪一组资源对完成时间形成约束”，而不是预先给定Cache/TLB/SM扩展机制并倒推作者论文的负载。此前A70四线与A75 R/D的源审都合理得到0个可晋升机制，但SOURCE_NO_SURVIVOR≠GPU无硬件空间。A73 H/A74-C的SM100 SFU↔TC同面积假说因模型与PPA权威不足停在PARKED，也不得换参数重新启动。

本文件设计**先CPU-only两条并行资格审查**：W77负责输入／软件／native计时authority；S77负责accepted模拟器、ISA/配置、可调资源轴和校准。之后仅当两者确实能绑定**同一输入与强实现**，再制定一个小型GPU/native／simulator实施Goal；本设计本身不启动109/174/164、不下载模型数据、不触碰已冻结C16/AWMA/ISCAS资产，不改变历史STOP。

主问题可以在没有预先证实硬件收益时进入科学诊断，但必须能**被一个低成本实验否定**；不得反过来要求先有强软件后的“肯定headroom”才准许任何测量，从而造成新的死循环。相反，若现有模拟器无法模拟该阶段或输入不是自然任务，仍如实STOP，而不是拿不相干合成trace或弱软件填洞。

## 1. 项目内可利用证据与不可偷换的准入

| 来源／固定auth | 已被接受的内容 | 本题资格限制 |
|---|---|---|
| **C16 Stage A** [terminal](https://github.com/swayhrl/accel-sim-framework/blob/ccd6928bfb420d1e4c554ec0e377bb8fbe377501/docs/vm_tlb/review_packs/C16_STAGEA_TERMINAL_INDEPENDENT_CONSUMER_174NEW_V1/STAGEA_TERMINAL_SYNTHESIS.md)，commit `ccd6928bfb420d1e4c554ec0e377bb8fbe377501` | MP01 BF16 Prefill局部composition；MP02 compiled BF16 B1 Graph ON 354.598206ms vs OFF 361.456543ms（各5正式请求、32token正确性，有范围实测） | MP03 B4缺合法Mode B formal；compiled runtime语义family仅1/96不同kernel名直接唯一对应；Stage A四DQ=INCOMPLETE。不能用静态FX恢复family wall，不能自动恢复Stage A或称B1→B4扩展曲线 |
| **C16 W4 AWQ／Split-K** [evidence index](../AI_WORKLOAD_C16_AWMA_EVIDENCE_INDEX_V1.md) `E-C06/E-C10/E-C16` | 小M/不同K的计算片段与访存效应真实，M64已有GROUP_M16等强软件吸收，预展开会改representation | 只能作为明确局部shape/软件负对照，不是原生完整Qwen请求可加速分母；不能把流量4.04×换成理想时间加速或再发旧机制 |
| **C16自然MoE路径** index `E-C02/E-C07` | Q30等MoE选定输入与访问数据；E3自然N/U近似 | 原E3为Prefill expert-loop，而非现代fused Decode；没有自然全请求／已优化MoE后端资源敏感度。不能将合成热点H当自然控制 |
| **AWMA RTX4080/Ada Simulator** [known limitations](https://github.com/swayhrl/accel-sim-framework/blob/29ce051f982f3854bd4392a94e4195c59340123b/docs/vm_tlb/review_packs/AWMA_RTX4080_V1_BASELINE_PROMOTION_V1/KNOWN_LIMITATIONS.md) | 通过有范围平台身份/指令/翻译quiescence；对象是`QUALIFIED_FOR_AWMA_MEMORY_TRANSLATION_STUDIES` | 明确`BASE_CONCURRENCY_MODEL_RESIDUAL`、small H_STREAM/H_COMPUTE launch-dominated；**不是所有AI指令/TC/SMEM/L2/内存并发均已量化验证的SM89模拟器** |
| **AWMA Native↔Simulator交叉校准** [README](https://github.com/swayhrl/accel-sim-framework/blob/29ce051f982f3854bd4392a94e4195c59340123b/docs/vm_tlb/review_packs/AWMA_NATIVE_SIMULATOR_CROSS_CALIBRATION_V1/README.md) | `MIXED_NATIVE_SIMULATOR_ALIGNMENT / V1_NATIVE_ALIGNMENT_PARTIAL` | native/sim对照在不同阶段和并发条件下不对齐，尤其不能把10/80当RTX4080真实PTW周期；不能凭已有Ada基准宣称Qwen完整模型的计算/存储资源配置可信 |
| **旧实际GNN负发现** [A68](../reviews/AI_ARCH_A68_A67_IGB_SMALL_EAGER_FULL_RESIDENCY_INDEPENDENT_REVIEW_2026-10-16_V1.md) | 完整GPU驻留对IGB-small更快，缓存ON/OFF有反常软件开销 | 当前优先主流通用模型，不以GNN替代不具资格的LLM；保留它作为“软件反证优先”的方法学参考 |

C16／AWMA所有已有执行branch、raw/模型资产、配置、已获批准的停止条件**只读**。新Goal不继承旧项目的GPU权限或预算，不尝试重新修Stage A observer V3、compiled module identity、AWMA translation baseline，亦不在node164找其它现成模型以制造执行理由。

## 2. 分层科学对象：主模型优先，局部family辅助，不倒置

**首轮主对象候选：Qwen真实BF16 Prefill与Decode（MP01、MP02相关模型／请求）**，必须先查model revision、checkpoint/config、实际自然prompt还是synthetic/shape replay、精度、batch、输入输出、compiled eager/Graph、合法软件；如果已获接收的请求并不是有业务意义的真实输入，标`SHAPE_PROXY_ONLY`，不为使它通过而偷偷替换自然数据。

**次对象候选：现有Qwen AWQ Layer0/W4小M与大M的特定真实GEMM形状**，允许做`KERNEL_FAMILY`资源敏感度对照；但强GROUP_M16/Marlin等近邻必须参与基线，不能当整模型或同一完整请求。**不因资产存在就把它列作“自然全模型主要工作”。**

**独立负对照：** 已接受的软件吸收/端到端低权重例（W4 M64 grouped或C16 FFN双流负例），若资源扫描给出与原强软件观察矛盾的巨大硬件加速，优先定位模型/trace/计时边界错配，而非将它解释为科学惊喜。

其它主流模型（Qwen3/Qwen3.5、Dense/MoE）**只有在新的输入、相应原生科学合同与配对后端确实合格时才能纳入**；不能把不同attention体系／硬件／精度的结果组成同一规模增长曲线。模型名字不等于程序身份。

W77须给每个候选一个`CANDIDATE_LEDGER`：
`{model_revision, tokenizer_and_prompt_identity, numeric_contract, input_license, lifecycle_phase, output, backend_version, native_wall_boundary, correctness, available_GPU, compiler_semantics, trace_identity, natural_time_coverage, promotion_status}`。
不可读取具体payload时标`NOT_DISCLOSED/ASSET_NOT_INSPECTED`，不得由README推断已PASS。

## 3. 三层测量与硬件反事实的科学合同

### Level 0：native真实完成时间基准（未来，非本轮执行）

- 从同一真实输入与冻结模型选合法的strong software路径；记录**无侵入**自然Prefill/Decode或完整请求wall，单独标记模型加载、CUDA编译、首次warmup、输入tokenize、KV准备、Graph capture、采样/输出及主机排队的计时边界。
- 现有旧native可以先作为资格锚点；只能引用其真实sample/版本，不能从未完成B4实验填补图形。语义family若不可追踪，就只能采用完整请求，不插入Python模块hooks到compiled路径声称每层时长。
- 捕获最小的有范围资源反证：应用完成时间随**合法任务尺寸或强软件实现**改变（如B1→B?、Prefill长短/缓存暖态）；每一次改变仍有明确原任务语义与数值/输出可比。B4合法性不自动获得。
- 只在未来另获GPU授权后执行，109必须用`/data/c16/locks/c16_gpu_campaign.lock`非阻塞独占，覆盖模型初始化、compile/warmup和自身进程树，冲突即DEFER；无新锁/无自动后台轮询。

### Level 1：经校准的资源敏感度（模拟器未来，非本轮执行）

**先验证模拟器能否接受与native相同的单GPU指令/trace/runtime模型。** SASS记录可随同一目标ISA下部分硬件参数变化被复用，不代表不同SM arch/编译实现可复用；若变ISA、数学kernel或需要native动态调度反馈，原trace不再无条件有效。PTX与SASS也不是同样的执行源。一份GPU模拟器配置能跑完不等于有架构准确性。

给定共同目标、相同trace/sim算法，先只选**两种已校准的独立资源轴**（例如`TC/FMA执行服务`与`L2/DRAM服务`），按以下诊断抽样设计，初版不扫所有轴：
- baseline \(R_0\)；
- 资源轴A的`0.5×`与`2×`、轴B的`0.5×`与`2×`，且**每一倍数仅在模拟器实现和配置支持正确含义时运行**；
- 选择一个交互点`A2×B2×`用于判断非加性与替代关系；合计至多6点/单一资格核，含baseline。遇到交互无意义、资源加倍改变源程序语义/覆盖，则不跑；
- 任何`infinite service`仅在单独事先批准的模型明确有该oracle时使用，叫`UNPHYSICAL_ORACLE`，不是芯片面积可行上界；不做默认无限ROP/DRAM扫。

所有资源改动需列出被保持不变的GPU clock/容量/指令/任务/warp scheduling/L2/DRAM服务与实际额外修改的其他参数；SM数量增加会改变总核心数、共享缓存/带宽争用/并发，不是独立纯发射宽度轴。cache容量变大可能有命中率变化、排队、命中延迟或面积成本，不能和L2吞吐增长互换。

**最小模型校准**：不仅`terminal`、instructions/CTA/UID可对上，还要在特定目标family验证baseline顺序、内核/整体周期分母及至少一对相同资源压力方向的native实验。数据不可对齐则停止将其命名为“准确GPU瓶颈”；可保留纯模拟器内部敏感度表和“模型失配”分析，不能硬贴native百分比。

输出：
`S_A=(T_0-T_A)/T_0`与`S_B`只用于相同合法测量边界；检查\(T_{A+B}\)是否与两轴单独变化符合，记录时间与数据服务、CTA/inst coverage以及negative；真正应用不可简单把并发局部时间相加。若\(T_{\text{native}}\)与\(T_{\text{sim}}\)没有可靠一致性与新模型反事实，标`SIM_ONLY_UNCALIBRATED`，不命名可制造机制。

### Level 2：自然coverage与独立验证（需另批）

- 时间价值必须有真正的自然完整程序分母。局部kernel改善`s`对全程序上界，可在串行且独立的强前提下表示为`1/((1-f)+f/s)`；\(f\)来自合法**wall**或非重叠服务阶段，而非逻辑字节占比或模型FLOPs。多流/重叠必须用实际关键路径。
- 训练/推理阶段要分开；Prefill/Decode、smallM/largeM、量化/原生BF16不可随意平均。编译Graph与无Graph为不同完整软件模式，不等于改了GPU hardware。
- 采用预冻结的探索/holdout输入、至少一个不用于资源轴选参的原生工作量族（如相同主模型的另一合法序列长度或另一真正发行模型）。失败/数值不合格和应用没有收益的点都要完整发布。
- 只有当不同资源轴有明确应用时间解释、天然规模规律、strong software对照与跨输入复核，才讨论“瓶颈迁移”或真正硬件机制。PPA是之后独立的物理资格，不能用几倍资源理想化参数等价合成面积。

## 4. 两条CPU-only Lane，先设计、再审、再预算

| Lane | 研究领域 | 必答且可STOP的事项 |
|---|---|---|
| **W77／node109** | `workload/native authority` | 回读旧C16/相关model/输入和原生计时身份，分明真实任务与shape代理、原生window与局部指标；给`BASELINE_CARD`／自然coverage或UNOBSERVABLE；至多两个可合法升级的工作量family，优先一条BF16 Prefill或Decode主对象。无模型加载、不访问164 |
| **S77／174-new** | `simulator/resource authority` | 只读冻结AWMA Ada资格和限制、Accel-Sim GPU ISA/config、GPGPU-Sim外部源码身份可追溯性；逐轴给`SUPPORTED / PARTIAL / UNVERIFIED / MODEL_MISMATCH`，区分翻译测试通过与TC/L2/DRAM测试未证；给本Goal至多两轴和一个低成本模型校准设计，若不能合法配对native输入则`STOP_MODEL_AUTHORITY_NOT_CLOSED` |

两个Lane都可给负资格结果但不应因对方未完成而停做自己的源审。**不拼来自不同模型／GPU代际的native和sim；协调者负责对照问题卡，不在各Lane分支合并数据**。完成先审已到回执，不等待所有。

共通资源：每Lane1个CPU worker、进程树RSS≤2GiB、额外新盘≤128MiB、公开源码/论文下载≤64MiB、90分钟内收口；不运行GPU/CUDA/JIT、torch import、模型、simulator、trace抓取或Profiler，不安装依赖、不下载权重/私有数据、不删除资产、不访问164。独立branch/worktree/output；仅更新本Lane四文件。某源需从另项目仓库或外部checkout读取，仅用已发布Git SHA的**只读公开文本**；需要现场目录/二进制才能核准确性时保留`NOT_INSPECTED`并STOP对应主张，不扩大授权。

交付结构：
- W77：`REPORT.md`、`WORKLOAD_NATIVE_AUTHORITY.tsv`、`BASELINE_CARDS.json`、`RECEIPT.json`。
- S77：`REPORT.md`、`SIMULATOR_RESOURCE_AXES.tsv`、`PAIRING_AND_PILOT.json`、`RECEIPT.json`。
- 各卡必须有身份SHA/具体Git路径、来源水平、强软件先验、例外、否定条件、未来实验预算待用户审批、可证伪的科学输出。可0 eligible，输出`INPUT_OR_BACKEND_NO_GO`／`MODEL_AUTHORITY_NO_GO`而不是制造positive。
- 各自push/fetch-back精确commit/tree/四blob SHA、clean，STOP；源级设计不是已运行的native/模拟器。

## 5. 科学判断、推广与停止

| 科学终态 | 使用条件 |
|---|---|
| `SOURCE_PAIR_READY_FOR_NATIVE_AND_SIM_GOAL_REVIEW` | 两Lane仅通过CPU/source核明与同工作量族、同ISA及强软件对照有关的合法配对资格和模型校准方式；**仍须用户另批GPU/模拟器预算** |
| `NATIVE_ONLY_RESOURCE_OBSERVABLE` | 可做单独真实平台资源敏感度但无相应sim权威；不输出硬件资源“倍数”预测 |
| `SIM_ONLY_UNCALIBRATED` | 仿真能跑/能调轴但没有被接受的原生归因或相同输入：只可产生模型内部假说，不能作为实机证据 |
| `INPUT_OR_BACKEND_NO_GO` | 无合法自然输入、强后端或数值/计时完整身份；不为执行而改变模型或编译路径 |
| `MODEL_AUTHORITY_NO_GO` | 模拟器缺ISA/时序/统计/资源轴或native与sim方向明显不一致，不能产生可信反事实 |
| `SOURCE_INCOMPLETE` | Git source/private root/模型状态缺失而当前未获访问；明确具体缺口，不声称自然现象为负 |

**任何终态不得自动推广Stage A V2、C16 Tier1、AWMA旧机制、GPU cache研究、B200资源改造。** 如果两个Lane只找到已有局部(native)与翻译(sim)但不能同对象配对，协调应明确`PAIRING_NOT_ESTABLISHED`，此时可以单独重评Native-only发现，但不能伪装统一资源曲线或继续第8轮同质source审计。

**本轮A77属于已设计、待CPU Codex派发；实验与GPU执行尚未授权。**