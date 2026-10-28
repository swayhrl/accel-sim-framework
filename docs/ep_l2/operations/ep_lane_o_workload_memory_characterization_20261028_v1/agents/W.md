# Lane O — W 写回行为审查（2026-10-28）

本线只读检查 Source78、现有架构/历史证据及冻结的小型接受结果；没有仿真、构建、Core 修改、控制器或注册表写入。数值派生表为同目录 W_reference_metrics.json。其人口严格来自 coverage_snapshot/RUN_STATUS.csv 的 CLOSED_ACCEPTED + REF32x8_L100 + S/F，不把候选或运行中端点纳入。48 个端点（25 S / 23 F）覆盖25个程序；这是含未配对端点的特征人口，并非48端点共同性能比较。每行保留输入 SHA、cohort、bundle 路径和 SHA256。接受资格来自冻结 RUN_STATUS，VALIDATED_APPLICATION_BUNDLE 本身的 pending-main 状态不单独充当接受。

执行源：/root/data/ep_l2_multiworkload_event_timeline_20261027_v1/core，HEAD 78f4b59e865b136eede74df74c44c210f5b4ca04。文档根 R=/root/data/ep_l2_full_workload_performance_20261027_v1/review。已读 AGENTS、CURRENT_SCIENTIFIC_STATE、NEXT_SCIENTIFIC_DECISION、架构 WAD/WB/banking 章节、最新探索 README、W_ONLY_EXACT3_MAIN_EXECUTION、历史 B W/V 审查。旧架构是设计意图，当前实际参考为64 slice ×32set ×8way、128B line、4bank/P1、DRAM latency100；每slice1168 payload=1024+128+16静态S分区，Tag实际只覆盖256 resident line。WAD128与S WBUF16是两个不同资源；pooled组织的 WB role 不是独立16-entry WBUF。

## 精简指标表与可靠性

| 指标 | 精确定义、分母与分布 | 现有覆盖及缺口 |
|---|---|---|
| 脏替换/写回量 | wb_created 是实际 L2_WRBK packet 创建次数，已 drain 时应等于 wb_lower_accepted、wb_completed。按请求率可除 unique_requesters；脏替换占比还需所有已提交有效victim替换次数作分母，当前不能用requests或store数代替 | 48端点均闭合。wb_created不是唯一地址数，也不包括仍留resident的dirty数据；所有dirty-victim替换占比缺分母 |
| WBUF/数据暂存生命周期 | FT staging_lifetime / wb_lower_accept。S从源payload实际读出（copy-read成功）到下层FIFO接受；pooled从p.born的reservation起算；不等于DRAM完成延迟 | 现有FT SUMMARY已输出sum；小bundle模型未保留该字段。不能直接把两模式均值当同起点。缺分段log2直方图及同起点统一比较 |
| WAD生命周期 | dirty reservation→对应WB set_done；sum/count，max，按完成WB的p95。计时为gpu_sim_cycle+gpu_tot_sim_cycle（CORE全局tick），非DRAM周期 | B0应用行已有每slice整数avg、p95、max。不能平均slice p95求全GPU p95；未保留sum/count时不可精确合并均值。源码保留完整整数duration map，未来可压成有界直方图 |
| WAD占用 | tick采样occupancy分布；sum/sample_count、p95、max；full fraction应为occupancy==128的tick数/sample_count | B0已有每sliceavg/p95/max，48端点覆盖。full precheck observations不等于时间占满tick，不等于不同受阻请求 |
| WBUF占用及阻塞 | FT wb_occupancy_sum/observed_cycles；staged_max是m_ft_wb包数峰，与包含reserved WB role占用不完全相同。wbuf_full是实际进入FT路径时staging资源预检失败的重试次数 | FT已有counter，但compact bundle不保留这些FT SUMMARY字段；重试可能先在Frontend被挡，不能视作全入口受阻率。本次48个REF端点MS observer均ON，已有wb_sum/sample_cycles、wb_peak及WB_DATA_SPACE/COPY_PIPELINE/DATA_SERVICE逐reason独立请求/重复观察/first-wait分布；MS0另组为NOT_OBSERVED。不能把四个heavy optional observer OFF误读成MS observer OFF |
| 同址WB再访问 | 新独立入口请求第一次观测到其128B地址在mandatory WAD内的数 / 所有独立入口请求；另按读/写/atomic分类。重复head观测、已接受forward响应另列 | B0已有hazard_events与hazard_wait_cycles，但两个字段在同一if各加1，都是特定native precheck域重复head-tick观察。MS已有更广入口SAME_ADDRESS_WB独立首次受阻请求与first-wait直方图，可除model.unique_requesters作已观测受阻请求率；仍缺实际read/write类别与WB age。B0零不能否定MS正事件 |
| copy数据搬移 | logical_copy_reads/writes 是独立payload RAM op，分别计一次，copy_lines×128为逻辑copy字节；bank服务占比=(copy_read+copy_write)/bank_logical_ops | 48端点可得，所有25个S满足copy_read=copy_write=wb_created。F的0是组织取消copy的机制结果，不能反推程序没有脏替换 |
| Bank等待 | true_conflict_ops/logical_ops为独立bank op发生至少一次冲突的比例；true_conflict_events为所有拒绝尝试；wait_cycles为每个最终获服务op首次冲突→grant的累计tick，按bank/服务类分别统计才可归WB | B0已有全类型和每banklogical/true/wait，operation_class粗分类。WB_READOUT同时包含S copy-read和lower-WB read，RESIDENT_WRITE同时包含copy-write与其他写；缺按client的WB/copy专用wait分布。全类型bank_block不能当WB等待 |

