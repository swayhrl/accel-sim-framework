# C2P-Cache 当前机制与实验审计

> 记录时间：2026-08-21（长时间 replay 仍在进行）。
>
> 本文是面向审阅的**中间审计**，不是论文复现结论。只有被标为“已完成并通过门禁”的数据才能用于判断趋势；正在运行、只完成部分 mode，或历史诊断数据都不能进入最终 Figure 10--14 聚合。

## 1. 当前要验证的命题与边界

目标是用 Accel-Sim/GPGPU-Sim C++ 模型复现 C2P-Cache 的主要机制和方向：

1. Snapshot Matrix 能在 L1 read miss 时筛出候选 peer，命中时避免一次原始 lower-L2 请求；
2. 它应在存在可共享数据、且 L2 延迟敏感的工作负载上带来 IPC/L2-access 的正向趋势；
3. 代价来自 Bloom/Snapshot 查询、候选 peer 的 tag/data-port 竞争、有限队列与 fallback，而不是被隐藏；
4. ATA、CCD、Ring 使用独立的 comparator 模型，不能因 64x1 端点适配而退化成单 L1 比较；
5. 全部结论必须同时通过时序、事务和统计不变量，不能只凭 IPC 数字。

本轮没有尝试逐周期复刻作者未公开的网络、地址 hash 或 trace。它是**机制与方向性复现**；PPA、功耗、Figure 16--21 参数扫掠不属于本阶段关账条件。

## 2. 可执行模型：实现位置与事务路径

| 部分 | 当前实现 | 审计结论 |
| --- | --- | --- |
| 入口挂接 | `src/gpgpu-sim/gpu-cache.cc`：L1 global read miss 调用 `c2p_cache::accept_miss()`；L1 fill/flush 调用 `on_l1_fill()`/`on_l1_flush()`。 | C2P 只处理 non-atomic、non-write 的 `GLOBAL_ACC_R` miss；其他访问保持原 cache 路径。 |
| 核心状态机 | `src/gpgpu-sim/c2p-cache.{h,cc}`。每周期由 `gpgpu_sim::cycle()` 调用。 | 事务有候选匹配、目标端 probe FIFO、probe、return、fallback 等显式状态，不是一个零延迟查表 shortcut。 |
| Snapshot Matrix | 64 bank；每 bank 16 tag-mask rows + 默认 64 BF rows；四编码（tag mask + 3 BF hash）；4 copy。 | `query_rows()` 选择地址行；所有行 bit-and 得到候选。`snapshot_bf_rows_per_bank` 已参数化，避免非默认 m/k 点仍用固定 bank row。 |
| 更新与陈旧性 | L1 fill 入 update queue，由 128 BF engines、2-cycle encoder 和 128B/cycle transport 服务；flush 清掉列并取消延迟 update；continuous rebuild（interval=0）逐列重建。 | 既模拟 update/backpressure，也阻止 flush 后迟到的 update 重建 stale bit。 |
| C2P 候选与 probe | Snapshot 完成后按 logical eight-SM cluster 距离排序；每目标 L1 有深度 32 的 probe FIFO；正常 target data-port 使用 7-cycle tag + 2-cycle return。 | target port 繁忙时排队，而不是把 peer 当成无限端口；满 FIFO/无进展 32 cycle 时 fallback 至原 L2。 |
| 实际命中 | probe 时重新调用目标 L1 `c2p_probe()`，成功后通过 requester fill port 回填，**不**下发 lower request。 | `remote_hits == l2_requests_avoided` 是逐 run 强制门禁，直接刻画 redundant-L2 reduction。 |
| Oracle | 接受 miss 时扫描 exact peer，但不接管事务。 | Oracle 仅测机会；它的 cycle 必须与 baseline 完全相同。 |
| Ideal | exact peer candidate discovery，保留 peer data-port/probe/return 时序。 | 用于隔离 Snapshot 候选质量，不被定义为 IPC 的数学上界：它可能发出更多 peer probe，反而比有限 C2P 产生更大争用。 |
| ATA | logical eight-SM group 内 exact aggregate tag，7-cycle tag、14-cycle line、每 cluster 每 cycle 4 次 issue。 | group size 由 `c2p_cache_comparator_cluster_size=8` 显式控制。 |
| CCD | per logical group 的 weak-taken two-bit counter；predict taken 后向八个 peer broadcast，再以 exact tag 选数据。 | 同时输出 CCD TP/FN/FP/TN，避免仅用 IPC 推断 predictor 品质。 |
| Ring | chip-wide serialized discovery；2-cycle hop、7-cycle tag。 | 串行注入与 hop 延迟均显式建模；其性能不能简单由 remote-hit 数量解释。 |

