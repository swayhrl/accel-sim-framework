# 174-STORAGE-API 下一批精确回收最终报告

Goal：`NODE174_API_NEXT_BATCH_RETIREMENT_V1`。执行日期：2026-11-10（用户时区 America/Los_Angeles）。

## 结果

| 顺序 | 资产 | 状态 | 文件 | 逻辑字节 | unlink 分配字节 | df 窗口增量 |
|---|---|---|---:|---:|---:|---:|
| 1 | atomic_add_bw (`TRACE_e05d004e4fdbfc1d`) | DONE | 2 | 5,008,635,717 | 5,008,650,240 | 5,008,617,472 |
| 2 | Bank Diagnosis (`TRACE_ffa286b1549088e6`) | DONE | 3 | 8,939,708,404 | 8,939,724,800 | 8,939,683,840 |
| 3 | M5 ATAX (`TRACE_6a972ad51c80d79c`) | DONE | 4 | 5,806,705,792 | 5,806,731,264 | 5,806,678,016 |
| 4 | M5 MVT (`TRACE_0997bf1fccd3524d`) | DONE | 4 | 5,777,389,848 | 5,777,408,000 | 5,777,358,848 |

合计：**13 个文件**，逻辑 25,532,439,761 字节（23.779 GiB），unlink 前分配 25,532,514,304 字节（23.779 GiB）。四个 df 窗口增量合计 25,532,338,176 字节；整个任务从首项前到最终 df 增加 25,532,309,504 字节（23.779 GiB）。这三种量分别计量，不相加；df 包含同期其他写入。

同一物理 SSD 的可用空间：首项前 **18,526,203,904** 字节，最终 **44,058,513,408** 字节（41.033 GiB）。原 174 的 overlay 与 174-new 的 /dev/sdf 最终读数一致。最终可用 inode：215,526,066。

## 命名空间、证明与保护

Source 位于原 174 `ssh hrl`（`huangrulin-174`，挂载命名空间 `mnt:[4026534768]`）的本地 overlay；原 174 的 `/root/share/mnt164` 是本地 `/dev/md127`，未作为备份。真 164 从 174-new（`huangrulin-sshfs-174`，`mnt:[4026535153]`）的 SSHFS 入口核对。

固定证据：归档基线 `bbb862ba96c70bdfb92f7b0bc2e319ab91ac58d8`；候选审计 `8c0ccaa2dbaa7d8a0a280fa5a38f5c5ebccc2b80`；前批已完成回执 `31e98302fab9a75105f1c7dc8f252c53a5364ec3`。本轮逐项复核 COMMIT SHA、Manifest SHA、范围/树回执链接、归档成员大小及归档时 mtime、恢复入口；原始 .trace 和 processed .traceg 分别匹配。复用已有完整 SHA 证明，未全量重哈希或做完整 native 恢复。

删除前每个 Source 成员的 dev、inode、大小、mtime、ctime、uid/gid、mode、nlink 与归档冻结身份一致；当前没有对应活动进程 FD/mmap 或精确路径登记。独立完成后回读确认 13 个数据成员缺失，控制文件 SHA 不变，原目录保留。Bank 的旧脚本默认路径已不含完整 Trace，未来使用前须按下面入口恢复；本轮未修改脚本或科研 registry。M5 目录和科研记录保留，未修改 immutable 属性；受 unlink 影响的目录 ctime 已更新，mtime 已恢复。

## 精确恢复入口

- atomic_add_bw：`/home/shared/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261024_verified_offload_reclaim_v1/assets/TRACE_e05d004e4fdbfc1d/RESTORE.sh`，原路径 `/workspace/worktrees/accel-sim-decoupled-l2/hw_run/decoupled-l2-pretraces/ubench/9.1/atomic_add_bw/NO_ARGS/traces`。
- Bank Diagnosis：`/home/shared/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261024_verified_offload_reclaim_v1/assets/TRACE_ffa286b1549088e6/RESTORE.sh`，原路径 `/workspace/worktrees/accel-sim-decoupled-l2/hw_run/decoupled-l2-bank-diagnosis/20260825-b07c0ad-full/traces`。
- M5 ATAX：`/home/shared/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261024_verified_offload_reclaim_v1/assets/TRACE_6a972ad51c80d79c/RESTORE.sh`，原路径 `/workspace/m5-trace-immutable/atax/atax/traces`。
- M5 MVT：`/home/shared/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261024_verified_offload_reclaim_v1/assets/TRACE_0997bf1fccd3524d/RESTORE.sh`，原路径 `/workspace/m5-trace-immutable/mvt/mvt/mvt/traces`。

## 回执与退出

`FROZEN_WHITELIST_AND_DONE.jsonl` 逐文件记录 Source 身份、归档 SHA、INTENT/DONE 和空间读数；`EXECUTION_RECEIPT.json` 保存节点、归档与资源汇总。原 174 持久事务目录保留每文件独立 INTENT/DONE。四组均 DONE，HOLD 0，ALREADY_RETIRED 0，剩余本批阻塞 0；未扩大清理范围或启动长期监控。
