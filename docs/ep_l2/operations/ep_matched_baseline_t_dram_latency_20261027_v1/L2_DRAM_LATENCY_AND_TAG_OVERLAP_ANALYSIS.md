# L2固定延迟与Tag预约重叠联合归因

本分析只读六个已接受点，完整统一表为[UNIFIED_COMPARISON_TABLE.csv](UNIFIED_COMPARISON_TABLE.csv)，实际逐Set和窗口在真164最终证据包的analysis/FINAL_SIX_ACCEPTED。身份、SHA与恢复入口见RESULT_IDENTITIES.json和FINAL_ARCHIVE_AND_RESTORE_RECEIPT.json。

| mode | dram_latency_core_cycles | RO_retire | RO_TIME_mean_L2_ticks | RO_LOWER_TIME_mean_L2_ticks | NEW_mean_lifetime_L2_ticks | RE_zero_lifetime_fraction | Tag_EVENT_PEAK | Tag_TICK_PEAK | reserved_Tag_L2_tick_area | NEW_unique_R8 | credit_block_candidate_attempts | Lower_FIFO_full_candidate_slice_ticks | scheduler_causal_block_candidate_attempts |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F | 100 | 250087 | 1218.5808578614642 | 872.6369583384982 | 811.8938613333333 | 0.9997627229804127 | 7 | 6 | 304481252 | 0 | 0 | 867760 | 1043849 |
| F_MINUS_T | 100 | 250087 | 1218.5808578614642 | 872.6369583384982 | 811.8938613333333 | 0.9997627229804127 | 7 | 6 | 304481252 | 0 | 0 | 867760 | 1043849 |
| S | 100 | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | UNKNOWN_NOT_INSTRUMENTED | UNKNOWN_NOT_INSTRUMENTED | UNKNOWN_NOT_INSTRUMENTED | UNKNOWN_NOT_INSTRUMENTED | UNKNOWN_NOT_INSTRUMENTED | UNKNOWN_NOT_INSTRUMENTED | 0 | 953624 | 1031152 |
| F | 200 | 250000 | 1317.807776 | 995.09794 | 877.82016 | 1.0 | 7 | 6 | 329182560 | 0 | 0 | 765888 | 1013685 |
| F_MINUS_T | 200 | 250000 | 1317.807776 | 995.09794 | 877.82016 | 1.0 | 7 | 6 | 329182560 | 0 | 0 | 765888 | 1013685 |
| S | 200 | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | UNKNOWN_NOT_INSTRUMENTED | UNKNOWN_NOT_INSTRUMENTED | UNKNOWN_NOT_INSTRUMENTED | UNKNOWN_NOT_INSTRUMENTED | UNKNOWN_NOT_INSTRUMENTED | UNKNOWN_NOT_INSTRUMENTED | 0 | 795311 | 1002558 |

PROVEN（受控差异）：F与F−T在每个同延迟点完整cycles相同，生产TagFAIL、relieve、detach为零，T无独立收益。F100→200的RO均值、NEW寿命及NEW到达R分布确有变化。NEW unique与重复head-cycle分别保存，不能用重试次数充当独立line。R0–R8完整分布、时间加权占用与NEW/RE完整寿命直方图随报告提供。事件峰7与tick末峰6不矛盾，单tick中事件顺序会形成瞬时峰；峰7也不能说明独立NEW曾在R7到达。满8路驻留只能取area[8]，REENTER不是满路周期。

NEW_WITH_ELIGIBLE和NEW_CAN_DETACH由包含T开关的can_detach谓词决定，F−T的0是policy-gated零，不能解释为结构上没有待脱离RO。F100的6634个NEW_WITH_ELIGIBLE与真实TagFAIL联合仍为0；不能将独立边际相乘来宣称机会。当前数据没有RAWFAIL，因而不能把reuse_seen或Frontend排除认定为这批零detach的直接原因。

