# Decoupled-L2 历史实验归档

> 归档日期：2026-08-28<br>
> 用途：保留 Decoupled-L2 迄今所有可追溯的实验输入、版本、原始结果和
> 解释边界。后续重构 baseline、拆分 TagRAM/DataRAM/lower-port 资源模型或修改
> workload 时，应把本文作为索引，而不是把旧周期数直接当作新模型的对照结论。

## 1. 阅读规则：结果的适用等级

| 等级 | 含义 | 本归档中的例子 | 后续是否可直接横比 |
|---|---|---|---|
| A：可复现实验事实 | trace、二进制、配置和 provenance 已门禁；原始日志仍在 | 17 项 closeout、5 项 b07 bank diagnosis | 可复跑；只有同一模型/配置才可直接横比 |
| B：部分完成事实 | 已完成的 arm 有完整日志，但整个计划未完成 | 8-bank 三臂候选的 atax/bicg/mvt | 仅可引用对应 arm；不可形成总体结论 |
| C：机制探索 | 验证一个局部参数/实现能否工作 | lower-read=64/128、WBQ=16 | 可保留方向和计数；不可推广为通用收益 |
| D：已知抽象限制下的推断 | 计数反映旧模型的共享资源排队，不等价于物理硬件因果 | 旧 `tag_requeue` / `lower_read_requeue` 分析 | **资源模型拆分后必须重做** |

本文件中的 `baseline` 一律指未改变的 GPGPU-Sim sector L2；`decoupled`
指 token/AAD/OTF/dirty-WBQ 的实验 L2。速度比统一为：

```text
speedup = baseline simulated cycles / experiment simulated cycles
```

因此大于 1 表示模拟周期减少。宿主 wall time、峰值 RSS 只用于排程估算，
不是体系结构性能指标。

## 2. 代码、配置和运行环境

### 2.1 两个仓库及版本

| 角色 | 路径 | 归档时分支/提交 | 说明 |
|---|---|---|---|
| Accel-Sim 前端、runner、实验资料 | `/workspace/worktrees/accel-sim-decoupled-l2` | `hrl/decoupled-l2-exp-v0`, `13d2a13` | 本文所在工作树；已有用户的未跟踪文档不属于本归档提交 |
| GPGPU-Sim 后端实现 | `/workspace/worktrees/gpgpu-sim-decoupled-l2` | `hrl/decoupled-l2-v0`, `971edd97` | 当前实现：`Account for Decoupled-L2 WBQ drain stalls` |
| 历史 5-workload bank diagnosis 后端 | 同上 | `b07c0ad6` | `Add Decoupled-L2 bank observability`；与当前实现不同，已明确标注 |
| 原生基线钉住版本 | 见 `docs/decoupled_l2_runs.md` | Accel-Sim `3016c658`，GPGPU-Sim `73774727` | 2026-08-10 native smoke 的上游参照 |

当前版本的关键实现演进（从早到晚）为：

1. `d4dbda26`：可选择的 Decoupled-L2 backend。
2. `56ee11e7`：bank/owner 唯一性与不变量。
3. `17e62004`：dirty WBQ。
4. `559be677`、`7e4bceff`、`9d971cba`：lower-read credit 与断言/统计。
5. `f8a024a6`、`eba378a0`：WBQ handoff 与 stalled-tag 下 lower traffic 优先。
6. `b07c0ad6`：bank 可观测性。
7. `971edd97`：WBQ drain stall 统计（归档时当前后端）。

### 2.2 归档时的 Decoupled-L2 默认结构

默认参数来自 `src/gpgpu-sim/gpu-sim.cc`：

| 项目 | 默认值 |
|---|---:|
| tag / hit / fill latency | 1 / 1 / 1 cycle |
| request token | 512 per slice |
| AAD entry | 256 per slice |
| in-flight lower-read credit | 32 per slice |
| WBQ entry | 4 per slice |
| 旧抽象 bank 数 | 4 per slice |
| bank hash | modulo |
| V100 QV100 L2 slice | 32 memory channels × 2 subpartitions = 64 |
| L2 容量 | `S:32:128:24` = 96 KiB/slice，6 MiB total |
| `gpgpu_l2_rop_latency` | 160 cycles |

