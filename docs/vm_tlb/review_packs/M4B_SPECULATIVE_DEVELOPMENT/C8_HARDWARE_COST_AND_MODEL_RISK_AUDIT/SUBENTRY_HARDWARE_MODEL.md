# Sub-entry L2 TLB：硬件模型审计

标签：`REFERENCE_APPROX_SUBENTRY_16`、`SPECULATIVE_CANDIDATE`。这是 C1 冻结的
64KiB-only 近似，不声称恢复 target/reference 的 exact implementation。

## 结论

base-tag + 16 leaf 的结构在概念上可实现，但当前 comparison 不是同存储预算：配置中的
`-gpgpu_vm_l2_tlb_entries 768` 在 standard mode 是 768 个 exact-page translation，而在
sub-entry mode 是 768 个 group、最多 12,288 个 valid leaf PPN。C7 所见的 geometry
compression 是机会证据，不会消除此不对称。必须在 C5 前选择 equal-bit budget 或明确的
leaf-capacity matched baseline；并把 lookup/fill/invalidate 的 critical path 建模为硬件而
非固定 80-cycle 黑盒。

## 1. exact-page 与 group 的真实 storage accounting（S1）

C4 有 `V=49-16=33` VPN bits（49-bit VA、64KiB page），group 的 base VPN tag 因 16
leaf 而少 4 bits，即 `B=29`。令 `A` 为 context/ASID bits、`P` 为 PPN/PA bits、`Z` 为
page-size class bits、`Q` 为每页权限/attribute bits、`R_exact`/`R_group` 为 replacement
state。硬件位宽不由 C++ 的 `uint64_t` 推导，故保留为符号量。

| 结构 | 每个有效 translation/组的最低逻辑 state | 当前可容纳的最大 translation | 关键注记 |
| --- | --- | ---: | --- |
| exact-page L2 | `valid + A + V + Z + P + Q`，外加 set replacement | 768 | 若 index 是 hash，tag 仍必须区分完整 `(ASID,VPN,page-size)` identity。 |
| 16-leaf group | `group_valid + A + B + Z` 加 `16*(leaf_valid + P + Q)`，外加 group replacement | 768 groups / 12,288 leaves | 省的是每 leaf 重复的 base tag，不是 PPN；所有 16 个 leaf slot 的 PPN/valid/属性仍需存储。 |

群组仅在 leaf occupancy 大于 1 时摊薄 group tag。单叶群组会支付额外 group valid/tag
层级，且 leaf PPN 没有消失。C4 bounded replay 的实际 L2 resident state 始终只有一个
valid leaf、没有 existing-group fill；它没有展示 storage compression 的动态使用。C7
的 25-file geometry `62 pages / 10 groups` 则只说明地址几何存在 sibling reuse 的可能，
不是 bit-budget 证明。

当前源码的 group 为 `{valid, asid, base_vpn, page_size, last_touch, object, leaves[16]}`；
leaf 为 `{valid, ppn, object}`。`object` 是 telemetry attribution，不是必须的 hardware
translation tag；`last_touch` 是 software 64-bit timestamp，也不是硬件 LRU 位数。本文不
将这两种 C++ representation 当成硬件成本。16-way exact/group replacement 至少各需要
某种 `R_16` state；若宣称 exact true-LRU，其编码最低信息量是 `ceil(log2(16!))=45` bits
per set，实际实现可能选择 PLRU/NRU。没有指定前用 `R_exact,R_group`。

## 2. base-tag、leaf lookup、fill/replacement 的关键路径（S2）

冻结 candidate 对 `(ASID, VPN>>4, page_size)` 做 set/hash 与 16-way group compare；命中
group 后选择 leaf `VPN[3:0]`。`768/16=48` sets，源码的 hash 以 modulo 48 选择 set，
而不是简单 power-of-two set index。软件把整个 L2 lookup 固定为 80 cycles，未分解如下
硬件动作：

```
request -> set/hash -> 16-way base-tag(+ASID,+size) compare -> way select
        -> 16:1 leaf valid/PPN/attribute select -> permission check -> response
```

