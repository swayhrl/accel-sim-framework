# UMT1：Conv与Scan压力感知RO的最终科学结果

本批授权4次，实际消费4次，**4/4正式接受、0模型技术失败、0重跑、0退款**。两个独立预算均CLOSED_COMPLETED、remaining0。每点完成真164完整SHA归档及两次独立Native完整恢复，共8次。Source KEEP，科学源释放0。

四模型在2026-11-06独立并行启动；Conv约69分钟/点，Scan约6.36小时/点，全部自然exit0。Scan昨日自然完成后，归档被一项未审查的新DTC Native入口阻塞；2026-11-07本次Main检查完成精确插入审查、原结果验证与归档。等待期间没有模型继续运行，不把这段收尾等待算作仿真墙钟。

## 同Source完整应用性能

Source均为Core812 / ELFa606，DRAM850MHz、L100、G32×8、FR-FCFS128、完整283项。每对仅pressure_epoch 0/1不同。旧Source78 cycles不进入新Source配对。

| 输入 | F_BASELINE cycles | F_PRESSURE_EPOCH cycles | 减少cycles | 改善 |
|---|---:|---:|---:|---:|
| Conv | 335088 | 333789 | 1299 | 0.387659% |
| Scan | 2224142 | 2212128 | 12014 | 0.540163% |

完整人口：Conv为4条命令、2 kernel、27648 CTA、714547200 instructions；Scan为34条命令、33 kernel、166608 CTA、1963460720 instructions。声明限于各自冻结输入的完整ordered commandlist，不将采集完整性或程序数值输出UNKNOWN改写为PASS。

## 策略实际激活

- Conv优化点：61次激活，61/64个RO runtime slice；未激活slice为3、42、63。激活前Native接纳229273。
- Scan优化点：4次激活，slice为25、27、36、62；激活前Native接纳13928689。
- 基线pressure开关关闭，其激活0应标POLICY_DISABLED，不能冒充策略开启时NO_ACTIVATION。

这两项都是真实ACTIVATED结果，扩展了此前Vector4M“开启策略但未激活”的开销对照。它们证明联合触发可达，但完整性能收益均小于1%，不支持把Vector的18.78%开销改善推广成压力输入的普遍收益。

激活证明该slice在首次激活时同时满足：timed frontend、directory-ready、合格RO候选、非HIT，以及RESERVATION_FAIL或普通Line-MSHR达到128。统计不导出全部联合事件次数或分母，不能由边际峰值还原它们。

## 生产RO计数

以下均为每slice最终累计记录，仅取一次；transaction不是独立地址人口。

| 输入/模式 | RO接纳 | transaction | merge | duplicate原计数 | detach |
|---|---:|---:|---:|---:|---:|
| Conv baseline | 1322070 | 376204 | 945866 | 1 | 14 |
| Conv pressure | 1111555 | 306537 | 805018 | 1 | 15 |
| Scan baseline | 14536577 | 3721306 | 10815271 | 0 | 0 |
| Scan pressure | 607828 | 156327 | 451501 | 0 | 0 |

RO响应数与接纳数闭合，接纳=transaction+merge。激活前Native接纳与RO接纳并非完整互斥分区：激活后仍有Native命中等路径，不强行用它们凑成所有合格候选的分母。

Conv的duplicate1原样保留，不标0。只读生产源码核对表明，该计数比较另一个live RO entry的issued mask，没有扣除ready位；而真正pending逻辑另用issued&~ready。因此1本身不能证明同时在途的DRAM重复请求，也不能据此认定实际事件一定只是ready/draining重叠。事件级原因仍UNKNOWN；完整定义及源SHA见DUPLICATE_COUNTER_SEMANTICS_REVIEW.json。本批不修改计数、Source或旧结果，不把验收扩大为通用零重复/全部程序数值正确性资格。

## 资源压力与真实服务等待

| 输入/模式 | 普通Line峰值 | 普通Line-full阻塞事件 | Tag-all-reserved阻塞事件 | RO查询数/查询等待观察 |
|---|---:|---:|---:|---:|
| Conv baseline | 128 | 2986 | 37279 | 1322161 |
| Conv pressure | 128 | 5649 | 30108 | 1111583 |
| Scan baseline | 128 | 4677 | 1090 | 14536577 |
| Scan pressure | 128 | 938 | 715 | 607828 |