这里的 **旧抽象 bank** 是最重要的限制：当前旧模型的 `m_bank_ready[bank]`
被 `TAG`、`LOWER_READ`、`FILL` 和 `WBQ` 四类动作共同占用。它不是独立的
物理 TagRAM bank，也不是独立的 DataRAM bank/port。

因此：

- `tag_requeue` 的准确含义是“tag queue 请求在竞争这个统一抽象资源时失败并回队”；
  它**不能**证明物理 TagRAM 已成为瓶颈。
- `lower_read_requeue` 是 lower-read 发射在竞争同一个统一资源时回队；真实硬件中，
  已经命中/未命中的 lower-read 发射通常只需地址和 lower port，不应因为 TagRAM 或
  DataRAM 端口而被同样阻塞。
- `FILL`、以及 payload 未随 WBQ 保存时的 `WBQ`，才自然需要 DataRAM 类资源；
  fill 的 tag 安装还需要 TagRAM 写端口。

故旧 bank 计数是有价值的**旧模型排队证据**，但在下一轮把资源拆为
`TagRAM`、`DataRAM`、`lower port/credit` 后，所有“瓶颈在何处”的因果判断都应重跑。

### 2.3 provenance 与完成门禁

runner 对每个可报告 arm 检查：正常退出、trace hash、二进制 hash、后端/源码身份、
非后端配置及要求的统计活动。具体格式、命令和目录约定见
[`decoupled_l2_runs.md`](decoupled_l2_runs.md)。

原生 smoke 结果（2026-08-10）：Rodinia `lud` 在钉住的原生基线上完成，
`gpu_tot_sim_cycle = 136216`，`gpu_tot_sim_insn = 420900`。这是环境连通性证据，
不是与 Decoupled-L2 的性能比较。

## 3. 已完成的完整双臂 closeout（17 项）

原始根目录：
`hw_run/decoupled-l2-closeout-20260822/`

完整报告：
[`PERFORMANCE_ALL.md`](../hw_run/decoupled-l2-closeout-20260822/PERFORMANCE_ALL.md)。
每一行均通过双臂 normal-exit、Decoupled 活动、双 provenance 和
simulator/source/trace identity 门禁。

| Workload | Baseline cycles | Decoupled cycles | Speedup |
|---|---:|---:|---:|
| cudasdk/BlackScholes | 9,032 | 8,986 | 1.0051x |
| cudasdk/convolutionSeparable | 305,818 | 272,891 | 1.1207x |
| cudasdk/fastWalshTransform_11_19 | 172,297 | 171,161 | 1.0066x |
| cudasdk/fastWalshTransform_7_21 | 668,522 | 516,074 | 1.2954x |
| cudasdk/scalarProd_13920 | 330,852 | 326,268 | 1.0140x |
| cudasdk/scalarProd_8192 | 200,294 | 197,522 | 1.0140x |
| cudasdk/scan | 2,250,657 | 1,541,304 | 1.4602x |
| cudasdk/sortingNetworks | 76,397 | 76,461 | 0.9992x |
| cudasdk/transpose | 201,054 | 200,971 | 1.0004x |
| cudasdk/vectorAdd_4000000 | 77,887 | 48,251 | 1.6142x |
| cudasdk/vectorAdd_6000000 | 115,708 | 69,318 | 1.6692x |
| ubench/atomic_add_bw | 1,167,104 | 1,153,925 | 1.0114x |
| ubench/atomic_add_bw_conflict | 5,250,571 | 5,250,512 | 1.0000x |
| ubench/l2_bw_32f | 1,153,606 | 1,154,893 | 0.9989x |
| ubench/l2_bw_64f | 2,331,492 | 2,330,289 | 1.0005x |
| ubench/mem_bw | 405,584 | 203,580 | 1.9923x |
| ubench/mem_lat | 2,053,499 | 1,703,026 | 1.2058x |

