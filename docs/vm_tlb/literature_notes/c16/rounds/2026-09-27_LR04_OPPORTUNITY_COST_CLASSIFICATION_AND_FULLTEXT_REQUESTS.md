# C16文献支线LR04：驻留机会成本、对象分类与待补全文

日期：2026-09-27。维护者：ChatGPT。

状态：**LITERATURE_REVIEW_ONLY_NO_EXECUTION_AUTHORITY**。不启动新GPU实验或timing simulation，不修改Lane 4、Core、运行配置、trace或冻结的Lane 3。M1F仍须等待原有project-level gate。

## 0. 远端起点与本轮范围

本轮开始核验：`swayhrl/accel-sim-framework` / `hrl/c16-chatgpt-literature-notes-v1`与`8d37abdde2a63643e248d0854649176564cc2678`为identical（ahead=0、behind=0）。重读LR03相关内容和README，接续其尚未完成的原文队列；不把LR02/LR03成果重复计为新发现。

本轮新增核读两个会议论文的机制相关正文，以及一份作者技术报告：Whirlpool（ASPLOS 2016）、EVA（HPCA 2017）、A Case for MLP-Aware Cache Replacement（TR-HPS-2006-003，2006-02-27）。MLP论文的技术报告不冒充最终ISCA会议稿。Leeway目前仅核作者机构摘要；DIP、RRIP、原始SHiP、MICRO 2025 eviction hints、PIPP仍缺本轮可读的完整原文。

作者内容、C16项目事实、我们的推论、拟核问题分别标明。本轮未复现任何论文代码，也未获得新的C16性能结果。

## 1. 新增原文核读

### R04-01｜Whirlpool: Improving Dynamic Cache Management with Static Data Classification

作者：Anurag Mukkara、Nathan Beckmann、Daniel Sanchez。ASPLOS 2016。DOI：10.1145/2872362.2872363。

阅读深度：作者提供的15页PDF，重点§2.2–2.3、§3与Appendix A；首屏截图核对题名及版本。相关后续页截图请求失败，以下只依据可解析正文，不从未能检查的图表推断数值。[S1]

**作者内容：**将数据结构静态划为memory pools，再由硬件动态决定缓存管理；静态分类不等于静态策略。§2.3还明确报告：作者曾尝试以pool分类扩展DRRIP的插入决策，但在单体缓存中增益有限，因此聚焦NUCA数据放置。评估环境是CPU缓存系统，不是C16 GPU。

**我们的推论：**qweight/layer标签能分离数据，不自动使策略优于已有动态方法。P_stable和同语义信息的SHiP-SW-style基线因而仍有必要；该论文的负面结果不能直接推导C16同样无效。

**拟核问题：**在C16中，新增语义信息究竟改善了哪些决策？旧策略获得相同信息后是否已能获得相同收益？本轮只保留问题，不新增实现。

### R04-02｜Maximizing Cache Performance Under Uncertainty（EVA）

作者：Nathan Beckmann、Daniel Sanchez。HPCA 2017。

阅读深度：作者提供的12页会议PDF，重点§III–IV、实现和评估边界；核对首屏。不要与2015年技术报告Bridging Theory and Practice in Cache Replacement合算为两个独立研究贡献。[S2]

**作者内容：**EVA将候选行预期产生的命中收益与占据缓存时间造成的机会成本放在同一度量中。正文的时间/年龄以访问次数度量；理论目标是命中率，而非直接最小化完整GPU执行周期。实现周期性估计、更新策略，并报告硬件开销。

**我们的推论：**只限制保护字节数并未衡量“为了未来一次有用复用，期间让其他工作失去多少机会”。但不能把EVA的命中效用直接当作C16已实现的周期效用控制，也不能用其理论证明M1F最优。

**拟核问题：**即使旧地址真的跨轮存活，保留它的整个时间区间是否仍值得？已有semantic cost/benefit账目用于检查最终净收益；本轮不新建EVA预测器或重新跑native。

### R04-03｜A Case for MLP-Aware Cache Replacement

作者：Moinuddin K. Qureshi、Daniel N. Lynch、Onur Mutlu、Yale N. Patt。

