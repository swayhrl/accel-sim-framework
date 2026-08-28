# TLS-Cache：V4/V5 实验含义、论文结果与当前性能记录

> 记录日期：2026-08-22。本文把论文陈述、本地已完成的结果、以及由两者作出的推断分开记录。它不是论文数值复现成功的声明；当前阶段的目标是机制正确、可观测、可复现，并据此解释已有 workload 的表现。

## 1. V4 和 V5 分别是什么

这里的 V4、V5 是本项目 **P9 实验与证据模式（schema）** 的版本，不是论文提出的两代 TLS-Cache 架构。

| 项目 | V4：已完成的正式结果 | V5：正在补强的观测版本 |
| --- | --- | --- |
| 核心目的 | 完成 TLS 机制、四 workload × 四架构 × 两种 placement 的性能矩阵，并验证 TLS 专有的请求阶段、服务层级、fabric 自然排空和 provenance。 | 使 Baseline、Shared L1、L1.5、TLS 四种模式都输出同一口径的读请求端到端延迟和最终服务位置，用于解释 V4 中的性能正负差异。 |
| 覆盖的性能结果 | 32/32 行已自然结束并通过 schema-v4 门禁；该矩阵是目前可引用的本地性能结果。 | 32 行正式矩阵仍在运行；其性能表在完成、门禁和最终审计前不作为新结论。 |
| TLS 专有细节 | 已有八阶段 `TLS_READ_*` 时间戳、CL1/RL1/内存最终服务统计、fabric 请求/响应守恒。 | 保留全部 V4 TLS 专有统计。 |
| 四模式可比观测 | 不完整：TLS 有详细路径，其他模式没有同口径的“接受 L1 请求 → 请求者写回完成”包络。 | 新增 `P9_READ_*`：本地/远端分类、最终服务层级、log2 延迟直方图、总/最小/最大延迟和未完成记录数。 |
| 是否改变被模拟的机制 | V4 是原始机制实现和完成的性能实验。 | **否。** V5 的统计是 sidecar：仅在一次 L1 读被接受时建记录、在请求者 writeback 时完成记录；统计状态不参与调度、缓存、fabric、路由或仲裁决策。 |

### 1.1 代码与版本证据

V4 的外层 Accel-Sim worktree 为 `hrl/tls-cache-repro-v0`（`ddc0b15b4b79e07cc0e0e6fb6948c5e61cb2f4e7`），核心 GPGPU-Sim worktree 为 `hrl/tls-cache-gpgpusim-v0`（`e50e733edd9d6de75a4ff8afac094b8cf487c468`）。

V5 从 V4 派生：外层为 `hrl/tls-cache-repro-v5-observe`（`5e21a1e81bd6ac9844afde6400bbc629e4a8d53c`），核心为 `hrl/tls-cache-gpgpusim-v5-observe`（`51df923984baa80f1a40677b2f9e97d441958c0f`）。核心提交标题为 `feat(tls): add cross-mode P9 read observability`，改动为 165 行新增、1 行删除，涉及 `gpu-sim.cc/.h`、`shader.cc` 和 `tls-cache.h`。

关键接口是 `record_p9_read_access()`、`set_p9_read_final_service()` 和 `finish_p9_read()`。它们分别在接受的 L1 读、服务类别最终确定、以及 requester writeback 时更新统计；源码注释明确说明这些 sidecar 是 observational，任何调度、缓存或 fabric 决策都不读取它们。因此，V5 不应被理解为“为了让 TLS 更快而优化实现”。V5 的模拟 IPC 若与 V4 有变化，需要作为可复现性/运行配置问题单独核查，而不能归因于这组统计字段本身。

V5 的门禁要求每一行都满足：

`local + remote = completed = Σ(final service) = Σ(latency histogram) = 两个时间戳计数`，且 `P9_READ_live = 0`。

这比 V4 多提供了 Baseline、Shared L1、L1.5 与 TLS 之间可比较的证据；V4 的 `summary.csv` 和配对 IPC 分析仍是性能的唯一来源，直到 V5 正式闭环。

### 1.2 当前执行状态

- P0–P8：已通过。
- V4 P9A（32 行矩阵）与 P9B（论文规模 4 chip × 64 SM 的 TLS dynamic/frozen 控制）：已通过自然排空、服务/延迟/阶段时间戳和 provenance 校验。
- V5：截至本文记录时，SRAD 8 行、CFD 8 行和 GEMM dynamic 4 行已完成；GEMM frozen 的四模式批次正在收敛（各行可先后结束，批次门禁尚未完成）。随后自动继续 FDTD 8 行、论文规模 dynamic/frozen 两行、V5 门禁和 P0–P9 closure audit。运行中的结果不提前汇总。

对应的 V4 完成标记和原始结果目录为：

- `/workspace/worktrees/accel-sim-tls-cache/hw_run/tls-cache-p9/matrix-v4/P9_completion.md`
- `/workspace/worktrees/accel-sim-tls-cache/hw_run/tls-cache-p9/matrix-v4/`
- `/workspace/worktrees/accel-sim-tls-cache/hw_run/tls-cache-p9/paper-v4/`

V5 runner 的说明在 `/workspace/worktrees/accel-sim-tls-cache-v5-observe/experiments/tls_cache/README_p9_v5.md`；运行状态写入 `/workspace/worktrees/accel-sim-tls-cache-v5-observe/hw_run/tls-cache-p9-v5/followup.log`。

## 2. 论文实际报告了什么

