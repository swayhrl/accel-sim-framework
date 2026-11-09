# DTC Native 写入承诺核账与 owner 关账 V1

## 裁决

2026-11-09 16:17:44 UTC，DTC-L1 Main 依现有 Native registry 独占锁、前后 SHA、epoch 2 和 request history 协议，对五项已经终结、真 164 归档且 Native restore 完成的请求关闭**结果增长与恢复窗口**承诺。每项仍保留原资源政策明确的 **268,435,456 B metadata** 保证。十项 DTC 准入占额从 **20,459,824,178 B** 降为 **8,380,228,658 B**；正式可释放与实际已释放的**承诺**均为 **12,079,595,520 B**。原 Native 数据和 Source KEEP 未删除，**物理释放 0 B**；科学 request、模型启动、预算消费、退款均为 0。

本轮不将 registry 的历史 `RUNNING` 字段改写成科研终态。关账仅调整五条 `reserved_write_bytes` 并添加对应 owner 证明引用。V100 的 72 次剩余预算、MLP 的一个未决 generation、Oracle initial8 的 13 条原池 claims 均保留。没有对这些记录推定未来写入为零。

## 十项逐请求账

金额均为 B；“释放”是本次正式减少的 Native **未来写入准入承诺**，不是 df 已占用字节的回收。逐项来源 SHA、终态、claims、逐 cohort 结果和归档证明见 [OWNER_CLOSEOUT_LEDGER.json](OWNER_CLOSEOUT_LEDGER.json) 与 [LIVE_EVIDENCE.json](LIVE_EVIDENCE.json)。

| DTC request | 原占额 | 当前仍保证 | 正式可释放／实际释放 | 未决与关账依据 |
| --- | ---: | ---: | ---: | --- |
| `DTC_AE_V100_FULL_SWEEP_20261025_V1` | 1,143,128,181 | 1,143,128,181 | 0 | 284/356 已消费，72 仍余；三个 departed 结果/恢复界及 1 GiB owner metadata。未来执行权限不由本账授予。 |
| `DTC_L2_MLP_FULL_WORKLOAD_EXPLORATION_20261027_V1` | 1,202,171,865 | 1,202,171,865 | 0 | 360/360 已消费，仍有一个 unresolved consumed generation 和 1 GiB metadata，claims=1。 |
| `DTC_ORACLE_INITIAL8_20261106_V1` | 4,155,880,420 | 4,155,880,420 | 0 | 32/32 结果及真 164 COMMIT/Native restore 存在，但原共享池 claims=13；未取得这些 claims 的正式逐项解绑回执。 |
| `DTC_ORACLE_REMAINING24_20261106_V1` | 268,435,456 | 268,435,456 | 0 | 96/96 归档恢复，claims=0；原占额已经只有 metadata 界。 |
| `DTC_PERF_FIRST_NON_TAG_REMAINING28_20261104_V1` | 4,563,402,752 | 268,435,456 | 4,294,967,296 | 28/28 终态，24 PASS、4 已归档负例；claims=0，全部 COMMIT/restore；保留 metadata。 |
| `DTC_PERF_FIRST_PHYS768_FIRST4_20261104_V1` | 805,306,368 | 268,435,456 | 536,870,912 | 4/4 PASS、COMMIT/restore，claims=0；保留 metadata。 |
| `DTC_PERF_FIRST_V2_CODESIGN16_LAYOUT_R1_20261105_V1` | 2,684,354,560 | 268,435,456 | 2,415,919,104 | 16/16 PASS、COMMIT/restore，claims=0；保留 metadata。 |
| `DTC_PERF_FIRST_V2_PHYSICAL_PIB16_20261105_V1` | 2,684,354,560 | 268,435,456 | 2,415,919,104 | 16/16 为已归档技术负例、无重试；COMMIT/restore 和 claims=0；保留失败及 metadata。 |
| `DTC_STAGE_IIA_FIRST16_CH_MATCH_20261104_V1` | 2,684,354,560 | 268,435,456 | 2,415,919,104 | 16/16 PASS、COMMIT/restore，claims=0。旧 carrier 与派生界之差**经过本次 owner 正式关账**才被释放。 |
| `DTC_STAGE_IIA_REMAINING48_CH_MATCH_20261104_V1` | 268,435,456 | 268,435,456 | 0 | 48/48 PASS、COMMIT/restore，claims=0；现有准入仅计 metadata。 |
| **合计** | **20,459,824,178** | **8,380,228,658** | **12,079,595,520** | 仍保证的金额并非确定会写入的字节。 |

