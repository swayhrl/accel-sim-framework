# 待 owner 确认的精确转交文本

状态：**NOT_SENT / NO_REPLY**。可直接交给各项目Main或科研owner；请保留对方原话、实际owner、项目branch/HEAD、状态文件路径、回复时间（含时区）和asset_id。U174没有可直接寻址的其它Codex窗口，不伪造已联系或已确认。以下均是科研使用问询，不授权启动实验、恢复、删除或改owner任务。

统一回复结构（每项资产分别回答，允许UNKNOWN；不得合并替别的项目授权）：

`asset_id | exact_source_path | project | actual_scientific_owner | branch | HEAD | status_file_or_reply | replied_at_with_timezone | running_direct_or_indirect_reader_and_task | next7d_with_date | next30d_with_date_or_probability | local_109_required_and_reason | restore_from_true164_accepted_Y_N_UNKNOWN | max_acceptable_restore_delay | exact_restore_prerequisites | irreplaceable_evidence_components | unfinished_or_paused_task | cold_tier_acceptance_Y_N_UNKNOWN | retention_objection`

窗口：2026-11-04T11:56:53+08:00起至2026-11-11T11:56:53+08:00 / 2026-12-04T11:56:53+08:00。任一方保留要求优先；owner未回复就维持OWNER_CONFIRMATION_PENDING。所谓“无需109常驻”必须说明恢复等待、离线包和规范证据责任。

## Q-EP｜发给 EP-L2 Main / 科研协调owner

我们是Lane U174，只做109跨项目资产使用审查，不动实验。已读EP Performance-First V2 @ f6e39296ef3a4bb26c237119c9c4a67e4667350e（16 accepted、11:04 +08自然结束）和机制归因 @ 2ba12fe7dd427b6791a0688a53f6c866d885f310。请确认你负责的**当前正式实验、未来7/30天参数探索、机制归因、暂停/拟续行**是否直接或经symlink/mount/预处理使用下列109资产：

- stagea_1/2 两个revision、Qwen3-30B exact revision；
- E1 `/data/c16/e1_bounded_decode_trace_v1`、`capture`、`rtx4080_suite_fill_20261024_v1`及shared env/wheelhouse；
- AWMA R26十个规范checkpoint、R27三个COMMON副本与B1_C1_K2；或明确你无权判断但确有间接读取。

已读索引未建立精确依赖，不代表你已确认不使用。请按统一八问逐asset答复，指出原始Trace与可再生成中间数据、仅需科研归档的接受/失败结果。你的答复只覆盖EP用途，不代表C16/AWMA/AI-ARCH同意冷存。哪些Source KEEP必须本地、在哪个节点，也请列精确路径。

## Q-DTC｜发给 DTC-L1 / DTC Stage-II 与 AE owner

我们已读first16 @5f67b4d6b94568a9f1acc80c3e56736bd81e4753、remaining48 @42ccc66c3e2e3be9a214b27fc477919a290a17c2。11:26 +08快照37 accepted/11 await、10 running；我们未干预owner/dispatcher。请确认当前Stage-II、AE及后续计划是否有109的模型/数据/历史native capture依赖，尤其上述StageA/Qwen3/E1/capture/RTX suite/env和R26/R27。

published trace路径在174 `/root/workspace/assets/traces/bundles/<bundle>/tree`，**请确认真实mount/symlink后端、间接reader、离线环境与恢复任务是否触及109**，不要只答“执行在174”。旧AE @b7a654356b75caeb45fbec392eb488151c600a9e 的10月27日状态已旧，请给当前权威状态文件和HEAD。逐项回答八问，指明当前运行、7/30天计划、原始证据保留、可接受164恢复等待；不得把本轮未授权的109实验提案写成已启动。

## Q-AI｜发给 AI-ARCH 项目协调者及各资产owner

请分别由A26GR1、A61/A65/A67、NequIP、A79真实使用方答复，不由单一执行lane替其它owner授权。

1. `context:aiarch_a26gr1_gsscale_rubble_109_20261014`：40.77GiB。官方Rubble压缩原包/解包图像与COLMAP、4x PNG、实际不同densification轨迹/原始观测、环境/wheels/cache各自需要保留什么？报告称raw/wheels未入164，也未产生完整可resume checkpoint。是否有后续质量/晚期GPU比较/分析计划、日期和owner？哪些可重建、哪些不能以再跑替代？
2. `context:aiarch_a61_igb_small_gnn_native_109_v1`：9.86GiB。A65 @3cdf0489b0b3a2cbbb4081e6dd13044f7ec70f79、A67 @c425819d1f41e0cbd3053315cd5590697e808a3c已实际复用其数据/环境。请核对A61官方tar/npy/CSC/split/order、A65冻结子图与失败pair、A67 raw、shared runtime/env/symlinks及编译cache，给全部使用方的7/30天分析/重派计划。不能只答A61已STOP。
3. `context:aiarch_nequip_static_batch_109_v1r1_20261013`：10.92GiB。444-file raw packet已有164，但整个环境/wheel闭包、原model/input、AOT compiled身份和224 binary cache是否完整可恢复？独立科学review/进一步分析还需本地哪些组件？确认原始timing/数值输出不被丢弃。
4. `stagea_1`：A79 @1ad28dbe2fe7280aea46a24f6ba9a97c021b08b7 的SOURCE_AND_RUNTIME.json精确指向 `/data/c16/stagea_runtime_qualification_v1/assets/qwen2.5-3b-instruct/aa8e72537993ba99e69dfaafa59ed015b17504d1`。GPU_RESOURCE_DEFERRED后是否计划重新派发？7/30天何时？是否必须109常驻，或接受恢复后重新资格？请与C16共同答复。
5. 是否还有GSSCALE/Rubble其它3DGS资产、A26/A61/NequIP关联数据或当前109GPU任务未进入本V2台账？只提供精确路径和已有状态，不启动新扫描/实验。

