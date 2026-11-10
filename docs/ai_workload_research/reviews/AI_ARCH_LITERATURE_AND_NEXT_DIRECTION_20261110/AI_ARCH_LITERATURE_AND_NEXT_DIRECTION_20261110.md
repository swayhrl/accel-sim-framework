# AI-ARCH：近期论文、已有原生证据与下一方向研判

日期：2026-11-10。范围：CPU 端文献与既有固定结果分析；**没有新 GPU 实验，也没有晋升硬件候选**。

## 1. 结论先行

**建议下一项具体工作是 Hybrid/GDN/KV 的真实执行资格调查，限 CPU 端只读。** 新论文证明状态持久化、分层重载和跨模型状态交接正在快速发展，也暴露出质量、状态版本和完整请求分母的复杂性；项目自身 A70N 仍没有合法的真实模型、自然会话、强 runtime 与质量门的完整组合。因此当前结论为 `NO_GPU_PROBE_READY`，先确定是否有可执行对象，再谈设计或性能。此建议维持既有 `SECONDARY`，不把文献热度当成资格通过。

**3DGS 保持项目内最强的真实分析基点。** Q1 晚期 T16 的窗口结果已接受；shN GPU 驻留 V1 在两段窗口净退化，原因未闭合。新近 BoundedGS 把显存峰值从渲染转移到结构重建，进一步说明“某块状态占用大”不能推导“让它常驻 GPU 会快”。3DGS 下一步若有明确新 GPU Goal，先做 shN 退化的有界机制归因与强软件反证；不要直接设计专用硬件。高分辨率渲染工作集是另一问题，不能用本项目 Rubble/downscale4 晚期数据宣称已验证。

**MoE 热度高，但 109 上的近期强软件近邻更强。** Ostinato 用真实 agent 轨迹在四张 RTX 4090D 上同时改善 prefill 与 decode；Bevy 用并发调度消除大量链路空转；OOM 甚至在多卡全参数训练中显示配置后 EP/Local 排名反转。因此普通“专家常驻/预测预取/减少搬运”不是新研究点。MoE 继续保留自然 route、同语义强软件和 H200/SM90a 条件路线；109 的单张 RTX 4080 不能承接这些论文的数字或替代 H200。

## 2. 核对方法与证据等级

- 复用已逐份读过的远端 `docs/ai_workload_research/literature/` 23 份文件及 [本机基线](REMOTE_LITERATURE_BASELINE_20261110.md)；不再把那些笔记计为本轮新论文。固定工程交接 `00abf55d44ad02a18d529eb0afe4d02dc0ceadfe`，Q1 执行 `5787826ca21f7af958e6e1c1f828d62fd58a1ec4`，shN 执行 `2838e93cfc129183d7d727e80eccc1b2f577a82d`，CPU 收口 `ea670fcdab45aa91a0b692fd615c2fb1721a1741`。
- 2026-11-10 通过公开 arXiv Atom 检索 10 组词、每组最多 15 条；这是一轮定向检索，非系统综述，不能据此推断全领域发文数量或覆盖率。去重与相关性筛选后查看下列论文的 arXiv HTML 原文，重点核方法、实验设置、表格分母、质量及限制。检索清单和 API 地址留在 [元数据记录](literature_scout_results_20261110.json)，检索脚本见 [脚本](literature_scout_20261110.py)。网页原文是**作者报告**，没有独立复现实验或源码能力审计。arXiv `html` 不可用的 2611.12362、2611.11696、2611.08363 没有充作全文证据。以下列出的 2026 文献均按**预印本**处理，未凭预印本页面推定同行评审。
- 证据标识：`P` = 本轮核对原文方法及实验章节；`P-部分` = 原文局部章节/摘要、未核完整实验；`H` = 项目远端既有文献审阅；`N` = 本项目原生 GPU 结果；`I` = 项目独立 CPU 复算/审阅。不同等级的结论不可相互替换。

## 3. 项目自己的可比证据

