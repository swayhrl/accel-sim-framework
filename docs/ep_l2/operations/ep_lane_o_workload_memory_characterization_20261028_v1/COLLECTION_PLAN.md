# Lane O 最小新增采集与实验计划

状态：供用户审查的设计，不是启动规格。正式采集由 EP-MAIN 统一登记和调度。Lane O 本阶段不启动完整 GPU 仿真、不构建或修改生产 Core、不接管 Main。

V1R2已落实独立审查修订。[MEASUREMENT_CONTRACT.md](MEASUREMENT_CONTRACT.md)是边界、人口和分布的规范合同；[NI_MATRIX.md](NI_MATRIX.md)规定各路径资格；[PILOT_GAPS.json](PILOT_GAPS.json)记录四个候选输入的既有证据及缺口。旧审查报告保留，不修改冻结实验数据。

## 先复用再补采

1. 固定小型状态投影与验收索引，按精确输入、Source、ELF、配置和 observer 分层。复用已验收 bundle 中的 FT、RO、TVD、STRUCT、B0/MS 汇总；对相同文件只解析一次，建立指标缓存。读不到的归档先请求 Main 提供小投影，不为补一个字段恢复整个大包。
2. 复用已接受的事件时间线、Reserved/LIFE 分布、历史 W/V 和 M0b 统计。历史 Motivation 已有10-workload stack-distance及post-eviction统计，先找回现有小CSV/manifest/后续closeout；Streaming prefinal有32B sector时间复用，但final promotion和多sector顺序证明须按原状态保留。先解决身份与验收索引，不重跑旧profiler。历史几何、输入、资格和运行模式分别保留，不与当前全负载混算。有限事件快照只用于例证。
3. 每个 workload×metric 生成 `OBSERVED / DISABLED / NOT_EMITTED / NOT_APPLICABLE / UNACCEPTED / IDENTITY_UNRESOLVED` 状态。数值零仅在功能开启、覆盖分母有效且记录完整时使用。
4. 先补解析器能够恢复的字段，再评审下面的轻量 observer 候选。没有新增指标需求的输入不安排补跑。

已发现 mandatory `model.mechanism_metrics.bottleneck` 保留 `distinct_requests_first_block`、`blocked_observations_over_slices`、65 桶等待分布、wait sum/max、resolved/unresolved 等字段；这与 optional lifetime/pressure observer 关闭不矛盾。每原因等待是 first-block→首次known-clear（仍阻塞到准入时才在准入关闭）；只有ANY项是 first-block→admission。先复用它们。下面“公共去重与等待”只补连续/反复阻塞、Tag专属阶段和全requester首见；不重复实现已有口径。

## 统一统计人口

明确区分`ingress_child`（真实push/sector拆分后、ROP之前）、`queue_enter`（进入ICNT→L2 FIFO）、`first_head`（首次成为可检查队头）及`admission`。现有MS/LIFE只支持其原head或准入人口，不能重新命名为入口到达。首批复用记录使用`head_*`字段；未在真实入口采集时，`ingress_gap`与入口定义的fill前重访均为NOT_COLLECTED。新代码若要回答入口重访，必须在入口hook对请求记录一次，不能扫描FIFO或用first-head时间倒填。

各边界分别按子请求UID及其生命周期去重；同UID重试不增加到达数。普通requester、独立line transaction、sector lower request、WB transaction、payload operation分别计数。父子闭合保留`(parent UID, child UID, line, sector mask)`；一个父请求拆成多个sector不得当作多个不同程序指令。

地址按已资格化模型的 canonical VA 与 128B line 对齐；保留 32B sector mask、读/写/atomic 类型。合并命中也算新的 requester，不能算新的独立地址。WB 不计入 demand-request 分母。memcpy 预热和初始化属于明确的输入/配置身份，不能混入 kernel demand 次数。