聚合（仅这 17 项）：baseline 16,770,374 cycles，Decoupled 15,225,432 cycles；
cycle-weighted speedup **1.1015x**（周期减少 9.212%），unweighted mean
1.2005x，median 1.0140x。

### 3.1 如何使用这批结果

这批数据是“旧 Decoupled-L2 相对旧 baseline 的端到端效果”最完整的一组事实，
应长期保留；但它不是下一版物理资源拆分模型的性能基线。后续结构改变后必须：

1. 同一 trace/config 重新跑新 baseline；
2. 重新跑新 Decoupled；
3. 把本表作为历史对照，不与新表混合计算几何平均。

当时 direct manifest 规划 24 项：17 项 pretrace 加 Parboil `mri-gridding` 和 6 项
PolyBench；closeout 中实际完成并通过门禁的是这 17 项。其它 archive/exploration
目录不自动具有同等证据等级。

## 4. 五 workload 的旧共享-bank 因果诊断

原始根目录：
`hw_run/decoupled-l2-bank-diagnosis/20260825-b07c0ad-full/`

总表：
[`bank_observability.md`](../hw_run/decoupled-l2-bank-diagnosis/20260825-b07c0ad-full/bank_observability.md)，
每个物理 slice、每个旧抽象 bank 的 attempts/grants/requeues：
[`bank_observability_by_bank.csv`](../hw_run/decoupled-l2-bank-diagnosis/20260825-b07c0ad-full/bank_observability_by_bank.csv)。

该轮后端为 `b07c0ad6`，不是当前 `971edd97`。所有五个 baseline/decoupled pair
通过 provenance 门禁。

| Case | B / D IPC | B / D cycles | B/D | req avg/peak | AAD avg/peak | fill avg/peak | WBQ avg/peak | credit stall | tag/lower requeue |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| bicg | 57.9392 / 58.1198 | 2,514,120 / 2,506,305 | 1.0031x | 2.30/51 | 0.91/51 | 0.91/32 | 0.00/1 | 19,216 | 1,602,659 / 16,312 |
| atax | 57.8169 / 57.2423 | 2,519,437 / 2,544,727 | 0.9901x | 2.27/62 | 0.90/56 | 0.90/32 | 0.00/1 | 26,154 | 1,599,531 / 28,194 |
| gesummv | 78.4446 / 79.9669 | 2,433,801 / 2,387,470 | 1.0194x | 1.37/63 | 1.09/58 | 1.08/32 | 0.00/0 | 98,665 | 107,186 / 73,713 |
| mvt | 57.1848 / 57.4012 | 2,547,288 / 2,537,684 | 1.0038x | 2.28/64 | 0.91/58 | 0.90/32 | 0.00/1 | 25,791 | 1,597,429 / 27,555 |
| syrk | 380.3102 / 373.4134 | 14,794,918 / 15,068,175 | 0.9819x | 0.91/117 | 0.01/37 | 0.01/32 | 0.00/1 | 1,459 | 83,415 / 275 |

旧资源模型下的直接观察（不是物理端口结论）：

- 4 个 bank 的最大 share 为 25.01%–26.44%，没有单 bank hash hotspot。
- `bicg`、`atax`、`mvt` 有大量统一资源 requeue；`syrk` 少得多，且负载几乎全为写。
- 所有五项的 WBQ 平均占用几乎为零，不能将这些退化解释为 WBQ 容量不够。
- fill peak 频繁到 32，是旧 fill queue/流水活动的观察；它本身不证明 DataRAM bank
  不足或 lower credit 是主因。

### 4.1 旧 owner 计数的正确语义

`requeue` 的体系结构含义是：一个已进入内部队列的请求在本周期无法获得所需的
抽象服务资源，因而保留语义、回到队尾（或指定位置）等待以后重试。它不是 cache
miss、不是被丢弃的 NACK，也不是唯一请求数量；同一请求可多次 requeue。

