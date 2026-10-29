# Lane O — T：Tag 占用与释放机会（有限只读审查）

日期：2026-10-28。只读数据与源码审查；未运行仿真、CPU fixture、build、Trace 扫描或控制器；未修改 Main、生产 Core、注册表。只写本文件。路径基准：
- R = /root/data/ep_l2_full_workload_performance_20261027_v1/review/docs/ep_l2/operations
- C = /root/data/ep_l2_multiworkload_event_timeline_20261027_v1/core/src/gpgpu-sim
- P = /root/data/ep_l2_full_workload_performance_20261027_v1
已阅读 Main AGENTS.md、CURRENT_SCIENTIFIC_STATE、NEXT_SCIENTIFIC_DECISION、架构蓝图与总体架构有关 Tag/RO 路径、旧 r5/11c/current78 报告及当前源码。旧静态状态须由后来的接受证据增量修正，不能用旧“无真实 detach”概括当前全体结果。

## 1. 简明指标表

| 指标 | 严格定义、分布 | 已实现/覆盖 | 解释边界/最低补充 |
|---|---|---|---|
| 每物理 Set RESERVED 占用 R(t) | 某 L2 slice 的某 Set 中含至少一个 RESERVED sector 的 Tag way 数；不是 RESERVED sector 数。记录 area[k] 的 set-L2tick、event/tick-end peak | LIFE 全物理 Set area[17]、峰；当前78 timeline 的8个接受程序，几何64slice×32set×8way；旧11c Vector64×64×16 | area 均值按面积/实际观察ticks；各Set最大值不能相加作全GPU同时峰。VALID/MODIFIED满路可以替换，不是 all-RESERVED |
| 新地址到达与占用联合 | NEW_HEAD 在 raw MISS/rawFAIL frontend head 的重复暴露；NEW_UNIQUE 为 FIFO head UID 第一次 NEW 暴露。两者分别按实际目标 Set 的 R=k 分布 | LIFE new_head_reserved[17] / new_unique_reserved[17]；R5同head raw状态×R联合 | NEW_UNIQUE@R=W 不等于“所有曾在后续等待中碰到满路的独立请求”；必须另记 ever-full 首次事件 |
| 实际满路阻塞 | preview raw Tag RESERVATION_FAIL、frontend拒绝、actual initial ft_access TagFAIL、relieve、detach分别计数 | R4/R5/LIFE/RO总结都有分层挂钩；current78 Conv/CFD证实 preview 与 actual 不同人口 | 阻塞检查是 retry/exposure，不能作独立请求或GPU损失cycles；B0 TAG_SET_PENDING不是生产Tag失败 |
| 等待时间 | 现有 WAIT_COUNT/SUM/MAX：first NEW→commit 的 L2ticks，仅已完成匹配UID；需要均值、log2分布、censor | LIFE已有总等待 count/sum/max，无该等待直方图 | 不是 Tag-only 延迟；可同时受WAD/WB/Bank等阻塞。新增 unique ever-full、累计真实Tag拒绝tick、first-full→commit/退出、completed/right-censored |
| Tag 预约寿命 | 预约进入→退出；NEW、RE-reservation、左/右censored分开；33-bin log2与sum/max | LIFE per-set NEW/RE histogram、面积守恒、incarnation/touch已实现 | 0tick多数不能概括所有事务均短；closed mean不代表censored完整寿命；Tag episode不等于一条RO |
| 旧RO占Tag且别址需进 | 同head、同Set、NEW ∧ R=W ∧ attached RO ∧ !reuse_seen ∧ required-not-ready；最好区分结构资格与策略开关 | LIFE缓存pending/eligible数量及各NEW边际、R4/R5有covered头联合部分；未有无歧义全覆盖该三重联合 | NEW_WITH_PENDING与NEW_WITH_ELIGIBLE分开计数不能相乘；必须按同次事件新增联合。当前eligible含T开关，见下面 |
| 释放机会与实际释放 | structural-candidate、policy-can-detach、preview consulted/rewrite、actual relieve/detach、new admitted、旧ROretire分别统计 | 当前RO summarizes实际detached；R4有完整漏斗，CPU构造正确性通过 | detach>0不等于独立T收益；S中RO/T为N/A，optional observer关闭为NOT_COLLECTED，不能填0 |

程序特征：地址流、首次独立到达、同址重用/证书只读域。机制运行结果：R(t)、RO准入/merge、预约寿命、排队时长、策略资格、detach。应并列呈现，不能把后者声称为机制无关程序属性。

## 2. 当前可靠证据与 Observation 范围

### A. 当前78 timeline 多程序：已证实真实 Tag 压力高度异质

