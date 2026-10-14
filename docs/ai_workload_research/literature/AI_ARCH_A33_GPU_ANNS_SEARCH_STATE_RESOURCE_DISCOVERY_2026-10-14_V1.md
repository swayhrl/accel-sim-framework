# Round A33｜GPU向量检索：搜索状态、重复工作与查询并发的资源权衡

**执行者：ChatGPT／AI-ARCH Discovery；日期：2026-10-14。**

**协调起点：** `80c4362fbe79fc92fb82c786513153a4f7231bb7`。用户批准继续Discovery，并报告Lane M还需数小时。本轮未连接109/174/164，未操作GPU锁、模型、实验环境或Codex。A26GR1保持原合同；A30T/A30N保持已审STOP；A31仍为储备。只有公开原文、官方固定源码、元数据和控制端纯算术推导；0新节点任务、0模型/数据/依赖下载、0模拟器/硬件机制。

## 0. 本轮结论与新增价值

保留一个新的**发现性负载候选**：GPU图式近似最近邻检索（ANNS）的每查询搜索状态与资源组织。它属于AI系统检索算子，不是神经网络forward，也不等于完整RAG。相较A30T的SM90a专属路径、A30N缺强GPU实现，当前候选有cuVS现成CUDA实现、可控状态参数和较小真实向量数据源；但**本机可运行性、实际瓶颈、性能剩余与机制新颖性仍未验证**。

科学问题不是“首次发现少存状态可以多算一点换性能”。CAGRA和Jasper已经研究此权衡。唯一待查问题是：**固定图、真实查询与质量条件，在已有历史表、单/多CTA、线程组织和持久执行能力之后，搜索状态占用与重复工作是否仍形成稳定、值得硬件干预的资源限制？** 更换查询批次、hash参数的性能曲线本身不是硬件创新。

本轮新贡献限于：三类候选筛选；最新固定源码中的多变量耦合识别；一张可复算的状态字节/寿命表；一个不需新机制的最小原生诊断设计。没有声称发现新硬件瓶颈。

## 1. 横向筛选与阅读深度

