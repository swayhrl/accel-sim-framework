# Vector r5 受控访存敏感性：最终科学报告

Goal：`EP_L2_MEMORY_PATH_CONTROLLED_SENSITIVITY_20261026_V1`。2026-10-26。唯一整合者：EP-TAG-ROOTCAUSE。

**科学执行、独立接受、比较及164归档均已完成；两个请求均CLOSED，预留已释放。** 最终综合决定：**维持现有T；不继续L1 MissQ参数扫描，不放松detach保护。**

## 已接受结果

复用同一850MHz/MissQ16已接受基线；只启动两个获新预算授权的完整应用，各一次。E1完成后按预注册规则决定E2，不把两个变化叠加。

|应用端点|DRAM MHz|L1 MissQ|core cycles|相对基线cycles变化|L1 MissQ重试|生产TagFAIL / relieve / detach|全set tick末最大RESERVED|
|---|---:|---:|---:|---:|---:|---|---:|
|既有基线|850|16|75039|—|1240787|0 / 0 / 0|3/16|
|E1 DRAM控制|935|16|69861|−6.900412%|1255502|0 / 0 / 0|3/16|
|E2 L1控制|850|32|75161|+0.162582%|790574|0 / 0 / 0|3/16|

E1 baseline/case周期比为1.0741186；E2为0.9983768。百分比均以固定core1132MHz的模拟周期计算，未使用主机wall time。E2比基线增加122 cycles；本轮不对其小幅退化作统计显著性主张。

**PROVEN**：在这个精确模型、输入和单因素控制下，提高DRAM域时钟降低端到端cycles；L1 MissQ扩容使局部重试减少36.2845%，却未降低端到端cycles。不能由基线重试次数高推出L1 MissQ容量是关键吞吐瓶颈。

**PROVEN**：两个控制均未形成真实TagFAIL，也未形成16路pending Tag的covered新请求联合；detach仍零。因此两项结果不能归功于T，亦不支持为了触发T继续扫参数。

## 身份、输入与接受边界

三端使用同Core `1093d2629e3d6a9130ba25b9dd119b6f3e16c092`、Framework `9dd1ee57a83d83b56b7874bc7c716185ab52c8f7`、vendor `f90c430c3a1ce8f08c09942a5a1c3a797bb2295b`。main SHA256为 `e511cce7d8bcd5a3ebbe6255f42ebe153547484a69c6857ab55f7a8835a2dc33`。未使用main61或A2 binary补结果。

|端点|UUID|raw SHA256|
|---|---|---|
|基线|`a6b61f77-2ff6-45ad-897c-df0812d01ae8`|`1f5519151cb381fbc370591d65e7ad78691435d5955ad99fea8dcdf7ffab0f6a`|
|E1|`375881f2-a811-4f71-a7cf-d171eed6fdf7`|`bb5b73b04b7c053ef58c69f7e05cc3f4693e6e635ed73b2e7f8a8f38f6bc6447`|
|E2|`e3045a2f-25b0-4ff1-9881-c6473ae25634`|`ceaef25bd55070d8fcbc237a58e438b516c4cdb4e8359094c12e77d3286248e9`|

每端均为56M thread instructions、15625 CTA、1kernel、64slice完整drain。独立检查全部282项实际option：E1仅clock DRAM850→935；E2仅DL1 miss_queue_size16→32且DRAM850。原四份config与输入语义逐字保留，第五份只含一个允许option。R4/212、r5、RO exact-once及闭合检查通过。cycles、动态merge、WB bytes和detach不作预设验收值。

输入103535960 bytes直接来自genuine164。FUSE inode变化后做case范围的双次关闭重开完整SHA，E1约2.384s、E2准备约2.151s；内容与旧接受receipt一致，本地新trace副本0B。E2随后qualification/launch复用元数据仍稳定的fresh内容证明，不声称那两步又完整读取trace。

本轮资格为模拟器生产协议和trace条件下的接受；SASS数值输出验证仍UNKNOWN，不证明硬件性能、PPA或T独立收益。producer内置点标记`pair:false`保留：这里的受控敏感性比较没有冒充旧S/F正式配对身份。

## 局部服务、并发与Tag机会

