# Round A77｜主流AI GPU资源饱和Characterization：两条Codex并行CPU资格Goal包

**日期：2026-10-16；状态：PREPARED_AWAITING_EXPLICIT_USER_DISPATCH。** 本文件由科研协调者发布，是**新CPU-only资质审计任务，不是GPU/native/simulator执行授权**。独立分支的固定Goal HEAD由本文件提交所得精确commit派发。用户发到目标节点Codex窗口后才视为已授权该source-only Goal；ChatGPT不能在此通过GitHub创建分支而直接启动109或174进程。

先完整阅读科研设计：
`docs/ai_workload_research/plans/AI_ARCH_A77_MAINSTREAM_GPU_RESOURCE_SATURATION_CHARACTERIZATION_DESIGN_2026-10-16_V1.md`

并固定阅读以下研究背景的范围，不必重读A70—A76全部论文：
- `docs/ai_workload_research/CURRENT_STATE.md` 的最新A76协调状态；
- `docs/ai_workload_research/AI_WORKLOAD_C16_AWMA_EVIDENCE_INDEX_V1.md` E-C01/C03/C06/C08/C11/C14/E-A01/A02， `AI_WORKLOAD_ARCHITECTURE_PROBLEM_ATLAS_V1.md` P01/P02/P13；
- `docs/ai_workload_research/COORDINATION_PROTOCOL.md` 相关冻结边界、fail-closed、solve-and-continue、发布规程；
- C16 Stage A terminal `ccd6928bfb420d1e4c554ec0e377bb8fbe377501`及AWMA fixed `29ce051f982f3854bd4392a94e4195c59340123b`只读报告；**不重新操作两个项目**。

## 0. 两条独立Lane，不同目标

| Lane / 默认节点 | 独立执行分支 | 写入本分支唯一目录 | 研究目标 |
|---|---|---|---|
| **W77／node109** | `hrl/aiarch-a77w-native-workload-authority-109-v1` | `docs/ai_workload_research/discovery/A77_W_NATIVE_WORKLOAD_AUTHORITY/` | 核已接受的真实Qwen原生输入/模型/强软件/数值/完整wall/family归因，提出最多两个真正可作为资源characterization输入的baseline family |
| **S77／174-new** | `hrl/aiarch-a77s-simulator-resource-authority-174new-v1` | `docs/ai_workload_research/discovery/A77_S_SIM_RESOURCE_AUTHORITY/` | 核AWMA Ada模拟器资格与Accel-Sim配置/ISA/原生校准边界，静态确定哪些资源轴具备有意义的控制量、同一负载是否可配对 |

两个Lane独立分支和output，**不互相等待、不轮询对方、不得修改协调分支或其它项目**。谁先完成就先给用户回执，ChatGPT逐个审查。W不能借模拟器论证自己的原生GPU数据；S不能按已有AWMA翻译模拟器通过而宣布C16 Qwen完整模型已被cycle calibrated。

## 1. 共同资源合同

- 所有执行仅CPU/source/已有GitHub冻结公开文本。每Lane最多**一个CPU工具worker**，有效线程OMP/BLAS/Git pack/index=1，进程树RSS≤2GiB，新增worktree/tmp/raw/日志≤128MiB，公开文献/代码网络下载累计≤64MiB，90分钟封顶；资料足够及时STOP。不得启动子agent池或无界CPU索引。节点重载/资源竞争严重则`RESOURCE_DEFERRED`，不杀/重启别人进程。
- **禁止**CUDA/GPU初始化、torch/vLLM实际模型import或推理、模拟器运行/构建/更换配置、采集新的trace、任何NCU/NSYS/NVBit，权重/用户数据集下载、安装依赖、扫描164、清理或写缓存、接受数据协议、重放已STOP的C16/AWMA实验。禁止为确定CUDA版本而在109运行GPU程序；只能只读固定历史source和发布日志，若缺当前资格标UNKNOWN。
- 使用独立sparse worktree、branch、tmp/output，保持路径白名单；可用官方GitHub精确commit读取其它项目已有报告，不merge/cherry-pick执行HEAD，不修改旧raw和共享manifest。不要走旧Codex工作目录的write paths，尤其C16/W-AWMA当时的runtime.env与原有共享campaign lock。
- 小CLI、文本解析、包装/路径错误在预算内solve-and-continue；科学模型/输入/精度/软件版本、资源限额或访问不合规时STOP报告。不为让某一family“合格”放宽要求、换模型/尺寸/数值阈值、偷偷开Profiler或追加native。
- 输出每一行区分`ACCEPTED_SOURCE`、`ACCEPTED_NATIVE_SCOPED`、`ACCEPTED_SIM_SCOPED`、`DERIVED_CPU`、`UNKNOWN`与`NOT_DISCLOSED`。Git commit/hash和部分raw能读不等于现场可复现性PASS；作者论文数值不是109实测。不得把理论指令上界当可制造资源。

