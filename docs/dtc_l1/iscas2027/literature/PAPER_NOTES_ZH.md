# 论文阅读笔记｜第一轮

日期：2026-09-26。P编号是阅读索引，不是新的工程任务名。来源使用作者公开稿或正式出版社页面；章节号随本页所链接版本。除特别标注外，实验数字不在此转抄，避免把不同平台和统计口径的加速比放到同一排名中。

## 阅读约定

“原文”部分只写本轮核读支持的内容；“对DTC的比较”是ChatGPT推断，不等同于作者说法；“待补”是阅读缺口，不表示原论文没有这部分。FULLTEXT_TARGETED仅表示取得全文并定向阅读关键部分，不表示全文逐句审计或复现。

<a name="p01"></a>
## P01｜NuRAPID：解耦用于数据位置与访问距离

**书目/状态。** Zeshan Chishti、Michael D. Powell、T. N. Vijaykumar，MICRO2003，*Distance Associativity for High-Performance Energy-Efficient Non-Uniform Cache Architectures*。FULLTEXT_TARGETED。

**原文依据。** [作者PDF](https://engineering.purdue.edu/~vijay/papers/2003/nurapid.pdf)，§2.1–2.2及后续放置、替换讨论；架构图所在PDF第3页已查看。它将组相联Tag查找与非均匀数据阵列的位置分开，用前向/反向指针关联两者。访问距离管理与真正驱逐数据是不同操作；将经常使用的数据放到较近位置是重要目标。评估对象是大型非均匀缓存，不是GPU的PIB或缺失指令队列。

**对DTC的比较〔推断〕。** 这已足以约束“通过指针分离Tag与Data是新方法”的泛化表述。DTC应比较的是：Tag地址映射改变以后，旧物理行为什么仍需保留、由谁引用、何时释放。不能仅以CPU/GPU不同跳过结构性先例，也不能从本轮阅读断言NuRAPID的全部未完成事务处理均与DTC相反。

**写作用途/待补。** 用作解耦映射的历史基础。引用前补核精确页码/DOI即可；若主张其生命周期规则与DTC完全不同，还需定向核其miss/replacement边界。硬件启发是把指针、反向定位和数据移动/布线成本计入，不只统计数据SRAM。

<a name="p02"></a>
## P02｜V-Way：解耦用于按需相联度

**书目/状态。** Moinuddin K. Qureshi、David Thompson、Yale N. Patt，ISCA2005，*The V-Way Cache: Demand-Based Associativity via Global Replacement*。DOI：10.1109/ISCA.2005.52。FULLTEXT_TARGETED。

**原文依据。** [作者PDF](https://hps.ece.utexas.edu/pub/qureshi_isca05.pdf)，§3.1–3.3、全局替换和评估/代价段落；PDF第4页的结构与操作已查看。Tag项多于数据行，利用双向定位使组相联Tag与全局数据分配不再一一绑定，从而改变各组能够实际利用的数据容量。数据复用计数服务于替换。实验围绕CPU缓存和SPEC工作负载，并有缓存代价建模。

**对DTC的比较〔推断〕。** DTC常见“物理行多于可搜索Tag”的比例与它不同，但比例反过来不是充分的新颖性证明。应比较分配/替换对象及旧消费者保护。V-Way的复用计数不能因名称相似而写成DTC的在用消费者引用计数。

**写作用途/待补。** 放在映射解耦一组，说明关联方式与数据替换自由度已有基础。未完成其所有瞬态miss状态的逐状态核对；比较矩阵不把这项缺口填写为“不支持”。

<a name="p03"></a>
## P03｜Locality-Driven Dynamic GPU Cache Bypassing：直接相关的Decoupled L1D

**书目/状态。** Chao Li、Shuaiwen Leon Song、Hongwen Dai、Albert Sidelnik、Siva Kumar Sastry Hari、Huiyang Zhou，ICS2015。DOI：10.1145/2751205.2751237。FULLTEXT_TARGETED。

**原文依据。** [NVIDIA条目](https://research.nvidia.com/publication/2015-06_locality-driven-dynamic-gpu-cache-bypassing)；[论文PDF](https://d1qx31qr3h6wln.cloudfront.net/publications/ICS_Cache_Bypassing_2015.pdf)，§4.1–4.3、§5；图6/7、表2/3已查看。文中设计本身称为Decoupled L1D。分离的Tag记录复用频率RC及数据位置Position，Tag覆盖可大于实际数据容量；初次访问可只登记Tag、旁路数据插入，达到复用条件再接纳数据，并用SM dueling控制适用性。

**实验阅读范围。** 核读模拟平台、Tag/Data配置和面向缓存不友好负载的效果口径；作者汇总不能移用为本项目12程序结果。

**对DTC的比较〔推断〕。** 这是必须正面比较的GPU先例。它的RC用于局部性判断，不是DTC中“尚有几个既有消费者”的Ref_cnt。可讨论的区别是过滤/保留可复用数据，与Tag被换出后继续保护旧物理行的不同目标和状态合同；不能简单说“前人只旁路，因此没有Tag/Data解耦”。

**待补问题。** 为正式表格逐项核清旁路返回路径、Tag替换与未完成请求的关系；不能仅凭本轮关键段落断言两种方案没有任何可组合部分。后续的DTC旁路提案还必须对照自身学位论文§4.4。

<a name="p04"></a>
## P04｜MRPB：在进入缓存之前重排与旁路请求

**书目/状态。** Wenhao Jia、Kelly A. Shaw、Margaret Martonosi，HPCA2014，*MRPB: Memory Request Prioritization for Massively Parallel Processors*。DOI：10.1109/HPCA.2014.6835938。FULLTEXT_TARGETED。

**原文依据。** [作者PDF](https://mrmgroup.cs.princeton.edu/papers/mrpb.pdf)，§2的争用分类、§3设计、§4方法及表1。请求优先缓冲位于访问缓存之前，通过分组重排和旁路缓解争用；区分warp内、跨warp/块的来源。原文明确讨论组内保留行、MSHR和miss queue等有限资源导致的阻塞，并研究ATAX、BICG、GESUMMV等程序。评估采用GPGPU-Sim、两种L1基线和PolyBench/Rodinia，不能套用到本项目新轨迹的机制分类。

**对DTC的比较〔推断〕。** 与DTC最接近的是研究问题，而非部件名称。MRPB改变哪些请求以什么顺序进入既有缓存；DTC重组已接纳请求的查询映射、等待元数据及物理行保留。PIB和MRPB都叫buffer并不等价，需比较位置、保存内容和释放条件。

**写作用途/待补。** 是“传统GPU miss处理受结构约束”动机的重要出处，也是未来旁路/节流策略的实质对照。正式论证还要界定各自内存顺序假设；不能把旧文在某输入上的争用归因直接当作我们BICG的答案。

<a name="p05"></a>
## P05｜MeDiC：跨层利用warp间延迟容忍差异

**书目/状态。** Rachata Ausavarungnirun等，PACT2015，*Exploiting Inter-Warp Heterogeneity to Improve GPGPU Performance*。DOI：10.1109/PACT.2015.38。FULLTEXT_TARGETED。

**原文依据。** [原始论文PDF](https://www.pdl.cmu.edu/PDL-FTP/associated/medic-pact15.pdf)，§3.2、§4.1–4.4、§5及部分结果。根据warp的L2命中行为分类，联合决定旁路、插入和内存请求优先级，以免少数长请求拖住较易完成的warp。评估含修改过L2 bank模型的GPGPU-Sim；方法中有每kernel指令上限，不能描述成所有程序完整执行的实机结果。

**版本去重。** [2018作者回顾](https://arxiv.org/html/1804.11038v1)，题为*Holistic Management of the GPGPU Memory Hierarchy to Manage Warp-level Latency Tolerance*，明确回顾PACT2015工作；不计为另一项独立机制。

**对DTC的比较〔推断〕。** 平均请求数或平均延迟不一定代表决定warp完成的请求。可用它解释为何本项目要区分总量、时序和完成条件；不能据其L2排队分析宣布DTC也具有同一个物理瓶颈。

**写作用途/待补。** 放在跨层策略一组。对DTC+MeDiC只能说存在组合研究空间，不能声称已经证明正交或无成本兼容。

<a name="p06"></a>
## P06｜SACAT：旁路、并发度和索引共同处理争用

**书目/状态。** Mahmoud Khairy、Mohamed Zahran、Amr Wassal，IEEE TPDS 28(6):1740–1753，2017。DOI：10.1109/TPDS.2016.2627560。FULLTEXT_TARGETED。注意2016是在线发表/DOI中的年份，卷期为2017，不是2021。

**原文依据。** [作者PDF](https://mkhairy.github.io/Docs/sacat.pdf)，争用分析、设计三部分及选择性评估。包括流式感知旁路、基于core sampling的动态warp节流DWT-CS、缓解冲突的PRIC索引。其控制并不只盯住一个队列，而是联合考虑流式行为、并发争用和地址映射。

**对DTC的比较〔推断〕。** 因而“增加并发不总是好”或“自动调warp数量”不能作为新的普遍创新。DTC当前的正反向程序和下游资源干预应定位为本结构的适用性证据。索引冲突、可搜索容量不足和物理行被旧消费者占用不能合并成一个cache-full概念。

**写作用途/待补。** 用作策略组合和争用分类的对照；本轮没有复算其所有基准组合和面积结果。不要把作者论文的程序分类覆盖到本项目，也不据已有组合作品直接生成新的DTC实验矩阵。

<a name="p07"></a>
## P07｜Poise：分别控制活动线程和缓存分配线程

**书目/状态。** Saumay Dublish、Vijay Nagarajan、Nigel Topham，HPCA2019，*Poise: Balancing Thread-Level Parallelism and Memory System Performance in GPUs Using Machine Learning*。FULLTEXT_TARGETED。

**原文依据。** [作者PDF](https://users.cs.utah.edu/~vijay/papers/hpca19.pdf)，整体设计、特征/回归、运行时选择和评估。以活动warp数量与允许缓存分配的warp数量构成二维控制；使用离线训练的回归模型和运行时决策，不是简单单阈值，也不应误写成决策树。评估明确区分训练/测试kernel，并采用模拟和执行上限。

**对DTC的比较〔推断〕。** “学习一个更好的并发上限”已经有强先例。DTC的GPU全局在途请求credit、warp发射数量、允许cache allocation的warp数是不同控制单位；未来比较必须把单位和执行位置讲清楚，不能只把N换名为cap。

**写作用途/待补。** 当前可以引用为并发与局部性联合控制的代表。若开展学习控制，应补读特征成本、跨工作负载验证和失效情形，而不是直接把机器学习作为新颖性来源。正式BibTeX的DOI本轮未核，暂不填写。

<a name="p08"></a>
## P08｜LLaMCAT：2025年已有面向LLM的缓存仲裁和节流

**书目/状态。** Zhongchun Zhou、Chengtao Lai、Wei Zhang，ICPP2025。DOI：10.1145/3754598.3754671。FULLTEXT_TARGETED。阅读[作者稿arXiv:2512.00083v1](https://arxiv.org/html/2512.00083v1)；其页首给出ICPP出版信息，不能只标成“尚未发表预印本”。

**原文依据。** §2.4、§4–6。它利用预期cache/MSHR命中与核心进度进行LLC请求仲裁，配合分层多档节流；特别关注请求到达时机对cache hit与MSHR hit的转换。硬件用Chisel/DC评估，性能采用Timeloop/Ramulator2等组成的研究模型，主要实验针对GQA的QK^T计算配置，不能扩大成真实GPU整模型端到端推理的加速结论。

**对DTC的比较〔推断〕。** 这是当前miss-state/时序讨论不能漏掉的近作。“MSHR命中有价值、请求时序影响局部性、控制注入有利”都不是DTC独有命题。DTC更需说明映射可见期、在途合并和退役但仍存活的物理行之间的差别。

**写作用途/待补。** 适合相关工作及后续AI负载启发，不是当前DTC十二程序的公平实测对手。不要采纳该文对其他模拟器的概括性评价来替代本项目已验证的SASS trace模式；也不要把其算子结果推广为所有LLM。

<a name="p09"></a>
## P09｜RPAWS：2026年的资源压力感知调度

**书目/状态。** Bo Yuan、Sheng Liu、Yang Guo、Zekun Jiang、Jianfeng Cui，IEICE Electronics Express 23(12)，20260028，2026。DOI：10.1587/elex.23.20260028。FULLTEXT_TARGETED。

**原文依据。** [出版社页面](https://www.jstage.jst.go.jp/article/elex/23/12/23_23.20260028/_article/-char/en)；[PDF](https://www.jstage.jst.go.jp/article/elex/23/12/23_23.20260028/_pdf/-char/en)。按I-buffer中指令类型形成计算/访存虚拟队列，再依据ALU/LSU发射资源忙闲选择warp。表1/2、算法和结构已查看；实验是Accel-Sim中的RTX3070配置及九个基准，而不是在硅上测量该调度器。

**对DTC的比较〔推断〕。** 它说明“资源压力感知”这个宽泛说法已有近期工作，但具体观测点是执行单元发射侧，不应写成直接测L2/DRAM瓶颈的工作。未来DTC的生命周期压力策略若存在，必须以不同的状态信息和正确性合同来区分。

**写作用途/待补。** 作为新近调度工作的边界参照，不宜挤占最直接Tag/Data和miss-state先例的版面。其开销估计也不能替代我们自己的RTL/DC。

<a name="p10"></a>
## P10｜CCWS：已核首页，详细阅读未完成

**书目/状态。** Timothy G. Rogers、Mike O'Connor、Tor M. Aamodt，MICRO2012，*Cache-Conscious Wavefront Scheduling*。DOI：10.1109/MICRO.2012.16。**PRIMARY_FRONTMATTER**。

**已核事实。** [原文PDF](https://people.ece.ubc.ca/aamodt/papers/tgrogers.micro2012.pdf)首页与[作者出版目录](https://people.ece.ubc.ca/aamodt/publications.html)支持：利用丢失局部性的检测信息影响wavefront调度，限制部分load发射以保护缓存重用。已足以作为“通过调度平衡并发和缓存局部性”的先例。

**未核范围。** 后续取文/页面展开不稳定；本轮没有完成检测器更新、调度阈值和完整实验方法的逐段核读。因此不填写内部参数、精确硬件状态对照或性能排名，也不把其他文章对CCWS的描述当作其原文。

**对DTC的比较〔推断〕。** 后续若主张全局cap或warp级选择与它不同，必须比较控制粒度与输入信号。当前笔记只约束泛化新颖性，不足以证明DTC全面优于CCWS。

<a name="p11"></a>
## P11｜DL-MSHR：最高优先级全文缺口

**书目/状态。** Yongbin Gu、Lizhong Chen，ICS2019，*Dynamically Linked MSHRs for Adaptive Miss Handling in GPUs*，DOI：10.1145/3330345.3330390。**METADATA_ONLY**。

**已核来源。** [作者目录](https://web.engr.oregonstate.edu/~chenliz/publications.html)及[出版入口](https://doi.org/10.1145/3330345.3330390)。目录链接的[PDF路径](https://web.engr.oregonstate.edu/~chenliz/publications/2019_ICS_Dynamcially%20Linked%20MSHRs.pdf)在本轮读取超时，未获得足够正文。

**现在不能写什么。** 不依据标题就断言它如何划分主缺失项/合并目标，不猜链表节点、动态分配器和面积；其他论文的评价仅作寻文线索。

**需从原文回答。** 哪种MSHR资源可动态共享？如何存地址和消费者？查找/分配/返回关键路径是什么？Tag变化后如何处理未完成请求？何种公平预算和输入证明有效？

**与DTC的关系〔待验证〕。** 它直接接近“以替代状态组织扩展并发缺失”问题，不能因DTC称为无独立MSHR而绕过。当前不具备miss-state方向的完整新颖性结论。

<a name="p12"></a>
## P12｜MiCache：不能因平台是FPGA而忽略

**书目/状态。** *MiCache: An MSHR-inclusive Non-blocking Cache Design for FPGAs*，ACM/SIGDA FPGA2024，DOI：10.1145/3626202.3637571。**METADATA_ONLY**。

**已核来源。** [出版入口](https://doi.org/10.1145/3626202.3637571)的索引题目/DOI；正文未成功取得。作者列表本轮未作完整第一方核对，未加入已核BibTeX。

**需从原文回答。** MSHR-inclusive到底把哪些状态放进缓存？Tag、数据和消费者元数据是否独立？资源不足时的退回路径是什么？流水线、端口和FPGA存储资源怎样计价？

**与DTC的关系〔待验证〕。** 这是审查“去掉独立MSHR、用其他结构承担miss状态”的必要候选。FPGA/GPU差异不构成自动的新颖性证明。本轮不记录任何未核实加速比、面积或具体算法。

<a name="recent-screen"></a>
## 2026外围筛查：只登记，不冒充详细阅读

**R01 TTP。** [arXiv:2605.16253v1](https://arxiv.org/html/2605.16253v1)，*TTP: A Hardware-Efficient Design for Precise Prefetching in Ray Tracing*。本轮只核摘要方向，涉及光线追踪预取；先放图形访存候选，不扩当前DTC实验。

**R02 TileLens。** [arXiv:2607.04031v1](https://arxiv.org/html/2607.04031v1)，*TileLens: Efficiently Using Large-Granularity Memory Systems with Transparent Two-Dimensional Memory Layout*。本轮只核摘要方向，涉及大粒度存储与数据布局；不等同于DTC的Tag/物理行生命周期。

两项都按当前检索到的预印本版本登记，不猜会议接收状态。它们也不说明2026年相关工作已查全。
