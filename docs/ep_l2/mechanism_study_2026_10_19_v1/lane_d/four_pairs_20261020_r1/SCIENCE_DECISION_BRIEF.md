# 四对正式S/F：科学决策短报 r1

E2冻结提交 `13718839b515542f332eca6a845701a8dbb9a922` 的三份D_MECHANISM_DETAIL_NOTICE已完整读取，接受声明与中央当前pair逐项一致；Conv旧正式配对保留。八端准确source/config/binary/trace/run-key/qualification/receipt身份在CURRENT_ACCEPTED_PERFORMANCE.csv及E_CURRENT_ACCEPTED_PAIR_SNAPSHOT.json；所有E接受的raw哈希由既有分析工具复核。主binary保持 `61aad385723ac97a76cb1f32c124b286a10bc8609c9c58b1a3ef8a87413f2dd5`，Core `d010911e3174a3764791183cd108fe4664ba8731`、Framework `9dd1ee57a83d83b56b7874bc7c716185ab52c8f7`，4bank/P1与1168payload合同不变。

| 应用 | S cycles | F cycles | S/F−1 | S−F cycles |
|---|---:|---:|---:|---:|
| sad | 110773 | 109754 | +0.928440% | 1019 |
| cfd_097k | 79093 | 79157 | -0.080852% | -64 |
| convolutionSeparable | 292932 | 291469 | +0.501940% | 1463 |
| dwt2d | 166519 | 167643 | -0.670472% | -1124 |

**当前四对临时几何均值 S/F=1.001679474（+0.167947%）**，仅这四个已接受输入。原七应用分母仍7，完整七输入GM为UNKNOWN；不是论文全应用总体结论。FWT两端INCOMPLETE，Vector只有S有效/F资源终止，Btree HOLD，不以旧binary、残缺端点或补1填入。四组正式机制图、四对性能图和原七位置主图均已导出PDF/PNG，负面结果完整保留。

## 能主张的结果

- CFD：49,962次真实victim读、51,678次line-MSHR分配避免，但整体多64cycles（−0.08085%加速）。S没有观察到line-MSHR-full阻塞，故“避免分配”未证明解除基线瓶颈；bank授权仅降约4.13%，lower读字节降约2.75%。新增160,847次V查询和206,448次RO查询是真实事件，可能抵消局部服务节省。V响应不能一对一视作相对S避免的miss；净下层读只少5,846包。各因素边际cycles未知。
- DWT：23,305次victim读、9,965次line-MSHR分配避免；bank服务少349,226（约13.84%），lower读少693,696B（约5.575%），却多1,124cycles。S同样未观察line-MSHR-full。F新增bank-compatible landing首次阻塞5,099请求/请求等待和148,372/max669；V查询311,718、RO查询39,836。其物理landing约束和查询路径是优先追查对象，**不是已证实的1,124周期因果分解**。WAD/复制/数据服务等待减少也照实报告。
- SAD：无victim读、RO准入、成功detach，lower读与WB字节完全不变，但少1,019cycles（加速0.92844%）。复制读写各3,975→0，物理bank授权少7,962，几乎对应7,950次复制操作；这支持W时序/共享服务假说，尚不能排除V保留/查询对置换与排队的间接作用。W_ONLY是可证伪的最小控制：若无法复现F的时间改善，单独W解释不足。
- Conv：保留+0.50194%及此前完整归因，不因新增结果重算为其他binary或旧H0数据。

## T机制科学措辞

四组F均T配置ON；最后64slice累计 **stats.detached之和每组都为0**。这是成功执行Tag detach握手的实际事件计数，不是关闭T，不是所有尝试/可避免拥塞的机会统计，也不证明T没有查询/检查成本。**这四个应用不能支持“Tag脱离获得实测应用收益”**；可写RO line-MSHR避免已触发，而T功能存在、其成功脱离收益在当前四应用未被观测。禁止把M准入/合并当作T收益或把T直接改为OFF主方案。

## 立即交E2/A2的最小控制方向

优先针对已经预登记并完成的输入分离机制，不按F加速选择新正式workload：DWT的S→W_ONLY→W+V(T/M OFF)→F两项缺口控制可区分W、V净作用与R净作用；SAD W_ONLY检验“无V/RO直接服务仍获益”的W假说；Conv原矩阵中的F_MINUS_R与WV_M可在已有S-MSHR压力背景隔离M。准确条件、信息价值排序、可证伪预测与是否超原矩阵由下一版最小需求表逐项列出。

目前累计20/40，原控制器STOPPED，无ready且已独立合格的新条件。请求不是运行授权：新profile先由A2确认源/配置、E2独立资格/资源；DWT/SAD新控制若不在原32矩阵内，必须明确科学范围/预算重分配批准后才可运行。D不启动完整应用，不改变中央台账或main61，不改EN-v20。

等待统计跨请求、slice和原因重叠，**不相加成程序stall**；不同路径重复投影也不重复计成本。上述“可能抵消”“影响关键路径”均为待控制检验的因果假设。当前四点没有重复运行/误差条证据，不声明统计显著性。
