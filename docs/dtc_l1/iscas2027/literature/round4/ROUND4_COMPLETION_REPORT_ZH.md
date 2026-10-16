# R4｜高关联文献补齐与英文LaTeX v0.2

2026-10-16。研究笔记与文稿修订，不是模拟器执行任务。此前文献分支锚点692fc0164546e76ff8c91f04dbf0509dcae1dbd9。

## 完成内容

原英文稿9条已经扩展并实际整合为20条，全部在正文中引用，没有nocite。R3的16条不再仅停留在候选BibTeX；本轮重写引言、相关工作和方法来源，生成英文v0.2并完成实际编译。

20条包括13篇独立技术论文、DTC学位论文、Accel-Sim、3项工作负载来源、NVIDIA白皮书及本项目数据记录。不能统称20篇竞争方案或20篇本轮全文精读。原数值、TBD、图源与结构例子保持不变，原v0.1文件不覆盖。

## 四项实质补强

**1. 非阻塞状态的第一手基础。** 取得Kroft作者上传的重印正文，核到MSHR保存请求地址、cache-buffer位置、请求者信息以及带标识返回。它还有obsolete状态处理，避免不应发生的旧数据更新。因此，稳定返回身份本身不能被DTC当成独有创新。引用采用实际读到的1998重印版，并注明1981原作，不与1998回顾短文混淆。

来源：[作者上传原文](https://www.researchgate.net/publication/241481142_Lockup-free_instruction_fetchprefetch_cache_organization)，Organization/Operation，重印pp.195–198。读取的是作者上传连续文本，未取得可独立下载的完整PDF图像。

**2. 消费者存放与释放的细粒度对照。** Hierarchical MHA的§2.4讨论把secondary miss信息留在LSQ的查找、退休与时序困难，不能把“消费者移到PIB”写成没有先例或没有代价的简化。该文还用每bank和共享MSHR兼顾容量与访问带宽。CPU LSQ不是GPU PIB，其结论不能直接否定DTC。

来源：[作者上传正文](https://www.researchgate.net/publication/221005277_Scalable_Cache_Miss_Handling_for_High_Memory-Level_Parallelism)，§2.4、§§3–4及§6.1。原作者PDF直链本轮不稳定。官方作者机构与索引分页冲突仍未消除，BibTeX省略页码而保留DOI。

DL-MSHR用户PDF第6–7页明确动态slot-set及返回转发后的回收；MiCache第6–7页明确f=1子项溢出旧记录不匹配新请求、但响应仍处理。普通hash-conflict迁出记录不应一并描述为新请求不可见。对照表见同目录文件。

**3. 现代GPU基线范围。** 新增NVIDIA Volta官方白皮书的L1 cache/coalescing与streaming描述，并与Accel-Sim§IV的Improved L1 throughput、§VI相关case study对照。reserve-on-miss是本文指定组织，不是所有现代GPU共有的限制；使用框架不自动继承定制L1的硬件验证。

来源：[Volta白皮书](https://images.nvidia.com/content/volta-architecture/pdf/volta-architecture-whitepaper.pdf)，印刷pp.17–18，目标页图像已检查；[Accel-Sim作者论文](https://people.ece.ubc.ca/~aamodt/publications/papers/accelsim.isca2020.pdf)，PDF6及11相关文本。厂商“unlimited”的字面表述不被当成物理无界；没有从未成功渲染的图8估读数值。

**4. 并发与服务的直接前驱。** Poise选择参与执行及允许cache分配的warp；ISPASS2017带宽研究区分缓冲减少停顿与提高可持续服务能力。用它们支撑研究背景和敏感性维度，而不把异平台性能数据搬进DTC。

来源：[Poise作者PDF](https://users.cs.utah.edu/~vijay/papers/hpca19.pdf)，设计及§VI.C；[带宽研究作者PDF](https://saumaydublish.github.io/papers/ispass2017.pdf)，§§IV–V。参与/分配warp的分类基础不被误称为Poise首次提出。

## 引文实际放在哪里

| 正文 | 引用用途 |
|---|---|
| 引言开头 | Kroft非阻塞背景、层次化MHA容量/带宽、DL-MSHR条目和槽位、Li2015组内预留 |
| 引言基线 | 特定结果存储组织引用学位论文；Volta与Accel-Sim限定现代GPU背景 |
| 引言末段 | NuRAPID/V-Way/MiCache先例；Poise及带宽研究说明并发与服务的关系 |
| 方法 | PolyBench GPU、Rodinia、Parboil各自来源；自有数据固定提交链接 |
| 局部服务敏感性 | 容量/缓冲与持续服务不是相同维度，不代表本项目敏感性已完成 |
| Related Work | 映射放置、缺失/消费者状态、请求流/服务三条线，各句附对应引文 |

## 读取程度与缺口

MSHR-rich正文仍未取得，仅使用作者摘要和[EPFL公开实现](https://github.com/EPFL-LAP/fpga19-MOMS)确认BRAM型可扩展miss state。Parboil原技术报告仍未取得，使用[官方SPEC套件来源](https://ftp.spec.org/accel/Docs/110.fft.html)核定报告身份。Farkas/Jouppi 1994只有作者页摘要，其余显示文本来自引用它的论文，不能误认作全文，因此未加进正文。

DD-L1D、NOMAD、SIMD miss tolerance、Vortex多端口cache及新LLM/调度方向保持候选或此前阅读等级；没有为了年份或数量加入。CACTI也不在尚未选定实际成本工具时被引用成已使用方法。完整性指本轮文献与改稿闭环，不是穷尽性新颖性证明。

## 书目与交付

新增4条为Kroft重印、Volta白皮书、Poise、ISPASS2017带宽研究。Parboil的Hwu姓名采用明确BibTeX姓/名格式修复排版；仍是IMPACT-12-01技术报告。Tuck等和其他未确认的可选页码不猜。项目记录的印刷标签缩短，超链接仍使用完整不可变提交及review-pack路径。

新稿实际为4页技术内容＋第5页参考文献，20条均被使用，默认IEEEtran字号/行距/边距不变。清理辅助文件后重新编译成功，最终无未解析引文、Underfull/Overfull或LaTeX警告，全部字体嵌入且无Type3。PDF182737字节。全部五页渲染审阅；这些仅为文稿工件检查，不是IEEE PDF eXpress或科学验收。

用户下载包包含完整LaTeX、PDF、逐条来源/实际引用位置、补丁及数值不变哈希。远端只保存原创文献笔记和书目，没有第三方PDF或字体。没有改Core、配置、主线handoff，没有模拟器或RTL运行，也不授权重开已冻结实验。计时公平、强化传统参照、作者信息与硬件结果仍待补。
