# C16 Grouped-Baseline Residual Parallelism Screen — Master V1

日期：2026-09-29。

## 0. 已关闭的问题

以下结论已经接受：
- ROW mapping下split8曾在大工作集点占优；
- cross-M weight-side reuse是高L2 read-hit的重要来源；
- GROUP_M16经典软件mapping恢复了split1大部分reuse；
- 相同GROUP_M16能力下，K3072/K4096的split1明显优于split8。

因此当前“cache-aware split8 / 新split机制”故事关闭。

本阶段只回答一个新的残余问题：

> 在已有grouped/swizzled CTA locality scheduling作为默认强基线、且weight-side工作集明显小于L2时，split-K是否仍会因为CTA供给不足而有价值？如果有，边界在哪里？

如果答案只在低CTA供给点成立，则该现象应定位为已有Stream-K/parallel decomposition类问题，而不是新的cache机制。

---

## 1. 冻结shape

固定：
- K = 4096
- N = 12288
- group_size = 128
- W4 synthetic
- mapping = GROUP_FULL_M
- split = {1,8}

只改变M：
- M=1
- M=16
- M=32
- M=64

共 4 M × 2 split = 8 cells。

不运行ROW。

## 2. 为什么选K4096/N12288

精确W4 weight-side footprint：

- qweight = 25,165,824 B
- qzeros = 196,608 B
- scales = 786,432 B
- total = 26,148,864 B = 24.9375 MiB
- /64MiB L2 = 0.38965×

即完整split1 weight-side集合本身明显小于64MiB。

最大M64时：
- input = 524,288 B
- split1 output/scratch = 1,572,864 B
- split8 scratch = 12,582,912 B

因此该screen有意把此前的容量knee降到次要位置。
仍不得声称“所有数据必然常驻L2”；真实set mapping、调度和其他访问仍存在。

## 3. GROUP_FULL_M mapping

Mtile count：
- M1 -> 1
- M16 -> 1
- M32 -> 2
- M64 -> 4

Ntile count固定：
- 12288 / 128 = 96

GROUP_FULL_M：
- linear = blockIdx.x % (m_tiles * 96)
- split_z = blockIdx.x / (m_tiles * 96)
- Mtile = linear % m_tiles
- Ntile = linear / m_tiles

因此同一Ntile对应的所有M tiles在线性block ID上连续。

这是经典grouped/swizzled思想的最强、简单控制，不扫GROUP_M。

## 4. CTA supply

理论grid：

| M | Mtile | split1 GEMM CTA | split8 GEMM CTA |
|---:|---:|---:|---:|
| 1 | 1 | 96 | 768 |
| 16 | 1 | 96 | 768 |
| 32 | 2 | 192 | 1536 |
| 64 | 4 | 384 | 3072 |

RTX4080有76 SM，因此split1 launch-level CTA supply约：
- M1/M16: 1.26 CTA/SM
- M32: 2.53 CTA/SM
- M64: 5.05 CTA/SM

这些只是launch-level供给，不等于同时resident CTA数。

M1 vs M16很重要：
- grid完全相同
- split数相同
- weight footprint相同
- 只改变一个16-row tile中有效M行数
可区分partial-tile利用率与单纯CTA数量。

## 5. 科学问题

### Q1：M1 vs M16
如果split8在M1明显更有利，而M16弱化：
说明partial-M tile利用率/有效工作量也参与选择，不只是CTA数量。

如果M1/M16表现接近：
说明低CTA供给可能更主导。

### Q2：M16 -> M32 -> M64
随着split1 grid从96→192→384增加：
- split8相对收益是否持续下降？
- 是否出现split1反超？

如果出现：
把剩余split价值定位为低并行度下补CTA供给。

### Q3：cache是否已经退出主导
对每个M检查split1 GROUP_FULL_M：
- L2 read hit是否保持高位
- DRAM是否随M只做合理变化
- 不应重现此前ROW mapping的63% hit knee