V必须同时区分128B line重复、同line首次访问新sector的空间延续、相同32B sector的真正时间重访。不能因Vector的line重复率高就称其时间复用强。多sector请求按prestate批量分类；distinct recency若采用单请求内顺序，必须证明该定义无歧义或正式数据每请求仅一个sector，不能重复旧prefinal的latent tie风险。

每项计数注明边界、请求类别、去重键以及`seen / eligible / checked / admitted / completed`层。记录首次等待、各原因累计等待、总等待及未完成人口；原因可以重叠，不能求和称独占stall cycles。周期域明确为CORE、L2或DRAM，物理时间不包含memcpy偏移。FT unique_requesters排除L1_WRBK，而MS原因人口未天然排除该类；没有过滤/零例外证明时不将两者计数比称为精确demand受阻率。Conv/Scan本次22份小型JSON未找到absorbed/请求类型投影，故先保留原始计数、不发表该发生率；不为此解压raw。

程序相关的观测为请求类型、认证地址覆盖、在所声明请求序列上的地址重复；cycle 间隔、替换、在飞并发、阻塞和 V/T 命中均受缓存、到达顺序及机制影响。即使在 S 中测量，也称“该输入在参考模型下的行为”，不称硬件无关属性。

## 基线特征与机制结果分别采集（V1R1补充）

| 来源 | 首先测什么 | 什么时候需要额外实验 |
|---|---|---|
| **S参考模式** | 新请求首次到达及地址间隔、读写/原子比例、脏替换/WBUF/WAD、普通MSHR、每Set Tag占用和满路实际拒绝；可在S中被动估计淘汰后再访 | 只有相同完整输入的已有小汇总或历史精确映射不足时，才补一次带轻量观察器的S |
| **F/WV合法模式** | V真实读服务及保留年龄、RO候选/事务/合并、同NEW∧目标Set满路∧旧RO结构可释放、detach与实际完成 | 优先复用当前接受的F/WV端点；缺少真正必要的联合条件时，再由Main安排有限F补采 |
| **同Source开关对照** | 观察器OFF/ON是否改变性能与协议，及未来必要的F−T/F或W/WV控制 | 不是全程序都要重新跑每一种模式；必须先有数据缺口或独立收益问题 |

尤其不可将S的Tag满路与不同配置F的RO统计相乘，推导“有T机会”；也不可把F的实际Victim命中直接当成S参考模型下固有的复用率。四个机制共用同一批低成本统计代码，但**S和F的数据人口分开记录**。

## 一个默认关闭的轻量采集包

