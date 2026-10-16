# Storage-Ops V7｜优先冷项目可恢复迁出，快速解锁EP-L2与DTC-L1（2026-10-16）

> **用户新授权：**为赶ISCAS 2027进度，在旧174寻找当前不用、占空间大的**用户自有历史项目数据**，将其完整迁到164，逐原路径记账、验证可恢复后从旧174有界腾退，未来需要时再原位迁回。此授权改变V6“完成备份一律SOURCE_KEEP”的默认做法，但**不允许盲目移动整棵项目、跨用户处理文件、清理Git对象、动热数据或把归档算作释放**。本文件是现有两个Storage-Ops Goal的增量CONTINUE，禁止新建执行窗口或重启工作，发布不代表服务器已执行。

## 0. 回读与当前执行边界

- 原V1–V6保护范围、合法bridge/164 root、单批≤512MiB、30MiB/s、Share空间≥40GiB、单条源stage/目标SSHFS传输流、真实df回收量、双方独立核查及SOURCE_KEEP Git pack仍有效；与本V7相冲突的**已批准冷项目可恢复迁出**优先按V7的严格分类执行。
- 源侧**第三仓库** `swayhrl/gpu-l2-cache-verilog` 分支 `hrl/ops-174-source-audit-exec-v1` 最新已知发布 `5e5ca557e35bb4763d2af4bac9752fad3dc0d3bd`；旧174 S01 52个`.vvp`已按V5独立经164 `DEST_VERIFIED` 后精确释放，`df /workspace`紧邻前后由38,039,896,064B→38,457,888,768B，**实际净+417,992,704B**。其它原始数据、Git pack均未动。S02仍未stage、待目标S01 closeout。
- 174-new目标侧 Framework分支 `hrl/ops-174new-164-archive-exec-v1` 已知发布 `50b65787764a927eca0ea9780c46b135c075ca33`，rev05 S01 52个文件完整SSHFS close/reopen SHA PASS，并作1文件抽样恢复（不是全批恢复）；其时尚未消费随后源侧释放回执。**优先双方闭合S01，再按原V5执行S02**；V7不得推迟该步骤。
- 当前已测源可用空间约35.8GiB（受其它写入影响会变动），Lane1官方R0.1构建仍按旧约定需要真实workspace≥48GiB并另有约2GiB增长余量、可用RAM≥64GiB。目标首先**真正净增加至少15GiB，争取20GiB以上额外空闲增长**，并以Lane5独立live check是否达到50GiB及DTC-L1连续写入余量为准；不是要求全部候选都迁完才通知科学Lane。**V7不自动调整任何构建/仿真门槛**。
- S01/S02以后无需反复审已完成hash；已完成的S01回执保持不变。所有头部信息只是快照：执行前各原窗口先fetch自己最新HEAD/STATUS/RECEIPT、真正挂载/进程与源数据修改情况。

## 1. 与仅归档不同的状态：COLD_OFFLOAD，不要求每个输出可重编译

**区分两种完全不同的操作**：

1. `ARCHIVE_COPY_SOURCE_KEEP`：仅复制到164并保留旧174文件，适合活跃/唯一/未证明空闲数据，不改善源盘。
2. `COLD_OFFLOAD_RESTORABLE`：针对确证**无人使用、无即将执行任务依赖的用户自有历史数据**，完整保存原文件、层级、哈希及必要元数据到164，通过端到端恢复检查后从旧174释放**准确列入manifest的文件**，以后从164取回**相同字节/路径/元数据**。这是本次用户新批准的优先空间恢复路径。对于这样的精确字节冷迁移，**无法确定性重新编译不等于不能迁出**：只要完整保存和可恢复到原位置、没有存活依赖，就不需先重建编译产物来证明可移动。不可把此结论推广为“无需追踪provenance/项目使用状态”。