执行 Core78f4b59e865b136eede74df74c44c210f5b4ca04；Framework9dd1ee57a83d83b56b7874bc7c716185ab52c8f7；ELF78d4e96bb79c776e27146bcf168d7c70cf3897ef9cb84d837d8974fec4c91b8a。统一64slice×32set×8way、dram_latency100；完整 declared Trace commandlist，不宣称 capture completeness 或数值输出已知。

| 接受程序/模式 | cycles | event/tick peak | first-unique NEW@R8 | preview失败head观察 | actual initial TagFAIL | T适用性 |
|---|---:|---:|---:|---:|---:|---|
| Vector F OFF/ON | 77237/77237 | 7/6 | 0 | 0 | 0 | 当前F正资格，detach0 |
| Conv S | 331234 | 8/8 | 289 / 1503281 NEW | 42717 | 0 | S：N/A |
| CFD S | 84851 | 8/8 | 1 / 171765 NEW | 11 | 0 | S：N/A |
| Gaussian S | 33800 | 0/0 | 0 | 0 | 0 | S：N/A |
| SAD S | 120840 | 6/5 | 0 | 0 | 0 | S：N/A |
| SGEMM S | 353921 | 5/5 | 0 | 0 | 0 | S：N/A |
| ATAX S | 3001729 | 3/3 | 0 | 0 | 0 | S：N/A |
| GESUMMV S | 3299323 | 4/4 | 0 | 0 | 0 | S：N/A |

Conv的42717与CFD的11是同head真实生产preview的Tag-array失败，全被Frontend admission拒绝，故其后actual ft_access初始probe失败计数为0。不是缺S hook，也不是“无Tag压力”。Conv有204个物理Set出现head@R8；area_R8=202478 set-L2ticks，不能称202478 GPU stall cycles。289仅统计first NEW恰在R8，晚些才遇满路的请求人口未知。

Conv单个捕获UID在CORE6903–7108有206次R8/Frontend拒绝；末端right-censored，仅为有偏示例，无最终接受/等待完整寿命。R4例子只有global64例，丢弃42653，未截断全局R4/R5/LIFE计数。

出处：R/ep_multiworkload_event_timeline_20261027_v1/{FINAL_SCIENTIFIC_REPORT.md,CONV_S_PRESSURE_TO_PRODUCTION_AUDIT.md,WORKLOAD_PRESSURE_AND_PERFORMANCE.csv,NEW_RESERVED_AND_TIME_OCCUPANCY_DISTRIBUTIONS.csv,TAG_PREVIEW_TO_COMMIT_FUNNEL.csv,CONV_S_R8_PER_SET.csv}。Conv接受UUID132559ec-249d-4bb8-b867-92b23050ed3d；rawSHA ddf5fd9d0588c6c6a9a0635194135c5ee26d84fa24f24d78602ecbab32b8aa9c。

排除：FWT未启动（格式容量HOLD），BICG未接受，DWT资源包络失格；不能以保存的诊断数回填正式接受人口。Gaussian确有L2访问31次全hit，与memcpy预热/极小输入相容，不能称无访存或证明单一预热因果。ATAX/ GES的16CTA/kernel并行度静态上界有证据，但不足单因解释低占用。

### B. 最新 Source78 Vector32×4：真实生产 detach 已出现

R/ep_full_workload_performance_20261027_v1/SMALL_G_VECTOR_MATCHED_RESULTS_V2.json 与 EXPERIMENT_RESULTS_SUBMISSION_20261028_V1.md：
- 32×8：S77184、F77237，F detached0。
- 16×8：S76585、F76156，F detached0。
- 32×4：S75484、F75583，F detached27；F比S慢99cycles。
三对同Source78/input、匹配geometry；不是T独立因果对照。全机制F慢于S不证明T无益，detached27也不证明T有净收益。

正点：P/cases/EP_PERF_VECTOR4M_F_G32_W4_V1/run/23cd91ed-ff51-4963-a16c-7488cd3d0849/ACCEPTED_POINT.json，SHA56fedb8b8726dfb6e755f2ce3ddc430185003fbb48e82a18dc6c9897d90da3a9；input ddf26d4f6b4b672de3c5f6d1ab633cc44d3d9ef8023b87ae9a10760f3f4057dc。其不可变初始point的archive_status仍写PENDING，闭合由control/ARCHIVE_RECEIPT.json独立证明：TRUE164_RESULT_SHA_AND_TWO_NATIVE_TARGET_RESTORES_PASS，archiveSHAe2420d1cbac03c3e432bde8d5db7c401f284ee49821a2c1b10b8f39bd89c9d5a，FIRST/INDEPENDENT各22文件全SHA恢复。没有修改原point。

