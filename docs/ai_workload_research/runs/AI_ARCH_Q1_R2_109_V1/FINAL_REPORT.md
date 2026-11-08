# AI-ARCH Q1 R2｜真实端到端恢复链闭合；线程亲和观测缺口后STOP

日期2026-11-08（Asia/Shanghai）。执行终态RESOURCE_STOP，科学总体INCONCLUSIVE；NO_HARDWARE_CANDIDATE_PROMOTED。

本轮完成了真实GPU的旧状态恢复、自然step5–7、完整capture/save与sidecar发布、两份新状态再次加载，六个资格job均exit0。晚期生产job已启动并严格恢复到next8，随后因AFFINITY_OBSERVATION:161792:ProcessLookupError被监控安全规则停止。没有形成晚期C_D/C_V，没有正式性能样本，不是GPU容量不足或训练算法数值FAIL。

## Authority、新授权与隔离

CPU加固基线24a1d00b9c4d8130324e2984a14de369f9ba9c3b / tree f0ca2858909d19a41634430699d860eb1530f5f1；R1固定39e129a6db5236f7acc595b5abaef14331df8ac9，原科学合同34a598f4e5f40fffde337ae6b167bd4ffb3fccac。

用户明确回复“已授权且窗口生效，单窗口”。新START1794109954、新分支hrl/aiarch-q1-3dgs-late-pipeline-r2-109-v1及独立输出、private/cache全部重新绑定。原V1/R1/CPU加固authority、失败raw和状态只读。单窗口之外无授权，不使用剩余预算再取锁。

复用已接受235项CPU证据，未重做论文或历史全审计。原trainer、CPUAdam C++及二进制SHA复核一致；两份早期状态全部metadata/chunks SHA完整重核。47项有针对性的重新绑定CPU回归通过，执行源码在锁前冻结于EXECUTED_SOURCE_FREEZE.json及raw/PRE_GPU_SOURCE_SET.tar.gz。

## 合法资源与真实GPU结果

训练自身非独占CPU亲和8–21共14logical，监督/CPU helpers22–23；内核接受这些集合，不声称独占核心。准入前MemAvailable约55.6GiB、磁盘约131.8GiB空闲。原Image-Lab线上实例、loaded gate、quiescence、共同锁inode、预约、设备UUID、桌面活动及实际NVML准入通过；仅一次fcntl.flock(EX|NB)。

| job | 实际结果 | 科学范围 |
|---|---|---|
| RESTORE_C_E | exit0，next5，0新step | 实际Runner完整semantic状态一致 |
| RESTORE_C_R_E | exit0，next8，0新step | 同上，pending/frontier完整 |
| EARLY_CONTINUE_A1 | exit0，真实5–7，保存C_R2_A1 | 完整manifest、chunks、sidecar、owner及公开收据 |
| EARLY_CONTINUE_A2 | exit0，同状态真实5–7，保存C_R2_A2 | 独立A/A实际重复，不进入formal |
| RELOAD_C_R2_A1 | exit0，next8 | 新态GPU恢复严格semantic一致 |
| RELOAD_C_R2_A2 | exit0，next8 | 新态GPU恢复严格semantic一致 |
| PRODUCE_LATE | 启动，初始实际恢复next8通过，未完成 | 后续到达step未被持久化；不能补造进度/退出码 |

这次R1的保存NameError未重现。两份新状态都真实可恢复，不再是失败job的orphan storage。检查覆盖参数/梯度、optimizer moments/counters、pending CPU梯度、CPU apply frontier、RNG、loader/camera cursor及alias。原max_steps=200000、refine_stop=15000、原GS-Scale/Rubble算法、CPUAdam、SH与deferred语义未改变。

CPU-only顺序计划器不导入Torch/NVML、不持锁、不创建GPU进程，只向已持锁的唯一监督器写任务。冻结计划为原线程/窗口矩阵；任何失败即停，不筛选样本，不自动重试。实际在PRODUCE_LATE停止后，计划器HALTED_NO_NEW_JOB，没有启动正式点。

## 数值事实

新状态重新加载时完整semantic hash分别等于保存时hash；旧legacy pickle memo差异仍保留，不用Python immutable对象共享差异冒充数学错误，也不修改旧authority。

