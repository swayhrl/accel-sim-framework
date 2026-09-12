# C14 Path P — Segment-positive continuation

状态：`AUTHORIZED_EXPLORATORY_PATH`

## P0. Scientific question

若 corrected C13 证明 exact-mode 下 Segment 仍有稳定收益，则下一步不能只继续扫 Lseg，而应回答：

> Segment 命中时，conventional exact translation path 还做了多少已经不需要的工作？能否通过 path gating / cancellation / scheduling，在不牺牲 correctness 的前提下，把 Segment 的收益从“必须极低 lookup latency”变成更稳定的收益？

该 Path 的目标是定位并原型化**低风险、可解释、与当前 C12 机制兼容**的交互优化，而不是立即设计大而全的新 TLB。

## P1. Source-level race audit

基于 C12 Core `57bb71...`逐调用链确认：

1. L1 miss后 Segment lookup何时创建；
2. L2 exact probe何时创建；
3. Segment/L2是否真正并发；
4. Segment hit前是否已经：
   - 消耗 L2 port；
   - 查 tag / 更新replacement；
   - allocate translation MSHR；
   - enqueue PTW；
   - 产生 PTE traffic；
5. Segment hit后，哪些已发工作能取消、哪些只能 late-discard；
6. fallback request是否必需从头重走 exact path；
7. repeated/merged requester在race中的处理。

必须画出至少四条 timeline：

- Segment hit fast case；
- Segment hit但exact path已部分启动；
- Segment miss/fallback；
- merged translation request。

输出到 C14 review pack：

- `PATH_P_RACE_AUDIT.md`
- `PATH_P_EVENT_ACCOUNTING.tsv`

## P2. Instrumentation-only patch

在 Core branch：

`hrl/vm-m4b-c14-segment-positive-v0`

增加 default-off / telemetry-only instrumentation。不得先改变timing。

建议至少记录：

- Weight requests entering Segment race；
- Segment winner / exact winner；
- Segment hit时 exact L2 probe：
  - not issued
  - issued-not-completed
  - already completed
- Segment hit前发生的 L2 port consumes；
- Segment hit前 translation MSHR allocations；
- Segment hit前 PTW starts / PTE requests；
- canceled / late-discarded exact outcomes；
- fallback重新进入exact path的额外周期；
- requester exposed latency按winner/path分类。

如现有实现天然无法观察某项，明确`NOT_OBSERVABLE_WITHOUT_SEMANTIC_CHANGE`，不要伪造。

instrumentation必须：

- default off；
- 开启后不改变调度/timing；
- 有unit test或deterministic micro test证明counter conservation。

## P3. Prototype candidates

在source audit后，只允许实现**最多两个**候选，且均 config-gated/default-off：

### P-CAND-1 — Segment-before-L2 gated issue

若一个请求已被immutable Segment registration明确覆盖，则：

- 先进行Segment lookup；
- Segment hit：不发 conventional L2 exact probe；
- Segment miss/fallback：再发 exact L2 path。

只有在 source audit 证明 correctness 可保持时才实现。

关键问题：

- Segment latency增加是否被推迟L2 probe抵消/放大；
- fallback penalty；
- merged requester；
- descriptor lifecycle / revoke；
- exact path作为correctness fallback是否仍完整。

### P-CAND-2 — Opportunistic cancel-before-admission

保留当前并发启动思想，但若Segment在L2真正消费port/MSHR/PTW之前返回hit，则取消尚未admit的exact work；已经admit的work不回滚，只做late-discard。

如果当前架构没有清晰可取消边界，记录`NO_GO`，不要强行实现。

不得同时再引入新的replacement/prefetch/object policy，避免混杂。

## P4. Microdiagnostics

使用`C14_MICRODIAGNOSTIC_MATRIX.tsv`中的P类点。

目标不是看最终speedup，而是验证：

- race accounting是否闭合；
- exact冗余工作是否真实存在；
- P-CAND-1/2是否减少这些工作；
- fallback penalty是否明显；
- 不同operator类型是否行为一致。

重点样本：

- direct FFN：layer 0 / 7 / 15代表kernel；
- Attention Projection：layer 0 / 7 / 15；
- final Embedding/Output kernel 691附近；
- 至少一个 Other Compute control。

若无法稳定构造独立单kernel replay，可使用小kernel window；必须保留window list SHA并标注cold/warm-state局限。

## P5. Go/No-Go

### GO 强信号

至少满足两项：

- Segment hit请求存在显著的冗余L2/MSHR/PTW工作；
- gated/cancel prototype在microdiagnostic中稳定减少冗余工作；
- fallback penalty较小；
- 多类operator方向一致；
- corrected C13最终仍证明Segment有full-ROI正收益。

### NO-GO

任一：

- 当前实现已经在Segment hit前有效避免绝大多数exact工作；
- 冗余工作极少，不足以解释fragility；
- gating造成明显fallback penalty，抵消收益；
- corrected C13最终显示Segment在正确geometry下没有稳定价值。

## P6. Deliverables

- source patch / tests in positive Core branch
- `PATH_P_REPORT.md`
- `PATH_P_PROTOTYPE_AUDIT.md`
- `PATH_P_MICRO_RESULTS.tsv`
- `PATH_P_GO_NO_GO.md`

所有性能数字必须保留`EXPLORATORY_MICRODIAGNOSTIC`标签。