# DTC L2 科学增量 V2（只读）

快照：2026-10-28 **02:50:41 CST**，固定对照2026-10-27 22:59:15的198 accepted锚。现在257 accepted＝251本轮＋6合法P0 references；新增59点，仅打开这59份新增accepted raw，旧198份raw未重扫。当前原始状态另有33 confirmed RUN、59 PENDING、1 spent未有标准终态。scan/M16的真实typed工程终态证书独立保留，不改原始状态或补cycles。

35程序：CH-P0 accepted30、DH-P0 accepted25，21程序DH-P0及八变体完整。189条严格DH/P0配对，较锚点新增或新可配对46条；严格input/binding/Core/FW/binary/完整population与所有非目标配置检查零错误。没有任何变体达到35条完整配对，不能从部分输入结果正式选择配置或启动新科学方向。CH非P0仍无accepted，189条relative DTC improvement均为None。

## 新增正负结果

加速比为DH-P0 cycles/DH-variant cycles。下列均保留同一冻结输入，不按结果增删workload。

|程序|配置|P0 cycles|变体cycles|DH自身加速|DRAM读变化|L2拒绝尝试变化|
|---|---|---:|---:|---:|---:|---:|
|ATAX|E768|31,880,220|30,987,395|1.028813|-4.847%|-5.757%|
|ATAX|M8|31,880,220|31,438,336|1.014056|-1.727%|+1.079%|
|ATAX|M16|31,880,220|32,527,908|0.980088|+2.130%|+0.693%|
|ATAX|Q128|31,880,220|33,774,401|0.943917|+6.118%|+2.064%|
|BICG|M16|28,685,812|28,338,906|1.012241|-0.575%|-3.624%|
|BICG|Q64|28,685,812|29,825,144|0.961800|+0.490%|+0.380%|
|MVT|M8|34,687,540|34,685,750|1.000052|+0.000%|-0.001%|
|MVT|Q128|34,687,540|35,470,077|0.977938|+2.966%|+10.132%|
|MVT|F128|34,687,540|35,332,620|0.981743|+3.558%|+7.474%|
|histo|F256|5,865,589|5,731,388|1.023415|-0.217%|-53.958%|
|convolutionSeparable|Q128|800,572|789,240|1.014358|-0.004%|-5.099%|
|mri-q|Q128|360,174|359,731|1.001231|+0.000%|-93.650%|

**ATAX**：E768与既有E384完全相同cycles，均1.028813x；M8为1.014056x，但M16反退至0.980088x。Q128退至0.943917x，DRAM读＋6.118%、entry拒绝139,657,561→161,783,927；最后打印MRQ却745→729。更大queue或更小末次MRQ不能单独证明应用更快，未打印MISS_QUEUE_FULL仍记None。

**BICG**：M16为1.012241x、DRAM读−0.575%，好于既有M8的0.967226x，说明merge方向非单调；仍不能据此断言赶上CH。Q64为0.961800x：miss-queue拒绝15,514,452→119,192，但entry拒绝142,533,205→158,482,166，L2接受读＋11.780%，DRAM读＋0.490%。阻塞转移与退化相关，尚未隔离因果。

**MVT**：M8/M16仅1.000052x/1.000039x（约0.005%/0.004%），DRAM读完全相同；不能称实质改善。Q128为0.977938x，DRAM读＋2.966%、entry拒绝＋63.193%；F128为0.981743x，虽然miss-queue拒绝52,360,071→56,276，entry拒绝却升到172,934,579，MRQ最后均值738→1366。

**新受益例**：Parboil histo F256为1.023415x，cycles5,865,589→5,731,388，DRAM读仅−0.217%，总拒绝−53.958%、miss-queue拒绝−78.104%，末次MRQ198→501。convolutionSeparable Q128为1.014358x，miss-queue拒绝−88.394%，entry拒绝1,057→14,785,749；DRAM读几乎不变。它们与并发/调度压力转移一致，但不能分离FR-FCFS窗口与共享credits。既有convolutionSeparable F256的1.422263x没有被本轮重复当新增发现。

**近乎不受益**：MRI-Q Q64/Q128均1.001231x、DRAM读不变，Q128拒绝1,937→123（−93.650%）仍只快约0.123%。dwt2d Q64 cycles完全不变，DRAM百分比缺分母则保留None。拒绝尝试不是唯一miss/请求或停顿cycles，末次MRQ不是全应用加权L2→DRAM往返延迟。

## 可用人口与固定共同人口

左侧每配置各自可用，人口不同不能直接排名；右侧固定同一21程序、八配置及DH-P0完整。两者均非全35最终GM。

|配置|可用n/35|可用GM|正/平/负|共同21 GM|
|---|---:|---:|---|---:|
|E384|24/35|1.000865|3/15/6|0.999874|
|E768|23/35|1.001121|3/15/5|0.999874|
|F128|23/35|1.009696|5/14/4|1.011497|
|F256|24/35|1.015101|5/14/5|1.016754|
|M16|24/35|1.001380|5/16/3|1.001956|
|M8|24/35|1.000709|5/15/4|1.001734|
|Q128|23/35|0.996101|4/13/6|0.999307|
|Q64|24/35|0.997210|4/14/6|0.999316|

