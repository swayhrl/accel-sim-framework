# 项目 owner 意见与权威状态核对

本轮没有直接owner回复，也未发送消息。没有可寻址的其它项目Codex窗口或经验证owner消息通道；依照任务要求交付待转交询问。下述全部为 READ_EXISTING_AUTHORITY（已读历史状态），不标为 OWNER_REPLIED；Git提交者身份也不等于科研owner。

审查截止 2026-11-04T11:56:53+08:00。所列commit_time是文件最近提交时间，不是owner本轮回复时间；content_observed_at是本次读取时间。所有候选的具体冷存接受均为UNKNOWN / OWNER_CONFIRMATION_PENDING。

| 项目 | 可定位的科研责任角色 | 实际实名owner | 权威状态核对 | 本轮直接回复 / 时间 |
| --- | --- | --- | --- | --- |
| EP-L2 | Main execution / scientific coordinator；机制分析Main | 未由本轮证据确定 | EP_CLOSE / EP_MECH / EP_INPUT；16结果已闭合，Source KEEP | 无 / N/A |
| DTC-L1 / DTC | Main sole scientific execution owner；Stage-II、AE协调方 | 未由本轮证据确定 | DTC16 / DTC48 / DTC48_README / DTC_AE；remaining48快照仍运行 | 无 / N/A |
| AI-ARCH | 项目协调者及A26/A61/A65/A67/NequIP/A79执行owner；不能以一条lane代全部 | 未由本轮证据确定 | 各独立执行报告；A79同StageA BF16路径；A61被下游复用 | 无 / N/A |
| C16 | 109 StageA producer + 174独立consumer；E1科学owner | 未由本轮证据确定 | STAGEA_CANARY / STAGEA_TERMINAL / E1 | 无 / N/A |
| AWMA | R26/R27报告标明Lane G /109；缓存三条线需各自owner | 未由本轮证据确定 | AWMA26/27R2/27R3；AWMA_STATE仅10月2日历史，不能当当前ACTIVE | 无 / N/A |

## 八问逐项目核对

| 项目 | 当前运行是否使用候选109资产 | 7天计划 | 30天确定/可能计划 | 109常驻 | 删除后恢复前提 | 原始证据 | 未完成/暂停 | 接受冷存 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EP-L2 | 有界文件未建立候选精确依赖；不能据此否定间接使用 | 未取得带日期计划 | 机制提案存在但无日程 | owner待确认 | 其Source/Trace/结果各有原authority；与候选路径映射待确认 | 接受结果、原始/失败Trace需要保留；不等于候选模型必须常驻 | 本轮Performance-First已完成；机制候选未授权，其它线未知 | 未取得 |
| DTC | remaining48在11:26快照运行；候选精确依赖未知；不能因为在174而否定109 | 当前批预计继续，未承诺日期或109候选使用 | 后续Stage-II/AE计划未知 | mount/symlink/原capture间接依赖待owner | Trace bundle metadata已有，后端及所有恢复任务需核对 | 原始/负结果/接受结果证据保护 | remaining48未最终收尾；AE旧快照不能替当前答复 | 未取得 |
| AI-ARCH | 未证明当前GPU reader；A79冻结方案直接依赖StageA BF16；A65/A67实际复用A61 | deferred和conditional提案未给日期 | 复审/分析和新派发可能性未知 | StageA BF16与A61共享树先HOLD | 所读A26/A61报告没有提供大payload的164归档；当前全树资格仍未建立；NequIP小raw不等整树；拆分后S109闭合 | 原始观测/失败/接受数值必须保留；官方可再下载数据和cache另列 | A79 GPU_RESOURCE_DEFERRED；其它独立STOP不等于放弃证据 | 未取得 |
| C16 | StageA terminal partial且旧campaign停止；当前精确reader由S109核 | 无新自动调度授权；计划未知 | E1/新问题重开均待新授权，日程未知 | 不能替AI-ARCH决定BF16；AWQ和E1待owner | exact revision/Trace + manifest/config/runtime；禁止重新生成等同 | E1原始/failure Trace和规范证据保护 | DQ问题incomplete；E1 slots历史pending；不自动续行 | 未取得 |
| AWMA | runnable Qwen3引用和checkpoint lineage确立；实时reader未建立 | 未知 | 数值/lineage继续分析可能性未获日程确认 | 需逐cache/父本/规范本单独回答 | 精确COMMON/W/m/v/RNG/step/cursor及模型输入/代码；HTTP离线闭包 | R26规范parent与B0反例；checkpoint不是全部可重跑替代 | R27r2/r3数值STOP；缓存线后续状态待确认 | 未取得 |

