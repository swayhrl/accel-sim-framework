# 覆盖与论文表述边界

截止数据：分析UTC 2026-10-29T00:08:15.273571+00:00，对应222个独立元数据闭合的CLOSED_ACCEPTED实验点、110组同硬件匹配对照；227次启动已全部消费，2次技术失败保留，3项长尾未闭合。分析来源：`/root/data/ep_l2_full_workload_performance_20261027_v1/agent_b/results_analysis_20261028_v1/versions/20261029T001004Z_ef632d38/RESULTS_ANALYSIS_CURRENT.json`，SHA256 `e81a90d58fecde006150d3e3fead6f9f4234d61c538d7422c45a3886fdbae163`。本文件不读取raw/Trace正文，不启动模型，不修改科研注册表。

**PROVEN：** 当前222点是多配置/多模式实验端点，不能称为222个不同工作负载。110匹配对照也不是110个程序。当前精确参考S/F为23输入、22程序，S/WV为7组且与S/F不保证不交叠，不直接相加。

原目标保留：主42程序，已冻结35精确代表与7个未裁决程序分别管理；125资产含100普通记录与25裁剪记录；100普通记录按完整有序命令内容归为96组，但不跨Suite、版本、算法实现和输入规模抹去科学身份。完整35/96共同合格集合没有闭合，因此全35/96 GM为UNKNOWN，未覆盖项不能填0或视为负例。

旧覆盖台账截止2026-10-28T06:09:39Z，SHA `08511fbb159112122edbf21daced146002e8908d62e6375bb53a557f5ce09752`；其中主35 18组S/F、2组S/WV是旧时点值，不代表当前新结果。它保留资格/HOLD原因；不能用旧计数覆盖更新后的23输入REF匹配值，也不能由当前总量反推主35的分母归属。

尚无参考规格的主35候选在旧台账为mri-q、bfs、sad、histo、cutcp、hybridsort、myocyte。Hybridsort有global STG地址0域HOLD；SAD有texture不计时限制；多项含post-kernel HtoD，需精确主机写入适用域，不能将Naive失败泛化为所有输入失败。Cutcp RO未知；WV名称不证明RO=0。Myocyte命令规模需要专属执行/输出资格。上述没有因本轮收尾自动解除。

7个未裁决程序：backprop、CFD、kmeans、nn、nw、pathfinder、streamcluster。其输入规模、实现/版本、迭代或命令域差异未闭合，仍保持UNRESOLVED；不得按性能正负替换冻结代表。

**PROVEN：** SRAD62行RO派生证据、真164归档与双恢复已完成，但native174 loader未运行、新F应用未启动；它仍不贡献接受F性能配对。FWT whole-epoch RO=0与particlefilter_float RO UNKNOWN应分开；未具备T适用资格的WV结果不能计作“真实零detach”。

论文可写：在已冻结trace-defined完整commandlist范围内，已测试候选有正有负，三个预先固定8输入验证人口均未显示同硬件完整EP总体净收益；小Tag几何存在真实detach机会，但尚缺T独立收益反事实。

论文不能写：全35/96程序验证完成、原GPU默认参数下T已加速、较小Tag即减少实际硅面积、理想端口诊断即硬件可部署最优。128B×1168×64=9,568,256B物理Payload数据存储，不含RO/TVD等元数据；Tag可寻址覆盖不是Tag SRAM面积。Source92 P2仅Vector同Source92 P1可比，不拼接Source78性能。

原始capture完整性和数值SASS输出正确性UNKNOWN；“完整”只指冻结Trace命令列表的完成与资源drain。后台长尾完成后应追加它们的精确状态/配对，不扩大授权、替换人口或补造缺失计数。


## Main精确覆盖补充

以本轮222接受点为时点，精确代表/普通输入覆盖见`FOREGROUND_COVERAGE_ADDENDUM.md`及对应CSV/JSON。它们是前台收尾快照，不冒充后续长尾的实时表。长尾的当前状态、接受点和新增配对见自动更新的`LONGTAIL_RESULTS_CURRENT.*`及上级`RUN_STATUS.csv`、`MATCHED_PERFORMANCE.csv`。主35为22个S/F、2个仅S/WV、2个LIVE输入、1个S_ONLY、1个技术失败输入、1个明确HOLD、6个未启动；主42另有7个UNRESOLVED slot。