## 2. W77任务：逐对象冻结真实工作负载和强原生基线

**唯一科学问题：现在是否真的有一个主流Qwen真实请求/算子族，其完整模型或family合法原生观测足以作为后续资源轴扫描的可靠分母？**

1. 固定[Stage A终态](https://github.com/swayhrl/accel-sim-framework/blob/ccd6928bfb420d1e4c554ec0e377bb8fbe377501/docs/vm_tlb/review_packs/C16_STAGEA_TERMINAL_INDEPENDENT_CONSUMER_174NEW_V1/STAGEA_TERMINAL_SYNTHESIS.md)和其索引到的原始MP01、MP02、MP05，以及Qwen AWQ W4（若可低成本获得）。核producer/consumer exact SHA、所选模型config/权重的已收SHA身份、真实用户任务prompt还是synthetic/shape代理、输出正确性、Graph/compile/precision、trace/运行态。已接受MP02 B1 354.598/361.456ms是`32token request-level`，B4 Mode B formal=0。严格区分MP01局部family组成vs完整compiled Mode B请求时间与语义映射0/4608 hook失败。
2. 查并说明`can these accepted source data be tied to an actual legal natural tokenized request or model layer input?` 不能从文件名“Qwen3”或随机tensor推断真实输入；不能用从别人README复制的prompt把原freeze raw变成新业务。若只有C16 family/operator输入，允许标`KERNEL_FAMILY_DIAGNOSTIC_ONLY`而非借用自然whole-run身份。
3. 至少列两个**被否定/局部**的强软件反证（W4 GROUP_M16、大M强GEMM，以及FFN双流负例或vLLM fused gate/up）说明为何不能用弱软件的流量/时钟异常做资源上限。只读原报告而非重跑这些negative。
4. 建立每个候选的机器可检查字段：`model/tokenizer/weights SHA`、`input source/text or token IDs`、`revision/split/seed/batch/context/precision`、`backend graph compile`、`native time boundary with repetitions`、`numeric/quality and reference repeatability`、`family time observability`、`natural coverage`、`available native hardware`、`trace ISA and source`、`missing scientific authority`。
5. 给0—2份`BASELINE_CARDS`，排序优先真实Qwen BF16 Prefill/Decode而非成熟强内核缺失的第三方特别模型；每卡必须有可证伪的最小表征问题，明确`WHOLE_REQUEST_NATIVE`或`KERNEL_FAMILY_NATIVE`或`SHAPE_PROXY_ONLY`，配独立验证输入/负对照。**不能先决定跑B1→B4再补未通过的B4数值路径**。
6. 若已有数据不足以解释资源归因，W应给一个**最小新native数据资格建议**（只做PROPOSAL）：确切强软件路径与模型、自然输入、未插桩完整wall、唯一科学反证、可STOP方式、109锁/VRAM/CPU/下载事先预算待定。没有明确源对象则`NATIVE_INPUT_OR_BACKEND_NO_GO`，不设置下载任务。

**交付四文件**：`REPORT.md`（科学裁决与旧原生证据）、`NATIVE_WORKLOAD_AUTHORITY.tsv`（每个观察及可复核source）、`BASELINE_CARDS.json`（0—2候选，状态与缺口）、`RECEIPT.json`（资源和publish细节）。禁止发布一个声称自然B4/native全模型资格已通过的Goal。

## 3. S77任务：当前模拟器到底能否对这个主流模型做资源扫描

**唯一科学问题：原AWMA Ada模拟器权限与C16原生Qwen阶段之间，是否存在合法的trace/配置/ISA和校准链，足以做至少两个独立硬件资源轴的受控测试？**

1. 独立只读查[AWMA已接受平台限制](https://github.com/swayhrl/accel-sim-framework/blob/29ce051f982f3854bd4392a94e4195c59340123b/docs/vm_tlb/review_packs/AWMA_RTX4080_V1_BASELINE_PROMOTION_V1/KNOWN_LIMITATIONS.md)及[Native↔Sim Cross Calibration](https://github.com/swayhrl/accel-sim-framework/blob/29ce051f982f3854bd4392a94e4195c59340123b/docs/vm_tlb/review_packs/AWMA_NATIVE_SIMULATOR_CROSS_CALIBRATION_V1/README.md)、基准的12点正确性收据及具体已冻结workload/config/trace ISA。**只读Git文件**，不恢复任何R23G等翻译机制或reset sim。
2. 阅读本repo相应确切ISA_Def、Ampere/Ada opcode归类、trace parser、sim config/trace config以及被冻结的外部GPGPU-Sim performance core来源身份。能静态审的查到哪一步就记录哪一步；external checkout在Github不存在且本Goal禁止本机扫描时状态是`EXTERNAL_SOURCE_NOT_INSPECTED`，不凭路径命名猜支持。若发现只有内存翻译qualification而无TensorCore/L2/DRAM kernel fidelity，按每轴`UNVERIFIED`。
3. 至多提出两项最值得首先验证的**独立资源轴**（计算/TC/FMA/issue vs L2/DRAM service等，仅作为候选，不预设一定支持）。对每轴列实际变量及代码路径、资源控制的有效含义、是否改变同时其它硬件参数、统计分母、校准现状、典型假响应及最小native matched control；明确SIM-only理想oracle不可直接报告芯片收益。
4. 设计一个未来只有**一个**输入family的条件性最小资源轴测试表：`baseline、A×0.5、A×2、B×0.5、B×2、(A×2,B×2)`，最多6点，仅在两个轴**可独立且模型正确**时有效；缺任一轴就收缩甚至0点。报告是否有已验证native-sim同family/ISA/软件，什么时候SASS trace可以复用、什么时候必须重新获取，不能将变GPU架构/Math kernel仍跑原trace称硬件正确。
5. 不能用Q05固定周期的理想翻译加速来校准Qwen的TensorCore/DRAM性能，也不能以`RTX4080_V1_BASELINE_PROMOTED_WITH_SCOPE`等字样覆盖known limitations；已确认旧SM100缺资格，禁止换到B200话题。
6. 至少给一个**明确失败路径**：模拟器对照与native方向/分母不一致、资源轴更改影响多个单元、trace无Qwen输入identity、existing source不完整、数值或terminal不闭合，则`MODEL_AUTHORITY_NO_GO`，保存可接受的SIM-only局部事实，不编造运行数据。未来如需修改模拟器ISA/时序模型等属于新研究与预算，不能在本CPU Goal先动代码。

**交付四文件**：`REPORT.md`、`SIMULATOR_RESOURCE_AXES.tsv`、`PAIRING_AND_PILOT.json`（有效性/极简矩阵/0点STOP）、`RECEIPT.json`。可以没有可用两轴，不为0硬补一个不合法的L2队列参数。

## 4. 收口与综合决策

两Lane各自提交独立分支上**仅自己的4文件**，本机commit/push/fetch-back验证最终SHA/tree/四blob、worktree clean，然后STOP；失效如实保留negative和source gap，不申请另一个工程小Goal。输出终态可为`SOURCE_PAIR_CANDIDATE_READY_FOR_CROSS_REVIEW`、`NATIVE_ONLY_ELIGIBILITY`、`SIM_ONLY_UNCALIBRATED`、`NATIVE_INPUT_OR_BACKEND_NO_GO`、`MODEL_AUTHORITY_NO_GO`、`SOURCE_INCOMPLETE`、`RESOURCE_DEFERRED`。不得声称`HARDWARE_HEADROOM_PROVEN`或`A77_NATIVE_DONE`。

ChatGPT独立审查两份后，优先决定：1）是否有单一共同对象配对、能否在accepted平台上做轻量6点；2）如不配对，是否先做一次小native family characterization更有价值；3）是否因不可解释软件权重/自然覆盖而停止该候选。任何GPU/模拟器、后端实现和输入变更，必须经**新的明确用户授权及预算**；本Goal只批准CPU文本阅读。**不自动创建下一执行Goal并运行**。

用户此前强调Codex效率：普通工程问题已授权一次性解决，无须每次汇报，但科学目标／模型/数据/数值/资源预算边界改变必须STOP；每条Lane完成即用户回执，协调者进行独立科学评估。