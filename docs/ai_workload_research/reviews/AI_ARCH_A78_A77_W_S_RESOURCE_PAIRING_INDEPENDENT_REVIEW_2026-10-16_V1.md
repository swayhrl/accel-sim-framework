# Round A78｜A77 W77/S77资源资格交叉审查：原生锚点存在，Native↔Simulator配对不成立

**日期：2026-10-16；审查者：ChatGPT／AI-ARCH科研协调。**

**终态：`A77_PAIRING_NOT_ESTABLISHED / SOURCE_REVIEW_ACCEPTED / STOP`。**
分别接受W77的`NATIVE_ONLY_ELIGIBILITY`和S77的`MODEL_AUTHORITY_NO_GO`。W77有两个真实Qwen2.5-3B-Instruct BF16**历史原生请求计时锚点**，但0个已获资源轴扫描资格；S77有2个待验证源码候选控制轴，**0个准入资源轴和0个合法pilot点**。不能将二者合并为任何Qwen硬件资源饱和曲线。两个结果不是GPU体系结构瓶颈被测负，也没有本轮任何Native/Simulator执行。

## 0. Git身份独立核验与边界

固定A77共同Goal：`9902ead45ed61d54bd5eb0e2a998e2ccc4ba3285`，科研协调起点`48921695a53b5d5db84f5ef43914d343385aad19`。

