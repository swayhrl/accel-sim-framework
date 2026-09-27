# C16文献支线LR05：五篇原文核读与强基线适配边界

日期：2026-09-27。维护者：ChatGPT。

状态：**FULLTEXT_REVIEW_AND_BASELINE_DESIGN_ONLY**。这是原文核读与研究设计，不是实现验收或运行授权。没有启动GPU实验、timing simulation或新的CPU机制实验；没有修改Lane 4、Core、配置、trace或冻结的Lane 3。M1F继续等待原有project-level gate。

## 0. 读取起点与证据层次

远端仓库：`swayhrl/accel-sim-framework`；文献分支：`hrl/c16-chatgpt-literature-notes-v1`。

本轮读取时，远端分支与`c27aaa2569759681dbc6016151c45c30db6c0603`为identical，ahead=0、behind=0。复核README与LR04，接续LR02/LR03的近邻判断，不把旧结论重复算成新发现。

本轮依据用户上传的五份原始PDF，通读正文并重点核对机制、实验条件、相关图表和脚注。不是五个新增研究方向，而是将既有五个条目从摘要/书目或待核状态升级到正文。未运行论文代码，未验证所有CPU策略在C16 GPU上的工程实现。安全论文的攻击部分仅用于理解研究边界，不开展攻击复现。

以下用“作者内容”“项目事实”“我们的推论”“待适配”分开记载。原文页码均指PDF页序，必要时附印刷页码。项目事实来自`C16_AI_WORKLOAD_HANDOFF_CONTEXT_2026-09-27_M1F_READY_LANE4_RUNNING.md`；不以文献代替新的节点receipt。

## 1. 五份输入及阅读登记

| ID | 完整题名 | 版本与重点定位 | 上传文件 |
|---|---|---|---|
| P1 | Security and Performance Implications of GPU Cache Eviction Priority Hints | MICRO 2025，15页；§4.1–4.2、§6、Table 1–2、Fig. 5/8/9，PDF第4、6、7、11、12页 | `3725843.3756116.pdf` |
| P2 | Adaptive Insertion Policies for High Performance Caching | ISCA 2007，11页；§4–6、Appendix A；特别是第5页脚注2、第6页set dueling、第8页bypass比较 | `1250662.1250709.pdf` |
| P3 | High Performance Cache Replacement Using Re-Reference Interval Prediction (RRIP) | ISCA 2010，12页；§4、§5、§6.4–6.8；第9页脚注6、第10页脚注7 | `1815961.1815971.pdf` |
| P4 | SHiP: Signature-based Hit Predictor for High Performance Caching | MICRO 2011，12页；§3、§4、§5.1、§7；第3页Fig. 1/Table 3，第9页采样与计数器变体 | `MICRO11_SHiP_Wu_Final.pdf` |
| P5 | PIPP: Promotion/Insertion Pseudo-Partitioning of Multi-Core Shared Caches | ISCA 2009，10页；§3–6；第5页正文与第7页Table 2/正文的参数差异 | `1555815.1555778.pdf` |

PDF SHA-256：

```text
338191801fe782bd919791a39f8d11d753d13efb16d9903e2f297ce294c20c4c  3725843.3756116.pdf
7469a0bc878628a9f677c15e8467cdf053bb0fa0c503497423109013969b8b4b  1250662.1250709.pdf
2b324753497ce067df3618db7940b4f87c99a9eec13d5586f01e55e35d365c5d  1815961.1815971.pdf
f62ae510051f5071b74a4dea4f61173e09de3b53a946b9ecf15f3a1bab3f2ac6  MICRO11_SHiP_Wu_Final.pdf
19261dccad4fe088e7b8c76a0a51f9c351dd623bb963c25416713d70599b1b26  1555815.1555778.pdf
```

本轮直接查看了上传内容中的页面图像，并对P1第7/12页、P2第5页、P3第10页、P4第3页、P5第7页另行本地渲染复核。未从图柱高度估计未披露的精确性能值。原PDF不提交文献分支。

## 2. 本轮真正改变的判断

