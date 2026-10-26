# EP-L2 Tag Detach 因果根因审查

Goal: `EP_L2_TAG_DETACH_CAUSAL_ROOTCAUSE_V1`

审查日期：2026-10-26（Asia/Shanghai）。唯一综合 owner：EP-TAG-ROOTCAUSE 主 Agent。三个有界只读子任务 A/B/C 已汇总并关闭；没有科研子 Lane。

## 决定

**维持现有 T。** 将三个已接受 r5 应用条件的结果登记为“在精确生产调用域及 covered 观测域缺少真实 TagFAIL”的科学负结果。当前没有证据支持为了得到非零 detach 改保护条件、继续参数扫描或立即追加 Conv 完整应用；本轮没有启动这些工作。

**PROVEN**：当前零 detach 的直接原因首先是实际 Tag 分配失败没有出现，而不是已经存在 TagFAIL 却统一被 `reuse_seen` 排除。**LIKELY**：T 是正确性已有有限测试支持、但在已测条件下低触发的机制。这个判断不等于证明所有输入都没有机会，也不等于完整协议形式化证明。

## 身份与证据索引

Framework 审查基准：`swayhrl/accel-sim-framework@62e402872027b3e9149f668da335dfce3d92c07f`。独立分支 `hrl/ep-l2-tag-detach-rootcause-20261026-v1`；本目录是新审查产物，原 EP-MAIN 的状态文件、controller、预算及科学注册表均未改。

以下相对路径缩写只用于文字引用：

- T = `../ep_main_native_takeover_20261023_v1/`；E = T 下 `evidence/github/`。
- V = `../ep_main_vector_r5_20261023_v1/`。
- Core 行号及函数均以 GPGPU-Sim r5 的精确提交为准，见 [代码审计](PREVIEW_TO_COMMIT_CODE_AUDIT.md)。

|谱系|Core commit|main SHA256|用途|
|---|---|---|---|
|原 native/main61|`d010911e3174a3764791183cd108fe4664ba8731`|`61aad385723ac97a76cb1f32c124b286a10bc8609c9c58b1a3ef8a87413f2dd5`|原 MAIN S/F、旧 Conv T/M 控制|
|A2 r4|`9243f769620653f2a9d4df5599e9581e9dae6067`|`d99ac88d60a596b123765009420a85eea1463c01e88807a8876ae946e380fd13`|E051 SGEMM、r4 定向测试|
|E2/native r5|`1093d2629e3d6a9130ba25b9dd119b6f3e16c092`|`e511cce7d8bcd5a3ebbe6255f42ebe153547484a69c6857ab55f7a8835a2dc33`|E056 CFD、E057 DWT、native Vector 单端诊断|

三个 runtime Framework 均绑定 `9dd1ee57a83d83b56b7874bc7c716185ab52c8f7`，vendor 为 `f90c430c3a1ce8f08c09942a5a1c3a797bb2295b`。文档分支 HEAD 不是 runtime HEAD。即使 A2/r5 部分生产文件逐字相同，也不拼接 binary、source、性能配对或资格。

## 按因果支持程度排序

|顺序|级别|发现|能解释的范围|
|---|---|---|---|
|1|PROVEN|三个 r5 应用的 production `raw_tag_fail_commit=0`，relieve/detach/after-detach 接受全为0；新 Tag covered 子域最多3/16 RESERVED|三个精确已接受条件的直接断点|
|2|PROVEN|SGEMM E051 正向证书被识别，但可见 RO candidate 全为 resident hit，RO transaction=0|SGEMM 的断点在生成 RO 受害者之前|
|3|PROVEN|非 RO requester 的 rawFAIL 在 Frontend preview 被拒绝，不能到 commit relieve；已有定向反例|真实生产路径限制；不是三应用零值的原因，因为其实际 TagFAIL 为0|
|4|PROVEN / UNKNOWN|reuse_seen 成功 merge 后持久为真；Vector 存在 newTag 与 reuse 同 set，但 rawFAIL 与 reuse 的联合为0；CFD/DWT本轮复用投影未含完整 reuse 联合|不能把 reuse 边际数当应用根因；放松 guard 的安全性未证明|
|5|PROVEN / UNKNOWN|即使 detach，descriptor、directory、WAD、payload/bank、MSHR/MissQ、响应背压仍可能阻止接受或收益|路径存在已证，应用实际损失与收益大小未知|
|6|LIKELY / HYPOTHESIS|当前 T 的现实机会很窄；更长 pending 生命周期及同 slice/set 地址集中可能产生机会|未做真实窗口验证；不据此提名完整仿真|