在 `bicg/atax/mvt` 中，tag 请求重试约占总 requeue 的 97%–99%。这只说明重试者
大部分来自 tag queue；在旧统一资源模型中，它们的 blocker 还可由 `TAG`、
`LOWER_READ`、`FILL`、`WBQ` owner 分类。以 bicg 为例，tag requeue 的 owner 分布为
TAG 1,065,991 / LOWER 522,301 / FILL 14,362 / WBQ 5。故不能把“tag 请求回队”简化为
“TagRAM 读端口不够”。

### 4.2 当时的 8-bank 候选选择与失效边界

当时选择将旧 abstract bank 从 4 调到 8，是因为 requeue 大、bank 分布均衡、并且
AAD/WBQ 容量没有饱和。这个选择对**旧统一-bank 模型**是合理的敏感性候选。

资源拆分后，`LOWER_READ` 不应与 tag/data bank 竞争，FILL/WBQ 也应按真实数据路径
重新建模；因此“bank=8”不能被继承为新的推荐结构，需要在新模型重做 4/8/... 扫描。

## 5. 容量与 WBQ 探索

### 5.1 lower-read credit：`l2_bw_32f`

原始目录：`hw_run/decoupled-l2-capacity/20260825-l2-bw32-lower_capacity.md`

| Decoupled lower credit | Cycles | 相对 default=32 |
|---|---:|---:|
| 32（默认） | 1,154,893 | 1.0000x |
| 64 | 1,156,214 | 0.9989x |
| 128 | 1,156,214 | 0.9989x |

默认的 lower-credit stall 为 360；64/128 时归零，fill peak 从 32 升到 37，
但没有端到端收益。这是该 microbenchmark/旧模型下“单纯扩大 credit 不足以改善”的
事实，不代表其它应用、其它 latency 或拆分资源模型没有收益。

### 5.2 dirty WBQ：压力 microbenchmark

原始目录：
`hw_run/decoupled-l2-wbq-capacity/20260825-wbq16-bank-safe/`

该试验将默认 WBQ 与候选 WBQ=16 作三臂对比，使用 dirty-WBQ 压力版
`vectorAdd_4000000`。结果：

| Case | Default speedup | WBQ=16 speedup | WBQ=16/default | WBQ peak：default → 16 | alloc stall：default → 16 |
|---|---:|---:|---:|---:|---:|
| vectorAdd_4000000 pressure | 9.0299x | 9.0027x | 0.9970x | 4 → 6 | 59 → 0 |

候选消除了已观测到的 allocation stall，却没有得到性能增益，故当时未采纳。注意：
该压力 config 与普通 closeout 的 vectorAdd 不同，不能把 9x 数值和第 3 节混合。

## 6. 被用户停止的 8-bank 三臂候选

根目录：
`hw_run/decoupled-l2-bank-candidate/20260826-8bank-current-model/`

2026-08-28，用户要求停止测试，进程组在 `syrk/decoupled` 期间终止。
`STOPPED.md`、`partial_three_arm_results.md` 和各 arm 的 `runtime_metrics.txt` 共同
定义它的证据范围。

已正常结束的 preflight 为 6 个 arm（`l2_bw_32f` 与 atomic 的三臂）；已正常结束的
primary 为 atax/bicg/mvt 的各三臂。未完成：`syrk/decoupled`、`syrk/optimized` 和
gesummv 全部三臂。因此没有 admission verdict，也不能形成五 workload 聚合。

| 已完成 case | Default speedup | 8-bank optimized speedup | optimized/default | B / D / O wall time | B / D / O peak RSS |
|---|---:|---:|---:|---:|---:|
| atax | 0.9901x | 1.0022x | 1.0123x | 769 / 885 / 870 s | 1.51 / 1.48 / 1.49 GiB |
| bicg | 1.0031x | 1.0027x | 0.9996x | 758 / 838 / 854 s | 1.53 / 1.50 / 1.50 GiB |
| mvt | 1.0043x | 1.0005x | 0.9963x | 750 / 868 / 877 s | 1.51 / 1.48 / 1.49 GiB |
| 仅以上三项的几何平均 | 0.9991x | 1.0018x | 1.0027x | — | — |

