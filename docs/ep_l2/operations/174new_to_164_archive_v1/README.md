# 174-new→164 Storage-Ops执行入口

此操作是用户单独授权的跨项目归档/空间恢复，不属于EP-L2 Lane 1–6，不替代Lane5的科学资格管理。

**最新授权与续行：**先读[AMENDMENT_SHARED_BRIDGE_V4.md](AMENDMENT_SHARED_BRIDGE_V4.md)，再按需读[V3 Overlay映射](AMENDMENT_OVERLAY_MAPPING_V3.md)、[V2 SSHFS](AMENDMENT_SSHFS_V2.md)及原[GOAL.md](GOAL.md)。

用户已明确授权唯一164 SSHFS归档根：`/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02`，允许专属目录创建与几字节写入/关闭/读回/hash/清理探针；父目录原有`git_packs_20260928`不动。新旧174的`/root/share`可按共享路径设计，但仍需两窗口几字节交叉可见性探针，不等于`/workspace`路径互通。

174-new目标侧继续原`hrl/ops-174new-164-archive-exec-v1`，旧174源侧另用独立Ops分支`hrl/ops-174-source-audit-exec-v1`。桥接只用专用目录，单批建议不超过512MiB，保留Shared至少40GiB空闲；源/桥/164逐文件hash并保留原始科研资料。高风险Git`tmp_pack_*`必须另经用户逐项批准才删，不重启或修改六个Lane。48GiB workspace门槛和额外构建余量不变。
