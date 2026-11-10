# EP-L2 exact5 受控后台执行回执

现场时间：2026-11-10 03:38:59 UTC。固定机器回执：`ACTIVE_BACKGROUND_RECEIPT_20261110.json`。

## 当前事实

原 `EP_L2_OPTIONAL_CLEAN128_EXACT5_EXECUTION_V1` 两族授权、两份登记请求、每点一次上限沿用。五点均由 `/root/data/ep_l2_dtc_l1_native_v2/bin/native` 正式入口消费并启动；没有新 Goal、预算或第二 dispatcher。当前均为 **RUNNING，未结束、未验收**。

| 点 | CPU | 模型 PID | UUID |
|---|---:|---:|---|
| GEMM EXT0 | 128 | 1502330 | aa15408e-0d48-4b89-ad2e-781160b0c419 |
| GEMM EXT1 | 130 | 1505311 | a79fe296-1b89-4687-a59f-6a80a526f362 |
| GEMM EXT2 | 131 | 1505399 | 9d617336-e18b-4c14-a1ad-6ac323486242 |
| Stencil EXT0 | 129 | 1504873 | 90644325-58b7-4eaf-bf07-102128f2868c |
| Stencil EXT2 | 132 | 1505512 | aede460f-6e30-4416-b5af-c64c92127db6 |

GEMM 请求已消费 3/3，Stencil 已消费 2/2，均无可再次启动余额。epoch 2 与 registry SHA `b9652caa06bedd459ae756f693a221a8e09fca5c4ae2a714eb2f1183d8b12e58` 匹配；五个 PID generation 在现场存活，`NATIVE_EXIT.json` 尚无。资源快照 `foreign_metadata_errors=[]`，Native 可用 36,266,340,352 B，主机 MemAvailable 约 194.28 GB，真164挂载有效。当前 CPU 使用 5/10，模型各约占一个逻辑 CPU；cap10 是上限。两族剩余写入 carrier 分别为 343,142,400 B 与 273,416,192 B，均覆盖当前 claims 加单个全局 128 MiB 恢复窗口及 metadata；5 GiB 有效 Native 底线和其他 owner 保证仍保留。

## 本批必要适配

首点 GEMM EXT0 按原 v2 Spec 启动。随后资源快照把已核实终态的旧 owner 连同合法运行的 exact5 peer 报为未映射活动 RAM；动态热盘 claim 与已发布 carrier 的严格相等检查也使独立后续点 HOLD。按已授权的本批适配范围新增版本化资源适配器 v3、v4、v5：核对活动模型 PID generation 与 claims/owner 记账，保留旧 owner 写入承诺；要求 carrier 至少覆盖既有活动 claims 和恢复窗口，允许新 staging claim 在发布 carrier 前计入本次准入。只对尚未消费的 Spec 做版本化重绑定，旧 Spec 与 prelaunch 回执均保留。GEMM EXT0 的已消费 Spec 未改；Stencil EXT0 使用 v4；其余三点使用 v5。两族 carrier 已经通过自身原 owner 流程补足，未改其他 owner 账本，也未清理资产。对应重绑定记录在执行根 `control/RESOURCE_V{3,4,5}_REBIND_*.json`。

## 后台控制与下一步

五个 `run-native` 主控均已脱离 SSH 会话，持续采样进程 RSS、热盘占用，并按已冻结的硬上限、硬墙钟及显式 ABORT 条件停止；自然结束将写 `NATIVE_EXIT.json` 和 Native 台账。未设置自动重试或退款。历史软时长推算 GEMM 约在 **04:30–05:00 UTC**、Stencil 约在 **07:15–08:00 UTC** 自然结束；现时约需再等 **3.5–4 小时** 才可能五点全部自然结束。并行负载会使估计变化；验收、真164归档、双 Native 恢复及最终发布另需时间。

下一项具体动作：逐点自然结束后先核 DONE 和真实身份/人口/协议，再按合同验收、真164 full SHA 归档、两次独立完整 Native 恢复与最终比较。不会把后台运行视作已接受。
