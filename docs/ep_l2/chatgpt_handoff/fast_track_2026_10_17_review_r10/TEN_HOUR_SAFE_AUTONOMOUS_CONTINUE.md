# EP-L2 / ISCAS2027 — r10｜接下来十小时有界无人值守续行（只针对现有窗口）

北京时间2026-10-17。**续行合同，不是新Goal、不启动第二进程或第二传输流、不扩大删除和科学认证权限。** 收到本文件的窗口以实际消费时间为T0、T0+10小时为本轮终点，记录UTC起止。若原Goal/已有worker在此期间自然退出，保留所有证据、不要假称无人值守仍在运行；不得使用未审计的守护进程代替已存在执行者。每项先读各自最新准确GitHub HEAD、STATUS/RECEIPT、桥接与live进程，旧快照不覆盖新状态。

## 0. 当前数据和唯一目标

- EP-L2优先级：**R0.1唯一正式producer → Lane5独立11-gate → 首个B16_BANKED/U_WB16科学接受pair → 余下四对 → Lane6英文稿结果**。五对完整前不写geomean。旧6条R0/R1应用科学SUSPENDED。六Lane共用预算、物理bank时钟/Tag warmup修复及元数据合同不变。
- Lane1独占GateWaiter已经在现场注册：Lane1最新Framework `649f8afa27503fd627483fc25a206776c56dd91c`，请求 `248c93acc611679afe42590760481f451773003d`；唯一PID/锁与原48h deadline已发布。工程pilot **没有自动许可**，只能由Lane5按review_r8/r9在全部保护预算独立闭合时对准确pilot_id发一次授权；正式50GiB先合格则优先正式driver。无新第二GateWaiter。
- Lane5 `300c1010161b270ae73414b8146d238c961f0cd0`的第一次`NO_SAFE_PILOT_ENVELOPE`发生于准确请求发布前；用户已给Lane5 r9增量复审指令，**不要再次派同一条**。即使请求已到，不得忽略外部写入突发/停止超调尚未知问题。若再次拒绝，待有意义的真实释放事件或独立预算改善再复核，不忙轮询、不擅降科学准入。
- Lane2 `dc21af497c319672c30752ed2192a2a8cc937bab`、Lane3 `e8d6f9671da0748b5f4eb780d6cdf163e91b58d1`、Lane4 `4a55269d5a4f1e11b93e67e9d4eadebe8b3b3493` 都已完成c948静态候选和一次有限依赖等待/准备，C++生产仍NOT_RUN；不再新增三个无效10h watcher、不用ENGINEERING_ONLY binary跑RO/TVD/ideal。Lane6 `d99195b5800de404b0f31c9c43742612428a168d` 的英文EN-v3与图位已交付，只有current accepted配对才允许更新真实数字。
- 双Ops：旧174源仓库 **`swayhrl/gpu-l2-cache-verilog`** 分支`hrl/ops-174-source-audit-exec-v1`；174-new目标Framework分支`hrl/ops-174new-164-archive-exec-v1`。R1 14/14批、18,565文件、4,737,658,722B已经164 DEST_VERIFIED+目标独立全内容恢复；B001 1,269文件/123目录已经旧174原生恢复验证，临时演练副本已精确清理。原R1和其它冷科学数据仍全部`SOURCE_KEEP`，R1原始文件释放0；S01/S02历史安全回收除外。
- 截至已读源侧 `POLYBENCH_SOURCE_COPY_SCOPE.json`：Decoupled-L2 `polybench.tgz`原文件17,943,970,556B、SHA256 `9feffb121c304412ea7b8289e9ae0c7cabff5aef2098ff025fb65af2f43653ca`，35个受限chunk，两个closeout stage合计66,331,215,249B与tar内容本地逐字节一致；11个state-T进程在cmdline提及归档（无打开FD），**未来消费者不能排除**。文件和stage保留，当前仅`COPY_OK_ONLY`。源侧V2 nanosecond修正plan SHA256 `a38ffd7a54d90d68a5d11135126ed31280fb23a963c32bf17e8550ce2e4ac5f9`；目标方有专门receiver `172affd2e826ba63256a2e6fe2b893bb938c557c`，`POLYBENCH_TARGET_RECEIVER_READY.json`；源copy scope commit `d4192019`（原回执）。有后续HEAD时精确核实，勿重复旧修正。

## 1. 两个已有Storage-Ops窗口：首要推进，不再因小协议差异人工排队

### 旧174源侧（唯一复制准备/READY与源释放owner）

