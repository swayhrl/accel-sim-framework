# Round A73｜H-A73：GPU资源反事实与强软件后的可证伪约束

执行：Codex / 174-new；2026-10-16（Asia/Shanghai）。固定Goal HEAD：9afcdf6faa5b8351b56c9cbbefd3530c19c89537；科学父提交：adf6ab9467887f74b0b509c105977128663707a5。

## 0. 裁决与交付含义

**SOURCE_QUESTION_READY_FOR_CROSS_REVIEW；1个问题、0个备选；native与模拟器均未获准、未执行。** 推荐的问题是：在成熟attention算法、warp specialization和重新调优之后，把固定硅面积/功耗预算从矩阵计算转给指数/片上数据服务，是否会改善真实通用模型的完整Prefill，还是局部attention改善被FFN/投影及状态处理的退化抵消？

这是一项**资源取舍的待证伪问题**，不是声称发现SFU瓶颈、证明硬件headroom或发明新softmax流水。FlashAttention-4已经直接处理非对称硬件扩展；Twill已为给定机器约束生成强调度。我们保留的是它们之后的边际资源价格、重新调优与完整模型分母的联合测试。若已有强软件使该边际为零，或者同预算矩阵损失更大，即停止。不能以“没有人给完整wall”作为阳性证据。

只写本H目录四文件。独立sparse worktree；没有读取W-A73产物、等待或轮询W；没有改协调文件、A70旧报告、AWMA/C16/ISCAS或旧STOP。

## 1. 阅读与筛选范围

已完整读本Goal（执行重点为第0—2、4—6节）、固定起点CURRENT_STATE、A72综合审查、协调规则第1—8节及问题图谱；按需回读证据索引相关C16边界。A70 M/N/O/P的固定原报告分别核初始结论、直接近邻与最后裁决，未把83条记录当83组native负结果。

保留12项初筛记录，见 PAPER_GROUPS.tsv：LLMCompass（ISCA24）、Duplex（MICRO24）、Kitsune（TACO25论文族，精读arXiv v1）、LIA（ISCA25）、Stratum（MICRO25）、InstAttention（HPCA25）、FlexAttention（MLSys25）、NanoFlow（OSDI25）、Twill/Syncopate/VTC（OSDI26），以及FA4（2603.05451v1，原始技术稿补充强反证；不冒称本轮已核其会议终稿）。

其中G01—G06是六个具体精审组；G01/G03/G04/G05可核正式会议正文，G02的发表身份由作者主页确认，但实验数字只归所读v1，不假定与最终22页TACO版完全一致；G06明确是技术稿。其余仅SCREEN/PARTIAL，不能据摘要倍数补配置。LIA完整论文入口受限；InstAttention本轮未取得完整正文；二者不承担推荐问题的量化依据。

## 2. 六组原始证据：资源、分母和不能外推的内容

| ID | 原始组与证据层级 | 资源反事实/强对照真正说明什么 |
|---|---|---|
| G01 | LLMCompass，§IV-A/D、Fig9；GPT-3单层FP16，A100等价参数；MODEL_ESTIMATE | 固定其余参数改变local buffer，Prefill与Decode敏感度不同且有饱和；不是整GPT-3实测，也不是现代fused attention的SFU/SMEM标定 |
| G02 | Kitsune v1，§6/Table2/Figs10—14；Llama3-8B ctx/tok/train分开，A100类NVAS；AUTHOR_SIMULATION | L2队列与调度改变后，省流量不等于同幅度wall；不能把所有应用的平均收益搬给Llama，更不能搬给Hopper/Blackwell |
| G03 | Twill OSDI26，§6.1/6.2.2、Figs8—9；B200 FP16非因果FMHA；AUTHOR_NATIVE_KERNEL + schedule model | 给定机器资源、依赖和支持的循环内可最优调度；kernel接近FA4不等于芯片资源配比最优，也不是完整模型Prefill结果 |
| G04 | Syncopate OSDI26，§6.1/6.3、Fig11；Llama/Qwen派生GEMM形状，4/8 H100；AUTHOR_NATIVE_OPERATOR | 同一通信计划下backend、通信SM配额及chunk存在耦合/非单调；不是只扩大NVLink带宽的硬件因果，更不是完整405B模型服务测量 |
| G05 | Duplex MICRO24论文族v1，§VI/VII、Fig13；Mixtral FP16，合成请求与uniform专家选择；AUTHOR_SIMULATION | H100等价GPU与Logic-PIM比较同时改变内带宽、计算和调度；容量相同不是面积/功耗相同，且非自然router分布 |
| G06 | FA4 v1，§3/5/AppA；Blackwell BF16 causal/noncausal attention；AUTHOR_NATIVE_KERNEL + roofline | 软件已经分担exp、减少rescale并使用TMEM/2-CTA；强基线必须包含这些和新cuDNN，不能恢复旧FA3或弱Triton来造增量 |

