# C12 Operator-Aware Operator Taxonomy

本文件冻结 `C12_OPERATOR_AWARE_CHARACTERIZATION` 的算子分类口径。分类目标是**可审计、可保守失败**，而不是尽可能把所有 kernel 强行贴标签。

---

## 1. 一级 operator class

### `ATTENTION_PROJECTION`

定义：由模型 Weight 参数范围直接证明 kernel 读取 Attention projection 参数。

典型参数族：

- `q_proj`
- `k_proj`
- `v_proj`
- `o_proj`

证据优先级：`DIRECT_PARAMETER_RANGE`。

如果一个 kernel 同时读取上述多个 projection 参数，仍可归入 `ATTENTION_PROJECTION`，并在 `evidence_detail` 中列出全部参数。

---

### `ATTENTION_CORE`

定义：不依赖 Weight projection 参数，而 semantic kernel name 本身直接表明其执行 Attention 核心运算，例如明确的 FlashAttention / SDPA / attention kernel。

证据：`DIRECT_SEMANTIC_NAME`。

仅含 `softmax`、`reduce`、`matmul` 等泛化词时，不自动归入本类；需要额外直接证据，否则进入 `OTHER_COMPUTE` 或 `UNRESOLVED`。

---

### `FFN_MLP`

定义：由模型 Weight 参数范围直接证明 kernel 读取 FFN/MLP 参数。

典型参数族：

- `gate_proj`
- `up_proj`
- `down_proj`

证据优先级：`DIRECT_PARAMETER_RANGE`。

---

### `NORM`

定义：直接访问归一化参数，或 kernel name 明确指向 RMSNorm/LayerNorm 等归一化操作。

典型参数族/名称：

- `input_layernorm`
- `post_attention_layernorm`
- final `norm`
- semantic name 中明确的 `rmsnorm` / `layernorm`

证据：`DIRECT_PARAMETER_RANGE` 或 `DIRECT_SEMANTIC_NAME`。

---

### `ROPE`

定义：semantic kernel name 明确指向 rotary embedding / RoPE。

证据：`DIRECT_SEMANTIC_NAME`。

不能仅靠执行顺序推断。

---

### `EMBEDDING_OUTPUT`

定义：直接访问 embedding 或 output-head Weight 参数。

典型参数族：

- `embed_tokens`
- `lm_head`
- 其他由实际 sidecar parameter name 证明的 embedding/output parameter

证据：`DIRECT_PARAMETER_RANGE`。

---

### `MIXED_DIRECT`

定义：同一 kernel 有两个或以上互相跨一级类别的 direct evidence，例如同时直接读取 Attention projection 与 FFN Weight，且不能证明只是统计/边界伪影。

必须保留所有 constituent classes，不得为了方便聚合强制选择一个类别。

---

### `OTHER_COMPUTE`

定义：已确认是 compute kernel，但 direct evidence 只能说明其不属于上述明确类别，或 semantic name 指向通用 elementwise/copy/reduction 等操作。

`OTHER_COMPUTE` 不等于 Activation，也不等于“不重要”。

---

### `UNRESOLVED`

定义：当前证据不足以可靠分类。

`UNRESOLVED` 是合法结果；不得为了 coverage 将其自动按模型执行顺序归入 Attention/FFN。

---

## 2. Evidence kind

每个 kernel 必须有且仅有一个最高主证据等级，同时可以记录辅助证据。

### `DIRECT_PARAMETER_RANGE`

trace 中真实访存地址与 runtime sidecar `weight_layout` 中某个 parameter SimVA range 精确相交。

这是 Weight-based operator 分类的首选直接证据。

### `DIRECT_SEMANTIC_NAME`

embedded `-kernel name = ...` 本身明确指出算子类型。

禁止从 opaque trace filename 推断。

### `MIXED_DIRECT`

存在多个相互冲突或跨类的 direct parameter/name evidence。

### `HEURISTIC_SEQUENCE`

仅依据 kernel 前后顺序、Transformer block 周期性、邻近 direct-labeled kernel 等推断。

此等级**不得进入 formal measured operator aggregate**；只能单独用于 heuristic sensitivity。

### `UNRESOLVED`

没有足够证据。

---

## 3. Formal operator group

为了形成更高层图表，可定义以下二级 group：

- `ATTENTION` = `ATTENTION_PROJECTION` + `ATTENTION_CORE`
- `FFN` = `FFN_MLP`
- `OTHER_MODEL` = `NORM` + `ROPE` + `EMBEDDING_OUTPUT`
- `OTHER_COMPUTE` = `OTHER_COMPUTE`
- `MIXED` = `MIXED_DIRECT`
- `UNRESOLVED` = `UNRESOLVED`

但 formal aggregation 只能纳入 `DIRECT_PARAMETER_RANGE`、`DIRECT_SEMANTIC_NAME`、`MIXED_DIRECT`。`HEURISTIC_SEQUENCE` 必须单独输出。

---

## 4. Layer ID

如果 parameter name 中存在明确 Transformer layer 编号，则解析为 `layer_id`。

规则：

- 只从实际 parameter name 解析；
- 不根据 kernel 序号推断 layer；
- 一个 kernel 访问多个 layer 时，标记 `MULTI_LAYER` 并列出全部 layer；
- 没有直接 layer 证据时为 `NA`。

---

## 5. 地址分类边界

### Weight

使用 runtime flat Weight allocation 的 SimVA base + `weight_layout.tensors[].offset_bytes/size_bytes` 建立精确 parameter ranges。

### KV Cache

KV 仍按已有 runtime sidecar / C4 object map contract 识别，不用 kernel operator 标签反推 KV 地址。

### UNKNOWN

未被现有对象证据覆盖的地址继续为 `UNKNOWN`。禁止将 `UNKNOWN` 统一解释为 Activation/Workspace。

---

## 6. 冲突处理

如果 direct parameter evidence 与 direct semantic name 冲突：

1. 不静默覆盖；
2. 标记 `MIXED_DIRECT` 或 `CONFLICT_DIRECT_EVIDENCE`；
3. 在 `evidence_detail` 中完整记录双方证据；
4. 从 formal Attention/FFN二分统计中单独拿出，直到人工/代码审计解决。

---

## 7. 不允许的分类方式

以下方式不能单独作为 formal operator 标签：

- trace filename；
- kernel 序号模式；
- “每层大约有N个kernel”这种模板猜测；
- Weight/KV访问量高低本身；
- Cache/TLB miss率高低；
- 性能收益方向；
- 为了让某一机制显得更有效而事后修改分类阈值。

---

## 8. 期望的最终解释层次

最终报告优先回答：

1. `ATTENTION_PROJECTION` 与 `FFN_MLP` 谁贡献主要 Weight translation footprint；
2. `ATTENTION_CORE` 是否贡献主要 KV reuse；
3. Prefill/Decode 中同一 operator group 的 Weight/KV/Cache/TLB 行为是否发生系统性变化；
4. Segment/PWC/Sub-entry 的机制活动和性能收益是否集中在特定 operator；
5. 若无法证明，则明确保留 `UNRESOLVED`，不夸大。