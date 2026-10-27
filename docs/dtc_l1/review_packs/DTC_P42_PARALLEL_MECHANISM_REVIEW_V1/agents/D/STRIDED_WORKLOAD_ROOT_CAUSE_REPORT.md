# ATAX / MVT / BICG 负收益归因（Agent D）

**已确认负收益来自跨步访问 kernel，并能在同一计数域精确解释“L2 接受读量少、DRAM 读量反而多”：DH 下行请求数量下降，但被接受的 L2 请求中 miss 比例明显上升。** 这证明流量关系，不等于已经证明造成 miss 上升的唯一微架构根因。

只使用冻结 23 项中的三个预先指定完整输入与原始 accepted 四配置；Core `2e3bef4364e578cddd0e881c0baace2e51c55930`。不替换为修复源，不删除负例，不修改 v0.23。

## 1. 原始性能与流量

|程序|CM/DM|DM/DH|CH/DH|DH cycles 增加|L2 accepted读量 CH→DH|DRAM读量 CH→DH|accepted L2 miss比例 CH→DH|
|---|---:|---:|---:|---:|---:|---:|---:|
|ATAX|0.763661|1.272575|0.891739|12.14%|-25.40%|+15.95%|25.38%→39.44%|
|MVT|0.665740|1.179869|0.766303|30.50%|-25.72%|+31.74%|23.91%→42.41%|
|BICG|0.616013|1.434765|0.916784|9.08%|-30.63%|+14.02%|24.02%→39.48%|

两边 `L2 GLOBAL_ACC_R TOTAL_ACCESS = 4 × 实际下行128B请求`；DRAM atom 为32B。六个原始 cell 都满足 `DRAM issued read atoms = L2 GLOBAL_ACC_R MISS + SECTOR_MISS`。因此可精确拆为：

`DRAM_DH / DRAM_CH = (L2accepted_DH / L2accepted_CH) × (accepted_miss_fraction_DH / accepted_miss_fraction_CH)`

这里 RESERVATION_FAIL 是未接受的尝试；MSHR_HIT 是补充状态，不能额外加到 accepted 总数或将 retry 当作 miss。上述口径由 `gpu-cache.cc:980–1000,1073–1088`、`l2cache.cc:829–850,897–904`、`dram.cc:555–580` 核对。两种设计都按完整128B下行读并在L2分成4sector，不能把差距归为“只有DH多抓了4倍sector”。

## 2. 负收益在哪一段

|程序/慢kernel|CH cycles|DH cycles|慢段DH增加|占CH应用cycles|慢段accepted miss sectors CH→DH|
|---|---:|---:|---:|---:|---:|
|ATAX K1|26,677,630|30,226,439|13.30%|93.84%|14,637,516→17,313,036|
|MVT K1|24,828,424|33,032,429|33.04%|93.41%|13,538,536→18,567,980|
|BICG K2|24,549,302|27,030,465|10.11%|93.35%|13,415,640→15,591,280|

相反，三个顺畅合并访问的另一 kernel 在 DH 均变快。ATAX/MVT 慢段为 `tmp=A*x` / `x1+=A*y1`，BICG 慢段为 `q=A*p`。源码规模4096、float4B：同一矩阵指令相邻lane跨度16384B；线程自己的内循环步进4B。不能把“单线程连续”误写成“warp访问连续”。另一kernel矩阵lane步进4B。源码函数/行号/SHA、两个kernel身份、CTA和指令人口逐项保留在JSON。

共享索引完整扫描慢kernel、逐文件SHA匹配：ATAX/MVT 各524,544条unique128B线，BICG524,416条；每个17,301,632个静态line-reference events，复访约32.98–32.99。交替32-line矩阵load与1-line广播/其它load是独立地址证据。**它不等于32次DRAM读取，不提供真实跨SM时间顺序，不证明在途重复请求。** 本Agent未再扫描trace。

每慢kernel16CTA、每CTA256线程、128warp，GPU64SM；最多16SM能同时承载这些CTA。低CTA限制延迟隐藏，但CH/DH共享同一人口，不能单独解释设计差异。静态unique慢段load footprint约64MiB，大于40子分区合计10MiB L2；这不能据此断言活跃重用工作集不适配，更不能代替L2逐set替换序列。

## 3. 排队与反压：已有事实及边界

|程序|avg_mrq CH→DH（core cycles）|mem_fetch平均延迟 CH→DH|ICNT→L2入口受阻事件 CH→DH|DRAM读atom最大controller/均值 CH→DH|
|---|---:|---:|---:|---:|
|ATAX|412→745|620→2369|31,062,137→158,348,591|1.755→1.806|
|MVT|455→738|620→2230|32,670,735→152,064,800|1.745→1.812|
|BICG|526→791|736→2548|42,823,201→157,588,835|1.697→1.783|

`avg_mrq_latency` 从 DRAM接口创建 dram_req_t 起，到FRFCFS把请求分配到bank为止（dram.cc:237–257；dram_sched.cc:231–250；mem_latency_stat.cc:352–365）。它是排队/调度等待的直接模型观测，**不是完整L2→DRAM往返延迟，也不含更早L2 FIFO停留和后续bank服务**。两设计请求人口不同，不能相减后给因果份额。

