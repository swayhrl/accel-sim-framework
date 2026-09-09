# C12 progress checkpoint 03

时间：`2026-09-09T12:12Z`；状态：`IN_PROGRESS_C5_REPLAY`。

冻结执行身份未变化：Framework functional anchor
`d64408a97d76a320a6d49468653d416e33677af8`、Core
`57bb71ecd015b6ec0ab32e45b0815e5beaf69172`、binary SHA-256
`2351f67bba60d333fdcc08b4cea81f39082958da67982d497ee8b4d83f321d3a`。

- 正式 terminal `PASS`：12/22。Checkpoint 02 之后新增 Decode1 F7-L5 与 F7-L20；
  两者均有完整 `740/740` marker/telemetry、对象/PTE 守恒、arm-specific invariant
  与 raw-log SHA 索引。
- Decode1 F7-L20 的初始失败由 parser 的 wait-both 假定造成：它错误要求所有
  Segment launch 都成为 hit/miss。依 C9 `HIT_FIRST / MISS_JOIN`，慢 Segment 可在
  L1-first completion 后成为 late discard。原始 counters 精确满足 completion 和
  late-discard 守恒；在同一 raw log 上以该冻结语义重解析后为 `PASS`。详见
  `FAILURE_RETRY_AUDIT.md`。没有 replay、identity 或输入改变。
- 正在执行：8 个唯一 owner arm。F7-L20 的 slot 被冻结 P2 队列中的 Prefill F8-L20
  自动补位；不改变 22 点矩阵或优先级。余下 10 个点将由既有 scheduler 继续完成。

资源保持 GREEN（约 85 GiB `MemAvailable`、memory/io PSI full 为 0、无 swap activity、
iowait 近零）。本 checkpoint 只固化小型状态、结果索引与审计文字；不包含 raw log、
trace、binary、config、registration 或 simulator source，且不影响运行中的 C5 worker。
