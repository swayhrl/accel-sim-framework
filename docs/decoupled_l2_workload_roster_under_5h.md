# Decoupled-L2 可用 workload 清单（已跑过，已知单 arm 不超过 5 小时）

这是后续 Decoupled-L2 结构改动可选的 workload 总清单。它合并了本项目、
C2P 和 TLS 的归档记录，并按**同名同输入**去重。

筛选规则：

1. 至少在 Decoupled-L2、C2P 或 TLS 中留有一次成功执行证据；
2. 已知的完整单 arm 历史墙钟时间不超过 5 小时；
3. 若只做过 TLS 的 10,000-cycle bounded replay，仍列出，但明确标为 `bounded`，
   不得作为完整 IPC/周期结果；
4. `syrk`（约 17--19 小时）、`fdtd2d`（约 44.5 小时）和 TLS `st2d`
   screen（约 8h13m）因已知超过 5 小时被排除。

“通过来源”只说明该 trace/输入曾成功运行，**不**表示可将不同项目的结果、
配置或收益混合比较。新结构仍要在当前同 revision baseline/decoupled 下重跑。

## 数量汇总

以“测试集 + workload + 保留输入”为一个条目计数（所以 Rodinia BFS 和 Parboil
BFS、PolyBench GEMM 和 Parboil/SHOC GEMM 分别计数），排除已知超过五小时的项后
共有 **52 个**条目。

| 来源数据集 | 条目数 | 完成性说明 |
|---|---:|---|
| CUDA SDK | 11 | Decoupled-L2 full 双臂 closeout。 |
| Accel-Sim V100 ubench | 6 | Decoupled-L2 full 双臂 closeout。 |
| Rodinia | 9 | TLS 或 C2P full；其中 LUD 另有 Decoupled-L2 native smoke。 |
| Parboil | 8 | Decoupled-L2 archive full 和/或 C2P full。 |
| PolyBench | 8 | Decoupled-L2 archive/bank diagnosis full 和/或 C2P full/部分完成。 |
| TLS V100 archive（Mars/SHOC） | 5 | 仅 bounded 10,000-cycle replay；不具完整性能资格。 |
| C2P V100 extension（ISPASS/Pannotia） | 5 | C2P 已运行；尚未变为本 L2 runner 的完整 pair。 |
| **总计** | **52** | |

## 按程序行为分类

以下分类是互斥的、用于挑选 L2 测试，而不是声称应用只有一种访存模式。

| 行为类 | 条目数 | Workload |
|---|---:|---|
| 规则 stencil / 邻域计算 | 6 | `convolutionSeparable`、`srad_trim`、`hotspot1`、Parboil `stencil`、`2DConvolution`、`3DConvolution` |
| 稠密线性代数 / 矩阵与向量计算 | 12 | `scalarProd_8192`、`scalarProd_13920`、`gaussian`、`lud`、Parboil `sgemm`、`atax`、`bicg`、`mvt`、`gesummv`、`3mm`、PolyBench `gemm`、SHOC `gemm` |
| 不规则图、稀疏、搜索或 traversal | 9 | `cfd_097k`、`btree`、`nn`、Rodinia/Parboil/ISPASS `bfs`、`spmv`、`ss`、ISPASS `ray` |
| 变换、归约、重排或阶段性访问 | 10 | 两个 `fastWalshTransform`、`scan`、`sortingNetworks`、`transpose`、`dwt2d`、`sad`、`fft`、`sort`、`redc` |
| 流式或粒子/领域数组计算 | 5 | `BlackScholes`、两个 `vectorAdd`、`mri-q`、`cutcp` |
| atomic / 热点更新 | 3 | `atomic_add_bw`、`atomic_add_bw_conflict`、`histo` |
| 显式 L2/DRAM 微基准 | 4 | `l2_bw_32f`、`l2_bw_64f`、`mem_bw`、`mem_lat` |
| 专项控制 / 动态规划输入 | 3 | ISPASS `lps`、ISPASS `lib`、Pannotia `fw_block` |
| **总计** | **52** | |

