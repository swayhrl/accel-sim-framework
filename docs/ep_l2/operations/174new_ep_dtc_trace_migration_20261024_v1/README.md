# EP-L2 / DTC-L1 trace COPY_ONLY迁移：全范围数据验收完成

合同79207bab15699ad76ffc821bb5e17663e6617545。本轮从两MAIN实际HEAD和科学输入证据建立去重清单，已完成全部20套合格输入：EP8套、DTC14套，跨项目共用2套，不把105个科学/计划引用当作105套数据。

| 核账项 | 实际结果 |
|---|---:|
| 不同输入集合 |20|
| 完整有序kernel成员 |663|
| 全部必要普通文件 |683|
| 不同输入原始字节 |22507635190B|
| 已有三套复用字节 |1216199026B|
| 新增17套Source传输 |21291436164B|
| 数据/映射HOLD |0/0|
| 完整native Target恢复 |5套|
| 大输入完整native恢复NOT_PERFORMED |15套|
| Source实际释放 |0B|

FWT19个kernel、Gaussian510个kernel、LUD94个kernel均完整；SGEMM2.216GB及Conv6.845GB通过offset分块，无32位大小截断。每套有原始commandlist字节、有序member、每文件全SHA与stat、原目录信息、Source读取前后身份、真164关闭重开整文件SHA、不可覆盖发布和COMMIT-last。P0 Vector/GEMM/legacyNN直接复用；现有两个生产输入映射不变，未重复上传旧数据。

真164为174-new的`/root/share/mnt164`，实际`admin-wcx@10.208.130.164:/home/shared`。新范围在`/home/shared/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261024_ep_dtc_trace_inputs_v1`，按EP/DTC/SHARED保存完整raw树及校验/恢复记录。Source同名本地shadow不作为164。

在174-new使用：

```sh
source /root/data/ep_l2_dtc_l1_native_v2/activate.sh
project assets --project EP_L2
project assets --project DTC_L1
asset ensure EP_FWT_7_21 --dry-run
asset ensure DTC_GAUSSIAN --dry-run
```

全部20个当前输入的asset ensure、原绝对路径realpath与实际open/seek/reopen均通过。只新增精确Target兼容链接，不把整个/workspace指向NAS，科研热写目录仍为native ext4。新增查询路由保持原科学frontend argv delegate，25份受保护科学文件哈希不变；未知资产/项目不符拒绝。数据READY不授予新scientific attempts或解除任何旧HOLD。

现有唯一Source sender/Target receiver、单数据流、≤128MiB原始块、≤256MiB任务暂存、原总限速与完整物理预算继续保留。CPU/IO使用保守低优先级；AEFAIR的实际PID/start_ticks、认证进度、资源和I/O被持续观察，未停止/重启/改写其控制器。host/cgroup/SSD/peer reservation证据见SOURCE_KEEP_AND_RESOURCE_ACCOUNTING.json，NAS logical、retained chunks、native端点分开，复制不冒称源空间回收。Share新增数据/control0，科学启动0。

原Source EP57/44/T0、DTC2/1及全部科研历史原样保留；合法并发owner研究进度只做观察，不用旧快照回写当前预算。原DTC3个ADMISSION_HOLD、EP Btree等科学边界和P2不在范围项见REMAINING_HOLDS_AND_NEXT_ACTIONS.md。初始空路径审计错误与清除记录单列，不隐去。

恢复分级：完整raw树可直接驱动现有SASS输入读取，所有原始SHA/数字元数据和可靠入口在TRUE164_TRACE_RECOVERY_INDEX.json。小输入实际独立恢复到新ABSENT native Target并逐文件核验；大输入受当前240MiB窗口约束，完整native恢复如实NOT_PERFORMED。不是native164恢复，不把短读压测当全工作负载速度证明，不清空共享page cache。

完整交付：CURRENT_ASSET_COVERAGE.csv（105引用/20unique）、SOURCE_SELECTOR_MANIFESTS/、SOURCE_TO_TRUE164_PATH_MAP.json、TRUE164_TRACE_RECOVERY_INDEX.json、MIGRATION_BATCH_LEDGER.jsonl、NATIVE_ASSET_ENSURE_VERIFICATION.json、两MAIN交付、恢复范围与资源核账。最终true164索引持久化、GitHub提交与逐文件远端回读是Goal闭合的最后独立门禁；相应回执单列发布。
