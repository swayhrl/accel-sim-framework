# AI-ARCH Round A30N｜图像 DiT 优化后的执行组织与资源剩余源审

**裁决：`EVIDENCE_INSUFFICIENT / NO_HARDWARE_PROBE_READY`。** 固定的 PixArt-Σ 1024 图像生成对象、公开权重 revision、20-step scheduler 和强 dense SDPA 源码入口可追溯；DiSC 已直接提出 cached-token、attention mask 复用及混合 dense/sparse 的片上 bank/执行单元组织，Cambricon-D 已提出全网络差分与 sign-mask dataflow。DiSC 的公布比例与模拟加速不能证明强 GPU kernel 后仍有未吸收的资源成本。本轮未取得可冻结的 CTR+ST GPU 同语义实现、逐 step/层实际 tile 与完整图片的同输入质量/时间配对，故只交付**可证伪的未来诊断设计和明确 STOP**，不申请或启动 GPU、模拟器或机制实现。

## 来源、起点与证据等级

用户指定 branch `hrl/aiarch-a30n-dit-postopt-resource-174new-v1` 的冻结 HEAD 为 `cfdad590390f75ff56d7e263c233f7b1bcd4a554`；fetch 后远端 SHA 完全相同，独立 worktree `/root/workspace/accel-sim-framework-aiarch-a30n-dit-postopt-resource-174new-v1`。Goal 文件正文仍称起点 `b806777afb33be0985ec7678e69f320578eefa43`；核查它恰为 `cfdad590^`，`cfdad590` 只新增本 Goal。**依最新用户指令以 `cfdad590` 为执行起点**，不回退或修改 Goal。已按序读 `CURRENT_STATE.md`、`COORDINATION_PROTOCOL.md`、问题图谱 P01/P13/P14 和 A29 §3/5/7–9。旧 Lane T/M、C16、AWMA 与协调分支只读，不参与本 worktree 写入。

