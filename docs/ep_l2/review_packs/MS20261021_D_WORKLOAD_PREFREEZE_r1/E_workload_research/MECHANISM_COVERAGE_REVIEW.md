# 现有五输入的机制覆盖审查

本审查只提取已接受结果及现成D统计，供补充输入筛选；不替代D的正式机理归因，不授予运行资格。只写本目录，未读active raw、未解码任何raw、未扫描trace、未运行native/应用，未改registry或D工作树。精确绝对来源、SHA、原始计数和缺证项见同目录JSON。

五个应用名称本身不能证明覆盖充分。现在更明确的不足是**关键机制层次缺证**：全部五个MAIN F的实际Tag detach均为0；仅部分输入有真实V读取/dirty forwarding；没有已建立的地址不规则度、重用距离、同时活跃working set或DRAM带宽饱和度覆盖。继续增加同类应用名称，未必扩大这些机制轴。

旧main61有5对同binary物理S/F、13个条件控制对，五输入GM为0.9977331349×（−0.226687%），原七输入GM仍UNKNOWN。13个共享锚点的控制对不能计成13个独立workload。新binary两组capacity OFF/ON仍是既有CFD/Vector两个输入，不增加workload分母，也不能并入旧MAIN GM。所有负结果、FWT缺失及Btree HOLD保留。

## 量化的已覆盖部分

以下均来自D `MS20261021_D_PRIMARY_FOUR_SCIENCE_r1/ACCEPTED_PAIR_TERMINAL_MECHANISMS.csv` 的MAIN行。S关闭V/RO时对应族为UNKNOWN，表中的F=0是启用后的真实计数。

|完整输入|F V读取 / 查询|F dirty-forward|F RO admissions / merges|F detach|S WB-data-space request-waits|S→F cycles|
|---|---:|---:|---:|---:|---:|---:|
|cfd_097k|49,962 / 160,847|101|206,448 / 154,770|0|5|79,093→79,157|
|convolutionSeparable|36 / 1,181,110|0|1,251,551 / 880,056|0|848,913|292,932→291,469|
|dwt2d|23,305 / 311,718|943|39,836 / 29,871|0|30,282|166,519→167,643|
|sad|0 / 69,511|0|0 / 0|0|0|110,773→109,754|
|vectorAdd_4M|0 / 375,000|0|1,000,000 / 749,882|0|460,461|73,696→75,039|

- **复用/dirtywrite：部分覆盖。** CFD和DWT的真实V读取分别49,962/23,305、dirty-forward101/943；Conv仅36次V读取，Vector/SAD为0。V安装数或slot-cycle留存大，不代表发生有用读取。所有五个S/F都有WB字节；S的WB空间等待从SAD0到Conv848,913。等待统计是跨请求/切片观察，不能加成GPU stall比例。
- **RO合并：覆盖；实际detach性能：缺证。** 四输入有RO admissions，SAD为0；全部F detach=0。Vector有1,000,000 admissions、749,882 merges，但S/F lower reads均1,000,000；合并或避免allocation不自动等于少访存、饱和缓解或更快。
- **bank需求：覆盖；关键性：尚未完全识别。** 五组F物理bank grants都降低，S需求从483,611至9,217,033；耗时却有正负两种变化。Conv独立有限资源DATA_FREE使S+599、F−149 cycles，COPY_FREE另为+739；DWT COPY_FREE+36。不能据此推导硬件端口收益或单调上界。
- **队列压力：有变化；带宽瓶颈：缺证。** Conv line-MSHR wait observations40,088→150,118；Vector MissQ1,131,061→818,741，另有大量零等待输入。读流量跨度12,768至75,504,832B，单凭字节数/等待总和无法判定DRAM带宽或依赖延迟瓶颈；需匹配时钟域的busy、速率及并发数据。
- **phase：覆盖；参数/架构泛化：缺证。** 现有精确输入有1/2/3/5/10个kernel。DWT WV→F+925 cycles主要在K5/K8，而新的RO admission只在K1，显示跨阶段状态敏感性；不证明K5/K8直接RO lookup开销。每个应用仅一个输入点、一个冻结P1硬件点，未覆盖尺寸或架构分布。

