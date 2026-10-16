# Storage-Ops V3｜Lane5源文件系统确认后的归档协作

时间：2026-10-16。本修订承接V1 Goal、V2 SSHFS修订，**优先于以前的“Lane5挂载映射未提供”状态**。保留原Goal的所有科学数据保护、双端校验、Git临时pack删除前逐项用户审批、48GiB磁盘/64GiB内存门槛，以及六Lane工作隔离。本文是执行协调，不代表已移动或删除任何文件。

## 一、可信来源、推断与未解决事项

已回读 Framework提交 `2fb8a6d1144f6fce038f51e60192f9fa8b0207af` 的 `docs/ep_l2/review_packs/FT20261016_LANE5_STORAGE_MAPPING_r1/RAW_OUTPUT.txt` 及 `RECEIPT.json`：

- Lane5旧174：hostname `huangrulin-174`，mount namespace `4026534768`；`/workspace` 是overlay `0:156`，stat device=156/inode=32926662；总量3,779,302,981,632B，使用3,543,282,597,888B，可用43,965,808,640B ≈40.946GiB；`/tmp`属于同一个overlay。
- 旧174 `/root/share` 是独立的`/dev/md127` ext4，观测可用47,728,230,400B。
- 174-new原只读审计Framework SHA `44dc0094068de01cfe1a52677f340533c95340c4`：另一mount namespace `4026535153`；其`/tmp`及`/root/workspace`属于overlay `0:258`；总量恰好3,779,302,981,632B，观测可用44,509,552,640B。相隔时间内两个df的used增加与free减少均为543,744,000B，**强烈支持共享底层容量核算**，但0:258≠0:156，不能把不同容器的`/tmp`或`/workspace`路径视为同一目录。是否由174-new的文件删除释放Lane5空间，还需实测Lane5 df确认。
- 174-new `/root/share`也为`/dev/md127` ext4；两个容器共享该后端设备的证据强，但跨容器同路径内容可见性应通过专用几字节探针确认。
- 174-new的`/root/share/mnt164`是实际SSHFS，源为`admin-wcx@10.208.130.164:/home/shared`；已有另一个窗口成功从挂载读取文件。**尚未确认可写、合法的独立归档根及其归档写入权限**。旧174内是否传播该SSHFS子挂载未知。
- 先前旧174另一个Codex发现`/tmp`过期临时候选约32.23GiB及`/workspace/.git/tmp_pack_*`约23.33GiB，只是历史审计线索；不可据目录年龄判断可删除。

恢复目标以最新本机测量与Lane1 admission为准。上述Lane5记录要达到48GiB floor需要约7.054GiB，要达到48GiB再加2GiB构建余量需要约9.054GiB的真实可用空间增量。

## 二、两侧Ops分工，不增加Lane编号

**源侧（旧174）**：优先复用之前能看到真正`/workspace/.git/tmp_pack_*`和旧`/tmp`的独立Codex窗口，或在同一旧174 namespace开独立Storage-Ops窗口。它不属于EP-L2 Lane1–6，不暂停/重启科学任务、不要共享可写worktree。负责定向盘点和判定真实旧174的源数据/安全删除候选。建议写独立Framework分支`hrl/ops-174-source-audit-exec-v1`，证据目录`docs/ep_l2/operations/174new_to_164_archive_v1/source_receipts/<run-id>/`。

**目标侧（174-new）**：继续已有Storage-Ops执行分支`hrl/ops-174new-164-archive-exec-v1`，只复核现有164 SSHFS活性、用户明确授权的归档根及写入权限。不要再重复大规模只读扫描，也不要尝试失败的root/huangrulin/admin-wcx直接SSH口令，不要读写已有C16科学资产。

**Lane5**：已经提供源FS映射；暂无必要重复原只读命令。只有源侧实际释放了空间，才由它在自己容器独立复测`df -B1 -P /workspace`并按48GiB门槛及至少2GiB构建增长决定是否继续R0.1修复。Lane1/5的既有任务不能被Storage-Ops动到。

