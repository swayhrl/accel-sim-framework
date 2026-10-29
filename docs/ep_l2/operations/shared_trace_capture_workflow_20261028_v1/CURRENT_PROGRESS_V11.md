# V11 当前采集与共享归档状态

状态时点：2026-10-29T08:56:32.239750+08:00。统一发现入口已更新到71份常规、71份裁剪对象和3份独立RAW归档，EP-MAIN与DTC两项目的14次实际查询均通过。SM70的125个精确输入、242条历史队列和typed8／153延期视图保持原值。[统一目录验收](evidence_v11/E107_ROOT_PUBLIC_UNIFIED71_RAW3_MAIN_DTC14.json)绑定新的不可变快照与公共指针；这次刷新只读取目录元数据。

## 采集与交付分别计数

| 范围 | 当前数量 | 含义 |
|---|---:|---|
| 原33项精确采集输入 | 31完成、1不完整保留、1运行 | 完成采集不等于完成后处理或模拟器资格 |
| 原33项资产交付 | 27完成、6待办 | 24对常规裁剪公共资产加3项RAW例外；待办为四份大资产、scan及SDK42 simpleStreams |
| 严格SM89公共对象 | 71常规、71裁剪 | 包含历史及其他已完成资产，不是71个独立程序 |
| 独立RAW归档 | 3 | 后处理、裁剪及consumer缺口仍明确保留 |

## scan 原窗口结束与新交付范围

ORD_EXT_scan_83142f69d5dd_A001触及原21600秒采集上限，实际经过约22025.76秒后以-15退出。原controller、leaf及GPU应用均已退出，远端cgroup为空；proposal、ACK、Native四锁释放链和实际锁检查已闭合。[原始Root验收](evidence_v11/E108_ROOT_SCAN_WALLBOUND_OWNED_CLOSED.json)将其保留为CAPTURE_INCOMPLETE_RETAINED。约37.56GB压缩文件属于不完整现场，不能作为完整RAW资产发布。

用户已选择：该精确scan输入完成采集后，做完整SHA归档和轻量检查，全量后处理与裁剪留明确缺口。[范围修订](evidence_v11/E109_ROOT_USER_SCAN_RAW_AFTER_COMPLETE_SCOPE.json)不把此例外扩展到同名程序或其他输入。旧alignedTypes及transpose继续完成全量后处理。

scan恢复目前是单独有限窗口的源码准备，尚未签署执行授权或启动新采集；旧scope及其截止时间不变。新恢复须等当前SDK任务实际退出并完成租约、资源检查后再准入。

## 最后一项SDK42采集正在运行

ORD_EXT_simpleStreams_9ac3d97c5c60_A001已通过V24精确末项入口启动。它与已归档的CUDA版本simpleStreams cd83980a2646是不同精确输入。Root核对了Native、远端controller、leaf和GPU应用的PID与start_ticks，并验证应用继承的Comfy共享锁、LOCAL_IO和GPU三份OFD。[启动实证](evidence_v11/E110_ROOT_LAST_SDK42_CAPTURE_START_AND3OFD.json)保留原始身份与字节绑定。

本项继续遵守原绝对截止1793241315.9269235，即北京时间2026年10月29日10:35:15；20GiB内存、80GiB输出及原采集profile保持。[本次只读状态](evidence_v11/E111_READONLY_ASOF_POST_AND_CAPTURE_METADATA.json)记录稿件时点的真实进程，尚不能据此称采集完成。

## 四份大资产继续分组

两份alignedTypes、transpose 2d93339b77a8及convolutionSeparable bac9679c8c68均已通过原F9完整记录校验，当前继续处理分组。分组回执的存在数量与时点见E111；它不代表所有分组、receiver、资源和进程闭合已通过，也不作为整体完成比例或结束时间。

本地临时work方案和增量续跑仍是私有源码候选，未切换四个健康任务。候选只拟将分区、frame和排序等临时文件放到109本地盘，权威来源、最终grouped正文及持久证据仍保存在164；真正部署须先独立审查并取得精确准入。

## 较大资产的体积

以下是原始压缩trace，采用十进制GB；完整归档包还可能包括grouped文件、程序和元数据。[机器表](RAW_TRACE_SIZE_TABLE_V11.json)保存精确字节数和原始manifest或冻结header统计引用。

| 精确资产 | 原始压缩trace | 状态 |
|---|---:|---|
| scan 8314 | 约37.56GB，仅不完整现场 | 等待单独恢复采集，完整后按新RAW范围归档 |
| streamcluster 1be5 | 33.50GB | 已归档，完整包约36.44GB |
| simpleStreams cd83 | 32.77GB | RAW归档约32.78GB，501个kernel的统计声明约56.9亿条记录 |
| stencil c3e9 | 14.02GB | 已归档，完整包约14.75GB |
| alignedTypes 0d19／f003 | 各约6.01GB | 各约9.72亿条记录，完整校验通过，分组进行中 |
| transpose 2d93 | 5.86GB | 约10.85亿条记录，完整校验通过，分组进行中 |
| convolutionSeparable bac9 | 2.47GB | 约3.85亿条记录，完整校验通过，分组进行中 |

## 已闭合的研究输入证据继续复用

[V10](CURRENT_PROGRESS_V10.md)的当前EP／DTC64条精确绑定保留64条启动、63条退休证据及61条至少一个精确配置的完整接受。三类科学接受限制仍按V10原时点证据解释；本增量不重新运行模型，也不把新归档或采集状态授予新的consumer、数值或性能资格。

typed8已闭合、153项DEFERRED；161项全部完成与全库SM70正文恢复均已取消为本轮硬门槛。全库Goal仍未完成。源KEEP、释放0，外部ChatGPT审稿仍未收到。
