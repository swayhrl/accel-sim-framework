# AWMA 下一步科研优先级｜174-new Lane E 独立审查

审查日期：2026-10-13（Asia/Shanghai）

执行任务：`AWMA_CPU_RESEARCH_PRIORITY_REVIEW_174NEW_V1`，由174-new Lane E执行，定位为CPU资料/源码与既有紧凑证据分析，不是性能实验。

执行分支：`hrl/awma-cpu-research-priority-174new-v1`。

执行提交：[`2de1daee9bcdac4b85ca6a6abd511d0ad5683b6f`](https://github.com/swayhrl/accel-sim-framework/commit/2de1daee9bcdac4b85ca6a6abd511d0ad5683b6f)，tree `06080a03da26a50812962ff5176f31d2c1fe51e5`。唯一直接父提交为冻结handoff `e32c47d4b54dac25bce94cc8020657e8932f3d26`（tree `8a5eb49d7de8ff2e3ec78f2f7caaac110d5ba947`）。

[本轮完整证据包](https://github.com/swayhrl/accel-sim-framework/tree/2de1daee9bcdac4b85ca6a6abd511d0ad5683b6f/docs/vm_tlb/review_packs/AWMA_CPU_RESEARCH_PRIORITY_REVIEW_174NEW_V1)。

## 独立科学决定

**接受 `NO_QUALIFIED_CANDIDATE_YET`，0个当前值得立即启动的已资格化研究实验。** 接受的是科研筛选结论，不是“该领域不存在瓶颈”的负面测量。研究方案与工程交付本身已完成，可以STOP，不再自动下发174或109新任务。

两项分开：

1. **训练数值：建议暂存。** 已接受R27R3在固定B1、固定WikiText输入上，两次原生B0的完整BF16总梯度有25/262,668,288元素违反原`atol=rtol=1e-2`逐元素合同。本轮只独立核对公开坐标、token频次、相关已冻结源码，没有读取node164两份完整张量，没有执行GPU。现有证据不能定位具体kernel，不能证明B0数学错误，也不能判断训练质量/收敛。R26窄范围重复序列1物理batch容量优势不变，B70完整步峰值S2略高、时间mixed；目前缺乏单独值得投入数值排障的训练质量或容量收益。
2. **动态计算准备/交接：保留一个`FUTURE_ONLY`问题，不进入运行名单。** 科学问题是：在合法邻居搜索、复用、最强可兼容网络计算之后，真实几何拓扑更新要求的索引转换、双向遍历和执行计划发布是否仍消耗显著完整能量/力时间？尚缺实际模型的相同数学语义接入和可信自然更新输入，不可通过模拟每帧重建或使用低效接口制造优化空间。

`0个立即可运行候选`不等于`0个值得保存的科学问题`；保留的条件性设计不构成授权。

## 论文与强软件原文复核

本轮表`PAPER_EXPERIMENT_GROUPS.tsv`共有**5个论文实际实验组（来自3篇）+1个官方API能力案例（不计性能组）**。审阅者直接在公开原文核对下列重要事实；论文作者数字**不升级为本机测量**：

- **Sobek v1** [原文](https://arxiv.org/html/2607.18074v1)：RTX5090/fp32，容量匹配的OpenEquivariance算子比较、合成图degree和graph count变化；其§5.1明确**编译、图生成、图准备均排除计时**，不能拿算子级内存/吞吐推完整真实力推理的索引准备代价。§5.4 Table3所记32/16/16 profile前向/反向/二阶4.52/1.37/1.73x均与原表一致，代表不同B上限、不同导数阶，不是统一训练步或端到端收益。
- **Kitsune v1** [原文](https://arxiv.org/html/2502.18403v1)：MeshGraphNets训练Table2确为148 operators、Kitsune可合并108、预计内存流量减少40.26%。应用性能采用修改后的NVArchSim模拟A100级GPU；独立硅片测量主要用于其队列原语。这一结果证明相关dataflow/producer-consumer机制已有近邻，**不是RTX4080真实动态图力计算净收益**。
- **VTC OSDI2026** [原文](https://www.usenix.org/system/files/osdi26-hu-muyan.pdf)：§7.5 Table3强vLLM decoder-layer组A100: 9.152→9.055 ms，H100默认4.230→4.230 ms，强制一种映射则4.230→4.600 ms；同时subgraph A100 1.972→1.890 ms。说明在有高效计算kernel时，减少物理数据移动也可能无益或变慢。§7.6 YOLOv11 C3K2与Fig9是静态layout交接示例，不会自动解决新的几何邻接关系生成。
- **ALCHEMI** [官方固定源码/文档](https://github.com/NVIDIA/nvalchemi-toolkit-ops/blob/32445c5f00e83fccd475589f1a6f5ac9e81e6b02/docs/userguide/components/neighborlist.md)：已经提供不同邻居构建方法、COO/matrix、容量输出、rebuild/reuse等。它是必要的强软件能力对照，但Lane E没有取得同一NequIP模型完整力推理的ALCHEMI vs Sobek实测；G06明确不是性能实验组。

这些核查支持把“普通融合、虚拟张量、边中间物化、简单邻居搜索”视为强软件已经处理或部分处理的领域；**不构成已经测到的硬件残余瓶颈**。

## 源码与实际模型兼容性

Lane E先复用了已接受AWMA Round21的图准备研究，而非重复旧综述。本审阅环境额外读取了固定原生源码：

- `Cortex-Discovery/sobek@c1f815bfee1de420342c7b660fb2b1f9eab2441e`的`tpconvproblem.py`：`uvu`路径要求输入/输出各角度段共用multiplicity；`irreps.py`拒绝同一`(l,parity)`重复段。
- `mir-group/nequip@27d9d2182da918ab7be0017d8300e53278f5e00e`的`interaction_block.py`：历史NequIP模板会逐coupling生成`uvu`中间表示、排序并交给后续线性层；这不等于当前实际模型已经得到Sobek兼容的完整问题描述。
- Lane E读取了node164已接受OAM-S包中一个20,996-byte `config.yaml`文本，报告其SHA与原authority一致，配置指向`ModelFromCheckpoint`，却**没有提供展开的每层TPProblem**。本ChatGPT环境没有直接SSH核该zip成员，故这一点是执行侧的限定收据。

因此能够接受的是**存在明确接口约束，当前OAM-S直接替换Sobek尚未证明可行**；不能扩大为所有NequIP模型必定不兼容，亦不能自行修改模型数学表达式后称同语义A/B。

自然几何更新也是另一未闭合前提：已有110个周期性Si帧、独立帧正确性资源，但未证明它们的文件顺序是可信物理时间顺序；不能推邻居表重建频率或跨帧摊销。保存的frame101/107只有条件性候选身份，当前不是已认定holdout。

## 条件性未来验证，仅设计、不执行

若未来要重新评估动态准备方向，应先由独立CPU/源码资料证明**一个真实已训练模型**与强后端同语义兼容，且存在合法自然图更新事件和可信输入时间关系；无法闭合则直接关闭该实例。

一旦前提成立才考虑新的科学合同：固定一个模型和实际rebuild事件，用最强现成软件路径与“同帧拓扑已准备”的诊断对照，**两个对照均保留必要邻居搜索**，计时从本帧GPU数据就绪直到energy与force完成，包含长度校验、索引发布、同步和必要一阶求导，不偷换二阶训练算子；保留独立验证输入。无显著净成本、合法复用摊薄、现成API足够、另一合法后端更快或只有昂贵移植才可测试，则结束。

不建议为了R26一个batch收益默认开展新的B0内核数值归因；只有获得独立训练质量/资源约束动机，才可能另批小范围观察。

## Git完整性与审查局限

- 独立核验Git exact execution SHA、tree、handoff parent及远端执行分支；相对handoff仅新增本轮CPU资料判断、表格、审查脚本和报告。未修改历史实验代码。
- 独立逐文件SHA256核对`SHA256SUMS`的**18/18项**（包括17个review-pack文件及1份最终报告）全部一致；`SHA256SUMS`自身SHA256为`4efbd711439743afe4f9593936ef97a99abd9b00ade19baf38f3b20fbd31a209`。该文件本身不在索引里，review pack总文件数18。
- 验证表记录19列6组数据、source register20行、原始索引7行、0个运行候选；条目均已与结构化文档检查结果相符。审阅者独立读取了紧凑结果并交叉核原论文/部分原生源码，**没有**通过node174独立运行全部资料提取，也没有亲自连接node164重算zip与旧control raw。
- Lane E报告GPU/CUDA/JIT、Accel-Sim、新模型和性能实验均为0，用户已确认它在174-new；本审阅环境无法独立监视现场任务和worktree clean，这些维持执行侧声明。

## 下一步与跨项目分工

AWMA当前没有新的174/109正式实验任务。AI-ARCH Discovery已负责P01/P13“GPU资源随模型/负载/阶段变化”的宽范围论文与科学规律工作；本轮`AI_ARCH_EXISTING_EVIDENCE_NOTE.md`已将AWMA既有翻译服务和模拟资源证据的适用范围整理为一页，供协调线查阅，**不是新实验结果**。

建议接受本轮科研止损，不再为“必须有下轮”分配GPU/模拟器时间。新问题应由真实应用/论文/源码证明其必要代价、强基线、单变量可证伪实验后再独立提交批准。旧R26–R27R3的所有独立接受结果及DTC-L1/ISCAS项目均不变。
