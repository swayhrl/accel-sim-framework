# C9 final report — Segment / Sub-entry Architecture Decision

状态：`COMPLETE — DESIGN_ONLY`。

## 唯一最终决定

```
ARCHITECTURE_READY_FOR_MODEL_IMPLEMENTATION
```

该决定关闭的是未来 v1 **模型实现**的架构前提，不是 C5 授权。C9 没有启动 C10/C5、build、
simulator、trace、PPA 或 Window A/B 操作。

## 已关闭的架构问题

### Weight Segment

- `C9_MODEL_DECISION`: hit 由可信 descriptor 的真实 PA 算术给出：
  `PPN = PA_base_PPN + (VPN - VA_base_VPN)`，并恢复 byte offset。identity `ppn=vpn` 被拒绝。
- `C9_MODEL_DECISION`: descriptor 包含 valid、16-bit ASID、33-bit VA base/limit、33-bit PA
  base、read-only、mapping class 和 16-bit epoch，共 135 accounting bits。只注册完整 64KiB
  页；非连续 Weight allocation 分裂为最大物理连续 extent。
- `C9_MODEL_DECISION`: privileged driver 验证 allocation/context/rights/pinning，并原子安装
  或完整回退 ordinary paging。`OBJECT_WEIGHT` object map 永远只作 telemetry。
- `C9_MODEL_DECISION`: v1 选择 35 份本地复制、总 8 slots、一个 provisioned ASID 的 table，
  每 local cluster 1 accept/cycle。N=1/4/8/16/64 的 descriptor/compare/replica proxy 已明确。
- `C9_MODEL_DECISION`: `HIT_FIRST / MISS_JOIN` 取代 wait-both。L1 hit 或 Segment hit 都能先
  完成；一个先出现的 miss 等待另一方；只有双方 miss 发射一次 L2。双 mapping 不一致是 fault。
- `C9_MODEL_DECISION`: `Lseg` 为参数，5/10/20 是必跑敏感性点，10 只是 compatibility point。
  local v1 match L1 ingress，因此 nominal queue 为零；带宽不足必须显式建模 queue/backpressure。
- `C9_MODEL_DECISION`: pinned immutable inference epoch 定义 install/ack/inference/revoke/ack/
  remap-free 顺序，ASID+epoch 防 stale。active epoch 内不支持 arbitrary migration/UVM remap。

### Sub-entry 与公平性

- `C9_MODEL_DECISION`: 64KiB exact baseline 为 `66,000` accounting bits。ABI 是 ASID=16、
  VPN/PPN=33、leaf attributes=2、16-way PLRU=15 bits/set。
- `C9_MODEL_DECISION`: 16-leaf group 为 622 bits。`G_equal_bit=96`（59,802 bits、1,536
  leaves）；112 groups 超基线。历史 768 groups（478,416 bits、12,288 leaves）永久排除。
- `C9_MODEL_DECISION`: base-tag/leaf select、existing/new group fill、PLRU replacement、leaf/group
  invalidate、ASID generation fill race 和 2MiB-reject scope 均已冻结。
- `C9_MODEL_DECISION`: Segment replicas 被全额收费。N=8 的 35 replicas 为 37,800 bits；
  combined candidate 只能是 32 groups（512 leaves），不是 96/768。
- `C9_MODEL_DECISION`: F0--F9 政策冻结 baseline exact、bit-matched/expanded exact、leaf-capacity
  diagnostic、pointer-payload PWC、2MiB diagnostic、charged Segment 和 charged combined。

### A checkpoint 的使用边界

`EXISTING_MODEL_FACT`: 只读 A checkpoint 提示 translation headroom，且“更少 miss 不保证更少
cycles”。它只促成 C10 记录 queue/backpressure/latency/stall；未与 C 数据混合，也没有用于
选择 N、G 或 Lseg。paper prefill 未完成，因而没有任何比较结论。

## C9 acceptance mapping

| 条件 | 结果 | 证据 |
| --- | --- | --- |
| C9-A | PASS | `INPUT_PROVENANCE.tsv` 绑定 C8 `468fe62d`、Core `c21137bc`、paper spec、A `73d25ebb`。 |
| C9-B | PASS | README/全部 spec 使用规定的五种 evidence labels。 |
| C9-C | PASS | `WEIGHT_SEGMENT_ARCHITECTURE_SPEC.md`：真实 base+offset PA mapping，禁止 identity。 |
| C9-D | PASS | `SEGMENT_DESCRIPTOR_AND_LIFECYCLE.md`：privileged registration、permissions、capacity/error fallback。 |
| C9-E | PASS | Weight spec：比较 three topologies、N=1/4/8/16/64，选择 local N=8。 |
| C9-F | PASS | `SEGMENT_LOOKUP_ORDERING_AND_THROUGHPUT.md`：完整 `HIT_FIRST / MISS_JOIN` transition table。 |
| C9-G | PASS | 同文件：1 accept/cycle/local、queue contract、5/10/20 和 timing decomposition。 |
| C9-H | PASS | lifecycle spec：pinned epoch、install/revoke ack、migration/remap/free/context/ASID reuse。 |
| C9-I | PASS | `SUBENTRY_EQUAL_BIT_BUDGET.md`：hardware-relevant formula，旧 768 group 明确非 equal-cost。 |
| C9-J | PASS | 同文件：concrete `G_equal_bit=96`，并给出 112 不可行边界。 |
| C9-K | PASS | `FAIR_BASELINE_POLICY.md` F0--F9：exact/PWC/2MiB/leaf/Segment/combined。 |
| C9-L | PASS | sub-entry spec：tag/leaf/fill/replacement/invalidation/ASID race/2MiB scope。 |
| C9-M | PASS | `A_CHECKPOINT_IMPLICATIONS.md`：motivation-only，禁止 A/C pooling/tuning。 |
| C9-N | PASS | `C10_IMPLEMENTATION_REQUIREMENTS.md`：bounded delta、tests、regressions、historical evidence boundary。 |
| C9-O | PASS | 仅 Framework documentation；Core clean/frozen；无 build/sim/C5/trace/PPA/A/B operation。 |
| C9-P | PASS | 只选择 `ARCHITECTURE_READY_FOR_MODEL_IMPLEMENTATION`。 |
| C9-Q | PASS | 本 closeout 仅 commit/push review pack，然后停止；不自动启动 C10/C5。 |

## Stop boundary

C10 仍需独立授权；之后才可能在完成其 directed/regression gates、fresh provenance 和 host
policy 后重新讨论 bounded/full replay。C9 到此停止，不进入 KV segmentation、12K、M5 或任何
functional implementation。