其 preflight 中 `l2_bw_32f` default/8-bank cycles 为 1,154,893 / 1,154,547
（1.0003x），说明旧统一资源机制被触发，但**不构成**物理 DataRAM/TagRAM bank 数的
设计证据。候选在旧模型中也未完成，资源拆分后不应继续补跑这个原计划。

`syrk` 的同周期数但不同宿主耗时是一个重要排程注记：旧 b07 run 的 elapsed 为
16:24:33（user 58,775 s），当前候选 baseline 为 25:35:38（user 91,530 s），二者的
模拟 cycles 都是 14,794,918。后一次处于高宿主负载，involuntary context switches
约 35.6M（旧 run 约 22.6M）。这不是模型性能回归，只能用于保守的资源排程。

## 7. 独立的 FRC Stage-3 探索结果

FRC 不是上述 Decoupled-L2 backend。它在独立工作树
`/workspace/worktrees/accel-sim-frc-v1/results/core_sweep_convolution_v2/`
完成了 `convolutionSeparable` 的容量 sweep；摘要保存在
[`PERFORMANCE.md`](../hw_run/decoupled-l2-closeout-20260822/PERFORMANCE.md)。
每个点使用相同 trace checksum
`ab2290810368438cabf35a3c0fcb9686473aaa2235607a6e2bc0347f651ff484`，
FRC simulator image 为 `13ec02…`，但它与第 3 节的源码 revision、容量配置不同。

| FRC sweep variant | Cycles | 相对结果 | 归档解释 |
|---|---:|---:|---|
| Baseline24 | 418,556 | reference | resident capacity 基准 |
| FRC4 | 426,441 | 0.9815x vs Baseline24 | 慢 1.88% |
| FRC8 | 427,066 | 0.9801x vs Baseline24 | 慢 2.03% |
| FRC16 | 406,197 | 1.0304x vs Baseline24 | 少 2.95% cycles；含额外 FRC payload |
| FRC32 | 390,216 | 1.0726x vs Baseline24 | 此 sweep 的最佳探索点；含额外 payload |
| FRC64 | 410,158 | 1.0205x vs Baseline24 | 少 2.01% cycles；含额外 payload |
| FRC128 | 423,482 | 0.9884x vs Baseline24 | 慢 1.18%；含额外 payload |
| Baseline25 | 414,644 | FRC128 的 capacity-matched ref | 多一 way 的参照 |
| FRC128 | 423,482 | 0.9791x vs Baseline25 | 严格 payload-matched 比较中慢 2.13% |
| Baseline26 | 389,237 | larger-baseline ref | 原始 capacity-sweep 点 |
| FRC256 | 420,691 | raw point | 未完成 matching-capacity audit |

这组探索同时保留正、负结果，但**不是** Decoupled-vs-FRC 的胜负表。要得到可发表的
三臂结论，必须使用同一个 workload、相同 trace checksum、源码 revision、容量核算和
配置重新运行 Baseline/FRC/Decoupled。此前的 `FRC复现.md`、`L2-S3.md` 和 `L2-S4.md`
仍是机制设计/实施资料，不能取代同轮三臂原始结果。

## 8. workload、trace 与运行资源记录

### 8.1 已验证 workload 覆盖

- 已完整双臂验证：第 3 节 17 项（CUDA SDK 11 + ubench 6）。
- 已完成旧 bank 诊断：bicg、atax、mvt、syrk、gesummv。
- 已 archive/探索但未在 closeout 中全部门禁：Parboil、PolyBench、CUTLASS 等；其
  下载/压缩包存在不等价于 workload 已正常跑完。
- FRC 有第 7 节的独立 `convolutionSeparable` capacity sweep；它保留为探索证据，
  但没有与第 3 节 Decoupled closeout 同版本、同容量的三臂配对。LateBind 目前仍是
  机制设计材料，不能把设计文档当作实验结果。

### 8.2 Workload catalogue：语义、历史耗时与证据等级

