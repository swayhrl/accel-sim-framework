# V9 中型三输入已归档并公共发布

Root验收时间：2026-10-29T04:26:19.059454+08:00。三个中型输入完成全量POST、完整CTA裁剪、常规及裁剪归档和公共发布，严格目录从68/68增至71/71。原33项有限输入现为24对常规裁剪公共资产，加3项用户指定RAW例外交付，共27项完成、6项待办。全库Goal尚未完成。

| 阶段 | 本次实际闭合 |
|---|---|
| 全记录与分组 | b_tree44f4、Sobol445a、streamclusterc71f三个精确输入，112,957,773记录、227组，原POST结果复用 |
| 完整CTA裁剪与package | 2576个CTA、3,327,857条选择记录；普通815成员、959,858,498B，其中SC717成员、732,570,207B |
| COPY与接收 | 6个对象、1063成员、966,755,879B；原source及关闭重开receiver wholeSHA与真实父COMMIT闭合，实际121.30秒 |
| 公共发布 | 71常规、71裁剪；旧68每条字典保留，142项metadata/stat独立核验；新增6对象Main/DTC36次实际命令通过，publisher真wait0、自有15锁释放 |

新增对象仅保留原single-F9数据资格，consumer为UNKNOWN，未执行模型或增加科学资格。COPY耗时属于本次工程记录，不用于科研I/O性能结论。[原始验收与源码索引](EVIDENCE_INDEX_V9.json)保留每个阶段的实际回执、来源字节数和SHA。

## 剩余六项与运行时点

剩余4个fullPOST输入是旧alignedTypes0d19、旧transpose2d933、新alignedTypesf003和convolutionSeparablebac。旧两个大单流仍按用户要求做fullPOST，不能改成RAW例外。另2项是scan83142f69d5dd和simpleStreams9ac3d97c5c60；两项均未计为capture正闭合。精确QID和本版增量见[机器账本增量](CURRENT_DELTA_V9.json)，V8原33账本保留原字节及其历史时点。

Root在2026-10-29T04:24:19.956595+08:00进行的只读观察确认5个Native长scope同PID和start_ticks，109四个POST guard及原capture APP身份相符。作者在2026-10-29T04:26:00.834526+08:00复核4个POST Native与GPU controller仍同身份；middle3旧parent缺席符合其自然成功闭合。以上只是带时点的运行身份观察，不据此宣布POST完成或实时GPU利用率，不干预健康任务。

## 保持的范围与工程边界

已接受的125个SM70精确输入、242历史条目、typed8及153延后原因保持。当前EP29与DTC35共64绑定、36个唯一SM70 bundle仍无已观察的选择器缺口。独立RAW3公共归档维持34,475,098,987B、675成员，POST、group、crop及consumer缺口继续明示。统一66快照保留冻结时点，最新71从实际架构catalog读取；本版不重复刷新发现快照。

本次SC普通对象超出原H的256成员及256MiB通用边界，因此使用只接受六个精确manifest的局部guard，原H和SHA/COPY语义不变。已有ST别名直接复用；64MiB/s每阶段本地工程限速上界是本作业边界，不是global quota。Root签发前先核模板schema与冻结入口一致，运行后不改签定数据。具体限制见[新增工程经验](PROVEN_PITFALLS_V9.json)及[实际运行的四份局部快照](code_v9/SOURCE_MANIFEST.json)。

全部源和旧partial保留，Source KEEP、释放0。未增加采集、模拟或科学预算，外部ChatGPT审稿仍未收到。