**进入COLD_OFFLOAD_RESTORABLE的所有门槛**（缺任何一项，保留源并报告）：
- 旧174项目真实归属已核验为用户可管理、非其他人的共享项目；文件具体所属owner及活动/计划任务被独立审查，不依赖root UID、目录名称或mtime猜测。近期要跑的EP-L2/DTC-L1及它们的input/trace/holdout/run registry/runner/binary、C16/AWMA/C2P其它活跃producer/consumer优先保留。
- 精确列出**只读/已封存**的文件、子目录、run-key/producing source/config（若有）、是否原始唯一科学数据、引用关系。检查正在运行的进程/FD/cwd、正在写文件、中央及项目registry/queued jobs、计划在投稿前重用的trace和所选目录是否有路径依赖。仅“未发现FD”不能证明没有未来消费者。
- 仅移动有明确范围的数据或build输出**子树/逐文件**；不破坏Git worktree登记、`.git`、objects、submodule、源码/配置authority、符号链接/硬链接关系。无法无损表示权限、mtime、稀疏分配、软链目标、hardlink或特殊文件则单项停；不通配rm整个项目文件夹。
- 旧174源端产生`OFFLOAD_MANIFEST`：原realpath、项目/owner、源namespace/mount、dev/inode/nlink、size与allocated bytes、每文件SHA256、相对目录、mode/uid/gid/mtime以及必要xattr/sparse/symlink信息、任务依赖/冷态证据、目标164精确路径、归档文件集及恢复方法、stage/DEST_VERIFIED/RESTORE_TEST/SOURCE_RELEASE证据。164保存manifest镜像，源侧GitHub及**旧174上不依赖迁走目录的轻量索引**保存位置，保证未来可查询；不在旧源路径自动插入破坏原消费者语义的stub/symlink。
- 174-new在V5专用授权164根 `/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02` 下按项目/原路径写入，用唯一版本标识，**不覆盖既有档案**。全部文件close/reopen逐项完整SHA256；`RESTORE_TEST`必须至少对该类资产从**164 SSHFS→bridge→旧174隔离临时目录**进行小样本端到端恢复与字节/关键元数据验证（不能仅在164原地copy称旧174路径恢复已验证）。完整批次目标hash合格，但抽样恢复严格称sample，不称full restore。孤儿文件或SASS trace中不可解读字节不能因此省去hash。
- 先持久发布两个独立receipt与可执行但默认dry-run的恢复清单/恢复脚本，再由**唯一旧174源侧Ops**核对源未变、owner许可仍有效、所有FD/registry与当前future consumer仍无依赖，使用精确manifest + opt-in释放本批源文件；绝不由目标侧删源。上传的字节不算释放，以每批`df -B1 -P /workspace`紧邻前后差为真实恢复指标，交给Lane5自己容器复核。
- **唯一、无法重新获取/重建的原始科学输入或签核证据**（含review/signoff/raw/trace）默认仅COPY+SOURCE_KEEP；若确需迁出它们，则要另提交**精确目录/项目owner及恢复可靠性**供用户单独批准，不依本文件泛化自动删除。对整目录的自动离线化或高风险不可逆操作同样要求单项批准。

## 2. 快速释放空间：先审这三类候选，而非先设计大系统

源侧V6已发布 `MULTIPROJECT_AUDIT.md` / `MULTIPROJECT_CANDIDATES.tsv`，以下**不是准入成功**，而是新冷迁移选取优先级：

| 优先级 | 准确发现范围 | 观测物理分配空间 | V7调查与执行 |
|---|---|---:|---|
| **A** | `/workspace/repos/gpu-l2-cache-verilog-v3r1-clean/build`、`...-v3r1r-clean/build`、`...-v3r2-clean/build` 中选定历史`.vvp/.o/.so` | **10,201,145,344B（约9.5GiB）** | 优先逐目录检查项目owner/无活跃或未来引用、精确字节档案和恢复方式；虽然重编译工具链不完整，只要满足V7完整可恢复cold offload可迁出**指定build输出文件**。原Git checkout/源/脚本留本地，不移除整个仓库 |
| **B** | `/tmp/c2p-gpgpu-pre-attribution-20260822`、`/tmp/c2p-gpgpu-build-20260821`、`/tmp/m2d-core-g21` 的历史`.o/.a/.so` | **1,429,032,960B（约1.33GiB）** | 和A同样逐项核验冷态、非唯一bin及当前C2P/M2D活跃引用，合格的构建中间文件批次可以源腾退；不要迁活动C2P工作树 |
| **C** | 旧174 `/tmp`根下**814个**历史`.vvp` | **7,003,811,840B（约6.52GiB）** | 来源不完整，不能称可重编译。但用户授权冷迁出时，对确证用户自有、独立旧实验、无人近期消费的**精确文件**，可在逐文件完整档案和恢复测试后有界释放；若属未知人/活跃任务/唯一证据则保留，不能一次性删814个 |
| **S02** | 既定第二组50个`.vvp` | **403,701,760B** | 目标闭合S01后，按已同意V5单批顺序完成。 |

A+B+S02即使全部合格实际释放，也不足当前约14GiB空间缺口；因此**并行审C中至少数GiB冷文件或其它真正闲置、较小风险的旧项目build/results副本**，目标优先让Lane1官方构建合格，不为迁满一个目录等到天黑。冷数据大头只需迁**足以解锁**的一部分，不必整片201GiB pretraces先耗掉带宽。

