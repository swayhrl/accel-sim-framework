# EP-L2 ISCAS2027 review_r11｜低空间工程构建仍拒绝后的资源解锁优先级

2026-10-17，协调侧只读审查。**非初始Goal；不重启已有Lane1 GateWaiter或任一Storage-Ops窗口；不赋予新的删除、正式编译、科学实验或quota授权。** R10十小时续行`23808bdd11f07b596ea4e1600357f96761b8bcb0`保留。本文件只确定下一科学/空间决策与证据依赖。所有分支HEAD只代表下述远端快照，后续须以新的STATUS/RECEIPT为准。

## 1. Lane1/Lane5：工程身份已经闭合，资源安全未闭合

- Lane1 Framework原分支HEAD `9b9eb4d801a26e21f9cfef215bda648b8f282c06`；pilot申请r2源码publication `50d3a648704235ff03be6b5b7e4f8f33a904500d`，raw request SHA256 `f992a65187ea46413cec85623af16cdd39e180b817e23f9002419d03cbf7129e`。同一pilot_id `EP_L2_R0_1_ENGINEERING_20261017_L1_P01`；独立Core`c948184504d82b80e23eb3f4ff6cdfd328ba9355`/Framework`3ab150b3e99ff3ed759b8cdc5154cfb5744042a7`/vendor`f90c430c3a1ce8f08c09942a5a1c3a797bb2295b`，2 CPU/8GiB reservation，最多1h工程campaign；21条Producer生产定向仍**NOT_RUN**，binary=null。
- 旧等待PID已由Lane1独立替换为唯一 `PID 1156558 / start_ticks 892416307`，600s复测，合同截止北京时间10月19日01:17；准确执行身份/独占锁在Lane1回执。该PID、lock仅有历史证据；协调侧没有服务器实时控制权。不要发送重新创建GateWaiter指令，也不允许在等待中占有build lease。标准50GiB正规构建路径仍优先。
- Lane5原分支HEAD `827a6377ac542dc57123d956d23e637313794ed0`独立发布新`NO_SAFE_PILOT_ENVELOPE_AFTER_REQUEST`。此次已消费Lane1准确r2，源码hash、runner/API以及私有ledger绑定得到确认；原先`NO_REQUEST`身份问题已经消除。本轮真正剩余五项：**(i)** 最终 `/workspace f_bavail=27,898,707,968B`，低于pilot自己设定26GiB entry `27,917,287,424B`约18.58MB；**(ii)** 1h内其他项目8GiB/2GiB预算无可信future burst上限；**(iii)** 编译+终止2GiB/512MiB aggregate overshoot没有实测/约束；**(iv)** Share的43GiB提议准入等于全部风险项之和、无额外算术余量；**(v)** 尚无Storage-Ops给出明确的低I/O时间窗口ACK。RAM、2CPU/8GiB预留、当前EP-L2 lease0这些不构成磁盘批准。
- Lane5未签pilot token/lease，Lane1 CMake0、21定向0、正式配对0。**不再为刚好差18.58MB连续降入口常量或反复跑同30秒静态审查**；这不会解决未来突发写入。User对一次工程构建的条件性opt-in继续保留，只有资源实测/保留与stop预算获得独立闭合之后才可使用，勿第二次索要同一通用审批。

## 2. Storage-Ops：变成实际`df`增量的两级候选（均未批准释放）

**A. 优先审查快可交付的窄范围R1：**
- 旧174第三仓库 `swayhrl/gpu-l2-cache-verilog`源侧 `R1_SOURCE_RELEASE_REVIEW_PENDING.json`冻结准确197项历史`.vvp`，有序TSV SHA256 `af1bf73951ab44258591afd625043c855e3a76bca67fb378abe8b226ee271c84`，allocated预计上限`4,464,783,360B`（约4.16GiB，**不是已回收量**）；保留R1其余日志、generated RTL、filelists、Git和reviews。
- R1完整14批/18565文件/4,737,658,722B已164 SSHFS DEST_VERIFIED，目标全内容独立恢复/哈希PASS；B001 1269文件、123目录的旧174原生权限/哈希/时间恢复演练PASS、临时演练目录精确清理。仍缺**目标索引恢复字节计数新版本对账、针对197文件的可执行双namespace恢复程序/验证、最新所有权和活跃消费者准入、用户对准确TSV manifest的单独批准**。原R1 SOURCE_KEEP、回收0。
- 原V5 scratch在原合同准入满足时可精确释放；但不能由R1的`COPY_OK_ONLY`借用删除权限。r10已委托双Ops整理R1集中批准包，不必再创建另一套parallel审计工作。