关键配置在 `configs/c2p-cache/c2p.config`，mode overlay 在
`configs/c2p-cache/{oracle,ideal,ata,ccd,ring}.config`。runner 对每一个
non-baseline mode 先加载完整 `c2p.config`，再仅覆盖 mode 差异；ATA/CCD/Ring
的 Table-1 latency/throughput 也在各 overlay 显式写出。这避免比较点依赖
C++ constructor 默认值；分析器将历史 run 的隐式默认规范化为同一 effective
configuration，仍保留 raw config hash 供逐字节追溯。

### 与论文机制逐项对照

下表按论文 §4.4--4.6 与 §3.2 的语义审查当前代码，不以 IPC 结果倒推
“实现正确”。

| 论文要求 | 代码中的证据 | 结论 / 仍保留的模型边界 |
| --- | --- | --- |
| 每个 Snapshot column 从一个 L1 的 valid tags 周期性重建，先 clear 后 OR；L2 fill 走同一 update path。 | `begin_next_rebuild()`、`issue_update()`、`on_l1_fill()`。 | 符合；replace/evict 通过随后 rebuild 修正，而非在 L1 hit path 维护可删 BF。 |
| miss-side query 比 background update 有更高 BF-engine 优先级。 | `cycle()` 先 `issue_query_encodes()`，再将余下 engine 交给 `issue_update()`。 | 符合；query/update queue overflow 均有独立 counter。 |
| 默认 Snapshot 为 64 bank、每 bank 四 physical copy；一个 miss 激活 tag-mask + 三 BF encoding。 | 64 bank `m_snapshot`、`m_bank_copy_used[bank][copy]`、默认 64 BF + 16 tag-mask rows 与四个 `query_rows()`。 | 符合；m/k 非默认点已用 parameterized bank index，旧 fixed-80-row 结果被拒绝。 |
| Result bitmap 产生 chip-wide candidate，按物理距离串行 confirmation；candidate L1 正常 tag/data array 可以同本地访问竞争。 | `ordered_candidates()` 的 logical-cluster distance 排序；`c2p_reserve_probe_port()` 和 target FIFO。 | 语义符合；真实 NoC 几何被 64x1 endpoint + explicit latency 近似，SID 在同 logical distance 内的顺序不是作者未公开的物理路由。 |
| busy remote confirmation 不无限等待，abort remaining candidates，走原 L2/fill path。 | `probe_timeout`、`WAIT_FALLBACK`、`c2p_send_lower()`；remote hit 走 `c2p_fill()`。 | 符合 fallback/ownership；32-cycle timeout 和每-target 32-entry FIFO 是公开论文未指定的**显式模型参数**，其影响由 queue sensitivity 单独报告。 |
| CCD 为每 cluster 2-bit counter，预测 taken 才 broadcast；ATA 是 cluster aggregate tag；Ring incremental/serialized traversal。 | `m_ccd_counters`、ATA issue width/tag latency、`m_ring_next_issue_cycle`。 | 符合三种代表性设计的核心差异；ATA/Ring 的完整物理 NoC 与 aggregate-array microarchitecture 仍是 cycle-model abstraction。 |

