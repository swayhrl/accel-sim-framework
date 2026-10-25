# 五个遥测失败点独立诊断 V3

本诊断读取了每点完整lossless raw、全部progress/resource与原始进程/网络trace，并校验完整raw SHA与原exit回执。未启动、重跑、附加任何科学模拟，未修改历史分类、活动源码、registry或账本。

## myocyte CH

- UUID：`a0a7bcfa-91d9-4498-aa2b-c18f9e696dc8`
- 直接触发：`DTC_TELEMETRY:MISSING_OR_STALE_PRODUCER`，returncode -15，elapsed 3913.140231795609秒。
- 已证实：旧producer在第8192条成功发出后，下一次observe因sequence_>=8192将enabled_=false；后续模型仍执行，但不会再发进度。原30秒freshness守护据实停止该不完整输入。
- 状态：`CONFIRMED_OBSERVATIONAL_PRODUCER_8192_RECORD_CEILING`

证据链：

1. 旧commit cfd3ff56 header第90/123行：达到8192后永久关闭producer。
2. progress seq1..8192完整连续；strace恰好8192个完整成功send，无失败/丢序。
3. phase counts显示大量强制阶段事件（BOUNDARY4915、PARSE1638、SIMULATE1638、INIT1），10秒cadence不会限制force的边界记录，因此5993-kernel输入在约1638个kernel后已耗尽容量。
4. 第8192条后raw继续产生kernel统计和后续kernel加载；终止尾部kernel CH1658/DM1657，明显未完成全部5993个kernel。
5. 结束时末条进度年龄约30秒；SIGTERM来自launcher；没有模型SIGABRT或死锁报告。

排除与边界：

- socket overflow/send失败：所有8192次send均完整成功，无EAGAIN/ENOBUFS。
- sequence gap：精确1..8192。
- 引擎deadlock/assert：完整raw没有对应fatal诊断，退出为launcher SIGTERM，且截止前模型继续处理后续kernel。
- RAM/disk/原资源policy：RAM/disk样本均PASS；原policy仅CONTINUE/WARN，没有STOP。

仍不确定：

- 未推断若取消守护后的最终性能或正确性；这些历史点仍无accepted cycles。

修复状态：后续从未花费的新点已注册并使用1,048,576-record observational profile；历史这两点保持失败、不重跑。

最小下一步：保留两点失败，报告归因容量不足；只对已授权且未启动的点使用现行1M profile，不从这两点恢复或补算cycles。

逐点全部SHA与完整采样：`E2-AEV100-977e34578994c3d2-CH.DIAGNOSIS.json`。

## myocyte DM

- UUID：`95fedea6-6293-4673-9150-e36822857be0`
- 直接触发：`DTC_TELEMETRY:MISSING_OR_STALE_PRODUCER`，returncode -15，elapsed 4017.0480416361243秒。
- 已证实：旧producer在第8192条成功发出后，下一次observe因sequence_>=8192将enabled_=false；后续模型仍执行，但不会再发进度。原30秒freshness守护据实停止该不完整输入。
- 状态：`CONFIRMED_OBSERVATIONAL_PRODUCER_8192_RECORD_CEILING`

证据链：

1. 旧commit cfd3ff56 header第90/123行：达到8192后永久关闭producer。
2. progress seq1..8192完整连续；strace恰好8192个完整成功send，无失败/丢序。
3. phase counts显示大量强制阶段事件（BOUNDARY4915、PARSE1638、SIMULATE1638、INIT1），10秒cadence不会限制force的边界记录，因此5993-kernel输入在约1638个kernel后已耗尽容量。
4. 第8192条后raw继续产生kernel统计和后续kernel加载；终止尾部kernel CH1658/DM1657，明显未完成全部5993个kernel。
5. 结束时末条进度年龄约30秒；SIGTERM来自launcher；没有模型SIGABRT或死锁报告。

排除与边界：

- socket overflow/send失败：所有8192次send均完整成功，无EAGAIN/ENOBUFS。
- sequence gap：精确1..8192。
- 引擎deadlock/assert：完整raw没有对应fatal诊断，退出为launcher SIGTERM，且截止前模型继续处理后续kernel。
- RAM/disk/原资源policy：RAM/disk样本均PASS；原policy仅CONTINUE/WARN，没有STOP。

仍不确定：

- 未推断若取消守护后的最终性能或正确性；这些历史点仍无accepted cycles。

修复状态：后续从未花费的新点已注册并使用1,048,576-record observational profile；历史这两点保持失败、不重跑。

最小下一步：保留两点失败，报告归因容量不足；只对已授权且未启动的点使用现行1M profile，不从这两点恢复或补算cycles。

逐点全部SHA与完整采样：`E2-AEV100-977e34578994c3d2-DM.DIAGNOSIS.json`。

## scalarProd DH

