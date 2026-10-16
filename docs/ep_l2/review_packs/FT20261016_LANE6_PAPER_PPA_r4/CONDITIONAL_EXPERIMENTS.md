# 条件性对照与结果槽位（未授权新增科学配置）

首轮仍是新R0.1 B16_BANKED/U_WB16五个原负载，主WBUF16、敏感8、N1168/1160不变。
以下只是可审阅的设计，不是运行spec、配置变更许可或配额申请。任何变体先冻结身份、
逐项明确改变的科学边界并取得所需批准及独立资格，不因本文表格而自动运行。

| 触发证据 | 对照 | 主要观测 | 不允许的解读 |
|---|---|---|---|
| 新合格应用显示静态配额压力与实际跨角色容量效应 | 同1168项静态1024 resident/112 bypass/32 WBUF | 不同角色容量、拒绝、WB/WAD与bypass损失、cycles | 只看到resident→WB role事件即宣称借用性能 |
| copy与容量因素同时改变 | 等copy服务归因变体，精确定义操作注入／保留与仲裁 | logical ops、copy/lower-send read、Bank等待及周期 | 加免费端口、把attempt当operation、用bank wait和直接减GPU cycles |
| 真实L2服务变化而应用无变化 | B/U×当前下层/一档证据支持的headroom | 同档两侧匹配、lower/WAD/DRAM变化 | 全矩阵泛扫、把修改下层的诊断当主配置结果 |
| R1.1官方binary+独立repair/ideal资格+同binary B16 | 原18格I_WB/I_META/I_READ_HIT及两格I_WB_META | 条件是否non-binding、blocking迁移 | 旧R0/R1/OLD_STATIC任意跨binary分子 |

吞吐代理：I_B=I_U且口径相同才有IPC_ratio=(I_U/C_U)/(I_B/C_B)=C_B/C_U。
记录该I/C的模拟器计数定义，不冒充单SM硬件IPC。无当前合格pair不填数、无全五点不填geomean。

图表槽位：

| ID | 将承载的信息 | 本revision内容与解锁 |
|---|---|---|
| F1 | Tag退出／payload转交／lower_accept／set_done的分离 | 正文生命周期表已写；可选机制示意后补，不需要性能数字 |
| F2a | 相同数据预算的五点配对与完整均值 | 留空；CURRENT_ACCEPTED新pair逐点进入，全五点后才求均值 |
| F2b | copy／capacity／下层／cycles四类归因 | 留空；与F2a同完整run-key来源，局部事件不先写收益 |
| T1 | RAM+latch与字段／逻辑成本 | 正文已有实数预算与符号账；不填工艺数字 |
| F3 | 同binary理想诊断及non-binding条件 | 留空；R1.1自身匹配基线与资格后再填 |

历史1.721259倍只保留独立历史诊断地位，13行locality仅作动机；旧sad图与解释继续撤回。
