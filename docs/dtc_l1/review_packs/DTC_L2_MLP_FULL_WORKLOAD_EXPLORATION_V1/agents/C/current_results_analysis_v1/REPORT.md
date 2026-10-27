# 当前结果的覆盖率、完成偏置与旧不完整输入

统一完成状态快照：**2026-10-27 19:32:14 CST**。117 accepted = 111 本轮新 strict + 6 exact-P0 reuse；350格、35个冻结普通输入，7未决保持。只读分析，零模型启动、零注册修改、零trace body读取。

DH自身可比配对 **73/280**；DH variant已接收 84/280。全8配齐 **5/35**；全10格齐 5/35。所有35个输入均保留，不按性能结果筛选。

## 各suite覆盖

|Suite|输入|accepted/格|P0 CH/DH/双齐|DH变体accepted/可配对|全8齐|
|---|---:|---:|---:|---:|---:|
|CUDA Samples|9|39/90|7/3/3|29/22|2|
|Parboil|7|15/70|4/1/1|10/6|0|
|PolyBench/GPU|9|6/90|3/3/3|0/0|0|
|Rodinia|10|57/100|6/6/6|45/45|3|

## 短输入优先完成偏置

规模来自350份canonical specs与35份冻结input-binding小metadata的expected active instructions/kernel/CTA交叉核对；未扫描trace body。Instructions用于规模与覆盖描述，不等于模拟运行时间预测。

|组别|输入数|instruction中位数|instruction总和|占35总instruction|
|---|---:|---:|---:|---:|
|all35|35|190,918,656|57,452,131,896|100.000%|
|all8_paired|5|13,830,125|65,296,353|0.114%|
|not_all8_paired|30|667,447,346.0|57,386,835,543|99.886%|
|all10_accepted|5|13,830,125|65,296,353|0.114%|
|not_all10_accepted|30|667,447,346.0|57,386,835,543|99.886%|
|has_any_new_strict|17|71,467,509|4,742,954,400|8.255%|
|no_new_strict|18|1,318,375,796.0|52,709,177,496|91.745%|

按instruction规模从小到大分组：

|规模组|输入|accepted/格|DH配对/目标|全8齐|
|---|---:|---:|---:|---:|
|shortest9|9|76/90|60/72|5|
|ranks10to18|9|33/90|13/72|0|
|ranks19to27|9|8/90|0/72|0|
|longest8|8|0/80|0/64|0|

当前完成输入显著偏短；例如myocyte虽仅42.92M instructions，却有5,993 kernels，仍无accepted，说明instruction规模不能单独预测完成时间。全8共同集仅可代表该明确子集，不能外推为全35最终GM；不同profile完成集合也不能直接排序。长输入与历史困难输入继续保留。

## 12个旧quad不完整输入：新performance与历史correctness分开

A=本轮新strict accepted；R=exact-P0 reuse；L=快照running；W=未接收且固定快照无活动条目（通常待调度，不能据此断言从未启动）。旧repair correctness记录一律不进入本表性能数值。

