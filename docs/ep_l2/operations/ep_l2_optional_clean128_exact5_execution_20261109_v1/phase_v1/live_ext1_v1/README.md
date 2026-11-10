# Stencil EXT1 单点执行中

2026-11-10 UTC：用户已授权的新增 Stencil EXT1 在固定 Source5、输入和 283 项配置上完成独立绑定、一次预算登记、Native 精确路由、无启动资格与实时准入。正式 Spec SHA256 `021ffd1c2c465bd21c043685566e316ffa8eee3ecf80113c94a8e8b42f37c54a`。

准入时 Native free `29939712000` B，保留其他 owner 未来写入 `8380228658` B、本点写入及全局 128 MiB 恢复窗口、5 GiB 有效底线后要求 `13952361522` B；RAM/CPU/真164 挂载检查通过。旧 request 状态字段仍为 RUNNING，但五点 cohort 均 CLOSED_ACCEPTED，旧写入保证不删。

本点一次消费已发生：request `EP_L2_OPTIONAL_CLEAN128_STENCIL_EXT1_20261110_V1`，cohort `EP_PERF_CLEAN128_STENCIL_WV_EXT1_20261110_V1`，UUID `b45ebc64-24f1-4f45-a43b-566879d64734`；模型 PID `1602856`、CPU `128`，受控后台 supervisor PID 1602833、终态监视 PID 1603132。监视只在自然完成后调用一次 `accept`，包括真164 full SHA 归档和两个不同 Native 目标恢复；失败保留证据且不自动重试。当前结果、应用 cycles 和最终归档状态仍待模型自然结束，不能当成已接受。

审查小文件见本目录，精确 Host 和资源适配源码见 `runtime/`；原始运行日志及 raw 保留在 174-new 执行根，不纳入 Git。
