# 来源、采样语义与证据限制

所有历史事实取自精确锚点 d9c192544622579a93d3efad98f56f82536c2fbe 下 `docs/dtc_l1/iscas2027/evidence_closure_20261019_v1/`。该锚点是 Goal 提交祖先，fetch 的目标分支 HEAD 精确等于 02ead59800e4559f90e17e28c898a7846c292b67。先读 CURRENT_STATE 顶部当前快照与指定 immutable 回执；底部历史段落未当作当前授权。

[LIFECYCLE.tsv](LIFECYCLE.tsv) 单列 RUN_START、实际fork、策略触发、封存与收尾；无精确时间字段的事件明确 UNAVAILABLE，不用预计时间冒充回执。

`PRIMARY_PROVENANCE.json` 记录 17 个主要文件的 Git blob、SHA256 与字节数；文件数以该 JSON 为准。每个 checkout 文件与锚点 blob 一致，RUN_START SHA 与 AG6_BUDGET_LEDGER 中记录一致。RESOURCE_MONITOR 为 2,921,484B、28 行，SHA256=f78a0844c438632ed009447f0c630f1527fa4ac12c5d6f22ef3a1451b671e39c，完整单次流式解析。后续计算使用独立证据目录的精简提取，不重复扫描监控或原 trace。

执行源码绑定链为 RUN_START.publication_head=62323c40df0add726cae52a96ca946e589f00343 → AG6_EXECUTABLE_PREREGISTRATION_V2 SHA256=45d994d7489880bdfe53a1c902207856f06f77ba7927ba8dd6f52124f7dfe9cc → 49 个 source_sha256。均从该提交 Git 对象读取并核验，同时核验诊断 worktree 的相同字节。完整 blob/SHA 在 EXECUTED_SOURCE_PROOF.json。运行时 source_core=c8090115bd57512b1b23fca7d925301fa620c751；模型路径来自 RUN_START，不读取或重哈希模型本体。

| 调用路径（execution/ 下） | SHA256 | 已静态核对的行为 |
|---|---|---|
| prepared_ag6/dispatch_ag6_v2.py | e13ddb22178e263d3b517459684ea12b98922a0d1b3309af46e0c1750ae66a45 | 真正 observer 调用 Runtime，写完整 snapshot/authority/decision/own；只采 root majflt 供策略，完整快照另含 helper |
| prepared_ag6/resources_v2.py | f1844de51555384a48227affe48d70bea09c98dc787269e5b43c43ea735f94f9 | host/cgroup 各实例 RuntimePolicy；cgroup 仅替换 pressure，保留共享资源人口；5GiB/OOM/输出 device 快速保护 |
| prepared_ag6/frozen_ag4_resource_policy.py.txt | a023f3d3d716088d5f2f596de60b15ac64332b1dc1a3e7a9875bbca53f077bb0 | full avg10>25，三个资格点，>=30s；IO 低值仅在资格时清零 |
| prepared_runtime/shared_authority.py | 103f5663c95dc3cfe4522a40e47043a5ff6fa8e38c16e5bb7f41c45585acfdbf | 分类视图不改变资源快照；本轮未调用此函数 |
| prepared_runtime/legacy_authority_runtime.py | c8ed095959d0f228c6db786c792d672f126a653713ccf7cedf4719f03d172cd9 | 以 SHA 绑定旧审计文本，仅抽取 proc/snapshot，不是文件名推断 |
| prepared_runtime/legacy_authority_evidence/frozen_audit_site.py.txt | 3a1ca0f502dee376a0b56ecbd5c5d6529afa326041e8daf0c703071229a1d2b7 | `/proc/pressure/{io,memory,cpu}`；固定 `/sys/fs/cgroup/`、要求 membership=0::/；读取 io.stat、diskstats、进程 stat/io 等 |
| prepared_runtime/vendor/guarded_process.py | ed1ba6b1edd8a7e415a82c2c3c461e8009e4b9324e5efae92c4ebeb24c2478e4 | mapping syscall before/after capture；事件 flush；周期 observer；历史受控清理 |
| prepared_runtime/vendor/mapping_roles.py | 1409539bad1d173c4bf48463c5465f54e8aba89db736e27bae745fd7a7f07155 | validate_snapshot→verify_file→file_record→digest_fd；每个 capture 重读映射文件 |

