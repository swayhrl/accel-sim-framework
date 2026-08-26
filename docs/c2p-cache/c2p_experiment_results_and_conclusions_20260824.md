# C2P-Cache 复现、诊断与 C2P+ 实验结果总报告

> 更新时间：2026-08-24
> 状态：论文主性能实验的方向性复现已完成；C2P+ 端口解耦、固定确认深度、PC/地址拓扑自适应确认策略均已完成可审计实验。PPA、功耗和 Figure 16--21 的广泛参数敏感性不在本阶段范围内。

## 1. 摘要结论

本轮实验得到五个层次清楚、且相互兼容的结论。

1. **C2P-Cache 的核心机制和论文主趋势已经可信复现。** 在本地 16 个完整兼容 trace 上，默认 C2P 相对无 C2P baseline 的 IPC 几何平均为 `1.018953`，L2 access 几何平均为 `0.898572`；即 IPC 提升约 **1.90%**、L2 access 减少约 **10.14%**。本地 R1S1 组 IPC 均值为 `1.218`，与论文报告的 `+23.5%` 同方向且量级接近；本地 R0S1 为 `0.954`，比论文约 `-2%` 的开销更大，但仍验证了“无冗余、却对 L2 敏感时共享协议可能带来负收益”的机制。
2. **本地 C2P 的 L2 reduction 方向正确，但弱于论文。** 本地 R1S0/R1S1 的 normalized L2 access 为 `0.831/0.840`，论文参考值为 `0.534/0.698`。差距与本地 trace/input、R/S 分组变化、地址映射以及显式 queue/target-port 模型有关，不能简单归因于 Bloom filter。
3. **已定位一个显著的实现/模型瓶颈：remote probe 与目标 L1 data port/FIFO 竞争。** 将 remote tag probe 从目标 L1 data port 解耦后，Btree、BFS、SGEMM、2DConvolution 分别较 default C2P 减少 `1.38%/4.64%/1.31%/1.23%` 周期；SGEMM 基本恢复 baseline。2DConvolution 和 LPS 仍有残余开销，说明端口竞争不是全部问题。
4. **不存在一个全局最优的固定确认深度。** Btree 需要确认到 4 次，2DConvolution 最适合 1 次，LPS 接近 exhaustive/4 次。因而后续采用了“首 probe 必发、最多 4 次、按请求学习是否继续”的小型自适应策略。
5. **最终同容量自适应对照显示地址拓扑特征在 canonical 16 上更好，但并不普适。** 相对同二进制的 four-probe C2P+ control：PC-hash 在 canonical 16 上 IPC 几何平均 `1.005890`，AddrTopo 为 `1.016560`；在 V100 extension 8 上则分别为 `0.994396/0.992614`。AddrTopo 的 canonical 收益明显受 ATAX 驱动，BICG、Btree、BFS、MIS 等仍是反例。因此当前结论是“**地址拓扑是更适合 L2/RTL 的有效特征候选**”，而不是“已经得到跨 workload 稳定增益的最终策略”。

## 2. 结果可比性与实验谱系

实验中存在三种不同的控制点，必须分开解读。

| 层次 | 严格控制点 | 可直接比较的实验 | 不能直接混入的结果 |
|---|---|---|---|
| 论文主复现 | C2P disabled baseline | baseline/oracle/ideal/default C2P/ATA/CCD/RING；16 个 canonical trace | C2P+、adaptive 策略 |
| C2P+ 协议诊断 | 同 workload 的 default C2P | separate-target-tag-port C2P+、固定 budget1/2/4、C2P+ Ideal | 论文 Figure 10--14 聚合 |
| 最终确认策略矩阵 | separate-target-tag-port + four-probe bounded exhaustive control | control/PC-hash/AddrTopo，24 个 workload 的同二进制三路配对 | 旧 v1/v2、不匹配容量或 unbounded control 的实验 |

因此：

- 论文主结果回答“C2P 相对普通 L2 是否有效”；
- C2P+ 结果回答“默认模型中哪些协议资源造成损失”；
- 最终矩阵回答“在已经解耦 target tag port、且统一四次硬上限后，哪种确认策略更好”。

