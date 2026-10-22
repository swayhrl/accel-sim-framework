# E2单一owner：detach=0彻底归因Goal

当前Goal ACTIVE，原campaign、T0、计数和唯一controller不重启。E2直接完成执行、独立终验、源码/原生证据/资源结构审查及最终归因；D仅接收论文整合材料，不是前置依赖。批准r4四端已经实际启动4/4，累计55次；Conv仍运行。

已查清的第一层原因：已接受的SGEMM/CFD/DWT/Vector实际production Tag RESERVATION_FAIL、relieve、detach调用均0。SGEMM另有无RO事务且已覆盖认证候选全resident-hit；其余三端真实RO事务分别51678/9965/250118。这些事实解释触发分支为何未进入，但不等于所有底层机会问题已完全回答。既有point内EXACT_POINT_CAUSE_CLOSED只按这个必要触发层理解。

新深审结果：

- [源码审查](trigger_semantics/REPORT.md)：RO新请求的rawFAIL→preview MISS→ft_access relieve路径真实可达；普通非RO requester的前端不咨询RO relief属于继承main61的确切范围边界，没有当作当前zero的原因或未经批准改变机制。
- [原生证据审查](native_coverage/REPORT.md)：保存控制中有6次真实detach成功并返回退尽，排除核心链整体计数断线；212项均发射，113项有非零实测，99项未刺激，不冒充全分支覆盖。
- [资源结构审查](pressure_structure/REPORT.md)：每slice64set×16way，Tag1024，D512/每line32、native-line128、统一payload1168、4bank物理P1。WBUF16不是mode2额外WB角色硬上限，wb_local_cap=0的合法共享借用不算新机制。
- [独立科学结论复核](INDEPENDENT_SCIENTIFIC_REVIEW.json)：55项有限检查通过，四已接收点明确不含尚运行Conv；源码/结构/正控不能扩张成应用T收益。

仍未解决的关键层：r4没有记录同一snapshot的reserved-way数量×raw状态/新Tag身份需求×eligible RO联合分布。bound_tag_peak达到1024只证明采样有效Tag绑定满，不表示16way全reserved；RO活跃峰值64/58/96为per-slice覆盖所有set的总数，不能平均分配或证明同set并发。甚至set16way全reserved时，若只发生same-line HIT/HIT_RESERVED/SECTOR_MISS，也不一定产生rawFAIL。因此不把‘没有FAIL’写成‘从未全reserved’，也不把它冒称彻底解决。

接下来E2继续独立完成Conv终验，并一次准备最小被动联合观测修订；新source/binary和额外完整应用不在已批准r4四端内，须取得精确批准后才执行。当前不新增启动、重跑有效端点或改变生产机制。全部失败/负结果/HOLD、旧main61及10/24GiB累计生成和workspace5+2GiB保护保留。
