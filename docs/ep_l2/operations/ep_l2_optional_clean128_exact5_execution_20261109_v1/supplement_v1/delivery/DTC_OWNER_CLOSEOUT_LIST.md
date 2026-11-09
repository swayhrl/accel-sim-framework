# 转交 DTC-L1 owner 的精确核账清单

EP-L2 Main 只读采样于 2026-11-09 15:21:29 UTC。来源为 Native registry SHA `c884c5afec814b6a8ab45bbc40c5d6eda4d275f9bca43a51ac8733c294efd3c8` 及同刻资源适配器明细；逐条路径、控制器 SHA、owner PID/start_ticks、execution receipt 计数见 `NATIVE_WRITE_LEDGER_RECONCILIATION.json`。下面各占额均**未释放**，EP-L2 Main 不改 DTC 行。

| request | 准入占额 B | 当前缺的正式关闭证据与建议动作 |
|---|---:|---|
| `DTC_ORACLE_INITIAL8_20261106_V1` | 4,155,880,420 | 32/32 已消费且有 execution receipt；需 owner 核对每项终态、真 164 归档/恢复、Native 留存与后续输出/metadata 义务，按原 owner 流程发布 release receipt 并修订 carrier。 |
| `DTC_ORACLE_REMAINING24_20261106_V1` | 268,435,456 | 96/96 已消费；同上。既有 Gate2 release 是运行资格，不是全部归档关账。 |
| `DTC_PERF_FIRST_NON_TAG_REMAINING28_20261104_V1` | 4,563,402,752 | 28/28 已消费；first4 terminal gate 不能替代本 28 项归档/恢复关闭。请给逐项闭合证据和剩余写入量。 |
| `DTC_PERF_FIRST_PHYS768_FIRST4_20261104_V1` | 805,306,368 | 4/4 已消费；registry 的 lifetime ceiling 解释已写明只按活跃/未归档项预测，请 owner 按实际终态、归档/恢复、metadata 减账并正式发布。 |
| `DTC_PERF_FIRST_V2_CODESIGN16_LAYOUT_R1_20261105_V1` | 2,684,354,560 | 16/16 已消费；direction/authority release 不是结果归档关闭。需逐项真 164、恢复与残余义务证明。 |
| `DTC_PERF_FIRST_V2_PHYSICAL_PIB16_20261105_V1` | 2,684,354,560 | 16/16 已消费，含旧技术负例；需保留负例并核对归档/恢复和剩余写入，不能因 execution receipt 或失败直接退款。 |
| `DTC_AE_V100_FULL_SWEEP_20261025_V1` | 1,143,128,181 | 72 预算仍余，适配器含三个 departed cohort 的结果/恢复界及 1 GiB owner metadata；请 owner 区分仍可运行预算、已写 bytes 和可正式关闭的义务。历史 35 GiB pool ceiling 未被直接叠加。 |
| `DTC_L2_MLP_FULL_WORKLOAD_EXPLORATION_20261027_V1` | 1,202,171,865 | 一个 unresolved consumed generation 仍占结果/恢复界，另有 1 GiB metadata；请 owner 核对该 generation 与归档/恢复，正式关闭后再调 carrier。 |
| `DTC_STAGE_IIA_FIRST16_CH_MATCH_20261104_V1` | 2,684,354,560 | 16/16 已消费，claims 空；适配器仍保留原 carrier，派生剩余界仅 268,435,456 B。差额 2,415,919,104 B 是待 owner 证明的可能释放量，不能由 EP-L2 Main 代减。 |
| `DTC_STAGE_IIA_REMAINING48_CH_MATCH_20261104_V1` | 268,435,456 | 48/48 已消费，claims 空，当前适配器只列未来 metadata。请 owner 核对正式收尾与释放条件；若仍保留该 metadata，说明其具体后续写盘用途。 |

需返回的最小材料：各 request 的不可变终态清单、逐项真 164 archive/restore/COMMIT 引用、当前 Native 已写与仍将增长的 byte 界、owner 对保留或释放 carrier 的事务回执与新 registry/epoch SHA。任何来源不明项标 `UNKNOWN` 并保留原保证。空间清理仍由用户负责。
