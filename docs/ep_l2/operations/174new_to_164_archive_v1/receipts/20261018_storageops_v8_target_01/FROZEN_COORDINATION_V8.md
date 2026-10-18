# EP-L2 /workspace 空间紧急恢复：OLD174 与 174-new 双窗口 V8

**执行日期 2026-10-18；两个旧Storage-Ops窗口上的新有界增量任务（不是重启已结束的R13/V7 Goal）。**
目标：在Lane5已获用户特定授权启动4路模拟之后，尽快以安全、可恢复、可证明的方式**实际增加Lane5所在 /workspace FS 的可用空间8–10GiB**。两条窗口**并行盘点、并行准备，但源释放单一owner，批量归档单传输流**。

## 0. 已证据闭合的历史与新状态：禁止重复计数/重复迁移

- Lane5新远端 commit `bad4c6c47f00bf8ae928e75a63ca0d68e0083dd5` （2026-10-18T03:23:55Z）明确：原campaign 32/72 new starts，4个central sims正在运行，现有接受结果generation47仍在；为用户特定四端点授权了保留**实际48GiB底线**的预测增长预留例外。原16GiB aggregate output上限、每次raw 2GiB、Share40GiB、RAM64GiB、4sim/8CPU/32GiB及2026-10-18T11:30:14.500719Z new-start期限均未取消。工作只是释放实际空间，Storage-Ops不得改Lane5的registry/runner/额度/资格/在途PID；不得因为另一个项目消耗内存或发生磁盘增长就kill任务。
- 截图记录的上一刻独立测量：Lane5 workspace空闲约48.88GiB；其常规保守预留单路需要约50.125GiB，2路约52.25GiB，4路约56.5GiB；分别短约1.24/3.37/7.62GiB。**这些是旧快照，4个进程现已启动，不可当实时余量**；立刻重新在Lane5或旧174相同源FS复测，8–10GiB为现实解压空间目标，不是授权降低底线。
- 已结束的Storage-Ops R13原执行分支：OLD174（`swayhrl/gpu-l2-cache-verilog`, `hrl/ops-174-source-audit-exec-v1`, HEAD `7aa1dec737a11524022531985ff3f71913e1ed9c`）；174-new（`swayhrl/accel-sim-framework`, `hrl/ops-174new-164-archive-exec-v1`, HEAD `54f9a591e031b1df6e4c7db12bb4ce4d1c8fdd48`）。
- R13准确完成过两处历史PolyBench closeout.stage源释放，共**66,329,825,280 B文件系统净空闲增加约61.77GiB**，13个准确源文件、14空目录。**不得重新扫描/删除/迁移这两处作为新释放**；根下原`polybench.tgz`仍保留。164目标恢复指针 `/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/POLYBENCH_RECOVERY_POINTER_R13.md`，对应目标审计 `docs/ep_l2/operations/174new_to_164_archive_v1/receipts/20261016_storageops_06/STORAGE_OPS_TARGET_CLOSEOUT_R13.json`。这份指针只在174-new实测SSHFS mount身份和真实源164路径匹配后可用于恢复。
- 新目标不是“归档字节数”，必须由**OLD174源namespace**测得真实 `df -B1 -P /workspace`净增加，并由Lane5自己的独立preflight再确认。旧174和174-new两Docker端口分别2233/2239，`/root/share`与`/root/data`有同host映射，但mount namespace不同；先`df/findmnt/realpath/stat dev`验证。清理174-new其它挂载或164目录，不能自动声称释放Lane5 /workspace。
- 本V8遵守先前用户硬约束：**不删`/workspace/.git`、`tmp_pack_*`或Git对象，不对Git做gc/prune；不删活跃DTC-L1/EP-L2/AWMA/C16/AI trace/raw/registry/唯一binary/源码，不动模型权重、密钥、其他用户数据。** 已审核的164备份不自动等于“可删除源科学原件”。

## 1. OLD174（旧2233）新短Goal：`OPS_OLD174_FAST_WORKSPACE_RECLAIM_V8`

