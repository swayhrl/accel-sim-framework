# Decoupled-L2 workload 峰值 RSS 与并行排程

本表服务于宿主机排程，而不是架构性能结论。RSS 指**一个自然结束的模拟器进程**
的峰值 resident set size；baseline 与 Decoupled 是两个独立进程，成对实验同时启动时
须分别预留两份内存。

数据状态：

* `D`：本 Decoupled-L2 当前树的实测 peak RSS；可直接用于本树排程。
* `X`：TLS/C2P 对同一保留 trace 的实测值；仅作保守的启动先验，首次本树 replay
  必须重新采样。
* `U`：没有可信峰值记录。不是“内存很小”；首次使用必须单独 profile 后才允许并发。

“预留”包含约 25% 余量并向上取整；它不含 OS page cache、trace 解压空间、其他用户
进程或 baseline/decoupled 的另一 arm。所有条目均来自
[workload roster](decoupled_l2_workload_roster_under_5h.md)，已排除已知运行超过五小时
的 workload。

## 已有记录概览

52 个可排程条目中，**3 个有本树实测值（D）**，**10 个有跨项目可用先验（X）**，
其余 **39 个为 U**。因此当前可安全做内存 bin-packing 的不是“全部 52 项”，而是这
13 项；每个 U workload 在首次进入批量实验前先做一个 single-arm profiling run。

当前最高内存先验是 Parboil `sgemm`（C2P，约 7.8 GiB），其次是 PolyBench `gemm`
（TLS，约 6.45 GiB）。这两项不得与其他高内存/未知项盲目批量启动。

## CUDA SDK

| Workload | Peak RSS | 状态 | 单进程预留 |
|---|---:|:---:|---:|
| `BlackScholes` | 待测 | U | 首跑单独 profile |
| `convolutionSeparable` | 待测 | U | 首跑单独 profile |
| `fastWalshTransform_11_19` | 待测 | U | 首跑单独 profile |
| `fastWalshTransform_7_21` | 待测 | U | 首跑单独 profile |
| `scalarProd_8192` | 待测 | U | 首跑单独 profile |
| `scalarProd_13920` | 待测 | U | 首跑单独 profile |
| `scan` | 待测 | U | 首跑单独 profile |
| `sortingNetworks` | 待测 | U | 首跑单独 profile |
| `transpose` | 待测 | U | 首跑单独 profile |
| `vectorAdd_4000000` | 待测 | U | 首跑单独 profile |
| `vectorAdd_6000000` | 待测 | U | 首跑单独 profile |

## Accel-Sim V100 ubench

| Workload | Peak RSS | 状态 | 单进程预留 |
|---|---:|:---:|---:|
| `atomic_add_bw` | 待测 | U | 首跑单独 profile |
| `atomic_add_bw_conflict` | 待测 | U | 首跑单独 profile |
| `l2_bw_32f` | 待测 | U | 首跑单独 profile |
| `l2_bw_64f` | 待测 | U | 首跑单独 profile |
| `mem_bw` | 待测 | U | 首跑单独 profile |
| `mem_lat` | 待测 | U | 首跑单独 profile |

## Rodinia

| Workload | Peak RSS | 状态 | 单进程预留 |
|---|---:|:---:|---:|
| `cfd_097k` | 1.60 GiB（TLS P9） | X | 2.0 GiB |
| `srad_trim` | 1.18 GiB（TLS P9） | X | 1.5 GiB |
| `btree` | 0.41 GiB（C2P host profile） | X | 0.6 GiB |
| `dwt2d` | 待测 | U | 首跑单独 profile |
| `gaussian` | 0.38 GiB（C2P host profile） | X | 0.5 GiB |
| `hotspot1` | 待测 | U | 首跑单独 profile |
| `lud` | 待测 | U | 首跑单独 profile |
| `nn` | 0.37 GiB（C2P host profile） | X | 0.5 GiB |
| Rodinia `bfs` | 待测 | U | 首跑单独 profile |

## Parboil

