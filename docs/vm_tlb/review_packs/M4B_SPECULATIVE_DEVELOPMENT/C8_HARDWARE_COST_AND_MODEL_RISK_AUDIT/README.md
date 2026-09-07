# C8：硬件成本与模型风险审计

状态：`ANALYSIS_ONLY — SPECULATIVE_CANDIDATE`。本审计保留
`REFERENCE_APPROX_SUBENTRY_16` 与 `SPECULATIVE_CANDIDATE` 标签。它不修改冻结的
Core，不构建、不启动 simulator、不生成 trace，也不是 PPA 或性能结果。

## 本轮结论

唯一 C5 gate 为：

```
ARCHITECTURE_DECISION_REQUIRED
```

原因不是 C4 受限回放失败；C4 已验证软件状态机的语义计数。原因是当前模型尚未选择或
实现能够支撑性能解释的硬件合同：Weight Segment 使用 identity-like `SimPA`，依靠软件
object map 才能把请求识别为 Weight，并且没有 descriptor 端口/排队/复制与失效生命周期
模型。另一方面，`768` 个 sub-entry group 的 leaf 容量最高为 `12,288`，不能与 `768`
个 exact-page L2 TLB 条目宣称同预算。先做 C5 会把这些设计选择误当作已证实的硬件。

## 交付物

| 文件 | 回答的问题 |
| --- | --- |
| `WEIGHT_SEGMENT_HARDWARE_MODEL.md` | Weight descriptor、lookup 拓扑、并行 L1、映射和规模化是否可实现。 |
| `SUBENTRY_HARDWARE_MODEL.md` | exact/sub-entry 存储、关键路径、失效及替代方案的公平性。 |
| `FAIR_BUDGET_COMPARISON.tsv` | 用符号位数而非伪 PPA 数字建立同预算比较。 |
| `MODEL_RISK_REGISTER.tsv` | 逐项风险、证据、影响、C5 前动作。 |
| `SOFTWARE_RUNTIME_CONTRACT.md` | 可信硬件/驱动/运行时的最小合同与 stale 防护。 |
| `C5_PRECONDITION_DECISION.md` | 唯一 gate 与必须先作出的架构决策。 |
| `FINAL_REPORT.md` | C8 closeout 和验收矩阵映射。 |
| `INPUT_PROVENANCE.tsv` | 只读输入、冻结版本和分析边界。 |

“硬件可行”在本文意为可以给出一个完整而可验证的实现合同；不表示当前 simulator
shortcut 已经是该实现。所有容量、比较器与端口均为 symbolic cost model；本文没有报告
无工艺依据的面积、频率或功耗数字。
