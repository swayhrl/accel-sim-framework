# AI-ARCH｜AI负载体系结构研究当前协调状态

新AI-ARCH Discovery窗口优先阅读：[2026-10-13完整交接](AI_ARCH_DISCOVERY_HANDOFF_CONTEXT_2026-10-13_V1.md)。历史C16旧Stage A/Reset不重启，AWMA最新R27R3独立审查已STOP。

> **快照日期：2026-10-13。只读科研导航；不是实时任务看板，不授予执行权限。**

| 主线 | 最新证据入口 | 当前科学状态 | 后续操作边界 |
|---|---|---|---|
| C16 | [`635b2f22cbe1bed5ac45de04b258a5f5e9bc6d4f`](https://github.com/swayhrl/accel-sim-framework/commit/635b2f22cbe1bed5ac45de04b258a5f5e9bc6d4f) | Stage A停止；10候选中0正式准入，2个未准入问题保留 | 无新C16 GPU/holdout/机制授权；研究目标保留 |
| AWMA·地址翻译/Pre-L1 | [机制资格化记录](https://github.com/swayhrl/accel-sim-framework/blob/29ce051f982f3854bd4392a94e4195c59340123b/docs/vm_tlb/review_packs/AWMA_PREL1_COALESCER_PAPER_QUALIFICATION_V1/FINAL_QUALIFICATION.md) | 模拟器与独立样本支持有范围的翻译服务抑制；运行加速有正/零/负 | 保留独立论文证据，不推断真实4080整模型加速 |
| AWMA·在线稀疏分派 | [`99d05f0ad221a1d44dd11bac0ed83965bb2c0942`](https://github.com/swayhrl/accel-sim-framework/commit/99d05f0ad221a1d44dd11bac0ed83965bb2c0942) | 固定公开批次的局部在线净时间正结果；非稳定普遍端到端提升 | 不自动推硬件 |
| AWMA·训练梯度容量 | [R26审查](https://github.com/swayhrl/accel-sim-framework/blob/0b8310ee4afe8429b3ed2de381594794ee12ae31/docs/vm_tlb/literature_notes/awma/empirical/R26_TIED_WEIGHT_CAPACITY_REVIEW_2026-10-02.md)；[R27R2审查](https://github.com/swayhrl/accel-sim-framework/blob/0b8310ee4afe8429b3ed2de381594794ee12ae31/docs/vm_tlb/literature_notes/awma/empirical/R27R2_VARIED_BATCH_CAPACITY_REVIEW_2026-10-13.md) | R26重复输入条件下增加1个物理Batch；R27R2不同输入数值未资格化 | 不改原合同，不声称真实多样batch容量效果 |
| AWMA·R27R3 | [execution](https://github.com/swayhrl/accel-sim-framework/commit/7bd31fae4c54e121d54743a803d978ee02a64959)；[独立审阅](https://github.com/swayhrl/accel-sim-framework/blob/d6e9bbfb562814bcd5dc5adb444d3c572e7f446b/docs/vm_tlb/literature_notes/awma/empirical/R27R3_B0_REFERENCE_REPEATABILITY_REVIEW_2026-10-13.md) | **接受**`R27R3_B0_REFERENCE_NOT_REPEATABLE`；同样起点/B1/固定bank k0两次B0，25/262,668,288 BF16总梯度元素超过原容差；内核归因未知 | R27R3 COMPLETE/STOP；未运行C1/S2组件归因、容量或32步；**无新AWMA GPU授权** |

## 下一步的科研组织

- 统一问题图谱和证据索引已发布为V1；训练与推理、LLM与非LLM均在研究范围。
- R27R3证据按[独立审阅接受后的E-A13](AI_WORKLOAD_C16_AWMA_EVIDENCE_INDEX_V1.md)归档；协调分支不把该B0重复性失败升级为硬件瓶颈，也不以此重启旧实验。
- 后续文献阅读与各项目既有实验并行，先查已解决的软件能力、观测范围和剩余约束。
- 实验只由具体可证伪问题触发；发现性小实验与正式机制验证分开。
- 共享资源不变：109 GPU按既有锁串行；174-new科研分析和模拟按原授权；164负责大文件的长期保存。
- 本文件不安排新Goal，不判定尚待审查的AWMA执行结果为accepted。

## AI-ARCH Discovery｜Round A2文献研究更新（2026-10-13）

- [Round A1：22条原始实验组](literature/AI_ARCH_P01_P13_EXPERIMENT_GROUP_AUDIT_2026-10-13_V1.md)和[Round A1资源/调度因果精读](literature/AI_ARCH_P01_P13_RESOURCE_MODEL_CAUSAL_READING_2026-10-13_V1.md)已完成。
- [**Round A2：Bullet、Kitsune、VTC、Tawa、Twill的实际实验组、软件近邻和资源限制审计**](literature/AI_ARCH_P01_P13_ROUND_A2_EXECUTION_RESOURCE_BOUNDARIES_2026-10-13_V1.md)已加入协调层。重要证据分界：Kitsune的应用性能及硬件资源缩放主要来自A100类模拟，queue微基准来自实芯；VTC的Llama/vLLM强对照是单Decoder Layer、在H100上不加速；Tawa与Twill主要是H100/B200算子级真实kernel，不是完整训练/服务。
- **仅保留两张待证伪问题**：Q-A2-01（强软件后的任务供给与资源服务饱和点）及Q-A2-02（异构task中的缓冲/寄存器与数据就绪生命周期）；都是DISCOVERY_DESIGN_ONLY，并非机制创新或native实验结论。
- **下一步建议Round A3**：复用已审查C16小型review pack和外部原文，做两张问题的可辨识性与最近邻反证账本；若无需真实GPU即可否定，则直接收口。仅文献/协调证据工作；没有109 GPU、174模拟器、C16 Stage A或AWMA新任务授权。
- 本研究更新**不改变**上表AWMA R27R3独立审查STOP、C16历史终态及共享节点权限。

## Round A3｜历史证据闭环与候选准入核查（执行者：ChatGPT／AI-ARCH Discovery，2026-10-13）

- [Round A3正式审查底稿](literature/AI_ARCH_ROUND_A3_HISTORICAL_EVIDENCE_CLOSURE_AND_CANDIDATE_ADMISSION_2026-10-13_V1.md)已写入：直接核固定C16 `a3a36e64` Split-K M1/16/32/64、`6d226cd9` K容量、`30b3016a` FFN理论headroom、`e8a2553f` 合法双流负例，并对照MPK固定作者源码与Tawa/Twill原文资源模型。
- **Q-A2-01**：当前只支持旧W4算子族**任务分解方案随规模反转**，不能证明单变量物理SM扩展或强软件之后有新硬件残余；保留有条件规律，不晋升新native。
- **Q-A2-02**：当前FFN双流性能负、F2B分块tile-ready依赖与合法oracle未定义，强软件/论文近邻充分；parked，不能据此开发硬件。
- **本轮裁决：0个机制晋升，0个109发现性探针、0个174模拟器任务**。没有改动C16历史、AWMA独立审查和GPU共享锁。
- **建议下一轮Round A4｜跨负载自然场景选样与资源问题辨识（执行者：ChatGPT／AI-ARCH Discovery）**：从已审训练和非LLM作者数据与AWMA Round09/21去重，找最多3个有真实输入、完整时间区间与成熟软件对照的family，最多保留2张可证伪问题卡；本轮仅文献/GitHub只读与协调笔记，无新的Codex执行Goal。新GPU探针只在具备独立完整科学合同后单独提出。

## Round A4｜跨负载自然场景选样与并行科研核查（执行者：ChatGPT＋Codex Lane T/N）

- [Round A4三family比较与并行方案](literature/AI_ARCH_ROUND_A4_NATURAL_WORKLOAD_PARALLEL_DISCOVERY_2026-10-13_V1.md)：ChatGPT已只读核作者公开MegaScale-MoE训练扩展、Sobek/ALCHEMI/NequIP公开强邻近能力、LLM混合Serving证据。包括固定NequIP tutorial `sitraj.xyz`的Git blob读取与110帧×64 Si extxyz结构核对；**未证相邻帧自然时间顺序**。
- **Codex任务已在协调分支准备、尚未由ChatGPT实际启动Codex窗口**：
  - [Lane T／174-new CPU-only：训练输入、强/弱扩展、Megatron-LM强基线](goals/AI_ARCH_ROUND_A4_TRAINING_SOURCE_REVIEW_174NEW_V1.md) → 独立`hrl/aiarch-a4-training-source-174-v1`
  - [Lane N／174-new CPU-only：非LLM自然几何、NequIP/MACE与Sobek/ALCHEMI消费者接口](goals/AI_ARCH_ROUND_A4_NONLLM_SOURCE_REVIEW_174NEW_V1.md) → 独立`hrl/aiarch-a4-nonllm-source-174-v1`
- 两Lane仅各写一个独立source review Markdown，禁止直接提交协调分支、调用GPU/模拟器、下载大资产、修改AWMA/C16正式实验；本ChatGPT窗口在其报告回来后独立核对，才选择性更新共有索引。
- **当前科学状态**：训练multi-GPU作者实测但不可直接投射到109；非LLM公开几何文件存在但真实时间身份与模型/消费者兼容待闭合；Serving已有强软件与paper输入，但无新本机probe合同。**当前无新109 GPU、174模拟器、Stage A或新机制执行授权**。
- **建议后续Round A5｜并行证据独立审查与优先候选收敛（执行者：ChatGPT／AI-ARCH Discovery；Codex Lane T/N交付结果）**：审核两支Git exact commit和输入/语义状态，最多保留2张新问题卡，若具充分依据再单独提出有界GPU发现性探针审查，不因线程空闲而启动。

## Round A5｜Lane T/N联合独立科学审查（执行者：ChatGPT／AI-ARCH Discovery）

- [**Round A5固定独立科学review**](reviews/AI_ARCH_ROUND_A5_LANE_T_N_INDEPENDENT_REVIEW_2026-10-13_V1.md)：审阅两Lane各自Git固定提交；两分支均以Round A4协调起点`4631fd56248bd23451b302401c07c625c920d593`为parent，分别只新增一份独立source-only报告。**不合并Lane分支**。
- **Lane T `ACCEPT_SCOPED`**：[训练源审`a1a70180736499687435b1e2d99984d4ebba4c53`](https://github.com/swayhrl/accel-sim-framework/blob/a1a70180736499687435b1e2d99984d4ebba4c53/docs/ai_workload_research/reviews/AI_ARCH_A4_TRAINING_SOURCE_REVIEW_174NEW_V1.md)；MegaScale-MoE 352B H800强/弱扩展为作者原文实测，但逐点微批/实际训练token/通信气泡分解不足，109单卡无法同语义复现；`NO_NEW_TRAINING_PROBLEM_QUALIFIED_WITHIN_A4`，非训练全领域否定。
- **Lane N `PARTIAL_DOCUMENT_INTEGRITY`**：[原始报告`e355f096eeac44328d7463ef3256cc649ec9cb03`](https://github.com/swayhrl/accel-sim-framework/blob/e355f096eeac44328d7463ef3256cc649ec9cb03/docs/ai_workload_research/reviews/AI_ARCH_A4_NONLLM_SOURCE_REVIEW_174NEW_V1.md)实际包含2,334个字面`?`且零中文汉字；本ChatGPT重算SHA256完全匹配报告值，证实已提交版本文本丢失。**不接受其完整中文叙述**。通过独立固定源码及Si文件核验，保留有限结论：110帧×64 Si输入身份成立，未认证时间顺序；OAM-S 128/64不符合Sobek**直接UVU**统一multiplicity要求，但不否定OAM-S现有OEQ强后端及Sobek其它模式；`NO_NATURAL_MODEL_CONTRACT_YET / NO_NEW_NATIVE_ADMISSION`只针对审查过的接口组合。
- **联合裁决 `ROUND_A5_NO_NEW_NATIVE_PROBE_ADMITTED`**：目前0个新109 GPU探针、0模拟器任务、0机制晋升；C16 Stage A与AWMA R27R3固定STOP保持。已审来源的有限结论不因未准入而扩展为否定整个领域。
- **建议下一轮Round A6｜自然非LLM强软件路径资格与训练领域拓展（执行者：ChatGPT主审；Lane N可选纯文本V2修复）**：若Lane N需可读报告，仅按原源码重建UTF-8 V2，不推断遗失文字、不重跑科学实验；本窗口继续OAM-S+OpenEquivariance+真实Si独立帧的可行性与另一公开训练family的源审。当前无109/174模拟/新下载/训练授权。
