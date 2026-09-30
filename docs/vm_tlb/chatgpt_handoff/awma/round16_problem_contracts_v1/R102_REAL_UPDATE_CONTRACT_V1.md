# 实验合同二｜R102：真实权重更新的检测—打包—应用

**2026-09-30｜R102_REAL_UPDATE_BOUNDARY_V1｜拟由Lane G / 109准备与执行。** 不恢复旧Goal；本页冻结新输入准入与最小实验，来源及统一规则见`SOURCE_AND_SCOPE_NOTES.md`。

**问题与假设。** 在真实RL发布权重、逐bit重建和强软件基线下，比较、压紧、打包、发布元数据、接收端应用是否还存在值得研究的GPU局部开销？不重新主张“低精度更新稀疏”这一已知发现，也不把通信压缩比当成GPU性能收益。[S5–S7]

**输入先行。** 旧R102仅闭合Helix源码，没有真实before/after，保留其STOP。新准入只接受同一训练run的4个相邻发布版本，或“完整anchor＋有序真实patch＋目标hash”确定性恢复出的版本；记录训练算法、optimizer、dtype/cast、实际step与发布间隔。发布窗口可能包含多个optimizer step，不冒充逐step。限定检查旧清单中未检查的PULSE/Grail入口、Helix新增artifact及新到位的本地资产；不重扫整块164。没有合格数据就输出精确缺口并休眠；本轮不自行训练、不用随机mask、统计CSV或R101的CE梯度冒充RL更新。[S8]

**冻结范围。** 3对相邻版本：前2对发现，第3对时间留出（不称独立训练验证）。按参数名排序取累计不超过256MiB的完整tensor形成一个固定bucket；不按变化率挑选，不切造热点。保留完整tensor的原shape、顺序和dtype。结论先限定bucket；原同步时间权重缺失时，不估计训练吞吐。

**最小对照。** B0：整个bucket新值覆盖旧值。B1：按公开实现的比较→索引压紧→取值→打包→应用reference。B2：同一payload格式/顺序下的一种有界强软件路径，最多两遍扫描的fused compare/compact＋scatter-apply，不扩成编译器工程。D1：离线预生成同一payload，单测apply；这是绕过encode的诊断，不是在线候选。科学候选仍必须扫描真实before/after，不得偷用原始patch索引。共3个实现×2对发现数据；值得继续才用第3对验证。

**数值与计时。** changed按存储bit判定，发送绝对新值而非浮点差值相加；重建bucket逐bit一致，覆盖NaN/±0、未变元素、零变化、索引顺序及错误base-version拒绝。单测可用fixture，性能证据只能用真实更新。主边界为两版本可读→payload及必要元数据就绪→consumer完成应用；复位在计时外，required同步/shape读取/分配计时内，encoder/apply及完整链均报告。记录payload、scan字节、临时峰值、launch和host同步。最多1次NSYS，只有残差有价值才采最多2个NCU目标。

**判断与终点。** 先报告B0/B1/B2完整局部成本，再算无重叠条件下`T_dense(B)=D/B+T_copy`、`T_sparse(B)=T_encode+S/B+T_apply`的盈亏平衡；这是参数化估计，不是网络实测，存在流水必须另建依赖图。若强软件后主要价值仅是网络少传数据，或GPU开销已无具体可定位残差，就保留软件/系统结论，不进174。只有真实输入、bitwise、重复与时间留出均通过，且在真实同步范围有至少5%的剩余乐观空间，才申请机制；无系统时间权重时仅保留局部结果，不伪造推广。