跨 campaign 将当前 control/PC/Addr 与旧 paper16 baseline 对齐，只能作演进参考。其 canonical 16 的指示性 IPC 几何平均分别约为 `1.0250/1.0311/1.0420`；这不是同二进制 matched comparison，正式结论仍以各自层内配对为准。

## 3. 共同模型、配置与已知适配

论文主实验使用统一 `paper-table.config`：

- 64 cluster × 1 SM，逻辑共享组仍为 8 SM；
- 64 KiB L1，16 sets × 32 ways × 128 B，4 banks，20-cycle L1；
- 20 memory channels × 2 subpartitions；
- L2 为 128 sets × 16 ways × 128 B，200-cycle L2 path；
- GTO scheduler；
- Snapshot 默认 64 banks、4 copies、128 BF engines；
- remote tag latency 7 cycles，probe timeout 32，target probe queue depth 32。

与论文描述相比有三项明确适配：

1. 论文同时写了 64 KiB、32-way、128 B line 和 4 sets，这四者容量不一致；本地保留容量、way、line size，采用 16 sets。
2. Accel-Sim 的 IPOLY 无法直接表示论文的 20 partition/128 L2 set hash；使用确定性的 partition/set mapping。论文未公开具体 hash，因此不声称地址级 bit-exact。
3. 字面 `8 cluster × 8 SM` 会触发原模拟器 reply/ROP 聚合死锁；改成 64 个单 SM endpoint，同时在 C2P/ATA/CCD 中保留逻辑 8-SM grouping。

这是一份机制与趋势复现，不是作者未公开网络、地址 hash、trace 和物理布局的逐周期复刻。

## 4. 论文主实验：16 个 canonical workload

### 4.1 七种模式的总体结果

| 模式 | IPC 几何平均 / baseline | L2 access 几何平均 / baseline | Remote hits | 解释 |
|---|---:|---:|---:|---|
| baseline | 1.000000 | 1.000000 | 0 | 普通 L2 路径 |
| oracle | 1.000000 | 1.000000 | 0 | 只观察 accept-time peer opportunity，必须保持 timing 不变 |
| ideal | 1.032516 | 0.884628 | 11,547,622 | exact peer candidate discovery，仍保留端口/probe/return 时序 |
| default C2P | 1.018953 | 0.898572 | 9,965,048 | Snapshot + 串行 remote confirmation |
| ATA | 0.984410 | 0.958626 | 5,181,763 | 8-SM aggregate tag comparator |
| CCD | 1.007751 | 0.974820 | 2,480,157 | cluster predictor + conditional broadcast |
| RING | 0.227161 | 0.906219 | 6,373,529 | 显式 serialized ring comparator；方向符合高协议代价，但绝对 slowdown 受模型抽象影响很大 |

默认 C2P 实现了约 `86%` 的 Ideal realized remote hits，同时 IPC 只获得 Ideal 收益的一部分。这说明 Snapshot 筛选有效，但 false candidates、候选顺序、target-port/FIFO 竞争和 fallback 会消耗机会。

### 4.2 本地 R/S 分类与论文趋势

本地分类使用两个独立测量：oracle redundancy `>=0.30` 判为 R1；`IPC(L2=50)/IPC(L2=200) >=1.10` 判为 S1。

| 本地组 | Workload | C2P IPC 均值 | C2P L2 access 均值 | 论文/机制预期 | 结论 |
|---|---|---:|---:|---|---|
| R0S0 | DWT2D、Gaussian、LUD、NN、MRI-Q | 1.007 | 0.981 | 无明显机会、低敏感，接近中性 | 一致 |
| R1S0 | Hotspot、CUTCP、SGEMM、2D、3mm、GEMM | 1.007 | 0.831 | 可减少 L2，但 IPC 收益有限 | 一致；SGEMM/2D 暴露协议开销 |
| R0S1 | ATAX、BICG、GESUMMV | 0.954 | 0.997 | 无共享机会却支付协议代价 | 一致，开销比论文略大 |
| R1S1 | Btree、Stencil | 1.218 | 0.840 | 核心获益组 | 与论文 `+23.5%` 接近 |