## 三个 r5 应用的实际漏斗

这里的 head-cycle、way exposure、request、transaction 单位不同，不能互换。统计不是跨应用性能合并。

|字段|CFD E056|DWT E057|Vector native r5|
|---|---:|---:|---:|
|RO transactions|51678|9965|250118|
|RO responses|206448|39836|1000000|
|covered head-cycle|1524394|1863454|3400296|
|TVD skip，raw维度为NA|218239|335584|375000|
|covered newTag head-cycle|162681|450831|915784|
|max RESERVED covered / newTag域|4 / 3|3 / 3|3 / 3|
|newTag 且 all16 RESERVED|0|0|0|
|newTag 且 structural eligible，全应用 head-cycle|NA|NA|2385|
|实际生产 raw probe reached|1163176|1793713|831673|
|实际生产 TagFAIL / relieve / detach|0 / 0 / 0|0 / 0 / 0|0 / 0 / 0|
|新请求 accepted after detach|0|0|0|

CFD/DWT 的 copied accepted projection 只有 eligible way 暴露105076/20185，不能冒充全应用二联合。CFD UID5 物理阶段有234次 `newTag∧certifiedRO∧eligible` 的实际三联合，但也没有 TagFAIL；不能把阶段三联合当全应用二联合。来源：E/`r5CFD.json:133–262`、`r5DWT.json:138–272`、`phaseReview.md:1–9`；V/`SCIENTIFIC_CAUSE_PROJECTION.json:2–51,96–106`。

Vector 2385次联合在原 route tuple 中分为：nonRO/NOT_CONSULTED/admitted1372，RO/NOT_CONSULTED/admitted179，RO/PROD_NOT_REACHED/QUERY-denied179，nonRO/NOT_CONSULTED/denied655。这里admitted是Frontend允许commit尝试，不等于commit成功；全应用1581555次尝试实际接受1500000、拒绝81555。它们都不是 CONSULTED_FAIL。newTag 的 raw 是 MISS 或 FAIL；SECTOR_MISS 使用已有 Tag，不计新 Tag 需求。见本轮 [离线结果](OFFLINE_CHECK_RESULT.json)。

## 对七个问题的回答

### 1. 为什么三个真实 r5 应用没有 TagFAIL？

**PROVEN（直接原因）**：冻结 probe 的 all-reserved 条件没有在 covered 新 Tag head 上出现；目标 set 的新需求最多3路 RESERVED。Tag 全被 VALID/MODIFIED 占用仍可选 clean/dirty 替换。只在新地址无匹配且16路均保留 pending sector 时才返回 raw RESERVATION_FAIL。

**LIKELY（机制层解释）**：这些执行的请求分布与未返回 Tag 生命周期没有形成足够同 set 的重叠。哪一种因素主导——地址分布、实际并发、lower/return 时序或提前门禁——没有逐事务时间线的独立因果分解，仍为 **UNKNOWN**。本报告不把“没有达到16”包装成已证明的延迟/带宽根因。

### 2. 哪些负载或窗口可能有16路不可替换 pending Tag？

**PROVEN（构造）**：在同一 slice/set 保持16个不同 Tag 至少一个 sector RESERVED，未返回释放前到达第17条不同 line；另需至少一条同 set 可脱离 RO，并让 requester 通过生产门禁。已有 fixture 用单 slice、64set、128Bline、8192B stride构造这种压力。

**HYPOTHESIS（真实输入）**：同 set 冲突密集 gather、跨 warp/CTA 突发读及长延迟窗口可能符合。真实映射要按当前 partition/set hash确认，不能把fixture stride直接套到整个GPU。现有数据没有识别一个已接受真实应用的合格窗口；Conv r5未运行。

### 3. reuse_seen 与实际 TagFAIL 共现吗？

**PROVEN（Vector covered域）**：newTag 与同 set 任意 reuse 的 head-cycle 为673364、reuse way暴露706461；rawFAIL与reuse的两种联合均0。存在 reuse 但不存在压力共现。跳过域NA；CFD/DWT全量reuse联合本轮没有重解码，**UNKNOWN**。详见 [寿命审查](REUSE_SEEN_AND_SECTOR_LIFETIME.md)。

