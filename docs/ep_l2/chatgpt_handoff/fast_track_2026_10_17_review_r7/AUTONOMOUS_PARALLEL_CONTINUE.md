# EP-L2 / ISCAS2027 — review_r7 六Lane自动续行与共享174安全准入
2026-10-17（北京时间，GitHub证据快照均需以新HEAD/现场复核更新）。

> **给六个已存在的Codex Lane的增量CONTINUE，而不是重新发布初始Goal。** 已有两个Storage-Ops窗口继续原V5–V7，本文不接管它们，也不批准Git pack、冷科学资产或其他人的数据删除。目标：在旧174不断写入、正式磁盘门槛仍未满足时，六Lane先低资源并行；用**一个磁盘条件等待者**在合法准入时自动启动唯一Lane1正式R0.1生产构建；随后Lane5独立qualification/五配对滚动；Lane2/3/4/6在各自有意义的依赖边界续行，不重新编译或扩大无意义的实验矩阵。

## 0. 消费前先检查真实权威和项目保护

- 科学主合同Framework `6c136e2a56a008695f8c8b815723bf8f1a760db9`、审查r5 `77a9fbe937ea23465cf0d0076d2df1909f52d055`、r6 `436bfae2abc73c1dea9e02153bd64c39a029f2c5`；冻结B16_BANKED/U_WB16同一1168 slots/4 banks/每bank每物理周期1op、WBUF8敏感性1160、共用copy latch和固定metadata budget、feature默认OFF。旧R0/R1应用科学SUSPENDED，当前0新合格pair；生产raw/trace/config/old binary保留。
- Lane1准确**未编译**修复源候选Core `c948184504d82b80e23eb3f4ff6cdfd328ba9355`，对外Core分支 `57e1c363aede1a7790bdf94136d832d35ee7b34b`同tree；Framework生产入口和pin `3ab150b3e99ff3ed759b8cdc5154cfb5744042a7`，Lane1 Framework状态 `85534de235345292a153d9983cfd0d24d8033bb2`。Core的重复getter+fixture clock已修复，**不能再叠加**Lane2/4/5旧 getter patch。
- Lane2 Framework `d1f302c51d3ec7718a22748792a1e610f17eb6d5` / Core `cbdf145314dbe5dcd9006a5de4e94f7b19fbbb71`；Lane3 Framework `5b5e6dd49781e97fdac4f120a8a2e652d32508d3` / Core `dfd9d5459f189d4d85a0ff33fc83ed7a75fc3ba2`；Lane4 `69671a55883f22cd9c7227b6dc0e6b87998f6e05`；Lane5 `e8f701995a27154ffcc54cc38245dde8cd7f9bdf`；Lane6 `20676888aa9f1d98bb318573a6569f5fe88aa17a`。均已交付低资源静态/工具工作，但尚未因此获得新producer或独立C++ runtime资格。
- 2026-10-16T16:22:59Z旧174来源快照 `df /workspace`可用**31,558,250,496B=29.39GiB**，距50GiB正式build准入约20.61GiB；非当前实时保证。目标Ops 2026-10-16T16:31Z已到R1_B010 DEST_VERIFIED，三个历史V3 build目录共**11,839,741,952B allocated**，但目前全部 `COPY_OK_ONLY/SOURCE_KEEP`，不能据已传GB数当作源释放。源Ops在 `swayhrl/gpu-l2-cache-verilog` 自己分支更新，同旧174命名空间有关；目标Ops在Framework `hrl/ops-174new-164-archive-exec-v1` 更新，并非同一个源执行者。
- 旧174另外运行**DTC-L1至少七个历史时点观察到的simulator**与C16等项目。执行时重新探测PID/registry/CPU/IO；绝不停止、kill、迁移、变更这些活跃项目的数据/配额；旧数量只是快照，不是许可额度。
- 本补充不自动降原有48GiB filesystem floor、Lane1另2GiB构建增长余量、64GiB可用RAM、registry/8CPU/2长期模拟/32GiB保护/scan独占等规则。它们是**正式生产准入政策**，不是所有源码工作前提。

## 1. 轻重拆开：六Lane现在就并行，不能六路抢同一生产构建

