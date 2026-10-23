# 174-new direct native takeover V2 — EP passed, DTC running

EP已实际完成174-new本地完整资格Q2，并独立严格验收、真164持久归档和native Target完整恢复。DTC已完成新资源准入并启动实际本地资格Q1，等待完整终态。整体迁移尚未完成，科学epoch未提前切换。

## 实际科学与预算状态

- 原174 EP57/T0、44接受与DTC AG8R1 2/2、1接受、0剩余不变，所有历史原件SOURCE_KEEP。
- EP迁移Q1实际本地启动后141.98s因保守并发预留门禁停止，计费1，不退款、不重跑原UUID；停止证据已164归档/完整恢复。
- 用户明确另批Q2。Q2 PID889746，namespace mnt:[4026535153]，uuid82c71041-cfc2-4669-9a90-1e644d8d1bdc，完整633.93s自然退出；原E纯终态校验器通过，cycles73696、instructions56000000、CTA15625、1kernel、64slices和hardware drain精确匹配。
- EP Q2新结果9文件/2目录、6029811B：真164归档和完整SHA/native Target恢复及uid/gid/mode/mtime_ns全部PASS。见EP_NATIVE_MIGRATION_Q2_ARCHIVE_AND_RESTORE_RECEIPT.json。
- DTC迁移Q1 PID890038，uuid35c3cc78-b7c0-4572-9ec5-91c0f1227500，实际174-new本地运行；原Source加载器/ELF、原BA认证遥测、非IO安全状态机、fresh30/no-retire600和21600s截止保留。小CPU工程fixture不计作科学进程。
- 新迁移启动计费EP2、DTC1；所有旧失败保留，0自动重试。当前许可无须再次批准，未来另一个科学启动仍需独立预算。

用户另行精确批准的短完整 NN 已完成：新 cohort DTC_LEGACY_FAST64_NN_NATIVE_SHORT_Q1、PID891413、uuid b89cd9a1-5967-4097-a206-9a41bcf89757，174-new 本地正常退出，2.237s、峰值 RSS494927872B。原冻结 parser 的严格检查及历史47项指标全部一致，cycles6105、instructions1284872、CTA168、1kernel、credit/ownership全排空。仅新增计费1次，重复启动被拒绝，临时并行写入预留已撤除，长GEMM未停止/重启。NN为原Core95ccdb7a/FAST64的独立完整重放，不能替代当前Corec809/AG8R1 AD资格。

NN结果10普通文件、2目录、1内部perf软链接，210643B，真164归档235520B及独立ABSENT native Target完整恢复（字节、SHA、uid/gid/mode/mtime_ns及链接语义）通过。见LEGACY_NN_COMPLETE_NATIVE_ACCEPTANCE.json、DTC_LEGACY_FAST64_NN_NATIVE_SHORT_Q1_ARCHIVE_AND_RESTORE_RECEIPT.json及TRUE164_NATIVE_RECOVERY_POINTER_INDEX.json。所有原件KEEP、源释放0B。短例完成不代表当前长AD或整体V2已完成；最新主线进度见DTC_NATIVE_MIGRATION_Q1_LATEST_PROGRESS.json。

## 本地工程与存储

Framework/Core/vendor精确Git代码、必要binary/库/脚本位于/root/data/ep_l2_dtc_l1_native_v2。DTC保留了原接受binary对应的AG7 Git观测层overlay，未改Core或binary，未替换系统库。

只导入EP vectorAdd S与DTC AD_GEMM确切两组输入成员，合计1214211207B，源/真164关闭重开全SHA通过。DTC大member还精确匹配原KERNEL_BODY_AUDIT.tsv历史全SHA。旧路径仅在174-new做精确只读兼容映射；不全搬trace，不把整个/workspace指向NAS，不SSH执行原174模拟器。

新结果本地热写后单receiver分块归档真164，完整原始字节与numeric metadata恢复。Share新增数据0，staging不超过256MiB，chunk不超过128MiB，传输不超过30MiB/s。严格保留5GiB+2GiB及其他项目预留和RAM规则。按用户批准仅预留当前串行阶段；DTC实际操作cap进一步收紧至128MiB（原允许上限512MiB内），基于原stdout5564041B及有界监测，不复制251MB旧全项目监控dump、不删除它。

## 入口与剩余工作

入口/root/data/ep_l2_dtc_l1_native_v2/bin/native支持project status/assets、已导入asset ensure、experiment prepare/run-native和result archive/restore；只处理明确冻结scope。旧管理入口保留，正式科学生产启用及唯一ledger切换仍须DTC实际合格和终态/旧控制权检查。

剩余：DTC完整科学终态、其新结果164归档恢复、两项目科学epoch的有条件正式切换、最终索引/资源核账/远端回读。所有原件保留，实际释放0B；C16/TLS/A–F未干预。