- UUID：`5fb1dece-aab7-459e-8dab-c53425d18972`
- 直接触发：`DTC_TELEMETRY:MISSING_OR_STALE_PRODUCER`，returncode -15，elapsed 32.477542124688625秒。
- 已证实：receiver在最后SIMULATE记录之后约30秒未收到任何新记录而停止。仅6次send均成功，无法归为record-cap或socket丢包；观测覆盖与长同步CTA trace加载路径之间存在窗口。
- 状态：`CONFIRMED_FRESHNESS_STOP_WITH_STRONGLY_SUPPORTED_IN_CYCLE_BULK_LOAD_GAP_LOWER_LEVEL_COST_UNRESOLVED`

证据链：

1. 最后seq6发生在首kernel，phase=SIMULATE、completed=0；以后没有send调用。
2. accel-sim.cc:190先同步调用cycle()，194才observe(SIMULATE)，同线程producer不能在cycle内部耗时子过程刷新。
3. gpu-sim.cc:2523 cycle调用issue_block2core；2337..2339遍历全部clusters，CTA issue链在2288进入virtual init_warps。
4. trace_driven.cc:1019..1031 init_warps→init_traces，1104..1112对文本.traceg批量载入完整CTA；trace_parser.cc:562..619逐行解析、分配所有warp的inst_trace_t，函数没有中途progress调用。
5. 完整raw从kernel1 header/launch延伸到thread block0..45；RSS在0.10/10.18/20.30/30.38秒约0.075/1.216/2.378/3.590GB，符合持续批量载入/分配，而非已证明模型engine循环死锁。
6. strace有cat→kernel1.traceg的真实打开与后续checkpoint stat调用，所有6个send完整成功；随后launcher向同一进程组发送SIGTERM。

排除与边界：

- record cap：运行1M profile，仅6条，远未到阈值。
- socket overflow/send failure/sequence gap：6次send完整成功、seq1..6连续，未见EAGAIN/ENOBUFS。
- OOM/16GiB硬cap/outer RAM或disk：peak约3.59GB，四个资源样本均PASS，OOM计数未增加，资源policy只有CONTINUE/WARN，没有STOP。
- 已证明的引擎deadlock/assert：完整raw无fatal诊断；此断言只排除捕获到的fatal触发，不能证明模型若继续运行必然成功。

仍不确定：

- 旧strace没有-t/-T和read/write跟踪，亦无每线程CPU时间、运行队列/IO等待、stack样本，故不能把30秒唯一归因于CPU解析、共享164/FUSE读延迟、cat pipe等待或调度；不能给这些项分摊比例。
- 根据源码和raw强支持cycle内多CTA同步bulk load超过观察窗口；终止当刻的具体栈没有被记录，不能称为栈级已证明的唯一callsite。
- 无仿真重跑、无新性能cycles，未证明最终数值正确性。

修复状态：未实施生产修复；1M record profile对此6-record gap无效。R12 RAM守护替换也未改变此遥测freshness规则。

最小下一步：先用纯CPU解析fixture复现首轮多CTA批量载入的observe间隔，并分别测CPU耗时与文件读取耗时；若另行授权新科学尝试，需独立注册新generation，记录低开销每线程CPU/IO与慢调用起止。候选修复是同线程安全解析/CTA边界增加明确phase的observational快照，并证明counter语义/模型输出不变；不得单纯放宽30秒或把外部心跳冒充producer进度。

逐点全部SHA与完整采样：`E2-AEV100-2b93f70cd0666c51-DH.DIAGNOSIS.json`。

## 纯CPU容量fixture

精确历史producer header，调用8194次force observe，真实AF_UNIX nonblocking socket只收到seq1..8192，producer随后enabled=0。没有科学模型。证据`CPU_PRODUCER_CAP_FIXTURE/RESULT.json`。

## lavamd CM（新增闭合失败）

UUID `eaa858dd-04d0-41ba-9a3c-a5975c330720`。直接触发 `DTC_TELEMETRY:MISSING_OR_STALE_PRODUCER`，elapsed 31.002449095249176秒，returncode -15。

最后首kernel SIMULATE记录后约30秒无新producer包，原freshness守护终止。源码和完整raw强支持与scalarProd同一cycle内CTA批量文本trace加载的观测窗口；底层耗时分解、终止当刻精确栈仍未被历史数据捕获。

证据链：

1. progress只有seq1..6，INIT→BOUNDARY→PARSE→BOUNDARY→BOUNDARY→SIMULATE，completed一直为0；最后seq6在mono 9689470114724161，没有terminal。
2. 所有6次sendto完整成功，无EAGAIN/ENOBUFS/sequence gap；cap为1,048,576，不是旧8192容量失败。
3. raw只进入kernel1，grid1000×128线程，逐个打印thread block0..56；没有首kernel终止统计或fatal断言。
4. accel-sim.cc:190同步cycle()，194才observe；gpu-sim.cc:2523 issue_block2core()在2337..2339遍历clusters；CTA issue通过2288 init_warps进入trace_driven.cc:1031 init_traces，1112批量文本trace读取；trace_parser.cc:562..619逐行解析并分配整CTA，没有中间progress。
5. 约0.27/10.52/20.77秒的RSS为327155712/1874853888/3477078016 bytes，持续增长，三个RAM/disk样本都PASS，三个原resource policy样本都CONTINUE。
6. 31.002秒launcher SIGTERM；推算最后包年龄约30.583秒，符合原30秒freshness条件。

