# 从 TLS/C2P 复用的 Decoupled-L2 workload 候选

本文只回答一个问题：TLS-Cache 与 C2P-Cache 工作中已经跑过的
workload，哪些值得、并且能够被复用到后续 Decoupled-L2 结构改进测试。
它**不**比较 TLS/C2P 的结构、参数或性能收益；其中的 TLS locality、C2P
remote-hit/candidate/probe 计数也不能直接当作 Decoupled-L2 的 AAD、bank、
fill 或 WBQ 特征。

已有 Decoupled-L2 自身的结果和动态画像仍以
[`decoupled_l2_experiment_history.md`](decoupled_l2_experiment_history.md)
为准。本文补充跨项目 trace 的来源、语义、成本和可复用性。

## 使用规则

* **A：立即可用**：trace 已在本工作树中，且已有自然结束或可信资源记录。
  结构改动后应从这一组选择 baseline/decoupled 成对重跑。
* **B：可用但需单独排程**：trace 已在本工作树，但历史成本高，或尚缺本结构的
  定向 profile。
* **C：先门禁再用**：只有 TLS/C2P 的 bounded replay 或 V100 archive 证据；先记录
  trace hash、输入映射、baseline 自然结束和 Decoupled-L2 不变量，才可进入回归。
* “历史时间”是不同工作、不同模式下的单进程墙钟时间，用于排程而非性能比较。
  `—` 表示 TLS/C2P 没有留下可比的 host profile，不应猜测。

## A 级：当前工作树中已有、适合作为 L2 改进测试的 workload

| Workload | 来源与保留输入 | 程序语义 / 典型访存 | 已留下的有用信息 | 历史单 arm 时间 | 推荐角色 |
|---|---|---|---|---:|---|
| `nn` | C2P: Rodinia 3.1, `filelist-4` | 地理记录的 nearest-neighbour 查询；短、小、不规则。 | C2P 记录为无 peer-sharing 的严格负控制；这不是 L2 结论，但说明它适合检测结构改动是否无故扰动。trace 本地可用。 | 3–4 s | 最快 smoke / 正确性回归；不用于容量或带宽结论。 |
| `cfd_097k` | TLS: Rodinia CFD, `fvcorr_domn_097K` | 非结构网格 CFD 更新，间接寻址与不规则 mesh 访问。 | TLS 有完整自然排空矩阵和资源记录；trace 本地可用。 | 5m25s（TLS baseline/dynamic） | 主力不规则应用项；适合 tag/AAD/lower-path 结构改动后的第一轮性能检查。 |
| `btree` | C2P: Rodinia 3.1 B+ tree, file+command | B+ tree 索引遍历；指针追逐、低规则性读访问。 | C2P 的 candidate-pressure 记录说明其跨线程/cluster 访问重叠值得关注，但不能推断 AAD merge。trace 本地可用。 | 8–14 min | 不规则读、hash/slice 分布、miss-path 回归。 |
| `srad_trim` | TLS: Rodinia SRAD, 1/40 retained trace | 图像 speckle-reducing anisotropic diffusion；迭代二维邻域 stencil。 | TLS 有完整 P9 资源记录；trace 本地可用。输入是 1/40 trim。 | 18m10s | 规则空间局部性和 fill 路径；必须在表中标明 trimmed。 |
| `spmv` | TLS: Parboil SPMV；本树亦有 retained Parboil trace | 稀疏矩阵向量乘，间接 gather、低空间规则性。 | TLS 仅有 bounded compatibility：64,456 TLS reads；对 L2 只可作为“有可运行 trace”的证据。 | 1–2.5 min（本 L2 archive） | 低成本不规则访问对照；先补 Decoupled-L2 profile。 |
| `atax` | C2P: PolyBench `NO_ARGS` | `A^T(Ax)`，两次密集矩阵-向量 streaming pass。 | 本工作树已有直接动态画像：两个 kernel，AAD merge 主要在第二 kernel；`merge/OTF=1.495`。 | 13–29 min | 同 line overlap、读写平衡和 AAD 改动的主力项。 |
| `bicg` | C2P: PolyBench `NO_ARGS` | `q=Ap` 与 `s=A^Tr`，双向矩阵-向量计算。 | 直接画像：AAD merge 主要在第一 kernel；`merge/OTF=1.505`。 | 13–16 min | 与 ATAX/MVT 配对，检验相同算法类但不同 kernel phase 的行为。 |
| `gesummv` | C2P: PolyBench `NO_ARGS` | `y=αAx+βBx`，两次矩阵-向量 streaming。 | 直接画像：读主导、几乎没有同 line outstanding merge（`merge/OTF≈0.001`）。 | 16–20 min | AAD/OTF 低收益负对照，区分“所有矩阵流都应合并”的错误假设。 |
| `mri-q` | C2P: Parboil, 32×32×32 full trace | MRI-Q 重建；大量独立 voxel/sample 计算、规则数组 streaming。 | C2P 记录为低/无 peer-sharing；不等同 L2 无复用。trace 本地可用。 | 9–16 min（本 L2 archive） | 规则 streaming 的应用型对照。 |

