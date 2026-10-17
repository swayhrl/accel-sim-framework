# Lane Z typed metric dictionary — V1

本合同先于任何新 K0/K1 结果消费冻结。只读输入为 Lane A `f5c37d6edcce832a72cb0830021bffa78df6cc13`、M `d723784a8b897566b63113f95972f7a8d12a01ce`、T `f520a445436b57c0a0f2494fb858a1636f04d2bc` 的 accepted small evidence。机器字段合同见 `METRIC_DEFINITIONS.tsv`；M 的逐字段定义、raw-name 绑定和精确源码 SHA 同时封存在 `sources/M/`，本合同补充 kernel 与失效策略边界，不改旧字段语义。

`AVAILABLE` 必须有明确原值；`UNAVAILABLE` 表示当前消费证据不能直接给出，绝不填零；`UNCOMPARABLE` 表示两边虽有值，单位、阶段或人群不相同。分母为零的比率记 `UNDEFINED_ZERO_DENOMINATOR`。类型分别为 uint64（计数/积分/周期）、float64（显示均值/比率）、string（身份）；比率正式计算保留整数分子分母，显示精度不参与判定。

| 指标 / 原字段 | 类型、单位 | 采集边界与分子 | 分母 / 限制 |
|---|---|---|---|
| whole-run cycles / `gpu_tot_sim_cycle` | uint64 GPU core-cycle | 完整有序输入自然终态最后累计值，含 tail | 1；同输入、ROI、clock/config 比较；不是 wall time |
| kernel cycles / `gpu_sim_cycle` | uint64 GPU core-cycle | 每个原 launch ordinal 的最终 kernel 周期；保留同名重复 kernel 与 stream | 1；不得按名称排序、合并或只取末个 kernel；`gpu_tot_sim_cycle` 快照不能当本 kernel 周期 |
| terminal queryable / lost mappings | uint64 logical128B mappings | 终端仍在 Tag 中可查的映射；已失去映射但物理行尚存的 allocation 分开 | 当前旧 small evidence 无直接统一输出：两者 `UNAVAILABLE`；不可用 physical integral、Tag eviction 或 map-loss completed count 倒推 |
| mapping invalidation events | uint64 mapping events | 明确的失效原因、line+generation、一次边界一次计数 | 现有 eviction 只是替换事件，不等于 kernel-boundary invalidate；后者旧证据 `UNAVAILABLE` |
| ready / pending / new outcome | uint64 accepted logical128B-reference events | 成功接受 reference 时 ready physical / pending attach / new allocation；IO new 原字段为 physical_allocations，OO 为 new_misses | 分母 D=ready+pending+new，与 completion_dependency_count 核对；不含失败重试，不是 lookup attempts 或 warp 指令数 |
| lower-created | uint64 lower-request creation events | DTC cacheable new request；与 credits acquire/release 的终端守恒分别核对 | 1；不是 successful ICNT injection；二者旧终态恰好相等也保留独立字段 |
| global read/write injected | uint64 successfully injected mem_fetch packets | `gpgpu_n_mem_read_global/write_global`，`icnt_inject_request_packet` 成功注入、`update_icnt_stats` 边界 | 1，或除同一 run 的 active-thread instructions 得 packets/instruction；不含失败注入重试，不是唯一地址 |
| lower/Tag/pool/MSHR retry/reject | uint64 attempt events | 失败尝试计数，可能同一请求重复累加 | 原事件数 / 1；若归一化须写明每成功 reference 或 injection，允许 >1；不能叫互斥 stall cycles |
| service samples | uint64 SM×core-cycle | `DTC_SERVICE_V1_samples`，所有64 SM、idle/gated/tail 都计 | samples=64×whole-run cycles；不使用 active-only 假定 |
| PIB integral | uint64 entry×core-cycle | `DTC_SERVICE_V1_pib_integral`，含 ordinary 的占用积分 | samples，得到 entries/SM；低均值不能排除短时满 |
| physical integral | uint64 physical128B-line×core-cycle | `DTC_SERVICE_V1_physical_integral`，所有分配行，含失去映射不可查的行 | samples，得到 lines/SM；不等于 retained queryable mapping 数 |
| map-loss-to-free sum/count | uint64 core-cycle / completed allocation intervals | `DTC_SERVICE_V1_map_loss_to_free_sum/count`，映射丢失到物理释放；含0cycle释放 | sum/count；排除仍映射或尚未释放的区间，IO/OO 与 K0/K1 可能改变条件人群，须连同 count 报告 |
| ready-to-collect | uint64 cacheable-warp×core-cycle | `DTC_SERVICE_V1_ready_to_collect_sum`，所有 refs admit 且 data ready 被观察到，至首次成功 collection | service retired；含选择/FIFO/端口等待，不能唯一归因 |
| collection | uint64 cacheable-warp×core-cycle | `DTC_SERVICE_V1_collection_cycles`，首次到最后 collection 服务周期，含端点和中间间隙 | service retired；不是 collected sectors 数 |
| post-collection WB | uint64 cacheable-warp×core-cycle | `DTC_SERVICE_V1_wb_wait`，末次 collection 后到成功退休，扣除源码规定边界 | service retired；不是完整 writeback latency |
| ready-to-complete | uint64 cacheable-warp×core-cycle | `DTC_SERVICE_V1_fully_ready_to_complete_sum`，fully-ready observation 至成功退休 | service retired；不是 issue/admit/refill/replay 总延迟 |
| retired / collected sectors | uint64 cacheable warp instructions / sector32B services | `DTC_SERVICE_V1_retired/collected_sectors`；每指令所需 sector union 的 collection 工作 | retired 用于延迟均值；collection sectors 不是下层四 sector fill 流量 |
| L2 read outcomes | uint64 sector32B access events | `L2_cache_stats_breakdown[GLOBAL_ACC_R][HIT/HIT_RESERVED/MISS/SECTOR_MISS]` | TOTAL_ACCESS=四项之和；MSHR_HIT 为补充桶，不能重复相加 |
| L2 retries | uint64 failed attempt events | GLOBAL_ACC_R RESERVATION_FAIL（另保留 all-access retry） | 若报 retry intensity 用同类 TOTAL_ACCESS，不加进成功 access 分母；不是概率 |
| L2 requested read payload | uint64 bytes | GLOBAL_ACC_R TOTAL_ACCESS×32B | 1；不是 DRAM、NoC wire/header 字节。旧 M 九臂为4×read injection，必须逐run核，不能泛化成定律 |
| DRAM n_rd / n_rd_L2_A / n_write / n_wr_bk | uint64 issued atom32B commands | 每 controller 终端最后 tuple，相加 controller，不能再加 Read/Write 别名或 kernel 累计快照 | 各 count / 1；包含所有实际访问类，非仅 DTC 主load |
| DRAM read/write payload | uint64 bytes | (n_rd+n_rd_L2_A)×32 / (n_write+n_wr_bk)×32 | 1；read command fraction 的分母 n_rd+n_rd_L2_A，write 同理；若报 bytes/instruction 用同run active-thread instructions |

