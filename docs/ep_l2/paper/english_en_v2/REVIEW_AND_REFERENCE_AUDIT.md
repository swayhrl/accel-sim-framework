# EN-v2：图位预算与引用核验

DOCS_ONLY。承接Lane6 r4（20676888aa9f1d98bb318573a6569f5fe88aa17a）和EN-v1（a1a9ae58dccd4628cc1d69de6a40cee4915a4d0b）。本轮只改独立英文编辑分支；不改模拟器、实验、Lane回执、Storage-Ops或任何运行资格。EN-v1和Lane6旧包保留。

## 1. 结构裁决与已修改内容

EN-v1的主线合理，但“能排入4页”不等于为真实结果留了版面。原来两张局部copy/生命周期图不能代替整体结构图，五负载小表也不能承载主结果与归因。本版先压缩重复的验收、限制和gross成本描述，再把正文组织为：Introduction → EP-L2 Design → Evaluation Methodology → Results and Causal Analysis → Related Work → Conclusion。

实际编译为4页技术正文＋第5页纯参考文献，IEEEtran conference常规字体和边距，无缩字挤版。格式依据 https://epapers2.org/iscas2027/ESR/authorinfo1.php 和 https://epapers2.org/iscas2027/ESR/samples.php 。作者信息及真实结果仍待补齐，不是可提交的最终稿。

| 图位 | 实际页 | 内容/高度 |
|---|---:|---|
| Fig.1(a)(b)，双栏复合图 | 2 | 新增单slice整体逻辑组织，合并copy路径与tr/ta/td释放说明；不是physical floorplan或实测时序 |
| Table I | 2 | 精简匹配配置，代替冗长实验流程介绍 |
| Fig.2(a)(b)，双栏 | 3 | 两个40mm内高panel：五负载性能、真实WB/copy工作量 |
| Fig.3(a)(b)(c)，双栏 | 4 | 三个46mm内高panel：容量/WAD压力、Bank服务、下游流量/排队 |
| Fig.4，单栏 | 4 | 36mm内高panel：按合同条件选择的强静态对照和/或WBUF8敏感性 |
| References | 5 | 10条均有正文用途的引用，不用无关文献填满页面 |

高度不含边框/内边距/caption。图2–4只是明确标注MEASUREMENTS PENDING的固定版面，没有模拟柱形、坐标轴、1x线、误差棒或均值。当前接受配对仍为0；以后用真实图替换对应panel，并将计划性文字替换为数据解释，不要只叠加新内容。图位不授权新实验。

## 2. 本轮最重要的新颖性约束

不能主张“第一次GPU存储统一”“第一次cache保存瞬态状态”或“Tag/Data间接映射本身创新”。V-Way、Gebhart等统一GPU本地存储、in-cache MSHR及MiCache均构成先例。EP-L2必须在固定resident Tag与payload/bank预算下解释dirty resident→WB数据角色转换，以及copy、容量、服务、性能和成本的具体结果。文献核验不等于穷尽性论文/专利新颖性证明。

MiCache是近邻，不能仅用FPGA平台差别排除；DL-MSHR也不能被误写为metadata-only，因为其slot可携带write-miss数据。V2正文已经据此改写相关工作与引言。

## 3. 逐条引用依据（与BibTeX key对应）

以下9项取得原文并核读所引用部分，不宣称逐字读完全部实验；Jouppi 1990本轮只有出版方摘要/元数据，仅用于其支持的背景事实。

### vway — V-Way, ISCA 2005, pp.544–555

M. K. Qureshi, D. Thompson, Y. N. Patt；DOI 10.1109/ISCA.2005.52。
原文 https://hps.ece.utexas.edu/pub/qureshi_isca05.pdf 。核读§3的Tag/Data间接映射、相对Tag容量、全局替换。正文只用来界定既有的灵活相联度，不引用其性能为EP-L2证据。

### unified — Unifying Primary Cache, Scratch, and Register File Memories in a Throughput Processor, MICRO 2012, pp.96–106

M. Gebhart, S. W. Keckler, B. Khailany, R. Krashinsky, W. J. Dally；DOI 10.1109/MICRO.2012.18。
原文 https://research.nvidia.com/sites/default/files/pubs/2012-12_Unifying-Primary-Cache/Gebhart_MICRO_2012.pdf 。核读§4特别§4.3–4.4及结构图：SM本地寄存器/cache/scratchpad统一组织、kernel前配置、所评估cache为write-through。与EP-L2区别为SM资源划分对L2 dirty-data瞬态转换，不能把“统一”本身当新意，也不混用两者bank端口模型。

### farkas — Complexity/Performance Tradeoffs with Non-Blocking Loads, WRL Research Report 94/3, March 1994

K. I. Farkas, N. P. Jouppi。实际读到的是DEC Western Research Laboratory报告版本： https://shiftleft.com/mirrors/www.hpl.hp.com/techreports/Compaq-DEC/WRL-94-3.pdf 。引用§2.3（印刷页4/PDF第12页）的in-cache MSHR及放置/端口约束。报告将相关观察归于更早的Franklin/Sohi，本稿不赋予其首次提出的优先权。关联ISCA 1994会议版pp.211–222、DOI 10.1109/ISCA.1994.288148不混填到报告书目中。