| 固定证据 | 观察与分母 | 对本轮决策的约束 |
| --- | --- | --- |
| Q1 `5787826c`；独审 `06355f73`，`N+I` | 同一 Rubble/downscale4，晚期两段互不重叠自然 camera，各 50 目标步 + 1 closure；20 正式样本，T16 相比 T8 的完整 Host 窗口时延下降 12.1397% / 12.1350%。T16 本来是接受基线。ON 诊断的 CPU Adam + 全参数生产/转发约占 Host 窗口 75.59% / 74.70%，显式 join/sync 很小。 | 只证明特定晚期线程/主线程路径的有限结论；ON 与 OFF 分池、CPU/GPU 时钟不可直接相减，逻辑搬运字节不是 PCIe 流量；没有第二场景、完整训练质量或硬件因果。 |
| shN V1 `2838e93c`；用户科学裁决与收口 `ea670fcd`，`N` | 同一自然晚期 50+1 窗口各 5 对：发现 OFF/ON 中位数 9.243/11.988 秒，验证 9.254/16.792 秒；验证 5/5 对 ON 更慢。四步确定性采样最大差 `7.45e-9`，正式工作量有极小波动。ON 最大自身 NVML 约 7.992 GiB。 | 接受**该实现的描述性净退化及本次容量可运行**，数值仅四步短窗；不能推断全部 `shN` 驻留方案失败，也不能唯一归因 GPU kernel、PCIe 或失去重叠。AlexNet 历史下载偏差不抹除。 |
| A70N Hybrid 源码资格；MoE A30T；Qwen V11，`H` | A70N 是 `SOURCE_SCOPE_ACCEPTED_NOT_NATIVE_NEGATIVE / NO_SURVIVOR_IN_SEARCH_SCOPE`；MoE H200/SM90a 是条件路线；Qwen V11 为 `NO_HARDWARE_CANDIDATE_PROMOTED`。 | 源码/config 或论文模型存在不等于 109 可合法执行。MoE 的 H200 数字不能搬到 SM89；Qwen 维持 PARKED。 |