下表的 `B/D` 是一次 baseline / Decoupled 单 arm 的历史宿主耗时；来源为
`RESOURCE_PLANNING.md` 中 simulator log 的 `gpgpu_simulation_time`，而不是 simulated
cycles。它受机器负载和 binary 影响，只用于估算后续排程。`A` 表示第 3 节同轮已通过
性能/provenance 门禁，`B` 表示有正常历史运行但未形成当前 closeout 的可比结论。

#### A. 已验证性能对照：CUDA SDK

| Workload | 程序语义/典型访存 | B / D 历史耗时 | 旧结果 | 对后续 L2 研究的价值 |
|---|---|---:|---:|---|
| BlackScholes | 批量期权定价；独立数据并行、少量迭代 | 9 / 10 s | 1.0051x | 极短 smoke，非主要性能点 |
| convolutionSeparable | 二维图像可分离卷积；行/列邻域读取 | 20m15 / 24m58 | 1.1207x | 有空间局部性；也有独立 FRC sweep |
| fastWalshTransform_11_19 | Walsh-Hadamard 变换；分阶段蝶形重排 | 3m48 / 3m30 | 1.0066x | 小规模 transform 对照 |
| fastWalshTransform_7_21 | 同上、较大规模 | 29m27 / 59m16 | 1.2954x | 有效吞吐型应用；D 的宿主开销明显 |
| scalarProd_13920 | 向量点积/归约 | 10m49 / 17m14 | 1.0140x | streaming + reduction |
| scalarProd_8192 | 同上、较小规模 | 5m02 / 6m21 | 1.0140x | 快速归约回归 |
| scan | 前缀和；多级 block scan 与全局中间数组 | 1h46m47 / 3h59m45 | 1.4602x | 强代表性；周期改善大但非常耗时 |
| sortingNetworks | 固定比较-交换网络排序 | 6 / 7 s | 0.9992x | 极快功能/负例检查 |
| transpose | 矩阵转置；规则 strided/coalesced 访问 | 3m27 / 3m20 | 1.0004x | 访问映射/局部性对照 |
| vectorAdd_4000000 | 两输入向量流式读、单输出写 | 3m14 / 5m26 | 1.6142x | 简单高收益微应用；不应单独代表真实程序 |
| vectorAdd_6000000 | 同上、更大工作集 | 4m25 / 7m29 | 1.6692x | 同上，用于尺寸敏感性 |

#### B. 已验证性能对照：Accel-Sim ubench trace

| Workload | 程序语义/典型访存 | B / D 历史耗时 | 旧结果 | 对后续 L2 研究的价值 |
|---|---|---:|---:|---|
| atomic_add_bw | 分散地址 atomic add 吞吐 | 33m10 / 34m36 | 1.0114x | 检验简化 atomic 与原子吞吐 |
| atomic_add_bw_conflict | 高冲突 atomic add，热点地址 | 1h32m13 / 1h26m03 | 1.0000x | 原子序列化/热点压力；旧 hash 分布很偏斜 |
| l2_bw_32f | L2 读带宽微基准（32f trace 版本） | 1h11m02 / 1h21m13 | 0.9989x | lower credit、bank 模型的首选敏感性 test |
| l2_bw_64f | L2 读带宽微基准（64f trace 版本） | 2h25m01 / 2h27m52 | 1.0005x | 更长带宽压力；完整回归较慢 |
| mem_bw | 内存带宽压力 | 25m17 / 43m15 | 1.9923x | 外存吞吐与 MSHR/lower path 代表项 |
| mem_lat | 依赖链式内存延迟压力 | 3m01 / 2m36 | 1.2058x | 低成本 latency 回归 |

#### C. 旧共享-bank 诊断的 PolyBench 子集

这些 case 有第 4 节的五项 B/D 周期与 occupancy/requeue 数据；下列是 archive
阶段的历史耗时范围，因运行轮次不同不用于速度比。

