# DTC-L1 实验主线 V5｜已验证执行效率与科学收口（2026-10-16）
 
**来源：** Lane A `d2f2f6c752cf0f4e7d4970514cc57cc2f31025a9` 的 11:53 UTC 检查点 `review_pack/checkpoint_20261016T115304Z/SUMMARY.json`、严格验收报告与状态清单。Lane B `d9f896a570da1218b0c93c2c68b930835eeac2fe`为最新可见远端证据；用户已发V2后续审查指令，但**还没有可确认的新远端完成结果**。Lane C `d6f0a330`、Lane D `d58e75ce`成果不变。本表不是实时进程监测，V1—V4保留。

## 科学状态与总体判断

| 类别 | 已发表验收证据 | 判断 |
|---|---|---|
| 44条R2注册模拟 | **22 terminal/invariant PASS + 19 LIVE + 3 Hotspot admission HOLD + 0 eligible unstarted** | **调度覆盖达到本轮上限；没有理由再增worker/开矩阵** |
| 科学可解释的通过数 | 20条通过不受已发现Hotspot解释问题影响，另2条Hotspot执行PASS但科学HOLD | 不能直接以22作为无条件论文样本 |
| 主三臂完成 | Btree、2DConvolution、DWT2D、MRI-Q、NN五个合法完整比较；部分其它arm已经PASS或LIVE | 数据已能做针对性机制说明，但不能称GM12或等面积比较 |
| 已完成WAIT128与matched-depth | Btree matched IO128/OO128及WAIT128 PASS；其它BICG/2D controls LIVE；Hotspot controls HOLD | 已有有用机制证据，需保留不同分母和状态存储代价 |
| Gaussian / LUD | Gaussian IO全510成员 PASS；LUD TRAD96全94成员 PASS、8:58.41 elapsed、700416KiB peak RSS | 长负载已经进入运行和自然验收闭环，不因多开窗口重跑 |
| 资源 | 19个live进程保留启动身份且CPU ticks增加；own RSS39.6GiB，MemAvailable258.9GiB，可写43.5GiB | 当前检查点未见内存/IO明显拖垮，但不等于保证所有剩余作业的完成时间 |
| B / Hotspot | 已接受继续**审查V2派生解释**，而非批准新输入生产；候选6PC/122760 records/2944024 active lane addresses变化 | 若语义/源绑定不闭合，保持HOLD和没有合法GM12 |
| C / 现代4080 | NO-GO for DTC comparison under fixed128KiB current contract, retain modern baseline only | 不投入大规模存储/端口/epoch新实现 |
| D / SM89 SpMV | NO-GO for simulated admission; native result retains | 不以89→86别名掩盖常量地址和依赖缺口 |
| AREA | 当前统一面积/时序报告未到位 | 资源效率不能直接写作等面积性能提升 |

## 执行效率判断

全部可合法启动的41条均已启动，每条只有一个attempt；当前19条LIVE说明真正的关键路径已经变成自然完成/逐行严格验证。**不再为提高并发增加未知实验。**这是本轮“先合法gate再滚动，长任务提前开始，冻结baseline精确复用”的目标状态。

下一步滚动策略仅包括：(1) 保持Lane A唯一launch authority、对应结果逐条严格验证；(2) Hotspot只由Lane B整理V2审查材料，不修改A的44行；(3) B/C/D均不得为追求现代结果或已知HOLD另建分支模拟矩阵；(4) 用户硬件面积与ChatGPT论文图表同步推进。

## Hotspot决定的影响

用户已选择继续V2重建解释审查，**但尚未批准派生地址进入模拟器**。严格保留 old input and results；若后续科学审查授权，建立新的派生输入SHA，重新配对B16/IO/OO及确实需要的传统控制，不准与旧baseline拼接。查证另11负载的旧格式适用性时限于CPU-only格式审计，不触碰他们已经在运行的仿真。

## 下一步最重要的三个验收门

1. **主结果门**：其余19条的真实终止、严格身份和数值验收；完整对照中明确所有不利点，不能半途计算GM12。
2. **Hotspot门**：Lane B来源模型、global/shared改变和独立raw地址证据均闭合，独立准入或明确缺项处理；目前不可用原语义宣称最终12项平均。
3. **硬件与写作门**：服务假设、输入范围、面积/时序、最合理传统增强资源向量都进入正式稿，不把原论文4.7%替代当前面积，也不推断现代DTC性能。

**本文件是已发布状态快照与审稿判断；没有启动后台监控、GPU job、Core修改或新的实验授权。**