原始链接：[G01](https://augustning.com/assets/papers/llmcompass-isca-2024.pdf)、[G02](https://arxiv.org/html/2502.18403v1)、[G03正式版](https://www.usenix.org/system/files/osdi26-soi.pdf)、[G04正式版](https://www.usenix.org/system/files/osdi26-qiang.pdf)、[G05](https://arxiv.org/html/2409.01141v1)、[G06](https://arxiv.org/html/2603.05451v1)。每组模型/输入/precision/指标/控制/未披露字段详列TSV。G03使用正式OSDI稿的数值与限定；不以旧preprint较宽的概括覆盖终稿。

### 三项直接纠偏

- G01的TableIV是多资源联合设计，不应与Fig9单buffer扫描混为一个单变量因果。我们用现有Poppler渲染并视觉核了作者PDF第9页Fig9/TableIV；表中die、内存、带宽、阵列与容量多项一起改变，不能把性能/成本改善全部归于DRAM或SM数量。
- G06正文§5称B200，AppA.1却写B100 180GB SXM6；同稿还同时列cuDNN9.13与9.19.1.2。**设备标识冲突未解决**；不能据其峰值数字校准某个B200。正文Fig4已说明较新cuDNN吸收部分技术，不沿用“FA4必然胜cuDNN9.13”的排序作为今天强基线。
- P08 VTC的Table1明确LLM对象为decoder layer，不能将作者称的end-to-end benchmark误写成完整8B请求；G04的“端到端operator”同理。G05有真实模型尺寸但合成长度/到达和uniform routing，不等于真实请求/自然专家激活。

## 3. 资源分类与因果约束

| 资源解释 | 本轮来源约束 | 后续必须分离的反事实 |
|---|---|---|
| 容量 | G01、LIA/InstAttention SCREEN、A70静态容量 | 固定请求/批次能否驻留，与加容量后扩大batch的策略收益分别记账 |
| 外部带宽/通信 | G04、G05、NanoFlow SCREEN | 固定模型/算法/plan/容量，只改链路服务；不能把新增近存计算与带宽收益合并归因 |
| 片上吞吐与依赖 | G02/G03/G06 | TC、exp、FMA/issue、SMEM/TMEM服务和同步分别约束；增加SM数量不是独立提高其中一种 |
| 并发/执行粒度 | G03/G04及A70-M | “可以重叠”“最优SM份额”与实际剩余关键路径不同；host排队变化单列 |
| CPU—GPU | LIA/InstAttention SCREEN | CPU算力、DDR/CXL容量与带宽、PCIe搬运分别控制；没有全文不填公平baseline结论 |
| 模拟器误配 | G01/G02/G05与旧C16/AWMA | 旧架构验证不支持自动预测tcgen05、TMEM或SM100同步；模型缺对象时必须STOP |

本轮没有硬件资源扫描、模型运行或仿真。论文作者的仿真保留为仿真，作者native kernel不升级为应用native；我们的算术也不升级为仿真。

## 4. A70四个0的有效边界

| A70 authority | 排除的同质方案 | 没有控制本问题的变量 |
|---|---|---|
| M：f2d6324da298be26f39cda427f3e7db1a7e7031d | 仅新增chunked P/D混合、动态SM划分或普通长KV感知 | 固定预算下SM内部非矩阵资源与TC比例；DuetServe是SM集合分配，不是增加exp服务端口 |
| N：5076223db5db0256fd0ccacec50b5347a0cab8c5 | 泛称hybrid不能复用、无人研究逐token state写回 | 强kernel后完整Prefill中attention与GDN/FFN分母的边际资源代价 |
| O：94ca01df352cf4cf707cd35e5f9f63d4eff014c6 | 普通token-sort/grouped/fused专家执行改名 | 未测现代强attention流水的片上服务资源配比；本题不恢复MoE专家热点机制 |
| P：f2399777a30f4fdafa26858b3cd418e497538db2 | 视觉Graph、embedding缓存或encoder分离能力 | 没测同预算SM专用资源价格；本题只走文本，不展开视频或视觉阶段 |

旧C16 grouped Split-K/FFN双流与AWMA翻译结论只在其冻结对象成立。保留图谱P13的资源扩展方法，但不继承其模拟器参数或执行许可。A70的0并没有证明所有硬件配比都无空间；同样，“没测”也不证明本题会为正。

## 5. 唯一推荐问题 H73-Q1

**问题：强算法补偿之后，增加exp/片上服务而让渡TC预算，能否在完整通用模型Prefill取得正净效应？**

主对象是[Qwen3-8B固定config](https://huggingface.co/Qwen/Qwen3-8B/blob/b968826d9c46dd6066d109eabc6255188de91218/config.json)：36层、Q32/KV8、head_dim128、BF16、全注意力。研究真实文本问答的完整Prefill，不缩小模型、不更换attention掩码或删FFN；输入候选仅要求合法自然文档问答，当前没有下载/冻结具体语料、token或质量门。输入身份是未来资格门，不等W交付才收口，也不自行扩成Workload-first调查。

最强软件：固定FA4内核源 e9d8944c855489e03c66262d07ba4c81d9d8dd31 的sm100 forward与softmax；配对当时最佳且合法的cuDNN/FA4完整路径，保留既有exp emulation、conditional rescale、TMA/TMEM和适用的2-CTA策略。正式基线在探索样本选定后冻结；不能只比教程Triton。当前源码已按is_sm103、causal、head_dim选择exp仿真策略；这证明软件在适应资源差异，**不证明新硬件增益为零**。[S01](https://github.com/Dao-AILab/flash-attention/blob/e9d8944c855489e03c66262d07ba4c81d9d8dd31/flash_attn/cute/flash_fwd_sm100.py)

与G06的区别不是重新发现不对称扩展，而是同时计入：软件可把exp移到FMA；硬件让渡TC的全模型机会成本；每种硬件点重新选择合法pipeline；以及实际attention占完整Prefill的权重。与G03的区别是改变机器资源约束而非在固定机器中再次搜索调度。此区别尚须协调者独立抽核，不宣称论文新颖性或最佳硬件机制。

两个相反预测：

1. **硬件残余预测**：在最优合法kernel已选后，exp或SMEM/TMEM服务仍暴露；适量资源让渡能降低完整Prefill，且单独加TC的收益小于匹配服务资源的收益。独立模型中收益随可测attention份额/资源压力变化，而非随品牌命名变化。
2. **软件/机会成本预测**：FA4/cuDNN的补偿已使该资源不暴露，或者让渡TC拖慢FFN/投影、GDN及准备阶段；kernel局部改善不能覆盖全Prefill损失。此时关闭硬件候选；若单靠参数/布局即可改善，归SOFTWARE_OPPORTUNITY。

## 6. 已做的最小纯CPU诊断

只以整数/有理数重算G06的简化tile服务需求，未import模型、未调用编译器/求解器/模拟器。M=N=d=128时，论文式的MMA、EXP、SMEM服务下界分别为1024、1024、768个抽象cycles。单独把TC或EXP能力翻倍，三项max下界均不变；同时翻倍才从1024降到768。**4/3只是两个简化下界的比值，绝非speedup上界或预测。** 它漏掉FMA、TMEM、寄存器、barrier、HBM、causal边界与软件exp分担；当前强软件后的数值必须重建。

另做无量纲净收益检查：设attention原占比f、其变化后加速s、其余部分退化r，则归一化串行时间为f/s+(1-f)*r。一个纯说明例s=1.2、r=1.05需要f>3/13才净受益。f/s/r均不是本机或作者Qwen测量；并发、重叠时必须改用合法关键路径，不直接相加模块时间。该检查帮助拒绝局部收益冒充全模型收益，不设统一百分比晋升门。

## 7. 轻到重的资格路径——全部PROPOSAL_NOT_AUTHORIZED

1. **CPU资格先行**：冻结模型/权重revision、自然文本合法来源、tokenizer/掩码/position、BF16及数值/任务质量门；从固定kernel源码确定每个backend的实际资源/shape支持。先核真实输入和强backend可配对，再考虑资产；无资格不下载。现有CPU算术只支持提出问题。
2. **一次最小native诊断**：另获批一张真正SM100的B200，建议8个自然请求/模型，探索/holdout各4，覆盖自然落在4K/8K附近的请求，B1为主、最多B2，不为凑长度复制token。固定输出目标，逐算子配对同一保存真实Q/K/V只是诊断，完整Prefill与request wall才是主分母。比较最多两条强合法路径；测未插桩完整wall、另记kernel/准备与已知pipeline参数。SFU/片上服务的独立计数若需要Profiler，必须另获授权；仅时钟敏感性或更换kernel不能直接证明某硬件单元因果。
3. **native否定优先**：强软件重调后无可重复暴露、纯软件已消除差异、准备或其他层抵消、数值/质量失败、成本不足区分竞争解释，即STOP。基准可能为0/负，不要求先有硬件收益。
4. **才可研究资源反事实**：校准目标ISA/TMA/TMEM/同步和实际kernel，固定容量/带宽/频率/请求/质量；独立改变TC、exp、FMA/issue和SMEM/TMEM服务后逐点重新调优。先做非物理理想资源灵敏度并明确标记；再用真实面积/功耗约束考察可行Pareto点。旧Accel-Sim配置不支持所需对象时为MODEL_MISMATCH，不运行后再补解释。
5. **独立验证/PPA**：建议Qwen3.5-4B纯文本完整模型作独立对象（固定revision沿A70-N），其full attention较少、还含GDN，可验证全模型机会成本预测；head_dim256实际强后端和模型质量要独立过门，不拿d128重放冒充。保留未选参自然文档；PPA必须包括新增单元/服务端口、布线、容量、时钟和同步成本，不用峰值单位数线性估计芯片成本。

未来资源建议仅供新Goal审查：native B200单卡排他≤20分钟、CPU≤2、host RAM≤32GiB、VRAM预算≤40GiB（需实际峰值资格）、新增盘≤24GiB、模型/输入下载≤20GiB。B200必要性来自TMEM/tcgen05/资源比例的科学对象，不是将16GiB 4080换个品牌当等价验证；4080最多承担另审的软件可移植性局部诊断，不能证明本SM100硬件问题。模拟器/PPA预算当前不估为“已可行”，须等native与模型资格后另审。无自动后续。

## 8. 反向自审与终态

- 是否只换模型？否：核心是同预算下资源互换、逐硬件点强软件重调及全模型机会成本；Qwen只作真实结构锚点。
- 软件最强路径是否兼容？源码有候选，但实际build、cuDNN选择、2-CTA/GQA/causal支持和数值仍待未来检查；不声称部署已合格。
- 是否必须真实输入？是；scalar distortion、随机张量和模型shape只够结构诊断，不能替代任务质量或主分母。
- 是否一次小实验可拒绝？可在合法强backend配对与全Prefill成本门拒绝；若仍不能区分，保留UNKNOWN，不硬升架构。
- 是否遗漏更直接反证？FA4和Twill都已处理大量非矩阵开销；G04已有SM配额/通信backend自动调优。因此未另荐“动态分SM”“通用融合/队列”或“更多带宽”作为第二题。
- 是否跨预算？当前未跨。未来B200/Profiler/下载/模拟器/PPA均明确另审，本条问题卡不是执行合同。

本轮科学交付已收口，状态SOURCE_QUESTION_READY_FOR_CROSS_REVIEW。没有HARDWARE_HEADROOM_PROVEN或GPU_NEGATIVE_MEASURED。四份文件语法/引用/去重与路径白名单自审后提交；push、单次fetch-back核commit/tree/四blob与SHA、clean后STOP。最终身份写私有回读收据及用户回执，避免RECEIPT自引用。
