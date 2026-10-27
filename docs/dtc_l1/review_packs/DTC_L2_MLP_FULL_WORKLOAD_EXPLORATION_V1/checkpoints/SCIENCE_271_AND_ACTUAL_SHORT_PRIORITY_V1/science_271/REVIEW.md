# DTC L2科学增量 V3：新增14点、完整输入增至23

快照：2026-10-28 **04:54:53 CST**。以已冻结257项快照（Main发布标识f519）为锚，现271 accepted＝265本轮＋6 references。仅新开14份accepted raw；旧257份raw与189条旧配对均按RESULT/UUID SHA复用。本轮只重做2条新配对的input binding/Core/FW/binary/全非目标选项及完整population验证，错误0。原始350格状态还包括23 confirmed RUN、55 PENDING和1个scan/M16 spent工程格；该格及未来补充V2均不进入accepted性能。

## 这次真正新增什么

ATAX F128、BICG E768完成后，完整DH-P0＋八变体的程序由21增至23，新增完整输入正是ATAX、BICG。总严格DH自身配对189→191。CH-P0新增GESUMMV、hybridsort、scan，覆盖30→33；DH-P0仍25，CH/DH-P0配对也仍25，没有新的DH基线完成。其余9个新DH变体仍等DH-P0，不能据它们的绝对cycles计算自身收益。

|程序|配置|cycles|本轮比较身份|
|---|---|---:|---|
|ATAX|DH-F128|31,894,637|新增DH/P0严格配对|
|BICG|DH-E768|28,830,072|新增DH/P0严格配对|
|GEMM|DH-F256|826,089|已accepted，待DH-P0|
|GESUMMV|CH-P0|114,860,845|CH-P0完成，DH-P0未完成|
|GESUMMV|DH-E384|89,424,572|已accepted，待DH-P0|
|GESUMMV|DH-F128|86,464,623|已accepted，待DH-P0|
|hybridsort|CH-P0|18,575,969|CH-P0完成，DH-P0未完成|
|scan|CH-P0|6,710,840|CH-P0完成，DH-P0未完成|
|scan|DH-M8|6,687,187|已accepted，待DH-P0|
|scan|DH-F128|5,748,280|已accepted，待DH-P0|
|scan|DH-F256|5,179,817|已accepted，待DH-P0|
|srad_v1|DH-Q64|7,324,411|已accepted，待DH-P0|
|srad_v1|DH-Q128|7,324,411|已accepted，待DH-P0|
|srad_v1|DH-F256|7,324,411|已accepted，待DH-P0|

新配对均未出现收益：

|程序/配置|P0 cycles|变体cycles|DH自身加速|L2接受读变化|DRAM读变化|总拒绝尝试变化|
|---|---:|---:|---:|---:|---:|---:|
|ATAX F128|31,880,220|31,894,637|0.999548|+2.370%|-0.290%|+2.351%|
|BICG E768|28,685,812|28,830,072|0.994996|+9.680%|-3.817%|-6.759%|

**ATAX F128接近无变化（0.999548x）**：miss-queue拒绝18,806,950→106,080（−99.436%），entry拒绝139,657,561→162,115,286（＋16.081%），末次MRQ745→1389。DRAM读只少0.290%，总拒绝反增2.351%；说明消掉一种排队拒绝并不等于提升应用吞吐。与既有F256 1.017823x相比，F128没有显示单调收益。这里是计数器关联，不是已隔离因果。

**BICG E768为0.994996x**：cycles及本轮所列流量与E384相同，DRAM读下降3.817%仍略慢于P0。miss-queue拒绝15,514,452→133,657,611，entry拒绝在该日志未打印，保持None。当前E384/E768在同一24个可配对输入上**24/24 cycles完全相同**；这只是已完成24输入上的饱和证据，不能替代剩余11输入或触发正式参数裁决。

## 更新后的可用与共同人口

每配置可用人口仍不同，右列固定同一23个完整程序。两组均不是全35统计，非P0 CH仍无匹配，不计算相对DTC改善或同配置CH/DH比。

|配置|可用n/35|可用GM|正/平/负|共同23 GM|
|---|---:|---:|---|---:|
|E384|24/35|1.000865|3/15/6|1.000902|
|E768|24/35|1.000865|3/15/6|1.000902|
|F128|24/35|1.009271|5/14/5|1.009676|
|F256|24/35|1.015101|5/14/5|1.015763|
|M16|24/35|1.001380|5/16/3|1.001440|
|M8|24/35|1.000709|5/15/4|1.000740|
|Q128|23/35|0.996101|4/13/6|0.996101|
|Q64|24/35|0.997210|4/14/6|0.997089|

共同人口从21变23，F256 GM 1.016754→1.015763、Q128 0.999307→0.996101。**这不是旧配置性能变了**：Q128本轮没有新配对，变化来自ATAX/BICG进入完整八配置共同集合。固定旧21上的原结论不变；当前23仍缺12输入。各suite完整人口现在为CUDA7/9、Parboil5/7、PolyBench5/9、Rodinia6/10；全部suite可用/共同GM与正平负分布保存在SCIENTIFIC_INCREMENT.json，不按收益删程序。

## 当前P0依赖

已accepted但因缺DH-P0暂不能配对的格由13增至22：srad_v1 7、GEMM6、scalarProd3、scan3、GESUMMV2、3MM1。GEMM、scan、GESUMMV、srad_v1的DH-P0已RUN；scalarProd和3MM仍PENDING。该优先级依据覆盖依赖，不依据收益。

