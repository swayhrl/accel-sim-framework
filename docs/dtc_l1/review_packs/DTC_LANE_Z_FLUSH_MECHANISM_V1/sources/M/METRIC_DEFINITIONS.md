# 指标定义与可比较域

逐字段机器可读定义见METRIC_DEFINITIONS.tsv：覆盖主表全部69列，包含typed units、logging stage、numerator/denominator、指令/地址范围、retry、累计范围、comparison和source location。精确finite/traditional源码SHA见SOURCE_SHA256.tsv；每个run的原字段名、原值、stdout SHA、完整effective options和CSV终端值见COUNTER_EVIDENCE.json、INPUT_RUN_IDENTITIES.json。字段不存在保留UNAVAILABLE；存在但单位/路径不同列为UNCOMPARABLE。0只用于原始日志明确打印0的项。

COUNTER_EVIDENCE的raw_scalars是原样数值备查区，未在主表/定义中注册的字段不作单位或科学解释；identity里的通用raw_counter_units简写不能覆盖这些逐字段定义。特别是gpu_sim_*是per-kernel、gpu_tot_*是累计值，配置/字节等原数字也不能默认为event。保留提取快照，不在DWT2D核对后改写已封存的主数据。

| 指标域 | 计数位置、单位和分母 | 比较限制 |
|---|---|---|
| 完整cycles/指令 | gpu_print_stat的末次gpu_tot_sim_cycle/insn；各kernel的gpu_sim_insn与已验body逐项核对 | 同一个原trace及完整ROI；不是steady-only或native |
| ready-hit / pending-merge / new allocation | common.h::IO/OO access成功128B logical reference：分别查询到ready物理分配、附着pending映射、新分配 | 成功ref三项之和等于completion_dependency_count；不是全部Tag尝试或warp指令数 |
| conventional ready/pending | gpu-cache.cc cache_stats按GLOBAL_ACC_R的HIT、HIT_RESERVED、MISS等计数；实际值另存CONVENTIONAL_LOOKUP_CONTEXT.tsv | C+存在这些字段，不能伪称完全无hit数据；其coalesced cache访问粒度不同于DTC去重128B reference，跨族UNCOMPARABLE |
| Tag grant/conflict | try_serve_tag配额检查及成功grant；失败allocation也可能已消费一次Tag service | 包含重试；IO打印，OO的同义全局压力字段未打印；BASE统计路径不同 |
| PIB/MSHR/pool拒绝 | BASE admit、cache MSHR容量/merge slot失败、IO no-free-physical/allocation-width失败 | 事件数可重试，不是cycle-deduplicated停顿。传统MSHR按全部access type汇总；不与DTC main-load路径混比 |
| successful lower reads | simt_core_cluster::icnt_inject_request_packet调用update_icnt_stats，GLOBAL_ACC_R一次成功注入一个mem_fetch | 比creation credit更接近共同边界；九臂均独立满足lower acquire=release=GLOBAL_ACC_R injection，且L2 GLOBAL_ACC_R TOTAL_ACCESS=4×injection |
| L2读payload | FINAL GLOBAL_ACC_R TOTAL_ACCESS是32B L2 sector访问；requested payload=TOTAL_ACCESS×32 | 本输入中N型普通L1的atom128及finite whole-line128均分裂成四sector；这是到L2的需求payload，不是DRAM流量或NoC wire/header字节 |
| L2 hit/miss/retry | GLOBAL_ACC_R按HIT、HIT_RESERVED、MISS、SECTOR_MISS等结果统计 | TOTAL_ACCESS=HIT+HIT_RESERVED+MISS+SECTOR_MISS。MSHR_HIT是补充桶，不再次相加；RESERVATION_FAIL是重试事件，不计入成功access分母 |
| DRAM实际传输 | dram.cc read/write命令成功issue增加n_rd/n_write；L2 allocation读、writeback写分别计数 | 取末次每controller tuple，不能累加重复Read别名或跨kernel累计快照；读字节=(n_rd+n_rd_L2_A)×32，写字节=(n_write+n_wr_bk)×32 |
| ordinary L1D/side path | L1D_total_cache_*只统计普通cache路径；finite主load不进入该路径 | finite这里主要是store side-array；其miss率不是DTC logical Tag miss率；全L2读写总量也不能当纯读量 |
| dynamic/ordinary warp指令 | ldst_unit::issue分类动态memory warp指令；M4 admits/observation retire统计ordinary sidecar | 与active-lane指令、sector或128B ref不同。DTC11服务retired仅cacheable load，非全部ordinary指令 |

