# Storage-Ops V6｜旧174→164多项目持续归档与真实空间回收（2026-10-16）

> **V5的增量扩展，不重启Goal。** 本文由用户新增诉求触发：174同时有EP-L2、DTC-L1等实验持续生成数据；在保持V5桥接和文件安全边界下，将一次性S01/S02迁移扩展为有界、多项目、可恢复的存储分层工作。发布本文不表示旧174、174-new已经执行了任意新命令。**两端仍使用各自已存在的Codex窗口和执行分支。** 一切执行前先fetch各自最新HEAD/STATUS/RECEIPT、真实进程和共享资源，不能使用整理快照取代实时检查。

## 0. 已核实的新起点

- 本合同接续V5修订 `011b827c6b686ff4cff0387cafc23977376698de`，以及原V1–V4中专属164归档root、桥接、保护原始科学数据、批次≤512MiB、单流30MiB/s、Share空间≥40GiB和源删除审批等边界。
- **目标174-new**：Framework `swayhrl/accel-sim-framework` / `hrl/ops-174new-164-archive-exec-v1`，最新已独立回读 `ffdcc4aef83ce3de631e3f81ebbeb0de466bc64f`，其中rev04 `STATUS.md`仍为 `BRIDGE_HANDSHAKE_COMPLETE_TARGET_READY_AWAIT_S01_READY`；新commit `PUBLICATION.json`是回读与哈希审计，**不是完成S01**。创建方已清理nonce与READY marker，并发布 `TARGET_RECEIVER_READY.json`；目标观察不能替代源侧自己的absence核查。
- **源旧174**：第三仓库 `swayhrl/gpu-l2-cache-verilog` / `hrl/ops-174-source-audit-exec-v1`，当前已发布 `67b625bb43b69f4241fe4770fb58cd3a13c5020f`，`STATUS.md`仍等待独立目标清理确认；冻结102个`.vvp`清单SHA256 `d34a952f7dfa5fcd0a2a965fc82623a6ff5fb9666f007b7626269e295a8505d7`。
- 最新可引用源侧 `/workspace` free = 40,417,042,432B（约37.64GiB），属于此前快照，`S01/S02 NOT_RUN`，源释放0B；目标侧36批Git pack只是11.563GiB归档副本，所有源pack `SOURCE_KEEP`。
- 两个namespace、两个mount的既有mapping不变：源旧174 `/workspace` 为overlay，旧174 `/root/share/mnt164` **不是**SSHFS；目标174-new的 `/root/share/mnt164` 才是经SSHFS readback验证的164；双方共同使用的**唯一V5 bridge**为 `/root/share/host174_storage_recovery_bridge/20261016_storageops_02`。164唯一授权根为 `/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02`；新项目按该根内子目录分隔，**不得自动创建新的外部归档root**。

## 1. 第一优先：先完成V5 S01/S02，不被V6调研打断

1. 旧174源侧原Ops窗口读取目标 `ffdcc4ae...`，**在自身mount namespace中独立核实nonce文件及READY marker确实都已消失**，并验证 `TARGET_RECEIVER_READY.json` 和源冻结manifest；有不一致则保留所有源文件、停止受影响批次并报告。
2. 源侧独占stage执行权：先核对S01 52个`.vvp`/418,020,580B准确inode/hash/稳定性/活动引用，随后按V5在合规bridge逐文件stage、关闭重开hash、原子发布 `S01_READY`。目标侧只作为receiver，等待准确source READY；它不抢做源目录扫描或另起source copier。
3. 目标侧先复核专属164 SSHFS根和Share可用空间，再按单批≤512MiB、30MiB/s、唯一传输流读取source READY，写164、close/reopen、逐项计算SHA256，发布 `DEST_VERIFIED`（准确源/目标路径/size/hash）。SSHFS重开哈希不冒称164原生SSH端验证。
4. 只有源侧重新核实最新inode/hash/进程/FD/链接、清楚的重建材料及V5既有`.vvp`允许清理范围，才能逐一释放具体文件，不删目录；记录真实 `df -B1 -P /workspace` 前后差异。S02 50个`.vvp`/403,579,225B在S01握手完成后按相同路径推进。保留全部源pack。
5. 源侧S01/S02阶段仍可做**低I/O只读meta扫描**；目标侧可以并行制作长期接收器和清单工具，但不启动另一条传输队列。用户尚未下发本V6时，两端继续已有V5任务，不重做探针。

