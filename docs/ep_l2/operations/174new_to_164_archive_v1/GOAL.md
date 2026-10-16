# Storage-Ops Goal｜174-new → 164 归档与174工作区容量恢复（V1）

**任务性质：独立的Storage/Ops任务，不属于EP-L2 Lane 1–6，也不更改科学合同或模拟器配置。**
授权背景：用户同意在六Lane进行期间，由174-new单独审计、经真实164 SSH路径归档已完成历史数据，并对被严格证明安全的源文件进行有界清理；要释放的是Lane5所在实际`/workspace`文件系统空间。Ops主线仅在当前窗口连续执行，不开重复任务、不重启Lane任务。

## 0. 完成定义与科学/数据边界

- 成功结果必须同时证明：(a)归档数据在164真实服务器的大容量存储目录下存在且完整；(b)只有获得授权并通过所有安全门的源对象才被移除；(c)**Lane5实际`/workspace`所在FS**的空闲字节实测增加，满足既定48GiB floor，且有足够构建峰值余量；(d)原始结果/完整科学provenance与当前任务不受破坏。
- “复制到`/root/share/mnt164`”不是“传到164服务器”；该路径据已知审计只是174 Shared上的目录，剩余空间约48GiB，禁止默认将其作为真实目标或中转。须走经核实的164 SSH/rsync（或已证实真实164远端挂载）。
- 原六Lane独立运行与共享registry由Lane5管理。本任务**不持有或改写它们的运行锁、结果目录、worktree、binary、主分支或科学CSV**。归档不能删除/迁移仍被使用的输入、唯一程序或证据；不杀他人进程。
- 当前只读历史线索（不是本次实测）：`/tmp`陈旧候选约32.23GiB（M5临时解压/恢复、RTL临时构建、C2P临时构建等），`/workspace/.git/tmp_pack_*`约23.33GiB，另有历史`/workspace/build/postcheck`、`build/review_pack_staging`、`build/sim`。路径大小、文件归属和14天不修改均**不等于**可安全删除。
- Lane5最后在2026-10-16本轮receipt内记录workspace free=50,802,106,368B ≈47.313GiB，floor=51,539,607,552B=48GiB，差737,501,184B≈0.687GiB；**由当前实时测量覆盖该快照**。保持48GiB磁盘门槛、64GiB可用内存、最多2长模拟/8 CPU/32GiB保留内存，不得替六Lane更改阈值。

## 1. 只读预检（无视此节不得开始迁移/清理）

1. 确定174-new当前真实账户、主机、mount namespace与可访问工作区。对`/workspace`、`/tmp`、`/root/share/container-workspaces/hrl-174-new`、`/root/share/mnt164`及候选实际路径执行`pwd`、`id`、`hostname`、`df -B1 -P`、`findmnt -T`、`stat`/realpath；不存在的路径只登记，不自行创造虚假映射。
2. **证明正在整理的源路径确实占用Lane5的workspace FS**。若174-new不能读取Lane5真实`/workspace`，或两个工作空间不共享设备/底层配额，不能声称本地清理会释放Lane5空间。可继续只读列候选，必要时请求Lane5独立回读其`df/findmnt`快照，但不能重启/打断Lane5。目标是同一文件系统的可用字节、不是另一挂载点的释放数字。
3. 读取当前进程、`lsof`/`fuser`可用信息、Git repack/gc/fetch/write进程、文件mtime/atime、目录大小、inode/符号链接/硬链接、所属项目与唯一性。要核查仍活动的EP-L2、AWMA、C16、DTC-L1/C2P、RTL任务，**未完任务输出即使14天未修改也不可删**。
4. 检查164真实SSH：先只读检查已配置的Host别名/known_hosts与以前的已授权连接记录，不输出密钥、token、完整SSH配置到Git。只在已有受信主机身份基础上用`ssh -o BatchMode=yes -o StrictHostKeyChecking=yes ...`做小只读握手；不自动信任未知host key，不改权限，不猜账户密码。确认证据目标是**远端164真实大数据盘**：SSH目标主机、`df/findmnt`、唯一可写的用户所属归档根；不要把164的home/root小分区和模型生产目录当任意归档位置。
5. 目标root：优先复用164上已有明确的用户archive/backup目录或确定由该用户管理的**大容量**数据挂载点下新建独立`174new_archive/2026-10-16/<run_id>`。如果无法唯一确定获准的远端登录身份、路径或host key，**停在COPY_GATE_BLOCKED并询问用户精确`user@host:archive_root`及主机指纹**，不自创目标、不进行真正复制或源删除。

产出先发布`SOURCE_FS_MAP.json`、`REMOTE_164_AUDIT.json`、`CANDIDATES.csv`、`PRECHECK.md`，每个候选标注EXACT_PATH/SIZE/DEVICE/OWNER/ACTIVE_USE/UNIQUE/REPRODUCIBLE/DEST_AVAILABLE/DELETE_ELIGIBILITY。不要为摸清情况递归hash整棵历史仓库或全量原始trace。

## 2. 候选优先级、处理级别

A. **同一目标FS内已停止、可以从确定性来源重建的临时内容**，如特定历史`/tmp`解压检查副本、闲置临时编译对象。若`/tmp`与workspace是不同FS，则清理`/tmp`不能用于满足Lane5 workspace floor，改先找同一FS候选。旧mtime仅作候选筛选；需证明非唯一、无活跃打开/被引用/进程写入、可重建来源。

