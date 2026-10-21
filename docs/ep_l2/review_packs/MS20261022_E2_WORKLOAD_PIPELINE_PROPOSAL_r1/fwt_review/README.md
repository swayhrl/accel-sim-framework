# FWT main61 恢复独立审查

结论：READY_FOR_APPROVAL；未授权启动。原 FWT S/F 专属资格仍为 INDEPENDENTLY_QUALIFIED，18 项门、正式 producer/build、17-native 收据及 terminal parser 小文件 SHA 均一致。main61 和 archive 现文件完整 SHA 一致，Core/Framework/Vendor 冻结 checkout 无 tracked 修改。20 个输入资产（19 kernel+命令表）的设备/inode/nlink/大小/mtime 与上次完整身份审查一致；本轮只重新哈希小命令表与配置/oracle，不扫描 trace 正文。

恢复采用原 main61 的同 binary 新 S/F，19 kernel、791,609,344 条指令、finite1168/物理P1，F 的 W/V/T/M 保持 1。有效空覆盖证书的 0 certified RO lines 不等于模拟器资格失败，也不支持正 RO/Tag detach 压力论证。该对恢复原 MAIN cohort，不能混入新93a9容量五对诊断。

旧 E011/E012 继续 INCOMPLETE 且不退费。退出状态丢失的已证实根因是 supervisor 生命周期及 orphan child 无法由后继进程 wait，原 session143 的发信方未知，不能推出原生exit0、模拟器错误或OOM。现有8项有界控制、之后同main61真实 wait4 exit0 证据覆盖已知工程缺陷；不能恢复旧退出状态，也不保证主机整体断电下仍有收据。

预算：建议仅批准2个新实际启动，每端384MiB，两端768MiB，另留collector/metadata；预计每端123–150MB。S80–110分钟、F85–120分钟；可同时准入时约90–125分钟，单路约165–230分钟，均为旧INCOMPLETE时长先验而非新测量。保留旧spec10800秒端点timeout，不恢复已取消的全局启动/intake截止。

关键缺口：当前actual46，原32槽位全部已占用；原seven_workload_common_S_F14/14，Btree F已被Vector重试替换，旧提案Btree双donor不可用。当前limits_policy对具体spec仍严格只准十个V3_CAPACITY条件，global maximum=null不会让FWT自动可执行。需要用户明确批准新的有限FWT/SGEMM四条件scope、独立批次计费，以及原中央流程中的最小受控scope适配，原32 reservations与旧十条容量条件不改。批准后应完成有界非应用控制、CLIENT源码重绑定、受影响spec/run/parser/Q证据适用性复核，再复用main61科学资格。

原控制器当前STOPPED；本审查未改registry、lease、controller、runtime、生产binary或旧结果。启动前仍须原runner完成完整内容身份及真实资源/结果预算准入；本轮metadata检查不能冒充该门。全部复核细项及原始引用见FWT_REVIEW.json。
