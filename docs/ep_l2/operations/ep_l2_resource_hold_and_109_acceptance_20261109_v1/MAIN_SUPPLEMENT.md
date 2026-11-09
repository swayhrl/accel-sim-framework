# 给 EP-L2 Main 的执行补充：Native 空间核账、正常续行与 109 上下文更新

补充编号：`EP_L2_NATIVE_STORAGE_AND_109_CONTEXT_SUPPLEMENT_20261109_V1`

执行端：现有 EP-L2 Main，本机 API 会话 `EP-L2交接-1`，节点 `hrl-174-new`。

**这是现有 `EP_L2_OPTIONAL_CLEAN128_EXACT5_EXECUTION_V1` 的执行补充。沿用原授权、两个已登记请求和各点一次消费上限；不另建科学 Goal 或预算，不重做接管，不重启已消费点。**

## 0. 先合并真实状态

接受你在 `f9f05065b277c3f01f74f9fa27c96ff9337d5168` 发布的状态：五点授权有效；GEMM 3、Stencil 2 各登记一次；五点 prepare 通过；13:58:14 UTC 的回执是资源 HOLD、消费/运行/接受 0、claims 已撤回。没有模型结果可等待。

开始本补充时，以一次必要的最新 registry/epoch/claim/执行回执核对为准；如后来已有合法消费或运行，保留原 UUID、Spec、记录与模型，只处理仍未消费点及不干扰活动任务的资料工作。不要将上述旧快照覆盖更晚事实。

大 Trace、大结果、长期归档在真 164，是既有要求且已在本批实现。当前问题是 Native 剩余写入承诺与可用空间，不需要再复制大输入或搬动环境。

## 1. 必要科学背景与不变范围

主线继续 Performance-First，检验 optional CLEAN 元数据保留能否覆盖扩展结构的真实付费代价。GEMM 完整应用 cycles 为 G0/G1/G2：

- 结构代价：G1−G0；
- 相同扩展硬件的保留增量：G1−G2；
- 整体净效果：G0−G2，净降低率 (G0−G2)/G0。

Stencil 只比较 S0 与 S2 的净效果，不增 EXT1、不拆独立保留贡献。工程 PASS、query 下降或额外响应都不能替代应用净收益；原负例与未知物理/数值性质继续保留。

五点共同 A Source5、WV_ZERO_RO、G32×8、850 MHz/L100、完整 283 项、冻结输入/完整有序命令不变。继续复用既有 A 生产 CPU、Main 复放、输入资格、consumer 数学主体及正式绑定。独立 CLEAN C 不合入。本补充不增加 RO/NI、参数扫描、GPU/Trace 采集、额外输入或论文工作。

| 已登记 request | 既有 actual cohorts |
|---|---|
| `EP_L2_OPTIONAL_CLEAN128_GEMM3_20261109_V1` | `EP_PERF_CLEAN128_GEMM_WV_EXT0_20261109_V1`、`EXT1`、`EXT2` 同一命名前缀和日期后缀 |
| `EP_L2_OPTIONAL_CLEAN128_STENCIL2_20261109_V1` | `EP_PERF_CLEAN128_STENCIL_WV_EXT0_20261109_V1`、`EXT2` 同一命名前缀和日期后缀 |

精确全集仍以现有 activation manifest 与各点 Spec 为准，不能从上表简称生成新 cohort。

## 2. 目录与固定资料

本机项目：`D:/Codex/Token-API/workspaces/EP-L2`  
持久上下文：`D:/Codex/Token-API/workspaces/EP-L2/CONTEXT.md`  
继续使用现有五点 delivery 目录，并为本补充建立小型子目录。

现有节点执行根：

```text
/root/data/ep_l2_full_workload_performance_20261027_v1/research/optional_clean128_exact5_execution_20261109_v1
```

共享 Native：

```text
/root/data/ep_l2_dtc_l1_native_v2
/root/data/ep_l2_dtc_l1_native_v2/bin/native
```

真 164 视图：`/root/share/mnt164`，已知合法源为 `admin-wcx@10.208.130.164:/home/shared`。沿用实际已绑定的输入、ELF、静态库及归档路径，核对挂载身份，不把同名目录或 shadow mount 当真 164。

