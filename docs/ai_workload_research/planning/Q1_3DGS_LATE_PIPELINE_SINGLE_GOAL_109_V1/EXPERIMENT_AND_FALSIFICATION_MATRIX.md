# Q1软件、诊断、独立验证与机制反证矩阵

提案，未运行；与[Goal](../../goals/AI_ARCH_Q1_3DGS_LATE_PIPELINE_SINGLE_GOAL_109_V1.md)一并派发。最小点数由识别力决定；可在资源内对称加重复或增加一个有预先假设的合法软件对照，不设任意完整仿真次数。

## 软件政策与抽样

T8/T16是OMP有效cap，不假设作者64 request消失，也不把它们当实际Torch线程数。记录OMP runtime、Torch intra/inter-op、实际线程与affinity/P-E/SMT/NUMA。所有臂使用同一owner批准CPU集合、source/math/environment、恢复起点、自然camera及closure。J是事前登记的一个joint Torch/OMP或P/E placement策略，不把多个变量一起变化却声称独立归因。

规范路径T16生成C_D和C_V；正式测量不选择快臂的状态当验证起点。C_D next_step15140、发现窗口15150–15200；C_V next_step15240、验证窗口15250–15300，均半开，10自然步骤预备。若真实合法late state更晚，按Goal内部规则在看性能前冻结等长结构及输入SHA；不事后移窗口。

每个policy×window是2个完整warmup区组、5个formal区组。每次恢复同起点，区组是独立执行重复但不是不同训练样本/scene。预热与restore时间不进入原训练窗口，另报并计总资源。主指标为50-camera目标窗口加共同合法closure的完整wall，body/drain分列；GPU时间不与Host直接相减。

固定最小formal顺序：
- 两臂：第1/3/5轮T16,T8，第2/4轮T8,T16；warmup同样交错。
- 三臂：五轮分别[T16,T8,J]、[J,T8,T16]、[T8,T16,J]、[J,T16,T8]、[T16,J,T8]；warmup正/反各一轮。
- 验证：T16与冻结胜出策略按两臂顺序；若胜出为T16只保留一个配置的独立窗口。
追加重复必须同时覆盖可比较各臂，以新编号保存全部样本，不删慢点。median/MAD、配对差值、drift和实际工作量都报告；小样本不夸大置信区间。


发现阶段选择规则：只使用全部已登记formal完整区组，比较median/MAD、drift及实际完成工作；有效且严格可比策略中以完整wall median较低者为冻结验证策略。若工作/数值仅描述性可比，就称“描述性候选”，不能称等价最优；仍在保留窗口原样验证。没有显著或稳定差异也报告零结果，不设置事后挑样本的胜出阈值。

## 科学问题矩阵

| 问题/假设 | 控制与观测 | 能否定该解释的结果 | 限制和行动 |
|---|---|---|---|
| CPU生产端是否关键 | T8/T16；自然N/U、scan/Adam/forward、完整wall/closure | CPU某组件更快但完整wall不改善，或主等待并非其下游 | 降低该组件优先级，不把组件加速当应用收益 |
| OMP/Torch/placement是否软件混杂 | 一个有依据的J，原source/math、同CPU集合/状态 | 合法线程策略吸收等待/完整时延残余 | SOFTWARE_ABSORBED，关闭相应硬件方向 |
| observer是否造等待 | 规范T16及冻结较强臂，各做同state OFF/ON配对；至少3对完整区组，诊断分池 | 只ON有等待、或数值/队列/更新次序受hook改变 | 不将ON现象外推OFF；修observer或保留缺口 |
| H2D/D2H是否真的负载 | 真实方向、src/dst、dtype、numel、unique storage与实际服务；SHdegree单列 | 调用存在但payload为0，或等待来自CPU而非传输 | 不从copy次数推带宽瓶颈 |
| 主线程是否暴露等待 | 同host时钟、TID/step、sync/join区间并集；worker并行另列 | 原大区间主要被CPUAdam重叠覆盖 | 保留A44解释，不重复跨线程加总 |
| GPU/link是否还有独立成本 | 一段真实输入的GPU服务诊断；必要时分离的合法时间线/counter | 数据未就绪而GPU服务短，或软件消除关键路径 | 最多局部归因；无供给轴不宣称SM/DRAM因果 |
| 重复传输/布局是否可软件吸收 | 私有最小同值/同alias/lifetime补丁，先验收数值与队列；局部及完整wall | 删除kernel但应用不快，或改数学/状态/质量才快 | 无完整收益不晋升；错误补丁弃用但保留原证据 |
| 结果是否只适用发现窗口 | C_V预冻结自然camera；同策略与完整state起点 | 独立窗口无效、方向反转或轨迹/质量变化 | 限定结论，不挑替代window |
| 是否存在硬件机会 | 强软件后实际残余、完整应用分母、具体物理变量及反证 | 残余已软件吸收、只有必要payload或无独立变量 | NO_HARDWARE_CANDIDATE_PROMOTED |

## 对照和结论不能混淆

- 无第二scene就只称单Rubble、跨自然窗口验证，不称跨场景。
- 原实现CPUAdam与GPU-only的数学/更新算法不默认等价；本Goal不以GPU-only替换CPUAdam作为主基准，也不自动跑late GPU-only。
- CLM覆盖reuse/appearance/overlap/调度；TideGS optimizer cold restart/camera顺序是另一语义。软件新意与性能测量排除分开。
- 单N/数据状态局部replay不得叫整应用；固定kernel字节不乘层数。
- 只有同起点且完成工作/轨迹可核才给严格配对；数值敏感但身份有效者给描述性对比并保留质量缺口。
- 硬件卡须列幅度、软件残余、拟改变量、收益机制、否定结果、独立验证、PPA/复杂度代价。无物理供给轴不升CAUSALLY_SUPPORTED，不自动改全局设置。
