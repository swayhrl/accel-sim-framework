# Lane C Goal — 分层采样、页/行指纹与历史校准

Goal：`C15_C_SAMPLING_AND_RETROSPECTIVE_VALIDATION`。
分支：`hrl/vm-c15-sampling-validation-v0`。全程CPU离线；新simulator/trace capture/GPU任务均禁止。优先现有已验证scan，不能为了建立低成本方法先重扫所有大trace。

## C15-0.1 / C15-0.4：历史输入adapter

读取固定C12、Operator-aware、corrected C13、C14 git对象。git路径不同主动定位，但只从manifest列出的目录只读取数据。核对C12 22 arms/Prefill692/Decode740以及Operator-aware原cycle/cumulative-metric保护。复用源码必须改为显式私有out_dir，禁止执行旧脚本的默认写路径。
只消费C13 `SUPERSEDING_C13_RESULTS.tsv`及accepted-after-EQ对象；旧mode1拒绝。C14保留`COLD_MICRO/STATE_CONTEXT_NOT_FULL_ROI_EQUIVALENT`。
T00/T16/T17/T23。产物`HISTORICAL_INPUTS.tsv`、`FIELD_OBSERVABILITY_AUDIT.tsv`和input adapters。缺raw时已发布compact数据可用于其支持的测试，不能声称重验raw。

## C15-3.1：特征成本与可观测性

每个候选feature写来源层级、单位、对象/地址域、可加性、获取成本、需要全trace与否、允许用途。
primary cheap selector只能用T0静态、T1原生目录、真实header/模块shape等廉价输入。历史完整trace-derived refs、完整模拟cycle或机制delta若用于选样，必须另列`TRACE_INFORMED_ORACLE/SIMULATOR_INFORMED_ORACLE`，不能把这种策略宣称为低成本主方法。
T01/T12/T14。产物`FEATURE_COST_AND_SCOPE.tsv`。

## C15-3.2：确定性选择器V1

按phase×operator×实现×dtype/量化×shape区间×KV布局×TP等先硬分层。未知维度单独bucket，不静默归入相似类。
实现三种可复现策略：
1. `LAYER_ANCHOR`：初/中/末层+固定seed内部层，并保留特殊输入输出、KV更新和实现变更。
2. `STRATIFIED_REPRESENTATIVE`：硬分层内中心代表+必要长尾；只使用允许的cheap features。
3. `STRATIFIED_RANDOM`：同strata随机抽样，用作对照，记录纳入概率和seed。

先在virtual budgets 8/12/24/48个目标窗口下做离线计划对比，不表示授权B采24/48个；B仍遵守<=12/部署。不能达到覆盖目标就报告INFEASIBLE，不能省略未覆盖类别。
95%覆盖同时列represented mass和actually sampled mass；如果没有native duration，不能用sim cycles冒充原生时间覆盖，单列proxy/oracle。保留多stream makespan边界。
T14/T15/T21。提前发布稳定selector CLI/API与sample schema给B，不等整套校准结束。

## C15-3.3：split冻结、防泄漏

固定seed=15001；主seed不因结果差而更换。可另用预定15002–15021评估随机抽样变动。选择代码/feature列/样本budget/metric列表/误差阈值形成hash，在打开candidate结果前发布`SAMPLING_VALIDATION_PROTOCOL.json`。

事实边界：团队已经分析过C12/C13所有结果，它们是retrospective calibration和cross-config test，不是真正未见数据。代码层仍将candidate结果作为独立评价输入，禁止用candidate delta选点。
新B部署若可用，预先锁定部分层/真实输入/scenario为`PROSPECTIVE_HOLDOUT`；首次评价后不再称新盲测。特征缺失导致只能做oracle时，主方法状态是未充分验证，不能用oracle成绩替代。
T14/T18；mutation test将候选speedup列置极端值，primary样本计划必须不变。

## C15-3.7：有界页/行指纹库

从已验证scan或小型新capture读取地址。实现exact refs/bytes/read-write-atomic统计、unique页/行区间并集、对象分布、页/行有效字节覆盖、跨窗口集合交并。每条向量访问考虑active mask、完整mem width、跨line/page。不能把cache transaction和lane reference混算。
对于格式确实保留的warp内序列可报告局部reuse；CTA重排后集合指标必须不变。全局order-dependent指标若无法证明顺序则不输出，或仅在显式合成交错/SM映射下标tag-only proxy。
页集合优先exact，巨量行集合可用合并sketch；stable address-hash采样而非独立丢事件。先用可手算和exact-small数据校准，再对有界真实片段使用；不得将估计写`TRACE_DERIVED_EXACT`。每种sketch记录采样率/seed/误差与适用范围。
T06/T11/T12/T13/T21。预算外大输入暂停精确集合并改为显式估计，不能吃满共享内存。

## C15-3.8：新颖性/升级建议

