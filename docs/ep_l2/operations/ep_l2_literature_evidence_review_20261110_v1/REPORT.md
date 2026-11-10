# EP-L2 文献与既有证据复核（2026-11-10）

**用途：**供 EP-L2-8 决定五点验收后的分析顺序与下一轮是否值得申请实验。本文是研究判断材料，不是五点正式验收或论文正文。远端现场状态只读采样时间为 **2026-11-10 14:46 UTC**。

## 1. 阅读范围、证据等级与版本

我先核对了 174-new 项目交接 review 与 `research/` 原件，再以 DOI/OpenAlex 元数据和可取得的作者公开 PDF 核对公开论文。远端 `REFERENCE` 命名文件多为实验参考数据、代码或复制工作树；未发现已成形的 EP-L2「相关工作」综述。历史 EN-v22 母稿、EN-v23/v24 候选的实际 TeX/PDF 尚未交付，故**没有审读或改写现存论文正文**。`PAPER_ARCHIVE_STATUS.md` 只保存已有图、表源、脚本和索引；`ORIGINAL_TRANSFER_STATUS.md` 仍为等待原件。归档检索有明确边界，不等于全局证明文件不存在。

以下项目资料按内容与权威层级阅读，重复 worktree 只取一份；早期路线图是历史设计，之后的 `project_spec`、已接受结果和最新五点申请覆盖其变化了的参数或计划。完整远端源根为 `/root/data/ep_l2_full_workload_performance_20261027_v1/`。主要 Git 原件均可在 `swayhrl/accel-sim-framework@9980581f84390400a197726672ae8d594386ec25` 的 `docs/ep_l2/` 中查到；下表 SHA256 为远端原件前 16 位，仅用于快速辨认，不代替完整归档 SHA。

| 已读资料组 | 具体原件及 SHA256 前缀 | 对本轮判断的作用 |
|---|---|---|
| 历史完整设计 | `ELASTIC_PAYLOAD_L2_ARCHITECTURE_AND_ROADMAP.md` `9f593e7753e0ea56` | Tag、Payload、descriptor、WAD/TVD 生命周期；银行与端口、公平基线、机会分析、成本与风险。旧方案并非当前五点实际硬件。 |
| 现行研究规范 | `project_spec/{RESEARCH_CHARTER,ARCHITECTURE_BLUEPRINT,EVIDENCE_AND_CLAIM_MODEL,EXPERIMENT_ROADMAP,MECHANISM_SEQUENCE_CURRENT}.md`；各件前缀依次 `b7603fbb05587a37`、`2371513637003488`、`768f60e06b97bf86`、`75f174c30ba23276`、`7e45cf38c0dad4d6` | 明确结构阻塞、服务效果、应用 cycles 分层；物理预算、正确性、消融和停止条件。另读 `project_spec/decisions/ADR-006`、`ADR-008`。 |
| 动机与机制准备 | `project_spec/{MOTIVATION_FIGURES_PLAN,PERFORMANCE_HEADROOM_PLAN,WORKLOAD_CHARACTERIZATION_SCHEMA,MECHANISM_IMPLEMENTATION_PLAN,WORKLOAD_ARCHETYPES_PRELIMINARY}.md`；前四件前缀 `b9916832b612e8a2`、`e71418ef9d39e45b`、`cae6af5a299cda8d`、`c4f1dd3eba4f781b` | 复用距离的分母、sector 与 line 区别、真实/影子阻塞、下游 headroom 交互、工作负载选择。Archetypes 是初步图谱，须服从更新的正式结果。 |
| 旧动机复核 | `chatgpt_handoff/{MOTIVATION_DISCUSSION_REFERENCE,MOTIVATION_FINAL_CHATGPT_REVIEW,STREAMING_REUSE_EXTENSION_HANDOFF}.md`；前缀 `f320514ff237281e`、`b1c9ddff39df946c`、`e83f06dcd15f19f7` | 旧 10 负载短复用、真实淘汰后重访、32B sector 的空间继续与时间重访不能混同。WBUF=4/8/16 是 shadow 压力，不是应用性能。 |
| 已完成的性能与归因 | `research/mechanism_attribution_20261103_v1/main/{PAPER_OBSERVATIONS_AND_CLAIM_BOUNDARY,FINAL_MECHANISM_ATTRIBUTION_REPORT}.md`，前缀 `a9102e3d9c82b1af`、`6380bb45bc6fab35`；V4 `FINAL_RESULT_SUMMARY.md` `4aa313b39fa74fdf`；V5 `V5_FINAL_REPORT_ARCHIVED_V1.md`；UMT1 `README.md` 与 `WORKLOAD_SELECTION_AND_PRIORITY.md` | 仅取已接受的同源对比及负结果；保留 Source、输入、时钟、Tag 几何和实际选项。归因报告不是未提供手稿的审稿证明。 |
| 当前申请与论文归档状态 | `research/next_cost_aware_architecture_20261107_v1/main/EP_L2_NEXT_COST_AWARE_ARCHITECTURE_AND_EXACT_EXPERIMENT_REQUEST.md` `f4caf4fa13bc7c70`；`research/performance_first_20261103_v1/paper_archive/{PAPER_ARCHIVE_STATUS,ORIGINAL_TRANSFER_STATUS,BOUNDED_SEARCH_RECEIPT}.md/.json` | 五点的实际 Source/成本/对照定义及手稿未到位边界。 |

