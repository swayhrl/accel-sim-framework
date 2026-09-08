# C12 / C5 全负载公平性能实验验收矩阵

## Gate A — 输入与身份

| 检查 | 通过条件 |
|---|---|
| primary points | 22/22 与 C11 `C5_ARM_MATRIX.tsv` 完全一致 |
| binary SHA-256 | `2351f67bba60d333fdcc08b4cea81f39082958da67982d497ee8b4d83f321d3a` |
| Core | `57bb71ecd015b6ec0ab32e45b0815e5beaf69172` |
| functional/config anchor | `d64408a97d76a320a6d49468653d416e33677af8` |
| prefill trace | 692 entries；SHA `a40d6832219e5b0a6232875bb181754ac121bb5f867c9b13c84370e2a2cb6e6f` |
| decode1 trace | 740 entries；SHA `b6c42eb1932fcacefc2429b91a2015d38003a764a5319fe4bcbaf65b3d0cd0dc` |
| prefill registration | SHA `6ae0e18cc3bba29871002c4ff1877052489740163424723a845ead45c4a5f4b0` |
| decode1 registration | SHA `3dc77c1f348028ba7b8abfef3dc6c4cffa0c9678f003bc23bdc9158d62762b48` |
| PA contract | `MODELED_DRIVER_PA / C5_MODELED_PA_HIGH_UNUSED_BIT_V1`；同 ROI 所有 arms 共用 |
| excluded arms | F3/F4/F6/H0 不执行 |

Gate A 任一失败：不得启动 C5 arm。

## Gate B — F0 基线

Prefill F0 与 Decode1 F0 均需：

- exit = 0；
- kernel marker = 692 / 740；
- telemetry record = 692 / 740；
- exact-once / quiescence PASS；
- PTE conservation PASS；
- object attribution conservation PASS；
- hash identity PASS；
- raw log + time-v sidecar 完整。

两个 F0 都 PASS 后，才允许正式计算 speedup。

## Gate C — 22/22 terminal

每个 primary point 必须归入且只能归入：

- `PASS`
- `FAILED_DIAGNOSING`
- `INVALIDATED_BY_IDENTITY_CHANGE`
- `HARD_BLOCKED`

最终成功要求 22/22 = PASS。

任何 resource kill / launcher error 不可直接记为 HARD_BLOCKED。

## Gate D — Arm-specific correctness

### F1

- G96 geometry 正确；
- `REFERENCE_APPROX_SUBENTRY_16` 标签保留；
- sub-entry counters 可解析。

### F5

- 120-entry physical PWC；40/40/40；four-way；
- charged bits = 64,745；
- 不是 legacy logical 128-entry PWC；
- queue/port/replacement/flush/drain invariants PASS。

### F7

- Segment N=8；35 replicas；
- exact remainder = 320；
- charged bits = 65,300；
- Lseg 5/10/20 均完成；
- Segment hit 返回 common modeled PPN。

### F8

- Segment N=8 + G32；
- charged bits = 57,734；
- Lseg 5/10/20 均完成；
- `REFERENCE_APPROX_SUBENTRY_16` 与 `SPECULATIVE_CANDIDATE` 标签均保留。

### F9

- exact-656；charged bits = 56,375；
- 作为 F8 no-Segment comparator。

## Gate E — 公平性

同 ROI 内所有 arms：

- 相同 trace-list；
- 相同 driver PA registration；
- 相同 modeled PA layout；
- 相同 simulator binary；
- 仅允许 frozen arm config 差异；
- 不允许因 Segment enable/disable 改变普通 PTW 的 PPN。

如发生 binary/config/registration/trace 语义变化，旧 arm 全部失效，不得跨 identity 计算 speedup。

## Gate F — 结果指标完整性

每个 arm 至少输出：

- cycles / instructions / IPC；
- L1/L2 TLB accesses/hits/misses；
- TLB replacement/port stalls；
- MSHR alloc/merge/full/wait/high-watermark/lifetime；
- walker/PWQ；
- PWC counters；
- PTE requests/responses/L2-only/DRAM/wait；
- requester latency total/max；
- L1D/L2 outcome；
- L2 queue pressure；
- DRAM/native memory latency；
- object attribution conservation；
- arm-specific Segment/Sub-entry/PWC telemetry。

缺关键字段不得 silently 填 0；必须标 `NOT_EMITTED` 并判断是否违反 acceptance contract。

## Gate G — 核心比较表

必须有：

1. F1 vs F2；
2. F5 vs F0；
3. F7-L10 vs F0；
4. F7-L5/L10/L20；
5. F8-L10 vs F9；
6. F8-L10 vs F1；
7. F8-L5/L10/L20；
8. Prefill vs Decode 的机制收益差异。

所有 speedup 只相对同 ROI 的 C5 F0 或明确指定 comparator。

禁止把 A/C4 的 cycles 当作 C5 baseline。

## Gate H — 机制解释边界

最终报告必须分层：

- `MEASURED_FULL_ROI_FACT`：直接测量值；
- `SUPPORTED_MECHANISM_SIGNAL`：由多项独立 telemetry 一致支持的机制信号；
- `UNRESOLVED`：仍缺直接因果证据。

以下表述不允许仅凭单计数器给出：

- “miss 少所以性能一定更高”；
- “队列更高就是唯一瓶颈”；
- “Segment 已证明是最优架构”；
- “modeled PA 等同真实硬件 PA”。

## Gate I — 工程与证据管理

- 每个 arm 独立输出目录；
- raw log 不覆盖；
- failed attempts 隔离保存；
- parser-only fix 可重新解析，不必重跑；
- semantic identity change 必须全矩阵重启；
- `git add .` / `git add -A` 禁止；
- review pack 只提交小型结构化结果、脚本和文档，不提交巨大 raw logs/traces。

## Final success

仅当 Gate A–I 全部通过，且 22/22 primary points PASS：

`C12_C5_FULL_ROI_COMPLETE_READY_FOR_REVIEW`