| Lane | 资源仍HOLD时立即做（小规模、可中断、不新增大文件） | 合法依赖解除后自动续行 |
|---|---|---|
| **1 Public Core** | 一次性确认c948/3ab生产身份、原21项producer定向和two repairs、正确性路径。实现/复用**唯一**的低开销GateWaiter，仅检测live资源与已有中央registry，不占资源lease等待；禁止重复CMake/无穷build retry。 | live满足50GiB build + 64GiB mem、其它运行/配额无冲突，至少两次间隔复核，获取唯一build lease并锁定后再次准入，**只通过原`build_r0_1.py`正式构建一次**，真实21定向及完整日志/测试/二进制/source/config身份发布给Lane5。普通工程错误允许在本Lane自己修并继续，但重建产生新版本/新目录，不覆盖已记录证据。 |
| **2 TVD** | 对新c948源做精确静态delta/rebase和实际WAD/dirty/TVD-host兼容检查；旧62补丁已包含getter删除，不重复删；新小补丁和输入身份发布后进入低开销依赖等待。 | Lane1官方基线确定后重新bind准确Core、以自己的隔离worktree做必要的有限C++定向；需受共享build/CPU/盘准入，优先不阻塞Lane1/Lane5。Lane1集成R2、Lane5独立TVD资格通过后才允许TVD应用，不重跑旧module证据冒充新runtime。 |
| **3 RO** | 同样精确rebase至新c948，保留直接`ft_try_force_tag_access` RO epoch guard、generation/sector/response/offset拒绝，静态最小diff；不重抓trace或更改完整commandlist oracle。 | Lane1完成官方父版本后做真实生产定向并由Lane5独立RO资格，不抢主线应用或共同执行额。 |
| **4 Ideal** | 审查c948与R1.1的静态差分、定位后续quiescent host prefill的I_READ_HIT reference版本同步最小修复与被测反例；Tag timestamp沿原生offset，Bank service物理cycle；不悄然收窄科学scope。准备完整原18格identity/runner并保留全部NOT_RUN。 | 仅在官方R1.1、独立repair+ideal资格与**同R1.1 binary B16**存在时按原矩阵rolling；不以旧1.721×作当前结果，也不抢R0.1构建/首批配对。 |
| **5 Independent Qualification / Formal Runs** | 按新c948/3ab精确bind 11个gate/21条production计划与五B16/U_WB16配对的身份模板；接受V2的dynamic withdrawal、旧六run仍拒绝。无需新run-key/构建，提前准备轻量preflight和受限等待。 | **只在Lane1发布真实唯一binary/hash以及当前资源、registry全部合法时**独立执行11个gate、后续正式五组配对，最多2长模拟/8 CPU/32GiB约束和其它项目保护；每个新run-key与全trace/hash绑定。每个合格pair立即发布，可交Lane6；五对俱合格后才能计算geomean。遇runtime/科学identity缺陷停止受影响实验而非反复重建。 |
| **6 Paper / PPA** | 可独立吸收英文编辑分支 `hrl/ep-l2-iscas2027-english-editorial-v1` 最新 `2d7091bf54f4aa77aca5f44e3005166dce8f7ae7` 的EN-v2结构、图位和已核实引用；先复核真正可用内容，再在本Lane**新revision**写作，不覆盖r4、不得凭本editorial生成产出性能。继续成本差分/图位结构，不吃旧174重资源。 | 新current-scientifically-accepted配对出现，沿既有Lane5 V2原生API/fail-closed current-authority+withdrawal复查，滚动填真实Fig2–4与摘要/结论；新论文结果不得未经接受直接读取旧`COMPLETE_VALID`。 |

**当前可同时运行的人/窗口数=6，允许同时跑的独占重资源生产活动不因此增加。** 研究Lane只写自己隔离worktree/branch并发布独立revision，原科学与源Ops冻结资产不触碰。

## 2. 单一磁盘等待者 + 分阶段自动续行（需实现真实守卫，默认执行现有政策）

**只有Lane1负责旧174`/workspace`磁盘GateWaiter**；Lane2–6不得各自运行`df`/du高频循环，更不得并发资源准入尝试。轻量等待可以是原Lane1 Goal持续sleep或**一个**可见且可停止的、有独占PID/锁的进程（前提是现有Goal允许、来源可审查）；防止多个Codex窗口/新shell重复创建watcher。示范策略：每10分钟只读`statvfs/df`、host/cgroup可用RAM、中央registry和相关PID/IO，记录状态变化而不每轮写庞大receipt；持续最多48小时或用户明确停止。真正建立入口前连查两次间隔至少60秒；**不能把一次`df`快照当许可**，得到正式lease并再次复核资源/原source/vendor pin后才调用一次原build入口。出现挂载/锁/入口身份不明、DTC冲突、可用空间下滑或watcher终止时fail-closed并报告。任何异常build失败遵循自身脚本证据/新revision，不重复自动clean/retry。目标是零忙轮询和零重复建造。