`fw_block` 是 blocked Floyd--Warshall；为保持分类互斥，它归入“专项控制 / 动态规划”
而不重复计入稠密线性代数类。

## 已知运行时间最长的前十项

按目前可读取记录中的**最长单 arm 墙钟时间**排序；不同项目、模式和宿主负载不同，
仅用于排程。`ss` 是 kernel-only screen，不能当作完整自然结束性能数据。

| 排名 | Workload / 输入 | 最长已知单 arm 时间 | 备注 |
|---:|---|---:|---|
| 1 | CUDA SDK `scan` | 3h59m45s | Decoupled-L2 arm。 |
| 2 | TLS Mars `ss` | 3h43m41s | 仅 kernel-only screen。 |
| 3 | `l2_bw_64f` | 2h27m52s | Decoupled-L2 带宽微基准。 |
| 4 | PolyBench `3mm` | 2h23m53s | Decoupled-L2 archive。 |
| 5 | Parboil `histo` | 2h11m54s | Decoupled-L2 archive。 |
| 6 | Parboil `cutcp` | 2h09m04s | Decoupled-L2 archive。 |
| 7 | `atomic_add_bw_conflict` | 1h32m13s | Decoupled-L2 热点 atomic。 |
| 8 | `l2_bw_32f` | 1h21m13s | Decoupled-L2 带宽微基准。 |
| 9 | PolyBench `gemm` | 1h07m05s | TLS baseline/dynamic；另有不同输入的 Parboil/SHOC GEMM。 |
| 10 | Parboil `stencil` | 1h06m12s | Decoupled-L2 archive。 |

## CUDA SDK：受控 kernel / 微应用

全部来自 Decoupled-L2 的完整双臂 closeout，均为 `full`。

| Workload | 程序类型 | 已知单 arm 时间 | 建议用途 |
|---|---|---:|---|
| `BlackScholes` | 批量期权定价，独立数据并行 | 9--10 s | 极快 smoke。 |
| `convolutionSeparable` | 二维可分离图像卷积，行/列邻域访问 | 20--25 min | 规则空间局部性、fill。 |
| `fastWalshTransform_11_19` | 小规模 Walsh-Hadamard 蝶形变换 | 3--4 min | 阶段性 stride/重排。 |
| `fastWalshTransform_7_21` | 较大 Walsh-Hadamard 蝶形变换 | 29--59 min | 变换吞吐和阶段边界。 |
| `scalarProd_8192` | 向量点积/归约 | 5--7 min | 小型 streaming + reduction。 |
| `scalarProd_13920` | 向量点积/归约 | 11--17 min | 中等规模 reduction。 |
| `scan` | 前缀和，多级 block scan 与中间数组 | 1h47m--3h59m | 代表性长项；不放入日常快速回归。 |
| `sortingNetworks` | 固定比较-交换网络排序 | 6--7 s | 极快功能/负例。 |
| `transpose` | 矩阵转置，规则 strided/coalesced 访问 | 3--4 min | 地址映射、局部性对照。 |
| `vectorAdd_4000000` | 两输入向量流式读、单输出写 | 3--6 min | 流式读写、简单带宽检查。 |
| `vectorAdd_6000000` | 更大工作集的 vector add | 4--8 min | 尺寸敏感性。 |

## Accel-Sim V100 ubench：资源压力与边界

全部来自 Decoupled-L2 完整双臂 closeout，均为 `full`。它们用于机制边界，
不应单独构成 application-suite 平均值。

| Workload | 程序类型 | 已知单 arm 时间 | 建议用途 |
|---|---|---:|---|
| `atomic_add_bw` | 分散地址 atomic-add 吞吐 | 33--35 min | 简化 atomic 和原子吞吐。 |
| `atomic_add_bw_conflict` | 热点地址 atomic-add，高冲突 RMW | 1h26m--1h32m | 原子串行化/热点压力。 |
| `l2_bw_32f` | L2 读带宽微基准 | 1h11m--1h21m | lower-read credit、bank 敏感性。 |
| `l2_bw_64f` | 更长 L2 读带宽微基准 | 2h25m--2h28m | 长带宽压力。 |
| `mem_bw` | 外存带宽压力 | 25--43 min | lower/memory path。 |
| `mem_lat` | 依赖链式内存延迟压力 | 2.5--3 min | response path、latency 回归。 |