PSI 语义：full 表示全部非空闲执行潜力因 I/O 停顿的压力，avg10 是平滑趋势，不是瞬时设备繁忙率。Linux 6.8 对每 CPU 状态聚合，故不能把 full=56% 解读成“同一时间整个容器所有进程停止56%”。[PSI 接口](https://docs.kernel.org/accounting/psi.html)；[6.8 聚合实现与说明](https://github.com/torvalds/linux/blob/v6.8/kernel/sched/psi.c)。本轮当前 kernel 为6.8.0-45-generic，但未取历史运行内核 build；上游实现解释语义，不构成该发行版二进制的完整审计。

历史 io.stat 含设备 8:0、8:48、8:32、8:16、9:127、8:64、8:80；keys 为 rbytes/wbytes/rios/wios/dbytes/dios。缺失 io.max、io.weight、io.latency、祖先路径、mountinfo、inode free、dirty/writeback、fsync 时长与每次输出增长。output st_dev=156（0:156），历史 mount_id=4461。不能从设备计数自行重建底层拓扑，不能对可能堆叠的 md/member 设备求和。[cgroup v2 I/O 控制与 writeback](https://docs.kernel.org/admin-guide/cgroup-v2.html#io)。

`OWN_PROCESS_COUNTERS.tsv` 仅保留三条历史事件证明身份与已注册 coordinator 的已存计数；不查询现时旧 PID。pid/start_ticks 与 STOP 实例精确匹配。rchar/wchar 含缓存与管道流量，不是存储读写字节；read_bytes/write_bytes 是另一组记账，不能互换或归到具体文件。[proc I/O 说明](https://docs.kernel.org/filesystems/proc.html)。`HOST_DEVICE_DELTAS.tsv` 以历史 diskstats 两端差计算完成次数/累计ms，包含所有 host 使用者、队列与执行时间，非请求分位数、非 cgroup 限速时间。[diskstats 字段定义](https://docs.kernel.org/admin-guide/iostats.html)。

受控终止/lock released/无 own live 以 STOP_SUMMARY 与 terminal 证明；当前 DTC 角色与 lease 仅取最新已发布 CURRENT_ROLE_STATUS。未做现时 /proc 全扫描、FLOCK 枚举或外部命令行读取，故后续其他窗口活动 UNAVAILABLE，不宣称现时全局空闲。

仅按 STOP_SUMMARY 指定路径读 closed ENGINE/stdout 一次（48,235B，SHA256=762bc2683456ad6badabcb7ffeed770d1a37ead4dd2471b2ee00cf8fbd6182a1，尺寸与摘要均匹配），无完成 cycles/指令/CTA 进展系列。thread block 坐标不能当作已完成 CTA。未读 maps payload、MAP_EVENTS body 或 trace body；8372 event rows/8369 frames、7,579,689B 仅引用发布 manifest，未独立重放。fsync 逐次耗时不可用；静态路径有 write/close/flush，没有用小文件尺寸推断低延迟。

本轮单次当前 metadata snapshot 2026-10-20T00:47:50.344679Z（北京时间08:47:50）：hostname/uid/boot_id 对应原174，membership=0::/，cgroup2 挂载 `/sys/fs/cgroup`（容器只读），io.max 空、io.weight=default100，io.latency ENOENT。输出与 trace目录 stat 同为0:156、overlay；output free=21,631,000,576B、free inodes=216,465,116。仅 stat trace 目录，未读任何 trace 内容。完整记录见 CURRENT_ONLY_NOT_HISTORICAL.json。boot_id 相同不足以证明控制项/挂载历史不变；不可见祖先限制 UNAVAILABLE。本轮没有第二次 PSI 采样或后台观察。

SEM1/ROB1 CPU 对照只采用 CURRENT_STATE 与角色总结中“10+6次短 fixture、40+24 resource receipts passed”的历史上下文；未重读或执行 fixtures，不能视为受控 simulator A/B 或据此放宽门槛。
