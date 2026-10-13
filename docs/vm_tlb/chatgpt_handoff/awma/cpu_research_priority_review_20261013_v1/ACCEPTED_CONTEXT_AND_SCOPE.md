# AWMA 下一步科研审查：已接受证据与分工

日期：2026-10-13（Asia/Shanghai）

性质：174-new的**纯CPU资料研究交接**。不是R27R4，不重新启动R27R3，不产生任何109 GPU、Accel-Sim、模型下载或新机制授权。

## 1. 本次科研问题

用户同意把AWMA从反复尝试微小容量收益转向更有研究价值的问题发现。合并完成三件事：

1. **数值方向止损判断**：只读R27R3已有B0控制及R27R2历史证据，判断是否值得另立一次小规模原生数值归因问题；不预设继续投入。
2. **AWMA近期重点：动态计算的数据准备与交接**，尤其P06（跨算子handoff）和P10（动态图拓扑就绪）。先对照过去AWMA Round21已有源码事实和成熟软件/论文，核查是否真的存在尚未被解决的必要代价。
3. **最少研究问题**：最终仅保留0—2个有真实应用对象、明确竞争解释、强软件基线和最小证伪实验的候选；不为凑数量制造机制。

## 2. 已接受的AWMA科学证据

- R26执行 `1a2485011b300cddd5137bbccb91dd6d30cfc22f`；独立review `097c2b6ed7905480ed72679f0cc79865087ae3c9`；R26在**复制同一序列的tied-W-only完整五步训练**中有C1 B70 PASS/B71 OOM、S2 B71 PASS/B72 OOM、四端点3/3；在B70 S2整步峰值高3.828 MiB，正式计时没有稳定加速。只是一物理batch窄范围容量差，不是可推广显存收益。
- R27、R27R1均因新输入不可获得STOP；之后的字节身份问题已解决。
- R27R2执行 `ba73fa0bacf3db09f44d8ad421a0a36f56645898`；WikiText-2 raw train exact parquet `6,357,543 bytes`/SHA256 `e83889baabc497075506f91975be5fac0d45c5290b6b20582c8cd1e853d0c9f7`合格；前540,672 token构成`[33,128,128]` CPU int64 bank，raw SHA256 `7ad359882a1a7153cd7c0d9321af53ac38fa17908cff1355a89696aec2c61387`；B1四步C1/S2总梯度对B0全部未过冻结数值合同，没有多样输入容量结果。
- R27R3执行 `7bd31fae4c54e121d54743a803d978ee02a64959`，tree `bcd3a9ab5890a946d03a49b46df4434abff4238c`；独立审查 `d6e9bbfb562814bcd5dc5adb444d3c572e7f446b`；最新AWMA状态 `f0a6ec310c09cd011fffbe8a5ca22d6effacdf6b`。两个相同输入/状态/B0 fresh processes，完整BF16总梯度`262,668,288`元素中25处超`atol=rtol=1e-2`；12处在行198、13处在行284，最大超限坐标(198,604)差0.09375、上限约0.06406；其余观测通过。B0参考重复性未达到冻结门槛，**不证明B0数学错，也不证明C1/S2对错，未查内核根因**。R27R3在此STOP，无组件归因、修正或容量观测。
- R27R3 review pack: `docs/vm_tlb/review_packs/AWMA_R27R3_NUMERIC_ATTRIBUTION_CONDITIONAL_CAPACITY_109_V1/` at exact execution commit；reviewer独立核了Git pack 20/20 SHA与25坐标，但未SSH重读node164两份各约3.15 GB完整原始控制张量。禁止把节点readback receipt升级成174或ChatGPT再计算的证据。

## 3. AWMA已做过的非LLM研究，禁止重做