| Workload | 程序语义/典型访存 | 历史单 arm 范围 | 诊断状态 |
|---|---|---:|---|
| atax | `A^T(Ax)`；稠密矩阵-向量与两次 streaming pass | 13m14–28m46 | 完整旧 bank diagnosis；1.0% 退化 |
| bicg | `q=Ap`、`s=A^Tr`；双向稠密矩阵-向量 | 13m13–16m17 | 完整旧 bank diagnosis；近中性 |
| mvt | 两次矩阵-向量更新 | 12m48–16m57 | 完整旧 bank diagnosis；近中性 |
| gesummv | 广义矩阵-向量：`y=αAx+βBx` | 16m19–20m18 | 完整旧 bank diagnosis；1.94% 改善 |
| syrk | 对称 rank-k 更新，重矩阵写回 | 17h22m42–18h51m53 | 完整旧 bank diagnosis；1.81% 退化；最慢项 |

#### D. Archive 中正常结束、但不具当前 closeout 资格的应用

下列是有正常历史运行日志的工作项；它们或使用了不同轮次的源码/配置，或没有完整的
当前 provenance 门禁，故是 B 级排程与 workload 覆盖资料，**不是**可和第 3 节合并的
性能结果。

| 测试集 | Workload | 程序语义 | 历史单 arm 范围 |
|---|---|---|---:|
| Parboil | bfs | 图上的广度优先搜索；不规则 frontier/邻接表访问 | 8m36–13m33 |
| Parboil | cutcp | 分子 Coulombic potential；规则格点对粒子累加 | 1h37m18–2h09m04 |
| Parboil | histo | 图像直方图；原子更新、热点竞争 | 45m14–2h11m54 |
| Parboil | mri-q | MRI 重建中的 Q 计算；复数数组/规则 streaming | 9m26–15m53 |
| Parboil | sad | Sum of Absolute Differences，视频块匹配 | 2m12–4m56 |
| Parboil | sgemm | 稠密单精度矩阵乘 | 12m29–26m06 |
| Parboil | spmv | 稀疏矩阵-向量乘；不规则索引 | 1m00–2m28 |
| Parboil | stencil | 三维 stencil；邻域读/规则写 | 43m27–1h06m12 |
| PolyBench | 2DConvolution | 二维卷积 stencil | 24m00–27m48 |
| PolyBench | 3DConvolution | 三维卷积 stencil | 25m38–40m18 |
| PolyBench | 3mm | 三次稠密矩阵乘链 | 1h43m46–2h23m53 |
| PolyBench | gemm | 稠密矩阵乘 | 27m06–31m11 |

原始 archive 时间、启动目录与已记录的 RSS 信息见
[`RESOURCE_PLANNING_ARCHIVE.md`](../hw_run/decoupled-l2-closeout-20260822/RESOURCE_PLANNING_ARCHIVE.md)。
该历史表记录 33 个 baseline 和 33 个 Decoupled 正常结束 run；中位单 arm 约 24 分钟，
最长为 `syrk` 的约 18–19 小时。多数旧 archive run 未记录可信 peak RSS；不能从一个
临时 `ps` 值倒推长期内存预算。

### 8.3 长期排程经验

17 个 closeout arm 汇总的宿主运行资源记录：baseline 总 wall time 约 9 h 17 min，
Decoupled 总 wall time 约 12 h 43 min；中位数约为 10 min 49 s / 17 min 14 s；最长
单 arm 约为 2 h 25 min / 3 h 59 min。并行时必须按实际可用 RAM、trace 解压占用和
I/O 控制并发，不可仅按 CPU 核数启动。

大 trace archive 的实用策略已经验证为：不整体展开 archive，而是先盘点 tar member
大小、按单 workload 临时展开、受控并行运行、完成后清理临时目录并保留 trace hash、
配置、日志摘要和 provenance。这可在有限磁盘空间下重复实验；下一轮应将它固化为
runner 的缓存/清理策略。

## 9. 后续重做时可复用与必须重做的项目

