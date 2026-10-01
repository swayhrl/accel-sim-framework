# C16文献支线LR03：近邻能力、论文故事与最小强基线

日期：2026-09-27。维护者：ChatGPT。

状态：**RESEARCH_DESIGN_ONLY_NO_EXECUTION_AUTHORITY**。本轮没有启动模拟或GPU实验，没有修改Core、运行配置、trace、Lane 4或已冻结的Lane 3结果。

## 0. 阅读起点与记录边界

本轮先读取远端 `swayhrl/accel-sim-framework` 的 `hrl/c16-chatgpt-literature-notes-v1`。读取时该分支与交接记录 `49c01401200f7944db31d066ebb331a9ba701882` 比较为identical，ahead=0、behind=0。

已读文件：

- `docs/vm_tlb/literature_notes/c16/README.md`，blob `614456082c55d17727254aa3462dadf61249b3fe`。
- `docs/vm_tlb/literature_notes/c16/rounds/2026-09-27_LR02_REUSE_SURVIVAL_AND_UTILITY.md`，blob `37d23af2383bd4309839c9505816b71d72f958e6`，完整读取。
- Lane 3冻结提交 `a402828860ced26124ddbf3c9d87baa6f6774d55` 下的 `docs/vm_tlb/review_packs/C16_E1_PAPER_EVIDENCE_AND_RESULT_INFRASTRUCTURE_V1/RELATED_WORK_INDEX.md`。该快照的E1文献入口仍为PENDING_LOCAL_AUTHORITY；不回写冻结文件，未来V2接入LR02/LR03。

项目科学事实沿用用户提供的 `C16_AI_WORKLOAD_HANDOFF_CONTEXT_2026-09-27_M1F_READY_LANE4_RUNNING.md`，不是本轮重新验收历史实验。Lane 4进度只是交接快照，本轮没有检查其新日志或据未闭合结果选解释。

LR02已经明确的“层间公平≠旧地址存活≠系统收益”、Talus地址采样近邻、AutoScratch附录SHiP-SW等，仍属于既有积累，不记为本轮新发现。

## 1. 本轮真正新增或加深的认识

### 1.1 最应增加的近邻对照，是简单稳定子集加优先级

**我们的研究判断：**仅比较R0、M1与M1F，能够说明在当前quota框架下改变eligibility是否有效，却不足以证明整套框架相对已有简单能力的增量。

应额外考虑：给与M1F完全相同的冻结地址子集较高替换优先级，但不启用M1的硬quota逻辑。它回答：是否只要“选对一小部分地址并优先保留”就已经足够？

这叫 **P_stable能力对照**，不是Talus完整复现，不是NVIDIA实际replacement重建。不能另外实现一个“相同stable selector＋相同M1硬quota”的方案，再把它包装为独立baseline；这在机制上就是M1F。

### 1.2 AutoScratch的附录比较不能被误读成完整timing比较

**作者原文：**附录A.1提出SHiP-SW，由软件给出关键地址区域，硬件只对关键signature学习resident/regular分类。A.2说明：不同替换决策会影响并发GPU的L2访问顺序，因此其比较记录默认策略下的L2访问序列，再输入独立Python功能模型，评价SHiP/SHiP-SW/Belady的DRAM流量。Figure 11的硅片—模拟对照也是normalized DRAM traffic。[S02]

**我们的推论：**这支持借鉴其软件辅助学习能力，但不支持把固定访问顺序下的miss/traffic排名当成C16完整周期排名。Lane 1的地址reference proxy也不能直接充当这种已记录的L2事务序列。

### 1.3 CUDA官方已把fractional persistence与抗抖动联系起来

**接口事实：**CUDA文档明确允许ordinary/streaming访问使用尚未被persisting数据占用的set-aside空间；并给出通过降低hitRatio缓解超容量window自我抖动的例子。[S03]

**必须保留的区分：**文档没有为C16证明“同一地址跨token永远获得相同属性”，也没有证明“每次访问都独立重新抽签”。缺少稳定性保证不等于已证实不稳定实现。

