# AI-ARCH｜Q1 3DGS晚期训练关键路径：一次性真实实验Goal V1

状态：**CONTRACT_READY_PENDING_EXPLICIT_RESOURCE_APPROVAL**。此文件是未来一次性派发合同；当前只批准定稿与协调更新，**不执行GPU、不取锁**。用户批准本文资源申请并确认设备/CPU窗口后，执行者可在一个Goal内连续完成全部合法分支，无需逐阶段再确认，也不得自动建立第二个恢复Goal。

执行者：现有109-AI-ARCH长期Codex窗口；单GPU owner/dispatcher，轻量CPU分析可串行或资源内并行。Framework：swayhrl/accel-sim-framework。建议未来执行分支 hrl/aiarch-q1-3dgs-late-pipeline-native-109-v1；全部新代码、缓存、checkpoint、日志、raw与收据隔离。V1–V11、GS A26GR1及其它旧任务只读。

## 0. Authority及科学变化登记

- 组合决策：f88e40123f4060328aa50a16d22fa328cee51cfe / tree03274c2ddb7c45aff4bd7ad1f7d48fca94e4a48f。
- GS原生执行：cf80f6ec07a31eccdaff264c3bce64e0511179f8 / treec66008a9da553d06a00195c8c133c3e7ec16692d。
- 作者source：6471e958f7e318f4870234d8107e0aa91c2d6932 / treebc99b237b3e050ddd46392acfe7adb8dd822b2a9，具体运行文件以A26GR1 SOURCE_PROVENANCE/RUN_IDENTITY的固定SHA为准，不将注册但当前不可读的blob声称已复核。
- A44线程归因、A28 source审计、A46独审位于旧协调ed365741b230718f6ffc1ccbed125fc2566aac15；A45H1936dffd204043a1ab6c0fad5e7aebf565497c1a仅CPU组件。
- 本轮协调更新：66b2dffc6141edf1c9f9f089091b3922556583f1 / treec9491cbc37d41c2155218763bf215615ef72b39b。
- Image-Lab共享协议以Qwen V11已接受的线上实例/门控/预约/共同flock规则为来源；PID不是固定白名单，执行当时重新只读验收实际实例。不得部署、重启或重复其基础设施canary。

与上一组合合同不同：**没有完整late state不再直接终止整个Q1，而是在本Goal获准资源内从真实合法初始状态连续推进并建立完整state。** 同时预算包含该生产阶段，不能沿用30分钟GPU草案。旧GS结果、原数值/质量界限和STOP均不改写。

首次只读fetch实际协调HEAD和本文发布固定commit；核差异，独立worktree，不强行reset或merge历史执行HEAD。报告science-field/source/input/resource合同SHA；工程修复另列，执行前冻结。

## 1. 唯一问题、竞争假设与结论层级

真实Rubble晚期训练的暴露等待，来自CPU状态生产、线程/流水软件策略，还是兼容强软件之后仍有GPU/CPU–GPU物理资源限制？

H_CPU：scan、实际CPUAdam、参数转发生产端滞后占主导，线程/放置/兼容流水能消除应用残余。
H_GPU_LINK：生产就绪之后，实际GPU服务或传输/同步仍形成可测关键路径。
H_OBSERVER：跨线程区间、错方向copy、不同轨迹/窗口或observer扰动造成表面等待。
H_OTHER：调度、分配、加载或不匹配数学语义仍混杂。

A44主线程候选并集14.084/14.746ms不是纯GPU空闲，也不是收益上界；旧30.871/32.128ms不可复用。仅observed时延/相关counter最多OBSERVED/MODEL_CONSISTENT/PARTIALLY_ATTRIBUTED，缺独立物理资源轴不得升级CAUSALLY_SUPPORTED。线程策略是软件控制，不能单独证明DRAM或SM饱和。

## 2. 同一Goal的执行路径

CPU身份/安全/状态实现资格 → 一次获准窗口的非阻塞GPU准入 → 完整state复用或自然连续推进 → 完整保存/恢复验收 → 发现窗口软件基线 → 有界诊断/软件反事实 → 冻结策略的独立验证 → 分析、drain、清理、Git归档。

普通路径、Python/C++包装、日志、监控生命周期、确定性state序列化和observer问题在预算内solve-and-continue；不因一个可选counter、线程档或局部观测不可用终止其它合法研究。真实身份不明、资源/共享安全失败、不可恢复运行错误或数学语义变化仍STOP。不要按“状态修复/线程/Profiler准备”拆新Goal。

### 2.1 CPU-only前置资格（本未来Goal内部）

