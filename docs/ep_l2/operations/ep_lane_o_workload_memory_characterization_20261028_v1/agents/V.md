# Lane O / V：替换与复用只读审计

日期：2026-10-28；主研究线 Main 未接管。仿真/构建/Trace正文扫描/生产代码修改均为 0。

## 证据与身份

最新全工作负载研究：`/root/data/ep_l2_full_workload_performance_20261027_v1`（下称 PERF）。使用 coverage_snapshot 中固定于 UTC 2026-10-28 10:31:56 的 RUN_STATUS.csv，不将继续运行的实验混入分母。独立读取已接受小型 VALIDATED_APPLICATION_BUNDLE.json，而非再次解析 raw.log.gz 或 Trace。

[V_ACCEPTED_REFERENCE_COUNTERS.json](V_ACCEPTED_REFERENCE_COUNTERS.json) 是可复核逐端点投影：30 个 CLOSED_ACCEPTED、REF32x8_L100 的 F/WV_ZERO_RO 点，覆盖 25 个精确输入、24 个程序（23 F + 7 WV）。读取 bundle 共 15,746,163 B；所有 30 个 bundle SHA 与 ACCEPTED_POINT.validation_ref 匹配；30 个 ARCHIVE_RECEIPT 的 SHA 与冻结 RUN_STATUS 匹配，状态均为 TRUE164_RESULT_SHA_AND_TWO_NATIVE_TARGET_RESTORES_PASS。保留绝对路径、JSON pointer、source/binary SHA。23 个 F 是单端点数，含当前尚无匹配 S 的 ATAX，不能写成 23 对；覆盖快照的 22 对/21 程序是另一分母。指标求和仅取 bundle 已终验的每 slice 末次记录，不跨 kernel 重复累加打印。

本批 Core=`78f4b59e865b136eede74df74c44c210f5b4ca04`，ELF SHA=`78d4e96bb79c776e27146bcf168d7c70cf3897ef9cb84d837d8974fec4c91b8a`。源目录 `/root/data/ep_l2_multiworkload_event_timeline_20261027_v1/core/src/gpgpu-sim`（下称 SRC）。当前 Source92 以及 main61/r4/r5 都是独立谱系；本表不向其继承计数。

历史 B 审查 `/root/data/ep_l2_main_20261023_v1/worktree/docs/ep_l2/operations/ep_main_native_takeover_20261023_v1/evidence/github/Breview.md:23-49` 的 FWT_7_21 main61 E011/E012 是 INCOMPLETE/NOT_ACCEPTED 快照，184,660 V 响应/12,489 dirty-forward 仅保留历史事件层，不冒充现有新完整端点。当前 accepted fastWalshTransform 输入 `fc3a9062...` 是另一精确输入，不能覆盖旧状态或拼接数字。旧 SGEMM 无 V 观测也不等于 0；下表现有新 sgemm 精确输入 `ab4ac5dd...` 的 0 是真实已测计数。

## 历史复用统计已经存在：必须优先复用

不能把“当前 Core78f4 PERF bundles 未保存 reuse distance”写成“项目从未测量 reuse distance”。以下是**历史审查接受/候选层**，与当前 accepted PERF 端点分开：