1. **GPU的3/12条不是无条件的占用硬上限。** P1区分空set装入evict_last与混入evict_normal后的可靠保留数量。还区分incoming请求类型；不是简单地给每条line一个固定优先级，然后永远替换最低优先级。
2. **RRIP已明确提醒大line/sector产生的“false temporal locality”。** 原文脚注要求区分不同sector的空间访问与同sector重访。这是GPU适配必须处理的语义问题，不是增加两个RRPV位就完成移植。
3. **BIP不是“每次访问独立抽签保护”。** P2实际报告的主要实现使用按miss递增的模计数器，选择每2^n次中的一次高位插入；策略不在每次hit时重新选保护资格。
4. **SHiP训练归因于插入signature，且不预测复用发生的时间。** 具体更新顺序已经能从原文明确，但这不证明它在C16会失败。
5. **PIPP同时改变插入和命中提升，且本来允许借用。** 不能将它简化成“前人静态切way”；其参数表存在需保留的原文不一致。

## 3. P1：GPU eviction hints的实际语义与适用范围

### 3.1 平台与接口

**作者内容：**§4默认结果主要来自RTX3080、CUDA 11.6、driver 510.39.01。Table 1还列出A40、RTX4090、A100多GPU系统。RTX4090驱动范围列为535–570.x。作者声明没有测所有GPU×driver组合。[P1 §4、Table 1、§4.2.5]

Table 1共列出三个单GPU配置和一个多GPU配置；§4开头的“三个系统、两个单GPU”概括与表不一致。本记录按表逐项登记，不替作者补造完整测试矩阵。

**项目事实：**C16 native authority是RTX4080 / R580.178.04。该组合不在论文列出的测试范围内。

**边界：**不能将论文的535–570分支结果直接外推成“我们的4080/R580每set只能保护3条”。这篇文章也没有给出C16的`cudaDeviceSetLimit`、access-policy window、hitRatio配置的逐项对应实验。Listing 1展示的是PTX `createpolicy.range`配合`ld.global.L2::cache_hint`。全文检索未找到上述runtime配置或fractional跨token选择相关性的实验说明。[P1 §2.3/Listing 1]

### 3.2 必须区分三件事

| 实验条件 | 作者报告 | 不能改写成 |
|---|---|---|
| 单条evict_last与普通数据竞争 | 低占用下普通访问不能淘汰它；普通load/store重访不清除其evict_last状态 | 任意数量target都永不被ordinary影响 |
| 从空set装入evict_last | 默认配置下可达到16条；到达全满有特殊装入行为 | evict_last的物理占用最多12条或3条 |
| 多条evict_last与evict_normal混合 | 旧driver下12条可可靠避免被normal淘汰；测试中的535–570分支为3条 | 任何环境固定切成12/4或3/13个物理way |

来源：P1 §4.2.1–4.2.5、Fig. 5、Table 2，PDF第6–7页。

**请求方向也重要。** §4.2.3在12条last/4条normal的混合状态中报告：装入新evict_last选择整个set的LRU行；装入evict_normal则依当前last数量，选择normal或last组中的候选。故高优先级新数据本身可以冲刷旧高优先级数据。[P1 Takeaway 8]

**我们的推论：**“总容量能放下”“normal不能驱逐部分target”“新target能否挤掉旧target”是不同能力。P_all/P_stable应明确叫理想化优先级能力对照，不叫已复现NVIDIA。若未来要建立文献反推的硬件模型，应独立命名、绑定论文平台与请求规则；本轮不增加该模型。

### 3.3 性能实验究竟证明了什么

§6.1以同set两类访问改变标记数量与访问频率比例，说明二者共同决定失效；Fig. 8来自RTX3080/driver510，不是R580。§6.2评估PageRank、BFS、FC、RNN，在5MB L2的旧driver平台扫描0–5MB标记量，正文报告最佳点约3.75MB，继续增加标记量收益下降。作者对新driver的3/16最佳比例使用的是可能性表述，而非另一套完整应用曲线。[P1 §6、Fig. 8–9]

