# AI-ARCH Q1 3DGS R1｜恢复验收完成，续行保存缺陷与监控安全STOP

日期：2026-11-08（Asia/Shanghai）。

**执行终态 RESOURCE_STOP；科学目标未完成，结论 INCONCLUSIVE；NO_HARDWARE_CANDIDATE_PROMOTED。** 本轮真实取得共享GPU资格，完成两份早期状态的实际Runner恢复验收，并两次自然执行5–7。新增worker保存代码的NameError使两次job均未完成；第二次退出时监控未获完整健康资格，严格停止并释放窗口。没有晚期训练、正式性能或线程收益结论。

## Authority与新授权

V1固定为ba477c42561cb265714b030d1c4346ede035c292 / tree63b05bc76c953bdd9dd2201e236c73084205b982。原科学合同34a598f4e5f40fffde337ae6b167bd4ffb3fccac。用户在新的用户及109资源所有者授权、窗口生效及资源上限确认项下回复“我批准”；R1重新绑定START1794106687、工作区、输出、缓存和资源账，不沿用V1剩余预算。所有历史authority、旧raw、checkpoint与STOP只读。

批准上限8h Goal、10800s持锁、14336MiB自身显存、40GiB sampled RSS、48GiB可信charged、新增64GiB且free≥32GiB、训练≤16logical/监督≤2logical均未放宽。实际训练亲和8–21（14logical），helpers22–23，属于内核允许范围内的自身非独占亲和，不声称独占CPU。

## 资格与实际执行

复用接受的GS-Scale/Rubble输入与环境，不重新调查论文或全量历史raw。原trainer、CPUAdam C++及二进制SHA一致；Python3.10.12/Torch2.2.0+cu121/IPEX2.2.0/NumPy1.26.4/psutil6.0.0身份复核。C_E、C_R_E的metadata与全部chunk SHA重新完整核验。旧大型状态通过只读resolver使用，未复制或改写。

针对性CPU回归164项通过（监控/协议122、store30、worker控制12），源码在取锁前冻结，精确版本保存于raw/PRE_GPU_SOURCE_SET.tar.gz。CPU测试没有覆盖实际Controller.save调用，是本次测试缺口，不能用164项通过宣称GPU路径全面验证。

唯一一次共同fcntl.flock非阻塞取得成功。Image-Lab实际实例、loaded gate、quiescence、预约、锁inode、设备UUID和活动准入通过；未重新部署门控或canary，一个GPU owner串行执行。

| 真实job | 实际结果 | 判定范围 |
|---|---|---|
| RESTORE_C_E | exit0，next5，0个新训练step | 实际Runner数学状态严格恢复一致 |
| RESTORE_C_R_E | exit0，next8，0个新训练step | 同上，CPU已apply至6、pending7、prepared camera8 |
| C_E_CONTINUE_A1 | 原自然step5–7后保存触发NameError，exit1已记录 | manifest/bundle/chunks写出，job未完成 |
| C_E_CONTINUE_A2 | 同样保存NameError；终态OS退出码未记录 | 同样保留失败payload，不能补造exit1或成功 |

第一条续行失败已通过严格finished-worker核验退出active预期，监督器保留return1并在同一锁内继续A2。A2退出期间出现WORKER_NOT_HEALTHY_OR_VERIFIED_NORMAL_EXIT及五项缺VmSwap未获安全censor资格；随后RESOURCE_STOP，不继续取锁。

## 数学状态与数值行为

旧legacy fingerprint含Python pickle immutable memo对象共享细节，CPU反例证明等值数学状态可有不同legacy hash。旧指纹和不一致事实全部保留，不改V1。

R1新增严格semantic fingerprint：保留Tensor对象与storage alias、dtype、device、shape/stride/offset、原始storage bits、mutable alias、optimizer/pending/frontier、RNG、loader/camera等；仅排除无数学意义的immutable memo选择，不采用任何新数值容差。两份旧状态在真实Runner重建后均严格一致。此为实际恢复事实，不等于后续数值轨迹或晚期资格PASS。

两个续行payload均在save_state完成后、写sidecar时失败。它们明确标为FAILED_JOB_ORPHANED_COMPLETE_STORAGE_NOT_RESTORE_QUALIFIED，不事后补造成功收据、sidecar或GPU恢复资格。独立CPU检查的原始证据在raw/EARLY_ENDPOINT_INDEPENDENT_COMPARISON.json。

历史C_R_E对A1，以及A1对A2，各有44个Tensor中的20项bit不同；layout、alias topology和scalar/RNG/loader/frontier一致。quat最大绝对差分别约0.00289011、0.00301355。A/A也出现同量级差异，因此不能把历史与恢复轨迹之差单独归为恢复错误，也不能直接定位为某个GPU kernel。没有适用的新质量容差，不判continuation Numeric PASS，不做性能等价推断。详细有限性、逐字段差异和CPU检查资源范围以独立结果文件为准。

## 工程失败与STOP边界

新增Controller.save使用semantic变量前未赋值，是真实工程缺陷。两次保存错误及其精确执行源码保留。后续CPU回归实际调用保存方法，修复前复现NameError、修复后通过；最终工具目录中的修复版没有GPU复测，不改写原执行失败。

监控对异常worker退出时的健康资格要求未满足。保存缺陷与监控STOP分别登记，不说成GPU显存不足、锁冲突或3DGS资源瓶颈。不能因为退出看似普通便忽略独立观测缺口；原唯一窗口已经释放，不能把剩余预算作为再次取锁授权。

## 资源与清理

持锁205.073844118秒，约3分25秒，不是GPU忙碌时间。监督窗口观测峰值：自身NVML1186MiB，sampled进程树RSS11.564GiB，session kernel charged峰值8.847GiB。未观测到批准cap超限；真实监控缺口保留，不声明完整Goal峰值或资源观测PASS。cgroup为只读root-owned独立SSH session，未设置可写硬上限。共享context与桌面逐进程活动遥测边界继承保留，不冒称完全独占GPU实验。

最终持锁内NVML确认自身context清除；共同锁unlock/close、NVML shutdown、预约释放均有原始收据。CPU后查自身PID消失、锁无holder、Image-Lab IDLE且无预约/在途scope。只移除本轮短TMP别名，保留失败IPC、所有实际chunk和日志，不清理旧资产。RESOURCE_RECEIPT.json原文与raw/SUPERVISOR_TERMINAL_ORIGINAL.json精确相同。

## 未执行与科学结论

晚期C_D/C_V、完整late state、T8/T16正式对照、observer OFF/ON配对、更新credit/drain性能、CPU/GPU关键路径、保留camera窗口验证均NOT_EXECUTED。FORMAL_SAMPLES.tsv只有表头；median、MAD、speedup均null，不制造性能负例。

本轮新增的是早期真实恢复与续行数值敏感性证据，不是Q1晚期资源归因。无法评价强软件后的物理资源剩余成本，不晋升硬件候选。完成独立Git发布、fetch-back、commit/tree/blob核验和clean后STOP；不自动R2、第二scene、模拟器或RTL。
