# Stencil EXT1 受控收尾设置

2026-11-10 17:27 UTC 现场：本点 request `EP_L2_OPTIONAL_CLEAN128_STENCIL_EXT1_20261110_V1` 唯一一次预算已消费，余额 0；cohort `EP_PERF_CLEAN128_STENCIL_WV_EXT1_20261110_V1` 的 UUID 为 `b45ebc64-24f1-4f45-a43b-566879d64734`。模型 PID 1602856、Native supervisor PID 1602833 仍运行。Native `/root/data` 可用 29,859,418,112 B；准入时保留的其他 owner 写入保证、5 GiB 有效底线和单个全局 128 MiB 恢复窗口未更改。

唯一验收监视 PID 1603132 只在自然完成后调用一次 Native `accept`，承担应用验收、真164全 SHA 归档及两个不同 Native 目标恢复；失败停止，不重启或退款。新增的结果发布监视 PID 1605389 只读前一监视的终态和 Native 账本，唯有 `CLOSED_ACCEPTED` 且 claim 清空时才运行一次 `publish_ext1_final.py`，发布本点与已接受 EXT0/EXT2 的同源对照。它不启动模型、不登记预算、不调用 `accept`，52 小时有界；任何失败停止，不自动重试发布。

实时状态：执行根 `control/EXT1_BACKGROUND_MONITOR_STATUS.json`、`control/EXT1_FINAL_PUBLICATION_STATUS.json`。最终提交将在 `phase_v1/final_ext1_v1/` 生成；**本文件和当前提交只证明受控收尾已布置，不是 EXT1 结果、验收或归档已完成的声明。** 旧五点 `CLOSED_ACCEPTED` 及旧 request 余额 0 保持原位。完整 raw 保留在 174-new 执行根，Source KEEP。

既有同输入运行显示本次自然模拟总墙钟约 5–8 小时，仅为排期估计。若模型自然结束并验收通过，EP-L2-8 应以最终固定 commit、Native registry、归档 SHA 和两份恢复回执审查结论；若任何环节停止，保留一次消费和错误证据，由 Main 手工诊断，不自动重新启动科学点。