## 2. 第二优先：扩大旧174可迁移资产发现范围，EP-L2+DTC-L1共存

**只有旧174源Ops维护一个全局候选inventory与可释放决策**，避免跨容器重复删除或相互覆盖；174-new维护目的端164容量、目标清单、接受校验及restore工具。DTC-L1当前有实验持续运行：先识别其当前生产分支、实际运行进程、run registry/lease、结果路径和用户/项目owner边界。若无法确认DTC-L1所有权和活跃状态，其文件均为SOURCE_KEEP，不得因项目名称推测旧run完成。

按优先级进行有界扫描：
- **P0 可重建历史scratch**：S01/S02后，审核旧174源侧审计中三棵干净git checkout构建树（分别约481MB/481MB/466MB的`.o/.a/.so`），逐项确认exact toolchain、源hash、唯一二进制和运行引用。检查其它完整build目录、明确可重建的编译中间产物及确证重复展开目录；不修改clean checkout的Git对象。
- **P1 待证明的`.vvp`**：旧174 `/tmp`直下814个`.vvp`计7,002,033,215B，只是逻辑大小，不是已批准可释放量。先归属源/filelist/toolchain与实验、检查hardlink/其他项目运行引用，再小批逐项处理；旧`v3_bugfix_r1_reqbuf_areq`的89个`.vvp`约932MB因dirty testbench和缺per-run快照仍为KEEP，不能仅因有RTL仓库而称确定重建。
- **P2 研究完成后的冷资产**：包括EP-L2、DTC-L1历史raw/log/config/CSV/plot、trace副本、实验review packs；可由项目owner标注 `COLD_COPY_OK` 后归档备份并验证，**默认SOURCE_KEEP**。对于重复的unpack-check trace目录（各约994MB）、老review包约828MB`.vvp`，先证明完整SHA相同、canonical authority、原实验确已完成及可恢复关系；不按名称、大小、mtime认为冗余。
- **P3 活跃输出及Git**：DTC-L1当前执行/计划重用数据、EP-L2五负载trace/current binaries/runner/registry、其他项目C16/AWMA正在写的路径、git worktree/object/`tmp_pack_*`、SSH凭据、个人配置和唯一原始科学输入一律排除自动迁移/释放；若只需备份，可单独提出手工批准范围，不覆盖源。
- **P4 盘使用分布**：在源真实namespace下按mount有界读取 `df`、`du -x` 或等效元数据，识别占用前列的cold worktree build、results、tmp、下载/解压副本，防止只盯`.vvp`；避免全系统遍历造成DTC-L1、EP-L2运行I/O争用。不可遍历其它命名空间当作源权威。

### 并行分工

| 原窗口 | 可在S01/S02期间并行做的事 | 独占/禁止 |
|---|---|---|
| 旧174源侧Ops | 有界目录空间热点、资源占用/进程FD、EP-L2/DTC-L1 owner inventory、重建资格、候选收益排序；源stage与后续精确release | 唯一源准备、READY、release owner；不得启动第二个source copier；大范围hash/du让位于活跃实验 |
| 174-new目标侧Ops | 独立检查164容量/归档目录/已有清单、建立接收脚本、恢复测试方案和分项目目标索引；消费现有source READY | 唯一164 receiver和DEST_VERIFIED owner；不得替旧174判断某文件可删除、不得并发多rsync或擅用源目录 |
| EP-L2和DTC-L1研究Lane | 继续各自科学任务；若有新写入的重结果，向源Ops提供owner/活跃路径、retention/冷归档参考 | 不参与迁移删除，不让迁移任务重写活跃result、runner、registry及Git源码 |

## 3. 建立最小、可重复、默认只读的归档流水线

先在各自Ops worktree实现**opt-in dry-run**清单和receiver（只读默认，所有 destructive动作独立开关且需显式已审核manifest）；普通脚本工程问题允许自行解决，但不扩权。

