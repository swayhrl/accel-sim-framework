# EP-L2 R20：写回近邻核查与Lane6合并说明

2026-10-17。DOCS_ONLY。用户要求在r19实验运行期间独立加强文献，后续与Lane6稿件合并。本文件不启动实验、修改配置、扩大科学资格或覆盖正在执行的结果。

## 1. 本轮结论

当前文献问题不只是引用数量：旧稿覆盖了Tag/Data解耦、存储统一、MSHR，却没有充分覆盖“写回数据仍在LLC、候选地址单独跟踪、dirty metadata独立管理”的直接近邻。新增四项作者原文：VWQ、Decoupled Last-Write Prediction、DBI、SMS。前三项强化WB-only新颖性对照，第四项支撑下游缓冲与服务的实验解释。

这不是证明EP-L2已经首次提出某种机制。可辩护的研究对象应收窄为：在相同resident Tag、payload容量和bank服务预算下，Tag被重新使用时旧dirty payload仍保持原物理slot及独立所有权，新resident取得另一合法landing；数据和在途地址排序分别退休。该区别是否有价值，仍由当前实现、真实性能与控制成本决定。

## 2. 四项新增原始来源及准确使用范围

### vwq — The Virtual Write Queue: Coordinating DRAM and Last-Level Cache Policies

Jeffrey Stuecheli, Dimitris Kaseridis, David Daly, Hillery C. Hunter, Lizy K. John；ISCA 2010，72–82，DOI 10.1145/1815961.1815972。

作者PDF：https://lca.ece.utexas.edu/pubs/ISCA_2010.pdf
作者会议目录：https://lca.ece.utexas.edu/pubs-conferences.php

核读PDF4–6的§4–4.3；PDF5有页面视觉检查。相关事实：LLC区域作为逻辑写队列，扩展待写回候选的可见范围，同时仍有物理write queue。不能据此声称“EP-L2首次用cache存储待写回数据”。EP-L2应比较Tag复用后的payload责任，而非泛化的cache buffering。

采用的是ISCA 2010版，不要混入IEEE Micro 2011扩展版的卷期/页码。没有使用原论文性能或功率数字作为EP-L2的收益。

### lastwrite — Improving Writeback Efficiency with Decoupled Last-Write Prediction

Zhe Wang, Samira M. Khan, Daniel A. Jiménez；ISCA 2012，309–320，DOI 10.1109/ISCA.2012.6237027。

作者PDF：https://people.engr.tamu.edu/djimenez/taco/pdfs/isca2012_dist.pdf
作者目录：https://people.engr.tamu.edu/djimenez/index.html

核读§4.1与PDF6的§4.2.1–4.2.3。相关事实：last-write buffer记录地址，数据仍在LLC；被驱逐dirty数据使用另一个write buffer。不能把所有前人概括为“立即复制完整dirty数据”。此项预测与提前清理不是我们Tag复用后的所有权转换，也不自动成为当前机制的一部分。

### dbi — The Dirty-Block Index

Vivek Seshadri, Abhishek Bhowmick, Onur Mutlu, Phillip B. Gibbons, Michael A. Kozuch, Todd C. Mowry；ISCA 2014，157–168，DOI 10.1109/ISCA.2014.6853204。

作者PDF：https://people.inf.ethz.ch/omutlu/pub/dirty-block-index_isca14.pdf

核读PDF2–4的§2.1–2.2与§3.1。相关事实：dirty metadata移出Tag阵列并按DRAM row组织，清理dirty信息不必等同驱逐数据。DBI的dirty状态不是WAD的在途同地址排序状态；该论文不替代我们32B sector/atomic/late-event的正确性验证。不要将“把metadata独立出来”单独包装为新贡献。

### sms — Staged Memory Scheduling: Achieving High Performance and Scalability in Heterogeneous Systems

Rachata Ausavarungnirun, Kevin Kai-Wei Chang, Lavanya Subramanian, Gabriel H. Loh, Onur Mutlu；ISCA 2012，416–427，DOI 10.1109/ISCA.2012.6237036。

作者PDF：https://people.inf.ethz.ch/omutlu/pub/staged-memory-scheduling_isca12.pdf

核读PDF3–4的§3.2–3.3及摘要的阶段划分。相关事实：request buffer容量影响调度可见性及选择/时序逻辑复杂度。它研究CPU/GPU异构干扰，不能据此证明当前EP-L2已经DRAM饱和。用于解释为什么要分开考察缓冲、服务速度与固定延迟，不借用其平台性能数字。

作者/标题/会议年份按原文和作者目录核对；DOI/最终页码另做书目索引交叉核对。部分出版方落地页未成功访问，不声称每项都完成出版方全文下载。

## 3. 现有十项引用的保留与降级

