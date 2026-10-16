# EP-L2 / ISCAS2027 review_r8 — 一次性、受监控、低空间工程构建授权

2026-10-17（北京时间）。**用户已明确同意：为加速EP-L2，在旧174上单独设计并启用一次Lane1的低空间R0.1工程构建例外，条件是Lane1和Lane5先独立核准实际资源余量，并继续保护DTC-L1和其他任务。** 本文件是上一轮review_r7的狭义、明确opt-in补充；既不是六个Lane的新初始Goal，也不是降低全部正式生产准入政策。

## 0. 范围与准确输入

- 科学合同：Framework `6c136e2a56a008695f8c8b815723bf8f1a760db9`，协调review_r7 `99e7515f81b0038ac49d274b73f774e8ea801e46`。
- 准备中的唯一R0.1生产源码：Core隔离候选 `c948184504d82b80e23eb3f4ff6cdfd328ba9355`，Core执行分支publication `57e1c363aede1a7790bdf94136d832d35ee7b34b`为同tree；Framework生产输入 `3ab150b3e99ff3ed759b8cdc5154cfb5744042a7`；Lane1状态提交 `85534de235345292a153d9983cfd0d24d8033bb2`。原 `util/ep_l2/ft_lane1/build_r0_1.py` 硬编码48GiB地板+2GiB增长余量，使用 `Registry.build_lease`；Lane5现有 `registry.py` 同样会因原48GiB地板拒绝build lease。**只改外部命令行或创建lease不够：必须保留共享中央registry排他和全部非磁盘配额，同时新增可审计、只允许一次工程构建的例外路径。**
- 最新Storage-Ops两端2026-10-16T16:46Z已公开R1 14/14批DEST_VERIFIED，源依旧全部SOURCE_KEEP；这不是回收量、不能解锁原50GiB。源曾观测旧174 `/workspace` free `30,767,472,640B`（16:38Z）；目标的一条更早快照为 `31,558,250,496B`。两者都不是此刻现场值，更不能在无安全预算时默认构建。
- 本授权覆盖：**在旧174上、Lane1隔离目录内、最多2个编译jobs、一个有界工程campaign**，CMake配置、既定R0.1 binary及必要的21项producer directed test，可发生普通工程编译修补；每一源码/配置/驱动变化都必须产生新revision和准确哈希。任务必须维持审计链、总时间和资源cap。无R1.1/TVD/RO/ideal集成，无GPU长应用、正式五配对、PPA工艺实验，也不批准使用164当编译盘。
- 本次例外的输出**仅ENGINEERING_BUILD_EVIDENCE**：无论CMake/21测试是否PASS，不可自动成为官方R0.1 producing binary、Lane5独立11gate证书或科研可接受应用结果。原正式编译脚本及其48GiB+2GiB/64GiB、正式Lane5 run门槛继续保持；未来要沿用试验binary或修改正式实验空间政策必须另行审查，不能静默提级。

## 1. 分工：仅现有Lane1与Lane5互相核准并执行

**Lane1（申请/唯一构建owner）**：先以只读/低IO方式刷新精确 HEAD/STATUS/RECEIPT、原生产输入和 `pybind11 f90c430c3a1ce8f08c09942a5a1c3a797bb2295b`，对照原入口CMake targets、flags、21项用例。检查旧174真实挂载、各实际写入文件系统（`/workspace`、`/tmp`与results所在的`/root/share`）、自身和其它项目进程、FD、资源registry。仅使用**独立全新**的工程build/log根（不能覆盖正式 `/workspace/build/ep-l2-ft20261016-lane1-r0-1`），绝不改冻结生产Core、源/测试或永久降低原 `build_r0_1.py` 中的默认地板。将计划的构建路径/输出字节上限/唯一ID/精确命令/监控责任/预计持续时间和明确STOP阈值写入 `LOW_SPACE_PILOT_REQUEST.json`，在原Lane1分支发布并回读。