Conv中普通Line-full事件增加，但完整应用略快；不能用单一受阻计数定义优化优劣。Scan的大幅RO查询减少只带来0.54%端到端改善，说明查询数量不是应用关键路径周期的替代物。

RO专属TAG_SET_ALL_PENDING head等待：Conv基线101个独立head请求、22656 first-to-accept累计周期；优化113个、18600累计周期。两项Scan为0。RO的Line-MSHR等待字段为0是在M bypass开启的该观察范围内，不否认B0报告的普通Native Line阻塞。

这些等待按各自边界和类别解释，互相重叠，不能相加成应用独占stall或关键路径cycles。issued lower-read bytes不是已完成DRAM实际带宽。各slice峰值不相加称同时GPU峰值。所有64-slice原记录、active slice及head原因见CLOSED_COUNTERS。

成本仍为每slice一个压力epoch控制位及现有压力比较/选择；Tag/Payload/Bank/目录、查询端口和原有限查询周期不增加或免费删除。物理PPA与关键路径未证明。

## 统一分类获得的反馈

Conv和Scan均由已有真实普通MSHR压力选出，实际激活得到验证；激活覆盖61/64与4/64又说明“发生过普通压力”不能预测所有slice都会触发RO。性能改善应单独作为验证目标。

Vector继续保留为无压力开销负对照，而不作为唯一开发输入。对后续结构优化，值得区分Native与RO服务选择、实际查询/完成背压及压力覆盖；不按merge比例或机制计数堆叠优劣。本批未追加配置或新模型，也不把这两项有意选出的输入称为盲测总体。

Victim方向既有Stencil/GEMM/3MM证据及CLEAN工程边界不因本批结果改变；没有自动启动那些范围。

## Scan收尾HOLD及严格修复

原守卫只认识已冻结的有限插入语法。运行期间新增DTC_ORACLE_INITIAL8专属路由，导致原两Scan在模型结束后进入ACCEPT_ARCHIVE_START_HOLD；原EXECUTOR_FINISHED/ATTENTION和所有失败日志保留。

Main核实共享Native当前字节严格等于“原header + 单一DTC有限块 + 原baseline其余全部字节”。32个DTC cohort均是明确字面量，与EP四cohort无交集；动作、handler和环境前缀固定，注册名单与用户科学authority吻合。增加命令、改变旧体、通配符或EP遮蔽的反例被拒绝。

审查只重新封存本次已消费、已结束的Scan自身postrun路由元数据，保留原launch baseline及闭合结果UUID/Spec/raw。原monitor、Core、ELF、Source、数学、43字段、22 Native和5 Host依赖不变；共享Native本体和其他owner台账未改。未知后续路由变化仍fail-closed；remaining0及原消费记录不授予任何重启权限。

见closed_scan_insert_review_20261107_v1/MAIN_INSERT_ONLY_REVIEW.json与MAIN_APPLY_RECEIPT.json。Main随后用原Native accept连续完成两份原结果的验证、真164归档和各两次恢复，没有重跑模型或修改历史失败。

## 完成证据和保留边界

FINAL_REQUIREMENT_COMPLETION_AUDIT.json逐点核对：同一Spec/Source/UUID，完整人口、硬件排空、自然exit0；真164整包及全部成员SHA；8次不同目标完整Native恢复；四模型和原Main调度/发布监督均结束；两个budget关闭、claim及reserved writes为0。原50条EP请求全部字段保持不变，其他owner的合法后续活动不被重置。

PERFORMANCE_CURRENT.json/md为当前科学结果。原RESULTS_CURRENT.json是原dispatcher在HOLD时的历史快照，最终状态以Native账本、FINAL_SCOPE_CLOSURE和本审计为准。METADATA_WATCH_ATTENTION保留历史，不再代表未解决故障。

应用NI未测、物理PPA未证明、程序数值输出UNKNOWN继续保留。本批科学启动4、技术失败0、重试0、退款0。成果与路由补充证据另存真164小型最终归档；原每点科学归档及源均保留。
