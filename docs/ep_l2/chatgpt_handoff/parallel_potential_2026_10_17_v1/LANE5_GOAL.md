# Lane5 CONTINUE — 并行实测性能潜力、有限机制与理想上限

## 0. 执行目标与当前任务接续

先完整阅读同目录 `PARALLEL_CONTRACT.md` 和 `EXPERIMENT_MATRIX.csv`。本Goal落实用户已明确授权的并行实验：继续探索L2及其上下游结构/参数，取得完整应用的理想访存上限与有限实现结果，同时向Lane6交付论文证据。**H0收益很小不是停止其他实验类别的条件；任何类别均不以另一类别先取得正收益为启动前提。**

你继续作为唯一full-application dispatcher和独立科学接受者，沿原Lane5工作树、分支、中央registry和V2科学账本执行。不是新开第二个Lane5服务，不重启原Goal，不reset分支，不重跑已完成的SAD，也不终止或重复启动现场其他在途任务。已结束的原窗口才在原工作树开启一次CONTINUE；仍运行的窗口直接吸收本增量。

本次准备最终核到Lane5 Framework HEAD `73d3e3eedbfd92643db2f674a49e16605d3e2260`（2026-10-17 10:43:05 UTC），STATUS路径 `docs/ep_l2/codex_handoff/fast_track_2026_10_16_v1/lane5/STATUS.md`。r19首8和D4 vectorAdd/SAD四条稳健性运行均已接受：vectorAdd B45055/U45052，SAD B110550/U110528；V2 generation17，共12次启动、12次接受、无活跃sim/lease。原Goal尚未完成，正等待D2/L25 producer交付。**先核本地中央registry、PID/start_ticks/boot和最新STATUS/RECEIPT，以上只是来源快照；若已有新在途任务，保留并续接。**

已有r19已在 `docs/ep_l2/review_packs/FT20261017_LANE5_R19_INITIAL8_AND_SELECTION_r1/SELECTION_CHECKPOINT.json` 选定D2与L25，每条件Convolution/FWT各B/U配对。消费该目录的 `LANE1_FOLLOWUP_REQUEST.json`，核对Lane1新交付并逐条件独立准入；不要重新挑选、重置或重复发起这8条。D4/Q4与H0已接受原结果继续复用。

## 1. 两个campaign分别记账，资源共同调度

### 原r19：保持原有合同和身份

- `experiment_id=EPL2_DOWNSTREAM_HEADROOM_R19`。
- 原deadline为 **2026-10-17 17:09:16 UTC（北京时间10月18日01:09:16）**；原cap24、已有计数、失败和在途记录完全不变。
- 原SAD及已选D2/L25均属于r19，**不计入新50个seed cells**，但占用同一真实CPU、内存、simulator槽和磁盘预算。
- 不因新campaign把r19改名、归零、延长或重开。临近deadline不启动不能在剩余时间内完成的运行；按原终止合同保留终态。

### 新campaign：并行性能潜力实验

- `experiment_id=EPL2_PARALLEL_POTENTIAL_20261017_V1`。
- **T0在中央registry第一次登记该新campaign时一次性确定并冻结**；不是写文档、启动Codex或重读状态的时间。
- `deadline = min(T0 + 24 hours, 2026-10-18 14:00:00 UTC)`，后者为北京时间10月18日22:00。
- **最多72次新full-application启动尝试**。失败、timeout、canary、补充同源锚点和实际重试都计入；定向小fixture、配置审核、纯输入hash读取不算full application。
- 每条full application沿用 **3600秒timeout**。新deadline只限制新启动，此前已准入的任务保留原timeout完成/退尽；deadline时发布在途快照，最后一条终态后发布最终报告，不借此在deadline后补发任务。不通过裁剪trace、截断epoch或减少迭代把超时改写成完整结果。
- 50个seed cells是计划覆盖集合，不是已启动或已接受结果。完整同identity已接受锚点可以复用，不能为了凑50次启动重跑；每个逻辑cell必须记录真实新运行或准确复用来源。
- 另22次是上限内余量，不承诺用满；具体候选见总合同与下文。完整失败与负结果保留，不通过换输入或隐瞒失败补齐正结果。

在现有registry的同一锁下新增明确的campaign/condition白名单、T0、deadline和尝试预算。已有源码 `util/ep_l2/ft_lane5/registry.py` 的 `claim()` 曾只接受r19及Q4/D4/D2/D8/L25；必须正向支持新条件，**不能冒用r19、跳过白名单、复制shadow registry或另建科学账本**。既有r19在途client和lease继续合法更新；不得因新工具hash发布使已运行进程失去写终态的资格。必要时保留旧client用于旧任务退尽、新client用于新准入，二者共用原锁和权威数据，原源及hash绑定保留。

预算核验与实际启动必须在串行准入中完成，防止两个dispatcher路径同时越额。仅生成spec/排队计划不算启动；一旦进入实际启动尝试即登记且失败也计数。失败重试须使用既有可审计恢复方式，保留旧attempt、计入新attempt，不能换无关identity字段规避去重。已存在CURRENT_ACCEPTED或RUNNING的完整run-key绝不重复执行。