## 可证实的实际现象

下表全为精确输入、REF S端，WAD满/同址B0是特定native precheck域64slice重复head观察之和；这不是MS全frontend覆盖；非独立请求、非GPU损失周期。p95区间是各slice p95的最小/最大，绝非合并p95。copy占比使用独立RAM操作口径。

| 程序（输入SHA前8） | WB/copy lines | copy RAM-op占比 | WAD峰 | full观察 | 同址B0观察 | WAD lifetime p95各slice区间 |
|---|---:|---:|---:|---:|---:|---|
| convolutionSeparable 438eefd6 |720834|14.44%|128|14876|0|1699–1809|
| scan cf8d1c4d |5310331|13.26%|128|457|55694|2018–2038|
| srad_v1 6ce41710 |5752820|11.25%|128|28|21589031|1745–1910|
| fastWalshTransform fc3a9062 |45703|3.61%|100|0|209836|1761–1967|
| 3MM f9f80028 |19587|0.070%|32|0|2031|653–1141|
| stencil bd0309df |1504136|11.13%|7|0|0|205–210|

- **已证实 O-W1**：存在有意义的dirty-victim copy工作量，且负载差异显著。Conv/scan/srad/stencil的S组织copy占全部独立payload RAM ops约11–14%；这证明W有可移除操作，尚不证明GPU cycles收益或主瓶颈。全机制F与S的WB创建数不同，故不能逐行相减当作同一批eviction的消除。
- **已证实 O-W2**：MS入口已有独立请求去重，写回地址依赖在Conv/srad/FWT/scan/3MM均存在。Conv的16791个独立head首次受阻请求对应3736508次观察；srad65753个对应21602967次。应保留独立率与等待长尾，不能按重复观察推断广泛性。
- **已证实 O-W3**：WB数量高不必然意味着WAD满。stencil有1504136次WB，但WAD峰7/128、同址及full观察均0；Conv/scan则真实达到128且有full预检观察。此处没有使用性能排序来挑样。
- **已证实负例**：25个S参考端点中10个WB=0：BlackScholes、dwt2d、gaussian、GESUMMV、heartwall、histogram、lud、mergeSort、particlefilter_float、transpose（各自本次SHA输入）。不能把零WB推广为程序只读、无store、其他尺寸也无W机会；memcpy预热/工作集/不flush及Tag背景均属于实验条件。
- **已证实但收益待验证**：WBUF16真实限制独立请求，scan的WB_DATA_SPACE为1737618个独立首次受阻请求、49938625次重复观察，max637ticks；Conv为49161个/max316。它们不是独占GPU stall。仍待测WB age/read-write类型及client专属bank等待，无法证明移除这些限制的GPU净收益。
- **当前不成立的推断**：以srad的21589031次hazard直接声称21589031个请求受阻；WAD峰128即WBUF16满；WB完成前重访等同可以安全forward；S/F或S/WV cycles差即可归因为copy。均应排除。

历史B证据R/docs/ep_l2/operations/ep_main_native_takeover_20261023_v1/evidence/github/Breview.md：旧FWT未接受快照178569copy、890294 WBUF重试及12489dirty-forward保留为未接受的事件见证；不可并入本次accepted表。旧SGEMM WB0也只限旧源/几何；当前精确sgemm ab4ac5dd S已测17416WB，说明跨输入/谱系概括不可靠。

### 优先采用的MS独立请求与等待证据

四个heavy optional observer OFF和MS observer是不同开关；本次48个参考端点MS均ON。默认语义必须按实际option/record核查。以下各例64slice的head_changes_without_admission=0，first-wait均resolved；每种reason对一个连续head最多计一次，原因可重叠，不能求和当独立GPU stalled cycles。B0提前return可漏掉部分同址域，因此上表的B0零仅是其窄域零，Conv不能写“没有同址访问”。

| S输入 | MS同址 distinct / observations | WB_DATA_SPACE distinct / observations | WAD_FULL distinct | WB占用时间均值 / peak |
|---|---:|---:|---:|---:|
| Conv |16791 / 3736508|49161 / 1319870|1004|2.140 /16|
| scan |390 /215979|1737618 /49938625|35|10.661 /16|
| srad_v1 |65753 /21602967|241485 /5691756|1|0.392 /16|
| FWT |830 /209836|8736 /193143|0|0.392 /16|
| 3MM |11 /2031|0 /0|0|0.000553 /6|
| stencil |0 /0|0 /0|0|0.00760 /2|

