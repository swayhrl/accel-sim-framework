# TLS-Cache 复现：运行时长与资源规划

更新：2026-08-23。本文记录的是**宿主机实际 wall-clock**，不是模拟周期；
用于安排后续实验并发，不用于论文性能结论。

## 证据与边界

- 已完成的原始 `accel-sim.out` 日志本身含有
  `gpgpu_simulation_time = ... (N sec)`，这是历史运行的首选时长。
- 文件 birth time 到最终写入时间也被保留在清单中，但只是交叉检查；不能
  代替模拟器自身的 wall-clock 记录。
- 历史 V4/V5 runner 未统一采集峰值 RSS，因而历史内存列必须保持为空，不能
  从日志大小、模拟周期或当前进程 RSS 倒推。
- 从本次整理起，ICL runner 用 `/usr/bin/time -v` 直接保存 wall time、user/
  system CPU time、峰值 RSS、文件 I/O。只有进程自然结束后该文件才会写入；
  运行中的零字节 `.resources.txt` 不是缺失数据，也不是 0 RSS。

完整逐配置清单：
`/workspace/worktrees/accel-sim-tls-cache/hw_run/tls-cache-runtime-inventory-20260822-v2.csv`。
它包含 63 个自然完成运行的原始日志路径、模拟器 wall 时间、周期、指令数、IPC
以及（若存在）直接资源记录。

2026-08-23 起的 4×64 P9B 公共参数样本不追加入这个历史 CSV，而是以每个结果目录
中成对的 `.out`、`.resources.txt` 与 `.provenance.txt` 为准。这样不会混淆 MINI
历史运行与论文规模运行；待 P9B 矩阵完整并通过资格门后，再生成单独的不可变清单。

## 已完成运行的实际时长

下表是同一 workload 的配置变体汇总；min/max 是该组各条具体配置的范围。

| Campaign | workload | 配置数 | 总 wall time | 单条 min / mean / max |
|---|---:|---:|---:|---:|
| V4 MINI P9 | SRAD trimmed | 8 | 49.8 min | 5.5 / 6.2 / 6.8 min |
| V4 MINI P9 | CFD 097K | 8 | 56.9 min | 5.6 / 7.1 / 8.6 min |
| V4 MINI P9 | PolyBench GEMM | 8 | 22.3 h | 1.45 / 2.79 / 4.35 h |
| V4 MINI P9 | PolyBench FDTD2D | 8 | 62.3 h | 5.37 / 7.79 / 10.89 h |
| V4 4×64 pre-public（ring=1 cycle、32 B/cycle） | CFD 097K | 2 | 1.36 h | 11.2 / 40.8 / 70.4 min |
| V5 observe | SRAD trimmed | 8 | 55.0 min | 6.1 / 6.9 / 7.7 min |
| V5 observe | CFD 097K | 8 | 52.1 min | 5.4 / 6.5 / 8.2 min |
| V5 observe | PolyBench GEMM | 8 | 18.7 h | 1.22 / 2.34 / 3.57 h |
| ICL baseline-only | FFT | 1 | 20 s | 20 s |
| ICL baseline-only | SPMV | 1 | 1.5 min | 1.5 min |
| ICL baseline-only | SHOC GEMM | 1 | 6.9 min | 6.9 min |
| ICL baseline-only | SORT | 1 | 12.3 min | 12.3 min |
| ICL baseline-only | REDC | 1 | 16.2 min | 16.2 min |
| ICL baseline-only | ST2D | 1 | 8.21 h | 8.21 h |
| ICL baseline-only | SS kernel-only v4 | 1 | 3.73 h | 3.73 h |

因此，若以单进程串行方式重跑当前 V4 的 4 workload × 4 mode × 2 placement
完整 MINI 矩阵，已有样本的总量约为 **86.4 wall-hours**。决定总墙钟时间的不是
CFD/SRAD，而是 FDTD2D（约 62.3 h 的累计 CPU/单进程时间）；即使其它作业充分
并行，FDTD2D 的 10.89 h 单条长尾仍是本矩阵的下界之一。

“一轮”若指每个 workload 的一个配置，可先按上表 max 预留；若指完整 P9 矩阵，
应按每个配置的 CSV 行排程，而不是仅采用 workload 平均值。TLS/L1.5 的配置会在
GEMM/FDTD 上显著改变运行时间，所以不能假定 baseline 时间可代表全部 mode。