本地分组与论文并非逐项一致：Gaussian、LUD、SGEMM、2DConvolution、3mm、GEMM 的本地 R/S 落点不同。这是实际跑过 oracle 和独立 L2=50 baseline 后得到的结果，不是人为重标。它也解释了为何不能把论文的组均值直接套到单个本地 workload。

### 4.3 与论文一致和不一致的地方

一致：

- R1S1 是核心收益组；本地 `+21.8%`，论文 `+23.5%`。
- R0S1 会因额外共享协议开销退化；本地约 `-4.6%`，论文约 `-2%`。
- R1S0/R1S1 都能减少 L2 access。
- ATA/RING 在缺少共享机会的 workload 上更容易付出高代价。

不完全一致：

- 本地 R1S0/R1S1 L2 access 只降到 `0.831/0.840`，弱于论文 `0.534/0.698`。
- 本地 workload 的 R/S 分类和论文图不完全相同，主要由 trace/input 规模、地址映射和模型适配共同造成。
- RING 的 IPC 几何平均 `0.227` 远低于论文量级。已定位为本地 comparator 的全局串行注入、head blocking 和显式 backpressure 模型，而不是 GPGPU-Sim 原始 cache 错误；RING 仅用于验证趋势，不作为需要继续精调的主设计。

### 4.4 Figure 10--14 对应产物

论文风格的 Figure 10--14 均已生成 PDF/SVG/PNG：

- Figure 10：分组 normalized IPC；
- Figure 11：分组 normalized L2 access；
- Figure 12：C2P/CCD 独立 TP/FN/FP/TN；
- Figure 13：`m2048-k2/m3072-k3/m5120-k4/m9216-k5` 实测 FP/IPC sweep；
- Figure 14：remote-hit 与 miss/fallback 的动态 peer-access distribution。

图和原始表位于：

- `/workspace/worktrees/accel-sim-c2p-cache/hw_run/c2p-paper16-analysis-final-v7-20260821/`
- `/workspace/worktrees/accel-sim-c2p-cache/hw_run/c2p-paper16-report-final-v7-20260821.md`

## 5. C2P+：target-tag port 解耦诊断

默认模型中 remote confirmation 会竞争目标 L1 的 data port，并可能在 target FIFO 中排队。C2P+ 提供独立、每目标每周期可启动一次、7-cycle latency 的 target-tag path；其目的不是声称论文一定如此实现，而是隔离端口竞争这一因果因素。

| Workload | Default C2P cycles | C2P+ cycles | 周期变化 | Default/C2P+ remote hits | Default/C2P+ target timeout | 结论 |
|---|---:|---:|---:|---:|---:|---|
| Btree | 229,052 | 225,882 | -1.384% | 161,628 / 562,391 | 438,570 / 814 | 高候选压力点显著改善 |
| BFS | 186,246 | 177,598 | -4.643% | 87,877 / 203,447 | 129,772 / 4,493 | 不是 Btree 单点特例 |
| LPS | 102,272 | 100,103 | -2.121% | 62,919 / 73,931 | 13,723 / 0 | 仍比 99,393-cycle baseline 慢 0.714% |
| SGEMM | 435,411 | 429,701 | -1.311% | 271,719 / 815,770 | 741,827 / 1,302 | 基本恢复 429,816-cycle baseline |
| 2DConvolution | 700,017 | 691,389 | -1.233% | 556,059 / 1,330,486 | 1,610,893 / 124 | 仅解释约 25.2% 的 baseline gap |
| NN | 7,224 | 7,224 | 0 | 0 / 0 | 0 / 0 | 严格负控制，无机会时完全无行为变化 |

核心判断：

- SGEMM 的“L2 减少但 IPC 下降”主要是目标端口/FIFO 竞争，C2P+ 后已基本消失。
- 2DConvolution 在端口问题消除后仍明显慢于 baseline，残余来自 Snapshot/query/probe/return 以及无效串行确认本身。
- LPS 捕获了大部分可实现 remote hit 仍略慢，证明“remote hit 更多”不等价于“IPC 一定更高”。

