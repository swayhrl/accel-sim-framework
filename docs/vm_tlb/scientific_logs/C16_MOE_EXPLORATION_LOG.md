# C16 MoE访存探索：过程、证据、阶段结论与下一问题

> **定位：Living scientific log**
>
> 本文件集中记录C16中与MoE访存行为有关的**探索过程、包括过往的accepted evidence、阶段结论、被降级/否定的解释、以及下一步科学问题选择**。
>
> 目的不是替代各阶段review pack，而是给后续研究者提供一条连续的科学主线：**我们为什么做、看到了什么、哪些结论成立、哪些原先的解释后来被修正、下一步为什么值得做。**
>
> 定量事实优先以node164 accepted authority和独立consumer重算为准。

---

## 0. 记录规则

### 0.1 证据等级

本文区分四类内容：

- **Accepted fact**：已经通过formal producer / consumer / authority闭合，可由版本库与node164 accepted raw追溯。
- **Interpretation**：基于accepted fact得到的阶段性科学解释，但不是因果证明。
- **Hypothesis**：下一步值得验证的假设。
- **Planned experiment**：尚未执行的实验设计，不得写成已有结论。

### 0.2 结论更新方式

- 新阶段若推翻或削弱旧解释，不删除旧结论，而是明确标记 **Superseded / 降级**。
- producer报告与receiver独立重算冲突时，以receiver / authority结果为准。
- 工程闭合只证明“证据可信”，不自动转化成科学结论。
- 多个模型落在同一runtime/kernel family时，不把“多模型共同现象”自动写成“独立实现共同现象”。

### 0.3 当前accepted shard证据不支持

除非后续实验合同明确改变，否则不能基于当前formal shards计算或宣称：

- cross-shard absolute VA union
- cross-shard global chronology
- cross-shard reuse distance
- fresh-process absolute VA关系
- 用shard顺序代表真实L2全局到达顺序
- 仅凭地址trace直接声称cache/TLB因果瓶颈
- 跨模型把相同static index当成相同机器指令
- 从单个frozen natural state推出routing population统计
- 把Q30 / DeepSeek / OLMoE三模型比较写成matched-input causal study

---

# 1. 起点：AI / MoE是否存在值得单独研究的访存行为？

C16最初的科学目标之一，是避免“因为MoE热门，就先设计MoE专用Cache/TLB机制，再去寻找支持它的实验”。

更合理的问题是：

> **真实MoE执行中，是否存在相对于普通Dense/GEMV更特殊、稳定、并且可被体系结构利用的访存行为？**

因此主线采用“先真实行为、后机制”的顺序：

1. 先在真实GPU上建立可审计的MoE expert访问证据；
2. 先从一个模型做清楚；
3. 再扩到独立模型lineage；
4. 区分“算子本身的共同结构”和“MoE路由真正带来的结构”；
5. 只有发现可利用机会后，才考虑Cache/TLB机制。

---

# 2. 第一条lineage：Qwen3-30B-A3B

## 2.1 Accepted authority

Producer：

`hrl/c16-qwen3-30b-s2-formal-capture-109-v3@28620a89d55fd9230103a31d31d14757b57e1e0f`

Accepted raw RUN_ID：

`C16R_qwen3-30b-a3b_s2-text_decode_nvbit-warp-mref-shard_s2-dec3-natural-expert21-down_20260917T034400Z_e210c0de5678`

node164 raw：

`/root/share/mnt164/huangrulin/c16_ai_workload/raw/C16R_qwen3-30b-a3b_s2-text_decode_nvbit-warp-mref-shard_s2-dec3-natural-expert21-down_20260917T034400Z_e210c0de5678`

核心语义：

- S2 Decode3
- Layer24
- natural Expert21
- `down_proj`
- BF16
- routing：top-8 / 128 experts
- input width：768
- output width：2048
- weight shape：`[2048,768]`
- weight bytes：3,145,728

## 2.2 Accepted / independently reproduced result

三-lineage consumer在174-new从node164 raw重新计算后，复现：

- selected static paths：243
- executed：41
- proven-zero：202
- failed：0
- dynamic warp records：100,352
- active-lane events：3,147,776
- executed fraction：0.168724

对象事件：

- WEIGHT：1,572,864
- INPUT：1,572,864
- OUTPUT：2,048
- OTHER：0

