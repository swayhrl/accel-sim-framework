# EP-L2：性能潜力、瓶颈与结构效用的并行实验合同

版本：2026-10-17 v1。用户已明确授权在投稿前充分并行开展 L2、上下游和理想性能实验；本文件把该指令落实为可执行任务。发布合同不等于远端 Goal 已启动，也不代表表内实验已经完成。

## 1. 本轮目标与优先级变更

必须用完整应用实测分别回答：

1. 原始 SM 和指令流在数据访存不产生资源等待、服务采用最小正延迟时，具有多大性能余量？
2. L2 数据配额、metadata、bank 服务、WAD、上游供给和下游完成时间中，哪些限制遮蔽了 EP-L2 的作用？多个限制是否相互替代？
3. 在明确、有限的资源条件中，EP-L2 能把多少机会变成应用性能；相对于更强静态分割和相同本地 WB 并发上限，其作用分别是什么？
4. 有效果和无效果的条件分别是什么，额外资源与实现代价是否合理？

立即并行推进以上问题，不以 H0 已有收益显著、D2/L25 完成或 TVD/RO 全部集成为前置条件。不得用已有 0.160% 结果推断实验空间已穷尽，也不得通过只保留有利参数点来制造性能结论。

本合同明确替代旧安排中“先看到局部收益才启动系统交互”的顺序限制，并把中央长模拟并发从 2 提高到 4。新增实验使用独立预算和期限。H0 主结果、原 R19 的身份/计数/期限、已撤回结果、原始 trace、数据正确性、真实生命周期和独立接收要求继续有效。

## 2. 已核验起点

快照截至 2026-10-17 10:43:05 UTC（北京时间 18:43:05）。Lane 必须读取自己的最新状态，不能把此快照当持续运行监控。

| 项目 | 核验状态与下一动作 |
|---|---|
| H0 五配对 | 全部接受，几何均值 1.0016002037656606；保留原 cohort |
| D4 Convolution/FWT | 两配对接受，原两负载均值 0.9997553732076547 |
| Q4 Convolution/FWT | 两配对均已接受，均值 0.994794657046569；FWT 待论文增量接收 |
| D4 vectorAdd/SAD | 两配对均接受；vectorAdd B45055/U45052，SAD B110550/U110528；作为扩展组，不改写原两负载组 |
| R19 | 已启动 12、接受 12、当前发布快照无活动 sim/lease；已选 D2/L25 还需 8 个应用运行，依赖 Lane1 精确 producer handoff |
| Lane6 EN-v7 | 1740009d1579b2402b32076f4f65f27619396c01；4 页正文 + 1 页参考，作为下一版母稿 |

证据：