## 2. 50个seed cells与立即并行顺序

`EXPERIMENT_MATRIX.csv`含50个计划cell，全部初始状态为 `PLANNED_AWAITING_QUALIFICATION`。用户已授权执行方向，待producer模式资格、精确配置和现场资源准入后即可运行，不逐点再请示。

1. **理想上限24 cells。** Convolution/FWT/vectorAdd/SAD各B16_OFF、I_WB、I_META、I_READ_HIT、I_MEM_ALL_DATA，共20；Convolution/FWT各I_WB_META，共2；CFD各B16_OFF/I_MEM_ALL_DATA，共2。
2. **L2有限结构10 cells。** Convolution/FWT各U_OFF、S64、U_CAP16，共6；P2条件下两负载各B16/U，共4。
3. **上下游有限参数16 cells。** ROP40_H0、L1_32_H0、ICNT2_H0、WAD256_Q4各在Convolution/FWT执行B16/U配对。

CSV中的条件名是协调标识，不是新造CLI。`B16_OFF`明确映射architecture `B16_BANKED`、H0；`U_OFF`明确映射architecture `U_WB16`、H0。I_WB/META/read等局部ideal以B16为母配置并切换准确ideal向量；I_MEM_ALL_DATA是相对同release B16 OFF的独立数据reference，按实际路径声明被绕过的物理结构，不强行伪称仍执行B16 WB。S64、U_CAP16、P2和其他条件的实际资源、时序与位向量严格读取总合同及producer manifest，不凭简称猜参数。producer_owner负责配置/模块，runtime_release_owner只要求新binary由Lane1发布；Lane3已资格的same-binary overlay可直接消费，不等重复包装。

workload alias沿用已有 `convolutionSeparable`、`FWT_7_21`、`vectorAdd_4M`、`sad`、`cfd_097k`。从既有完整trace/input manifest解析真实路径、顺序、内容SHA和native opcode/legacy scope；不创造trace文件名，不重抓，不改输入以寻求收益。

**调度采用跨类别轮转，目标同时执行两个B/U配对。** D2/L25交付即消费，若现场已有r19在途任务则保持其执行；与此同时让至少一个新类别进入实际执行。可从快速vectorAdd理想点开始验证完整路径，也可先启动已资格的有限结构配对；不要等待全部模式集成、全部producer交付、全部论文接收或理想矩阵齐备才开始首条应用。单个条件阻塞时继续其他已资格类别；配对两侧优先连续完成，同一条件缺一侧时不计算机制收益。

额外22次预算可依据实测在checkpoint中选择：I_BANK的Convolution/FWT各B/U共4；I_L2_SERVICE在两负载各B16共2；最多两个联合有限条件各两负载B/U共8；一个解释清楚的有限候选在vectorAdd/SAD上各B/U共4；其余留给确实必要的同源锚点、canary或失败处理。以上是允许分配方向，所有额外启动合计仍受72总额；出现额外锚点需求时先削减低优先候选，不能把所有候选加总后突破预算。不要承诺填满余量，也不强迫失败重试用尽预算。

有限二因素联合必须有同binary/同输入/同背景的00/10/01/11四格，各含所需B/U；缺失单因素或背景锚点先补并算72，不能用P2_H0代替P2_Q4。余额不足则选择已配齐单因素的组合。若某有限条件要成为论文性能主张，优先在该条件补S64/U_CAP16的Conv/FWT（4次），从同一余量替代其他可选项；H0强静态对照不自动覆盖新环境。

## 3. 四sim并行与真实资源预算

唯一中央registry仍为 `/workspace/ep_l2_ft20261016_shared/RUN_REGISTRY.json`。按总合同正向更新host policy为最多 **4个长期sim、8CPU、32GiB总预约**；小fixture/构建也计入同一共享资源lease。保留 **available RAM64GiB、workspace48GiB、Share40GiB** 安全底线，scan沿原独占策略，不动DTC-L1/C16及其他用户任务。

- 已完成SAD的历史8GiB预约原样保留；若现场出现任何新在途任务，其既有预约不缩、不重登记。
- 已有同输入/路径实测峰值充分支持的小任务，新预约可为4GiB/run；新机制或未知占用先8GiB。必须按真实RSS和配置变化判定，不把旧峰值自动推广到所有ideal/容量扩展。
- 四个1CPU sim外保留剩余CPU给小构建；32GiB共用上限包括构建与验证，不只是sim。
- 实际输出路径先检查文件系统身份。已有 `/workspace/results` 可能解析到Share；不能按路径文字判断。新产物可放在确认的真实workspace物理盘新目录，manifest记录实际路径及hash，不迁移、删除或覆盖历史证据。
- 本次来源快照Share仅约41.45GiB、workspace约70.2GiB；先预算新build/log增长再发任务。资源不足时不持空lease等待，不新建磁盘waiter；继续可做的CPU轻任务并报告具体受阻条件。

