# Round09｜宽范围支线：执行组织、表示生命周期与训练新成本

日期：2026-09-27。维护：ChatGPT。**只做文献与研究设计；未启动新GPU任务、未改Lane F/R81和Lane G/R82。**

## 1. 阅读与交付口径

27项核心工作：19项正文关键方法/实验/局限章节；1项部分正文（Ekka）；6项原始摘要；1项作者artifact/发表元数据（Coruscant）。不是27篇全文精读，不是27个复现实验，也不把跨轮次计数相加为去重论文数。

扩展证据表有53条：39条实验/分析组、8条源码或方法审查、6条摘要证据。按原文对象、输入、变化/控制变量、测量层次与解释边界拆开。没有用第三方AI论文总结补未取得的正文。

本轮本地资料包包含详细报告、27项来源JSON/CSV、53条TSV证据、4项artifact状态、机制借鉴与后备问题卡、文件校验和发布记录。此远端文件保存研究结论与原始来源，便于后续续接。没有运行论文代码、下载模型、安装GPU环境、占用109、启动174/Accel-Sim或新增第三个Codex执行窗口。

## 2. 原始来源登记

KEY=正文关键章节；PARTIAL=部分正文；ABS=原始摘要；ARTIFACT=作者源码说明。以下“借鉴/边界”不等同论文已证明未解决问题。

| ID | 来源/指定版本 | 深度及位置 | 核心能力与证据边界 |
|---|---|---|---|
| R901 | Twill，2512.18134v1 | KEY，§3–6，尤其5.4/6.1 | SWP与warp分工联合约束求解；最优性限机器模型/程序类；v1性能代码仍人工lower到CUDA，tile并非自动联合搜索。OSDI26元数据不代替最终稿阅读。 |
| R902 | Tawa，2510.14719v2 | KEY，异步引用/依赖划分/§V-A | 有限缓冲full/empty生命周期；H100 GEMM/Attention，部分缓冲与流水参数人工调节。 |
| R903 | Exo-GPU，2609.16389 | ABS | 显式并行/同步变换与验证；未核完整验证器覆盖和实验。 |
| R904 | CAKE，2608.12629 | ABS | compiler-agent共同改IR/规则；摘要中一项搜索预算8000万tokens，不能据此继承低成本复现预期。 |
| R905 | Syncopate，OSDI26 PDF | KEY，设计/§6/附录及PDF图表截图 | chunk通信图与compute tile协同；4/8 H100，模型派生算子形状不等于完整大模型；同高层计划不同lowering有助因果对照。 |
| R906 | Entwine，2609.11562 | ABS | 规则化tile生产节奏与通信资源共享；全文未取得。 |
| R907 | AsyncSparse，2604.17834v1 | KEY，§III–IV | BCSR/WCSR异步SpMM，414 SuiteSparse/H100；其persistent计数器方案未超过静态拆分，不能泛化成所有动态调度无效。 |
| R908 | Fused3S，2505.08098v1 | KEY，格式/融合/§4 | 融合SDDMM-softmax-SpMM，A30/H100图计算；部分精度不同，forward不代替backward。 |
| R909 | IO-aware GNN，2605.31500v1 | KEY，实现/实验 | 缓存描述符、workspace、转置与归一化，按度数/特征组织归约；强库基线不是每次重做准备。 |
| R910 | N:M graph reordering，PPoPP25 / 10.1145/3710848.3710881 | ABS，PNNL机构页 | 图重排适配Sparse TC；尾部、转换摊销未核，不能推断任意图无代价变2:4。 |
| R911 | Celty，2608.01536v1 | KEY，RLC-CSC/软硬件/质量 | 双稀疏SpMspV；A5000软件、native删除/替代操作的硬件投影与局部RTL是不同证据层；剪枝质量单列。 |
| R912 | Coruscant，MICRO25 / 10.1145/3725843.3756065 | ARTIFACT | 有kernel评估入口，端到端模型准备/集成/脚本仍Coming Soon；正文未取得，不据第三方填机制。 |
| R913 | MUSTAFAR，2505.22913v2 | KEY，剪枝/实现/质量性能 | bitmap稀疏KV，性能RTX6000 Ada；剪枝不是exact dense attention，质量模型集与性能模型集不同。 |
| R914 | HiMuon，2606.27216v1 | KEY，§4/§6及README | tile-local有限NS丢弃跨tile谱耦合，明确改优化器；1000步单seed训练不能当完整收敛。源码说明已有batch/图捕获。 |
| R915 | Muon²，2604.09967v1 | KEY，方法/谱/训练 | 二阶矩预条件与NS更新；减少迭代是算法变化，真实momentum不等于模型权重。 |
| R916 | SparseRL-Sync，2605.07330v1 | KEY，表示/同步/实测与投影 | 同步BF16变化稀疏而FP32主权重仍稠密变化；106B/128H100实测，671B时延与额外高压缩估计需单列。 |
| R917 | QeRL，2510.11696v1 | KEY，§3/质量与性能 | H100经Marlin执行NVFP4权重，非原生FP4 TC；量化噪声影响探索，不能归纯kernel。已核ICLR26元数据，正文仍v1。 |
| R918 | EcoRec，SC24 / 10.1109/SC41406.2024.00055 | ABS，会议页 | TT压缩embedding收缩/微batch，扩展至32GPU；全文与可运行artifact未核。 |
| R919 | FlowTT，2609.03459 | ABS | TT索引前缀共享中间收缩、融合/persistent；Meta合成输入不是生产请求；完整摊销边界未核。 |
| R920 | Anatomy of SDC，2605.04213v1 | KEY，门级方法/错误分布 | 63微基准及门级注入，错误常为finite和结构化多bit；条件错误分布不是现场率。 |
| R921 | LLM-PRISM，2604.10390v1 | KEY，§III–VI | RTL模式→训练软件注入；7664次GPT-2规模实验，格式/位置/注入率；不等于现场GPU故障统计。 |
| R922 | Exploring SDC in LLM Training，2604.00726v1 | KEY，注入/训练/恢复 | 单L40S、HMMA输入操作数注入与寄存器恢复；检测/重算实验，压力注入率不等于现场率。 |
| R923 | Ekka，2606.04594v1 | PARTIAL，前部方法/动机 | 语义组件和中间态对齐定位实现差异；90 issue样本不代表缺陷流行率；完整评估未核。 |
| R924 | Sim-FA，2605.00555v1 | KEY，事件模型/校准/验证 | H800 FA事件模型，不是完整SASS；部分计算为固定周期段，映射假设不能当硬件事实。 |
| R925 | DECA，2505.19349v2 | KEY，三资源模型/接口/§8 | 存储-向量解压-矩阵乘共同建模；CPU仿真/局部成本，不是GPU实测。 |
| R926 | StreamTensor，2509.13694v2 | KEY，流式类型/实验 | FIFO、融合、遍历与资源共同设计，U55C FPGA；精度不同的GPU比较不能归硬件单因素。 |
| R927 | Chameleon，2411.17741v2 | KEY，调度/cache/负载/实验 | LoRA adapter缓存与非抢占队列；Azure仅提供长度，Poisson到达与adapter分布另构造；不是L2 cache机制。 |