## 6. 固定确认深度：不存在统一最优 budget

`budgetN` 表示前 N 个 exact candidate 均失败后回退 L2；不是并行 race L2。

| Workload | C2P+ exhaustive | budget1 | budget2 | budget4 | C2P+ Ideal | 最佳方向 |
|---|---:|---:|---:|---:|---:|---|
| LPS cycles | 100,103 | 100,735 | 100,933 | 100,070 | 99,316 | 4/exhaustive |
| 2DConvolution cycles | 691,389 | 673,876 | 676,881 | 682,399 | 672,326 | 1 |
| Btree cycles | 225,882 | 229,229 | 227,761 | 225,084 | 224,879 | 4 |

2DConvolution 的 budget1 虽然增加 L2 access，却减少了大量无效串行 probe，因此更快；Btree 的 useful peer 常出现在更后面，budget1/2 会过早损失机会。这直接否定了“所有请求统一早停”的方案。

## 7. 自适应确认策略的演进

### 7.1 Stage 1--4

| 阶段 | 机制 | 得到的结论 |
|---|---|---|
| 观察阶段 | 不改时序，记录 probe ordinal、PC hash、lower-ready、target credit | PC bucket 存在差异；简单 queue-pressure 信号不足以解释所有结果 |
| PC-hash × ordinal | 3-bit 饱和计数器，首 probe 必发，最多 4 次，1/64 exploration | 能剪掉 2D/SGEMM tail，但在 BFS/Btree 过早停止 |
| 加 candidate-count bin | 记录 `1--2/3--4/5--8/9+`，并观测 stop 后首个 exact peer 距离 | 深候选集不能只按“下一次 probe 命中率”判断；四次范围内仍可能有高累计机会 |
| bin-aware package | 第一次失败后一次性决定是否连续确认到上限 | 避免每次失败都用同一阈值重复早停；成为最终 PC/Addr 同容量对照的基础 |

最终策略统一为：

- 首 probe 强制发出；
- 初始候选数分为四个 bin；
- 一个 `64 feature × 4 bin × 3 bit = 768 bit` 表；
- 初值 4、阈值 4、remote hit `+2`、完整 no-hit package `-1`，0--7 饱和；
- 每 64 次低分机会保留一次 exploration；
- 最多确认 4 次；
- PC 和 AddrTopo 除 feature hash 外容量、更新规则、探索规则和硬上限完全一致。

### 7.2 三个反例的定向统计

Btree/BFS/LPS 中所有 learned stop 都立即进入 lower path：PC 共 `333,988` 个、AddrTopo 共 `483,340` 个样本均处于 zero-existing-fallback-pressure 桶，stop-to-lower-send 为 0。因此这些反例不是 fallback queue 排队造成，而是早停后损失后续 exact peer，或额外 probe 本身不值。

`smallfull`（候选数不超过 4 时全部扫完）相对普通 PC：

| Workload | cycles | L2 access | remote hits | 判断 |
|---|---:|---:|---:|---|
| Btree | -0.66% | -2.68% | +21,586 | 短列表继续确认有价值 |
| BFS | +0.05% | +0.21% | -2,439 | 额外确认不能恢复有效 peer |
| LPS | -0.43% | -3.80% | +13,388 | 存在短列表确认机会 |

仅把表初值调为 6/7 没有稳定跨 workload 收益，说明“更保守地早停”不能替代更好的特征或 request criticality 信号。`smallfull` 只是诊断候选，未混入最终矩阵。

## 8. 最终 24 项同容量 PC-hash vs AddrTopo 矩阵

### 8.1 资格与实现

矩阵共 72 次 replay：16 canonical + 8 V100 extension，每项包含 control/PC/Addr 三路。同一 triplet 使用相同 simulator、runtime 和 trace，只有确认策略 overlay 不同。