当前**明确不应作为第一轮自动迁出对象**：
- `/workspace/worktrees/accel-sim-decoupled-l2/hw_run/decoupled-l2-pretraces` 约201.85GB和`.../decoupled-l2-extract`约96.83GB：容量很大但有旧归档进程及DTC trace依赖疑点；须逐消费者映射并获项目owner专门通过，不能按“大文件夹旧”判定闲置。
- 历史RTL `build/postcheck`约83.35GB：是过去明确保留的signoff/review证据，除非另外逐小目录获得用户审批，不把内部`.vvp`当缓存通配释放。
- `m5-trace-immutable`约29.49GB、DTC-L1服务闭环路径、C16交换与模型资产、Git 64.48GB pack、当前EP-L2工作树及所有其他正在写的科学输出。Git tmp_pack仍全部SOURCE_KEEP、禁止gc/prune。
- 其它用户的资料或权限不清文件，即使磁盘日益紧张也不能迁动。

## 3. 最小实施方式与两窗口并行（本周只求解锁）

1. **旧174源侧Ops是唯一源端发现、资格、stage、源释放owner。** 可以边等目标164上一批receiver时低I/O读取A/B/C目录结构，做小规模热引用检测、逐项manifest并发布`COLD_OFFLOAD_CANDIDATES_r1`（列清可动/不可动与理由），但**不再开第二条大文件rsync**，不对全盘做重hash；S01 closeout→S02依序仍先行。
2. **174-new仍是唯一164目标receiver**。并行仅做端侧项目子目录/可恢复manifest/restore流程，不接管旧174源动作；完成一批后核对源侧release回执并标`CLOSED`，再处理下一批S02或cold offload。若单个待迁文件超过512MiB，采用小块有序传输＋每片和整文件哈希、目标原子成品和恢复路径证明，不擅加大批次。
3. **快路径**：S02先结束；尽快完成A/B中首个有明确cold证明的小批，测`df`并验证最小端到端恢复；流程可行后滚动批次，必要时转C。只用现有两窗口和V5 bridge，不引入另一个扫描/复制服务，不扩大操作面。每得到有意义的空间增量即发布简短GitHub`STATUS/RECEIPT`，不必等整个项目迁完。
4. **优先保证DTC-L1与EP-L2**：任何紧邻新运行/当前生产的trace、二进制、配置、run registry、当前工作树都不搬。DTC-L1或C16实时I/O升高时让迁移降优先级，不主动暂停其科学任务；系统I/O有抖动也不会把差额错误归因给某个项目。
5. 启用**只读增量空间归因**：记录同一mount上的`df`、按明确旧项目目录的`du -x`、可能正在增长的输出路径的mtime/size与已确认PID/FD/registry；不推断其他用户的写入归属、不删除其他人的数据。区分`archived_bytes`、`source_allocated_offloaded`、`df_net_gain`、`live_free`和`shortfall_to_50GiB`。旧174与Lane5不同时间测量只可作为时间序列，不强制一致。
6. **触发论文主线**：当**真实**旧174`/workspace`达到原约定Lane1 build所需门槛，源Ops立即发布精确df/进程/owner和提醒；Lane5在自己的容器重新live check，Lane1按最新已发布Framework`3ab150b3e99ff3ed759b8cdc5154cfb5744042a7`+Core`c948184504d82b80e23eb3f4ff6cdfd328ba9355`的唯一guarded `build_r0_1.py`开始构建（须重新核对最新HEAD与源码/二进制身份）。Lane5独立资格→五B16/U_WB16成对run→论文消费。**迁移Ops不负责降低48GiB+2GiB/64GiB及正式应用门槛**。
7. 若A/B/C未能因冷态或所有权证明而安全迁出，提交具体拒绝项和替代小批；再讨论单独用户批准的更大冷科学目录或经过实测的分文件系统准入策略。**不能因投稿紧迫而凭猜测删除唯一科学输入，不能把复制到164伪装为释放源盘**。

## 4. 交付及最小复核

- 两端按原仓库/执行分支分别发布增量revision、精确`OFFLOAD_MANIFEST`、`DEST_VERIFIED`、`RESTORE_TEST`（注明抽样范围）、`SOURCE_RELEASED`及旧174实测`df`。还需一份小型`RESTORE_MAP.md`或JSON（原路径→164路径→恢复命令→sha/metadata），为投稿后把历史实验取回做准备。
- 只stage本窗口负责文件，不force push，不动科学冻结结果/其它Lane、DTC进程或Git pack。遇meta/hash/进程/权限/恢复不一致或疑似唯一数据，立即保留源，报告具体阻塞；普通校验脚本问题自己修并继续。
- V7是**加速空间恢复的有界执行授权**，但不默许关闭双端核验、外部项目所有权检查或把整个科研档案当作可删的缓存。目标是让实验合法尽早启动，而不是把归档系统做完才允许运行。
