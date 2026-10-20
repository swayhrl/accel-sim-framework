# C16条件性退役已完成

原174 P3 AWQ两片先行、P2 RAW四片随后，六个精确外发权重文件全部退役；HOLD为0。原174当前源全文SHA6/6与真164全文SHA6/6、冻结历史SHA逐一匹配。164 RAW1–3复用有效证明，没有重读；仅其余三片由C16-164-Verify新核验。没有上传、复制或大型恢复权重。

| 包 | 释放文件 | 权重字节 | 原174实测df净增长 B | GiB |
| --- | ---: | ---: | ---: | ---: |
| P3 | 2 | 5,570,829,760 | 5,570,838,528 | 5.188248 |
| P2 | 4 | 15,231,271,888 | 15,231,295,488 | 14.185249 |

分包实测合计 **20,802,134,016 B（19.373497 GiB）**。从P3前到P2后的完整窗口实测净增长 **20,801,974,272 B（19.373348 GiB）**；窗口间其他工作产生小额空间变化，未把理论分配块上界当成唯一因果收益。

源操作前准入证明已提交、远端回读：`366fc5e55d935011be0484b603a7b24126c185d7`。164最终完整性证明：`2aa2e5f73c024c313bc6835816523773f24c898a`。新项目级条件授权及IO竞争例外来自本轮用户；未冒称历史A/G签字。IO10不是本轮阻塞条件，科学控制器和共享租约没有被修改。

[RETIREMENT_CLOSEOUT.json](RETIREMENT_CLOSEOUT.json)、[SOURCE_RELEASE_JOURNAL.jsonl](SOURCE_RELEASE_JOURNAL.jsonl) 与两个独立包签收回执记录精确路径、身份、INTENT/DONE及df。持久主日志在 `/root/share/c16_storage_audit_restore_20261020_v1/SOURCE_RELEASE_JOURNAL.jsonl`。六个源路径当前均不存在，P2/P3目录中其余126个控制/清单/交付文件全部保留且SHA未变；六个c16_assets模型原件ACTIVE_KEEP，监督器PID/start_ticks与脚本未变。

恢复使用 [CURRENT_RESTORE_INDEX.tsv](CURRENT_RESTORE_INDEX.tsv)、[RESTORE.sh](../RESTORE.sh) 和 [RESTORE_USAGE.md](RESTORE_USAGE.md)。真实路径为164 `/home/shared/...` 经174-new现有真实SSHFS、已验证的commonShare前台FIFO送回原174精确路径；不用旧容器同名假挂载，不落完整Share副本。默认仅计划、不覆盖已有文件，保留字节、0:0/0600和原mtime；历史inode/ctime不要求恢复。真实跨namespace小探针已确认，隔离小数据已验证恢复字节/属性/无覆盖及FIFO路径；没有宣称做过大型模型恢复。将来实际恢复时仍检查当时容量与保留空间，未改变未来C16任务配置或增加控制器。

109现存等待任务由实际准备回执绑定到3B模型，与本7B六片无关。历史交付已闭合；当前监督器及A的手工producer使用保留的c16_assets原件。未来7B需求按本轮用户政策从164恢复原外发路径后消费。没有发现实际未接管的六路径消费者。用户授权范围外的模型、科学任务、109资产、E2/TLS P9和已接受结果未被改动。
