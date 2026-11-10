# DTC-L1 相关论文再调研与实验策略判断

**后续核验更新（2026-11-10）：** 本报告下文关于“尚未读到 v0.23 全文”和 Tag-Split 仅有摘要的描述，是首轮检索时的状态。随后已在本机核验私有 v0.23 母稿 ZIP 和 Tag-Split 12 页 PDF，并完成 Short-Collect R0 fresh 准入核查。最新结论与来源等级见 [补充报告](REPORT.md)；原首轮记录保留以便追溯。

日期：2026-11-10。性质：只读文献研究与冻结证据综合研判；新增模拟、科学 request、预算消费均为 **0**。本报告不是新机制的科学准入或英文论文 v0.23 的修改稿。论文逐条出处和阅读等级见 [SOURCE_INDEX.md](SOURCE_INDEX.md)。

## 一、先读远端：我们已有的基础是什么

我先读了 174-new 的 DTC 历史文档树 `.../dtc_main_v100_sweep_20261025_v1/docs-worktree/docs/dtc_l1/`、现行隔离 Core 的 `DTC_L1_SPEC.md`，以及已发布的 CORE32 Main 审阅包。可直接定位的**外部相关工作笔记只有两份** `RELATED_WORK_BOUNDARY.md`，逐字 SHA 相同，内容聚焦 XOR placement 与 skewed associative cache。它们已经正确承认：XOR 映射和消除冲突并非 DTC 或 AE 首创；AE 是固定的保留 bank 位的 row XOR 控制，不能写成 skewed cache，也未证明同频、面积或 GEMM/Gaussian 收益。[R03–R04]

另有历史 `DISCUSSION_REFERENCE.md`，讨论 BICG/GESUMMV 下游定位：L2 内部 miss queue、L2→DRAM、DRAM admission/return 和 ICNT→L2 ingress 的受测扩容均未给 BICG 带来实质收益；把 DRAM 时钟域理想化从 850 调到 1700 的 E 点有较大响应，BICG 还有 L2 容量敏感性。其正确表述是**已测路径的服务时序/速率敏感，不能说 DRAM 唯一瓶颈，也不能说真实 V100 需要 2× HBM 时钟**。[R02] 历史 FAST12、finite service 的配置和资源口径、论文编辑边界也已读；这些是旧实验/写作依据，不能覆盖后来的固定 CORE32 结论。[R05–R08]

当前冻结科学基准是 `b9ff89f00ea8ff889e4189136501c714c5d7e345` 的 CORE32 Main 包及其接受回执：SM70/V100-derived 64SM 固定 trace，32 输入、同 build 实际 OFF/M/L2/L1 共 128 格，96 组配对。GM `M=1.676758525810`、`L2=1.280648684508`、`L1=1.939911577005`；L2 为 19 正、11 精确零、2 负。`myocyte` L2 慢 2 周期，`srad_v1` 慢 14,652 周期。GESUMMV OFF/M/L2/L1 为 `89,502,220 / 8,699,612 / 21,659,576 / 2,496,495` 周期；3MM、GEMM 的 L2 精确零而 M/L1 有响应。[R09] 这些是**受控 data-availability 反事实**，不是现有有限结构收益、严格数学上界或硬件等面积结论。

旧真实结构响应则属于不同 Core/binary/配置身份：GESUMMV DH-P0/F128/F256 为 `89,502,220 / 86,464,623 / 90,151,547` 周期，vectorAdd 为 `217,305 / 213,053 / 236,217`；扩大 F 容量出现回退。1024 Tag / physical640 曾触发合法 `NO_FREE_LINE` 安全 HOLD。[R09–R10] 后续 Short-Collect-First Core `9a0de9b9f97144f481b3e3637e329ebab01acb74` 只获 17/17 CPU 资格，Native R0 为 `HOLD_NO_SCIENCE`，**没有**新科学 request、模型格、自然应用曝光或性能结果；其证据见本机 `CONTEXT.md` 和固定包 `281ca00af3ccaf24d4073231e7559bd993c02738`。因此不能把它写成“新机制已经验证”。

