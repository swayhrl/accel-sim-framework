# EP-L2：109 历史工作调查与 API 接管上下文

日期：2026-11-09（Asia/Shanghai）。用途：供全新本机 API Codex 会话 `109-EP-L2` 读取，接手 EP 在109侧的历史资产、采集工具和后续联络职责。本包由科学审查窗口依据固定 GitHub 记录整理；**尚未访问109现场，尚未证明109接管完成，不是新的GPU采集或科学实验授权。**

## 0. 当前状态与责任

- EP-L2 唯一科学 Main 是本机 API 会话 `EP-L2交接-1`，简称 **EP-L2 Main**，在174-new执行。原 Main 只保留历史查询，不是第二个调度owner。
- 用户在本次对话明确确认：五点执行指令已经给入 EP-L2 Main。本包未取得随后激活/登记/消费/完成回执，不能推断五点已全部启动、同时运行或完成；也不能继续把接管前的“批准0/登记0/消费0”当成现在的实时状态。
- 08fc完整交接及eb41接管回执曾纠正更早聊天的“五点已经运行”。这些都是有时间边界的记录。**用户具体指令决定允许做什么；实际登记、执行与结果回执决定已做什么。**
- 当前主线 Performance-First：提高Victim/Payload资源效率，保留真实结构成本与正/负/零收益。RO为辅助；不恢复论文写作或非必要细归因。
- 当前Main精确范围：GEMM EXT0/1/2、Stencil EXT0/2；同A Source5、WV_ZERO_RO、G32×8、850MHz/L100、完整283项、3+2两个独立族。109不参与这批CPU模拟，不替换输入，不补新trace，不创建dispatcher。
- 最近完成科学基点为UMT1 `eae40596cb9a550785a50a3d64617686a6daa160`；当前工程基点 `ea480a05fb32eeb6b88dd1d8be1b0b9c89eb8526`。A Core为 `3d3887bb2e8d5073d13b0792ff9116834e89fe2f`；编译Framework为 `9dd1ee57a83d83b56b7874bc7c716185ab52c8f7`；ELF SHA256为 `9db48c06ca64e441b5824071f52e0aa0be50374045fbdcef6cdf5d4469182f86`。这些只用于识别当前Main主线，不是要求109重建或验证。
- 真164保存大资产。115项历史迁移不重做；Source KEEP。独立CLEAN C、额外RO/输入/GPU/论文工作均不属于本轮。

主线依据：[完整交接][E01]、[Main接管回执][E02]。用户随后确认“已经给入执行”是本包明确记录的对话增量，不伪装为Git执行回执。

## 1. 调查结论

**109确实做过与EP-L2有关的工作，主体是共享RTX4080/SM89 Trace资产链。** 它由EP操作记录协调，同时供多个研究项目使用；部分目录在 `/data/c16/`，部分工具复用AWMA工作树，不能由路径名称推断专属归属。

该链的分工是109真实GPU原生核对与采集，174-new接收、CPU后处理、工程消费者审查与公共目录发布，真164长期保存。早期EP校准中的“native DRAM”则指模拟器原有DRAM统计，不能列为109真实GPU校准成果。[E04][E06][E20]

### 1.1 已核历史任务

| 工作 | 109实际承担部分 | 已核结论与保留边界 | 固定证据 |
|---|---|---|---|
| 2026-10-16已有SpMV来源 | DTC原生覆盖任务生产SpMV/LayerNorm；EP后来的资产调查引用其来源 | SpMV有4个完整kernel、真实RTX4080身份与164回执；原owner为DTC。引用不转移DTC执行权，也不证明EP已消费该输入 | E03、E04 |
| 2026-10-24 VectorAdd4M试点 | 原生数值核对、完整SASS采集、109到164传输链 | 第3次capture成功；15,625CTA、125,000warps、2,125,000records。原格式仍SIM_ISA_HOLD；前2次exit0但无trace，attempt1 stdout被覆盖的缺口保留 | E04、E05 |
| 普通应用批量资产 | 共享suite原生核对与采集；固定source/input/binary/tool/GPU/attempt | 174-new另管CPU后处理、接收与公共发布。目录里的旧pending/running不构成今日启动授权 | E06、E16 |
| CUDA/SDK/PolyBench准备子Lane | 固定源码与输入分母、私有构建、原生运行、数值/平台分流 | Phase5明确该子Lane的native supervisors已终结、GPU锁已释放；它没有生产正式trace或运行模拟器。不能由此推出整个109今天空闲 | E07、E08 |
| Ada7普通语义与C8输入观察 | typed寄存器/宽度/谓词/constant记录修复，实际GPU正负例，HtoD主机源字节观察 | 同producer完整记录资格是有限profile。C8不是完整CUDA初始状态快照，也不自动授予consumer或timing资格 | E09、E10 |
| Ada8/9扩展工程 | embedded CALL/RET、实际JIT loaded cubin、WARPSYNC、旧Driver launch、LINEAR-U32 texture、NN观测I/O等受限fixture | 109生产证据与174-new的有限消费者验证分开。174-new工程consumer campaign最终8/8消费，不退款；这不是109 GPU采集次数或当前EP科学预算。CALL旧失败等保留，没有全suite或EP科学晋升 | E11、E12、E13、E14、E15 |
| 大Stencil闭合 | 原100-kernel GPU capture沿用 | 后续grouping、retained-byte恢复、COPY、完整Native cold与catalog关闭在174-new完成；不需109重采，不重做已关闭CPU链 | E17 |