- [Cambricon-D，ISCA 2024，DOI 10.1109/ISCA59077.2024.00070](https://ieeexplore.ieee.org/abstract/document/10609724/)：**`ABSTRACT_ONLY`**；出版者摘要和[作者机构说明](https://ict.cas.cn/xwgg/jssxw/202404/t20240408_7083571.html)可核。未取得可合法逐组审的全文，不把摘要的硬件比值升级为已核真机/模拟器明细。
- [DiSC，arXiv `2605.25798v1`](https://arxiv.org/html/2605.25798) §II–V、Fig.5/7/9–18、Table I–III：**`PAPER_AUTHOR_MODEL`** 对 gem5/Ramulator 周期模型、**`PAPER_AUTHOR_NATIVE_BASELINE`** 对 A100 80GB PCIe 的 Nsight Systems 延迟；SystemVerilog/Samsung 28nm 综合是面积功率估算，不是已制造 DiSC 芯片。没有本节点测量。
- [DiTPA，ISCA 2026 作者机构记录](https://researchportal.hkust.edu.hk/en/publications/ditpa-a-dit-based-action-planner-accelerator-exploiting-action-de/)：**`ABSTRACT_ONLY`**。这是 VLA 动作闭环近邻，仅作边界反证，不从 217.65Hz 或 LIBERO-Long 1.73s 推图像生成时间。
- 强软件与部署的固定入口：[PixArt-Σ 作者仓库 `1ce521afddcc2fab329b35b7374aa86d654e12f7`](https://github.com/PixArt-alpha/PixArt-sigma/blob/1ce521afddcc2fab329b35b7374aa86d654e12f7/README.md)、[Diffusers `v0.28.0` PixArtSigmaPipeline](https://github.com/huggingface/diffusers/blob/v0.28.0/src/diffusers/pipelines/pixart_alpha/pipeline_pixart_sigma.py)、[同版本默认 attention processor](https://github.com/huggingface/diffusers/blob/v0.28.0/src/diffusers/models/attention_processor.py)。这是**`SOURCE_CODE` 能力**，非本机执行/具体 CUDA kernel 选择证明。源与 checkpoint 版本是否正是 DiSC 作者内部使用的版本 `NOT_DISCLOSED`。

## `SOURCE_EXPERIMENT_MATRIX`

| 实验组/原文 | 对象与输入身份 | 控制、质量与性能分母 | 可接受结论及不可外推处 |
|---|---|---|---|
| **C-D0 Cambricon-D 出版者摘要** | “various diffusion models / resolutions”；确切模型、checkpoint、scheduler、提示词/seed、dtype 未在可得摘要披露。 | sign-mask 只取 1-bit 符号以避免非线性层反复读原输入；作者摘要声称对 Diffy 减少 off-chip access 66–82%，对 A100 总加速 1.46–2.38×。 | 已有 full-network differential 硬件近邻；原文实验组、画质、模拟/实机及分母无法独立判定，故数字只作 `ABSTRACT_ONLY`，不能与 DiSC/本地 GPU 等值排名。 |
| **D0 DiSC §V-A、Table I** | DiT/ImageNet 512²、100 steps；PixArt-Σ/[PixArt-Eval-30K](https://huggingface.co/datasets/PixArt-alpha/PixArt-Eval-30K/commit/48c70fd1e8c3c7b77962ca5479fbcaf551c839e0) 512²/1024²/2048²、20 steps；论文称各自官方 default inference。 | CTR/ST 参数在随机 10% 子集选定；FID 与 CLIP score，2K 因 GPU 时间昂贵只取 50 outputs 报 SSIM 参考。表列整体 token pruning 25.3–62.6%、ST sparsity 56.2–66.1%，全模型 FID 相对 vanilla 增量 <0.6；PixArt-Σ 1024 的 Table III，5k 样本 FID 14.32→14.86。 | 指标是**统计质量与汇总工作量**；prompt ID/seed、实际 checkpoint SHA、每一 step/层有效 token/tile、训练无关的推理 dtype 未明确。不能把 56% sparsity 当 56% wall 可省。 |
| **D1 DiSC §III/IV、Fig.9–16** | CTR 用相邻 latent 差阈值+patch OR 选 active query；K/V **仍对全 token 计算**，FFN/attention 各层与缓存输出合并。ST 在 dense step 产生 softmax 阈值 mask，在后续 step 复用；QK 成 SDDMM、PV 成 SpMM。 | 专用 DPU 执行矩阵、VPU 执行 softmax/LayerNorm 与 SpMM；hash 把非零映射到各自 SRAM bank，前置 K/V 投影重排以免下游格式转换；Fig.15 在 PixArt-Σ 2K 的真实生成 mask 上比较三类 hash 的**分配标准差**。 | “token skip/mask reuse/bank 消冲突/混合执行”均已有直接论文覆盖。Fig.15 说明作者的专用硬件内均衡，不是 commodity GPU 的寄存器/SMEM/occupancy 或完整 wall 实测。 |
| **D2 DiSC §V-A/B、Fig.17–18** | 同上模型/分辨率；A100 80GB PCIe 原生 GPU latency 对照，H100 比值另报；DiSC 为 gem5+Ramulator 周期模型，38 cores 对齐 A100 峰 MAC（311.3 vs 312 TFLOPS）和 HBM（2048 vs 1935 GB/s），RTL 1GHz/28nm 综合。 | Fig.17 全网络 FLOPs 减 29–37%；Fig.18 `DiSC_Baseline`（新硬件无 CTR/ST）→`DiSC_CTR`→`DiSC_All` 是**累加对照**，对 A100 分别 2.64–3.44×、3.41–4.01×、3.47–4.74×。 | 不能把新硬件 baseline 与 GPU 原生实现的差值全归 CTR/ST；对 H100 的 2.48–3.50×亦不是 H100 上运行 DiSC。area 按 28nm→7nm 缩放为估算，不能当硅片实测。 |
| **D3 DiSC §V-D、Table III** | PixArt-Σ 1024²，5k outputs。 | Vanilla 14.32、DiSC CTR+ST 14.86、TOME 50.61、EXION 15.96、ToCa 21.06 FID；作者对其它方法只移植相应 self-attention 方案，ToCa 未移植 token FFN/cross-attention 缓存。 | 有质量近邻对照，但方法覆盖不全、质量/计算改变，不可当所有其它实现最强 GPU kernel 的性能排名。 |
| **A0 DiTPA 摘要** | VLA/DiT 动作生成，单任务数百动作、每动作约 10–50 去噪 step；LIBERO-Long。 | action 预测/交替去噪/多模态近似+重构 PE 与调度；作者报 217.65Hz、1.73s/任务、1.05W 且保持成功率。 | action 频率、闭环成功率与图像 FID/CLIP 不是同分母；仅登记动作领域既有冗余硬件，未审正文细节。 |

## `ALREADY_SOLVED_VS_UNQUALIFIED`／`NOVELTY_COLLISION`

| 看似可提的新题 | 已发表/公开强能力 | 当前不合格的剩余断言 |
|---|---|---|
| “跨去噪 step 的 token cache” | DiSC CTR 已在图像 DiT/PixArt-Σ 使用 latent 差选 query 并重用各层缓存；Cambricon-D 跨步差分是另一直接近邻。 | 不能重新命名为新 cache；DiSC 未给出可复核 GPU CTR+ST 同语义实现及每层有效 tile/时间，尚无强软件后残余。 |
| “attention 稀疏 mask 复用、稀疏 QK/PV” | DiSC ST 已用密步构 mask、稀步 SDDMM+SpMM；中等稀疏 50–60% 仍保证作者限定的统计画质。 | mask 存取、压缩、重排与 kernel 调度可能吞掉收益；作者模拟 DPU/VPU 不能直接证明现有强 GPU SDPA/稀疏 kernel 之后的亏损。 |
| “解决 SRAM bank conflict/复用同一矩阵单元” | DiSC hash bank 映射、前置 K/V 行次序与 DPU/VPU 混合布局已直接覆盖。 | 不得以同名 bank 数据流申请机制；GPU SMEM/register/tile 的具体剩余需真实同输入同质量实现，不能从 Fig.15 的模拟阵列标准差推出。 |
| “优化后 shape 不变所以 tile 必然浪费” | CTR 只减 query 侧有效工作，K/V 全量；ST 是细粒度非零，不自动变成合法 block sparse tile。Diffusers `v0.28.0` 在 Torch2/默认 scale 下选 `AttnProcessor2_0`，调 PyTorch SDPA，可用 flash/memory-efficient 后端。 | 论文没给按 step/层的可执行 tile 数、runtime kernel 选型、SMEM/register、完整 block wall。same tensor shape、稀疏率、FLOPs 各自都不是可实现 speedup。 |
| “动作 DiT 推广到图片” | DiTPA 已覆盖 VLA 的 action/denoise/multimodal 冗余与专用硬件。 | 其 action 成功率不能给图片 FID 阈值，动作/视频不并入本部署。 |

## `ONE_IMAGE_DIT_DEPLOYMENT`

**选择理由（我们的归纳）**：优先论文实际使用且有公开产品级入口的 **PixArt-Σ 1024² text-to-image**，而非借本机已有资产选题。DiSC Table I/III 在同分辨率提供真实生成质量与中等稀疏的作者证据；官方模型/代码有固定 ref，可审完整生成路径。2K 的论文质量只含 50 张 SSIM 参考、无同样 FID，资源需求更高；故不把 2K 作为首个本机候选。DiSC 作者选择覆盖多分辨率和验证高分辨率稀疏效果；1024 的本轮选择是我们的最小资格判断。

| 部署项 | 本轮能冻结什么 | 尚缺什么 |
|---|---|---|
| checkpoint/代码 | [官方 Diffusers 模型库 revision `e102b3591cc82e97071b8b4cb90d834d0c487207`](https://huggingface.co/PixArt-alpha/PixArt-Sigma-XL-2-1024-MS/commit/e102b3591cc82e97071b8b4cb90d834d0c487207)，目录显示总量约 21.8GB；transformer config（该 revision 中既有文件）28 层、16 heads×72、patch 2、latent sample 128，故名义 self-attention 4096 tokens；[作者代码 `1ce521…`](https://github.com/PixArt-alpha/PixArt-sigma/blob/1ce521afddcc2fab329b35b7374aa86d654e12f7/README.md)、Diffusers `v0.28.0`。 | 未下载/哈希完整权重，DiSC 文中未给出它使用的确切 checkpoint/revision；本节点无模型或平台运行资格。HF 官方整库包含 T5/VAE，实际常驻内存与设备需要测前审，不由 0.6B transformer 规模推 16GB 必可用。 |
| scheduler/条件 | [模型 `model_index.json`](https://huggingface.co/PixArt-alpha/PixArt-Sigma-XL-2-1024-MS/blob/e102b3591cc82e97071b8b4cb90d834d0c487207/model_index.json) 为 `PixArtSigmaPipeline` + `DPMSolverMultistepScheduler`；[scheduler_config](https://huggingface.co/PixArt-alpha/PixArt-Sigma-XL-2-1024-MS/blob/main/scheduler/scheduler_config.json) 指 `dpmsolver++`/order2/midpoint；`v0.28.0` pipeline 调用默认 20 steps、CFG 4.5、negative prompt 空、batch/prompt 1、`max_sequence_length=300`；模型卡演示 fp16，新页面亦示 BF16。 | DiSC 仅说官方 default，未列作者具体 scheduler 配置、CFG、prompt ID/seed 与 dtype；未来必须在**同一** revision/precision 下冻结这几个值并核模型质量，不能把 fp16/BF16/TF32 混合比较。CFG 双支可能使实际 transformer batch=2，影响 tile/显存。 |
| 输入/质量 | [PixArt-Eval-30K revision `48c70fd1e8c3c7b77962ca5479fbcaf551c839e0`](https://huggingface.co/datasets/PixArt-alpha/PixArt-Eval-30K/commit/48c70fd1e8c3c7b77962ca5479fbcaf551c839e0)公开；DiSC 使用其 prompts，1024 Table III 5k FID 14.32→14.86，另有 CLIP score 报告。 | 数据库约 49GB，prompt JSON 约 17.8MB；本轮未下载。确切 prompt 子集、order/seed/初始 latent、10% 调参子集与独立验证子集未披露或未获 bytes/SHA，故不能声称复现 Table III。FID 是样本分布指标，单图只能做配对误差/感知 canary，不能冒称 FID 合格。 |
| 强 kernel | `Diffusers v0.28.0` 的 `AttnProcessor2_0` 默认走 PyTorch `scaled_dot_product_attention`（满足 Torch2/scale 条件），模型卡另推荐 `torch.compile`；这是合法 dense 候选集的起点。 | 真正选择 flash、memory-efficient 或 math kernel 由 dtype、head72、mask、目标 GPU 决定，`SOURCE_CODE` 不等于实际运行。DiSC 论文未链接可识别的参考 CTR+ST GPU 实现；不能拿朴素 Python gather/`torch.sparse` 与强 dense SDPA 计时就叫 post-opt 硬件残余。 |

## `WORK_RESOURCE_HYPOTHESES`

- **H-S（软件组织充分）**：在固定质量可接受 CTR/ST 下，合法动态 shape packing、dense SDPA 与可适用的现成 sparse/block kernel 选优，已经使索引/mask 的额外开销小或令 sparse 路径总体没有收益。若此成立，所谓 tile 不匹配是软件后端/布局选择问题；即使 sparse FLOPs 少也可能不快。
- **H-R（待测资源剩余）**：相同工作量和强选优后，适中、非块状 mask 与部分 query 使实际 tile 利用、SMEM/register 驻留或矩阵↔非矩阵交接形成稳定 block wall 成本。需要真实 kernel/CTA、有效与发射 tile、寄存器/SMEM、带宽及完整 region wall 验证；不能把 DiSC 的模拟 bank 消冲突直接移植到 GPU 微结构。
- **H-A（必要工作/质量支配）**：CTR 仍需全 K/V、mask/softmax/合并与非目标 FFN；若高分辨率下 active query 多，或阈值提高损坏图片，则硬件组织不是主要可去时间。此与 H-R 竞争。

上述均为 `OUR_HYPOTHESIS`。DiSC 提供总体 sparsity/FLOPs 与其专用硬件模型的证据；**不提供**目标 GPU 上真实 PixArt-Σ 1024 的逐层后端选择、actual launched tile、寄存器/SMEM、准备/重排 bytes、完整 block wall 或强 sparse GPU 实现结果。

## `ONE_PROBE_OR_STOP`：条件性最小合同，当前 STOP

若以后有独立设备/获取批准，**最多一份**发现性设计：固定上述 1024 模型 revision、Diffusers/torch/CFG/dtype、官方 20-step DPM-Solver++、同一 PixArt-Eval-30K prompt/seed/初始 latent 与图片输出；选择一个已经发表的策略 **DiSC 的 CTR+ST**，不得自创新 token/跨步 cache 规则。先取得/审核可执行 GPU 实现或由作者提供的同语义实现与质量证明；这是**资格门**，本 Goal 不编写它。保留 10% 调参 prompts 与独立验证 prompts 的分离，预定最多三个 step×layer 实例：一个 mask 生成/缓存建立的早期实例、一个已有 mask/缓存的中期实例、一个晚期实例。具体 step 编号、layer 编号、prompt ID 与实现参数须在首个 native 采集前冻结；本轮没有真实逐步统计可支持事先挑“最稀疏”点。

未来对照为同模型/输入的**强 dense**（SDPA 实际最快合法后端，并比较官方可用 `torch.compile`）与**同质量 CTR+ST**（允许合法 sparse kernel/packing 选优，且完整计 mask/index/合并）。质量先看整 20-step 生成：独立 prompt 集上的 FID/CLIP 与必要单图可视/数值 canary，预先声明相对 vanilla 的可接受差异；可参考论文 1024 的 FID +0.54，但不能凭本源审把这个阈值自动授权给新设备/实现。若不合格，性能不排名。

观测分别记录：有用 MAC/active query/非零 mask、**实际发射 tile 与被跳过 tile**、mask/index/pack/reorder 字节和时间、kernel 选型/CTA、寄存器/SMEM/占用与必要同步、目标完整 transformer block 的未插桩 wall、20-step 采样全时间及最终图像质量；局部 kernel、block、整图片三层都报告。source-only 可得到名义维度、DiSC 公布的总体比例及代码准备边界；实际 tile/资源/时间只能由未来合法 native/profiler 取得，不能由 FLOPs 算出。若强 kernel 选优后 block 残余消失、CTR+ST 只靠损坏质量减少工作、或必须为这个 probe 开发新策略/重型移植，立即 `NO_HARDWARE_PROBE_READY`。即便 H-R 观察成立，还须再独立设计受控资源干预；不能自动启动模拟器、扩大 GPU、做机制。

**当前停止依据**：本轮只有公开模型与 dense 源路径及 DiSC 的硬件模型；未见作者在论文中给 GPU CTR+ST 参考仓库，检索未取得可审实现；5k prompts/seed、逐 step/layer mask/token/tile 身份未冻结，目标平台上 T5/VAE/transformer 与强 sparse kernel 的资格未知。以朴素稀疏实现造负基线会把软件组织缺口误称硬件剩余。故最终状态为 `EVIDENCE_INSUFFICIENT`，本分支不生成任何可执行 GPU Goal，不扩视频或 VLA。

## `CLOSEOUT`

- G0：174-new 预检 load 349.61/353.77/354.58（512逻辑 CPU），CPU pressure `some avg10=2.38%`、`full=0`；RAM available≈339GiB、swap 2/2GiB、overlay free≈101GiB/98% used；进程表未见本命名空间高 CPU 长任务，旧 AWMA launcher 为 sleep。本轮仅短时单进程 Git、网页/元数据读与一份小报告；不接触 109/164、模型、CUDA/GPU、模拟器或依赖安装。worktree 初始≈2.6MiB；新增文件总严格≤100MiB、worker≤2/RAM≤4GiB。终态复核 IO pressure `some/full avg10=0`、CPU pressure `some avg10=0.05%/full=0`、RAM available≈339GiB、overlay free≈100GiB；报告写前 17,485 bytes，严格 UTF-8 解码且 U+FFFD=0，全文未下载 PDF/权重/数据。最后改写后的精确 byte/SHA 由提交读回校验。
- G1–G3：Cambricon-D `ABSTRACT_ONLY`；DiSC `PAPER_AUTHOR_MODEL` + A100/H100 作者对照、官方 checkpoint/软件 `SOURCE_CODE`；DiTPA `ABSTRACT_ONLY`。一条 PixArt-Σ 图片部署、三竞争解释、至多一份条件性 probe；无 `NATIVE_MEASURED`。未核字段已逐表列出。
- G4：只新增 `docs/ai_workload_research/reviews/AI_ARCH_A30N_DIT_POSTOPT_RESOURCE_DISCOVERY_174NEW_V1.md`。提交后以远端 fetch-back 回执提供 exact commit/tree/blob 与本地/远端 SHA-256；Git 文件不自填包含自身内容的 commit SHA。branch 不合并、不写 `CURRENT_STATE.md`，工作完成即 STOP。
