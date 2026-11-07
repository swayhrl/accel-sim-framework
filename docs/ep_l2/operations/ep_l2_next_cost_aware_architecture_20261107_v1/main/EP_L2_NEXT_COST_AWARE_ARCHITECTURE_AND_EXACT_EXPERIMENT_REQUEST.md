# EP-L2 下一阶段成本感知架构与精确实验申请

以UMT1 authority eae40596cb9a550785a50a3d64617686a6daa160为基点。本轮新增完整应用仿真 **0**、预算消费 **0**、新增正式dispatcher **0**；旧模型、raw、失败、验收和Source保留。

## 首选Victim结构

保留原Base128及mandatory/WAD128，增加128项只容纳optional CLEAN的metadata。Base淘汰CLEAN时，将原Payload handle转存到扩展段，不增加或复制Data，不将dirty/WB责任挪入扩展段。固定G32×8、每slice Data1168、四Bank/P1、descriptor512、Line-MSHR128、per-address32。

查询复用一个128项地址比较结构：Base查1周期，真实miss后扩展段再1周期。另增一个有限indexed Ext读视图和一个更新lane，合并有明确row/UID及fanout上限，其他竞争等待。Base选择及同Bank回收收费2周期，列入128×101位tap、Bank比较、127个64位age比较及winner mux。Ext只检查固定RR目标并付费重核，不提供免费LRU扫描。

额外row字段保守计128×460=58,880逻辑位/slice（7,360字节；64slice共460KiB），另计控制状态、比较器和读写端口。80B C++ entry不是物理面积；物理PPA、关键路径、最高频率UNKNOWN，不宣称比扩Tag更便宜。

既有Stencil/GEMM/3MM的真实V服务和“目录接近或达到上限、Data仍空闲”的终态支持机会假设。终态不是运行峰值、满目录发生率、错误淘汰率或预期加速比。收益仍须新Source匹配完整应用测量。

最终A Core：3d3887bb2e8d5073d13b0792ff9116834e89fe2f；Framework：9dd1ee57a83d83b56b7874bc7c716185ab52c8f7；ELF SHA：9db48c06ca64e441b5824071f52e0aa0be50374045fbdcef6cdf5d4469182f86。

| extension | 角色 |
|---|---|
| 0 | 原Base128资源和时序的新Source基线 |
| 1 | 真实两段查询与扩展硬件，保留关闭 |
| 2 | 与1同硬件，允许CLEAN保留 |

1→2隔离同扩展硬件下的保留收益；0→1衡量迁移开销；0→2衡量含metadata资源变化的净效果。不能把0→2称为所有硬件资源相同的纯策略比较。

生产CPU覆盖256个Base/Ext唯一owner与symbolic sector标签、跨阶段Base创建后的付费重查、Bank292满载前进性、非RR原子/写/缺失sector、ICNT拒绝、reader lease、epoch耗尽和内部WB排空。新增失效ticket活锁及提前busy=false问题已修，原失败保留。Main独立复放关键实际partition用例。8份完整283项parser/constructor映射逐字段匹配；extension0与接受Source78的有限生产CPU轨迹一致。工程PASS不是应用性能、数值oracle、通用NI或所有组合资格。 extension1/2限Tag≤512、CLEAN扩展和冻结的assertion-enabled构建；RO、runtime flush、目录已填充后的Host prefill未资格。

见 [A工程](../agent_a/README.md)、[成本](../agent_a/FINAL_COST_AND_QUALIFICATION.json)、[Main复放](MAIN_INDEPENDENT_A_PRODUCTION_REPLAY.json)。

## RO收敛

| 背景 | 原始F | pressure_epoch | 改善 | 激活slice |
|---|---:|---:|---:|---:|
| Vector4M/1700MHz | 55,925 | 45,425 | 18.7751% | 0/64 |
| Conv/850MHz | 335,088 | 333,789 | 0.3877% | 61/64 |
| Scan/850MHz | 2,224,142 | 2,212,128 | 0.5402% | 4/64 |

Vector体现无压力时回避开销，不证明压力下RO收益。Conv/Scan确有激活，但端到端改善较小。Scan查询减少约95.82%不等于关键路径缩短95.82%。不同频率不合并平均。

Conv line-full/Bank等待增加、duplicate=1及事件级原因UNKNOWN均保留。issued字节不称完成带宽，重叠等待不求和当关键路径，Victim响应不称避免DRAM。本轮不增加阈值、频率或输入扫描，RO申请0。见 [小型跨输入总结](../agent_b/RO_STRATEGY_CONVERGENCE.md)。

