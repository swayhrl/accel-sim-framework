# EP-L2 optional CLEAN128 五点执行：首次资源准入 HOLD

截至 2026-11-09 13:58 UTC，EP-L2 Main 已接受本轮正式五点授权，并完成 Source5、输入、实际 283 项配置、Host/consumer、Native 路由与逐点 Spec 绑定。共享 Native epoch 2 下，两族 scoped 请求各登记一次：GEMM 预算 3、Stencil 预算 2。五点的 Native `prepare` 均通过，均未消费、未启动；无 UUID、cycles 或应用接受结果。

这是用户授权 `EP_L2_OPTIONAL_CLEAN128_EXACT5_EXECUTION_V1` 的执行状态，不是交接快照里的“待授权”。授权确实允许五点各启动一次；当前阻塞来自实时资源准入。唯一 Main 管理预算、调度、验收、归档及 Git 集成。研究执行根为 `/root/data/ep_l2_full_workload_performance_20261027_v1/research/optional_clean128_exact5_execution_20261109_v1`；共享 Native 精确入口为 `/root/data/ep_l2_dtc_l1_native_v2/bin/native`。两族 request 分别为 `EP_L2_OPTIONAL_CLEAN128_GEMM3_20261109_V1` 和 `EP_L2_OPTIONAL_CLEAN128_STENCIL2_20261109_V1`；没有复用旧预算。

| 点 | Native cohort | 状态 |
|---|---|---|
| GEMM EXT0 | `EP_PERF_CLEAN128_GEMM_WV_EXT0_20261109_V1` | 资源 HOLD；消费 0 |
| GEMM EXT1 | `EP_PERF_CLEAN128_GEMM_WV_EXT1_20261109_V1` | 资源 HOLD；消费 0 |
| GEMM EXT2 | `EP_PERF_CLEAN128_GEMM_WV_EXT2_20261109_V1` | 资源 HOLD；消费 0 |
| Stencil EXT0 | `EP_PERF_CLEAN128_STENCIL_WV_EXT0_20261109_V1` | 资源 HOLD；消费 0 |
| Stencil EXT2 | `EP_PERF_CLEAN128_STENCIL_WV_EXT2_20261109_V1` | 资源 HOLD；消费 0 |

五点依序对应固定申请中的 `NEXT_A_OPTIONAL128_GEMM_WV_EXT0_V1`、`EXT1_V1`、`EXT2_V1` 及 `NEXT_A_OPTIONAL128_STENCIL_WV_EXT0_V1`、`EXT2_V1`。所有实际 cohort 的 `FROZEN_SPEC.json`、版本 1 原件、Native `prepare` 回执和配置覆盖文件都在远端审查包内。正式 Spec SHA256 依上述顺序为 `6dd21123c895d8ab9b3f546ee46f9b10d66a9adfbacede73af694bc893c3b740`、`e2c2944c7e235bcb9ce93b9cdeec6ba51f221e09247a1894d4bd6b7d2ac03d5c`、`ead81ca3c7fc10c6f43f983b8080b9393dd943b35be95653f57aebca6a156810`、`797b259611a59152bef3c62b8d2982633b3671b93feb1d0ce7a7e1f2f7396044`、`428303549ad6f2208055419906399957c5cd9d567f432e4336d58a5afc1e6860`。

Source5 固定 Core `3d3887bb2e8d5073d13b0792ff9116834e89fe2f`、Framework `9dd1ee57a83d83b56b7874bc7c716185ab52c8f7`、pybind11 `f90c430c3a1ce8f08c09942a5a1c3a797bb2295b`，ELF SHA256 `9db48c06ca64e441b5824071f52e0aa0be50374045fbdcef6cdf5d4469182f86`。GEMM 输入 SHA256 为 `140f6ed3a5cdb1d7183cd4d2acc37b086224a054893ef12d990fdb2d5ea3659b`，Stencil 为 `bd0309dfeec5745ba97400978c2c5f1413fa9c604376b3dd97e1dd3d5c8cc146`。五点均为 `WV_ZERO_RO`、G32×8、DRAM 850 MHz/L100，按精确申请的 ordered commands 与 283 项配置绑定；旧 Source78 性能不作为本轮 EXT0。

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

EP-L2-8 远端审查位置：仓库 `swayhrl/accel-sim-framework`，分支 `hrl/ep-l2-optional-clean128-exact5-20261109-v1`，目录 `docs/ep_l2/operations/ep_l2_optional_clean128_exact5_execution_20261109_v1/activated/`。该目录含小型源码、执行合同、五份 Spec、Native 资格、HOLD 回执和逐文件 SHA 索引；大 Trace、raw、模型和私有状态留原位。空间条件解除后需在同一分支后续提交真实消费、结果、验收、真164归档、双 Native 恢复与科学比较；现阶段这些结果均尚未发生。