原文没有在该节完整给出每项应用的模型/图输入规模、逐层对象清单、完整kernel实现与重复测量统计。因此不能把FC/RNN当成已经覆盖我们的自然低比特LLM decode，也不能从图复造一张精确数值表。

**研究影响：**“扩大priority coverage反而退化”已有实测先例。C16的native抵消仍不能据此命名为该文阈值问题；原有`unique microarchitectural cause = UNESTABLISHED`保留。

## 4. P2：LIP/BIP/DIP的原始规则

### 4.1 原文机制

- LIP：新行插入LRU端；真正命中后提升到MRU；victim仍选LRU。
- BIP：多数新行插入LRU端，少数插入MRU端，使已保留子集能逐步适应工作集变化。
- DIP-SD：两组leader sets分别执行LRU和BIP，PSEL根据两组miss计数选择follower策略；不是另建两套完整cache再用oracle挑优。[P2 §4–5]

默认正文参数：BIP的epsilon=1/32；每种策略32个leader sets；10-bit PSEL；原1024-set配置使用complement-select。LRU leader miss增PSEL，BIP leader miss减PSEL；高半区选择BIP。[P2 §5.2–5.3]

### 4.2 事件选择不等于独立随机访问

PDF第5页脚注2明确：作者同时尝试`rand`与1-out-of-2^n计数器实现，效果接近；论文报告采用后者。计数器每次cache miss递增，计数值为零时高位插入；epsilon=1/32对应5-bit计数器。[P2 §4.4、§6.4]

**对C16：**BIP的事件依赖不等于每次hit也重抽。我们的stable-vs-nonstable消融必须单独定义资格在哪个事件决定、已有line何时改变状态。不能用“旧算法每次随机，我们地址稳定”一句话代替真实比较；更不能把此消融命名为CUDA实际实现。

### 4.3 两个容易误读的边界

其循环模型在always-admit条件下，K条cache容纳T>K条循环工作集，LIP稳态保留K−1条，保留一条位置承接新到访行；论文给出的(K−1)/T依赖该模型及预热/阶段条件。不能拿它否定允许不同保护/bypass语义的q/T toy，也不能把任一种toy当真实GPU预测。[P2 §4.1/Table 3]

低位插入不是bypass。作者在§6.2另测DIP-Bypass，说明低位插入仍保留短时间内命中与提升机会。多数结果是trace-driven cache MPKI；§6.3另用execution-driven CPU模型评价IPC。15-bit为在原LRU之上的增量控制存储，不是GPU完整实现总代价。[P2 §3、§6.2–6.4]

## 5. P3：DRRIP可明确为强基线，但GPU事件语义仍待适配

### 5.1 原文算法骨架

以2-bit RRPV为例：

| 操作 | 原文规则 |
|---|---|
| SRRIP插入 | RRPV=2 |
| BRRIP插入 | 多数RRPV=3，少数RRPV=2；epsilon=1/32 |
| HP命中提升 | RRPV=0 |
| FP命中提升 | RRPV减1，最低为0；这是另一个已评估变体 |
| victim | 固定起点查找第一条RRPV=3；没有则增加set内RRPV，继续寻找 |
| DRRIP | 两组SDM在SRRIP与BRRIP间选择；正文主要采用HP |
| 控制参数 | 每SDM32 sets，10-bit PSEL；不是默认每个layer独立控制 |

来源：P3 §4.2–4.3、§6.2、§6.4脚注6。

不能给饱和值相同的行额外做LRU排序后仍称原始victim规则。TA-DRRIP是原文面向硬件线程的扩展；改成28个layer/class的独立选择器是C16适配，不是原版DRRIP。[P3 §4.5]

### 5.2 本轮最重要的实现提醒：false temporal locality

PDF第10页（印刷69页）脚注7明确提醒：当LLC line大于上层cache line时，需要修改DIP/RRIP的命中提升，过滤由空间局部性造成的“false temporal locality”；访问大line中的不同sector不应被当成同sector再访问来更新LRU状态。[P3 §6.6脚注7]

