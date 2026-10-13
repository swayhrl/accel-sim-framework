# Codex Goal｜AWMA科研价值再筛选（174-new，纯CPU）

日期：2026-10-13
项目：AWMA，独立于AI-ARCH Discovery的当前工作线
仓库：`swayhrl/accel-sim-framework`
阶段：`AWMA_CPU_RESEARCH_PRIORITY_REVIEW_174NEW_V1`
Handoff：`hrl/awma-cpu-research-priority-handoff-20261013-v1`
新执行分支：`hrl/awma-cpu-research-priority-174new-v1`

**唯一目标：不用GPU、模拟器或新模型，把AWMA的下一步选择收敛成清楚的科研判断。**

用户同意由174-new把既有R27R3数值证据判断、动态计算的数据准备研究和最小验证方案**合并为一轮**完成。不要为每篇论文、一个小文档或普通资料路径问题另开Codex轮次。完成后一次提交，STOP待AWMA ChatGPT科学审阅。

## 0. 阅读顺序、独立性和主问题

必须完整阅读本目录：

1. `START_HERE.md`；
2. `ACCEPTED_CONTEXT_AND_SCOPE.md`；
3. 本Goal；
4. `RESEARCH_CONTRACT.json`；
5. 仓库 `AGENTS.md` 的分支/来源/证据/报告规则。

以启动消息给出的exact handoff HEAD/tree建立**独立工作树**；不在AWMA旧执行分支上写文件。此次没有任何R27R4数值、R28 GPU、Accel-Sim或新机制授权。

### 研究组织

- **主线一：训练数值问题是否值得再投入？** 理解现有R27R3 B0/B0 25个元素失败给科研主目标带来的限制，判断是否存在清楚、有限、值得另行申请的小实验，而非默认继续排障。
- **主线二：动态计算的数据准备、结果交接是否留下真实开销？** 优先P06/P10：动态图邻居表、source/receiver遍历、执行计划、几何模型消费者，兼顾异构算子producer→consumer交接。必须把已由Kitsune、VTC、Sobek和ALCHEMI解决的能力视作强软件对照。
- **跨项目边界：GPU资源扩展规律P01/P13已交AI-ARCH Discovery**。本轮仅整理AWMA已有被审阅的相关事实和它们的证据局限，供另一窗口参考，不重复生成新的广泛资源扩展文献综述。

最后只选0—2个**仍有可证伪空间**的候选，其中“动态几何图的准备和交接”仅为初始优先对象，不保证一定合格。若没有，明确结论“目前没有值得立即启动的实验”。

## Gate A｜只读已有证据、去重与来源登记

### A1. AWMA数值研究

- 从独立接受的 `R27R3_B0_REFERENCE_REPEATABILITY_REVIEW_2026-10-13.md`及R27R3结果commit `7bd31fae4c54e121d54743a803d978ee02a64959`读其`B0_REPEATABILITY.json`、`FAILURE_COORDINATES.tsv`、`TOKEN_FREQUENCIES.tsv`、`PRE_DIAGNOSTIC_PLAN.json`及`NUMERIC_ATTRIBUTION.json`。
- 再按需查R27R2数值资格记录、R26实验结论。保持三个层次区分：两次B0存在原容差外差异；尚不知来自哪个kernel/归约；这种差异是否会造成训练质量问题或性能限制也未知。
- **默认不读取两份各约3.15GB node164原始`.pt`**，不复制checkpoint或权重到174，不做95/207/21项归档重复hash。若任何科研判断必须靠这些raw新计算才能成立，列出所需字段及理由，标记未完成，不在本Goal中擅自扩大预算。
- 有价值的CPU-only工作：复核25处异常是否全落在lookup参与的token行、row198单次/row284双次意味着什么、用原源码识别B0/C1/S2比较尚缺哪些分量证据；这不等于根因定位。
- 形成价值判断：R26仅多一个物理batch，B70整步峰值无优势，时间MIXED；为了这一点继续进行BF16 kernel非确定性分析的成本与可得到的科研结论是否匹配？如果没有独立于单batch收益的数值研究意义，建议暂存。

### A2. 动态图/交接研究去重

先从固定AWMA文献分支读：

- `docs/vm_tlb/literature_notes/awma/rounds/2026-10-02_ROUND_21_POST_R20_PROBLEM_DISCOVERY.md`
- `docs/vm_tlb/literature_notes/awma/empirical/ROUND21_SOURCE_REGISTER.tsv`
- `docs/vm_tlb/literature_notes/awma/empirical/ROUND21_EVIDENCE_AND_DECISIONS.tsv`
- 按需参考Round09、Round22中P06/P10/R20/R21相关段落，不全量重复。

