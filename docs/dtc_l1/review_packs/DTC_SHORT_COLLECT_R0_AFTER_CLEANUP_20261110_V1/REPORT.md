# Short-Collect R0：清理后 Native 准入续核

**裁决：`R0_HOLD_NO_SCIENCE`；本轮 STOP。** 2026-11-10 17:13 UTC 的 fresh 检查中，Short-Collect 的真实科学 request 登记、UUID、模型启动、预算消费均为 **0**。冻结合同 `dfd6d7aa0383b8fda9ff08672f8c9efc392df26f` 和候选 Core `9a0de9b9f97144f481b3e3637e329ebab01acb74` 未改。

用户清理后，174-new `/root/data` 可用 **29,924,651,008 B**，高于不可放松的 5 GiB 底线；164 挂载可用约 42.19 TB。物理底线已通过，大资产继续按既定原则放 164。当前**无需为本轮继续清理**。这些数字是时间点快照，不构成 R0 全面准入。

旧 `route_guard.py` 按 registry 原始 lifetime carrier 相加，fresh peer 为 **69,589,119,972 B**，再加首格窗口 **1,610,612,736 B** 和 5 GiB 底线，要求 Native free 严格大于 **76,568,441,828 B**；按该口径尚差 **46,643,782,629 B**。这不是实际未来写入量，也不能仅为了让 guard PASS 而忽略 owner 保证。旧 pinned outbox gate 同时 HOLD。`FRESH_R0_AFTER_CLEANUP.json` 保存了 registry SHA `6632d4b06858c6ef180773babe3d9698c3cf3ac833d0dd039578f6ce567450c6`、epoch SHA `fef90eb1f13964ddfd219df0eee9ff3ef37a7abf8e1c18fa0b207a3f7bcd74e6`、73 条 request、未登记的 C1 准备稿和资源结果。

已用只读 `resource_reconcile_readonly.py` 尝试把正式 DTC owner 十项有效界与 EP 两族适配器的 peer carrier 接起来。固定十项有效 DTC 保证为 **8,380,228,658 B**；此前 EP GEMM/Stencil 两族保留的 carrier 分别为 **337,641,472 / 270,532,608 B**。仅按这组*旧的完整且无活动模型*来源，首格加 5 GiB 的诊断门槛约为 **15,967,724,594 B**，说明旧 76.57 GB 门槛有很大历史上界成分；该诊断数字**不是当前准入 PASS**。脚本 pin EP 适配器 SHA `3c637b65488123b7db22d936c9e700f9a5ca7f46bf6918c6748b02c582402d02` 和 DTC owner ledger SHA `e9622ccc20306ca1b9b35c91ae4e7c215cd951b96e5fa21e8e55fded3e5d97bb`，遇到未知 owner/活动模型即失败，没有调整 registry 或 guard。

本轮关键新事实：在只读诊断期间，EP-L2 新请求 `EP_L2_OPTIONAL_CLEAN128_STENCIL_EXT1_20261110_V1` 已进入共享权威记录；适配器报告 `unknown exact5 shared claim owner/cohort`，且首次查询报告 `UNMAPPED_LIVE_SIMULATOR` PID **1602856**。17:14 UTC 的只读 `ps` 仍见该 PID 存活。EP 适配器因活动模型不能再完成原终态 legacy 行的静态 RAM 清解。因此原先没有 EP 活动模型的快照失效，不能用 8.38 GB 有效 DTC 界自行宣告整个共享 Native 资源门通过。本轮没有停止、修改或竞争 EP 的进程、claim、锁或请求。

R0 还缺生产 dispatcher/launcher、真正的 parent lease 与 PID/maps/私有 loader 链、机制专属 guard 的正式审查、CPU 合成 true164 `SOURCE_KEEP` 正路径归档和 typed Native restore、损坏负例及独立科学审查。原 17/17 候选 CPU 资格与本轮既有小型 route fixture 均不代替这些 Gate。本轮仅新增一份**只读、失败即 HOLD** 的诊断脚本；没有改冻结 Core、binary、旧 outbox、registry、Source、论文或其他 owner 服务。

按固定 Goal，R0 任一 Gate 失败即 `R0_HOLD_NO_SCIENCE` 并 STOP。EP 活动与新请求需要由其合法 owner 自行完成；之后下一条明确任务可重新做 fresh 共享资源核账，并继续未完成的 R0 工程与独审。此时仍须使用原固定候选和同一合同，不自动注册 C1、运行 GESUMMV/vectorAdd 或扩大到 C2。

## 本轮证据

- `FRESH_R0_AFTER_CLEANUP.json`：fresh 原 guard、权威 SHA、input/runtime 与归档容量。
- `CROSS_OWNER_DIAGNOSTIC_HOLD.json`：新 EP 请求、未知共享 claim 与 fail-closed 结果。
- `ACTIVE_PROCESS_READONLY.txt`：PID 的只读存活回执。
- `DF_FRESH.txt`：Native 与 164 的同轮空间快照。
- `resource_reconcile_readonly.py`：只读诊断源码；`OWNER_CLOSEOUT_LEDGER_PINNED.json` 为此前已发布十项账的原字节副本。

固定前置报告：DTC owner 十项关账 `f81149b169a2c794170a7cbefa76232e074d0850`；Stage48 关账及原 R0 HOLD `c59ecadb555378f96807f1ea51690a6fe54bd9bd`。本轮无科学性能结果，正零负均为 UNKNOWN。
