# Storage-Ops V7｜ISCAS紧急空间恢复：整项目冷归档、可恢复后迁出

日期2026-10-16。**在现有V6/V5两个Storage-Ops窗口内增量执行，不重启Goal，不新增并发迁移worker。** 目标是在保护旧174当前DTC-L1和EP-L2正式实验的前提下，尽快腾出至少足够Lane1 R0.1 build + Lane5正式实验的真实磁盘余量。用户已同意重点搜索旧174中当前停用但占盘大的**本人历史项目线**，先完整归档到164并保留原路径/恢复方法，后续需复用再恢复；不要把实验推进锁死在逐个几百MB的.vvp清理中。本V7不授权删除其他用户或未知owner的数据，不授权Git对象、活跃数据、唯一未校验源资产的删除。

## 0. 最新有界进展与协调

- 174-new目标分支 `hrl/ops-174new-164-archive-exec-v1` 已发布 `ba81c44e41eec16f8ac9b420753327059936fcbd`：S01经目标端SSHFS哈希闭合、旧174确实回收约417,992,704B，已完成bridge清理并准备S02。旧174源侧分支在第三仓库 `swayhrl/gpu-l2-cache-verilog`，已发布 `5e5ca557e35bb4763d2af4bac9752fad3dc0d3bd`。先依既有V5/V6推进S02；本V7大项目审计可同步进行，文件传输仍单流/总限速30MiB/s、≤512MiB一次批次、Share≥40GiB。
- 旧174 overlay容量受其它正在写入的研究影响；不能假设所有free变化来自我们，也不能只靠S01+S02约0.765GiB为Lane1解锁。始终使用**实时**old174 `df -B1 -P /workspace`、Lane5独立复测，以及DTC-L1活跃进程和run root保护。
- 来源V6第一轮topology：`/workspace/worktrees`约410.7GB allocated，`/workspace/repos`约117.7GB，`/workspace/.git`约67.5GB，`/tmp`约49.3GB。父子分项重叠不可累加。大型潜在冷资产包括：三个V3 clean RTL build的约10.20GB编译产物、三个C2P/M2D旧build约1.43GB；`/tmp`直下814个vvp约7GB尚缺完整rebuild provenance；Decoupled-L2 worktree大约330GB包含pretraces/extract，但**存在归档进程或DTC读者风险，当前仍KEEP，不自动移动**；RTL postcheck约83.3GB包含历史signoff证据，需要owner/复现闭合。当前EP-L2/DTC-L1、C16、C2P活跃路径和Git objects继续KEEP。

## 1. 立即并行两类工作，不扩大rsync并发

**旧174源侧窗口**负责：独立核对当前进程/FD/cwd/实验registry/写入状态、项目owner与项目索引，盘点**完整项目目录或成组静态产物**（不只找单文件）占用和可恢复性，生成按实际allocated bytes排序的 `COLD_PROJECT_PRIORITY.tsv`：精确原路径、项目、当前owner、是否有运行消费者、Git commit、必要的source/config/raw/trace与完整相对路径清单、allocated/logical、inode/nlink、hash索引、restore命令、归档目录、release资格和保护项。不要归因磁盘增长责任，更不要动其他人的数据。可同时低I/O进行元数据审计，但整目录全面hash/批次源上传不能抢正在执行的S02/真实科学任务。

**174-new目标侧窗口**负责：164专属授权根下多项目目录和可恢复映射索引、hash校验、按原目录结构分片接收、恢复抽样/完整清单验证、失败后可恢复续传与幂等校验。不要在164另起GPU/编译工作或改变原项目路径；不干涉旧174源侧的源删除决策。

## 2. 按价值/风险寻找真正可offload的历史项目

