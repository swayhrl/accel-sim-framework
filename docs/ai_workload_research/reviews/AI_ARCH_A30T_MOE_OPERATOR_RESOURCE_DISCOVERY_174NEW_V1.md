# Round A30T｜完整 MoE decode operator：强软件后有用工作与资源证据

**执行者：Codex Lane T / 174-new；2026-10-14；CPU/source-only。**
**主裁决：SOURCE_QUALIFIED_PROBE_CANDIDATE（仅 H200/SM90a 的自然 route 边界补证据）；SM89/RTX4080 为 PLATFORM_NOT_QUALIFIED。没有新硬件机制资格或本轮 GPU 授权。**
**证据等级：PAPER_AUTHOR_NATIVE / PAPER_AUTHOR_ESTIMATE / OFFICIAL_API_SOURCE / HISTORICAL_SCOPED / OUR_INFERENCE / UNKNOWN 分列。**

## SOURCE_AND_EXPERIMENT_GROUPS

### 1. Git、资源与审查范围

远端分支 hrl/aiarch-a30t-moe-complete-op-source-174new-v1 初始 HEAD **6f4cd8bc1e2c9623cbc70053eba607d8c0484ec3**，等于用户本次固定起点；独立 worktree 与 /tmp/aiarch-a30t-lanet-174new-v1 临时目录均未覆盖旧 Lane。Goal 内的 b806777afb33be0985ec7678e69f320578eefa43 是其父提交，较用户固定点早一个提交；按用户新输入采用 6f4cd8bc。初检 174-new：512 逻辑 CPU、load≈350、CPU pressure some avg10≈2.91%/full=0、RAM available≈339GiB、swap 2GiB 已满、根盘可用≈101GiB，容器进程表无高 CPU 作业；worktree 约 2.6MiB。仅小文本与公开网页读取，没有并行 CPU worker pool、模型/权重/依赖/PDF下载。