只读复用A26GR1合法本地Rubble、作者source、4×预处理与既有隔离环境身份。检查manifest及文件stat/必要变动SHA；没有变化不重hash全部9.77GB归档、不重建旧审计、不重复论文。数据/依赖下载、安装升级均为0。科学实体缺失则记录确切缺口，不造数据、不新下载。

冻结原Rubble算法、输入/相机/seed、densification、CPUAdam、LR、SH、deferred/pipeline语义，nominal max_steps=200000与steps_scaler=1不改；本研究只外部结束于晚期窗口，不冒称完成200k。refine_start500、refine_stop15000、reset3000、refine_every100等以原配置完整字段为准，不提前停增密。

检查本人允许的cpuset、P/E/SMT、NUMA、OMP及Torch实际线程状态；本次规划SSH helper看到24 logical CPUs只是历史瞬时可用范围，不是未来CPU预约。资源所有者先分配CPU集合，全部worker/loader/子线程继承，不使用taskset/NUMA策略干预他人。不以64请求当64物理核。

在私有source副本实现完整state与监控、最小计时和可选observer，不修改生产GS/vLLM/Image-Lab或旧环境。工程补丁不可改变计算、精度、Adam/增密、相机和调度；线程策略改变只作为明确受控变量。CPU单测覆盖state schema/alias/RNG/cursor/deferred队列、原子落盘、坏hash、退出竞态/AccessDenied/PID复用、资源超限及错误清理。未知异常不能宽泛忽略。


所有复用监督器必须重新绑定本Goal实际启动时刻、输出/private/cache/日志/预约路径与新资源字段，不能照搬V1–V11的硬编码START/OUT或Qwen预算。记录执行源码SHA与配置SHA，CPU预检验证绑定后才可尝试GPU锁。

## 3. 完整真实state：先检查，缺少则连续生产

### 3.1 已有state分支

只检查A26GR1登记路径和明确授权的私有完整state，避免全盘扫描。合法来源、完整内容、source/config/input SHA和恢复位置均符合本文才能复用。旧splat-only、只有模型参数、无moments/队列/随机状态的文件不合格；不从文件名推断late恢复资格。

### 3.2 无完整state分支

从同一合法真实SfM/相机初始状态，按原GS-Scale训练连续推进。初期真实数值/保存canary属于这条真实路径，不另造合成训练；通过后继续，不回来请求新Goal。遇工程包装问题优先恢复本轮已验收checkpoint，不无理由重跑昂贵前缀。

建立可轮转的本轮私有恢复点。频度根据实测写入时间与推进速率选择，目标丢失工作不超过约15分钟、避免checkpoint主导生产；此为工程目标不是每15分钟硬STOP。写入本身、停顿和初始化均计入资源预算。接近硬上限时优先安全保存/清理，不再开启新测量。保留原调度，不以max_steps=15200改变LR等。

目标状态用明确的next_step语义登记：
- C_D：next_step=15140；发现预备步骤[15140,15150)，正式自然camera窗口[15150,15200)。
- C_V：从规范T16自然轨迹连续推进取得next_step=15240；验证预备[15240,15250)，验证窗口[15250,15300)。
实际原源码step计数若不同，以CPU资格中证明的映射换算，半开区间与相机序列SHA在对照前冻结，不悄悄偏移。若合法已有state晚于这些位置，则用同样结构：首个可恢复的post-refine自然窗口为发现，后面不重叠且未看结果的窗口为验证；起止、预备长度和SHA在看性能前固定，无需另开Goal。

C_V来自规范基准轨迹，不能取性能最好的分支状态。发现/验证使用不同自然camera序列，但不强制每个camera唯一，不把相机不重复等同Gaussian无复用。没有合法第二scene不补造跨场景结论。

### 3.3 完整内容与暂停边界

至少保存参数/全部训练buffer、精度/shape/stride、稳定Gaussian身份及membership、optimizer各param-group/moments/counters、deferred与pending梯度/更新/转发、已完成但未消费的工作结果、RNG（Python/NumPy/Torch CPU/CUDA等实际使用者）、sampler/loader/camera cursor与prefetch队列、SH/LR/增密reset等schedule、线程/stream拥有关系与source/input/runtime身份。不能只保存torch模型state_dict。

在原算法合法safe point暂停新提交、等待**已提交**CPU/CUDA工作达到可序列化frontier；禁止为了“清空pending”额外做原调度没有的optimizer更新。记录completed/submitted/applied/published frontiers，已完成未消费的结果仍按原算法之后消费。恢复时重新建立stream/event/worker和别名，不把设备pointer当跨进程身份。不得丢梯度、重复apply或重走camera。