准入时核现场资源、活跃进程和producer资格。4sim是上限及可用并行目标，不是在内存或磁盘不足时强行启动的配额。中央调度唯一owner不意味着科学类别串行。

## 4. 精确身份、锚点复用与科学接受

原已资格H0/r19 producing身份：Core `7b8e6ac70b8fe0f1bd37efca11acb5284938825d`、Framework `9bd17f9db3e8cbbc3fdad7283d1e292918546fd5`、binary SHA256 `23094a9d6d6bc5edc4afae4dfc1c5ef0fb3b5d45fbfe56ffb4a33db46c597dee`。新runtime或新ideal实现使用自己的准确身份，不能继承这个binary的科学资格。

每cell绑定Core/Framework/vendor/source、binary、完整有序有效config、trace内容及epoch范围、architecture/feature/ideal向量、termination contract、producer qualifier与独立证据。run-key使用既有完整identity规则；额外记录campaign、cell_id、实际condition，不以workload+mode选择“最新一条”而混掉H0、Q4和新源。

CSV的baseline_cell_ids是科学对照意图，不自动证明同源。**只有同binary、同输入和同完整有效配置/位向量/范围的锚点可直接复用；否则必须补新binary OFF锚点，计入72次上限。** 需要新增source版本时按producer最小受影响范围补资格，不重复所有既有不受影响测试，也不能只凭OFF cycles相似接受新ON路径。

按mode的实际scope验收：

- 真实有限机制和保留完整访存路径的诊断：核原生完整instructions、request exact-once、实际slice范围、sector/reference、WB created/lower accepted/set_done、credit及硬件退尽；资源改变后同步检查有效参数与对应守恒，不能套固定64slice或固定容量常数。
- 全访存理想参考路径：按producer明示的reference semantics、保留/省略部件、请求与完成对应、数据/版本参考、依赖/退休和终态检查接受。允许独立reference实现，不强制伪造不存在的真实64slice WB通路；缺失的物理counter标 `NOT_APPLICABLE` 或 `NOT_OBSERVED`，不能填0冒充实测。
- I_READ_HIT、仅DRAM减压和I_MEM_ALL_DATA必须各自独立：前两者不能充作“无全部访存阻塞上限”。全理想模式是否还留有memory issue、scoreboard、bank、queue/credit、return/response等待须由明确证明和实际统计说明，不能仅靠名称宣布全部解除。
- 新条件出错只阻塞该条件/受影响source范围，保留失败并修普通工程问题后继续；不撤回无关的合法结果，也不降低数据/顺序/生命周期标准以完成矩阵。

独立重算完整配对cycles及S=C_B/C_U，headroom同时给与对应OFF/H0的绝对差和交互。理想上限用同源OFF/ideal比率及残留限制解释，不能混成EP-L2可实现收益。所有已跑负结果、无效结果和未完成cell保留；原H0五例0.16%均值不覆盖，不把不同实验群组混入该平均。

## 5. 增量交付、持续推进和结束

每个完整有效pair接受后立即发布独立科学receipt、raw log/hash索引、配置/source/binary/输入身份和current V2引用，并向既有Lane6 intake入口发本地已约定事件/产物；不等整矩阵。单个已资格ideal完整cell也可按单点scope交付，但不得先算不完整配对或群组均值。Lane6自行执行论文侧接收，Lane5不得替其宣称已入稿。

最新 `docs/ep_l2/review_packs/FT20261017_LANE5_R19_ROBUSTNESS_DELIVERY_AND_PRODUCER_WAIT_r1` 已有六个单pair adapter；组合adapter只是索引，不能当作既有单事件入口直接输入。Lane6 EN-v7在 `1740009d1579b2402b32076f4f65f27619396c01` 已接收D4 Convolution/FWT及Q4 Convolution。Q4 FWT可沿单pair adapter进入；普通SAD/vector及后续D2/L25、新campaign需要在原接收器上做additive scope/condition支持，正确绑定各自既有proof，不能移植r17不同输入作用域的证明或另建平台。

更新原Lane5 STATUS/RECEIPT以及新campaign ledger：50 seed逐cell真实状态、已启动/接受/失败/运行/复用计数、余量和截止时间、实际PID/lease、下一可执行条件及准确依赖。既有r19单独列出，保留历史与原来源。commit/push后回读精确HEAD和关键文件；没有push权限时保留本地产物并报告，不宣称远端已发布。

在现有会话连续solve-and-continue：有已资格工作即跨类别推进，普通spec/包装/解析/构建问题自行修正；不要每完成两条便停止等待用户再次给指令，不用短周期空轮询伪装并行。达到全部必要交付、72次启动上限或新deadline时停止新准入；此前已准入任务依原timeout退尽后结算新campaign，期间发布真实在途状态。旧r19仍按自身合同结算。缺科学输入、功能语义不可成立或现场资源不足时停止受影响任务并清楚报告，其余可行工作继续。

**本Goal成功标准：取得真实完整应用的理想访存上限、L2内部有限结构及上下游干预结果，解释潜力与约束，并持续交付可入稿证据。结果不必为正，实验不能停留在计划、代码或producer自测。**