因此，一个自行定义的event-fractional模拟器对照不能命名成“真实CUDA实现”。已有native CUDA结果继续作为外部证据，不能用自行设弱的CUDA-like模拟策略取代。

### 1.4 CPU cache-resident LLM也研究了权重与attention的相互干扰

**作者原文：**《Cache-Resident LLM Inference in GB-Scale Last-Level Caches》不仅提出权重驻留，还通过weight–attention执行域分离与同步组织处理驻留受到干扰及驻留后出现的成本。正文区分有限部署的端到端实测、分析模型外推和机制消融。[S05]

**与C16的区别：**该工作围绕GB级CPU LLC与执行放置；C16保留现有GPU程序及连续上下文，研究远超64MiB L2的target集合中，有限子集怎样存活。不能因平台不同忽略其问题近邻，也不能将CPU系统直接当作同平台replacement baseline。

## 2. 逐项原文核读与能力映射

| 工作 | 本轮阅读深度与定位 | 作者内容 | C16定位 |
|---|---|---|---|
| Talus，HPCA 2015 | 作者PDF，复核§III–VI，尤其§V-C/§VI | 通过地址采样、shadow partitions与miss curve处理容量悬崖；区分地址采样、事件插入与真正bypass | 稳定子集的直接思想近邻；不能把hash-based subset当独立新发明 |
| AutoScratch，MLSys 2023 | 会议正文相关部分及附录A.1–A.2；第16–17页截图复核 | 搜索驻留配置；附录软件关键region＋硬件复用学习；功能模型评价流量 | 最重要的GPU软件辅助强基线来源；使用SHiP-SW-style能力适配，不冒充完整AutoScratch复现 |
| Vantage，ISCA 2011 | 作者PDF，复核分配/落实、managed/unmanaged与候选相联度讨论 | 将资源分配与落实分开，通过替换控制细粒度分区 | quota落实与借用近邻；若不主张一般分区创新，不必复现整套系统 |
| Cache-Resident LLM Inference，arXiv 2606.25353v1 | 从摘要升级为正文，§2.3–6相关机制与方法 | CPU LLC驻留、weight–attention分离、同步组织；实测与外推分开 | 系统问题近邻和评价边界参考，不是直接GPU策略baseline |
| APCM，ISCA 2017 | 新增作者机构提供的PDF，重点§4–5 | 按load复用类型管理L1，利用消费者依赖估计保护寿命 | 说明reuse-aware保护已有GPU先例；主要时间尺度为kernel内，当前RELATED-WORK-ONLY |
| CUDA L2 Cache Control | 官方§4.13.1–4.13.5 | set-aside借用、access window、hitRatio及抗抖动说明 | 必须保留native参照；接口不等于已知内部实现 |
| PTX createpolicy/eviction hints | 官方ISA相关段落 | range/fractional cache policy及架构要求 | baseline接口能力依据，不是内部replacement规范 |

阅读范围说明：这些不是七篇新论文。Talus/AutoScratch/Vantage属于加深旧记录；Cache-Resident LLM属于补正文；APCM是新增正文条目；CUDA/PTX是文档。未运行任何论文代码。

本轮仍未闭合DIP、RRIP、原始SHiP及MICRO 2025 GPU eviction hints的完整原文实现合同。前三者不能用熟悉算法名称代替原文核实；MICRO 2025仅有作者说明，具体硬件矩阵与内部推断仍未核实。PRESERVE和Marlin沿用LR02已标明的阅读深度，不虚增本轮全文阅读数量。

### 2.1 Talus与M1F：相近，但不能直接画等号

Talus采用地址采样；其理论将bypass作为一个大小为零的shadow partition的特殊情况，并明确列出假设及对不同基准策略的限制。[S01]

M1F只限制protection eligibility，未选中的qweight仍按普通规则使用L2，并非全部绕过L2；它也没有实现Talus的miss-curve/convex-hull分配。因此，本轮不能宣布两者等价，更不能引用Talus的理论给M1F背书一个GPU timing最优性结论。

合理做法是保留最接近的简单能力对照。若将来主张优于完整Talus，仍需要合法、完整的同平台适配，不能用P_stable替代该主张所需的实验。

### 2.2 SHiP-SW应给与候选相同的语义信息