### 4. 是否保守条件排除了可正确脱离的情况？

**PROVEN**：nonRO requester 的 preview 拒绝会排除同 set eligible RO 的 relief机会；历史fixture甚至展示 direct access 可 detach 后再被directory拒绝。该结果不能证明开放 frontend 后请求可正确完成或获益。

**HYPOTHESIS**：曾经 merge、但 merged waiter已退休仍pending的事务，现有 payload/descriptor 路径看起来可能支持另行证明。**UNKNOWN**：移除sticky reuse guard、多waiter、ready-pinned或nonRO扩展的完整安全性。本轮没有实现或授权这些改版。

### 5. 真实 TagFAIL 后哪些门禁可能抵消收益？

已证路径包括：RO证书/owner/directory及query ticket；D512、同地址32 waiter、M-OFF line128与唯一性；MissQ；held frontend；same-address WAD；payload pins/pending与同bank落点；dirty victim的TVD/WAD/WB staging和quota；bank带宽、ReturnQ、ICNT和响应入队。preview会提前挡住部分情形；direct access仍可能先detach后deny。detach仅解除Tag绑定，旧payload和descriptor并未释放。因此事件链必须分别记录 `relieve→detach→new accept→retire`，不能合称成功。

### 6. 当前 T 是低触发机制还是实现缺陷？

**LIKELY：有功能证据的低触发机制，附明确路径限制。** 历史CPU fixture已在真实构造性TagFAIL下detach、保持旧payload、避免旧返回污染新Tag并完成drain。没有证据证明三应用的零值由实现坏掉造成。nonRO preview限制为 **PROVEN**；是否违背设计意图属于 **UNKNOWN**，不能抹去，也不能用它替代已证的触发缺失。

### 7. 即使触发，能预期端到端 cycles 降低吗？

**UNKNOWN，当前没有正向依据。** 同一旧main61 Conv：F E009与T-OFF WV_M E025均291469 cycles；M-OFF WV_T E026也291469。原Conv S/F292932/291469是全机制差异。原CFD79093/79157、DWT166519/167643、Vector73696/75039保留各自负结果，不能归到T。三个r5是单端诊断，没有新的同binary T-OFF配对。

detach不减少旧请求所需的lower包，也不自动增加payload、descriptor、bank或DRAM吞吐。只有被Tag等待阻塞的关键路径确被解除且未转成其它瓶颈，才可能获益；没有这样的接受证据。

## 历史正负与口径边界

E051正向证书的accepted oracle candidates2317312；可见candidate head2282704全部hit，RO事务0。covered rawFAIL0，但r4无r5 `raw_tag_fail_commit` 字段，production值保留NA。E051原FAILED是同raw解析问题，后续离线修复补充接受，未重新启动。见E/`SGEMMaccepted.json:98–128,187–241`、`SGEMMresult.md:3–19`。

旧Conv T/M控制：T/`PAPER_TABLE_SOURCE_INDEX.csv:12–13`与`ACCEPTED_RESULT_AND_PAIR_INDEX.json:6382–6491`。r4 Conv E055的接受不补写r5联合。FWT旧E011/E012未接受快照中V/dirty-forward只保留历史观察；后来恢复配对不追认旧快照。B/C额外联合fixture未接受，128B父请求分sector/merge使reuse保护持续，不能凑事件获得正结果。见E/`Breview.md:21–49,65–67`、`E2final.md:7–18`。

旧Core27/main773 Conv的TVD assertion、SIGSEGV/HOLD属于更早生产失败，不证明r5的零detach有同一原因。MAIN6/7、Btree HOLD、SGEMM独立探索、Corefe7e容量oracle始终分开。

## 本轮实际验证与交付

实际执行：单CPU、nice、30s超时的有界离线脚本；Vector 8.6MB raw SHA、三个terminal SHA与接受点绑定；r5原decoder重解码结果逐项相同；normalized全部phase/slice/global数学复核通过；独立聚合与既有projection/CSV相同；CFD/DWT仅对已批准投影重新求和。最终脚本运行5.852s，不授予新的科学接受。见 [最小验证计划](MINIMAL_DIAGNOSTIC_PLAN.md) 与 [结果](OFFLINE_CHECK_RESULT.json)。

