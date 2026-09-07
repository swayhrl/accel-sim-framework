# C8 final report — Hardware Cost and Model Risk Audit

状态：`COMPLETE — ANALYSIS_ONLY`。

标签保持不变：`REFERENCE_APPROX_SUBENTRY_16`、`SPECULATIVE_CANDIDATE`。

## 直接回答

当前冻结模型足以作为一个**软件状态机候选**，但还不能对应为“合理、可实现、可公平比较的
GPU translation architecture”。Weight Segment 的 PA mapping、可信分类、port/throughput 与
lifecycle 尚未定义；sub-entry 使用 768 groups 而非 768 leaves，未在同存储预算下与 exact
TLB/PWC/2MiB alternative 比较。因此唯一 C5 gate 是：

```
ARCHITECTURE_DECISION_REQUIRED
```

没有启动 C5，也没有 build、simulator、trace、新实现、Core 修改或 Window A/B 操作。

## 主要发现

### Weight Segment

- 有可实现路径：privileged driver 为一个 context 受控、物理连续或经受控间接映射的
  Weight allocation 安装 descriptor；硬件做 context/range/permission/epoch match，并以
  明确 port/bank/queue 服务请求。对 C4 的 `N=1` 这可能很小，但不是当前 vector 的自动
  硬件等价物。
- 当前 range vector 仅持有 `start,end`，且命中返回 identity-like `ppn=vpn`。没有
  `PA_base`/mapping root、ASID、permission 或 epoch；固定 ASID 0 未覆盖多 context。
  这是 `HIGH_MODEL_RISK`，不允许拿 C4 latency/resource numbers 代表真实 PA translation。
- range eligibility 经 simulator object map 的 `OBJECT_WEIGHT` gate，虽然该 map 被定义为
  observability metadata。真实硬件必须以 driver-proven allocation/range 作为来源，不能
  “知道 Weight”。
- C4 的 35 cluster、每 cluster 1 L1 port，给出最高 35 lookup/cycle ingress；当前 Segment
  无 port/queue state 且对所有初始 lookup launch。共享 1-port table、banked table 和
  35份 per-SM replica 的吞吐、成本、L1-hit 影响不同。`10=10` 只是在无队列模型中掩盖
  了 `max(TL1,Tsegment+queue)` 的等待。
- `N=1/4/16/64` 的 symbolic descriptor/compare/port scaling 已给出；没有任何无工艺依据
  的面积、功耗或频率数字。

### Sub-entry

- 64KiB、16 leaf group 的 base tag 从 `V=33` VPN bits 降到 `B=29`，但每个 leaf 仍须存
  valid、PPN 和可能的 protection/attribute state。C++ 64-bit fields 和 software timestamp
  没有被误作硬件位数。
- 现有 `768` groups 的最大 leaf capacity 是 `768*16=12,288`，而 exact baseline 为 768
  translation。因此同名 `entries=768` 不是 equal-bit、也不是 equal-capacity 比较。
- critical path 要包括 base-tag way compare、16:1 leaf valid/PPN select、permission check、
  fill arbitration 与 group replacement；固定 80 cycles 未说明它们能否与 exact L2 相同。
- ASID-scoped group/leaf invalidation、racing fills、migration、context reuse 与 superpage
  priority 必须定义。candidate 的 2MiB reject 是范围限制；不可把它悄然从公平 baseline
  中删除。

### 既有 C4/C7 证据的正确边界

C4 的 512 次 Segment hit 与 `1539=512+1027`、raw/effective L1、L2/MSHR/walker/PWC/PTE
守恒仍是已验证的 simulator state-machine 证据。suppression 计数表示 request 没有进入
conventional path，不表示 512 个独立物理 L2/PTE/walk 被消除。C7 Weight `HIGH` 和
sub-entry `MEDIUM` 仍是 analytical opportunity，不因本审计改变，却不能抵消 architecture
风险。

## C8 acceptance mapping

| 验收项 | 结果 | 证据 |
| --- | --- | --- |
| C8-A1 | PASS | `INPUT_PROVENANCE.tsv` 与本报告停止点：未启动 simulator/build/new trace/C5/大 ROI scan。 |
| C8-A2 | PASS | `INPUT_PROVENANCE.tsv` 绑定只读 Core `c21137bc`；最终 Core status/HEAD 再核对。 |
| C8-A3 | PASS | provenance scope boundary 及最终操作审计：Window A/B 未触碰。 |
| C8-A4 | PASS | `INPUT_PROVENANCE.tsv` 显式绑定 C1/C3/C4/C7、C8 docs 与 Core SHA。 |
| C8-A5 | PASS | `WEIGHT_SEGMENT_HARDWARE_MODEL.md`：descriptor 字段、`D` 公式及缺失 ASID/PA/protection/lifecycle。 |
| C8-A6 | PASS | 同文件：N=1/4/16/64 comparator/table/placement/port/latency alternatives。 |
| C8-A7 | PASS | 同文件：35 ingress、parallel L1 `max()`、queue/backpressure/replication 风险。 |
| C8-A8 | PASS | 同文件与 runtime contract：identity `ppn=vpn`、migration/remap/UVM 风险。 |
| C8-A9 | PASS | `SOFTWARE_RUNTIME_CONTRACT.md`：ASID、install/remove、epoch/invalidation、load/unload。 |
| C8-A10 | PASS | 同文件：privileged driver provenance 与 object map telemetry-only boundary。 |
| C8-A11 | PASS | Weight hardware model、runtime contract及 FB9：1/4/16/64 symbolic scaling。 |
| C8-A12 | PASS | `SUBENTRY_HARDWARE_MODEL.md`：exact/group/leaf state和 replacement accounting。 |
| C8-A13 | PASS | 同文件：base-tag/leaf/fill/replacement/invalidation/superpage audit。 |
| C8-A14 | PASS | `FAIR_BUDGET_COMPARISON.tsv` FB1--FB11：baseline/larger L2/PWC/2MiB/subentry/segment/combined。 |
| C8-A15 | PASS | 成本只用 `A,P,Q,Z,R,N,V` symbolic model；无 unsupported PPA。 |
| C8-A16 | PASS | `MODEL_RISK_REGISTER.tsv`：17 项分类、影响和最低解法。 |
| C8-A17 | PASS | `C5_PRECONDITION_DECISION.md`：只选择 `ARCHITECTURE_DECISION_REQUIRED`。 |
| C8-A18 | PASS | 仅新增 Framework review documents；没有 candidate/Core/config implementation 或执行工作负载。 |
| C8-A19 | PASS | 本目录包含 mandatory deliverables、provenance、风险与一致性的 acceptance mapping。 |
| C8-A20 | PASS | 本 closeout 仅 commit/push 此审计包，随后停止供独立评审。 |

## 停止点

C8 到此停止。没有自动发起 C5，也没有进入 KV segmentation、12K KV 或 M5。后续只能在
相关 architecture decisions 获批准、模型工作被单独授权、standard-mode correctness 可验证，
并且原有 farm/resource gate 满足之后重新发起。
