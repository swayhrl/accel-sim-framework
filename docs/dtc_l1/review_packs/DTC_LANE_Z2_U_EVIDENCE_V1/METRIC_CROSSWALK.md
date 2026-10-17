# U/T → Z typed metric crosswalk

Z V1固定 `ccf208c723f44387160c0edfe9e4d56855dfbafd`，78个typed定义、2790行旧表和413个校验结果全部逐blob保留。本包使用其中48个指标生成 `U_T_TYPED_EVIDENCE.tsv`；未重定义V1字段、未覆盖V1缺失值。全部字段别名、单位和跨路径资格见 `METRIC_CROSSWALK.tsv`；provenance/status/cohort等列是证据元数据，不是新增性能指标。

固定来源：U `16e56912cfd02f2311a1603a29415dee829fd495` 的完整LATEST_REPORT、FULL_MATRIX、STRICT_AUDIT、FINAL_CONTRACT_AUDIT、terminal机制与可比性证据；T `f520a445436b57c0a0f2494fb858a1636f04d2bc` 的已完成发现包；V `26abd496417d9392245052e54fbd9ba27c6ffd96` 的语义合同。仅读取不可变Git blob，源路径/commit/bytes/SHA封存在 `SOURCE_BLOBS_SHA256.tsv`；snapshot不代表本轮重读raw或重做原strict。U报告中的历史后台说明仍是历史文本，本轮不探测任何PID。

| terminal字段 / 别名 | Z V1 metric id | 单位与分母 | 同路径 / 跨C+ |
|---|---|---|---|
| cycles | cycles | whole-run GPU core-cycles / 1 | 相同完整输入ROI可比；不是wall time |
| active_instructions | active_thread_instructions | active-thread instructions / 1 | 同输入有序scope检查；不是warp数 |
| accepted_128b_reference_count | accepted_reference_count | accepted logical128B refs，D=ready+pending+new=completion_dependency_count | 只在有限DTC路径比较；C+统一DTC分母UNAVAILABLE |
| ready/pending/new_reference_outcomes | ready_hit_events / pending_merge_events / cacheable_new_line_requests | accepted128B reference outcomes / 1；fraction除D，不含失败retry | 不能和C+ coalesced HIT/HIT_RESERVED拼接统一命中率 |
| dtc_lower_created | lower_created | 新建下层request / 1 | DTC creation边界；C+同名placeholder不赋值；不等于successful injection或唯一地址 |
| gpgpu_n_mem_read/write_global | global_read/write_injected | 成功注入mem_fetch packets / 1；若归一化用本run指令数 | U公开comparator含共同ICNT成功边界，可跨C+计数；失败inject retry不能相加。T选择表未发布则UNAVAILABLE |
| DTC_SERVICE_V1_samples | service_samples | 64SM×whole-run core-cycle，含idle/gated/tail | finite路径；C+无同定义样本字段 |
| pib/physical_integral | service_pib/physical_integral | entry×cycle / line128B×cycle；均值除samples | physical包含不可查旧allocation，不能倒推可查mapping数；不是active-only平均 |
| ready_to_collect / collection / wb_wait / fully_ready_to_complete sums | service_*；mean_ready_to_collect / mean_collect / mean_post_collect_WB / mean_ready_to_complete | 原sum为cacheable-warp×core-cycle；均值除service_retired | post-ready条件区间，会跨指令重叠；C+无统一区间，不能做GPU周期因果分摊 |
| map_loss_to_free_sum/count、mean_completed_map_loss_to_free | service_map_loss_to_free_sum/count、mean_map_loss_to_free | core-cycle和completed allocation intervals；均值除count | 排除终端仍映射/未释放者，0cycle事件合法；均值0不等于从未失去映射；count缺失照报UNAVAILABLE |
| L2_read_* / requested_payload | 同名V1字段 | 32B sector；TOTAL=HIT+HIT_RESERVED+MISS+SECTOR_MISS；payload=TOTAL×32B | U已发布same-path/controller/stream/atom证据支持跨C+；MSHR_HIT不二次相加，RESERVATION_FAIL是retry事件，不加入成功access分母 |
| DRAM_n_rd/n_rd_L2_A/n_write/n_wr_bk | 同名V1字段 | 每controller最后issued-command tuple求和；atom32B | U同定义可跨C+；read bytes=(n_rd+n_rd_L2_A)×32，write bytes=(n_write+n_wr_bk)×32；不是credits×128或NoC wire bytes |
| terminal_queryable_mappings / terminal_lost_resident_allocations / kernel_boundary_invalidated_mappings | 同名V1补充字段 | 必须有直接snapshot/event与边界定义 | 本包全部UNAVAILABLE；不从evictions/physical积分/map-loss count补造 |

所有DTC/cache/DRAM lifetime重复输出只取最终值，不把各kernel累计打印相加。U comparator的完整原序kernel cycles/指令与whole-run已核对；这里不把kernel差分升级为独立reset计数。logical line128B、sector32B与sets×ways分开；32×4/64×8分别128/512映射，物理池仍640×128B，不能说数据容量也增加4倍。

`denominator`列给出原始计数的1或fraction/均值的相应分母。T若只公开均值而缺sum/count，保留均值、写明已发布normalization或缺失count，不逆向制造整数积分；T新点可由strict中的service_metrics补充11项终值。T的L2/DRAM和成功inject在本次选择的小机制证据中缺失，因此显式UNAVAILABLE，不拿M旧baseline量补新点。U则直接使用其公开comparator的raw_scalars及controller tuple，未打开那些path所指的raw。

三种比较资格必须分开读：`WHOLE_RUN_SAME_INPUT`（周期/指令）、`U_TYPED_L2_DRAM_CPLUS_COMPARABLE`/`U_COMMON_SUCCESSFUL_INJECTION_CPLUS_COMPARABLE`（U已证共同计数边界）、`DTC_SAME_PATH_ONLY_CPLUS_UNCOMPARABLE`（ready/new/服务/占用等DTC指标）。后者即使在两边出现同名字符串，也不允许计算跨C+比率。UNAVAILABLE不填0，零分母比率为UNDEFINED_ZERO_DENOMINATOR。发现输入与holdout仍分别标cohort，不形成总体GM。

本crosswalk沿用V1计数类型与人群；K1 V2只修正未来源事件时间合同。U/T均是冻结旧模型的Tag比较，不是K1四格结果，也不提供写后数值正确性、coherence、真实面积/时序或主配置晋升资格。

V1的 `kernel_boundary_invalidated_mappings` 保留其历史字段名与UNAVAILABLE状态，不能暗中改成V2 source-request计数。未来若发布源事件观测，须独立注册request次数、实际撤销的唯一mapping、reclaim次数、source/SM/sequence/phase与reset/重复规则；每次重复idle request不等于又撤销同一映射。具体观测开关和实现字段仍待其正式合同，Z2不虚构CLI名称，也不将插桩前后cycle直接混比。