八个已消费完毕的近期请求共 256 个逐项结果、归档回执和同 txid 真 164 `COMMIT.json`，并见 `RESTORE_VERIFIED_NATIVE_TARGET.json` 与 Native 恢复路径。五个正式降额请求共 80 格；其中 PHYSICAL_PIB16 的全部失败及 NON_TAG28 的四个失败原样保留。该核验仅读取既有小型 JSON/路径元数据，没有重做科研 strict、raw 或大型 Trace 扫描。每个 `RESOURCE_POLICY.json` 的 `metadata_reserve_bytes` 均为 268,435,456 B；其 SHA 与逐格证明冻结在 owner intent 中。

EP 快照的 `recorded_peak_result_logical_bytes_sum` 是运行期逻辑峰值累计，并非物理分配量或新写入要求，PHYSICAL_PIB16 的该字段为 0 也不代表无失败原件。已落盘 Native 结果及 Source 已计入实时 `df`。本轮未运行逐文件块分配清点，因此十项可归属的**实际物理已写字节均为 UNKNOWN**；保留的 metadata 界与 V100/MLP/Oracle claims 承诺是真正仍需准入的量，精确将来增长仍为 UNKNOWN。164 tar 占用不作为 Native 再扣；Native restore 的既有产物不删除。

## 原子事务和独立回读

固定 EP 来源提交 `79582eac99a308671ccd8542d52b2b62a53e5587` 的三件原文 SHA 见 [SOURCE_INDEX.json](SOURCE_INDEX.json)。事务前 registry SHA `c884c5afec814b6a8ab45bbc40c5d6eda4d275f9bca43a51ac8733c294efd3c8`、current epoch SHA `61880c3c289e3fed982a4ced8514d2bb9981b3e747a00febed4994961b2c2665`；事务后分别为 `99d308561466e45470456121c3a24dd51ace29ab6e9f7718283f0960cd493592`、`4b81fa564096db462d58cb2a1717f3c5e1f9e6adadea488c132af923fbb12024`。epoch 仍为 2，指向新 registry SHA，科学预算 89→89。registry 72 条 request 中只有上述五条改变，其他 **67 条逐字段一致**；其他 registry 顶层字段及 epoch 除 SHA 指针/版本回执外的字段逐字段一致。旧账完整保存在 Native `request_history`，本机 deliveries 保存完整前后字节快照。正式 [owner intent](DTC_NATIVE_WRITE_CLOSEOUT_INTENT.json) SHA `6f03c570c9395a3b18c6698a3a89c47af7ce03db41e4aa18d02a319a36b9e1d5`；[COMMITTED 回执](DTC_NATIVE_WRITE_CLOSEOUT_COMMITTED.json) SHA `3e8486af8b108c1d0c8393b54aa67153536b7c4c1a42df1b5eac56ccb2ffbf9f`。事务没有改变 EP 或其他 owner 的保证。

[Registry 差异证明](REGISTRY_CHANGE_PROOF.json) 逐字段确认仅五行的 `reserved_write_bytes` 与 owner 证明引用变化，并给出 67 条未改 request 的摘要；完整前后 registry 字节快照保留在本机交付目录，不把共享 registry 全文写入公开审阅包。

## EP-L2 可消费的资源结论

有效 Native 安全底线仍为 **5,368,709,120 B（5 GiB）**。16:20:25 UTC 对 GEMM/Stencil 的**只读**资源适配器回读新 registry SHA，`foreign_metadata_errors=[]`、EP 消费仍为 0；两族分别报告 foreign remaining writes **8,650,761,266 / 8,717,870,130 B**。差额正是对方 family carrier。DTC 的 8,380,228,658 B 加上 GEMM/Stencil 各自未消费 carrier 337,641,472 / 270,532,608 B 及 5 GiB 底线，构成无 claim 的共同诊断需求 **14,357,111,858 B**。该刻 Native 可用 **18,526,584,832 B**，诊断账面裕量 **4,169,472,974 B**，因此在这一采样与这些已知承诺下**未见 Native 磁盘缺口**。这不是逐点准入 PASS；瞬时 RAM、claims、真实模型以及 df 随时变化，EP owner 必须按其原五点合同 fresh admission。DTC 本轮不触发 EP 实验。

仍需留存 V100 未消费预算和三条 departed 义务、MLP 未决 generation、Oracle initial8 的 13 条 claims；后者只有原 pool owner 的逐项关闭证据才能进一步减额。Oracle remaining24、Stage IIA remaining48 以及五个降额请求的 metadata 保证也保持。任何物理盘清理、删除或迁移 Native Source 须由用户另行授权。本轮不恢复旧 owner、不退款、不重启模型、不修改 EP-L2 `CONTEXT.md`。下一科学任务之前维持 STOP。