如果split1在这些capacity-safe点仍突然掉hit，必须先解释cache，而不能把timing差异直接归因并行度。

---

## 6. 使用同一patched kernel

Lane8应复用/泛化上一轮GROUP_M16 patch思想。

所有8 cells使用同一个compiled target kernel。
mapping固定GROUP_FULL_M，不需要ROW对照。

可保留runtime mapping_mode但所有科学cell必须走同一GROUP path。
如果为支持动态m_tiles需要新增整数算术：
- split1/8/M1/16/32/64全部走同一代码路径；
- 不允许M-dependent branch改变GEMM主体。

AWQ数学、K-loop、dequant、MMA、tile、block、数据布局保持不变。

## 7. synthetic authority

优先复用现有参数化synthetic公式；若既有公式只冻结特定shape，则Lane8可建立新的：
`C16_GROUPED_RESIDUAL_SYNTH_V1`

要求：
- deterministic
- A/B同一input/qweight/qzeros/scales bytes
- 每个M只改变input/output shape，不改变weight-side bytes
- tiny CPU reference和SHA闭合

该screen是人工kernel机制实验，不称GPT-3 public-shape proxy。

## 8. correctness

每M：
- split1 vs split8使用原容差 `rtol=1e-2, atol=5e-2`
- all finite / shape/dtype一致
- 若自然bitwise equal则记录

GROUP_FULL_M必须静态证明output tile覆盖一次，无重复遗漏。

## 9. Timing

每cell：
- 10 global warmups
- 25 complete mirror blocks
- 50 samples/cell
- 2 same-cell warmups/sample
- CUDA event只包module call
- 不使用conditioner

建议每M：
`A8, B1, B1, A8`
并在不同M之间轮转顺序，避免固定M顺序漂移。

## 10. NCU

每cell1份，共8 profiles。

已有必须指标：
- L2 read hit sectors
- L2 read miss sectors
- L1/TEX bytes
- L2 bytes
- DRAM bytes
- duration

Lane7 CPU-only阶段额外查询最小并行度指标，优先语义明确的：
- launch waves / SM
- active warps/SM或SM throughput

不预设具体metric名字。
若找不到语义清楚的指标，不扩大section sweep；核心screen仍可继续，但“并行度”结论必须表述为launch-level supply + timing响应，而不是直接occupancy证明。

split8 reduction必须单列：
- GEMM duration
- reduction duration
- reduction DRAM

## 11. 判读

### A. 只在低CTA供给点split8有利
例如M1/M16 split8更快，但M32/M64 split1逐渐反超，同时split1 L2 hit一直高。

结论：
- residual主要是CTA supply / tile utilization / reduction tradeoff
- 属于已有parallel decomposition/Stream-K问题范围
- 不再追求新的cache机制

### B. GROUP + high split1 CTA supply后split8仍明显有利
例如M64时：
- split1 hit高
- split1 grid=384
- split8仍显著更快

才允许继续诊断低比特特有的dequant/latency-hiding/CTA-resource机制。

### C. split1在所有点都更快
说明grouped mapping已经基本关闭当前split8需求，支线可停止。

### D. cache再次成为主导
若split1 hit随M/shape异常下降：
先做cache解释，不把它叫parallelism residual。

## 12. 不做

禁止：
- GROUP_M sweep
- split=2/4/16
- K/N sweep
- replica experiment
- EVICT
- SASS/NVBit
- Accel-Sim
- full-model extrapolation

## 13. 三Lane流水

Lane8 / 174-new：
- CPU-only source/mapping/shape/footprint/launch audit
- 尽快发布EARLY_GATE

Lane7 / 109：
- 同时CPU-only build/runner/metric-query prep
- gate支持后一次GPU lock完成8 cells

Lane6 / 174-new：
- 同时准备consumer
- producer完成后独立重算

Lane4不动。