以下均为论文 [TLS-Cache a two-level shared L1 cache for multi-chip GPUs.pdf](../papers/TLS-Cache%20a%20two-level%20shared%20L1%20cache%20for%20multi-chip%20GPUs.pdf) 第 4 节的作者报告，不能与本地 MINI 配置的数字直接混合。

### 2.1 论文实验契约

- 基线是 4 chip、每 chip 64 SM（总 256 SM）、每 SM 128 KB L1；每 chip 16 个 LLC slice、8 个内存控制器；跨 chip 为 ring，768 GB/s、每跳 32 cycle；页面为 4 KB first-touch。
- 比较四种架构：Private-L1 Baseline、cluster-shared `Shared L1`、以部分 LLC 容量形成 remote data cache 的 `L1.5`、以及三份 cluster-shared L1 加一份 remote-shared L1 的 TLS-Cache（cluster size = 4）。
- workload 为作者筛选出的高 intra-chip locality 应用：SS、SRAD、FFT、SPMV、SORT、CFD、GEMM、ST2D、REDC。论文因机制目标而选择这组高 locality workload，不是无筛选的总体 GPU workload 平均。
- 指标为 IPC，相对 Baseline 归一化；论文还报告 read-request latency、服务层级分布、placement/SM 数/chip 数/L1 大小/cluster 大小敏感性和硬件开销。

### 2.1.1 高 intra-chip-locality workload 集如何得到

这九项不是“基准套件中任取的九项”，也不是本项目后来为 TLS 指定的列表。论文明确说明：先从多芯片 GPU 研究常用的 benchmark suites 中选取候选项；再在一个每 chip 配备足够大 ideal remote-data cache 的理想多芯片 GPU 中测量 intra-chip locality；最后特意选择具有较高 intra-chip locality 的应用来评价 TLS。论文把最终集合和测得的指标直接列在 Table 2，但没有在论文中公开可逐项复现的 trace、输入规模或 page map。

论文的定义为：`ICL = remote-read frequency × ideal RDC hit rate`。Table 2 给出的完整集合为：

| 论文名称 | 来源 | ideal RDC hit rate | remote memory access frequency | ICL | 本地对应情况 |
| --- | --- | ---: | ---: | ---: | --- |
| SS | Mars | 0.93 | 0.54 | 0.50 | 尚无。 |
| SRAD | Rodinia | 0.86 | 0.60 | 0.52 | 有 Rodinia SRAD，但为 1/40 trimmed trace，输入未与论文对齐。 |
| FFT | SHOC | 0.92 | 0.63 | 0.58 | 尚无正式 P9 行。 |
| SPMV | Parboil | 0.96 | 0.75 | 0.72 | 已有候选 trace 的兼容性配对，不属于正式 P9 性能矩阵。 |
| SORT | SHOC | 0.97 | 0.74 | 0.72 | 已有候选 trace 的兼容性配对，不属于正式 P9 性能矩阵。 |
| CFD | Rodinia | 0.97 | 0.75 | 0.72 | 有 Rodinia CFD 097K 完整五 kernel trace；论文的确切输入仍未知。 |
| GEMM | SHOC | 0.98 | 0.75 | 0.74 | 本地有 **PolyBench** GEMM，算子同名但不是 SHOC GEMM。 |
| ST2D | SHOC | 1.00 | 0.74 | 0.74 | 本地有 PolyBench FDTD2D；不是论文 ST2D。 |
| REDC | SHOC | 1.00 | 0.75 | 0.75 | 尚无正式 P9 行。 |

因此，论文给定了“最终九项名称和其筛选指标”，但筛选过程来自作者的 ideal-RDC 测量；本地目前覆盖 4 个 trace，严格意义上没有一项已经与论文的实现、输入和 trace 完整对齐。SRAD/CFD 是同一 suite、同一应用名的近似对应；GEMM/FDTD2D 只能算算子或邻近模式，不是 paper-equivalent workload。

### 2.2 论文的总体性能结果

| 论文报告项目 | 相对 Baseline 或对照的结果 |
| --- | ---: |
| TLS-Cache 平均 IPC | **+30.2%** |
| TLS-Cache 最大 IPC 提升 | **+77.2%** |
| Shared L1 平均 IPC | +9.3% |
| L1.5 平均 IPC | +19.7% |
| TLS 相对 Shared L1 的额外提升 | +19.6% |
| TLS 相对 L1.5 的提升 | +8.8% |
| CFD | +77.2% |
| GEMM | +49.2% |

作者对平均提升做了 paired-samples t-test，并报告相对 Baseline 在 95% 置信水平显著。该显著性结论只适用于论文自己选定的完整 workload 与实验设置，不能移植到当前四个本地 trace。

### 2.3 论文如何解释收益

- 对高 intra-chip locality 应用，平均 read latency 相对 Baseline：Shared L1 为 76.7%，L1.5 为 49.3%，TLS 为 **36.9%**。
- 示例中，SORT 的 read latency 降到 Baseline 的 22.8%，但 IPC 仅提升 14.2%，说明“低延迟”不必然等比例转成 IPC；CFD 的 latency 为 Baseline 的 30.1%，IPC 提升 77.2%，反映其更 memory-sensitive。
- TLS 相比 L1.5 的解释是更细粒度地在 L1 层捕获 reuse、避免访问更高延迟的 RDC；论文报告其 L1 命中比例从 18.3% 提至 30.0%，并有 42.6% 的请求由 remote-shared L1 服务。
- 作者也明确承认共享路径的传输和竞争开销；其结论是，对所选高 locality 应用，收益超过该开销，而非宣称任何应用都会加速。

