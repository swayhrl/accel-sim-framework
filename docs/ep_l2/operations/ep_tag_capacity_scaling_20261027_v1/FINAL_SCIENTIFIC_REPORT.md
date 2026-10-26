# EP-TAG-FLOW 最终科学报告

Goal：EP_L2_TAG_CAPACITY_SCALING_AND_DETACH_OPPORTUNITY_V1。2026-10-27，Asia/Shanghai。

**决定：维持现有T及协议保护，结束本轮缩容序列。** 四项统一新Core/binary的完整Vector实验均接受、归档和CLOSED；从8MiB减到2MiB名义Tag覆盖容量仍无生产TagFAIL、relieve或detach。T-OFF条件没有满足，未登记或启动对照；没有继续缩容、延长DRAM延迟或放宽reuse/sector保护来寻找正结果。accepted EP-MAIN/Core没有合并本轮结构补丁。

## 结果和身份

|配置|Set×Way|cycles|相对A|事件峰 / tick末峰|平均RESERVED/Set|DRAM写字节|dirty WB创建|
|---|---:|---:|---:|---:|---:|---:|---:|
|A|64×16|75,039|+0.000%|4 / 3|0.928633|12,897,536|100,762|
|B|64×8|75,785|+0.994%|4 / 3|1.005951|14,391,296|112,432|
|C|32×16|75,733|+0.925%|7 / 6|2.051350|14,347,904|112,093|
|D|32×8|77,237|+2.929%|7 / 6|1.924887|15,050,112|117,579|

所有行：64 Slice、32 DRAM Channel、64 Memory Subpartition、128B line、56,000,000 instructions、15,625 CTA、1 kernel和完整in-flight drain。所有行生产TagFAIL=0、诊断raw-reservation-fail=0、relieve=0、detach=0、detach后接受=0。L2服务、SM/L1/ICNT/DRAM时序、队列和W/V/M/T保护保持。物理Payload始终1024 Resident+128 Bypass+16 WB=1168槽/Slice、4 banks；逻辑Tag分别1024/512/512/256。

生产Core `c67b332db703f09571ba6628222c77d71440e141`；ELF `ad4421b441d1f8efef4c956381ede5e6fd7389147d26960931e202e0a38e4b07`；实际静态库 `74becb34ba74646e56109f181d4cbae61b2e94540171729754fa6b430f2547c9`。运行Framework9dd与研究基准a9a分开，完整五元身份见CAPACITY_SCALING_DESIGN_AND_IDENTITY.md。A确实复现75,039cycles；其他行没有继承旧producer的应用接受资格。

## 按证据强度回答研究问题

1. **PROVEN：当前Vector的不可替换预约Tag存在余量。** A峰4/16；D峰7/8且tick末峰6/8。每项375,000个独立NEW，实际到达前遇到满Way RESERVED的联合事件均0。全时area、实际到达联合和生产失败计数相互支持；不是由独立边际计数相乘，也不是仅由全GPU平均值推断。D平均占用约24.06%的逻辑Ways，但不把平均值当作极值证明。
2. **PROVEN：Tag也承担有效Resident数据驻留，16-way不能被概括为完全无用。** B/C约1%和D约2.93%的cycles损失真实保留。DRAM读字节各32,000,000；写字节和dirty-replacement WB增加。源码`ep-l2-ft-cache.inc:558-585`只在已绑定的dirty replacement L2_WRBK_ACC路径增加WB_created。较少逻辑Tag限制可关联的Resident行，即使物理1024槽不变。不能据此声称物理Payload SRAM或芯片面积减少。
3. **PROVEN：Set缩减更集中地产生同Set预约重叠；实际TagFAIL先由Set还是Way主导仍UNKNOWN。** 等4MiB的B每Set独立NEW91–93，C183–184；B事件峰4、C7。C采用真正IPOLY32，不能拿IPOLY64结果简单&31。C仍有16Ways，两者平均预约占Way约12.6%/12.8%，均无TagFAIL。C比B少52cycles只描述该受控Vector结果，不推广为普适几何优劣。
4. **PROVEN：存在真实NEW与eligible RO共现，但它没有与TagFAIL联合。** R5在A/B/C/D分别记录2385/1567/14204/14534次NEW-head与结构eligible共现；这些是重复covered-head exposure，不是独立请求。FAIL∧eligible、FAIL∧reuse、满Way-head均0。LIFE的独立NEW/Set联合另列，不能混合分母。缺少TagFAIL使本轮T没有实际执行机会。
5. **PROVEN（观测范围）：其他队列与服务约束确实出现。** 各配置missq/lowerq/DRAM scheduler的单Slice/Channel采样峰达到128；存在missq前置阻塞及bank拒绝。B0这些是采样峰，不是假称完整intratick高水位。descriptor采样峰低于512，WAD低于128，Bypass采样使用0，Tag预约没有满Way。Resident在A可达物理1024、缩容时可关联驻留下降；不能把它们统一叫TagFAIL。
6. **LIKELY：额外dirty写回及相关队列/服务变化是缩容损失的重要路径。** B相对A多11670个dirty WB和1493760写字节，恰为128B/WB；本轮只改变几何，其他服务预算固定。源路径与流量变化支持解释，尚未分离DRAM服务、bank时序、队列重叠各自贡献。不能把全部cycles差都分配给WB、Tag或某个局部stall计数。
7. **UNKNOWN：T的独立端到端性能效应和8-way跨负载充分性。** 没有满足条件的同几何T-ON/OFF实测对照，因此没有实测T speedup，包括不能编造0.0%对照收益。8-way在本Vector两种Set配置中足以避免TagFAIL，但有容量/驻留性能代价，无法推广CFD/DWT/Conv或新SM70负载。