| Key | 原文定位与本轮阅读等级 | 使用边界 |
|---|---|---|
| micache | 用户出版版3626202.3637571.pdf；本轮PDF1–4、§§2–4.2；PDF2–4页面图已见 | data BRAM在cache data/MSHR subentries之间共享；victim stash不是dirty WB pool |
| dlmshr | 用户出版版3330345.3330390.pdf；本轮PDF8–11、§§4.6–6.5；设计字段沿用此前§2–4原文审计 | write-miss data可以在slot中；RF与IPC不是比例关系；不能借用其PPA数字 |
| vway | 继承EN-v2作者原文审计，§3/PDF3–4 | Tag/Data indirection不是新概念 |
| unified | 继承作者原文审计，§§4.3–4.4/PDF5–6 | 共享的是SM寄存器/cache/scratchpad，不等于post-tag-retirement WB ownership |
| farkas | 继承WRL94/3原报告，打印p4/PDF12 §2.3 | 只引用实际报告版本，不把该报告当作首次发明证明 |
| tsc | 继承作者原文§§3–4 | 区分请求和存储粒度，不等于WB生命期 |
| accelsim | 继承作者原文框架/验证部分 | 工具来源，不给修改后的EP-L2背书硬件相关性 |
| gpgpusim | 继承作者原文模型部分 | 模型谱系，不替代当前生产验证 |
| mrpb | 继承原文§§4–5，本轮摘要级筛查 | 条件引用：正文确实讨论L1 reorder/bypass时才保留 |
| victim | 出版方摘要/元数据；没有本轮全文 | 条件引用：TVD背景；不扩写未核读实现/时序 |

旧原始来源定位：
- vway：https://hps.ece.utexas.edu/pub/qureshi_isca05.pdf
- unified：https://research.nvidia.com/sites/default/files/pubs/2012-12_Unifying-Primary-Cache/Gebhart_MICRO_2012.pdf
- farkas：https://shiftleft.com/mirrors/www.hpl.hp.com/techreports/Compaq-DEC/WRL-94-3.pdf
- tsc：https://people.cs.rutgers.edu/zz124/assets/pdf/ics16.pdf
- accelsim：https://people.ece.ubc.ca/~aamodt/publications/papers/accelsim.isca2020.pdf
- gpgpusim：https://people.ece.ubc.ca/~aamodt/publications/papers/gpgpusim.ispass09.pdf
- mrpb：https://mrmgroup.cs.princeton.edu/papers/mrpb.pdf
- victim：DOI 10.1145/325164.325162（会议版本）

建议WB-only主文使用12项。MRPB和victim在确有扩展讨论时才启用，文献库共有14条但不以全部引用为目标。

## 4. 与r19并行实验的衔接：以下是本轮分析建议，不是新增任务

Q4、D4和固定延迟干预需要分别说明其变化对象。文献支持分开考察这些因素，但不预先决定本项目的结果。队列统计可能是重复拒绝事件，不能从累计等待直接减出GPU cycle收益；较高占用也不自动意味着更差服务。

若headroom改善后B/U优势扩大，应核对改变的具体资源成本和有效区间；若两者一起变快而B/U不变，说明快内存改善系统，不自动说明原配置掩盖机制收益；若更快服务也消除B16的积压，可能出现中间区间优于极快端点。后三项是我们为实验定义的判读问题，不是上述文献替EP-L2测得的结论。

若未来需要进一步调查写回调度/读写干扰，VWQ、last-write和DBI可提供设计入口，但当前不自动加入这些机制，不改r19运行范围，也不把它们的headline speedup当目标。

## 5. 合并到Lane6的最小路径

阅读起点为Lane6 `d3d7b4fe9059d68aa0793eec58b5f32488138c10`：
`docs/ep_l2/review_packs/FT20261017_LANE6_R18_FIVE_PAIR_EN_V6_r1/EP_L2_EN_v6.tex`。
它已完成5/5论文侧接收和真实Fig2/3，Fig4强静态对照待测。后续合并必须读取最新Lane6和当前Lane5权威，不能用本模块回退结果。

1. 原稿新revision中合并references_verified.bib，保留旧key；新增key仅vwq/lastwrite/dbi/sms。
2. ENGLISH_MERGE_BLOCKS.tex有四段：引言bridge、Related Work替换、evaluation context、可选TVD/policy背景。按注释分别放置，不把整个文件input到一个section，也不要旧综述保留后又追加新综述。
3. Related Work替换段约284英文词。若引言重复，可删重复事实，把精确研究问题留下。不要挤占真实结果图位或缩正文/边距。
4. 若原稿使用内嵌thebibliography，须统一到一种bibliography生成方式并按实际首次引用排序；不要同时留旧内嵌和新BibTeX两套。
5. 保持4页技术正文＋参考页预算。引用已在本地IEEEtran小稿编译两次，14个key均解析；一条underfull排版提示、无溢出或未定义引用。这个是片段语法检查，不是新完整论文排版通过。
6. 不修改任何结果数值、scientific ledger、raw CSV或生产代码。Lane6后续择机单次合并即可，无需因本次文献工作重启实验窗口。

## 6. 筛除与获取限制

Using Dead Blocks as a Virtual Victim Cache的作者原文只核读摘要/引言，留给TVD进一步研究；CMD(arXiv2408.09483)及ATA-Cache(arXiv2302.10638)只作摘要筛查，不进入当前主文微架构对比。新近年份不构成引用理由；没有获得可靠原文的候选不填写实现细节。此为有界调研，非穷尽2025/2026全领域的新颖性证明。

Library原始字节materialize失败，后续部分页面读取失败；几份公开PDF截图也不可用。本轮没有把这些操作写成成功，不依靠未见图表读数值。交付包不包含第三方论文PDF或字体文件。

本地完整交付另含LITERATURE_AUDIT、逐条EVIDENCE_MAP、拆分tex、编译脚本与校验记录，方便离线审阅。远端本目录存放核心合并源码及上述原文证据定位。