只读阅读：生产源码、历史测试源码及历史执行receipts。未重跑CPU模拟器fixture、未编译、未运行完整应用或GPU采集、未消费epoch2预算。多sector+detach+新Tag+ICNT组合及完整preview状态snapshot仍只是计划。策略改版的最小设计与证明清单保留在 [下一决策](CLAIM_BOUNDARY_AND_NEXT_DECISION.md)，状态NOT_EXECUTED、需独立授权。

六份指定交付由主Agent统一提交，另附一个只读诊断脚本及其小型结果；无自动合并accepted simulator，无原有数据资产或protected source修改。

## 追加整合：Memory-path MLP 与瓶颈归因（2026-10-26）

追加研究 `MEMORY_PATH_MLP_AND_BOTTLENECK_ATTRIBUTION_V1` 已完成同分支只读整合，见 [访存路径主报告](GPU_MEMORY_PATH_BOTTLENECK_MAP.md)、[逐层漏斗](UPSTREAM_TO_L2_MLP_FUNNEL.csv)、[模型与counter审计](L1_ICNT_TLB_MODEL_AND_COUNTER_AUDIT.md)、[per-set分析](PER_SET_TAG_PRESSURE_CAUSAL_ANALYSIS.md)、[未执行的最小控制计划](MINIMAL_CONTROLLED_EXPERIMENT_PLAN.md)。

**不改变“维持现有T”的决定，但修正“全GPU MLP不足”这一可能误解。** Vector的RO下游独立line每slice峰63–70，B0全set tick末RESERVED总峰90–96，任一set峰均3/16；所以在各slice总峰时刻至少30–32个set同时有pending Tag。Tag压力没有集中到16路，与没有访存并发不同。

Vector最强的三条约束证据是：DRAM域服务/调度排队；L1→L2→lower有限queue反压；core ready/RAW依赖与EP局部bank/landing等待。它们可能属于同一反压链，不能按阻塞次数拆分端到端cycles。DRAM byte利用率77.8143%、scheduler-full26.4978% channel-DRAM-cycle；L2 ingress full32.1966% slice-L2-tick；L1 missq重试1240787。这些是有界模型中的观测，不是物理硬件测量或严格因果排序。

当前runtime无实际TLB/PTW时序模型；LOCAL_XBAR按packet建模，不能证明真实NoC字节链路饱和；异常Bank_Level_Parallism_Col被排除。CFD/DWT完整raw本轮本地未找到，不能用Vector补写它们的全路径瓶颈。单set到达率与Tag RESERVED寿命仍UNKNOWN，未用全GPULittle Law推失败概率。

本次追加实际只做两份既有raw约12.9MB及小metadata的SHA验证/解析，未模拟、构建、恢复、采集或触碰迁移任务。未来若获新授权，最值得的一至两个单因素控制是DRAM域服务缩放和L1 MissQ容量；只形成设计，不启动、不消费余额，不以非零detach为验收条件。T独立性能收益仍无接受证据。

## E1执行推进授权后的状态（2026-10-26）

用户已同意推进，已形成 [DRAM935执行准备包](DRAM935_EXECUTION_PACKAGE/README.md)：复用同binary850MHz接受基线，只请求新增一个935MHz端点；配置、source身份和三项非启动负控制通过。当前为 **STAGED_RESOURCE_HOLD**：本地ext4可用约33.64GiB，计入正在运行的DTC预留及现有EP规则后需要45.75GiB，缺约12.12GiB。未注册或消耗预算，未改共享native入口，未调用模拟器或help，尚无实验结果。L1 MissQ控制未叠加。

这不会改变前述科学结论；它是已授权研究的执行准备/资源阻塞记录，不能写成E1已完成或有性能收益。

## 用户存储约定及预留核算修正（2026-10-26）

大资产默认真164，174仅必要热工作集；显著I/O影响先报告，空间由用户清理。已写入本项目AGENTS.md。先前12.12GiB清理缺口来自把DTC并发池ceiling全额相加的旧保守算式，不能当实际增量需求，确定性结论撤回；详见[存储口径修正](STORAGE_ACCOUNTING_CORRECTION.md)。当前为STAGED_PENDING_RESOURCE_RECONCILIATION，仍未启动E1或修改任何peer预留。
