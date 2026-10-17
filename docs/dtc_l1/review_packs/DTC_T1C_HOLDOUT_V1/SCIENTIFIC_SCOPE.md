# 固定 T1-C 的两个独立 holdout

仅原 DWT2D 与 BICG 完整输入，各一个新 UUID、一次实际启动；DWT2D strict PASS 后才运行 BICG，最多1个新DTC并发。固定64 sets×8 ways、OO PIB128，其余所有有效选项和默认值与各自原OO完全一致。原Core/build/binary/parser/runtime不变，不修改原A/M/T/44行/raw/锁。

两输入未用于T1-C选型，但旧baseline已知，不能称完全未见过的程序。原GEMM/Gaussian A/B/C矩阵只作已完成发现证据，不重新选择配置。没有新增硬性能门槛或holdout GM；逐输入报告R_OO、R_CPLUS及周期增减，所有负结果、timeout、deadlock与未启动项完整保留。严格不完整点没有正式速度比。

DTC reference的ready/pending/new outcomes采用相同128B接受事件分母；服务驻留取全64SM累计integral/samples，ready/collect/WB等条件均值取相应retired分母，不能当可加整机周期贡献。实际L2/DRAM字段复用Lane M定义与带范围检查的只读extract；任何单位/路径/stream/controller/CSV终态范围不闭合，标UNCOMPARABLE，不把credit变成DRAM字节。

strict沿用Lane T已核语义：自然exit0、完整list/member、每ordered kernel的CTA/active instructions、实际全选项echo含defaults、64SM、credit/dependency/lower/ordinary守恒及PIB/inflight/activeRef/partial排空、physical分配回收平衡、11finite统计、stdout/terminal/config/runner/runtime SHA。Tag-visible retained物理数据合法；不强制allocated=0。

独立sector返回计数、ordinary内部MSHR占用、完整数值load正确性及PPA仍UNAVAILABLE。640×128B物理80KiB、ordinary16KiB、shared96KiB及finite资源不变；512条Tag只扩大可查询映射。额外比较、metadata、端口、fanout、generation/Ref/waiter和时序不免费；1cycle查找只是冻结模型假设，不能宣称等面积/同频/native或更新论文主设计。

旧44行的41 PASS/3 Hotspot HOLD、原GM12未定义、modern128 HOLD及所有既有STOP保持。本Goal不运行T2、新observer、物理池调参、新Tag、第三输入或任何Hotspot/Btree/2D/LUD/SpMV/LayerNorm扩展。两点或合法STOP后结束交审，无自动论文替换权。