## 当前 P9B 4×64 公共参数：可直接用于排程的样本

结果目录为
`/workspace/worktrees/accel-sim-tls-cache/hw_run/tls-cache-p9-public-v1/matrix-d10fe92`。
以下均为 CFD 097K、4 chip × 64 SM/chip、32-cycle/hop、768 B/cycle ring 的自然
完成样本。wall/RSS 来自同一 job 的 `/usr/bin/time -v`，模拟器时间来自 raw log；
它们可用于安排资源，不是论文性能结论。

| placement | mode | 模拟器 wall | 宿主实际 wall | peak RSS | 状态 |
|---|---|---:|---:|---:|---|
| dynamic | baseline | 5:24 | 5:25.13 | 1.60 GiB | 自然完成、证据齐全 |
| dynamic | shared | 6:02 | 6:03.09 | 1.56 GiB | 自然完成、证据齐全 |
| dynamic | L1.5 | 5:46 | 5:47.15 | 1.58 GiB | 自然完成、证据齐全 |
| dynamic | TLS | 6:03 | 6:03.81 | 1.56 GiB | 自然完成、证据齐全 |
| frozen-hash | baseline | 1:03:53 | 1:03:54 | 1.50 GiB | 自然完成、证据齐全 |
| frozen-hash | shared | 39:21 | 39:22.28 | 1.50 GiB | 自然完成、证据齐全 |
| frozen-hash | L1.5 | 53:02 | 53:03.04 | 1.48 GiB | 自然完成、证据齐全 |
| frozen-hash | TLS | 1:04:49 | 1:04:50 | 1.51 GiB | 自然完成、证据齐全 |

CFD dynamic 的四 mode 串行累计为 **23:19**；若机器负载、I/O、内存余量相近，四条
同时启动的理论墙钟下界约为最长的一条 **6:04**，保守峰值 RSS 预算为
**4 × 1.60 GiB = 6.4 GiB**，另须预留系统和其它用户作业的余量。`frozen-hash` 不能
套用这个 6 分钟估计：四个 mode 的完成时间为约 **39--65 分钟**，说明地址放置会
显著放大模拟成本。它们的 peak RSS 仍集中在 1.48--1.51 GiB；本轮 CFD 的 8 个
样本现已通过 P9B public-v1 严格资格门。

## 已获得的直接资源样本

ST2D 与 SS 的自然完成记录现已可用于排程：ST2D 为 8:12:40、peak RSS 432 MiB；
SS kernel-only v4 为 3:43:41、peak RSS 444 MiB。P9B 4×64 TLS-CFD 的 10k-cycle
smoke 为 8.91 s、peak RSS 1.18 GiB；它只用于启动资源形状估计，不能外推完整
CFD 的时长或峰值内存。上节的完整 dynamic-CFD 样本现已提供直接观测到的约
1.5--1.6 GiB 量级。

### 当前 P9B GEMM 资源观测（8 条均已完成且通过严格子矩阵门）

2026-08-23 启动的 4×64 `polybench_gemm` dynamic 四 mode 已自然结束（退出状态均为
0）；下表的 wall/RSS 来自同一 job 的 `/usr/bin/time -v`。其 first kernel trace
约 1.11 GiB，峰值 RSS 比 CFD/SRAD 的约 1.5 GiB 大得多，故 GEMM 排程不能沿用小
workload 的内存预算。

| placement | mode | simulation cycles | host wall | peak RSS |
|---|---|---:|---:|---:|
| dynamic | baseline | 361,306 | 1:07:05 | 6.45 GiB |
| dynamic | shared | 494,586 | 1:19:26 | 6.43 GiB |
| dynamic | L1.5 | 343,432 | 1:06:12 | 6.46 GiB |
| dynamic | TLS | 328,287 | 1:08:49 | 6.52 GiB |

四条 GEMM 并行至少应按约 **26 GiB RSS 加余量** 预算。与之配对的 frozen-hash 四条
已经全部自然结束（退出状态均为 0）；下表补充 frozen-hash 对照。GEMM 的完整八条
样本已通过 `verify_p9_paper_public_matrix.sh ... polybench_gemm`，但仍只是完整 P9B
中的一个 workload，不能据此代替全矩阵结论。