本轮版本：TR-HPS-2006-003，2006-02-27，22页作者技术报告。存在ISCA 2006会议论文，但本轮未将技术报告核读算作最终会议稿逐段核验。[S3][S4]

阅读深度：重点问题定义、§3.1成本算法、策略与实验方法；PDF截图请求失败，仅使用可解析正文，不依据图形提取性能数值。

**作者内容：**MLP指memory-level parallelism。并发缺失能重叠，故不同miss对停顿的代价不同；报告给出按未完成需求miss数分摊等待成本的估计方法，并结合历史成本与替换策略。研究基于CPU执行模型，成本是估计而非每次miss精确关键路径归因。

**我们的推论：**保护命中数、DRAM字节数或miss数改善都不能代替完整测量范围的周期改善。C16尚未证明native抵消由MLP造成；此文提供的是分析维度，不是现有抵消的因果解释。

**拟核问题：**减少的访问是否本来可以重叠，而被保护流量干扰的访问是否更影响进度？仅在未来已接受证据确有区分价值时再考虑诊断，不现在增加criticality/MLP机制。

## 2. 本轮对paper story的增量

**我们的综合判断：**当前故事需要依次经过三个检验：信息是否有用；容量是否真正转成旧地址存活；存活带来的收益是否超过机会成本。

Whirlpool提醒信息增量不一定等于性能增量；EVA提醒驻留必须计入占用期间的代价；MLP-aware研究提醒不同miss的时间代价并不相等。这三项思想都有前例。不能把“semantic”“cost-aware”“criticality-aware”作为新名称就宣布创新。

这不否定当前C16。值得继续回答的是：在固定GPU程序和完整自然干扰区间中，现有简单能力之后还剩什么具体限制；如果M1/M1F解决了该限制，增量来自哪里。

LR03的P_all/P_stable/M1/M1F能力对照与同信息强基线设计继续保留。Whirlpool、EVA和MLP-aware当前属于解释框架及related-work来源，不自动扩张成三个必须实现的baseline。

## 3. 请用户优先补充的四篇完整原文

以下条目是全文需求，不表示已读完机制。题名及会议信息已由作者页面、原始文献引用或书目记录交叉核对；书目记录只用于识别论文，不充当技术结论。[S5–S10]

### P1｜Security and Performance Implications of GPU Cache Eviction Priority Hints

- 作者：Qizhong Wang、Xiangyue Huang、Yanan Guo、Yuanchao Xu。
- MICRO 2025，1058–1072。
- DOI：10.1145/3725843.3756116。
- 当前：作者主页与项目说明已读；出版社/作者入口未取得本轮可读正文。
- 需要核查：GPU和driver矩阵、hint的实测含义、同优先级竞争、thrashing实验及推断边界。不能据作者简介补出具体内部replacement规则。

### P2｜High Performance Cache Replacement Using Re-Reference Interval Prediction (RRIP)

- 作者：Aamer Jaleel、Kevin B. Theobald、Simon C. Steely Jr.、Joel S. Emer。
- ISCA 2010，60–71。
- DOI：10.1145/1815961.1815971。
- 当前：书目与后续原始论文引用已核，未取得本轮可读原始全文。
- 需要核查：SRRIP/BRRIP/DRRIP、hit更新、插入、aging及set-dueling配置；不能只凭常见伪代码冻结实现合同。DRRIP不另列为一篇待找论文。

### P3｜SHiP: Signature-Based Hit Predictor for High Performance Caching

- 作者：Carole-Jean Wu、Aamer Jaleel、William Hasenplaugh、Margaret Martonosi、Simon C. Steely Jr.、Joel Emer。
- MICRO 2011，430–441。
- DOI：10.1145/2155620.2155671。
- 当前：作者机构摘要可读，原文下载未成功。
- 需要核查：signature、有限SHCT、outcome更新、碰撞与metadata，再对照AutoScratch附录SHiP-SW；不能拿SHiP++或SHiP-SW替代原始SHiP。

### P4｜Adaptive Insertion Policies for High Performance Caching

