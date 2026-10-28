# Lane O Workload Memory Characterization

本阶段只读审查和采集规划已完成，供用户审查。五个有限子Agent分别审计W、V、M、T及全负载覆盖；没有启动新GPU仿真、构建或修改Main/生产Core。结果与计划保存在独立Lane O目录。

当前最有依据的论文观察是：脏替换搬移与写回空间压力存在明显负载差异；部分淘汰数据确有继续读服务的价值；RO请求有显著同址合并；Tag压力必须按新请求与目标Set联合衡量。所有机制收益仍按独立控制的证据边界表述，正负样本均保留。

## 审查入口

| 交付 | 内容 |
|---|---|
| [简明指标表](METRICS.md) | W/V/M/T定义、分母、统计分布、现有覆盖和新增成本 |
| [现有证据与缺口报告](EVIDENCE_REPORT.md) | 已验收结果支持什么、哪些仍未观测、谱系和统计口径 |
| [最小采集与实验计划](COLLECTION_PLAN.md) | 先复用，再按缺口准备被动计数；正式采集由Main统一安排 |
| [初步Observation草案](OBSERVATIONS.md) | 已证实、历史证据边界、待验证、不成立的推断 |
| [42程序指标覆盖CSV](METRIC_COVERAGE.csv) | 按完整输入SHA连接的当前metric可用性；[解释](METRIC_COVERAGE_NOTES.txt) |
| [全负载身份与验收CSV](agents/coverage.csv) | 35冻结代表与7身份未解，覆盖不以成功子集替代 |

## 核心事实

- Main快照为北京时间2026-10-28 18:30:57：214个accepted点，22个REF S/F输入配对；主35中25个输入至少有一个accepted点。其后新结果不自动加入此固定报告。
- scan参考S：WBUF峰16、均值10.661；1,737,618个独立请求遇WB_DATA_SPACE，对应49,938,625次检查。Conv有16,791个同址WB独立受阻请求。已有MS等待统计应直接复用。
- 当前23个F参考端点中10个有V读响应、13个为零；FWT WV存在3,312次dirty-forward。它们证明服务事件，不直接给出victim命中率或所需容量。
- Vector约75%的RO requester合并到存活事务，严格fill前重访比例仍未知。Conv普通MSHR满载与SGEMM同址chain上限是不同现象。
- Conv已测同Set满路preview压力；较晚Vector4M的32×4已出现27次detach。当前仍不能声称独立T加速。
- 历史Motivation已有reuse distance及post-eviction统计；Streaming prefinal已揭示空间sector触达与真正时间复用的区别。应先补历史小CSV/manifest索引，不重复扫描大Trace。

后续建议先由Main增量导出现有小汇总，再审查轻量统计候选；如批准工程，使用独立工程分支。计划中的pilot与全代表覆盖均未启动，也不在本轮注册预算。

## 保存与审计

本地：`D:/repo/ep-l2-lane-o-20261028`。

远端：`hrl-174-new:/root/workspace/ep-l2-lane-o-20261028`。

Agent附录：[W](agents/W.md)、[V](agents/V.md)、[M](agents/M.md)、[T](agents/T.md)、[覆盖](agents/COVERAGE.md)。小型原投影固定在`agents/coverage_snapshot`，逐端点派生JSON保留原bundle/验收路径与SHA。此目录不含Trace、巨大raw、Core补丁或启动脚本。SHA256SUMS记录本交付目录自身的小文件校验，不替代Main正式验收。