### 2.4 论文敏感性和开销结果

- 每 chip 80/96 SM 时，TLS 平均提升为 15.6%/27.6%；均低于 64 SM/chip 的 30.2%，作者归因为资源竞争增强。
- chip 数增至 8 时，论文报告 TLS 相对 Baseline +42.0%。
- cluster size = 2/4 的平均提升为 30.4%/30.2%，size = 8 降至 20.2%；原因是 remote-shared L1 容量比例下降。论文推荐 cluster size 4、每 cluster 三个 CL1 与一个 RL1。
- 综合后的二维 crossbar 与 router 的估计额外成本为每 chip 3.48 mm² 和 2.75 W，即典型 GPU chip 面积/功耗的 0.57%/0.92%。

### 2.5 从论文 Fig. 8 读取的单应用近似 IPC

下表由 Fig. 8 柱状图按纵轴刻度人工读取，保留两位小数只是便于比较；不是作者公开的原始 CSV，建议按约 ±0.03（靠近高柱时约 ±0.05）理解。Baseline 恒为 1。论文正文直接确认 CFD TLS = 1.772、GEMM TLS = 1.492，和图读数一致。

| Paper workload | Shared L1（约） | L1.5（约） | TLS（约） |
| --- | ---: | ---: | ---: |
| SS | 1.10 | 1.04 | 1.08 |
| SRAD | 1.08 | 1.12 | 1.20 |
| FFT | 1.00 | 1.02 | 1.08 |
| SPMV | 1.02 | 1.45 | 1.44 |
| SORT | 1.01 | 1.10 | 1.13 |
| CFD | 1.05 | 1.59 | **1.77** |
| GEMM | 1.30 | 1.12 | **1.49** |
| ST2D | 1.03 | 1.12 | 1.20 |
| REDC | 1.24 | 1.20 | 1.32 |
| 图中 Mean | 1.09 | 1.20 | 1.30 |

这张图也说明论文并非每个对照都严格按 `TLS > L1.5 > Shared` 排序：例如 SPMV 中 L1.5 与 TLS 接近，GEMM 的 Shared L1 高于 L1.5。论文的结论是选定集合上的整体趋势和 TLS 的均值优势，不是所有单项、所有比较器的严格支配关系。

## 3. 当前本地 V4 性能数据

### 3.1 实验口径和边界

这是已通过 V4 P9 gate 的四 workload、四模式、两种 placement 的完整 32 行矩阵。数字来自 `per_app_normalized_ipc.csv`；每个单元为 `mode IPC / 同 workload、同 placement baseline IPC`。

- `dynamic`：first-touch page placement 允许不同模式因请求到达时序不同而得到不同 owner map；它反映“机制 + 该执行时序”下的端到端行为。
- `frozen_hash`：强制四种模式使用相同的 page placement map，用来拆开 placement 时序的影响；它是控制实验，不是论文原始的 first-touch 方法。
- 当前是可用 trace 下的 MINI 实验配置，workload/input、微结构和样本规模都不同于论文。因此它证明机制与方向性，不应被表述为复现了论文的 `+30.2%`。

### 3.2 dynamic placement：当前主要性能对比

| Workload | Baseline IPC | Shared L1 | L1.5 | TLS |
| --- | ---: | ---: | ---: | ---: |
| SRAD | 54.6000 | 1.0269（+2.7%） | 1.0443（+4.4%） | **1.0431（+4.3%）** |
| CFD | 190.7446 | 1.0971（+9.7%） | **1.2314（+23.1%）** | **1.1842（+18.4%）** |
| FDTD2D | 69.2973 | **1.2003（+20.0%）** | 0.9006（−9.9%） | 0.8269（−17.3%） |
| GEMM | 144.9310 | 0.6043（−39.6%） | 0.9448（−5.5%） | 0.8341（−16.6%） |

四个应用的简单 app-ratio 平均为：Shared L1 0.9821、L1.5 1.0303、TLS 0.9721。每组只有 4 个样本，TLS 的 95% CI 为 `[0.6962, 1.2479]`，覆盖 1；因此不能从该均值得出“TLS 总体变慢”或“总体加速”的统计结论。

### 3.3 frozen placement：验证 placement 敏感性

| Workload | Shared L1 | L1.5 | TLS |
| --- | ---: | ---: | ---: |
| SRAD | +3.4% | −0.1% | +0.8% |
| CFD | −3.5% | +11.3% | −0.3% |
| FDTD2D | +2.5% | −4.8% | −6.3% |
| GEMM | +3.1% | +4.0% | −0.8% |

冻结 placement 下的简单平均：Shared L1 +1.38%、L1.5 +2.57%、TLS −1.63%；三个模式的 95% CI 都覆盖 1。尤其是 GEMM，dynamic baseline 的 IPC 为 144.93，而 frozen baseline 为 52.32，说明该 trace 对 first-touch 所形成的页归属和执行时序极敏感。

这不是“TLS 没有触发”的证据，反而说明必须把 page placement、互连流量和路径延迟与 IPC 一起报告。V5 的共同读路径观测正是为这个问题加入的，而不是改变 TLS 来追求更高 IPC。

### 3.4 已确认的 TLS 机制触发证据（dynamic）