原英文 LaTeX v0.23 的可靠可编辑路径仍未由交接确认；远端这些目录可定位的是历史讨论、审阅包和 M0 规格，**本次没有读到 v0.23 全文**。109 的 DTC 文档中检到的是上述讨论和 FAST64 分析的副本；其大量 `literature_notes` 属于 AWMA/AI-ARCH 等其他项目，不并入本报告。164 的 `paper_suite` / `paper42` 是实验集或结果审阅命名，不视作外部论文综述。这个检索边界也意味着本报告不声称已覆盖原稿所有参考文献。

## 二、外部论文：按机制而非标题相似度比较

检索使用 Crossref 核 DOI、出版年和作者，OpenAlex 取摘要及开放链接，并检查可取得 PDF 的**实际首页标题**。对 ATA-Cache、CIAO、2018 年 Volta 内存系统建模、Huerta 等人的 Accel-Sim 建模审查，读取了可取得 PDF 的摘要、方法/结果/讨论/结论相关段落；没有声称逐页通读其全部正文。其余以下结论限定为论文摘要、出版元数据或远端先前核对的作者原文。Springer 的 Lal 等 PDF 链接返回 HTML，不能算全文已读。各论文自己的平均收益使用不同 GPU、负载、基线与资源，**不可与我们的 CORE32 GM 相减或排位**。

### 2.1 Tag、数据和粒度

| 文献 | 核心做法与可比处 | 对 DTC 的真正提醒 |
|---|---|
| [P03] Tag-Split Cache (ICS 2016) | 分拆 tag，允许细粒度数据存储而保持请求数，摘要报告该作者基线的平均改善。 | 它直接挑战“细粒度且不增请求”这一设计空间。DTC 若只声称空间利用更好，创新区分不够；应展示逻辑 Tag→physical 重命名、pending merge、PIB/Ref 生命周期与有限完成。 |
| [P04] Elastic-Cache (TACO 2019) | 将不连续的 32/64B 数据放入 128B 行，借未用 shared memory 保存辅助 tag；Elastic-Plus 并行 32B 请求。 | 需对照 32B sector 的**真实**过取、请求放大及 shared memory 使用，而非仅比较命中率。它占用的 shared 资源与 DTC 独立 physical/metadata 资源不同。 |
| [P05] Lal 等 (IJPP 2022) | 摘要量化 divergent workload 的 L1 inter-warp locality、过取和 sector 取数后的 lost spatial locality。 | 32B sector 少取字节也可能多发请求，须同时报告 line、sector、request、DRAM atom 四口径及后续再取。其“约 50%”是其样本观察，不是我们 CORE32 事实。 |
| [P06] ATA-Cache (TCAD 2024；2023 预印本) | 聚合多 GPU core 的 tag 以利用**跨 core**副本并抑制共享 L1 竞争。 | 与本项目单 SM 内 logical Tag/physical 生命周期层级不同，名称相似不等于机制相同。其预印本与期刊摘要的平均数不一致，故本报告不转引该数字。 |
| [P17–P18] Decoupled Fused Cache、Partial Tag–Data Decoupled LLC | 分别是 DRAM cache/CPU LLC 的 tag 路径重构或延迟 data 分配。 | 只作广义 tag/data 分离先例，不可当作 GPU L1 DTC 的直接强基线或同一权利要求。 |
| [P01–P02] González 等、Seznec | XOR placement 和 skewed associativity 的经典先例。 | AE row XOR 不具新颖性；DTC Tag 冲突实验需要相同 bank/way/容量、hash 逻辑成本与对照，且不能借 Oracle L1 强响应归因 hash。 |

### 2.2 Cache 准入、旁路与并发控制

| 文献 | 其证据范围 | 对我们的实验设计 |
|---|---|---|
| [P07–P08] Li 等两篇 GPU bypass (2015) | 以低重用/运行 footprint 决定旁路度，后一篇摘要说明跨七平台、16 应用。 | DTC 放大并发时，低重用请求可能挤占 Tag、physical 和下游服务。旁路是强竞争思路，但旧论文不能证明 DTC 适用；若未来比较，必须同输入、同 build、相同可缓存语义及显式资源代价。 |
| [P09] APCM (ISCA 2017) | 对**静态 load 指令**识别 streaming、warp 内/间重用，按类 bypass 或 pin。 | 我们的逐应用 GM 掩盖 load 类型与 kernel 混合。若想解释 GESUMMV、3MM 等，先按 load/sector 的可复用证据分层；不能用总命中率替代。 |
| [P10] APRES (ISCA 2016) | 根据 load 局部性分组调度 warp，并让请求合并到 MSHR 或预取行。 | 其收益来自 warp 调度与预取共同改变；不能把它当成 Short-Collect-First 的同机制复现。可借鉴“候选必须有实际合并/顺序改变的曝光计数”。 |
| [P11] CIAO (IPDPS 2018) | 全文显示：隔离严重 cache 干扰的 warp 至未用 shared memory，必要时再限流；论文强调只按潜在局部性调度可能增加干扰。 | DTC 的更多 MLP 不必然更快。应保留物理 F256、L2 回退和同 build ON 退化作反证；限流/重定向会动用资源，不能当免费后处理。 |