## Q-C16｜发给 C16 StageA / E1 owner

已读runtime canary @3f62f909a474e4c56695ffacf36ddcb5d7b5f147及terminal consumer @ccd6928bfb420d1e4c554ec0e377bb8fbe377501：旧campaign停止，但Tier0 terminal仍PARTIAL、DQ问题incomplete。请分别确认：

- `stagea_1` BF16（5.76GiB）与`stagea_2` AWQ（2.51GiB）是否有当前、7天或30天资格/参数/归因/对照用途？是否只保留规范证据即可？能否接受真164按原绝对路径恢复、需要多少提前量？不要将PARTIAL直接改成ABANDONED。
- AI-ARCH A79同精确BF16路径用途是否已经协调？单方关闭StageA不能覆盖AI-ARCH。
- E1 43.29GiB原始/失败Trace、capture8.37GiB、RTX suite11.74GiB、merged_gate_up8.57GiB及env/wheelhouse的实际owner和未完成任务是什么？E1论文/consumer证据链哪些必须保留、哪些中间数据确实可再生成？
- 你是否授权对Qwen3的C16使用范围冷存？AWMA用途由AWMA另答。已退役OLMoE/Llama本地0GiB不在本轮回收量内。

## Q-AWMA｜发给 AWMA Lane G / 主协调者及缓存三线owner

逐项按八问回复，不以R27数值STOP或Qwen模型已有归档替代使用判断：

- `awma_http_cache_1` R19 FP8、`_2` R17 graph、`_3` VLA RTC，合计8.49GiB：未来环境重建/离线依赖是否需要原HTTP bodies？有无唯一sdist/yanked wheel、平台特定包或网络不可达来源？请给已存在的pinned requirements、wheel/source hash与可用wheelhouse状态；未验证就保留。我们不运行pip重建。是否接受独立冷存/可重建资格方案？
- `awma_r27_file_1/2/4`三个COMMON父副本，7.34GiB：近期是否直接本地读取/续行？能否从R26规范COMMON按各原路径恢复，允许多长等待？是否有独立本地副本必要？R26 COMMON先保留；三路径不能混成一次同inode回收。
- `qwen3_30b_revision` 56.89GiB：请明确AWMA与C16未来7/30天模型计划及runnable脚本是否仍可派发，是否接受冷恢复、恢复容量预留和runtime前提。EP/DTC未引用不能代表AWMA不需要。
- `awma_r26_checkpoint_1..10` 24.46GiB：确认正式lineage和长期保留责任。COMMON_START_STATE有receipt-only hash差异、单次accepted derivation，不能以重跑再生成替代。逐checkpoint能否冷存、规范manifest及恢复责任是谁？
- `awma_r27_file_3` B1_C1_K2，2.45GiB：fresh-load/switch虽通过，整体数值STOP是否计划继续归因？是否要保留109本地？
- `awma_r27_file_5/6` B0 raw：原始repeatability反例、全部统计与未执行后续状态如何保留？不在候选回收组合。
- AWMA_STATE的10月2日R23G active已旧，请提供当前权威分支/HEAD与状态；不要按旧ACTIVE冒充当前，也不要重启旧任务。

## Q-S109｜转交 Lane S109（不修改其执行范围）

请核对U174新增科学依赖与V2台账：A79同stagea_1、A65/A67复用A61、NequIP局部raw归档不等整树、R26精确artifact不可随意再生成。V2 archive CSV中B1/B0的通用parent-copy措辞请按其独立目标路径复核。候选P1为cache+三个R27父副本约15.83GiB，当前科学ready为0。

收到真实owner回复后，由S109在自己的任务内决定是否及如何闭合当前文件身份、真164/SHA、reader、恢复资格、块量与精确白名单；U174不要求干预V3、不启动额外全量SHA。科学owner与技术台账有分歧时请双方保留原证据并复核，不相互覆盖。任何实际删除均等待用户另行授权。

本文件交付后STOP；没有预设owner肯定答复，也不自动安排问询或实验。