**Lane5（独立资源授权/registry owner）**：不代替Lane1实际编译，也不修改scientific acceptance。独立验证申请、真实空间、主机和cgroup内存、DTC-L1及其他项目进程与I/O、registry锁/boot ID、已有run和build lease、各文件系统剩余量和构建估计的局限。至少用短时多点观测估算共享磁盘写入/突发风险；历史R0/R1最终build占用0.71/1.01GiB只是参考，**不能直接充当瞬时编译峰值**。填写真实数字与依据：`entry_free_bytes`、`hard_stop_free_bytes`、`max_pilot_allocated_growth_bytes`、`external_write_reserve_bytes`、`monitor_and_kill_overshoot_bytes`、`minimum_untouched_emergency_bytes`，并对每个实际写盘文件系统重复预算。必须证明：
`entry_available >= max_pilot_growth + external_write_reserve + monitor_kill_overshoot + untouched_emergency`，
并在整个运行期间执行精确stop余量；所有数值必须>0且有证据或保守显式上限，不能把未知项作为零。CPU=2、memory reservation=8GiB、available RAM在扣减后≥64GiB、中央EP-L2的8CPU/32GiB总预算及不可与scan独占冲突均按原政策维持。**如果不能核准一组足够可靠的数字，发`NO_SAFE_PILOT_ENVELOPE`、不启动编译，而不是替用户编一个较低GiB常数。**
- Lane5审核通过才发布精确`LOW_SPACE_PILOT_AUTHORIZATION.json`（绑定Lane1申请SHA、Core/Framework/driver/vendor、唯一pilot_id、精确旧174host+boot_id、entry/stop/growth caps、TTL、资源配额、preflight及监控计划、科学用途禁令），并在Lane5执行分支推送回读。只授权这个pilot_id。用户已同意此**条件性一次工程例外**，在独立通过后不必就普通工程预算明细重复问用户；超出一台主机/一次工程campaign、需减少其他项目保留空间、或不能定量安全时，必须回报用户另审。

## 2. 最小工程实现；默认绝不绕过正式registry

- 先审查原生产驱动+ `util/ep_l2/ft_lane5/registry.py`：`Registry.build_lease()` 内 `Registry.admission()` 同样强制48GiB，因此**禁止**在没有中央登记时直接开CMake，也不能简单猴子补丁、修改 `RUN_REGISTRY.json` 而不加永久`REGISTRY.lock`。
- Lane5实现一个*独立*、显式opt-in、可测试的`ENGINEERING_PILOT` lease/admission路径；建议复用现有 `Registry.locked()` 的永久 `flock` 与原 `resource_leases` 结构，在锁内保持CPU/内存总和、active owner、host boot身份、sim/scan规则，仅对**所授权pilot_id**替换 **build-entry 磁盘子门槛**；原 `Registry.admission`、`Registry.build_lease` 和所有正式simulation / build callers的48GiB检查字节不变。若额外lease字段破坏已有consumer，先修兼容与回归后才能继续。保存精确lease/进程身份，异常也必须释放；拒绝同pilot_id第二次claim，跨进程重启也不能消除审计。
- Lane1采用独立 `engineering_pilot` runner或在**新审查的opt-in wrapper**中调用原build命令和测试矩阵；从准确源码导入可重用的`repair_commands`，保证CMake target list、编译参数和宏/断言与原正式driver一致。**不要直接删改正式生产driver/registry中的48GiB判断或重用正式输出目录**。显式`--pilot-id`、`--authorization`和一次性执行开关；默认dry-run；`source/driver/vendor/mode`身份不一致就STOP。新输出root不应是符号链接或覆盖原历史结果。
- 实际运行前和拿到独占pilot lease之后重新检查全条件；在构建和定向测试阶段对**真实f_bavail**、自身增量allocated bytes、结果Share挂载容量、cgroup/host可用RAM、进程组、CPU和超时做周期监控；监控间隔不得大于2秒，避免用root可用`f_bfree`冒充非root `f_bavail`。超过任何resource cap、其它项目出现资源风险、DTC-L1状态不明/文件系统身份改变或无法持续监控，立即只终止**本pilot自己**启动的进程组（TERM后必要时KILL），记录退出码和失败/剩余目录，不杀其它项目。
- 一个有界pilot campaign可以在同一审计和上限内解决普通C++编译/fixture问题并按修正版本继续，但每次变化必须保存原身份和新源SHA、重新冻结与经过独立准入审计；不能跨出原授权资源/时间/输出上限、不能自动全量clean/rebuild或无限retry。若源改动触及硬件语义或科学合同，停止报告。结束后归还中央pilot lease并设token不可再用，记录`COMPLETE_ENGINEERING_ONLY`或`PILOT_STOPPED_...`，不对正式二进制发布`runtime_ready=true`。
- 先用模拟资源/假registry至少覆盖：floor不足但合法pilot允许、过期/伪造许可拒绝、单次token拒绝重放、CPU/内存超额拒绝、其它活跃lease并发冲突、错误host/boot或源SHA拒绝、正常资源地板不变、监测超限只kill pilot、失败仍释放lease。通过后才向真实中央registry提交一次性授权登记；普通小工程问题可自行修复，无需让用户审批测试脚本排版。