建议移植时把同一份28个up_proj.qweight地址区域交给SHiP-SW-style基线。不能让候选知道qweight，baseline只知道通用PC，再把所有差异归为策略优势；也不能机械沿用原文应用中的activation关键区域，故意不给基线与C16对应的信息。[S02]

需要核实其有限SHCT、signature粒度、outcome更新、碰撞、metadata与请求标记成本。若叠加M1硬quota，应单独标成C16 hybrid，而非原论文原样实现。

**待验证假设：**kernel内重复访问可能把某region训练成“有复用”，但这一标签未必对应跨完整decode间隔的保留效用。这是后续可检验的问题，不是已经证明SHiP-SW在C16失败。

### 2.3 不能把新PTX语法倒灌到SM89实验

官方ISA区分不同cache hint形式的架构支持：createpolicy及相应L2 cache-hint路径与较新的直接L2 eviction modifier不是同一支持条件。[S04] 后续native能力适配应核实际工具链与SM89合法路径；本轮不改现有部署或trace。

## 3. 论文故事：从局部价值到净收益，而不是从M1写到M1F

建议工作标题：**《从局部驻留到有效复用：低比特LLM解码中的共享L2管理》**。这是故事方向，不是冻结投稿标题。

### 3.1 中心问题

> 当某些低比特权重具有局部驻留价值、但全部候选权重远超L2时，怎样把有限保护容量转化为跨完整复用间隔的有效命中，并使其收益大于对其它执行的代价？

论文论证顺序建议如下：

1. **机会**：当前量化部署中，部分projection的压缩状态进入可能的L2容量区间，局部实验确有价值。
2. **落差**：自然执行破坏孤立热态；保护、扩覆盖、扩family并不自动形成whole-decode收益。
3. **问题拆分**：eligibility、admission、old-address survival和timing是四个不同环节，不能由占用或aggregate hits互相替代。
4. **机制比较**：M1回答硬上限内的全量target保护是否足够；M1F只在相应gate通过后回答稳定eligibility是否补上缺口。
5. **净收益与边界**：最终用完整测量范围、其它semantic work代价、实现成本与强基线决定贡献，而不是用机制名字决定贡献。

其中第1–2项主要依托已冻结native链；第3项部分为结构证据与待验机制解释；第4–5项的性能结论仍待闭合。不能把写作顺序变成结果预设。

### 3.2 Contribution framing

| 候选贡献 | 现在可以写什么 | 现在不能写什么 |
|---|---|---|
| C1：部署相关的驻留机会 | 当前RAW/AWQ实施路径下的容量几何与局部residency sensitivity | 纯bit数因果；所有低比特后端/LLM普遍适用；首次权重进cache |
| C2：local-to-system gap的定量闭合 | 在当前完整native decode中，将local gain与其它semantic work代价对应起来，揭示局部收益未转化为系统收益 | 首次发现cache污染；唯一原因就是L2冲突或target-target churn |
| C3：面向有效复用的机制贡献，条件项 | 用明确资源与信息条件，检验保护准入是否带来旧地址存活和净周期增量 | M1F已产生性能收益；stable hash本身新颖；已实现最优效用分配 |

采集—对象身份—连续trace—独立consumer构成支持证据的方法，不作为主要机制创新。

更适合当前证据的定位是**measurement-driven architecture research**。若后续强基线之后仍有明确增量，可发展为机制论文；若简单已有能力已覆盖收益，则保留解释与证据，不为“挽救M1F”继续添加功能。

### 3.3 必须收紧的两个词

**Cost-aware**现在是研究目标，不是已实现特性。M1/M1F约束保护字节，但没有因此自动测量其它工作每个周期的机会成本。

**Fairness**不是最终目标。28层属于同一次decode，并非28个独立租户；等份占用不是天然系统目标。M1F的稳定资格也不提供每层占用、每地址存活或性能下限。

## 4. 最小强基线：先覆盖能力，再决定实现数量

以下是未来形成机制主张时的设计需求，**不是现在授权运行的矩阵**。

### 4.1 MUST-HAVE