固定旧结论：
1. Sobek与cuEquivariance已经减少/避免相当一部分中间张量；**不重做“等变卷积必须物化巨大边张量”的旧故事**。
2. Sobek存在双向遍历、source permutation、prepared graph缓存、图版本/shape/key；**不能假定每步或每层重建**。
3. ALCHEMI具备GPU邻居列表、cell-list、合法索引布局和重建/复用能力；**不能用朴素全对计算当唯一软件基线**。
4. 真实模型兼容、邻居更新事件、必要double-backward、几何帧时间语义、正确性与整段时间占比仍未资格化；这是本轮重点判别缺口。

### A3. 统一计划只读接口

从 `hrl/ai-workload-research-coordination`读取最新README、完整AI-ARCH Discovery交接、图谱P06/P10/P08/P09/P01/P13及跨项目证据索引。记录读到的协调commit；把它当导航而不是覆盖AWMA科学结论的authority。

AI-ARCH Discovery已负责P01/P13总文献调研。本轮不发布协调分支新提交、不给GPU建议直接执行、也不使协调分支成为AWMA的实验父分支。

## Gate B｜针对性论文与成熟实现调研：实际实验组而非摘要堆砌

**先看Round21来源登记和已有证据差在哪里，再回原论文/官方源码补缺口。**

优先四个研究对象，若有重要新近邻可替换或增补但需说明原因：

1. **Sobek**：`https://arxiv.org/abs/2607.18074`、`https://github.com/Cortex-Discovery/sobek`。区分fixed graph/varied graph、receiver/source排序与预备缓存、operator-only vs完整模型、前向/一阶/二阶求导、能力限制与输入分布。不要猜已有benchmark是否计入图准备。
2. **ALCHEMI Toolkit-Ops**：官方neighbor-list文档和2025/2026官方软件说明。它是源码/开发者资料，并非自动与论文同级的peer-reviewed实测；核查邻居构建、cell-list/cluster-tile、COO/matrix、预分配、reuse、兼容目标，且不能把作者H100数据当109数据。
3. **Kitsune**：`https://arxiv.org/abs/2502.18403`。以某个有明确输入/执行阶段的实验组检查GPU dataflow如何降低跨算子物理搬运/设备闲置，以及它未解决哪些动态几何拓扑问题。
4. **VTC（OSDI 2026）**：`https://www.usenix.org/conference/osdi26/presentation/hu-muyan`、`https://github.com/ADAPT-uiuc/VTC`。核查virtual tensor对数据layout/张量搬运的能力和强baseline，哪些转换已软件消除，哪些是必须构建的新拓扑信息。
5. **可选一个实际模型/几何输入来源**：MACE、NequIP、MD22等官方文档，首先确认应用模型、合法边、训练/力推理语义、source/consumer数据结构兼容、公开input是否真正有时间顺序。**不下载checkpoint/大型dataset，不冒充已实机跑过。**

**每一行`PAPER_EXPERIMENT_GROUPS.tsv`都是一组可定位的实际实验/案例**。建议4—6行来自至少3个相互独立的primary来源；如果论文正文/某个图表无法取得，记`NOT_VERIFIED`并减少合格行数，不为凑表格伪造。需要字段：

- 来源标题、年份、原文版本/URL、页码/表号/实验名、材料类型（论文/官方代码/文档）；
- 研究问题、真实/合成模型及输入、训练或推理与导数阶、GPU/平台、软件基线、变化变量和控制变量；
- 结果指标和分母（时间、内存、实际数据搬运、必要准备成本）；
- 作者实际报告的结果与范围；独立的“我们由此推断”；
- 原文明确没覆盖的场景、没有披露的项（直接写`未披露`）；
- 对AWMA的新颖性约束与可测试缺口。

禁止把论文作者数字复制到“本机测量”栏；不能由源码“支持某接口”推出实际端到端更快，也不能以operator-level加速估算完整能量/力加速。确认是否包含source preparation、模型推理或力的backward、GPU同步、有效输入等分母。

## Gate C｜只用证据筛选下一步，而不是先定机制

交付三份互相支持、篇幅克制的中文判断：

### C1. 训练数值方向价值判断

`R27R3_FURTHER_DIAGNOSTIC_DECISION.md`应回答：

- 现在**已经知道/还不能知道**什么；尤其25个元素分布并非已定位kernel。
- 最多提出一个真正有区分能力的未来GPU实验（若有必要）：明确比较哪个阶段或分量，使用已冻结输入和R26共同状态，具体指标、失败条件及计算/开发成本，不涉及改容差。
- 判断继续投入数值问题的科研收益是否足以匹配成本，并明确`继续但需另批`或`暂存`。没有足够研究价值就干脆建议归档，不为了把小实验圆满复现而耗时。
- 不将R27R2原数值STOP改称已经证明C1/S2错误，也不修改R26 accepted结论。

### C2. 动态计算的强软件之后还有什么

`DYNAMIC_HANDOFF_EVIDENCE.md`应完成：

