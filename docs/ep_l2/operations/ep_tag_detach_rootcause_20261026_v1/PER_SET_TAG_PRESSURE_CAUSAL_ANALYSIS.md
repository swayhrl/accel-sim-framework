# 每 Set Tag 压力的因果分析

级别约定：PROVEN为本轮可复核观测或精确源码结论；LIKELY为与证据一致但未隔离的解释；UNKNOWN为缺失；HYPOTHESIS为待验证机制。统计身份沿用 [访存路径主报告](GPU_MEMORY_PATH_BOTTLENECK_MAP.md)，不跨Core/binary拼接性能。

## 已有数据能分辨到哪一级

|工作负载|真实TagFAIL/relieve/detach|r5目标set covered最大 / newTag最大|newTag且16 RESERVED|额外全set时间观测|
|---|---|---|---|---|
|CFD E056，r5|0 / 0 / 0|4 / 3|0 head-cycle|本轮无完整raw，UNKNOWN|
|DWT E057，r5|0 / 0 / 0|3 / 3|0 head-cycle|本轮无完整raw，UNKNOWN|
|Vector native r5|0 / 0 / 0|3 / 3|0 head-cycle|每slice75039个L2 tick末样本；全64set中最大3，所有slice相同|

CFD/DWT来自既有accepted projection，不是本轮重读raw。其raw当前未在核查的本地roots找到；DWT历史恢复证明不能替代今天文件存在。Vector按实际raw最后snapshot选择64slice与32channel，结果与接受终态SHA绑定。

**未知项不补零**：r5 hist没有set index、Tag生成/释放事件时间或Tag lifetime；route保留slice和physical phase，但不能还原每个set的arrival/lifetime。CFD/DWT的全应用newTag∧eligible及完整reuse联合不在copied projection中，仍NA。TVDskip的requester/raw/eligibility也NA。

## Vector：存在并发且分散，并非全GPU MLP稀少

本轮 [JSON](MEMORY_PATH_EVIDENCE.json) 与 [CSV](UPSTREAM_TO_L2_MLP_FUNNEL.csv) 保留64个slice的独立行：

- 每slice的RO live transaction高水位90–96；真正issued且尚有未ready sector的独立RO line高水位63–70。两种高水位可以发生在不同时刻。
- B0的全slice RESERVED总数，时间样本平均整数下取整37–66，峰90–96；任一set峰始终3/16。
- descriptor高水位344–369/512；missq峰128、lowerq峰128；不存在“所有队列空闲所以Tag没压力”的证据。
- 一个严格空间下界：对每个slice，在总RESERVED达到该slice峰值的那个样本，单set不可能超过其全时段上界3，因此至少 `ceil(total_reserved_peak/3)` 个set同时含RESERVED，即30–32个不同set。这是由全域上界保证的同刻下界，不是把独立边际相乘，也不假设均匀分布。
- 不能把各slice峰相加成GPU同刻峰，不能用90−70推算queued事务数，不能将63–70除64推算任意指定set的概率。

B0在每L2 tick末、无head也采样，维护全cache的reserved_by_set compact状态，具体源码见 [模型审计](L1_ICNT_TLB_MODEL_AND_COUNTER_AUDIT.md)。这比r5 requester-conditioned观测更宽，但仍只覆盖tick末样本，不宣称捕获tick内任意瞬态。

## 目标set联合分布：这不是新Tag到达率

r5的newTag raw选MISS/RESERVATION_FAIL，不包含使用已有Tag的SECTOR_MISS：

|workload|newTag head-cycle总数|RESERVED=0 / 1 / 2 / 3|含义|
|---|---:|---|---|
|CFD|162681|144979 / 16025 / 1636 / 41|covered目标set暴露，可有同一head重试|
|DWT|450831|402510 / 47449 / 870 / 2|同上|
|Vector|915784|241972 / 639528 / 34089 / 195|同上|

因此不能用915784/75039当作Vector真实新Tag分配率；这些是反复preview的head-cycle。用同窗口真正接受的新line事务作arrival也要区分native、RO、新Tag分配、已有Tag sector miss。

Vector newTag且eligible实际head联合2385；same-set newTag且任意reuse head673364，rawFAIL且reuse为0。CFD UID5的234次三联合只是物理阶段newTag∧certifiedRO∧eligible，不是全应用二联合。r5实际production探测域的FAIL经验计数0/831673，也不是独立伯努利样本；不拟合置信区间或未测概率。

## VALID、MODIFIED、INVALID与replacement

Vector covered way分类只有RESERVED、REPLACEABLE_CLEAN、REPLACEABLE_DIRTY，INVALID为0；这是head/way暴露分布，不是全cache所有时间的状态直方图。B0 resident-valid平均957–986、resident-dirty平均286–294属于payload-resident统计，不能直接相减拼出每个set的Tag分类。

