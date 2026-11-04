# Lane U174｜109 大型资产跨项目科研使用审查 V1

Goal：`NODE109_CROSS_PROJECT_ASSET_USAGE_REVIEW_174NEW_V1`
执行节点：174-new；分支：`hrl/node174new-node109-crossproject-usage-20261104-v1`。
审查截止：2026-11-04T11:56:53+08:00（Asia/Shanghai）；7/30 天窗口截止分别为 2026-11-11T11:56:53+08:00 / 2026-12-04T11:56:53+08:00。

## 裁决摘要

**目前有证据支持且 owner 明确接受的可降温量：0 GiB；本 Goal 的实际删除、移动、实验启动量均为 0。** 未取得任何本轮直接 owner 回复；以下分类是 U174 根据既有权威状态形成的保守审查建议，不冒充 owner 授权，也不构成 S109 清理白名单。

优先推进 **三处 AWMA pip HTTP 缓存 + 三份 R27 父 checkpoint 本地副本，合计约 15.83 GiB** 的确认与资格闭合。这是低科研风险的**条件候选**：缓存的离线包闭包和 reader 边界未证实，父副本的精确恢复映射与 AWMA 意见仍缺。任一门未闭合都不能释放。StageA 两套 + 缓存的 V2 方案仍是条件 16.76 GiB，但新增 A79 同路径依赖后，不宜再把整套 StageA 当作简单的优先低风险对象。

## 109 大型资产保留与可降温建议表

下表空间全部继承 S109 V2 已分配块口径；不代表本轮重新测量或实际 df 收益。当前使用列区分历史/冻结依赖与当前进程使用。所有“待确认”都保留本地。