共同21中的F256/F128 GM分别1.016754/1.011497；当前只是观察趋势。缺失输入、长任务和回退都保留，不能将剩余14个程序假定为1或排除。

各suite可用人口统计如下，单元格为**GM（n/固定suite规模；正/平/负）**，详情与各suite同一共同子集的统计都在SUPPLEMENT.json。

|配置|CUDA Samples /9|Parboil /7|PolyBench/GPU /9|Rodinia /10|
|---|---|---|---|---|
|E384|1.000366 (7/9; 1/4/2)|0.999769 (5/7; 0/4/1)|1.003874 (5/9; 2/0/3)|1.000000 (7/10; 0/7/0)|
|E768|1.000366 (7/9; 1/4/2)|0.999769 (5/7; 0/4/1)|1.006106 (4/9; 2/0/2)|1.000000 (7/10; 0/7/0)|
|F128|1.027656 (7/9; 2/4/1)|1.002804 (5/7; 2/3/0)|1.004251 (4/9; 1/0/3)|1.000000 (7/10; 0/7/0)|
|F256|1.038808 (7/9; 1/4/2)|1.004818 (5/7; 2/3/0)|1.013928 (5/9; 2/0/3)|1.000000 (7/10; 0/7/0)|
|M16|1.000000 (7/9; 0/7/0)|0.999763 (5/7; 1/2/2)|1.006881 (5/9; 4/0/1)|1.000000 (7/10; 0/7/0)|
|M8|1.000000 (7/9; 0/7/0)|0.999668 (5/7; 1/2/2)|1.004586 (5/9; 4/0/1)|0.999400 (7/10; 0/6/1)|
|Q128|1.000758 (7/9; 1/4/2)|1.000450 (5/7; 2/3/0)|0.980705 (5/9; 1/0/4)|1.000000 (6/10; 0/6/0)|
|Q64|1.000945 (7/9; 2/4/1)|0.999776 (5/7; 1/3/1)|0.985595 (5/9; 1/0/4)|1.000000 (7/10; 0/7/0)|

PolyBench/GPU可用Q64/Q128 GM为0.985595/0.980705，其回退不能被CUDA/Parboil的收益遮掉。Rodinia已配对多数完全平，但仍缺大型/慢输入，不能把当前Rodinia人口推广为全suite结论。

## P0覆盖依赖

有13个已accepted DH非P0格因缺DH-P0暂不能配对：GEMM5、srad_v1 4、scalarProd3、3MM1。优先P0只依据覆盖依赖，不依据加速比。

|程序|缺失P0（原始快照状态）|已accepted DH变体|暂阻配对|
|---|---|---:|---:|
|scalarProd|DH:PENDING|3|3|
|scan|CH:RUNNING_CONFIRMED, DH:RUNNING_CONFIRMED|0|0|
|sgemm|DH:PENDING|0|0|
|3MM|DH:PENDING|1|1|
|GEMM|DH:PENDING|5|5|
|GESUMMV|CH:RUNNING_CONFIRMED, DH:RUNNING_CONFIRMED|0|0|
|SYRK|CH:RUNNING_CONFIRMED, DH:PENDING|0|0|
|hybridsort|CH:RUNNING_CONFIRMED, DH:PENDING|0|0|
|lavamd|CH:PENDING, DH:PENDING|0|0|
|srad_v1|DH:RUNNING_CONFIRMED|4|4|

scalarProd DH-P0当时未启；已accepted E384/F128/F256，分别自然wall 26.30/23.40/19.68分钟，E768/M8未accepted。GEMM DH-P0未启，已有五个变体自然wall约104–119分钟；3MM DH-P0未启，F256自然wall5.826小时；srad_v1 DH-P0已运行。wall用于既有任务资源排程参考，不能替代cycles，也不保证P0耗时。全部cohort/UUID/DONE SHA见BASELINE_DEPENDENCIES.json。

## 全35覆盖

A为accepted，其余保留原始状态；DH变体分母固定8。scan/M16另有已验真实工程负例sidecar，不冒充accepted或标准DONE/EXIT。