**阅读口径：**上表是对科学设计、论文准备与结果解释有直接作用的去重核心原件，非宣称逐字读完远端所有代码、Trace、raw、历史 handoff 和复制目录。文献表中「摘要」表示 DOI、题名、年份和摘要已核对；只有 Zhao 等 ISCA'19 的作者公开 13 页 PDF 已直接查阅正文。ACM/Springer 的部分 PDF 链接受访问限制。OpenAlex 将 `arxiv:1810.07269` 错配为 *Accel-Sim* 的开放 PDF；打开后实际为另一篇文章，因此本文只用 *Accel-Sim* 的 DOI/摘要，不把该 PDF 当原论文。

## 2. 我们已有的可靠实验事实

本节的数字来自对应已接受批次，**不跨 Source、ELF、输入、时钟或配置拼接匹配基线**。cycles 越小越好；百分比以该行明确的对照为分母。

| 证据 | 已接受同源观察 | 对后续判断的约束 |
|---|---|
| Stencil，Source78，Tag 几何 | G32×8：S `5,242,939`、WV `4,768,893`，WV/S 减少 `9.0416%`；G64×8：S `4,299,729`、WV `4,282,418`，WV/S 减少 `0.4026%`。 | 几何扩展本身带来很大变化，Victim 的同背景增量随之缩小。不能把 S 几何改善算为 Victim 收益，也不能以旧 Source78 的 S 代替新 EXT0。 |
| Source78 W→WV 包效果 | GEMM `558,957→550,642`；FWT `181,635→178,951`；Stencil G32×8 `5,240,684→4,768,893`。 | W→WV 识别的是 retention、lookup、allocation、service 的整体包效果；不是单次 Victim 命中的纯收益。旧 Source 的量级不能直接预报新 Source。 |
| Victim 实际服务 | Source78 G32×8 的 Stencil 约 `4.93M` retained-sector responses、G64×8 为 `2,547`；GEMM G32×8 `609,858`，G64×8 为零。 | 是已保留 sector 再服务的证据。response 数不等于避免的 DRAM 请求数、节省周期数或更优的净收益。 |
| V5 冷查询与压力 RO | FWT cold filter ON 对 OFF `178,951→180,074`，**慢 `0.6275%`**；Conv/Scan 的 pressure-aware RO 改善约 `0.3877%/0.5402%`；Vector1700 改善 `18.7751%`，但激活 slice 为 `0/64`。 | 查询减少或局部资源缓解未必进入关键路径。Vector 证据是无压力时避开 RO 服务成本，不证明活跃 RO 加速。 |
| 机制归因 | FWT S→W 清除 copy/WB 空间等待，cycles 仅约 `-0.1056%`；Conv 的 T 实际 detach 增加且相对无 T 的 B 改善，但对 F-minus-T 仍慢约 `0.4609%`。 | 事件数、局部阻塞、服务、端到端性能必须分别陈述；重叠等待不能加和成独占关键路径。 |
| 新结构成本 | Base128 + mandatory/WAD128；EXT 另增 optional CLEAN128 metadata，不增 Data。估算 `58,880` 逻辑位/slice（额外控制/比较器/端口另计）；Base miss 后 Ext 查询再付一周期，选择与清理有明确定时。 | 当前只有逻辑位和模型成本；物理 PPA、时序、能耗和关键路径仍未知。不能称“免费 128 容量”，也不能把 C++ entry 字节数当硅面积。 |