**该窗口为唯一source owner/唯一释放owner**；继续原Codex窗口、原ops分支，先读本V8、旧V7与R13。不得重启旧R13 Goal或恢复旧已删目录。新报告写独立V8 review pack，保留旧日志/hash/Git identity。

1. **15分钟内只读定位与实时底线：**报告`/workspace`/`/tmp`/`/root/share`文件系统及设备号、实时可用Bytes、与Lane5 workspace的同FS证据、4个Lane5 PID/start_ticks/lease/current registry的只读关联。使用当前`lsof/fuser/proc fd/cwd`（若可用）排除运行消费者；不要以mtime旧代替未使用。元数据扫描nice/ionice，限定候选前2层与小清单，禁止对整个410GB worktrees和117GB repos重新全盘hash。
2. **按真实allocated占用优先审3组历史冷对象，并检查是否仍存在：**
   - **P0** 历史V3清洁RTL `build` 编译产物（旧V7估算约10.20GB），C2P/M2D旧build约1.43GB；只找经Git/输入可重建、无PID/FD/registry/近期科研读者的**确切子目录和文件**，保留不可再生的PPA/signoff/raw/receipt。
   - **P1** 先前旧174 R10审计的 `/tmp/m5-gesu-unpack-check.{FGnex7,F9XDGy}` 作为两份独立重复校验副本候选，历史共约1.99GB allocated，canonical`/workspace/m5-trace-immutable/gesu/gesu`与`gesu.tar.zst`必须留。先验`/tmp`是否真占用同overlay、每一份内容hash及外部消费者；旧R10只标记**未获自动源释放授权**，不能复用旧PASS充当本次授权。
   - **P2** 原先归档/完整恢复的R1/R1R/R2历史`.vvp`（历史总约10.15GB allocated）及确切冷的非唯一构建副本，需重核当前存在/消费者、164全量恢复闭合、是否有用户具体manifest授权。**目前旧证据注明原`.vvp`一律SOURCE_KEEP；本V8不授权删除原件**，只能形成集中批准表。已释放的PolyBench A/B目录不得再列。
3. 为每一个P0/P1/P2实存候选生成准确`SOURCE_COLD_PRIORITY_V8.csv`：`realpath, st_dev, st_ino, nlink, owner, project, source commit, stat allocated, logical, live FD/PID/registry, canonical source/config/raw status, archive root/hash, restore command, release class`。区分：`PREVIOUSLY_RELEASED`、`SOURCE_KEEP`、`PROVEN_REBUILDABLE_SCRATCH_RELEASE_GATE`、`READY_FOR_EXACT_USER_APPROVAL`。源是唯一科研数据或归属不明时严禁作删除候选。
4. **可马上真实释放的仅有此前V5已明确授权的、经此刻重查无消费者且源/目标/可重建闭合的确切非唯一scratch文件。** 源释放逐个exact path+expected dev/inode/nlink/size/hash compare-and-act，禁止通配/递归rm/目录整树删除；所含目录若混有科学结果，只细分文件，无安全精确列表就STOP并交审批。
5. 科学原件/归档副本、旧`.vvp`、trace、signoff/raw，即使164 hash全验，也只给用户**1–3组按allocated净释放排名的准确集中批准manifest**，列出恢复演练与可能影响；没有具体清单的明确授权不删除。此V8不是“删除所有不活跃数据”的总许可。
6. 每批释放独立取OLD174`df -B1 -P /workspace` before/after，并仅以即时变化报告`ACTUAL_SOURCE_DF_GAIN`；并行其它进程写入需分离，不能把累计归档量当作新可用量。第一批安全净释放达到≥2GiB即立即发出Lane5独立preflight请求，目标≥8–10GiB；若达不到，30–45分钟交待批准确manifest请用户集中批准，避免为找完所有候选耽误4路运行。
7. 最大90分钟的首轮紧急源侧任务；不抢Lane5/RTL R3的CPU/RAM/IO lease，不改其代码/目录/运行、无daemon或循环监视。GitHub仅push旧source ops分支`swayhrl/gpu-l2-cache-verilog:hrl/ops-174-source-audit-exec-v1`与既有共享bridge的带hash小receipt；不push到Lane5/科研分支。

