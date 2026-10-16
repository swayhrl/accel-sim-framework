# 174-new→164 Storage-Ops执行入口

此操作是用户单独授权的跨项目归档/空间恢复，不属于EP-L2 Lane 1–6，不替代Lane 5资源和独立资格管理。

请完整读取[GOAL.md](GOAL.md)，在174-new Codex窗口单独执行。优先核对源和Lane5 `/workspace`是否同一存储FS；`/tmp`和`/root/share/mnt164`不保证释放Lane5空间，后者不是164大容量存储的证明。

先经已有受信SSH连接核实真正164的归档目录，才小批量rsync复制并双端校验。删除仅限不活跃、非唯一、可重建、远端验证的明确临时文件。`/workspace/.git/tmp_pack_*`需另行用户明确批准后才删；不删除历史raw/trace/唯一binary/review pack。保留48GiB workspace磁盘和64GiB可用内存门槛。六Lane由原窗口继续，不动其worktree/registry/任务。

Ops执行证据写独立分支`hrl/ops-174new-164-archive-exec-v1`，此任务文件和发布提交只读。