| 资产 | 本地 GiB | 已识别使用项目及状态 | 未来 7 天 / 30 天 | 109 常驻必要性 | owner 接受真164恢复 | owner 确认 | 给 S109 的建议 |
| --- | ---: | --- | --- | --- | --- | --- | --- |
| StageA BF16 | 5.76 | C16 历史资格；AI-ARCH A79 冻结方案**精确引用同一本地路径** | 均未知；A79 deferred 不是定期计划 | 待 C16 + AI-ARCH 联合确认，先保留 | 未取得 | OWNER_CONFIRMATION_PENDING | 不因旧 StageA STOP 而整体降温；补登记 A79 reader |
| StageA AWQ | 2.51 | C16 资格/对照；canary neutrality 门曾阻塞；terminal 仍 PARTIAL | 均未知；旧 campaign 不自动续行 | 未确定，先保留 | 未取得 | OWNER_CONFIRMATION_PENDING | 可单独询问是否只需证据归档；不得把 PARTIAL 改为 ABANDONED |
| AWMA 三处 HTTP cache | 8.49 | AWMA R19 FP8 / R17 graph / VLA RTC 环境构建历史依赖 | 均未知；离线重建需求待 owner | 缓存本身不等于运行环境；闭包未证实 | 未取得；也未证实有164缓存归档 | OWNER_CONFIRMATION_PENDING | 首选问询；只限定 http-v2，不扩到 wheels/venv/编译缓存 |
| R27 三份 COMMON 父副本 | 7.34 | AWMA R27/R27r1/R27r2 lineage；R27r2 已有同 SHA 父 seed 收据 | 均未知；后续数值 replay 待确认 | 是否允许恢复后读原绝对路径待确认 | 未取得 | OWNER_CONFIRMATION_PENDING | 第二优先；精确恢复三条路径，保留 R26 规范父本，S109 独立闭合技术门 |
| Qwen3-30B | 56.89 | C16/AWMA 118 runnable exact-revision 引用（V2）；不是当前 PID 证明 | 均未知；未来模型计划缺回复 | 尚不能否认，先保留 | 未取得 | OWNER_CONFIRMATION_PENDING | HOLD；容量、延迟和离线路径要明确，不按 EP/DTC 单线意见替 owner 决定 |
| R26 十个规范 checkpoint | 24.46 | AWMA 正式重复输入结果及 R27 规范 parent lineage | 均未知；分析/恢复需求待确认 | 规范证据必须保留，109 常驻另议 | 未取得 | SCIENTIFIC_CANONICAL_KEEP + owner pending | 不纳入首轮低风险组合；精确恢复而非重跑再生成 |
| R27r2 B1_C1_K2 | 2.45 | AWMA fresh-load/switch 已有资格；整体 varied-input numeric STOP | 均未知；数值续研未授权 | 待确认，先保留 | 未取得 | OWNER_CONFIRMATION_PENDING | 单独保留；不得与三个 COMMON 副本混算 |
| R27r3 B0_a/B0_b 原始张量 | 5.87 | AWMA 原生 repeatability 失败的原始证据 | 未来分析未知；失败不抹去证据义务 | 原始规范证据先保护；本地/冷存待 owner | 未取得 | SCIENTIFIC_CANONICAL_KEEP + owner pending | 排除候选；不操作 raw |
| E1 bounded decode Trace/results | 43.29 | C16/E1；独立 consumer/论文证据链；部分 timing slots 历史待定 | 7/30 天均缺 owner 日程 | 原始/failure Trace 先保护 | 未取得 | SCIENTIFIC_CANONICAL_KEEP + owner pending | 禁止全树降温；不要把 A65 历史已退役 E1-v3 硬链接混为当前 E1 树 |
| A26GR1 Rubble / GS-Scale | 40.77 | AI-ARCH 已完成 bounded discovery；非 200k 收敛/可续训 full checkpoint | 新 GPU 任务未自动授权；后续分析日程未知 | 混合树，原始观测/输入和可重建环境须拆分 | 未取得；报告称 raw/wheels 未入164 | SCIENTIFIC_CANONICAL_KEEP + owner pending | 原包/相机/图像、预处理、原始观测、环境、缓存分别列账；先保留整树 |
| A61 IGB-small | 9.86 | AI-ARCH；A65/A67 **实际只读复用数据和环境** | 新 GPU 未授权；复审/再分析日程未知 | 不能只按 A61 STOP 决定共享树 | 未取得；A61 完整数据/环境未入164 | SCIENTIFIC_CANONICAL_KEEP + owner pending | 原官方数据与派生图、失败观察、环境、cache 拆分，核 A65/A67 全部使用方 |
| NequIP V1R1 | 10.92 | AI-ARCH 已完成；原始 timing、数值输出、固定 compiled identity；独立审查待定 | 7/30 天均未知；无自动下一 GPU 任务 | 小 raw 有归档，不代表全树可恢复 | 未取得 | SCIENTIFIC_CANONICAL_KEEP + owner pending | 444-file raw packet 不是整个 10.92 GiB 环境闭包；分组件恢复审查 |
| env / envs / wheelhouse | 27.61 / 8.25 / 2.90 | C16/AWMA/AI-ARCH 可能共享；A61 后续复用证明需逐路径核对 | 均未知 | 共享/离线闭包未证实 | 未取得 | OWNER_CONFIRMATION_PENDING | 排除首轮；不得随 pip HTTP cache 扩大范围 |
| RTX4080 suite / capture / merged_gate_up | 11.74 / 8.37 / 8.57 | V2 保护 suite、capture；merged 环境/恢复未闭合 | 均未知，suite 活跃性由 S109 更新 | 未确定，先保留 | 未取得 | canonical 或 owner pending，详见逐行 CSV | 不从无 FD 或历史结束推出可释放；逐子资产找 owner |
| 已退役 OLMoE / Llama | 0 | S109 标为 ALREADY_RETIRED | 本地回收不适用 | 无本地量可再计 | 既有归档不等于本轮授权 | 无新增意见 | 回收增量 0；不恢复、不重复计算 |

逐文件/逐目录的继承资产 ID、源路径、空间、项目范围意见与来源见三个 CSV。树中含不可替代观察不意味着每个 cache 都是原始证据；本轮缺少细分恢复证明，因此拒绝整树退休。

## 跨项目使用证据与边界

**EP-L2。** EP_CLOSE 的 Performance-First V2 在 2026-11-04 11:04:43 +08 自然退出：16 accepted、两个条件 GEMM 未释放，下一实验不自动授权；Source assets 明确 KEEP，大型 Trace 继续在已验证 true164。EP_MECH 的机制分析仍有后续结构候选但不构成新模型启动许可。所读 EP 状态/精确 source-input 索引没有建立本台账 StageA/Qwen3/R26/R27 的直接依赖；这是有限文件读取结论，**不是 EP owner 的“不使用”答复**。未来参数探索、机制归因及原始 Trace 的7/30天计划仍待 Main 确认。论文/接受结果证据保留与109模型常驻分开。