| Workload | CL1 hit | RL1 hit | 最终由 memory 服务 | 解释 |
| --- | ---: | ---: | ---: | --- |
| CFD | 229,116 | 29,155 | 1,026,577 | TLS 两级路径实际工作，且获得 +18.4% IPC。 |
| SRAD | 474,930 | 262,548 | 1,010,358 | CL1/RL1 都有实质命中，获得 +4.3% IPC。 |
| FDTD2D | 4,551,518 | 570,502 | 72,599,480 | 命中存在，但很大 memory 流量、共享路径与动态 placement 的代价仍主导，TLS 为 −17.3%。 |
| GEMM | 11,883,849 | 252,916 | 8,867,523 | 有大量 CL1 hit，却仍为 −16.6%；说明“命中数”不能独立预测 IPC，需结合请求者端到端延迟、队列/backpressure 和页归属。 |

已验证的事实是：TLS 的 CL1、RL1、fabric 和完成路径均被实际使用并守恒；尚待 V5 完整矩阵量化的是：各模式到底有多少读请求在何服务级完成、其端到端延迟分布如何、以及这些量怎样和 IPC 关联。对 FDTD2D/GEMM 的“额外互连/共享开销及 placement 敏感性主导”是当前基于 V4 的合理推断，不能在 V5 完成前把它写成唯一根因。

### 3.5 论文规模控制实验的范围

V4 P9B 已在论文目标拓扑（4 chip × 64 SM、32 memory channels、cluster size 4）上完成 CFD 的 TLS dynamic 与 frozen-hash 自然排空和观测守恒校验。它证明当前实现可以在论文规模的配置中运行、无 deadlock，并非一组 Baseline/Shared/L1.5/TLS 配对的论文规模 speedup 实验。因此，P9B 不能产生或支持“论文规模下 TLS IPC 提升为某数值”的说法。

### 3.6 本地已跑的配置数与 workload 覆盖

| 范围 | 每 workload 的架构/placement | 工作量 | 状态 |
| --- | --- | ---: | --- |
| V4 P9A MINI 正式矩阵 | Baseline、Shared L1、L1.5、TLS × dynamic/frozen-hash | 4 × 8 = **32** | 全部自然结束并通过。 |
| V4 P9B paper-scale 控制 | **仅 TLS** × dynamic/frozen-hash，CFD 097K | **2** | 全部自然结束并通过；不是性能对照矩阵。 |
| V5 P9A 观测复核 | 与 V4 P9A 相同的 4 × 8 = 32 | **32** | 已通过 SRAD 8、CFD 8、GEMM dynamic 4；GEMM frozen 批次与后续 FDTD 尚在运行。 |
| V5 P9B paper-scale 控制 | **仅 TLS** × dynamic/frozen-hash，CFD 097K | **2** | 排在 V5 P9A 后自动执行。 |

所以对每个当前正式 workload，V4 已有八个可比配置；其中 dynamic 是主要 first-touch 结果，frozen-hash 是相同 page map 的控制。论文主图则是九个 workload 各跑四种架构、使用作者的 first-touch policy，外加多组敏感性实验。当前本地没有完成 paper 的 9 × 4 性能矩阵。

### 3.6.1 运行盘点与暂停快照（2026-08-22）

用户要求是：已启动的模拟自然结束；尚未启动的暂不启动。下表只把已自然结束且无失败标识的 V5 行计为完成；不把“文件已创建”误记为完成。

| 阶段/配置 | 已完成 | 已启动、等待自然结束 | 尚未启动/已暂停 |
| --- | --- | --- | --- |
| P0–P8 机制门禁 | 对应 directed/smoke/pressure gate 均通过 | 0 | 0 |
| V4 P9A：4 workload × 4 mode × 2 placement | **32/32**：全部通过 | 0 | 0 |
| V4 P9B：4×64 CFD TLS dynamic/frozen 控制 | **2/2**：全部通过 | 0 | 0 |
| V5 P9A：SRAD | **8/8** | 0 | 0 |
| V5 P9A：CFD | **8/8** | 0 | 0 |
| V5 P9A：GEMM dynamic | **4/4** | 0 | 0 |
| V5 P9A：GEMM frozen | **4/4** | 0 | 0 |
| V5 P9A：FDTD2D | 0 | 0 | **8/8**：暂不启动 |
| V5 P9A finalizer / read summary / V5 gate | 0 | 0 | 暂不执行 |
| V5 P9B：4×64 CFD TLS dynamic/frozen | 0 | 0 | **2/2**：暂不启动 |
| P0–P9 closure audit | 0 | 0 | 暂不执行 |

因此，当前 V5 已合格完成 **24/32** 个正式 P9A 行，FDTD 的 8 行尚未启动。自动 follow-up 脚本原本会在当前 batch 完成后继续 FDTD/P9B；为遵守暂停要求，已将仅供后续启动的 V5 runner `experiments/tls_cache/run_p9_matrix_v5.sh` 的执行权限由 `755` 临时改为 `644`。四个已完成的 GEMM frozen 模拟不受影响。控制器随后写出 FDTD dynamic 的 launch 标记，但其 driver 均在 exec 前因 `Permission denied` 退出，未产生 FDTD 模拟器或原始模拟日志；这些失败 driver 不属于实验结果。恢复实验时，先由操作者显式将该文件恢复为 `755`，再根据本表选择要运行的未启动行；不得把失败的启动尝试或不完整日志纳入结果。

## 3.8 4×64、32-cycle/hop 与 ideal-RDC ICL：可行性和资源边界

### 3.8.1 4 chip × 64 SM/chip 能否做到

**可以，且已经证明模型在该拓扑下能自然结束。** V4 P9B 已完成 CFD 的 TLS dynamic/frozen 两条 4×64-SM 控制运行；配置含 256 个 SM、32 个 memory channel、每 chip 16 个 LLC/RL1 slice、cluster size 4。它证明拓扑/资源索引、TLS endpoint 和排空路径能够在论文规模运行。