- [Lane5 最新状态快照](https://github.com/swayhrl/accel-sim-framework/blob/73d3e3eedbfd92643db2f674a49e16605d3e2260/docs/ep_l2/codex_handoff/fast_track_2026_10_16_v1/lane5/STATUS.md)
- [R19 运行、资格与选择记录](https://github.com/swayhrl/accel-sim-framework/blob/73d3e3eedbfd92643db2f674a49e16605d3e2260/docs/ep_l2/codex_handoff/fast_track_2026_10_16_v1/lane5/R19_CONTINUE_RECEIPT.json)
- [D2/L25 已有精确请求](https://github.com/swayhrl/accel-sim-framework/blob/73d3e3eedbfd92643db2f674a49e16605d3e2260/docs/ep_l2/review_packs/FT20261017_LANE5_R19_INITIAL8_AND_SELECTION_r1/LANE1_FOLLOWUP_REQUEST.json)
- [EN-v7 论文与检查](https://github.com/swayhrl/accel-sim-framework/tree/1740009d1579b2402b32076f4f65f27619396c01/docs/ep_l2/review_packs/FT20261017_LANE6_EN_V7_OWNERSHIP_D4_r1)
- [研究章程](https://github.com/swayhrl/accel-sim-framework/blob/1db2ff7a1aa2eb3b221e6184b9abf149c7e178de/docs/ep_l2/project_spec/RESEARCH_CHARTER.md)

### 不变的 H0 身份和资源

- Core：`7b8e6ac70b8fe0f1bd37efca11acb5284938825d`。
- Framework producer：`9bd17f9db3e8cbbc3fdad7283d1e292918546fd5`。
- binary SHA256：`23094a9d6d6bc5edc4afae4dfc1c5ef0fb3b5d45fbfe56ffb4a33db46c597dee`。
- 对照 B16_BANKED / U_WB16：每 slice 1024 Tags，1168 × 128B payload，4 banks × 292 slots，每 bank 每物理 GPU cycle 至多 1 次真实 line operation；共同 128B latch 在池外。
- 512 requester descriptors、128 Line-MSHR、每地址 32 requests、128 WAD；64 slices / 32 channels；TVD、RO 和所有 Ideal 均关闭。
- L1 64KiB / 4 banks / 20 cycles；实际 ROP 延迟 160 GPU cycles；core:ICNT:L2:DRAM = 1132:1132:1132:850 MHz。
- ICNT→L2 / L2→DRAM / DRAM→L2 / L2→ICNT queues = 64/128/64/64；scheduler128、return192、derived credits319；`dram_latency=100` GPU cycles。
- 完整原生 trace 的现有 non-atomic scope、32B sector/producer-version 和生命周期审计保持；这不等于已经验证全数值 SASS 输出。

Q4 = queues64/512/256/64、scheduler512、return768、credits1279、DRAM850、接口100。D4 = Q4 + DRAM3400。已选 D2 = Q4 + DRAM1700，L25 = D4 + 接口25；其余字段以精确有效配置为准，不允许凭条件名补造。

## 3. 同时推进的四条实验线

| 线 | 第一批干预 | 主要责任 | 独立回答的问题 |
|---|---|---|---|
| 下游 | 续行已选 D2、L25；复用已接受 H0/Q4/D4 | Lane1 配置、Lane5 应用 | DRAM 服务与固定接口时间是否限制性能或相对收益 |
| L2 结构 | 固定总量 S64、U_CAP16、有限 bank P2 | Lane2 模块、Lane1 release、Lane5 应用 | 更强静态、动态 WB 并发和 bank 服务的实际作用 |
| 上游及控制 | ROP40_H0、L1_32_H0、ICNT2_H0、WAD256_Q4 | Lane3 配置/受影响检查、Lane1 必要接入 | 固定延迟、L1 需求形态、NoC 供给和 WB 完成控制是否遮蔽作用 |
| 分层与全数据访存理想参考 | I_WB、I_META、I_WB_META、I_READ_HIT、I_MEM_ALL_DATA；有依据时 I_BANK/I_L2_SERVICE | Lane4 模块、Lane1 release、Lane5 应用 | 局部资源机会、L2 服务机会和整个数据访存机会各有多大 |

Lane6 与这些实验同步写作和接收。TVD/RO 候选保留，但不是四条线的共同依赖；本轮 Lane2/3 优先完成上述结构/参数任务。不要覆盖原模块或让扩展开发阻塞已经合格的条件。

## 4. 有限配置与结构的精确定义

所有新名称都是本合同的逻辑 profile，不表示当前 CLI 已实现。Producer 必须提供真实 source/config 映射、effective dump、功能向量和资格，不得只把字符串写进报告。

| Profile | 干预；未列项保持所指基准 |
|---|---|
| S64 @ H0 | 总 payload 固定1168；静态 resident1024 + bypass80 + WB64，4 banks 各256/20/16；B16 copy read→共同 latch→staging write→send read、WAD128、原 bank 服务和 tag 数保持 |
| U_CAP16 @ H0 | U 原位协议、落点和1168池保持；加入最多16个本地 WB 数据责任 token，包含 pending/reserved/live；`reserved+live<=16`，lower acceptance 释放，WAD 到真实 set_done 另行保留 |
| P2 @ H0 | 同4 banks、1168容量和映射；每 bank 每物理 GPU cycle 可执行2次真实 line operation，B/U 同时获得这一有限服务预算；明确额外端口/吞吐模型的成本 |
| ROP40_H0 | 有效 `-gpgpu_l2_rop_latency` 从160到40，其余 H0 |
| L1_32_H0 | L1 从64KiB到32KiB；保持128B line、4 banks、20cycles及已声明其他队列/策略；通过真实 cache-config 仅改变容量字段，输出有效 sets/ways/capacity |
| ICNT2_H0 | clock domains = 1132:2264:1132:850 MHz，仅 ICNT 为 H0 的2倍 |
| WAD256_Q4 | Q4 下 WAD 从128到256，其余 Q4；若配置 guard 需扩展，做明确 opt-in 范围并验证，不关闭 guard |

S64 不能通过简单设置旧 `wbuf=64` 实现：当前源码按 `1152+wbuf` 分配，会得到1216而非1168。准确边界为 resident0..1023、bypass1024..1103、WB1104..1167；所有派生 getter、统计、配置验证一起一致化。S64 必须实际测是否仍达 WB 配额，不以 U 曾出现55项 WB record 峰值就宣称最优静态。

U_CAP16 不能直接使用 WAD.size 或仅检查 WB map 大小；pending reservation 和 bank retry 也占 token。比较 U_CAP16/B16 是相同本地 WB 并发额度下的组织整体差异，含复制与物理 bank 落点差异，不能标作纯 copy-only 消融。U/U_CAP16 才在 Unified 协议内部隔离额外 WB 数据并发额度。

L1 容量改变会改变到达 L2 的请求流，属于显式系统配置敏感性；它复用相同原始应用 trace，但不声称保持同一条 L2 请求序列。P2、ICNT2、WAD256 等额外资源必须同时给 B/U，报告成本和基准变化。

## 5. 理想参考语义与验收范围

| 模式 | 解除 | 必须保留 / 解释限制 |
|---|---|---|
| I_WB | Static WB 数据槽容量拒绝；需要时显式超预算 backing | 保留 source read、copy write、send read、4bank限制、WAD128、地址排序、lower acceptance/set_done；不是零成本 WB |
| I_META | Line-MSHR / global descriptor / per-address count 三类容量 | 动态跟踪仍真实持有请求身份；Tag、payload、sector、依赖、bank 和下游保留 |
| I_WB_META | 以上两项联合 | 直接检查瓶颈替代；不假设单项无效就组合无效 |
| I_READ_HIT | 合格 demand read 的真实 L2 miss/lower-read 服务 | 包括冷读的版本参考服务；保留当前 ROP、bank、响应路径和先行 producer/WAD/MSHR 依赖，write/atomic/写分配伪read走普通路径；不是 RO 机制上限，也不是全访存无阻塞 |
| I_BANK（预备追加） | payload bank 资源竞争等待 | 逻辑 line 读写及数据版本记账；独立理想资源标签，不能混入有限P2 |
| I_L2_SERVICE（预备追加） | demand-read参考、WB/metadata容量和payload-bank竞争联合解除 | 保留明确的L2/ROP基础延迟、L1、NoC、SM及消费端；write/WB责任仍闭合，不叫全memory ideal |
| I_MEM_ALL_DATA | 已发起数据访存采用最小正延迟1个物理GPUcycle，取消数据层次的容量、bank、队列、链路服务等待 | 保留原完整指令流、SM指令发射/计算资源、寄存器依赖、屏障和真实producer顺序；明确取指路径不变；全数据作用域见下文 |

### 全数据访存端点必须真正落实

I_MEM_ALL_DATA 必须覆盖 global/local；shared/constant/texture 也须覆盖，或用每个样本的真实访问与等待证据证明没有残留该类阻塞。若只能完成部分作用域，按实际范围改名并发布部分诊断，但不能把它当作本合同要求的 ALL_DATA 端点已完成。

严格服务定义：请求达到真实发起且必要先行 producer 已合法可见的 eligible 时刻后，reference-ready 必须发生在下一物理 GPU cycle，即 `t_ready=t_eligible+1`。该路径不得保留有限 memory admission、response/LDST FIFO、每拍返回配额或链路服务等待。内存指令仍消耗原 SM 指令发射资源；完成事件按真实请求/指令协议消费 snapshot、更新 pending 计数，并在实际寄存器写回/依赖完成后释放 scoreboard，不能直接提前清除。若保留原 SM 寄存器端口竞争，单独记录 reference-ready 到 architectural consume 的延迟；普通 LDST/response FIFO 不能改名为 SM 约束。真实 producer 依赖单列，不得提前服务未具备依赖条件的 read，也不能把额外资源等待藏进 eligible 的定义。

Lane1/4 选择改动更小、能证明语义的一条实施路线：

- 保留生产 transaction/lifecycle，逐级理想化相关资源，所有原事务仍经过真实数据提交和完成钩子；或
- 在 LDST 请求边界建立隔离的端到端 reference 服务，保持真实指令/请求身份、byte mask、producer version、read snapshot 和完成事件；从 quiescent 模式入口起不再创建普通 cache dirty 状态。所有原始 store 必须恰好一次提交 reference；已有 dirty/WB 必须先排空或拒绝非 quiescent 入口，不能丢弃责任。此模式没有经过的物理 cache/WB/DRAM 活动统计记 N/A，不当作节能。

参考存储的未知初始字节使用既有符号身份/版本语义，不虚构为已知数值零。非 atomic 样本保持原 scope；若 trace 有未支持的 atomic 等，明确阻塞该样本或实现对应参考语义，不默默忽略。

旧候选的 I_READ_HIT 与 WB/META/U 组合尚不合法。新组合需要实现和针对依赖、服务、数据、退尽的检查，不能删除非法组合断言就宣称可用。`gpgpu_perfect_mem`、`l2_ideal`、Local-Xbar PERFECT 或 simple DRAM 的名字都不构成 ALL_DATA 资格；必须核实实际执行路径和残余等待。

理想模式采用与其真实路径匹配的独立接收 scope。端到端 reference 合法绕过物理 L2 时，不要求它伪造不存在的64-slice WB活动；应检查原始指令/请求、原始store/reference提交、顺序、返回snapshot和全状态退尽。有限模式继续原生缓存路径的身份、bank、sector、WB、WAD和终态检查。任何模式都不能靠删除检查获得 PASS。

这些是操作性乐观参考。调度、合并和替换轨迹可能变化，不宣称在任意交错下都是严格数学上界；实测若无改善或退化，照实保留。

## 6. 首轮矩阵、预算与期限

新 experiment_id：`EPL2_PARALLEL_POTENTIAL_20261017_V1`。

[EXPERIMENT_MATRIX.csv](EXPERIMENT_MATRIX.csv) 列出50个预声明 seed cells，状态仅为计划、等待资格；不包含旧 R19 已选的8次 D2/L25 运行。

| 组 | Cells |
|---|---:|
| Convolution/FWT/vectorAdd/SAD：B16 OFF、I_WB、I_META、I_READ_HIT、I_MEM_ALL_DATA；另 Conv/FWT I_WB_META | 22 |
| CFD：B16 OFF 与 I_MEM_ALL_DATA 负样本端点 | 2 |
| Conv/FWT：U OFF、S64、U_CAP16；P2 的 B/U | 10 |
| Conv/FWT：ROP40_H0、L1_32_H0、ICNT2_H0、WAD256_Q4，每条件 B/U | 16 |
| 合计 | 50 |

统一上限 **72 次新增完整应用 STARTS**，失败、timeout、全应用 canary、新 release 的匹配锚点也计数；不是72个成功结果。原生定向小 fixture 不算完整应用，但照常占中央资源。新 T0 为首次新 campaign 注册时刻，期限为 `min(T0 + 24h, 2026-10-18 14:00:00 UTC)`，即不晚于北京时间10月18日22:00；每次应用 timeout3600s。期限后不新增启动，已准入任务按其原 timeout 完成/终止并发布实况。若开启时已过绝对期限，不回填 T0，发布过期未启动状态。

精确相同 source/binary/config/trace/作用域且仍被接受的既有 anchor 可复用；新 binary 的 B/U 对照不得拿旧 binary 一边拼接。滚动 release 若需要更多匹配 anchor，计入72。矩阵中的一个逻辑 B16_OFF cell 不能冒充所有未来 binary 的共同锚点；按具体比较关系派生必要锚点，并留出预算。

剩余预算最多22次用于有证据的联合诊断/有限配置、锚点、失败修复和验证，不要求填满：

- I_BANK 的 Conv/FWT B/U（4次）、I_L2_SERVICE 的 Conv/FWT B（2次）。
- 至多2个有限二因素组合，每个联合端点为 Conv/FWT B/U（联合端点最多8次）；必要的背景/单因素补点另计预算，启动前记录选择依据、确切资源差分和对应单因素点。
- 最有解释力的有限候选在 vectorAdd/SAD 各 B/U（最多4次），或已有不参与这轮选择的验证输入；历史 btree/dwt2d 不能声称从未见过。
- 若新有限条件成为论文性能主张，优先在该同一条件下补 S64 和 U_CAP16 的 Conv/FWT（最多4次），从同一22次余量分配；H0 的强静态点不能自动证明另一环境中的竞争力。视必要性替代其他可选项，不把各项额度相加后突破72。
- 若锚点/失败已消耗余额，缩减后续可选项并说明；不能悄悄加预算或把运行换 campaign ID 绕过限制。

每个有限二因素联合必须具备同 binary、同输入、同背景配置的00/10/01/11四格，每格有相应B/U。缺失的背景锚点或单因素点也算新增启动；预算不足时选择已配齐的组合，不省略对照。例如 P2_H0 不能当作 P2+WAD256_Q4 的单因素背景，后者需要 Q4、P2_Q4、WAD256_Q4、P2+WAD256_Q4 的同源四格。

组合选择看“解除后仍被哪个具体限制挡住”，不只看哪个单点 speedup 最大。单因素均弱而联合强是允许被验证的研究假设。完整 Cartesian sweep、无限迭代和新大型 trace 收集不属于本轮必要路径。

原 R19 始终保留 `EPL2_DOWNSTREAM_HEADROOM_R19`、planned20/cap24、T0=2026-10-17 07:09:16 UTC、deadline=2026-10-17 17:09:16 UTC（北京时间10月18日01:09:16）。不重启、不重计、不延长，也不把已选 D2/L25 伪装成新 campaign 以逃避旧规则。

## 7. 实际并行与共享资源

继续使用唯一中央 `/workspace/ep_l2_ft20261016_shared/RUN_REGISTRY.json`。Lane5 负责所有完整应用的去重、调度和科学接收；“唯一调度 owner”不意味着串行执行。各 Lane 在独立 worktree 同时准备配置、模块、文稿和小 fixture。

- 全局长 sim 上限4；总预约8 CPU units / 32GiB。真实单线程 sim 每条1 CPU。
- 已测小代表的未来运行可预约4GiB/run；未知新模式初次8GiB/run，后续以实测峰值加余量设置。已准入任务的预约不事后缩小。
- available memory ≥64GiB，workspace 空闲 ≥48GiB，Share 空闲 ≥40GiB，现有其他项目保护保持；不能为凑4并发降低下限。
- 小构建/fixture 同样登记资源 lease，可在4个 sim 之外使用剩余 CPU/RAM；不在每个Lane各启动无登记的全量并行编译。
- 新结果和 build 应选择有空间的真实物理文件系统；核实 realpath、st_dev 和 statvfs，不能由 `/workspace/results` 的名字推断挂载盘。最新 Share 约41.4GiB，新大产物优先使用具备余量的 workspace 盘；不搬动/删除旧证据或终止其他工作抢空间。
- 资源不够时已准入任务正常继续，降低后续并发，完成配置/分析等独立工作并报告具体限制。

当前 registry 的 claim 白名单硬编码 R19 与 Q4/D4/D2/D8/L25。Lane5 对现有工具做窄幅、受锁保护的正向扩展：新增 experiment/profile/单独计数和期限，并明确兼容在途 client/PID/start_ticks/boot/lease 绑定。保留旧记录和撤回历史，不另建 shadow registry，不把所有新 profile 塞进 R19 名下。

调度采用就绪队列轮转：优先接续 D2/L25，其他空槽同时跑已就绪的 Ideal、结构或上游配对；初轮各新线都有结果前，避免某一线独占所有空槽。通常同时运行两组 B/U pair；单臂 Ideal 与匹配 anchor 可按同等资源准入。没有就绪配置就继续实现/审核，不派发未经资格的空壳运行。

## 8. 滚动发布与独立接收

Lane1 先逐条件交付旧 binary 的 D2/L25，不等新代码编译。Lane2/3/4 交付的一个模块或 profile 就绪即发布自己的 patch/config、scope、必要检查和精确 hash；Lane1 小步集成可就绪模块。可以合并同时就绪的模块减少重编译，但不为等待未就绪功能阻塞已有实验。

CSV的producer_owner为模块/配置材料责任者，runtime_release_owner表示新binary由Lane1发行。Lane3在已冻结binary上直接可用且已补齐资格的overlay可以直接交Lane5，不需要Lane1重复包装；实际需改公共接口或源码时才走新release。不要把runtime发行角色扩大成所有现成配置的共同等待点。

所有新功能默认OFF，不覆盖已冻结 binary。新 release 有独立 Core/Framework/binary/config/feature-vector 身份；完整路径语义、受影响生产测试、关闭态和有限共享路径回归按改动风险验证。复用有内容身份的未改动检查，避免重跑所有历史矩阵；新模式不能继承未覆盖的旧资格。

Lane5 接收 producer 后独立校验并启动，接收完整应用的 native/ref scope 后发布 single-pair 或 single-ideal adapter。Lane6 逐项通过现有接收器的显式 scope/condition 分派复核后写入论文。普通控制、新条件、新理想作用域使用窄幅可审查扩展，不移植别的条件的 PASS 证明。

已验证且内容不可变的 pack 可缓存校验结果；每次仍检查目标行的当前接受/撤回状态、实际身份及条件资格。与目标无关的全局账本追加不应强制重复全量内容 hash；只有能证明目标内容和资格未变才可复用。科学 payload 缺失或无法证明不变时不得猜补。

## 9. 每条结果必须能支持怎样的结论

主性能效应始终在同一有限系统条件 h 内计算：`S_EP(h)=C_B(h)/C_U(h)`；交互 `J(h)=S_EP(h)/S_EP(H0)`。同时给出 B/U 绝对 cycles，避免两者都加快被误写成 EP-L2 收益扩大。

系统理想余量单列 `C_B(H0)/C_I(H0)`，匹配同 release 和声明的 Ideal 语义；它不是 EP-L2 加速比。若引用捕获理想余量的比例，只能对同条件、同身份且分母为正的 `(C_B-C_U)/(C_B-C_I)`，保留负值且说明这只是该参考下的描述。不得把不同 blocker 的计数/等待相加当成总可优化 cycles。

每项包含：完整身份、真实有效参数、instructions、cycles、request/response exact-once、copy与bank逻辑工作/实际grant、各资源有效分母的拒绝/等待/occupancy、WB-data/WAD分界及真实drain；理想模式按实际路径给出 removed/residual waits 和 N/A 字段。不得把 retry events 当唯一请求或 stall cycles。

现有 `staged_max` 是 WB record/event 峰值，不能替代采样的物理 payload-role occupancy。B16 的 staging 计时从 copy readout 起，U 从 producer commit 起，两者不能当作同起止延迟直接比较；同模式跨条件可比，跨模式应使用真正共用边界的既有观测或明确新增观测。

H0 五组、D4 原两组、Q4 原两组及 D4 扩展组各自保留预声明成员。新矩阵均值按 profile/condition 与预声明workload集合计算，不能把同属IDEAL或L2_STRUCTURE的不同模式混成一个均值。只有完整组才计算组均值；负例、失败、未测各自保留，失败/未测不填0或并入平均。显著高性能的有限点必须带其资源变化和负例，不替换 H0。

当前数据/metadata差分账可立即更新；实测 PPA 需要对应RTL、技术库、约束和匹配综合/时序证据。C++字段字节数不等于物理面积；增加1周期的性能敏感性不等于STA。新结构默认不宣称得到物理净收益。

## 10. 完成标准与短期交接

每个 Lane 按同目录 LANE<N>_GOAL.md 直接续接原工程，先读现场真实状态。普通实现问题自行修复；独立工作可继续时不因一个未就绪项整体停转。

代码/config 每就绪一项就发布 producer handoff；完整应用每接受一项就形成不可变证据；每个完整 pair 或可用 Ideal 端点即可触发短论文更新。Lane6 本轮完成当前已到结果接收、现有图、未来 schema 和成本差分后正常结束，不建立长期轮询器。

到预算/期限或任务结束时发布实际已完成、仍在途、缺资格、失败/timeout和可执行下一步，不把“计划50格”写成“已跑50格”。最终目标是提交时具有机制、潜力、有限实现效果和代价之间可追溯的证据链，而非追求实验数量本身。