上述项目结果的固定入口：[Q1 报告](https://github.com/swayhrl/accel-sim-framework/blob/5787826ca21f7af958e6e1c1f828d62fd58a1ec4/docs/ai_workload_research/runs/AI_ARCH_Q1_COMPLETION_109_V1/FINAL_REPORT.md)、[独审](https://github.com/swayhrl/accel-sim-framework/blob/06355f73caaa6f38697d9acac94ac81a47c27e62/docs/ai_workload_research/reviews/AI_ARCH_Q1_INDEPENDENT_REVIEW_20261109_V1/Q1_INDEPENDENT_REVIEW.md)、[shN 执行](https://github.com/swayhrl/accel-sim-framework/blob/2838e93cfc129183d7d727e80eccc1b2f577a82d/docs/ai_workload_research/runs/AI_ARCH_Q1_SHN_GPU_RESIDENCY_NATIVE_V1/FINAL_REPORT.md)、[shN 收口](https://github.com/swayhrl/accel-sim-framework/blob/ea670fcdab45aa91a0b692fd615c2fb1721a1741/docs/ai_workload_research/reviews/AI_ARCH_Q1_SHN_CPU_CLOSEOUT_20261109_V1/REPORT.md)。

## 4. 新论文的实验组与可迁移边界

表内倍率均属**作者自己的基线和分母**，不能相加、不能移植为 109 的收益。

| 方向与原文 | 受控设置、作者结果、质量/边界 | 对 AI-ARCH 的作用 |
| --- | --- | --- |
| 3DGS [BoundedGS, 2610.34233v1](https://arxiv.org/abs/2610.34233v1)，`P` | RTX 4090；13 个 Mip-NeRF 360 / Tanks and Temples 场景，每景 SfM 起步 30K 步、两路径同一 densify/prune 计划。5K 户外组 Original→BoundedGS 训练 36.7→33.9 分钟，**临时渲染工作集** 9.97→1.76 GiB，PSNR 24.44→24.42。其内局部固定 Gaussian 模拟与完整训练分开；结构重建峰仍 8.68 GiB、Host RSS 13.37 GiB，不能把 1.76 GiB 当整个训练显存峰。 | 最直接的强软件近邻。渲染缓存、梯度、重建、图像供应按生命周期分账；本项目 downscale4 Rubble 晚期窗口与 5K/4K、30K 全训练不同，尚不能套其速度。 |
| 4DGS [GSPIM, 2611.04804v3](https://arxiv.org/abs/2611.04804v3)，`P-部分` | 三种动态 4DGS、六场景；Jetson Orin 标定的 GPU–PIM **模型**加 1z DRAM 电路实现，作者报帧渲染几何均值 4.15×、能效 4.99×、最大 PSNR 差 0.011 dB。 | 热点是跨帧活跃集/深度关系；这是**动态渲染模拟与电路**，不能当本项目静态 3DGS 训练、109 GPU 实测或 PPA 佐证。 |
| MoE [Ostinato, 2611.11533v1](https://arxiv.org/abs/2611.11533v1)，`P` | DeepSeek-V4-Flash、四 RTX 4090D；held-out SWE 13 会话与 τ² 60 任务，真实轨迹回放；对 llama.cpp 两路径、ik_llama.cpp、KTransformers、buun、FreeToken。工具返回后 TTFT 中位数 1.26/0.98 秒；相对最快调优 buun 总请求时间节省 16.5%/20.4%，对 KTransformers 58.0%/60.4%。一个 GPU 的 FreeToken 对比只看总请求时间。作者称不改专家计算，但每引擎回放固定轨迹，不是重新生成 agent 行为质量。 | “部分专家常驻 + 短 prefill 路由拆分 + 长 prefill 冷专家上传 + decode graph”已是强基线；109 单卡 16 GiB 和四卡 4090D 不等价。 |
| MoE [Bevy, 2611.04794v1](https://arxiv.org/abs/2611.04794v1)，`P` | Apple M6 mini/Jetson Thor 统一内存，Q4_0 Qwen3.6-35B-A3B/Gemma4-26B-A4B；2–16 并发，缓存 10–70%。同一 llama.cpp 引擎下相对最快预取基线解码吞吐 1.01–1.55×；**只报 512 decode steps 后半段**，剔除共同 SSD 慢读步；没有完整 agent 请求时间。加预取反而在 2/4 并发降吞吐 4.2%/5.4%。 | 并发调度可替代预测预取；硬件、并发和计时边界均与 109 单窗口不同。若没有自然并发请求，不能构成项目候选。 |
| MoE [vExpert, 2611.06057v1](https://arxiv.org/abs/2611.06057v1)，`P` | 8 节点、每节点 8×H100，DeepSeek-V3.1；用 ShareGPT/LongBench/LiveCodeBench 构造在线漂移。SGLang B0/B1/B2/Offload 强对照；batch256 对 B0 吞吐 +28.4%，Offload 反而约 −10%，需计算 H2D 与 A2A/PCIe 争用。 | “多放一个专家”不一定有净益；这里是 64 卡分布式负载均衡，不是 109 的单卡容量实验。作者基于公开数据的**合成到达序列**，不是生产流量原始实测。 |
| MoE 训练 [OOM, 2611.11364v1](https://arxiv.org/abs/2611.11364v1)，`P` | 四 H100 或四 24 GiB 4090，五个 MoE、最长 1M/512K 上下文；同 global batch 与 CPU-offloaded FSDP2，吞吐几何均值 1.58×/4.08×。H100 batch96、4K 时，配置前 EP4 快 1.17×，配置后 Local 快 1.21×。含数值/训练质量章节，但本轮主要核系统实验；不可当项目质量审查。 | 与 shN 负结果同向提醒：驻留收益依赖激活、工作集、NUMA 和路径配置；没有“常驻总会快”的跨负载定律。硬件和训练模型均不具 109 资格。 |
| Hybrid/KV [SARIA, 2610.31169v1](https://arxiv.org/abs/2610.31169v1)，`P` | 主台 RTX PRO 6000 96 GiB，发布的 Qwen3-8B 与 Qwen3.5-9B BF16；A30 24 GiB 辅台用随机初始化的缩小结构，**并非发布 checkpoint**。TraceLab/WEKA 只给长度与块身份，作者重建确定性合成 prompt；请求止于首 token。相对 full duplicate，WEKA/Qwen3.5-9B 在 E3 下 SSD 写入少 78.2%，但平均 TTFT **高 78.4%**；对 DRAM-only TTFT 少约 94.9%。质量未测。 | 分层持久化存在延迟、写寿命、共享入口带宽三目标折中，不能只选一个最好倍率。Hybrid GDN checkpoint 16K token 一次；与本项目完整自然请求/质量门仍有距离。 |
| KV 生命周期 [The Storage View of KV Cache, 2611.10178v1](https://arxiv.org/abs/2611.10178v1)，`P` | 11 条生产/公开 trace、六类工作负载；其中自采 Open Deep Research 为 Qwen3-8B BF16/A100，部分上游并发/轮数缩减。按统一 tokenizer、16-token 块和 Qwen3-8B KV 几何做**trace 驱动分析**，不模拟具体有限容量系统。按 workload 的 TTL 最多多保留 22% 会话内命中、少留 40% 死状态；session 完成信号解除单会话空闲超时取舍。 | 工作负载 ID、会话 ID、完成信号是可迁移的最小接口问题；百分比不是完整服务加速。项目需先有自然会话和完整状态生命周期。 |
| KV [FlashOffloading, 2611.07542v1](https://arxiv.org/abs/2611.07542v1)，`P` | GLM-5.2/MTP3，32 Ascend910C（64 die）prefill/decode 分离；作者报 64K decode 吞吐 1.68×，在 30ms TPOT 门下最高 1.91×。64K、batch4→12 同时 TPOT 17.0→30.2ms；完整系统吞吐与单请求延迟必须同列。 | 强近邻是模型定义的稀疏注意力 + 全 KV 保留 + 分阶段 offload。Ascend 大集群不证明 109 或 GDN 可行；也不应把吞吐增益说成单请求时延收益。 |
| GDN 压缩 [SPARE, 2611.07552v1](https://arxiv.org/abs/2611.07552v1)，`P` | 1.3B 纯 GDN，FP32 recurrent state，RTX A6000；对 Dense/DRRQR/Uniform，batch512 时 full-model decode 最高 2.55×、峰值显存 3.31× 降；同 12 MiB 状态预算检索准确率 60.35% vs DRRQR 33.20%，但作者明确**两类压缩都低于 Dense 质量**。 | 证明表示层与系统层可以联动，也直接触发项目质量门；它不是 exact-state tiering，也不是可替换的 Hybrid 原生运行结果。 |
| GDN 量化 [Low-Bit GDN Recurrent-State Quantization, 2610.39931v1](https://arxiv.org/abs/2610.39931v1)，`P` | 发布的 Qwen3.5-4B/9B、A100 80 GiB/SGLang 0.5.12；七任务，按固定 prompt/seed、多次生成，质量与输出长度同报，状态账含 scale/pivot/近期写队列。INT4/6 与 FP32/16 不等价。 | 小模型看似更接近 109，但若为装入显存更改 state dtype，必须单列质量/算法研究，不能算原 precision 的硬件收益。 |
| Hybrid 状态转接 [Beyond K/V Caches, 2611.08133v1](https://arxiv.org/abs/2611.08133v1)，`P` | Qwen3.5 4B/9B→27B，两 A800 80 GiB；五任务，完整 FA/REC/Conv 状态。9B→27B 任务保留率均值 94.11%；**已存在源缓存的合成 16K 上下文**，仅状态转换+目标续接体 8,823→403ms（21.91×），排除源 prefill、LM head 和答案生成。 | “状态”不止 KV，还包括 recurrent/conv 历史与版本；21.91× 不是完整请求速度，也有质量差距。109 无法凭这个数字跳过模型/数据资格。 |
| Hybrid 转接 [Translating KV Caches Between Hybrid-Attention Language Models, 2611.12062v1](https://arxiv.org/abs/2611.12062v1)，`P-部分` | Kimi MLA/KDA 与 Qwen GDN 16–48B，RTX PRO 6000 96 GiB，一/两卡；作者报告同几何 GDN 在部分任务达 native 水平，64K 首 token 18.7/46.8×短于重新 prefill，但多轮必须**分段只转一次**，天真重复翻译会塌陷；部分方向仅一个 seed，另有源模型拒答继承。 | 强调输入 token 身份与版本边界。现阶段只作为问题生成，不能把跨模型翻译误当 exact 同模型状态迁移。 |
| GDN 稀疏 [SparseGDN, 2610.41420v1](https://arxiv.org/abs/2610.41420v1)，`P-部分` | Qwen3.5-4B/9B，4K–128K；作者报保留约 29% recurrent 事件后，对 FLA 原生核的 **GDN-core prefill** 1.50–1.94×，含在线 selector；输出仍为每 token，但递归事件被选择性近似。 | 它不是 full-model/full-request、不是 exact state。若纳入强软件对照，需同时纳入 RULER 质量与选择开销。 |
| 稀疏/点云 [PointTransformerX, 2604.24169v2](https://arxiv.org/abs/2604.24169v2)，`P` | ScanNet 20 类，单 H100 batch12 训练；H100/MI300X/CPU 测推理。作者报与 PTv3 相比准确率达 98.7%、推理 1.6×、253 MB；网络结构和精度格式也变了。 | 提供“消除稀疏卷积本身”的强算法/软件反证；不能与 A69 MinkUNet34 同任务等价比较或说稀疏硬件必胜。 |
| RL [BunshinRL, 2611.10453v1](https://arxiv.org/abs/2611.10453v1)，`P` | OSWorld/WebArena，Qwen3-VL-8B，单 H100 policy 机+64 线程/256GB 工作空间机；相同 GRPO/任务/轨迹对 CRIU 与 AgentENV。WebArena 对 AgentENV 峰值工作空间内存降 43%；作者报 rollout 延迟降 23%，reward 保持；收益主要在**环境快照与工具调用**，非 GPU 算子。 | 是跨层状态生命周期热点，但项目没有该自然 episode 与环境资格；不会因“RL 很热”重开 A75。 |
| 视频 [Runway Characters, 2611.05642v1](https://arxiv.org/abs/2611.05642v1)，`P` | 57B 视频 DiT，四 H100、704×1088、24fps；真实服务与 56 turn 追踪、容量/时延/唇同步分账。四卡 159.3ms diffusion step；八卡 fused kernel 更快时 decoder 仍设周期瓶颈；作者也给出部分估计和不同模型对照。 | 说明“局部核快≠会话快”，但 109 16 GiB、Wan2.2 已有容量边界，不形成当前 GPU 资格。 |

## 5. 热点与项目内未解决问题的交叉判断

1. **状态生命周期/分层所有权：高热，项目内最值得先判资格。** SARIA、Storage View、FlashOffloading、GDN 两篇及跨模型转接都在处理状态的存放、寿命、复用和质量；它们覆盖 SSD/DRAM/HBM、session、recurrent state、KV、conv 历史。项目尚缺可合法运行的真实 Hybrid 输入。可提的问题是：**在同模型、同精度、自然会话中，状态与 KV 的生命周期是否导致强 runtime 后仍存在完整请求的、可归因的资源剩余？** 已有论文使“普通 KV cache 多一层/简单 LRU”缺乏新意；项目需要状态版本、质量和完整请求账来形成差异。
2. **3DGS 训练峰值迁移：高相关，但晚期单场景不能证明新机制。** GS-Scale/CLM/TideGS 已覆盖 CPU Adam、转发、重叠和工作集；BoundedGS 又表明缓冲生命周期优化可把峰移向重建。项目 shN V1 是反证：静态容量能装下且 OFF 局部 CPU 劳动很多，ON 仍变慢。新的可证伪问题是**在原 deferred 语义下，ON 新 GPU 工作、ID/counter 协调和失去的重叠各占多少闭合关键路径**；必须使用同一时钟域和实际重叠，并维持数值门。只有归因后仍有强软件未覆盖的剩余，才值得谈硬件。
3. **MoE 路由与异构协同：论文热、109 资格低。** MonoMoE/Patterns/Not All Models/MoE-Lightning/DALI/CoX-MoE/HiNa-MoE 是旧基础；Ostinato、Bevy、vExpert、OOM 又加深自然 route、局部 resident、并发/主存争用与配置反转。真正的剩余问题应锁定特定模型、自然 route、完整 prefill+decode、质量和 H200 条件资源。随机 router 或仅专家命中率不能晋升。
4. **稀疏点云、RL、视频：热度不等于近期可投。** PointTransformerX 使“稀疏算子必要性”本身成为问题；BunshinRL 主瓶颈在环境机；Runway 是多 H100 完整系统。项目 A69/A75 的原 STOP/SOURCE_ONLY 边界继续有效。

## 6. 下一步排序与最小可证伪合同

排序按**本项目当前证据增益与资格成本**，不是领域发文数量。`Ready` 仅表示本轮 CPU 研究可做，不表示 GPU 可启动。

| 优先 | 决策对象与最低合同 | 判否条件、成本和状态 |
| --- | --- | --- |
| **1** | **Hybrid/GDN/KV 真实资格调查（CPU 只读）**。逐项固定权重与许可/可读资产、tokenizer 和自然多轮会话字节身份、模型的 FA/GDN/Conv 状态形状与版本/跨请求寿命、实际强 runtime 与相同 dtype/质量门；把 SARIA/Strata/HybridKV 的适用性差异列清。交付可复核的身份表和完整请求计时合同，不实施性能实验。 | 任一真实实体、合法输入、状态恢复/质量判据或同语义 runtime 缺失即 `NO_GPU_PROBE_READY / STOP`；不能用随机权重或合成 prompt 代替。成本：本机资料/现有资产清点，**不下载、不训练**；CPU ready，GPU not ready。 |
| **2** | **shN V1 机制归因的判别设计**。先利用固定源码/日志把 ON 的每一类新增 GPU 更新、ID/counter、参数版本、迁移及可能的 CPU/GPU 重叠列成可测账；若未来有新 GPU 合同，事前冻结同 camera/状态/精度、原 T16 OFF、同钟 Host 区间与独立 GPU 事件、容量同活、完整 50+1 分母及短窗外质量门。 | 若静态证据已足以说明实现错误，可在隔离补丁中先修并做 CPU 检查；若要新 GPU，须另授权和共享窗口。数值/容量门失败、净收益不显著或新增工作抵消，即停止驻留硬件路线。成本：CPU 低；受控 GPU 中等，**当前不 ready**。 |
| **3** | **3DGS 跨阶段/分辨率工作集假说**。只有在可合法取得另一个自然阶段/分辨率和相同质量门后，比较渲染临时态、结构更新、CPU optimizer、Host 供给与共享容量的峰值同时存活；将 BoundedGS/CLM/TideGS 作为强软件基线。 | 缺第二自然输入或无法保持原训练语义则留 SOURCE_ONLY；不能以 5K 论文数字替代 Rubble/downscale4。成本较高，当前不 ready。 |
| **条件** | **MoE**：自然 route、真实模型与 agent 请求、精度/质量、Ostinato/Bevy/MonoMoE 等强软件；H200/SM90a 路线另核真实资源。 | 无当前 H200、路由或可比 runtime 即不转 GPU；109 SM89 不做替代。Qwen V11 PARKED，其余旧 STOP 不自动重开。 |

## 7. 供 AI-ARCH-5 审查的待决点

1. 是否同意把 Hybrid 资格调查列为下一 CPU 工作，而不把它升级为 GPU Goal？新文献强化了问题价值，也使“简单状态缓存”创新空间明显收窄。
2. shN V1 的描述性退化已接受，但**ON 逐操作和机制归因仍未知**。是否值得在未来独立、资源有界的合同中做一次归因，还是让 Q1 停在负结果分析基点？本报告不替科学窗口裁决。
3. 若未来追求硬件论文，哪一个**同语义强软件后仍剩余的物理服务量**可被独立测量？目前 Q1、Hybrid、MoE 都没有可直接上升为 PPA 的因果链。

本轮停止于文献与规划。没有访问 164、下载模型/数据、安装依赖、运行 Profiler/模拟器/RTL、恢复 Q1 或启动 GPU。