### 1.2 原生可运行、数值、采集、归档和科学接受要分别记账

CUDA Samples v11.8的最终原生准备表记录205个源码名称、187条实际ELF程序路线、255次实际native尝试，182个名称至少有一条exit0路线。SDK4.2.9为82个名称、91次尝试、81个名称有原始或明确变体的exit0路线。其余平台需求、原失败与修改后的variant均保留。这些不是182/81个正式trace，也不是一揽子数值或EP性能PASS。[E08]

失败后改过输入、Host代码或GPU kernel的变体有独立身份，不能替canonical结果。既有source fabs检查不含显式finite guard时，不能升级为更强数值保证。采集exit0但没有callback/trace也是失败；工具或consumer能解析不等于全程序捕获完整；归档SHA/恢复通过不等于某模拟器profile或硬件时序已获资格。[E04][E07][E08][E09][E16]

## 2. 工具谱系、关键反例和不能扩大解释的性质

### 2.1 普通Ada7与C8

普通Ada7冻结producer为：

`55c6f4829e8c92e11e0ab54496bf8f507f6cfa3a10cd01a857c6de147ee68b73`

历史109路径：

`/data/c16/ada_trace_semantics_20261024_v1/frozen/producer_v7_55c6f482/producer.so`

它保留原SM89/tracer7身份，补typed UR/P/UP、宽寄存器高半、隐式依赖、active/predicate mask与constant bank/byte offset。constant地址是符号身份，不冒充GPU物理地址。消费者的embedded-constant辅助操作是内部模型工作，不是额外GPU SASS。[E09]

C8观察输入的producer为：

`c8cfa41fcabc90ff962159b77cda4a7b6c3ba0dd12236bf5d41849d159ad1352`

历史109路径：

`/data/c16/ada_trace_extensions_v8_20261024_v1/frozen/producer_v7_input_c8cfa41fcabc_r2`

C8保持冻结普通device instrumentation，增加受限HtoD主机源字节、完成证明和context/launch日志。它不覆盖全部bank0、Memset、D2D、managed、graphics或任意copy API；Async host缓冲的完整存活期还需source规则。runtime-random observer/capture输入曾明确INPUT_DIFF，不能把source/seed一致当成实际数组字节相同。[E10]

### 2.2 扩展工程与原始失败

- 旧CALL消费者截断64-bit PC时曾“退出0、issued0”，不接受；独立Core64修复保留原始完整PC，不回改旧证据。[E11]
- WARPSYNC采用受限的whole-warp序列化工程模型；JIT核实际loaded SM89 cubin；旧Driver分别解码真实launch结构。这些都不证明一般硬件latency/overlap。[E12][E13]
- Ada9仅覆盖实际LINEAR unsigned32×1资源、一个context/object/launch、37线程与指定TLD形式；consumer最终接受不授予通用texture/surface、filtered/array或EP科学资格。[E14][E15]
- Ada9的旧环境变量名曾被忽略，以实际stdout flags为准；不事后改写采集设置，不因此自动重采。[E14]
- NN完整I/O与地址核验保留42764个输出范围；实际输入走sqrt fast path、动态CALL/RET为0，不能据此宣称NN动态调用已证明。V4仅加紧Host重放契约，不新增GPU或SIM。[E21][E23]
- 原simpleTemplates多context复用曾覆盖早期raw；不能通过重命名剩余文件恢复丢失证据。原prototype部分ELF曾被原地重建，无法承诺逐字重现全部失败版本。[E09][E10]

### 2.3 Stencil不重做

最终完整父对象：`ORD_LATE_stencil_c3e987b033b4_A002_CPU_ADOPT_V2`；派生对象在其后加 `_CTA_STRIDE_40_V1`。