因此：当前 C2P path 的 correctness 不依赖 Snapshot 精确性；false
positive/negative、queue contention 和 stale column 只改变是否/何时 fallback，不能产生错误数据。最终性能差异必须先在这些已记录的近似项、local trace 行为和 L1/L2 geometry 中解释，不能把未公开细节伪装成已复刻硬件。

## 3. 论文配置与明确的模拟器适配

`configs/c2p-cache/paper-table.config` 是唯一的主表配置。已固定：64 SM、1.41GHz、GTO/4 scheduler、64KiB 32-way 128B L1（20 cycle）、20 memory partition、128-set/16-way 128B L2（200-cycle ROP path）。

以下不是“悄悄等价”，而是已记录的必要适配：

* 论文 L1 的 `4 sets x 32 ways x 128B = 16KiB` 与标称 64KiB 矛盾；本模型保留容量、way 和 line size，因此为 `16 sets x 32 ways`。
* Accel-Sim IPOLY 不能表示论文的 20 partition / 128 L2 set hash；使用确定性的 consecutive partition / linear L2 set mapping。论文未给出 hash，故这不能宣称与作者 bit-exact。
* 字面 `8 cluster x 8 SM` 会触发 GPGPU-Sim reply/ROP 聚合死锁。改为 `64 cluster x 1 SM` endpoint 后 forward progress 正常；C2P、ATA、CCD 的 logical peer group 仍明确为 8 SM，C2P 仍搜索 64 个 L1。
* `16x32` L1 暴露了 inherited clean-first victim 选择的 set-local forward-progress bug；修正后 SGEMM 完成，并与恢复旧 `4x64` 几何的隔离对照 cycle 相同。这是 cache forward-progress 修正，不是为性能结果换几何。

详细证据和旧诊断在 [paper_reproduction_status.md](paper_reproduction_status.md)。

## 4. 实验矩阵、产物与当前完成度

16 个完整兼容 trace 在 `configs/c2p-cache/paper16_workloads.tsv`：Rodinia 6、Parboil 4、PolyBench 6。每个主点需要：

* 七 mode：`baseline/oracle/ideal/c2p/ata/ccd/ring`；
* 独立 50-cycle-L2 baseline（只把 200 改成 50），以 `oracle redundancy >= 0.30` 和 `IPC50/IPC200 >= 1.10` 得到本地 R0/R1、S0/S1；
* C2P `m2048-k2/m3072-k3/m5120-k4/m9216-k5` 四点，用于 Figure 13；
* CCD replay，用同一 resolved config 收集 CCD TP/FN/FP/TN。

主根为：

```text
hw_run/c2p-paper16-v7-20260821
hw_run/c2p-paper16-l2-50-v7-20260821
hw_run/c2p-paper16-ccd-metrics-v1-20260821
hw_run/c2p-paper16-fp-sweep-v1-20260821
```

为缩短串行尾部，已启动独立补充根；分析器只在主根缺少完整 `summary.txt` 时回填，主根优先：

```text
hw_run/c2p-paper16-v7-parallel-v2-20260821
hw_run/c2p-paper16-v7-parallel-v3-20260821
hw_run/c2p-paper16-l2-50-v7-parallel-v2-20260821
hw_run/c2p-paper16-ccd-metrics-parallel-v2-20260821
hw_run/c2p-paper16-fp-sweep-parallel-v2-20260821
```

当前覆盖审计结论：所有 16x7 主 mode、16 个 L2-50 点、16 个 CCD 点和 16x4 个 m/k 点均为“已完成”或“正在运行”；不存在未排程的必需点。完整七 mode + L2-50 + CCD evidence 已完成的工作负载是：Btree、DWT2D、Gaussian、Hotspot1、LUD、NN、SGEMM。其余九个仍有至少一个完整 trace 在运行，因而**尚不能参与 group aggregate 或最终图**。

各 run 目录保留 copied binary、resolved config、trace/config/simulator/runtime hash、full `run.out` 和 `summary.txt`。`scripts/analyze_c2p_paper16.py` 也检查 mode contract、effective config、provenance、oracle timing 和 remote-hit/L2-avoidance 不变量。