**DTC-L1 / DTC。** DTC16 为16/16 accepted；DTC48 的 2026-11-04 11:26:13 +08 发布快照为 EXACT48_BACKGROUND_EXECUTION，37 accepted、11 await、列出10个 running，最终科学收尾未完成。该数字仅为该快照，不是本轮实时进程普查。DTC48_README 明确 supplemental/deferred/unresolved、新 capture/109 实验都不在该批授权。精确 DTC_INPUT / DTC_ONE_INPUT 绑定174路径下的 Trace bundles；FUSE/mount 后端不能仅从路径推断。旧 AE 的 10月27日快照仍有运行/恢复任务，明显早于当前，不能称已全部结束。**DTC 在174执行不等于完全不依赖109**；本轮未访问活动 raw，也未把这些 bundle 与 E1/AI资产强行等同。需 owner 核对 indirect symlink、远端 mount、历史 native capture、AE与未来任务。

**AI-ARCH。** A26GR1 已完成有界真 Rubble 训练观测，raw/wheels 私有且未入164；外部 bounded stop 不产生完整可续训 checkpoint。官方压缩原包可按固定身份重新取得的可能性，与已实际观察的两条不同 densification trajectory、失败/修复历史可否再生成，是两回事。A61 的初始 compiled qualification FAIL 后，A65 新同 batch 数值诊断、A67 eager六窗口均真正复用 A61 官方数据/环境；不能把 A61 状态当全树无用户。NequIP V1R1 完成144 timing、45份数值输出的汇总与 compiled identity；其444文件66,850,400B raw publication范围比10.92GiB树小。A79 为 GPU_RESOURCE_DEFERRED，零正式样本，冻结 model_path **完全等于 stagea_1**；未来重派需要新授权，当前没有确定7/30天日期。没有证据据此标 HOT_ACTIVE 或 WARM_NEXT_7D，但足以阻止把 BF16 当无人使用。

**C16 / AWMA。** STAGEA_TERMINAL 为 C16_STAGEA_TIER0_TERMINAL_PARTIAL，建议停止当前 campaign、不得自动修缓存/Observer；这既不等于 ABANDONED，也不替 A79 后续用途授权降温。AWMA26 的 COMMON_START_STATE 指出 parent snapshot 不可取得，receipt-only hashes 有差异，单次 accepted-semantics derivation被冻结；因此“再跑一次得到同一个规范 checkpoint”不成立。R27_PARENT 的 COMMON SHA 与 R26 一致，是历史 lineage 证据；R27_SWITCH 确认 B1_C1_K2 的 fresh-load/switch，不证明未来不用。R27R2 数值 STOP、R27R3 B0_REFERENCE_NOT_REPEATABLE 都保留原始反例。AWMA_STATE 的 R23G active 记录日期为10月2日，不能移作11月4日当前运行证明；其“164长期authority/109活跃副本”只是一般政策，不是具体候选 owner 接受。

## 热度、期限与合并规则

- HOT_ACTIVE 仅适用于有证据映射到资产的当前科研需求。本轮确认了 DTC 项目级运行快照，未确认这些109候选的实时 reader，所以没有虚标候选 HOT。
- WARM_NEXT_7D / WARM_NEXT_30D 需要带日期的计划或足够明确预期；所有所审候选均缺本轮 owner 日期答复，不把 deferred/提案写成日程。
- COLD_RESTORE_ON_DEMAND_ACCEPTED 需要真正使用方明确接受；本轮数量为0。
- SCIENTIFIC_CANONICAL_KEEP 表达证据保留义务；不自动意味着永远109常驻。
- OWNER_CONFIRMATION_PENDING 是未解决的使用/本地/恢复授权。NOT_OWNED_BY_THIS_PROJECT 只表示该项目不能替真正 owner 决定，**不等于其无间接使用**。
- 合并时任一真实使用方要求保留即 HOLD；未知意见不能通过其它项目的否定意见覆盖。矩阵中的项目范围路由是 U174 判断，不是伪造 owner 表态。

未来7/30天均是从审查截止起的滚动窗口；“未知”不是“无计划”，CSV 明确表示 UNKNOWN_PENDING_OWNER。

## 恢复前提与责任

StageA：由 S109 根据24-file清单，从真164经已验证 bridge 恢复确切 revision/原绝对路径，保留config/tokenizer/index和环境/权限；U174不做实际恢复或重新SHA。A79 BF16需双方确认恢复等待时间及重新资格边界。

缓存：当前未证明真164有对应 HTTP cache。可选择已验证 pinned源/wheelhouse 的离线重建闭包，或由 S109 另行提出归档方案；HTTP缓存不能代替完整 wheel/source/hash/平台 ABI 证据。本轮不执行 pip install、下载或环境重建。

R27父副本：先保留R26规范 COMMON、确认三个路径到规范父本的历史映射，按原布局恢复，保留optimizer/RNG/step/cursor及代码和输入authority；禁止用 fresh run 替代。B1_C1_K2 恢复自己的真164路径，不能套用 COMMON。R26十个 checkpoint 和 B0原始反例逐对象保留。