RO_LOWER_TIME累计“issued但未ready”的RO状态暴露，始于真实L2→DRAM FIFO入队接受后，含Lower FIFO/固定等待/Scheduler/Bank/返回与fill接受，不能命名纯DRAM延迟。该packet尚在MissQ而未lower接受的时间不计入；多sector RO可同时有另一未issued sector滞留MissQ，但此指标不计量逐packet MissQ驻留。S没有RO，填NOT_APPLICABLE，不补0。现有EPL2ROC1 LOWER_CONCURRENCY事件峰逐slice报告于RO_LOWER_CONCURRENCY_EVENT_PEAKS.csv，只选择epoch_end等于完整cycles的64行，保留peak_lower_transactions及peak_independent_lower_lines；全slice最大值不等于全GPU并发峰。该事件人口是RO_ISSUED_NOT_RETURNED_PER_SLICE，不能冒充LIFE未ready状态暴露的时间加权直方图。当前Core没有RO_LOWER_CONCURRENCY时间加权直方图；仅可由完整SUM_LOWER除同人口时域slice ticks导出一阶平均，每点的派生均值在统一表标明，不能冒充实际峰值或分布。

PROVEN（饱和观察）：L2 MissQ与Lower FIFO峰达到128，DRAM Scheduler峰达到128；它们有非零full/候选拒绝。Credit/ReturnQ这些已覆盖的阻断统计为0，不能泛称所有路径都不受限，也不能把未采到的固定延迟队列叫空闲。Payload bank存在服务冲突；TVD/descriptor/WAD不等于Tag资源，分别保留原计数。

F100→200：Lower FIFO/full、MissQ/full和Scheduler观察计数可能下降，而RO未ready和预约面积上升。观察到排队压力重新分布。较长deadline改变credit持有/到达节奏是LIKELY解释；实际credit在飞数量/时间、固定等待、到期后等待和具体packet路径贡献仍UNKNOWN，不能把未测credit变化写成已证归因。c7d scheduler_full_observed为候选观察；causal_block仅排除当次return/credit其他先阻断，仍不等于该Tag分配失败的因果证明。各计数不能相加为独占stallcycles。

窗口方法：LIFE8192 L2ticks及其begin_gpu/end_gpu提供真实core边界；B0约5000core窗口、C7E的实际core边界另存，C7E占用分母为DRAM ticks。WINDOW_BOUNDARY_JOINS逐区间求真实交集，绝不按编号、绝不对边界重叠按比例分摊计数。一个channel供两个slice，join链接不能双算channel样本。PER_SET_WINDOW_CORRELATION把同一Slice/Set的area和同LIFE窗口STAGE关联；同slice的block数重复列于各Set仅供查看，禁止跨Set求和。TOP_RESERVATION_WINDOWS给每点面积最高五窗。它们只能证明同窗相关，未观测逐Tag→queue阻断因果链。窗口尾部覆盖空洞在WINDOW_COVERAGE逐条保留，不用application总量补齐。

S已自然完整drain且B0/C7E最终统计完整，但当前c67只在RO epoch关闭时发LIFE终端，S没有终端META/SET/INC/STAGE/END。完整S NEW/RE寿命、事件全程峰、R0–R8需求联合及总面积标UNKNOWN_NOT_INSTRUMENTED；已有整窗口仍可分析。不是把S的禁用RO零值当测量结果。没有为补计数改Core/ELF/开关或重跑。

m_dram_latency_queue尚无可接受的应用级入队/到期/实际Scheduler进入的驻留统计，标NOT_INSTRUMENTED。配置100/200只能说明deadline偏移，不能替代实际驻留。被动补充计数仅候选，见MINIMAL_CONTROLLED_EXPERIMENT_PLAN.md。

附加观察修正：EPL2DRAM successful_read/write及LIFE DRAM_SERVICE发生在L2→DRAM FIFO pop到固定延迟队列，read/write表示requires-return/无需return(WB)分类。真正列命令/总线字节由32个最终DRAM块提取n_rd+n_rd_L2_A、n_write+n_wr_bk及32B/burst。两类人口分别报告，既不混称DRAM完成，也不以相同数值推断普遍等价。

计数补充：统一表MissQ/Lower_FIFO的candidate_slice_ticks是精确frontend plan拒绝时的候选暴露；LIFE LOWER_QUEUE_BLOCK是下游drain时miss_queue非空且LowerFIFO满的L2tick暴露。它们既不是同一事件，也不是单纯队列每tick占满采样，按COUNTER_POPULATIONS_AND_DOMAINS.md的源行号与分母解释。
