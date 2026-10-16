# 174-new→164 Storage-Ops执行入口

此操作是用户单独授权的跨项目归档/空间恢复，不属于EP-L2 Lane 1–6，不替代Lane 5资源和独立资格管理。

请先读[AMENDMENT_SSHFS_V2.md](AMENDMENT_SSHFS_V2.md)，再读原[GOAL.md](GOAL.md)，在174-new现有Codex窗口**继续**（不要重启）任务。`/root/share/mnt164` 已证实是真实164 SSHFS共享挂载且可读；尚未确认目标可写、归档根授权和Lane5 `/workspace`源映射。`/tmp`清理不一定释放Lane5空间。

优先核实现有SSHFS挂载的目标写权限及用户专属归档根，无须反复尝试新SSH登录；若已有挂载不满足要求，再报告SSH认证需求。源端可达且所有安全门通过后才小批量复制并双端校验。删除仅限不活跃、非唯一、可重建、远端验证的明确临时文件。`/workspace/.git/tmp_pack_*`需另行用户明确批准后才删；不删除历史raw/trace/唯一binary/review pack。保留48GiB workspace磁盘和64GiB可用内存门槛。六Lane由原窗口继续，不动其worktree/registry/任务。

Ops执行证据写独立分支`hrl/ops-174new-164-archive-exec-v1`，此任务文件和发布提交只读。