| 模块 | 记录与计算 | 输出分布 | 增量成本与边界 |
|---|---|---|---|
| 公共去重与等待 | 复用MS head first-block；ingress、queue、head、admission各自一次计数；累计阻塞另设live状态 | 每原因first-block→首次known-clear与ANY→admission分开导出65桶；同人口分母未证明则只报计数 | 仅现存live对象；无全应用UID集、无FIFO扫描；入口未观测不得由head回填 |
| W 生命周期 | dirty victim 选择/提交、WAD 插入、copy enqueue/grant、lower accept、true set_done 时间；既有 WB 对象附时间戳 | 分段 WB 时间、WAD/WBUF 占用的时间面积与 full ticks；同址 R/W/A 首见与等待 | 复用现有 map/对象；不额外扫描 Tag/WAD，不触发额外 cache probe |
| V 地址重复 | request-index 与 cycle 间隔；post-eviction 首次再访问；读写类型、dirty/WB 阶段 | log2 间隔；有限距离档；retention CDF、未再见/失配/删失分开 | 最多每 slice 1024 个带标签的历史项，确定性地址采样；固定 hash/seed；表替换必须计为删失，不能当无复用 |
| V 有限 shadow | 最多 128 个 victim 地址/slice，分别跟踪 clean、dirty、WB 完成；只在已有 eviction/touch/WB/reclaim hook 更新 | metadata 容量 8/32/128 的可命中率，按相同准入规则分层；可用 payload 与目录必须联合满足 | 在一个固定有界结构中共享时间戳/位置；可选，不同时启用大量 shadow policy；不改变实际 victim 选择 |
| M 到达与在飞 | ingress/head各自独立requester的certificate判定及fill/retire前重入；normal/RO事务另计地址并集 | 比率需同边界/同类分母；head gap与ingress gap分开；ready前、ready-only drain分开 | 入口未采集则该人口NOT_COLLECTED；使用sector ready精确条件，不把live merge当fill前重访；地址并集不加峰 |
| T 联合机会 | 每 set 的 RESERVED 与 live attached RO 数在状态变化处更新；NEW 首见时记录目标 set R、RO eligibility、reuse/sector/pin 条件 | occupancy 时间直方图；NEW-at-R；NEW∧all-reserved∧eligible；unique Tag-block 与等待；实际 relieve/detach/commit | 每 set 常数状态，按 `Δtick×旧状态` 结算时间面积；只读已有预检结果，不增加 Tag probe/完整扫描 |
| Bank 等待 | 将既有 logical operation 首次创建至 grant 的等待按 hit/fill/WB-copy/WB-read/TVD/RO 分组 | ops、attempts、grants、冲突 op、wait 分布；per-bank 不平衡 | 不把 grant 乘128B冒充实际带宽；不把各 bank 的峰值相加称同时峰 |

### 分布与缺失处理

- 时间和访问序号间隔采用 `0, 1, 2–3, 4–7, …` 的固定 log2 桶；输出 count、sum、max 与 overflow。由桶恢复的 p50/p95 是区间，不能报告为精确分位数。
- “访问间隔”是中间 requester 数或序号差；“复用距离”是两次访问间不同 line 的数量。两者字段不得混名。必要时有界128项LRU栈只提供distance<128的短距离分布；超界/未追踪为 `OUT_OF_WINDOW`，不声称全范围精确stack distance。必须对完整声明地址流更新栈；采样子流栈距离不能冒充全流距离。全局精确reuse distance不属于最小采集。
- 所有地址历史表记录采样分母、碰撞、替换、首次未匹配与结束删失。确定性采样是容量受限估计，不能将有偏 surviving 项直接外推为全 workload 比例。
- WB、pending RO 或 victim 在应用结束仍存活时进入 censored 桶。跨 kernel 事务保留 origin epoch；不在未 drain 的边界清空状态或将物理阶段当作 requester kernel 因果归属。
- 时间占用与 NEW 到达分布分别输出，禁止相乘得到联合机会。联合机会在同一请求、目标 set、同一时刻直接计数。

### 内存与输出预算草案

默认以所有 64 slices 为人口，固定全应用聚合直方图；不产生逐请求日志或 per-set×per-kernel×per-window 全笛卡尔积。单个 1024 项/slice、48B/项的地址历史表约 3MiB；128 项/slice、40B/项的 victim shadow 约 0.313MiB。实际结构 padding、live 元数据和统计数组须由 `sizeof` 与配置上限实测，不能把估算称 RSS。

候选目标为 observer 自有常驻状态 ≤16MiB、全应用新增 compact 输出 ≤8MiB；均需按最长 commandlist 和真实序列化字节预检，不继承旧格式的经验上限。不能为满足上限截断人口；若输出预测超限，应合并直方图层次或保持未启动。完整 per-kernel 表不是第一轮硬要求，先保留 kernel 数和请求人口边界；只有已观测到有意义阶段差异时才增加有限分组。上面成本是待验证设计预算，不是已实现性能承诺。

## 覆盖与最小实验矩阵

覆盖母表沿用 authoritative42：35 个冻结代表输入与 7 个身份未解程序全部保留。96 个 ordinary 内容组是扩展层，25 个 fraction/trim 与 SM89 另列，不能替换原代表输入。Vector4M 为已有辅助控制，不代替主 Vector6M；历史 tiny Gaussian 不代替 GaussianN64；CFD 5-kernel 诊断不等于完整 timestep。