**B. 最值得争取的较大空间：PolyBench两份纯`closeout.stage`目录（不同于正在使用的`polybench.stage`）**
- 独立旧174源审计 `POLYBENCH_STAGE_METADATA_V2_SCOPE.json`：完整精确13个普通文件（其中11个非空、2个0B完成标记）、14目录、allocated包含目录`66,331,324,416B`（约61.77GiB）。这两个closeout目录在源侧完整tar成员比较中11个非空文件内容与`polybench.tgz`中对应数据逐字节相等；压缩包本身`17,943,970,556B`，SHA256`9feffb121c304412ea7b8289e9ae0c7cabff5aef2098ff025fb65af2f43653ca`。零字节标记**不在tar内**，需要单独还原路径和原数值UID/GID/mode/mtime；元数据sidecars已冻结。
- 源 `POLYBENCH_CLOSEOUT_CONSUMER_AUDIT.json` 对两个精确closeout stage的已查`/proc cmdline/cwd/fd`和限域脚本未发现直接引用，但**未来/手动`--staged-traces`引用尚不能排除**。另有11个state-T停止进程命令行引用的是原tgz，原tgz不得删或替换，不能唤醒/终止这些进程。
- 174-new目标已开始按V2接收17.94GB原tgz分35 chunks；源旧174截至参考点`PB_CHUNK_000`经DEST_VERIFIED/SOURCE_KEEP/BRIDGE_CLEANED、`PB_CHUNK_001`已stage。**这只是COPY，不是两个stage目录独立可恢复证明，更不是源释放授权。** 原archive和两份stage仍SOURCE_KEEP。
- 现实解锁候选：若且仅若完整17.94GB archive在164重新组装/验证SHA、对13文件/14目录可独立恢复原内容**与元数据及两0B标记**的跨namespace流程被验证、项目owner/当前及可预见消费者能由明确暂停/恢复计划消除、并取得用户对两条绝对路径和冻结manifest的单独释放授权，才可以提出**精确stage文件释放**，预期有望回收大于R1 197项的量，足以帮助Lane1标准50GiB资格（但不能保证，因为其它项目持续写盘）。缺一项保留SOURCE_KEEP。
- R1R/R2 copy-only可作为下位补充，但不应在未确认PB/主线余量的情况下把有限时间用于无限归档，还不产生旧174任何实际df收益。不能把目标端`archived_bytes`记作空间恢复。

## 3. 不改变六Lane科学序列，不在拒绝后空转

- Lane1：保持现有单GateWaiter；若正式源盘达到50GiB，按原构建driver准入一次；若Lane5日后独立证实pilot安全并签准确token，执行最多一次工程构建。工程binary不能直接成为官方producer。
- Lane5：已完成r9对申请的独立审查，**不建议立即发新的相同pilot复审Goal**；只有真实空间释放、可验证外部写入quiet-window边界或新的独立资源证据才重新评估。空闲内可复查正式11gate和五配对身份，不开生产sim。
- Lane2/3/4：静态候选交付已完成、无需新增10h busy polling/大编译或自动启用RO/TVD/ideal。Lane6英文EN-v3与图位已准备，0当前合格pair，不动旧SUSPENDED统计。
- 双Ops已有r10夜间分工和单流、40GiB Share reserve、<=512MiB批次、<=30MiB/s规则；不打断既有chunk。优先产生**可审查批准材料与真实可恢复性**，不能直接释放R1、PolyBench、Git pack或其它科研资产。
- 收到任何新审批或新source/target状态，原Lane/原Ops自查实时HEAD、源/目标/registry/FD/mount/space并记录；不可把本次Git协调文档视为运行时资源身份。

**本r11只是审查备忘，不生成新执行进程、没有额外Codex指令派发、没有扩大删除许可。** 下一次值得用户审的是R1 197或PolyBench两closeout stage的**准确待批准包**，而不是又一轮相同低空间拒绝测试。