| 项目 | 可直接复用 | 必须重做/原因 |
|---|---|---|
| trace 定位、archive member 清单、hash/provenance runner | 是 | 新 trace 或 binary 时只需重新生成 identity |
| baseline 原始周期表 | 作为历史资料 | baseline 一旦重构或配置改变，必须同轮重跑 |
| 17 项双臂 workload 集合 | 是，优先回归集合 | 新结构需重新测周期/IPC |
| token/AAD/credit/WBQ 不变量与统计框架 | 大部分可复用 | 新资源路径需对应更新断言和统计定义 |
| 旧 bank per-bank CSV | 是，保留旧模型行为 | 不可用于物理 TagRAM/DataRAM 均衡性判断 |
| `tag_requeue` / `lower_read_requeue` 结论 | 仅保留为旧模型排队现象 | 拆分后改为 tagram/dataram/lower-port/credit 的独立计数 |
| bank=8 候选 | 仅保留为部分结果 | 旧候选不补跑；在新模型重新定义 bank sweep |
| lower=64/128、WBQ=16 参数探索 | 可作为敏感性起点 | 改变数据路径后需重新 sweep |
| FRC sweep 与 LateBind 文档 | FRC 的旧探索点、机制需求和设计约束 | 需按同版本/同容量三臂重新验证；LateBind 还需实现、功能验证与对照实验 |

## 10. 下一轮实验的最低记录要求

为避免再出现“数值有了但无法解释/横比”的问题，baseline 到新结构的每一轮至少应保存：

1. 源码 commit、binary hash、完整配置、trace hash、backend mode 与 overlay 指纹；
2. 正常退出、功能/不变量断言、每 arm 的 simulated cycles/IPC；
3. request token、AAD、fill、WBQ 的平均和峰值占用；
4. 独立的 `tagram_requeue`、`dataram_requeue`、`lower_port_stall`、
   `lower_read_credit_stall`、`fill_data_bank_stall`、`wbq_data_bank_stall`；
5. 每种资源按 bank/port 的 attempts、grants、requeues，及按 requester/owner 分类；
6. 可选但应保留的宿主 wall time、peak RSS、trace 展开空间和执行时 host load；
7. 完整/部分/中止状态。部分结果必须明确未完成 arm，不得自动进入 aggregate。

未来正确的数据路径应至少区分：

```text
request -> TagRAM lookup/hit-miss/AAD
miss    -> lower port + in-flight credit
fill    -> DataRAM write + TagRAM install/update
WBQ     -> (若未持有 payload) DataRAM read -> lower write
```

这套拆分完成前，旧 unified-bank 的性能、回队和参数敏感性结论均保留为历史，
但不用于提出“物理 bank 不够”或“hash 不好”的设计结论。

## 11. 原始资料索引

| 内容 | 路径 |
|---|---|
| 运行方式、provenance、backend 定义 | `docs/decoupled_l2_runs.md` |
| 17 项 closeout 结果 | `hw_run/decoupled-l2-closeout-20260822/PERFORMANCE_ALL.md` |
| closeout scope/resource audit | `hw_run/decoupled-l2-closeout-20260822/` |
| 五 workload 总表 | `hw_run/decoupled-l2-bank-diagnosis/20260825-b07c0ad-full/bank_observability.md` |
| 五 workload per-bank CSV | `hw_run/decoupled-l2-bank-diagnosis/20260825-b07c0ad-full/bank_observability_by_bank.csv` |
| lower credit sweep | `hw_run/decoupled-l2-capacity/20260825-l2-bw32-lower_capacity.md` |
| WBQ=16 压力结果 | `hw_run/decoupled-l2-wbq-capacity/20260825-wbq16-bank-safe/three_arm_results.md` |
| 已停止 8-bank 候选状态 | `hw_run/decoupled-l2-bank-candidate/20260826-8bank-current-model/STOPPED.md` |
| 已停止候选的部分结果 | `hw_run/decoupled-l2-bank-candidate/20260826-8bank-current-model/partial_three_arm_results.md` |
| FRC 独立容量 sweep 摘要 | `hw_run/decoupled-l2-closeout-20260822/PERFORMANCE.md`，原始根：`/workspace/worktrees/accel-sim-frc-v1/results/core_sweep_convolution_v2/` |
| FRC 复现计划 | `docs/FRC复现.md` |
| LateBind 第四阶段设计 | `docs/L2-S4.md` |
