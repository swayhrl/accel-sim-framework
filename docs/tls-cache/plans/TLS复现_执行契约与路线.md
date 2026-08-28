# TLS-Cache 复现：执行契约与路线

> 状态：已审阅，待实现。  
> 依据：[TLS-Cache 论文](../papers/TLS-Cache%20a%20two-level%20shared%20L1%20cache%20for%20multi-chip%20GPUs.pdf) 与 [原始总体思路](TLS复现_总体思路.md)。  
> 目标：先重建 TLS 的机制并验证趋势；只有获得作者 artifact 且参数、输入均可对齐时，才主张数值复现。

## 1. 结论和范围

TLS 的机制复现可行，但不能直接沿用当前单芯片 Accel-Sim 配置或将现有地址译码中的 `chip` 字段解释为 GPU chip。首轮工作严格分成两条证据链：

1. **机制重建与趋势验证**：实现论文中的四种体系结构，检查访问路径、容量/带宽公平性和 IPC/延迟趋势。
2. **数值复现**：仅在获得精确 workload、输入、mapping、网络参数和作者配置后开展；若有缺失，结果须标为“基于公开描述的重建”。

本文件是后续实现的门槛、假设记录和验收清单。原始思路保留为设计背景，不以其未决假设作为实现依据。

## 2. 不可变的论文机制

默认论文系统为 4 个 GPU chip，每个 chip 64 个 SM，共 256 个 SM；每个 SM 有 128 KB、4 bank、sector 化（128 B line / 4×32 B sector）的 L1。每个 chip 有 16 个 256 KB LLC slice、8 个 memory controller；跨 chip 以 ring 相连。

TLS 的默认 cluster 有 4 个 SM，物理 L1 endpoint 静态划分为 3 个 CL1 与 1 个 RL1：

- CL1 是 cluster 内全局地址唯一的 L1 home；每个全局请求首先直接路由至其 CL1，而不是本地 L1 miss 后探测同伴。
- CL1 miss 后，home page 在本 GPU chip 时访问本地 LLC；home page 在另一 GPU chip 时访问本 cluster 的唯一 RL1。
- RL1 是该 chip 内分布式远程数据缓存，只缓存 remote-home page。RL1 miss 后，经过 inter-chip 网络访问远端 LLC 或 DRAM；数据返回时填入 RL1，再填入 CL1。
- TLS 的每 chip 总 L1 容量仍为 8 MB：48 个 CL1 共 6 MB，16 个 RL1 共 2 MB。

比较组必须为：baseline 私有 L1、Shared L1（4 个 CL1/cluster、无 RL1）、L1.5（私有 L1 + 从 LLC 划出的 RDC）和 TLS。L1.5 的 RDC 除容量外还必须匹配 RL1 的 slice、端口和带宽。

## 3. 实现时必须区分的身份和地址概念

每笔事务应有清晰且互不复用的四类身份：

| 概念 | 含义 | 不可混用对象 |
|---|---|---|
| requester SM | 发出 load/store 的 SM | cache owner |
| cache owner endpoint | 实际查 tag、占 bank/MSHR、负责 fill 的 CL1/RL1 | requester SM |
| GPU home chip | page first-touch 后所属的 GPU chip | DRAM channel |
| memory partition | GPU home chip 内的 LLC slice/DRAM controller | GPU home chip |

现有 `addrdec` 的 `chip` 表示 memory channel/controller，而非论文中的多 GPU chip。实现时必须增加独立的 `gpu_chip_id` 和 page-placement 层；不得通过覆写既有 `set_chip()`/`set_partition()` 临时伪造多 GPU。若修改地址归属，必须在完整 decode 前完成，或重新计算所有受影响的 partition 字段。

优先在 TLS fabric 维护以事务 UID 为键的 `tls_transaction` sidecar，记录 requester、owner、page home、阶段、waiter 和时间戳。除非下层组件确实需要，避免把大量实验性字段塞入 `mem_fetch`。

## 4. Page placement：两个明确模式