原stride40尝试actual exit1完整保留；新的retained-byte恢复actual exit0，核100 kernels、2600 CTA、54,123,600 selected records，沿用原106个prepared文件。随后COPY、108成员完整Native恢复及目录发布已独立接受。新的恢复谱系不能将原失败改成PASS，也不声称重新读取完整父body作fresh比对。最终仍标consumer/timing NOT_GRANTED、historical crop equivalence NOT_CLAIMED。[E17]

这些历史SM89 Stencil对象不能仅因名称相同就替换当前五点中已冻结的Stencil输入。

## 3. 历史时间线与当前仍需核实的状态

| 时间/证据 | 当时记录 | 今天的使用方式 |
|---|---|---|
| 10月24日试点 | Vector4M完整采集与164读回闭合 | 继承结果/失败，不重跑 |
| 10月24～25日CUDA Phase5 | 准备子Lane终结；锁释放；没有正式trace/SIM产出 | 不恢复该native队列 |
| 10月25日Stencil最终关闭 | 25 full+25 derived版本；CPU恢复链闭合 | 版本数不是程序数，后续更晚目录可能增长 |
| 10月26日09:40～09:48资产快照 | 38 full+38 derived；242队列行=38 COMMITTED_VERIFIED+1 RUNNING+36 PENDING+161 SPECIALIST+4 FAILED_RETAINED+2 SUPERSEDED | 不是当前运行证明或续跑授权。需找该有限批次后续终态回执 |
| 11月4日存储盘点 | suite目录当时ACTIVE_PROTECTED；CUDA/PolyBench与两个Ada目录TARGET_UNVERIFIED | 不是今天活跃性证明；没有FD也不等于无用户或允许删除 |
| 11月4日已执行清理 | 精确38文件：R26九份、R27三份、Qwen3-30B二十六份 | 不含RTX4080 suite/Ada/EP采集，不能扩成EP资产释放许可 |
| 本次用户消息 | 已将五点执行指令给入唯一Main；另指定109-EP-L2做接管 | 109首轮只读盘点与文档，不继承新科学启动 |

10月26快照明确普通目录38份并非38个独立benchmark，派生计数不是额外完整应用；工程证据包也不能计入workload分母。[E16] 11月4跨项目报告没有取得owner直接新答复，所谓7/30天未知不是“确认不用”。[E18][E19][E22]

本次Git调查没有闭合：**当前109是否还有该共享链的进程、最新队列终态、各热目录今日是否仍在、是否存在更晚迁移/redirect、各公共对象现在的可达性。** 这些由首轮现场只读检查解决；本包不推断无活动采集。

## 4. 已证实的定位路径

所有路径都是固定历史记录中的定位线索，不代表已经核实今天存在；先核小型metadata与真实mount，不恢复大包来使路径“重新存在”。

| 节点/类别 | 历史路径 | 说明 |
|---|---|---|
| 109试点 | `/data/c16/rtx4080_asset_pilot_20261024_v1` | 原试点attempt与证据 |
| 109普通采集 | `/data/c16/rtx4080_suite_fill_20261024_v1` | 优先读control、已封receipt、manifest |
| 109在途目录 | `/data/c16/rtx4080_suite_fill_20261024_v1/local_staging/inflight` | 只定位与读取已关闭小证据，不读活动raw |
| 109任务私有挂载 | `/data/c16/rtx4080_suite_fill_20261024_v1/nas_rtx4080` | 历史经hrl174new桥接；不要擅自重挂载 |
| 109 Ada7 | `/data/c16/ada_trace_semantics_20261024_v1` | 冻结普通producer、对照、失败 |
| 109 Ada8/C8 | `/data/c16/ada_trace_extensions_v8_20261024_v1` | 输入观察与专项producer |
| 109源码准备 | `/home/huangrulin/workspace/rtx4080_cuda_polybench_20261024_v1` | manifests、native_control、private build/inputs |
| 109历史tracer工具 | `/home/huangrulin/workspace/worktrees/accel-sim-awma-simcompat-v1/util/tracer_nvbit/tracer_tool` | 复用工具，不转移AWMA项目职责 |
| 109共享GPU锁 | `/data/c16/locks/c16_gpu_campaign.lock` | 只查当前owner，不获取、重建、清空或释放 |
| 更早DTC共享来源 | `/data/c16/dtc_native_coverage_109_v1` | 只读来源引用，不接管DTC执行 |
| 174-new资产控制 | `/root/data/shared_rtx4080_trace_library_20261024_v1/control` | 不由109新窗口启动/接管publisher或dispatcher |
| 174-new公共入口 | `/root/workspace/assets/traces/rtx4080_sm89/bulk_20261024_v1` | 历史reader：`/root/workspace/assets/bin/trace-assets-rtx4080` |
| 真164 canonical根 | `/home/shared/huangrulin/traces/rtx4080_sm89` | bulk下objects与不可变COMMIT/MANIFEST |
| 174-new真164视图 | `/root/share/mnt164/huangrulin/traces/rtx4080_sm89` | 路径名本身不证明真实后端 |