`gpu_stall_dramfull` 实为 `gpu_stall_icnt2mem` 的旧打印标签：L2时钟每tick对子分区检查，入口full且ICNT真有包才累加（gpu-sim.cc:1845,2432–2446）。它既不是PQ那个L2→DRAM FIFO-full，也不是GPU独占stall-cycle；不能除以总cycles直接声称“受阻百分比”。

DH的controller读流量不均衡更明显，与miss比例上升、等待增大和慢段退化相关。但没有真实请求时间序列、set/victim/fill事件，尚不能断言是L2冲突替换、容量压力、相位错位、跨SM请求节奏或同线重取中的某一个。输入地址跨度还包含不连续分配，不能把地址span视为dense working set。

## 4. OO完成/物理池是否另有独立阻塞

|程序|OO lower-create queue-full|ready-but-WB-blocked事件|load全ready→complete均值cycles|全部SM时间均值PIB项|全部SM时间均值physical行|
|---|---:|---:|---:|---:|---:|
|ATAX|0|553|4.2261|1.6757|152.6143|
|MVT|0|744|4.2828|1.5876|152.6440|
|BICG|0|1576|4.3245|1.6477|264.9822|

共同lower-outstanding-cap-full也明确为0。上述实测拒绝点与后段service数据不支持把全部退化直接归给lower-create队列或写回服务；但不排除**全ready之前**的Tag、metadata、physical或PIB admission阻塞。均值分母含idle SM与先前kernel留下的Tagvalid/Ref0物理行，不能归一到16个活跃SM后声称“池已满”。终点occupancy=0更不能否认运行中满过。

**明确缺失：** OO PIB-full拒绝、NO_FREE_LINE/physical耗尽、allocation-width限流、OO Tag-bank conflict、逐请求L2替换/真实复用距离、同线物理generation重叠的DRAM请求、分阶段排队分布。源码确有OO PIB-full返回false（dtc-l1-common.h:544–557）和NO_FREE_LINE路径（637–698），终端未打印对应统计，因此为null，不能记0。

CH的4bank×20stage L1流水与DH的Tag+1、返还metadata+1、4waiter/SM/core-cycle、4sector gather/core-cycle、1instruction retire/core-cycle不等价；不能把20cycle写成串行吞吐1/20。DH完整read不走相同20stage hit队列，但也承担真实返回/收集代价。见Agent C源核查；本比较保留容量96KiB vs80KiB、logicalTags512、OO PIB128、conventional地址merge上限等差异，不声称等面积单机制收益。

## 5. 假设判级

- **H1 CONFIRMED：** DH has fewer accepted L2 GLOBAL_ACC_R sectors but a larger accepted-miss fraction; its accepted read misses exactly match issued DRAM read atoms in each of these six closed original cells. 限制：Arithmetic and counter-domain explanation; does not establish which schedule/cache policy caused the miss increase.
- **H2 CONFIRMED：** Negative application differences originate in strided kernel: ATAX/MVT K1, BICG K2. The other, coalesced kernel is faster under DH. 限制：Kernel-level localization only, not unique microarchitectural cause.
- **H3 CONFIRMED：** Same input has matrix lane stride 16384 bytes, alternating 32-line and broadcast/1-line global load records, about 33 static 128B line references per unique line and only 16 CTAs on 64 SMs. 限制：Trace body order is not simulated cross-SM time; static repetition is not a duplicate outstanding request. Low CTA is shared and cannot independently explain CH/DH difference.
- **H4 SUPPORTED_ASSOCIATION：** DH has greater L2 accepted-miss fraction, higher controller request imbalance, higher DRAM-scheduler pre-bank waiting and greater ICNT-to-L2 input backpressure while strided kernel slows. 限制：Temporal locality/replacement/re-request timing is a candidate connecting path. No address-timestamp L2 replacement or DRAM overlap history is available.
- **H5 UNPROVEN：** Tag invalidation while physical references remain live causes overlapping DRAM reads for the same line across distinct physical generations. 限制：Deferred reclaims and static revisits exist; no request-ID/address/generation/timestamp join proves duplicate DRAM traffic. Could be sequential re-miss after reuse, altered scheduling, bank conflicts, or combinations.
- **H6 UNPROVEN：** Independent OO physical-pool exhaustion or PIB saturation materially causes the remaining slowdown. 限制：Source has real NO_FREE_LINE and PIB-full rejection paths, but corresponding OO terminal counters were not printed. Mean occupancy and final current occupancy cannot establish absence or saturation.
- **H7 SUPPORTED_ASSOCIATION：** Measured ready-to-complete post-ready service is only a few cycles and ready-but-writeback-blocked events are small, while lower-create queue-full and common lower-cap-full are measured zero. 限制：Evidence reduces the plausibility of those measured points dominating; it does not exclude pre-ready metadata, bank/Tag, allocation-width, physical or PIB admission blocking.
- **H8 UNPROVEN：** DRAM bandwidth or the L2-to-DRAM FIFO is the sole causal bottleneck. 限制：avg_mrq_latency excludes prior L2 FIFO residence and later bank/DRAM service. E reports mixed PQ CH effects and PS changes both service and absolute DRAM timing plus traffic; all DH P0-to-PQ/PS sensitivity pairs and relative recovery factors remain pending in its fixed snapshot; the BICG PS CH/DH within-profile pair is already accepted.
- **H9 CONFIRMED：** CH and DH have unequal L1/data/Tag geometry, per-address merge limits, PIB design and hit/complete timing. 限制：Original four-config evidence compares complete modeled designs, not an isolated equal-area Tag/Data-decoupling effect.