### micache — MiCache: An MSHR-inclusive Non-blocking Cache Design for FPGAs, FPGA 2024, pp.22–32

S. Xu, S. Lu, Z. Shao, X. Liao, H. Jin；DOI 10.1145/3626202.3637571。
核读用户Library中的出版版3626202.3637571.pdf，§4.1–4.3/PDF第4–6页、图4–6：cache line与MSHR subentries共享数据区、统一记录格式，response时MSHR可转换为cache记录。EP-L2的区别是保留现有dirty数据并转变resident/WB角色，metadata/WAD仍独立有界。未移用其BRAM或speedup数字。

### accelsim — Accel-Sim: An Extensible Simulation Framework for Validated GPU Modeling, ISCA 2020, pp.473–486

M. Khairy, Z. Shen, T. M. Aamodt, T. G. Rogers；DOI 10.1109/ISCA45697.2020.00047。
原文 https://people.ece.ubc.ca/~aamodt/publications/papers/accelsim.isca2020.pdf 。核读SASS前端、性能模型及验证方法。引用仅标明工具来源；其硬件相关性不自动验证修改后的EP-L2。没有采用新版本流程就不为增加新年份而追加Accel-Sim 2.0。

### gpgpusim — Analyzing CUDA Workloads Using a Detailed GPU Simulator, ISPASS 2009, pp.163–174

A. Bakhoda, G. L. Yuan, W. W. L. Fung, H. Wong, T. M. Aamodt；DOI 10.1109/ISPASS.2009.4919648。
原文 https://people.ece.ubc.ca/~aamodt/publications/papers/gpgpusim.ispass09.pdf 。引用性能模型来源；不把2009年论文称为SASS前端出处，不移用其验证精度。

### tsc — Tag-Split Cache for Efficient GPGPU Cache Utilization, ICS 2016, Article 43, 43:1–43:12

L. Li, A. B. Hayes, S. L. Song, E. Z. Zhang；DOI 10.1145/2925426.2926253。
原文 https://people.cs.rutgers.edu/zz124/assets/pdf/ics16.pdf ，书目对照作者目录 https://people.cs.rutgers.edu/zz124/publications/ 。核读§3–4：粗粒度请求与细粒度数据存储分开。此为空间粒度/利用率优化，不等同于resident/WB跨角色生命期；文章编号不是普通顺序页码。

### dlmshr — Dynamically Linked MSHRs for Adaptive Miss Handling in GPUs, ICS 2019, pp.510–521

Y. Gu, L. Chen；DOI 10.1145/3330345.3330390。
核读用户Library中的出版版3330345.3330390.pdf，§2–4/PDF第2–6页：动态链接slot适配primary/secondary misses，slot可有write-miss数据。原文把dirty eviction另放evicted buffer。正文不把它贬为metadata-only，也不声称其slot池等同于EP-L2的resident/bypass/WB payload池。

### mrpb — MRPB: Memory Request Prioritization for Massively Parallel Processors, HPCA 2014, pp.272–283

W. Jia, K. A. Shaw, M. Martonosi；DOI 10.1109/HPCA.2014.6835938。
原文 https://mrmgroup.cs.princeton.edu/papers/mrpb.pdf ，书目对照Princeton作者机构出版记录。核读§3请求重排与bypass。正文只把它作为GPU L1前端访问策略代表，不当作原位WB或可直接相加的收益。

### victim — Improving Direct-Mapped Cache Performance by the Addition of a Small Fully-Associative Cache and Prefetch Buffers, ISCA 1990, pp.364–373

N. P. Jouppi；会议DOI https://doi.org/10.1145/325164.325162 。本轮核对出版方摘要/元数据，未取得可读完整原文；只支持“保留被替换行利用随后重用”的背景，不写具体端口/时序/性能。该文同有SIGARCH期刊版本DOI 10.1145/325096.325162，不能混淆版本。

## 4. 未加入的条目

CACTI/McPAT/GPUWattch：没有用其取得EP-L2 PPA，不能用引用代替测量。更多调度/bypass工作：MRPB已经支撑该区别，不为了数量堆同类论文。基础MSHR史、文件系统writeback、软件KV-cache、专利标题命中：没有新的直接正文论点，不加入。没有引用外部工作的性能数字填补当前结果。

## 5. 交付与质量检查

单文件EP_L2_EN_v2.tex包含完整正文、TikZ结构图、固定图位及10条bibliography。远端首次发布blob `80e51fd51825ee6b60a82884dbdf4695ad167fd3`与生成附件PDF的本地源码一致。配套references.bib保留DOI和准确文献版本。对话附件提供等价模块化源码、逐条引用JSON/CSV、完整中文审查和PDF检查记录；无字体和他人版权全文。

已实际编译5页，检查未定义引用/Overfull均无，全部字体嵌入、无Type3，五页渲染检查无裁切或图文重叠。PDF质量检查不是科学资格，也未完成最终会议投稿检查。

Lane6吸收时产出新revision，保留r1–r4；新结果仍必须走Lane5原生V2 current acceptance、完整identity/run-key/proof和动态withdrawal。不得因本稿换了图位与文献就放松结果接收。
