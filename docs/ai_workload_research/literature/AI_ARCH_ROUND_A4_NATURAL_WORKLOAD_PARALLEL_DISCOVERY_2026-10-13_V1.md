# Round A4｜跨负载自然场景选样与并行科研核查（第一阶段）

**执行者**：ChatGPT／AI-ARCH Discovery（总体科学判断），Codex Lane T／174-new CPU-only（训练源审），Codex Lane N／174-new CPU-only（非LLM输入与消费者源审）  
**状态日期**：2026-10-13。**此文件是并行执行准备和ChatGPT先行证据，不是Codex已经启动或完成的报告。**  
**科学状态**：`ROUND_A4_SOURCE_DISCOVERY_IN_PROGRESS`，**三个family均无新native/模拟/机制晋升权**。

## 0. 本轮为何从旧Split-K/FFN转向新的自然family

[Round A3正式决定](AI_ARCH_ROUND_A3_HISTORICAL_EVIDENCE_CLOSURE_AND_CANDIDATE_ADMISSION_2026-10-13_V1.md)：原W4 Split-K的M/split反转是可信的局部现象，但规模变化并非“独立任务供给”单变量，GROUPED已经回收主要cache局部性；FFN gate/up直接双流性能为负，分块的tile-ready DAG未资格化。两题均未达到新原生机制准入。因此不能仅因为已有C16资产而重做封闭扫描。

本轮三类**备选自然family**：多GPU训练MoE、真实几何/等变非LLM、真实长度分布的LLM混合Prefill/Decode服务。均按：准确模型/输入身份→强软件→实际阶段与任务ready变量→可比较时间/容量分母→最近邻反例→最便宜下一步与STOP 研究，不由下载库存反推。

## 1. Family T（训练）：MegaScale-MoE多GPU扩展

### 已可确证的作者原始证据