优先选择**同时满足**本人/已授权owner、当前长期不用、无进程/FD/cwd/registry/未来近期任务引用、可完整归档、有来源与恢复策略、源释放后不会破坏当前DTC-L1/EP-L2/其它活跃项目的一整组历史数据。按目标净回收空间与审计成本排序：
- P0：明确停止使用的旧build、独立历史worktree的可重建缓存和过期scratch；优先审查已识别V3 10.20GB / C2P/M2D 1.43GB的exact compiler input/config/唯一性；若完整目录的后续保留可以通过164恢复而不是本机实时访问，允许提出**cold-project offload**，不用执着于逐个物理输出在旧174现场重编译，但必须证明确无当前消费、全项目/依赖闭合与恢复能力。
- P1：历史完成的占盘较大、自有且无活跃读者的实验数据目录（含cold trace/原始日志），先全量复制+hash和完整restore map；**这些是科学资产，不因164已有copy就自动批准源释放**。对已明确归属、具有完整恢复清单/校验和独立恢复验证的**精确项目/目录manifest**，旧174源侧向用户提出一份**集中批准表**：可一次批准成组迁出，避免大量逐文件人工问答；待明确批准该manifest后才执行源释放。
- P2：部分运行项目中的**确切冷子目录**，只有在正在运行的项目owner明确给出冷/热分界、不影响后续trace重用/holdout且可恢复时才提案；不整目录移动活跃项目。Decoupled-L2的pretraces/extract、RTL postcheck和M5 immutable trace属于高价值潜在冷库，但第一轮**只读**拆分canonical/redundant/active/owner，未批准不得迁出源。
- 永久排除自动释放：`/workspace/.git`、`tmp_pack_*`、Git checkout metadata、当前DTC-L1/EP-L2 run roots/二进制/trace/registry、C16活跃资产、未知owner/其他用户文件、SSH配置及任何未证明可恢复的唯一科学输入。

**每个候选独立记录 SOURCE_KEEP、COPY_OK_ONLY、READY_FOR_USER_APPROVAL、RELEASE_AUTHORIZED（具体manifest）等状态。** 用户对“加快迁移”的原则性授权不等于对上述未知科学项目逐项删除授权；但应尽快提交**1–3个大而明确**的集中批准选项，让用户只需一次确认。可重建scratch已经受V5许可的仍按原精确条件处理，无需新人工批准。

## 3. 真正的冷迁出（需有条件的双端握手）

1. 源确认项目/子目录静止、无live writers/readers、含完整依赖/restore recipe和精确manifest；如果有部分活跃，把它缩成纯冷集合。建立 `OLD174_PATH_TO_164_PATH.json`：original realpath、完整相对结构、archive realpath、source identity hash/manifest/hash算法、source commits/config/trace/run references、预期权限/ownership、恢复路径、完整性、释放和审计签收。
2. 由唯一旧174 source owner按已通过的V5/V6 bridge逐批stage原始目录的确定文件，174-new单流水转164；每批≤512MiB，不以逻辑文件切块绕过单批预算（必要时有序分块、全文件hash闭合），SSHFS关闭重开SHA256，`DEST_VERIFIED`与目标位置索引。遇错误保留源并中断受影响批次。
3. 对整个拟迁出项目的准确清单和全部文件做 `ALL_FILES_DEST_VERIFIED`，抽样恢复检查大小/路径/权限/内容；对关键不可重建科学资产应做足够的独立恢复测试，不因一个小文件的抽样恢复而声称整项目可恢复。建立可实际执行、默认不会覆盖已有文件的restore dry-run脚本，验证可在旧174对应目标路径恢复。
4. **释放源之前**再确认源文件没变化、没有新消费者、符号链接/hardlink/目录挂载安全，且属于V5已授权可重建文件或用户后来明确批准的准确冷项目manifest；有任何不确定保留源，不能按通配符递归rm或rename活跃tree。逐文件精确安全释放后留目录/manifest stub但不能用软链直接替代正在写的目录。记录真实 `df -B1 -P /workspace` 净增；区别 `archived_bytes`、`allocated_bytes`、`actual_df_gain`。
5. 每次源盘真实恢复到足以Lane1准入附近，立即告知Lane5在自己的容器复测资源/registry；无需要为了完成V7完整工具链而推迟EP-L2正式编译。若DTC-L1正在写入增长，按实时余量继续寻找大冷资产，不停止DTC-L1。

## 4. 时间与风险合同

- 追求的是**尽快恢复论文科学进展**，不是完整归档平台：先S02、再对空间贡献最大的1–3个自有冷项目做有界确认和最小归档；小收益或复杂项目先暂停。目标是至少48GiB可用+约2GiB预计构建增长，对本轮来说优先满足正式Lane1当前约50GiB准入政策；如Lane1/Lane5后续拿到足够依据另行审准入调整，不能由Ops绕过或自行改driver。
- 可并行做源资产调查与目标端接收器/索引/恢复工具，但**只有一条实际传输流和一个源释放owner**。V5授权的S02不因V7而停止/重启；其它项目不会因磁盘紧张被kill。
- 不得借“停用”“巨大”“看似冗余”自动定义科学可删；不会在无完整清单和用户批准的情况下迁出有唯一性/恢复风险的科学原件。Git pack仍单项用户批准。两个原Ops窗口在各自分支只更新自己证据、发布准确STATUS/RECEIPT和集中批准建议，不force push。
