# EP-L2：Native 空间 HOLD 审查与 109 接管接受

审查日期：2026-11-09。本文根据固定 GitHub 文件审查，未连接 174/109 节点，未访问用户 D 盘，未修改运行环境、预算、claims 或控制器。现场数值属于相应回执的观测时刻。

## 1. 当前结论

1. **五点授权有效，登记与 prepare 已完成；最新已发布 Main 回执为资源 HOLD，消费、运行、接受均为 0。** 不再使用早期“五点正在执行”聊天描述，也不倒退为“待科学授权”。没有 UUID 或 cycles 可等待。[Main HOLD 报告](https://github.com/swayhrl/accel-sim-framework/blob/f9f05065b277c3f01f74f9fa27c96ff9337d5168/docs/ep_l2/operations/ep_l2_optional_clean128_exact5_execution_20261109_v1/activated/documents/RESOURCE_HOLD_REPORT_20261109.md)
2. **大资产放真 164 的指令和实际路由均已存在。** 应补的是逐 owner 的 Native 剩余写入账、实际空间义务与正常续行实现，不是重发五点 Goal。[原授权 §6](https://github.com/swayhrl/accel-sim-framework/blob/f9f05065b277c3f01f74f9fa27c96ff9337d5168/docs/ep_l2/operations/ep_l2_optional_clean128_exact5_execution_20261109_v1/activated/control/USER_REQUEST.txt)
3. **109 只读接入与知识接管可以接受。** 最新更新将 exact36 dispatcher 的终态从未找到证据改为 `FAILED_STOP`；剩余 33 项的后续合法处置仍未知。[109 最新主回执](https://github.com/swayhrl/accel-sim-framework/blob/74cba90276e5056b3c401e83bf3298883a19f688/docs/ep_l2/operations/ep_l2_109_api_takeover_20261109_v1/takeover_receipt_v1/TAKEOVER_RECEIPT.md)
4. 默认科学 owner 仍为 **EP-L2 Main（本机 API 会话 EP-L2交接-1，174-new）**。109-EP-L2 是历史采集、工具与资产的执行端；原 Main 仅供历史查询，不设第二个科学调度 owner。109 的未决资产资格和旧队列不构成本轮五点的新前置门。[109 上下文增量](https://github.com/swayhrl/accel-sim-framework/blob/74cba90276e5056b3c401e83bf3298883a19f688/docs/ep_l2/operations/ep_l2_109_api_takeover_20261109_v1/takeover_receipt_v1/MAIN_CONTEXT_ADDENDUM.md)

本包只有审查与可转发的执行补充。用户转交 [MAIN_SUPPLEMENT.md](MAIN_SUPPLEMENT.md) 后，Main 在现有五点授权内完成必要核账与续行；本文发布本身不代表 Main 已读取或已作任何修复。

## 2. 为什么不是“忘了放 164”

原授权已明确大 Trace、大结果、长期归档留真 164，174 只保留必要热工作集。仓库 [AGENTS.md 的存储偏好](https://github.com/swayhrl/accel-sim-framework/blob/f9f05065b277c3f01f74f9fa27c96ff9337d5168/AGENTS.md) 也记载了同一用户要求，并要求把实际剩余增长与历史 pool ceiling 分开，空间不足由用户处理。

实际 [GEMM EXT0 Spec](https://github.com/swayhrl/accel-sim-framework/blob/f9f05065b277c3f01f74f9fa27c96ff9337d5168/docs/ep_l2/operations/ep_l2_optional_clean128_exact5_execution_20261109_v1/activated/cases/EP_PERF_CLEAN128_GEMM_WV_EXT0_20261109_V1/control/FROZEN_SPEC.json) 与 [Stencil EXT0 Spec](https://github.com/swayhrl/accel-sim-framework/blob/f9f05065b277c3f01f74f9fa27c96ff9337d5168/docs/ep_l2/operations/ep_l2_optional_clean128_exact5_execution_20261109_v1/activated/cases/EP_PERF_CLEAN128_STENCIL_WV_EXT0_20261109_V1/control/FROZEN_SPEC.json) 的 ELF、静态库及 Trace 入口均在 `/root/share/mnt164/...`。实际归档程序直接将 tar 写往：

- `/root/share/mnt164/huangrulin/host174_storage_recovery/ep_l2_optional_clean128_exact5_20261109_v1/gemm`
- 同级 `stencil`。

归档前核对挂载源 `admin-wcx@10.208.130.164:/home/shared`、`fuse.sshfs` 与目标设备；两个完整 Native 恢复目标在共享恢复锁内依次建立，验证后只释放自有临时 scratch，科学源保留。[GEMM 归档实现](https://github.com/swayhrl/accel-sim-framework/blob/f9f05065b277c3f01f74f9fa27c96ff9337d5168/docs/ep_l2/operations/ep_l2_optional_clean128_exact5_execution_20261109_v1/activated/runtime/host_gemm_bound_v2/ep_perf_archive.py)、[Stencil 归档实现](https://github.com/swayhrl/accel-sim-framework/blob/f9f05065b277c3f01f74f9fa27c96ff9337d5168/docs/ep_l2/operations/ep_l2_optional_clean128_exact5_execution_20261109_v1/activated/runtime/host_stencil_bound_v2/ep_perf_archive.py)

Main 回执给出的真 164 可用量是 42,233,184,329,728 B，挂载已验证。NAS 容量充足不能消除 Native 本地热结果、受控恢复窗口以及其他 owner 已承诺的未来本地写入。

## 3. 空间算式：本轮 452 MiB，主要待解释项是五点以外的承诺

时点为 **2026-11-09 13:58:14 UTC / 21:58:14 Asia/Shanghai**。以下是对 [HOLD JSON](https://github.com/swayhrl/accel-sim-framework/blob/f9f05065b277c3f01f74f9fa27c96ff9337d5168/docs/ep_l2/operations/ep_l2_optional_clean128_exact5_execution_20261109_v1/activated/documents/RESOURCE_HOLD_RECEIPT.json) 的归一化计算，数值只用于解释该快照。

| 项目 | 字节 | 说明 |
|---|---:|---|
| 五点以外请求的剩余写入承诺 | 20,459,824,178 | 约 19.055 GiB；从任一族 foreign 总额扣除另一新族承诺推导 |
| GEMM 三点承诺 | 270,532,608 | 258 MiB |
| Stencil 两点承诺 | 203,423,744 | 194 MiB |
| 本轮两族合计 | 473,956,352 | 452 MiB；上两行的小计，不再另加一次 |
| 有效 Native 底线 | 5,368,709,120 | 5 GiB |
| 所需合计 | 26,302,489,650 | 约 24.496 GiB |
| 当时 Native 可用 | 20,480,413,696 | 约 19.074 GiB |
| 缺口 | 5,822,075,954 | 约 5.422 GiB |

计算为：

```text
20,459,824,178 + 270,532,608 + 203,423,744 + 5,368,709,120
= 26,302,489,650 B

26,302,489,650 - 20,480,413,696
= 5,822,075,954 B
```

两个 family 的 foreign 数不同，是因为各自包含另一新族；不能把两个 foreign 列相加。即使不计本轮 452 MiB，其他承诺加底线仍超过当时可用空间 5,348,119,602 B。因此不能指望更改本轮小窗口的表述就消除全部缺口。

### 尚缺逐 owner 明细

已发布包包含 audit 脚本，但没有给出足以复算 19.055 GiB 的完整 `foreign_write_entries`、逐请求 bytes、已写量和剩余归档/恢复义务表。这些承诺是否全部仍有效、是否存在已落盘后仍按未来增长计入的项，尚未证明。

[资源适配器](https://github.com/swayhrl/accel-sim-framework/blob/f9f05065b277c3f01f74f9fa27c96ff9337d5168/docs/ep_l2/operations/ep_l2_optional_clean128_exact5_execution_20261109_v1/activated/runtime/host_gemm_bound_v2/resources_exact5_v2.py) 明确保留 6 个 DTC 请求的 advertised write commitments，只在有界终态检查后清理过时的 RAM 映射诊断。预算用完、无活动模型、有 execution_receipt，均不单独证明其归档与恢复义务已经关闭。公开材料也不足以把上述 19.055 GiB 全部归给这 6 项。

下一步应让 Main 导出精确明细。Main 可按原 owner 流程处理自己具有完整关闭证据的承诺；其他 owner 的行继续保留，形成可由用户转交的精确核账请求。不能通过清除 foreign 行、放宽 floor 或删科学源让准入表面通过。

## 4. 两个有界实现问题，应随资源补充解决

### 4.1 恢复窗口的身份与上界

[注册脚本](https://github.com/swayhrl/accel-sim-framework/blob/f9f05065b277c3f01f74f9fa27c96ff9337d5168/docs/ep_l2/operations/ep_l2_optional_clean128_exact5_execution_20261109_v1/activated/runtime/register_exact5.py) 按每族 `点数×64 MiB + 64 MiB窗口 + 2 MiB metadata` 登记，合计 452 MiB。原授权每次恢复上界为 128 MiB，Spec 的 `stored_hot_envelope_bytes` 也为 128 MiB。

归档 tar 直接写 164，不应把归档上界再作为一份 Native 输出扣除；两次独立恢复按单一全局窗口串行。当前两个族各 64 MiB 的窗口合计恰是 128 MiB，**不能看到两个 window 就直接减掉 64 MiB**。结果监控的 64 MiB 界限也不能自动证明所有终态、退出后 metadata 和技术负例的完整恢复成员都不超过 64 MiB。应把已批准的单个全局 128 MiB 窗口、唯一记账位置、释放/转接时机和实际恢复边界对齐；任何更小派生值都必须已有完整、严格的边界依据。

[V3 资源代码](https://github.com/swayhrl/accel-sim-framework/blob/f9f05065b277c3f01f74f9fa27c96ff9337d5168/docs/ep_l2/operations/ep_performance_first_v3_20261104_v1/activation_20261104_v1/agent_c_resources/resources_v3.py) 有恢复窗口去重，但只识别其 SCOPES 中的指定条目类型。本批每族适配器只注入本族映射。是否命中、最终准入采用哪个调整后的总额，需要一份实际 `foreign_write_entries` 与 `admission.global_restore_dedup` 小回执。现有汇总不能独立回答这一点。

### 4.2 首次整族 staging 不能成为正常续行的跨族门

[stage_dispatch_exact5.py](https://github.com/swayhrl/accel-sim-framework/blob/f9f05065b277c3f01f74f9fa27c96ff9337d5168/docs/ep_l2/operations/ep_l2_optional_clean128_exact5_execution_20261109_v1/activated/runtime/stage_dispatch_exact5.py) 要求整族未消费、全机无模型、共享 claims 为空、整族 CPU/RAM 满足、所有 decisions 通过。若将其原样作为正常续行入口，第一族开始运行后会阻止另一族增量准入，部分消费后也不能正常继续。

不能只删除 assert。两个族共用 `ROOT/control/DISPATCH_CLAIMS.json`，当前 [resource_gate](https://github.com/swayhrl/accel-sim-framework/blob/f9f05065b277c3f01f74f9fa27c96ff9337d5168/docs/ep_l2/operations/ep_l2_optional_clean128_exact5_execution_20261109_v1/activated/runtime/host_gemm_bound_v2/ep_perf_native_wv_modes_draft.py) 和 [publish_own_write_carrier](https://github.com/swayhrl/accel-sim-framework/blob/f9f05065b277c3f01f74f9fa27c96ff9337d5168/docs/ep_l2/operations/ep_l2_optional_clean128_exact5_execution_20261109_v1/activated/runtime/host_gemm_bound_v2/ep_perf_common_v2.py) 遍历整个 claims 集。直接放开会带来跨族重复记账或错误发布本族 carrier 的风险。

Main 仅需在实际使用的本批路径落实 request/cohort 过滤、增量 claim、合法现有模型识别、逐点 fresh 准入与保留其他 claims。复用工程/输入资格，只对这一具体改动做有限无启动验证并维护受影响的 pins。空间 HOLD 在当前快照独立成立；这项实现问题不表示已经重复启动。

## 5. 109 接管接受与 exact36 最新更新

接受状态：`COMPLETE_READONLY_NODE109_ENDPOINT`。固定最新提交：

`74cba90276e5056b3c401e83bf3298883a19f688`

该提交更新了原 5 份接管文件，后续观测补充到 2026-11-09 22:43:59 +08。本文读取的是已发布现场回执与所列小文件 SHA，未亲自读取或重新计算节点上的私有原件。

| 字段 | 当前应记录的状态 |
|---|---|
| 切换控制器 | `EXACT36_BATCH_STARTED_CONTROLLER_COMPLETE`：切换及新批启动交接完成 |
| 新有限 dispatcher | `FAILED_STOP` |
| dispatcher 停机时间 | 2026-10-27 06:15:24 +08 |
| 直接停止原因 | 第三项 `ORD_Rodinia_streamcluster_1be5fda1aa60_A001` 的 worker/guard exit 75 |
| 冻结 36 项末次状态 | 2 COMMITTED_VERIFIED、1 FAILED_RETAINED、33 PENDING |
| 33 项后续合法处置 | UNKNOWN |
| 36 项全部完成 | 未证明，不能标成全部完成 |
| 新采集或续跑权限 | 本次接管与历史回执更新均未授予 |

依据：[TAKEOVER_RECEIPT.md](https://github.com/swayhrl/accel-sim-framework/blob/74cba90276e5056b3c401e83bf3298883a19f688/docs/ep_l2/operations/ep_l2_109_api_takeover_20261109_v1/takeover_receipt_v1/TAKEOVER_RECEIPT.md)、[CURRENT_STATE.json](https://github.com/swayhrl/accel-sim-framework/blob/74cba90276e5056b3c401e83bf3298883a19f688/docs/ep_l2/operations/ep_l2_109_api_takeover_20261109_v1/takeover_receipt_v1/CURRENT_STATE.json)、[OPEN_ITEMS.md](https://github.com/swayhrl/accel-sim-framework/blob/74cba90276e5056b3c401e83bf3298883a19f688/docs/ep_l2/operations/ep_l2_109_api_takeover_20261109_v1/takeover_receipt_v1/OPEN_ITEMS.md)。

旧 `51dc42f…` 的“尚未找到 dispatcher 终态”已被新证据覆盖；保留旧快照，不回写历史。不能把 exit 75 推成已证明的硬件故障、输入错误或应用性能失败。

公共目录普通与派生各 82 个已提交**版本**，与全队列 242 行（41 提交、33 待处理、161 专项待处理、5 失败、2 被替代）以及 exact36 子集是不同口径。三项 transpose 的旧边界批提交记录也不等同于本次 exact36 的两项提交。版本数不证明所有程序或队列完成，不授予消费者/时序资格。

历史资产、有限资格、失败、Source KEEP 和 Stencil 已闭合 CPU 恢复链直接继承；109 两个 NAS 挂载通向同一真 164 对象树，不是两份独立物理备份。[资产索引](https://github.com/swayhrl/accel-sim-framework/blob/74cba90276e5056b3c401e83bf3298883a19f688/docs/ep_l2/operations/ep_l2_109_api_takeover_20261109_v1/takeover_receipt_v1/ASSET_INDEX.json)

## 6. 下一步及交付

向 EP-L2 Main 转交 [MAIN_SUPPLEMENT.md](MAIN_SUPPLEMENT.md)。核心工作为一次有界的剩余写入核账、必要本批资源/续行修正，以及将**最新** [MAIN_CONTEXT_ADDENDUM.md](https://github.com/swayhrl/accel-sim-framework/blob/74cba90276e5056b3c401e83bf3298883a19f688/docs/ep_l2/operations/ep_l2_109_api_takeover_20261109_v1/takeover_receipt_v1/MAIN_CONTEXT_ADDENDUM.md) 合并到本项目 `CONTEXT.md`。

五点科学目标保持：GEMM 0→1 的结构代价、1→2 的同硬件保留增量、0→2 的净效果；Stencil 仅 0→2 净效果。工程 PASS 仍不是应用收益。本补充不增加 CLEAN C、RO、GPU、额外输入、论文或旧队列任务。

资源与身份实际满足后，Main 按既有两个请求接续合法未消费点，不重登记、不重复批准同一范围。若仍 HOLD，交付逐 owner 账和准确需要用户/owner 处理的动作；不把“请腾 5.42 GiB”当成已经核清的最终方案。109 端本轮已经完成，不追加新科学任务。