|Program|expected instructions / kernels / CTA|CH-P0|DH-P0|DH已接收/可配对|已接收DH变体|运行中|缺失格|
|---|---:|---|---|---:|---|---|---|
|bfs|121,542,388 / 11 / 76|A|W|3/0|E384,F128,F256|DH-E768|DH-P0,DH-E768,DH-M8,DH-M16,DH-Q64,DH-Q128|
|cutcp|8,538,061,976 / 11 / 1,331|W|L|0/0|—|DH-P0|CH-P0,DH-P0,DH-E384,DH-E768,DH-M8,DH-M16,DH-Q64,DH-Q128,DH-F128,DH-F256|
|GESUMMV|190,918,656 / 1 / 16|L|W|0/0|—|CH-P0,DH-F128|CH-P0,DH-P0,DH-E384,DH-E768,DH-M8,DH-M16,DH-Q64,DH-Q128,DH-F128,DH-F256|
|histo|2,196,264,084 / 80 / 4,260|L|W|0/0|—|CH-P0,DH-E384,DH-E768|CH-P0,DH-P0,DH-E384,DH-E768,DH-M8,DH-M16,DH-Q64,DH-Q128,DH-F128,DH-F256|
|hybridsort|6,276,086,260 / 68 / 115,324|L|W|0/0|—|CH-P0|CH-P0,DH-P0,DH-E384,DH-E768,DH-M8,DH-M16,DH-Q64,DH-Q128,DH-F128,DH-F256|
|lavamd|10,396,775,488 / 1 / 1,000|W|W|0/0|—|—|CH-P0,DH-P0,DH-E384,DH-E768,DH-M8,DH-M16,DH-Q64,DH-Q128,DH-F128,DH-F256|
|myocyte|42,921,588 / 5993 / 11,986|L|L|0/0|—|CH-P0,DH-P0,DH-E384,DH-E768,DH-M8,DH-M16,DH-F128,DH-F256|CH-P0,DH-P0,DH-E384,DH-E768,DH-M8,DH-M16,DH-Q64,DH-Q128,DH-F128,DH-F256|
|scalarProd|730,610,912 / 1 / 128|A|W|0/0|—|DH-F128|DH-P0,DH-E384,DH-E768,DH-M8,DH-M16,DH-Q64,DH-Q128,DH-F128,DH-F256|
|scan|1,963,460,720 / 33 / 166,608|L|W|0/0|—|CH-P0,DH-E384,DH-F256|CH-P0,DH-P0,DH-E384,DH-E768,DH-M8,DH-M16,DH-Q64,DH-Q128,DH-F128,DH-F256|
|stencil|2,193,446,000 / 100 / 6,400|L|W|0/0|—|CH-P0,DH-E768,DH-F128|CH-P0,DH-P0,DH-E384,DH-E768,DH-M8,DH-M16,DH-Q64,DH-Q128,DH-F128,DH-F256|
|SYRK|5,626,658,816 / 1 / 4,096|L|W|0/0|—|CH-P0,DH-M16|CH-P0,DH-P0,DH-E384,DH-E768,DH-M8,DH-M16,DH-Q64,DH-Q128,DH-F128,DH-F256|
|vectorAdd|84,000,768 / 1 / 23,438|A|W|1/0|E384|DH-E768,DH-F128,DH-F256|DH-P0,DH-E768,DH-M8,DH-M16,DH-Q64,DH-Q128,DH-F128,DH-F256|

## 全35输入覆盖表

完整digest、逐格spec/result路径与bytes/SHA、cycles、绑定证据及所有缺项见ANALYSIS.json。下表digest短写仅用于阅读。