Lane5可用**一个低频、只读官方release事件监听**（如每10–15分钟只fetch Lane1最新`RECEIPT`准确binary字段及当前Lane5权威，不直接等于认可），在真正binary发布后先独立验source/binary/producer tests/脚本/目录，符合原准入才开启自己的测试/配对；禁止仅从GitHub `runtime_ready`文字推断现场还有空间和lease。Lane2/3/4/6只做源级轻量准备后可在已有Codex Goal内低频读取**所依赖的确切提交/事件**或通过用户/协调窗口续行；无二次disk watcher。无被授权的R1.1/TVD/RO重运行仍保持HOLD。

如果Codex运行环境不支持长期安全waiter或48小时后仍被写入压力阻塞，发布`RESOURCE_WAIT_EXPIRED`（带实际df/registry/相关活跃项目、阻塞原因）后停止**等待子任务**，不对主工作假装已完成；不要采用粗暴`nohup`无审计常驻、无限刷GitHub或在无准入时抢编译。

## 3. 加急备选：仅针对Lane1的**受监控、低于48+2GiB的工程构建试验**（本文件只设计、不激活）

目前目录快照远低于50GiB，且三个V3冷build全部合规释放最多也仅约11.03GiB；依赖自然恢复可能赶不上ISCAS。历史两次build清理前静态文件量约0.71/1.01GiB，**不代表**新source的编译/链接峰值，因此不能直接断言现在29GiB空间够用。

允许Lane1+Lane5在轻量阶段准备一份**仅一次、2 jobs、完整输入pin和独立目录**的工程构建exception申请（`EARLY_BUILD_OPT_IN_PROPOSAL.md`）：测量当前workspace与实际临时目录、results所在Share、实测近时窗口其它进程总写入、真实disk block/free/reservation、监控检测和停止延迟，提出清晰起点/强制中断阈值、保留DTC等项目余量和额外日志限额；方案只能由用户**明确批准准确门槛和范围后**启用独立开关、独立receipt。即便提前编译通过也仅视为`ENGINEERING_BUILD_EVIDENCE`，**不能默认成为正式科学run的准入**；生产是否沿用binary、Lane5独立科学qualification和正式应用space threshold仍需另审。不能通过局部改写`build_r0_1.py`常量、在`/tmp`（同overlay）、在未准入的`/root/share`（Stage需40GiB）偷偷绕过原入口。164目前是archive receiver，不是生产编译盘。

源 `df`的一条读数同时列出容量3779302981632B、used3555690156032B、avail31558250496B，差值**192054575104B≈178.86GiB不在Avail中**。要求Ops/Lane5仅**只读**调查`statvfs(f_bfree vs f_bavail)`、后端FSType/quotas/reserved blocks等原因；这个差额不等于可以动用的可用空间。不得`tune2fs`、改quota、改ext4保留比例、越过挂载/用户权限或让watcher使用`f_bfree`代替`f_bavail`。若运维管理员证实有可安全调整的独立预留策略，需由用户/设施owner显式批准再执行，不在本文自动处理。

## 4. 迁移两窗口与论文截止协同

源旧174第三仓库独立Ops + 174-new目标Ops **继续R1/R1R/R2单流水**，最新目标已R1 B010；这是目标readback和copy，而不是源释放。对已部分归档的完整R1，优先完成全部批次、完整目录清单与双namespace真实恢复演练，并尽快形成**精确用户待批release manifest**；保留未审核科学raw/trace、Signoff、M5正在使用的Trace、DTC-L1当前run、Git对象。即使源释放所有三个V3 build也不能承诺一定触发50GiB；源Ops继续风险加权审核更多可恢复的大冷项目，但科学数据必须获取用户对准确目录和证据的单独批准。不要为完善无限通用迁移工具延迟首个已具备资格的release请求。
DTC-L1/EP-L2/C16所用的其它项目限额和进程不变。任何用户另外批准的高风险释放，不由六研究Lane执行。每次源真正释放后Lane1 GateWaiter只重测真实free，Lane5独立复核；不能把`archived_bytes`当`source_df_gain`。

## 5. 交付与成功定义

- 每个Lane发自己的新revision，准确branch HEAD、精确source/binary/config/trace/oracle/run-key身份、实际执行计数、资源/阻塞、下一触发条件、是否存在`GateWaiter`及PID/锁/截止、GitHub push/fetch/readback。
- 正式序列：`R0.1唯一producer build → Lane5独立11gate → 首个B16/U_WB16 current-accepted pair → 五对滚动 → Lane6英文稿结果更新`。R1.1/ideal/TVD/RO各自只有在自己的生产/资格门槛满足且不抢主线资源时继续。
- 绝不以“六Lane并行”解读为“六份同时运行的完整生产sim”；不自动授权任何新的大实验矩阵、删除Git临时pack、修改共享科学合同或降低现有资源门槛。