| ID | 能力/角色 | 主要回答的reviewer objection | 状态与公平条件 |
|---|---|---|---|
| R0 | 冻结原始replacement、无候选机制 | 基准是不是被改弱了？ | 复用身份匹配的accepted结果，不调平台 |
| N-CUDA | 已冻结native targeted/shared/coverage/cost-benefit证据 | CUDA现成接口是否已经做过类似事情？ | 保留已有证据，不重跑；不与模拟cycle直接混算 |
| P_all | 同样target identity，全量target仅提高优先级，不使用M1硬quota | M1是否只是priority hint的包装？ | 同64MiB物理容量；不是B16严格预算匹配实验 |
| P_stable | 与M1F相同冻结stable subset，仅提高优先级 | 简单固定子集＋优先级是否已经足够？ | 同selector、不调seed；必须报告实际分区占用 |
| A_scan | 至少一个无需模型语义的成熟抗扫描/抗抖动策略 | 只赢LRU，是否只是经典抗抖动收益？ | DRRIP为优先候选；原文实现合同尚待补齐，不同时铺开整族算法 |
| A_semantic | 软件关键region＋硬件复用学习 | 是否只因候选拿到了更多语义信息？ | 以AutoScratch附录SHiP-SW-style为来源，给同一份qweight区域；明确适配与成本 |
| M1 | global elastic hard quota＋全量target eligibility | 仅容量约束是否已足够？ | 当前Lane 4，不改运行 |
| M1F | 同quota下的stable fractional eligibility | 地址选择是否补上M1缺口？ | 候选，不是外部baseline；仅当Lane 4 project gate授权后进入timing |

这里的MUST-HAVE是论文能力覆盖，不要求现在新增八条simulation，也不要求所有对照都先完整实现。R0、N-CUDA、M1已有工作；M1F有资格但无timing授权；其余先做源代码语义映射与原文合同，最终依拟主张决定运行。

### 4.2 最有解释力的2×2能力表

| 保护资格 | 仅priority，无M1硬quota | M1硬quota框架 |
|---|---|---|
| 全量target | P_all | M1 |
| 冻结stable subset | P_stable | M1F |

它把“选择哪些地址”和“如何落实容量约束”分开。横向不是天然的严格等预算消融；左列没有B16硬上限，必须说明这一点。若源码审查证明某两个格子在给定条件下完全等价，应记录等价，不重复实现和长跑。

### 4.3 为什么P_stable是很强、而非故意设弱的对照

交接中的冻结选择结果为：130,571个selected lines，小于B16总quota 131,072；但每subpartition为7,956–8,269，而均分quota是8,192。全局静态总量能容纳，**不等于每个局部硬quota都满足**。

因此，P_stable可能在同64MiB物理L2下保留更多局部selected lines；这不应被悄悄禁止，也不应被称为与M1F完全相同的容量保证。比较时分开报告物理容量、global protected occupancy、每subpartition resident+pending、ordinary代价和执行时间。

若P_stable已达到相同或更好的系统结果，而M1F没有可量化的资源、代价或实现优势，现有M1F不能仅凭“更严格”成为机制贡献。反之，有硬上限下的实际优势，也仍要比较相关资源控制近邻并说明代价。

## 5. 必要消融与可选近邻

### 5.1 Stable eligibility主张需要一个非稳定fractional对照

这一项的功能不同于A_scan：它检验“稳定”本身，而不是泛化替换算法。

建议未来定义 **EVENT_FRACTIONAL_CONTROL**：在明确的独立target allocation事件上，以同一名义比例决定eligibility；同一个请求的重试和MSHR生命周期不重新抽签；其余hard admission、ordinary规则保持可解释。最终在哪个pipeline事件取样，需先核accepted source，不能在此直接冻结代码语义。

必须说明：这是自定义非稳定机制消融，不是NVIDIA真实hitRatio实现；相同名义比例也不自动意味着相同unique coverage或实际admissions，应一并报告。结果若只能由实际admission数量差解释，不能直接归为跨token稳定性优势。

### 5.2 NICE-TO-HAVE / 条件必须