对象比例：

- WEIGHT：0.4996746909564086
- INPUT：0.4996746909564086
- OUTPUT：0.0006506180871828237
- OTHER：0

关键per-executed-shard分布：

- active-lane events：min 2,048 / median 65,536 / max 131,072
- unique 128B lines：min 12 / median 32 / max 24,576
- unique 4K pages：min 1 / median 2 / max 768
- unique 64K pages：min 1 / median 1 / max 48
- unique 2M pages：min 1 / median 1 / max 2

role-conditioned：

- WEIGHT shards：20
- INPUT shards：20
- OUTPUT shards：1
- MIXED：0
- OTHER：0

其中WEIGHT shard典型footprint：

- median unique 128B lines：24,576
- median unique 4K pages：768

INPUT shard典型footprint：

- median unique 128B lines：12
- median unique 4K pages：1

## 2.3 当时的解释

**Accepted fact**：一个自然路由expert的`down_proj`具有清晰的weight / input / output对象归属，并且weight和input事件量对称。

**当时仍未知**：这是Q30特有、GEMV特有，还是MoE expert普遍特征。

因此不能直接上升为“MoE共同规律”。

---

# 3. 第二条lineage：DeepSeek-V2-Lite

## 3.1 Accepted authority

Producer：

`hrl/c16-deepseek-v2-lite-s2-producer-109-v23r1@baf892ced6d66cbacabb995caf095e5280995097`

Accepted raw RUN_ID：

`C16R_deepseek-v2-lite_s2-text_decode_nvbit-warp-mref-shard_v23r1-moe-e4-down_20260917T024000Z_b23b23b23b23`

node164 raw：

`/root/share/mnt164/huangrulin/c16_ai_workload/raw/C16R_deepseek-v2-lite_s2-text_decode_nvbit-warp-mref-shard_v23r1-moe-e4-down_20260917T024000Z_b23b23b23b23`

核心语义：

- S2 selected decode state
- Layer1
- natural Expert4
- `down_proj`
- BF16
- routing：top-6 / 64 routed experts + 2 shared experts
- natural top-6：`[4,24,25,55,60,26]`
- input width：1408
- output width：2048
- weight shape：`[2048,1408]`
- weight bytes：5,767,168

## 3.2 Accepted / independently reproduced result

三-lineage consumer复现：

- selected static paths：243
- executed：169
- proven-zero：74
- failed：0
- dynamic warp records：362,496
- active-lane events：11,538,432
- executed fraction：0.695473

对象事件：

- WEIGHT：5,767,168
- INPUT：5,767,168
- OUTPUT：4,096
- OTHER：0

对象比例：

- WEIGHT：0.4998225062122826
- INPUT：0.4998225062122826
- OUTPUT：0.0003549875754348598
- OTHER：0

关键per-executed-shard分布：

- active-lane events：min 4,096 / median 65,536 / max 131,072
- unique 128B lines：min 1 / median 32 / max 4,096
- unique 4K pages：min 1 / median 2 / max 1,408
- unique 64K pages：min 1 / median 1 / max 88
- unique 2M pages：min 1 / median 1 / max 3

role-conditioned：

- WEIGHT shards：84
- INPUT shards：84
- OUTPUT shards：1
- MIXED：0
- OTHER：0

WEIGHT shard：

- median unique 128B lines：2,048
- median unique 4K pages：1,408

INPUT shard：

- median unique 128B lines：1
- median unique 4K pages：1

---

# 4. 两-lineage阶段：Q30 + DeepSeek

## 4.1 Accepted consumer

`hrl/c16-cross-model-moe-q30-deepseek-174new-v25@2538feb8862cd9b1828e9c805cb88ee46a4741ce`

V25第一次把两个独立模型lineage放到同一分析合同下比较。

## 4.2 当时成立的共同观察

两个自然路由BF16 expert `down_proj`都表现出：

- selected static paths = 243
- weight事件约占一半
- input事件约占一半
- output极小
- OTHER = 0

同时两者在执行覆盖率和footprint上明显不同：

- Q30：41 / 243 executed
- DeepSeek：169 / 243 executed

## 4.3 Runtime实现关系

V25 durable static evidence显示：

Q30：

- BF16 cuBLAS `internal::gemvx`
- template/shape specialization包含 `...,false,true,true,false,7,...`

