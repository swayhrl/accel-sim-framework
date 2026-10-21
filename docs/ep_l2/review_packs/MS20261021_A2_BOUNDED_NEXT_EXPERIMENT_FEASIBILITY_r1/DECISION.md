# EP-L2 A2：下一阶段有限实验决策（待用户批准）

结论：首选 **DWT F_MINUS_R＋Conv S_WB64＋Conv S_L2_DATA_FREE＋Conv F_L2_DATA_FREE，最多4次新启动**；第二选择为 **前两个P0＋Vector F恢复，共3次**，不为凑满4次添加实验。优先先交付并资格审查DWT F_MINUS_R，不等其他profile全部齐备。FWT恢复和L2/DRAM敏感性暂不列首批。此报告不授予启动权；由用户选择、批准具体槽位替换后，唯一E中央控制器实施。

核对用户指定E HEAD `ac5b22afc27450d38d61a3b3208ca97dd5ae7b72`，并fetch到其收尾提交 `b8a1ddc5995456332ef4ac8e36d028ec8f77e097`。累计32/40、剩8，controller STOPPED、无ACTIVE lease。四项主S/F和全部既有accepted控制保持原身份；原失败尝试不退款。此次A2、E可行性复核和DWT逐kernel复核并行，均只读；没有启动、构建或修改中央runner/registry。

## 候选、最小缺口与成本

时间是规划估计，不能用模拟GPU cycles推算host walltime。所有实际启动仍有既定每端10800秒timeout、8GiB RAM；每端原spec结果guard为384MiB。下表最坏空间按该既有guard计算，另需收尾文件/监控采样越界余量，不能把poll guard当文件系统硬配额。

| 候选 | 当前矩阵／精确资格 | 最小资格或批准缺口 | 新启动；结果guard；预计walltime |
|---|---|---|---|
| **P0 DWT F_MINUS_R** | **不在当前批准矩阵**；source-supported；已有W/V/R相关工程控制PASS。Conv/CFD同profile及DWT S/F、W_ONLY输入资格均可复用，但没有DWT此profile的独立资格 | 提议用未启动`V2_FWT_7_21_F_MINUS_W`原REMOVE_ONE槽替换为DWT F_MINUS_R；需明确批准。E绑定现成config、完整10-kernel/148684429指令输入、RO OFF scope；复核profile语义、终验与共有native证据，无需重跑17项 | **1；384MiB；15–30分钟**。已有DWT各成功端约643–827秒；新端尚无实测，硬界3小时 |
| **P0 Conv S_WB64** | 已在矩阵`V2_convolutionSeparable_S_WB64`、STATIC_CAPACITY余1；source-supported；旧静态工程fixture PASS，**main61精确profile/parser资格未具备** | 真实布局1168=1024 resident＋80 landing＋64 WB，每bank256/20/16；相对S的1024/128/16，48个新增WB槽取自landing。E需专属parser分支、布局与reference-data/lifecycle资格处置；accepted Conv S为基线，F仅作旁证 | **1；384MiB；45–90分钟**。既有Conv S/F约52/57分钟；硬界3小时 |
| **P1 Conv S_L2_DATA_FREE** | 已在LOCAL_DIAGNOSTIC矩阵；source-supported；历史local-service/ROP7等工程fixture PASS，当前parser已支持；**精确main61资格未授予** | 复用accepted Conv S完整输入。补独立finite-residual-service/profile处置，保留固定copy latch、ROP、有限队列/容量、reference data和drain；不重复大规模native | **1；384MiB；45–90分钟**，不假定诊断一定更快；硬界3小时 |
| **P1 Conv F_L2_DATA_FREE** | 已在LOCAL_DIAGNOSTIC矩阵；source-supported；历史工程控制PASS，当前parser已支持；**精确main61资格未授予** | 复用accepted Conv F输入和RO证书。必须满足`full_data_free_finite_residual_service=PASS`专属生产门，结合新E17与RO身份修复证据；旧main67 fixture不可直接冒充main61资格 | **1；384MiB；45–90分钟**；硬界3小时 |
| **P1 Vector F恢复** | 原科学条件在矩阵；main61 S/F资格仍有效，accepted S可复用；**新attempt槽位尚未批准** | 旧E014因WORKSPACE_STOP_RESERVE收到SIGTERM，真实wait_status15/exit−15。建议第二选择明确放弃未启动Conv F_MINUS_W的REMOVE_ONE槽，以原配额记账资助一次Vector F恢复，科学标签仍为MAIN F恢复，不伪称remove-one。E复查preflight并绑定原E014、retry_reason；不自动重试 | **1；384MiB；15–30分钟**。S约704秒；旧F在748秒被终止，不能视作完成耗时；硬界3小时 |
| **P2 FWT S/F恢复** | 原两端在矩阵；19-kernel、791609344指令完整输入与main61 S/F资格仍有效；旧两端INCOMPLETE不变 | 两次charged新attempt，contingency已耗尽。若将来选择恢复，须明确放弃/重分配未启动Btree S/F的两个MAIN槽，另获批准；旧从WV-T/M转槽提议已经过时（该bucket现余0）。每端仍需真实exit0、全输入与drain独立终验 | **2；768MiB；S约1.4–2h、F约1.5–2h**。旧5040.8/5394.7秒含恢复期，仅作估计；硬界各3h，顺序最坏6h |
| **P2 L2/DRAM敏感性** | 无新增批准条件或新资格；**不推荐执行，不生成参数网格** | accepted Conv确有bank/MissQ/line/WB等待，但无足以指定某档L2/DRAM变化的关键路径或DRAM饱和证据。先使用DATA_FREE与WB布局控制；不以总等待/流量推出带宽敏感性 | **本轮推荐0次、0空间、0耗时**；若以后形成依据，一档必须用同一参数S/F共2次、至多768MiB guard并重新批准，不借用本轮名额 |