### 二进制版本与默认点等价性

长批次在代码演进期间使用了多个、均已记录在 `provenance.txt` 的
GPGPU-Sim binary revision。这里不能仅因 commit 不同就混合结论，也不能
为形式统一而盲目重跑已经可证明等价的默认点：`5ad465ec -> 04962526`
的功能改动是 Figure-13 非默认 m/k 的参数化、bank-index 修正和 CCD
分类计数；默认 `m5120-k4`（5,120 rows、4 encodings）保持原布局与路径。

`scripts/check_c2p_default_equivalence.py` 将主实验的默认 C2P run 和由
`04962526` 产生的 `fp-sweep/m5120-k4` 逐字段比对。2026-08-21 的实时
检查已覆盖 Btree、DWT2D、Gaussian、Hotspot1、LUD、NN、SGEMM：每一项的
cycle、L2 access、candidate、remote-hit、fallback 和 Snapshot 分类计数均
bit-exact（新加、且为零的 CCD counter 除外）。因此这七个已完成的默认
C2P 点可以作为同一机制版本的证据；尚未配对的九项仍须等待当前 binary
结果落盘。Figure 13 的非默认 m/k 点则**只**接受 `04962526` 或之后的
parameterized implementation，绝不使用旧 binary 的结果。

## 5. 已完成点的实测行为（仅局部证据）

下表来自当前 v7 主根；IPC 为 `baseline_cycles/mode_cycles`，大于 1 更快。它用于发现方向和异常，**不是 16-workload aggregate**。

| workload | C2P IPC | C2P L2 access / base | C2P remote hit | ATA IPC | CCD IPC | Ring IPC | 初步解释 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Btree | 1.0258 | 0.8862 | 161,628 | 0.9868 | 0.9967 | 1.0335 | 有强冗余；有限 C2P 少于 ideal 的 remote hit，但较低 probe 压力可使 IPC 更好。 |
| DWT2D | 1.0347 | 0.9717 | 46,330 | 0.9860 | 0.9962 | 0.9189 | C2P 正收益；Ring 代价明显。 |
| Gaussian s=256 | 0.9998 | 0.9965 | 15,355 | 0.9987 | 0.9999 | 0.9281 | 机会较低且 L2 不敏感，接近中性是合理预期。 |
| Hotspot1 | 1.0189 | 0.9086 | 80,181 | 1.0009 | 0.9987 | 1.0011 | 明显 L2 reduction，C2P 正收益。 |
| LUD | 1.0038 | 0.9362 | 87,882 | 1.0019 | 0.9996 | 0.9483 | 机会存在但延迟敏感性低，收益小。 |
| NN | 0.9975 | 1.0000 | 0 | 0.9997 | 1.0001 | 0.9935 | 负控制；没有凭空 remote hit，有限查询只有很小开销。 |
| SGEMM | 0.9871 | 0.8046 | 271,719 | 1.0005 | 0.9965 | 0.7420 | L2 access 大幅减少但 IPC 下降，是当前最重要的待解释 workload。 |

所有上述 completed mode 的 `oracle_cycles == baseline_cycles`，且每个 nonzero `remote_hits == l2_requests_avoided`。因此它们至少证明：机会测量没有改写 baseline timing，remote return 确实替代一次 lower request，而非双重完成。

### 已经解释、且不应误判为 Bloom 错误的现象

**Btree 机会保留不足。** canonical C2P（target FIFO 32 / timeout 32）有 161,628 remote hits、438,570 target timeout fallback 和 132,808 requester-queue bypass。只增大 requester FIFO 到 1,024/4,096 只使 cycle 改善 0.19%；同时无限放宽 target 等待会将 remote hits 提至 576,589，却让运行慢 47.8%。原因是 peer probe 会长期占有原 miss，而 baseline L2 可在更短路径完成。

