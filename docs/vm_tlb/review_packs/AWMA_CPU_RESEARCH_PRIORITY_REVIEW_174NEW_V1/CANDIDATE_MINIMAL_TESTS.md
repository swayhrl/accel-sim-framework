# 最小可证伪设计与准入状态
当前 shortlist = **0**。没有 READY_FOR_GPU 的设计；以下只保存一个动态路径的**条件性设计**，避免后来再用弱基线或错分母。数值线唯一条件性 observer 设计已在独立文件说明，建议暂存，不在本名单再登记。

## 条件性问题 D（FUTURE_ONLY / BLOCKED_COMPATIBILITY_AND_INPUT）
科学问题：强软件合法复用之后，真实拓扑更新所需的格式/双向索引/执行计划是否仍给完整能量/力路径带来稳定净成本？相反解释是准备被共享摊薄、主要时间是必要搜索/算术，或成本只是 API 使用/后端选择问题。

**真实身份入口**：原 OAM-S:0.1 package SHA `63d4bafd…407aa`，sitraj 原文件 SHA `c08d3771…3e770`，旧 frame55 只作已知 development canary，r_max=4.5、64 Si、周期 image 完整。这不是新 holdout，不将这些独立帧顺序当时间。当前 Sobek 接入未资格化，所以此身份不能自动转成 Sobek 实验。最便宜先验检查是读取现有 package 的每层 TPProblem/最后径向线性层/归一化 metadata，逐项映射到固定 Sobek 合约；config.yaml 的 existing checkpoint 引用不足以证明这项映射。若必须改网络表达式或构造大零填充 uvw，停止该实例，不扩大移植。

**强基线**：同一真实 model 的最快合法公开消费者（原已接受 OEQ atomic/compile、能保持 task contract 的 cuEquivariance/Sobek，仅兼容后才入组），配合法 GPU neighbor 方法、预分配、合法 skin/rebuild、跨层共享。不可规定每帧重建，也不可为了 sort 问题要求任务原本不需要的确定性。

**唯一主要诊断变量**：同一已确认的自然 rebuild 帧，Bstrong 正常在线索引/计划准备，Dready 以同帧 exact topology/索引/计划已就绪开始 consumer。两臂保留完全相同的邻居搜索（其结果都在计时内产生）、当前几何特征、网络和力求导。Dready 是 prepared-state 诊断；为它预构的缓存/布局/分配状态需要记录，不能称部署收益或严格上界。若公开 Spublic API 已合法免去额外转换，应作为 Bstrong 本身，不能另立弱对照。不得将邻居搜索也一起移出 Dready。

**必要成本及分母**：GPU-resident 本帧 coordinates/species/cell/PBC 就绪→energy 与 force 完成，同一同步端点。计入 neighbor/rebuild判断、长度/溢出处理、int32/int64/边方向、CSR/置换/plan、分配与发布、当前 SH/径向、模型前向和一阶求导；observer 分类每项，但不相减并发 kernel duration 冒充分量 wall。另报完整区间、准备区间、分配峰值、版本/缓存命中、边数/容量及非目标网络区间。共享/跨帧成本只按确证 chronology 计费。

**数值/离散合同**：原子 ID、有效有向边+periodic shift multiset、cutoff/self-edge/PBC 规则、容量无漏边/溢出严格一致；当前边几何需正确 autograd。OAM 实例沿旧能量/力 `atol=rtol=5e-5` reference 检查，不改容差；比较任务级输出与坐标梯度，不能把算子 algebraic 等价当部署通过。力推理不加训练 double backward。若原强 baseline 重复性不合格，停止比较。

**最小未来预算与停止**：一个 model/一个 admitted rebuild 事件，预冻结 balanced 两组各 8 paired observations（每臂固定 warmup），完整 raw 全保留；不是参数扫描。只有两组完整区间方向一致且超过事前 noise rule，局部准备信号和 correctness 都成立，才值得审阅后扩大。无 rebuild 事件、准备被复用摊薄、Dready 差异落入噪声、另一强 backend 已消除、主要搜索/算术占主导、或只有重型改模型才可比较，直接关闭。噪声合同、软件版本、强臂选择在看时延前另批冻结；本轮不发执行 Goal。

**独立验证保留**：本轮不读取 sitraj frame101/107 的几何，可作为未来独立帧候选；必须先核旧使用 ledger、冻结逐帧 SHA 和模型适用性才获得 independent status。两帧不能替代 chronological trajectory。若要研究自然 update frequency，需另有公开时间索引与对应同模型适用域，当前为 UNKNOWN；不自动下载 MD22 或新增采集。

**本轮止损**：上述兼容性与自然更新前提尚未闭合，故不进入实验名单。原 R21A/R22 仍关闭；该设计不能作为续跑凭证。