## CLEAN生产协议

C独立Core40a815dba41a690d2c16a377492fd246a92d5779，配套Framework d5bf17360d88e058ca3e048651a49fc947540d81，没有与A合并。

K1优先，K2仅有限读lane比较；六个depth1注册head共享一条计数提交路径。入口1+READ1+COMMIT1，CLEAN净0替换仍收费，取消不退READ。K2不声称任意双非零delta合并，陈旧count重核、第二次写等待。

真实接线覆盖CLEAN、DIRTY与真实WB UID原子发布、lower enqueue前预留、completion/credit释放、clean/dirty promotion、reader begin/退役/ICNT拒绝、pre-Native rollback及终态cleanup。18/18实际生产CPU通过。Main独立复放3个关键cache/partition用例，并新生成生产事件轨迹，与新Python V2的16个快照一致；未把旧Python模型称作生产实现。

支持initial HtoD后一个或多个kernel、跨kernel保留、after-commandlist真实L2 tick清理。after-kernel memcpy、per-kernel flush提前拒绝；RO/NI/任意组合未资格。128行清理包括EMPTY行，最低384 L2 ticks；全目录选择也最低384 ticks，另加修改。这是保守正确性/成本负参考，不是性能优化，不恢复旧串行LRU科学方向。

C本轮申请0。后续先解决选择成本及Source-specific完整Host/consumer资格，再考虑cap128/64/0；K2不预设吞吐收益。物理CDC/PPA仍UNKNOWN。见 [边界](../agent_c/PRODUCTION_BOUNDARY_AND_ACCEPTANCE_V2.json)、[Main复放](MAIN_INDEPENDENT_C_PRODUCTION_REPLAY.json)、[新合同复放](MAIN_INDEPENDENT_C_NEW_CONTRACT_REPLAY.json)。

## 下一批建议：两个独立范围，5次待授权

精确Source5、输入SHA、ordered commands、283项配置、模式、资源和consumer差分以 [JSON申请](../agent_d/FINAL_EXACT_EXPERIMENT_REQUEST.json) 及 [MD申请](../agent_d/FINAL_EXACT_EXPERIMENT_REQUEST.md) 为准。

| 优先级 | 输入/850MHz/L100/G32×8/WV_ZERO_RO | 点 | 科学信息 |
|---|---|---|---|
| 1 | GEMM | extension0/1/2，共3次 | 迁移开销、同硬件保留增量、净绝对cycles |
| 2 | Stencil | extension0/2，共2次 | 持续复用、跨kernel保留的净收益 |

新Source基线必须新测，不借旧ELF配对。旧自然墙钟GEMM WV约1.257h、Stencil约3.714h/点，仅作排期背景，不保证新结构时长；CPU busy秒UNKNOWN。各点独立释放，可三短两长并行，无跨族归档/完成门；cap10按CPU/RAM/cgroup/SSD/真164/其他owner承诺动态准入。未来正式激活前冻结Host/Native43字段、依赖pin、boot/mount、Spec和安全hard wall，运行中不改。

3MM作为下一长负载备选，旧G32 WV_REF=1,671,121已接受，不再称缺失或以F替代；旧三点约3.42–3.88h/点。本次不增加3MM启动。Transpose保留低V机会负对照备选，不重复旧FWT cold/容量实验。Vector不再作为唯一开发输入。保留103输入/槽位=96内容组+7未决、35代表输入、42程序/槽位的不同人口；D的290接受context/28输入不是103个独立workload，也不是EP全历史计数。

未来每点仍需完整命令序列、kernel/CTA/instructions、排空、真164全SHA及两次独立Native恢复。Base/Ext实际服务分列并与全局Payload role守恒，Ext query不是response。评价完整cycles、真实成本和跨输入正负结果，不以机制次数定义成功。

## Main关闭边界

四项交付是工程与精确申请准备。A/C独立Source分别接受，未拼接成联合资格；未登记或消费新科学范围，未安装dispatcher，未启动GPU/Trace/NI/论文或完整应用。

旧52个EP请求行不变；共享registry的DTC进展由其owner保留，全局预算变化不代表本Goal消费。Source KEEP、释放0。原失败、未选R1假设、应用NI/数值输出、PPA/时序/CDC缺口按真实范围保留。

若新Victim无净收益或成本不合理，保留负结果并停止无明确新机会的扩容，不为堆次数追加配置。

**待审批A：3+2=5次。B=0，C=0。工程PASS不代替正式科学授权。**
