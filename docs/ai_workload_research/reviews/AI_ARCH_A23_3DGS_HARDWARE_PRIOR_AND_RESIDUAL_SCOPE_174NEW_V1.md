# AI-ARCH A23｜3DGS 硬件最近邻与剩余空间源审（Lane N）

**结论：`NO_HARDWARE_HEADROOM_QUALIFIED`。** GSArch 已公开提出片上冷热 Gaussian 缓冲、低贡献梯度过滤和 bank 请求重排；GS-Scale 已把大训练状态放到 host、用选择性驻留、参数前递、CPU Adam 延迟更新与 image splitting 降低容量和时间成本；GS-Cache 证明跨帧解码复用是已发表的软件能力，但其对象是推理渲染。现有可核原文没有在**同一真实场景、同一强 GS-Scale 训练语义**下隔离剩余的物理带宽/容量/原子服务时间。此结论否定当前硬件准入，不否定未来可能有可测瓶颈；本轮没有新原生执行、模拟或机制方案。

## 来源、权限与身份

- 起点：`swayhrl/accel-sim-framework@47acc712aff232bbb4685746ea68e9cb12bcc0a9`；本报告所在独立分支 `hrl/aiarch-a23-gsarch-hardware-nearest-174-v1`，worktree `/root/workspace/accel-sim-framework-aiarch-a23-gsarch-hardware-nearest-174-v1`。只读继承 [A20 §1](../literature/AI_ARCH_A20_REAL_AI_WORKLOAD_REDISCOVERY_THREE_FAMILY_AUDIT_2026-10-14_V1.md) 对 GS-Scale 的已审组，不重做 Lane T 的 Mill-19 输入/事件时间线。旧 Lane N A4 `e355f096eeac44328d7463ef3256cc649ec9cb03` 保持 STOP，未触碰其工作区；其报告的中文损坏不能由本报告追认修复。
- [GSArch：HPCA 2025，DOI `10.1109/HPCA61900.2025.00037`](https://ieeexplore.ieee.org/document/10946749/)：本轮能合法核对出版者摘要和[作者机构列目](https://cs.sjtu.edu.cn/en/jiaoshiml/jiangli.html)。IEEE 全文入口/`stamp` 未返回可用原文；检索作者公开全文及 artifact 未取得。**`ABSTRACT_ONLY / SOURCE_BLOCKED_FULLTEXT`**，其图号、表号、具体场景、样本/模拟器、强 baseline、消融、PSNR/LPIPS 原数及完整训练 wall 全部 `NOT_VERIFIED`。摘要的“至多 6.49× 对 A100、15.42× 对 Jetson AGX Xavier”和 negligible image-quality loss 仅为作者摘要层声明，**不能标成原生 A100 测量或已核架构模拟数据**。
- [GS-Scale：arXiv `2509.15645v1`，ASPLOS 2026](https://arxiv.org/html/2509.15645)：直接核 §3/§4/§5 与 Fig.3–4、Fig.9、Fig.11–16、Table 1–3；[作者公开代码快照 `6471e958f7e318f4870234d8107e0aa91c2d6932`](https://github.com/SNU-ARC/GS-Scale/tree/6471e958f7e318f4870234d8107e0aa91c2d6932) 仅作 `CODE_ONLY` 接口核查，不能声称它等于原论文运行的确切代码。重点文件：[optimized trainer](https://github.com/SNU-ARC/GS-Scale/blob/6471e958f7e318f4870234d8107e0aa91c2d6932/examples/simple_trainer_hybrid_optimized.py)、[naive host trainer](https://github.com/SNU-ARC/GS-Scale/blob/6471e958f7e318f4870234d8107e0aa91c2d6932/examples/simple_trainer_hybrid_baseline.py)、[CPU Adam](https://github.com/SNU-ARC/GS-Scale/blob/6471e958f7e318f4870234d8107e0aa91c2d6932/cpu_adam/src/cpu_adam.cpp)。
- [GS-Cache：arXiv `2502.14938v1`](https://arxiv.org/html/2502.14938)：直接核 §3–§7、Table 1–6。它是完整**推理渲染框架**论文；没有把它当训练 optimizer 或 GS-Scale 的数值等价实现。三篇已够回答最近邻；未加入第四篇凑数。

## 原论文实验组与分母

| 组、来源与证据级 | 平台/输入与对照 | 可核结果与严格范围 |
|---|---|---|
| **G-A0 GSArch**，[出版者摘要](https://ieeexplore.ieee.org/document/10946749/)，`ABSTRACT_ONLY` | 作者概述冗余 off-chip 加载、梯度 atomic 写、片上读 bank conflict；提出按 Gaussian 形状/像素覆盖冷热分片缓冲、低贡献梯度过滤、冲突请求重排，并对 A100/Xavier 声称峰值加速。 | 摘要不披露真实/合成 scene、simulator/实体实现、强 gsplat/GS-Scale 对照、各机制消融及完整训练 wall/质量表。不能从峰值速度比推同平台剩余硬件 headroom；梯度过滤含质量语义，不能当严格等价归约。`PAPER_SIM` 或 `PAPER_NATIVE` 标签均暂不授予其数字。 |
| **G-S1 GS-Scale §3 Fig.3–4**，`PAPER_AUTHOR_NATIVE` | 大场景训练内存与每步视锥使用；Fig.4 平均统计，不是 per-ID 时序。 | 作者大场景平均每步使用 **8.28%** 的总 Gaussians；这不是跨 step 命中率、state 重用率或 cache 收益。每步 cull 仍需查看所有 Gaussian 几何，optimizer 原始路径仍更新全体状态。 |
| **G-S2 §5.1 Table 1–2、§5.2–5.4 Fig.11–12**，`PAPER_AUTHOR_NATIVE` | 真实 Mill-19 Rubble/Building、GauU LFLS/SZIIT/SZTU，合成 MatrixCity Aerial；Intel i7-13620H + RTX4070 Mobile、i9-13900K + RTX4080 **Super**、双 Xeon 6530 + H100 PCIe；gsplat v1.5.0、CUDA12.4、torch2.2、batch1。比较 **GPU-only**、**naive host offload**、优化但无 deferred、完整 GS-Scale；为 GPU-only 可比缩小部分场景 Gaussian 数，Aerial 起始就 OOM。 | Fig.12 allocated GPU peak 相对 GPU-only 几何均值降低 **3.98×**；Fig.11 epoch throughput：完整版相对 naive host 在 laptop/desktop 为 **4.47×/4.57×**，相对 GPU-only 为 **1.22×/0.84×**，后两者仅对非 OOM 配对。不同高斯规模与 OOM 不是等工作量时间 A/B；`allocated` 也不是 reserved/整机 RAM。RTX4080 Super 不是 109 的 RTX4080。 |
| **G-S3 §5.5 Table 3、§5.6 Fig.13**，`PAPER_AUTHOR_NATIVE` | 六场景固定训练设置的 Original/GS-Scale 质量，以及在同 GPU 容量下扩 Gaussian 的前沿。 | Rubble PSNR **26.63/26.62**、LPIPS **0.194/0.194**；Aerial PSNR **27.69/27.66**、LPIPS **0.127/0.128**（前/后）。桌面可训练 Gaussian 数 **9M→40M** 随容量扩展，画质收益同时改变模型规模。§5.5 明说 deferred Adam 因子化时**忽略 ε**：质量近似不是每步参数、moment 或梯度逐 bit 等价。 |
| **G-S4 §5.7–5.8 Fig.14–16**，`PAPER_AUTHOR_NATIVE` | H100 PCIe 双 NUMA、不同 GPU、`mem_limit` 和图像分辨率敏感性。 | 作者称 PCIe 在其平台训练时间中占小部分，双 NUMA 随机 CPU state 访问使服务更难；较小 `mem_limit` 需额外 cull/gradient accumulation；更高分辨率延长 GPU 阶段，给 CPU update 更多重叠窗口。换 GPU 同时改算力、HBM、容量和平台；分辨率/`mem_limit` 又改工作量/软件路径，都不是单因子物理资源实验。 |
| **G-C1 GS-Cache §7 Table 1–3**，`PAPER_AUTHOR_NATIVE_RENDERING` | 实体 i9-14900/128GB、**2× RTX4090 PCIe4.0×8**、Quest3；MatrixCity 城市场景本身合成，Scaffold-GS/Octree-GS 预训练 40k iterations；航拍曲线/街道直线相机路径是为模拟漫游而设置，连续关键帧用于推理。 | 单 GPU aerial Octree-GS origin→our **18.04→44.55 average FPS**（2.47×）；加入 elastic 双 GPU为 **96.46 FPS**（5.35× 相对单 GPU origin，混合软件/资源变化）。街道对应单 GPU **54.26→113.97 FPS**。Table 2–3 同列 99% FPS 与 decoding/rasterization ms；这些是渲染帧率，不是训练 step/epoch 或 Adam 状态访问。 |
| **G-C2 §7.2–7.3 Table 4–6**，`PAPER_AUTHOR_NATIVE_RENDERING` | 比较缓存/去冗余/专用 kernel 的软件消融；最大 reuse depth 10 个先前渲染帧，质量用渲染图像的 MSE/PSNR/SSIM/LPIPS。 | City Octree-GS 单 GPU完整 41.15 FPS、去 reuse 22.48 FPS（表中 speedup loss 1.83×）；Street Octree-GS 115.88→93.02 FPS（1.27×）。去 kernel 又是另一组。cache 增加少量渲染内存；Table 4 品质是与渲染图像的比较，**不是训练收敛或 Adam 数值**。 |

## `NOVELTY_COLLISION_MATRIX`

| 拟议题目/资源 | 公开已覆盖者与语义 | 当前仍缺的证据、裁决 |
|---|---|---|
| 热 Gaussian on-chip cache、L1/L2 减少重复读 | GSArch 摘要已经提出按屏幕 footprint 的冷热缓冲；GS-Cache 跨帧缓存**derived anchor/Gaussian 解码结果**；GS-Scale 保留 GPU 几何属性并按视锥迁移其余状态。 | “热点 Gaussian cache”作为名称直接撞 GSArch；三者缓存对象/时间尺度不同。未取得 GSArch 全文，不能声称它解决/没解决 L1/L2 中某个确切容量或替换策略。 |
| backward gradient atomics/bank conflict | GSArch 摘要已有低贡献梯度过滤与 bank 请求重排；GS-Scale 比较的 GPU-only 是成熟 gsplat v1.5.0。 | 缺相同强 gsplat/GS-Scale、相同质量下的梯度/atomic 时间与负载比例；过滤还改变数值，不能从 6.49× 峰值推出通用无损硬件剩余。 |
| host 参数、moment、gradient 与迁移 | GS-Scale selective offload、GPU cull、参数前递、CPU/GPU 流水已解决朴素全量迁移和全同步的一大部分；论文称 PCIe 小份额。 | optimized trainer 固定源码仍有 `valid_ids.to("cpu", non_blocking=False)` 和 pinned H2D，属 `CODE_ONLY` 可观察同步入口，不是已测关键 wall。桌面 0.84× GPU-only 表明**整系统差值**，尚不能分给 PCIe、CPU RAM、cull、split、GPU backward。 |
| CPU Adam/零梯度状态 | GS-Scale OpenMP CPU Adam 有 counter/延迟更新，论文 §4.3/§5.5 已研究该问题。 | 忽略 ε 导致非 bitwise 等价；原论文质量表支持应用容差。若未来要求完全同一 Adam，需冻结真实应用的数值/质量合同，不能临时提高阈值把已发表软件排除。 |
| 动态可见集/跨 step Gaussian ID | GS-Scale 8.28% 是**每步空间稀疏率**；代码在 densification 分支不做 lazy update，并重建 cull/IDs。 | 未披露可审的连续 camera→稳定 Gaussian ID 交集、出生/删除与失效账本。不能将 8.28% 变为时间 reuse、8 倍 cache 收益或固定生命周期。Lane T 的来源/时间线审查另行进行，本报告不依赖其结果。 |
| 跨 frame 复用 | GS-Cache 已在 3DGS **inference** 的结构化 anchor 解码上做 depth≤10 的时间复用与质量调度。 | 训练时参数、梯度、Adam moment 与 densification 改变状态；GS-Cache 的 1.83× inference reuse 消融不支持复用训练状态，也不能当同语义对照。 |

## Q-N23 的可证伪界限与 STOP

`OUR_INFERENCE`：若未来获得同一真实场景/相机次序/初始化、已优化 GS-Scale 与合法 GPU-only/gsplat 配对，唯一可问的剩余资源问题是：**在完整、同质量目标的训练 wall 中，是否仍有不可被现有流水隐藏的 host-state 服务或 GPU backward/gradient 聚合等待，且能由单因子物理资源改变而非 camera/高斯规模、kernel 或调度改变来解释？** 需先记录实际 per-step ID 生灭、D2H/H2D、CPU Adam、GPU renderer/backward、重叠与等待的 wall union，再判断干预。这里未提出 cache、atomic 或新硬件设计。

**最小反例/STOP**：若同点强软件下这类未隐藏等待很小，或只换 CPU 排布/camera 顺序/分块就消失，则关闭硬件解释；若证据只能来自 GSArch 摘要峰值、GS-Cache 推理、naive host 基线或不同 GPU/高斯规模，也停止晋升。当前没有同点剩余 wall/质量/单因子物理测试，故 `NO_HARDWARE_HEADROOM_QUALIFIED`。所有时间与容量数字均为上述作者报告，没有本节点新计时；不自动启动实验。

## `UNATTENDED_20H_CLOSEOUT`

- **状态机**：`PREFLIGHT→SOURCE_IDENTITY→SCIENCE_EVIDENCE→REPORT_AND_SHA→PUSH_AND_FETCH_BACK→STOP`。本 Goal 于 **2026-10-14 01:49 CST** 启动；结束时刻和 exact commit/tree/blob 由提交后的远端读回回执给出。Git 文件无法在自身内容中稳定写入包含自身的 commit SHA，故不伪造自引用 ID。
- **身份与隔离**：起点 `47acc712aff232bbb4685746ea68e9cb12bcc0a9`；仅本分支的一份 `docs/ai_workload_research/reviews/AI_ARCH_A23_3DGS_HARDWARE_PRIOR_AND_RESIDUAL_SCOPE_174NEW_V1.md`。Lane T/A4/协调分支均不编辑、不合并；不依赖 Lane T 完成。
- **资源**：预检 512 逻辑 CPU、quota 384 cores、load≈397、CPU pressure `some avg10≈2.67%/full=0`；RAM available≈337 GiB，swap 2/2 GiB，根盘 available≈11 GiB。实际使用只读网页/Git 元数据与单报告、小 UTF-8 探针；未启动 GPU、CUDA、模拟器、训练、编译、环境安装、PDF/场景/模型大下载。报告写后复核新增 bytes、worker/RAM 上界和 UTF-8 严格解码。
- **证据层**：GSArch `ABSTRACT_ONLY`；GS-Scale `PAPER_AUTHOR_NATIVE` + 固定代码 `CODE_ONLY`；GS-Cache `PAPER_AUTHOR_NATIVE_RENDERING`。本节点 `NATIVE_MEASURED=0`、`PAPER_SIM` 细节未核。未核的 GSArch 全文实验组/模拟方法、训练工作集 ID 时序、强软件后 wall、精确 host RAM/PCIe/atomic 占比和单因素物理干预留为 `NOT_VERIFIED`，不由摘要填空。
- **审查冻结**：2026-10-14 01:57 CST；报告 12,712 bytes（改写前），严格 UTF-8 解码通过，中文字符 2,002、U+FFFD=0；仅短时只读进程，无持续 worker；复核 RAM available≈337 GiB、根盘 available≈11 GiB，新增远低于 100 MiB。最终文件 byte/SHA 与提交时间以远端 fetch-back 为准。
- **后续权限**：`NO-GO` 当前硬件/原生实验；本 A23 子任务在远端 commit/tree/blob/SHA 一致性核验后 STOP。任何新任务需另立合同。