DeepSeek：

- BF16 cuBLAS `internal::gemvx`
- specialization包含 `...,false,true,true,false,6,...`

因此：

**Accepted interpretation**：

> 两个不同MoE模型的expert `down_proj`出现类似对象构成，但它们仍属于同一广义cuBLAS GEMV实现家族。

**Claim boundary**：

当时只能称为 **two-lineage MoE-family pattern**。

V25明确授权的下一步是：

> 保留当前两条anchor，等待第三条独立MoE lineage，而不是继续扩同模型采集。

---

# 5. 第三条lineage：OLMoE

OLMoE这条线的价值，是提供第三个独立模型家族；同时也暴露了“模型独立 ≠ kernel实现独立”的方法论问题。

## 5.1 Target冻结

模型：

`allenai/OLMoE-1B-7B-0125-Instruct`

revision：

`b89a7c4bc24fb9e55ce2543c9458ce0ca5c4650e`

V34冻结：

- S2_TEXT B1/T2048/D32
- Layer1 decode32
- natural top-8：`[58,59,47,51,25,15,12,48]`
- rank-0 Expert58
- `experts[58].down_proj`
- input `[1,1024]` BF16
- weight `[2048,1024]` BF16
- output `[1,2048]` BF16
- same-module replay bitwise equal

## 5.2 Runtime variant问题

V36发现同一语义目标可能出现不同实际cuBLAS JIT实现：

- variant A：BF16 `internal::gemvx`，1096 static instructions
- historical variant B：不同template/implementation context

V37在固定formal protocol下16个fresh processes：

- A = 16/16
- B = 0
- unknown = 0

因此OLMoE formal anchor明确限定为：

> **actual-JIT variant A conditioned**

不能声称variant B不存在，也不能声称OLMoE implementation invariant。

## 5.3 Complete static scope

V38/V39系列工作关闭了actual-A完整static scope：

- all static instructions：1096
- selected address-bearing GLOBAL / GLOBAL_TO_SHARED / LDGSTS set：243
- historical all-static SHA：
  `089d264460999f54f9279ccced4b4bab72483d0572e1d08d6797338ef76a9aa3`

历史V38 normalized selector checksum：

`9d2d414999e417200167664dc0b4c716f1dcfb72aaf505d89736e14dbedbcb33`

后续发现其精确serialization producer未被durably retained，因此V40做了provenance repair：

- raw TSV SHA：
  `d70035debd62f0821f7b4b0c802ecdd3ca101b7213eafb591b3cc56438a271eb`
- `C16_SELECTOR_CANONICAL_V1`：
  `cb20c01619acf563de69776a7a098b21c31c6ce6d836ea0bc0beab9fe42c979b`

历史`9d2d...`保留为opaque historical checksum，不伪称重新复现。

## 5.4 Final formal authority

174-new authority：

`hrl/c16-olmoe-v40-formal-admission-174new-v1@85563ec6f55a0ad743d21483aa49c24fdb5cf3bf`

Accepted RUN_ID：

`C16R_olmoe-1b-7b-0125-instruct_s2-t2048-d32_decode32_nvbit1771-c16warp1_expert58-down-proj-actual-a_20260922T100810Z_fc0f3cf67edf`

node164 raw：

`/root/share/mnt164/huangrulin/c16_ai_workload/raw/C16R_olmoe-1b-7b-0125-instruct_s2-t2048-d32_decode32_nvbit1771-c16warp1_expert58-down-proj-actual-a_20260922T100810Z_fc0f3cf67edf`

positive ACK SHA：

`9c4d08a960f53acece00dbb3143cba460c22bc638ff4a879833c0e4460b98e39`

174独立重算闭合：

- selected：243
- executed：129
- proven-zero：114
- failed：0
- dynamic warp records：132,096
- active-lane events：4,196,352
- executed fraction：0.530864

对象事件：

- WEIGHT：2,097,152
- INPUT：2,097,152
- OUTPUT：2,048
- OTHER：0

对象比例：

- WEIGHT：0.4997559785261103
- INPUT：0.4997559785261103
- OUTPUT：0.0004880429477794046
- OTHER：0

role-conditioned：

- WEIGHT shards：64
- INPUT shards：64
- OUTPUT shards：1