旧动机图还提示：line 级短距离可能只是同一 128B line 内新 32B sector 的空间继续；即使是真实 sector 重访，条件分布也要与 reuse 覆盖率、淘汰后重访和真实 resident/retained 服务一起看。`cfd/FWT/scan` 的旧淘汰后重访只支持候选筛选。旧 `gemm` 图零重访更不能否定新 Source5 上的实际机会。WBUF shadow 是潜在阻塞结构描述，不是新机制 speedup。

## 3. 相关论文矩阵

「层级/证据」同时说明论文实验对象与我本次可核查深度。论文报告的百分比只描述其自身基线、负载与模型，**不用于预测 EP-L2**。

| 论文与固定 DOI | 层级/本轮证据 | 机制与对 EP-L2 的具体启发或边界 |
|---|---|---|
| Jouppi, *Improving direct-mapped cache performance by the addition of a small fully-associative cache and prefetch buffers*, ISCA 1990，[DOI](https://doi.org/10.1145/325164.325162) | CPU L1；摘要 | victim cache 的经典先例：被淘汰 line 进入小型全相联缓存。不能把 GPU L2 retained sector、并发与查询成本说成首次 Victim 思路。 |
| Qureshi 等，*The V-Way Cache: Demand Based Associativity via Global Replacement*, ISCA 2005，[DOI](https://doi.org/10.1109/ISCA.2005.52) | CPU 二级缓存；摘要 | Tag 数多于 Data line，动态 set 关联度、全局替换。最重要的 Tag/Data 解耦先例；我们的比较必须解释固定 Data、optional CLEAN、GPU L2 生命周期和定时成本的不同。 |
| Sanchez 等，*The ZCache: Decoupling Ways and Associativity*, MICRO 2010，[DOI](https://doi.org/10.1109/MICRO.2010.20) | CPU/CMP cache；摘要 | 通过 skew/cuckoo 候选和 miss 后额外查找改善有效关联度；提醒不能把额外 metadata 查询、比较和迁移成本忽略。 |
| Jaleel 等，*High performance cache replacement using re-reference interval prediction*, ISCA 2010，[DOI](https://doi.org/10.1145/1815961.1815971) | CPU LLC；摘要 | RRIP 用短状态预测远期重访、抗 scan/thrashing。若未来做保留策略，应与简单替换/不保留对照；CPU LLC 收益不可直接外推 GPU L2。 |
| Qureshi 等，*A Case for MLP-Aware Cache Replacement*, ISCA 2006，[DOI](https://doi.org/10.1109/ISCA.2006.5) | CPU cache；摘要 | miss 的关键性受并发 MLP 影响。支撑本项目把 avoided miss、服务、cycles 分开，而非以命中数选策略。 |
| Li 等，*Tag-Split Cache for Efficient GPGPU Cache Utilization*, ICS 2016，[DOI](https://doi.org/10.1145/2925426.2926253) | GPU cache；摘要 | 将 Tag 拆分以支持细粒度数据存储，并保持请求数；摘要报告平均性能 `17.2%`。是 GPU Tag/存储分离的直接对照，但其核心是空间粒度和请求数，并非本项目的 L2 optional CLEAN retained 生命周期。 |
| Li 等，*An Efficient GPU Cache Architecture for Applications with Irregular Memory Access Patterns*（Elastic-Cache）, 2019，[DOI](https://doi.org/10.1145/3322127) | GPU L1；摘要 | 借未用 shared memory 放辅助 Tag，按 32/64B 细粒度组织 128B line。说明利用旁路/闲置存储扩展 GPU cache metadata 已有先例；它与本项目 GPU L2 固定 Data 的问题不同。 |
| Gu 与 Chen，*Dynamically linked MSHRs for adaptive miss handling in GPUs*, 2019，[DOI](https://doi.org/10.1145/3330345.3330390) | GPU L1/L2 miss handling；摘要 | 把 primary entry 与 secondary slot 动态组成 MSHR；摘要称 reservation fail 减 `88.1%`、IPC 增 `19.2%`、L1/L2 面积附加 `0.6%/0.1%`。EP-L2 的 descriptor/RO pending 贡献不能笼统称为首次动态 miss metadata；要证明不同状态/生命周期和实际收益。 |
| Zhao 等，*Adaptive Memory-Side Last-Level GPU Caching*, ISCA 2019，[DOI](https://doi.org/10.1145/3307650.3322235)，[作者公开 PDF](https://biblio.ugent.be/publication/8625915/file/8625916.pdf) | GPU memory-side LLC/NoC；**13 页正文核查** | 共享 LLC miss 低，private LLC 对跨 SM 共享数据可因复制后的服务带宽更高而胜出；17 个 GPU 负载，论文报告 sharing-intensive 子集平均 `28.1%`。证明“miss 更少”不足以推断性能，需同时看 bank/NoC/服务带宽；不是 EP-L2 数据。 |
| Xie 等，*Coordinated static and dynamic cache bypassing for GPUs*, HPCA 2015，[DOI](https://doi.org/10.1109/HPCA.2015.7056023) | GPU cache 竞争；摘要 | 编译期与线程块动态 bypass 缓解争用。保留不该无条件开启；低复用或高争用输入需负对照。其摘要平均加速不是 EP-L2 预测。 |
| *Locality-Driven Dynamic GPU Cache Bypassing*, ICS 2015，[DOI](https://doi.org/10.1145/2751205.2751237) | GPU L1；摘要 | 用局部性判断低复用数据是否旁路。与 CLEAN 保留策略相邻，但层级和服务对象不同。 |
| *Access Pattern-Aware Cache Management for Improving Data Utilization in GPU*, 2017，[DOI](https://doi.org/10.1145/3140659.3080239) | GPU L1；摘要 | 区分 streaming、同 warp 与跨 warp 复用，再决定 bypass/pin；提醒后续策略先识别真实复用人口，不能只看负载名或总命中率。 |
| *Efficient Cache Performance Modeling in GPUs Using Reuse Distance Analysis*, 2018，[DOI](https://doi.org/10.1145/3291051) | GPU L1 建模；摘要 | 详细 RDA 纳入 reservation fail 与 MSHR，抽象 RDA 误差较高；直接支持 EP-L2 的「reuse 图仅筛选机会，必须用生产时序与资源门验证」原则。 |
| Lal 等，*A Quantitative Study of Locality in GPU Caches for Memory-Divergent Workloads*, 2022，[DOI](https://doi.org/10.1007/s10766-022-00729-2) | GPU L1；摘要 | 多粒度局部性研究；与本项目 128B line、32B sector 口径区别相互印证，但不能代替本项目淘汰后重访和成本计数。 |
| *RBGC: Repurpose the Buffer of Fixed Graphics Pipeline to Enhance GPU Cache*, 2023，[DOI](https://doi.org/10.1145/3583781.3590305) | GPU L1 victim；摘要 | 复用闲置固定图形流水缓冲做 L1 victim，并按 load 可复用性筛选；摘要报告该论文自身基线提升 `39.1%`。GPU victim/保留筛选不是新颖点；我们需要聚焦 L2、固定 Data、optional CLEAN metadata、两段查询与全应用净效果。 |
| Khairy 等，*Accel-Sim: An Extensible Simulation Framework for Validated GPU Modeling*, ISCA 2020，[DOI](https://doi.org/10.1109/ISCA45697.2020.00047) | GPU 模拟方法；DOI/摘要 | 使用 native ISA trace 与验证过的 GPU 模型。EP-L2 的完整 Source/ELF/输入、实际选项和 simulator 校准要披露；模拟结果不能自动声称物理时序/PPA或真实硬件性能。 |

**文献综合判断。**目前足以说明 EP-L2 不应以“首次 victim”“首次 Tag/Data 分离”“首次 GPU 动态 MSHR”作为贡献。较可能成立、但须五点和物理成本进一步支撑的具体贡献，是**在固定 Data 容量和明确端口/查询/选择成本下，针对 GPU L2 的 optional CLEAN 保留状态给出同 Source 全应用净收益及可解释的失败边界**。此表仍不是穷尽性新颖性检索；正式投稿前需获取最接近论文全文、核其硬件细节和实验设置，再收紧贡献措辞。

## 4. 五点结果到达后的判别流程

最新申请固定 `850MHz/L100/G32×8/WV_ZERO_RO`、完整 283 项和同一新 Source/ELF；两族输入分别绑定。EXT0 是新 Source 原 Base128 时序/资源基线；EXT1 是扩展硬件已存在但禁 CLEAN 保留；EXT2 在同扩展硬件上启用 CLEAN。**GEMM 0/1/2 与 Stencil 0/2 的判别力不同。**

| 对照 | 可以回答 | 不能单独回答 | 最小配套证据 |
|---|---|---|---|
| GEMM EXT0→EXT1 | 扩展硬件和两段查询等迁移包的净成本 | 某个单独门/周期的独占成本 | 同 Source 配置差异、query/等待、bank/端口、cycles/人口/排空。 |
| GEMM EXT1→EXT2 | 同扩展硬件下允许 CLEAN 保留的增量效果 | 每次 retained response 的独占收益；跨输入普适性 | Ext/Base 实际占用与淘汰、CLEAN admission/reclaim、sector response、lower-issued 请求类别、负载阶段及 cycles。 |
| GEMM EXT0→EXT2 | 含新增 metadata/时序的总净效果 | “相同硬件下纯策略收益” | 前两段一起解释，同时报告逻辑位、未量化的物理成本。 |
| Stencil EXT0→EXT2 | Stencil 100-kernel/跨 kernel 背景的总净效果 | 不能分解迁移成本与纯保留增量，因为无 EXT1 | 完整 100-kernel 人口、Base/Ext 保留、服务与阶段、额外查询/选择成本、cycles。若净结果模糊，未来才考虑单独申请 Stencil EXT1。 |
| GEMM 与 Stencil | 在各自固定输入上的正负结果及机制差异 | 不能跨 Source 或输入拼成直接加速比；不能由两输入推出普适性 | 各自同族对照、相同指标定义、source/ELF/实际 options/trace SHA。 |

先做五点的正式消费者、完整人口、配置/ELF、守恒、硬件排空、真164 full SHA 与两次独立 Native 恢复，**然后**冻结 cycles 与反事实对照。不得仅根据 DONE `exit0`、日志末尾或局部命中发布性能结论。已知应用程序数值 oracle/NI、物理 PPA/关键路径以及最终 dirty flush 范围的限制继续标注。

若 EXT2 responses 多但 cycles 无改善：先检查 0→1 的查询/选择/清理成本，1→2 的保留增量，bank/NoC/下游压力、请求关键性和阶段覆盖；不以单一“策略失败”概括。若 responses 少且目录/metadata 满，则查 CLEAN 入列、驱逐和可借 Payload 的同步机会；不要从终态空闲推断运行中可用。若 miss/issued bytes 降而 cycles 持平，检查是否只是并行 miss、带宽或下游排队被重新分配。若新五点为负，保留负结果；同成本未量化前不宣称物理上值得扩容。

## 5. 后续工作排序与停止条件

1. **先验收既有五点，不新增模型。**截至 14:46 UTC，五份 `EP_FULL_PERF_NATIVE_DONE_V1` 均已出现，launcher 返回 0、`stop_reason=null`，五个不同 UUID 的压缩 raw SHA 已生成，现场无 `accel-sim.out`。GEMM 三点约 3331/3492/3565 秒，Stencil 两点约 13698/14140 秒。此为运行完成现场记录，**不是正式接受、归档或双恢复**；先按原已授权流程收尾并固定比较。
2. **先做同源效应分解与失败归因。**以 GEMM 0→1、1→2、0→2 和 Stencil 0→2 为四张主表，附绝对 cycles、百分比、真实保留服务、lower-issued 分类、Bank/端口/查询等待、metadata 占用与阶段。任何比例先核分母与重复累计语义。优先检验“保留服务是否抵过真实查询/选择成本”，再谈新策略。
3. **若总净收益实在且机制归因一致，再补成本证据。**对 58,880 逻辑位/slice 之外的比较器、读写端口、扇出、选择器、控制和关键路径做可复现估算；适用时再做 RTL/CACTI/PPA。未取得物理结果前只写 modeled cost，不写 equal-area 或频率闭合。
4. **仅对明确剩余问题提出新申请。**若 Stencil 0→2 结果无法解释硬件成本与保留增量，最有信息量的是同 Source 的 Stencil EXT1；若 GEMM 与 Stencil 都无保留机会或成本已压倒收益，则先停止 optional CLEAN 扩容方向，不扫更多输入寻正例。3MM 或新的 streaming/压力负载只有在已接受五点指出明确可检验机制、人口及预算时再申请；旧已接受资格复用，不重跑历史 Goal。
5. **论文定位。**未来正文应把 GPU L2 服务/状态生命周期与 V-Way、Tag-Split、DL-MSHR、RBGC 并列区分，明确旧论文各自层级与基线。结果表分结构、服务、全应用、成本四层；给失败输入和 Source 边界，不选结果重写假设。手稿原件未到位时只维护本证据综述，不声称已审过 EN-v22/v24。

**本轮下一件具体工作：**按原五点授权完成正式验收与真164归档/双恢复，然后用已冻结的同源数据填上节四张对照表。本文不触发新的科学 Goal、预算、模型、Trace、109 GPU 采集或论文编辑。