## 采集方法与范围

SSH只在174-new运行Git/轻量状态读取及独立报告仓库操作；未登录109/164、未开GPU/模拟器/dispatcher、未访问活动raw或checkpoint payload，未做新Trace/模型SHA或全盘扫描。GitHub插件用于固定HEAD、内容和分支发现，Git SSH用于隔离仓库取得同一公开科研文档。Git对象传输不等于科研payload迁移。

S109输入固定V2 HEAD 0915c630a740dc863505ce86012440be322117cb。本轮多次GitHub node109分支发现只返回V2和unified-audit V1，未发现V3；此结论限查询快照及分支命名，不推断V3未在后台执行。没有写S109分支、Goal、锁或报告。五份V2优先文件均完整阅读。

EP/DTC的“未发现候选依赖”限下列source_ids中的状态/报告/绑定索引；未全分支扫描raw、二进制、大日志、环境或研究payload。174两处项目根仅枚举小型控制文件名称，未将其mtime作为热度判据。没有用户或owner新增回复。额外A65/A67/E1通过GitHub固定HEAD阅读，读取收据记录实际内容blob。

## 来源索引（均可按固定HEAD复核）

以下时间及blob来自Git/GitHub，本轮读取截止为 2026-11-04T11:56:53+08:00。路径、branch、HEAD不能省略为“最新”；同名CURRENT_STATE按独立执行分支限定scope。矩阵source_ids引用本节ID。

### A26

