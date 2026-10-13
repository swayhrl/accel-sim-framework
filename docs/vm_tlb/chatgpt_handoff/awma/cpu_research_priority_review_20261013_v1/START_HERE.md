# START HERE｜AWMA 174-new下一步科研选择（仅CPU）

日期：2026-10-13（Asia/Shanghai）

Stage：`AWMA_CPU_RESEARCH_PRIORITY_REVIEW_174NEW_V1`

Handoff branch：
`hrl/awma-cpu-research-priority-handoff-20261013-v1`

新执行分支：
`hrl/awma-cpu-research-priority-174new-v1`

请按启动消息给出的**exact handoff HEAD/tree**建立新的独立worktree，不能从旧R27R3执行分支直接继续，不修改旧AWMA历史。

必读（依次完整阅读）：

1. `ACCEPTED_CONTEXT_AND_SCOPE.md` — 已接受的R26–R27R3边界、Round21旧证据与跨项目分工；
2. `RESEARCH_CONTRACT.json` — 本轮权限、必要交付与停止边界；
3. `LANE_174_CPU_RESEARCH_GOAL.md` — 单轮全部研究工作；
4. `AGENTS.md` — 仓库通用文档/提交纪律；
5. 最新 `hrl/ai-workload-research-coordination` 上的README、AI-ARCH交接、图谱P06/P10/P01/P13和协调规则，**只读**。

### 一轮解决三件事

- R27R3数值证据：判断是否值得另行申请进一步定位，或者暂存；
- P06/P10动态计算数据准备与交接：查Round21之后尚未解决的真实应用兼容性、成熟软件baseline和必要开销，对原始论文具体实验组重新核实；
- 科研选择：仅0—2个值得继续的问题，每个给出最小可证伪实验**设计**，不运行。

**P01/P13 GPU资源扩展规律的广泛调研现由AI-ARCH Discovery负责。** AWMA本轮仅提供不超过一页现有实测/模拟证据与适用范围，不另做重复综述。

### 资源红线

这是**纯CPU文献与已有证据分析**。不得：
- 启动109 GPU、CUDA/JIT、NCU/NSYS/NVBit、任何模型计算；
- 运行174 Accel-Sim/模拟器、重做旧C16 Stage A、R27R3或完整raw审计；
- 新下载模型权重/实验数据集或复制node164大型训练控制张量；
- 修改AWMA旧实验或AI-ARCH协调分支；
- 根据研究判断自动启动候选的任何最小实验。

普通文档、资料访问、报告包装问题在同一Goal内解决并继续。若缺少原文、独立验证或有效输入，明确写“未披露”“未验证”及后果，不能伪造细节或转为性能结论。

交付一份中文简洁、证据充分的科研判断及结构化来源表；commit/push/fetch-back SHA/tree、clean worktree后STOP，提交给AWMA ChatGPT独立审核。