这符合论文“target L1 正常 tag/data array 竞争 + 有界 abort/fallback”的机制要求。因此默认有限队列被保留，不能为了获得更大 remote-hit 数而采用无限等待。该诊断由 `scripts/analyze_c2p_queue_sensitivity.py --strict` 检查。

**Ideal 不必逐 workload 支配 finite C2P IPC。** Ideal 使用 exact candidates，可能检查更多目标；C2P 会 pruning 掉一部分候选。因此在相同真实 target-port 争用模型下，C2P 可能以更少的 remote hit 获得更短临界路径。比较它们时应同时看 `remote_hits`、`peer_l1_accesses`、timeout 与 Figure-14 peer-access 分布，而非把 ideal 误作无代价上界。

## 6. 当前不能解释为“正确”的红灯

以下是必须在最终 16-workload aggregate 里复核的项目；它们不是被掩盖的例外：

1. **SGEMM：L2 降 19.54% 但 C2P IPC -1.29%。** 它的独立 L2 sensitivity 为 `429816/396350 = 1.084`，故本地是 R1S0（低于 1.10 的 S1 门槛），本就不应套用论文 R1S1 的 23.5% 平均收益。更重要的是机制计数给出了可审计的 slowdown 原因链：2,194,621 个 C2P query 中 741,827 个（33.8%）target-timeout fallback，平均 4.054 candidates/query，Snapshot FP 为 14.8%，1,694,593 次 peer L1 probe 最终只完成 271,719 次 remote hit；其 fallback probe P95/P99 分别为 4/10 个 peer。相对地，ideal 为 423,904 cycle、348,129 remote hit、888,305 probe，说明 Snapshot 候选/port contention 使 C2P 多发大量 probe 且丢失远端返回。这是**量化的模型行为解释**，不是以 L2-access 数字掩盖 slowdown；最终仍须检查其余 R1S0/R1S1 workload 是否同样出现，若普遍存在再审查 timeout/FIFO 模型而不是对 SGEMM 单点调参。
2. **旧 CCD 训练语义错误，已隔离并重放。** 旧模型只在预测 taken 的 broadcast 后更新 counter；第一次 no-share 将 weak-taken counter 降到 not-taken 后，之后的 false negative 永远不能恢复训练。这不是可接受的 CCD 负控制。GPGPU-Sim `f5eff2cd` 改为每个请求按 exact tag-time in-cluster outcome 训练 two-bit counter；独立 DWT2D 验证得到 22,062 TP、16,339 remote hit，而旧点为零。所有旧 CCD 结果已从 closeout 排除，fresh root `c2p-paper16-ccd-refresh-v2-20260821` 的 16 项重放是最终唯一可接受证据。
3. **Ring 的 Btree IPC 高于 C2P，而 DWT2D/LUD/SGEMM 显著变慢。** 该 workload 依赖性可由 serialized issue、nearest hit hop、减少的 probe 数共同导致；仍须检查 Ring 的 L2 access、hop/probe 分布和网络时序。不能在 aggregate 前声称已匹配论文 Ring 开销。
4. **本地 R/S 分类与论文图的 workload 分组不同。** 例如 Gaussian 本地是 R0S0 而论文参考标签为 R1S0；这是 trace input/规模、mapping 和模型适配的直接信号。最终图会同时保留 paper reference group 和 local measured group，绝不强行 relabel。
5. **未完成任务没有结果资格。** 当前运行中的 CUTCP、Stencil、PolyBench 等可能改变任何 group aggregate 和均值；在 strict gate 通过前，不能给出“与论文一致/不一致”的结论。

## 7. 已实施的正确性门禁