例如Conv同址受阻率=16791/5239872=0.32045%；scan为390/42763048=0.000912%。这说明较大的等待观察可以集中于很小请求子集。MS COPY_PIPELINE各例distinct等于WB/copy lines、max1tick；它反映显式copy-latch协议等待。DATA_SERVICE不专属WB，不能全部归于copy。scan DATA_SERVICE的unknown_while_unresolved=40必须保留，不能将它解释为完整因果等待。完整reason.hist_log2及sum/max已写入W_reference_metrics.json，无需新仿真获取。

## 最小新增采集方案（交EP-MAIN审查，不执行）

1. **先补投影，不加仿真**：复用已接受FT终端SUMMARY与B0应用统计，把wb_occupancy_sum/observed_cycles、staging_lifetime/lower_accept、wbuf_full、staged_max、copy_lines及closure投影成小表。优先现存parsed对象或已归档terminal摘要；若必须读raw，由Main把所需字段并入其已有单次解析，不另开重复全日志/Trace扫描。WBUF这批字段已有实现，不能标成必须加代码或重跑。
2. **现有MS数据直接复用，不重复加采集**：48个REF端点已经有reason去重、重复观察、resolved、sum/max及65-bin first-wait直方图。先投影SAME_ADDRESS_WB/WAD_FULL/WB_DATA_SPACE/COPY_PIPELINE/DATA_SERVICE及observer wb_sum/peak，主文案例head_changes_without_admission均0。后续只新增确缺的dirty_replacement_commit/all_valid_victim_replacement_commit、read/write/atomic类别和WB年龄关联；不要重做seen_reason/通用first-wait采集。已有first-wait是首次blocked→该reason首次已知clear，不是该reason累计所有间歇等待，也不是唯一/排他的GPU损失。
3. **复用已有WB record加少量时间戳**：统一起点dirty reservation，分别记录reservation→copy-read、copy-read→copy-write、packet-create→loweraccept、loweraccept→set_done；每段64-bin log2+count/sum/max，明确S/pooled不适用段。WB identity用packet pointer/UID+generation或token；WAD address只作lookup，匹配不能混用raw/normalized address。自然drain要求created=loweraccepted=completed、active0；kernel中间快照允许在途。
4. **同址访问分布**：在mandatory WAD命中时，仅对独立到达请求计count及WB age/residual completion wait log2，按read/write/atomic及WB状态（reserved/staged/inflight）分类；复用现有WAD128有界状态，每WB设置seen_read/seen_write标志并报“至少一次再访WB比例”=该类WB数/完成WB数。无需保存逐请求轨迹。
5. **Bank按现有client细分**：COPY_READ/COPY_WRITE/LOWER_WB各自logical、true-conflict-op、retry、wait sum/max/log2；利用已有pending_op首次冲突时间，不添bank请求或目录查询。占用采用状态变化时积分或已存在tick sample，输出0..16 WB occupancy直方图及WAD0..128直方图，full fraction使用time bins；统一记录sample时钟域。

建议总状态预算约每slice≤16KiB（WB/WAD已有128 bounded条目上增加2–4时间戳及位标志；若6组64-bin计数器则3KiB/slice，再加占用及分组统计）；64slice约≤1MiB新observer状态，上限需候选实测。host运行成本O(现有事件数)，不加trace正文扫描，不输出逐事件记录，应用/每kernel紧凑counter预计数十至数百KiB。复杂多维联合直方图先不做。若需代码，仅独立候选分支；使用生产fixture验证same-line sequential WB、并行WB、loweraccept/WAD完成分离、retry去重、censor与drain，再由Main按现有计划安排OFF/ON计时不干扰性验证。本线未准备或合并代码，也未启动新实验。

## 源码锚点（Core78f4，全部相对src/gpgpu-sim）

- ep-l2-ft-cache.inc:173–191：FT tick occupancy与可选MS sample；:387–448：WAD-full、WBUF-full预检和dirty reservation/birth；:466–491：S copy及p.born在source-read成功时重置；:567–595：实际WB packet绑定；:620–669：lower bank服务、loweraccept、staging release及lifetime；:702–720：FT SUMMARY各字段映射。
- gpu-cache.cc:2716–2758：WAD normalized address+UID匹配、set_done lifetime、hist及mandatory释放；gpu-cache.h:3201–3238：WAD定义、p95 nearest-rank、mandatory查询。
- l2cache.cc:1427–1430：hazard_events与hazard_wait_cycles各加1的重复观察实现；:2387–2460：B0应用avg/p95/max与WB生命周期打印。应用scope累计优先，不把kernel_shared_delta相加或拿累计WAD lifetime当kernel差分。
- gpu-cache.h:2697–2762：bank logical/retry/true-conflict-operation/denial事件与首次冲突到grant等待；:2869–2874：copy client独立操作计数。
- ep-l2-mechanism-observer.h:45–83：连续head按reason去重及unknown语义；:102–105：OFF明确DISABLED_NOT_OBSERVED。

未读任何Trace正文、未扫描巨大raw；本次读取48个小型validation bundle（现有解析结果）和有限源/文档。W_reference_metrics.json给出所有样本，不只展示正向例子。所有数字严格保留输入/源/模式背景，特征观察不充当机制净收益证明。