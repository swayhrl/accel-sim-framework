# 跨工作负载 T 机会与事件时间线：最终科学报告

Goal：`EP_L2_MULTIWORKLOAD_TAG_OPPORTUNITY_AND_EVENT_TIMELINE_V1`。

**决定：维持现有 T 协议保护；下一轮优先做精确 Conv 输入的当前 Core RO 资格重绑，再以独立授权准备同几何、同 ELF 的 F−T/F 最小因果配对。不自动扩大到20/全部候选，不加延迟，不再缩 Tag。** 本轮发现了真实的同 Set 满路 NEW 压力，但还没有证明当前 F 下同一时刻存在可 detach 的 RO，亦没有 T 独立 cycles 收益。

## 本轮执行人口

冻结矩阵有11个程序、12个端点（Vector含Observer OFF/ON，两端点T均开启），实际启动11次；9个端点、8个不同程序正式接受。FWT启动前因已证明的统计格式容量下界封存1次未用额度；BICG与DWT保留为两种不同的未接受结果。全部已花启动不退还、不重试。

|程序/端点|模式|最终分类|cycles|事件峰/末tick峰|独立NEW∧R8|预检Tag失败检查|actual access TagFAIL|detach（T适用时）|
|---|---|---|---:|---|---:|---:|---:|---|
|vectorAdd ET-OFF|F|ACCEPTED_TRACE_DEFINED|77237|7/6|0|0|0|0|
|vectorAdd ET-ON|F|ACCEPTED_TRACE_DEFINED|77237|7/6|0|0|0|0|
|convolutionSeparable|S|ACCEPTED_TRACE_DEFINED|331234|8/8|289|42717|0|NOT_APPLICABLE|
|fastWalshTransform|S|PRELAUNCH_PROVEN_FORMAT_CAPACITY_HOLD_NOT_RUN|UNKNOWN|UNKNOWN|UNKNOWN|UNKNOWN|UNKNOWN|NOT_APPLICABLE|
|cfd|S|ACCEPTED_TRACE_DEFINED|84851|8/8|1|11|0|NOT_APPLICABLE|
|dwt2d|S|INVALIDATED_AFTER_C3_RESOURCE_CAP|UNKNOWN|UNKNOWN|UNKNOWN|UNKNOWN|UNKNOWN|NOT_APPLICABLE|
|gaussian|S|ACCEPTED_TRACE_DEFINED|33800|0/0|0|0|0|NOT_APPLICABLE|
|sad|S|ACCEPTED_TRACE_DEFINED|120840|6/5|0|0|0|NOT_APPLICABLE|
|sgemm|S|ACCEPTED_TRACE_DEFINED|353921|5/5|0|0|0|NOT_APPLICABLE|
|ATAX|S|ACCEPTED_TRACE_DEFINED|3001729|3/3|0|0|0|NOT_APPLICABLE|
|BICG|S|UNACCEPTED_FORENSIC_CLOSED_NO_RETRY|UNKNOWN|UNKNOWN|UNKNOWN|UNKNOWN|UNKNOWN|NOT_APPLICABLE|
|GESUMMV|S|ACCEPTED_TRACE_DEFINED|3299323|4/4|0|0|0|NOT_APPLICABLE|

所有新结果使用同一执行 Core `78f4b59e865b136eede74df74c44c210f5b4ca04`、Framework `9dd1ee57a83d83b56b7874bc7c716185ab52c8f7` 和 ELF `78d4e96bb79c776e27146bcf168d7c70cf3897ef9cb84d837d8974fec4c91b8a`，固定64 Slice、32 Set×8 Way、`dram_latency=100`。这是本轮声明条件，不能称原始 GPU 默认配置的收益。审查分支 HEAD 是文档身份，不是执行 Framework 身份。

## 按证据强度解释结果