| 门禁 | 覆盖的错误 | 当前状态 |
| --- | --- | --- |
| baseline/oracle cycle 相等 | oracle 意外改变排队/时序 | 已完成 run 通过；最终 strict。 |
| remote hit = avoided L2 request | remote return 与 lower request 双重完成/漏完成 | 已完成 run 通过；最终 strict。 |
| 每 mode resolved-config contract | 模式 flag 互相污染、ATA/CCD group size 退化 | 已完成 run 通过；最终 strict。 |
| primary/supplement provenance | 并行补跑混入不同 binary/config | effective config、binary family、source path 被记录。 |
| m/k resolved shape | 目录名与真实 Bloom rows/hash 不一致 | 通过后才进入 Figure 13；曾实际发现并修复 bank-index bug。 |
| default m5120 preservation | 参数化 refactor 改坏主实验 | `check_c2p_default_equivalence.py` 已对七个已配对 workload 的完整公共 summary 字段逐项 bit-exact；新增 CCD fields 为零。 |
| TP/FN/FP/TN 双时间点 | 把等待中的 L1 fill/evict 误称 Bloom 精度错误 | 同时记录 accept-time paper classification 与 query-time diagnosis。 |
| Figure-14 histogram | 只报均值而掩盖长 probe tail | 完整 hit/fallback count + P90/P95/P99/MAX 均保留。 |
| CCD all-outcome training | counter 在首次 not-taken 后永久失活 | `f5eff2cd` 后 fresh 16-item CCD root 独占 closeout；DWT2D 非零 TP/hit 定向验证通过。 |

## 8. 最终关账的唯一入口

待所有 `summary.txt` 落盘后执行：

```bash
PYTHONPATH=/tmp/c2p-matplotlib-py311 \
scripts/finalize_c2p_paper16.sh \
  --results-root hw_run/c2p-paper16-v7-20260821 \
  --supplemental-results-root hw_run/c2p-paper16-v7-parallel-v2-20260821 \
  --supplemental-results-root hw_run/c2p-paper16-v7-parallel-v3-20260821 \
  --l2-fast-root hw_run/c2p-paper16-l2-50-v7-20260821 \
  --supplemental-l2-fast-root hw_run/c2p-paper16-l2-50-v7-parallel-v2-20260821 \
  --ccd-metrics-root hw_run/c2p-paper16-ccd-refresh-v2-20260821 \
  --ccd-mode-root hw_run/c2p-paper16-ccd-refresh-v2-20260821 \
  --sweep-root hw_run/c2p-paper16-fp-sweep-v1-20260821 \
  --supplemental-sweep-root hw_run/c2p-paper16-fp-sweep-parallel-v2-20260821 \
  --queue-sensitivity-root hw_run/c2p-btree-query-sensitivity-v1-20260821 \
  --analysis-dir hw_run/c2p-paper16-analysis-final-v7-20260821 \
  --figures-dir hw_run/c2p-paper16-figures-final-v7-20260821 \
  --report hw_run/c2p-paper16-report-final-v7-20260821.md \
  --python /scratch/root/oss-eda/oss-cad-suite/py3bin/python3
```

该入口会依次执行七 mode/L2-50/CCD strict analysis、default `m5120-k4`
跨 binary 等价检查、m/k strict analysis、queue strict diagnosis、Figure 10--14
strict plotting 和最终 Markdown report。任一缺 run、配置不一致、默认点不等价、oracle
timing 改变、remote/L2 不一致、缺 CCD counter 或 m/k shape 不匹配都会失败；失败就不能产生最终“论文复现完成”的声明。

`scripts/watch_c2p_paper16_closeout.sh --interval 120` 是本轮长 replay 的
无侵入守护入口：它只轮询 `summary.txt` 是否完整，绝不启动/停止模拟；所有
16x7（其中 CCD 必须来自 fresh root）、16 个 L2-50、16x4 个 m/k 都已落盘后才调用上述唯一 strict
入口一次。strict failure 会保留日志并退出，不会通过重复运行掩盖配置或机制错误。

## 9. 缺失论文 workload 的记录

以下论文点尚无可验证的兼容 trace，明确保留为缺失而非用相似 workload 代替：

* ISPASS：BFS、LIB、LPS、RAY；
* Pannotia：color_max、fw_block、mis、pagerank。

它们会被最终 report 列出，但不阻塞本阶段定义的“现有 16 条兼容 trace 上的方向性复现”。
