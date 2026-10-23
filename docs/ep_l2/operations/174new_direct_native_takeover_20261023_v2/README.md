# 174-new 原生接管 V2：已完成

EP-L2 MAIN61 vectorAdd S 与 DTC-L1 AG8R1 AD_GEMM 均已在174-new本地完成独立计费的完整资格运行、严格科学验收、真164持久归档和独立 native Target 完整恢复。单一科学执行权已提交到174-new epoch2；原174官方新科学dispatch行政退休，原管理epoch1和所有历史资产/账本保留。

## 实际验收

| 项目 | 本地PID / UUID | 完整终态 | 实际耗时 |
|---|---|---|---|
| EP Q2 | 889746 / 82c71041-cfc2-4669-9a90-1e644d8d1bdc | cycles73696、instructions56000000、CTA15625、1kernel、64slices、hardware drained | 633.929s |
| DTC Q1 | 890038 / 35c3cc78-b7c0-4572-9ec5-91c0f1227500 | cycles1044499、instructions739246080、CTA1024、1kernel、270配置及原strict/ownership/credit检查全部通过 | 9587.230s |
| 独立旧NN重放 | 891413 / b89cd9a1-5967-4097-a206-9a41bcf89757 | cycles6105、instructions1284872、CTA168、1kernel、47项历史指标精确一致 | 2.237s |

PID/mnt namespace、实际映射ELF、真164 trace打开、无原174 SSH科学执行，以及自然完整退出均有实际证据。NN使用旧FAST64/Core95，只代表独立完整重放；当前AD资格由上表长GEMM独立完成。

原Source EP57/T0、44接受及DTC AG8R1 2/2、1接受/0剩余不变。迁移EP Q1因并发预留门禁停止，计费1且证据保留；用户另批Q2计费1，DTC Q1计费1，额外NN计费1。共4次新实际启动、0退款、0自动重试。当前新科学预算为0，下一次科学启动需自己的精确owner规格、显式预算和实时资源准入；本次切换不授予无限运行额度。

## 本地代码、输入与归档

原生专属根`/root/data/ep_l2_dtc_l1_native_v2`已建立精确Git Framework/Core/vendor、必要脚本、原binary和隔离ELF依赖。DTC原接受AG7观测层Git overlay单独保留；未改binary字节、系统库或RPATH。运行用私有原Source加载器；CUDA11.8仅属于未来重建依赖，本轮不要求新装。

本轮主输入仅EP vectorAdd S与DTC AD_GEMM两套有序成员，合计1214211207B；额外NN输入1987819B。源/真164关闭重开全SHA、原EP组合身份及DTC历史完整body SHA均匹配。真实164为`admin-wcx@10.208.130.164:/home/shared`，挂在174-new `/root/share/mnt164`。原174同名路径是本地shadow，不用于归档。

仅在174-new创建精确旧路径兼容视图：本地代码/runtime、真164只读输入、原生本地results/tmp/cache/log/registry/locks。其它未导入历史资产明确标记不可直接使用，不把整个/workspace指向NAS。NAS与本地prefix性能已量化且注明可能warm cache；完整应用证明本轮输入实际可用，不推广为所有trace性能无损。

EP Q2和DTC Q1新结果20普通文件，均已真164归档、关闭重开完整SHA、ABSENT native ext4完整恢复，校验uid/gid/mode/mtime_ns和目录/内部perf链接语义。加上停止EP Q1及独立NN，共37普通文件、16398330B原始结果、16496640B归档payload，全部恢复通过。恢复不是native164执行，持久归档确实在真164。

完整恢复索引见`TRUE164_NATIVE_RECOVERY_POINTER_INDEX.json`。每个精确bundle保留SOURCE_MANIFEST、PATH_MAP、原始SHA、ARCHIVE_INDEX、COMMIT、独立恢复证明、RECOVERY_POINTER及可重放RESTORE脚本，无需原174运行软件即可取回原始结果。旧E057、AD_GEMM完整历史结果及9个sidecar未重传。

## 空间与边界

本任务原生目录当前分配222789632B（有时间戳的endpoint测量，非连续全局峰值）；共享SSD可用12353515520B。EP Q2峰值/耗时、DTC Q1峰值RSS5138022400B及各阶段输出观测均分项记录。两容器overlay及/root/data共用同一SSD池，不重复计算。

真164已知精确范围总逻辑字节2447336901B，包含1216199026B不同输入、1214211207B保留的输入恢复chunks、16496640B结果归档及元数据。不能把FUSE逻辑字节冒称NAS物理分配；不把NAS retained chunks重复计入本地暂存。只盘点本次3个输入范围和4个txid，未扫整座NAS。

单receiver、单流30MiB/s、原始chunk≤128MiB、暂存≤256MiB、Share新增数据0、精确5+2GiB迁移资源授权和其它项目预留均保留。所有旧新原件SOURCE_KEEP，源盘实际释放0B。未操作C16/TLS/A–F，不启动新的科研应用或后台守护进程。

## 使用与证据

在174-new执行`source /root/data/ep_l2_dtc_l1_native_v2/activate.sh`后使用`project status/assets`、`asset ensure`、`experiment inspect/prepare/run-native`及`result archive/restore`。精确命令及新预算边界见`OPERATE_ON_174NEW.md`；后续部分资产归档见`FUTURE_ASSET_COPY_ONLY.md`。未知资产和已消费科学预算实际拒绝。

正式执行权与账本证据见`NATIVE_SCIENCE_EPOCH2_COMMIT_RECEIPT.json`；逐项合同验收见`FINAL_ACCEPTANCE_AUDIT.json`；实时本地入口检查见`FINAL_NATIVE_ENTRY_VERIFICATION.json`；空间核账见`FINAL_NATIVE_RESOURCE_ACCOUNTING.json`及`TRUE164_KNOWN_SCOPE_STORAGE_ACCOUNTING.json`。完整交付还需本次GitHub push及逐文件远端回读成功，其结果单独发布。