|程序|缺失P0状态|已accepted DH变体|待P0配对数|
|---|---|---:|---:|
|scalarProd|DH:PENDING|3|3|
|scan|DH:RUNNING_CONFIRMED|3|3|
|sgemm|DH:PENDING|0|0|
|3MM|DH:PENDING|1|1|
|GEMM|DH:RUNNING_CONFIRMED|6|6|
|GESUMMV|DH:RUNNING_CONFIRMED|2|2|
|SYRK|CH:RUNNING_CONFIRMED, DH:PENDING|0|0|
|hybridsort|DH:PENDING|0|0|
|lavamd|CH:PENDING, DH:PENDING|0|0|
|srad_v1|DH:RUNNING_CONFIRMED|7|7|

## 全35覆盖

|程序|suite|CH-P0|DH-P0|DH变体A/8|新增A|
|---|---|---|---|---:|---:|
|BlackScholes|CUDA Samples|A|A|8/8|0|
|convolutionSeparable|CUDA Samples|A|A|8/8|0|
|fastWalshTransform|CUDA Samples|A|A|8/8|0|
|histogram|CUDA Samples|A|A|8/8|0|
|mergeSort|CUDA Samples|A|A|8/8|0|
|scalarProd|CUDA Samples|A|PENDING|3/8|0|
|scan|CUDA Samples|A|RUNNING_CONFIRMED|3/8|4|
|transpose|CUDA Samples|A|A|8/8|0|
|vectorAdd|CUDA Samples|A|A|8/8|0|
|bfs|Parboil|A|A|8/8|0|
|cutcp|Parboil|A|A|0/8|0|
|histo|Parboil|A|A|8/8|0|
|mri-q|Parboil|A|A|8/8|0|
|sad|Parboil|A|A|8/8|0|
|sgemm|Parboil|A|PENDING|0/8|0|
|stencil|Parboil|A|A|8/8|0|
|2DCONV|PolyBench/GPU|A|A|8/8|0|
|3DCONV|PolyBench/GPU|A|A|8/8|0|
|3MM|PolyBench/GPU|A|PENDING|1/8|0|
|ATAX|PolyBench/GPU|A|A|8/8|1|
|BICG|PolyBench/GPU|A|A|8/8|1|
|GEMM|PolyBench/GPU|A|RUNNING_CONFIRMED|6/8|1|
|GESUMMV|PolyBench/GPU|A|RUNNING_CONFIRMED|2/8|3|
|MVT|PolyBench/GPU|A|A|8/8|0|
|SYRK|PolyBench/GPU|RUNNING_CONFIRMED|PENDING|0/8|0|
|dwt2d|Rodinia|A|A|8/8|0|
|gaussian|Rodinia|A|A|8/8|0|
|heartwall|Rodinia|A|A|8/8|0|
|hybridsort|Rodinia|A|PENDING|0/8|1|
|lavamd|Rodinia|PENDING|PENDING|0/8|0|
|lud|Rodinia|A|A|8/8|0|
|myocyte|Rodinia|A|A|7/8|0|
|particlefilter_float|Rodinia|A|A|8/8|0|
|particlefilter_naive|Rodinia|A|A|8/8|0|
|srad_v1|Rodinia|A|RUNNING_CONFIRMED|7/8|3|

## 证据和限制

14/14新增raw自然闭合、strict、归档/native restore及完整stream身份检查通过。271份累计sidecar中148行positive原因与aggregate闭合、123行未打印原因；缺失字段从不填0。新增14点的IO链为13 legacy、1 shared-JSON额外链，通过原冻结只读审计器052dc251...；其既有CPU/actual资格未无故重跑。没有重扫历史72或旧257 raw，也没有重新全面审计旧189配对。

拒绝计数是尝试数，非唯一miss、请求数或应用停顿cycles；最后打印MRQ不是全应用加权L2→DRAM往返时延。非P0 CH缺失、未完成人口与原scan工程负例都保留。源/输入身份与v0.23论文母稿不变。未注册或重建补充V2计划；它不在本报告scope/GM中，未来native route稳定性由Main另行决定。

锚：`/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1/agents/E/results_increment_v2/20261027T185040Z/report.json` SHA `d79c0cda94f48b2c65858e746975eb7a8b3b40f692f8301c80d9127dfad5f13c`；旧配对证据`/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1/agents/E/results_increment_v2/20261027T185040Z/ANALYSIS.json` SHA `3da859050c218c0344d4c342f7c03f59dc2a1f1168d30103de2d314c78ffdb83`。当前run：`/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1/agents/E/results_increment_v3/20261027T205453Z`。

`SCIENTIFIC_INCREMENT.json.gz`含新增14点的cohort/UUID/RESULT路径SHA、2条新配对的binding/optionsSHA及counter、完整35覆盖、当前所有suite分布、22格依赖和旧189配对锚；`NEW_RAW_REASONS.json.gz`仅新增14 raw提取。CAPTURE与manifest记录解析器source SHA。D report工具commit fce10d92eb09bc8f562b84a5a84b202bbf1ea385、raw reason发布927c8bd；Core9eedb3131937748f0492fa83aad37d3691118d70、Framework02775fd795cde5aae1480d81cee6eb481d0a08f4，DRAM850。

本轮0模型、0重试、0生产/科学台账修改。