|同单位字段|基线|E1|E2|范围|
|---|---:|---:|---:|---|
|DRAM读服务bytes|32000000|32000000|32000000|32channel求和|
|DRAM写服务bytes|12897536|12882560|12890240|32channel求和|
|DRAM byte利用率|77.8143%|75.9577%|77.6748%|byte numerator/denominator分别求和再相除|
|DRAM ticks/每channel|56346|57704|56438|32个channel各自相同，跨端时钟不同|
|DRAM scheduler-full|477774|472286|471492|channel-DRAM-tick求和|
|L2 MissQ full观察|818741|447814|699179|slice-L2-tick事件求和|
|L2→DRAM queue full观察|797984|434569|681865|slice-L2-tick事件求和|
|L1 bank/latency queue conflict|122492|135158|82608|application重试事件|
|RO transactions|250118|250204|250013|64slice求和|
|RO merges|749882|749796|749987|64slice求和|
|独立RO lower-line峰范围|63–70|65–73|62–70|每slice各自峰的min/max，不求和|
|RO transaction峰范围|90–96|90–97|88–96|每slice各自峰的min/max|
|B0 RESERVED总峰的最大值|96|97|96|单slice总Tag峰；不是单set|
|covered newTag∧structural eligible|2385|2219|1518|同快照target-set head-cycle实际联合|

更多同单位数据与精确来源见 [CSV](SAME_IDENTITY_METRICS.csv) 和 [投影](RESULTS_PROJECTION.json)。生产probe/commit计数与observer covered域分开；TVD skip仍为NA，不补成零。

E1降低了L2两个queue的阻塞观察，但L1重试和bank queue冲突上升；E2同时降低多个局部重试，却不改善endpoint。两者均说明：不能将重叠阻塞计数相加、相减成“节省global cycles”，也不能要求性能改善时所有局部指标单调改善。

每slice已有数十条独立RO lower line在飞，单slice总RESERVED接近百条，而单set仍最多3路。**LIKELY**：Tag机会缺失与并发分散在不同set、每条事务pending窗口及请求合并共同相关；“没有全GPU MLP”不是已支持解释。**UNKNOWN**：哪个因素主导单set压力。没有逐事务、同slice/set到达率与RESERVED寿命序列；本轮未从全GPU均值套Little's Law推TagFAIL概率。

E2反例收窄了因果解释：单独MissQ16→32并没有把Tag压力推近16，也不带来cycles收益。它不证明任意L1容量、核心依赖或其它上游资源永远无影响。

## 瓶颈归因与论文边界

1. **PROVEN（有限因果）——DRAM域服务条件影响端到端时间。** E1证明所选DRAM时钟控制有6.90%周期效应；结合scheduler、lower queue观察，是当前最强的服务敏感性证据。时钟同时改变命令时序的物理时间及带宽，不是纯带宽隔离，也不能据此估计Amdahl串行比例或宣布唯一瓶颈。
2. **PROVEN（局部约束，非已证critical bottleneck）——有限请求queue造成大量重试。** L1 MissQ及L2/lower queue有真实阻塞；E2显示容量扩展可以消除部分重试而不改善endpoint。继续扩容扫描的信息价值低。
3. **PROVEN观测 / UNKNOWN因果份额——core ready/RAW依赖及EP bank/landing等待。** 原路径审查已提供依赖与局部拒绝证据；新端点仍有bank/landing拒绝。未改变core或bank服务，不能排出它们的独立周期贡献，也不能把它们与上述反压链当互斥原因。

Tag associativity、L1 MSHR entry/merge、RO descriptor容量、DRAM return queue在相应观察域没有表现出饱和：两个新端点L1 entry/merge失败均0，descriptor峰374/367小于512，production TagFAIL0且单set峰3/16，DRAM returnq-full0。这个结论不覆盖未观测窗口或所有其它资源；局部bank/landing确有拒绝。L2/DRAM queue达到128，不能称整个L2“没有压力”。

当前Core没有实际TLB/PTW生产时序模型，不能将其写成瓶颈；LOCAL_XBAR是packet队列抽象，不能据此断言物理NoC字节带宽饱和。排除异常`Bank_Level_Parallism_Col`。重复打印后被覆盖的最后slice/channel标量不作global统计，投影只保留带scope的聚合和明确application标量。

CFD/DWT完整路径raw仍未在本轮复用到，两个Vector控制不补写它们的瓶颈排序；历史最大4/16与3/16及production零值仍按原身份保留。结论仅覆盖当前Vector受控点及原已接受条件。

论文可以准确表述：

> 在已接受r5应用条件下没有观察到生产Tag分配失败，因而T未获得触发机会。Vector的有限DRAM域加速降低周期，而L1 MissQ扩容只降低局部重试；两者均保持每set RESERVED峰3/16和零detach。当前结果支持服务/queue反压与Tag关联压力应分别分析，不提供真实应用T性能收益证据。

## 实际执行、工程调整与未执行事项

实际执行：两个新budget/request各一个完整native模型，均自然exit0、无retry/refund；每case一次native help资格；新intent在fork前消费；独立接受/比较；五项不启动模型的guard mock；输入SHA；E1/E2归档及各两个174-new ext4恢复Target核验。每case单CPU16/nice10，模型hard9GiB、wall7200s；RSS峰E1约548MiB、E2约552MiB。主机elapsed930.875s/689.560s仅作工程记录。