排除项：

- record ceiling：只有6条，非8192/1M耗尽。
- socket overflow/send错误/sequence gaps：6次send完整成功、序列连续。
- 采样到的OOM、16GiB硬cap或outer RAM/disk/原resource policy STOP：均无相应触发；peak_tree RSS约3.48GB，显著低于16GiB。
- 已捕获的模型deadlock/assert fatal：全raw未见；不能据此断言若继续运行必然完成。

不确定性：

- 源级调用链和多个CTA头/RSS增长强支持同类同步bulk-load缺口；缺少终止当刻stack，不能称为栈级唯一callsite实证。
- 历史strace无read/write耗时、无-t/-T，也没有进程/线程CPU时间或调度与IO等待，所以CPU文本解析/分配、164/FUSE读取、cat pipe等待和调度各自贡献仍不可证实。
- 没有重跑，无最终科学结果，不能接受partial cycles。

修复状态：未对该点修复或重跑；1M容量与RAM新profile不修复同线程观察窗口。历史exacttelemetry分类和archive保持不变。

最小下一步：与scalarProd一起做非模拟CPU/解析fixture，量化同线程多CTA加载期间observe间隔和CPU/IO成本；候选修复需在安全的同线程CTA/解析边界提供语义明确的observational阶段快照，并验证输出/计数不变。新的科学generation须另行注册，不恢复本次attempt，不用外部心跳代替进度。

V1（三点）报告与全部历史classification保持原字节；本V2新增第四点，不覆盖V1。逐点完整SHA、全部六条progress、全部资源样本见`E2-AEV100-ddb6806316876a85-CM.DIAGNOSIS.json`。

## lavamd CH（新增闭合失败）

UUID `b6e28445-8e1b-48fd-b352-aeca570bff64`。直接触发 `DTC_TELEMETRY:MISSING_OR_STALE_PRODUCER`，elapsed 31.08816835284233秒，returncode -15。

最后首kernel SIMULATE记录后约30秒无新producer包，原freshness守护终止。源码和完整raw强支持与scalarProd同一cycle内CTA批量文本trace加载的观测窗口；底层耗时分解、终止当刻精确栈仍未被历史数据捕获。

证据链：

1. progress只有seq1..6，INIT→BOUNDARY→PARSE→BOUNDARY→BOUNDARY→SIMULATE，completed一直为0；最后seq6在mono 9690823893457260，没有terminal。
2. 所有6次sendto完整成功，无EAGAIN/ENOBUFS/sequence gap；cap为1,048,576，不是旧8192容量失败。
3. raw只进入kernel1，grid1000×128线程，逐个打印thread block0..55；没有首kernel终止统计或fatal断言。
4. accel-sim.cc:190同步cycle()，194才observe；gpu-sim.cc:2523 issue_block2core()在2337..2339遍历clusters；CTA issue通过2288 init_warps进入trace_driven.cc:1031 init_traces，1112批量文本trace读取；trace_parser.cc:562..619逐行解析并分配整CTA，没有中间progress。
5. 约0.27/10.53/20.78秒的RSS为352321536/1782579200/3326083072 bytes，持续增长，三个RAM/disk样本都PASS，三个原resource policy样本都CONTINUE。
6. 31.088秒launcher SIGTERM；推算最后包年龄约30.676秒，符合原30秒freshness条件。

排除项：

- record ceiling：只有6条，非8192/1M耗尽。
- socket overflow/send错误/sequence gaps：6次send完整成功、序列连续。
- 采样到的OOM、16GiB硬cap或outer RAM/disk/原resource policy STOP：均无相应触发；peak_tree RSS约3.33GB，显著低于16GiB。
- 已捕获的模型deadlock/assert fatal：全raw未见；不能据此断言若继续运行必然完成。

不确定性：

- 源级调用链和多个CTA头/RSS增长强支持同类同步bulk-load缺口；缺少终止当刻stack，不能称为栈级唯一callsite实证。
- 历史strace无read/write耗时、无-t/-T，也没有进程/线程CPU时间或调度与IO等待，所以CPU文本解析/分配、164/FUSE读取、cat pipe等待和调度各自贡献仍不可证实。
- 没有重跑，无最终科学结果，不能接受partial cycles。

修复状态：未对该点修复或重跑；1M容量与RAM新profile不修复同线程观察窗口。历史exacttelemetry分类和archive保持不变。

最小下一步：与scalarProd一起做非模拟CPU/解析fixture，量化同线程多CTA加载期间observe间隔和CPU/IO成本；候选修复需在安全的同线程CTA/解析边界提供语义明确的observational阶段快照，并验证输出/计数不变。新的科学generation须另行注册，不恢复本次attempt，不用外部心跳代替进度。

V2（四点）报告与全部历史classification保持原字节；本V3新增第五点，不覆盖V2。逐点完整SHA、全部六条progress、全部资源样本见`E2-AEV100-ddb6806316876a85-CH.DIAGNOSIS.json`。