| 对象 | 核查入口及已知能力 | 本轮处理 |
|---|---|---|
| 推测解码中的变长验证 | [DScale，arXiv 2609.37532](https://arxiv.org/abs/2609.37532)，摘要及Introduction：已有路径相关tile、动态验证长度和固定地址CUDA Graph工作区。A10040GB作者实验，不是4080资格。 | 不重复提出“变长验证去padding＋动态图捕获”；只有该直观入口降级，未否定整个推测解码方向。 |
| 大beam线性注意力推荐 | [OneLA，arXiv 2609.12399](https://arxiv.org/abs/2609.12399)，摘要及Introduction：共享prompt状态、追加式GDN转移记录、祖先索引和跨beam fused GPU复用。 | 不重复提出共享状态/延迟重建；未开展作者实现固定源码或native审查。 |
| 图式向量检索 | [CAGRA v2 §IV-B–D](https://arxiv.org/html/2308.15136v2)、Jasper可视PDF指定页、IVF-RaBitQ §3.4/4，以及下文cuVS固定源码。 | 保留一个有实验出口的资源诊断候选，不先搭完整RAG或开发新index。 |

领域边界依据：[ASPLOS2025《Accelerating Retrieval-Augmented Generation》出版者摘要](https://doi.org/10.1145/3669940.3707264)确有检索加速与CXL近存硬件研究，但对象是exact retrieval及完整RAG，**不是本轮CAGRA控制状态机制**。其结论还提醒：检索质量会改变生成负担，因此不能把ANNS局部吞吐提升直接写成RAG加速。本轮对此文仅摘要级，不引用硬件加速数字作本机论据。

## 2. 强近邻到底已经解决了什么

### CAGRA：遗忘历史是已有设计，不是错误

[CAGRA v2 §IV-B3/B4、IV-C、IV-D2/D3](https://arxiv.org/html/2308.15136v2)使用visited hash避免重复距离计算，并已有小型shared-memory表的周期清理及frontier重新登记；还用节点标志记录已扩展状态。作者已经比较小型遗忘表与完整global表、单CTA与多CTA。不能把这两种已有模式的差值直接命名为新硬件空间。

### Jasper：少记录有时比完全避免重算更有利

[Jasper PDF入口](https://arxiv.org/pdf/2601.07048)，可视首页为`2601.07048v5 / 31 Jul 2026`，本轮核可视p6 §4.1–4.3：作者移除来自CPU方案的有损历史hash及deferred merge，以减少状态/控制负担；较小线程块和较大线程块分别偏向查询并发和单查询计算资源。这里不是“所有状态都可以删除”，也不是我们测得的收益。

**版本审计限定：** 本次PDF文本解析与可视页的部分小节/消融内容不一致；仅采用可视页确认的机制，不引用不一致的ablation数字、512B容量或图号结论。未取得固定作者源码、未执行或逐图复算。Jasper是强反证入口，不能据此认定CAGRA当前所有状态管理都冗余。

### IVF-RaBitQ：图式检索也必须接受其他算法路线的反证

[IVF-RaBitQ v1 §3.4、§4.1](https://arxiv.org/html/2602.23999v1)已有LUT与bitwise两种算术/SMEM折中、cluster-local融合及按阶段复用shared memory。其GPU实验为单L40S48GB，通常10k查询batch；不是4080低batch数据。它表明当前不能把CAGRA称为所有条件下的最强ANNS，更不能将“重用临时片上buffer”本身当新机制。首次固定CAGRA诊断无需完整复现全部ANN算法；真正申请通用检索硬件结论时，应比较适用的强替代方案或限制claim。

## 3. 固定官方源码：不从论文旧版本推当前实现

实际读取`NVIDIA/cuvs@bc23aa84a0ef26d85900185ad5e68d3372be487e`；GitHub该提交时间2026-10-14T02:48:48Z。旧`rapidsai/cuvs`入口重定向到NVIDIA所有者。此为本轮固定研究快照，**不是论文实验commit，也不等于已验证发行包**。

| 源文件 | Git blob | 核查范围 |
|---|---|---|
| `cpp/src/neighbors/detail/cagra/search_plan.cuh` | `a6d1bd12047a55673aecda44ccbd2c61b3f9da16` | 1–420：AUTO模式、search参数调整、history表容量与清表间隔 |
| `cpp/src/neighbors/detail/cagra/search_single_cta.cuh` | `8fd50a15496df3172aa4ed383b025a74f2d9301c` | 1–250：SMEM字节、自动block尺寸、global hash分配 |
| `cpp/include/cuvs/neighbors/cagra.hpp` | `418db9d88f508525cd081ace26efa645bc1fe570` | 160–350：图构造参数、dataset非拥有视图/lifetime |
| `README.md` | `b66b075fdc3b47d72ab3846915cb632de111a18e` | 1–150：用途、当前官方文档、发行方式 |

[固定planner](https://github.com/NVIDIA/cuvs/blob/bc23aa84a0ef26d85900185ad5e68d3372be487e/cpp/src/neighbors/detail/cagra/search_plan.cuh)揭示三项应进入实验合同的事实：

1. **算法AUTO不是固定算法。** 非persistent时，它依据`itopk_size<=512`与有效`max_queries>=2*num_sm`选择single-CTA，否则multi-CTA。有效max_queries仍需核API到planner的实际传入，不能只按用户batch名称推断。
2. **当前multi-CTA不是只有一种global visited表。** 代码分别维护CTA私有shared visited表与CTA间共享的traversed表，前者会清理重建。旧论文TableII的简表不能替代当前完整实现。
3. **SMALL容量与寿命共同变化。** `hashmap_min_bitlen`可能增大实际表，也使planner自动延长reset interval；如果让block大小保持AUTO，增加SMEM还可能导致更大block。这同时改变软件工作、执行粒度和资源占用，绝非“仅扩大硬件存储”。

[固定single-CTA源码](https://github.com/NVIDIA/cuvs/blob/bc23aa84a0ef26d85900185ad5e68d3372be487e/cpp/src/neighbors/detail/cagra/search_single_cta.cuh)的`set_params`还依据候选数选择排序路径、依据SMEM和查询数量调整block。诊断必须保存**调整之后**的algo、hash位数、reset、block/team、迭代上限；相同CLI参数不保证相同实际执行形态。

官方[安装文档](https://docs.nvidia.com/cuvs/installation)列当前源码要求CUDA12.2+及Ampere/CC8.0+。因此没有MonoMoE式SM90a硬性排除，但**不证明109的现有driver/runtime、选定发行包和该具体CAGRA路径已资格通过**。未来优先兼容发行物，不修改现有环境/driver；若选发行版，重新核其对应上述代码，不能以main源码替旧包背书。

## 4. 从代码计算一张状态账：不是GPU测量

约定单CTA、uint32索引、float距离，`itopk_size=128`，`graph_degree=64`，`search_width=1`，`hashmap_max_fill_rate=0.5`，无filter；descriptor额外workspace未知。令表项数`2^h`。有效容量满足`128+64 <= 0.5*2^h`。planner逐步增长清表间隔，得到：

`reset_interval = floor((0.5*2^h - 128)/64)`。

| 实际h | 表项 | 仅历史表shared字节 | 清表间隔（迭代数） | 源码基础SMEM字节，不含descriptor/额外workspace |
|---:|---:|---:|---:|---:|
| 9 | 512 | 2048（2KiB） | 2 | 3604 |
| 10 | 1024 | 4096（4KiB） | 6 | 5652 |
| 11 | 2048 | 8192（8KiB） | 14 | 9748 |
| 12 | 4096 | 16384（16KiB） | 30 | 17940 |

基础字节来自`8*192 + 4*2^h + 4*1 + 4*3 + 4`。在同例且完整global HASH的`max_iterations=64`时，planned visited上界4224、填充率0.5使表需16384项，即64KiB/global/query；这不是shared分配。以上以控制端Python重新执行planner算术得到，**未运行cuVS或GPU**。

这张表能证明一个实验设计问题：从2KiB到16KiB同时把遗忘间隔从2改成30。它不能证明重复计算变少多少、recall变多少、占用率多少或会加速。CTA驻留还受到寄存器、线程/warp、SMEM分配粒度和硬件上限约束，不能只拿每SM容量除以上表算真实occupancy。

## 5. 唯一保留的问题及反证

**Q-A33-01：** 在同一真实图搜索中，强软件可选的历史状态组织是否已经充分处理了重复距离计算与查询并发的矛盾？若没有，剩余完整search时间是否对明确的状态服务/片上资源约束稳定响应，且不能仅靠已有block、algo、reset及布局选优解释？

竞争解释：
- **H0：已有软件足够。** AUTO/显式合法选优后差距很小；或所谓状态瓶颈仅是弱路径、默认误选、数值/召回不同、查询供给不足。
- **H1：确有候选资源代价。** 在相同质量下，减少重算与维持并发仍呈稳定冲突，强可实现路径都保留可定位成本。它只支持继续定位，不自动证明需新硬件。
- **H2：主成本不是历史状态。** 距离读数、图拓扑依赖、排序等已经解释search时间；表扩大减少计数但未改善完整时间。

现有论文已经研究这类权衡，所以**只复现“小表快”或“少hash快”不算新发现**。只有出现超出已有能力的具体限制，或者严谨的、跨独立样本可迁移资源规律，才讨论论文贡献。软件调优有效本身可以作为结果，但不能假称新硬件。

## 6. 小型真实workload与资源量级

候选为`GloVe-100-angular`，不是为了已下载资产选题，而是它包含真实向量、查询和ground truth，可低成本观察数据依赖图搜索。

[ANN-Benchmarks固定README@2e081ad32c1eccab72dcb739ad886c310b90f715](https://github.com/erikbern/ann-benchmarks/blob/2e081ad32c1eccab72dcb739ad886c310b90f715/README.md)列1,183,514条100维base、10,000条query和top100真值，HDF5标称463MB。该仓库已声明不再积极维护，**只利用其固定数据说明，不采用其旧CPU排行榜作为强GPU基线**。

条件性FP32容量账：base473,405,600B；queries4,000,000B；拟degree64/uint32图302,979,584B。base+最终图约740.42MiB。**不是峰值显存或磁盘上界**：构图中间图、scratch、padding、距离/排序、运行库、allocator和副本另计。没有下载HDF5、实际数据SHA或构图时间；不宣称16GB已通过。

Angular输入须采用明确的规范化/距离定义，检查zero-norm、浮点舍入与tie规则；参照[cuVS数据转换说明](https://docs.rapids.ai/api/cuvs/stable/cuvs_bench/datasets/)核原始真值与派生向量的对应。不能随意转FP16后仍称同精度。GloVe是经典词向量，不是现代生产RAG请求；它可做发现集，不足以承担所有AI检索的泛化。后续独立现代embedding对象是验证需求，不是现在追加下载。

## 7. 一个12格的发现实验草案：本轮不执行

**目标：** 一次完整search的真实观察，不是先写trace工具/控制器。数据与图构造一次后冻结，构图成本单列，不在不同配置间换图。

拟比较3个batch（1/32/256）×4条现成路径：

| 路径 | 作用 |
|---|---|
| 固定SINGLE_CTA＋SMALL最小位数9 | 较小、较频繁遗忘的既有路径 |
| 固定SINGLE_CTA＋SMALL最小位数11 | 较大、较长历史的既有路径 |
| 固定SINGLE_CTA＋完整global HASH | 另一既有记录方式，不是无限免费oracle |
| 官方AUTO reference | 防止仅在不适当single-CTA上发现人为机会；保存真实所选算法 |

前三臂采用同一个受支持block/team、k、候选宽度、迭代合同和种子；从同一真实query集合分批，不复制一条query冒充并发。具体block/team、图构造器、软件tag/build、dataset派生SHA与query划分在未来canary之后、正式计时之前冻结。控制端提出的上表数字不是作者最优参数，也不是已生效实验合同。

**两种分母必须分开：** 固定算法配置诊断记录recall与路径变化，不能把不同重算/遍历量叫纯硬件干预；实际性能评价则比较同一recall@10目标下强软件的合法选择。ANN结果不必逐bit同一ID，但recall未匹配不得直接排名。必要的少量质量调参单列预算，使用与报告集分离的query；不能无限增加itopk直到找到正例。

先收无插桩search GPU时间、host到完成wall、recall@10、结果/实际planner参数、必要迭代信息；有区别才增加限定的资源诊断，核是否真是state/重算/并发。内部迭代统计有源码入口不等于公共API已经可直接观测，缺失时保留UNKNOWN，不先造一套插桩。profile运行与正式计时分离，不能以NCU序列化后的时间替原始wall。稀疏样本不报尾分位SLO。

**native观察不要求预先拿到完整oracle。** 但任何新机制结论仍需受控因果、真实成本、独立样本及适用层级验证。只见hash比值不同、SMEM大、重复访问多均不够。当前不设计RF/SMEM×2模拟、不抓SASS，不预设Accel-Sim能覆盖cuVS实际kernel。

**停止/降级：** 同召回强软件已吸收；目标时间对状态工作不敏感；差异只来自质量/路径/弱后端；所需部署代价明显超过小probe；或者仅得到CAGRA/Jasper已经解释的结论。不得为保住候选反复换数据/改假说。若只有软件默认选择不佳，报告软件结果而不升级硬件。

## 8. 交付与后续边界

A33完成了source-level候选与最小实验草案，不是批准原生执行。下一项有意义的工作是把这个候选与A31以及M的结果按科学区分度、强基线和增量成本比较；无需让T/N再跑一轮相同文献资格，也无需等待M结果才承认本轮Discovery完成。

真正进入109时，应另给一个完整、有限预算的连续合同：先同版本资产/环境和功能canary，通过即进入小矩阵；普通工程问题同Goal解决；不改现有driver、不读写Lane M的目录、只在其结束并释放原GPU锁后申请。**本轮未发该Goal、未批准下载/安装/运行，M优先级与原合同不变。**

已知而尚未解决的事项：cuVS主线快照与实际发行版对应；本机运行资格；真实数据完整SHA和峰值存储；现成三条诊断路径是否在同一质量范围内可用；实际时间、重算、资源响应；相对Jasper/IVF-RaBitQ的增量。它们是未来实验应回答的内容，不是当前已经通过的门。
