# EP-L2：分离 GPU L2 中的数据驻留、写回暂存与事务完成

版本：V1，2026-10-16。本文为可审阅正文；机制描述是本轮设计合同，历史实测单独标注。本轮功能结果尚未入表。会议版式、页数与截止日期沿用用户投稿要求，当前未核查。

## 摘要

GPU L2 同时维护缓存驻留数据、等待返回的事务和待下发的脏写回。这些对象需要的地址可见性、数据存储与完成状态具有不同的释放边界。固定分区使数据容量只能服务预先指定的角色，而简单地释放 Tag 或移除 MSHR 又可能破坏返回落点、合并关系及写回顺序。本文研究 EP-L2：将物理 payload 通过带代际的句柄与 Tag、请求链和写回控制状态关联，在保持总数据预算和 Bank 服务能力一致的条件下，首先让真实写回暂存使用共享容量，再独立考察瞬态受害者保留与只读 pending 事务。主比较采用每 slice 1024 resident、128 bypass 和 16 WBUF 项对应的 1168 项数据预算；8 项 WBUF 是预先指定的敏感性配置。本文区分有限资源实现、只读 oracle 辅助实现、影子观测和理想化诊断，并以数据/版本参考模型、事务退尽和来源绑定作为实验有效性的前提。历史校准已说明，移除单个元数据阻塞并不必然带来系统加速；本轮机制性能、完整覆盖率及工艺相关 PPA 结论保留为待验证项，不提前填写收益数字。

## 1. 引言

一次 L2 miss 的生命周期远长于一次数据阵列操作。请求可能先消耗合并和响应描述符，随后等待下层发行及 DRAM 返回，最后还需等待上层响应队列接收。与此同时，一个被替换的脏 line 可以已经退出 Resident Tag，却仍需占用某处数据存储，直到下层真正接收其内容；地址顺序约束又可能继续保持到写回完成。把这些边界视为同一个事件，会同时造成资源计账失真和错误的释放行为。

EP-L2 的出发点是分别表示三种关系：Tag 是否让一个地址可被命中，事务是否仍对等待者承担完成责任，以及哪些物理存储项仍承载有效数据。它们可以通过同一个 payload 句柄关联，却不需要同时创建或同时销毁。共享数据池的价值也不能仅从“池中有空闲项”推出：必须存在真实、有限且会背压的消费者，并确认借用释放了有效服务的限制。

已有校准提供了这一研究纪律的直接例子。在历史 1152 项静态模型中，将描述符从 256 扩到 512 消除了相应容量阻塞，但多数工作负载的周期近似持平或略有增加。对 convolutionSeparable，继续将 Line-MSHR 从 128 扩到 256，使 931,416 次精确 full 阻塞事件降至零，周期仅从 292,211 降至 291,108。这组结果支持瓶颈替代的解释，不能被写成完整理想 L2 的上限，更不能替代新的有限 WBUF 基线。[H1, H2]

本轮设计因而从真实 WB staging 开始。用户确认独立 WBUF 的数据容量位于原 1024 resident＋128 bypass 之外，并允许其物理并入共享池。我们在观察性能之前固定 C16 为 primary、C8 为 sensitivity，在相同 Bank 数和单 Bank 服务能力下比较静态分区与统一分配。TVD 与 RO 在各自正确性和覆盖条件满足后独立加入，避免通过同时改变多个资源来制造难以归因的加速。[C0]

本文的当前贡献是：提出生命周期与数据归属分开的 EP-L2 设计；给出有限 WBUF、原位写回、TVD 和 oracle RO 的接口及正确性条件；建立等预算、Bank 匹配并包含强静态重划分对照的评估方法；提供可重算的硬件 bit 账与来源约束。哪一个功能最终构成性能贡献，将由 Lane 5 的独立验证与 Lane 4 的诊断结果决定。

## 2. 问题定义与已有证据

### 2.1 写回 staging 不等于写回完成

令 t_v 为 dirty victim 被破坏前开始预留资源的时刻，t_r 为实际数据读出/packet 创建时刻，t_a 为下层真实接收数据的时刻，t_d 为真实写回完成时刻。WB staging 的有效数据驻留区间为 [t_r,t_a]，预留还可能覆盖 [t_v,t_r)；WAD 的地址顺序状态保持到 t_d。若下层只接收到指针、仍依赖源 payload，则 t_a 尚未构成可释放数据的交接边界。本文显式记录每段数据驻留，保留下层数据队列的存储和服务成本。[C0, S2]