E2运行中peer给shared entry添加DTC continuation。完整entry SHA因此变化，首次accept检查HOLD，没有重跑模型。已另建**仅postrun accept/archive**适配：旧EP dispatch body逐字保留，peer前缀不匹配EP；其余62个pins及10个env hash逐项一致，原spec/科学源码未改。精确委派链与实际终态绑定见 [证明](evidence/E2/POSTRUN_ENTRY_ROUTE_EQUIVALENCE.json)。该证明本身不授予科学接受；后续独立decoder仍完整执行。保留peer更新，不回滚共享入口。

只读子任务分别复核资源、E1/E2生产身份与比较、E2 live header及输入适配。没有并行修改生产源码或建立永久Lane，独立审查见 [检查说明](INDEPENDENT_REVIEW_AND_ACTUAL_CHECKS.md)。

未执行：基线重跑、两因素组合、额外参数扫描、GPU采集、新CPU cache fixture、T策略改版、passive counter实现。未消费原EP-MAIN耗尽的epoch2预算或借DTC预算。protected source与原EP-MAIN科学资产不修改。

## 归档与收尾

E1已完成genuine164 COPY_ONLY、关闭重开range/full SHA及两份native ext4恢复验证；archive17684480 bytes，SHA `33b2b0ad8048946c7fedf96ec9f2a35b7ed8dbb7b69311dd54e85a2ecce0c3c5`。恢复的两个Target都在174-new，不能称“164主机独立恢复”。portable第二恢复不导入runtime/controller。详见 [E1回执投影](evidence/E1/ARCHIVE_AND_RESTORE_PROJECTION.json)。

E2亦已完成同样的164归档和两Target恢复，archive17612800 bytes，SHA `806ebe44ddd97385a9dd8e111241c32e92e9f7b22fadb0b6cd8a9c7326d528e5`；source KEEP。见 [E2回执](evidence/E2/ARCHIVE_AND_RESTORE_PROJECTION.json)。

E2首次归档HOLD来自本轮私有归档适配误用完整模型准入：它重新计入9GiB模型RAM和peer未来最大增长，而模型已经退出、原whole-operation预留仍完整持有。那份HOLD快照真实保留，**不是归档文件自身缺约3GiB**，也没有伪改成原admission PASS。

经独立设计复核后，另建仅该E2 `result archive` 收尾适配，不改冻结脚本或spec：先核验自然DONE、模型进程已退出、accepted/raw/spec/UUID、原3.5GiB登记预留仍完整；保持peer登记和原512MiB写入包络。每进程AS上限256MiB，两个主要Python进程包络512MiB（另有短暂findmnt等helper，继承AS cap）；磁盘实际门仍为8GiB+512MiB，RAM分别留64/48GiB floor再加512MiB余量；新增本地写入硬限128MiB。snapshot的`admission_pass`继续为null，明确属于保留预留内的continuation，不授予新模型准入。

实际E2收尾本地logical新增35180368B、allocated新增35332096B（约33.7MiB），低于上限；归档源17553044B。新增主要是两份恢复检查副本，归档payload在164；没有清理资产、减少peer预留或新model/help fork。新阶段证明与闭合回执均写control，不改变已归档source集合。见 [阶段证明](evidence/E2/ARCHIVE_CONTINUATION_STAGE_PROOF.json)、[资源投影](evidence/E2/ARCHIVE_CONTINUATION_RESOURCE_SAMPLES_PROJECTION.json)、[收尾回执](evidence/E2/ARCHIVE_CONTINUATION_CLOSEOUT.json)。两case仅在全SHA及两次恢复通过后CLOSED/reserve0。

## 下一决策

**维持现有T。** 已完成本轮最有价值的两个单因素控制，保留E2负结果；不因detach为零继续容量扫描或松guard。

若另获新科学授权，优先级为：第一，补同slice/set的被动到达/Tag RESERVED生灭联合，先用小CPU fixture验证非干扰性，分清分散与寿命；第二，仅当需要区分DRAM时序与带宽时，设计一个精确隔离服务条件的有限控制。它们均为NOT_EXECUTED，没有新budget或模型启动。真实应用T收益、机制改版正确性以及跨应用普遍瓶颈排序仍UNKNOWN。

最终独立收尾复核：E2 range/full SHA与两个既有恢复目录各27行全inventory/metadata/fileSHA通过，4项补充工具SHA匹配；仅只读验证，没有二次归档或恢复写。最终[范围检查](evidence/FINAL_SCOPE_CHECK.json)确认两request CLOSED、各consumed1及reserve0。protected EP-MAIN由其它owner推进到0cd84ed文档提交且tracked clean，本任务未回滚；原审查基准62e402及runtime身份分别保留。