WEIGHT shard：

- median active-lane events：32,768
- median unique 128B lines：2,048
- median unique 4K pages：1,024

INPUT shard：

- median active-lane events：32,768
- median unique 128B lines：1
- median unique 4K pages：1

---

# 6. 三-lineage consumer：Q30 + DeepSeek + OLMoE

## 6.1 Accepted consumer

`hrl/c16-three-lineage-moe-consumer-174new-v1@08536be9940590be101c7f5bac2117ba82056db5`

三份node164 accepted raw均重新读取并用统一定义重算。

Historical reproduction check全部PASS：

| lineage | selected | executed | zero | warp records | active-lane events |
|---|---:|---:|---:|---:|---:|
| Q30 | 243 | 41 | 202 | 100,352 | 3,147,776 |
| DeepSeek | 243 | 169 | 74 | 362,496 | 11,538,432 |
| OLMoE | 243 | 129 | 114 | 132,096 | 4,196,352 |

## 6.2 T3：三个模型lineage共同观察

### T3-1：weight / input事件严格平衡

| lineage | WEIGHT fraction | INPUT fraction | delta |
|---|---:|---:|---:|
| Q30 | 0.49967469 | 0.49967469 | 0 |
| DeepSeek | 0.49982251 | 0.49982251 | 0 |
| OLMoE | 0.49975598 | 0.49975598 | 0 |

### T3-2：output事件占比极小

- Q30：0.00065062
- DeepSeek：0.00035499
- OLMoE：0.00048804

三者均 < 0.001。

### T3-3：OTHER = 0

三个accepted object map中，当前formal evidence均能完整落入WEIGHT / INPUT / OUTPUT。

### T3-4：selected scope都是243

三个anchor的accepted static selected path count均为243。

**重要限制**：

这不代表三者的243条static path是同一组机器指令，也不能跨模型按static index对齐。

---

# 7. 三-lineage后，原先解释发生了什么变化？

这是目前最重要的方法论结论。

## 7.1 原先可能的解释

在Q30、DeepSeek两个模型阶段，看到：

- weight≈50%
- input≈50%
- output极小

一种自然猜测是：

> 这可能是MoE expert计算的共同访存特征。

## 7.2 第三lineage加入后，现象被确认，但解释需要降级

OLMoE确实再次出现几乎同样的对象构成。

然而进一步的role-conditioned结果揭示了更直接的结构：

| lineage | WEIGHT paths | INPUT paths | OUTPUT paths |
|---|---:|---:|---:|
| Q30 | 20 | 20 | 1 |
| DeepSeek | 84 | 84 | 1 |
| OLMoE | 64 | 64 | 1 |

并且三者都是BF16 expert `down_proj`，都落在cuBLAS `internal::gemvx`广义实现家族。

因此当前更合理的解释是：

> **weight/input约各一半、output极小，首先像是GEMV / down_proj计算结构与实现映射的共同结果，而不是已经证明的MoE稀疏路由特性。**

### 结论状态

- “三模型都观察到weight/input平衡”仍然是 **Accepted fact / T3**。
- “这是MoE特有行为”被 **降级为不成立/未证明**。
- 当前不能据此直接设计MoE专用Cache/TLB机制。

---

# 8. 真正有信息量的差异

## 8.1 Executed static coverage差异很大

- Q30：41 / 243 = 16.87%
- OLMoE：129 / 243 = 53.09%
- DeepSeek：169 / 243 = 69.55%

Q30是明显的lineage-specific低coverage行为。

三-lineage consumer将其标为：

`L1: executed_fraction`

这说明：

> 相同“expert down_proj”语义下，底层实际执行路径组织可以显著不同。

## 8.2 空间footprint差异也明显

WEIGHT shard median unique 128B lines：

- Q30：24,576
- DeepSeek：2,048
- OLMoE：2,048

WEIGHT shard median 4K pages：

- Q30：768
- DeepSeek：1,408
- OLMoE：1,024

INPUT shard median unique 128B lines：

- Q30：12
- DeepSeek：1
- OLMoE：1

这再次说明：

> “同一神经网络语义算子”并不等于“相同底层访存实现”。

因此后续研究必须显式区分：

1. model-lineage effect
2. operator semantics
3. runtime/kernel implementation effect

---