B. `/workspace/.git/tmp_pack_*`据旧审计约23.33GiB，为高价值但**高风险Git临时对象**。禁止直接`rm`、`git gc`、`git prune`或以文件名“tmp_pack”断言无效。要核对准确Git目录、Git写进程/锁/引用、临时pack是否包含唯一可恢复对象、现有pack/index和`git fsck`健康状态；保留SHA/size/mtime并在164先全量归档、哈希回读。**即便归档完成，对Git tmp_pack源文件执行删除之前仍需用户对具体列表明确批准**，除非该文件已被Git自身可靠机制自动处置；不能自行推断。

C. 历史`build/postcheck`、`build/review_pack_staging`、`build/sim`只做候选清单。里面可能含RTL科学验证报告、唯一产物或活动任务的增量文件，未经逐批非唯一/可重建/不活跃证明不自动删除。历史trace、review pack、Git refs、模型权重、原始log/config/CSV/RECEIPT与唯一binary归档可以先COPY，**不得自行删除源**。

D. 归档操作不要进入`/root/share/mnt164`中转，不改`/root/share/container-workspaces/`权限，不复制`~/.ssh`、私钥或连接凭据。与源文件夹中的符号链接、hardlink、ACL、UID权限边界按报告保留，不递归追随符号链接到任意外部挂载。

## 3. 有界归档执行（所有前置门通过后）

1. 将准备复制的数据划分为小批次，优先恢复workspace 48GiB门槛和**足够实际编译余量**（推荐先争取至少8GiB真实同FS可用增长，按候选实际与构建峰值修订；不是硬件科学参数）。先dry-run并记录精确文件列表，复制前记录source大小/mtime/sha256，复制过程中源文件不得正在被写入。
2. 只允许**一条**限速传输，例如使用`nice`/`ionice`（支持时）与`rsync -aH --partial --bwlimit=30m`经真实SSH直接到164已确认的大盘root；按目标账号权限决定是否需要`--no-owner --no-group`。不使用`--delete`、`--remove-source-files`、`rm -rf`通配批删，不对当前运行的工作树/结果根做`--inplace`写入。不要往remote根目录随机落数据。
3. copy后在**真实164主机**核对文件数量、byte length、完整sha256清单、必要符号链接/权限和source稳定性（复制前后再统计），保存双端校验结果与remote receipt；任何一项不匹配不许释放source。证据包含原始绝对路径到归档相对路径的稳定映射。Git敏感数据与用户信息避免写入公共raw日志。
4. 源清理边界：**只允许**明确判为无活动/非唯一/可重建、且通过完整远端hash校验的**单个已列明临时候选**，逐小批依exact paths进行显式删除。每次操作前再次核验process/open refs和文件身份，清理后立即`df -B1 -P`测Lane5同源FS空闲量。高风险Git temp packs、历史科研数据、trace、review packs和任何不明对象：只复制、不可自动删，列`REQUIRES_USER_APPROVAL`请求用户决定。任何新的活跃写入/变化则暂停该批。
5. 若copy可行但无法释放workspace，报告`ARCHIVE_COPY_OK_SPACE_NOT_RECOVERED`而非成功。如果48GiB floor恢复，通知Lane5在**它自己的容器中**重新量测实际空间并按原门槛决定是否可编译；Ops不得自行降低资格门槛或代替Lane5重启任务。可用空间足够才继续其它低优先级归档，不长时间抢IO。

## 4. GitHub审计与交付

本Goal所在协调/发布提交只读。Ops使用独立执行分支`hrl/ops-174new-164-archive-exec-v1`写状态和紧凑证据，不对EP-L2的六个执行分支、冻结结果或协调分支push。建议路径：
`docs/ep_l2/operations/174new_to_164_archive_v1/receipts/<run_id>/`

产物（没执行就明确NOT_RUN、不编造）：
- `STATUS.md`：真实阶段PRECHECK/COPY/VERIFY/SPACE_RECOVERED/BLOCKED等、主机身份、是否已动source、下一动作。
- `SOURCE_FS_MAP.json`、`REMOTE_164_AUDIT.json`（密钥和机密信息全部脱敏）、`CANDIDATES.csv`。
- `TRANSFER_MANIFEST.csv`：每条exact source、destination relative path、size/hash、copy status、verify status、source action。
- `SPACE_BEFORE_AFTER.json`：源/目标设备、测量时间、free bytes、变化、Lane5独立复测结果（未取得则null）。
- `ACTION_LOG.md`：执行命令（不含凭据）、退出码、是否真正执行、必要参数；`APPROVAL_REQUIRED.md`：需要用户裁决的候选。
- 只提交小体量日志/manifest及164归档路径/校验和；大数据与凭据不入Git。
- 普通权限/rsync/script错误自己修复并继续；如果源路径或164实际SSH/目标根无法确定、涉及数据不可逆删除或跨项目使用，则精确暂停并提一个最关键问题给用户。
- 提交前`git diff --check`，仅stage本路径，commit/push后fetch回读准确SHA。无法push须说明阻塞并保留本地receipt，不假称远端已写入。

## 5. 开始与退出

从只读盘点立即开始，不因六Lane运行而等待；不得在资源紧张时并行启动大量hash/rsync进程。若目标路径已确认且所有门通过，允许小批复制归档与受限临时清理；否则止于有质量的候选清单与单一待确认项。退出时必须明确“哪些byte真的释放了Lane5 workspace”，而不是仅报告复制了多少GiB。
