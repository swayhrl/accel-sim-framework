# C12 progress checkpoint 02

时间：`2026-09-09T07:29Z`；状态：`IN_PROGRESS_C5_REPLAY`。

冻结执行身份未变化：Framework functional anchor
`d64408a97d76a320a6d49468653d416e33677af8`、Core
`57bb71ecd015b6ec0ab32e45b0815e5beaf69172`、binary SHA-256
`2351f67bba60d333fdcc08b4cea81f39082958da67982d497ee8b4d83f321d3a`。

- 正式 terminal `PASS`：10/22 — Decode1 F0/F2/F5/F7-L10/F8-L10/F9，以及
  Prefill F0/F2/F5/F7-L10。所有已通过 arm 具有完整 marker、telemetry、对象/PTE
  守恒、arm-specific invariant 与 raw-log SHA 索引。
- 正在执行：8 个独立 arm；每个 output dir 保持恰好一个 `accel-sim.out` owner。
  余下 12 个矩阵点由既有 scheduler 以冻结的 P2/P3 顺序继续补位。
- 此批新增 terminal 是 Prefill F2、F5、F7-L10。它们的 simulator 都先以 exit `0`
  完成；旧 collector 将有限浮点 IPC 误作 integer。F5 还受到已修正的
  physical-PWC-payload 与 whole-arm-budget 混淆影响。当前 parser 在相同、完整 raw
  log 上重解析三点均为 `PASS`，没有重放、没有 identity/input/source 修改。

资源继续为 GREEN（约 168 GiB `MemAvailable`、memory/io PSI full 为 0、无 swap
activity、iowait 约 0.08%）。本 checkpoint 仅提交轻量审阅状态、结果索引与审计文字；
不包含 raw log、trace、binary、config、registration 或 simulator source，也不改变
正在运行的 C5 worker。