## 3. 跨论文机制归纳

### 3.1 执行计划也应成为研究对象

Twill/Tawa说明流水和warp分工不能脱离中间值活跃区间；Syncopate/Entwine说明数据何时产生、消费和释放，与总字节数一样重要。可借鉴有限buffer、ready/consumed分离和生产节奏控制，不直接移植Hopper/Blackwell接口到SM89。

对R82的价值是后续解释和强基线资料，不要求正在运行的Lane G换工具栈或重做实验。Exo-GPU/CAKE暂作为验证/编译器方法线索，不根据摘要建立完整实验合同。

### 3.2 稀疏要同时看结构寿命和数值寿命

AsyncSparse的动态取任务不胜静态是一个有用反例；不能因FlowTT采用persistent就判哪篇矛盾，两者任务粒度和共享方式不同。Fused3S与IO-aware GNN则提醒，融合、准备缓存、重排和不规则长尾都需计入。

我们的推导：对固定结构，预处理可多次摊销；只更新值和改变结构应分别触发失效。简单无重叠模型为 `T_total(R)=T_prepare+R*T_execute`，但不能把独立分项时间机械相加成异步critical path。新问题若只相当于“缓存cuSPARSE描述符”，已有能力已覆盖。

### 3.3 训练状态不是forward资产的替身

HiMuon/Muon²的真实对象是momentum及有限矩阵映射。可另问固定映射下的执行代价，但不能把tile-local更新当作完整Muon的等价优化。模型权重与随机矩阵不足以代表自然momentum分布。

SparseRL-Sync表明“未变化”取决于表示：低精度同步权重可不变，FP32主权重仍变化。按BF16值+int32索引的简单编码，变化比例ρ时payload比约 `1/(3ρ)`；ρ=1%约33倍，额外metadata未计。更高比率需其他密度/编码，不是自动100倍。此公式是核算，不是新增测量。

### 3.4 非原生低比特平台的边界需要分层

QeRL在H100上以Marlin执行NVFP4权重，说明应区分存储格式、软件解码、原生TC算术。前两项可在非Blackwell形成真实实验；最后一项不能软件模拟后称native。该说明不重启R55原生NVFP4问题，也不声称4080已具备QeRL资格。

### 3.5 可靠性与软件数值差异不可混用

Anatomy/LLM-PRISM/训练SDC工作针对物理故障模型，Ekka针对实现差异定位。finite、短greedy一致、相近loss各自只提供有限证据。应该按研究对象选检查：复制状态可逐bit、layout置换可整数唯一编号、算术重排按预先定义数值/应用合同；物理错误另需注入模型。

