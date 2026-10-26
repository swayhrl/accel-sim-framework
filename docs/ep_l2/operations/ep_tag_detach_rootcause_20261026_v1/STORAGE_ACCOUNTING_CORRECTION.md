# 174 / 164 存储口径修正（2026-10-26）

用户明确要求：大资产默认放真164；若显著影响速度，报告具体影响；空间不足由用户清理。该偏好已写入本审查项目根 [AGENTS.md](../../../../AGENTS.md)。

## 运行数据放在哪里

- Vector trace的已资格成员在真164：`/home/shared/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261023_native_v2_inputs/EP_VECTORADD_S/tree`，通过已验证的174-new只读映射使用。两个成员合计103535960B，本次没有复制到174。
- 174只承担本次运行的热输出和必要短期工作集。既有r5完整结果44文件合计15679278B（约14.95MiB）：raw8593124B、strace1570349B、其余终态/元数据等。源结果已按既定规则归档164；不因归档成功擅自删除174源。
- E1的1.25GiB是沿用旧上限：engineering256MiB、staging256MiB、results384MiB、restore384MiB；不是预计会产生1.25GiB，更不是需要迁入大trace。
- 只有明显I/O性能损失才考虑有界local cache，并先报告测量和容量需求。当前没有新的164读速实测，不声称必须缓存。

## 上一轮45.75GiB是什么意思

它来自旧EP保守算式：DTC35GiB池上限＋repair1.5GiB＋EP1.25GiB＋7GiB floor＋1GiB其它headroom。它不是EP实验自身的空间需求。

复核发现，DTC35GiB在write_reservation_history中明确是并发写入池ceiling。当前DTC `tools/sweep_native.py:430–464`实际按已承诺的剩余结果增长和native restore核算，并注明已落盘字节已反映在df，未启动且未claim的队列可等待，不能全部重复预留。将该池上限直接解释成“还必须新增35GiB”过于保守。因此，上一轮“必须再清出12.12GiB”的确定性结论撤回。

只读核对快照（2026-10-26 13:29 Asia/Shanghai）：

|项目|值|
|---|---:|
|DTC登记池ceiling|35GiB|
|观察到的已知剩余写入/restore，含其1GiB自身headroom|25141022575B，约23.414GiB|
|未归档或已claim的case数|23|
|df可用|36094922752B，约33.616GiB|
|保留其余旧边界后的示意阈值|36683747183B，约34.164GiB|
|该示意快照差额|588824431B，约0.548GiB|

快照前后registry与dispatch claims哈希未变。这个只读重算没有修改DTC reservation或controller；也不是最终原子启动准入：输出还在增长、其它任务还会按自己的门禁接纳新case，必须绑定当前owner/claim与剩余承诺后重新判断。不能把0.548GiB当成永久固定缺口，更不能再要求用户按12GiB清理。

当前状态应读作 **STAGED_PENDING_RESOURCE_RECONCILIATION**，而非已证明物理磁盘无法容纳E1。旧 [PRELAUNCH_CHECK.json](DRAM935_EXECUTION_PACKAGE/PRELAUNCH_CHECK.json) 保留为旧算式的历史回执；准备工具已明确标注其legacy全额池上限估算不构成最终准入。

## 不变的执行边界

目前仍无E1模型启动、预算登记/消费、共享入口安装或新native help。新cohort的sole-entry接入、fresh资格和注册仍待按精确资源口径完成；不能因为纠正了过度预留就直接调用ELF。用户负责清理，不自行删除、改其它任务预留、干预SM70迁移或GPU109采集。