这比 exact-page “tag compare + data select”多一层 leaf mux/valid test。base-tag hit 且
selected leaf invalid 是 leaf miss；它不能与 normal hit 混淆。fill 路径也不同：先命中
existing group 并只写一个 leaf，或替换一个完整 group（清除最多 16 leaf）；并需仲裁同一
group 的并发 fills。当前 1 L2 port config 限制 lookup ingress，却没有给 group fill port、
read/modify/write、bank conflict 或 eviction writeback/invalidation 定义。80-cycle 也没有
证明该复合操作可在与 exact L2 相同的周期内完成。

这不意味着结构不可实现；意味着应选择并记录一种 SRAM/CAM banking、leaf data layout、
replacement 编码和 fill arbitration，然后才可以给每种 path 不同或经验证相同的 latency。
在选择前，该 80-cycle 等时假设为 `MODEL_ASSUMPTION_NEEDS_VALIDATION`。

## 3. ASID、invalidation、superpage 与语义边界（S2）

candidate 的 key 有 ASID 与 page size，且 C1 明确冻结为 64KiB。真实 group invalidation
必须至少支持：

- ASID/PASID scoped flush；按 group base 或单 leaf 的 VA invalidation；全局 flush；
- permissions/remap/migration/shootdown 同时清除 group 的每个受影响 leaf，并且不把一个
  leaf 的 stale PPN 通过 sibling group 留存；
- fill 与 invalidate racing 时的 epoch/serialization；context reuse 后不得命中旧 group；
- superpage overlap priority、demotion/promotion 与 coalescing policy。

现有 candidate 对 2MiB 直接拒绝，不是“相同功能但较慢”。standard exact L2 仍可处理
该页型。这可以作为窄 scope 的 C1 approximation，却要求公平实验把“只 64KiB”列为 policy
限制，不能用其结果声称 general page-size superiority。若将来纳入 superpage，group tag
mask、leaf count/offset、overlap priority、invalidate granularity 与 storage accounting
都需要新架构决定；本 C8 不实现或发明这些语义。

## 4. 同预算的公平比较（S3）

令 exact 768-entry 总位预算为：

```
B_exact = 768*(1 + A + V + Z + P + Q) + R_exact_total
```

令 group 数为 `G`：

```
B_group(G) = G*(1 + A + B + Z + 16*(1 + P + Q)) + R_group_total(G)
```

equal-bit group budget 必须满足：

```
G <= floor((B_exact - replacement allowance) /
           (1 + A + B + Z + 16*(1 + P + Q) + group replacement allowance))
```

目前的 `G=768` 不是此方程的解，而是把“entry”从 page 改成 group 后仍复用数字。它在
leaf capacity 上最多为 baseline 的 16 倍，故 C5 若使用 current pair，只能称为“fixed
group-count candidate vs 768 exact entries”，不可称 “same L2 TLB storage”。互补公平基线
至少需要：

1. equal-bit budget 的 `G` group candidate 对 768 exact entries；
2. 或为当前 `G=768` group provision 足以持有最多 12,288 exact leaves 的 exact-page L2
   baseline，并把 tag/replacement bits 一并报告；
3. 在相同总 translation-storage 预算下，扩大 exact L2、把位数投到 PWC、以及一个有
   page-allocation/contiguity/OS成本说明的 2MiB page policy。

PWC 的 128-entry config 不能简单按 entry 数与 TLB 对比：其每 level prefix/tag、PTE/pointer
payload、replacement、port和 hit latency 都不同。因此表中只给 `B_pwc` 符号项。2MiB 页面
也不是零成本 baseline：需要 contiguity、promotion/demotion、fault、migration、fragmentation
和 shootdown policy。它是必须纳入的 architecture comparison，而不是可凭现有 config
免费宣称的结果。

## 审计判定

| 问题 | 判定 |
| --- | --- |
| 16-leaf group 是否是可实现的 TLB organization？ | 是，前提是明确 leaf SRAM/CAM、tag/mux、fill 和 invalidate 微架构。 |
| 当前 `768` group vs `768` exact 是否同存储或同容量？ | 否；最大 leaf capacity 为 12,288 vs 768。 |
| C4 无收益是否反证 sub-entry？ | 否；C4 只形成一个 leaf、无 sibling fill。 |
| `REFERENCE_APPROX_SUBENTRY_16` 是否可当作 reference-exact？ | 否；保持 approximation 标签。 |
| C5 前是否需先批准 budget/page-size/latency policy？ | 是；这是 `ARCHITECTURE_DECISION_REQUIRED` 的一部分。 |