## 资格复用的准确边界

冻结生产：Core `d010911e3174a3764791183cd108fe4664ba8731`；Framework `9dd1ee57a83d83b56b7874bc7c716185ab52c8f7`；vendor `f90c430c3a1ce8f08c09942a5a1c3a797bb2295b`。main实物重新SHA256=`61aad385723ac97a76cb1f32c124b286a10bc8609c9c58b1a3ef8a87413f2dd5`；archive实物=`3c6ce15b88ae16c17c30718618aedc769495168d6e3d0c371270ba95b7b0aca8`。完整路径、现成配置/有效runtime SHA、输入SHA和证据SHA见`CANDIDATES.json`、`EVIDENCE_INDEX.json`。不重建模拟器；WB64有效runtime hash尚待E用accepted Conv bases与已有overlay封存，不编造hash，也不采用旧production spec。已有SPEC_CANDIDATE仍为不可启动草案，含PENDING资格和旧producer-publication字段；E仅复用核对过的配置/输入，须重新绑定正式A2 release和精确资格后封存spec。

- **WB64实际源码**：Core `src/gpgpu-sim/gpu-cache.h:2301–2305,2323–2325`，`tests/ep_l2/test_potential_s64.cc:6–30,50–73`。FT1、WBUF16 anchor、P1、所有V/RO关闭。当前E `MS20261020_E2_MAIN61_TERMINAL_COMPAT_r1/parse_main_terminal.py:23–26,129,136`缺S_WB64且强制static_s64=0/False；直接开跑会被终验拒绝。最小建议为E添加该profile专属分支，严格验证1168/1024/80/64、FT1/WBUF16/P1并保留其他门。不能放宽所有profile的static_s64断言。
- **DATA_FREE准确标签**：“L2数据服务无争用诊断，保留有限残余资源和固定流水延迟”。`gpu-cache.h:2257–2260,2625–2632`豁免payload bank服务但仍执行数据/生命周期操作；`ep-l2-ft-cache.inc:462–465`保留S固定1-cycle copy latch；`:660–670`标记hardware-P1-throughput-ineligible。E parser `:230–242`要求diagnostic=1、throughput_eligible=0和physical_grants=0。`util/ep_l2/mechanism_e/policy_v2.py:145–151`对F显式要求专属finite-residual-service门；S也应明确记录该范围的reference-data/finite-resource处置。不得称为取消全部L2延迟或可实现P1硬件结果。
- **复用而非追认**：旧`E_INDEPENDENT_DIAGNOSTICS_STATIC_r1/RECEIPT.json`绑定Core c994/main67，相关fixture exit0，但科学门仍PENDING_E_REFERENCE_DATA_AND_SOURCE_REVIEW。c994→d010的`gpu-cache.h`、`ep-l2-ft-cache.inc`及static64/local-service/partition三个fixture Git blob逐字相同；新own-pending重排已有E17，新增RO lower身份保持须纳入F审查。E可以源码等价审查处置已有fixture；若仍有确切缺口，仅运行对应单个小fixture。工程PASS、source support和E精确profile资格不能合并为一个PASS。
- **FWT退出证据**：旧supervisor退出143后原wait父进程丢失，重连只看zombie/进度不能重获真实退出码。当前`durable_exit.py:85–149`由真实父进程`os.wait4`并原子fsync保存回执；`:181–197`缺回执拒绝成功；`runner.py:174–194`继续校验原生exit0、全输入与drain。覆盖此工程缺陷，不能追认旧E011/E012；143发送者仍UNKNOWN。新E031/E032已有当前退出链的成功使用证据，但不等于FWT已经重新完成。