sector32B 与 logical line128B 是不同对象；32×4 和64×8是 sets×ways，分别128/512个逻辑映射，地址覆盖16/64KiB，不能当物理容量。physical640×128B=80KiB 未因扩 Tag 改变。C+ 的普通 coalesced cache `HIT/HIT_RESERVED` 与有限 DTC accepted unique128B-reference outcome 跨族 `UNCOMPARABLE`。finite 的普通 L1D 多为 side/store 路径，不能当主load Tag 命中率。也不能把同名 frontend-ready 历史字段代入 DTC_SERVICE_V1。

逐 kernel 重复打印的 DTC、cache、DRAM lifetime counters 只取最终累计值。kernel 周期/指令是显式例外，按 ordinal 保存自己的非累计值；只有验证单调、相同对象/clock、无 reset、边界完备以后才允许以相邻累计差分形成另命名的 kernel counter，缺前提则 `UNAVAILABLE`。多 stream 或重叠 kernel 不默认 sum(kernel cycles)=whole-run；旧 M 串行样本可独立核此等式。T small pack 的多 kernel 周期未逐项保存时如实缺失，不从总周期平均分摊。

严格指令区间恒等式：ready-to-complete sum = ready-to-collect sum + collection cycles + wb_wait。这些指令区间会并行重叠，恒等式不能转成 GPU 周期精确因果分解。post-ready 退化即使 whole-run 获益也必须报告。

Lane X 若增加低扰动 event counters，单独登记 observer flag（默认/有效值）、Core/source/build/binary SHA、计数钩子、clock、对象与 reset/lifetime、pre/post invalidation 边界、retry 去重、idle/失败路径、边界调用次数及额外存储/采样开销。X 的发布合同与开关在本次未消费，均为 `UNAVAILABLE_PENDING_X_PUBLISHED_CONTRACT`；这里不指定未经验收的 CLI 字段名。新计数与旧 observer-off 数据分区，跨插桩前后不直接混比 cycles；四格若非同一观测合同就不估计交互。