|Program / Suite|input digest前16|instructions / kernels / CTA|P0 CH/DH|DH配对/8|全8齐|缺少的可比profile|
|---|---|---:|---|---:|---|---|
|2DCONV / PolyBench/GPU|`d984ea5475a581ad`|620,347,492 / 1 / 65,536|L/W|0/8|否|E384,E768,M8,M16,Q64,Q128,F128,F256|
|3DCONV / PolyBench/GPU|`79f8ab6241faeed6`|823,239,400 / 254 / 65,024|L/W|0/8|否|E384,E768,M8,M16,Q64,Q128,F128,F256|
|3MM / PolyBench/GPU|`977a2f7007cb1f96`|1,813,512,192 / 3 / 3,072|L/W|0/8|否|E384,E768,M8,M16,Q64,Q128,F128,F256|
|ATAX / PolyBench/GPU|`eededb785179fc04`|145,666,048 / 2 / 32|R/R|0/8|否|E384,E768,M8,M16,Q64,Q128,F128,F256|
|bfs / Parboil|`1df9d5479504d9c7`|121,542,388 / 11 / 76|A/W|0/8|否|E384,E768,M8,M16,Q64,Q128,F128,F256|
|BICG / PolyBench/GPU|`ae34174fbbdf83b2`|145,666,048 / 2 / 32|R/R|0/8|否|E384,E768,M8,M16,Q64,Q128,F128,F256|
|BlackScholes / CUDA Samples|`b31a85e4eb8d32ef`|13,830,125 / 1 / 480|A/A|8/8|是|—|
|convolutionSeparable / CUDA Samples|`4114a3dc0d06b55b`|714,547,200 / 2 / 27,648|L/W|0/8|否|E384,E768,M8,M16,Q64,Q128,F128,F256|
|cutcp / Parboil|`af7320f9d9dc6629`|8,538,061,976 / 11 / 1,331|W/L|0/8|否|E384,E768,M8,M16,Q64,Q128,F128,F256|
|dwt2d / Rodinia|`e5638b94095098ac`|6,312,741 / 10 / 342|A/A|7/8|否|Q64|
|fastWalshTransform / CUDA Samples|`f7f22a2ccc836a8a`|180,944,896 / 16 / 7,040|A/L|0/8|否|E384,E768,M8,M16,Q64,Q128,F128,F256|
|gaussian / Rodinia|`16f4c42373e4961e`|4,526,592 / 126 / 1,071|A/A|8/8|是|—|
|GEMM / PolyBench/GPU|`fc0705ae3721e999`|739,246,080 / 1 / 1,024|L/W|0/8|否|E384,E768,M8,M16,Q64,Q128,F128,F256|
|GESUMMV / PolyBench/GPU|`769e6d9fd5f9cd53`|190,918,656 / 1 / 16|L/W|0/8|否|E384,E768,M8,M16,Q64,Q128,F128,F256|
|heartwall / Rodinia|`731af5428c4b8155`|6,900,708 / 1 / 51|A/A|8/8|是|—|
|histo / Parboil|`2c506bf13c81ff5d`|2,196,264,084 / 80 / 4,260|L/W|0/8|否|E384,E768,M8,M16,Q64,Q128,F128,F256|
|histogram / CUDA Samples|`3722a5c85d91a948`|17,088,656 / 8 / 1,130|A/A|8/8|是|—|
|hybridsort / Rodinia|`09f94fcc7494a03b`|6,276,086,260 / 68 / 115,324|L/W|0/8|否|E384,E768,M8,M16,Q64,Q128,F128,F256|
|lavamd / Rodinia|`ddb6806316876a85`|10,396,775,488 / 1 / 1,000|W/W|0/8|否|E384,E768,M8,M16,Q64,Q128,F128,F256|
|lud / Rodinia|`b33381cf25d44359`|22,950,272 / 46 / 1,376|A/A|8/8|是|—|
|mergeSort / CUDA Samples|`dd9f695c4f53b083`|10,111,750 / 13 / 209|A/A|6/8|否|M8,F256|
|mri-q / Parboil|`dc7a91531846c113`|1,411,757,056 / 4 / 390|A/W|0/8|否|E384,E768,M8,M16,Q64,Q128,F128,F256|
|MVT / PolyBench/GPU|`f437190767aaed49`|145,666,048 / 2 / 32|R/R|0/8|否|E384,E768,M8,M16,Q64,Q128,F128,F256|
|myocyte / Rodinia|`977e34578994c3d2`|42,921,588 / 5993 / 11,986|L/L|0/8|否|E384,E768,M8,M16,Q64,Q128,F128,F256|
|particlefilter_float / Rodinia|`b41cc74c66ca6ed4`|71,467,509 / 36 / 72|A/A|7/8|否|F128|
|particlefilter_naive / Rodinia|`3f85d1878aba9f04`|35,981,229 / 9 / 72|A/A|7/8|否|F128|
|sad / Parboil|`db89be14146b9163`|157,583,646 / 3 / 1,782|A/A|6/8|否|M16,F256|
|scalarProd / CUDA Samples|`2b93f70cd0666c51`|730,610,912 / 1 / 128|A/W|0/8|否|E384,E768,M8,M16,Q64,Q128,F128,F256|
|scan / CUDA Samples|`6df3a84b612086e8`|1,963,460,720 / 33 / 166,608|L/W|0/8|否|E384,E768,M8,M16,Q64,Q128,F128,F256|
|sgemm / Parboil|`ffc8a89493c8a211`|1,658,916,864 / 1 / 528|A/W|0/8|否|E384,E768,M8,M16,Q64,Q128,F128,F256|
|srad_v1 / Rodinia|`0e62c67daa020853`|10,136,693,400 / 502 / 181,000|L/W|0/8|否|E384,E768,M8,M16,Q64,Q128,F128,F256|
|stencil / Parboil|`c885293ad99e21ee`|2,193,446,000 / 100 / 6,400|L/W|0/8|否|E384,E768,M8,M16,Q64,Q128,F128,F256|
|SYRK / PolyBench/GPU|`b51811aca9dc70cf`|5,626,658,816 / 1 / 4,096|L/W|0/8|否|E384,E768,M8,M16,Q64,Q128,F128,F256|
|transpose / CUDA Samples|`65151d2c661f88f3`|208,428,288 / 24 / 24,576|A/L|0/8|否|E384,E768,M8,M16,Q64,Q128,F128,F256|
|vectorAdd / CUDA Samples|`e7bb67e63e3c3847`|84,000,768 / 1 / 23,438|A/W|0/8|否|E384,E768,M8,M16,Q64,Q128,F128,F256|