- `docs/vm_tlb/literature_notes/awma/rounds/2026-10-02_ROUND_21_POST_R20_PROBLEM_DISCOVERY.md`：动态几何图的producer→consumer就绪是有源码事实支撑的**待测科学问题**，没有新的native实测；已排除“等变卷积巨大逐边中间张量必需物化”的旧动机（Sobek等已有强软件）。
- 同目录的 `../empirical/ROUND21_SOURCE_REGISTER.tsv` 与 `ROUND21_EVIDENCE_AND_DECISIONS.tsv` 保存Round21原文/源码证据级别。Round21已指出Sobek有sorted/CSR、source/receiver双向遍历、预计算与缓存接口，不代表每帧都重新排序；ALCHEMI已有邻居搜索、COO/matrix格式及合法复用，不能假设GPU近邻构建未优化。
- `docs/vm_tlb/literature_notes/awma/rounds/2026-09-27_ROUND_09_BROAD_SIDE_RESEARCH.md` 与Round22证据账本记录旧研究背景；按需读相关范围，不全量重复纸面审计。
- C16已对一个FFN双流gate/up方案得到负面净时间，不能重复用相同FFN作新发现；也不能以该结果否定所有异构生产者与消费者。

## 4. 最新跨项目协调边界，防止重复任务

AI-ARCH是统一研究计划，独立Discovery窗口负责P01/P13“GPU瓶颈随负载/阶段/资源规模变化”的广泛原文阅读和跨负载研究设计。

协调分支 `hrl/ai-workload-research-coordination`，本次写作时已核到HEAD `4e5953c189792dd5a4ac5c13c33ba922b8c2a1e9`；优先读：

- `docs/ai_workload_research/README.md`
- `AI_ARCH_DISCOVERY_HANDOFF_CONTEXT_2026-10-13_V1.md`
- `AI_WORKLOAD_ARCHITECTURE_PROBLEM_ATLAS_V1.md` 的P06/P08/P09/P10/P01/P13
- `AI_WORKLOAD_C16_AWMA_EVIDENCE_INDEX_V1.md` 的E-A11/A12/A13/A14、E-C08/E-C09、E-L02/E-L03/E-L04
- `COORDINATION_PROTOCOL.md`。

**AWMA不另行做一份P01/P13大范围论文综述。** 本轮只从已有AWMA模拟器/本机历史结论写不超过1页的可复用事实/限制清单，供AI-ARCH Discovery参考；不直接修改协调分支，也不在本次CPU Goal下发行GPU任务。

## 5. 第一批外部来源（要求回原文实验组核实，不是已测结果）

- Sobek：`https://arxiv.org/abs/2607.18074`，`https://github.com/Cortex-Discovery/sobek`。查其容量匹配的forward/backward/double backward组是否包括动态graph准备成本；不能把算子级收益当完整模型加速。
- NVIDIA ALCHEMI Toolkit-Ops邻居表：`https://github.com/nvidia/nvalchemi-toolkit-ops/blob/main/docs/userguide/components/neighborlist.md`，`https://developer.nvidia.com/blog/accelerating-ai-powered-chemistry-and-materials-science-simulations-with-nvidia-alchemi-toolkit-ops/`。已有邻居构建、合法格式和复用；源码能力和作者benchmark不等于当前109净收益。
- Kitsune：`https://arxiv.org/abs/2502.18403`。已公开GPU dataflow执行方案，查具体模型、输入、对照和支持范围。
- VTC（OSDI 2026）：`https://www.usenix.org/conference/osdi26/presentation/hu-muyan`、`https://github.com/ADAPT-uiuc/VTC`。已实现虚拟张量消除部分数据移动；重点区分索引映射与真正图拓扑/动态数据就绪。
- 必要时补一个真实几何模型及输入的官方来源，如MACE/NequIP或MD22，但只做source/interface与数据许可/适用性研究，**不下载训练模型或数据集**；尤其确认模型对Sobek的连接结构是否兼容和MD22帧序是否可视为时间序列。
- 文献正文/图表若无法合法取得，写`未获取/未披露`，不以摘要或二手总结代替该实验组完整证据。论文作者数字只用于其实际实验组，不能转成RTX4080估计。

## 6. 证据级别与禁止事项

- 仅Git源码：`SOURCE_ONLY`；作者论文实验：`PAPER_AUTHOR`；已接受原生结果：`ACCEPTED_NATIVE`；模拟器：`SIM_SCOPE`；构想：`HYPOTHESIS`；未核：`UNKNOWN`。
- 未得到原始数据时不得写“独立重算”；负面/STOP仅在原冻结条件成立，不能推广领域无问题。
- 全任务CPU-only；不SSH到109启动程序，不提交GPU/Accel-Sim Goal，不重启R27R3、不发新模型下载，不修改C16、AWMA历史或AI-ARCH协调的现有执行权限。