Qwen3：完整26-file revision恢复到原绝对路径，校验manifest/索引并恢复可用runtime；V2时可用54.08GiB小于56.89GiB整套量，需要未来容量预留及可接受恢复延迟。不能假定 SSHFS 可直接作为运行模型盘。这个容量数是历史快照，应由S109更新。

E1/A26/A61/NequIP及其他混合树：先拆原输入、不可再生观测、派生模型、环境、cache、最终接受结果；每类有精确archive/manifest/路径/环境前提才谈局部冷存。没有证明的恢复步骤标为 NOT_QUALIFIED，由S109闭合，不能借本报告宣称已能恢复。

## 条件组合与不重复计数

| 候选组合（不可执行） | 继承块估计 GiB | 尚缺科学/恢复条件 |
| --- | ---: | --- |
| P1：三 HTTP cache + R27三个 COMMON 副本 | 15.83 | AWMA owner 对7/30天与离线构建/本地恢复等待的明确答复；缓存闭包；S109 当前身份/reader/归档/恢复映射 |
| P2：三 HTTP cache + StageA AWQ 单套 | 11.01 | P1缓存门 + C16/AWMA确认AWQ当前/未来控制用途；不能影响BF16/A79；AWQ24文件子集需S109精确选出 |
| V2 A：StageA两套 + 三 HTTP cache | 16.76 | 新增 C16 + AI-ARCH 对A79 BF16同路径的共同意见；不能只看旧StageA停止 |
| V2 B：V2 A + R27三个COMMON副本 | 24.10 | 上述全部门；与P1/P2/V2 A重叠，不能相加 |

P1相对优先，是为了避开已查明的 A79 BF16 和规范R26/原始证据。它仍有归档/重建与科学门，不能称“已低风险可删”。Qwen3、规范R26、B1_C1_K2、raw、E1、A26/A61/NequIP不用于凑10–30GiB目标。估计按继承精确 bytes 求和后四舍五入；与S109两位小数累加可能差0.01GiB。

## 证据差异与交接 Lane S109

1. 增补依赖：V2 StageA审计的4条历史copyback之外，A79_RUNTIME有同一 stagea_1 model_path。请求S109与C16/AI-ARCH复核reader登记和保留范围，不能覆盖V2原事实。
2. 状态分层：V2 runtime qualification PARTIAL 与 C16后续terminal Tier0 PARTIAL 是不同scope。当前campaign停止不取消新AI-ARCH用途，也不更改任何owner Goal。
3. A61 STOP不是无下游使用：A65/A67只读复用；请AI owner与S109对共享env/data/symlink细分复核。
4. NequIP444文件raw归档不是整树环境/依赖闭包；A26/A61报告明确大数据未入164。不得从模型/小报告已归档推整树可恢复。
5. V2 archive CSV对R27非COMMON条目的 archive_proof 有通用“canonical R26 parent/duplicate copies”措辞。B1_C1_K2及B0有其独立目标路径，不能继承COMMON映射；请S109精确复核，这里不认定其归档已错误。
6. 未找到可直接联系外部Codex窗口的工具/地址；未发送问询、未收到回复。待转交文本是明确交付，不是已完成联系的证明。

S109负责文件身份、真164/源SHA、块量、当前进程/reader、恢复技术资格和最终白名单；本报告仅提供科研证据。S109 V3发现检查见 PROJECT_OWNER_RESPONSES 的采集说明；本轮不干预V3或其它lane锁/分支。所有候选继续HOLD，后续实际清理仍需用户另行授权。

## 交付、验证与停止

交付本目录六文件。逐项来源、分支、固定HEAD、blob与文件提交时间完整列在 PROJECT_OWNER_RESPONSES；其它表通过source_ids关联。CSV基于V2全部资产ID生成，检查唯一性、覆盖、枚举、exact bytes、不重复组合和owner接受门；执行git diff --check与仅六文件提交范围检查。提交后完成GitHub远端commit、tree和六个blob/内容回读，最终回执记录于聊天及本独立仓库.git私有验证收据，避免报告自引用。

STOP：发布并回读后不继续运行、清理、恢复或自动联系owner。未解决问题保留在 QUESTIONS_PENDING_OWNER_CONFIRMATION；报告完成不表示科学授权完成。

Validation scope: 34 inherited asset IDs; 170 asset/project rows; 34 forecast rows; 34 aggregate decision rows; 32 immutable source entries. Owner-accepted cold rows: 0; science-eligible reclaim bytes: 0.
