# Round A4｜训练负载资源扩展与可验证性审计

**执行者：Codex Lane T／174-new CPU-only（独立新窗口）**  
**Stage：AI_ARCH_A4_TRAINING_SOURCE_FEASIBILITY_V1**  
**权限类型：SOURCE_ONLY，不是GPU/模拟器/训练/新机制实验授权。**  
**科学归属：AI-ARCH Discovery，ChatGPT窗口后续独立审查。**

## 一、具体科学问题

从原文证据中判断：在现代MoE训练完成成熟并行映射和通信重叠之后，**GPU数增加时每GPU可就绪微批次减少、pipeline bubble增加、通信暴露**分别有什么独立的可观测证据？能否构成P01/P13的可证伪自然训练工作量，而非伪造一份单GPU的352B模型？

## 二、必读已审来源（先去重，不重复全量阅读）

1. 本分支最新`AI_ARCH_ROUND_A3_HISTORICAL_EVIDENCE_CLOSURE_AND_CANDIDATE_ADMISSION_2026-10-13_V1.md`、Round A2文献审计、证据索引及`COORDINATION_PROTOCOL.md`。
2. MegaScale-MoE，EuroSys 2026/arXiv HTML：`https://arxiv.org/html/2505.11432`，明确核§3–6中Table 2/3/5、强扩展与弱扩展，以及Figure 12和训练输入披露情况。
3. 作者所声明的最强固定对照：`NVIDIA/Megatron-LM@f1f039224584f0bc6ba89c21ef4f491d7136e3ce`（公开commit，**仅按必须的文件/方法核查，不全仓克隆**）。
4. AWMA既有[Round09](https://github.com/swayhrl/accel-sim-framework/blob/0b8310ee4afe8429b3ed2de381594794ee12ae31/docs/vm_tlb/literature_notes/awma/rounds/2026-09-27_ROUND_09_BROAD_SIDE_RESEARCH.md)与[Round22材料](https://github.com/swayhrl/accel-sim-framework/blob/0b8310ee4afe8429b3ed2de381594794ee12ae31/docs/vm_tlb/literature_notes/awma/empirical/ROUND22_FAMILY_BOUNDARY_LEDGER.tsv)：只读用于避免重新研究已审R24–R27数值资格化和已处理的训练方法，不触发AWMA任何Goal。

## 三、只做有界CPU/source审查（可以与另一个Codex并发）

- 首先检查git仓库/ref、174-new的CPU/RAM/swap/剩余磁盘，以及有没有正在运行的独立任务；仅当两个轻量只读工作不造成冲突才继续。独立worktree/branch、独立小型output与临时文件；不得争用AWMA和其它正在使用的workspace。不要推测109资源空闲。
- **训练实验组身份核查**：列明352B的实际`model configuration`、序列长度、global batch、PP=15、每组GPU/TP/SP/EP/DP，判断哪些变量真实固定，哪些在选择最优parallelism时一起改变；明确真实训练输入token/source是否论文披露，未披露就标`UNDISCLOSED_IN_CHECKED_VERSION`，不能从“production”推断数据可获取。
- **强扩展vs弱扩展分离**：强扩展固定global B720，GPU数240→1440；弱扩展GPU和B同比增加；表中iteration time和tokens/s是作者实测，1T token训练天数是**换算估计**。MFU下降必须区分作者解释与本窗口推断；“microbatches/stage数量”仅在作者明确给出PP/MB划分时可计算，否则保留符号/区间，**不反推虚构microbatch size**。
- **软件能力**：作者已提供SP+EP、inter/intra-op overlap、选择性activation rematerialization以及compressed communication，并已启用baseline现有DP/PP overlap；不要把它们重命名为新的架构发明。Table 5是累积消融，不可把incremental数字当独立可加speedup。
- **P13资源问题判别**：枚举compute、communication、pipeline occupancy、activation capacity哪项在原文确有可测控制变量；区分单GPU适用性、训练质量/精度与强/弱扩展。
- 若同一公开模型较小训练family有明确自然数据和成熟baseline，可在报告末登记**至多一个**下一步的source-only候选；不能为了填空提出新下载/新训练。

## 四、交付及状态

只新增（如有足够证据）：
`docs/ai_workload_research/reviews/AI_ARCH_A4_TRAINING_SOURCE_REVIEW_174NEW_V1.md`

包含：
1. 论文版本/原始Figure/Table定位和受控变量表；
2. 作者实测/估计/源码事实/我们的推断明确分列；
3. 训练模型输入、workload真实性、数值/质量要求、平台与最强软件baseline；
4. P01/P13可辨识性：什么可测、什么不能用109单卡验证；
5. 一个可证伪问题或明确`NO_NEW_TRAINING_PROBLEM_QUALIFIED`；
6. 科学STOP及以后真正需要的最小额外信息，不生成GPU Goal。

完成markdown自检、git diff、提交本独立worktree并push、远端fetch-back及commit/tree核验；报告commit SHA及source refs。**不merge进协调分支；ChatGPT窗口审查后再选择性摘录。**

## 五、严格禁止

不得调用CUDA、torch GPU/JIT、NSYS/NCU、Accel-Sim、NVBit，不下载模型/大型dataset，不运行训练或CUDA benchmark，不写/清理164权威资产，不改109锁，不触碰AWMA R27R3、C16 Stage A、DTC-L1工作区。失败的source URL或资料不齐不能自行替代为猜测；记录`SOURCE_NOT_ACCESSIBLE`并STOP该子项。普通包装/路径问题可轻量solve-and-continue，不因小问题扩充工程任务。

**原始输入/自然模型/同语义软件资格不成立时必须按证据停止，而不是另起训练实验。**
