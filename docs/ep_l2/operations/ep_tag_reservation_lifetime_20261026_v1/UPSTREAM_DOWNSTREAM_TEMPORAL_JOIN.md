# 前后级访存路径的同窗联合

PROVEN：从已接受ON原始数据严格解析40,960个set-window；Stage在同slice的64个set行中重复，先按(slice, begin_L2, end_L2)去重为640组再求和。完整窗口[0,75039) L2 ticks，8192一窗，最后一窗缩短；GPU core/L2均1132MHz。所有下表计数来自同一8d55 ELF/输入/配置/ON raw09d6…；不是把不同历史runtime拼成漏斗。

|Stage|实际计数|单位|
|---|---:|---|
|DRAM_ACCEPT|1100762|L2_lower_queue_pop_into_DRAM_memory_packet|
|DRAM_RETURN|1000000|actual_DRAM_to_L2_return_packet_push|
|DRAM_SERVICE|1100762|actual_read_or_write_column_service_command|
|FRONTEND_COMMIT|1500000|actual_frontend_commit_event|
|FRONTEND_DENY|1818741|actual_frontend_head_denial_event|
|FRONTEND_HEAD|3400296|actual_frontend_head_decision_exposure|
|ICNT_INJECT_ACCEPT|1500000|actual_shader_packet_injection|
|ICNT_INJECT_DENY|0|same_head_buffer_full_retry_event|
|L1_ACCESS|1500000|existing_L1_cache_stats_access_outcome|
|L1_MERGE|0|actual_accepted_MSHR_HIT_branch|
|L1_MISS|1500000|existing_L1_cache_stats_miss_outcome|
|L1_MISSQ_BLOCK|1240787|same_access_actual_fail_counter_delta_retry_event|
|L1_SEND|1500000|actual_missq_to_memport_packet_push|
|L2_INGRESS|1500000|post_sector_split_ingress_packet|
|L2_MISSQ_BLOCK|818741|actual_L2_missqueue_denial_event|
|LOWER_QUEUE_BLOCK|2403077|actual_lower_queue_denial_event|
|RESPONSE_ACCEPT|1500000|actual_response_accept_event|
|RO_READY_EVENT|1000000|newly_ready_sector_bit_count|
|TVD_EARLY|375000|actual_TVD_early_path_event|

上述单位并不完全相同。重试/拒绝不是唯一request，也不是wall stall cycle；DRAM列服务命令不等于warp memory instruction；RO_READY_EVENT为新增ready sector位。不能相减生成“丢失请求”，也不能把2,403,077次LOWER_QUEUE_BLOCK除以75,039得全GPU停顿比例。L1 warp指令→coalesced transaction阶段及core issue/scoreboard的本轮精确逐请求关联仍UNKNOWN。

## 实际同窗共现

在有uniqueNEW且有正预约面积的同slice/window，L1 MissQ阻塞共现576组，L2 MissQ阻塞384组，lower queue阻塞420组，Frontend deny576组；ICNT injection deny共现0组。它们来自真实联合窗口检查，不是将独立边际计数相乘。Stage属于slice上下文，不能说每个set中的每个NEW都受该阻塞。所有window均无真实TagFAIL。

PROVEN这些队列曾阻塞请求；LIKELY它们改变到达与返回重叠节奏。UNKNOWN各自排他因果份额、未被发出的请求数和放宽资源后的TagFAIL概率；没有逐请求跨全路径祖先ID，本轮只称时间关联。

## RO时段不能等同DRAM服务时延

250118个RO全部退役，RO总owner时间285686930 L2 ticks，均值1142.208598。issued-notready暴露205915326（72.0773%）；required全ready但仍live的response-only暴露262540（0.091898%）；其余79509064（27.8308%）为未分类/可能发齐前暴露，不得归纯DRAM。比例是RO owner暴露份额，不是全GPU周期瓶颈份额。

整个Tag预约面积285424390，恰等RO_TIME−RESPONSE_ONLY；只作本次总体守恒核对，不推出每个RO与一个Tag episode一一对应。NEW/RE、mask新增ready和RO right-censor仍独立核验；RO right=0。

## 可排除与不能排除

Tag在所有事件最多4/16、时间面积最多3/16，未饱和。ICNT_INJECT_DENY=0支持本次注入buffer未观察到该类拒绝；LOCAL_XBAR配置不能由此推断真实芯片NoC带宽。L1_MERGE=0只限定此挂钩实际MSHR-hit分支，不能说所有层都不合并；L2 RO merge实际749882。TLB/PTW未在此生产访存路径中建模，不能作为已测瓶颈归因；本次observer未增加该模型。核心计算吞吐、scoreboard等待、精确DRAM bank并行度/带宽饱和与resource service-time分解仍不足证据。

旧已接受r5/e511独立受控证据中，DRAM域850→935 cycles降低6.9004%，L1 MissQ16→32局部重试下降36.2845%但cycles增加0.16258%。该结果支持优先关注下游服务而非单独扩大L1 MissQ；本轮8d55未重跑这些干预，也不把旧/新binary拼成性能pair。见父审查分支CONTROLLED_SENSITIVITY_20261026_V1/FINAL_REPORT.md。
