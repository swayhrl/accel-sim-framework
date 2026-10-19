# 图题与逐事件分析规则

主图：七应用在同一最终binary、同一完整策略、同一非实验变量下，传统静态结构S相对完整方案F的周期比。F=W+动态完整victim+T+M；不同输入仅证书范围不同，未认证line回退。F不触发/退化仍保留。只发布7/7同版本完整均值，缺项显示待测，不使用旧H0替代或给未测S画1。

三项去一项：Conv/FWT中去掉W、V、R后，相对于同版本完整F的周期变化。ratio=cycles(去一项)/cycles(F)，>1表示该项在当前完整背景下有利。它是条件贡献，不是三项可相加的独立收益。F−W须保留V/R的共同映射与原位身份，固定WB16且付真实复制服务；若A报告DEPENDENT_CONTROL_UNSUPPORTED则该点未实现，不用S冒名。

写回子方案：在相同S和F锚点下比较W-only，分别给cycles(S)/cycles(W)及cycles(W)/cycles(F)。不会以某一应用最快W-only替代F。

只读四格：固定W+V背景，T/M00=F−R、10=WV_T、01=WV_M、11=F。既报告每格真实拒绝、并发、完成吞吐和重复lower字节，也报告C11−C10−C01+C00（cycle）交互；四格不齐不填交互。并发峰值与独立地址峰值可能不同时发生，不能相除解释重复率；读取lane引用也不是L2请求数。闭世界oracle假设与覆盖分开呈现，不宣称硬件认证器。

固定淘汰区：Conv预先采用既有64/1104同容量控制，四bank各16/276，固定/动态目录查找与P1数据收费一致。现有源码仅fixed-clean，dirty+RO组合尚未资格，不能把它叫完整固定对照。预登记不根据F速度调容量。

局部服务诊断：S_COPY_FREE仅免复制两阶段与约定staging服务，实际版本搬运及发送读仍正确收费；S/F_L2_DATA_FREE免L2数据bank争用，保留固定复制锁存、tag/MSHR/descriptor/WAD/槽容量、真实miss及下游/响应背压。二者分别解释复制服务和数据端口压力，不称整个L2理想。F_L2_DATA_FREE需新组合生产资格。

静态WB64：同最终binary、同1168总槽，新增48个静态写回槽必须说明从何角色转入；不是赠送总容量。未冻结转移定义前不启动。

每个E接受配对立即运行一次full_v2_analysis.py。沿用现有E accepted_results/accepted_pairs及qualification哈希，E只需发布显示绑定（条件ID→已有profile/配对ID、同一final source和固定策略hash）；这不是第二个验收器或调度器。没有真实E映射则单独保持未测。源、输入、配置、撤回、科学hold任一变化只hold受影响数据；历史保留ANALYSIS_HISTORY。不得从终端截图或进程退出推断接受。

每对按四层写解释：传统瓶颈→真实触发→局部服务/流量变化→总周期。W重试不等于uniqueUID，V只接受真实L2序机会/命中/避免lower读取，R只读覆盖不能代替实际受阻UID交集；缺少trigger/local仍可报告真实周期，但因果标UNKNOWN。跨slice重叠等待不能相加当程序stall。

D不启动完整应用、native测试或修改E台账；10个新增显示完整性测试只证明控制工具。原15机会表、四预登记、旧科学结果、EN-v17保持。