完整状态落盘和恢复标准见 [STATE_AND_RESTORE_QUALIFICATION.md](../planning/Q1_3DGS_LATE_PIPELINE_SINGLE_GOAL_109_V1/STATE_AND_RESTORE_QUALIFICATION.md)。streaming/chunked CPU序列化，临时buffer≤256MiB为目标，禁止为了checkpoint全量clone第二份主存state。文件、manifest和SHA写完后fsync/原子发布；提交Git只放精确私有index，不提交Rubble或大型checkpoint。

### 3.4 恢复科学资格和数值范围

GPU实际恢复后、任何新forward前，schema、dtype、tensor值、计数/队列、RNG/camera位置、alias与update frontier必须精确一致。不能复现的state字段是缺口，不伪称PASS。

执行固定短自然continuation：规范不断流参考与恢复路径，同一策略两次恢复A/A，保留首个偏差、loss/params/moments/indices与全部身份。不同训练轨迹已有不逐bit复现历史，因此不临时发明1e-5或借Qwen logprob容差：
- roundtrip/restored起始state的精确身份是硬资格；
- 连续数值若有已接受适用容差，沿用且不放宽；
- 没有适用容差或出现小数值差异，数值等价记NOT_ESTABLISHED，报告分布与首差；只要输入/算法/状态映射有效、值有限、实际完成工作可核，可继续固定自然窗口的**描述性**时延，不能标NUMERIC_PASS或严格同轨迹加速。
- 缺counter/队列、重复或漏apply、错camera、恢复起点不符等观察/恢复实现错误，必须修复后重验；不可修复则STOP_STATE_AUTHORITY。
若N/visible/updated集合或质量不同，降为MATCHED_START_DESCRIPTIVE；没有独立完整收敛对照不声称time-to-quality。

## 4. 完整工作计时与最终drain

在GPU前写MEASUREMENT_BOUNDARY.json，依据原pipeline源码定义window每个camera工作产生的梯度/更新credit、submit/apply/publish frontier及合法收口：
1. 有原实现合法flush/drain接口时按原语义调用，计其完整wall，不能增加数学更新。
2. 没有接口时，按原算法自然后续camera运行到目标窗口全部credit已apply/publish。所需pipeline lag L从实际源码与初期canary确定；所有策略采用相同自然closure前缀，完整追加时间和额外工作都计入并披露，不减去来“校正”。
3. 最终仍属于未来camera的pending状态完整保存/记录，不能说队列全空；目标窗口credit必须闭合。不支持合法闭合时不发布“完整更新时间加速”，只保留body描述与状态缺口。

正式主指标：相同恢复起点、预备过程、自然50-camera窗口及共同closure的host monotonic wall；另报body、closure、完成的camera/梯度/update数量。checkpoint载入/实验准备不混进本来的训练窗口，但分别报告其时间和未来checkpoint开销；不得把正常更新或同步挪到计时外。GPU event/device服务是单独时间域。未校准host/device关联前不相减。

observer OFF不装逐op hook、每步GPU同步、tensor dump或Profiler。用最小外层计时及既有必要计数；资源监督器配置各策略一致。observer ON独立诊断并明确扰动，不把其耗时混进正式pool，不用不同camera半窗相减估observer overhead。

## 5. 软件基线与最小研究矩阵

主基准仍是GS-Scale CPUAdam完整pipeline。T8/T16表示OMP cap受控变量，记录作者64 request、实际OMP、Torch intra/inter-op终态与CPU占用；不把OMP cap当整个进程线程数。原source如重设Torch64须披露，不能暗中让某一臂不同。允许一个资源内、事前冻结的joint Torch/OMP或P/E placement策略J作为独立变量；不强制T64或无界扫线程。

各策略从同一C_D独立恢复，原自然10-step预备后测相同窗口+closure。先每策略2轮warmup，再5轮formal，预冻结交错区组顺序；restore和compile/warmup费用单列但计预算。样本是完整恢复区组，不把50相邻step当50个独立重复。保留全部formal、中位数/MAD、区组配对和drift。

最低矩阵：
- T8/T16，若实际CPU资源容许；每格2 warmup+5 formal。
- 一个有明确问题的J策略：仅当实际线程/placement证据有信息量，执行前登记变量/预测/反证，使用相同重复。
- 规范T16与发现阶段较强策略各一组配对observer OFF/ON诊断；与formal分池。
- 冻结较强策略与T16用于C_V自然保留窗口，同样2+5；若较强就是T16，保留T16独立窗口即可，不人为重复同配置。
- 只在真实噪声/漂移或具体软件假说需要时增加**对称**交错区组或一个兼容软件反事实，预算内预写分析，不按速度筛样本。

