# EP-L2 optional CLEAN128 五点执行：首次资源准入 HOLD

截至 2026-11-09 13:58 UTC，EP-L2 Main 已接受本轮正式五点授权，并完成 Source5、输入、实际 283 项配置、Host/consumer、Native 路由与逐点 Spec 绑定。共享 Native epoch 2 下，两族 scoped 请求各登记一次：GEMM 预算 3、Stencil 预算 2。五点的 Native `prepare` 均通过，均未消费、未启动；无 UUID、cycles 或应用接受结果。

| 点 | Native cohort | 状态 |
|---|---|---|
| GEMM EXT0 | `EP_PERF_CLEAN128_GEMM_WV_EXT0_20261109_V1` | 资源 HOLD；消费 0 |
| GEMM EXT1 | `EP_PERF_CLEAN128_GEMM_WV_EXT1_20261109_V1` | 资源 HOLD；消费 0 |
| GEMM EXT2 | `EP_PERF_CLEAN128_GEMM_WV_EXT2_20261109_V1` | 资源 HOLD；消费 0 |
| Stencil EXT0 | `EP_PERF_CLEAN128_STENCIL_WV_EXT0_20261109_V1` | 资源 HOLD；消费 0 |
| Stencil EXT2 | `EP_PERF_CLEAN128_STENCIL_WV_EXT2_20261109_V1` | 资源 HOLD；消费 0 |

两族先后独立阶段化准入，均返回 `confirmed remaining writes + own future writes exceeds native free`。脚本已撤回临时 claims，当前 `DISPATCH_CLAIMS.json` 为 `{ "claims": {} }`；未调用 `run-native`，未建立第二 dispatcher。完整首次准入记录见两份 `STAGED_ADMISSION_*.json`。

## 现场空间账（13:58:14 UTC）

| 字段 | GEMM | Stencil |
|---|---:|---:|
| Native 当前可用 | 20,480,413,696 B | 20,480,413,696 B |
| 其他请求剩余写入承诺，含另一五点家族 | 20,663,247,922 B | 20,730,356,786 B |
| 本家族写入承诺 | 270,532,608 B | 203,423,744 B |
| 适用 Native 安全底线 | 5,368,709,120 B | 5,368,709,120 B |
| 所需 Native 空间 | 26,302,489,650 B | 26,302,489,650 B |
| 当前缺口 | **5,822,075,954 B（约 5.42 GiB）** | **5,822,075,954 B（约 5.42 GiB）** |

Stencil 冻结策略自身写 1 GiB，实时资源快照确认的其他 owner Native 底线为 5 GiB，准入采用两者较高值。真实 164 挂载已核实，可用约 42.23 TB；它不能代替 174-new 的 Native 热工作盘。其他 owner 的已公布写入承诺仍原额计入；历史 pool ceiling 没有再当作额外写入重复叠加。上述数值是带时间的现场快照，后续必须重新采样。

## 接续条件

按现行准入合同，需要 174-new 的 Native 可用空间增加，或由相应 owner 正式关闭其剩余写入承诺，使实时账达到 `其他请求承诺 + 本家族承诺 + 5 GiB 安全底线`。本 Main 不清理旧资产、不削减其他 owner 保证、不自动重试退款。空间由用户处理后，本 Main 重新核对 registry/epoch、claims、模型、真 164 与实时资源，再为独立合格点阶段化并经共享 Native 精确入口一次性消费。当前不等待不存在的模型结果。

固定授权原文 SHA256：`900e9b6b1a31f1a9f3b8dd13c7e4580df415f27af3acc5727e59d930b7d7efc0`。现场 registry SHA256：`b8201d78a8dca6b406007c343391460c23c19169c15178fc44077eea935fb93d`。精确数值与版本修正见 `RESOURCE_HOLD_RECEIPT.json`；其前一版低估了 Stencil 的有效底线，已保留为历史版本并显式废止。