| 对照 | 什么时候有价值 | 不应怎么做 |
|---|---|---|
| fixed protected partition | 论文确实主张elasticity优于不可借用静态容量时 | 不能把固定4/16way叫真实CUDA；way切分也改变候选相联度，不是纯借用开关 |
| weight streaming/evict-first能力 | 检查放弃权重长驻是否反而保护更有价值的ordinary工作 | AWQ trace上的策略修改不能叫Marlin复现 |
| 完整Talus或Vantage适配 | 主张优于其完整能力，或一般性分配/落实创新时 | 不因论文年代旧或CPU平台而直接忽略；也不立即重建全套系统 |
| 更多抗扫描策略或M1-on-另一replacement | 首个强基线暴露差异，或主张跨replacement稳健性时 | 不先铺BIP/DIP/DRRIP/SHiP全参数网格 |
| 固定同源序列的oracle/Belady功能对照 | 确有必要估计该序列的miss空间时 | 不称GPU timing上界，不用Lane 1 proxy冒充实际L2序列 |

### 5.3 RELATED-WORK-ONLY（以当前主张为限）

APCM的kernel内L1保护、PRESERVE的使用前预取/通信重叠、GB级CPU cache-resident执行、以及UCP/PIPP的一般分配思想，目前无需各自完整复现。理由是它们不对应当前最小对照中的同一控制变量，而不是“不同平台就不相关”。若论文主张扩展，对照义务随之改变。

MICRO 2025 eviction hints论文仍需要补全文；现阶段只用于提醒真实GPU hint行为需要实测，不用未核实内部机制来定义模拟baseline。

## 6. 最终证据链应该怎样衡量

以下是论文评价设计，不要求在Lane 4进行中添加counter或改binary。

### 6.1 四个层次必须分开

`oracle_target → protection_eligible → protected_admitted → old-generation survival → next-use hit → local cycles → measured-window cycles`。

“同一个地址再出现”不等于“上一轮那条resident line一直活着”。被淘汰后重新填入相同地址，也可能产生大量kernel内protected hits。要支持跨token存活，应依据已接受diagnostic的旧地址/世代证据；现有观测区分不了时明确标记未辨识，不能补造结果。

同时报告两种分母：对全部目标/全部eligible的有效保留，与条件于已admitted旧行的survival。否则少量admission的高条件存活率可能掩盖低覆盖。

### 6.2 B16 footprint比例不等于性能上界

B16约等于一个32.375MiB qweight的49.42%，但仅是28个target总footprint的约1.765%。它提示不能把“稳定活了一小部分”自动写成“明显decode加速”；也不能反过来直接把1.765%当速度提升上界。关键路径、访问频次、流量组织与ordinary代价仍需实际证据。

### 6.3 当前1565-kernel窗口是机制canary，不是全层稳态decode

Lane 4测量范围是D1完整加D2到L0 up_proj结束。它保留L0的完整自然reuse interval，但不能单独证明28层各自下一轮复用都获益，也不能把D1暖态建立成本与稳态TPOT混成一个数。

因此本轮不改当前scope、不追加timing。将来若要系统级主张，应单独设计与该主张匹配的范围，并防止针对当前L0终点选择对L0特别有利的策略。

### 6.4 泛化按问题选择，不按已有模型数量选择

未来最小泛化方向是：一个相同语义但不同低比特后端，用于检查实现依赖；一个独立模型家族，用于检查几何/复用解释；少量明确改变batch或context压力的边界点。先审已有资产与证据能覆盖什么，再决定是否需要新采集。它们不是当前已批准任务，更不是模型×场景全组合。

## 7. 与Lane 4冻结解释合同的关系

本轮没有更改预注册gate或增加新的数值门槛。

- M1缺乏足够window benefit，且合格diagnostic支持高protected→protected churn/低old-address survival：才优先审M1F timing。
- survival本来良好但没有收益：优先查复用价值、critical-path coverage与collateral cost，不因M1F已实现而运行。
- M1已足够有效：不为形成第二个机制增加复杂度；优先检查已有强基线之后是否仍有增量。
- hard admission denial主导：先分离invalid-priority和no-local-protected-victim，不能把admission realization失败重新命名为fairness。