| placement | mode | simulation cycles | host wall | peak RSS |
|---|---|---:|---:|---:|
| frozen-hash | baseline | 9,373,813 | 14:48:21 | 6.38 GiB |
| frozen-hash | shared | 9,433,913 | 13:14:29 | 6.34 GiB |
| frozen-hash | L1.5 | 9,243,639 | 21:45:13 | 6.35 GiB |
| frozen-hash | TLS | 9,389,284 | 15:43:16 | 6.36 GiB |

其 IPC 分别为 78.8629、78.3605、79.9735、78.7330；相对于对应 dynamic 的约
0.036--0.052 倍。这种跨 mode 都很强的退化首先归因于 frozen page map 的远端/竞争
路径（而非 host 阻塞或内存增长），最终解释仍要结合 P9 全矩阵的 page-map、ICL、ring
与服务层级统计。

## 历史资源观测（已完成，不进入原先进行中样本）

2026-08-23 初始只读检查时，以下两条 ICL 筛选 run 均仍在自然执行。表中 elapsed 是
`ps` 的宿主机运行时长，RSS 是检查瞬间值；二者只是排程观测，**不能替代**进程
退出后 `/usr/bin/time -v` 给出的完整 wall time/峰值 RSS。

| run | 输入与状态 | elapsed（检查时） | 瞬时 RSS | CPU |
|---|---|---:|---:|---:|
| ST2D | 原始 V100 trace；检查时已完成 2,845 / 4,000 kernels | 5.20 h | 412 MiB | 99.6% of one logical CPU |
| SS kernel-only v4 | 199 kernels、仅去掉 trace-list 最后的 post-kernel HtoD；检查时已完成 16 个、正在第 17 个 | 10.3 min | 444 MiB | 99.7% of one logical CPU |

SS 的原始 trace-list run 已在处理完所有 kernel 后、最后一个 post-kernel HtoD 的
cleanup 路径断言退出；它保留为失败证据，不计入时长分布。v4 是经清单哈希和
派生 manifest 约束的重试，不会覆盖原日志。当前两个 run 的资源输出分别位于：

- `hw_run/tls-cache-icl-screen/candidates-v1/st2d.baseline.dynamic.resources.txt`
- `hw_run/tls-cache-icl-screen/ss-retry-kernel-only-v4/ss.baseline.dynamic.resources.txt`

二者现已自然结束且校验通过；直接资源摘要已写入上节，完整清单仍应在 P9B
首批样本结束后统一重建，避免把进行中的行误作完成样本。

用于当前排程的粗略 ETA 也须与正式时长分开：ST2D 在上述快照约为 9.1 kernels/min，
若后续 kernel 保持同类成本，余下 1,155 个约需 **2.1 h**；这只是线性估计。SS 的
kernel 成本高度不均（第 17 个已显著长于前 16 个），在至少完成一个较长 kernel 前
不产生 ETA，也不以 16 个短 kernel 的均值推断总时长。

整理时宿主机有 512 个逻辑 CPU、约 66 GiB `MemAvailable`，但 swap 已满且系统
load average 约 113。当前主机另有用户的 Accel-Sim 长任务（其中一条 RSS 约 32 GiB）。
故在没有每类 trace 的完整 peak-RSS 样本前，不以“可见 CPU 空闲”直接放开大批量
并发；这既会污染耗时基线，也有内存抖动/换页风险。

## 后续排程规则

1. 每条新 job 必须保留其 `.resources.txt`（GNU time `-v`）和原始 `.out`；失败、
   中断、或没有自然收尾的日志不进入时长分布。
2. 先从每一类新 trace 的单条 run 获得峰值 RSS，再以保守预算确定并发：
   `min(可用物理核心的 70%, MemAvailable 的 60% / p95_RSS)`；还要为已存在的
   其它用户作业留余量。swap 非空时进一步降低并发。
3. 同一个 matched baseline/proposal 对应尽量在相近系统负载下运行；资源监测只服务
   于排程，不能改变配对实验的性能归因。
4. 可并行的是彼此独立的 candidate 或完整的 matched pair；不能在同一 raw log
   上重跑/覆盖，也不能把未完成的 V5 FDTD/P9B 自动补启动。

支持脚本位于
`/workspace/worktrees/accel-sim-tls-cache/experiments/tls_cache/`：
`run_icl_screen.sh`、`monitor_process_resources.sh`、
`summarize_run_timing.sh`。后者能从历史 raw log 自动建立同口径清单，并优先采用
直接 GNU-time 资源记录。