但它还不是论文主图复现：要比较 IPC，需要在这一拓扑上针对同一 trace/input 跑 Baseline、Shared L1、L1.5、TLS 的完整配对，而不是只跑 TLS 两行；还需要论文对应的九个 workload trace。运行成本随 SM 数、trace 长度和模拟周期显著上升，不能从 MINI 的 wall-clock 直接线性外推。

### 3.8.2 32 cycles/hop 能否做到

**可以，无需先改核心机制。** `-mgpu_interchip_link_latency` 已是配置项，代码将其定义为“以 core cycle 计的 inter-chip ring link latency”，并把值传给 multi-chip fabric；将该项从当前的 `1` 改为 `32` 即可进行论文给出的 hop-latency 敏感性/主配置实验。

不过要形成“论文公开参数重建”而非只改一个数，还必须同时处理以下可审计事项：

1. 论文使用 1 GHz，而当前 QV100 基础配置为 core/interconnect/L2 1132 MHz、DRAM 850 MHz；需决定改到 1 GHz，还是将论文带宽严格换算到当前 core cycle。
2. 论文写 ring 为 768 GB/s；若按 1 GHz 且将其解释为单方向每 link 带宽，对应 768 B/cycle，但论文未说明它是单 link、双向还是整环 aggregate。当前 MINI 值仅为 32 B/cycle。这个口径已在 `assumptions.yml` 列为未公开参数，不能偷偷任选一个而声称数值复现。
3. TLS xbar latency、队列深度、仲裁和 CL1/RL1 精确地址位论文未公开；应保留为明确假设，做 32-cycle/hop 主配置和带宽/仲裁敏感性，而不是把结果说成 cycle-faithful。

暂停期间不会修改正在使用的 V5 配置。恢复后的正确顺序是：先建立独立的 `paper-public-32hop` 配置、做极短 directed/baseline 回归，再跑 4×64 的四模式小 workload 配对；通过后才扩大到完整矩阵。

### 3.8.3 ideal 无限 RDC 的 ICL 筛选能否做到

**已经能做，且现有四条 trace 已产生第一版数值。** P4 的 ideal-RDC observer 是 timing-neutral 的 shadow cache：只记录同一 requester chip 上重复 remote line 的机会，不改变真实 hit/miss、延迟、替换、网络流量或 IPC。P4 已验证 observer 开/关关键时序统计一致；每一条 V4 P9 log 也输出 `TLS_IDEAL_RDC_ICL`。

当前 Baseline observer 结果为：

| 本地 trace | dynamic ICL | frozen-hash ICL | 说明 |
| --- | ---: | ---: | --- |
| SRAD trimmed | 0.818 | 0.786 | 当前 trace 上的高机会样本。 |
| CFD 097K | 0.473 | 0.401 | 与论文 CFD 0.72 不同，首先说明输入/placement/模型并不等价。 |
| PolyBench GEMM | 0.654 | 0.649 | 仅能用于本地筛选，不能同论文 SHOC GEMM 相比。 |
| PolyBench FDTD2D | 0.788 | 0.745 | 非论文 Table 2 workload。 |

对尚缺的 paper-family workload，流程是：先获得/生成可复现 V100 trace → 在 baseline + ideal-RDC observer 下自然 replay → 按同一统计定义记录 remote frequency、ideal RDC hit rate、ICL、trace/input hash → 再决定是否进入正式 TLS 性能矩阵。**ICL 测量本身不需要 GPU**，它在 CPU 上重放已有 trace；GPU 只用于缺失 trace 的生成。

### 3.8.4 是否需要租服务器

分为两类资源，不能混用。

| 目的 | 是否需要 GPU | 建议资源 | 原因 |
| --- | --- | --- | --- |
| Accel-Sim trace replay、4×64 TLS 矩阵、ICL observer | 否 | 起步 32–64 个高频 CPU 核、256–512 GiB RAM、≥1 TB 本地 NVMe；先以 1–2 个重放并发校准，再决定是否增并发。 | 模拟器是 CPU/内存/磁盘 I/O 负载；租 GPU 不会加速 cycle-level replay。当前四条正式 trace 已约 7 GB，完整高保真 trace 集通常应预留远大于此的空间。 |
| 生成缺失的 V100 trace | 是 | 一张 V100 16/32 GB、足够 CPU/RAM/本地 SSD 的短租实例；先做每个应用短 trace smoke 和 hash/provenance，再跑正式输入。 | 为减少目标 ISA/行为差异，优先 V100；GPU 只承担原程序/NVBit tracer 的执行。 |