**PROVEN — 当前计数人口必须修正解释。** Conv有289个独立 NEW 在同 Set 已8路 RESERVED 时到达；42,717次 head 检查（包含重复观察）直接得到生产预检的 Tag-array `RESERVATION_FAIL`，全部在 Frontend 被拒，actual `ft_access` 的初始 probe 因而没有执行这些请求。CFD对应1个独立 NEW、11次预检失败。两者 actual-access TagFAIL 计数0不能证明没有 Tag 压力。独立请求数与等待检查数不混用；这是实际联合计数，不是边际乘积。代码和行号见 `CONV_S_PRESSURE_TO_PRODUCTION_AUDIT.md`。

**PROVEN — 当前 F 的零触发与 S 的不适用是不同结果。** 只有 Vector完成本轮当前 Source/输入的 F RO 资格。其有250,087个 RO事务、749,913次merge，事件峰7/8、末tick峰6/8；独立 NEW 到来前的 RESERVED 最高为6，没有 NEW∧R8，也没有实际 TagFAIL、relieve 或 detach。其余正式 S 结果的 T/RO为 NOT_APPLICABLE，不能补0并概括成这些应用的真实 T 零触发。

**PROVEN — Conv不存在“历史无正RO证书或无RO事务”的结论。** 当前精确输入与历史 whole-commandlist 的两个 kernel body和commandlist完全匹配。历史证书覆盖294,912条128B line，旧F实际 RO admit1,251,551、事务371,495。旧main61的 T/M controls无cycles差异仅限旧谱系/几何。历史 RO 正覆盖与本轮 S 的满路压力不能拼成当前 F 的同 Set/同时间 eligibility；当前联合和收益仍 UNKNOWN。CFD/DWT亦有历史正证书和非零事务链；SGEMM历史事务0与resident-hit相容，不是没有RO数据。见历史资格小报告与三输入CSV。

**PROVEN — 新事件快照记录到了真实等待。** Conv第4槽捕获 UID156198在 CORE6903–7108间206次同 UID/R8/前端拒绝联合，等待结束右censored；没有伪造接受或 detach。Vector130个完整同UID固定延迟队列片段均为deadline−enqueue=100 CORE ticks，deadline后实际MC push为1或2 CORE ticks。后者是所选窗口事实，不是全应用队列分布或纯DRAM/Bank等待。

**PROVEN / LIKELY边界 — 多工作负载的压力差异不能只看峰。** SGEMM的NEW分布主要在R0，事件/末tick峰5/5；GESUMMV峰4/4而独立NEW仅出现在R0–R2，单kernel只有16CTA，在80SM模型下同时activeSM≤16是可证的静态上界。Gaussian确有L1/L2/ICNT访问，L2为31次命中、0miss，不能称无访存；这与配置开启memcpy预热和极小输入相容，但未做关预热对照，单因归因仍UNKNOWN。ATAX两个kernel各16CTA，事件/末tick峰3/3，独立NEW同样仅在R0–R2。SAD等最终分布见统一CSV。低压力、网格并行度、命中/合并与各级等待共同限制T机会是LIKELY；没有受控对照就不能把任一停顿计数排序成独占GPU瓶颈或cycles损失。

**UNKNOWN — T的端到端价值。** Conv的S模式1,503,281个独立NEW中有289个在R8状态首次观测到；其F背景可能改变合并、RO reuse_seen和请求到达顺序。当前没有同Core/同输入/同硬件的F−T/F结果，不能从完整机制收益、历史控制或CPU构造性detach推出T加速。不得据此放松reuse/sector/generation保护。

## Observer：实际验证与未达边界

默认OFF的被动通知不增加Tag probe、目录查询、bank调度或队列操作。固定环与4个有界快照输出一次，离线生成UID HTML/VCD；VCD使用明确的合成ordinal轴，真实CORE/L2/DRAM计数是独立信号。有限快照有触发偏置、左右censor和未保留事件，不冒充全路径追踪。

生产CPU fixture验证满way真实Tag失败、T-ON detach/T-OFF阻塞、sector合并/乱序返回、旧generation/payload隔离、背压、重复preview及完整drain；12次生产fixture执行形成6对OFF/ON。独立header/decoder/converter安全控制另有明确记录。真实新ELF的Vector Observer OFF/ON（两次T均开启）在cycles、instructions、CTA、完整C3协议投影、LIFE wire、DRAM命令与所检原生统计一致，实际host耗时本次增加1.0911%。这只是一次配对，计时包含legacy seal/proof阶段，不是普适≤5%证明。