## Rodinia：应用导向计算核

| Workload | 通过来源 | 程序类型 | 已知单 arm 时间 | 建议用途 |
|---|---|---|---:|---|
| `cfd_097k` | TLS `full` P9；trace 本地可用 | 非结构网格 CFD，间接 mesh 访问 | 5--6 min | 主力不规则应用项。 |
| `srad_trim` | TLS `full` P9；1/40 trace | 迭代图像扩散，二维邻域 stencil | 18 min | 规则局部性；必须标明 trimmed。 |
| `btree` | C2P `full` | B+ tree 指针追逐/索引遍历 | 8--14 min | 不规则读、miss path。 |
| `dwt2d` | C2P `full` | 二维小波变换，多阶段局部访问 | — | stage-dependent locality。 |
| `gaussian` | C2P `full` | Gaussian elimination，pivot/行更新 | 19--21 min | 稠密线性代数近中性对照。 |
| `hotspot1` | C2P `full` | 热传导 grid stencil | — | 第二个规则 stencil。 |
| `lud` | C2P `full`；Decoupled-L2 native smoke | LU decomposition | — | dense update。 |
| `nn` | C2P `full` | 最近邻地理查询 | 3--4 s | 极快不规则负控制。 |
| `bfs` | C2P directed `full` | 图 frontier / 邻接表遍历 | — | 图访问与不规则压力。 |

## Parboil：应用型科学与数据处理 kernel

| Workload | 通过来源 | 程序类型 | 已知单 arm 时间 | 建议用途 |
|---|---|---|---:|---|
| `bfs` | Decoupled-L2 archive `full` | 图 BFS / frontier 邻接表 | 9--14 min | 不规则图访问；与 Rodinia BFS 输入不同。 |
| `cutcp` | C2P `full`、Decoupled archive `full` | 粒子到网格 Coulombic potential | 1h37m--2h09m | 混合规则/不规则访问。 |
| `histo` | Decoupled archive `full` | 图像直方图，原子热点更新 | 45m--2h12m | atomic/hotspot 应用对照。 |
| `mri-q` | C2P `full`、Decoupled archive `full` | MRI-Q 重建，规则数组 streaming | 9--16 min | 应用型 streaming 对照。 |
| `sad` | Decoupled archive `full` | 视频块匹配，sum of absolute differences | 2--5 min | 快速图像/局部访问项。 |
| `sgemm` | C2P `full`、Decoupled archive `full` | 单精度 dense GEMM | 12--26 min；C2P 曾约 7.8 GiB RSS | dense reuse；与 PolyBench GEMM 分开。 |
| `spmv` | Decoupled archive `full`；TLS `bounded` | 稀疏矩阵-向量 gather | 1--2.5 min | 低成本不规则访问。 |
| `stencil` | C2P `full`、Decoupled archive `full` | 三维 stencil | 43--66 min | 规则 3-D 邻域读写。 |

## PolyBench：受控数值计算 kernel