- 主来源：[MegaScale-MoE EuroSys 2026／arXiv HTML 2505.11432](https://arxiv.org/html/2505.11432)，§6.1 Table3/§6.2 Table5，原文有EuroSys'26 DOI 10.1145/3767295.3769325元数据。
- 使用内部352B MoE（非公众可直接下载的完整checkpoint），seq8192、vocab65536、global batch720，PP=15，240/480/720/960/1440张H800作**强扩展实机训练**。MegaScale-MoE相对Megatron-LM的吞吐比约1.65–1.88×；作者说明增加GPU时每条pipeline microbatch数减少，pipeline bubbles增多，MFU从32.48%降至27.89%。
- **控制变量/测量层级**：固定B、模型/训练设置，改变GPU数；系统比较时双方还分别使用不同但各自择优的并行映射，故“新策略加速”不是只增加SM或只减少通信的一变量。迭代时延和吞吐是实测；“训练1T tokens需要多少天”由吞吐计算。
- Table5采用同一MegaScale-MoE软件内部的**累积消融**：TP基线归一化1.00→SP+EP 1.13→inter-op overlap 1.22→intra-op overlap 1.28；不能把各步收益称为纯带宽硬件收益。其不同公开MoE模型的小规模消融曾减少layer数适应显存，不能直接当完整公开原版模型的自然训练性能。
- 强基线是公开[Megatron-LM固定commit `f1f039224584f0bc6ba89c21ef4f491d7136e3ce`](https://github.com/NVIDIA/Megatron-LM/commit/f1f039224584f0bc6ba89c21ef4f491d7136e3ce)。双方已启用DP/PP现有overlap，不能以禁用它们的弱基线制造硬件headroom。
- **尚未审查为具备公开可复现输入**：训练语料具体token bank、随机初始化/权重checkpoint的完全公开权限与实验manifest在本轮核验位置未取得。原论文real training evidence不能变成109的352B native结果。

**科学候选**：在已有强通信/计算重叠之后，固定global batch扩GPU时，pipeline-ready microbatch数与通信暴露之间是否存在可计算的资源饱和切换？  
**限制**：P13**分布式训练背景证据**有效，但109单RTX4080无法做240→1440 H800真正硬件扩展；目前不构造“在4080上估算1440卡性能”的假模拟。交Codex Lane T检查作者输入/可复现设计及是否存在更小公开的同类合法family，**允许结论为不可本机验证**。

## 2. Family N（非LLM）：真实几何变化→图准备→强等变Tensor Product

### 已直接核查的来源与输入

- [Sobek `2607.18074v1`](https://arxiv.org/html/2607.18074v1)的RTX5090 FP32 benchmark控制图边数、degree、graph count与导数阶；比较OpenEquivariance，实现流式径向投影、Tensor Product与聚合，删除不必要的逐边大中间量。但**编译、图生成和图准备不纳入其计时**，且是生成/重复的图，不是完整自然分子轨迹。
- AWMA [Round21](https://github.com/swayhrl/accel-sim-framework/blob/0b8310ee4afe8429b3ed2de381594794ee12ae31/docs/vm_tlb/literature_notes/awma/rounds/2026-10-02_ROUND_21_POST_R20_PROBLEM_DISCOVERY.md)已经确认Sobek固定源码`Cortex-Discovery/sobek@c1f815bfee1de420342c7b660fb2b1f9eab2441e`的receiver/source CSR、排序/permutation和prepared graph复用；ALCHEMI固定源码`NVIDIA/nvalchemi-toolkit-ops@32445c5f00e83fccd475589f1a6f5ac9e81e6b02`有GPU邻居生成/skin重建和结果复用。**不能假定每帧每层都重新prepare**。
- 已直接从GitHub固定版本读取[NequIP tutorial `sitraj.xyz`](https://github.com/mir-group/nequip-tutorial/blob/8f90935ba42fd9e03df323cf03428c456d87b881/sitraj.xyz)：Git blob `baac4e23364d00d29b2410fa60a92ade0cbf35a3`，文本含**110帧×每帧64个Si原子**，每帧有周期Lattice、species、position、forces、energy字段；按extxyz原子计数遍历110帧完整闭合。**文件内部并未由这次解析证明相邻帧是实际连续时间步**，不可据名字`sitraj`直接计算天然neighbor rebuild发生率。
- 训练好的神经网络模型适用Si/PBC以及强执行后端是否与Sobek`uvw/uvu`/NequIP路径同语义，仍未资格化。ALCHEMI示例在模型未加载时可回退Lennard-Jones，未来必须拒绝这种回退冒充AI workload。

**科学候选**：当几何连续变化、GPU邻居构建能合法按skin复用之后，双向索引/执行计划与真实力计算的准备成本是否仍在关键路径，且未被公开强软件消除？  
**限制**：已知source级依赖不等于时间headroom；训练导数二阶不能冒充推理所需一阶力求导；一个100%有效的随机图也不替代自然几何数据。交Codex Lane N只核**确切模型/输入/消费者接口兼容性与重建语义**，不重复AWMA Round21全部源码分析。

## 3. Family S（推理对照）：LLM mixed Prefill/Decode服务

- [NanoFlow OSDI25](https://www.usenix.org/conference/osdi25/presentation/zhu-kan)、[Bullet](https://arxiv.org/html/2504.19516)与[Exclusive Batching `2606.00516`](https://arxiv.org/html/2606.00516)已提供计算/访存/网络重叠、SM配额与独占/混合策略的强软件近邻。许多实验的**真实**是来自ShareGPT等来源的输入/输出长度；请求到达则由Poisson/饱和队列产生，不能直接称自然生产时间戳重放。
- 同一模型、GPU、请求来源的mix比例和策略交叉能形成P01研究动机；但跨GPU型号的带宽与算力/cache/后端同时改变，不构成“只增加DRAM带宽”的P13干预。
- AI-ARCH历史C16 Stage A的Qwen2.5-3B编译强模式B1有合法A/B同点，但B4缺合法配对；旧observer/V2/MP03_B不恢复。若未来有一项全新serving问题，需要**新的、独立、输入/正确性与软件baseline合法的发现性合同**，不由本Round启动。

**初步判定**：保留作为P01的有效外部对照与未来可能本机诊断family，但服务端到端SLO输入、当前本机最强合法软件、固定条件下可辨识时间目前均未闭合。当前不申请109。

## 4. 并行执行布局（CPU/sources only）

| 角色 | 执行内容 | 输出权限 | 不触碰 |
|---|---|---|---|
| **ChatGPT／本窗口** | 上述三family原文核对、P01/P13横向对照、独立审核Codex结果、协调证据汇总 | `hrl/ai-workload-research-coordination`的文献/索引/计划文档 | GPU、模拟器、AWMA source权威 |
| **Codex Lane T／174-new CPU-only** | 核MegaScale训练强弱扩展、input披露、Megatron-LM固定基线及可复现范围 | 独立`hrl/aiarch-a4-training-source-174-v1` branch、单文件报告 | CUDA、训练、模型/输入下载、AWMA R27 |
| **Codex Lane N／174-new CPU-only** | 核真实Si几何与NequIP/MACE对Sobek/ALCHEMI的接口、强软件复用及导数要求 | 独立`hrl/aiarch-a4-nonllm-source-174-v1` branch、单文件报告 | GPU、MD模拟、NequIP模型下载、AWMA R21 |

两Codex Goal位于：
- [AI_ARCH_ROUND_A4_TRAINING_SOURCE_REVIEW_174NEW_V1.md](../goals/AI_ARCH_ROUND_A4_TRAINING_SOURCE_REVIEW_174NEW_V1.md)
- [AI_ARCH_ROUND_A4_NONLLM_SOURCE_REVIEW_174NEW_V1.md](../goals/AI_ARCH_ROUND_A4_NONLLM_SOURCE_REVIEW_174NEW_V1.md)

**并发策略**：两窗口各自独立worktree、branch、output、临时文件；源和历史Git对象只读共享；开始前各自检查CPU/RAM/swap/disk负载，避免174本地已满导致反复重试/误清理。优先复用原仓库和GitHub只读源码，严禁大clone/大型scratch。Git推送失败时保留本地exact commit并尝试既有SSH备用传输，但不能因发布失败重跑/改科学结论。

**这个文档的存在不代表Codex已通过UI启动**：两个Codex任务需把分别冻结的Goal发到真实Codex窗口，ChatGPT当前仅通过GitHub准备文件与做只读研究。Codex完成后报告commit、受控证据和STOP，本窗口只采纳经过核查的限定结论；禁止两个Codex同时直接修改协调主分支。

## 5. 当前阶段的科学判定与准入

**Family T**：多GPU训练扩展规律有作者实测，但不具备109单卡自然复现条件 → `LITERATURE_EVIDENCE_ONLY / TRAINING_SOURCE_AUDIT_PENDING`。

**Family N**：真实几何文件存在，强GPU邻居构建和等变算子源码存在，但模型/输入/语义/重建时间资格未闭合 → `REAL_GEOMETRY_INPUT_EXISTS / MODEL_CONSUMER_COMPATIBILITY_PENDING`。

**Family S**：合法请求长度来源和同平台软件策略实验存在，但新本机strong serving与独立GPU需求尚未冻结 → `SERVING_SOFTWARE_BASELINE_EVIDENCE / NO_NEW_NATIVE_CONTRACT`。

Round A4目前只有这三项paper/source证据，**0已准入新硬件机制、0已准入新109 GPU、0模拟器重启**。任何单项停下均按`UNKNOWN/SOURCE_BLOCKED/STRONG_SOFTWARE_SUFFICIENT`说明，不为了维持节点负载扩大搜索。

## 6. 下一阶段建议：Round A5｜并行证据独立审查与优先候选收敛

**执行者：ChatGPT／AI-ARCH Discovery主审；Codex Lane T/N仅负责交付各自已冻结CPU-source任务，除非另经授权不增加新Lane。**

工作内容：
1. 根据两支Codex返回的Git exact commit和源文件，独立审查训练和非LLM资格矩阵（作者/源码/推断/未披露分开），按资源与工作量变化可辨识性选最多2个candidate；不把未经审查的新分支自动合入权威图谱。
2. 若非LLM模型/几何兼容，经明示同意后再设计**一份**非常小的自然执行诊断（模型+真实几何、合法备选索引结构、energy/force、强软件、未插桩wall、正确性、STOP）；仍不会自动运行GPU。
3. 若训练仍只有千卡MoE实测而无小规模同语义合法工作量，明确`NOT_PORTABLE_TO_SINGLE_4080`并停本地复现；保留分布式研究线而非伪造单卡缩放。
4. 与Inference Family S的正式服务到达/SLO分母再交叉比较；任何准备大环境、模拟器resource scaling、下载模型或开启109，都需要具体科学合同和资源审批。

**Round A5起点条件**：至少一个Codex Lane实际完成且结果可审；如果两个都未运行，继续当前ChatGPT原文研究，不宣称并行执行已经发生。
