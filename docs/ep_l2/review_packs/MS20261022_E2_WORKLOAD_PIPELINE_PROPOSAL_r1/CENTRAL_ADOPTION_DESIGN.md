# 原中央流程接入设计（待批准，当前未修改生产）

当前中央`limits_policy`把已取消的数值/时间限制绑定到准确十个旧容量条件。原32矩阵桶也已耗尽；不能通过直接加旧reservations或重用旧FWT condition_id来绕开。此提案申请两个各2次的新scope，并保留原32、8次contingency、10个容量条件与原46次启动历史。

批准后只在原中央执行流程内加入新四条件范围和独立batch ledger。新scope必须绑定用户批准文件的commit/path/SHA、四个condition_id、准确main61/source/archive、完整trace、S/F profile与spec/Q。旧limits-removal记录和其original_reservations/oldsource/oldmatrix快照保持；旧十条件分支仍按原规则。新增路径不能借其`maximum=null`授权。

`coordinator.reserve_application`在同一永久REGISTRY.lock内识别明确批准的新batch，与原bucket分支分别计量；所有实际启动仍进同一attempts计数、runs和resource_leases。FWT两端必须精确指向E011/E012历史INCOMPLETE；SGEMM建立自己已获批的独立D输入选择/比较组，只引用已发布中立冻结证据，不覆盖原七选择或Btree。每个新condition仅一次尝试，失败仍收费，无第五次、隐式替换或自动retry。

原唯一controller采用新plan的明确phase，继续既有runner、durable_exit、resource gate与永久CONTROLLER.lock；不另开实验调度器。运行时utility改动必须先经原发布/回读及CLIENT源码清单重新绑定。main61/Core/Framework/vendor/archive和生产协议不改、不重建。已有source/native/parser资格仅在确实未受影响的范围复用；新spec/工具/操作门逐项重绑。

新四端拟effective_timeout=null，以准确新批准的操作override承载；不重写原FWT identity中冻结的10800终止字段，也不恢复旧18:00/22:00或总46限制。FWT子审的10800是旧spec事实，本提案的最终请求以PROPOSAL.json的显式新操作范围为准。正常退出、完整命令/指令、64slice、资源退尽、全身份及科学终验仍全部必须成立。

只做有界非完整应用控制验证：精确四端允许/额外ID或错误binary/input/profile拒绝、重复/fifth拒绝、失败计费、old46prefix/矩阵/桶/接受结果/HOLD不变、原资源和累计结果门、单controller和真实wait持久化。测试用临时内存/假进程状态，不启动模拟器或新native；不得把这些工程控制当科学资格。验证通过后才按同一原中央准入逐路启动，资格或预算不满足仅停受影响项。

本设计没有当前中央写入、CLIENT改绑、生产源码变化或运行授权。实际审查发现上述范围之外的语义/身份/比较/预算变更时，单独提交审查。