- 作者：Moinuddin K. Qureshi、Aamer Jaleel、Yale N. Patt、Simon C. Steely Jr.、Joel Emer。
- ISCA 2007，381–391。
- DOI：10.1145/1250662.1250709。
- 当前：原始摘要、书目信息及后续作者文献引用已有，完整会议正文未闭合。
- 需要核查：LIP/BIP/DIP怎样抗thrashing、事件级选择及适应行为。优先ISCA 2007原稿，不以2008年IEEE Micro延伸或课程讲义替代。

## 4. 第二优先补充

**PIPP: Promotion/Insertion Pseudo-Partitioning of Multi-Core Shared Caches**

作者：Yuejian Xie、Gabriel H. Loh。ISCA 2009，174–183。DOI：10.1145/1555754.1555778。[S10]

当前只有可核对的题名、书目与摘要线索，不宣称核过算法。待查插入/提升与分配落实的关系、借用和公平性边界；优先级低于上述四篇，不为PIPP延迟已有文献工作。

## 5. 暂不请用户重复寻找的材料

Whirlpool、EVA会议正文和MLP-aware作者技术报告已可读；Talus、Vantage、AutoScratch、APCM等沿用LR02/LR03的既有获取与阅读记录。它们无需作为本轮新增找文任务。

Leeway: Addressing Variability in Dead-Block Prediction for Last-Level Caches（Priyank Faldu、Boris Grot，PACT 2017，DOI 10.1109/PACT.2017.32）仅核作者机构摘要及accepted-manuscript入口；入口下载失败。本轮保留队列，不把摘要升格成全文，也不增加为必需补充件。[S11]

## 6. 后续核读合同

收到原文后优先完成“原文机制→C16适配→未核信息”的差异表：触发事件、可用信息、状态与容量、victim规则、重试/MSHR生命周期、元数据和训练成本、正式比较范围。

“某论文提供了这个能力”和“我们已在当前GPU模拟器正确实现该能力”是两项不同资格。本轮仅推进前者，不授权实现、采集或长跑。

Lane 4解释仍按既有预注册条件；不利用中途prefix选择解释，不修改M1F seed/threshold，不因新读论文而预定必须运行M1F。

## 7. 来源登记

[S1] Whirlpool作者会议PDF： https://people.csail.mit.edu/sanchez/papers/2016.whirlpool.asplos.pdf 。关键定位§2.2–2.3、§3、Appendix A。

[S2] EVA作者会议PDF： https://people.csail.mit.edu/sanchez/papers/2017.eva.hpca.pdf 。关键定位§III–IV、§VI–VII；书目[17]、[30]、[39]辅助核对RRIP、DIP、SHiP题名，不代替它们的原文。

[S3] MLP-aware作者技术报告： https://hps.ece.utexas.edu/pub/TR-HPS-2006-003.pdf 。关键定位§1、§3.1、方法与策略章节。

[S4] HPS技术报告目录： https://hps.ece.utexas.edu/hps_techreports.html 。用于核对TR编号与版本。

[S5] GPU eviction hints作者页： https://qizhong-wang.github.io/ ；通讯作者论文入口： https://yuanchaoxu6.github.io/ ；项目说明： https://cuda.fail/ 。均不等于已取得论文正文。

[S6] GPU eviction hints书目： https://dblp.org/rec/conf/micro/WangHG025.html 。仅用于题名、会议、页码与DOI识别。

[S7] SHiP作者机构摘要： https://istc-cc.cmu.edu/publications/papers/2011/SHiP_abs.shtml 。DOI 10.1145/2155620.2155671。

[S8] RRIP书目： https://dblp.org/rec/conf/isca/JaleelTSE10.html 。仅用于书目识别。

[S9] DIP会议信息： DOI 10.1145/1250662.1250709；EVA作者正文书目[30]核对题名、作者与ISCA 2007。仍未核原始全文。

[S10] PIPP书目： https://dblp.org/rec/conf/isca/XieL09.html 。仅用于书目识别。

[S11] Leeway作者机构记录： https://www.research.ed.ac.uk/en/publications/leeway-addressing-variability-in-dead-block-prediction-for-last-l/ 。仅摘要及版本入口，本轮无可读PDF正文。

---

结论：先补四篇直接决定强基线合同与GPU hint解释的原文；PIPP为第二优先。继续研究语义信息、旧地址存活和净周期收益之间的缺口，但不预定缺口存在，也不把近邻调研变成全套论文复现任务。