**我们的适配要求：**先核C16实际L2事件和line/sector单位，再定义何为用于promotion/training的合格重访。不能把tag匹配、sector缺失、pending/MSHR合并、失败重试都折成同一种“hit”。同kernel内同sector的真实复用仍是合法复用，也不能为了偏向跨token故事一概过滤。

这是一条未来baseline移植合同，不是指控冻结M1存在错误。当前M1的protected-bit和资格链与RRIP预测训练不同；文献本身不构成重做M1、改Lane4的依据。

### 5.3 不能用理论或proxy预先判输赢

SRRIP的理想scan容忍条件为Slen <= (2^M−1)(A−w)，依赖文中的活动工作集、扫描和更新模型。[P3 §4.2末尾，PDF第6页]

Lane1是trace reference/set-pressure proxy，不是实际L2事务流；不能把其约千条pressure直接代入该式并宣布DRRIP必败。SRRIP也不等于DRRIP，后者还有BRRIP和在线选择。

§6.4已有photoshop例子：miss减少约10%但性能下降，作者直接指出miss成本不同、优化miss数不等于优化吞吐。这收紧了“净周期收益”作为新颖性概念本身的表述。[P3 PDF第9页]

## 6. P4：SHiP的精确训练规则及其与SHiP-SW的区别

### 6.1 原始SHiP

SHiP将memory region、PC或instruction-sequence等signature与后续复用关联。原文在SRRIP基础上改变插入预测，不改变其victim选择和hit promotion。[P4 §3、Fig. 1/Table 3]

原文事件规则：

1. 新行保存**插入时signature**，outcome初始化为0。
2. cache hit时，outcome置1，并增加该line保存的signature对应SHCT计数器；不是改用当前命中指令的signature，亦不是只在第一次hit时增加。
3. 行被淘汰且outcome仍为0时，减少其插入signature对应SHCT计数；已经复用的line被淘汰不执行这条decrement。
4. 新插入查看SHCT：zero→RRPV=3，positive→RRPV=2；命中时沿用HP令RRPV=0。

这些是原始逻辑，不是已经处理GPU并发、reservation与sector事件的代码。

### 6.2 预测对象不是下次复用时刻

作者明确说SHCT记录signature是否被再次引用，不记录其时间。[P4 §3.1，PDF第3页]

**待验证假设：**C16中，同kernel内的重复访问可能训练出“有复用”的signature，但该信息是否足以决定跨完整decode区间的保留，尚待比较。不能预设SHiP无法保留旧行；它的插入学习与SRRIP aging已能改变长间隔行为。

### 6.3 状态与测量边界

正文默认16K-entry、3-bit SHCT；后续采样与2-bit计数器是明确的变体。训练采样可以降低每line保存signature/outcome的成本。第6页用于估计预测准确率的8-way victim buffer是研究观测器，不属于实际SHiP硬件。[P4 §4.1、§5.1脚注2、§7.1–7.2]

Fig. 2使用16KB region示例，不能仅凭示例冻结所有memory signature粒度；正文还讨论地址高位与哈希实现。C16移植需明确region粒度、有限表项、哈希、碰撞、初始化及采样点。[P4 §3.2、§4.1]

**SHiP-SW仍是AutoScratch附录的另一项适配。** 本轮原始SHiP不能自动代替SHiP-SW合同。后续给软件辅助基线与M1/M1F相同28个qweight区域，同时保留其合理的细粒度signature，不把它故意压成仅28个粗类而无解释。若给SHiP再加M1硬quota，必须标成C16 hybrid，不算原论文复现。

## 7. P5：PIPP提供什么，哪里仍有原文不确定性

### 7.1 原文机制

给定各core目标份额pi_i，Basic PIPP把新行插在对应priority位置；命中时以pprom概率只上升一位；淘汰始终选最低priority。它不硬限制实际occupancy，允许借用其他core的空间。[P5 §3.1–3.3]