论文采用 4 KB page 的 first-touch placement。为了既保留论文语义，又能比较体系结构，支持以下两种模式：

| 模式 | 定义 | 用途 |
|---|---|---|
| `dynamic-first-touch` | 模拟期间由第一个实际访问该页的 GPU chip 决定 home | 论文主结果 |
| `frozen-page-map` | 先记录 baseline 的动态 page map，再在各比较组重放 | 公平性与隔离控制 |

禁止把简单 trace 预扫描的文件顺序视为 first touch。每次实验都要保存 page-map、随机种子和 placement policy。

## 5. 网络和访问路径契约

每 GPU chip 有自己的 TLS fabric，不能建立一个无竞争的全局 fabric。baseline 的非 TLS 路径保持字节级/周期级不变；TLS 开关关闭时，所有 baseline 统计应完全一致。

TLS 访问路径至少区分：

| 情形 | 请求路径 | 返回路径 |
|---|---|---|
| CL1 位于 requester SM | 直接进入本 endpoint | endpoint 返回 requester |
| CL1 位于同 cluster 其他 SM | intra-cluster xbar | 反向 intra-cluster xbar |
| remote page，RL1 与 CL1 同 cluster | CL1 → intra xbar → RL1 | RL1 → intra xbar → CL1 |
| remote page，RL1 位于另一 cluster | source intra → inter-cluster → destination intra → RL1 | 对称反向路径 |
| RL1 miss | 再经 inter-chip ring 到 remote LLC/DRAM | remote hierarchy → RL1 → CL1 → requester |

请求和 128 B response 要分别建模带宽和方向；queue depth、仲裁、flit 与每跳延迟均需作为显式配置。论文只给出部分网络参数，因此以下参数在拿到 artifact 前均属于假设，而非“论文数值”：TLS xbar 延迟/队列/仲裁、ring 的 768 GB/s 定义、非 2 次幂 endpoint remap。

cluster-size 敏感性必须同时改变 endpoint 角色比例与网络规模：2-SM 为 32 个 2×2 intra 和 32×32 inter；4-SM 为 16 个 4×4 intra 和 16×16 inter；8-SM 为 8 个 8×8 intra 和 8×8 inter。

## 6. 缓存、sector 与一致性边界

复用 `l1_cache` 的 tag、MSHR、sector 和替换语义，但将 endpoint bank、入口端口和 response arbitration 放在可共享 endpoint/fabric 边界。不能令多个 `ldst_unit` 共用同一个 `m_L1D` 指针：现有命中完成、bank pipeline、response FIFO 与 scoreboard 均假定 owner 即 requester。

从 Shared L1 的真实 workload 阶段开始即保留：

- 32 B sector valid/dirty mask 和 partial fill；
- endpoint-owned MSHR，以及多个 requester 的 fanout；
- 原 baseline 的 store/write policy；
- 原 baseline 对 atomic 的处理（trace 中 atomic 若绕过 L1，则记录并保持该假设）。

可先做只读 directed prototype，但其不能作为完成的 Shared L1/TLS 实现。trace-driven 模拟没有真实数据值，因此“无 stale hit”是 metadata/policy 不变量，不是数据正确性的直接证明。

## 7. CL1/RL1 映射策略

论文描述基于地址片段/tag bits 的映射，但没有公开具体位号。实现应提供命名策略，而不是把一种 hash 隐藏为论文行为：

1. `selected-tag-bits`：显式位段，配合对 3 CL1 的非法编码 remap；拿到作者信息后作为主策略。
2. `modulo-line`：以 line address 取模；仅作为公开信息不足时的默认假设。
3. `xor`：作为 mapping sensitivity。

CL1 与 RL1 的 mapping 各自记录。所有结果须在图表/日志中声明使用的策略。

## 8. 工作负载准入与现有资产盘点（2026-08-21）

论文工作负载为 Mars SS、Rodinia SRAD/CFD、SHOC FFT/SORT/GEMM/ST2D/REDC、Parboil SPMV。下表区分“论文同名/同套件”的可信程度与当前无需 GPU 即可使用的资产；已有 trace 可以被模拟器重放，不需要本机 GPU。

