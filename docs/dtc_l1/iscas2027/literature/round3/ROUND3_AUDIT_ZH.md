# R3｜英文LaTeX v0.1文献核查与针对性补充

2026-10-16。ChatGPT文献支线；只读研究与文字整理，不授权新模拟器实验。输入为用户提供的英文v0.1 PDF及LaTeX源码、四篇相关论文PDF和既有文献记录。旧分支锚点606f62813c479525a1bac420b4f14d8ebb0b5261。

## 1. 当前九条不是九篇独立比较工作

参考文献由六篇技术相关工作、DTC学位论文、Accel-Sim工具论文和项目artifact组成。没有发现虚构论文、错误年份或作者的实质问题；主要缺口是引文用途、研究脉络和方法出处，不是数量本身。

建议候选库增至16条：增加NuRAPID、Scalable Cache Miss Handling、MSHR-rich、MeDiC，以及PolyBench GPU/ACC、Rodinia、Parboil三个方法来源。MeDiC随下游段落取舍；MSHR-rich仅使用本轮能确认的高层事实。最终可以是15或16条，不以数量为指标。

## 2. 九条逐项核查

| 原编号／key | 核查结论 | 应采取的动作 |
|---|---|---|
| 1 dlmshr | Gu／Chen、ICS2019、510–521和DOI10.1145/3330345.3330390匹配用户PDF | 保留动态entry/slot组织解释；不能单独支持传统PIB完整结果存储 |
| 2 li2015 | 六位作者、题名、ICS2015、DOI10.1145/2751205.2751237正确 | §2.2支持组内预留失败；§4支持Tag/Data与局部性过滤；RC不是消费者引用数 |
| 3 zhao2024 | 英文封面、作者、UCAS、2024及第4章对应 | 是既有DTC与PIB组织来源，不能移植旧平台结果 |
| 4 vway | 作者、ISCA2005、IEEE DOI10.1109/ISCA.2005.52正确 | 空间映射与全局替换先例；不能由不同目标推断没有未披露的瞬态保护 |
| 5 micache | 五位作者、FPGA2024、22–32和DOI10.1145/3626202.3637571匹配 | 不参与新查询的旧记录特指subentry-overflow的f=1状态，不能泛化到所有冲突迁移记录 |
| 6 accelsim | 原文作者Zhesheng Shen，Z. Shen正确；ISCA2020、473–486正确 | 补DOI10.1109/ISCA45697.2020.00047，并用于streaming L1边界，而不只作为工具出处 |
| 7 dtc-artifact | 自己的数据记录，不是独立同行评审工作 | 用固定commit和明确review pack路径；不能算作novelty先例 |
| 8 mrpb | 题名、作者、HPCA2014、DOI10.1109/HPCA.2014.6835938正确 | 作者机构记录核定页码272–283；区分request reorder/bypass与CCWS发射控制 |
| 9 ccws | 作者、MICRO2012、72–83、DOI10.1109/MICRO.2012.16匹配 | 控制load发射资格，不是GPU全局在途credit或简单改变驻留warp数 |

第一段原来把miss records、reserved ways、instruction-result buffers一起引向DL-MSHR与Li2015，覆盖不完全。应拆开：前两项引用这两篇，本文所采用的完整结果缓冲组织引用学位论文。论文实际已经写“organization considered here”，不应指责它明确宣称所有GPU都一样。

元数据不填猜测：Li2015与V-Way缺少页码，但可选页码未完成第一手核实时保留缺项。Tuck等的页码有冲突：Illinois作者机构为409–420，DBLP为409–422，作者PDF12页；本轮BibTeX省略页码而保留DOI。Parboil写成IMPACT-12-01技术报告，不采用别处误传的期刊卷号127。

## 3. 最重要发现：Accel-Sim同时限定动机

