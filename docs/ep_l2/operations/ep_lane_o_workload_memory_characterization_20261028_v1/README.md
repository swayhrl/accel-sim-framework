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
| [V1R2计量合同](MEASUREMENT_CONTRACT.md) | ingress/queue/head/admission、同人口分母、ready/retire与统计状态 |
| [V1R2路径NI矩阵](NI_MATRIX.md) | 新统计各路径的资格要求；未准备新Core/ELF，不继承旧NI |
| [四候选输入缺口表](PILOT_GAPS.json) | Scan、Conv、FWT、Vector6M现有数据与缺口，非启动清单 |
| [给Main的交接文字](MAIN_HANDOFF.md) | 可直接转发的范围、接口与最小回包要求 |

## 核心事实

- Main快照为北京时间2026-10-28 18:30:57：214个accepted点，22个REF S/F输入配对；主35中25个输入至少有一个accepted点。其后新结果不自动加入此固定报告。
- scan参考S：WBUF峰16、均值10.661；1,737,618个独立请求遇WB_DATA_SPACE，对应49,938,625次检查。Conv有16,791个同址WB独立受阻请求。已有MS等待统计应直接复用。
- 当前23个F参考端点中10个有V读响应、13个为零；FWT WV存在3,312次dirty-forward。它们证明服务事件，不直接给出victim命中率或所需容量。
- Vector约75%的RO requester合并到存活事务，严格fill前重访比例仍未知。Conv普通MSHR满载与SGEMM同址chain上限是不同现象。
- Conv已测同Set满路preview压力；当前接受点中Conv 16×8和32×4分别实际detach **237/1,141** 次，Vector4M 32×4为**27**次。缩容点完整F均慢于相应S；没有同背景F−T/F，不能声称T的独立正负收益。
- 历史Motivation已有reuse distance及post-eviction统计；Streaming prefinal已揭示空间sector触达与真正时间复用的区别。应先补历史小CSV/manifest索引，不重复扫描大Trace。

后续先由Main核对已有小汇总和PILOT_GAPS，确定基点与确实缺失项；如需工程，再使用独立候选分支。pilot与全代表补采均未启动，不在本轮注册预算。

## V1R2 审查问题已落实

- **边界固定**：真实入口、入队、first-head与准入分开；旧head数据不回填入口重访。
- **百分比收窄**：Conv/Scan 22份小JSON没有找到absorbed类别投影；撤下尚未证明同人口的精确受阻发生率，原始计数不变。
- **NI按路径核对**：撤销固定4 ON+1 OFF足够的假定；新Source/ELF、S/F/WV路径资格均未由Lane O准备或通过。
- **可交接**：新增计量合同、路径矩阵、四输入缺口表及Main交接文字。旧214点冻结分析和25/23/30等各统计人口不刷新，Main新接受点不自动混入。

落实记录和本次QA在[revisions/20261029_v1r2](revisions/20261029_v1r2/RESOLUTION.md)。本轮无仿真、构建或Core改动，也没有替用户向Main发消息。

## V1R1 只读复审修订（不新增科学运行）

本次仅在独立Lane O文档分支补齐审查意见，**原始冻结统计投影和Main实验接受状态不回写**；报告时点仍固定于2026-10-28 18:30:57（北京时间）。

- **T证据补全**：补录同一冻结接受人口中的Conv 237/1,141次实际detach及匹配S/F cycles，保留Vector27和没有T独立因果对照的边界。
- **首批观察加入Scan**：与Conv、FWT、Vector6M组成互补输入。此版曾暂定4 ON+1 OFF；该固定足够假定已由V1R2路径NI矩阵取代，不再作为当前点数依据。
- **分开S/F观察**：S用于地址复用、WBUF/WAD、普通MSHR及Tag需求；F/WV用于实际Victim、RO、Detach与联合机会；禁止跨模式拼接事件或把F机制行为叫作程序固有特征。
- **四条论文主观察**：按W、V、M、T四项资源需求组织，原O1–O8保留为证据条目而非八个并列贡献。

原 `REPORT_QA.json` 的PASS仅对应Lane O第一阶段文档/数据一致性检查；本次修改未开展仿真、实验重验或额外Trace扫描。新的文件内容SHA列于同步更新的 `SHA256SUMS`。所有新增采集仍由Main在独立资格和预算确认后决定。

## 保存与审计

本地：`D:/repo/ep-l2-lane-o-20261028`。

远端：`hrl-174-new:/root/workspace/ep-l2-lane-o-20261028`。

以上保留第一阶段冻结副本；V1R2独立工作副本为本地`D:/repo/ep-l2-lane-o-v1r2-20261029`及远端`/root/workspace/ep-l2-lane-o-v1r2-20261029`。Git分支当前文档以V1R2为准。

Agent附录：[W](agents/W.md)、[V](agents/V.md)、[M](agents/M.md)、[T](agents/T.md)、[覆盖](agents/COVERAGE.md)。小型原投影固定在`agents/coverage_snapshot`，逐端点派生JSON保留原bundle/验收路径与SHA。此目录不含Trace、巨大raw、Core补丁或启动脚本。SHA256SUMS记录本交付目录自身的小文件校验，不替代Main正式验收。