### 2.3 下游服务、短优先、公平性

[P12] CLAMS 依据每个 core 的 latency tolerance，在关键请求优先与局部性优先之间切换。[P13] FR-RR-FCFS 是**多应用并发**公平性调度，在保留 first-ready/FR-FCFS 特性的同时按应用轮转。它们说明请求优先级与公平性是已有研究领域；我们的“有界短收集优先”只有在作用点、有限窗口、age 上限、eligible 选择条件、完整完成语义和真实 workload 曝光上证明确切差异，才可能形成新的贡献。它不能只靠一个正速度比称为“解决下游瓶颈”。[P12–P13]

历史 DTC 下游讨论 [R02] 与这些论文并不矛盾：扩容队列无效并不排除**服务顺序、行命中局部性或最慢依赖**的影响；理想化 DRAM 时域大响应也不说明某个局部调度能兑现它。合理的判别次序是先量出机制在真实自然 trace 中是否触发，再核更改了哪一条请求的等待/完成，最后才分析周期变化。若 `eligible_choice_different=0`，即使应用有 Oracle 大响应，该候选也没有实证作用点。

### 2.4 模拟器与外推

[P14] Accel-Sim (ISCA 2020) 强调 native ISA trace、性能模型和逐计数器对真实 GPU 的验证。[P15] 其 2018 年 Volta 内存系统建模前作全文指出：sector/tag hit 的 profiler 定义与下游实际取数可不同，模型细节会改变 L1 bypass 与 DRAM scheduler 的相对结论。这个论点直接支持我们坚持区分 Tag 命中、32B sector fill、request、DRAM atom 和完成路径，也支持对 capture/ELF 与 native 数值限定声明。[P16] Huerta 等预印本全文显示 Accel-Sim 的前端、result bus 和 memory pipeline 细节变化能改变个别应用结果，进一步要求保留配置/binary pin、逐 kernel 分布与反例。**这些外部论文是方法论支持，不认证我们的特定模拟器或数据。**

一次来源校验尤其值得保留：OpenAlex 曾把 `arxiv:1810.07269` 列为 [P14] 的开放 PDF，实际 PDF 首页是 [P15] *Exploring Modern GPU Memory System Design Challenges through Accurate Modeling*；不能说已经读了 [P14] 全文。另一个 2024 arXiv PDF [P16] 内印的 DOI 与 Crossref 返回的另一标题冲突，本报告只用其 arXiv 身份，不引用那条冲突 DOI。上述问题及 PDF SHA 见来源索引。

## 三、结合自己的数据：可说什么、不能说什么

| 我们的冻结观察 | 文献提供的机制线索 | 目前仍只是待证假设 / 反证 |
|---|---|---|
| GESUMMV Oracle M/L2/L1 响应巨大，历史 F128 小正而 F256 负；vectorAdd F128 正而 F256 负。 | [P09–P12] 表明请求类别、竞争和优先级可左右并发收益。 | “更多 entry 或更短项先行必能变快”已被本项目负例削弱。Short-Collect 的自然 `eligible_choice_different`、完成因果及性能均 UNKNOWN，Native R0 仍 HOLD。 |
| 3MM/GEMM L2 精确零，M/L1 有响应。 | [P03–P05] 提醒细粒度、Tag/data、请求数可能互相作用；[P15] 提醒 sector/tag 口径不同。 | 不能推出它们“只受 L1 限制”或“L2 不重要”。需按来源阶段、每 kernel、sector 请求和完成等待分解，且缺失计数不填零。 |
| myocyte L2 慢 2 周期、srad_v1 慢 14,652；srad_v1 502 kernel 中 274 慢。 | [P11,P16] 强调并发/模型改变有负作用和分布差异。 | 精确小回退保留为反证，不因 GM 或显示位数抹去；不从汇总周期直接推微结构原因。 |
| 旧 BICG 队列扩容近中性，理想化 DRAM 时域敏感。 | [P12–P13,P15] 的调度/服务研究给出多个不同可检验方向。 | 不能据此直接选择 DRAM 频率、扩大队列或声称唯一瓶颈；需分清排队时间、服务时间、row locality 与公平性。 |
| 1024 Tag/physical640 的 `NO_FREE_LINE` HOLD。 | [P01–P06] 的 Tag/数据分离设计均有资源与映射成本。 | 更大逻辑 Tag 不是单调收益；若无 Ref/old generation/回收前进性证明，任何性能探索先 STOP。 |

