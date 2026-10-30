# 当前交付与一小时收尾窗口 V4

这是2026-10-30北京时间10:18附近的进度快照；后处理终态以同run回执为准。用户最新要求：主Lane集中审核，仅收尾已启动任务，未启动的不启动，截止北京时间10:52:56。此限制覆盖旧的继续扩展计划。本报告不是整个Goal完成声明。

## 实际交付

共享SM70 NAS输入125；SM89公共目录82份常规、82份裁剪，统一发现164行。另保留RAW7；simpleMultiCopy两份共44 kernel的逐kernel后处理和辅助归档已接受。对象数包含输入与版本，不是独立程序数或专项适配完成数。

冻结153延期精确输入行/115 binary：有效交付现为2项完成、151项未完全闭合。第二项是原LUD -s256 -v：46 kernel /1,014,768条完整F9/GROUP、父绑定裁剪COMMIT、公共目录、统一发现、安装后按需恢复元数据检查均已接受。历史161状态、旧153身份/argv/指纹不改；C8是第一项。

LUD普通入口实际运行新私有V5 frontend faff2126/core83c035ae，完整kernel1/CTA0退休17,604 lane-uops。公共child同一kernel1/CTA0经仅四项header转换，与已运行小样的压缩文件和单kernel索引字节完全相同，Root绑定既有运行证据，无需重跑同字节。其余45 kernel、改变shape的28 kernel、完整child索引及全46 terminal许可不继承。没有完整程序、所有分支或性能资格。

## 仍在执行的仅两项POST

SDK4.2.9新alignedTypes R2与transpose R2完整采集均已结束：24/32 kernel，统计声明60,768,064/39,485,440记录，压缩375,784,880/206,398,364字节。原程序检查和owned进程/cgroup/锁闭合已接受。四处历史母模板描述错误在新来源合同明确更正，原回执未改。

两项全记录F9/GROUP已启动，109 CPU6/7各一项、硬内存各2GiB、CPU各100%；正文、分组和sort scratch全在164，Native仅有界控制。10:17实际两项进入分组，尚无完整终态。必须等全部记录/CRC/SHA和owned释放，不能按文件增长或单kernel成功宣布完成。此窗口不增加GPU、POST批次或模型任务。

## 已执行并审完

- simpleStreams R2：11 kernel、141,557,760记录全量校验；90成员、2,832,028,830字节无损自定义source归档164，有独立receiver wholeSHA。ordinary7转换及模拟器入口未启动，不增公共普通/裁剪计数。
- modern reduction R2：实际5 launch、1538 warp、49,216有效EXIT lane闭合，动态CALL/RET/WARPSYNC均0。旧分析器误将空mask组当作参与者不全；私有最小修正明确NOT_EXERCISED，非空组检查全部保留。不授动态mask支持；全SASS未启动。
- 原2DCONV、SDK4.2.9 asyncAPI：实际Native QA通过且owned闭合。前者只验4094²内部区域；未写边界不合格。后者原全N整数26检查通过，但异步输入生命周期/trace资格未完成，不继承C8同步输入权限。
- kmeans400：实际1,088,000有效TLD返回值已核对。TLD-only CPU组件1400条TLD含40条谓词关闭，因此有效内存指令1360正确；共1408条含8个synthetic EXIT全部保留。实际组件通过，不等于完整CTA或程序模型运行。
- kmeans完整私有producer A3已集成、离线SO编译及现有CPU检查通过。新SO GPU运行0次、未部署，完整动态F9/GROUP/归档/consumer未完成。本窗口只封存候选。
- 方法论、执行检查单和经验已形成，程序特性分析40个profile。第二批65份源码由Root在109重开核SHA；源码到旧ELF的绑定不一概证明。只缩减可剥离benchmark重复，算法迭代、依赖、工作集与拓扑损失逐项说明。

## 未启动项保留缺口

simpleStreams ordinary7投影/consumer；kmeans A3 GPU；modern R2全SASS；2DCONV/async同次输入采集；其他未启动专项或性能实验。保留源码、失败历史和最短后续步骤，不能把未实施包装成不支持或完成。

所有大输出真164，Source KEEP、释放0；Native实际余量至少5GiB。全库Native正文回读继续取消。科学资格、历史和预算未改，外部ChatGPT审稿尚未收到。

## 入口

- [有效153台账](progress4_closeout/data/FROZEN153_EFFECTIVE_STAGE_LEDGER_V4.json)
- [一小时窗口](progress4_closeout/evidence/ROOT_USER_ONE_HOUR_FINALIZATION_WINDOW_20261030_V1.json)
- [V13交接](progress4_closeout/evidence/ROOT_ACTIVE_GOAL_PROGRESS_HANDOFF_V13.json)
- [采集和缩减方法](progress4_closeout/methodology/METHOD_V2.md)
- [执行检查单](progress4_closeout/methodology/EXECUTION_CHECKLIST_V1.json)
- [实际采集经验](progress4_closeout/methodology/PITFALLS_V1.json)
- [前22 profile](progress4_closeout/characteristics/first22/WORKLOAD_CHARACTERISTICS_AND_REDUCTION_REVIEW_V2.md)
- [后18 profile](progress4_closeout/characteristics/next18/UNCOVERED_PROGRAM_CHARACTERISTICS_AND_ACTIONS_V4.md)
