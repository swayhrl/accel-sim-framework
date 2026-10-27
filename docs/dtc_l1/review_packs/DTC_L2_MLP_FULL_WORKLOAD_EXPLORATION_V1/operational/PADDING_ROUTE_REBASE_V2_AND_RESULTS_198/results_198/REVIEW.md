# DTC L2科学增量消费 V1

快照：北京时间2026-10-27 22:59:15。对照checkpoint04（21:50:23），accepted由172增至198：新增26个闭合点，另外因P0新完成形成更多配对，本次新增或新可匹配DH比较共30条。该快照仍有69个确认运行、83个pending；没有被当作accepted的失败点。

35输入中CH-P0完成26、DH-P0完成23，完整DH-P0+八变体完成10。当前共143条严格匹配DH/P0比较；没有一个统一变体达到35个完整配对，不能据此正式选套件winner。七个UNRESOLVED仍独立排除。

只打开checkpoint04之后26个新增accepted raw，旧172条提取按UUID/RESULT SHA复用。198/198 raw闭合/stream覆盖和身份均通过；99条有正值拒绝原因、99条未打印正值字段，后者保留None。未修改strict、原始结果、矩阵、派发或搜索规则，未启动或重跑模型。

## 三项负例的新完整结果

加速比=DH_P0 cycles / DH_variant cycles，>1才更快。下面保留E384已有结果作为新点的上下文；其余未accepted的E/M/Q/F项在覆盖表中明确缺失。

|输入|配置|P0 cycles|当前cycles|DH加速|L2接受读变化|DRAM读变化|L2拒绝尝试变化|
|---|---|---:|---:|---:|---:|---:|---:|
|ATAX|E384|31,880,220|30,987,395|1.028813|-0.172%|-4.847%|-5.757%|
|ATAX|F256|31,880,220|31,321,955|1.017823|-2.809%|-2.213%|-3.100%|
|BICG|E384|28,685,812|28,830,072|0.994996|+9.680%|-3.817%|-6.759%|
|BICG|M8|28,685,812|29,657,807|0.967226|-6.970%|+3.092%|-4.411%|
|BICG|F256|28,685,812|28,883,488|0.993156|-0.189%|-1.297%|+0.949%|
|MVT|E384|34,687,540|34,862,954|0.994968|-2.344%|+1.375%|-0.978%|
|MVT|E768|34,687,540|34,862,954|0.994968|-2.344%|+1.375%|-0.978%|

- **MVT E384与E768完全同cycles和本表计数器**，都是0.994968x。L2接受读下降2.344%，但DRAM读增加1.375%；MISS_QUEUE_FULL从52,360,071升至151,908,183。MSHR_ENRTY_FAIL在新raw未打印，仍是None。这与压力移向发送队列相符，尚不能单独证明哪一级决定性能。
- **BICG M8退化至0.967226x**：merge拒绝15,401→6,638，entry拒绝142,533,205→132,138,078，但miss-queue拒绝15,514,452→18,914,524、DRAM读增加3.092%。减少某一类拒绝并不保证更快。F256也仅0.993156x，不能把更大的调度窗口当成无条件收益。
- **ATAX F256有1.017823x改善**：DRAM读下降2.213%，MISS_QUEUE_FULL 18,806,950→25,877，entry拒绝却139,657,561→153,600,188；末次MRQ均值745→1,873。MRQ是排队/调度阶段的观测均值，不是完整L2→DRAM往返时延，也不能单凭它判断全应用吞吐。

这三项的非P0 CH均尚未有accepted对照，relative DTC improvement与同配置CH/DH都保留None；不能用CH-P0除以DH-variant来宣称DTC相对优势恢复。

## 新增最值得关注的正负案例

|输入|配置|DH自身加速|DRAM读变化|L2拒绝尝试变化|说明|
|---|---|---:|---:|---:|---|
|convolutionSeparable|F256|1.422263|-0.005%|-31.402%|P0新完成后首次可比|
|convolutionSeparable|F128|1.187151|-0.005%|-17.023%|新variant完成|
|2DCONV|F256|1.078012|+0.000%|-47.937%|P0新完成后首次可比|
|2DCONV|F128|1.057515|+0.000%|-37.754%|P0新完成后首次可比|
|2DCONV|M8|1.036346|+0.000%|-57.977%|P0新完成后首次可比|
|BICG|M8|0.967226|+3.092%|-4.411%|新variant完成|
|BICG|F256|0.993156|-1.297%|+0.949%|新variant完成|
|convolutionSeparable|E768|0.993961|+0.007%|-3.999%|新variant完成|

