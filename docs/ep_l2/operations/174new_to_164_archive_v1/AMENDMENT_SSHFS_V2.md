# Storage-Ops V2修订｜确认164 SSHFS只读可达，继续排除源端映射/写权限阻塞

**2026-10-16用户补充证据。执行分支继续原** `hrl/ops-174new-164-archive-exec-v1` **，不重新启动Goal。** 本修订优先于V1中与之冲突的164连接方式描述。原Goal的科学数据保护、双端校验、安全清理、Git tmp_pack删除前用户审批、六Lane隔离和48GiB/64GiB资源门槛继续生效。

## 1. 已有证据能证明什么

- Storage-Ops 先前独立审计：`findmnt -T /root/share/mnt164`指出`fuse.sshfs`，source=`admin-wcx@10.208.130.164:/home/shared`；`df`在此挂载上报告约49TiB可用。该目录不是本地`/root/share`的普通目录。旧Goal“只是本地Share”的表述不再适用。
- 用户新提供的另一个Codex窗口**实际读取**此挂载上`huangrulin/c16_ai_workload`的catalog和一份raw记录，并看到captures/parsed/reports；证明该共享挂载当时至少可读。无需重复打开该C16原始运行记录，A70历史项目限制不自动转化为访问或修改它的许可。
- root、huangrulin及先前admin-wcx的新建交互式SSH认证失败；**不构成已建立SSHFS不可读的证据**，也不必反复试密钥或要求用户发送密码。SSHFS只覆盖`/home/shared`导出的路径，不代表可以访问164其余磁盘。
- **未证明**：当前挂载可写、其中哪一目录是已授权归档根、远端写入后持久可读、174-new是否能接触Lane5真实`/workspace`、归档删除源文件是否能释放Lane5目标FS空间。

## 2. 174-new窗口下一步：最小增量检查

1. 读取本修订和上轮执行分支`44dc0094068de01cfe1a52677f340533c95340c4`的STATUS/PRECHECK/SOURCE_FS_MAP/REMOTE_164_AUDIT，查看自身最新分支后有界继续；已完成只读扫描不重复。
2. 以超时保护、低IO的`findmnt`、`stat`、`df`及对用户可读顶级目录的最小`ls`确认`/root/share/mnt164`当前活跃、后端identity和容量。用户新提供的读取证据视为只读访问已核实；不需要再次深入或读取`c16_ai_workload`内容。禁止重试失败账户、放松SSH主机指纹校验或改mount。
3. 在`/root/share/mnt164/huangrulin`或其它明显属于用户的现有目录，**只读**核对目录`stat`、权限/ACL、已有归档命名约定；注意FUSE展示的权限未必等于164服务端真实授权。候选归档根仅作提议，**不得自动写入`c16_ai_workload`、现有模型目录或他人目录**。
4. 只有已经明确证实该目录由用户授权用作独立archive root，才在该root下创建唯一新`174new_archive/<run-id>`并做一个几字节的可删除探针：写入→关闭/flush→重新通过SSHFS读取并SHA256校验→删除探针。检测没有残留。记录`SSHFS_MOUNT_READ_VERIFIED`或`SSHFS_ARCHIVE_WRITE_VERIFIED`准确级别；仅通过FUSE读回不能写`SERVER_SIDE_NATIVE_VERIFIED`。若目标写根不明确，记录`ARCHIVE_ROOT_APPROVAL_PENDING`并问用户一个精确归档绝对路径，不冒进。
5. **源端依然是主阻塞。** 174-new SSH namespace没有`/workspace`。请求Lane5执行本文件第3节的只读`df/findmnt/stat`，对比是否同底层设备/配额；若无同源映射，不允许通过猜测符号链接、修改目录权限或跨容器越权访问来找源。可合法方案：由Lane5所在容器/获授权宿主机从真实`/workspace`直接推送到已证实可写的164归档点，或先取得明确定义的只读源映射后由174-new做归档。现有174-new`/tmp`较小，清理它不是本轮恢复Lane5的捷径。
6. 目标/源均验证后才使用单份限速rsync/受控复制和源端SHA256、SSHFS接收端关闭/重开读回SHA256，以及路径/大小/权限清单。未有独立164主机登录时只能宣称`SSHFS_READBACK_VERIFIED`，不可冒充远端原生独立校验。唯一科学原始数据只COPY不DELETE；无活动且可从确定性来源重建的具体临时文件可依原Goal逐条、安全授权清理。**`.git/tmp_pack_*`仍必须逐个分析、先归档并另请用户批准后才能删除。**
7. 若归档源仍不可达或root未获授权，发布准确`COPY_GATE_BLOCKED_SOURCE_MAPPING`/`ARCHIVE_ROOT_APPROVAL_PENDING`，不要再将“没有新SSH密码”作为唯一阻塞项。六Lane无需被打断；Lane5真正通过48GiB门槛和预留增长空间仍需在它自己环境测得。

## 3. 给Lane5的最小只读回执（不允许顺带清理）

在Lane5真实环境执行以下只读命令，并记录原始输出、时间与主机/容器名；不要dump密钥、环境变量或凭据：

```bash
hostname
readlink /proc/self/ns/mnt
df -B1 -P /workspace
findmnt -T /workspace -o TARGET,SOURCE,FSTYPE,MAJ:MIN,FSROOT
stat -c '%d %i %n' /workspace
df -B1 -P /tmp /root/share 2>/dev/null || true
findmnt -T /root/share 2>/dev/null || true
```

这不是让Lane5降低48GiB floor、清理数据、编译或暂停科学任务；只让Ops能判断174-new与Lane5的真实存储映射。有权限又不会冲突时，可将其写入Lane5独立小receipt并给出准确发布SHA；如果Lane5繁忙，也可以由用户在该相同容器的终端执行后贴回。

## 4. GitHub证据与退出

继续写Storage-Ops原执行分支，生成新revision而非覆盖`20261016_storageops_01`；至少包含挂载活性、164实际授权归档根、SSHFS read/write分级、目标探针若执行的hash/清理记录、Lane5 FS映射信息与真实源释放字节。紧凑脱敏产物commit/push/readback。若尚无源端映射或目标写根，则保持阻塞并报告最少补充信息，不重复全库扫描。

**本V2只修订工作流程，不宣称已复制、校验远端归档或释放任何磁盘字节。**
