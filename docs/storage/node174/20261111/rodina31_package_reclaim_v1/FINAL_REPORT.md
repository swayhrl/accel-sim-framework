# 原 174 Rodinia 3.1 历史压缩包归档与精确回收

Goal：`NODE174_RODINA31_PACKAGE_ARCHIVE_AND_RETIRE_V1`。执行日期：2026-11-11（America/Los_Angeles）。**单文件归档与回收 DONE；未选择第二个对象。**

## 结果与空间

原 174 的 `/workspace/worktrees/accel-sim-decoupled-l2/hw_run/decoupled-l2-pretraces/rodina-3.1.tgz` 已在真 164 完整归档，随后仅对该文件执行 unlink。源文件原逻辑长度 **15,358,485,561 字节**，原分配 **15,358,529,536 字节（14.304 GiB）**。

原 174 SSD 在 unlink 前可用 **3,797,291,008 字节**，unlink 后 **19,155,750,912 字节**；该窗口实际增加 **15,358,459,904 字节（14.304 GiB）**。最终回读时原 174 可用 **19,139,063,808 字节**，174-new 同一物理层可用 **19,139,055,616 字节**。分配块数与 df 增量分别记录，df 包含同期科研写入。

## 来源身份与归档证明

Source 是原 174 `ssh hrl`（`huangrulin-174`，`mnt:[4026534768]`）的 regular file，删除前 dev/inode、大小、分配量、mtime/ctime、nlink、mode、uid/gid 与执行前冻结身份一致。归档端为 174-new 独立挂载的真 164 SSHFS；原 174 同名 mnt164 是本地 shadow，不参与归档。传输前没有目标文件的活动 FD、mmap、进程命令引用或精确路径任务登记；真 164 的指定历史恢复范围内未找到同名可信原包。

完整 Source SHA256（流式传输中计算）：`89df88f3d141dd854344e36440a0690740455cf75afde92b6ce48af635b8857c`。真 164 对关闭重开的完整目标文件计算 SHA256：`89df88f3d141dd854344e36440a0690740455cf75afde92b6ce48af635b8857c`，两者一致。归档目标：`/home/shared/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261111_rodina31_package_v1/rodina-3.1.tgz`；大小 15,358,485,561 字节。传输采用单流、1 MiB 缓冲、15 MiB/s Source 限速和 64 MiB 持久化边界；中断可对真 164 临时文件的保留前缀与 Source 双端 SHA 校验后续传。本轮从 0 开始，没有在原 174 或 174-new SSD 放置完整副本。

Manifest：`/home/shared/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261111_rodina31_package_v1/SOURCE_MANIFEST.json`（SHA256 `8bc58163f592d615716fa273ff28a1fa7eeac9637521f7ee7668476047cadf24`）。COMMIT：`/home/shared/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261111_rodina31_package_v1/COMMIT.json`（SHA256 `734cd89c3752a7ff7444805f03ba6b2338c59f7c936c9eae15b2e1cb4656fef8`）；COMMIT 引用 Manifest SHA 与双端完整文件 SHA。删除后独立回读确认真 164 仍为 regular file，大小、Manifest/COMMIT 链接及恢复说明仍有效。已解压 Rodinia Trace 不作为压缩包证明。

## 精确删除与保留

原 174 持久事务目录 `/root/data/rodina31_package_archive_20261111_v1` 保留 `INTENT.json` 和 `DONE.json`。删除前再次核对 Source 身份与当前使用者，INTENT 落盘后只 unlink `rodina-3.1.tgz`。回读确认路径不存在，原 `decoupled-l2-pretraces` 目录及 `parboil.tgz`、`accelwattch-artifact-appendix.tar`、`rodinia-first-batch` 保留。M5 压缩包、其他科研控制文件、结果、registry 和真 164 既有归档未修改。

恢复说明：`/home/shared/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261111_rodina31_package_v1/RESTORE_INSTRUCTIONS.txt`。后续如需恢复，需从真 164 归档对象复制到原路径所在磁盘的临时位置，核对上列 SHA256 后再原子放入当前已缺失的原路径；恢复是单独任务，本轮未做完整 native 恢复测试。

GitHub 发布以此报告所在的独立分支提交为准；完整最终 HEAD 与 GitHub 远端逐文件回读结果在本轮交付回复中给出。