先读本分支 CURRENT_STATE（导航，不当节点实时状态）、COORDINATION_PROTOCOL、问题图谱 P01/P05/P13、[A29 §3–4/7–9](https://github.com/swayhrl/accel-sim-framework/blob/6f4cd8bc1e2c9623cbc70053eba607d8c0484ec3/docs/ai_workload_research/literature/AI_ARCH_A29_3DGS_HARDWARE_HOTSPOT_AND_PARALLEL_NON3DGS_PORTFOLIO_2026-10-14_V1.md)与证据索引去重。A29 当时只得到 MonoMoE 摘要；**本轮已直接取得原始 v1 HTML 正文**，因此以下方法和实验组不再标 ABSTRACT_ONLY。没有回写 A29 或任何 C16/AWMA authority。

| 来源/确切检查 | 真实对象、输入与测量 | 支持与边界 |
|---|---|---|
| [MonoMoE arXiv:2609.04244v1 §2–5，Table 1–3，Fig 1/4/8/9](https://arxiv.org/html/2609.04244v1) | **PAPER_AUTHOR_NATIVE，H200 132SM/141GB/4.8TB/s，E4M3 block-FP8 128×128。** §4.2：生成的 FP8 expert weights、BF16 输入及 router logits，B=1/2/4/8，20 warmup+200 CUDA-Graph replay，隔离的 routed-MoE operator；vLLM Triton grouped 是同点强对照（含 top-k、token align/量化、两投影、SwiGLU、requantize、final reduce），作者为其调 shape-specific config。Fig8 Qwen3.5-35B 1.17–1.54×为**该合成路由完整 routed boundary**的作者结果 | 不把速度提升归为新硬件收益；不是自然逐层 expert census。Fig8 称 FlashMoE-FP8 完整，但 §4.1 明说隔离 FlashMoE 比较关闭其 dispatch/combine；因此 2.20–3.84× 不作同边界完整 operator 的可靠排名 |
| 同文 §4.4/4.5 Fig9/Table3 | **PAPER_AUTHOR_NATIVE，Sonnet 固定形状文字服务**：50 prompts、1600 输入、200 生成、200 共享 prefix，关 prefix cache、开 chunked prefill，concurrency 1/2/4/8；Qwen3.5-35B TPOT 相对 grouped 降 18.7/13.0/12.3/9.9%，GSM8K/HumanEval 报任务准确率 | TPOT 是请求级后首 token 平均时间，含其它层；公开正文未给同一自然运行的逐层 route histogram、完整 routed operator 独立 wall 或 raw trace。共享 expert gate 已在并发流重叠，非待消除免费项 |
| 同文 §2.1 Table1 与 Fig1/4 | Fig1 的两 GEMM 15.8+7.2μs、低于峰值约17–22% BW及 kernel gaps 为作者 profile；Table1 的 32–36% B1–8 entitlement 由实测项**加**目标带宽0.8×peak、相对baseline提升上限1.5×等模型参数算出 | **PAPER_AUTHOR_ESTIMATE**，不是已实现硬件加速；“低峰值BW”不独立证明新资源机制或所有权重都来自 HBM |
| [SonicMoE arXiv:2512.14080v2 §5–6，Fig11–13/Table2](https://arxiv.org/html/2512.14080v2) | **PAPER_AUTHOR_NATIVE**：H100/B300 的训练单层 forward/backward及 7B FSDP2 系统，训练 token rounding 取微批 T、M_tile=128；变更每 expert 路由频数以减少 padding。作者也用若干开放模型尺寸作 kernel config | 是强 IO/tile 软件近邻，但 token rounding 可丢弃或增补路由 token、改变路由/质量合同，且论文明确训练后验证切回 top-k；不能当固定自然 decode 的同语义优化或完整 decode operator 对照。Fig13 main kernel 不含 router |
| [FlashInfer 0.7.1 fused_moe 与 mono_moe API](https://docs.flashinfer.ai/generated/flashinfer.fused_moe.mono_moe.html) | **OFFICIAL_API_SOURCE**：公开 mono_moe 仅固定 E=256、I=512、H=2048、M≤8，block-FP8，SM90a；bf16 输入与 router_logits、FP8权重/FP32尺度，top-k 1–8，输出 bf16。论文四模型和生成调度不等于此公开 API 全部可用 | 输入已经是 router_logits，API 自身不能证明它计算 logits 的上游线性投影；若使用此 API，边界必须从 logits 到输出，router projection、shared expert、残差及跨卡通信另列。SM89 没有此 MonoMoE 运行路径 |
| [vLLM MoE kernel features 文档@2521446ac8c92937b5a32b7dc2a84ef7fa8e99c5](https://github.com/vllm-project/vllm/blob/2521446ac8c92937b5a32b7dc2a84ef7fa8e99c5/docs/design/moe_kernel_features.md)，blob 2528bc9ea459d60e9866076ae3ac024866fae927 | **SOURCE_ONLY**：列 Triton fused_experts 及 prepare/finalize 模块化，量化格式和 activation/路由接口多样 | 固定的是当前文档，不是 MonoMoE 论文的 vLLM 执行 commit；文档没有证明 RTX4080 上某一模型/精度/backend 全链已可执行且最优 |
| [Qwen/Qwen3.5-35B-A3B-FP8 config@b955db3baa2e2fe51de7455fdfa08d7c29865abd](https://huggingface.co/Qwen/Qwen3.5-35B-A3B-FP8/blob/b955db3baa2e2fe51de7455fdfa08d7c29865abd/config.json) 与 MonoMoE Table2 | **SOURCE_CONFIG**：text hidden=2048、MoE I=512、E=256、top-k=8，weight block=128×128；Mono 表列 TP=1、softmax、H=2048/I=512 | 固定形状/格式，不表示本节点拥有或加载权重，也不提供自然 Sonnet per-layer route |
| [C16 E3@378487015e513ed666c0929ca3f6c00392ff11c3 的 NATURAL_ROUTING.json](https://github.com/swayhrl/accel-sim-framework/blob/378487015e513ed666c0929ca3f6c00392ff11c3/docs/vm_tlb/review_packs/C16_E3_Q30_ROUTING_DIAGNOSTIC_109_V1/NATURAL_ROUTING.json)，blob a86f9a5cf939bf635a0aa8d1bdaa9b5b25ca38a0；[解释](https://github.com/swayhrl/accel-sim-framework/blob/378487015e513ed666c0929ca3f6c00392ff11c3/docs/vm_tlb/review_packs/C16_E3_Q30_ROUTING_DIAGNOSTIC_109_V1/SCIENTIFIC_INTERPRETATION.md) | **HISTORICAL_SCOPED**：Qwen3-30B-A3B BF16 Layer24、M=2048、k=8、16384 assignments，93 active experts，median 14/max1602；expert-loop body N 11.577ms，均匀 U 11.638ms，合成8-expert热点 H 6.473ms | 这是较大 M 的固定点和弱 expert-loop backend，不是 Qwen3.5 的 B1/4/8 decode route，也没有当前强完整 operator wall；不得把H缩专家数当自然免费优化或把93专家迁移到新家族 |

## STRONG_BASELINE_AND_SM89_GAP

**同一完整边界：** 本报告的最小可审 operator 从已有 BF16 router logits + 激活开始，经过 top-k/score、路由准备、gate+up、SwiGLU、down、按权重 combine，到 BF16 routed 输出结束。router logits 的上游 matmul、shared expert、残差、TP/EP网络、其它层及请求级TPOT在边界外并分别计。MonoMoE论文所称“含 router-logit computation”的融合比公开 FlashInfer mono_moe(router_logits=...) API更宽；未来对照必须先把两臂边界锁成相同起止，不可拿 API 内核与 vLLM 含上游 router 的时间相除。论文 vLLM grouped 比较按正文属于完整 routed operator，但公开代码调用/原始计时边界未在本机复核。

| 平台/后端 | 已解决软件能力 | 本轮合法判断 |
|---|---|---|
| H200/SM90a，MonoMoE论文与官方 API | weight-major 按 expert 权重 tile 扩 CTA，M≤8的持久单launch、on-chip token tile、warp分工与ready flags，把量化/激活/部分归约压入weight stream；还做 shape-specific offline tune | 这些能力已覆盖“再提出融合 router+两个GEMM”“增加持久CTA”“免expert token pad”等宽泛新意；只剩自然route下强实现的实际未覆盖 wall/资源解释可审 |
| H200，vLLM tuned Triton grouped | 论文同点的 top-k→align/quant→两 grouped GEMM→SwiGLU/requant→reduce；已有 shape-specific tune，CUDA Graph | 不是 naive torch逐expert。Mono vs vLLM 的 H200 结果已有作者实测；新实验要新增自然逐层身份与强软件后残余，而非重复 Fig8 合成路由数值 |
| H100/B300，SonicMoE | IO-aware grouped计算、activation memory 优化与训练 tile rounding | 训练/前后向、可能变路由的质量合同，不能替代固定decode route 的 FP8 H200强基线 |
| 109 RTX4080/SM89 | 旧 C16 E3 证明一份 BF16 expert-loop 诊断可以运行；vLLM文档列 Triton/CUTLASS等候选 | **PLATFORM_NOT_QUALIFIED**：公开 MonoMoE SM90a/TMA/WGMMA路径不可当SM89 native；未核一个与目标权重格式、路由/输出相同且在SM89确实可用的最强完整 operator后端、权重fit与数值门。不可退回旧loop或套H200速度 |

## USEFUL_WORK_RESOURCE_LEDGER

选 **Qwen3.5-35B-A3B-FP8 的一个 routed 层，H200 TP1** 为唯一 source-qualified未来对象；固定官方 config 与 Mono Table2：H=2048、I=512、E=256、k=8、block-FP8 128×128。令 M 是同一 decode step 有效 token 数，n_e 为自然落到专家 e 的 token 数，R=Σn_e=Mk，U 是 n_e>0 的专家数。**自然 n_e、selected ID、实际权重cache状态均未披露：UNKNOWN。** 下表是算术身份/条件范围，非测得 latency、FLOPs利用率或DRAM流量。

| M（预选） | R=Mk | U合法范围（每token选8个不同expert） | 有用 expert MAC = R×3HI | 选中权重唯一语义字节范围（含128×128 FP32尺度） |
|---:|---:|---:|---:|---:|
| 1 | 8 | 8 | 25,165,824 | 25,171,968 B |
| 4 | 32 | 8–32 | 100,663,296 | 25,171,968–100,687,872 B |
| 8 | 64 | 8–64 | 201,326,592 | 25,171,968–201,375,744 B |

推导：每 token–expert 经过 gate 与 up 两个 H×I、down 一个 I×H，故 3HI=3,145,728 MAC。一个 FP8 expert 的唯一权重为 3HI=3,145,728 B；三个权重矩阵的 128×128 FP32 block scale 合计 768 B，故每 selected expert 3,146,496 B。这里是**唯一语义容量**：若权重已在L2，真实 HBM bytes 可更少；布局、重复加载和读放大又可更多，必须另测，不能称必然DRAM读取。Mono Eq(5) 的 uniform-route 期望 U=E[1−(1−k/E)^M] 只是模型估计，不填到“自然route”列。

token-major 条件账：令真实后端 BLOCK_M、BLOCK_N 与每expert n_e 有记录，调度行 S=Σceil(n_e/BLOCK_M)×BLOCK_M，形式上的有用行比 R/S；up/down 输出tile任务数分别 Σceil(n_e/BLOCK_M)×ceil(2I/BLOCK_N) 与 Σceil(n_e/BLOCK_M)×ceil(H/BLOCK_N)。Mono正文用 **BLOCK_M=16 的例子**展示 M=8 且64个expert各获一个pair时 R/S=1/16=6.25%；这**不是**本窗口核准的 vLLM 实际 tuned tile。当前该 backend 的实际 BLOCK_M/N、CTA数、寄存器/SMEM、padding指令和真实 util 均 UNKNOWN，不能从6.25%直接换算 headroom。

router/dispatch/combine 条件账：公开 API 的 BF16 logits 至少是 M×E×2 B 输入，BF16 routed 输出 M×H×2 B；top-k ID/score的字宽、排序与被写回的中间激活由具体实现决定。若某 contiguous expert-major BF16 路径物化 R×H 的token特征，仅该特征的一次写+读约 4RH B；vLLM Triton grouped 在论文描述中主要写 padded token索引/专家元数据并从原 activation gather，**不能套用这笔dense特征流量**。若中间 gate/down 激活或 reduction 另物化，还需加各自真实字节；当前 full operator 的实际 HBM/L2 traffic、必要权重服务、launch gaps与调度重排成本均 UNKNOWN。

## ONE_PROBE_OR_STOP

**一项未来 DISCOVERY_PROBE 设计，绝非本次执行请求：** 只在有合法 **单 H200/SM90a + 官方固定FP8 checkpoint + 具体vLLM/Mono固定源码与可冻结Sonnet输入** 的新合同下，预选 **一个 routed layer、M=1/4/8 三个自然decode点、两条同边界强后端**（MonoMoE 与作者同格式、同CUDA Graph的调优vLLM Triton grouped）。在同一次模型/activation/weight状态下记录 logits→BF16 routed输出的 uninstrumented complete-op wall、逐token selected ID/score 与 n_e、实际后端 BLOCK_M/N/CTA配置、数值输出门；router projection/shared expert/TP通信单列边界外。自然 route 是主结果；任何人工均匀/热点 route只可标诊断且不能代自然收益。正式输入须预先冻结 prompt ID、token位置、tokenizer/checkpoint SHA、请求到达/并发与不参加调参的独立prompt集；不由正面route选样。

**只在无插桩完整operator wall出现稳定残余时**，才对同一可重复点另采最少 NCU/计数器诊断：实际DRAM与L2权重bytes、achieved BW、CTA数/SM活动、调度/padding、router+dispatch+expert+combine各段与non-target开销。比较两种竞争解释：①低token grid/fill-drain与非必然tile工作导致资源供给失配；②必读权重、cache/带宽和强软件可重调度已解释wall。相同数值/精度与权重layout、同一自然route和边界是硬门；不得用第二个稀疏度/精度/模型变化冒充资源干预。未来需要完整模型和GPU资产/环境授权，当前不下载也不运行。

**预冻结反例/STOP：** 任一后端无法在该H200/格式与相同 logits→output 边界运行或数值不合格；公开API只覆盖一部分作者shape/缺上游router而无法公平补齐；自然route不出现少token/expert区域；强Mono已把额外时间吸收到必要的实测权重服务与不可隐藏依赖；或被观测差异由普通tile重调、layout、数据准备解释。以上都否定**当前硬件机会的资格**，不否定MoE领域。若未来只有109/SM89可用，则 **PLATFORM_NOT_QUALIFIED → STOP该probe**，不得移植Mono、换BF16旧loop或把naive后端列为strong。target family→应用覆盖加权→真实请求三层效果需未来分别评价，本轮不预报speedup。

## RESULT_AND_LIMITATIONS

**SOURCE_QUALIFIED_PROBE_CANDIDATE（H200条件性）/ SM89_PLATFORM_NOT_QUALIFIED。** MonoMoE已用成熟软件证明低token分解、持续weight stream和跨阶段重叠的重要性，SonicMoE则限制训练tile/路由的宽泛新意；公开FlashInfer Mono API比论文四shape范围窄且 logits 为输入。故当前没有可命名的新fusion、dequant cache或SM资源机制，也没有109原生资格。增量科学价值仅在**同一自然decode routed operator**的强软件后残余是否可辨，而这份逐层route/完整operator/counter联表在已查原文中尚未披露。H200未来probe需要另立输入、预算、GPU锁与数值合同；本报告不是该授权。

**CLOSEOUT_RECEIPT（提交前记录）：** 唯一输出 docs/ai_workload_research/reviews/AI_ARCH_A30T_MOE_OPERATOR_RESOURCE_DISCOVERY_174NEW_V1.md；起点6f4cd8bc1e2c9623cbc70053eba607d8c0484ec3；独立worktree和空临时目录，模型/权重/依赖/PDF字节下载0，GPU/CUDA/Torch import/模拟器/109/164接触0。新增文本为小量级；RSS峰值未单独采样，未运行CPU计算worker。完成提交、push、远端fetch-back的commit/tree/blob回执在最终答复列出，本报告无法自包含自身提交SHA。至此 STOP，不创建后续GPU Goal或机制开发。