历史GPU为RTX4080/SM89，UUID `GPU-ce6cba36-415b-4e27-40e2-bded6bc1ee59`，driver580.178.04；这些不能替代当前只读设备识别。不得为接管升级driver、CUDA或NVBit。

## 5. 现场需要闭合的问题

1. 当前109连接与账户、上述根的存在/redirect/权限状态、旧工具实际冻结位置。
2. 共享RTX有限dispatcher/worker、SSHFS或reader/writer是否仍存；以PID+starttime+owner与控制回执join，历史PID不作今天的身份。
3. 10月26 transpose与exact36批次是否已有后续terminal/COMMIT/closeout；如果没有，记录未决，不恢复队列。
4. 当前ordinary/derived catalog的只读版本、精确计数与读取时点；若不在109权限内，引用既有接收回执并标待Main/资产owner补证，不能为此影响五点。
5. 每类资产的109源、164 canonical对象、已完成接收/恢复证据与qualification boundary是否能定位；缺热副本不等于丢失，目标未核实也不等于已删除。
6. 比较11月4存储快照与今天现场，任何新迁移/删除必须有对应精确receipt；本轮不追加清理授权。
7. 早期EP使用的 `decoupled-l2-pretraces`、`decoupled-l2-extract`、`c2p-polybench-full-20260821` 若能在小manifest中闭合109 producer链则补记；不能仅从路径认定GPU或节点，不需大范围追扫。早期Streaming-Reuse本来就要求复用已有trace，未单独授权不生成新hardware trace。[E24]

C16 bounded D1–D3是另一条109生产链；本次未找到将其绑定为EP消费者输入的固定证据，不纳入本轮执行范围。发现明确EP引用时只增加共享依赖记录，保留C16原owner。

## 6. 109-EP-L2的接管完成条件

接管完成意味着：已核执行端与职责；完成一次必要现场对齐；历史主要资产与来源可定位；当前进程/共享owner边界明确；本机CONTEXT与远端接管回执已发布并回读。**不要求把旧未支持profile、161个专项项、整个共享库或所有历史未知都补齐。**

当前执行任务全文在 [EP_L2_109_TAKEOVER_GOAL.md](EP_L2_109_TAKEOVER_GOAL.md)。证据逐项固定在 [EVIDENCE_INDEX.json](EVIDENCE_INDEX.json)。科学知识与路径摘要在 [ASSET_AND_ROLE_LEDGER.json](ASSET_AND_ROLE_LEDGER.json)。本包不包含新执行结果；API完成后追加自己的带时点回执。