- `docs/ep_l2/chatgpt_handoff/MOTIVATION_FINAL_CHATGPT_REVIEW.md:3-46`（Main worktree 相对路径）：状态 DATA/SEMANTICS PASS，仍需 PACKAGING-ONLY CLOSEOUT 才能 FINAL_PASS；Core `2a6a31591bc42023e5997cca969e4b672efe0405`、Framework `02f36816f60afcff55e910cdef2b60937e691cdc`。审查已接受 final10 工作负载 provenance、reuse-distance accounting 及 Stage6 CSV，无需重跑。历史10工作负载标签为 convolutionSeparable、cfd_097k、FWT_7_21、scan、dwt2d、btree、vectorAdd_4M、spmv、sad、gemm（由该review:26-44列举）；其精确输入manifest/hash、epoch清单与当前输入映射本次尚未核验，不能仅按同名混入当前native accepted population。DATA/SEMANTICS PASS不自动等于本次Main native应用资格/数值正确性。原始 CSV/压缩包本次未在主 worktree 中找到，不应把审查约数改写成已直接核验 CSV 的精确值。
- 此历史 all-demand/128B line 的 reuse-instance CDF：<=32约68.8%（CFD）至100%（Vector），<=128约86.2%（Conv）至100%，>1024几乎零；reuse_instances/eligible_demand约0.75至0.999。分母是 reuse instances，许多可能是正常 resident hits，不能推为 V-buffer capture。
- 同一历史 real post-eviction rereference supplement：CFD约27.2%、FWT_7_21约24.8%、scan约15.2%、Conv约3.7%、DWT约1.8%、btree约1.2%；Vector4M/spmv/sad/gemm为zero/none。已有的是平均 reference-sequence/cycle gap，不是 post-eviction distinct-line stack histogram，不能据此选择容量K。旧 btree 观察的存在不解除后续 Btree 地址域 HOLD。
- `docs/ep_l2/chatgpt_handoff/STREAMING_REUSE_PREFINAL_CHATGPT_REVIEW.md:3-10,28-69`：Core `ca3e7bc0b8f61b5d7c052bcda2a91955a1e5c919`、Framework `db1c90182fad02aacbd282b67ecdc57b8e4cc365`；PASS_FOR_SCIENTIFIC_DIRECTION，FIX_REQUIRED_BEFORE_FINAL_PROMOTION，scan尚未纳入。Vector4M 与 BlackScholes 的 line reuse fraction=0.75、temporal sector reuse fraction=0、spatial-new=0.75，说明高 line reuse 可以全由32B-sector空间触达贡献。mergeSort约10.50%、transpose约15.79% sector temporal reuse，均为此 prefinal 科学方向层。
- 同一 prefinal 报告在 true temporal-sector reuse 条件下 >1024 比例：FWT约61.44%、Conv39.27%、DWT23.25%、btree19.03%、CFD18.01%、spmv9.54%。不能用先前 line histogram 的近零 tail 断言不存在远距离真实复用。该 review:139 起明确 multi-sector request 顺序产生未来 recency tie 的缺陷，仍需原有修复/最终delta证据；本次不追认 final，也不宣称已核验它的原始数据包。
- `M0B_PREFINAL_9OF10_CHATGPT_REVIEW.md` 及 ADR-008 已审查的是 old dirty payload handle 在 reassignment 后不再 live、WAD寿命、pending候选寿命/role需求；这不是访存 stack-distance。其 NO_OPPORTUNITY 只排除旧模型“提前释放旧 resident payload handle”的特定动机，不能否定后来的有限 victim data read service。

因此最小新增计划的第零步应补齐旧 MOTIVATION/STREAMING 小型 CSV、manifest、final delta 的精确保全位置与输入映射，先由 Main/存储已有索引做按名单读取，禁止为找文件全盘/巨大 Trace 扫描。如果旧 histogram 适配目标精确输入，直接用于历史观察；与当前新输入、配置、source 的覆盖差异仍列缺口。新 profiler 首先参考已审查旧实现，不能从零重复开发。

## 已实现语义及 V 指标表

128 B line / 32 B sector；必须保存精确输入、地址域、L1 配置、L2 几何、机制和观察器状态。架构参考 PERF/review/docs/ep_l2/project_spec/ARCHITECTURE_BLUEPRINT.md:75-95（Tag、descriptor、128 B Line MSHR、payload generation、WAD 真 set_done）。它是早期蓝图，实际 V 行为以以下当前源码为准。