ATAX/BICG/GESUMMV 的直接动态画像来自本项目旧 shared-bank diagnosis；它们是
当前最有价值的“程序属性已被本 L2 实际测得”的三个跨项目候选。详见历史文档的
第 4 节和 8.3 节。C2P 只提供了它们的 trace/input 保留和独立复现证据。

## B 级：trace 已有，但适合有目标地安排而不是日常回归

| Workload | 来源与语义 | 历史时间 / 资源 | 对 Decoupled-L2 的价值与限制 |
|---|---|---:|---|
| `gaussian` | C2P Rodinia, `s=256`；Gaussian elimination，pivot 与行更新。 | 19–21 min，约 0.38 GiB RSS | 可作为较规则密集线性代数的低机会/近中性对照；trace 本地可用，但尚无本 L2 的详细动态 profile。 |
| `lud` | C2P Rodinia, matrix-512；LU decomposition，块/行列更新。 | — | 另一种 dense update；trace 本地可用。适合补全矩阵类覆盖，但不要从 C2P 的 peer 数据推测 L2 行复用。 |
| `dwt2d` | C2P Rodinia, 1024×1024；二维小波变换，多阶段局部访问。 | — | 规则性随 stage 改变，适合未来加入 fixed-window R/W/OTF/AAD profile；trace 本地可用。 |
| `hotspot1` | C2P Rodinia, 1024×1024 × 2 iterations；热传导 stencil。 | — | 规则网格邻域访问；适合作为 SRAD/2DConv 的独立 stencil 交叉检查。 |
| `cutcp` | C2P Parboil, `watbox-sl40`；粒子到网格的 Coulombic potential 累加。 | — | 混合规则/不规则的 particle-grid 访问；有助于避免只测试纯 stencil 或纯 GEMM。 |
| `stencil` | C2P/Parboil, 128×128×32；三维 stencil。 | 43–66 min（本 L2 archive） | 规则 3-D 邻域读与写；较慢，适合结构稳定后的长验证。trace 本地可用。 |
| `2DConvolution` | C2P PolyBench `NO_ARGS`；二维滑窗卷积。 | 24–28 min（本 L2 archive）；C2P 记录 34–46 min | 规则 stencil、输入/输出流和空间局部性；trace 本地可用。 |
| `gemm` / `sgemm` | C2P PolyBench GEMM / Parboil medium SGEMM；稠密矩阵乘。 | GEMM 27–31 min（本 L2 archive）；SGEMM 12–26 min，C2P 最多约 7.8 GiB RSS | 高复用、tile 映射敏感；是有价值的 dense 对照，但不能把 C2P 的 peer-port 现象解释为 L2 bank 压力。两个 trace/输入不同，必须分开命名。 |
| `3mm` | C2P PolyBench；三次串联矩阵乘，带中间数组。 | 1h44m–2h24m（本 L2 archive） | 更长、更多阶段的 dense reuse；适合最终覆盖，不适合快速迭代。 |
| `fdtd2d` | TLS PolyBench FDTD-2D, 1/40 trace；电磁场二维有限差分时间推进。 | 44h30m（TLS baseline/dynamic） | 极端长的迭代 stencil。只有在机制已稳定、需要长时/多轮读写验证时单独排程。 |

## C 级：TLS/C2P 已使用，但不可直接纳入当前 L2 回归

