# Storage-Ops V5｜修正桥接路径，优先能够恢复空间的归档

2026-10-16。承接用户授权的V4，原V1–V4有关唯一科学数据、Git源文件删除审批、专属164目录、最多512MiB/批、Share可用空间和Lane1/5资源门槛继续有效。本文件是执行次序/证据审阅，不宣称任何新操作已由ChatGPT在服务器执行。

## 1. 已读取的准确快照

- 174-new目的侧Framework分支`hrl/ops-174new-164-archive-exec-v1`，已发布HEAD`466f725a6210b1030fa57d8b9a07d0c83434c6e4`；证据位于`docs/ep_l2/operations/174new_to_164_archive_v1/receipts/20261016_storageops_03/`。最新冻结回执显示15/36 Git临时pack文件已复制，4,833,673,396B≈4.502GiB，源/Stage/164 SSHFS重新打开后SHA256一致；原始源文件仍KEEP，空间实际释放0B。该快照不是对当前正在执行批次的实时观测。
- 旧174源侧在**另一仓库**`swayhrl/gpu-l2-cache-verilog` 的`hrl/ops-174-source-audit-exec-v1`，准确提交`84eec175760f735848746835b2bb90936e1767e0`；证据`docs/ep_l2/operations/174new_to_164_archive_v1/source_receipts/20261016_storageops_02/`。源侧源pack复核SHA一致，源KEEP；两批可重建、无活跃引用的历史Verilog编译产物：S01 52个`.vvp`总418,020,580B，S02 50个`.vvp`总403,579,225B；待合规桥接和真正归档验证。其Verilog/filelist源快照保留，不动其它文件。
- 174-new目标侧已实现可写164专属root及跨旧174共享Probe，但**实际Stage根放在禁止作为V4桥接的** `/root/share/container-workspaces/hrl-174-new/staging/storage-ops-20261016_storageops_02`（路径首尾空格仅为排版，不是路径本身）。旧174源侧因V4桥接根 `/root/share/host174_storage_recovery_bridge/20261016_storageops_02` 当时不存在而拒绝新批次，是合理的。源/Stage/目标内容的SHA一致使已归档文件在字节层面可当保留的备份副本；不能因此把不合规中转过程追认成V4合规执行，也不能据此释放源。
- 源Git `git fsck --full --no-dangling` 90秒超时；对已完成的临时pack副本执行`index-pack`报告`early EOF`，其独立可索引性或源对象恢复价值**未知**，不是“安全可删”的证明。Git pack不删除、不开展`git gc/prune`，任何后续删除需要单项用户明确批准和合格对象/引用审查。
- 最新目的侧空间记录源旧174 `/workspace` free 40,524,115,968B≈37.741GiB，距50GiB（48GiB floor+2GiB编译增长）约12.259GiB；不是归档4.502GiB就释放了4.502GiB。共享目录Stage空间不计Lane5 recovery。
  
## 2. 174-new下一阶段动作：在批次边界纠正路线

1. 若有单个rsync/SSHFS传输正在运行，不强制kill、不删半成品、不移动打开的文件。**该文件安全完成/失败并落日志后，在下一批启动前暂停新Git-pack批次调度**。若当前36批已经全部复制，则不重复复制；报告对应现有manifest和SPACE_NOT_RECOVERED。
2. 只在共享ext4上V4明定的任务专用路径 `/root/share/host174_storage_recovery_bridge/20261016_storageops_02` 创建root、严格控制不碰已有文件。174-new生成几字节唯一nonce，完全关闭后记录SHA/realpath/dev/inode/size；将准确路径/hash和可读完成标记提交到目标侧独立执行分支。旧174源侧读取同一路径独立核查SHA和inode，双方确认后，探针由创建方删除并检查两端消失。旧禁用目录不再用于任何**新文件传输**；历史已核验164副本只作保留备份，不需仅为修正中转路径而重复归档。
3. 确认164 SSHFS根仍为V4授权唯一归档root且可写，继续一条限速流、≤512MiB每批和每批完整source/bridge/SSHFS readback哈希。只有源侧标记READY、目的侧按batch发DEST_VERIFIED，源侧才评估原Goal已经授权的低风险源清理资格。Git pack保持KEEP并单项另行报批。
4. **优先S01/S02历史`.vvp`及其它经同等审计的可重建scratch，而非继续把36个Git临时pack全部复制当作空间回收。**这两批合计约0.765GiB，即使全部合格回收仍不足恢复Lane1/5构建。因此源侧同时做有界且项目保护的更多可重建临时内容候选审核，目标是实测至少50GiB free（以Lane1准入脚本和真实df为准），不因忙于备份高风险Git pack推迟低风险回收。
5. 如果用户后续确实希望继续完整备份所有Git pack，可保留现有15批与剩余21批清单作为**低优先级纯备份工作**；任何批次开始前仍须合规stage、有资源余量、不影响六Lane。即使全部36批完成，不自动允许删除任何Git pack。

## 3. 旧174源侧下一阶段动作

1. 在旧174真实namespace核对V4桥接目录新nonce，在自己的独立repo/分支写跨容器SHA与inode回执；没有探针PASS不启动S01/S02。
2. S01/S02仅精确选择历史`.vvp`编译产物，保留Verilog/filelist快照，检查进程/FD/mtime与源文件身份稳定；逐个文件hash、上传校验、复测，取得174-new SSHFS DEST_VERIFIED后才逐具体路径释放符合低风险条件的源编译产物，不能扩大到整个目录。已归档的Git临时pack均维持SOURCE_KEEP。
3. 有界筛选更多大且可重建、非活动的scratch；不能仅凭名字或14天年龄猜。归档/删除各自提交真实source/action/provenance；每释放一小批即在旧174跑`df -B1 -P /workspace`，达到门槛后通知Lane5独立复测。
4. 如果用户已另开Ops源侧窗口，不新建重复任务；不要使多个Codex对同一源对象执行rm/mv/rsync。

## 4. 停止与资格边界

任何时点共享Stage空间不足40GiB、164 SSHFS挂载异常、输入正在写、进程/FD不可确认或SHA不一致，停止该批并保留源。因V4阶段不合规而创建的旧Stage如果已逐文件验证且属本Ops工作，可以由其所有者按精确路径清理，但不可触碰其它容器workspace内容。源侧清理权限仍严格限于原Goal；保护Git tmp packs和所有真实科学原始资产。

旧174实际free容量通过同一文件系统的df展示；Lane5只有在其独立48GiB+2GiB构建增长门槛合格后才恢复编译，不能用归档manifest代替资格。此次V5修正不重启、暂停或修改六Lane科学进程。