- Backend commit：`9b7245008ca12c5acb3c62fa269df29b1729c3d3`
- Simulator SHA-256：`ae8ee5113bded602d30802b8264ff6e98187dff3055a5961405e87cae13a7df8`
- `libcudart` SHA-256：`220dbb275a3ae387c7631a6fd5e693450294e140aa93687420a8953156db635b`
- 72 个 summary、72 个 host profile、0 个 error file；全部 normal exit。
- 全部通过 `remote_hits == l2_requests_avoided`、probe reason、continuation/package、residual opportunity 守恒；没有 probe 超过统一四次硬上限。

Control 是“在四次硬上限内 bounded exhaustive”，PC 和 AddrTopo 都使用 package policy。AddrTopo 用 cache-line address region × requester cluster hash；它不依赖 PC，更适合 L2/RTL 接口。

### 8.2 聚合结果

| 范围 | 策略 | IPC 几何平均 / control | L2 delta | Remote-hit delta | Probe delta | 四次上限后的 residual exact peers |
|---|---|---:|---:|---:|---:|---:|
| canonical 16 | PC | 1.005890 | +1,292,443 | -1,338,554 | -8,484,723 | 79,537 |
| canonical 16 | AddrTopo | 1.016560 | +1,513,826 | -1,442,537 | -8,207,290 | 72,695 |
| extension 8 | PC | 0.994396 | +455,591 | -408,142 | -2,973,318 | 66,205 |
| extension 8 | AddrTopo | 0.992614 | +680,082 | -595,541 | -3,362,084 | 21,571 |
| all 24，次要视图 | PC | 1.002044 | +1,748,034 | -1,746,696 | -11,458,041 | 145,742 |
| all 24，次要视图 | AddrTopo | 1.008515 | +2,193,908 | -2,038,078 | -11,569,374 | 94,266 |

两个策略都实现了预期的权衡：显著减少 probe，但损失 remote hit、增加 L2 access。canonical 16 中节省协议工作能转化为净 IPC 收益；extension 8 中损失机会占主导，出现小幅回退。

### 8.3 每 workload 性能

IPC ratio 定义为 `control_cycles / policy_cycles`，大于 1 表示策略更快。

| 层级 | Workload | Control cycles | PC IPC/control | Addr IPC/control | 主要观察 |
|---|---|---:|---:|---:|---|
| canonical | Btree | 225,084 | 0.985797 | 0.983617 | 两种策略均过早丢失 useful peer |
| canonical | DWT2D | 232,115 | 0.990772 | 1.000496 | Addr 近中性，PC 回退 |
| canonical | Gaussian | 3,220,349 | 1.000312 | 0.999859 | 近中性 |
| canonical | Hotspot1 | 76,466 | 0.998159 | 0.997391 | 轻微回退 |
| canonical | LUD | 995,351 | 0.999061 | 0.997190 | 轻微回退 |
| canonical | NN | 7,224 | 1.000000 | 1.000000 | 严格 no-op 负控制 |
| canonical | CUTCP | 4,450,839 | 1.000070 | 0.999880 | 近中性 |
| canonical | MRI-Q | 363,136 | 1.000000 | 1.000000 | 严格 no-op 负控制 |
| canonical | SGEMM | 427,701 | 1.000435 | 1.005586 | Addr 小幅有效 |
| canonical | Stencil | 3,322,064 | 0.999821 | 1.000631 | 近中性 |
| canonical | 2DConvolution | 682,399 | 0.999893 | 1.008311 | Addr 能解释并改善一部分 residual |
| canonical | 3mm | 2,745,909 | 1.005435 | 0.998164 | PC 略优，Addr 略退 |
| canonical | ATAX | 37,187,577 | 1.071956 | 1.289012 | Addr 最大收益点，也是 canonical aggregate 的主要驱动者 |
| canonical | BICG | 31,802,204 | 1.010716 | 0.961964 | Addr 明显反例 |
| canonical | GEMM | 910,071 | 1.001294 | 1.011320 | Addr 有效 |
| canonical | GESUMMV | 112,154,997 | 1.033474 | 1.046560 | 两者均有效，Addr 更好 |
| extension | BFS | 179,814 | 0.999572 | 0.981469 | useful peer 较晚，Addr 早停更差 |
| extension | LIB | 2,570,260 | 1.000000 | 1.000000 | 无变化 |
| extension | LPS | 100,070 | 0.992925 | 0.994524 | 固定 cap4/control 已接近该点最优 |
| extension | RAY | 27,484 | 1.000000 | 1.000000 | 无变化 |
| extension | ColorMax | 1,664,913 | 0.984677 | 0.988443 | 两者均回退 |
| extension | FW-block | 621,249 | 0.999842 | 0.999802 | 近中性 |
| extension | MIS | 1,245,911 | 0.978146 | 0.977345 | 两者均明显回退 |
| extension | Pagerank | 4,776,674 | 1.000268 | 0.999630 | 近中性 |