固定资料：

1. [本轮原授权全文，尤其 §3、§6、§7、§9](https://github.com/swayhrl/accel-sim-framework/blob/f9f05065b277c3f01f74f9fa27c96ff9337d5168/docs/ep_l2/operations/ep_l2_optional_clean128_exact5_execution_20261109_v1/activated/control/USER_REQUEST.txt)。
2. [当前 HOLD 报告](https://github.com/swayhrl/accel-sim-framework/blob/f9f05065b277c3f01f74f9fa27c96ff9337d5168/docs/ep_l2/operations/ep_l2_optional_clean128_exact5_execution_20261109_v1/activated/documents/RESOURCE_HOLD_REPORT_20261109.md)、[结构化 HOLD](https://github.com/swayhrl/accel-sim-framework/blob/f9f05065b277c3f01f74f9fa27c96ff9337d5168/docs/ep_l2/operations/ep_l2_optional_clean128_exact5_execution_20261109_v1/activated/documents/RESOURCE_HOLD_RECEIPT.json) 与同一固定提交的 activated Spec、资源适配器、stage/Host/archive 源码。
3. [仓库存储偏好与 owner 边界](https://github.com/swayhrl/accel-sim-framework/blob/f9f05065b277c3f01f74f9fa27c96ff9337d5168/AGENTS.md)。
4. [109 最新接管回执](https://github.com/swayhrl/accel-sim-framework/blob/74cba90276e5056b3c401e83bf3298883a19f688/docs/ep_l2/operations/ep_l2_109_api_takeover_20261109_v1/takeover_receipt_v1/TAKEOVER_RECEIPT.md)、[CURRENT_STATE.json](https://github.com/swayhrl/accel-sim-framework/blob/74cba90276e5056b3c401e83bf3298883a19f688/docs/ep_l2/operations/ep_l2_109_api_takeover_20261109_v1/takeover_receipt_v1/CURRENT_STATE.json)、[MAIN_CONTEXT_ADDENDUM.md](https://github.com/swayhrl/accel-sim-framework/blob/74cba90276e5056b3c401e83bf3298883a19f688/docs/ep_l2/operations/ep_l2_109_api_takeover_20261109_v1/takeover_receipt_v1/MAIN_CONTEXT_ADDENDUM.md)。使用 `74cba902…` 更新版，旧 `51dc42f…` 保留为历史。
5. 本目录 [README.md](README.md) 的科学窗口审查及 [EVIDENCE_INDEX.json](EVIDENCE_INDEX.json)。

不假定两端聊天、D 盘目录或 CONTEXT 自动同步；固定 Git 文件与现场现有绑定是可复核来源。

## 3. 一次有界核账：先解释真正的剩余 Native 写入

13:58:14 UTC 的归一化历史账为：

```text
五点以外承诺 20,459,824,178 B
+ GEMM 本族 270,532,608 B
+ Stencil 本族 203,423,744 B
+ 有效 floor 5,368,709,120 B
= 26,302,489,650 B

当时 Native 可用 20,480,413,696 B，缺 5,822,075,954 B。
```

不要把 5.42 GiB 当永久目标，也不要把两个 family 的 foreign 总额相加。请用一次有界、带时间的只读采样，导出能复算最新准入判定的小型明细：

- registry/epoch SHA、当前 request 状态、有效 claims 与必要的 owner/PID/start_ticks 身份；不读取活动 raw。
- 每个 request/owner 的 published carrier、对应来源路径/SHA、逐条 `foreign_write_entries` 的 kind 和 bytes。
- 已写入且已反映在 df free 的 bytes、尚会增长的 Native bytes、真正写到 164 的 bytes，分别列示；未知项写 UNKNOWN，不用 0 填空。
- 后续 output、归档、两次串行恢复及 metadata 的剩余义务、执行/归档/恢复/关闭回执引用。
- 单一共享恢复窗口的记账位置、当前/后续所有者和释放条件；实际 `admission.global_restore_dedup` 输出。
- 最终使用的有效 floor 来源，去重前后算式，以及 fresh admission 实际采用的总量。

只查与这些承诺直接相关的小型 control/receipt/已封清单和必要目录量；不做全盘大资产盘点、全 Trace 重 SHA、115 项重迁移或公共 catalog verify-all。

优先解释资源适配器仍保留的下列 6 个 DTC 请求，但不要预设它们已经关闭，也不要预设它们等于全部 19.055 GiB：

```text
DTC_ORACLE_INITIAL8_20261106_V1
DTC_ORACLE_REMAINING24_20261106_V1
DTC_PERF_FIRST_NON_TAG_REMAINING28_20261104_V1
DTC_PERF_FIRST_PHYS768_FIRST4_20261104_V1
DTC_PERF_FIRST_V2_CODESIGN16_LAYOUT_R1_20261105_V1
DTC_PERF_FIRST_V2_PHYSICAL_PIB16_20261105_V1
```

“预算全部消费”“execution_receipt 存在”“没有模型”不等于归档/恢复/剩余写义务关闭。优先用已发布或现场已封 owner 回执，不要求重跑该项目验证。

## 4. 允许处理的范围与需要 owner 处理的部分

保持 5 GiB 有效 Native 底线及其他 owner 已有保证。已落盘 bytes 不再作为同一份未来增长重复扣除，pool ceiling 不自动再加成新写入承诺；但每项未来写义务必须仍有覆盖。

你可在现有 owner 流程中核清、正常关闭自己已经具备完整终结证据的剩余承诺，并修复本批可证明的重复计账或路径归属问题。每次实际改变保留旧版本、引用证据、记录差额，并按现有锁/epoch 规则保持其他行不变；不能因为同属 EP 就改用本五点 helper 去更新其他请求。

对其他 owner 的请求，保持原行和原保证。若发现尚未正式关闭或来源不明，形成一份**可由用户转交给相应 owner 的精确核账/收尾清单**：request、当前占额、实际缺的关闭证据、建议由该 owner 完成的动作。不要直接给其他窗口发消息、替它改 registry 或代签关闭。

本补充不授权删除科学源、raw、Trace、其他 owner 资产或未知临时文件，不授权新的大资产迁移、重挂载、服务重启。Source KEEP 保持。单纯复制到 164 也不算释放了 Native 空间。若确认是真实空间缺口，列清实际盘、净缺口和所需动作，由用户按原存储偏好处理。

## 5. 对齐单个全局恢复窗口，保持批准的安全语义

本批原合同为：Native 结果硬界 64 MiB；164 归档上界 128 MiB；每次完整 Native 恢复上界 128 MiB；两次恢复在两个独立目标上**串行复用一个全局窗口**。Spec 的 stored_hot_envelope 也为 128 MiB。

请解释当前每族“64 MiB window”如何覆盖该合同，并使正常路径的唯一记账载体、实际上界、跨族转接和释放时机一致。当前两族各 64 MiB 的总和为 128 MiB，不能直接减成全局 64 MiB 来过 HOLD。恢复包括完整终态、退出后 metadata 和技术负例；如主张更小派生窗口，必须有覆盖全部这些内容的现成严格边界证据。

164 归档 tar 与 Native 恢复 scratch 分开记账，不能把写往 164 的 tar 再预留为一份本地 tar。既有 128 MiB 单窗口保证不得因“串行”而丢失。实际 archive/restore 路径应核实成员量在受保护上界内，超界则保留原件并准确 HOLD，不能截断、丢弃负例或把超界恢复写成 PASS。

优先复用现有 archive、双恢复和共享锁，不为本补充重做历史应用恢复。

## 6. 正常续行按点增量准入，修正本批必要实现

目前已发布 `stage_dispatch_exact5.py` 是整族首次 staging 路径，要求 whole-family 未消费、全机无模型、shared claims 为空并整族资源通过。若实际接续仍沿用它，请在本批范围内修正，使其满足已授权的逐点独立准入与释放：

1. 按精确 request/cohort 判定本族 claims，保留另一族和其他合法任务的 claims、模型、CPU 绑定及消费记录。
2. 对仍合法未消费的点增量 claim、fresh admission、一次消费；不要求同族全部同时可运行，也不要求另一族结束。
3. `resource_gate`、`publish_own_write_carrier`、资源映射与归档释放使用一致的归属过滤。两个 family 共享一个 claims 文件，**不能只删除空 claims/无模型 assert**。
4. 正确识别已登记且身份匹配的合法运行模型，计入真实 CPU/RAM/未来写入；身份不明或冲突仍 HOLD。
5. 保持全局 EP cap10 为上限，保持 once-consumed 与原科学/资源安全语义，不创建第二 dispatcher。

只修改实际需要使用的本批 Host/调度/资源适配路径；若已存在可证明满足上述条件的正式续行路径，直接复用。保留原脚本/Spec 版本，对受影响的未消费点更新必要依赖 pins 和正式绑定；不得热改已运行或已消费点的冻结合同。

若确有代码改动，只做足以验证真实新增风险的有限无模型启动检查，例如跨族 claim 不重复计账、部分消费后未消费点能正常处理、未知 owner 仍 HOLD。复用旧工程与输入资格，不引入全套 CPU/NI/协议重验证门。

## 7. 接续现有五点；真实 HOLD 则给出准确闭环

完成必要核账后，只要现行冻结合同与届时实时资源满足，就按原授权接续合法未消费点，继续自然结束、正式验收、真 164 full SHA、双 Native 恢复及结果发布。无需再请用户批准同一五点，也不追加预算。

无消费的资源 HOLD 后重做 fresh admission，不是已消费模型的科学重试。已消费技术失败仍不自动重跑、退款或转移预算。若空间/owner 证据没有变化，交付准确 HOLD 与需要用户/owner 处理的清单，不设置持续轮询，也不空等模型结果。

本补充不会把五点全部同时运行或跨族完成设为要求；实际能准入的点独立推进。

## 8. 接受 109 接管并合并最新知识

将 `74cba90276e5056b3c401e83bf3298883a19f688` 的 MAIN_CONTEXT_ADDENDUM、CURRENT_STATE 与未决项合并到 Main 的 `CONTEXT.md`，标注来源和时点：

- 109-EP-L2 只读接入与知识接管完成；你仍是唯一科学 Main。
- exact36 切换控制器完成；其新 dispatcher 于 2026-10-27 06:15:24 +08 因第三项 streamcluster 的 worker/guard exit 75 进入 FAILED_STOP。
- 冻结 36 项末次为 2 提交、1 失败保留、33 PENDING；33 项后续合法处置 UNKNOWN。覆盖旧“dispatcher 终态未找到”的概括，不把整批写成全部成功。
- 公共 catalog 普通/派生各 82 个是版本；全队列 242 行和 exact36 子集为不同口径。
- 历史有限消费者资格、原失败、Source KEEP 与已关闭 Stencil CPU 恢复链直接继承。当前五点冻结输入不能被同名历史资产替换。
- 109 无新增科学任务，不续跑旧队列、不清锁、不补采、不迁移。旧队列和资产未决项不是五点前置条件。

只需吸收已发布资料，不再让 109 重做接管或为此发起节点检查。

## 9. 必要交付与 CONTEXT

在现有正常项目分支交付小型补充，不整体覆盖其他 owner 的工作：

1. `NATIVE_WRITE_LEDGER_RECONCILIATION.json`：带时间、固定来源、逐 owner/request 明细、实际准入算式和恢复窗口归属。
2. 一份简短报告：究竟为真实容量缺口、未闭 owner 承诺、可证重复计账或其组合；原快照与当前事实分开，列出已做/未做动作。
3. 必要修正的源码/依赖与最小无启动验证回执（若未改代码，说明复用路径）；如需其他 owner，附可转发精确清单。
4. 五点当前登记、消费、运行、终结/验收/HOLD 真实计数。若已接续，继续原五点交付，不因本补充再停下来等批准。
5. `CONTEXT.md` 更新摘要：存储规则、最新资源账、现有授权与身份、109 接管和 exact36 的新状态、固定 commit、保留负例与未决项。

发布后回读远端 HEAD 与关键小文件，返回固定 commit。大资产继续留原合格位置，不复制进 Git 或 Windows。不能把补充文件的发布预填成核账已完成、资源已解除或五点已启动。