## 3. 与Storage-Ops和六Lane自动续行协同

- 保留review_r7的**唯一Lane1 GateWaiter**作为**正式50GiB构建入口**的等待器；不要让工程pilot和正式入口在两个进程里重复构建。先检查已有GateWaiter/PID/锁，如果正式条件提前达到，优先唯一正式build，**取消工程pilot**。若pilot在进行，标准等待器只记录、不执行，直到pilot结束与资源/正式源复核。
- Lane2/3/4源码准备、Lane6英文EN-v2写作仍可并行，不向pilot索取正式binary或运行自己的C++大构建；Lane5做pilot安全复核不能同时在旧174开启未经授权的应用模拟。
- Ops旧174/174-new维持V7：S01/S02源已各回收、R1等冷项目有独立copy和restore合同、所有R1/R1R/R2暂为SOURCE_KEEP，不能因pilot磁盘紧张而擅自删、压缩/清空或修改冷项目与Git pack；归档byte数不等于释放byte数。
- 原应用科学接受0 pair，旧R0/R1全部SUSPENDED；工程pilot的21 directed checks即使通过仅属于工程验证。后续只有**正式 producer binary**（经现有标准或未来单独修订合同）+Lane5独立11 gate/current acceptance+正式resource admission才能启用五负载B16/U_WB16。一次工程pilot批准不能传播为通用生产实验授权。
- 输出要有：Lane1 `LOW_SPACE_PILOT_REQUEST`/`ENGINEERING_BUILD_RECEIPT`、Lane5 `LOW_SPACE_PILOT_AUTHORIZATION`/`INDEPENDENT_RESOURCE_GATE`，共同准确记录实际执行、计时/peak bytes、外部写入约束、停止原因、lease id、源差分与远端SHA，以及是否仍然低于原正式50GiB。只stage自己的新增文档/工具并远端readback，不覆盖已有STATUS/RECEIPT中的冻结科学终态。

## 4. 必须停下的人审边界

下列事项**未被本次用户同意授权**：降低正式应用运行空间/当前实验预算；改变B16/U_WB16资源、bank/copy时钟、host prefill语义；在164或其他机器构建；对DTC-L1、C16或未知其他用户数据迁移/删除；Git gc/prune；把engineering binary变成正式性能证据；没有Lane5认可数字就启动CMake；多个并行工程pilot；共享配额无法登记时无锁构建。

**当前下一动作**：给**Lane1和Lane5两个原有Codex窗口**分别发送本r8链接；Lane1先提出准确请求，Lane5独立复核、批准或拒绝。仅批准后由Lane1一次性pilot execute。六Lane的review_r7其余工作照常并行，迁移两个窗口不重启。