| 指标 | 定义与分布 | 现有可靠覆盖 | 最小新增成本 |
|---|---|---|---|
| 已保留数据实际读服务 | successful response enqueue 后的 L2 requester 服务数、sector 数/bytes；按 CLEAN、WB_STAGED、WB_INFLIGHT、WB_COMPLETE 分层更有意义 | 当前 30 accepted reference 点有 read_responses、served_sector_bytes；只有 dirty_forward 这一合并分层 | 复用 existing entry 状态，增加 4 组计数；无需地址表 |
| 同址请求间隔 | 第一次进入 L2 观察边界的不同请求 UID 对同一 line 的相邻 gap_cycles 与 gap_requests；读→读/写→读分别统计 log2 直方图 | 当前 PERF未测；历史 MOTIVATION已有stack而非完整interarrival；当前 directory_queries、installs、responses 都不能代替 | 固定 hash 抽样地址，有限 last-touch 表；collision/censor/terminal 明示 |
| 真 reuse distance | 两次同 line 独立访问之间**不同其他 line 的数量**；不等于所有请求数量 | 当前 PERF未测；历史 MOTIVATION10点已有line stack，STREAMING prefinal有sector stack，不向当前输入继承；不能由 V 命中或 retention_slot_cycles 推导 | 最小计划先不强求全局精确 stack；必要时额外有限 LRU shadow，报告超容量/未见均为 censored，不能当 cold |
| 淘汰后首次再访问 | committed replacement → 下一不同请求首次 L2 到达；cycle/request gap，dirty/clean、sector overlap 分层 | 当前 PERF未测；历史 MOTIVATION有posteviction re-ref比例与平均gap；当前V服务不知年龄/距离 | 有限 sampled ghost，首次再访一次结算；容量丢失/epoch尾未再访单列 |
| 短期重复读 | 不同 read UID 对同 line 的 gap CDF，并分前一请求仍 pending / 已完成 | V 响应、RO merge 有事件见证，但全请求率和 gap 未测 | 复用 last-touch + pending M/descriptor，gap bins；不追踪逐请求日志 |
| 保留窗口与机会 | 淘汰对象年龄、首次服务年龄、未服务回收年龄；retention 的占用积分；未来容量适应度只作反事实 | 现有 clean_retention_slot_cycles、retention_slot_cycles（WB_INFLIGHT+WB_COMPLETE），总和；非存活年龄分布 | 每 retained entry 数个 timestamp/first_service 位 + histogram，接入实际 install/response/reclaim；无额外 lookup |
| 独立需求与重复等待 | 有无等待的distinct request；每reason首次block→首次known-clear，ANY项→admission；另存retry observations | mechanism_metrics.bottleneck已有distinct_requests_first_block/hist_log2；不是独占GPU stall | 优先复用UID/state；新增观测不重复调用admission / bank / lookup |

源码语义：SRC/ep-l2-tvd-directory.h:98-112 列现有 counters；177-209 install；240-262 在 lease、真实 bank 服务和 response enqueue 后 response_commit，一次成功读响应增加一次 read_responses（按 mem_fetch/L2 requester 服务，非唯一 line/程序父 load）；dirty_forward 是 begin_read 时 mandatory（WB_STAGED/WB_INFLIGHT），非“自始至终仍脏”的推断；非 dirty-forward 不能全称 clean-victim，其中可能有 WB_COMPLETE 保留数据。372-382 的 retention 是物理 slot×cycle 积分，非年龄直方图，WB_STAGED 另有 staging 字段。

SRC/ep-l2-tvd-cache.inc:81-92 首次 head 请求设置 lookup，实际查询后缓存 ticket，queries 是目录服务事件并非唯一地址；104-131 的 WB/PIN/BANK/ICNT wait 是每次 frontend 观察/尝试，不是不同请求或独占全 GPU stall。138-160 在真实 response commit 后调用 ms_observe_frontend(...accepted...)。SRC/ep-l2-tvd-directory.h:146-173、326-363 及 ep-l2-tvd-cache.inc:39-55 明确有限目录、pending/inflight 不可回收，优先回收 clean 再 WB-complete、bank-compatible reclaim；因此实际 V 命中是有限机制结果，不是 workload 固有命中率或容量 oracle。

## 当前数据可支持的观察

以下为同一 reference 背景下，30 点中代表端点的 sum(slice)；精确路径与逐点 hash 位于上述 JSON，pointer `/model/mechanism_metrics/full_mechanism_records/victim`。

| 精确程序/输入前缀/模式 | V 响应 | dirty-forward 响应 | served bytes | clean installs | dirty installs |
|---|---:|---:|---:|---:|---:|
| stencil / bd0309df / F | 4,930,616 | 20 | 157,779,712 | 875,359 | 1,501,831 |
| 3MM / f9f80028 / F | 1,147,507 | 75 | 36,720,224 | 53,946 | 16,247 |
| GEMM / 140f6ed3 / F | 586,844 | 0 | 18,779,008 | 8,433 | 10 |
| convolutionSeparable / 438eefd6 / F | 44,974 | 0 | 1,439,168 | 736,452 | 725,656 |
| scan / cf8d1c4d / F | 5,584 | 296 | 178,688 | 4,099,309 | 5,312,352 |
| fastWalshTransform / fc3a9062 / WV_ZERO_RO | 88,069 | 3,312 | 2,818,208 | 249 | 59,532 |
| GESUMMV / a953fb7d / F | 7,522 | 0 | 240,704 | 1,048,390 | 0 |
| vectorAdd4M / ddf26d4f / F | 0 | 0 | 0 | 257,421 | 117,579 |
| vectorAdd6M / efced2c3 / F | 0 | 0 | 0 | 382,587 | 179,913 |
| 2DCONV / 0ae13552 / F | 0 | 0 | 0 | 532,569 | 515,751 |
| 3DCONV / 8f268365 / F | 0 | 0 | 0 | 530,432 | 509,984 |
| sgemm / ab4ac5dd / F | 0 | 0 | 0 | 80,864 | 17,408 |