# 9. Implementation coupling：三模型独立，但底层实现并不完全独立

Accepted durable evidence：

Q30：

- cuBLAS BF16 `internal::gemvx`
- template tuple含 `...,false,true,true,false,7,...`

DeepSeek：

- cuBLAS BF16 `internal::gemvx`
- tuple含 `...,false,true,true,false,6,...`

OLMoE：

- accepted upstream identity表明actual-JIT variant A属于BF16 `internal::gemvx`
- 早期V38 upstream evidence记录过family `false,true,true,false,6`
- 但当前V40 accepted raw selector本身没有完整template文本，因此三-lineage raw-only consumer严格将DeepSeek–OLMoE exact/near-exact specialization relation标为：
  `U / NOT_RECOMPUTABLE_FROM_CURRENT_RAW_SELECTOR`

### 当前最严谨的表述

> 三者是独立model lineages，但runtime implementation-family coupling存在或可能存在。

因此，三模型共同现象不能被写成“三个独立GPU实现共同证明”。

---

# 10. 当前阶段科学结论

## 10.1 已经可以说

> Across the three accepted independent model lineages, the natural-routed expert `down_proj` anchors show a shared descriptive weight/input-balanced, output-small, OTHER-zero event composition under the observed cuBLAS gemvx deployments.

中文可概括为：

> **三个独立MoE模型lineage中，自然路由expert `down_proj`都观察到weight/input事件近似对半、output极小的共同描述性结构。**

但必须紧接限定：

> **这一共同结构目前更像是GEMV/down_proj算子与cuBLAS实现家族的结构性特征，而不是已经证明的MoE稀疏路由特性。**

## 10.2 当前不能说

- 所有MoE模型都这样
- 这是MoE的普遍规律
- MoE天然造成某种cache/TLB瓶颈
- routing导致了当前50/50对象构成
- Q30/DeepSeek/OLMoE之间是严格matched-input因果比较
- DeepSeek和OLMoE已经被当前raw证明为完全相同的kernel specialization

---

# 11. 为什么当前不应该直接进入MoE专用Cache/TLB机制设计

现在最稳定的三-lineage T3：

- weight / input平衡
- output极小
- OTHER=0

都可以由“GEMV读权重 + 读输入 + 少量写输出”自然解释。

也就是说：

> 如果现在直接根据这些现象做MoE专用Cache/TLB机制，很容易优化的是GEMV/down_proj本身，而不是MoE真正独特的稀疏路由行为。

因此，当前正确动作不是继续增加更多expert样本，也不是立即设计机制，而是换一个更MoE-specific的问题。

---

# 12. 下一科学问题：routing-driven active-expert working set

## 12.1 Hypothesis

MoE真正区别于Dense FFN的核心，不是“单个expert内部怎么做GEMV”，而是：

> **routing决定哪些expert被激活，以及连续调用中active expert集合如何重复和切换。**

因此下一问题应为：

> **在模型、层、tensor shape、E、top-k和底层runtime不变时，仅改变routing pattern，MoE区域的weight working set、page footprint和跨expert调用局部性是否发生系统性变化？**

这才是可能产生MoE-specific Cache/TLB机会的问题。

---

# 13. Planned E3：受控routing实验

> **状态：Planned experiment，尚未执行。**

沿用此前E3框架，但根据三-lineage结果收紧科学问题。

## 13.1 固定变量

主实验固定：

- 同一个模型
- 同一个MoE layer / region
- M = 2048
- expert count E
- top-k
- dtype
- kernel/runtime
- tensor shape
- execution region
- warmup / measurement protocol

只改变routing pattern。

## 13.2 Routing conditions

沿用已规划四类：

- N
- U
- H
- P

具体生成方法必须在E3正式执行合同中再次明确，避免名称先于定义。

## 13.3 分析区域

不再只看一个孤立`down_proj`。

应覆盖完整MoE区域：

`router -> dispatch -> expert execution -> combine`

但router / dispatch / expert / combine成本分别报告。

## 13.4 第一层要回答的指标

### Active expert set

- 每个窗口激活expert数量
- expert ID分布
- 热点expert占比
- expert切换次数
- 相邻调用重复expert概率

### Weight working set

- unique 128B lines
- unique 4K / 64K / 2M pages
- active expert数变化时working set如何变化
- 同一expert再次出现时，其weight working set与之前的重合程度