- File: [docs/ai_workload_research/runs/AI_ARCH_A26GR1_GSSCALE_RUBBLE_109_V1/FINAL_REPORT.md](https://github.com/swayhrl/accel-sim-framework/blob/cf80f6ec07a31eccdaff264c3bce64e0511179f8/docs/ai_workload_research/runs/AI_ARCH_A26GR1_GSSCALE_RUBBLE_109_V1/FINAL_REPORT.md)
- Branch: `hrl/aiarch-a26gr1-gsscale-rubble-bounded-tar-109-v1`
- HEAD: `cf80f6ec07a31eccdaff264c3bce64e0511179f8`
- Blob: `aeba830eb4f37d157027a07a77c6874209c07299`
- File commit_time: 2026-10-14T17:22:24+08:00
- content_observed_at: 2026-11-04T11:56:53+08:00; mode: READ_EXISTING_AUTHORITY; owner_reply_at: N/A

### A61

- File: [docs/ai_workload_research/runs/AI_ARCH_A61_IGB_SMALL_GNN_NATIVE_109_V1/FINAL_REPORT.md](https://github.com/swayhrl/accel-sim-framework/blob/37120f98186b83a946f4812755523f5d73245491/docs/ai_workload_research/runs/AI_ARCH_A61_IGB_SMALL_GNN_NATIVE_109_V1/FINAL_REPORT.md)
- Branch: `hrl/aiarch-a61-igb-small-gnn-native-109-v1`
- HEAD: `37120f98186b83a946f4812755523f5d73245491`
- Blob: `28b043b759870c32c115843f7d9784f16c0d7dcd`
- File commit_time: 2026-10-16T09:35:33+08:00
- content_observed_at: 2026-11-04T11:56:53+08:00; mode: READ_EXISTING_AUTHORITY; owner_reply_at: N/A

### A65

- File: [docs/ai_workload_research/runs/AI_ARCH_A65_IGB_SMALL_COMPILED_NUMERIC_109_V1/FINAL_REPORT.md](https://github.com/swayhrl/accel-sim-framework/blob/3cdf0489b0b3a2cbbb4081e6dd13044f7ec70f79/docs/ai_workload_research/runs/AI_ARCH_A65_IGB_SMALL_COMPILED_NUMERIC_109_V1/FINAL_REPORT.md)
- Branch: `hrl/aiarch-a65-igb-small-compiled-numeric-109-v1`
- HEAD: `3cdf0489b0b3a2cbbb4081e6dd13044f7ec70f79`
- Blob: `1ab8875628af4788bf1abe9bbc530b363e557d86`
- File commit_time: 2026-10-16T03:35:42Z
- content_observed_at: 2026-11-04T11:56:53+08:00; mode: READ_EXISTING_AUTHORITY; owner_reply_at: N/A

### A67

- File: [docs/ai_workload_research/runs/AI_ARCH_A67_IGB_SMALL_EAGER_SCOPE_BOUNDED_WALL_109_V1/FINAL_REPORT.md](https://github.com/swayhrl/accel-sim-framework/blob/c425819d1f41e0cbd3053315cd5590697e808a3c/docs/ai_workload_research/runs/AI_ARCH_A67_IGB_SMALL_EAGER_SCOPE_BOUNDED_WALL_109_V1/FINAL_REPORT.md)
- Branch: `hrl/aiarch-a67-igb-small-eager-scope-wall-109-v1`
- HEAD: `c425819d1f41e0cbd3053315cd5590697e808a3c`
- Blob: `e22778101114ac69edcf9da1201614c887e6bde5`
- File commit_time: 2026-10-16T04:23:20Z
- content_observed_at: 2026-11-04T11:56:53+08:00; mode: READ_EXISTING_AUTHORITY; owner_reply_at: N/A

### A79

- File: [docs/ai_workload_research/runs/AI_ARCH_A79_QWEN25_3B_NATIVE_WORKLOAD_SENSITIVITY_109_V1/FINAL_REPORT.md](https://github.com/swayhrl/accel-sim-framework/blob/1ad28dbe2fe7280aea46a24f6ba9a97c021b08b7/docs/ai_workload_research/runs/AI_ARCH_A79_QWEN25_3B_NATIVE_WORKLOAD_SENSITIVITY_109_V1/FINAL_REPORT.md)
- Branch: `hrl/aiarch-a79-qwen25-3b-native-workload-sensitivity-109-v1`
- HEAD: `1ad28dbe2fe7280aea46a24f6ba9a97c021b08b7`
- Blob: `31a4ea4af0026211fdf69ae28d2217b249ca9950`
- File commit_time: 2026-10-26T11:22:08+08:00
- content_observed_at: 2026-11-04T11:56:53+08:00; mode: READ_EXISTING_AUTHORITY; owner_reply_at: N/A

### A79_RUNTIME

- File: [docs/ai_workload_research/runs/AI_ARCH_A79_QWEN25_3B_NATIVE_WORKLOAD_SENSITIVITY_109_V1/SOURCE_AND_RUNTIME.json](https://github.com/swayhrl/accel-sim-framework/blob/1ad28dbe2fe7280aea46a24f6ba9a97c021b08b7/docs/ai_workload_research/runs/AI_ARCH_A79_QWEN25_3B_NATIVE_WORKLOAD_SENSITIVITY_109_V1/SOURCE_AND_RUNTIME.json)
- Branch: `hrl/aiarch-a79-qwen25-3b-native-workload-sensitivity-109-v1`
- HEAD: `1ad28dbe2fe7280aea46a24f6ba9a97c021b08b7`
- Blob: `e953557e90b506cbc8a77fffc477ec9dbdf2812e`
- File commit_time: 2026-10-26T11:18:49+08:00
- content_observed_at: 2026-11-04T11:56:53+08:00; mode: READ_EXISTING_AUTHORITY; owner_reply_at: N/A

### AI_STATE

- File: [docs/ai_workload_research/CURRENT_STATE.md](https://github.com/swayhrl/accel-sim-framework/blob/1ad28dbe2fe7280aea46a24f6ba9a97c021b08b7/docs/ai_workload_research/CURRENT_STATE.md)
- Branch: `hrl/aiarch-a79-qwen25-3b-native-workload-sensitivity-109-v1`
- HEAD: `1ad28dbe2fe7280aea46a24f6ba9a97c021b08b7`
- Blob: `9f906264aee17115bd005b344ec5702e274bd71e`
- File commit_time: 2026-10-16T22:01:31+08:00
- content_observed_at: 2026-11-04T11:56:53+08:00; mode: READ_EXISTING_AUTHORITY; owner_reply_at: N/A

### AWMA26

- File: [docs/vm_tlb/codex_handoff/awma/r26_tied_weight_production_capacity_v1/LANE_G_FINAL_REPORT.md](https://github.com/swayhrl/accel-sim-framework/blob/1a2485011b300cddd5137bbccb91dd6d30cfc22f/docs/vm_tlb/codex_handoff/awma/r26_tied_weight_production_capacity_v1/LANE_G_FINAL_REPORT.md)
- Branch: `hrl/awma-r26-tied-weight-production-capacity-109-v1`
- HEAD: `1a2485011b300cddd5137bbccb91dd6d30cfc22f`
- Blob: `7eaad36c4f26728902e3b94d7074225e23633f1d`
- File commit_time: 2026-10-02T23:45:22+08:00
- content_observed_at: 2026-11-04T11:56:53+08:00; mode: READ_EXISTING_AUTHORITY; owner_reply_at: N/A

### AWMA27R2

- File: [docs/vm_tlb/codex_handoff/awma/r27r2_varied_batch_capacity_seeded_continuation_v1/LANE_G_FINAL_REPORT.md](https://github.com/swayhrl/accel-sim-framework/blob/ba73fa0bacf3db09f44d8ad421a0a36f56645898/docs/vm_tlb/codex_handoff/awma/r27r2_varied_batch_capacity_seeded_continuation_v1/LANE_G_FINAL_REPORT.md)
- Branch: `hrl/awma-r27r2-varied-batch-capacity-109-v1`
- HEAD: `ba73fa0bacf3db09f44d8ad421a0a36f56645898`
- Blob: `e647684d0e50864575703d2ea8cfb8fba0bb128b`
- File commit_time: 2026-10-03T09:55:44+08:00
- content_observed_at: 2026-11-04T11:56:53+08:00; mode: READ_EXISTING_AUTHORITY; owner_reply_at: N/A

### AWMA27R3

- File: [docs/vm_tlb/codex_handoff/awma/r27r3_numeric_attribution_capacity_v1/LANE_G_FINAL_REPORT.md](https://github.com/swayhrl/accel-sim-framework/blob/7bd31fae4c54e121d54743a803d978ee02a64959/docs/vm_tlb/codex_handoff/awma/r27r3_numeric_attribution_capacity_v1/LANE_G_FINAL_REPORT.md)
- Branch: `hrl/awma-r27r3-numeric-attribution-capacity-109-v1`
- HEAD: `7bd31fae4c54e121d54743a803d978ee02a64959`
- Blob: `ccb1f0012cf7c530076c1eab0b389b55e2c5c789`
- File commit_time: 2026-10-13T10:44:15+08:00
- content_observed_at: 2026-11-04T11:56:53+08:00; mode: READ_EXISTING_AUTHORITY; owner_reply_at: N/A

### AWMA_STATE

- File: [docs/vm_tlb/chatgpt_handoff/awma/context_2026_10_02_r23g_active/AWMA_PROJECT_HANDOFF_CONTEXT_2026-10-02_R23G_ACTIVE.md](https://github.com/swayhrl/accel-sim-framework/blob/2b96d94ed79f0fb2a3360aa55c3f0184a590c523/docs/vm_tlb/chatgpt_handoff/awma/context_2026_10_02_r23g_active/AWMA_PROJECT_HANDOFF_CONTEXT_2026-10-02_R23G_ACTIVE.md)
- Branch: `hrl/awma-main-context-r23g-active-20261002-v1`
- HEAD: `2b96d94ed79f0fb2a3360aa55c3f0184a590c523`
- Blob: `0e7d2481440d5e8a465bf67764e4dafdf5e4eb4d`
- File commit_time: 2026-10-02T14:56:30+08:00
- content_observed_at: 2026-11-04T11:56:53+08:00; mode: READ_EXISTING_AUTHORITY; owner_reply_at: N/A

### DTC16

- File: [docs/dtc_l1/review_packs/DTC_STAGE_IIA_FIRST16_CH_MATCH_20261104_V1/README.md](https://github.com/swayhrl/accel-sim-framework/blob/5f67b4d6b94568a9f1acc80c3e56736bd81e4753/docs/dtc_l1/review_packs/DTC_STAGE_IIA_FIRST16_CH_MATCH_20261104_V1/README.md)
- Branch: `hrl/dtc-stage-iia-first16-execution-20261104-v1`
- HEAD: `5f67b4d6b94568a9f1acc80c3e56736bd81e4753`
- Blob: `3e85cc49cb1a2857060c3e49b8508ce18036d018`
- File commit_time: 2026-11-04T00:20:25+00:00
- content_observed_at: 2026-11-04T11:56:53+08:00; mode: READ_EXISTING_AUTHORITY; owner_reply_at: N/A

### DTC48

- File: [docs/dtc_l1/review_packs/DTC_STAGE_IIA_REMAINING48_CH_MATCH_20261104_V1/LATEST_STATUS.json](https://github.com/swayhrl/accel-sim-framework/blob/42ccc66c3e2e3be9a214b27fc477919a290a17c2/docs/dtc_l1/review_packs/DTC_STAGE_IIA_REMAINING48_CH_MATCH_20261104_V1/LATEST_STATUS.json)
- Branch: `hrl/dtc-stage-iia-remaining48-execution-20261104-v1`
- HEAD: `42ccc66c3e2e3be9a214b27fc477919a290a17c2`
- Blob: `bc32d8c61bee7589cf04a130fa95d993eba19cb5`
- File commit_time: 2026-11-04T03:26:23+00:00
- content_observed_at: 2026-11-04T11:56:53+08:00; mode: READ_EXISTING_AUTHORITY; owner_reply_at: N/A

### DTC48_README

- File: [docs/dtc_l1/review_packs/DTC_STAGE_IIA_REMAINING48_CH_MATCH_20261104_V1/README.md](https://github.com/swayhrl/accel-sim-framework/blob/42ccc66c3e2e3be9a214b27fc477919a290a17c2/docs/dtc_l1/review_packs/DTC_STAGE_IIA_REMAINING48_CH_MATCH_20261104_V1/README.md)
- Branch: `hrl/dtc-stage-iia-remaining48-execution-20261104-v1`
- HEAD: `42ccc66c3e2e3be9a214b27fc477919a290a17c2`
- Blob: `8ce242157abe2c4f46bdefdc85fd8a82c105b247`
- File commit_time: 2026-11-04T03:06:45+00:00
- content_observed_at: 2026-11-04T11:56:53+08:00; mode: READ_EXISTING_AUTHORITY; owner_reply_at: N/A

### DTC_AE

- File: [docs/dtc_l1/review_packs/DTC_AE_V100_FULL_SWEEP_20261025_V1/r20_archive_namespace_completion_20261027_v1/README.md](https://github.com/swayhrl/accel-sim-framework/blob/b7a654356b75caeb45fbec392eb488151c600a9e/docs/dtc_l1/review_packs/DTC_AE_V100_FULL_SWEEP_20261025_V1/r20_archive_namespace_completion_20261027_v1/README.md)
- Branch: `hrl/dtc-ae-v100-full-sweep-174new-20261025-v1`
- HEAD: `b7a654356b75caeb45fbec392eb488151c600a9e`
- Blob: `5712f687ee07f1d1398e27d16bd64fabd23382a3`
- File commit_time: 2026-10-27T00:08:46+00:00
- content_observed_at: 2026-11-04T11:56:53+08:00; mode: READ_EXISTING_AUTHORITY; owner_reply_at: N/A

### DTC_INPUT

- File: [docs/dtc_l1/review_packs/DTC_STAGE_IIA_REMAINING48_CH_MATCH_20261104_V1/independent_reviews/B_completed_short_programs_v1/INPUT_AND_CAPTURE_BINDINGS.json](https://github.com/swayhrl/accel-sim-framework/blob/42ccc66c3e2e3be9a214b27fc477919a290a17c2/docs/dtc_l1/review_packs/DTC_STAGE_IIA_REMAINING48_CH_MATCH_20261104_V1/independent_reviews/B_completed_short_programs_v1/INPUT_AND_CAPTURE_BINDINGS.json)
- Branch: `hrl/dtc-stage-iia-remaining48-execution-20261104-v1`
- HEAD: `42ccc66c3e2e3be9a214b27fc477919a290a17c2`
- Blob: `c9f3b4e287edbaa7505ae4b942b358468f2f8826`
- File commit_time: 2026-11-04T03:26:23+00:00
- content_observed_at: 2026-11-04T11:56:53+08:00; mode: READ_EXISTING_AUTHORITY; owner_reply_at: N/A

### DTC_ONE_INPUT

- File: [docs/dtc_l1/review_packs/DTC_STAGE_IIA_REMAINING48_CH_MATCH_20261104_V1/independent_reviews/B_scalarProd_F256_v1/ACTUAL_INPUT_CONTRACT.json](https://github.com/swayhrl/accel-sim-framework/blob/42ccc66c3e2e3be9a214b27fc477919a290a17c2/docs/dtc_l1/review_packs/DTC_STAGE_IIA_REMAINING48_CH_MATCH_20261104_V1/independent_reviews/B_scalarProd_F256_v1/ACTUAL_INPUT_CONTRACT.json)
- Branch: `hrl/dtc-stage-iia-remaining48-execution-20261104-v1`
- HEAD: `42ccc66c3e2e3be9a214b27fc477919a290a17c2`
- Blob: `feecd57321603d47df0956ae43ec0ed2d71c0e4f`
- File commit_time: 2026-11-04T03:26:23+00:00
- content_observed_at: 2026-11-04T11:56:53+08:00; mode: READ_EXISTING_AUTHORITY; owner_reply_at: N/A

### E1

- File: [docs/vm_tlb/review_packs/C16_E1_PAPER_EVIDENCE_AND_RESULT_INFRASTRUCTURE_V1/README.md](https://github.com/swayhrl/accel-sim-framework/blob/a402828860ced26124ddbf3c9d87baa6f6774d55/docs/vm_tlb/review_packs/C16_E1_PAPER_EVIDENCE_AND_RESULT_INFRASTRUCTURE_V1/README.md)
- Branch: `hrl/c16-e1-paper-evidence-results-v1`
- HEAD: `a402828860ced26124ddbf3c9d87baa6f6774d55`
- Blob: `d2c0bd77faebdb87599b0397a60e7dac8f3ba7b0`
- File commit_time: 2026-09-27T03:26:02Z
- content_observed_at: 2026-11-04T11:56:53+08:00; mode: READ_EXISTING_AUTHORITY; owner_reply_at: N/A

### EP_CLOSE

- File: [docs/ep_l2/operations/ep_performance_first_v2_20261103_v1/activation_20261104_v1/recovery_20261104_v1/concurrency10_20261104_v1/closeout_20261104_v1/FINAL_SCIENTIFIC_REPORT.md](https://github.com/swayhrl/accel-sim-framework/blob/f6e39296ef3a4bb26c237119c9c4a67e4667350e/docs/ep_l2/operations/ep_performance_first_v2_20261103_v1/activation_20261104_v1/recovery_20261104_v1/concurrency10_20261104_v1/closeout_20261104_v1/FINAL_SCIENTIFIC_REPORT.md)
- Branch: `hrl/ep-l2-performance-first-v2-20261103-v1`
- HEAD: `f6e39296ef3a4bb26c237119c9c4a67e4667350e`
- Blob: `949d1d867418839838aee2b7b1511d982c9911a3`
- File commit_time: 2026-11-04T03:15:03+00:00
- content_observed_at: 2026-11-04T11:56:53+08:00; mode: READ_EXISTING_AUTHORITY; owner_reply_at: N/A

### EP_INPUT

- File: [docs/ep_l2/operations/ep_performance_first_v2_20261103_v1/activation_20261104_v1/agent_b_binding/ACTUAL_SOURCE_RO_INPUT_BINDING_INDEX.json](https://github.com/swayhrl/accel-sim-framework/blob/f6e39296ef3a4bb26c237119c9c4a67e4667350e/docs/ep_l2/operations/ep_performance_first_v2_20261103_v1/activation_20261104_v1/agent_b_binding/ACTUAL_SOURCE_RO_INPUT_BINDING_INDEX.json)
- Branch: `hrl/ep-l2-performance-first-v2-20261103-v1`
- HEAD: `f6e39296ef3a4bb26c237119c9c4a67e4667350e`
- Blob: `ca53b1af8de295c488ed5b6465f2c3e36c53327c`
- File commit_time: 2026-11-03T18:02:52+00:00
- content_observed_at: 2026-11-04T11:56:53+08:00; mode: READ_EXISTING_AUTHORITY; owner_reply_at: N/A

### EP_MECH

- File: [docs/ep_l2/operations/ep_mechanism_attribution_20261103_v1/README.md](https://github.com/swayhrl/accel-sim-framework/blob/2ba12fe7dd427b6791a0688a53f6c866d885f310/docs/ep_l2/operations/ep_mechanism_attribution_20261103_v1/README.md)
- Branch: `hrl/ep-l2-mechanism-attribution-20261103-v1`
- HEAD: `2ba12fe7dd427b6791a0688a53f6c866d885f310`
- Blob: `31106dd630b744a88837626259d58589ba05a2ab`
- File commit_time: 2026-11-03T09:18:27+00:00
- content_observed_at: 2026-11-04T11:56:53+08:00; mode: READ_EXISTING_AUTHORITY; owner_reply_at: N/A

### NEQUIP

- File: [docs/ai_workload_research/review_packs/AI_ARCH_NEQUIP_STATIC_BATCH_DISCOVERY_109_V1R1/FINAL_REPORT.md](https://github.com/swayhrl/accel-sim-framework/blob/1f69559df4f51290589de72876f36a756c5439f0/docs/ai_workload_research/review_packs/AI_ARCH_NEQUIP_STATIC_BATCH_DISCOVERY_109_V1R1/FINAL_REPORT.md)
- Branch: `hrl/aiarch-nequip-static-batch-109-v1r1`
- HEAD: `1f69559df4f51290589de72876f36a756c5439f0`
- Blob: `7f2a0ea009cee93555904dac7a9deed500061ccc`
- File commit_time: 2026-10-13T21:10:00+08:00
- content_observed_at: 2026-11-04T11:56:53+08:00; mode: READ_EXISTING_AUTHORITY; owner_reply_at: N/A

### R26_PARENT

- File: [docs/vm_tlb/review_packs/AWMA_R26_TIED_WEIGHT_PRODUCTION_CAPACITY_BOUNDARY_109_V1/COMMON_START_STATE.json](https://github.com/swayhrl/accel-sim-framework/blob/1a2485011b300cddd5137bbccb91dd6d30cfc22f/docs/vm_tlb/review_packs/AWMA_R26_TIED_WEIGHT_PRODUCTION_CAPACITY_BOUNDARY_109_V1/COMMON_START_STATE.json)
- Branch: `hrl/awma-r26-tied-weight-production-capacity-109-v1`
- HEAD: `1a2485011b300cddd5137bbccb91dd6d30cfc22f`
- Blob: `281f1e97f9750a322a937755a97e51901e7fca71`
- File commit_time: 2026-10-02T23:45:22+08:00
- content_observed_at: 2026-11-04T11:56:53+08:00; mode: READ_EXISTING_AUTHORITY; owner_reply_at: N/A

### R27_PARENT

- File: [docs/vm_tlb/review_packs/AWMA_R27R2_TIED_WEIGHT_VARIED_BATCH_CAPACITY_STABILITY_109_V1/PARENT_SEED_QUALIFICATION.json](https://github.com/swayhrl/accel-sim-framework/blob/ba73fa0bacf3db09f44d8ad421a0a36f56645898/docs/vm_tlb/review_packs/AWMA_R27R2_TIED_WEIGHT_VARIED_BATCH_CAPACITY_STABILITY_109_V1/PARENT_SEED_QUALIFICATION.json)
- Branch: `hrl/awma-r27r2-varied-batch-capacity-109-v1`
- HEAD: `ba73fa0bacf3db09f44d8ad421a0a36f56645898`
- Blob: `add6febe4117d416cdcf69a357b74e4379e7b090`
- File commit_time: 2026-10-03T09:55:44+08:00
- content_observed_at: 2026-11-04T11:56:53+08:00; mode: READ_EXISTING_AUTHORITY; owner_reply_at: N/A

### R27_SWITCH

- File: [docs/vm_tlb/review_packs/AWMA_R27R2_TIED_WEIGHT_VARIED_BATCH_CAPACITY_STABILITY_109_V1/B1_CHECKPOINT_SWITCH_QUALIFICATION.json](https://github.com/swayhrl/accel-sim-framework/blob/ba73fa0bacf3db09f44d8ad421a0a36f56645898/docs/vm_tlb/review_packs/AWMA_R27R2_TIED_WEIGHT_VARIED_BATCH_CAPACITY_STABILITY_109_V1/B1_CHECKPOINT_SWITCH_QUALIFICATION.json)
- Branch: `hrl/awma-r27r2-varied-batch-capacity-109-v1`
- HEAD: `ba73fa0bacf3db09f44d8ad421a0a36f56645898`
- Blob: `07f979b5921b3d47b2a0fb790053a0b9ddf9ea5e`
- File commit_time: 2026-10-03T09:55:44+08:00
- content_observed_at: 2026-11-04T11:56:53+08:00; mode: READ_EXISTING_AUTHORITY; owner_reply_at: N/A

### STAGEA_CANARY

- File: [docs/vm_tlb/review_packs/C16_STAGEA_RUNTIME_QUALIFICATION_CANARY_109_V1/FINAL_INTERPRETATION.md](https://github.com/swayhrl/accel-sim-framework/blob/3f62f909a474e4c56695ffacf36ddcb5d7b5f147/docs/vm_tlb/review_packs/C16_STAGEA_RUNTIME_QUALIFICATION_CANARY_109_V1/FINAL_INTERPRETATION.md)
- Branch: `hrl/c16-stagea-runtime-qualification-canary-109-v1`
- HEAD: `3f62f909a474e4c56695ffacf36ddcb5d7b5f147`
- Blob: `4ef6cd02b9608aad0379b4af7c784064202f06d2`
- File commit_time: 2026-10-01T23:55:55+08:00
- content_observed_at: 2026-11-04T11:56:53+08:00; mode: READ_EXISTING_AUTHORITY; owner_reply_at: N/A

### STAGEA_TERMINAL

- File: [docs/vm_tlb/chatgpt_handoff/c16/C16_STAGEA_TERMINAL_CURRENT_STATE.md](https://github.com/swayhrl/accel-sim-framework/blob/ccd6928bfb420d1e4c554ec0e377bb8fbe377501/docs/vm_tlb/chatgpt_handoff/c16/C16_STAGEA_TERMINAL_CURRENT_STATE.md)
- Branch: `hrl/c16-stagea-terminal-independent-consumer-174new-v1`
- HEAD: `ccd6928bfb420d1e4c554ec0e377bb8fbe377501`
- Blob: `a23f959d81b5b585185078f7097822b83a39c74b`
- File commit_time: 2026-10-02T12:18:48+00:00
- content_observed_at: 2026-11-04T11:56:53+08:00; mode: READ_EXISTING_AUTHORITY; owner_reply_at: N/A

### V2_ARC

- File: [docs/storage/node109/20261104/v2_non_imagelab_reclaim/NON_IMAGELAB_TRUE164_ARCHIVE_CLOSURE.csv](https://github.com/swayhrl/accel-sim-framework/blob/0915c630a740dc863505ce86012440be322117cb/docs/storage/node109/20261104/v2_non_imagelab_reclaim/NON_IMAGELAB_TRUE164_ARCHIVE_CLOSURE.csv)
- Branch: `hrl/node109-non-imagelab-reclaim-v2-20261104`
- HEAD: `0915c630a740dc863505ce86012440be322117cb`
- Blob: `bca5c8892c46a2b4742fc3c183307ab6bd59f58b`
- File commit_time: 2026-11-04T11:15:32+08:00
- content_observed_at: 2026-11-04T11:56:53+08:00; mode: READ_EXISTING_AUTHORITY; owner_reply_at: N/A

### V2_DEP

- File: [docs/storage/node109/20261104/v2_non_imagelab_reclaim/SCIENTIFIC_READER_DEPENDENCY_AUDIT.md](https://github.com/swayhrl/accel-sim-framework/blob/0915c630a740dc863505ce86012440be322117cb/docs/storage/node109/20261104/v2_non_imagelab_reclaim/SCIENTIFIC_READER_DEPENDENCY_AUDIT.md)
- Branch: `hrl/node109-non-imagelab-reclaim-v2-20261104`
- HEAD: `0915c630a740dc863505ce86012440be322117cb`
- Blob: `57dd3927a21e067e25d8f03ef83822a4d445b063`
- File commit_time: 2026-11-04T11:15:32+08:00
- content_observed_at: 2026-11-04T11:56:53+08:00; mode: READ_EXISTING_AUTHORITY; owner_reply_at: N/A

### V2_FINAL

- File: [docs/storage/node109/20261104/v2_non_imagelab_reclaim/FINAL_REPORT.md](https://github.com/swayhrl/accel-sim-framework/blob/0915c630a740dc863505ce86012440be322117cb/docs/storage/node109/20261104/v2_non_imagelab_reclaim/FINAL_REPORT.md)
- Branch: `hrl/node109-non-imagelab-reclaim-v2-20261104`
- HEAD: `0915c630a740dc863505ce86012440be322117cb`
- Blob: `6ffaebee479ac8999e383540a37c57d80529a296`
- File commit_time: 2026-11-04T11:15:32+08:00
- content_observed_at: 2026-11-04T11:56:53+08:00; mode: READ_EXISTING_AUTHORITY; owner_reply_at: N/A

### V2_INV

- File: [docs/storage/node109/20261104/v2_non_imagelab_reclaim/NON_IMAGELAB_COLD_ASSET_INVENTORY.csv](https://github.com/swayhrl/accel-sim-framework/blob/0915c630a740dc863505ce86012440be322117cb/docs/storage/node109/20261104/v2_non_imagelab_reclaim/NON_IMAGELAB_COLD_ASSET_INVENTORY.csv)
- Branch: `hrl/node109-non-imagelab-reclaim-v2-20261104`
- HEAD: `0915c630a740dc863505ce86012440be322117cb`
- Blob: `8eaecff4f04704565dcae6952b929790ee60c373`
- File commit_time: 2026-11-04T11:15:32+08:00
- content_observed_at: 2026-11-04T11:56:53+08:00; mode: READ_EXISTING_AUTHORITY; owner_reply_at: N/A

### V2_SPACE

- File: [docs/storage/node109/20261104/v2_non_imagelab_reclaim/SSD_RECLAIM_OPPORTUNITY_SUMMARY.md](https://github.com/swayhrl/accel-sim-framework/blob/0915c630a740dc863505ce86012440be322117cb/docs/storage/node109/20261104/v2_non_imagelab_reclaim/SSD_RECLAIM_OPPORTUNITY_SUMMARY.md)
- Branch: `hrl/node109-non-imagelab-reclaim-v2-20261104`
- HEAD: `0915c630a740dc863505ce86012440be322117cb`
- Blob: `1ceee826f69c45cb5103d7dd2dc766da7e658b15`
- File commit_time: 2026-11-04T11:15:32+08:00
- content_observed_at: 2026-11-04T11:56:53+08:00; mode: READ_EXISTING_AUTHORITY; owner_reply_at: N/A

## Interpretation boundary

All source paths/HEADs above are immutable evidence anchors. No source was promoted into a new owner reply or a dated future plan. Historical archive/SHA statements were read, not rerun. The five S109 V2 inputs remain unmodified.