ATAX 的大幅收益是真实动态时序结果，但它也使 canonical geomean 对单点较敏感。若排除或改变 ATAX，AddrTopo 的总体优势会显著收窄；因此报告同时保留 per-workload、canonical 16、extension 8 和 all-24 四种视图，不用单一均值替代分布。

## 9. 机制结论与后续优化方向

### 9.1 已经可以确认的结论

- C2P 的核心价值来自 redundant L2 reduction；`remote_hits == avoided L2` 已逐 run 强制验证。
- candidate 数量不是越多越好。远端命中收益必须与 serial probe、target resource、fallback 延迟共同衡量。
- 简单地“少 fallback、多等 remote”可能把可并行的 L2 路径替换成长队列等待，反而更慢。Btree 的无限等待诊断曾将 remote hits 提到 576,589，却让周期增加约 47.8%。
- C2P+ 独立 target-tag path 是合理且有效的优化：它解决 SGEMM 的主要瓶颈，并在 Btree/BFS 上显著有效；NN 证明它不会凭空产生行为。
- 地址 region × requester cluster 是 L2 可见、RTL 友好的特征；在 canonical 16 上优于同容量 PC-hash，但还不是稳定通用的最终预测器。

### 9.2 尚未解决的关键问题

- 当前策略主要学习“后续 peer 是否值得确认”，还不知道该 miss 的 L2 fallback 是否位于 IPC 临界路径。BICG、BFS、MIS 等说明同样的 remote-hit 损失对不同请求代价不同。
- AddrTopo 只有 64 个 feature bucket，ATAX 获益与 BICG 回退可能包含 aliasing 和动态训练反馈；需要按 feature/bin/score update 检查冲突，而不是盲目增大表。
- 对 2DConvolution，短确认深度比深确认更好；对 Btree/LPS 则相反。下一步若继续优化，应加入低成本 criticality/cost proxy，或对已识别的短候选列表采用受限规则，而不是增加复杂多级预测器。
- extension 8 总体回退说明当前 policy 尚不具备跨 suite 稳定性。任何“优于论文”的主张都必须先在 extension 和新的 graph workload 上通过。

### 9.3 RTL 可实现性

最终 AddrTopo feature 需要：

- line-address region hash；
- requester cluster ID；
- candidate-count bin；
- 64 × 4 × 3-bit 饱和表，共 768 state bits；
- request context 中约 6-bit feature、2-bit bin、active 和最多四次 ordinal；
- 同周期多个更新时的仲裁，或小型有界 update queue + forwarding。

它不要求 L2 获取 PC。当前 `decouple_cache_v3` RTL 尚无 Snapshot candidate discovery、remote private-L1 tag interface 和 requester-cluster interface，所以该策略不能直接单独落入现有 L2；它是在 C2P 协议基础具备之后的小型附加模块。

## 10. 被排除或仅作诊断的数据