## 6. 正在执行的PQ/PS：独立来源旁证

仅消费Agent E固定 `2026-10-27T07:32:45+00:00` 发布快照：10accepted / 8pending。Core9eed、FW02775；不再读取活动raw、不重新调度。CH完整输入PQ的P0/PQ为ATAX0.924878、MVT1.127420、BICG1.079744；对应DRAM变化+9.524%、−13.303%、−7.147%。同队列改动已改变请求流量，而非只减少固定人口的排队。

CH PS为1.371738、1.444049、1.170177，DRAM读量反而分别增加42.665%、31.590%、66.010%；PS既提高DRAM域服务频率，也缩短原周期参数对应的绝对纳秒时序，不是纯带宽加倍。此快照所有DH配对及相对恢复K仍PENDING，不能声称DH恢复多少，更不能拿新源CH替代原2e3的CH。CH新源P0 cycles即使恰好与历史一致，也不自动赋予跨源DH等价性。

## 7. 最小后续区分实验（仅设计）

1. **Bounded observation-only matched CH/DH request and blocking attribution** — `NEW_SCIENTIFIC_EXECUTION_APPROVAL_REQUIRED`。Three frozen full input digests; six matched CH/DH points on one explicitly registered Core/FW/binary. No replacement of original accepted cells. Prefer same scientific model as downstream18 for any future joins, after proving observation-only timing equivalence; never combine cross-source control values. Only bounded instrumentation and counters; no queues, capacities, service quotas, timing, Hash or scheduler changes. Counters per SM/kernel for PIB-full, NO_FREE_LINE, allocation-width, Tag grant rejects, lower-create/full, refill/notify/gather/retire blocking; record request lineage at lower creation, L2 accepted lookup, replacement/fill, DRAM ingress/bank assignment/column issue/return. 目的：Simultaneous same-line DRAM duplicate vs later sequential re-miss vs L2 replacement/locality and which blocking point actually delays progress. Same address alone insufficient; count accepted requests once by root+sector identity.
2. **One-factor L2 associativity/capacity sensitivity after request audit** — `NEW_SCIENTIFIC_EXECUTION_APPROVAL_REQUIRED`。Start with MVT CH/DH, the largest original relative regression; registered full digest unchanged. Two additional variant points against a matched same-build pair. Predeclare L2 ways16->32 with sets128, line128B, sector32B and partition mapping unchanged; fixed hit/port timing and all other parameters. Capacity rises10MiB->20MiB. 目的：Whether increased L2 residency reduces observed repeated accepted misses/DRAM atoms and recovers cycles. This diagnoses residency sensitivity but cannot alone separate conflict from capacity; request-event replay into a shadow fully-associative cache requires actual temporal sequence.
3. **Only if blocking counters implicate physical or completion resource** — `NEW_SCIENTIFIC_EXECUTION_APPROVAL_REQUIRED`。One predeclared culprit input, one DH variant plus matching same-build DH baseline; separate single-factor contracts. Choose exactly one resource from evidence: physical lines640->768, OO PIB128->256, or matched pipelined completion service. Never enlarge all at once. 目的：Measure reduction of the named reject/blocked event and corresponding accepted miss/DRAM/cycle response. If counters do not implicate resource, do not run this variation.

优先请求级只读观测插桩，其次只对最大退化MVT做L2驻留敏感性；资源扩容仅在计数器指出具体阻塞后选择一个变量。任何新执行都需单独科学合同/预算，不能重发已有PQ/PS。

## 8. 可追溯性与交付

`STRIDED_WORKLOAD_ROOT_CAUSE_REPORT.json` 为每个输入保留完整digest、原始四配置accepted/strict/DONE/archive/launch/config与实际Core/Framework/binary身份（沿用Agent A独立92celljoin）；CH/DH额外保留原始rawSHA、每个原始计数器行号、kernel人口和累计差分。`CLOSED_RAW_EVIDENCE.json.gz`仅六个已关闭旧raw提取，解压SHA逐项对上DONE。`SOURCE_SEMANTICS.json`为精确旧Core的逐行源码证据和全文SHA。`../B`共享特征/索引为唯一trace producer，扫描更正单独保留；`../E`快照独立标源。

验证通过 171 项身份/源码SHA/计数器人口/累计差分/流量分解检查；本Agent模拟启动0、trace扫描0、活动raw读取0、controller/Goal/lease/config/ledger修改0。