| Lane | final commit | Git tree | 各自输出文件 |
|---|---|---|---|
| S77／174-new | `c837d5d85a78c70cb1a0deb28cb8279940510785` | `423c73f8f0545ccc78fba73e46d6980ce9025df5` | [REPORT](https://github.com/swayhrl/accel-sim-framework/blob/c837d5d85a78c70cb1a0deb28cb8279940510785/docs/ai_workload_research/discovery/A77_S_SIM_RESOURCE_AUTHORITY/REPORT.md)、SIMULATOR_RESOURCE_AXES.tsv、PAIRING_AND_PILOT.json、RECEIPT.json |
| W77／109 | `4fa849b16ff7828959486ccafe404c86a9115918` | `e24eb81a96c4475ee1ef43824b71e35e35fbc4c3` | [REPORT](https://github.com/swayhrl/accel-sim-framework/blob/4fa849b16ff7828959486ccafe404c86a9115918/docs/ai_workload_research/discovery/A77_W_NATIVE_WORKLOAD_AUTHORITY/REPORT.md)、NATIVE_WORKLOAD_AUTHORITY.tsv、BASELINE_CARDS.json、RECEIPT.json |

本审查独立从GitHub读取两条commit/tree/parent，确认每条从共同Goal仅新增1个commit和本Lane的4个文件、各final与其执行分支远端HEAD完全一致；本轮解析W TSV及S TSV：W证据字段与ID唯一、S两行18列且无结构异常；两个原机读JSON已读。两Lane自身的本地worktree clean和全部私有HTTP文件SHA256由其原RECEIPT承担，本审查未通过SSH重新检查109/174进程、文件与资源或重算其所有私有下载物。没有继承它们的节点执行权限。

## 1. W77科学裁决：自然文本和原生wall确实存在，但不等于资源扫描就绪

**模型与input:** 不是Qwen3，也不是S77的0.5B模型。W固定`Qwen/Qwen2.5-3B-Instruct@aa8e72537993ba99e69dfaafa59ed015b17504d1`、BF16 TP1，历史资产manifest含两片权重及tokenizer/chat-template的checksum；W77仅核Git已发布元数据，未访问当前模型盘。输入是WikiText-103 raw train事先冻结的128行、41,457B自然文本，取2044字节构成512-token chat prompt；`TRAIN_A_DISCOVERY_00`的源SHA256为`423f9086b24eff32fdd8f34630f841fa10ed34e34a33e1e18db02b97a3cdb60f`，token IDs哈希另有独立收据。它是自然语料派生的固定请求，**不等于自然用户会话/模型在真实业务中自由输出的质量样本**。历史freeze没有明确的输入许可grant/hash，W77为`NOT_DISCLOSED`，新执行应先核来源许可；不能把有Git源就自动升级完整输入/权重资格。

**原生计时锚点:**

| 点 | 历史正式计时 | 合法解释 |
|---|---|---|
| MP01 Graph ON/OFF | 40.23619079589844／39.90697479248047 ms；B1、512 prompt、1 output、每模式3 formal | eager/初轮Graph差异下的单请求CUDA-event，非剥离采样的纯Prefill；Graph OFF局部composition不能外推Compiled全请求 |
| MP02 Compiled Graph ON/OFF | 354.59820556640625／361.45654296875 ms；B1、512 prompt、32 output、每模式5 formal | 同一已冻结compiled强路径请求，32-token输出及reference正确性有范围通过；B相对A增加1.9341%时间、ON相对OFF减少1.8974169% |
| MP05 AWQ量化对照 | 167.931198／275.276398 ms ON/OFF，B1、512+32 | 不同表示/权重/软件路径的控制，不是与BF16只差一个dtype的单变量对照，不提升为第三个resource基准 |

本审查独立读取[MP02原始独立正式样本表](https://github.com/swayhrl/accel-sim-framework/blob/ccd6928bfb420d1e4c554ec0e377bb8fbe377501/docs/vm_tlb/review_packs/C16_STAGEA_TERMINAL_INDEPENDENT_CONSUMER_174NEW_V1/DQ2_INDEPENDENT_RECALCULATION.tsv)和[CUDA event计时门](https://github.com/swayhrl/accel-sim-framework/blob/a12bbfa4609ece57fadde107f9fd2e3bc0380cdf/docs/vm_tlb/review_packs/C16_DQ2_NATIVE_RECOVERY_109_V1/TIMING_AUTHORITY.json)。完整wall是pre-sync→CUDA event包围单次llm.generate→post-sync，排除初始load/compile/warmup/tokenize与host排队。MP01与MP02的Graph/compile+生成长度不同；它们**不是B或上下文伸缩曲线**，不能用请求时长除以32构造“纯Decode ITL”。

**已知family观察：** [MP01 Graph-OFF局部union](https://github.com/swayhrl/accel-sim-framework/blob/9d82ff41132e7b1a1fdd18a287c13627fe62e5b7/docs/vm_tlb/review_packs/C16_STAGEA_DENSE_FIRST_TIER0_INDEPENDENT_CONSUMER_174NEW_V1/DQ1_HEADROOM_DECISION.tsv)的gate/up=51.8157%、down=25.4153%、attention=16.6441%、activation=2.0929%，分母38.108350ms CUDA-parent；不是compiled Graph-ON parent或无重叠整请求比例。compiled路径模块hooks 0/4608、96个不同runtime kernel名仅1个直接唯一语义映射；B4 Mode B formal=0，四DQ仍`QUESTION_INCOMPLETE`。不重复开启Observer V3、cache identity修补、Stage A Tier1/B4，也不将W4强GROUP_M16或双流负例改写。

**W结论：** `NATIVE_ONLY_ELIGIBILITY`只能解释“存在能比较完整CUDA-event时间的同一冻结B1请求”，不意味着已有资源调参、trace或全模型硬件瓶颈。当前asset/VRAM/runtime/独占GPU锁是`NOT_INSPECTED`。两历史卡的`resource_scan_ready=false`是合理的。

## 2. S77科学裁决：既有AWMA翻译资格保留，计算/L2/DRAM不闭合

**受限平台：** [AWMA known limitations](https://github.com/swayhrl/accel-sim-framework/blob/29ce051f982f3854bd4392a94e4195c59340123b/docs/vm_tlb/review_packs/AWMA_RTX4080_V1_BASELINE_PROMOTION_V1/KNOWN_LIMITATIONS.md)明确`QUALIFIED_FOR_AWMA_MEMORY_TRANSLATION_STUDIES`和`BASE_CONCURRENCY_MODEL_RESIDUAL`。S正确区分初次heldout与后续requalification；12点终态身份/CTA/UID/翻译quiescence PASS不等于BF16 TensorCore/L2/DRAM数值与性能都已校准。

本审查从原[Native↔Simulator分析](https://github.com/swayhrl/accel-sim-framework/blob/29ce051f982f3854bd4392a94e4195c59340123b/docs/vm_tlb/review_packs/AWMA_NATIVE_SIMULATOR_CROSS_CALIBRATION_V1/CROSS_CALIBRATION_ANALYSIS.md)再次核：Native M1→M2为−4.5840%，Sim同方向条件+86.5202%，不只幅度不符而是符号相反；M0→M1模拟8.347872×方向支持部分working-set作用。不能调换模型后硬拿比例拟合当前Qwen服务。

**外部性能核来源：** AWMA已发布config SHA `de9ee8f30325c033e0de624640ffa8803f0eae40633eebaa0b3144f549f5ccb8`、trace config SHA `a46fe47a14f3ca4116a35c5bf1dc156f4e861484b91278e8b3f6e09519bd7e5b`以及执行binary SHA `a866c219b7d71a3075e032c9179bcd679074d6f2e9f1750b435170aabb413b24`是已发表身份；但当前无法绑定到完全公开、同SHA的外部GPGPU-Sim性能核源和补丁。因此`EXTERNAL_SOURCE_NOT_INSPECTED`合适；“框架有Ada OP映射”并非已校准性能模型。

**待审轴A（TC）：** `trace_opcode_latency_initiation_spec_op_3`调整HMMA specialized initiation service，源码提案32→64（0.5×）或32→16（2×），不是任意“增加TensorCore数量”真实轴。未核实际frozen core的发射/寄存器/scoreboard/wb和native matched pressure，`UNVERIFIED`而非已获准。

**待审轴B（L2）：** `-gpgpu_cache:dl2` data port width 32→16/64B；同时影响hit、fill与writeback，不能称纯L2 hit bandwidth。最重要的是本审独立回读固定公开scaffold [gpu-cache.cc@dc56ca74](https://github.com/dzwduan/gpgpu-sim_distribution/blob/dc56ca74fa51d333cacb6a8aac91bce804301ae1/src/gpgpu-sim/gpu-cache.cc)：hit使用`data_size/port_width + (data_size%port_width>0)`向上取整，而fill `get_atom_sz()/m_data_port_width`与writeback `modified_size/port_width`可向下取整。若atom为32B，将宽度从32→64B，32/64整数=0周期，32B hit仍为1；该`B×2`不是保真2倍带宽服务。这是**公开参考实现的代码事实**，不是AWMA实际binary已被证明存在这个缺陷（外部core未审）。不能偷偷修这个内核、改资源参数后用其输出声称真实性能。

**两轴合格数量均0**；条件6点模板中的基准点R0也未执行。S的pilot JSON正确列`admitted_axes=[]`、`admitted_points=[]`；本轮没有任何性能扫描结果。

## 3. 最关键的跨Lane硬不匹配：T1不是W的MP02模型

- **W77 Native**：`Qwen/Qwen2.5-3B-Instruct@aa8e725...`，真实WikiText自然文本、B1 512+32，完整compiled强路径请求事件wall。
- **S77 Simulator候选T1**：历史`Qwen2.5-0.5B-Instruct` s2-text prefill的一个`PREFILL_GEMM_PRIMARY_OCC0`单kernel trace，producer`8f49ba3b9228b5f8a9163e961225ffd415107734`，独立trace SHA`e36178f9a92033cd91f3c1ff4b165321b7958157c7deed2a9aaa4696e7c73e8c`。S没有读取raw trace、完整token身份/权重/数值/强kernel backend与Native对应关系。
- **不可拼接**：模型scale和可能的软件kernel、运行范围与时间分母都不同；Qwen2.5-0.5B单kernel模拟周期不允许乘或除一个因子拟合3B compiled完整请求毫秒。S77有范围的trace admission不构成3B的同ISA/同kernel/同输入/相同计算时序的trace。因此`PAIRING_NOT_ESTABLISHED`不仅是外部core未闭合，而是同一科学对象根本不相同。

W优先使用MP02 B1历史锚点，S选择T1可供未来独立family诊断，但二者这轮不能互为真值。

## 4. 综合裁决：关闭本条配对路线，而不关闭主流大模型的Native-only探索

**当前不可批准**：A77 6点模拟资源扫描、TC/DRAM/L2模拟器参数变化、AWMA R23G/Stage A恢复、C16原B4、SM100重建或新硬件机制。没有可靠资源轴、相同程序trace和校准链，任何正速度曲线都将难以解释。

**真正值得考虑的下一步是一次单独的新Native-only现象发现合同（`PROPOSAL_ONLY`；**本轮未创建/派发GPU Goal**）：**

1. **目标：** 已有合法自然文本和权重身份的Qwen2.5-3B-Instruct，强BF16 vLLM compiled Mode A（与MP02相容，但不得直接将历史资产存在性视现场可运行），109 RTX4080。
2. **首先确定输入与数值：** 独立资格检查WikiText固定源文本和输入分发许可；不解封旧holdout作探索，冻结A00/A01各自SHA及真实token序列，要求相同模型和tokenizer/模板、合法完整输出、不同seed/形状/精度不偷偷变。旧MP02 A/B历史输出是有范围参考，而不是新自然任务输出必然一致。
3. **最小对照应回答一个新的问题：** 强compiled路径在**固定B1/同真实文本**时完整请求wall是否重复合格，接着**仅在前一步PASS后**用源文本中原始连续前缀构造两个自然且不同的长度（例如512和2048 tokens，非人工复制/填充）以及输出1/32这两个明确执行范围。该工作量变化只是`NATIVE_WORKLOAD_SENSITIVITY`，**不是物理资源轴变化，也不等于真正GPU饱和曲线**。数值/质量和重复性、CUDA event与host wall分母各自固定；任何样本变化和编译/Graph path改变需独立资格，不能未经对照将不同输入长度叫同语义同工作量。
4. **强软件及已知失败绕开方式不可使用**：默认只用已经合法的Mode A，不重开Mode B缺失、B4旧identity、Python hook观测和W4 merged数值STOP。未来若允许硬件Profiler，必须独立审批，有侵入观测与未插桩wall分离；先用自然规模变化、已有kernel事件分解来判断是否有值得进一步采样的资源现象，不对compiled name硬贴family归因。
5. **停止条件：** 当前权重/数据或Runtime不合格、目标输出质量/数值未闭合、GPU lock冲突、资源峰值/时长不足、自然长度不满足输入要求、时间变化只是执行工作量与冷启动、无法区分执行限制，均STOP/DEFER。不得因`native-only`名义自动获得109 GPU、下载、安装或后续模拟器资格。

此途径科学价值是用很小的新测量建立主流模型的阶段/规模响应和软件反证，而不是复制C16 Stage A四个旧DQ。用户批准预算前不做GPU工作。若上面的最小Native-only入口依然无法带来不同资源状态，需更换科学工作负载阶段或平台，并承认“现有模拟器资源上限路线不就绪”；不能再次拆一个同源CPU-only读取原有C16收据的Goal。

## 5. 溯源、资源与终态

- S77原始`MODEL_AUTHORITY_NO_GO`、W77原始`NATIVE_ONLY_ELIGIBILITY`均原样保留；各自记录的CPU-only、无native/sim/GPU/model/dataset/download和单次Git fetch-back依原RECEIPT接受为执行者陈述，本审查只读。
- Git总协调源：[A77设计](../plans/AI_ARCH_A77_MAINSTREAM_GPU_RESOURCE_SATURATION_CHARACTERIZATION_DESIGN_2026-10-16_V1.md)、[A77 CPU Goal](../goals/AI_ARCH_A77_RESOURCE_CHARACTERIZATION_PARALLEL_CPU_ADMISSION_GOAL_PACK_2026-10-16_V1.md)。A70/73/74/75原所有source-only STOP/质检不变。
- 本次只在`hrl/ai-workload-research-coordination`发布本审查和CURRENT_STATE导航，**不merge两执行HEAD，不改它们原始REPORT、TSV、JSON或旧项目科学结果**。109、174-new和164不收到新任务、锁不触及。
- 终态`A77_PAIRING_NOT_ESTABLISHED`；资源扫描ready数0；有两个历史native anchor；无原生/模拟器新执行。下一阶段最多一次有预算的Native-only科学现象诊断待单独批准，不自动进行GPU。