另有 ATAX(11,457)、BICG(11,072)、MVT(12,040)、heartwall(162) 的 F 实际 V 读服务，完整点表包含正、零以及 WV 点。当前分母：F 23端点=10正+13零；WV_ZERO_RO 7端点=3正（BICG11,104、GEMM609,858、fastWalshTransform88,069）+4零（2DCONV、3DCONV、particlefilter_float、transpose）。合计30端点=13正+17零，去重精确输入25，其中11输入至少一个端点V响应>0。它们不是13个不同workload，也不是13对性能样本。

`eligible V read-check / distinct-read-lookups` 未单独输出。directory_queries 包含读/写/原子路径以及无目录命中的查询，不能作“V读hit rate”分母；read_responses 是成功服务数而不是命中尝试数，正在等待/被拒绝不等于已完成响应。当前报告只给响应、安装和明确来源，不计算 responses/全L2请求、responses/queries 或 responses/installs 作为命中率。新增最小计数可在查询结果确定后，对新UID的 op=READ 且 V_LOOKUP完成分子/分母各记一次，分 MISS/READ_READY/MISSING_SECTOR/WAIT_WB；另将response enqueue作为服务完成率，分开等待重试次数。23 个 F 端点中 10 个 read_responses>0；这是此 reference accepted 单端点集合的描述，非全 workload 普遍率、非全研究最终覆盖率。`responses / installs` 不能称 hit rate；同一安装对象能服务多次，安装/请求/地址分母各异。不能把 responses 转成同数独立避免 DRAM 请求，sector/merge/动态调度会改变对应关系。

可在论文使用的表述必须分证据层：历史 O-V0a（MOTIVATION DATA/SEMANTICS PASS）表明 line 局部性强但不能预测 victim capture；历史 O-V0b（STREAMING prefinal方向通过）表明空间sector触达与真实sector时间复用必须分开，远距离 temporal reuse仍可存在。以下 O-V1—4 是当前 accepted PERF端点：

- **O-V1 / 已证实，机制运行条件性**：在数个真实 trace-defined 已接受应用中，被替换而保留的数据仍被实际读取；stencil、3MM、GEMM 是强事件见证，Conv、ATAX/BICG/MVT/GESUMMV/heartwall 是较稀疏见证。不能附加“短距离”“关键路径收益”“全程序固定比例”。
- **O-V2 / 已证实，保留负例**：大量 clean/dirty 安装不保证后续 V 读服务。vector4M/6M、2DCONV/3DCONV、sgemm 的上述精确背景下 read_responses=0；这些点仍占保留资源。它不证明“程序完全无复用”，可能已在 resident 层命中或越过有限保留窗口。
- **O-V3 / 已证实，W/V 交叉事件**：当前 accepted fastWalshTransform WV 有 3,312、scan F 有 296 次 mandatory-WB 背景的真实读响应；3MM/stencil 也有较少计数。说明 writeback 生命周期和读取需求确有交叠，不能由此断言需要长期 dirty retention 或性能净收益。
- **O-V4 / 已证实，分层干净样本**：GESUMMV F dirty_installs=0 且 read_responses=7,522，证明其现有目录服务来自 clean 安装域；大多数其它非 dirty-forward 仍混合 CLEAN 与 WB_COMPLETE，需新增极小状态分层才能精确区分。

待验证（当前新PERF输入/背景，历史已知统计见上）：post-eviction next-touch 有多短？多少请求落在 WB pending/inflight/completed 窗口？多少独立 evicted line 被再读、多少反复读取？有限目录下多少潜在可复用对象被提前回收？保留对象的年龄和容量是否适配？不能通过已有 S/F 速度反推这些答案。