## 2. 174-new（新2239）新短Goal：`OPS_174NEW_ARCHIVE_VERIFY_FAST_V8`

**该窗口为唯一164 target归档/恢复owner，不删old174源。** 继续原ops执行分支，读同一V8及R13真164/SSHFS闭合，不重启旧10小时Goal、不重做36批Git包或35片PolyBench迁移。

1. 同步15分钟内fresh验证`/root/share/mnt164`是真实164 SSHFS，目标用户可写且位于允许根`/home/shared/huangrulin/host174_storage_recovery/...`，对真实FS/mount/free做read/write/close/reopen/hash小探针并清理**仅自己探针**。如果挂载、164端目标容量或权限发生变化，立刻fail-closed而不是存到174 Share伪装164。保护Share40GiB底线，现有bridge空间有限，优先小而严的streaming传输，不产生未计费临时目录。
2. **与旧174同时做只读目标资产复用索引**：读取R13`PROJECT_INDEX_R13_V9`和已有V3、C2P/M2D、R1/R1R/R2完整接受manifest；判断哪些目录已有准确的164校验和可执行恢复方法，可省重复上传。不要因名字相似合并不同hash/source。
3. 收到旧174的精确新candidate manifest后，仅一个旧V5/V6协议限定的单流、≤30MiB/s、≤512MiB/batch逐批复制；每批和整组必须有源+真实164 target全量hash/size/relative path/permissions，关闭重开后复核，并至少一个实际恢复演练（无覆盖原目录）。如源文件在复制期间修改，保持SOURCE_KEEP；不在同目录覆盖历史archive。
4. 向旧174source owner提交`DEST_VERIFIED_AND_RESTORE_READY`的精确签收，以及科学原件所需`READY_FOR_EXACT_USER_APPROVAL`列表；source是否释放、何时释放**完全由旧174在真实旧源无活跃引用+具体授权+再次hash条件下决定**。目标端禁止自己清理旧源、修改Lane5额度/registry、kill任何作业；不可为追求16GiB结果配额去删已经接受的raw。
5. 快速发布`TARGET_ARCHIVE_V8_RECEIPT`和`SOURCE_TO_164_RESTORE_INDEX_V8`（相对路径+实际目标164位置+source identity+SHA+恢复脚本dry-run），每收到一批就回执，不等待长达90分钟大闭合。首批30分钟内让旧174判断可释放；归档吞吐/Share紧张时以既有164完整备份和精确可重建scratch优先。
6. 只push自己的`swayhrl/accel-sim-framework:hrl/ops-174new-164-archive-exec-v1`执行分支及bridge小receipt；R13 frozen review pack和历史科学资产保持不动。无常驻poller/二次迁移/重复工作器，CPU-only、I/O低压，不跨项目抢资源。

## 3. 双窗口+Lane5握手

- 可**并行**：旧174小范围审源/FD/冷资产；174-new复核真正164目标、索引和已有归档。
- 必须**串行的实际破坏性动作**：源释放只有旧174单writer并经exact-manifest和当前引用审查；归档上传只有174-new唯一数据流及已有bridge租约，不让两个窗口同时上传相同目录、同时删除或双开新迁移worker。
- 源每批释放后立刻记录旧174 `df -B1 -P /workspace`，发带时间戳、root FS设备、available bytes、来源项目、文件hash与本批净收益的短通知给Lane5；**只有Lane5**能从它自己的namespace重新审当前用户四路、RAM/disk、16GiB总结果/48GiB硬底线/原72配额和期限。已运行四路继续自己的资源监控，Storage-Ops不能暗改已启动任务。
- 此时四路已由`bad4c6c4`启动，另两个生产/分析Lane尚未把MQ2/RG1作为正式性能接受；不让disk cleanup新开这18个logic cells。Lane3`36e4fb3f`已完成机会证据交接，暂不下发重复Goal。
- 若无合法可释放对象、被占用/无法闭合归档/remote校验失败或恢复边界不明：**STOP在报告与精确用户授权清单**。严禁放宽磁盘硬底线、删Git pack或科学结果、释放仍活跃的文件句柄来硬凑8–10GiB。