历史 M0b 发现，已完成样本的旧 resident payload 句柄在替换后已经失效；WAD 仍活跃不能推出旧 resident 数据也被一直固定。因此本文不再将“提前释放一个被 WAD 固定的旧 resident slot”当成已证实的贡献。新模型引入真实有限 WBUF，其暂存容量与分配背压需要新的实测证据。[H4]

### 2.2 静态数据配额与共享控制预算

静态 C16 将 1168 个 line-sized 项分给 1024 resident、128 bypass 和 16 WB staging 项。共享模式保留相同数据总量，允许 WB 在合法空闲或可回收容量中分配；它不再受原 16 项数据角色配额约束。这个改变不能同时赠送无限 WB 控制节点。WAD、发行 credit、句柄及控制队列都保持明确边界，新增 pointer/state 在 PPA 中单独计费。对没有 bypass 请求的计算 trace，也不能把闲置 bypass 区域本身当成已发生借用的证据。

### 2.3 时间重用与空间访问必须分开

归档的 sector 观测表明，vectorAdd_4M 的 line 重用率为 75%，但同一 sector 的时间重用率为零：对一个 128B line 中不同 32B sector 的访问造成了前者。这说明 line 级重用分布不能直接支持 victim-cache 命中率或 TVD 避免下层读取的结论。本文使用 sector-valid 条件判断 TVD 服务，实际避免的读取和字节必须由启用功能的运行记录给出。历史 sector 数据仅作为工作负载异质性动机。[H5]

### 2.4 适用范围

本文讨论的是明确定义的架构模拟模型，而非对商业 GPU 内部组织的逆向断言。我们不新增 AI/graphics trace，也不声称当前计算 trace 覆盖真实图形 bypass。历史 oracle、影子投影与本轮真实执行产生的统计分别保存；低收益、退化与未完成结果分别呈现。

## 3. 架构与状态接口

### 3.1 固定预算与比较对象

每个 slice 的 Resident Tag 为 64 sets × 16 ways，line 为 128B、四个 32B sector；共享 requester descriptors 为 512，Line-MSHR 为 128，每地址上限为 32，WAD 为 128。全芯片有 64 slices、32 memory channels。主 DRAM 频率为 850MHz，L1 沿用已校准 BASE。[C0, H1]

| 模式 | 每 slice 数据项 | Bank 组织与服务 | 角色/含义 |
|---|---:|---|---|
| OLD_D512_STATIC | 1152 | 4×288，1 line-op/Bank/cycle | 历史静态模型；没有本轮真实 WBUF16 |
| B16_BANKED | 1168 | 4×292，同一服务上限 | 1024/128/16 静态分区，真实有限 staging |
| U_WB16 | 1168 | 4×292，同一服务上限 | WB 使用统一容量，TVD/RO 关闭 |
| B8_BANKED / U_WB8 | 1160 | 4×290，同一服务上限 | 预设敏感性配置 |
| U_WB_TVD16 / U_WB_RO16 / FULL16 | 1168 | 同主配置 | 逐项加入 TVD、oracle RO 或组合 |

表中本轮模式描述已同意的设计，不是已完成的实验结果。每个 mode 是否已实现、接入或运行，以 Lane 1/2/3 的准确 source contract 和 Lane 5 的验证 receipt 为准。LEGACY_SEPARATE_C 是分离 RAM 参考，其新增 WBUF 端口数尚需明确建模，不能由“数据在外部”推成一个免费独立端口。

本稿已读取 Lane 1 发布 `cb7d92e4edde97e81520cfdd00762dfe81ee9b20` 中的 V1 接口与 baseline contract：共同父版本为 Framework `54fbc7869f4e40b6b48dc936b527fee85dd46406` / Core `1fc248aa89abefbd1b417f7f4053cd2bf56d7a1e`，接口源码为 Core `4fb91f0a5c9eb3bf494a154ea1f24b9a56b34617`。该合同明确 `runtime_ready=false`，binary/config 为空；因此可以按已发布接口描述架构，但尚不宣称新模式已运行。V1 声明首版拒绝 generation wrap；这仍不决定物理 generation 的最终位宽。

### 3.2 句柄、身份与两阶段提交

Resident Tag 不再普遍满足 tag index 等于 payload ID。它保存 payload 指针，并在适用时关联 generation。统一分配首先保持 resident 的 bank class，即 payload_id mod 4 等于 tag_index mod 4；放宽这一约束属于独立 placement 机制。preview 只检查资源，不修改 Tag、描述符、WAD 或数据归属。commit 必须原子地取得所有必要资源；失败不能留下半个写回或已破坏的 victim。