| 论文应用 | 当前资产 | 状态 | 用法与限制 |
|---|---|---|---|
| SRAD | 完整 Rodinia 3.1 trace（21 GB、507 kernels）和 `srad_v1_1of40_trim`（508 MB） | 可直接重放，需核论文输入 | 最可靠候选；主实验优先全 trace，开发用 trimmed trace，并记录截取规则 |
| CFD | Rodinia 3.1 的 097K/193K/0.2M 输入和完整 trace（575 MB/1.1 GB/1.3 GB） | 可直接重放，需核论文输入 | 论文同套件同名；每个本地输入均有 5-entry `kernelslist.g` |
| Parboil SPMV | 本地有 `Dubcova3` large-input 的 app/staging 记录，无 trace；官方 Accel-Sim V100 trace 包有 `parboil.tgz` | 可离线获取，待下载/核验 | 官方包下载约 8.7 GB、解压约 182 GB；本工作区余量约 338 GB，须在下载前确认不影响现有作业 |
| SHOC FFT | 本地无 trace/source asset；[官方 SHOC 源码](https://github.com/vetter/shoc) 包含 CUDA/OpenCL 实现 | 源码可得，trace 缺失 | 不以 CUDA SDK fastWalshTransform 代替；旧 CUDA 源码需先适配 tracer 环境 |
| SHOC SORT | 本地无 trace/source asset；官方 SHOC 源码可得 | 源码可得，trace 缺失 | 不以 CUDA SDK sortingNetworks 或 mergeSort 代替 |
| SHOC GEMM | 本地无 trace/source asset；官方 SHOC 源码可得 | 源码可得，trace 缺失 | CUTLASS/PolyBench GEMM 仅可作机制筛选，不是论文替代 |
| SHOC ST2D | 本地无 trace/source asset；官方 SHOC 源码可得 | 源码可得，trace 缺失 | Parboil stencil、PolyBench FDTD2D 可作筛选，不可冒充同一应用 |
| SHOC REDC | 本地无 trace/source asset；官方 SHOC 源码可得 | 源码可得，trace 缺失 | 需将 SHOC Reduction 适配至 tracer 环境，或获取作者 artifact |
| Mars SS | 本地无 source/trace；[Mars 官方下载](https://cse.hkust.edu.hk/gpuqp/Mars.html) 含 Similarity Score（SS）CUDA 实现 | 源码可得，trace 缺失 | 该版本面向 CUDA SDK 2.3，需移植和功能验证；不以其他排序/scan 应用替代 |
| 补充筛选负载 | PolyBench GEMM/FDTD2D/2MM/3MM 等 trace；CUTLASS GEMM trace；Parboil MRI gridding trace | 可直接重放 | 只用于 directed test、ICL 筛选、压力测试和机制调试；单独报告 |

当前已确认的可直接重放 trace 包括论文同名的 SRAD、CFD，以及 PolyBench GEMM、FDTD2D、2MM、3MM 等、CUTLASS WMMA GEMM、Parboil MRI gridding。它们对无需 GPU 的开发很有价值，但后四类不得并入论文 9-workload 平均值。Parboil SPMV 可通过 Accel-Sim 官方预生成 V100 trace 离线取得；这不是重新跑 GPU，但包很大且仍须核对论文输入。SHOC/Mars 目前只有可取得的源码，没有已确认可直接重放的 SASS trace。

### 工作负载准入规则

在任何 IPC 对比之前，对每个候选 trace 运行 ideal/充分大的 RDC characterization，并输出：

\[
ICL = \text{ideal RDC read hit rate} \times \text{remote LLC access frequency}
\]

主图工作负载应优先满足：套件/应用与论文一致、输入有记录、trace 完整、ICL 与论文 Table 2 同数量级。无法满足者进入“补充机制实验”，不参与论文平均值与逐应用数值对照。

## 9. 分阶段实施与出口条件

### M0：实验契约与 artifact

- 请求作者提供 simulator commit/patch、配置、输入/trace、CL1/RL1 mapping、xbar/ring 参数、L1.5 RDC 组织和 store/atomic 规则。
- 建立 workload manifest：来源、版本、输入 hash、trace hash、CTA 截取、可用状态。
- 记录所有未决参数与默认假设。

出口：没有未标注的参数假设；每个候选负载都有 manifest。

### M1：论文 multi-chip baseline

- 建立 4×64 SM、每 chip 独立 LLC/memory partitions/memory NoC 的 baseline。
- 引入 `gpu_chip_id`、动态 first touch 和可重放 page map。
- 用 directed test 验证同 chip、相邻 chip、两跳 chip 的路径与延迟。

出口：TLS 关闭时与原 baseline 的 cycles、instructions、L1/L2/DRAM 统计完全一致；page map 可重复。

### M2：ICL 与 ideal RDC

- 实现容量足够大的远程数据缓存观测器/模型。
- 产出 RDC hit、remote frequency、ICL，并筛选论文工作负载。

出口：每个拟纳入主图的负载都有 ICL 证据；不符合者被明确降级为补充负载。

### M3：Shared L1

- 实现 endpoint-owned CL1、bank/MSHR/sector、requester 回送。
- 遵守完整 load/store/sector 基线语义。

出口：请求守恒、单次完成、MSHR fanout 守恒；cluster 内每条 line 只有一个 CL1 home。

### M4：L1.5

- 保留原私有 L1；从 LLC 划出 RDC。
- 容量、slice、端口、带宽与 TLS RL1 对齐。

出口：无额外免费端口或 injection bandwidth；RDC remote-only invariant 成立。

### M5：TLS

- 实现 3 CL1 + 1 RL1、conditional xbar 路径和 RL1→CL1 多级 fill。
- 支持三种 mapping 策略和动态/冻结 placement。

出口：RL1 只保存 remote-home line；所有网络 hop、bank/port/link 带宽和 response queue 受限且可统计。

### M6：压力、死锁与回归

- 高并发、同 line 多 requester、sector partial fill、store/atomic、拥塞与长 trace。
- 检查无死锁、无 response FIFO 饥饿、无重复 completion。

出口：所有不变量通过；TLS-off 回归仍精确一致。

### M7：主结果

- Fig. 8 IPC、Fig. 10 latency、Fig. 11 service distribution。
- 报告 per-app normalized IPC 平均方式和 paired t-test 95% CI。
- service distribution 分开统计 CL1、RL1/RDC、本 chip memory hierarchy、remote chip memory hierarchy；不要把“endpoint 远近”和“page home 远近”混为一个 local/remote。

### M8：扩展结果

- Fig. 9 locality correlation。
- cluster size、L1 size、chip count 和 placement sensitivity。
- 仅对有足够 ICL/trace 可信度的 workload 汇总主结论。

## 10. 每次运行必须保存的 provenance

- 源码 revision（顶层与 nested GPGPU-Sim）；
- simulator/config hash、TLS mapping/网络/placement 参数；
- workload、输入、trace、截取和 page-map hash；
- random seed、运行命令、统计定义和 postprocess revision；
- 架构模式（baseline/Shared/L1.5/TLS）及是否为 paper-literal 或 assumption sensitivity。

## 11. 近期可执行事项（无 GPU）

1. 写出 M0 workload manifest；为 SRAD/CFD 记录准确输入、kernel list、trace hash 与裁剪比例。
2. 决定是否下载官方 Parboil V100 trace 包并只提取 SPMV；这是无 GPU 时补齐第三个论文应用的最低成本路径，但需预留约 182 GB 解压空间。
3. 为现有 SRAD/CFD、PolyBench、CUTLASS、Parboil MRI trace 编写离线 ICL/地址分布分析器，用作早期 mapping/first-touch 设计输入。
4. 获取 SHOC 与 Mars SS 源码并做静态适配评估；没有 GPU 时不生成新 trace，先不把它们排入正式结果。
5. 联系作者或检索其 artifact；在获得 SHOC/Mars trace 前，不开始“论文九负载平均 IPC”的正式实验。
