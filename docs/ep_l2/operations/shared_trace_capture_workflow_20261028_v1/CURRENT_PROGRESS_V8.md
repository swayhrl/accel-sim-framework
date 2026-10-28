# V8 现有资产交付与剩余缺口

更新时间：2026-10-29T03:39:10.146795+08:00。本版以用户确认的资产优先范围收尾：先交付已经采集的精确输入、必要后处理、真164归档和公共读取，并核对当前EP和DTC真正需要的输入。全161完成不再是硬门槛；全库SM70正文恢复至174或174-new已取消。全库Goal仍未完成。

| 范围 | 已验收交付 | 剩余工作 |
|---|---|---|
| SM70及当前研究 | 125精确输入公共访问验收保持。EP29、DTC35共64绑定，36个唯一SM70 bundle，原exact成员及命令选择器无缺口 | 按需读取；不能用同程序名的SM89输入替换已绑定的精确SM70输入 |
| SM89严格公共目录 | 68常规与68裁剪对象；最新小DWT和小SC新增4对象，全部136 metadata及Main/DTC新增24次查询正式接受 | 对未交付输入继续必要流程；对象数不等于程序数或workload数 |
| RAW独立公共目录 | 精确3个超大多流输入，675成员、34,475,098,987B；真实sender与关闭重开receiver全SHA、公共目录及Main/DTC读取已接受 | 全量POST、group、crop和consumer明确为GAP；不进入strict POSTqualified目录 |
| 统一发现 | 实际公开的统一66/66快照，保留125输入、242历史条目、typed8/153和capture31时点；Main/DTC14次读取通过 | live68从架构目录可读，冻结66快照保持其时间点，本版不重复刷新 |
| 原33有限输入 | capture31正闭合、2尚未闭合；按精确binary和argv，21常规裁剪公共pair及3 RAW例外交付，共24项完成 | 9项：中型3待裁剪归档公共、4大输入fullPOST运行、2采集未正闭合 |
| typed精确适配 | 8个精确scope正式闭合；另153项按原缺口延后，历史不改 | 114 ISA、19实际输入、11source/runtime、5mapping、3exact GPU、1variant；有实际需求或以后空闲再按精确范围处理 |

## 正在收尾的输入

原33项的[逐QID表](ORIGINAL33_DELIVERY_TABLE_V8.md)和[原始机器账本](ORIGINAL33_CURRENT_EXACT_STAGE_LEDGER_V8.json)固定其验收时点。两项smallF9已由package推进至公共68，并已从待办转入21公共pair。

此前5个wholePOST CPU任务与scan GPU并行。随后middle3在99.08分钟内自然完成全POST及227组，合计112,957,773记录，已获[Root正式数据验收](evidence_v8/E083_ROOT_MIDDLE3_112957773_RECORDS_227GROUPS_AND_OWNED_ACCEPTANCE.json)；仍待实际裁剪、package、归档和公共pair，不把交付完成数24改成27。middle3已按新有界入口启动CPU2裁剪与打包；已闭合的全量校验和分组继续复用，不重做。剩余4个大输入fullPOST分别为旧aligned0d19、旧transpose2d933以及新alignedf003和convolutionbac，不能凭进程运行或原统计声明称POST通过。scan831在所引用时点GPU100%，仍为OPEN，尚未成为capture成功；最后另一项同样未计成功。最新变动另见[时点增量](CURRENT_DELTA_V8.json)。

旧两个大单流输入由用户明确要求fullPOST，不能套用多流RAW例外。RAW3只覆盖simpleStreams cd839和两项simpleMultiCopy精确QID。已公开RAW对象保持POST_PENDING，不冒充group、裁剪、数值、consumer或科学性能通过。

## 资格与范围

G256是原33之外的精确输入，单列在typed8及公共对象中；它不会增加原33完成数。全部68常规、68裁剪、RAW3与typed8是不同计数，不能相加为workload覆盖。公共文件可发现或可读，也不等于适用于任意模拟器、所有输入、全部潜在分支或科研性能实验。小DWT和小SC只具原single F9数据验收，consumer保持UNKNOWN。

当前EP和DTC的64条研究绑定来自36个唯一SM70 bundle，原成员身份、wholeSHA证据和命令顺序检查已接受；本轮SM89库存缺口不直接构成这些当前SM70输入的缺口。[明确待办](CURRENT_DELIVERY_GAPS_AND_DEFERRED_EXCEPTIONS_V8.json)和[typed8及153延后原因](TYPED8_AND153_EXACT_DEFERRED_REASON_PRESERVATION_V8.json)分别保留，不以HOLD代替完成。

## 复核入口

[证据索引](EVIDENCE_INDEX_V8.json)从E070起保存25份原始小证据，每份含原路径、字节数与SHA。[源码快照](code_v8/SOURCE_MANIFEST.json)仅保存已审且实际运行的局部member guard、COPY和统一发现及wholePOST核心，不构成新安装或运行授权。[工程边界](PROVEN_PITFALLS_V8.json)记录429成员局部准入、实际裁剪比例、同NAS改名、已有ST别名和计数资格边界。

正文、归档和原失败回执继续保留在真164；Source KEEP、释放0。没有扩大科研资格或预算。外部ChatGPT审稿仍未收到。