- 以一个真实应用路径画清producer→数据结构/转换→consumer→输出/求导的**必要**信息依赖，标出证据级别。
- 区分强软件已解决的“邻居搜索”“融合/流式算子”“静态tensor view/layout转换”“prepared图复用”与剩余可能的“动态图必需再排序/双向索引发布/同步”。
- 明确竞争解释：准备被跨层/跨帧复用摊薄、只是错误使用API、真正耗时主要是必要搜索/算术、不同后端同语义本来更快，或确有剩余交接代价。
- 尽可能判断一个现成真实模型/合法几何输入能否**在不改变数学语义**的条件下接强软件做公平对照；如果不确定，列阻断项与最小CPU/API核查，不得宣称已能运行。
- 评价近期是否具有独立论文潜力，还是仍只是软件集成问题。不要假定“索引有两份”就是不必要冗余。

### C3. 最终科研决策与最小实验设计

`FINAL_RESEARCH_JUDGMENT.md`控制在可阅读的简明篇幅，明确：

1. 继续/暂存训练数值及理由；
2. 动态准备与交接最值得核的真实应用与最重要未知；
3. 从当前候选中挑**0—2项**（宁缺毋滥），每项用真实可证伪的科学问题表述，而非机制名称；
4. 对每项给出 `CANDIDATE_MINIMAL_TESTS.md`中的最便宜未来实验**设计（不执行）**：真实输入/模型身份、强软件baseline、一个主要变量、时间/容量/正确性指标及测量边界、两种相反解释、预计停止条件和**保留未用于选题的验证输入**；
5. 明确若完整路径不成立，如何止损/关闭；
6. 清晰说明为什么目前不授权109 GPU、174 Accel-Sim或某个新的硬件机制。

**GPU资源扩展规律P01/P13**：只产生不超过一页`AI_ARCH_EXISTING_EVIDENCE_NOTE.md`，指出AWMA已有翻译敏感度/模型失配、资源配置反事实等证据在何种范围有效、何种外推不行，以及可供AI-ARCH Discovery查阅的固定commit/文件。不要独立重新检索一整套NanoFlow、MPK及资源扩展论文，不与总研究线抢题。

## Gate D｜一次提交与清楚的最终结论

在一个新执行分支上形成：

`docs/vm_tlb/review_packs/AWMA_CPU_RESEARCH_PRIORITY_REVIEW_174NEW_V1/`
- `README.md`（统一入口）
- `FINAL_RESEARCH_JUDGMENT.md`
- `R27R3_FURTHER_DIAGNOSTIC_DECISION.md`
- `DYNAMIC_HANDOFF_EVIDENCE.md`
- `PAPER_EXPERIMENT_GROUPS.tsv`
- `CANDIDATE_MINIMAL_TESTS.md`
- `AI_ARCH_EXISTING_EVIDENCE_NOTE.md`
- `SOURCE_REGISTER.tsv`（标明论文/官方源码/已审阅结果/未获得材料）
- `SHA256SUMS`
- `OPEN_ISSUES.md`和简短验证记录（若有）。

本轮的final report：
`docs/vm_tlb/codex_handoff/awma/cpu_research_priority_review_20261013_v1/LANE_174_FINAL_REPORT.md`。

只保存论文出处/自己的结构化笔记/短摘录和项目证据引用；不得将整篇有版权的论文全文或大raw直接复制到Git。普通获取失败/目录变动可在合法源中另找正文并继续；无法证实的字段明确`未披露/未验证`，不以自动总结填空。

提交前：核对实际来源与版本、正确性/分母边界、报告中的限制、`git diff --check`、`SHA256SUMS`、显式路径stage（禁用`git add .`/ `git add -A`）；提交后push并fetch-back精确SHA/tree，确认worktree clean。无需创建节点164大型raw，也不重写AWMA文献或AI-ARCH协调分支（科学审阅之后才由ChatGPT同步）。

完成后**STOP**，报告最有价值的0—2个问题、是否需要任何进一步实验及其批准前提。不再自动开始下一项科研或运行任务。

### 资源与权限（绝对）

- **174-new：纯CPU文献/源码/轻量已有证据分析**；可合理并行互不冲突的只读工作。
- **禁止109 GPU/CUDA/JIT/Profiler/新的模型运行**；禁止Accel-Sim、无论旧还是新配置；禁止实验数据集/权重下载、完整复制6.31GB R27R3控制raw；禁止修改历史R26—R27R3实验结果、裁判容差、数据/源码或任何新机制。
- 研究计划与执行授权是两回事；本Goal只批准书面研究判断/证据整理，**不授权执行候选的最小实验**。
- 如果文献和既有证据不能支持任何有价值的实验，最终结果可以为`NO_QUALIFIED_CANDIDATE_YET`，这不是工程失败。