### 合法连续调用局部性

E3必须保留同一执行上下文内真实的连续关系，例如：

`expert A -> expert B -> expert A`

重点观察第二次A是否重新访问大量相同weight lines/pages。

这是当前single-shard formal证据无法回答、但与Cache/TLB潜在机会直接相关的问题。

### Cost breakdown

分别记录：

- router
- dispatch
- expert compute
- combine

避免“expert局部优化明显，但整个MoE region收益很小”的误判。

---

# 14. E3继续/停止判据

## 14.1 值得继续进入Cache/TLB研究

如果观察到：

- routing pattern显著改变active-expert working set；
- 热点/重复expert带来稳定跨调用weight line/page重合；
- 集中routing相比均匀routing明显缩小page working set或提高重复访问；
- 该趋势在独立模型family验证中仍出现；

则可以进一步问：

> 现有Cache/TLB为什么没有充分利用expert-level temporal locality？

之后才值得进入机制研究。

## 14.2 不值得继续MoE专用机制

如果结果主要表现为：

`total working set ≈ active expert count × per-expert weight size`

并且：

- 几乎没有可利用跨调用复用；
- routing pattern只改变“扫多少权重”；
- 行为基本可由GEMV shape解释；
- 独立family也不支持额外MoE-specific locality；

则应收住MoE专用Cache/TLB方向。

这同样是有价值的负结果。

---

# 15. 当前状态

截至三-lineage consumer：

- Q30 formal anchor：**closed**
- DeepSeek formal anchor：**closed**
- OLMoE formal anchor：**closed**
- 三-lineage raw-only consumer：**closed**
- “单expert内部50/50结构是MoE特性”：**未证明，解释已降级**
- “routing可能形成active-expert working-set局部性”：**待验证hypothesis**
- E3：**尚未执行**
- 新TLB/cache机制：**尚未授权**

当前主线应从：

> 单expert内部访存特征

转向：

> **routing-driven active-expert working-set behavior**

---

# 16. Evidence index

## Q30

- producer：
  `hrl/c16-qwen3-30b-s2-formal-capture-109-v3@28620a89d55fd9230103a31d31d14757b57e1e0f`
- review pack：
  `docs/vm_tlb/review_packs/C16_QWEN3_30B_S2_FORMAL_CAPTURE_109_V3/`

## DeepSeek

- producer：
  `hrl/c16-deepseek-v2-lite-s2-producer-109-v23r1@baf892ced6d66cbacabb995caf095e5280995097`
- review pack：
  `docs/vm_tlb/review_packs/C16_DEEPSEEK_V2_LITE_S2_PRODUCER_109_V23R1/`

## Q30 + DeepSeek two-lineage consumer

- `hrl/c16-cross-model-moe-q30-deepseek-174new-v25@2538feb8862cd9b1828e9c805cb88ee46a4741ce`
- review pack：
  `docs/vm_tlb/review_packs/C16_Q30_DEEPSEEK_TWO_LINEAGE_MOE_174NEW_V25/`

## OLMoE final authority

- `hrl/c16-olmoe-v40-formal-admission-174new-v1@85563ec6f55a0ad743d21483aa49c24fdb5cf3bf`
- review pack：
  `docs/vm_tlb/review_packs/C16_OLMOE_V40_FORMAL_ADMISSION_174NEW_V1/corrected_fc0f3cf67edf/`

## Three-lineage consumer

- `hrl/c16-three-lineage-moe-consumer-174new-v1@08536be9940590be101c7f5bac2117ba82056db5`
- review pack：
  `docs/vm_tlb/review_packs/C16_THREE_LINEAGE_MOE_CONSUMER_174NEW_V1/`

---

# 17. 后续维护约定

每个新的MoE科学阶段结束后，更新本文件时至少增加：

1. **Question**：这轮具体想回答什么；
2. **Evidence**：用了哪些accepted authority / 新实验；
3. **Result**：关键定量数据；
4. **Interpretation**：当前最合理解释；
5. **Superseded**：哪些旧解释被削弱或否定；
6. **Next question**：下一步为什么值得做；
7. **Stop condition**：什么结果意味着不值得继续。

这样本文件始终保留“科学推理链”，review pack继续保留“证据审计链”。