## 每Set生命周期与计数边界

逐物理Set分析使用LIFE；R5没有物理Set ID，其“target-set@head”统计不能被伪装成逐Set全时分布。新到达在预约数k时的真实联合保留全17-bin向量；D的NEW只在R0..6出现，R7/R8均0。各配置预约episode左右删失均0，逐Set核验ENTER=EXIT=CLOSED_NEW+CLOSED_RE，SUM_NEW+SUM_RE=加权预约area。对同一Set、同一episode定义，λ_new×寿命_new+λ_re×寿命_re严格等于实测平均占用；没有据此推断失败概率。详细分布、CSV和原始联合在164证据包的analysis/目录。

|配置|独立NEW/Set范围|正寿命NEW均值（L2 ticks）|零寿命NEW|满Way NEW联合|
|---|---:|---:|---:|---:|
|A|91–93|1141.591732|125000|0|
|B|91–93|1248.950772|125000|0|
|C|183–184|1272.566016|125000|0|
|D|183–184|1217.840792|125000|0|

上述均值排除125,000个零寿命新分配episode时才称“正寿命均值”；全部新分配episode另有均值，不能混称RO返回时延。全GPU同时峰值、精确episode分位数、逐Set VALID/MODIFIED/INVALID全时联合及未发出的终态dirty行精确数仍UNKNOWN。未将各Slice独立峰相加或各层不同单位请求计数相减。

## 实际执行、未执行及下一步

实际执行：最终clean源40次四几何CPU验证/20对observer非干扰；22次原16-way回归/11对，与11c语义参考一致；31份ON wire严格校验；解析、Host、路由、输入及归档定向工程检查；一次native `-h`加载；四次完整应用。A/B实际并发，C与D依赖前批科学结果接续。每项新预算1、durable consume-before-fork、实际PID/maps/env/strace打开真164输入、自然DONE、64-Slice统计/RO/descriptor/line closure及全282项打印选项均核验。没有重试、退款、GPU采集或旧预算复活。

未执行：完整应用T-OFF、更多几何/延迟扫描、Tag+Payload同步缩容、保护条件放宽、accepted simulator合并、真实数值SASS输出比对。真实应用detach旧事务完成路径本轮NOT_EXERCISED；构造CPU fixture覆盖旧Payload/generation、乱序sector返回、ICNT背压与无Tag旧RO完成，不能替代实际触发收益。

**PROVEN完成边界：** Trace只有两次HtoD和一个kernel，没有输出DtoH；L2 final flush选项为0。当前cycles含模型in-flight drain，未证明末端dirty cache全写回DRAM，也不包含可用于宣称host-visible输出传输的完整时延。源码flushL2的实际DRAM写回仍TODO，本Goal没有开启或修改它。因此DRAM写流量是本次观测边界内的服务量；容量改变可影响写回时点，完整后续flush成本UNKNOWN。

**HYPOTHESIS / 未执行后续设计：** 若需进一步研究T现实机会，先离线筛选具有高同Set独立pending overlap的真实负载及窗口，再另行申请一项精确新producer的最小真实压力验证；保留负结果，不通过继续缩Way或拉长DRAM来声称现实收益。若需硬件面积结论，另立Tag+Payload同步缩容设计、容量映射和正确性证明，再取得独立科学授权。当前没有证据需要放宽reuse/sector协议或改版T。

论文表述建议：在此统一producer的完整Vector上，Tag-only覆盖容量8→4→2MiB扫描未产生真实TagFAIL和T执行；零detach体现所测配置/负载缺少触发机会。缩容有可测的驻留/写回代价，不能把“未触发T”写成“Tag容量完全免费”或把人工CPU压力等同真实应用收益。

## 证据与恢复

七份要求交付齐全。TAG_PRESSURE_AND_PERFORMANCE_RESULTS.csv保存全部四项正负性能结果与完整raw/spec/point/archive SHA；CONTROLLED_CONFIG_MATRIX.csv含四项已接受规格和两个条件未满足、未登记的T-OFF槽。APPLICATION_ARCHIVE_AND_RESTORE_RECEIPTS.json给每项真164路径、完整SHA及两次独立原生恢复回执；在对应bundle目录运行`python3 -B RESTORE_TAGFLOW.py --destination /ABSENT_NATIVE_EXT4_PATH`仅恢复证据，不运行模型。源码恢复入口见SOURCE_RECOVERY_ENTRY_SUPPLEMENT.json；CPU/控制/分析/报告整体快照另见最终EVIDENCE_ARCHIVE_RECEIPT.json。所有Source KEEP。最终审查HEAD在提交后单独回执，不把自身commit SHA嵌入自身文件造成循环。有限ABC子任务均完成，由Main统一审阅。