| 阶段 | 工作 | 新完整仿真上限 | 停止条件 |
|---|---|---:|---|
| A 本轮 | 小汇总复用、身份/状态矩阵、缺口清单 | 0 | 本报告交用户审查 |
| B 后续独立工程 | Main确定冻结基点后，仅在独立候选分支准备；先闭合边界、CPU控制与尺寸/序列化，不并生产 | 本轮0；没有工程或模型启动记录 | 按NI_MATRIX逐路径提供新Source/ELF及证据；S证明不自动覆盖F/WV |
| C Main批准后pilot | Scan、Conv、FWT、Vector6M四个候选；按PILOT_GAPS逐格先复用，有必要才选本批S或合法F/WV观测。FWT现有合法端是WV，不能替成未资格化RO-F | 本轮0授权。先算`N_ON + N_missing_OFF`；原“4 ON+1 OFF足够”的固定假定撤销；不得据此自动增加启动 | 先提交精确输入/模式/开关/新ELF/路径NI/预算清单。若暂定上限不足，缩小范围或另报精确控制。host≤5%为待测目标，非全workload保证 |
| D Main 批准后代表覆盖 | 35个已冻结代表输入优先补齐**S参考行为**；自然运行时附带轻量采集，按已得数据去重。F/WV机制结果由现有接受点和必要有限新F采集另列，不用S代替 | S侧≤35个ON（含pilot复用），实际仅为确实缺基线指标的合格输入数；F侧另按缺口与独立资格审查，不预先整批登记 | 所有可用输入有值或明确HOLD/NA；不得为了填满35而重复启动 |
| E 机制验证候选 | 只在实测机会成立的少量输入上安排 WV 或合格 F 对照；T 用同背景 F−T/F | 本阶段不分配 | 用户审查机会之后另定精确点；不做全 workload×W/V/M/T 笛卡尔积 |

若候选的身份或资格不成立，保留HOLD；如Main选择替代，必须重新列精确身份和所覆盖问题。FWT输出风险先用compact新格式界定。NI须使用同新ELF的OFF/ON，旧ELF不能直接充当OFF；若本批仅采S，则F/WV新增hook保持UNQUALIFIED，不能从S配对继承。

RO 在 S 上的首次认证检查仅复用已存在且精确绑定的证书；载入/判定必须证明不改时序。不合格/未认证不补零，也不为本轮重复扫描 Trace 获取新 RO 证书。Main 已在进行的资格工作按其现有结果增量接入。

每个有效代表输入首轮至多按缺口安排一份 S 参考行为采集，已有完整证据则不再启动。V的实际读取、RO准入与Tag释放属于F/WV机制运行结果，应优先复用既有F数据，只有联合机会不足时才安排必要的F观测。V的独立净收益和RO bypass/detach效果仍需后续合法匹配控制；本阶段不能提前宣称。参数搜索、延长 DRAM 延迟、刻意缩 Tag 制造现象、全程序精细根因分解均不属于 Lane O 最小计划。

## 通过条件与交接

设计审核至少覆盖同 UID 重试、同址多个 requester、sector 分裂、同址多 detached RO、clean/dirty eviction、写回 set_done、backpressure、tag reuse/generation、跨 kernel 与尾部删失、容量与序列化上限。计数满足 `first_seen = admitted + terminal_unadmitted` 等明确的闭合关系，分母与 coverage 状态必须一起输出。有限采样不能用同样的等式冒充全人口。

由 Main 决定 Source 基点、native 资格、精确预算和调度时机；Lane O 交付指标与解析合同，Main 返回同一 schema 的小汇总。既有 controller、运行中 Core、冻结配置、正式账本和实验费用保持其原状态。本计划无新启动授权。