## 四、下一轮实验分析的建议顺序（建议，不是授权）

1. **先恢复可审的自然路径，再谈性能。** Short-Collect 候选目前 CPU 资格已过、Native R0 未过且科学格为 0。若未来用户另授权，先让 request、唯一 dispatcher/lease、真实 PID/loader、guard、strict、true164 SOURCE_KEEP、typed restore 与独立审查闭合；Native 资源准入要 fresh 判断。任何一步失败就按合同 HOLD，不拿 fixture 当应用结果。
2. **把“机制曝光”定为首个可证伪读数。** 固定 GESUMMV 与 vectorAdd 的同一新 binary 下实际 OFF/ON；预先定义 eligible 次数、`eligible_choice_different`、优先项/被延项年龄、有限 quota/credit、sector parent/generation/Ref、完整 WB/retire、P50/P95/P99 等待和每 kernel 周期。若 GESUMMV ON 仍 `eligible_choice_different=0`，候选缺乏该输入的自然机制曝光；不得靠扩大窗口或重新挑输入事后补救。
3. **将自然负例写进主分析。** 若以后合法进入预冻结发现集，保留 3MM/GEMM 的 L2 精确零、myocyte/srad_v1 的 L2 回退、vectorAdd 的历史 F256 回退和所有新 ON 的零/慢/失败。每个新输入都须同 build 实际 OFF；旧 Oracle OFF、DH-P0 和旧 UUID 不可代入。逐 kernel 与应用合计同时呈现，按实际接受交集算 GM。
4. **避免继续把“压力计数大”直接翻译为容量方案。** 对 BICG/GESUMMV，按 queue occupancy/满事件、到达速率、真实服务速率、row/locality、ready→collect→WB 时间与最慢依赖分开统计，并做守恒核查。已有队列扩容近中性和理想化 DRAM 敏感性可以生成假设，不能替代新候选的因果证据。
5. **把公平与成本作为独立门槛。** 若短优先改变选择，记录被延请求的最大等待和无饥饿进展；若比较 AE/Tag/physical 新方案，匹配容量、ways、bank、Tag/key 宽度与端口，列出额外比较器、状态、路径延迟、面积/频率/PPA。现有数据不能支持等面积、同频或可兑现 Oracle 倍数。未来 CH 强基线与原生数值/capture 绑定也需各自资格。

优先科学问题由此收敛为：**在正常有限 DTC 路径中，是否真的存在足够频繁、可安全重排、且影响完整应用关键完成时间的短收集机会？** 这是一个可被零曝光、无性能改善、回退、公平性违反或资源成本击败的问题；文献支持把它问清，并未预先给出肯定答案。

## 五、可供后续写作的边界

文献定位可写为：DTC 关注单 SM 内逻辑 Tag 与 physical 数据资源解耦、pending line 合并、Ref/PIB 生命周期和有限完成；Tag-Split/Elastic-Cache 着重数据粒度与空间利用，ATA 着重跨 SM tag 聚合，APCM/APRES/CIAO 着重准入与 warp 调度，CLAMS/FR-RR-FCFS 着重下游请求顺序或公平。XOR placement 和 skewed associativity 是明确先例。这个定位目前是**研究笔记**；正式论文新颖性与逐句引用须在拿到 v0.23 可靠母稿、核对各论文全文/版本以及硬件成本后另审。英文 v0.23 本轮保持冻结。

本轮没有修改远端工作树、registry、HOLD 或实验身份；只更新本机研究资料与 `CONTEXT.md`。下一项科学执行仍等待用户明确任务。