允许的最小软件反事实：私有副本内线程/调度、可证明同值且不改更新顺序的状态复用或冗余传输消除。先写输入/alias/lifetime/同步正确性与反证，再做局部/整段比较；无法证明则不删除copy。原基准不被覆盖，不修改生产库。不通过换精度、换optimizer、关闭增密/SH、重排自然camera、缩小Rubble或换小N强行得益。

## 6. 诊断、软件排除和物理归因

observer ON记录N_total、自然N_visible、实际N_updated及U/N；这些名称必须映射到真实culling/optimizer集合，不拿tile计数或gathered行数冒充更新数。记录稳定ID与每个集合关系，无法建立ID时明确边界。不要为了统计在OFF每步全N扫描。

对scan/CPUAdam/参数转发记录真实线程/源行/访问行数及工作量；H2D/D2H记录实际src/dst、dtype、numel、unique storage、方向、有效payload与enqueue/service区别。SHdegree0仍可能有调用，不能用调用数推字节。GPU服务、Host sync/join以及关键线程区间求并集，并保留组内累计以展示重叠。不能将worker同步与CPUAdam重叠时间相加。

必要时用一段有界时间线、已有合法API或少量counter辅助；只在原生正式测量完成/分离后启用，所有工具开销计预算，不改驱动、系统Profiler权限、时钟或功率。若已安装工具不可安全用，跳过，不为此部署大环境或终止其它结果。一次同真实输入的服务replay仅作局部诊断，不等于完整训练；clock关联不足不计算纯GPU空闲。

CLM已有camera/visibility reuse、选择性appearance搬运、optimizer overlap/调度；TideGS已有跨层working set和异步，但其cold restart/顺序改变是不同语义；GS-Scale自身deferred/forwarding已是软件基线。只引用已接受排除，不再广泛文献。凡线程、兼容调度/复用/传输已解决的问题记SOFTWARE_ABSORBED，不升级硬件。

若剩余成本具体可测，才记录哪个物理资源、独立变量、预期响应/反证、完整应用上界及面积/功耗/时序/复杂度。无独立物理轴可写后续审批问题卡，不自动改GPU全局设置或启动机制/模拟器。零残余也是有效结果。

## 7. 待明确批准的整包资源与安全边界

**以下全部为新申请，不继承历史权限。** 详细测算见[RESOURCE_REQUEST.md](../planning/Q1_3DGS_LATE_PIPELINE_SINGLE_GOAL_109_V1/RESOURCE_REQUEST.md)/json；没有批准与合法当前窗口不得启动本Goal的GPU部分。

- 节点仅109 RTX4080、GPU UUID GPU-ce6cba36-415b-4e27-40e2-bded6bc1ee59；一个GPU owner、各worker/工具严格串行。
- 整Goal硬上限8小时；累计GPU持锁硬上限10800秒（3小时）。预计保守分配：连续生产75min、state/恢复30min、矩阵/诊断35min、工程与噪声余量25min、最终安全收口15min；这些是合计估算而非每阶段独立硬门。完成即结束，不跑满额度。
- own GPU NVML≤14336MiB。Image-Lab受控resident加已认证桌面合计≤512MiB，真实活动/门控满足已接受协议；不能仅凭空队列或显存少准入。
- 自身进程树sampled RSS≤40GiB，charged-memory保守上界≤48GiB；优先owner提供私有delegated cgroup。无私有group时，只有能证明包含全部自身进程、无漏子cgroup的共享祖先memory.current作为**含他人开销的保守上界**才可用，超限只停自身；不以shared差分冒充own峰值。无法取得可信上界即RESOURCE_DEFERRED。
- 不依赖swap扩容。准入要求MemAvailable≥50GiB；运行MemAvailable低于10GiB或自身VmSwap较准入增长超过64MiB按安全规则停止自身新工作并收口，不能逼迫其它任务让路。
- 私有新增磁盘总额≤64GiB；持续保留文件系统available≥32GiB。最大两个完整state存储槽加≤8GiB代码/cache/raw/log，执行内测S要求2S+8GiB≤64GiB。只轮转本Goal自己已登记且不再需要的临时恢复文件；旧资产不清理。预准入free≥96GiB，不能以当前瞬时138.9GiB空闲视为预约。
- CPU由owner明确分配至多16 logical CPUs给训练进程树，另至多2 logical CPUs给轻量监督/分析；具体集合先核P/E/SMT，helper限速。T8/T16为软件策略，不宣称16物理核。无合适分配可做许可范围的CPU准备，但不挤占别的任务。
- 模型/数据下载=0、依赖安装/升级=0、164访问=0、模拟器/RTL=0。不改Image-Lab、不清旧cache、不改变全局线程/时钟/功率/权限。