| Workload | 通过来源 | 程序类型 | 已知单 arm 时间 | 建议用途 |
|---|---|---|---:|---|
| `atax` | Decoupled bank diagnosis `full`；C2P 有 trace/部分 evidence | `A^T(Ax)`，两次矩阵-向量 streaming | 13--29 min | 已直接测得高 AAD overlap。 |
| `bicg` | Decoupled bank diagnosis `full`；C2P 有 trace/部分 evidence | `q=Ap`、`s=A^Tr` | 13--16 min | 已直接测得高 AAD overlap。 |
| `mvt` | Decoupled bank diagnosis `full` | 两次矩阵-向量更新 | 13--17 min | ATAX/BICG 的配对对照。 |
| `gesummv` | Decoupled bank diagnosis `full`；C2P 有 trace/部分 evidence | `y=αAx+βBx` | 16--20 min | 已直接测得低 AAD merge 对照。 |
| `2DConvolution` | C2P `full`、Decoupled archive `full` | 二维滑窗卷积 stencil | 24--46 min | 规则 stencil。 |
| `3DConvolution` | Decoupled archive `full` | 三维卷积 stencil | 26--40 min | 规则 3-D stencil。 |
| `3mm` | Decoupled archive `full`；C2P 有 trace/缺完整 bundle | 三次串联 GEMM | 1h44m--2h24m | 多阶段 dense reuse。 |
| `gemm` | C2P `full`、TLS `full`、Decoupled archive `full` | 稠密矩阵乘 | 27--67 min；TLS 一点约 6.45 GiB RSS | dense-tile reuse。 |

## TLS V100 archive：仅 bounded compatibility 的补充项

下列项都曾在 TLS 中达到有界 10,000-cycle replay 并观察到有效请求；它们不等价于
完整自然结束。已知没有单 arm 超过 5 小时的记录，但其完整运行成本尚未建立。

| Workload | 数据集 | 程序类型 | 状态 |
|---|---|---|---|
| `ss` | Mars/V100 | similarity search / pattern matching，不规则遍历 | `bounded`；一次 kernel-only screen 3h44m、444 MiB。 |
| `fft` | SHOC/V100 | 多阶段 butterfly FFT，stride 随 stage 改变 | `bounded`。 |
| `sort` | SHOC/V100 | key/value 重排，阶段性不规则访问 | `bounded`。 |
| `gemm` | SHOC/V100 | dense GEMM | `bounded`；与 PolyBench/Parboil GEMM 输入不同。 |
| `redc` | SHOC/V100 | tree reduction，many-to-one 聚合 | `bounded`。 |

## C2P V100 补充 trace：已运行但需导入当前 L2 runner

| Workload | 数据集 | 程序类型 | 已知时间 / 状态 |
|---|---|---|---|
| `ispass_bfs` | ISPASS/V100 | 图 frontier / 共享压力 | C2P 定向运行通过；完整 host 时间未统一保留。 |
| `ispass_lps` | ISPASS/V100 | 低 candidate-count 的协议压力工作负载 | 91--146 s，C2P 运行通过。 |
| `ispass_ray` | ISPASS/V100 | ray traversal | C2P 运行通过；时间未统一保留。 |
| `ispass_lib` | ISPASS/V100 | ISPASS archive library workload | C2P 运行通过；时间未统一保留。 |
| `fw_block` | Pannotia/V100 | blocked Floyd-Warshall，全对最短路动态规划 | C2P 运行通过；时间未统一保留。 |

这些 V100 trace 在当前工作树有 remote-run/archive 资料，但尚未形成 Decoupled-L2
的本地完整 pair；首次使用前必须固定 trace/config hash 并跑 baseline/decoupled
自然结束门禁。

## 推荐的日常子集

为了避免每次结构改动都跑数十项，优先使用：

```text
nn + cfd_097k + spmv + atax + bicg + gesummv + mem_lat
```

这组覆盖极快 smoke、不规则 mesh/gather、高 AAD overlap、低 AAD overlap 和纯延迟。
结构稳定后增加 `btree`、`srad_trim`、`mri-q`、`2DConvolution`、`sgemm`，最后才加入
`scan`、`l2_bw_64f`、`cutcp`、`3mm` 等长项。

## 证据来源

* Decoupled-L2：`docs/decoupled_l2_experiment_history.md`，尤其第 3、4、8 节。
* C2P：`docs/c2p-cache/workload_catalogue.md`、
  `docs/c2p-cache/current_mechanism_and_experiment_audit_2026-08-21.md`、
  `docs/c2p-cache/validation_results.md`。
* TLS：`docs/tls-cache/workload_catalogue.md`、
  `hw_run/tls-paper-workload-coverage.md`。