固定对象+声明aux为3,868,584B，低于8MiB；已接受应用的压缩事件与wire都低于16MiB，精确字节见最终ETON表。然而ELF新增约20MB只读初始化常量；全实现存储不能只用3.69MiB概括，全进程新增resident RSS的普适8MiB上限未知。该限制保留；优化仅为未执行设计，未更换冻结ELF。离线生成的HTML/VCD大小不等于应用压缩事件大小。

## 三个工程负结果与恢复

FWT：旧R4/R5等格式随kernel数增长，16kernel的必要raw下界已超80MiB在线界限，因此未启动；不是T零触发。

BICG：运行中的资源检查受GES已生成元数据仍按未来16MiB计费的错误影响，被监控终止；当时物理SSD/RAM足够。其consumed1保留，按未接受forensic归档，实际两次恢复，无重试/退款。GES的剩余claim之后按实际尚需写入下调为160KiB上界，实际增长96KiB；硬cap、Source、配置和资源模块没有放宽。

DWT：自然完成并保留C3窄人口诊断点（178,315 cycles、148,684,429 instructions、4,654 CTA、10kernel），但格式化bundle落盘使原目录实占103,452,672B，超过冻结96MiB的100,663,296B。原compact JSON预检未界定pretty输出。本轮最终NOT_ACCEPTED_RESOURCE_ENVELOPE，原文件不改；C3点仅保存为preserved引用，已退出正式accepted人口。已知诊断数值与NEW分布单独保留于 `UNACCEPTED_DWT_C3_DIAGNOSTIC_ONLY.json`，不抹除也不作正式accepted性能比较。独立工程parcel归档与两恢复、逐原文件全SHA/元数据核验不使原包络合格；另已完成两份原文件树的独立工程恢复，实际各103,440,384B，上界按清单推导为103,505,920B；逐文件SHA与元数据均通过，仍不改变原科学包络失格。不能用工程恢复收据伪造原科学96MiB PASS。

真164存放Trace输入和归档；174仅保留Source/build、必要hot与有界恢复。独立Source/runtime包、各应用、负结果、全分析/事件视图与发布收尾包的manifest/archive SHA和恢复入口见 `RECOVERY_AND_SHA_INDEX.json`。SOURCE_KEEP，未清理外部资产、未改DTC任务、未合并accepted EP-MAIN Core。

## 唯一后续科学建议

先对精确Conv的已存在正证书做当前Source/模式的CPU loader和配置资格重绑，再申请新的精确预算，准备同ELF、同64×32×8、同dram_latency100的F−T/F两个点；只有资格全部成立才能复用本轮S参考。若更换ELF，则重建完整匹配参考，不能跨binary拼接。比较NEW∧R8∧eligible、preview→actual access→relieve→detach→新接受、旧RO返回/退休、queue与DRAM字节及完整cycles。成功detach仍不以加速为验收条件。

不自动启动该候选，不扩大至20/全部负载。CFD仅是较弱的第二候选，优先级低于先闭合Conv联合证据。并行工程候选包括消除observer只读初始化重复、按真实序列化字节界定输出、及时更新剩余postrun写入、避免仅因别的完成任务的元数据估计错误终止已获准模型；这些都需要独立资格，不改写本轮负结果。

## 可复核交付

工作负载去重/排除/资格CSV；`WORKLOAD_PRESSURE_AND_PERFORMANCE.csv`；`NEW_RESERVED_AND_TIME_OCCUPANCY_DISTRIBUTIONS.csv`；`TAG_PREVIEW_TO_COMMIT_FUNNEL.csv`；带人口口径的访存统计CSV；Source与CPU/实际NI报告；Conv/Vector典型事件、小CSV和离线工具；真实164 archive与恢复索引。原始事件、大视图及CPU工程证据在真164，GitHub只存小型汇总与工具。