安全准入使用/data/c16/locks/c16_gpu_campaign.lock的fcntl.flock(LOCK_EX|LOCK_NB)，覆盖任何CUDA/NVML准入、模型、loader/子进程、Profile、context存活和退出清理。一次连续GPU窗口只尝试一次取锁，冲突不等不重试。取锁成功后复验inode/所有权、GPU UUID、Image-Lab运行版本/加载gate/预约/quiescence、当前PID+UID+start_ticks、所有compute与桌面身份、显存和有界低活动采样。协议不符立即STOP，不干预其它进程、不为本Goal重部署canary。

全程监控锁/预约/门控、GPU进程与显存、RSS生命周期/cgroup/磁盘。NoSuchProcess仅按V7已审条件记录OWN_EXITED_CHILD_RSS_RACE并保留censored；AccessDenied、PID复用、worker死亡、外部未知GPU任务或同时监控缺口不能忽略。单个资源安全故障停止对应GPU工作，可靠保存已完成证据、清理自身进程/context/预约/锁；不开始第二轮抢锁。

硬上限前预留收口；若预测剩余预算不足下一完整区组就不启动它。CPU工程/分析可在剩余8小时内完成归档。状态不能安全保存时不伪造恢复资格，保留已完整验证的上一代和错误收据。


共享测量沿用V11已披露的桌面逐进程activity遥测缺口，标注VERIFIED_GATED_RESIDENT_SHARED_NATIVE_OBSERVATION，不伪称完全独占。这个既有范围限制不等于允许缺失门控、quiescence、GPU进程身份或共同锁；关键字段缺失仍停止。全局低利用率或低MAD不能证明无干扰。CPU侧也记录获准集合与可取得的系统级负载范围，不读取他人敏感数据。

## 8. 交付、判断与STOP

独立新目录runs/AI_ARCH_Q1_3DGS_LATE_PIPELINE_NATIVE_109_V1，至少：
FINAL_REPORT.md、SCIENCE_CONTRACT.json、SOURCE_AND_INPUT_IDENTITY.json、STATE_MANIFEST.json、RESTORE_QUALIFICATION.json、MEASUREMENT_BOUNDARY.json、POLICY_AND_CPU_TOPOLOGY.json、FORMAL_SAMPLES.tsv、OBSERVER_DIAGNOSTICS、TRANSFER_AND_CRITICAL_PATH.json、SOFTWARE_EXCLUSION.md、DISCOVERY_AND_VALIDATION.json、RESOURCE_RECEIPT.json、CLEANUP_RECEIPT.json、PRIVATE_RAW_INDEX.json、RECEIPT.json及冻结私有补丁/CPU测试。

报告严格分开state精确恢复、continuation数值、matched-start描述性/严格工作可比、observer扰动、完整应用与局部counter、发现与保留输入。没有长期收敛就不声称同质量训练加速；没有第二scene不声称跨场景；没有独立物理控制不声称memory-bound或新硬件成立。

科学终态可为SOFTWARE_ABSORBED、EXPOSED_COST_PARTIALLY_ATTRIBUTED、INCONCLUSIVE、NO_HARDWARE_CANDIDATE_PROMOTED；执行失败分别STATE_AUTHORITY_NO_GO、INPUT_OR_RUNTIME_NO_GO、GPU_RESOURCE_DEFERRED、RESOURCE_STOP。失败不覆盖其它有效样本，也不补造未运行点。即使有残余也只提交可证伪问题卡，不自动新机制。

整批完成或合法STOP后，先保存所有已完成真实输出/统计，再做资格判定；归档正负原始证据，commit/push/fetch-back验证commit/tree/全部blob，worktree clean，明确自身进程/context、预约及锁已清理。完成后STOP，不自动Q1R2、第二scene、GPU重试、硬件、Profiler扩展、模拟器或其它Goal。

[State/restore qualification](../planning/Q1_3DGS_LATE_PIPELINE_SINGLE_GOAL_109_V1/STATE_AND_RESTORE_QUALIFICATION.md) | [Controlled experiments and falsifiers](../planning/Q1_3DGS_LATE_PIPELINE_SINGLE_GOAL_109_V1/EXPERIMENT_AND_FALSIFICATION_MATRIX.md) | [Resource application](../planning/Q1_3DGS_LATE_PIPELINE_SINGLE_GOAL_109_V1/RESOURCE_REQUEST.md)