物理项以一个互斥主 owner 分类，pending sector、读取引用和 pin 作为附属状态。任意时刻 FREE＋live payload 项数等于物理预算；统计不能把同槽同时作为 resident、fill 和 WB 各计一次。跨 Tag 复用、同地址多事务以及晚到响应都通过 {id,generation} 区分。generation 位宽必须由最大未退尽引用与复用界限证明，不能直接沿用模拟器 unsigned 的宽度。

### 3.3 静态 WBUF 与原位统一写回

B16 在 dirty victim 改写前预留 WAD、WBUF 数据落点和确实需要的发行槽位/credit。resident→WBUF 拷贝消耗读出、写入及必要传输暂存；WBUF→lower 又消耗读取服务。实际端口占用由 Lane 1 的生产路径确定，并在局部消融中检验。

U_WB16 将旧 resident payload 原位转成 WB_STAGED，控制句柄保持其可达性；新 resident 使用另一合法落点。旧数据被下层真正接收并有已计账的数据承载后，WB staging 可释放，WAD 继续保留到 set_done。若同 Bank 空间或 mandatory landing credit 不足，分配必须合法拒绝或等待。reserve 数从等待依赖与最坏 Bank 情况推导，不能按加速结果选取。

容量共享与拷贝消除可能同时影响结果。因此若发现收益，除了原生实现比较，还需在代表点保留相同 copy 服务成本、只切换容量借用，以分离两者。正收益还需面对同总量的强静态分区对照，例如 1024 resident＋112 bypass＋32 WBUF；compute-only 1024＋0＋144 只能标为牺牲 bypass 能力的竞争参考。

### 3.4 TVD：可见性与延长的数据保留

Tag miss 后增加一拍 TVD 查询是本轮时序假设；其目录、Bank 请求与仲裁都计入竞争。这一拍不代表已通过静态时序分析。read 只有在所需 sector 全部有效时才可 serve-in-place。clean victim 的 write/atomic 先 promote，保留原 payload，通过原子可见性切换保证单一可写 owner。

dirty WB 数据在 lower accept 之后继续保留以支持 inflight read-forward，属于 TVD 新增 retention，不能再归入原 staging 区间。WB_PENDING/INFLIGHT 不能当成可回收 clean 缓存项；write/atomic 等待 WB 完成。dirty read-forward 必须在生产入口可达，不能被旧 WAD preview 无条件拦截。sector 不全时使用保持顺序和单 owner 的回退路径，不能将整个 line 视作 hit。

### 3.5 完整 epoch 的只读 oracle 与 pending 事务

首版 RO 允许完整 epoch/line 粒度 oracle。它排除同 line store、atomic、写分配产生的伪 read、别名重叠以及无法排除的并发/外部写。分类为只读不等于当前请求是 load；未被证明的请求走普通路径。oracle 覆盖率、离线预处理和潜在运行时替代成本单独报告。

RO transaction 可在 attached 状态通过 Tag 合并等待者，detach 后仍通过 payload 和描述符链承担完成责任。同地址 detached/attached 实例按不同 {id,generation} 共存，不能被按地址清理误删。attached fill 核对 Tag generation；detached fill 不重新安装 Tag。返回落点、sector masks、响应背压和最后一个消费者读取完成之前的 pin 都需保留。RO 可减少 address-indexed MSHR 压力，但 completion 状态仍有硬件成本，且重复 lower read 可能增加 DRAM、描述符及 payload 压力。

### 3.6 数据驻留与前进保证

| 阶段 | 数据驻留/责任 | 释放边界与验证 |
|---|---|---|
| 静态 dirty victim→WBUF | resident 与 staging 的拷贝窗口 | 两侧都计数；服务完成前保持 source pin |
| U_WB staged | 原 resident slot 转 WB owner | 下层实际收数且后续承载已计账 |
| 下层发行/排队 | 明确的队列、传输缓冲或有生命周期的共享 slot | 不能把 mem_fetch 指针当免费数据 RAM |
| TVD dirty inflight | retained payload＋mandatory WAD | WB 完成前不可随意回收 |
| RO detached fill | 已预留 landing＋completion chain | sector 与所有 requester/读取引用退尽 |

## 4. 实验方法与证据契约

### 4.1 运行身份与接收门槛

每条用于正文性能图的记录绑定 Core SHA、Framework runtime SHA、binary SHA256、完整 runtime config SHA256、trace 内容身份、workload/epoch 范围及 feature/ideal 向量。协调提交只确定任务合同，不作为 runtime 源码。图表 publication SHA 也不替代 runtime SHA。仅 COMPLETE_VALID、正常退出且数据/版本、request identity、payload、退尽检查通过的记录可以进入主性能表。

