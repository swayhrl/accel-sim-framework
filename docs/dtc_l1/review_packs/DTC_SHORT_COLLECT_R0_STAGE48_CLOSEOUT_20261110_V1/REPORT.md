# Short-Collect R0：Stage II-A Remaining48 正式关账与 fresh 准入

2026-11-10，唯一 174-DTC Main。固定 Short-Collect 合同 `dfd6d7aa0383b8fda9ff08672f8c9efc392df26f`；候选 Core `9a0de9b9f97144f481b3e3637e329ebab01acb74`。本轮终态 **`R0_HOLD_NO_SCIENCE`，STOP**。新科学 request、UUID、模型启动、预算消费、164 归档均为 **0**。

## 已完成的 owner 事务

`DTC_STAGE_IIA_REMAINING48_CH_MATCH_20261104_V1` 已有 48/48 终态、逐格归档与 Native restore、SOURCE_KEEP，fresh claims 为 0，预算剩余为 0。政策 `RESOURCE_POLICY.json` 的 metadata 底额为 268,435,456 B。锁外逐格读既有小型回执及 true164 COMMIT/restore；锁内重核本地终态、claims、policy SHA 和 registry/epoch 一致性。通过原子 EX 锁、history、INTENT、registry/epoch 双 SHA 与 COMMITTED 回执，将该项原始 carrier **9,395,240,960 → 268,435,456 B**。正式承诺减少 **9,126,805,504 B**；物理磁盘释放 **0 B**。

事务前 registry/epoch SHA：`04f11b84af86728dd854a5734622839e15f6e84052def40de0fc4c0a2732d1d2` / `cdeba85077011afe7de72df4282f69120b1cccb7481fa1c3cd974506e350ab92`。事务后：`71d40678efd24108b112d5b0b4ab515de69760139af3ae84d334ca0309c511b1` / `c71ecac5ee5e819f8b559a08163fedf94e8ad6e824a06795b93db7ad3688236f`。回读逐字段确认另外 **71 条 request**、registry 无关字段及 epoch 无关字段相同；科学总预算 84 保持。INTENT SHA `34fddb2273f80016c1856cc03353c20af712e13a9f79342bd43c2db6502d28f7`。

固定源 SHA：Stage48 terminal `d52566d24228f8ce02961da4788d8b23759238f0ffac500d649f4f780c25132f`；空 claims `2feab82b19b434a984e853b70a24b5a45763c3443ba55aea9d447125ea0e46bd`；resource policy `67fea641f491cee0e27b033708a5440f3faa5fba1a8147b29166734b6a317e5c`。事务脚本 SHA `a79564aca4136ca0bb426cd28a381f105d38cba9993339c9e817e659ab8ddfa2`。完整 48 项小型证明在 INTENT；未重扫大型 raw/trace、未重做科学 strict。

## 仍不能关闭的承诺

Fresh 只读 claims 与既有 owner 回执相同：V100 已消费 284/356，尚有 **72** 次预算，claims 0，registry carrier 37,580,963,840 B；MLP 已消费 360/360，仍有 **1** 条未决 claim，carrier 25,769,803,776 B；Oracle initial8 已消费 32/32，仍有 **13** 条原池 claims，carrier 4,155,880,420 B。这些项目没有新的逐项正式解除证明，本轮没有修改。此前十项 owner 账中 V100/MLP 的有效准入派生界与 registry 原始 lifetime carrier 口径不同；不能混加或把原始 carrier 全额视为必然未来写入。Stage48 这次减少的是原始 registry carrier，前一份十项账已将其**有效准入界**视为 268,435,456 B，故不可再把 9,126,805,504 B 记成该十项有效账的额外释放。

## R0 fresh 裁决

15:51:36 UTC 的锁内 registry/epoch 匹配；冻结 C1 prepared request 未登记。GESUMMV 输入 SHA、冻结 binary/lib SHA 和 271 effective options 静态核对 PASS；true164 挂载接收空间 PASS。Native `free=4,493,602,816 B`，比 **5 GiB =5,368,709,120 B** 底线还少 **875,106,304 B**。当前 Short-Collect guard 按 registry 原始 active carrier 求和，peer 为 `69,385,696,228 B`，加首格窗口 `1,610,612,736 B` 和 5 GiB，要求 free 严格大于 `76,365,018,084 B`，按该保守 guard 尚差 `71,871,415,269 B`。该差额是准入承诺口径，并非实际物理待写入量。既有 pinned outbox gate 同时报 `HOLD`。

由于连不可放松的 5 GiB 物理底线都未满足，本轮不能做 true164 正路径写入资格或正式请求登记，更不能运行模型。生产 dispatcher/launcher、真实 frozen simulator PID/maps/私有 loader 链、正路径 typed restore 及独立 R0 科学审查仍待完成；旧 17/17 CPU fixture 和原 guard 修正继续保留，但不构成 R0 PASS。没有通过合成测试冒充真实资格。

## 后续条件

物理空间恢复及大额 V100/MLP/Oracle claims 的正式解除需各自 owner 证明；Source/raw/Native 数据的删除或迁移需要用户另行明确授权。本轮未进行物理清理，也未干预任何合法运行中的模型、raw 或锁。只有 fresh Native 安全底线与全部 R0 工程/独审 Gate 同时通过，后续明确任务才可依原合同考虑 C1；本轮保持 **STOP**。