- `c2p-confirmation-policy-v1-20260823`：低 candidate bin 额外使用 PC-hash × ordinal side table，PC/Addr 容量不匹配；只作反例诊断。
- `c2p-confirmation-policy-v2-20260823-invalid-unbounded-control-*`：control 的 `max_candidate_probes=0` 可越过四次上限，与 adaptive 不公平；整体排除。
- v2 pilot / pilot-refresh：旧 backend 或 unbounded control；不用于最终资格。
- 第一次 Pagerank launcher 在生成 summary 前被中断；保留为诊断，最终矩阵只使用同 binary/trace 的完整 replay。
- `smallfull`、initial6/7：只属于紧凑诊断，不进入 24 项正式聚合。
- 旧 CCD training 和旧 RING queue-full escape 结果已隔离；最终 paper16 报告只接受修正后的证据。

## 11. 主要审计门禁

所有正式结果至少满足：

1. normal simulator exit；
2. 同一配对/三路实验 binary、runtime、trace 身份一致；
3. resolved config 的差异只允许出现在命名的机制 overlay；
4. oracle timing 与 baseline 相同；
5. `c2p_remote_hits == c2p_l2_requests_avoided`；
6. probe hit/miss/timeout、issue reason、continue/stop、package outcome、residual opportunity 分别守恒；
7. 最终矩阵无 probe 超过统一四次硬上限；
8. NN/MRI-Q 等无共享 workload 不产生 remote hit，C2P+ NN 配对 cycle 和已有 C2P 计数完全一致。

## 12. 产物索引与复跑入口

### 论文主复现

- 最终报告：`/workspace/worktrees/accel-sim-c2p-cache/hw_run/c2p-paper16-report-final-v7-20260821.md`
- 原始 CSV/图：`/workspace/worktrees/accel-sim-c2p-cache/hw_run/c2p-paper16-analysis-final-v7-20260821/`
- 机制审计：`docs/c2p-cache/current_mechanism_and_experiment_audit_2026-08-21.md`

### C2P+ 与自适应诊断

- target-port、budget sweep：`docs/c2p-cache/c2p_stage_a_attribution.md`
- 自适应策略演进：`docs/c2p-cache/c2p_adaptive_probe_policy.md`
- Btree/BFS/LPS 紧凑诊断：`docs/c2p-cache/c2p_confirmation_policy_diagnostics_20260823.md`
- 反例记录：`docs/c2p-cache/c2p_confirmation_policy_counterexamples_20260823.md`

### 最终 24 项矩阵

- 最终审计报告：`hw_run/c2p-confirmation-policy-v3-cap4-20260823/final_report.md`
- 完整逐项数据：`hw_run/c2p-confirmation-policy-v3-cap4-20260823/policy_matrix.csv`
- Pilot：`hw_run/c2p-confirmation-policy-v3-pilot-cap4-20260823/`

复跑命令：

```bash
export C2P_GPGPUSIM_ROOT=/workspace/worktrees/gpgpu-sim-c2p-addr-observe
scripts/run_c2p_confirmation_policy_matrix.sh \
  --out-root hw_run/c2p-confirmation-policy-v3-cap4-20260823 --jobs 1
python3 scripts/finalize_c2p_confirmation_policy_matrix.py \
  --root hw_run/c2p-confirmation-policy-v3-cap4-20260823 \
  --pilot-root hw_run/c2p-confirmation-policy-v3-pilot-cap4-20260823 \
  --output hw_run/c2p-confirmation-policy-v3-cap4-20260823/final_report.md
```

## 13. 最终判断

当前成果已经超过“workload 跑通”的层次：论文核心机制、主性能趋势、L2 reduction、remote hit、R/S 分类、filter/candidate/probe 分布和三个 comparator 均有可审计证据；两个重要反例 SGEMM/2DConvolution 已通过资源隔离和确认深度实验拆解；最终 PC/AddrTopo 矩阵完成 72 个同二进制 replay 并通过守恒门禁。

现阶段最稳妥的研究结论是：

> C2P 在存在冗余且 L2 敏感时能够以 remote L1 hit 减少 L2 traffic 并提高 IPC；实际收益受 remote-confirmation 资源、候选质量和 miss criticality 共同制约。独立 target-tag path 是明确有效的 C2P+ 优化。小型地址拓扑确认表在 canonical 16 上优于同容量 PC-hash，但尚未在 extension workload 上形成普适增益，因此应作为下一步优化基础，而不是最终定论。