## 槽位、空间、资源和截止

当前bucket余额：MAIN 2、REMOVE_ONE 2、LOCAL_DIAGNOSTIC 2、STATIC_WB64 1、FIXED_VICTIM 1；contingency、W_ONLY、WV-T/M均0。MAIN余2对应原未启动Btree条件，不是任意免费重试池。F_MINUS_W和完整fixed64 dirty＋RO继续不支持；此轮不开发、不用不等价替代物。

首选四次：DWT F_MINUS_R使用明确替换的FWT F_MINUS_W槽，其余使用原WB64和两个local诊断槽；累计最多36/40。第二选择三次：DWT F_MINUS_R同上、WB64同上、Vector F另用明确放弃的Conv F_MINUS_W槽；累计最多35/40，两个local诊断槽继续保留。E需在用户批准后按现有矩阵审批机制修改精确行及retry记账，保持原32行/各bucket配额与40次上限；A2此次不写入这些变更。上述两个组合互斥，不叠加自动执行。

资源快照：E自身门禁available RAM约218.7GiB（考虑cgroup），workspace free约29.7GiB，share free约41.2GiB；无活动lease。现有单端8GiB RAM、系统64GiB floor、workspace 5GiB floor＋2GiB monitor reserve、share40GiB floor均有空间。启动时E须重新检查全部活动lease与剩余增长；I/O压力本身不作为停机条件。默认最多两端并发，既有global CPU/32GiB RAM预约和最多4 simulator限制不变。

新增结果现用4,766,183,693B，6GiB余额1,676,267,251B；旧＋新19,075,760,077B，20GiB余额2,399,076,403B。四个原384MiB guard合计1,610,612,736B，仅余65,654,515B，不宜无条件预留四个满guard再额外增大日志。**建议E审核后为此批重封每端256MiB guard**（coordinator.py:464–465允许128MiB至既定FULL_GROWTH），加批次64MiB收尾/采样越界规划余量，总规划1,140,850,688B，仍余535,416,563B新增额度。已有相近成功结果含85MB main拷贝共约96–107MB，FWT旧树约123–127MB；256MiB具有实物依据，但不是未来输出保证。`maximum_result_bytes`不在科学identity/run_key内，改变资源终止边界时仍须保留旧spec、记录新spec、重新inspect/preflight；不更换资格、timeout或失败谱系。64MiB同样只是工程缓冲。保留既有monitor与非PASS资源终止语义，不删除历史证据、不增加6/20GiB上限。如果E坚持384MiB，可先两项、封存后按实余量准入其余，不因尚未填满guard而拒绝科学机会。第二选择3×384MiB=1,207,959,552B，另加64MiB仍在当前新增余额内。

资格准备估计15–45分钟，取决于E等价证据处置；不是已完成资格或时间承诺。首批四次在默认两并发下按两个wave规划，常态约2–3小时，timeout包络最多6小时（timeout不等于有效结果）；要保证两个3h wave均在既定窗口内，第一wave应在北京时间10/21 **15:00前**真正启动，第二wave仍须严格早于18:00，22:00前封存接收。无论批准多晚均不延长原T0或截止；每端当前时间＋3h应不越过intake。Vector替换可降低常态耗时，不触发自动补跑。

## DWT E031/E032交D消费

已向共享入口发送`A2_TO_D_DWT_E031_E032_KERNEL_COMPARISON_REQUEST_r1.json`，并行完成轻量只读复核。精确使用S E017、S_COPY_FREE E031、W_ONLY E032、F E018，四份raw SHA均与状态/终验一致，全部exit0、10kernel/148684429指令、正常终止、hardware drained；未混用E027/E028失败尝试。

逐kernel表见`DWT_FOUR_PROFILE_KERNELS.csv`。总cycles依次166519、166555、166792、167643；final residual全部0。**W_ONLY→F的+851=K5 +998＋K8 +157＋其余−304**。K5/K8新增RO查询均0，F的V查询68107/65536、landing wait sum718/339；只能定位额外时间，不能独立分摊V与RO、不能把等待总量当关键路径。DWT F_MINUS_R补齐S→W→WV→F相邻背景，正是此次P0的直接信息价值；仍不宣称无交互的机制贡献。
