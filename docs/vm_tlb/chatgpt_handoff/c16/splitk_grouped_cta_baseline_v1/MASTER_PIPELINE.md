# C16 Split-K Grouped/Swizzled CTA Strong Baseline — Master V1

日期：2026-09-29。

## 0. 当前接受结论

已由独立consumer确认：
- cross-M combined weight-side物理地址复用是当前高L2 read-hit的重要来源；
- split-K缩小per-split local working set，有助于这类复用存活；
- 继续replica-count或split-count扫描价值低。

本阶段回答LR09提出的更强问题：

> 不增加split、不增加partial-output/reduction，仅通过经典grouped/block-swizzled CTA映射，把共享同一weight-side地址的M tiles在逻辑顺序上排得更近，能恢复多少L2复用与性能？

如果可以，说明当前split收益有相当部分是在补偿原始CTA映射的局部性不足；如果不能，剩余“并行度—局部工作集—归约成本”冲突才更值得机制化。

---

## 1. Related-work约束

文献入口：
`hrl/c16-chatgpt-literature-notes-v1@38d4df40b615625c15d1843a69a23eb954ac0bef`

重点：
- Triton官方GEMM教程采用GROUP_M grouped ordering促进L2复用；
- CUTLASS/Stream-K相关工作已经讨论CTA次序、并行分解与cache复用；
- 因此“调整CTA顺序提高L2 reuse”本身不是新机制。

本实验只把它作为**必须通过的强软件基线**。

---

## 2. 原始与强基线映射

当前AutoAWQ：
- M=256 → Mtile count=16
- N=49152 → Ntile count=384
- within split，原线性映射：
  - ROW: Mtile = linear / 384
  - ROW: Ntile = linear % 384
- 同一Ntile跨相邻Mtile在线性block ID上距离384。

强基线只用一个映射：
`GROUP_M16_FULL_M`

因为Mtile总数正好16，它等价于：
- GROUPED: Mtile = linear % 16
- GROUPED: Ntile = linear / 16

因此同一Ntile对应的16个M tiles在线性ID中连续。

不扫GROUP_M=2/4/8；避免把强基线变成调参。

---

## 3. 同一patched binary，branch-free mapping选择

主比较不能直接拿accepted原binary对另一个patched binary。

新独立extension中，所有cell使用同一个compiled target kernel。

runtime `mapping_mode`：
- 0 = ROW
- 1 = GROUP_M16_FULL_M

kernel内无状态branch，建议：
- 先计算ROW的(M,N)
- 再计算GROUPED的(M,N)
- 用整数branch-free select组合
- 最终重构logical `blockIdx_y = Mtile*j_factors1 + Ntile`
- split_z公式保持原样

两种mapping必须执行同一套新增整数地址映射指令。
之后A/input、B/qweight/qzeros/scales、C/output、K-loop/dequant/MMA等全部沿原公式。

---

## 4. 实验矩阵

固定：
- M=256
- N=49152
- K={3072,4096}
- split={1,8}
- mapping={ROW,GROUP_M16}

共8 cells。

为什么只选这两个K：
- K3072：刚进入capacity-knee之后，split1仍有约17%优势，但L2 hit已降至约63%；
- K4096：native split1/split8接近crossover，最适合判断mapping能否替代split带来的locality收益。

不加入K2560、K12288。

---

## 5. 必要校准

同一patched ROW路径必须先证明没有把旧问题改坏。

对K3072/K4096 × split1/8：
- output对accepted authority闭合；
- launch/grid/scratch/reduction闭合；
- ROW timing与accepted历史median方向一致；
- 不要求bitwise相同性能，但若median偏差>5%且大于两边CV，则STOP review，不进入强基线解释。

这个校准不需要额外GPU矩阵；ROW cells本身就是8-cell中的4个。

---

## 6. correctness

同一split：
- ROW vs GROUP_M16应bitwise equal。

split1 vs split8：
- 继续原 `rtol=1e-2, atol=5e-2`；
- 若自然bitwise equal则记录。

必须验证所有output tile覆盖一次且无重叠/遗漏。

---

## 7. Timing / NCU

每cell：
- 10 global warmups
- 25 complete mirror blocks
- 50 CUDA-event samples
- 2 same-cell warmups/sample

建议mirror：
`A_ROW, B_ROW, A_GROUP, B_GROUP, B_GROUP, A_GROUP, B_ROW, A_ROW`
A=split8，B=split1。

NCU：8 profiles。
冻结：
- L2 read hit sectors
- L2 read miss sectors
- L1/TEX bytes
- L2 bytes
- DRAM bytes
- duration

A reduction单列。
主locality解释用GEMM rows。

---

## 8. 主要科学问题

### Q1 split1能否靠mapping恢复reuse？
比较：
- K3072 B_ROW vs B_GROUP
- K4096 B_ROW vs B_GROUP

看：
- L2 hit提升
- miss/DRAM下降
- timing改善

### Q2 给双方同样的mapping后，split8还剩多少价值？
比较GROUP_M16下：
- A_GROUP vs B_GROUP

如果split1_GROUP恢复到高hit、并重新显著优于split8_GROUP：
当前split8优势主要来自补偿原ROW mapping的locality问题。

如果两者都改善，但split8_GROUP仍明显优于split1_GROUP：
说明在强mapping之后仍存在split缩小工作集/增加并行度等独立价值。

### Q3 split8本身是否也从grouped mapping获益？
A_ROW vs A_GROUP。
若split8已接近饱和hit，改善应有限；若仍明显改善，说明原mapping对两种split都有未利用locality。

---

## 9. 结论边界

这只是同一AutoAWQ kernel family上的软件调度强基线。

不得声称：
- grouped mapping是新贡献；
- 逻辑block-ID顺序等于GPU真实发射顺序；
- 所有W4 kernel都应采用GROUP_M16；
- 结果代表完整GPT-3模型。

如果strong baseline基本解决问题，应接受并降级“新split机制”空间。
如果仍有清楚残余，才进入新机制设计。

---

## 10. 三Lane流水

Lane8 / 174-new：
- CPU-only source patch/static bijection/coverage proof
- 内存/launch/runner contract
- 尽快发布EARLY_GATE

Lane7 / 109：
- 同时CPU-only build prep
- EARLY_GATE支持后一次GPU lock跑8 cells

Lane6 / 174-new：
- 同时准备consumer
- producer结束后独立raw重算

Lane4不动。

本阶段不抓SASS、不跑Accel-Sim。