正式结果使用stream-sensitive PIPP：利用UMON的访问数和假设独享cache时的miss数判断streaming；streaming类低位插入、低概率提升。全部类都streaming时还会恢复高位插入。原结果也包含目标份额估计，不能只抽出低位插入便当完整PIPP。[P5 §3.4、§4.2]

因此，“容量控制+部分适应+允许借用”的组合本身早有明确工作。M1的resident+pending硬上限与PIPP的soft/pseudo分配不同，但“不同”不自动构成优越性或独立新意。

### 7.2 保留参数不一致，不悄悄替作者修正

PDF第5页§4.2正文给pprom=3/4、pstream=1/128；第7页§5.2正文再次说原始pstream=1/128。但是同页Table 2的Baseline PIPP和Stochastic MRU Promotion列出1/64。本轮直接查看页面图像确认，这不是文本解析错误。[P5 §4.2、§5.2/Table 2]

登记为`PAPER_INTERNAL_PARAMETER_DISCREPANCY`。本轮未获得作者代码或勘误，不能断定哪处对应实际所有实验。未来若必须实现，应依据作者artifact确认；若采用正文1/128，必须公开标成选择依据，不能声称该值已经唯一闭合。不为这个局部问题阻塞其他四篇核读，也不立即扫描两个版本的长跑。

### 7.3 不把28个顺序执行的layer当28个并发租户

原文是2/4核多程序共享，份额由效用监测或外部策略给定，不是自然要求等份。它也明确不提供QoS保证。[P5 §3.2、§4.1、§7]

本文的stolen hits/forced misses用于解释借用效果，作者提醒这些数并非直接正比于性能，部分后续命中在基线重新装入后本来也会出现。[P5 §5.1–5.2]

**当前定位：**PIPP是直接思想近邻和条件强基线。只有论文主张细粒度分区/公平性或优于PIPP时才升级完整适配，不为文献齐全而再建28类控制器。

## 8. 面向C16的强基线最小集合：能力优先，不全部实现

以下是未来论文比较设计，是否实现/运行由后续独立授权决定。

| 能力 | 建议对象 | 本轮状态 | 要回答的问题 |
|---|---|---|---|
| 实际参考 | 冻结R0与accepted native CUDA evidence | 不重做 | 默认执行与真实接口能达到什么 |
| 简单priority | P_all、P_stable | 保留；明确非NVIDIA硬件复现 | 不用M1硬quota是否已经足够 |
| 通用抗抖动 | 2-bit DRRIP-HP | 原文规则/参数明确，GPU适配未完成 | 经典策略是否覆盖主要收益 |
| 同信息复用学习 | SHiP-SW-style能力，原始SHiP作基础 | 原始训练明确，SW合同仍单列 | 相同region信息下是否仍有增量 |
| 项目机制 | M1；有条件M1F | 按既有Lane4 gate | 有界quota、稳定eligibility是否增加实际价值 |
| 必要消融 | stable与明确事件定义的nonstable fractional | 仅当主张稳定性时需要 | 收益来自减少准入还是选择稳定 |
| 条件基线 | PIPP；DIP/BIP；固定分区；完整Talus | 不自动全部上 | 针对最终实际主张追加 |

DRRIP可以先承担通用抗抖动能力；但并不宣称它对所有负载支配DIP/BIP。若论文对事件插入作出具体优劣主张，或筛查显示有不同解释，再把DIP/BIP升级，而不是一开始全部长跑。

## 9. 适配前必须写明的合同

**A. 更新单位。** line/sector/granularity、首次装入、真实重访、sector miss、reservation hit、MSHR merge和retry分开。仅在最终明确的逻辑事件更新PSEL、RRPV、SHCT或计数器；同一失败尝试不能反复抽签、老化或训练。原文未给GPU路径的地方标C16适配。

**B. 事务种类。** 原CPU论文对demand与writeback有所区分。C16的普通load/store、writeback、prefetch和其它事务如何初始化与更新要逐项说明，不能只管qweight而把其它流量偷偷bypass或改快。

**C. 并发与liveness。** reservation、pending fill、不可替换项、set内没有合法victim时的反压沿冻结基础接口；探索策略不得通过丢请求或重复释放获得收益。不能为了简便加入免费cross-set victim。