不是把验收再加重，而是避免所有任务都用一套top2/top8门槛。没有物理故障资料时，软件注入只是声明范围内的敏感性分析，不能称真实4080缺陷率。

### 3.6 迁移跨架构思想，不迁移性能数字

DECA的存储/解压/矩阵三速率模型、StreamTensor的流式生命周期、Sim-FA的局部事件抽象都能启发设计。具体CPU/FPGA/多GPU吞吐与PPA不可继承。Chameleon也提醒“真实输入”要细到字段：长度真实不意味着到达时间和adapter选择真实。

## 4. 后备问题卡：非执行Goal

**Q91：固定矩阵优化器更新的执行代价。** 先核作者batched/graph强实现，再冻结一个真实optimizer状态与有限更新映射，尝试有界中间态/调度变化。需真实momentum资产，当前未采集。若收益来自改变NS迭代、tile-local谱耦合，转为算法变量，不称等价硬件优化。状态 `RESERVE_SOURCE_AND_INPUT_DESIGN`。

**Q92：稀疏结构寿命与表示准备摊销。** 分结构不变、仅值变化、结构变化；计准备、更新、执行及存储。必须代表成熟库缓存准备能力，并与R81索引/R82片上转换去重。若只反复重做本可缓存的准备，软件基线已能解决。状态 `RESERVE_AFTER_F_G_DEDUPLICATION`。

**Q93：TT部分共享后的中间值寿命。** 部分前缀共享已被FlowTT覆盖；下一步只补全文、artifact、输入/TT-rank和训练失效规则，不下载大推荐数据集。状态 `FULLTEXT_AND_ARTIFACT_REQUIRED`。

这些不是三个已证明的新机制。允许文献驱动小原型帮助发现现象，不要求提前证明5% headroom；扩大投入再要求强基线、有限资源、因果区分与留出验证。当前不启动第三个GPU窗口。

## 5. Artifact公开状态

- Celty `RuokaiYin/Celty/README.md` blob `a7c810f926479a980fcb79733606c67bde8a3186`：代码待上传占位；没有可复现实验已运行的证据。
- Coruscant `dhjoo98/coruscant/README.md` blob `4f1182babc9bace22738fb22e4dc9a6b424c7765`：kernel入口；E2E准备/集成/脚本Coming Soon。
- Syncopate读取ref `ce2b13e496eb6629ab42aac2aec1d9e31e084ba6`，README blob `83ee9be179ff742e3902176fe4fb0eb1ec2350d1`；其README将AE ref写为`9c4c0db9919a6243df41cc5033000797dc6ce901`。保留与PDF附录差异。CPU测试未执行。
- HiMuon `tang0389/himuon/README.md` blob `2f88d617ac6af0c030366cb795c33f774ace265e`：跨层batch、完整optimizer CUDA Graph、参数bank分片和单卡/DDP/FSDP。未运行。

未绑定commit的源码读取保留blob与日期，不捏造当时HEAD；README能力不当作本机资格PASS。

## 6. 原始来源

- R901 https://arxiv.org/html/2512.18134v1
- R902 https://arxiv.org/html/2510.14719v2
- R903 https://arxiv.org/abs/2609.16389
- R904 https://arxiv.org/abs/2608.12629
- R905 https://www.usenix.org/system/files/osdi26-qiang.pdf
- R906 https://arxiv.org/abs/2609.11562
- R907 https://arxiv.org/html/2604.17834v1
- R908 https://arxiv.org/html/2505.08098v1
- R909 https://arxiv.org/html/2605.31500v1
- R910 https://www.pnnl.gov/publications/accelerating-gnns-gpu-sparse-tensor-cores-through-nm-sparsity-oriented-graph
- R911 https://arxiv.org/html/2608.01536v1
- R912 https://github.com/dhjoo98/coruscant
- R913 https://arxiv.org/html/2505.22913v2
- R914 https://arxiv.org/html/2606.27216v1
- R915 https://arxiv.org/html/2604.09967v1
- R916 https://arxiv.org/html/2605.07330v1
- R917 https://arxiv.org/html/2510.11696v1
- R918 https://sc24.supercomputing.org/proceedings/tech_paper/tech_paper_pages/pap518.html
- R919 https://arxiv.org/abs/2609.03459
- R920 https://arxiv.org/html/2605.04213v1
- R921 https://arxiv.org/html/2604.10390v1
- R922 https://arxiv.org/html/2604.00726v1
- R923 https://arxiv.org/html/2606.04594v1
- R924 https://arxiv.org/html/2605.00555v1
- R925 https://arxiv.org/html/2505.19349v2
- R926 https://arxiv.org/html/2509.13694v2
- R927 https://arxiv.org/html/2411.17741v2

完整paper/source registry、experiment evidence和后备问题卡见本轮交付资料包。accepted实验分支、raw与正在运行的F/G任务不改动。