[E01]: https://github.com/swayhrl/accel-sim-framework/blob/08fc797a44d24906e8e8b08ef8a95cb25a288e64/docs/ep_l2/operations/ep_main_full_handoff_20261109_v1/EP_L2_FULL_HANDOFF.md
[E02]: https://github.com/swayhrl/accel-sim-framework/blob/eb41e43b814d5b67267b8b2b00c143e625da6f20/docs/ep_l2/operations/ep_main_full_handoff_20261109_v1/EP_L2_MAIN_TAKEOVER_20261109.md
[E03]: https://github.com/swayhrl/accel-sim-framework/blob/08fc797a44d24906e8e8b08ef8a95cb25a288e64/docs/ep_l2/operations/shared_rtx4080_trace_pilot_20261024_v1/evidence/EXISTING4080_EVIDENCE.json
[E04]: https://github.com/swayhrl/accel-sim-framework/blob/08fc797a44d24906e8e8b08ef8a95cb25a288e64/docs/ep_l2/operations/shared_rtx4080_trace_pilot_20261024_v1/FINAL_REPORT.md
[E05]: https://github.com/swayhrl/accel-sim-framework/blob/08fc797a44d24906e8e8b08ef8a95cb25a288e64/docs/ep_l2/operations/shared_rtx4080_trace_pilot_20261024_v1/ARCH_COMPATIBILITY_CLARIFICATION.md
[E06]: https://github.com/swayhrl/accel-sim-framework/blob/08fc797a44d24906e8e8b08ef8a95cb25a288e64/docs/ep_l2/operations/shared_rtx4080_bulk_20261024_v1/README.md
[E07]: https://github.com/swayhrl/accel-sim-framework/blob/08fc797a44d24906e8e8b08ef8a95cb25a288e64/docs/ep_l2/operations/shared_rtx4080_cuda_polybench_20261024_v1/PREPARATION_HANDOFF.md
[E08]: https://github.com/swayhrl/accel-sim-framework/blob/08fc797a44d24906e8e8b08ef8a95cb25a288e64/docs/ep_l2/operations/shared_rtx4080_cuda_polybench_20261024_v1/PHASE5_NATIVE_CLOSEOUT.md
[E09]: https://github.com/swayhrl/accel-sim-framework/blob/08fc797a44d24906e8e8b08ef8a95cb25a288e64/docs/ep_l2/operations/ada_trace_semantics_20261024_v1/README.md
[E10]: https://github.com/swayhrl/accel-sim-framework/blob/08fc797a44d24906e8e8b08ef8a95cb25a288e64/docs/ep_l2/operations/ada_asset_contracts_20261024_v1/README.md
[E11]: https://github.com/swayhrl/accel-sim-framework/blob/08fc797a44d24906e8e8b08ef8a95cb25a288e64/docs/ep_l2/operations/ada_trace_extensions_v8_20261024_v1/README.md
[E12]: https://github.com/swayhrl/accel-sim-framework/blob/08fc797a44d24906e8e8b08ef8a95cb25a288e64/docs/ep_l2/operations/ada_native_maps_candidates_20261024_v1/README.md
[E13]: https://github.com/swayhrl/accel-sim-framework/blob/08fc797a44d24906e8e8b08ef8a95cb25a288e64/docs/ep_l2/operations/ada_legacy_driver_candidate_20261024_v1/README.md
[E14]: https://github.com/swayhrl/accel-sim-framework/blob/08fc797a44d24906e8e8b08ef8a95cb25a288e64/docs/ep_l2/operations/ada9_linear_texture_fulltyped_20261024_v1/HANDOFF.md
[E15]: https://github.com/swayhrl/accel-sim-framework/blob/08fc797a44d24906e8e8b08ef8a95cb25a288e64/docs/ep_l2/operations/ada9_parent_closeout_and_asset_cpu_resume_20261024_v1/README.md
[E16]: https://github.com/swayhrl/accel-sim-framework/blob/08fc797a44d24906e8e8b08ef8a95cb25a288e64/docs/ep_l2/operations/asset_library_parallel_status_review_20261026_v1/CURRENT_STATUS_REVIEW.md
[E17]: https://github.com/swayhrl/accel-sim-framework/blob/08fc797a44d24906e8e8b08ef8a95cb25a288e64/docs/ep_l2/operations/rtx4080_stencil_recovery_copy_cold_catalog_closed_20261025_v1/CURRENT_STATE.md
[E18]: https://github.com/swayhrl/accel-sim-framework/blob/8700af7cd3e0cd530f8efa8dfe5333ebdd9f1d1e/docs/storage/node109/20261104/cross_project_usage_review/FINAL_CROSS_PROJECT_USAGE_REPORT.md
[E19]: https://github.com/swayhrl/accel-sim-framework/blob/b290790401e248a19427c26c0dde51e6b55ded67/docs/storage/node109/20261104/fast_retirement_v1/FINAL_EXECUTION_REPORT.md
[E20]: https://github.com/swayhrl/accel-sim-framework/blob/b7dbdecb94054f08aaf2e33bfef48e453747ceb5/docs/ep_l2/calibration/TELEMETRY_SEMANTICS.md
[E21]: https://github.com/swayhrl/accel-sim-framework/blob/08fc797a44d24906e8e8b08ef8a95cb25a288e64/docs/ep_l2/operations/ada_nn_observed_io_candidate_20261024_v1/ADMISSION_V4.md
[E22]: https://github.com/swayhrl/accel-sim-framework/blob/b290790401e248a19427c26c0dde51e6b55ded67/docs/storage/node109/20261104/ASSET_INVENTORY.csv
[E23]: https://github.com/swayhrl/accel-sim-framework/blob/08fc797a44d24906e8e8b08ef8a95cb25a288e64/docs/ep_l2/operations/ada_nn_observed_io_candidate_20261024_v1/README.md
[E24]: https://github.com/swayhrl/accel-sim-framework/blob/b7dbdecb94054f08aaf2e33bfef48e453747ceb5/docs/ep_l2/chatgpt_handoff/STREAMING_REUSE_EXTENSION_HANDOFF.md
