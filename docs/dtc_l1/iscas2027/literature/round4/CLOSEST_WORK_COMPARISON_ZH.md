# R4｜最接近工作的状态对照

2026-10-16。结构比较不代替同平台性能。未披露细节不等于没有该能力。

| 工作 | 保存/查找对象 | 响应与释放 | DTC需说明的区别 |
|---|---|---|---|
| Kroft，1981（1998重印） | 请求地址、cache-buffer位置、请求者信息与在途匹配 | 带标识返回；obsolete等状态避免旧数据错误更新 | 返回身份已有先例，不能作为独有创新；DTC重点是消费者取数前保留实际数据及映射/引用共同回收 |
| NuRAPID/V-Way | Tag关联与数据位置的间接映射 | 面向距离、替换、相联度组织 | 不将一般Tag/Data解耦作为新发现，不从目标不同推断瞬态缺失 |
| Hierarchical MHA，2006 | per-bank及shared MSHR，过滤共享访问；讨论LSQ中消费者 | 容量与访问带宽协同；LSQ搜索、退休和时序制约替代方案 | 不能仅说消费者搬到PIB就消除代价；CPU LSQ并非GPU PIB |
| DL-MSHR，2019 | 动态slot-set池分给独立缺失或同址消费者 | 返回并转发后拆链回收，数据仍可cache命中 | 等待槽位弹性与实际数据持续保留是不同对象 |
| MSHR-rich，2019 | BRAM型可扩展miss state，作者摘要及实现确认 | 正文未取得，不填详细流程 | 只用高层可扩展组织事实，不基于MiCache二手介绍声称已读全文 |
| MiCache，2024 | cache-data与MSHR-subentry共享BRAM项，另有stash | 响应转换BRAM记录；f=1子项溢出旧记录停止匹配新请求但匹配响应 | 新请求不可见的旧状态已有先例；DTC以PIB存指令、pool存数据，消费者取数后释放引用 |
| Volta/Accel-Sim | cache/coalescing与streaming L1提高miss throughput | 未公开与DTC相同的完整状态字段 | reservation基线不是所有现代GPU通则；工具引用不认证custom配置 |

## 来源定位

Kroft的Organization/Operation，重印pp.195–198；Hierarchical MHA §2.4与§§3–4；DL-MSHR用户PDF第6–7页§4.3–4.4；MiCache用户PDF第6–7页§4.3–4.4；Volta官方白皮书印刷pp.17–18；Accel-Sim §IV及§VI。链接和读取深度见READING_REGISTER.tsv及ROUND4_COMPLETION_REPORT_ZH.md。

## 三条比较线

1. 映射和放置：NuRAPID/V-Way/Decoupled L1D构成先例，DTC应说明旧消费者与数据保留的关联。
2. 缺失与消费者：Kroft/Hierarchical MHA/DL-MSHR/MSHR-rich/MiCache说明已有多种查找、存放和释放方案，不能统一简化成小固定MSHR。
3. 请求流和服务：MRPB重排/旁路，CCWS发射资格，MeDiC shared-L2与DRAM协调，Poise参与/分配warp选择；不同位置不自动产生可叠加收益。

本文未对上述全部方案实施同平台复现，也不从表格直接推断性能排名。硬件成本和局部服务核查继续作为独立实质问题，文献补齐不会自动关闭。
