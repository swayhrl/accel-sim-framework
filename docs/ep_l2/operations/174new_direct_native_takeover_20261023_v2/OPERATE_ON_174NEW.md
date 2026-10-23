# 174-new操作入口与边界

在174-new执行：

```sh
export PATH=/root/data/ep_l2_dtc_l1_native_v2/bin:$PATH
project status --project EP_L2
project status --project DTC_L1
project assets --project EP_L2
asset ensure EP_VECTORADD_S
asset ensure DTC_AD_GEMM
experiment inspect EP_NATIVE_MIGRATION_Q2 --project EP_L2
experiment prepare EP_NATIVE_MIGRATION_Q2 --project EP_L2
```

状态查询分开显示旧Source历史计数与本地新迁移计费，不把旧57或DTC2重置成新预算。`asset ensure`仅验证本轮已导入的两个精确冻结输入集合，零重传、不重复大文件SHA。其它历史资产明确不可直接用，须先有新的精确owner清单和源/目标准入；不允许自动全盘扫描或搬迁。

`run-native`是本地fork/exec，仅接受已冻结、单独批准且尚未消费的cohort。当前已用EP Q1和Q2、正在运行DTC Q1，全部0自动重试。成功后这些迁移额度全部耗尽，下一次科学启动仍需新的唯一request/spec和预算；正式native epoch不会赋予无限新实验额度。旧Source模拟器没有SSH执行fallback。

```sh
# 已完成的本地迁移资格证据按cohort归档；重入只核验并复用。
# 活动科学资格期间拒绝启动另一条大型归档操作。
result archive EP_NATIVE_MIGRATION_Q2
```

所有新结果先写各项目原生ext4的run/results/<new UUID>。依次完成完整终态/科学验收、COPY_ONLY归档、关闭重开全SHA、独立native Target恢复与numeric metadata，四种状态分别记录。原件一律KEEP，不提供源释放API。失败证据可归档但始终STOP_UNACCEPTED，不冒充科学通过。

精确真164恢复入口见TRUE164_NATIVE_RECOVERY_POINTER_INDEX.json；各bundle的RECOVERY_POINTER_NATIVE_V2.json、SOURCE_MANIFEST.json、ORIGINAL_FILE_SHA256SUMS、PATH_MAP.json、ARCHIVE_INDEX.json和COMMIT.json可独立定位原始字节。恢复使用新ABSENT目录，并传入真实当前其它项目预留字节数：

```sh
# BUNDLE为索引列出的真实164挂载下的某一精确bundle，不猜测父目录。
# OTHER_RESERVED_BYTES由当前独立资源核对取得，不擅自填0。
sh "$BUNDLE/RESTORE_NATIVE_V2.sh"   /root/data/ep_l2_dtc_l1_native_v2/EP/run/recovery/NEW_ABSENT_COPY   "$OTHER_RESERVED_BYTES"
```

完整恢复仅标RESTORE_VERIFIED_NATIVE_TARGET；不标native164恢复。容器/机器身份、挂载或device变更后重新准入。无需联系旧Source或重建源侧软件环境即可读取本轮完整PAX档案；新恢复目录仍受5GiB+2GiB、RAM和精确并发写入预留约束，不与活动科学任务争用大型I/O。

EP代码Framework9dd1ee57/Core d010911e/vendor f90c430c；DTC代码Framework8e43c75/Corec8090115以及已接受AG7观测层overlay36903703，详见资产索引。运行用原binary/private Source ELF loader，未修改系统库或RPATH。CUDA11.8属重建依赖，本轮未新装；未来改变编译器、Core或binary需单独生成身份与资格，不可宣称旧SHA仍适用。

当前正式科学epoch尚未提前切换。只有EP/DTC各自真实科学通过、真164归档恢复和最新Source活动/预算/owner核对全部通过，才执行native_authority.py的条件提交；旧管理epoch1保留，原Source官方新dispatch行政退休。root越过协议手动执行不属于该行政fence的安全保证。所有原Source账本与历史结果保持原样，C16/TLS/A–F不变。
