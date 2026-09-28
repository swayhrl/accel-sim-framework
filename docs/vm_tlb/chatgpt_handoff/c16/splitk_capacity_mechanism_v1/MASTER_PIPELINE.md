# C16 Split-K 容量机制确认 — 并行准备V1

日期：2026-09-28。

## 0. 当前状态

已完成：
- Lane8静态地址集合审计：commit `c72d28b17247f25d0c3613604ab6cab1737666e0`
- Lane7 K-threshold native series：commit `b17193ff6b3786fd01d5bfe83b5c1a0a03859729`
- Lane6正式独立消费：尚未完成，使用独立resume handoff。

当前producer/static数据显示：
- K2560 full footprint 62.34MiB，split1 DRAM约180MB，gain约+44%
- K3072 full footprint 74.81MiB，split1 DRAM约729MB，gain约+17%
- K4096 full footprint 99.75MiB，split1 DRAM约972MB，gain约0%
- split8 total DRAM在K2560→3072仅约491→504MB，且其中约243MB是reduction。

这强烈提示capacity knee，但项目结论仍等待Lane6独立consumer。

---

## 1. 下一步采用“轻量硬件确认 + 模拟器准备”并行

### Lane7 / 109
只做**机会性L2 read-hit诊断**，不抓SASS。

目的：
确认K2560→3072附近，split1 GEMM的L2 read hit行为是否同步恶化，而split8 GEMM相对稳定。

先CPU-only查询/选择当前ncu 2025.1.1.0在Ada支持的最小L2 read sector hit/miss/hit-rate指标。
只有指标语义明确，才获取GPU lock。

### Lane8 / 174-new
CPU-only准备**K4096 paired capacity-counterfactual**，但不执行模拟。

绑定：
- K4096, M256, N49152
- split1 vs split8
- 只关注GEMM weight-locality机制
- accepted RTX4080 simulator baseline：
  `hrl/awma-174-rtx4080-v1-baseline-promotion-v1@8d1f14a32f5538660d74da86ccb03a2c504c5735`
- baseline config blob：
  `configs/rtx4080_ada/SM89_RTX4080_AWMA_V1/gpgpusim.config`
  Git blob `3306caa589baa07c046e16fddd3066351ba10d2c`
- baseline L2：
  `S:2048:128:16` × 16 subpartitions = 64MiB

设计候选capacity：
- 64MiB baseline
- 128MiB
- 256MiB
必要时32MiB只作下界，不默认加入长跑。

只允许改变dl2 sets（associativity=16、line=128B、subpartition数量不变），并明确“容量变化同时改变set-index范围，不能称纯物理L2容量隔离”。

### Lane6 / 174-new
先完成threshold independent consumer。
Lane6最终中文判断决定是否允许后续trace/sim gate。

---

## 2. 为什么先做L2 hit诊断而不是直接抓SASS

K-threshold实验已经固定M/N/grid/scratch，只改变K/footprint；native DRAM knee很强。
再抓完整SASS的成本远高于补一轮4–8个NCU profile。

若L2 read hit行为也在K2560→3072明显改变，机制链加强：
`静态可复用集合 -> footprint跨容量 -> L2 read hit恶化 -> DRAM增加 -> timing恶化`

若hit行为不支持：
先重新解释，不抓trace。

---

## 3. Simulator后续候选为何选K4096

K4096：
- split1 full W4 = 99.75MiB
- split8 local = 13.875MiB
- native split1/split8 timing近crossover
- native B/A DRAM≈1.83
- 动态规模仅K12288的1/3

因此非常适合问：

> 若模拟器L2从64MiB提高到128/256MiB，split1的L2/DRAM行为是否显著恢复，而split8相对不敏感？

如果出现这种容量响应，才值得称为更强的counterfactual支持。

---

## 4. 当前不授权

本coordination本身不授权：
- 新SASS capture
- Accel-Sim长跑
- 新split值
- 新M/N/K
- 修改Lane4

Lane7仅可做bounded NCU cache-read诊断；
Lane8仅做CPU设计/资格审查。

后续GPU trace/simulator由新gate单独授权。