V2明确保留早期V1错误：V1手写“全三点0”与自己的逐行27冲突，不能引用其结论。此点optional Tag-pressure/lifetime stats absent时，production TagFAIL和寿命机会为UNKNOWN；RO summary实际27是可靠独立证据。不能为补细节立即重跑。

### B2. 当前Source78 Conv缩容的真实Detach正例（V1R1新增）

Lane O自身冻结的 `coverage_snapshot/RUN_STATUS.csv` 和 `MATCHED_PERFORMANCE.csv` 已含以下接受点，不能因原审查仅列Vector而遗漏。

| Conv同输入 `438eefd6` | F实际RO detach | 匹配S cycles | F cycles | S/F |
|---|---:|---:|---:|---:|
| 16 Set×8 Way | **237** | 360,380 | 367,152 | 0.981555 |
| 32 Set×4 Way | **1,141** | 395,820 | 425,074 | 0.931179 |

两组均为Core78/ELF78d4、同一输入与几何下的完整S/F正式接受结果；不同配置间不可拼成T的因果比较。这里直接引用已接受真实detach，不将optional Tag lifetime/详细TagFAIL缺失补0。**Detach次数增多并未带来更快的F，但还不能判断T自身是正收益还是负收益**：必须在同一Source/ELF/背景下完成F−T/F后才有独立贡献。应保留Conv 16×8和32×4作为后续低成本T候选对照，不再单纯追求更多detach。

### C. 历史谱系保留为独立负证据

- r5/E057 Core1093d262…/e511 ELF：CFD RO51678，covered Rmax4/16（NEW子集3）；DWT RO9965，Rmax3/16；Vector RO250118，covered NEW Rmax3/16，生产TagFAIL/relieve/detach0。TVDskip保持未覆盖NA。旧r5不可与current78拼性能pair。
- 11c02df…/8d55 ELF Vector OFF/ON：75039cycles，375000unique NEW，event峰4/16、tick峰3/16；85set瞬时4但area_R4=0；500000/750121 episode为0tick，250000正寿命NEW均值1141.591732 L2ticks。全部4096Set NEW91–93，是地址分散/有限聚集的真实观察。RO总时间均值1142.208598，其中issued-notready暴露72.0773%，response-only0.091898%；不是纯DRAM时延或GPU瓶颈份额。出处R/ep_tag_reservation_lifetime_20261026_v1/{FINAL_STATUS_AND_RECEIPT.md,UPSTREAM_DOWNSTREAM_TEMPORAL_JOIN.md}。
- 较早容量Goal的四几何TagFAIL/detach0与条件T-OFF未执行，只是那个Goal人口，不能覆盖后来Source78 G32W4的27。CPU满路ON/OFF通过证明构造性协议正确性，不证明真实workload收益。

## 3. 精确源码口径

所有下列行号为C的实际Core78f4b59：
- gpu-cache.cc:365–452：Tag probe按sector状态；all-reserved才无可替换way，dirty有fallback。
- l2cache.cc:1474–1495：同一cached snapshot/plan进入R4、LIFE；1551–1593只有admit才access。
- gpu-cache.cc:2796–2823：common/S preview；ep-l2-ft-cache.inc:300–339：actual初始probe327/diagnostic328，RO guard只控制relieve338。
- ep-l2-reservation-lifetime.h:135–140 accumulate面积；episode_close:166起维护NEW/RE/censor。frontend:264–284仅first NEW UID；commit_new:291–300的WAIT是firstNEW→commit。
- 同文件ro_update:228–251缓存eligible/pending；NEW_PENDING_SECTORS_SUM、NEW_CAN_DETACH_SUM及NEW_WITH_PENDING/ELIGIBLE均独立边际，不是三重联合。
- ep-l2-ro-runtime.inc:240–257在目标Set寻找live可detach；preview:273–279仅rawFAIL且可detach才重写MISS。
- ep-l2-ro-transactions.h:211–213 can_detach = feature.tag_detach && attached && !reuse_seen && (required & ~ready)。merge把reuse_seen置真且即使waiter退休也保守保留；detach核generation/payload/Tag握手后仅解除Tag绑定，事务仍完成。
- 同文件:365 observer eligible同样含feature.tag_detach。因此T-OFF eligible=0是策略关闭，不是结构机会为0。未来必须分别记录结构资格（不含T位）与策略资格，不能直接拿ON/OFF的eligible比较程序属性。
- 当前LIFE支持32/64set×8/16way，受固定容量限制；不能认为4way点有LIFE覆盖，不能在生产直接开启无资格几何。