例如，AWS 的 R7i 内存优化实例最高可提供 64 vCPU/512 GiB（更大规格可到 192 vCPU/1536 GiB），适合作为 CPU 重放的规格参考；AWS 公开的 `p3.2xlarge` 有一张 16 GiB V100，可作为 trace 生成规格参考。[R7i 规格](https://aws.amazon.com/ec2/instance-types/r7i/)，[P3/V100 规格](https://docs.aws.amazon.com/ec2/latest/instancetypes/pg.html)

这不是要求现在租用：当前停止点的最佳动作是先等 3 条已启动的 GEMM frozen 自然结束，读取 V5 同口径统计，并用现有 trace 完成机制定位。只有确定需要补论文原始/等价 trace 时，才租一张 V100；只有准备做完整 4×64 四模式矩阵时，才租高内存 CPU 机。

### 3.8.5 为什么目前没有完整采用论文规模/时序参数，以及后续公开参数重建决策

这不是做不到。实施顺序原本是先在 TLS-MINI（4 chip × 8 SM/chip）证明请求生命周期、有限队列/带宽、page placement、CL1/RL1、store/atomic 和自然排空正确，避免在 256-SM 长运行里调试基础状态机；随后 P9B 先用 CFD 的 TLS-only dynamic/frozen 控制确认 4×64 的数组规模、端点索引和排空不会失败。这个顺序解释了为什么先有 MINI 32 行和 4×64 两条控制。

但必须区分“分阶段合理”与“论文参数已完成”：P9B 当前只匹配了拓扑、L1/LLC/RL1 容量比例和 memory-channel 数，**没有**匹配论文的 32 cycles/hop，也没有四模式的同 trace IPC 对照。因此它是 topology-scale mechanism control，不是 paper-faithful performance result。实施细则要求论文规模配置承载公开参数；在此项补齐前，不能宣称 P9 的论文对照部分完成。

用户授权对论文未公开处采用有据可查的最佳工程方案。这里的“最佳”应理解为**静态、有限资源、可复现且不根据 IPC 结果事后挑选**，而不是把某个 workload 的最佳数字当成默认配置。公开参数重建的默认决策如下；所有项都应打印到 `TLS_CONFIG`、写入 `assumptions.yml`，并做敏感性而不是隐藏它们。

| 项目 | 论文公开事实 | 采用的公开重建主配置 | 原因与保护措施 |
| --- | --- | --- | --- |
| 拓扑 | 4 chip × 64 SM/chip，cluster = 4 | 4×64、16 clusters/chip、每 cluster 3 CL1 + 1 RL1 | 已由 P9B TLS control 验证可运行。 |
| core/NoC/L2 时钟 | 表中公开 1 GHz，当前 QV100 基础为 1132 MHz | `1000:1000:1000:850` MHz（DRAM 保留 V100 基础值，因论文未给 DRAM domain） | 让所有公开的 cycle/带宽值用 1 GHz core domain 解释；把 DRAM domain 留作假设，不伪称论文值。 |
| ring latency | 32 cycles/hop | `-mgpu_interchip_link_latency 32` | 已有配置项与 fabric 接线；需用 0/1/2 hop directed test 验证逐跳增量。 |
| ring bandwidth | 768 GB/s，未说明单链路/双向/整环口径 | 主配置解释为**每条有向 physical ring link** 768 B/cycle（1 GHz）；同时报告 192/384/768 B/cycle 敏感性 | 保守地把口径显式化；不能只报最有利的一个数。 |
| ring queue | 未给 | 512 entries | 与论文表中 NoC in/out buffer limit 512 对齐，仍是有限回压。 |
| TLS 两级 xbar latency | 未给 | 每个 xbar pipeline 1 core cycle | 小型 4×4/16×16 crossbar 的固定、可复核假设；需报告 1/2/4-cycle 敏感性。 |
| TLS xbar bandwidth/queue | 未给；论文 NoC flit 40 B、buffer 512 | 40 B/cycle、512 entries | 用公开 flit/buffer 作为统一有限资源基准；对 32/40/80 B/cycle 做敏感性。 |
| CL1/RL1 地址映射 | 精确 selected bits 未给 | line-address modulo 的均匀静态映射 | 不使用 oracle 或动态调优；记录 hash/映射，并比较可选 xor mapping。 |
| L1.5 对照 | 需同容量/带宽公平比较，但细节未公开 | RDC 容量、slice、bank/port、xbar 资源与 TLS RL1 对齐；仅缓存 remote-home line | 防止以额外容量或无限端口获得不公平结果。 |

这些参数在当前暂停期间只作为记录，**不修改正在运行的 V5 MINI 配置**。恢复后应先新建独立 `paper-public-32hop` 配置与 lockfile，不覆盖 V4/V5 结果；通过 directed 逐跳、带宽上限、dynamic/frozen replay 和四模式短 workload 配对之后，才扩大到 4×64 正式矩阵。

### 3.8.6 ideal-RDC ICL：已经做过什么、还应做什么

当前服务器已经完成了“自己做一遍”的第一层：P4 ideal-RDC observer 通过 timing-neutral gate，V4 的四个正式 trace 都已在 baseline 下测得 ICL（见 3.8.3）。因此不需要为了验证 observer 是否可用再重跑同一四条。

仍有必要在当前服务器继续做第二层，但它是**候选 workload 筛选**，不是重复验证：对已有的 FFT/SPMV/SORT/GEMM/ST2D/REDC 等候选 trace 逐条 replay，并以同一 observer 输出 remote frequency、ideal-RDC hit rate 与 ICL；仅 ICL 与 trace provenance 合格者再进入 4×64 性能矩阵。这一步仍只需要 CPU，不需要租 GPU。当前用户要求“未启动的暂不启动”已暂停这类候选 replay；等 V5 已启动的三条 GEMM frozen 自然结束、并由用户明确恢复后再按 manifest 逐项启动。

### 3.8.7 为什么 32-SM replay 已很久、256-SM 会怎样，以及可审的加速策略

一个 Accel-Sim trace replay 的主要 wall-clock 近似为：

`simulated cycles ×（每 cycle 的全局 fabric/cache 工作 + SM 数 × 每 SM pipeline 工作）+ trace I/O`。

因此不能简单用 `256 / 32 = 8` 推出论文规模一定慢八倍：SM 数增加会使每 cycle 处理的对象变多，但相同 trace 的 CTA 可并行到更多 SM，模拟周期可能显著下降。已有同一 CFD 097K trace 的实证是：TLS-MINI dynamic 为 633,642 simulated cycles，而 4×64 TLS control dynamic 为 187,695 cycles；frozen 则为 808,379 与 580,961 cycles。后者的每 cycle 开销更高，但模拟周期更少，最终 wall-clock 必须以一次 pilot 实测，不能凭拓扑比例估计。

当前最久的是 PolyBench GEMM frozen：739,246,080 指令、约 14.1–14.2M simulated cycles，单行已超过 3 小时。它慢的直接原因是 trace/计算量和 frozen placement 下的低 IPC，而不是内存不足：单个进程 RSS 约 1.5 GiB、CPU 接近一个满核；但宿主机当前可用内存约 76 GiB 且 swap 已满，不能仅因 CPU load 未满就盲目大量并行。

可采用的优化按安全性和收益排序如下：

1. **减少不必要的运行数**：ICL 筛选只跑 baseline + P4 ideal-RDC observer；不跑 TLS、Shared、L1.5，也不需要 V5 的通用读路径 sidecar。对 7 个已验证 paper-candidate trace，这将是 7 条而不是 14 条成对/56 条四模式运行。
2. **分层筛选**：先所有候选跑 dynamic baseline ICL；仅对 ICL/trace-provenance 合格者再跑 frozen robustness；仅最终入选者进入昂贵的 4×64 四模式矩阵。正式结果仍必须自然 drain，不能用 cycle/CTA 截断替代。
3. **资源自适应并行**：先启动一条短/中等候选作为 pilot，记录 RSS 峰值、trace I/O、simulated cycles/s；再按可用 RAM 和 swap 状态决定 1、2 或最多 4 个独立 replay。不同 mode/workload 的输出目录必须不可变，禁止同一日志并写。
4. **复用已构建的 release 与本地 trace**：正式筛选使用 P4/V4 core（不含 V5 每读 sidecar），保留 V5 只用于需要跨模式服务/延迟分析的少量配对；trace 均从本地 NVMe/已校验路径读取，不复制到网络盘。
5. **把配置/机制优化与实验优化分开**：可改进 runner 的资源 guard、结果重用、并行调度和统计解析；不能为了提速去掉有限 queue/bandwidth、缩小 workload 或放松 natural-drain gate。编译器/PGO 级优化需在独立二进制身份和 baseline regression 下验证，不能混入机制结果。

### 3.8.8 ICL 数字的准确含义与候选筛选提案（待审）

对每条 global read，P4 observer 先判定其 page home 是否在 requester 以外的 chip；若是 remote read，再用一个只观察、容量足够大的 shadow RDC 判断该 sector 是否已在 requester chip 上因较早 remote 返回而驻留。因此：

`remote read frequency = remote-home global reads / all global reads`  
`ideal RDC hit rate = 已驻留的 remote reads / remote-home reads`  
`ICL = 两者相乘`

例如 SRAD dynamic 的 remote frequency 为 0.8372，ideal RDC hit rate 为 0.9767，乘积为 0.8177。这表示约 81.8% 的所有被统计 global reads 在“无限、零替换压力的本 chip remote-data cache”下有重用机会；它**不是**实际 TLS 的 CL1/RL1 hit rate，也不是“IPC 将提升 81.8%”。实际 TLS 仍受有限容量、endpoint mapping、MSHR/queue、xbar/ring 带宽、实际返回延迟、memory dependence 和 page placement 影响。

CFD dynamic 的 0.4728 可拆为 remote frequency 0.7894 × ideal RDC hit rate 0.5989：远端访问不少，但可由无限 RDC 重用的比例低于 SRAD。GEMM 为 0.7623 × 0.8577 = 0.6539，FDTD2D 为 0.7915 × 0.9962 = 0.7885。frozen 值不同，恰好说明 page home 会改变远端比例与可重用机会；这也是必须同时记录 placement 的原因。

待审的候选筛选 campaign 如下，不在当前暂停状态下自动启动：

| 顺序 | 输入 | 实验 | 产物/门禁 | 目的 |
| --- | --- | --- | --- | --- |
| 0 | `ss`、`fft`、`spmv`、`sort`、`gemm_shoc`、`st2d`、`redc` 的现有 candidate-verified trace | 只读检查 manifest、kernel list、SHA、trace 大小 | 可用性与 provenance 清单 | 不花模拟时间先排除错误输入。 |
| 1 | 选一个中等规模候选（优先 FFT 或 SPMV） | **一条** dynamic Baseline + P4 observer，自然 drain | remote frequency、ideal RDC hit rate、ICL、RSS/时间/profile | 校准运行成本和脚本。 |
| 2 | 余下六条 | 每条一条 dynamic Baseline + observer；并发度由步骤 1 的 peak RSS/host headroom 决定 | 同一 CSV、无死锁、observer/trace provenance gate | 形成 paper-family ICL 排名。 |
| 3 | 排名靠前且 paper mapping 清楚者 | frozen Baseline observer 控制 | dynamic/frozen ICL 差异与 page hash | 排除仅由不稳 placement 造成的候选。 |
| 4 | 入选者 | 4×64 public-parameter 四模式配对 | IPC、P9_READ 延迟/服务、hops/backpressure、配置/二进制/trace provenance | 才进入论文趋势对照。 |

这套筛选能在当前 CPU 服务器完成，且比直接扩大所有 workload 的四模式矩阵节省数量级的时间。它不代替论文 trace/input 对齐；每条仍保持 `candidate-verified`，直到来源/输入映射充分证明后才晋升为正式 aggregate 输入。

### 3.8.9 ICL campaign 执行记录

候选 baseline-only campaign 的工具已放在 V4/P4 worktree：`icl_candidates.csv`、`run_icl_screen.sh`、`verify_icl_screen.sh` 和 `summarize_icl_screen.sh`。它们使用 P4 已验证的 timing-neutral observer，不使用 V5 sidecar，也不启动 TLS/Shared/L1.5。每条日志不可覆盖；门禁检查自然结束、baseline mode、统计版本、request/response fabric 排空，以及从原始计数重算 ICL。

首条 FFT pilot 于 2026-08-22 完成：22,061,056 instructions、61,815 cycles、IPC 356.8884，`root_remote_reads = 0`、`ICL = 0`。因此该 V100 SHOC FFT trace 在本地 first-touch 配置中没有可供 TLS 利用的远端重用机会，不应仅凭论文 Table 2 的 FFT 名称进入后续 4×64 TLS 性能矩阵。原始日志、CSV 和 provenance 位于 `/workspace/worktrees/accel-sim-tls-cache/hw_run/tls-cache-icl-screen/pilot-fft-v1/`。

### 3.7 可以做的单 workload 对照，以及目前差异的含义

只有 SRAD、CFD、GEMM 在名字或算子上能勉强与 Fig. 8 对照；FDTD2D 不在论文 Table 2 中。下表故意同时给出本地 dynamic 与 frozen 控制，避免把 page placement 效应误当作 TLS 效应。

| 名称重合/相近项 | Paper TLS（约） | 本地 TLS dynamic | 本地 TLS frozen | 初步判定 |
| --- | ---: | ---: | ---: | --- |
| SRAD（Rodinia 对 Rodinia） | 1.20 | 1.043 | 1.008 | 同为小幅正向/近基线，但本地收益明显更小。 |
| CFD（Rodinia 对 Rodinia） | 1.77 | 1.184 | 0.997 | dynamic 同为正向但幅度较小；冻结 page map 后收益消失，说明 placement/执行时序影响很强。 |
| GEMM（Paper SHOC，对本地 PolyBench） | 1.49 | 0.834 | 0.992 | 方向不同，但二者不是同一 benchmark 实现或输入，不能直接判为机制错误。 |
| FDTD2D（本地 PolyBench） | 不适用 | 0.827 | 0.937 | 非论文 workload；只能作为负效与压力诊断样本。 |

**现阶段不能把这些差距归咎于 TLS 实现错误。** 已通过的守恒、最终 completion、有限带宽、自然 drain、dynamic/frozen replay 和 TLS 服务层级检查，排除了最明显的请求丢失、重复完成、未排空 fabric、完全未触发 CL1/RL1 这类功能性错误；但这些门禁不能证明性能模型与论文完全等价。

差异首先有四类可验证来源，优先级由高到低如下：

1. **实验不等价（已确认）**：V4 P9A 为 4 chip × 8 SM/chip MINI，论文为 4 × 64；当前 MINI 配置的 ring/TLS xbar latency 都为 1 cycle，论文报告 inter-chip 为 32 cycles/hop。P9B 虽扩大到 4 × 64，却仍是 TLS-only 控制，且当前公开重建配置仍使用 1-cycle inter-chip latency；它不能验证论文图的 IPC。
2. **workload 与输入不等价（已确认）**：SRAD 为 1/40 trimmed；CFD 的 paper input 未知；本地 GEMM/FDTD2D 来自 PolyBench，而 paper GEMM/ST2D 来自 SHOC。应用的 kernel mix、memory sharing 和 first-touch 次序会直接改变 ICL 与收益。
3. **论文缺失的模型参数（已登记）**：CL1/RL1 的确切地址位、TLS xbar latency/queue/arbitration、768 GB/s 的带宽口径、L1.5 组织和 store/atomic policy 都未公开；当前 `assumptions.yml` 将这些标为公开描述重建的待确认项。
4. **仍待排查的模型瓶颈或实现偏差**：不同模式的最终服务比例、请求者端到端延迟、queue/backpressure、link byte/hop 和 dynamic page hash 如何共同造成 IPC 差异。V5 的共同 `P9_READ_*` 数据正是第一个可证伪检查。

后续判别顺序是：先完成 V5 并确认“观测不改变 V4 IPC”；随后按 workload 比较四模式的 `P9_READ_*` 服务/延迟、page hash、hops、link bytes 和 backpressure；只有这些量显示与预期路径不一致时，才回到请求路由、endpoint mapping、fill/response 和仲裁代码逐段定位。最后再以 4×64、论文公开的 32-cycle/hop 参数和同一 workload/输入组成完整四模式配对矩阵，才有资格判断是否存在相对论文的机制性能差距。

## 4. 后续如何使用本文

1. 当前分析与图表使用第 3 节的 V4 CSV，明确写为“本地 MINI workload 机制矩阵”；Fig. 8 的纸面近似读数只能作定位参考。
2. V5 完成后，仅用通过 `P9_READ_*` 守恒门禁的 `p9_read_summary.csv` 来比较读延迟和服务层级；用 V5 的配对 IPC 表复核 V4 性能不因观测改变。
3. 只有获得论文对应的完整 trace/input、严格匹配 4×64 配置并完成四架构的配对实验后，才讨论与论文 `+30.2%` 的数值接近程度。
4. 对负效 workload，优先检查共同 read-path 统计、page hash/placement、request/response hops、link bytes、queue peak 与 backpressure；不要通过选择性调参删除负例。
