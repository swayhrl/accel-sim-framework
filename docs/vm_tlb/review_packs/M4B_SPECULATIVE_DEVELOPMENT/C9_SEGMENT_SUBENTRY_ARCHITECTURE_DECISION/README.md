# C9：Segment / Sub-entry Architecture Decision

状态：`DESIGN_ONLY — ARCHITECTURE_READY_FOR_MODEL_IMPLEMENTATION`。

历史证据继续保持 `REFERENCE_APPROX_SUBENTRY_16` 与
`SPECULATIVE_CANDIDATE` 标签。C9 是新的一组项目架构决定，绝不是对论文未公开 RTL、
PPA 或 target artifact 的声称。

## 唯一最终决定

```
ARCHITECTURE_READY_FOR_MODEL_IMPLEMENTATION
```

这只授权未来一个单独批准的 C10 模型实现阶段；**不**在 C9 启动 C10、C5、build、
simulator 或 trace 工作。

## 已冻结的 v1 架构选择

| 主题 | C9_MODEL_DECISION |
| --- | --- |
| Weight mapping | context-bound、64KiB page-granular、物理连续 extent。`PA = PA_base + (VA - VA_base)`；非连续 allocation 拆成 descriptors，绝不使用 `ppn=vpn`。 |
| eligibility | privileged runtime/driver registration；object map 仅为 telemetry。 |
| Segment topology | 每 translation cluster 复制的、总计 `N=8` descriptor slots（一个 provisioned ASID）的小表；每 cluster 1 lookup/cycle。 |
| ordering | `HIT_FIRST / MISS_JOIN`：L1 hit 不等待慢 Segment；L1 miss 必须等待 pending Segment；仅双方 miss 才去 L2/PTW。 |
| latency | `Lseg` 参数化；nominal 10 cycles 是 reproduction point，sensitivity 为 5/10/20，不是硬件事实。 |
| lifecycle | pinned immutable inference epoch，ASID+epoch，driver install/revoke acknowledgement；overflow 或 registration failure 完整回退 conventional paging。 |
| standalone sub-entry | 64KiB-only、16 leaves/group、16-way，按 C9 accounting profile 的 `G_equal_bit=96` groups。 |
| combined fairness | local replicated Segment state 被全额计费；同 `B_total` 下 combined 为 32 groups，而非历史 768 groups。 |

## 证据标签

- `PAPER_SPEC`：论文规格明确陈述的事实；不扩展为未公开细节。
- `EXISTING_MODEL_FACT`：冻结 Core/C1--C8 的当前模型事实。
- `USER_APPROVED_DIRECTION`：本 C9 handoff 已明确授权的设计方向。
- `C9_MODEL_DECISION`：为了可实施、可审计的 v1 所作项目决定。
- `UNKNOWN`：论文/冻结模型未提供，不能伪造精度的事项。

## 文件索引

| 文件 | 内容 |
| --- | --- |
| `ARCHITECTURE_DECISION_RECORD.md` | 全部决定、来源标签与拒绝的替代方案。 |
| `WEIGHT_SEGMENT_ARCHITECTURE_SPEC.md` | descriptor 映射、N=1/4/8/16/64 topology 和 lookup 细节。 |
| `SEGMENT_DESCRIPTOR_AND_LIFECYCLE.md` | privileged registration、pin/epoch/invalidate/fallback 合同。 |
| `SEGMENT_LOOKUP_ORDERING_AND_THROUGHPUT.md` | `HIT_FIRST / MISS_JOIN` 状态机、端口、排队与 telemetry。 |
| `SUBENTRY_EQUAL_BIT_BUDGET.md` | concrete bit accounting 与 `G_equal_bit=96`。 |
| `FAIR_BASELINE_POLICY.md` | exact/PWC/2MiB/Segment/combined 的计费规则。 |
| `A_CHECKPOINT_IMPLICATIONS.md` | A checkpoint 的非数值动机及所需 stall observables。 |
| `C10_IMPLEMENTATION_REQUIREMENTS.md` | 受限未来实现 delta、tests 和不变量；未实施。 |
| `FINAL_REPORT.md` | C9 closeout 和 acceptance 映射。 |

没有无工艺依据的面积、功耗或频率数字。bit、compare-input、replica 和 port 均是透明的
symbolic/accounting proxy，不能当 PPA。
