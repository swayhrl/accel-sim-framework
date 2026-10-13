# Round A5｜Lane T/N联合独立科学审查：训练扩展与非LLM自然计算资格

**执行者：ChatGPT／AI-ARCH Discovery**  
**日期：2026-10-13**  
**证据模式：GitHub固定提交直接只读＋公开论文/源码定点复核；不是174/109/164原始运行的重新执行。**  
**最终科学决策：当前0个新GPU发现性探针准入；Lane T `ACCEPT_SCOPED`，Lane N `PARTIAL_DOCUMENT_INTEGRITY`且其受限`NO_NATURAL_MODEL_CONTRACT_YET`有独立上游依据。**

## 1. 源身份与Git树边界

| 源 | 精确提交／tree | 文件及变更 | 本次独立核验 |
|---|---|---|---|
| Lane T／174-new CPU-only | [`a1a70180736499687435b1e2d99984d4ebba4c53`](https://github.com/swayhrl/accel-sim-framework/commit/a1a70180736499687435b1e2d99984d4ebba4c53)，tree `3ac23ccc96cfcac557e1c9c0b6dd0a941dcd04eb` | [训练review](https://github.com/swayhrl/accel-sim-framework/blob/a1a70180736499687435b1e2d99984d4ebba4c53/docs/ai_workload_research/reviews/AI_ARCH_A4_TRAINING_SOURCE_REVIEW_174NEW_V1.md)，Git blob `e204c8936ac375b0ae2069d2efea8dd74f3b845d` | 固定commit读回、Git compare与原协调起点：**仅新增一份报告；ahead 1、behind 0**；parent为`4631fd56248bd23451b302401c07c625c920d593` |
| Lane N／174-new CPU-only | [`e355f096eeac44328d7463ef3256cc649ec9cb03`](https://github.com/swayhrl/accel-sim-framework/commit/e355f096eeac44328d7463ef3256cc649ec9cb03)，tree `8a40881ed603cee09f217dbd66fb61d0979198b` | [非LLM review原样保存](https://github.com/swayhrl/accel-sim-framework/blob/e355f096eeac44328d7463ef3256cc649ec9cb03/docs/ai_workload_research/reviews/AI_ARCH_A4_NONLLM_SOURCE_REVIEW_174NEW_V1.md)，Git blob `47b048c64edbd895166b46193b0b4230eab8625a` | parent同一`4631…`，**仅新增一份报告；ahead 1、behind 0**；远端报告存在重大字符丢失问题（详§3） |
| AI-ARCH研究协调 | [`4631fd56248bd23451b302401c07c625c920d593`](https://github.com/swayhrl/accel-sim-framework/commit/4631fd56248bd23451b302401c07c625c920d593) | Round A4计划、独立Goal、既有A1–A3及协调协议 | 只是知识和审查导航，不是scientific producer或者被写入的Lane execution authority |

Lane T/N的报告“worktree干净、时长和token消耗”、174 CPU/swap/disk状态来自各自Codex自述；本ChatGPT**没有SSH重新取进程或磁盘日志**。Git证据不能核验这些现场声明。两个Lane均未在Git差异中修改C16/AWMA科学文件或模拟器代码；本次审查不访问node164原始大文件。

## 2. Lane T训练线：ACCEPT_SCOPED

### 2.1 原始作者论文与基线

来源：[MegaScale-MoE arXiv `2505.11432v3`](https://arxiv.org/html/2505.11432v3) §6.1 Table3/Figure12、§6.2 Table5，和作者指定[Megatron-LM固定源码`f1f039224584f0bc6ba89c21ef4f491d7136e3ce`](https://github.com/NVIDIA/Megatron-LM/commit/f1f039224584f0bc6ba89c21ef4f491d7136e3ce)。本次直接从v3 HTML核对Table3、§6.1强弱扩展文字与Table5累积消融；Megatron-LM实现能力及其配置身份以Lane T固定源码审查为准，**未新建/运行baseline**。

- **PAPER_AUTHOR/NATIVE_EXTERNAL**：内部352B MoE、seq8192、H800、PP=15；固定global B720时240→1440 GPU，Mega吞吐272.9k→1407.7k tokens/s，MFU32.48%→27.89%；Megatron比较同点吞吐151.1k→746.6k。真实系统扩展数据可信为**作者原文报告**，不是本项目实际运行。
- **PAPER_AUTHOR**：弱扩展GPU480→1440，global batch360→1080同比增；作者报告Mega相对近似保持吞吐扩展效率、Megatron有约2.74%的归一化下降。弱扩展的“效率曲线”不是绝对tokens/s下降，也不能与强扩展固定B混为一个干预。
- **PAPER_AUTHOR_CAUSAL_EXPLANATION**：作者将强扩展MFU下降归因于固定global batch下每流水段microbatch减少、pipeline bubble增长。但在Table3/Figure12**未逐点披露**TP/SP/EP/DP、microbatch size、virtual PP、ready队列、bubble时间线或352B各扩展点exposed communication统计。只能归纳为作者解释，不可伪称这些中间量实测。
- **STRONG_SOFTWARE**：两系统配置分别择优且均启用既有DP/PP通信重叠；Table5的1.00→1.13→1.22→1.28是Mega内部逐步累积技术消融，不能当四个独立改善或一个“未被软件消除”的硬件上限。
- **INPUT/NUMERIC**：352B的确切训练token bank、随机种子、实际微批及checkpoint/完整长期数值质量合同未在已核章节披露；论文其它7B/35B/176B的loss曲线不是352B每点长期收敛资格。1T tokens训练天数是作者用吞吐推算，不是已完成1T训练的实测。
- **NUMERIC_CAVEAT**：原文Table3的240-GPU Megatron 39.94s和151.1k tokens/s相乘，与B720×seq8192的token/iteration不严格一致（T已指出）；本次再次核原表确实如此。记录`PAPER_TABLE_INTERNAL_METRIC_IDENTITY_UNEXPLAINED`，不改写作者数值、不将差异猜成运行错误，也不将表作为逐iteration token身份验证。

### 2.2 T裁决

`ACCEPT_SCOPED: NO_NEW_TRAINING_PROBLEM_QUALIFIED_WITHIN_A4_SOURCE_REVIEW`。

**接受的是有限的准入否决**：这篇论文确立分布式多GPU训练扩展的有条件研究动机，但缺少可公开固定的自然输入、逐点管线配置以及可单因子干预的实际执行轨迹；109单RTX4080无法承载PP15/240–1440×H800的同一系统对象。不能因此宣布“训练系统中没有AI体系结构问题”或“原论文扩展机理错误”。不安排新的训练、模拟、模型下载或109任务。

## 3. Lane N非LLM线：PARTIAL_DOCUMENT_INTEGRITY，有限源证据仍可保留

### 3.1 重要且独立确认的远端文档完整性缺陷

**所见不是仅显示乱码**：

- 在精确`e355f096…`分别通过GitHub contents UTF-8、raw URL和blob接口读取，文件**10,477字节全部为ASCII**；有**2,334个字面量`?`，中文汉字0个**。例如报告标题实际为`# AI-ARCH Round A4?174-new ?LLM???????????`。中文解释性句子已被实质性替换。
- 本ChatGPT使用独立SHA-256算法在远端完整ASCII字节上计算，得到**`26ce76b3d1ba5beeb03ddf3439c33f96ee65282313097a8db1b050f6562ebdf3`**，与Lane N自报值完全一致；Git blob亦固定。
- 所以文件/传输完整性校验确实PASS，但**校验对象是已经损坏的文本**；SHA相同不构成科学说明文字完整。原commit不覆盖、不改写、保留作为发生过程记录。当前不能给整篇Lane N报告`ACCEPT_SCOPED_FULL`。

**分类**：`N_REPORT_REDACTION_OR_ENCODING_LOSS_CONFIRMED / TEXT_REISSUE_NEEDED`，原因究竟是进程输出编码、写文件环节、源字面量被替换还是其它路径，**未诊断**，不能只凭表象断言UTF-8 locale是根因。应该最小化生成一份可读V2而不是重跑15分钟研究。报告英文路径、数值、状态仍可审，但未保存的中文不能根据语境填造。

### 3.2 脱离损坏文字后，独立可确证的主要科学事实

- **REAL_INPUT_SOURCE**：[NequIP tutorial固定Si extxyz `sitraj.xyz`](https://github.com/mir-group/nequip-tutorial/blob/8f90935ba42fd9e03df323cf03428c456d87b881/sitraj.xyz)，Git blob`baac4e23364d00d29b2410fa60a92ade0cbf35a3`；本ChatGPT直接独立解析：完整110帧×每帧64个Si、周期Lattice、positions、energy/forces等属性；文件784,661字节，本次重算SHA-256 `c08d3771a06beb82b0ed4258f78eecc7ce623f73ca6df20be99bd5722163e770`与N报告所存ASCII值吻合。但**没有认证相邻帧为连续实际时间步**，不能从110帧自然数量推断邻居重建频率。
- **MODEL_CONFIG_SOURCE**：[NequIP tutorial固定`config.yaml`](https://github.com/mir-group/nequip-tutorial/blob/8f90935ba42fd9e03df323cf03428c456d87b881/config.yaml)确实给出Si-only、r_max 5.0、float32、l_max1、3 layers、num_features32、能量/力loss等。它是**训练配置**，不是已执行或下载的训练好checkpoint。其uniform 32特征在multiplicity这个单独维度上可能更接近Sobek UVU要求，但完整instructions/weights/backward/path-normalization仍未合格。
- **MODEL_PAGE_SOURCE**：[NequIP-OAM-S:0.1作者模型页](https://www.nequip.net/models/mir-group/NequIP-OAM-S%3A0.1)披露tensor features l=0为128、l=1为64、layers2、r_max4.5Å，并列Si为支持元素；还提供OpenEquivariance modifier。特征128/64来自作者公布的模型配置，**不能直接假设其完整checkpoint的每一处TP输入输出都是相同multiplicity**，但已经提示直接通用UVW/UVU转换需要层内逐instruction检查。
- **SOURCE_COMPATIBILITY**：[Sobek固定`tpconvproblem.py`](https://github.com/Cortex-Discovery/sobek/blob/c1f815bfee1de420342c7b660fb2b1f9eab2441e/sobek/nn/tpconv/tpconvproblem.py)明确`uvu`要求每个输入/输出irrep角区统一且相等的multiplicity，且不支持混合`uvu`/ `uvw`指令。它也有纯`uvw`路径：**128/64不能直接满足该`uvu`统一要求，但这只否定未经变换的直接UVU替换；不等于Sobek所有模式不可能、OAM-S不能通过现有OpenEquivariance运行、或自然力计算对象无效**。
- **CORRECTNESS/NEIGHBOR**：[NequIP固定`interaction_block.py`](https://github.com/mir-group/nequip/blob/27d9d2182da918ab7be0017d8300e53278f5e00e/nequip/nn/interaction_block.py)含`uvu` TP scatter与两侧Linear、edge MLP、残差/skip；Sobek统一TP路径是否可替换其中一段，除了multiplicity，还需核路径归一化、权重矩阵、edge方向、periodic shifts、dtype和force反传。AWMA [Round21固定笔记](https://github.com/swayhrl/accel-sim-framework/blob/0b8310ee4afe8429b3ed2de381594794ee12ae31/docs/vm_tlb/literature_notes/awma/rounds/2026-10-02_ROUND_21_POST_R20_PROBLEM_DISCOVERY.md)已审Sobek双向CSR、prepared cache与ALCHEMI GPU邻居重建/复用。存在源码能力**不代表**已测得自然完整力推理的准备时间。
- **MACE_FALLBACK**：ALCHEMI官方MACE示例存在checkpoint失败后回退Lennard-Jones的风险，必须在未来任何实测确认真实MLIP加载，不能把fallback当训练模型的性能。该能力及风险沿用既有Round21来源，而非Lane N损坏正文的新增实验结果。

### 3.3 N裁决

`PARTIAL_DOCUMENT_INTEGRITY + ACCEPT_SCOPED_SOURCE_ALIGNMENT + NO_NEW_NATIVE_ADMISSION`。

当前调查的NequIP-OAM-S/Sobek直接UVU、Si tutorial无训练checkpoint、MD22缺本次可核的连续输入、MACE checkpoint/fallback均未形成**同一个**可执行自然model+geometry+strong backend+force数值合同。故**当前没有合法的新109 GPU实验**，这一有限科学判断可接受。

但不得表述为`ALL_NON_LLM_ARCHITECTURAL_PROBLEMS_REJECTED`。Si真几何可支持**独立静态帧**的CPU/source核查，只有真实连续时间证明后才允许谈重建频率；OAM-S公开且支持Si和强OEQ后端，能够继续用作源审候选，不应为使其适配Sobek硬改模型语义。Lane N有文档质量问题，应以**仅文档的可读V2**修复，不因失败重新运行GPU/研究/模型下载。

## 4. 跨域联合决策（科学问题为主）

| Family | 原有外部/本地证据 | 本轮独立判断 | 阻塞最低限度下一步 |
|---|---|---|---|
| T：大规模MoE训练 | 原论文352B/千卡H800真实训练扩展；有强Megatron软件 | 保留分布式扩展研究动机，**本地不准入** | 自然训练token身份、逐点DP/微批/PP、exposed comm与stage ready时间、数值质量；单4080不代表原对象 |
| N：几何/等变非LLM | 110个自然Si结构（非认证连续MD）；真实已训练OAM-S存在，但与Sobek直接UVU不兼容；ALCHEMI已有强graph API | 保留条件性研究动机，**本地不准入**；N源审文本部分损坏 | 选择同一trained model/strong kernel、合法图接口、force一阶数值、静态帧到准备端到端wall；重建频率需连续帧证明 |
| S：LLM混合Serving | NanoFlow、MPK、Bullet、Exclusive Batching已提供强软件以及多平台原生限定结果 | 仍为外部P01竞争/补充，不从T/N失败中推其正/负 | 自然到达vs合成到达、同软件/平台、TTFT/TPOT/SLO和完整请求时间；当前无新109合同 |

**总状态：`ROUND_A5_NO_NEW_NATIVE_PROBE_ADMITTED`。** T/N是本次两个指定family的条件性STOP，不表示整个AI-ARCH Discovery应结束，更不意味着旧C16/AWMA科学门槛可下调。现有AI-ARCH P01/P13仍是有意义的横向方法研究，但没有新硬件机制或真实GPU余量获准。

## 5. 下一轮计划（提案，不因本文件而自动运行）

### Round A6｜自然非LLM强软件路径资格与训练领域拓展（执行者：ChatGPT主审；Codex Lane N仅可做文本修复）

1. **轻量修复Lane N文档**：在自己的分支保留原V1，新增`AI_ARCH_A4_NONLLM_SOURCE_REVIEW_174NEW_V2.md`，从固定原始source refs重新梳理必要论据，生成后校验至少正文中文字符存在、标题可读、源字段完整、UTF-8 roundtrip、SHA256/远端fetch-back；不要靠替换`?`猜造丢失句子，不重复原有source crawl，不扩大科学范围。如果lane N已STOP，不要求其自动重启。
2. **ChatGPT继续自然非LLM源审**：优先以OAM-S原生NequIP＋OpenEquivariance作为**成熟baseline**，图构建/force完整路径与公开Si帧（不假设连续）；Sobek仅作为可兼容时的选择，避免“必须换成Sobek”的强制工程。查切实的调用与正确性合同，不下载模型权重。若仍无同语义路径/必要时间指标，保持停止。
3. **训练方向换一个公开可复现实验组**：MegaScale 352B的外部扩展证据保留，但不把其私有batch变成109单卡目标；先调研至少一项自然训练的真实公开输入＋当前软件强基线，必要时讨论适当规模平台。重点查看backward/optimizer/通信ready时间，而不是仅仅比较GPU总数。
4. **可交付**：两张source-only资格卡/强软件与竞争解释矩阵；有结论再决定是否准备独立小额GPU探针提案。**Round A6的文献与source工作不启动109 GPU、174模拟器、新模型/几何下载、训练或AWMA R27R3**。

## 6. 冻结权限

- C16 Stage A仍`TERMINAL_PARTIAL`，四DQ未闭合；不恢复Mode B/Observer V3/Tier1/holdout。
- AWMA R27R3仍`R27R3_B0_REFERENCE_NOT_REPEATABLE`、独立审查STOP；不改标签、不重跑。
- Lane T/N成果分支各自保持独立；本文件写入协调分支属于**科学审查新文档**，不是合并、cherry-pick或复制历史执行数据。
- 本次`GITHUB_ONLY_NOT_RAW_REVALIDATED`，也没有重新执行109 GPU、174模拟器或174 Codex；不得把本文Git来源查阅称作独立raw复算。