1. **只一次精确协议收敛**：比较源V2 plan、`POLYBENCH_SOURCE_COPY_SCOPE`、目标`POLYBENCH_TARGET_RECEIVER_READY`及receiver脚本schema、路径`PB_CHUNK_000/files/payload.bin`、索引从0开始、源UID/GID/mode/目录sidecars；用确定性fixture验证双方一致。当前无有效READY或有源身份改变就不stage。已验证过的98ns精度修正不重复整批重做。
2. 然后按原V7唯一bridge/一stream逐个stage下一个`PB_CHUNK_NNN`，每个源切片<=512MiB，保留单流<=30MiB/s、Share可用>=40GiB和原nonce/跨namespace身份规则。READY必须原子发布、SHA256关账；上一批只有在目标DEST_VERIFIED、旧174独立SOURCE_KEEP ACK经GitHub/bridge回读、目标bridge closeout后才能下一批。**所有原始tgz与两份stage永远KEEP，夜间不自动删除。** 单个chunk fail时先保存失败证据/精确小范围自行修；不能重传已VERIFIED块、不同时起第二队列；两次有界同类修复仍不能前进则停止该流并记录BLOCKED，不创造新协议版本反复消耗10小时。
3. 与传输**低I/O并行**完成R1既有`R1_SOURCE_RELEASE_REVIEW_PENDING.json`的精确资格包：仅197个已冻结`.vvp`，manifest TSV SHA256 `af1bf73951ab44258591afd625043c855e3a76bca67fb378abe8b226ee271c84`，预计allocated 4,464,783,360B（**非已回收量**）。补目标全内容restore与PROJECT_INDEX计数差异、可执行的两namespace原始路径恢复说明、真实owner/current process/FD/registry检查、当前身份与科学回溯风险；输出**一个**`R1_197_EXACT_RELEASE_APPROVAL_REQUEST`供用户晨间审。无用户对该准确清单的明确授权，不删除任何R1源。不得把宽的整个build作为默认选项。
4. 优先推动真正有资格且用户已授权的旧V5 scratch 精确释放；其它项目科学文件即使已复制到164也只COPY_OK_ONLY。不得删Git pack、共享trace、DTC-L1/C16/EP-L2活跃文件，不kill或resume state-T进程。真实`df -B1 -P /workspace`变化和独立源释放收据分开记录，不把归档字节当作回收。

### 174-new目标侧（唯一164接收与DEST_VERIFIED owner）

1. 消费并回读源准确`COPY_SCOPE`/V2 plan与完整receiver schema；目标`READY`、源`READY`完整契约相同才接收PB_CHUNK_000，不允许先运行旧不兼容工具。每个chunk只在源READY后单流写164，close/reopen SHA256并以准确offset/range/文件身份提交DEST_VERIFIED；消费源SOURCE_KEEP ACK之后才清bridge，严守前述B002顺序修正规则。
2. 按自然下一个chunk循环最多T0+10h且不新开第二rsync；若某批失败可对该批有界重试或继续同一流的正确恢复，不重复上传已通过chunk。所有chunk完毕则在164重新组合/stream hash核对**整个17,943,970,556B档案SHA256**，完成来源元数据和manifest验收；必要时做无覆盖的目标端恢复测试，结果标`ARCHIVE_VERIFIED_SOURCE_KEEP`，**不自动对66GB stage发删除指令**。
3. 与源侧低I/O并行核实R1 全project restore receipt `R1_FULL_CONTENT_RESTORE.json`与`PROJECT_INDEX_RECEIPT.json`的`verified_restore_bytes`不一致（索引是更旧的快照，不可擅改历史证明）；发布新versioned reconciliation，不能覆盖旧回执。目标为R1的197-file精准release proposal提供已验证path/Hash/restore证据，但**无权判断用户/源owner授权**。
4. PB归档完成且仍有时间/空间余量，则在双方共识下**单流、依原batch**推进R1R/R2可恢复的copy-only最小批次；它们仍SOURCE_KEEP。若Share<40GiB、另一项目写入压力、目标164容量/权限/SSHFS异常，严格等待/停止新批，不降低保护；不为使用十小时而制造填满磁盘的额外备份。

## 2. 夜间资源配合：只在事件触发时协调

- 唯一Lane1 GateWaiter、工程pilot/正式build mutex及Lane5一次性独立资格继续现有r7–r9，不从Ops另启任何构建。若Lane5发布准确有效的pilot准入且Lane1将进入已授权工程编译，两Ops**只在批次边界**暂停新PB源staging/164接收（已有批次可靠完成和closeout），尽量避免与Linker/Share日志写入重叠；不得停止或优先级操作其它DTC/C16研究任务。pilot结束及Share/registry gate恢复后再继续下一PB批。
- 若原50GiB门槛由**实际源释放**达到，GateWaiter+Lane5各自按合同核查，正式R0.1优先；Ops无需中断正在进行的有效验证批次，但暂停新大批I/O。Lane5只有OFF→ON/current真实资格通过后才可以滚动五配对；任何ENGINEERING_ONLY结果不得被论文、Lane2/3/4当作正式binary。
- Lane6 EN-v3不受理缺少当前完整source/binary/config/trace/proof+V2 acceptance的新数值；没有合格pair时继续使用待测图位，不重做英文整稿。研究Lane2/3/4依赖为空时保持有界HOLD、**不运行新的10h无意义轮询**。
- 每60–90分钟或有阶段性里程碑时各Ops发小状态回执（batch编号、分流hash/数量、源释放真实df、当前活跃用户/阻塞、时间和剩余工作），不对旧大体积文件全hash刷屏。T0+10h必须有终态或清晰`NIGHT_WINDOW_EXPIRED`证据；不虚构持续后台进程。即使原Goal停止，留下精确可恢复的next action。

## 3. 绝不能夜间自动跨越的闸门

**用户尚未授权**删除R1 197个`.vvp`、整个R1/R1R/R2构建目录、PolyBench的原tgz和66GB stage、Git对象/pack、任何其它科学trace/raw。默认`SOURCE_KEEP`。可以完整准备集中审批资料、可恢复脚本与独立证明，但不能把10小时无人值守要求解释为授权不可逆删除。另不可修改48GiB+2GiB正式构建和Lane5正式performance gates、C16/DTC-L1在途执行、共享registry不可绕过。

**最有效的十小时验收**：在不干扰活跃科学任务的前提下，持续生产PB归档的有序DEST_VERIFIED、修正R1恢复索引并准备197个准确候选的用户待批申请；在任何合法释放之后使旧174的真实`df`上升；Lane5如果仍不给pilot许可则保留完整否决和可行替代路径，禁止急于得到实验结果而制造不合格binary。