两侧Ops分别commit/push自己的分支，不同时push同一分支；双方仅消费明确SHAs的source/dest manifest/receipts。旧review pack不覆盖。

## 三、优先执行路径

1. **旧174侧检查164挂载是否直接可见：**只读执行`findmnt -T /root/share/mnt164 -o TARGET,SOURCE,FSTYPE,MAJ:MIN,FSROOT`及`df -B1 -P /root/share/mnt164`。只有其FSTYPE确实是`fuse.sshfs`、指向164，才允许视为直接归档路径；若返回的是父挂载`ext4 /root/share`，禁止误判归档已写入164。
2. **新174侧验证归档根：**在已明确是用户授权的独立Archive目录内才做极小写入→关闭→重开读取→SHA256→清理探针。权限未知只能只读stat并报告`ARCHIVE_ROOT_APPROVAL_PENDING`；无原生164 SSH访问时只承诺SSHFS readback，不称远端native审计。
3. 若旧174直接看到同一SSHFS目录且可写，优先旧174以一条限速rsync将明确、非活跃的源候选直接COPY到授权archive root；源和目的逐文件SHA、大小、稳定性核对。不要跟随源软链接离开授权树，不清理科学原始证据。
4. 若旧174不直接看到SSHFS，允许**考虑**以双方共用的`/root/share` ext4作为非常有限的小批次中转（不是长期存储、也不代表164）。必须先进行几字节自有probe证明旧174创建的文件174-new可读；必须先证明164独立archive root可写；目前Share剩余仅约44.45GiB，必须保留至少40GiB空闲并监控活跃任务。一个活跃stage建议≤512MiB、绝不能>1GiB。超过上述空间/IO限制即停止，不批准大目录整批临时复制到Share。
5. 中转采用可核验的四阶段：旧174创建source hash及stage hash清单，完整写完后发布READY；174-new复制stage到164 SSHFS并关闭/重开hash核验发布DEST_VERIFIED；旧174确认source未变化及删除资格后单项发布SOURCE_KEEP/SOURCE_RELEASED；174-new最后清理桥接stage并核对Share df。中断则原source不动、stage不得当作正式archive。
6. **快速恢复旧174可用空间**可以独立推进候选盘点：针对旧174`/tmp`中不活跃、非唯一、可确定重建的解压/编译scratch，优先用164归档并双端hash验证，随后按原Goal逐项核验并有界清理，记录源/所有者/开放文件引用/再建来源与清理前后df。无法归档/验证时只列出候选，不自动删除；只有用户另行对具体源对象明确批准后才可采用不归档的安全回收流程。长时间未修改本身不是删除许可。
7. **高风险禁止项：**`/workspace/.git/tmp_pack_*`无论已过期多久，在验证Git health/引用/唯一对象并完整归档以后仍要给用户逐个精确路径/hash/风险，取得用户明确批准才允许删；禁止`git gc/prune`或通配`rm -rf`。历史raw/trace/config/CSV/receipt/review pack/唯一binary及活跃/未知文件不可自动删。
8. 每批旧174清理后看`df -B1 -P /workspace`；达到至少50GiB或Lane1更严格准入要求时再通知Lane5做独立复测，不代替它跑科学资格。到达下限不等于已经编译完成；发布应写明实际源释放字节、是否同目标FS、未完成的授权与风险项。

## 四、仅有的下一步证据

源侧需要：旧174 `/workspace`及`/tmp`的同FS盘点、优先级最高的具体旧`/tmp`路径、精确bytes/active refs/reproducibility、旧174是否看见164 SSHFS子挂载、是否能使用小Share桥接。
目标侧需要：现有SSHFS挂载活性、独立归档根的属主/授权与小探针（无授权则不探测写入），不重复浏览C16内部数据。
若以上尚不完整，只交有界只读报告、明确BLOCKED reason，不重复无效检查，也不称已恢复空间。
