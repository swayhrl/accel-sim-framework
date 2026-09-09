# C12 progress checkpoint 01

时间：`2026-09-09T06:22Z`；状态：`IN_PROGRESS_C5_REPLAY`。

冻结执行身份未变化：Framework functional anchor
`d64408a97d76a320a6d49468653d416e33677af8`、Core
`57bb71ecd015b6ec0ab32e45b0815e5beaf69172`、binary SHA-256
`2351f67bba60d333fdcc08b4cea81f39082958da67982d497ee8b4d83f321d3a`。

- 正式 terminal `PASS`：7/22 — Decode1 F0/F2/F5/F7-L10/F8-L10/F9，以及
  Prefill F0。每点均有完整 marker、telemetry、conservation 与 raw-log SHA 索引。
- 正在运行：8 个独立 arm — Prefill F2/F5/F7-L10/F8-L10/F9/F7-L5，以及
  Decode1 F7-L5/F7-L20；每个 output dir 只有一个 `accel-sim.out` owner。
- 尚未启动：7 个冻结矩阵点；scheduler 将在 worker slot 可用时按既有 P2/P3
  priority 补位，不改变输入或矩阵。

Prefill F0 的 simulator exit 为 0；初始 validator 仅因旧常驻 collector 把合法
浮点 IPC 判为 integer error 而暂时诊断失败。当前 parser 已在同一完整 raw log 上
reparse 为 `PASS`，没有重新运行 simulator。详见 `FAILURE_RETRY_AUDIT.md`。

最新资源样本保持 GREEN：约 158 GiB `MemAvailable`、memory/io PSI full 为 0、无
swap activity、iowait 约 0.06%。本 checkpoint 不含 raw log、trace、binary、config、
registration 或 simulator source；它只固化可审阅的状态与结果索引。