**convolutionSeparable F256达到1.422263x、F128为1.187151x**。F256 DRAM读只下降0.00475%，L2接受读反而增加0.0953%，因此收益无法用大幅削减流量解释。读miss-queue拒绝17,062,330→2,900,015，entry拒绝1,057→9,192,483，MRQ均值321→905；这些支持发送/调度并发结构改变的关联证据，不能隔离FR-FCFS窗口与memory-partition credit的贡献。F256共享credit从255增至447，DRAM始终850MHz。

**2DCONV的P0现在完成**，八变体均可合法比较；F256为1.078012x、F128为1.057515x、M8/M16各1.036346x。DRAM读量不变，说明至少存在流量以外的影响。MRI-Q的E384/E768/M8与P0的cycles及本次摘取计数器全部完全相同；本轮这三项尚未显示作用，不能称为本次miss减少。以前Hash比较的miss变化属于另一组对照，本次不迁移其结论。

拒绝数是尝试次数，不是唯一miss、唯一请求数或应用停顿cycles。未打印的reason不填0；计数变化和性能变化是关联，不是隔离的因果结论。

## 部分统一配置统计

各行左侧使用各自已完成配对人口，不能直接排名；右侧固定同一10输入、八配置均完整的共同集合。两者都不是完整35输入结论。

|配置|可用配对n/35|DH GM|正/零/负|固定共同10输入GM|
|---|---:|---:|---|---:|
|E384|20/35|1.001399|3/13/4|1.000977|
|E768|20/35|0.999926|2/14/4|1.000977|
|F128|15/35|1.016456|3/11/1|1.007355|
|F256|20/35|1.017563|4/12/4|0.998656|
|M16|18/35|1.002349|3/15/0|1.004228|
|M8|18/35|1.000263|3/12/3|1.003806|
|Q128|17/35|0.999485|1/13/3|0.999242|
|Q64|15/35|1.000237|2/11/2|1.000411|

例如F256在20输入可用人口的GM为1.017563，但同一10输入共同人口GM为0.998656；F128在共同人口为1.007355。人口改变足以改变表面排序，不能据本次快照晋升统一参数或触发组合。

## 全35覆盖简表

A=accepted；其余列明未验收状态。DH变体列只数八个非P0配置。完整SHA及全部cohort/UUID、RESULT/raw路径和SHA在ANALYSIS.json/report.json中。