源码PROVEN：sector冷启动为INVALID；line有任一RESERVED sector才不可替换；INVALID可分配，VALID及MODIFIED可替换（dirty需要后续写回/资源门禁）。原始raw143明确perf_sim_memcpy1，317–318实际执行两段HtoD各16MB；prefill发生在RO epoch之前且无时序付费。prefill存在为PROVEN、它导致所有covered target set无INVALID为LIKELY；没有逐地址覆盖证明，不能当作FT初始状态强制全VALID。

## 合并如何降低Tag身份需求

Vector accepted RO requester1M，transactions250118，merges749882，约3.99811请求/事务、74.9882%请求merge。它与32B sector、128B line身份的共用一致，**PROVEN降低了相对sector请求数的事务身份需求**。不能称减少了同样比例DRAM流量：实际仍有1M读包、32MB读服务。

newTag请求、Tag reservation episode、RO事务和lower sector包不是同一个人口：已有Tag的sector miss也可能让一条line再次进入RESERVED；同linemerge可扩展required mask；ready但response待送仍持有descriptor，却不一定保留RESERVED Tag。只有把这些状态分别记录，才可能解释Tag压力形成。

## Little's Law可以怎样用，当前为什么不能代算

对固定slice `s`、固定set `j`，定义：

- `R_sj(t)`：该采样时刻真正为RESERVED的Tag数。
- `A_R_sj`：Tag从非RESERVED进入RESERVED的episode数，含新分配和已有Tag sector miss，分别打标签。
- `tau_R`：同一Tag generation及reservation-episode从进入到退出RESERVED的时间。
- `A_new_sj`：真正接受的新Tag分配数，另列offered/denied/merged；不是head-cycle暴露。

对相同人口、同一时间窗口并处理首尾carry-in/out，离散时间守恒关系为 `sum_t R_sj(t) = sum_episode overlap_duration`；在适当平均定义下有 `mean_R ≈ lambda_R × mean_tau_R`。不需要用全GPU平均来代替某个set，也不能把lambda_new直接替代lambda_R而忽略已有Tag的重新reservation。

当前没有 `A_R_sj/tau_R/A_new_sj` 联合，也没有每个set完整time histogram；B0只保留总数及跨set最大，r5只保留被请求target set的条件分布。因此本轮**不计算**每set Little Law、不用平均mf latency1266代Tag lifetime、不从全GPU19.99packet/cycle预测TagFAIL概率。

mf包含request创建到SM response-buffer接收及WRITE_ACK；icnt2mem/mrq区间嵌套且人口不同。它们不能证明Tag“很快就返回”，也不能证明某特定set因为长延迟必然满。

## 为什么最大值是3/4：证据分级

|解释|Vector|CFD/DWT|
|---|---|---|
|高L1命中遮蔽流量|PROVEN不符合本例：实际L1 100%miss|UNKNOWN|
|全GPU或每slice几乎没有并发|PROVEN不能这样解释：RO lower独立line每slice峰63–70、总RESERVED峰90–96|只有RO/target-set投影，不能给全路径结论|
|请求分散到多个set|PROVEN至少30–32set在各slice总峰时刻有RESERVED；精确分布和贡献率UNKNOWN|LIKELY候选，逐set数据不足|
|多个sector共用line/merge|PROVEN 1M请求到250118RO事务；贡献比例不能与其它因素独立分离|已有事务/merge数，但缺精确时序归因|
|L1/L2/DRAM有限queue限制后续入流|PROVEN有full/拒绝；它们导致max3的净贡献为LIKELY/UNKNOWN|UNKNOWN|
|RESERVED生命周期短|UNKNOWN；总memory latency不是Tag寿命，现有后端压力不支持轻率假定快速返回|UNKNOWN|
|Frontend/query/landing阻塞|PROVEN存在，query固定1cycle、commit bank/landing拒绝合81555|已有projection中提前路径，完整分层统计不足|
|TLB/PTW瓶颈|当前生产模型无该阶段，不能归因|同r5源码模型边界|
|真实NoC字节带宽瓶颈|当前LOCAL_XBAR不支持这种归因|需其精确config/raw，不补写|

结论是“已证明触发条件缺失，已证明Vector并发存在且分散；缺少分解权重”，不是“已经完全证明max3只由某一个上游gate导致”。

## 若上游约束独立line数量，T还剩多少机会

只有对同一slice/set证明其同时pending Tag硬上界K<16，才能推出该机制在该约束下无触发机会。目前没有这样的配置级硬上界证明；63–70是RO下游line的slice高水位，不是某set上界。观测到tick末set≤3及实际production TagFAIL0，只支持已接受执行条件中的零触发科学负结果。

T需要真实newTag失败、同set live attached !reuse missing的RO、可达的Frontend/commit路径及后续资源允许；当前精确执行中首个必要条件缺失。未来通过资源扩容/服务变慢制造16路pending，仅能研究敏感性，不能写成原始真实应用T收益。下一步优先验证后端服务/上游queue对cycles与Tag压力的关系；机制保持不变。