Lane 6 从 Lane 5 的独立验证结果接收预算内实现，从 Lane 4 接收历史复用与 ideal 诊断；先核对 receipt、manifest 和逐行来源，再制图。暂缺的性能单元用 NOT_RUN 或 DEPENDENCY_PENDING，失败、超时与身份不匹配行保留原因并排除聚合。框架整体聚合、几何平均与每 workload 结果必须采用相同预定集合，包含不加速和退化的 workload。

### 4.2 预定集合与比较顺序

开发集为 convolutionSeparable、FWT_7_21、cfd_097k、vectorAdd_4M、sad；btree、dwt2d 是不参与首轮调参的验证集，二者此前已被观察，不能称从未见过。scan 作为独立长任务排队。首个功能比较是 B16_BANKED 对 U_WB16，随后滚动加入 TVD、RO 与已合格组合。C8 是敏感性，不能根据结果反选 primary。资源配额和 run-key 去重由 Lane 5 管理，论文 lane 不启动长模拟。[C0]

### 4.3 正确性先于周期

生产驱动测试将实际缓存/写回/事务路径与小型数据及版本参考模型比较，覆盖同地址不同 sector、stale generation、部分 fill、Tag 复用、同地址 RO 多实例、response backpressure、TVD promotion/forward 以及 epoch/flush 退尽。cycles/instructions 相同只构成时序与工作量一致性，不能替代返回数据正确性证明。未知 oracle 类别与非法 feature/ideal 组合需显式拒绝。

### 4.4 指标及消融

系统层报告 cycles、instructions 和 speedup=T_baseline/T_candidate；同时给出 useful admits/responses、独立请求与重试 attempts、阻塞 cycle 及其分母、等待/生命周期分布。局部指标包括 WB staging 与 WAD 各自寿命、role occupancy、借用/拒绝、Bank 操作与等待，TVD 的有效服务和 avoided reads/bytes，以及 RO 的重复读取放大和描述符压力。lower admission rate 不称作物理 DRAM bus utilization；只有定义明确的原生总线指标使用后者名称。

消融依次考察同 Bank/总量下的容量共享、copy 服务、强静态重划分、TVD retention 与查找成本、oracle RO 及重复读代价。只有主配置中先出现可测局部效果，才采用保持正交的机制×headroom 2×2 检验 downstream masking。baseline 和机制同样受益于 headroom 时，不把系统通用收益归给 EP-L2。

### 4.5 五种证据类型

| 类型 | 可支持结论 | 限制 |
|---|---|---|
| FUNCTIONAL_IMPLEMENTATION | 有限资源模型中功能的局部/系统效果 | 需生产正确性与预算一致性 |
| ORACLE_ASSISTED_IMPLEMENTATION | 给定完整 epoch 分类条件下的功能效果 | 不声称硬件自己获得该未来知识 |
| SHADOW_OBSERVATION | 固定执行流上的机会或投影 | 不声称改变了执行与周期 |
| IDEAL_DIAGNOSTIC | 指定非约束/理想假设下的诊断 | 与实现分表；不是可实现收益 |
| HISTORICAL_CALIBRATION | 旧模型已测敏感性及动机 | 不补填新 B16/U_WB16 单元 |

## 5. 历史结果与本轮结果占位

历史 D512 Banked 的 13-workload 比较没有产生普遍加速；其中 convolutionSeparable、vectorAdd_4M、scan 的 speedup 分别约为 0.99349、0.99258、0.99752。它们是修改元数据容量的历史校准结果，数据预算仍为 1152 项，不能标成本文统一 WB 池的加速。[H1]

| 本轮单元 | 数据/正确性验证 | 周期与加速 | 本文当前用法 |
|---|---|---|---|
| B16_BANKED vs U_WB16 | DEPENDENCY_PENDING | NOT_RUN | 首个功能主表；待 Lane 5 receipt |
| B8_BANKED vs U_WB8 | DEPENDENCY_PENDING | NOT_RUN | 敏感性；不替换 primary |
| U_WB16 vs 强静态重划分 | DEPENDENCY_PENDING | NOT_RUN | 仅在共享有效后选代表点 |
| +TVD / +oracle RO / FULL | DEPENDENCY_PENDING | NOT_RUN | 分别完成验证后加入 |
| I_WB / I_META / I_READ_HIT | DEPENDENCY_PENDING | NOT_RUN | 待 Lane 4，单独 diagnostic 表 |

