# detach=0：E2 当前归因与批准四端执行

**原批准执行进行中；四个追加诊断已获用户批准并由原唯一中央控制器滚动执行。** 最新实际启动、逐条件状态、资源及结果预算见 [STATUS](STATUS.json) 和 [RECEIPT](RECEIPT.json)。不新建Goal或controller，不自动重试、加端或形成新S/F配对。

已完成两种不同原因：

- 新SGEMM E051：真实正向证书有效，但实际RO事务0；可见2282704次候选head观测全缓存命中，未产生可detach的活跃RO对象。跳过探测的head保持NA。
- CFD E052：真实RO事务51678、合并154770；1163176次实际FT生产Tag探测中reservation-fail为0，原始Tag失败触发分支从未进入，relieve与detach调用均0。不是“没有RO事务”，也不证明所有未观测路径Tag一直充足。79157周期及公共RO统计与原sameinput F相同，仅为复现描述，不产生跨binary S/F加速结论。

CFD [正式接受点](approved_four_r1/results/cfd_097k/CURRENT_ACCEPTED_POINT.json)、[独立终验与逐物理phase计数](approved_four_r1/results/cfd_097k/INDEPENDENT_TERMINAL_AND_CAUSE_REVIEW.json)和[D交付回执](approved_four_r1/results/cfd_097k/D_DELIVERY_RECEIPT.json)均已发布。D真实消费状态以本人ACK为准，不冒称完成。

DWT E053 也已独立接受并以E2-87交D：148684429条指令、167643周期、9965个RO事务，实际FT Tag失败/relieve/detach均0，公共cycles/RO计数与原sameinput F相同。见[接受点](approved_four_r1/results/dwt2d/CURRENT_ACCEPTED_POINT.json)。

Vector、Conv各有独立新r4 Q、完整原输入/条件证书及终验绑定。按实际资源准入执行；当前workspace约9GiB时原每运行监控预留只允许先单路，符合单路就滚动、不为多路等待。每端真实native exit0、完整指令/命令/64slice、212计数与退尽、身份和独立raw复核全部通过后才正式交D。大trace只按原runner启动前/结束后的必要身份检查读取；不重跑原生套件。

原SGEMM空证书、原FWT全epoch同line写入排除及其他历史失败/HOLD保留。E051原自动解析FAILED和费用不改；其正常native完整执行已凭明确工程证据经原中央API补充接受，未重跑。新版四端使用原CLI加已审固定decoder；分析中的物理phase不是因果kernel，跨phase事件差不当作存量。

保留原T0、原51次及后续照实计费、main61和冻结r4、10/24GiB累计生成、workspace5GiB底线+2GiB监控、CPU/RAM/Share及唯一中央锁。用户取消的全局次数、路数、时间限制不恢复。完整归因尚未标记完成；四端之外无额外启动授权。

E2现已直接并行完成四个已接受点的跨workload表及CFD/DWT/Vector逐物理阶段统计，见[直接归因报告](approved_four_r1/E2_DIRECT_PARALLEL_ANALYSIS_r1/README.md)。D消费不是执行前置。Vector E054已正式接受，Conv E055正由原控制器运行；累计55，批准四次已全部实际启动。