DRAM atom以冻结gpu-sim.h:296–298的 `BL*busW*gpu_n_mem_per_ctrlr` 计算，现场配置为2×16×1=32B。CSV `dram_reads_per_mc_*` / writes在mem_latency_stat.cc:283–294按实际进入DRAM的请求sector数累计；终端已排空时九臂均与DRAM命令tuple逐项总和相等。这是交叉核对，不把采样sector请求与中途已发命令当同一个瞬时量。各臂数据传输量包含所有实际DRAM访问类型，不是按PC归属的纯cacheable load量。既有perf CSV没有任何DTC字段，不能从CSV补出未打印的OO拒绝或PIB-full。

统计范围：主表采用最终累计值，不相加kernel快照。GEMM一kernel；BICG两kernel、相同stream，末次cache/DRAM累计值单独取一次；原代码在对象创建初始化这些计数，未在两kernel间重置。解析器另核完整有序kernel和每kernel活动指令数。nine-run CSV均有覆盖终端的最后一行（gpu_tot component+gpu_sim component与stdout最终值相等）。所有scope和controller单调性检查保存在COUNTER_EVIDENCE.json。

11个finite服务字段由shader.cc:2105–2127采集、5727–5740汇总；不是历史的frontend-ready计数：

| raw字段后缀 | typed unit与分母 |
|---|---|
| samples | SM-core-cycle样本；精确64×full GPU cycles，含idle、clock-gated和tail |
| pib_integral | 所有PIB项（含ordinary）占用的entry×core-cycle；除samples得全64SM全周期平均 |
| physical_integral | 所有已分配物理行的line×core-cycle；除samples，包括丢失Tag映射、暂不可查询的物理行 |
| retired | cacheable load warp指令成功退休数 |
| collected_sectors | 每cacheable指令所需sector union的32B collection工作量，不是每次fill的四sector流量 |
| fully_ready_to_complete_sum | 所有ref已admit且数据ready后的观察时刻，到成功writeback/retirement的core-cycle间隔和；除retired |
| ready_to_collect_sum | 上述ready时刻到首次成功collection的等待间隔和；除retired，可包含FIFO/selection/port等待，不能专指某一个原因 |
| collection_cycles | 从首个到最后一个collection服务cycle，含端点的间隔和；除retired；可以包含端口间隙 |
| wb_wait | 最后collection完成之后至成功退休的等待和，源码扣除规定的一cycle边界；除retired |
| map_loss_to_free_sum | 失去逻辑映射到释放物理allocation的完成间隔和；除对应count |
| map_loss_to_free_count | 已完成上述释放事件数；不含终端仍映射行，含OO立即回收的0cycle事件 |

实际ready时间在shader.cc:4964–4983对所有符合条件的PIB项观察，独立于IO是否已经到FIFO头；collection helper也有一次性fallback观察。严格恒等式为fully_ready_to_complete_sum = ready_to_collect_sum + collection_cycles + wb_wait。它是指令区间分解，许多区间并行，不能把总和或其差直接换成GPU cycles的因果贡献。完整issue→admission→refill→replay延迟未输出。

map-loss平均只比较同一种区间的单位；IO和OO回收政策、0cycle事件比例及观察人群不同。长map-loss不直接等于额外miss数，低physical平均不证明pool从未短时饱和，低PIB平均也不证明depth无关。IO no-free-physical=0是该路径的直接计数；OO同项缺失不能填0。

C16/C80的旧cap=8192，原已验reuse表证明其cap-full=0、peak128/489；其余选中原臂cap32768。保留这个配置差异及原非绑定资格，不把旧baseline改写为共同32768运行。finite cap-full=0只表示未被该特定全局credit上限拒绝，不能排除L2/DRAM/ICNT/MSHR/finite服务瓶颈。