表中 NOT_RUN 表示 Lane 6 尚未接收并验证对应完整证据，不推断其他 lane 当前是否已有进程。不能将“移除 full counter”解释为系统天花板已达到；有限扩大仍有剩余阻塞时，只称 sensitivity。

## 6. PPA 方法与当前成本

主配置数据 RAM 为每 slice 1168×128B=146KiB、全芯片 9.125MiB；C8 为 145KiB/slice、9.0625MiB/chip。静态与统一比较的原始数据 bit 数相等，但相同容量不推出相同面积、访问能量或最高频率。若保留完整寻址，Tag→payload 的 11-bit 指针为 1408B/slice；若 128 个 WAD/TVD 项各增加 11-bit 指针，则该字段单独为 176B/slice。它们均未包含 generation、owner、sector、pin、目录、仲裁或工艺实现代价。

`PPA_LEDGER.md` 将共同资源、候选新增字段、可能复用和未知项分别列账。描述符总量继续为 512，不因 RO 绕过 MSHR 就扣掉 requester 节点；额外 completion 与 oracle 数据也不能省略。链长可取 0..32，因此若显式保存计数需 6 bits；512 项 next 指针需 9 bits，加独立有效位或采用明示 sentinel 编码。不能照搬早期 256 项/8-bit 指针和 5-bit count 的示意。

当前只报告原始 bit 容量、参数化控制开销与操作事件账。已有历史 V3 RTL 和综合工具不等于存在本轮 B16/U_WB/TVD/RO 的匹配 RTL 对。缺少候选模块、工艺库和约束时，不输出门数、mm²、mW 或已达频率。TVD +1 cycle 保持为模拟时序假设。获得匹配 RTL 后，才在同工具/工艺/宏/时钟/IO 条件下进行 changed-module 差分综合，并保留下层数据 queue、copy 临时存储及 interconnect 的成本。

## 7. 局限与后续结果填写规则

本稿尚不支持“完整 EP-L2 已验证”或任何新机制平均加速的结论。完整 epoch RO oracle 提供有条件的分类信息，不能直接计作零成本硬件能力。当前 workload 不构成 graphics bypass 实证，历史 stack distance 也不保证 TVD 可捕获的 reuse。若新功能无收益，正文应如实保留，并可据证据将最终贡献收敛到 WB pooling 或少数有效组合。本文不为保留架构故事扩大未经授权的实验范围。

## 来源键

- C0：冻结协调提交 `6c136e2a56a008695f8c8b815723bf8f1a760db9` 的 COMMON_CONTRACT、COORDINATION_PROTOCOL 与 LANE_6_GOAL。
- H1：Framework `aa44f9e8d685b6f9bbe410b996e07ef185a8de96`，`FINAL_CALIBRATION_CONVERGENCE_r1/` 与主分支 baseline decision；历史 D256/D512，不是新有限 WBUF。
- H2：Framework `b7dbdecb94054f08aaf2e33bfef48e453747ceb5`，`LINE_MSHR_CAUSALITY_r1/CONVOLUTION_2X2.csv`。
- H3：Framework `c0a71e204715289895028d27ac82190041d83b85`，`M1_ELASTIC_SUBSTRATE_r1/`；Core `955a50cbb5e8d928b6c7b0c78e1af062b835df44`。
- H4：Framework `7ad2b240fee32492e778611cb6deb45516c29bcf` 的 M0b 9/10 checkpoint；未补造 scan 终态。
- H5：Framework `cdab5765b65f6e1575d9c185de127a1c1c49dd70` 的 `STREAMING_REUSE_PREFINAL_r1/line_vs_sector_reuse.csv`，12 个已归档 prefinal 行、不含 scan。runtime 为 `db1c90182fad02aacbd282b67ecdc57b8e4cc365` / Core `ca3e7bc0b8f61b5d7c052bcda2a91955a1e5c919`。
- S1：Core `1fc248aa89abefbd1b417f7f4053cd2bf56d7a1e` 的 `gpu-cache.h/.cc`、`l2cache.h/.cc`，作为待 Lane 1 核实的共同工程父版本。
- S2：Core `ca3e7bc0b8f61b5d7c052bcda2a91955a1e5c919` 的 `L2interface::push`，shadow WB lower-accept 在真实下层 queue push 之后；不是新物理 WBUF 的实现证明。

图表及来源的准确 blob/hash 见本 pack 的 `FIGURE_INPUT_MANIFEST.json` 和 `SOURCE_EVIDENCE_MANIFEST.json`；未引用外部论文的普遍性/新颖性断言留待相关工作核查。
