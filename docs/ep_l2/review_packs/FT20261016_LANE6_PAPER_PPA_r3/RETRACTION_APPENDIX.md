# r3 科学资格撤回附录（非论文性能结果）

依据 review_r3 a41bfb55934303a4d4a342762f74a16d137d0316 与 Lane-5
b134f76d8f4cd759c0852b68edf922ecbd445ea9，本附录主动撤回 r2 的 §5.1
“已独立合格”应用资格文字、§6 sad 性能/占用/归因结论及 formal_sad/WB_PAIRS
图的当前科学效力：**SUSPENDED / RETRACTED_AS_SCIENTIFIC_RESULT**。
此前 sad 的110593→110573 cycles 是旧模型执行记录；“基本持平”与“无容量收益
证据”均不可当作当前机制的科学定论。它们不进入新正文性能表、主图、图表清单或均值。
原稿、图、日志、CSV、binary、receipt不覆盖，准确旧路径和hash见RETRACTION_INDEX。

执行事实与科学资格分开：旧六次run的COMPLETE_VALID仅说明当时执行与旧合同
终态检查；较新的APPLICATION_ACCEPTANCE已将它们标为SUSPENDED_MEMCPY_PHYSICAL_CLOCK。
已运行sad/vectorAdd_4M/cfd_097k各两次，另外convolution/FWT四条NOT_RUN。
全部十条身份及raw索引保留于撤回索引，没有将旧终态改写。

确认反例：真实production partition在memcpy offset4096时，B16/U_WB16分别
出现124/15次同bank同物理cycle多grant，最大2次；offset0未观察到该违规。
Host预热线立即读还触发payload-owner断言。不能将此归咎于无数值SASS，不能
关闭断言过关。Core1565f1f0只是已测clock-only增量；832d986b的warmup候选在
所消费receipt中尚未编译，R0.1/R1.1官方freeze及独立资格待新身份发布。

旧静态vectorAdd的1.721259×是另一系统的历史乐观读诊断，未自动被FT bank反例
证伪，仍保留独立图；不是R0/R1/R0.1加速或严格上界。历史13行locality与资源
bit算术继续复用其准确原证据，均不填补修复版应用结果。

验收顺序：最新明确supersession/撤回 > 历史release资格 > 原run终态。
当前消费者在线解析固定Lane-5执行ref，绑定当次精确APPLICATION_ACCEPTANCE、
VALIDATION_MATRIX、RECEIPT及完整supersession pack校验闭包；无匹配CURRENT_ACCEPTED
则拒绝正式图。原r2程序只作冻结历史实现，不是当前允许的消费者入口。