## 4. 最小新增采集：只给 Main 的候选设计，不执行

优先级0：在已有接受小JSON/CSV上做一次有界统一schema合并。按input、source/ELF、geometry、mode、observer、接受状态键控；独立保存0、N/A、disabled/uncovered、unknown、not accepted。现有177点快照不是177个独立程序，也不是全都含LIFE。先复用RO summaries/R4/R5/LIFE终端汇总；不重复Trace、不扫描raw正文求不存在字段。

优先级1：如Main下一次既定完整采集可携带，只加被动计数（独立候选分支）：
1. 每slice当前FIFO-head保存UID、firstNEW tick、firstTagFail tick、累计TagDenied tick、everFull、everStructuralEligible，离队时清除；保持head/instruction/kernel定义，记录退出/censor。分别输出所有独立NEW、ever-full unique、重复preview拒绝检查数，不混成一个分母。
2. 直接在已有snapshot/生产判定site累计 NEW或TagFAIL ∧ R=W ∧ structural candidate；再分policy enabled、preview consulted、rewrite、admit。无新Tag probe或directory/bank查找；既有RO mutation更新cached structural count，避免每head扫way。
3. 两个33-bin log2：完成请求累计Tag拒绝tick与first-full→commit；另记sum/max/count/right-censored。并行给firstNEW→commit，明确后者包含其它阻塞。L2tick与COREtick各自标签，零tick独立bin。
4. 可选按Set只加ever-full unique/Tag-denied-tick两个计数，沿用现有完整area与NEW分布；不再扩逐请求或逐窗口记录。
5. 输出run-end或固定window个数、固定per-slice聚合，按实际序列化字节预估；避免按kernel重打全部旧212/R4/R5导致FWT格式HOLD。候选新增状态目标<128KiB（64slice FIFO状态+两个33bin+少量联合hist/计数；可选perSet另约32KiB–64KiB），新增终端文本目标<128KiB。这是设计上界，未编译测量；实现后须静态sizeof/serializer上界与CPU控制验证，不能宣称已达标。

建议复用现有full采集点：保留default几何所有workload的0与正现象；先Conv、Vector默认及已有32×4正点，CFD次级，SAD/SGEMM/ATAX/GES/Gaussian负对照。不为追非零继续缩Tag/加延迟；不改变Main正在跑的规格。若历史小汇总能满足，不新增完整运行。

只有需要回答T独立收益时，再由Main单独安排同ELF/geometry/input/background/observer的F与F−T；本Lane阶段不启动。该因果实验不是当前workload characterization的前置。Source78 G32W4是已知真实detach的可提名母点，Conv当前S满路是候选机会点，但其current F结构联合仍需证据，不能历史RO与当前S跨条件拼接。

## 5. 可直接用于论文的草案

已证实：
1. “Tag需求与保留占用须联合度量。相同32×8观察配置下，Conv与CFD存在同Set满路新地址需求，分别289和1个first-unique到达；其42717与11次preview失败不会进入actual-access失败人口，故后者0不能排除真实Tag压力。”
2. “工作负载间预约压力差异显著；观察到的低峰和低NEW-at-high-occupancy均保留为负证据。单个全局峰不能概括需求到达时机会。”
3. “真实Vector4M在32×4出现27次Tag detach；Conv在16×8和32×4分别出现237和1,141次。对应完整F均慢于匹配S。触发事实、结构释放机会及T自身的独立性能收益分属不同证据层，不能互相替代。”
4. “Vector64×16的预约寿命呈0tick大量短episode与约1142tick的正寿命群体并存，仍没有满路到达。平均寿命/单独事务数不足预测释放机会。”

待验证：
- 同Set旧RO占Tag与独立新地址满路需求的结构联合在多workload中是否常见，以及出现于哪些程序阶段。
- 观察的Tag拒绝是否覆盖大量独立请求，还是少数请求长时间重复等待；目前first-NEW@R8不是完整ever-full人口。
- 在同背景释放这些Tag能否减少拒绝等待/改善端到端cycles；不预设正收益。
- 高RO merge/reuse_seen对结构候选窗口有何实际限制：需同事件联合，不从merges或总RO比例推算。

不成立/不得作结论：
- “所有真实workload均无Tag压力/无detach”：被Conv/CFD preview压力及Vector32×4 detach27直接否定。
- “actual TagFAIL0 ⇒无满路等待”；“R=W的面积就是GPU stall cycles”；“S中RO eligible0说明无只读机会”。
- “detach27证明T加速”或“F比S慢证明T必然无益”；均无独立T控制。
- 将旧r5/11c/current78、默认与缩容、S和F、只读证书域和runtime transaction域拼成同一特征样本。