比较绝对尺寸及参考容量归一化比值，分开模型结构、实现、布局差异。第一版不训练神经采样器。单纯距离近只叫`CANDIDATE_KNOWN_CLASS`；真实审核窗口一致才标`KNOWN_CLASS_PROFILED`。
新结构、kernel实现/shape派发改变、KV布局、专家活跃并集或误差超标进入`NEEDS_T2_AUDIT/PROPOSE_T3`。无新数据不能宣布跨模型共性已成立。
T22/T18。产物`NOVELTY_AND_UPGRADE.tsv`。

## C15-4.1：无抽样identity control

先把全量已有per-kernel数据经过新adapter再聚合：cycle、instructions、同源加性counter精确回原总量；hit/miss率由分子分母重算；unique页并集只在有实际集合时闭合。
缺值/重复kernel/cumulative快照断裂/旧mode1输入必须报错而非默认0。保留15,752原C12 cycle-row coverage作为参考核对，不把C13新行混进这个固定计数。
T16/T17。通过后才能解释任何采样误差。

## C15-4.2：代表性回测（不新模拟）

用选择的kernel在原full-ROI里的真实指标估计全体，单独测纯选样误差。可加且组内可交换的计数可用sum(n_g*mean(sample_g))；确定性代表点不声称设计无偏。
至少同时报告cycles（仅符合原ROI加和条件）、TLB accesses/misses/PTW/PTE、可用Cache hits/misses/refs等。rate比较absolute count error、relative count error和percentage-point error；低miss率不能掩盖miss计数倍增。
目标：有exact参考的页/行基数>100时相对误差<=5%，小集合绝对误差<=max(1,ceil(0.05*N))；宏观cycles<=5%只作为筛选目标，不能裁决亚百分比机制。不给没有集合ground truth的union编造误差。
T15/T16/T18。输出`REPRESENTATIVENESS_ERROR.tsv`、`COVERAGE_COST_FRONTIER.tsv`，保留所有budgets/seed成绩包括失败。

## C15-4.3：跨配置成对响应

同一份样本计划用于control和candidate，不为每arm重选有利点。至少涵盖C12 F1/F2、F5/F0、F7-L5/L10/L20，以及corrected C13 L8/L9和容量点；只对确实有相同kernel索引和可归因数据的项评价。
记录delta_cycles、delta_rel、估计误差和sign agreement。C13已见数据标签固定为`RETROSPECTIVE_CROSS_CONFIG_TEST`。不能把budget-dependent exact-capacity变化和lookup latency混成同一个变量。
对于未来推断，抽样区间跨0即INCONCLUSIVE；没有可辩护区间的确定性方法不能伪造bootstrap置信度。自举只衡量抽样变动，不能覆盖context bias。微小效应必须报告分辨能力，不因总cycle误差<5%就判胜负。可报告error-to-effect ratio和已测经验误差带，明确不是普适CI。
T17/T18。产物`CROSS_CONFIG_HOLDOUT.tsv`、`MECHANISM_SIGN_AUDIT.md`。

## C15-4.4：上下文偏差审计

只利用现有C14 micro和对应C12原kernel作比较。先核对kernel identity、配置、binary lineage和telemetry影响；无法证明同条件的pair标confounded，不全部差异都归因cold state。
报告代表性误差与context误差分开。不要用被截断trace的标签预热冒充真实cache/TLB/在途队列恢复。若只有cold和full两个点，不能声称context-window已被验证。
T19/T17。产物`CONTEXT_BIAS_AUDIT.md`、`CONTEXT_COMPARISON.tsv`、未来warmup窗口契约。**不得为补此表启动C15模拟器。**

## C15-4.5：精度失败与成本受限加样

在已冻结virtual budgets内比较增加样本是否改善，采样率/sketch参数调整要有版本和独立测试。不能事后从所有策略选最好成绩充当预注册primary。若所有低成本点都不满足需求，结论为`LOWCOST_ESTIMATOR_NOT_QUALIFIED`，这也是有效结果。
T13/T14/T18。生成每metric适用范围和不适用范围，明确哪些只适合结构分类、哪些可估计统计、哪些可裁决机制。

## C15-4.6：成本

计入header读取、已用native目录、capture、解析、warmup、重试和校准。历史成本缺失标NA，只对可匹配baseline给ratio。virtual样本减少不能直接当实际wall加速。使用历史完整scan的oracle把原采集成本单列，不伪装免费。
T20。输出`COST_LEDGER.tsv`、`LOWCOST_VALUE_ASSESSMENT.md`。

## C15-4.7：发布与C15-5.3未来申请

最终报告必须给：哪种廉价分层最稳、代表性误差多大、上下文偏差多大、哪些量不能低成本估计、是否仍需新full-ROI，以及最多3个高信息量升级点。
未来T3申请含测量对象/前置warmup/原始输入和结构不变/身份及对照/时间磁盘上限/通过和否定标准；本轮`NOT_AUTHORIZED_TO_EXECUTE`。
B尚无数据时仍完成全部历史校准、synthetic测试与selector发布，另列`DYNAMIC_CROSS_MODEL_PENDING`。不要长期空等。工具成功和科学精度成功分开。只commit/push C分支；原C12/C13/C14全部只读。
