# EP-L2 Performance-First V5：最终科学结果与成本判断

本批三个独立范围A3+B2+D3共8次完整应用启动，**8/8正式接受、0次模型技术失败、0次补跑、0次退款**。全部结果完成真164完整SHA归档及每点两次独立Native完整恢复，共16次恢复。三个预算均CLOSED_COMPLETED、remaining0。调度器和元数据发布监督自然结束。原V3的8项接受/2项技术失败、V4的6项接受及原Source/Spec/raw/台账保留。

本报告的完成范围是本次授权8点。C仍是部分生产工程，不构成完整CLEAN配额资格；本批无C模型。论文、109新采集、额外Trace和NI模型均未启动。8点不是EP-L2项目累计实验上限。

## 完整应用结果

| 范围 | 完整应用点 | cycles |
|---|---|---:|
| A | FWT G32×8 S | 181827 |
| A | FWT G32×8 WV，cold过滤OFF | 178951 |
| A | FWT G32×8 WV，cold过滤ON | 180074 |
| B | Vector4M 1700，新Source F_BASELINE | 55925 |
| B | Vector4M 1700，同Source F_PRESSURE_EPOCH | 45425 |
| D | 3MM G64×8 S | 1666917 |
| D | 3MM G64×8 WV_ZERO_RO | 1662803 |
| D | 3MM G32×8 WV_ZERO_RO参考 | 1671121 |

复用已接受的同Source78、同输入、同背景3MM G32×8 S_REF=1696618，不消耗新启动。缺失的WV_REF本次实际测量，未用旧F替代。完整命令/kernel/CTA/instructions、硬件排空、Source5及模式由[不可变执行清单](EXACT_EXECUTION_MANIFEST.json)、[完整数值表](PERFORMANCE_CURRENT.json)和[最终逐项审计](FINAL_REQUIREMENT_COMPLETION_AUDIT.json)约束。FWT为18命令/16 kernel/7040 CTA/180944896 instructions；Vector为3命令/1 kernel/15625 CTA/56000000 instructions；3MM为10命令/3 kernel/3072 CTA/1813512192 instructions。所有声明均限于冻结Trace定义的完整命令序列；不把原始采集完整性或程序数值输出的UNKNOWN改写成PASS。

## B：有明确收益，来自条件准入

同一Core812、ELFa606及完整283项硬件背景下，优化F相对原始F减少10500 cycles，改善**18.7751%**。两点同时独立准入，没有基线完成/归档前置门，最终比较使用本次正式接受的新Source基线。

冻结计数表明：本输入的压力epoch激活次数为0；优化点1000000次合格读计数走激活前Native服务，RO接纳/事务均为0。原始F的RO接纳为1000000、事务250849、merge749151，detach为0。本结果支持“无压力时避免不必要的RO服务成本”，不证明活跃RO路径变快，也不把RO/M/T联合差额单独归因于T。未用旧Core862的S/W/WV结果拼接新Source对照。

成本为每slice一个控制位及现有压力比较/选择；原查询端口和完整查询周期保留，无新增CAM、队列、Payload或Bank。物理时序/PPA尚未证明。1700MHz属于服务敏感性诊断背景，不宣称真实GPU校准。后续值得准备不同访存/真实压力输入的有限匹配申请；不在本次自动增加模型。

## A：查询减少，端到端负结果

同Source7b4、ELF1f978、G32×8和283项背景下，cold过滤ON比OFF**慢1123 cycles（0.6275%）**。OFF相对同Source S改善1.5817%；ON相对S改善0.9641%。

最终64个slice累计前端查询：OFF150462、ON148843，总量减少1619（1.0760%）。没有把每kernel重复累计快照相加。冻结Source未导出逐次cold_bypasses计数，因此该总量差额不冒充精确bypass次数或纯查询周期归因。

机制仅是“生命周期从未安装过Victim”的负证明：每slice一个sticky位，首次安装后永久回退原查询，不是通用空目录oracle。保持Tag256项/slice、Payload1168、四Bank/P1及原目录/MSHR/descriptor资源，无免费额外端口或数据阵列；控制mux物理时序/PPA未证明。本批不支持推广该cold过滤作为统一性能优化，也不能认为它解决了Stencil持续保留问题。128周期串行LRU备用方案及重复已有bank-aware落点方向未进入新科学范围，负证据保留。

## D：G64×8有小幅收益，EP增量仍小

同Source78/ELF78d、850MHz、L100、FR-FCFS128及冻结资源下：