| Workload | 来源与语义 | 已有记录 | 进入 Decoupled-L2 前的必要动作 |
|---|---|---|---|
| `ss` | TLS Mars/V100 archive，similarity search / pattern matching，较不规则遍历。 | bounded TLS replay；一次 kernel-only screen 约 3h44m、444 MiB。 | 定位并 hash trace，完成 baseline/decoupled 自然排空 pair。 |
| `fft` | TLS SHOC/V100，butterfly 多阶段、访问 stride 随阶段变化。 | bounded TLS replay。 | 同上；优先作为“阶段性访问模式”候选，不进入快速回归。 |
| `sort` | TLS SHOC/V100，key/value 重排、相位行为不规则。 | bounded TLS replay。 | 完成 provenance 和自然排空门禁。 |
| `st2d` | TLS SHOC Stencil2D/V100，二维 stencil。 | bounded replay；一次 screen 8h13m、432 MiB。 | 先确认 V100 trace 和当前 config 兼容；已有 Rodinia/PolyBench stencil 时优先级较低。 |
| `redc` | TLS SHOC Reduction，树形 many-to-one reduction。 | bounded TLS replay。 | 作为归约/阶段边界补充，需先完整 replay。 |
| ISPASS `bfs/lps/ray/lib` | C2P V100 archive；分别为图 frontier、低候选压力、ray traversal 与库型 workload。 | LPS 91–146s、约 0.69–0.72GiB RSS；其余无可比 host profile。 | 当前目录仅保留 remote-run 资料；需导入/定位原 trace、hash 和配置。LPS 可作为快 smoke 候选，但其 C2P candidate 统计不是 L2 特征。 |
| Pannotia `fw_block` | C2P V100 archive；blocked Floyd–Warshall，分块 all-pairs shortest paths。 | 无可比 host profile。 | 同样先把 trace 变为本地可重放输入；随后可补充图/动态规划类访问。 |

## TLS/C2P 实验实际留下了哪些“可用特征”

### 可直接使用

1. **输入和可运行性**：C2P 的 `paper16_workloads.tsv`、TLS P9 provenance 和
   resource records 明确保留了多项输入、trace 及自然结束证据。对选择新 L2
   workload 很有用。
2. **宿主成本**：NN、CFD、Btree、Gaussian、SGEMM、2DConvolution、FDTD-2D
   的时间/RSS 可用于并行排程，但不用于 IPC 结论。
3. **算法级模式**：stencil、dense linear algebra、sparse gather、tree traversal、
   reduction、atomic/hotspot 的覆盖维度足以组织一个不偏科的 L2 测试集。
4. **本项目已有直接画像**：ATAX/BICG/MVT/GESUMMV/SYRK 的 R/W/atomic、OTF、
   AAD merge、writeback、credit-stall 和 kernel 级差分，是唯一可直接用于
   Decoupled-L2 设计判断的动态资料。

### 不能直接使用

* TLS 的 `ideal_remote_reads`、`resident_hits`、TLS service latency 和 request hops
  描述其 remote-placement 模型，不能换算为 L2 line reuse、bank conflict 或 AAD fan-in。
* C2P 的 remote hit、candidate/query、probe timeout、target FIFO wait 描述 L1 peer
  discovery。它们最多提示“该输入有跨 cluster 数据重叠”，不能证明本 L2 的 tag/data
  bank、lower-read 或 WBQ 是瓶颈。
* 因此不能因 TLS/C2P 曾在某 workload 上有收益或退化，就预言下一版 L2 结构的收益。

## 建议的后续 L2 测试选择

每次结构改动先选一个小矩阵：`nn`（smoke）+ `cfd_097k`（不规则）+
`atax` 或 `bicg`（已测 AAD overlap）+ `gesummv`（低 merge 对照）+
`spmv`（稀疏 gather）。稳定后扩为 `btree`、`srad_trim`、`mri-q`、`2DConvolution`、
`sgemm`；最后才安排 `stencil`、`3mm`、`fdtd2d`。

新增的 profile 应直接在 Decoupled-L2 admission/tag/fill/WBQ 路径采集：按固定
cycle window 的 R/W/atomic、line reuse、AAD fan-in/lifetime、slice/bank/DRAM 映射、
admission wait 和 WBQ/fill occupancy。这样才能将 workload 语义转化为可验证的
L2 结构设计依据。

## 来源

* TLS：`/workspace/worktrees/accel-sim-tls-cache/docs/tls-cache/workload_catalogue.md`，
  `hw_run/tls-paper-workload-coverage.md`。
* C2P：`/workspace/worktrees/accel-sim-c2p-cache/docs/c2p-cache/workload_catalogue.md`，
  `configs/c2p-cache/paper16_workloads.tsv`，`experiment_runtime_planning.md`。
* Decoupled-L2：`docs/decoupled_l2_experiment_history.md` 的旧动态画像、archive
  resource planning 和 trace/provenance 记录。
