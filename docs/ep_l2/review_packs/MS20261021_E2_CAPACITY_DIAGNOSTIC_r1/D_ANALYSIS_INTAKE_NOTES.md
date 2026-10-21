# D增量分析入口：新runtime容量/数据服务诊断

本页仅说明已接受配对的消费方式，不宣告当前运行结果。只消费E发布且远端回读后的 `CURRENT_ACCEPTED`；不要读取活动raw或由进程退出推断PASS。当前五组使用同一新main `93a9f28d…`、Core `fe7e1fc1…`，与旧main61主结果分开。原五组MAIN GM **0.9977331348587999不变**，原七输入GM仍UNKNOWN。新诊断只能形成独立OFF/ON对照；五对完整接受后再给单独诊断GM，不替换旧S锚点或混入MAIN分母，保留慢化及负结果。

**交付与身份。** 每对文件名为 `CAPACITY_DIAGNOSTIC_<workload>_OFF_ON_NEW_RUNTIME_ACCEPTED_PAIR.json` 和同前缀 `_D_DELIVERY.json`；共享通知为 `E2_TO_D_<pair_id>.json`，写入原events/inbox及旧共享目录。`report.py`直传两端source/profile/labels、cycles、完整instructions、64slice、qualification_id、真实native退出身份、机制汇总及逐slice `capacity_diagnostic`。先以 `endpoints[side].receipt.sha256` 核对其 `receipt.path`；对应Git副本在本pack的 `<attempt>_run_status.json`。完整输入/配置身份在该回执的 `identity`、`input_audit` 和原 `result_directory/input_spec.json`；archive/build身份沿qualification绑定的正式A release追溯。通知写入仅表示DELIVERED，不能表示D已消费。

**精确结果入口。** 完整回执保留 `summary`、`validation`、`raw_log_sha256` 和退出证据；`result_directory/terminal_summary.json` 应与回执内summary一致，`result_directory/raw.log` 须匹配回执raw SHA，`NATIVE_EXIT.json`须匹配退出回执SHA。当前平铺通知没有单独复制以下字段，D应从完整回执读取，数据没有丢失：

| 内容 | 完整回执内路径 |
|---|---|
| 最终容量标签及原因 | `summary.capacity_classification`，并与 `validation.capacity_classification`核对 |
| 精确逐slice配置、容量/峰值/拒绝/覆盖与闭合 | `summary.capacity_diagnostic.slices["0"…"63"]` |
| 原生容量/Tag替换来源、物理服务与观测记录 | `summary.native_capacity_records`、`summary.structural_observations`、`summary.mechanism_slice_records` |
| 原生完整kernel UID闭合 | `summary.kernel_completion`；该字段不等于逐kernel时间表 |

**标签与机制边界。** OFF为 `FINITE_OFF_BASELINE`；ON可为 `OPERATIONALLY_NEAR_UNBOUNDED_NAMED_VECTOR`、`LARGE_FINITE` 或UNKNOWN。采用E的最终classification，不能只按通知中的简版“零拒绝且<=50%”文字重算：Tag还要求完整timed-clean/timed-dirty/host-prefill替换计数覆盖且替换为0；普通成功替换也是有限容量压力证据。保守上界不是精确占用，未覆盖计数不是0。拒绝检查次数不等于独立拒绝请求数；host预填替换不是计时GPU stall。ON是传统S加共同有限大容量与L2_DATA_FREE，**hardware_P1_throughput_eligible=0**；零物理grant仍执行真实数据/版本、固定copy-latch、同址顺序及lower-WB生命周期，不能解释为正常硬件P1加速。OFF/ON同时改变容量和本地数据服务，不能唯一分解两者因果。

**逐kernel消费。** 只对上述已接受raw做一次SHA绑定解析，保存D自己的行号索引。native `kernel_name =`、`kernel_launch_uid =`、`gpu_sim_cycle =`、`gpu_tot_sim_cycle =`和完成UID用于核对相同kernel顺序；命名kernel时长来自原生 `gpu_sim_cycle`，程序总时长取最终累计 `gpu_tot_sim_cycle`，不能按slice求和。保留 `final cumulative − sum(named durations)` 的独立FINAL_RESIDUAL及UNKNOWN原因，不直接称作DRAM drain。`EPL2B0V1|scope=kernel|interval=kernel_shared_delta|slice=…|kernel_uid=…`、`EPL2M0AV1`提供明确kernel区间/overlap信息；`EPL2MSV1/V2`观测和WAIT为累计快照，邻接差值须标注snapshot delta。64slice聚合前核对UID/区间及完整覆盖，缺值保留UNKNOWN。D现有 `util/ep_l2/mechanism_study_lane_d/paper_four_pair_details.py:observe/paired_timing`可复用SHA与时长对齐逻辑，但输出标签应改成OFF/ON，不能沿用S/F旧binary假设；新增容量/Tag记录需按本次source协议解码。

请求wait可跨原因、请求、slice及kernel窗口重叠；histogram/request-wait之和不是互斥GPU停顿，不能相加得到“节省周期”，最大值也不能作相邻快照减法。每对接受后立即分析cycles、流量、容量绑定及阶段变化；不用等待其余四组，也不从尚未接受端点推断论文结论。