R0、M1、diagnostic必须有终态、identity、neutrality和source authority闭合。Speculative diagnostic按原合同admit。收到Codex报告时先核commit/review pack/provenance，再讨论性能解释。

## 8. 本轮决策

**保留研究问题，降低对机制名称的承诺，提高对最接近能力的比较要求。**

当前论文最重要的增量候选，不是“首次有elastic quota/region hints/stable sampling”，而是：在低比特decode的完整复用上下文里，量化局部价值、具体旧行存活与系统机会成本之间的关系，并检验一个简单、可实施策略是否比已有强能力提供额外价值。

当前不发新的Codex长跑Goal，不启动M1F、其它budget或完整baseline matrix。本文档只为Lane 4返回后的决策和未来Lane 3 V2准备依据。

## 9. 原始来源与检索限制

[S01] Nathan Beckmann, Daniel Sanchez. *Talus: A Simple Way to Remove Cliffs in Cache Performance*. HPCA 2015. 作者PDF：https://people.csail.mit.edu/sanchez/papers/2015.talus.hpca.pdf 。核读正文§III–VI；本轮部分截图请求失败，未依靠图中柱高推导性能数字。

[S02] Yaosheng Fu et al. *AutoScratch: ML-Optimized Cache Management for Inference-Oriented GPUs*. MLSys 2023. 会议PDF：https://proceedings.mlsys.org/paper_files/paper/2023/file/9d32b9324a89001520ae456b9e5ec73b-Paper-mlsys2023.pdf 。主要定位§2–4与Appendix A.1–A.2；第16–17页截图核读。本文不复制原图，不转发PDF。

[S03] NVIDIA. *CUDA Programming Guide, 4.13 L2 Cache Control*. https://docs.nvidia.com/cuda/cuda-programming-guide/04-special-topics/l2-cache-control.html 。访问日期2026-09-27；尤其§4.13.1–4.13.3。官方API语义不等于内部replacement实现。

[S04] NVIDIA. *Parallel Thread Execution ISA*. https://docs.nvidia.com/cuda/parallel-thread-execution/index.html 。访问日期2026-09-27；cache eviction priority hints、createpolicy及Target ISA Notes。版本相关要求只用于未来设计，不回写现有实验。

[S05] Wanning Zhang, Tongzhou Gu, Marco Canini, Ceyu Xu, Jian Weng. *Cache-Resident LLM Inference in GB-Scale Last-Level Caches*. arXiv:2606.25353v1. https://arxiv.org/html/2606.25353v1 。明确使用v1，不冒充最终会议稿；重点§2.3–6，实测/外推分开。

[S06] Daniel Sanchez, Christos Kozyrakis. *Vantage: Scalable and Efficient Fine-Grain Cache Partitioning*. ISCA 2011. https://people.csail.mit.edu/sanchez/papers/2011.vantage.isca.pdf 。本轮复核allocation与enforcement、managed/unmanaged、候选相联度边界。

[S07] G. Koo et al. *Access Pattern-Aware Cache Management for Improving Data Utilization in GPU*. ISCA 2017. 作者机构入口：https://csarch.korea.ac.kr/publication/gpu_apcm_isca17/ ；该入口提供的原文：https://filedn.com/luEeJVCCazShDlU4ibloXvu/publication/gpu_apcm_isca17/gpu_apcm_isca17.pdf 。重点§4–5；图表截图请求失败，本文只据可解析正文描述机制，不取图中数值。

[S08] Qizhong Wang et al. *Security and Performance Implications of GPU Cache Eviction Priority Hints*. MICRO 2025. DOI:10.1145/3725843.3756116。作者书目：https://qizhong-wang.github.io/ ；实验室说明：https://cuda.fail/ 。本轮仍未取得可核读全文，只有作者说明，不构成内部机制实现依据。

[S09] LR02已登记的DIP/UCP/原始SHiP/PRESERVE/Marlin原始来源与阅读等级，保留在同目录 `2026-09-27_LR02_REUSE_SURVIVAL_AND_UTILITY.md`。未闭合的DIP/RRIP/SHiP原文不以二手博客补成已读全文；DRRIP只是本轮推荐的抗扫描基线候选，具体实现合同待审。
