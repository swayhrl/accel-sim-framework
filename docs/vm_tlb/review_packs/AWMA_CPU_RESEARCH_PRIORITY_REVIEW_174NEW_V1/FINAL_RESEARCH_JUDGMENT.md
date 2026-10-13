# 下一步哪些研究真正值得做
**建议暂存训练数值支线；本轮保留 0 个已资格化运行候选。** 动态几何图的准备/交接仍是最具体的后备问题，但目前应停在真实消费者兼容性与输入更新语义的缺口，不发 GPU 或硬件任务。

## 数值方向：有资格问题，尚无独立科研收益
R27R3 原控制的完整梯度门失败成立。本轮只复核 Git 公布的 25 个坐标及 token 频次，没有读取两份 3.15 GB 张量。row198 输入一次、无 label；row284 输入两次、label 两次。这既不能定位 embedding backward，也不能否定 classifier/上游微小扰动/总梯度合并的解释。其余冻结观测通过，不等于长期训练质量已证明。参见 [数值价值判断](R27R3_FURTHER_DIAGNOSTIC_DECISION.md) 与 [CPU 收据](NUMERIC_COORDINATE_RECHECK.json)。

R26 保留一物理 batch 扩展的 accepted 结论；共同 B70 整步峰值略高，正式时间 MIXED。当前没有训练质量、稳定性能损失或广泛容量收益说明继续定位 BF16 非确定性会产生独立科学结论。只为恢复小容量实验而继续排障，投入与已知收益不匹配。

## 动态方向：边界具体，但运行前提比“还有排序”更重要
原文补核确认：Sobek 的实际评估排除 graph generation/preparation；这使完整应用准备成本保持未知。不能由排除项推导显著 headroom。Kitsune 已研究数据流执行，但关键结果含调度器扩展的模型；VTC 的强 vLLM 组同时给出正、零和强制优化退化，说明保留快计算内核不可省略。具体组和分母只在 [实验组表](PAPER_EXPERIMENT_GROUPS.tsv) 登记。

本轮新增的阻断证据是 **OAM-S→Sobek 不能当作现成同语义接入**：固定 NequIP source 的中间 irrep/path 结构与 Sobek 校验规则不同；官方 OAM-S 页另描述异构 128/64 特征，本轮读到的 accepted package config 仅引用 checkpoint，仍未提供展开的每层 TPProblem。ALCHEMI 的拓扑格式、skin/rebuild、预分配/复用是必须采用的强基线，其 borrowed buffer 生命周期与 Sobek immutable prepared graph 也需显式协调。[完整路径与兼容表](DYNAMIC_HANDOFF_EVIDENCE.md)。

有真实图更新且同模型强实现兼容之后，最值得证伪的问题才是：**已经采用合法复用的完整能量/力路径中，更新事件的双向索引与计划发布是否仍产生稳定净成本？** 这张问题卡目前为 FUTURE_ONLY，未进入运行名单。预备缓存、必要搜索/算术、普通 API 集成、另一后端更快均可否定它。

## 科研与止损
[最小设计](CANDIDATE_MINIMAL_TESTS.md)只保存一个条件性动态路径对照；数值定位设计另见数值价值文件，当前建议暂存，二者均未获准执行。已有 sitraj 文件可供独立帧正确性，但其顺序没有时间资格；MD22 loader 也不证明数组行序是 MD 时间。没有真实更新输入，不能报告 rebuild 频率或跨帧摊销。

若同语义接入需要改网络连接/权重/导数，或主要成本由合法复用/现成软件吸收，应关闭该实例。若将来观察到净成本，再判断是否为软件集成成果及是否有最近邻差异；目前没有独立架构论文主张。P01/P13 广泛调研继续由 AI-ARCH Discovery 负责，本轮只交 [一页旧证据](AI_ARCH_EXISTING_EVIDENCE_NOTE.md)。

本轮信息增量：确认计时边界、找到消费者接口阻断项、区分原控制失败和科研价值。科学审查可据此接受“暂不启动实验”，无需为产生下一轮而降低准入条件。