[Accel-Sim原论文](https://people.ece.ubc.ca/~aamodt/publications/papers/accelsim.isca2020.pdf)的§IV（PDF第6页）“Improved L1 throughput”描述Pascal／Volta streaming L1：大量缺失可以在途，不简单依赖分配给L1的行数，MSHR吞吐不随该容量变化。§VI（PDF第11页）又讨论了新L1模型中的预留失败和吞吐瓶颈变化。

这是对本文baseline适用范围的直接相关证据。需要明确：reserve-on-miss基线是本文研究的设计点，不是所有现代GPU的共同状态。使用Accel-Sim框架不自动继承原文特定配置的硬件验证。不要把这一发现扩大成“DTC已被否定”“所有现代L1都完全没有限制”，也不要未经源码依据将streaming等价为某一个具体allocate-on-fill实现。

建议引言增加紧凑一句：The reservation-based baseline is not universal: Accel-Sim describes streaming Pascal/Volta L1 caches with much higher miss throughput and reduced reservation bottlenecks.

本轮依据原文可读段落，没有从未成功渲染的图8估读任何柱高。需要更强的当代GPU竞争主张时另行决定比较；本轮不因此自动重开实验。

## 4. 值得新增的四项研究

### NuRAPID（MICRO2003）

Chishti、Powell、Vijaykumar，正式题名Distance Associativity for High-Performance Energy-Efficient Non-Uniform Cache Architectures。取得[作者全文](https://engineering.purdue.edu/~vijay/papers/2003/nurapid.pdf)，定向核读§2.1–2.4。

Tag相联关系与不同访问距离的数据放置通过指针连接。它与V-Way属于空间映射的前驱；DTC强调旧消费者尚未结束时的物理保留。正文与V-Way共用一句即可，不新增独立大段，不声称指针本身是DTC创新。

### Scalable Cache Miss Handling（MICRO2006）

Tuck、Ceze、Torrellas，DOI10.1109/MICRO.2006.44。取得[作者全文](https://sampa.cs.washington.edu/papers/micro06_mshr.pdf)，核读§2.4、§3–4。

其Hierarchical MHA使用每bank小型专用MSHR和共享大MSHR，Bloom过滤不必要共享查询，关注容量、带宽与不均衡。更重要的是§2.4直接讨论把secondary miss信息留在LSQ、返回时反查的问题：全局搜索、指令退休和关键时序都会影响可行性。它与DTC的PIB状态组织非常接近，但CPU LSQ不是GPU PIB，不能直接搬用其否定结论。

正文放在DL-MSHR之前，建立层次化miss state→动态消费者槽位→DTC等待与数据保留这条脉络。作者机构[题录](https://experts.illinois.edu/en/publications/scalable-cache-miss-handling-for-high-memory-level-parallelism/)与索引分页冲突保留，不擅自统一。

### MSHR-rich（FPGA2019）

Asiatici、Ienne，Stop Crying Over Your Cache Miss Rate: Handling Efficiently Thousands of Outstanding Misses in FPGAs，DOI10.1145/3289602.3293901。

本轮**仅核作者摘要及[EPFL公开实现README](https://github.com/EPFL-LAP/fpga19-MOMS)，原论文正文未取得**。可以支持BRAM／哈希组织可扩展miss state这一窄事实，不能写流水线细节或性能数字已核。它是MiCache直接相邻的实现方向，有助于避免把传统MSHR概括成只能用小型全相联结构。

### MeDiC（PACT2015）

正式题名Exploiting Inter-Warp Heterogeneity to Improve GPGPU Performance，MeDiC是机制名。取得[作者全文](https://www.pdl.cmu.edu/PDL-FTP/associated/medic-pact15.pdf)，定向核读§3–5。

它利用warp间访存差异协调共享L2缓存策略和内存调度，不是私有L1的物理行回收。仅在正文保留下游协调讨论时使用，与MRPB和CCWS分别注明控制位置。不因为“都涉及并发”就扩大成同机制或可叠加收益。

## 5. 三项方法来源

- PolyBench GPU/ACC：[维护站点](https://cavazos-lab.github.io/PolyBench-ACC/)明确要求引用Grauer-Gray等InPar2012 Auto-tuning a High-Level Language Targeted to GPU Codes。已查看作者论文题录及方法范围。套件引用不证明本项目捕获代码完成了该文auto-tuning，也不补齐输入尺寸。
- Rodinia：[维护站点](https://rodinia.cs.virginia.edu/)及[作者论文](https://www.cs.virginia.edu/~skadron/Papers/rodinia_iiswc09.pdf)，Che等IISWC2009，44–54，DOI10.1109/IISWC.2009.5306797。只支持来源，不认证trace版本。
- Parboil：Stratton等，IMPACT-12-01，2012。原报告服务器读取失败；[SPEC官方来源说明](https://ftp.spec.org/accel/Docs/110.fft.html)支持报告身份。**书目核对，不是全文精读**。姓名常用变体Ray/I-Jui、Daniel/Geng Daniel不应误判为新增作者。

放在Evaluation的workload一句，不塞到Related Work。它们是研究方法出处，不是假装多了三个技术比较方案。

## 6. 没有盲目加入的候选

| 候选 | 本轮读取程度 | 处理 |
|---|---|---|
| Farkas/Jouppi，ISCA1994 non-blocking loads | 作者摘要，正文未得 | in-cache MSHR前驱高优先级补读；不把MiCache二手介绍当原文已核 |
| DD-L1D，NAS2017 | 作者机构题录／摘要 | Li2015的阈值调节后续，保留长笔记，未全文核读不直接比较瞬态 |
| NOMAD，HPCA2023 | 作者题录／摘要 | OS管理DRAM缓存的Tag/Data解耦，概念相关但层级与事件不同，未排除重叠也不强塞短文 |
| Increasing Memory Miss Tolerance for SIMD Cores | 作者PDF摘要筛查 | lane分歧与PIB整指令完成不同，当前不展开 |
| LLaMCAT，ICPP2025 | 摘要／方法范围 | LLM缓存仲裁节流不是当前私有L1主线，不为新年份加入 |
| Poise、SACAT、RPAWS | 本轮未重新全文核读 | 旧记录保持，不升级阅读等级 |

这不是穷尽性新颖性检索。未取得全文的项目不会记录为“原文没有”，也不会从标题直接断言与DTC无关。

## 7. 建议英文Related Work写法

NuRAPID decouples tag association from data placement across latency regions; V-Way uses indirection for global replacement and demand-based associativity. Decoupled L1D retains reuse history in an enlarged GPU tag store to control data insertion. DTC instead retains an unmapped data line for previously admitted consumers, until their references are released.

Hierarchical MHA combines per-bank and shared miss records with Bloom-filtered lookup. DL-MSHR dynamically links slots for independent misses and same-line consumers, while MSHR-rich designs scale FPGA miss state using BRAM-based structures. MiCache shares cache-data and MSHR-subentry storage; subentry-overflow records may cease matching new requests while still matching responses. DTC stores instruction metadata in the PIB and data in a physical pool, reclaiming an unmapped line after all consumers finish collection.

MRPB reorders or bypasses requests before cache access; CCWS gates wavefront load issue; MeDiC coordinates shared-cache policies and memory scheduling using inter-warp heterogeneity. Different intervention points do not establish additive benefits.

正式LaTeX应逐句接上对应citation，不将整段的全部引用堆在末尾。本轮本地资料包另含精确diff、原九条表和占位外的引用检查；原v0.1 PDF及数值不覆盖。参考文献语法试编译成功不等于全文四页版面已收口，合入后须检查实际分页。

## 8. 项目边界

本轮只写文献支线文字与BibTeX，不改主handoff、Core、配置、实验结果、运行脚本或已关闭任务。旧README和round1/2记录保留。所需的新基线／服务比较需另行审定，不是本记录授权内容。