- 源索引最小字段：`project`、source namespace/mount及精确`realpath`、size和**allocated bytes**（不能只用st_size）、dev/inode/nlink、mtime/ctime、SHA256、source_commit/source_config/producer/run_key、读者与在途引用、rebuild/rehydration recipe、owner/retention标签、source状态、目标目录、batch id、源删除准入证据。大规模扫描优先stat/元信息，针对具体静态候选再计算hash，不全盘hash热结果。
- 每批状态独立记录：`DISCOVERED` → `OWNER_SCOPED` → `SOURCE_STABLE_HASHED` → `STAGED_READY` → `DEST_VERIFIED` → （需要时）`RESTORE_VERIFIED` → `RELEASE_AUTHORIZED` → `SOURCE_RELEASED`；若只需备份到164则在`DEST_VERIFIED + SOURCE_KEEP`结束，不自动顺延到删除。
- 复用V5专属bridge、164授权root、≤512MiB单批、单rsync、30MiB/s、Share≥40GiB；大文件如果超过单批额度，先规划分块/offset+整文件SHA重组+恢复测试，不直接扩大传输上限，也不把部分上传当DEST_VERIFIED。
- 每批必须源前后稳定性复核，目标经SSHFS close/reopen SHA一致，必要时在独立路径`restore dry run`重组，并保留项目目录结构/可复现metadata。若要真正offload原始raw/trace，需先由相关项目owner验证重建路径、restore可用和后续runner输入查找策略；默认先保留源。
- 源侧释放只针对**已有V5许可或以后经用户批准的精确类别与manifest**，且必须在真实旧174namespace独立执行、逐路径防TOCTOU复核inode/nlink/FD/后续run索引。其它类别即使完整归档也**不构成删除授权**。
- 同时汇总 `archived_bytes`、`source_released_allocated_bytes`、`df_free_before_after`、`verified_restore_bytes`、仍受保护的候选量。跨容器overlay、hardlinks、whiteouts可能导致逻辑删除量≠真实df增量，不准以transfer bytes顶替回收。
- 当源`/workspace`可用空间发生有意义的真实增长，通知EP-L2 Lane5独立在自己容器测量准入；DTC-L1运行用户不因本迁移而自动收到清理或运行命令。

## 4. 48GiB构建安全门槛的澄清

48GiB可用`/workspace`是目前**正式生产活动**的项目保护规则，不是六个Lane读取、静态代码修改或论文写作的固有需求；Lane1官方R0.1 build此外预留约2GiB增长，因此当前目标约50GiB；Lane5正式实验还有64GiB可用RAM、2长模拟/8CPU/32GiB预留、其他项目并发保护。**V6不降低任何既有gate。**

在回收空间的同时，Lane1/Lane5允许各自**只读**审核已有构建树、历史实际编译生成量、旧workspace和Share挂载信息、每类模拟log峰值及合理余量，输出独立的 `BUILD_ADMISSION_ALTERNATIVES.md`，区分“历史构建大小”“本次真实峰值未知”“48GiB策略地板”。如发现安全的不同文件系统构建路径或可支撑更小地板的实测证据，先提交用户审核单独修改准入合同；不得因猜测R0/R1 build只占1GiB便绕过 `build_r0_1.py`。

## 5. 停止条件与交付

- DTC-L1或其它项目source/consumer不明、仍在运行、文件仍有写入或FD、hash不合、SSHFS不可用、bridge/mount身份不符、share<40GiB、有不可恢复或唯一性疑点：停止受影响文件，源保持KEEP。发现科学文件意外删除风险先报告，不盲目复原/覆盖。
- 不删除旧174/174-new/164任何Git临时pack、`.git`对象、研究科学raw/trace/唯一binary；不执行`git gc/prune`，不对整个`/tmp`、`/workspace/results`、项目目录做通配清理。
- 每端仅提交自己repo与execution branch新revision、STATUS/RECEIPT、候选账（包括明确拒绝项及原因）、数据字节/真实df变化与可恢复证据。只stage自己负责的路径，push后fetch/回读，不force push。
- **先做S01/S02阶段和第一轮TOP目录/多项目候选inventory**。之后在有明确证据的最小批次上试运行流程，不能为完整自动化设计推迟真实空间回收；不启用无人值守auto-release、常驻scanner或新进程窗口。
