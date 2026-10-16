# Storage-Ops V4｜164专属归档根获授权与共享中转默认路线

2026-10-16用户明确回复：“应该是能共享的，你按能共享的安排”，并针对174-new提出的164目录授权问题，批准在下述专属路径内开展归档。本V4优先于V1–V3中“归档根授权尚缺”的状态，不覆盖原科学合同、Lane 5空间门槛、完整性/安全删除门、以及.git临时pack须单独批准的约束。**本文件发布本身并未执行挂载探针、归档或删除。**

## 1. 已获授权的164目录和限制

- **唯一归档目标根**：`/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02`。挂载源经只读证据为`admin-wcx@10.208.130.164:/home/shared`，FSType=`fuse.sshfs`。在当前挂载上对应164导出空间内的`/home/shared/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02`；绝不可把本地Share父目录误认为已归档到164。
- **授权动作**：只读检查目标及父目录权限/realpath/mount身份；在该专属根内创建任务自有子目录；几字节写入、关闭、重开readback、SHA256核对及删除探针；通过后收取经源端manifest冻结且hash核对的小批数据。仅授权这一新目录及其内容，不允许修改父目录已存在`git_packs_20260928`或其它资产。
- 明确不授权修改164已有C16、AI、模型或任何旁支科研目录，不授权新SSH密码尝试、切换账号、挂载重配置、软链接跳出当前目标根、覆盖目录中预存文件或在归档根执行`--delete`。
- 在首次写入前检查`findmnt -T /root/share/mnt164`仍为预期sshfs且有效，归档根不存在意外符号链接/冲突；权限不足则保持`ARCHIVE_ROOT_PERMISSION_BLOCKED`。写入探针使用唯一名字、低资源、超时和失败回滚，目标已存在同名非自有文件时不覆盖。
- SSHFS写完再关闭/重新读取做完整内容hash，可以如实称`SSHFS_READBACK_VERIFIED`，不能冒充独立164主机原生校验；独立SSH登录失败不妨碍现有受信SSHFS路径的使用。

## 2. 两个174环境的共享中转按预设方案执行

- 本轮**优先假设**旧174和174-new的`/root/share`对应同一`/dev/md127` ext4；原始只读设备/df为强证据。但不将两个overlay的`/workspace`误认成路径相通，也不把Shared上有空间等价为获得其它文件访问权。
- 授权专用临时中转根：`/root/share/host174_storage_recovery_bridge/20261016_storageops_02`。只限本次任务，不能作为最终归档，不能使用其它项目/其他用户目录，也不能在`/root/share/container-workspaces/hrl-174-new`内写旧174源文件。
- 先由174-new创建唯一几字节带nonce的probe并close；由旧174源侧Codex只读检查同一路径与SHA256；双方核验后由拥有该probe的窗口清理，记录两端mount/stat/path和hash。**只有探针证实共享可见**才开始文件复制。不能用同盘设备名/相似df代替可见性验证。
- 桥接阶段一条传输流、同一时刻只有一个active batch；每批建议<=512MiB，硬上限1GiB，起始Share free不少于40GiB且全过程不能耗到40GiB以下，实际IO资源占用不得影响六Lane。需要更大归档则拆成小批；如当前空间/IO不足保持`BRIDGE_RESOURCE_HOLD`而不是增配额。
- 流程：旧174源侧只为非活跃、授权范围、具体已审核源对象计算hash/manifest → COPIED_TO_BRIDGE且stage与源hash一致 → 原子生成READY manifest → 174-new核对READY/大小/hash、复制到164专属root → close/reopen并对整个文件计算hash，写DEST_VERIFIED证据 → 旧174检查源文件未变化并记录SOURCE_KEEP或基于明确授权和删除资格实施SOURCE_RELEASED → 174-new删除自己任务唯一创建且已验证不再需要的bridge副本，复核Share用量。
- **源释放条件没有降低**：不得因为用户同意“共享中转”而自动删除原始trace、raw/CSV/配置、review-pack、唯一程序或仍活动文件；旧`/workspace/.git/tmp_pack_*`须具体对象的Git对象完整性/引用/锁审核、164完整备份和用户**再次明确批准**，即使源端看起来闲置也不授权通配删除。
- 旧174`/tmp`若能定位确定性可重建的非唯一不活跃编译/解压scratch，严格按V1–V3安全门处理；无需等待将所有历史数据归档。只读属性不足时先报告对象级候选，不扩大清理权限。

## 3. 两窗口当前分工与确认

**174-new目标Ops原窗口**：读取本V4与此前SHA`44dc0094068de01cfe1a52677f340533c95340c4`的只读审计；先目标根微探针，再Shared桥接探针并向旧174提供其精确路径/sha；成功后担任目标接收与SSHFS读回校验者，继续原执行分支`hrl/ops-174new-164-archive-exec-v1`发布新revision。

**旧174源侧Ops窗口**：必须运行在能访问Lane 5真实`/workspace`和旧`/tmp`的旧174环境；消费V4后只读验证Shared探针、检查真正旧174`/tmp`/Git候选的具体可用空间与文件权限，选择最小风险批次，准备source/bridge manifest。使用独立分支`hrl/ops-174-source-audit-exec-v1`，不与174-new抢push。若旧174本身也有确实指向164的SSHFS挂载，允许省略桥接直接按同一独立归档根与安全门复制。

**Lane 5**：此前准确挂载receipt`2fb8a6d1144f6fce038f51e60192f9fa8b0207af`已提供，不再重复读同样数据；待旧174实际释放候选后在Lane5自身namespace复测`df -B1 -P /workspace`并核对Lane1 R0.1构建admission。以前48GiB floor加2GiB构建增长对应目标50GiB，旧174源侧空间释放目标约9GiB起，具体采用最新df。

## 4. 审计与停止条件

在GitHub各自执行分支留下源SHA、exact path、bytes、活动引用检查、候选风险等级、远端路径、源/stage/destination SHA256、SSHFS readback验证范围、阶段状态、空间before/after、需要进一步审批的列表。不修改当前协调/科学分支，不启动或重启EP-L2任务。若探针失败、目标不是预期FUSE、Share不足40GiB或源资格无法证明，则停止该批并如实报告；不要凭本V4推断任何迁移/删除已实际发生。