| Workload | Peak RSS | 状态 | 单进程预留 |
|---|---:|:---:|---:|
| Parboil `bfs` | 待测 | U | 首跑单独 profile |
| `cutcp` | 待测 | U | 首跑单独 profile |
| `histo` | 待测 | U | 首跑单独 profile |
| `mri-q` | 待测 | U | 首跑单独 profile |
| `sad` | 待测 | U | 首跑单独 profile |
| `sgemm` | 7.8 GiB（C2P full point） | X | 10 GiB |
| `spmv` | 待测 | U | 首跑单独 profile |
| `stencil` | 待测 | U | 首跑单独 profile |

## PolyBench

| Workload | Peak RSS | 状态 | 单进程预留 |
|---|---:|:---:|---:|
| `atax` | 1.53 GiB（B/D/O 最大值） | D | 2.0 GiB |
| `bicg` | 1.53 GiB（B/D/O 最大值） | D | 2.0 GiB |
| `mvt` | 1.51 GiB（B/D/O 最大值） | D | 2.0 GiB |
| `gesummv` | 待测 | U | 首跑单独 profile |
| `2DConvolution` | 0.35 GiB（C2P policy/adaptive） | X | 0.5 GiB |
| `3DConvolution` | 待测 | U | 首跑单独 profile |
| `3mm` | 待测 | U | 首跑单独 profile |
| `gemm` | 6.45 GiB（TLS P9） | X | 8 GiB |

## TLS V100 archive（仅 bounded replay）

| Workload | Peak RSS | 状态 | 单进程预留 |
|---|---:|:---:|---:|
| Mars `ss` | 0.434 GiB（kernel-only screen） | X | 0.6 GiB |
| SHOC `fft` | 待测 | U | 首跑单独 profile |
| SHOC `sort` | 待测 | U | 首跑单独 profile |
| SHOC `gemm` | 待测 | U | 首跑单独 profile |
| SHOC `redc` | 待测 | U | 首跑单独 profile |

`ss` 的记录不是自然结束性能点，RSS 仍可作为该 replay 形态的启动先验；它不能外推到
其它 Mars 输入或完整 replay。

## C2P V100 extension

| Workload | Peak RSS | 状态 | 单进程预留 |
|---|---:|:---:|---:|
| ISPASS `bfs` | 待测 | U | 首跑单独 profile |
| ISPASS `lps` | 0.69–0.72 GiB（C2P） | X | 1.0 GiB |
| ISPASS `ray` | 待测 | U | 首跑单独 profile |
| ISPASS `lib` | 待测 | U | 首跑单独 profile |
| Pannotia `fw_block` | 待测 | U | 首跑单独 profile |

## 启动规则

1. **测量先行。** 对 U 条目，先以当前 binary、trace、config 跑一个 arm，并以
   `/usr/bin/time -v` 记录 `Maximum resident set size`；将 KiB 原值、换算 GiB、
   backend、commit、trace/config hash 写入本表或对应 run 目录。
2. **成对实验按两个进程计。** 例如 PolyBench `gemm` baseline+decoupled 同时启动，
   仅模拟器预留就是 `2 × 8 = 16 GiB`，不是 8 GiB。
3. **高内存隔离。** `sgemm`（10 GiB reserve）与 `gemm`（8 GiB reserve）不与 U
   条目同批；多个 U 条目也不要在 RSS 未知时一起启动。
4. **总量门槛。** 以 cgroup/主机实际可用内存为准，所有预留之和最多使用可用内存的
   75%，余下空间留给 OS、page cache、trace staging 与其它用户。CPU 核数不是当前
   首要门槛：每个 Accel-Sim replay 基本只占一个计算核，而峰值 RSS 才决定可安全并发数。
5. **trace 空间独立预算。** RSS 不等于压缩包、临时解压或输出日志空间；仍保持既定的
   磁盘余量门槛。

## 证据来源

* 本树 D：`hw_run/decoupled-l2-bank-candidate/20260826-8bank-current-model/partial_three_arm_results.md`。
* TLS X：`/workspace/worktrees/accel-sim-tls-cache/docs/tls-cache/workload_catalogue.md`。
* C2P X：`/workspace/worktrees/accel-sim-c2p-cache/docs/c2p-cache/workload_catalogue.md`。