|程序|suite|CH-P0|DH-P0|DH变体A/8|新增A|缺失DH变体|
|---|---|---|---|---:|---:|---|
|BlackScholes|CUDA Samples|A|A|8/8|0|—|
|convolutionSeparable|CUDA Samples|A|A|8/8|4|—|
|fastWalshTransform|CUDA Samples|A|A|8/8|1|—|
|histogram|CUDA Samples|A|A|8/8|0|—|
|mergeSort|CUDA Samples|A|A|8/8|2|—|
|scalarProd|CUDA Samples|A|PENDING|3/8|2|E768, M8, M16, Q64, Q128|
|scan|CUDA Samples|RUNNING_CONFIRMED|RUNNING_CONFIRMED|0/8|0|E384, E768, M8, M16, Q64, Q128, F128, F256|
|transpose|CUDA Samples|A|A|8/8|0|—|
|vectorAdd|CUDA Samples|A|A|8/8|0|—|
|bfs|Parboil|A|A|8/8|1|—|
|cutcp|Parboil|A|A|0/8|1|E384, E768, M8, M16, Q64, Q128, F128, F256|
|histo|Parboil|A|A|8/8|5|—|
|mri-q|Parboil|A|A|8/8|3|—|
|sad|Parboil|A|A|8/8|0|—|
|sgemm|Parboil|A|PENDING|0/8|0|E384, E768, M8, M16, Q64, Q128, F128, F256|
|stencil|Parboil|A|A|8/8|2|—|
|2DCONV|PolyBench/GPU|A|A|8/8|0|—|
|3DCONV|PolyBench/GPU|A|A|8/8|0|—|
|3MM|PolyBench/GPU|A|PENDING|1/8|2|E384, E768, M8, M16, Q64, Q128, F128|
|ATAX|PolyBench/GPU|A|A|7/8|5|F128|
|BICG|PolyBench/GPU|A|A|7/8|4|E768|
|GEMM|PolyBench/GPU|A|PENDING|5/8|4|Q64, Q128, F256|
|GESUMMV|PolyBench/GPU|RUNNING_CONFIRMED|RUNNING_CONFIRMED|0/8|0|E384, E768, M8, M16, Q64, Q128, F128, F256|
|MVT|PolyBench/GPU|A|A|8/8|6|—|
|SYRK|PolyBench/GPU|RUNNING_CONFIRMED|PENDING|0/8|0|E384, E768, M8, M16, Q64, Q128, F128, F256|
|dwt2d|Rodinia|A|A|8/8|1|—|
|gaussian|Rodinia|A|A|8/8|0|—|
|heartwall|Rodinia|A|A|8/8|0|—|
|hybridsort|Rodinia|RUNNING_CONFIRMED|PENDING|0/8|0|E384, E768, M8, M16, Q64, Q128, F128, F256|
|lavamd|Rodinia|PENDING|PENDING|0/8|0|E384, E768, M8, M16, Q64, Q128, F128, F256|
|lud|Rodinia|A|A|8/8|0|—|
|myocyte|Rodinia|A|A|7/8|9|Q128|
|particlefilter_float|Rodinia|A|A|8/8|1|—|
|particlefilter_naive|Rodinia|A|A|8/8|1|—|
|srad_v1|Rodinia|A|RUNNING_CONFIRMED|4/8|5|M8, Q64, Q128, F256|

## 可复核证据与边界

257/257 accepted raw身份和完整stream统计覆盖均匹配；135行positive原因与总拒绝闭合，122行未打印原因保持None。新增59行中IO链57 legacy、2个额外IO binding均只读核验通过；实际IO canary与三种错误链回放共4项PASS。没有调用会创建sidecar的terminal()。

Core `9eedb3131937748f0492fa83aad37d3691118d70`；Framework `02775fd795cde5aae1480d81cee6eb481d0a08f4`；binary `02a289360b42a573832698c978f21ad2125182a453067a35be60410f1eb8888d`。全部严格配对保持DRAM850、同design、完整输入绑定与非目标选项。

当前run：`/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1/agents/E/results_increment_v2/20261027T185040Z`。`ANALYSIS.json`/`STRUCTURED_PAIRS.json`逐pair含输入digest、P0/variant cohort、UUID、RESULT路径/SHA、bindingSHA、非目标选项SHA、完整population及raw原因证据；`NEW_RAW_REASONS.json`只含新增59 raw；`CAPTURE.json`记录锚/解析器SHA；`SUPPLEMENT.json`记录完整suite分布和共同人口。

冻结锚：`/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1/agents/E/results_increment_v1/20261027T145915Z/report.json` SHA `9d354efbde4f592ed278edb959e374b86a2001943092fd9996cf418e0922a117`。D report生成器commit `fce10d92eb09bc8f562b84a5a84b202bbf1ea385`，raw reason工具发布commit `927c8bd`；实际source SHA全部在CAPTURE/manifest，优先按SHA复核。

scan工程负例：`/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1/engineering_negative_evidence_v1/E2-DTCL2MLP-6df3a84b612086e8-DH-M16-V1/1e968456ccefd837eacee605d7ffacc712860114e8a7fea17b4633b25cecbf5f/ENGINEERING_TERMINAL_NEGATIVE.json` SHA `37842f4191c6a0f293a01d22834c28794c3e23a477b1d657976d01bdb055c9e7`；独立typed-gate ACK `/root/data/dtc_l2_mlp_exploration_20261027_v1/control/operational_amendments/typed_negative_full35_v2/ACK.json`。不从这份负例产生cycles。

本轮只读，没有新模型、重试、科学台账或调度规则修改；没有触碰历史72输入，7个UNRESOLVED仍排除，未改英文v0.23母稿。
