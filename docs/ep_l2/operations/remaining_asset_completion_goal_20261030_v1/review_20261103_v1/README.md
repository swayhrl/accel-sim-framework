# 2026-11-03：现有后台任务完成情况，供 ChatGPT 审阅

本包是**当前状态与既有结果的审阅交接**，覆盖SDK4.2.9新alignedTypes R2、transpose R2两个精确输入。没有启动任何新采集、后处理、模型或恢复任务。它更新了10月30日V4报告中“两项仍在运行”的旧状态；不把整库Goal标为完成。

## 已完成的事实

| 输入 | kernel | 完整记录 | 完成时间（北京时间） |
|---|---:|---:|---|
| alignedTypes R2 | 24 | 60,768,064 | 2026-10-30 10:43:32 |
| transpose R2 | 32 | 39,485,440 | 2026-10-30 10:39:46 |

两个CPU_RESULT均为REPEAT_ONLY_SINGLE_STREAM_F9_RECORDS_AND_GROUPS_CLOSED；两个独立资源回执均为PASS_REPEAT_ONLY_SINGLE_STREAM_F9_GROUP_DATA_NO_MODEL、service returncode0、qualification_error=null、owned/cgroup已闭合、Native资产锁已释放。两项都在用户当时截止10:52:56的一小时窗口内结束。11月3日再次只读核对，原进程身份不存在，原cgroup为空。

本次逐一核对56份GROUP_RECEIPT的原字节SHA与链式引用，均声明GROUPED_ALL_SHARDS_CRC_PASS和closed_reopened_full_xz_crc=true，各项分组记录总和与完整F9/统计记录一致；分组文件当前大小匹配。**本次没有重新读取分组正文计算wholeSHA，也没有重跑CRC。** 因而本包是已有成功回执的核查快照，不替代尚未完成的主Lane独立payload终验。

## 尚未完成，不能混算

- 新两份SDK429版本的裁剪、正式COMMIT归档/公共发布与轻量模拟器入口证据仍未完成。数据已在真164的工作目录，不等于已形成公共资产COMMIT。
- 当前公共SM89仍82常规＋82裁剪，SM70 NAS输入125；冻结153延期精确输入台账仍2项有效交付、151项未完全闭合。两份新版本不能直接扣掉原输入的延期数。
- 新R2的binary/argv/原空间/版本独立；不冒充旧默认长输入，也不与已有CUDA11.8 R2混为同一输入。新来源合同明确列出并更正四项母模板描述错误，原PROCESS_START/EXECUTION未改。
- 当前原程序QA、F9/GROUP、接收回执、公共资产发布、模拟器入口和科研资格是不同阶段。actual_input_capsules=false、consumer_qualification=false、whole_input_functional=false等字段保留。
- simpleStreams普通格式投影、kmeans A3 GPU、modern R2完整SASS、2DCONV/async同次输入采集等未启动项继续封存；不启动以“补证”为名的新实验。
- 主Lane的最后交接和汇总停在10月30日V14的运行中快照，没有及时反映上述自然完成。本次明确揭示该滞后，不覆盖旧报告或伪造当时已验收。

## 请 ChatGPT 重点审查

1. 两项精确binary/argv/profile、原QA与source/mapper/producer身份是否闭合；四项母模板描述纠正是否仍有遗漏？
2. FULL_RECORD_VALIDATION、CPU_RECEIVER、56份GROUP_RECEIPT及CPU_RESULT/独立owned回执的引用SHA、kernel/record/stream计数是否相互一致？哪些仅是协议自证，还缺独立终验？
3. 报告是否把“统计声明、全记录验证、CRC、wholeSHA、程序QA、模拟器入口、科研资格”混淆，或把两个新版本冒充旧输入交付？
4. 在不重采、不完整重放、不验证所有配置、不默认保留全部host数组的前提下，最少还需哪些收尾才能安全作为公共常规/裁剪资产？哪些证据可复用？
5. 后续裁剪/公共COMMIT/consumer应继续哪些精确门，哪些属于可省的重复工作？请指出阻断问题和非阻断文档问题，并引用本包路径/字段；不能访问NAS的内容请标未核，不凭路径存在推断通过。

## 审阅导航

- [当前机器可读状态](CURRENT_STATUS.json)
- [来源与SHA清单](SOURCE_SNAPSHOT_MANIFEST.json)
- alignedTypes：[全记录验证](ALIGNED/FULL_RECORD_VALIDATION.json)、[接收回执](ALIGNED/CPU_RECEIVER.json)、[24份分组原始回执](ALIGNED/GROUP_RECEIPTS_SNAPSHOT.json)、[最终结果](ALIGNED/CPU_RESULT.json)、[独立闭合](ALIGNED/INDEPENDENT109_CLOSURE.json)
- transpose：[全记录验证](TRANSPOSE/FULL_RECORD_VALIDATION.json)、[接收回执](TRANSPOSE/CPU_RECEIVER.json)、[32份分组原始回执](TRANSPOSE/GROUP_RECEIPTS_SNAPSHOT.json)、[最终结果](TRANSPOSE/CPU_RESULT.json)、[独立闭合](TRANSPOSE/INDEPENDENT109_CLOSURE.json)
- [真实来源与历史描述纠正：alignedTypes](ALIGNED/FROZEN_SOURCE_INPUT_CONTRACT_V1.json)、[transpose](TRANSPOSE/FROZEN_SOURCE_INPUT_CONTRACT_V1.json)
- [原验证算法及两项执行包装源码](sources/)
- [此前完整进度V4](../CURRENT_PROGRESS_V4.md)、[有效153台账](../progress4_closeout/data/FROZEN153_EFFECTIVE_STAGE_LEDGER_V4.json)
- [采集/缩减方法论](../progress4_closeout/methodology/METHOD_V2.md)、[经验清单](../progress4_closeout/methodology/PITFALLS_V1.json)、[前22个profile](../progress4_closeout/characteristics/first22/WORKLOAD_CHARACTERISTICS_AND_REDUCTION_REVIEW_V2.md)、[后18个profile](../progress4_closeout/characteristics/next18/UNCOVERED_PROGRAM_CHARACTERISTICS_AND_ACTIONS_V4.md)

所有旧源与失败KEEP，释放0。未改变科学资格、历史或预算。**ChatGPT外审尚未收到**；本包仅准备供审。