**D. 资源。** 物理L2容量与相联度相同；保护quota、实际占用、峰值、metadata和控制表成本分别报告。P_stable没有M1硬quota，因此与M1F不是自动等B16预算；全局selected数低于quota也不保证局部subpartition无超额。

**E. 学习与采样。** 冻结PSEL/SHCT初态、随机种子或计数器相位、leader选择、是否全局或per-subpartition。原文“每SDM32sets”不等于必须给C16每个subpartition复制32sets；复制改变成本，减少改变覆盖，均需公开。不能按当前trace正结果调leader/seed。基线从相同自然前序建立各自状态，不在目标入口额外清空学习表，也不免费灌入未来反馈。

**F. 相同可用信息。** 软件辅助基线得到相同qweight区域；通用DRRIP不需要oracle标签。标签可用性、signature精度和实际policy能力分别比较，不把信息不平等藏进机制增量。

**G. 评价。** 实际admission、旧地址存活、同sector复用、目标周期、完整窗口周期、ordinary代价分开；当前1565-kernel窗口不是完整D2全层稳态TPOT。trace proxy、固定访问序列功能模型与详细时序模型保持不同证据等级。

这些要求不等于新增一轮庞大审计。后续真正移植baseline时把普通工程问题顺手解决；本轮不要求174另开任务。

## 10. 对paper story与贡献边界的更新

**已经有前例的概念：**保住超容量循环集的一部分（DIP/RRIP）；按signature学习（SHiP）；插入+promotion调份额并允许借用（PIPP）；GPU priority过度使用导致thrashing（P1）；miss下降而周期无益（RRIP正文及LR04）。这些不能作为C16的“首次”。

**仍值得研究的具体问题：**在当前低比特LLM实际部署中，有局部价值的权重面对同层内部复用、跨层干扰和跨decode复用时，有限保护容量究竟在哪一环节无法转成净收益？同信息、同物理资源的强基线已经解决了多少，候选还解决什么剩余限制？

建议候选贡献保持三层：

- 驻留机会：量化部署改变工作集几何与局部行为；尚不升级为量化bit数的纯因果或跨LLM普遍结论。
- 局部—系统落差：native semantic cost/benefit闭合；不把“更多hint更慢”单独包装为新发现，不指定未经验证的微架构原因。
- 有效复用机制：只有强基线之后仍存在旧地址存活和净周期增量，才评价M1/M1F及其具体能力。cost-aware仍是目标，不是已存在的周期效用控制器。

一个可能的细化假设是“短尺度复用反馈是否能指导长尺度保留”，但其有效性、与SHiP/DRRIP的实际差距、以及硬件必要性都待证。不得因此把旧方法描述成完全不考虑长间隔，也不因此新增预测器。

## 11. 后续阅读缺口与执行边界

本次五篇PDF的正文获取缺口已经关闭。仍未关闭的是：PIPP参数冲突、具体作者artifact核对、C16 GPU事件映射，以及将来确需实施的SHiP-SW细节。它们是不同层次的问题。

P1参考文献还给出`Pushing the Performance Envelope of DNN-based Recommendation Systems Inference on GPUs`（MICRO 2024）和`MonoNN: Enabling a New Monolithic Optimization Space for Neural Network Inference Tasks on Modern GPU-Centric Architectures`（OSDI 2024）的GPU驻留相关线索。本轮仅登记为书目队列，没有取得正文核读，不计为新增已读工作、不要求立即添加实验。

唯一长跑科学关键路径继续是Lane4的M1 B16 primary/diagnostic。它没有terminal receipt之前不作最终科学判定；诊断先通过既有admission，再按原解释合同决定是否需要M1F。原条件不因文献更新而修改。

---

结论：五篇原文补齐后，最有价值的增量是收紧GPU hint条件、落实经典策略的精确语义，并识别sector级“复用”定义这一适配风险。目标是比较已有强能力之后的真正剩余问题，不是把更多旧论文机械加入长跑。