## 不能从名字或静态footprint推出的结论

已存在且SHA绑定相同trace的闭世界oracle输入报告给出CERTIFIED_RO line数量：SAD396、DWT24,576、CFD51,612、Vector250,000、Conv294,912；这是分类/整epoch地址集合的输入事实。文件明确 `trace_reuse_order_inference:false`、`runtime_qualification:false`。它们不能充当重用距离、同时活跃working set、每set冲突率、warp coalescing或真实V reuse证据。

本次消费的统计没有给出地址stride/warp-sector分布、load依赖链或图frontier/degree分布，因而不能只凭CFD/Vector/SAD名字写“irregular/streaming/compute-bound”。也没有可证明五个输入构成随机或代表性样本的抽样合同。

## 新capacity两对提供的边界

|新binary完整配对|OFF cycles|ON cycles|OFF/ON|ON Tag身份占用界/65,536|ON分类|
|---|---:|---:|---:|---:|---|
|CAPACITY_DIAGNOSTIC_cfd_097k_OFF_ON_NEW_RUNTIME|79,093|79,742|0.991861×|1,570|UNKNOWN|
|CAPACITY_DIAGNOSTIC_vectorAdd_4M_OFF_ON_NEW_RUNTIME|73,696|42,788|1.722352×|5,862|UNKNOWN|

两端均同新main93a9，各为完整指令、64slice、独立接受。ON timed-clean/timed-dirty/host-prefill三类成功valid-victim replacement总数都为0；覆盖的最大资源比例分别约2.396%/8.945%。**两者仍为UNKNOWN**，因为64slice的MissQ完整full-check覆盖没有闭合；不是测试失败，也不能写成已证明near-unbounded。

ON同时改变多个容量及L2 data service，`hardware_P1_throughput_eligible:false`、physical grants0是诊断服务豁免。CFD+649 cycles、Vector−30,908 cycles不是capacity-only边际效应。Vector ON lower read/WB bytes都为0，OFF为32,000,000/12,872,704B；这确认计量范围内流量变化，但不能把其中的容量驻留、host预装填、data-service豁免、时序重排拆成唯一因果份额。ON零Tag replacement也不能证明任意更大输入都无冲突。

精确接受receipt：

- CFD OFF `/workspace/ep_l2_ms20261019_e_results/E037_a423c80f/parser_recovery_r1/run_status.json`；ON `/workspace/ep_l2_ms20261019_e_results/E038_d7ffe08b/parser_recovery_r1/run_status.json`。旧FAILED原件未改，新receipt为decoder恢复后的独立接受。
- Vector OFF `/workspace/ep_l2_ms20261019_e_results/E041_6412b85d/run_status.json`；ON `/workspace/ep_l2_ms20261019_e_results/E042_307fac20/run_status.json`。

## 最多四个优先补证层次

1. **有实际Tag detach的RO独立line压力。** 优先弥补五个F均detach0的空白。按完整来源/oracle和已有S独立line并发、Tag/payload压力筛选，验收时量化detach、lower事务和队列压力。不能按已知F加速比筛选，也必须保留仍为0的结果。
2. **可证实的victim重用及dirty-forward强度。** 用既有输入重用/dirty访问证据补足“安装很多、读取很少”的一侧，量化V读取/查询、dirty-forward/读取、字节与阶段耗时；保留无重用和负效应参照。
3. **footprint/set冲突与可量化地址不规则度。** 匹配有完整数据语义、已有活跃footprint/stride/sector证据的一个预登记输入点，分开说明host预装填、容量驻留和set冲突。整epoch line集合不替代动态working set；不生成无差别网格。
4. **bank/service压力与下游限制的对照层次。** 按现有baseline服务/队列和DRAM/ICNT busy/并发证据选输入，保留低bank压力比较端；量化同binary正常S/F及逐kernel结果。没有busy/速率证据时，明确不标带宽受限。

这些是供root与D/B/C匹配候选的机制层次，不是新执行清单；新输入和科学条件仍须完整来源、资格和用户范围审查。当前五对可以支持“这些冻结输入上机制触发与净收益混合、存在负效应”的有限结论；增加输入应优先填上述机制空白，不能只扩应用名字数量。