独立CPU程序重新核验历史C_R_E与两份新状态的manifest、metadata和所有chunks，并逐字段检查真实storage。历史对A1、A1对A2各44个Tensor字段中20个有bit差异；全部布局、alias拓扑和scalar/RNG/loader/frontier一致，浮点检查均有限。完整误差分布见raw/EARLY_ENDPOINT_INDEPENDENT_COMPARISON.json。A/A也存在差异，因此不能直接归因于恢复、某个kernel或算法不等价。没有新容差、continuation Numeric PASS或质量等价结论。

CPU比较约11秒，单进程HWM约107MiB，affinity22–23；不是Goal树/cgroup峰值。

## 为什么再次停止

失败原始row显示root和worker均为健康、同incarnation，已成功读取的线程亲和都在获准集合内。随后某次affinity(tid)读取抛ProcessLookupError。原代码只持久化外层PID161792，没有保存具体失败TID、该TID birth或消失复核。因此“短命线程在枚举后退出”是合理竞争解释，不能把它追认为已证明且合格的退出竞态。

这与之前VmSwap缺字段及semantic变量遗漏不同：本次没有Python监控未捕获崩溃，监督器按现行未解释观测缺口规则严格RESOURCE_STOP。不能将其归为CPU亲和越界、显存不足或主存超限。额外准入阈值也未触发。

当前合同尚无可接受的线程亲和退出censor规则；没有cpuset硬隔离证据时，更不能凭worker健康便声称所有短命线程亲和已完整观测。不能原样再试并期望该竞态自然消失，不自动R3或第二窗口。

## 资源与实际清理范围

累计持锁480.423746806秒，约8分；自身NVML取样峰值1278MiB、sampled进程树RSS11.510GiB、own session kernel charged peak12.366GiB。未观测到批准cap超限；实际监控缺口保留，不声明完整资源观测PASS或完整Goal峰值。持锁时间不是GPU busy时间，共享context及桌面逐进程活动缺口不冒称独占。

原终态NVML观测own_GPU_contexts_cleared=false，随后仍释放了锁和预约。这一顺序缺口明确保留，不能写成“持锁内清理通过”。后续CPU只读/proc与已有Image-Lab新鲜attestation确认全部已知自身PID消失、共同flock无holder、无自身compute、Image-Lab IDLE、无预约或在途scope。后续检查没有本地NVML初始化、CUDA或再次取锁。只能确认后查时已清理，不能反推context具体何时清除。

RESOURCE_RECEIPT.json原文与raw/SUPERVISOR_TERMINAL_ORIGINAL.json精确一致。只删除本轮已不用的短TMP symlink，保留全部状态和失败证据，不清历史资产。

## 本Goal内的CPU收口

在STOP后仅追加候选观测改进，未GPU复测：
- 以后亲和异常持久化具体正在读取的TID及错误详情；仍将未获资格的线程缺口判STOP，不实现隐式censor。
- 对自身进程结束后的驱动context，在原锁仍持有时增加有界清理观察（最多11次，读取间检查10秒deadline及原GPU期限）；不重新取锁，不延长预算。若观测失败或仍残留则保留RESOURCE_STOP/cleanup_gap。
- 清理观测异常不能让终态误留COMPLETE。
69项CPU回归通过，包含健康worker中短命TID错误仍STOP、context短暂残留后清除、持续残留有界退出与清理观测错误。实际执行版本已完整封存；最终工具中的这些改进不回写本轮raw，也不称已GPU验证。

## 未完成与结论

晚期完整C_D/C_V、T8/T16正式软件对照、observer ON、完整更新credit/drain性能、CPU/GPU关键路径归因、预冻结自然camera验证均未完成。FORMAL_SAMPLES.tsv只有表头，median/MAD/speedup为null，早期资格数据不代替正式性能。

本轮实质新增是完整真实GPU保存/恢复链资格及正常完成A/A续行证据；Q1晚期科学目标仍未完成。保留软件排除边界，不提出硬件候选。完成资源与数据收据、Git发布、远端commit/tree/blob回读和clean后STOP；不自动R3、第二scene、硬件、模拟器或RTL。