- S G64×8相对S_REF32×8：减少29701 cycles，改善**1.7506%**。
- WV G64×8相对本次WV_REF32×8：减少8318 cycles，改善**0.4977%**。
- G64×8同背景WV相对S：减少4114 cycles，改善**0.2468%**。
- G32×8参考背景WV相对S：减少25497 cycles，改善**1.5028%**。

Tag从256增加到512项/slice，逻辑Tag容量翻倍；Payload1168及四Bank/P1不增加。S和WV分别从几何扩展中获益，但G64×8上的额外EP增量较小，不能把全部几何收益算成EP机制收益，或提前认定G64×8普适最优。物理Tag存储、比较/选择和关键路径成本未以完整PPA量化。

D请求名保留PFV4_A2，但此前从未批准或消费，本次是独立新预算3，不重启旧V4。真164归档沿用准备时目录前缀，实际新cohort、UUID、Source5、Spec和归档SHA绑定均已逐项核对。

## C：部分真实生产实现，仍无模型资格

旧bf4基线及各独立后继Source分别保存，未混入A/B/D。

已完成真实有限K1/K2 READ/COMMIT、下层WB预留/提交与completion背压；必要set_done调用移出assert。后续独立Core0ab接通MISSING_SECTOR的CLEAN计数-1，Core8e93接通动态ROoff CLEAN安装+1及满配替换net0：HOLD不破坏旧row/payload/native tag，成功后一次count发布再释放/转移。取消不能退款物理READ lane。新增生产CPU检查及实际ELF banner核对闭合，旧12组/3185组合等未重复跑。K2在原有合成握手序列未显示吞吐增益，负结果保留。

DIRTY安装、promotion、其他reclaim、reader begin/retire、完整rollback/epoch cleanup、全producer公平性及单counter提交路径、真实metadata控制端口/CDC/PPA仍未完整闭合。CPU工程PASS不是应用PASS；本批C科学预算0。未来须在完整生产资格后另提新Source的匹配cap128/64/0申请。

## Host修复与原始失败留存

A先遇到旧消费者固定282计数，再暴露预提交build banner缓存。Main从规范Source7b4全树独立核832个tracked文件；142个新编对象、8个静态库及整个ELF与原消费产物逐字节一致。首次因输出basename导致GNU版本元数据不同的重现失败亦保留。限定三个已消费结果的Main签字守卫严格检查原完整banner文字、原ELF/库及重现证明，不把Source改标78，不重写raw或Spec；原43字段、22个Native/5个Host依赖、完整283、7cc/bf91数值体及全部外层检查保留。

D三点缺少compact_module_ref。Main的隔离消费实例只补已有资格的c17压缩模块引用；原282、Source/Spec/raw、数值体与PID/argv/env/maps/syscall/gzip检查均未改。全部原VALIDATION_HOLD及首次错误保留，原消费UUID直接重新审结至待归档，不重置启动、退款或补跑。兼容元数据和代码也进入每点结果归档。

后续必要流程改进：先冻结commit再构建；直接检查最终ELF实际嵌入的Core/Framework banner，不能仅看generated header；在登记前核对下游消费者需要的compact等元数据字段。上述都是具体Host契约修复，不启动大规模观测归因或历史重测。

## 执行与最终证据

8点在唯一Main动态队列中独立释放，全局EP cap10按CPU/RAM/cgroup/SSD/真164及其他owner承诺准入。旧900秒、3600秒及12/14小时仅为软参考；激活前分别冻结B2h、A8h、D72h有限安全上限，运行中未热改。所有模型自然exit0，没有因旧软参考强制中断。两类消费端工程HOLD已按明确补充审结，未伪装为从未发生。

[最终逐项审计](FINAL_REQUIREMENT_COMPLETION_AUDIT.json)核对8个不同UUID、2+3+3预算、每点完整实际配置/应用人口、硬件排空、实际域/CPU/argv/环境、归档正文和全部成员SHA、两次不同Native目标完整恢复、监督自然结束及原47条EP请求逐字节保持。Source KEEP，释放0。临时恢复工作集按原受验证流程在验证后释放，科学源与归档保留。

应用NI未测、B0/M0a未证明边界、物理PPA和程序数值输出UNKNOWN均保持。没有新增NI、完整GPU校准、109采集、Trace或论文编辑。后续科学模型仍需独立准确授权。

审计与统一报告也保存至真164，入口见FINAL_CLOSEOUT_TRUE164_RECEIPT.json。每点原归档与恢复回执在PERFORMANCE_CURRENT.json和最终审计中保留精确路径/SHA。