## 缺失重点与边界

优先审视以下两类缺口，不改变现有调度或挑选输入：

- DH-P0缺失但已有DH variant accepted：bfs（3个variant，P0=NO_ACCEPTANCE_OR_ACTIVE_ENTRY_IN_FIXED_SNAPSHOT）; fastWalshTransform（3个variant，P0=RUNNING_SNAPSHOT）; mri-q（1个variant，P0=NO_ACCEPTANCE_OR_ACTIVE_ENTRY_IN_FIXED_SNAPSHOT）; transpose（3个variant，P0=RUNNING_SNAPSHOT）; vectorAdd（1个variant，P0=NO_ACCEPTANCE_OR_ACTIVE_ENTRY_IN_FIXED_SNAPSHOT）。补齐基线后才能转为合法自身比较。
- instruction最大且全8未齐的10个：lavamd (10,396,775,488, 0/8), srad_v1 (10,136,693,400, 0/8), cutcp (8,538,061,976, 0/8), hybridsort (6,276,086,260, 0/8), SYRK (5,626,658,816, 0/8), histo (2,196,264,084, 0/8), stencil (2,193,446,000, 0/8), scan (1,963,460,720, 0/8), 3MM (1,813,512,192, 0/8), sgemm (1,658,916,864, 0/8)。这反映尚未覆盖的工作量，不代表敏感性判断。
- 非P0 CH点不在当前350格内；CH/DH非P0四角比较需后续独立标识的扩展矩阵，不能由DH自身变化替代。

快照BATCH running有58条；postprocess的1条中1条已经accepted。spent=167、remaining=177与逐文件读到的running/results非全局原子事务，不将其混加为精确启动计数。175个格在固定快照中既无accepted也无活动条目；保留为待调度/未观测，不擅称never-started。

7个未决：backprop, cfd, kmeans, nn, nw, pathfinder, streamcluster；不晋级、不替换。所有冻结资产标签仍为NO_FRACTION_LABEL_NOT_FULL_CAPTURE_CERTIFIED，结论只针对精确冻结trace input，不能延伸为完整原始benchmark capture证明。

证据：Agent A固定SOURCE_SNAPSHOT.json SHA256 `1372a18ab807fd93ccfad4b127ebfe7212ec54fa6c0bc0fb1fc337b3114015b6`；本地METADATA_SNAPSHOT.json SHA256 `aff57f08e89a4c5a63516d95d4a94ffe5ab13e00707b030f19fdc3d95860d1b2`。后者读取时间2026-10-27T11:38:10.781021+00:00，只用于身份和规模交叉核对，不引入该时间的新完成结果。