不成立的现有推导（保留为否定结论）：V 响应高 ⇒ 平均复用距离短；dirty install 多 ⇒ dirty-forward 多；非 dirty-forward 都是 clean；slot_cycles/installs ⇒ 平均可复用寿命；directory_queries 或 wait retries ⇒ 唯一请求；F-S lower流量差 ⇒ V 独立节省；无 V 响应 ⇒ 程序无复用。

## 面向全 workload 的最小追加计划（候选，未实施/未启动）

1. **零仿真优先**：将这 30 点原有 V 计数与 coverage 的 S/ref 分母对齐；新接受结果到达时由 Main 做一次增量 bundle 投影。既有 counter 足以记录 V actual service、dirty-forward、占用积分和重复等待边界；不重扫 Trace，不重解析所有巨型 raw，不为缺失 histogram 立刻补跑。
2. **极小 always-off 候选模块**：在独立工程分支预备 V_SERVICE_KIND（CLEAN/STAGED/INFLIGHT/COMPLETE 四类响应计数）、V_ENTRY_AGE（install→first successful service、install→reclaim，0/unserved 单列）；64-bin log2 或 32-bin saturating histogram，输出 per-slice terminal/per-kernel phase + epoch 总结，记录 overflow 和 completed/censored。对实际 selected entry 读现有 born/generation，无附加功能性 CAM、无额外 admission/reclaim 调用。每个 retained entry 增 1 first_service 位/少数时间戳，可先用已有 born；目录最大 128/slice。纯统计新增数据量约 KB 至百 KB，不能当作硬件资源更改。
3. **最小 workload arrival 采样**：固定 hash(line) 抽样，例如 1/1024；同一表保存32B sector mask/prestate，分 spatial-new-sector 与 repeated-same-sector，禁止 line gap直接称 temporal sector reuse；每 slice 64-entry last-touch 表，记录 line、last first-arrival cycle、all-distinct-request sequence、前次 R/W、同址 pending 状态。观察边界在新 mem_fetch 首次进入 L2 队列处，retry 不更新序号、不重计；同 UID 的 sector 展开与程序父请求分层须明确。输出 same-line gap_cycles / gap_requests，R→R/W→R/previous-live 分层。64 slices × 64 entries × ~40 B≈160 KiB host metadata，固定容量、碰撞计数和未观测标记；它是所见 L2 需求流，受 L1 filtering/调度背景影响，不能称输入程序固有分布。cycle gap 更是机制相关。
4. **淘汰后首次触达**：共享上述固定采样，实际 commit replacement 时在有限 ghost 记 line+generation、evict cycle/sequence、dirty/valid mask；下一不同 request 首次到达一次结算 age与sector overlap。另存 overwritten/terminal-censored，不能把未再见一概当 never-reused。可限 128 ghosts/slice（约 0.3-0.5 MiB）；更新 O(1) expected，不保存逐请求日志。
5. **真 stack distance 只在必要时追加**：gap_requests 不等于 distinct-address reuse distance。若论文必须需要后者，独立可选 bounded shadow LRU（优先沿用既有 exact-through1024 语义，必要时例如每 slice4096条）对固定完整 L2 流更新并计算 capped stack rank，地址表+LRU/Fenwick 树估计数 MB至十余 MB/模型、O(log4096)/request；reuse 距离≤cap可精确，超cap/未见为 censored。先 CPU fixture 衡量开销，不把地址 hash 稀疏子流的 stack distance 标成全流精确值。此项不是最小第一轮必需。
6. **由 Main 协调后续覆盖**：首次接入只做有限 CPU fixture（去重、hist边界、sector/generation、overflow、censor、观察器开关非干扰）；若后续批准正式采集，可随 Main 下一次已安排相同 baseline S 模型被动采集全部可运行精确输入，一次提供 W/V/M/T 所需 counters，避免另开 V 扫描。机制 F 的 entry-age/state 若已无其它必要运行，仅先列缺口，不追加整轮仿真。优先检查代表：stencil/3MM/GEMM、fastWalshTransform/scan、vector4M/6M/2DCONV/sgemm；最终有资格的全输入表仍保留正、零、缺失与 HOLD，不按速度筛选。

本阶段无需实现代码便可形成可审查规划。V 独立净性能因果控制（同 binary/背景 V-OFF）属于后续结构验证，不能取代本阶段 workload 现象采集，也不在本阶段启动。
