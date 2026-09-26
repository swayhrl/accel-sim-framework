# 当前相关工作与创新点表述边界｜Round 2

更新：2026-09-26。本页替换Round1的未取文判断；旧版保留在提交`9d1026d3c49d56c584e074a76071c90a456aebce`。四篇新依据均来自用户上传PDF，详见[Round2综合](round2/ROUND2_SYNTHESIS_ZH.md)。本页是我们的综合比较，不是新颖性已经得到排他证明。

## 1. 相关工作分三组

**映射/局部性。** NuRAPID、V-Way作为历史基础；ICS2015 Decoupled L1D明确将GPU Tag与Data分离，用复用频次和位置指针控制数据插入。不能称GPU Tag/Data分离为DTC首次提出。

**缺失状态的组织。** DL-MSHR动态链接slot set，在新地址和同址消费者之间分配等待资源；MiCache把cache entry和MSHR entry的空间统一，并以stash处理冲突及子项溢出。它们是结构先例，而非只做调度或把MSHR简单加大。

**访问流与并发控制。** CCWS用失去局部性的历史Tag反馈限制load发射；上一轮MRPB、MeDiC、SACAT、Poise等从其他位置控制请求/并发。当前DTC下游实验的意义是解释本结构的适用范围，不是首次发现并发与缓存/内存的权衡。

## 2. 本轮必须收紧的区别

MiCache §4.4的f=1 stash保存旧消费者记录，忽略新PE请求查找但仍处理内存响应。这与“旧状态不再对新请求可见，却不能马上丢弃”有概念重叠。

因此DTC应比较更具体的**状态归属**：新查询的逻辑Tag、未完成指令的PIB/依赖、数据最终所在物理行、Tag被替换后的消费者引用以及释放条件。可以说与MiCache的cache/MSHR空间转换不同；不能跳到“任何前人都未分离可见性与生命周期”。

DL-MSHR同样有动态等待者组织/回收。“不用传统独立MSHR”是一项结构描述，不能单独证明状态更少、没有合并限制或首次突破并发瓶颈。

## 3. 中文相关工作段落草稿

已有研究从数据放置、缺失状态与请求调度三个层面改善缓存效率。NuRAPID和V-Way通过间接关联分离地址查询与数据放置，Li等进一步在GPU L1中利用扩展Tag存储进行局部性过滤。针对缺失状态，DL-MSHR将固定entry/slot组织改为动态链接的slot-set池；MiCache则使缓存数据与MSHR子项共享存储，并使用stash处理冲突和溢出。CCWS等工作通过改变load发射资格保护缓存局部性。本文基于既有DTC设计，关注可搜索Tag、等待指令元数据与物理数据行之间的归属和回收关系，而不是将间接映射、动态等待资源或节流本身作为新的基本思想。尤其与MiCache区分时，需要比较其等待记录保留与DTC物理数据行保留的具体目的和规则。本文的性能与资源干预用于评估这一具体组织，不构成与上述方案的跨平台数值排名。

这是内部中文草稿，引用位置和篇幅应随全文压缩；“基于既有DTC设计”的自有工作来源需要在正式论文中按作者关系与出版情况准确处理，不由本笔记替代。

## 4. 英文精简草稿

Prior cache designs decouple address lookup from data placement, and locality-driven GPU bypassing applies separate tag and data stores to selective insertion. Miss-handling proposals address a different resource trade-off: DL-MSHR dynamically links slot sets to accommodate primary and secondary misses, whereas MiCache shares storage between cache data and MSHR subentries. MiCache also retains overflow records for response processing while excluding them from new-request matching. CCWS instead shapes the access stream by controlling load-issue eligibility. The DTC organization considered here must therefore be distinguished through the ownership and reclamation of searchable mappings, pending-instruction metadata, and physical data lines, rather than through indirection or dynamic allocation alone.

本段不是“first”或优越性声明，也没有把所测队列/DRAM诊断写成前人没有研究过的一般规律。

## 5. 禁止或需要限定的句子

| 表述 | 当前处理 |
|---|---|
| 首次在GPU中分离Tag与Data | 不使用，ICS2015已有直接先例 |
| 前人都是固定MSHR，我们才动态 | 不使用，DL-MSHR直接反例 |
| 不需要独立MSHR所以没有等待状态开销 | 不使用，须列状态实际去向 |
| 旧状态不参与新查询但继续服务旧请求是独有创新 | 不使用泛化表述，MiCache f=1必须比较 |
| MiCache只是FPGA，所以无需比较 | 不使用，先比较机制再区分成本平台 |
| DTC总体比DL-MSHR/CCWS快 | 当前无同平台同预算对照，不支持 |
| 我们首次发现并发过高会降性能 | 不使用，CCWS等已明确研究 |
| CCWS击败固定流的Belady最优 | 错误；不同scheduler流且Belady不报IPC |
| 本轮四篇读完，因此新颖性查全 | 不支持；参考链及源码边界仍存在 |

## 6. 本轮不引出的工作

不因此修改冻结结果，不自动启动CCWS、DL-MSHR、MiCache复现，不新增自适应控制。当前可立即落实的是相关工作措辞、架构状态图、硬件成本分项和实验统计口径。需要更强竞争声明时，另行评审其必要性，而不是为填表无边界扩实验。