|程序|suite|CH P0|DH P0|DH变体A/8|本次新A点|未accepted变体|
|---|---|---|---|---:|---:|---|
|BlackScholes|CUDA Samples|A|A|8/8|0|—|
|convolutionSeparable|CUDA Samples|A|A|4/8|4|E384:RUN, M8:RUN, Q64:RUN, Q128:RUN|
|fastWalshTransform|CUDA Samples|A|A|7/8|0|F128:PEND|
|histogram|CUDA Samples|A|A|8/8|0|—|
|mergeSort|CUDA Samples|A|A|6/8|0|M8:PEND, F256:PEND|
|scalarProd|CUDA Samples|A|未A|1/8|0|E384:PEND, E768:PEND, M8:PEND, M16:PEND, Q64:PEND, Q128:PEND, F256:PEND|
|scan|CUDA Samples|未A|未A|0/8|0|E384:RUN, E768:RUN, M8:RUN, M16:RUN, Q64:RUN, Q128:RUN, F128:RUN, F256:RUN|
|transpose|CUDA Samples|A|A|8/8|0|—|
|vectorAdd|CUDA Samples|A|A|8/8|1|—|
|bfs|Parboil|A|A|7/8|0|M16:PEND|
|cutcp|Parboil|未A|A|0/8|0|E384:PEND, E768:PEND, M8:PEND, M16:PEND, Q64:PEND, Q128:PEND, F128:PEND, F256:PEND|
|histo|Parboil|A|未A|4/8|2|M8:RUN, Q64:RUN, Q128:RUN, F256:RUN|
|mri-q|Parboil|A|A|5/8|3|Q64:RUN, Q128:RUN, F128:PEND|
|sad|Parboil|A|A|8/8|0|—|
|sgemm|Parboil|A|未A|0/8|0|E384:PEND, E768:PEND, M8:PEND, M16:PEND, Q64:PEND, Q128:PEND, F128:PEND, F256:PEND|
|stencil|Parboil|A|A|6/8|5|E384:RUN, Q64:RUN|
|2DCONV|PolyBench/GPU|A|A|8/8|3|—|
|3DCONV|PolyBench/GPU|A|A|8/8|3|—|
|3MM|PolyBench/GPU|未A|未A|0/8|0|E384:PEND, E768:PEND, M8:PEND, M16:PEND, Q64:PEND, Q128:PEND, F128:PEND, F256:RUN|
|ATAX|PolyBench/GPU|A|A|2/8|1|E768:PEND, M8:RUN, M16:RUN, Q64:RUN, Q128:RUN, F128:PEND|
|BICG|PolyBench/GPU|A|A|3/8|2|E768:PEND, M16:RUN, Q64:RUN, Q128:RUN, F128:RUN|
|GEMM|PolyBench/GPU|A|未A|1/8|0|E768:RUN, M8:PEND, M16:PEND, Q64:PEND, Q128:PEND, F128:PEND, F256:PEND|
|GESUMMV|PolyBench/GPU|未A|未A|0/8|0|E384:RUN, E768:RUN, M8:PEND, M16:RUN, Q64:PEND, Q128:PEND, F128:RUN, F256:RUN|
|MVT|PolyBench/GPU|A|A|2/8|2|M8:RUN, M16:RUN, Q64:RUN, Q128:RUN, F128:RUN, F256:RUN|
|SYRK|PolyBench/GPU|未A|未A|0/8|0|E384:PEND, E768:PEND, M8:PEND, M16:RUN, Q64:PEND, Q128:PEND, F128:PEND, F256:PEND|
|dwt2d|Rodinia|A|A|7/8|0|Q64:PEND|
|gaussian|Rodinia|A|A|8/8|0|—|
|heartwall|Rodinia|A|A|8/8|0|—|
|hybridsort|Rodinia|未A|未A|0/8|0|E384:PEND, E768:PEND, M8:PEND, M16:PEND, Q64:PEND, Q128:PEND, F128:PEND, F256:PEND|
|lavamd|Rodinia|未A|未A|0/8|0|E384:PEND, E768:PEND, M8:PEND, M16:PEND, Q64:PEND, Q128:PEND, F128:PEND, F256:PEND|
|lud|Rodinia|A|A|8/8|0|—|
|myocyte|Rodinia|未A|未A|0/8|0|E384:RUN, E768:RUN, M8:RUN, M16:RUN, Q64:RUN, Q128:PEND, F128:RUN, F256:RUN|
|particlefilter_float|Rodinia|A|A|7/8|0|F128:PEND|
|particlefilter_naive|Rodinia|A|A|7/8|0|F128:PEND|
|srad_v1|Rodinia|未A|未A|0/8|0|E384:RUN, E768:RUN, M8:RUN, M16:RUN, Q64:RUN, Q128:RUN, F128:RUN, F256:RUN|

## 证据定位与边界

- checkpoint04：`/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1/derived_reports/checkpoint_04/dashboard/report.json`，SHA `a58786002bad18adca32e95949011f99a0f40d2d2e4c528677a984c1fab72c22`。
- 本次闭合快照：`/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1/agents/E/results_increment_v1/20261027T145915Z/report.json`，SHA `9d354efbde4f592ed278edb959e374b86a2001943092fd9996cf418e0922a117`。
- 仅26个新raw提取：`/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1/agents/E/results_increment_v1/20261027T145915Z/NEW_RAW_REASONS.json`，SHA `a703234dac0a530251e69b9a1b87e8a261c50fccca1d5477c759cadff3029dfa`。
- D基础生成器commit `fce10d92eb09bc8f562b84a5a84b202bbf1ea385`；raw-reason merger commit `927c8bd0a1d55a3e5491ee39d49a233330eca4fa`，各源码SHA在CAPTURE.json。
- 同input/完整population、Core `9eedb3131937748f0492fa83aad37d3691118d70`、Framework `02775fd795cde5aae1480d81cee6eb481d0a08f4`、binary与全部非目标effective options逐对核验：143对、0错误。
- 六个P0仅复用严格证明完全匹配的downstream18结果；没有用旧72矩阵的失败、修复验证或HOLD替代性能数据。
- 所有配置DRAM850MHz、L2容量10MiB、DTC/Hash结构固定；资源扩张不代表等面积。英文v0.23未修改。
- 尚不能确认：更深FR-FCFS与credit分别贡献多少；Tag/PIB/完成服务与下游等待如何交叠；精确occupancy/逐请求时间。缺失计数保持未知，未新增插桩或模拟。
- 本快照非跨文件事务；报告之后任务仍可自然完成。
