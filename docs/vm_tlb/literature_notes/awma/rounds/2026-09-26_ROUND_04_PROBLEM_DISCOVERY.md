# Round04｜AWMA负结果之后的研究问题重选

日期：2026-09-26。维护：ChatGPT。**文献笔记，不是执行Goal，不授权新实验或机制。**

## 1. 范围与阅读深度

本轮核心15篇论文/预印本：10篇回到正文机制、实验或局限章节；5篇只取得原始摘要。另核对作者技术文章与NVIDIA官方文档。未运行论文代码，不声称全文精读全部论文；不使用二手自动摘要作技术结论。

既有resident translation、classic warp VPN dedup、model-derived UVM及generic resource map保持冻结。UNKNOWN归属是证据缺口，aggregate misses不能解释周期是简单解释失败，不升级成整个研究领域被否定。此前22篇/83实验组工作簿没有在本轮逐条重新审核。

## 2. 最有决策价值的原文事实

| 来源/指定版本 | 实验层次与条件 | 对选题的约束 |
|---|---|---|
| FlashInfer 2501.01005v2，Appendix B | page size=1，Q/KV heads=32，head dim=128，变化batch/长度；kernel对照 | 稀疏/连续KV的decode差在1%内，prefill约10%；不能默认gather慢。软件KV页不是UVM物理页。 |
| NSA 2502.11089v1，§3–5 | 自定义27B/3B-active架构质量；A100系统Triton效率实验 | 选择粒度与GQA共享已有联合设计；随机mask不代表自然NSA。 |
| HISA 2603.28458v1，§4–7 | TileLang索引器；query chunk1024、block128、top-m64、top-k2048；另有质量/IoU | mean IoU>99%不等于每次集合完全相同；核验章节未找到完整GPU型号说明，不补猜。 |
| IndexCache 2603.12201v1，§3–4 | 30B DSA的training-free/training-aware；另有GLM-5初步结果 | 跨层索引复用已有直接近邻；质量依赖层选择和训练。 |
| StreamIndex 2605.02568v1，§4、§6–7 | H200上V4-shaped合成索引器/层级pipeline | 分块top-k合并已有实现；理想全序定理与torch.topk未指定tie-break不能混同。不是完整checkpoint端到端。 |
| HiSparse 2608.07009v1，§3–4 | DSA/NSA/Quest；核验8×H200、32K输入/8K输出消融 | no-IO oracle会使用错误KV、输出无效；特定设置下metadata解析无可测TPOT代价，不能推广所有平台。 |
| SpecSA 2605.19893v1，§4–7 | 1.2B NSA目标+EAGLE-3端到端；另有Llama3-1B/8B改装NSA verification | exact grouping、approximate共享indices和跨层reuse须分别报告。 |
| LLM-42 2601.17768v2，§2–5 | Llama-3.1-8B，4×H100 PCIe；synthetic/ShareGPT/ArXiv；确定性流量2%–100% | 固定形状验证/回滚已有系统方案；该占比是实验变量，不是部署统计。 |
| SonicMoE 2512.14080v1，§4–6 | H100单层fwd/bwd、不同expert粒度；另有7B FSDP训练 | IO/tile优化已存在；token rounding训练后切换TC top-k评估，不是固定推理路由的等价重排。 |
| FlashAttention-4 2603.05451v1，§3、§5 | B200 BF16，seq1K–32K、总32K tokens；确定性backward另做消融 | Tensor/SFU/SMEM流水和semaphore归约调度已有强软件基线。 |

“未找到”仅限本轮版本与核验部分。没有估读未标数字的图柱，不把不同版本最大speedup合并。

## 3. 五个问题与本轮决策

### P1 数值合同下的长归约并行性——优先级1，诊断候选

问题：同一请求的输出不随batch/调度改变时，现有实现是否仍把固定归约顺序转化为不必要的跨CTA等待或中间结果写回？

已有：Thinking Machines的fixed split-size；LLM-42的固定形状验证/回滚；CoRun的固定decode形状；NVIDIA CUB的不同determinism级别；Taming Bitwise Behavior的归约描述、编译器固定树和bit-equivalence类调优；FA4的semaphore及CTA调度。

因此“固定树”“数值顺序与调度解耦”“确定性kernel”本身都不是新意。Taming全文本轮未取得，不能宣称其不覆盖跨CTA长归约。

我们的待证假设：固定算术树可能仍允许producer乱序完成；真正的剩余代价可能在完成/提交/暂存组织。先在同一数值合同下比较优化软件，不先设计硬件。

最小实验建议（未执行）：一个Split-KV归约+一个GEMM，固定目标请求的数据，少量batch档；标准优化实现、固定合同实现、同合同下的优化调度/等价类实现。记录逐bit结果、完整operator时间、partial-result字节、launch、可测等待；另一输入/长度作留出。

停止条件：软件强基线已消除主要损失；收益来自更换合同；或局部损失没有有意义的整体占比。109先做功能/数值与native代价，174的timing trace不能证明浮点等价。

### P2 在线选择—索引就绪—数据消费——优先级2，诊断候选

问题不是发现“索引器开销”，而是在固定selector/选择精度下，真实在线依赖经过强软件优化后还剩什么。

已有FlashInfer、NSA、HISA、IndexCache、StreamIndex、SpecSA、HiSparse；官方PTX/CUTLASS已有gather4，不能沿用旧Hopper限制断言新硬件不支持gather。

我们的待证假设：某些配置下索引产生/合并/发布与后续搬运之间仍有不可隐藏依赖。但“必须exact”需有实际用途，不能人为加约束制造机会。

最小实验建议（未执行）：真实在线链；同结果indices提前就绪的诊断；仍在线计算的强软件优化链。完整计入评分、top-k、发布和attention，检查集合/tie-break/输出/地址与缓存入口。提前就绪只是诊断，不是候选，更非严格性能上界。

停止条件：差距近零；只反映评分计算；软件已解决；或只有随机mask正例。现有小模型可配冻结Quest实现生成实际算法indices，但这叫新稀疏部署，不是原dense模型或自然NSA。4080只能支持相应Ada路径，gather4结论需要对应硬件。

### P3 固定自然route下的细粒度MoE映射——第三候选，先补全文

SonicMoE已处理IO/tile浪费；MonoMoE摘要更直接覆盖少token/expert decode，采用weight-major persistent megakernel和全operator融合。因此不能只用“Sonic训练route可变、我们做推理”作为创新差别。

可问：相同route、精度、完整operator边界下，强实现后是否还存在可局部化的tile/执行组织损失？先离线核有用MAC/实际tile MAC，padding比不是速度损失。FP8/H200的MonoMoE不能直接当BF16/4080等价基线。

停止条件：weight-major/persistent软件已覆盖；成本不重要；或收益改变route/精度。近期不建议为此新增trace。

### P4 输入缓存后的SSM状态提交长尾——降级保留

ReplaySSM已缓存输入、延迟state write、ring-buffer rollback，并处理continuous batching、per-sequence flush及device commit。TreeWY摘要已处理GDN草稿树、只重建accepted state。

因此这些直观机制都已直接覆盖。剩余只能条件化询问：已有方案下，异构请求进度是否仍造成额外flush长尾；不能把功能已支持说成未支持。实验须计完整token序列与长期均摊，并验证状态数值，不只挑一次慢flush。

停止条件：已有per-sequence处理和合理buffer参数已解释/消除损失。当前没有为其重新搭SSM平台的依据。

### P5 Tensor/非GEMM的线程—寄存器组织——长期备选

FA4已有强流水；FIBER摘要直接针对固定并行度、粗粒度调度和私有寄存器归属，联合ISA/微架构/编译器。问题真实具体，但近邻非常近，当前Ada模型也不能直接验证TMEM/2-CTA机制。

先只做文献与寄存器/数据转换账本；不重新修Tensor/SFU×2来补表，不以微架构实现困难反推创新性。

## 4. 方法边界

同一launch重复、跨batch不变、跨GPU不变、与reference逐bit相同是不同合同。任务准确率近似、top-k集合重叠高、保持稀疏格式，也不是逐结果等价。数学实数等价不自动等于浮点bitwise等价。

小型发现实验不要求事先证明整篇论文新颖；需要可证伪假设和最近邻对照。正式机制必须说明其相对强基线的剩余能力。允许机制原型帮助解释现象，不再要求先把所有characterization做完。

本轮未启动109/174实验、未下载模型、未改任何冻结source/config、未发布Codex Goal。下一步优先把P1/P2分别压成小型实验合同，P3先补全文，P4/P5暂不投入工程。

## 5. 原文来源登记

正文关键章节：
- S01 FlashInfer，2501.01005v2：https://arxiv.org/html/2501.01005v2
- S02 NSA，2502.11089v1：https://arxiv.org/html/2502.11089v1
- S03 HISA，2603.28458v1：https://arxiv.org/html/2603.28458v1
- S04 IndexCache，2603.12201v1：https://arxiv.org/html/2603.12201v1
- S05 StreamIndex，2605.02568v1：https://arxiv.org/html/2605.02568v1
- S06 HiSparse，2608.07009v1：https://arxiv.org/html/2608.07009v1
- S07 SpecSA，2605.19893v1：https://arxiv.org/html/2605.19893v1
- S09 LLM-42，2601.17768v2：https://arxiv.org/html/2601.17768v2
- S12 SonicMoE，2512.14080v1：https://arxiv.org/html/2512.14080v1
- S16 FlashAttention-4，2603.05451v1：https://arxiv.org/html/2603.05451v1

原始摘要，全文待补，不能作最终novelty排除：
- S10 CoRun，2608.14376：https://arxiv.org/abs/2608.14376
- S11 Taming Bitwise Behavior in GPU Kernels with Tensor Core，2609.11356：https://arxiv.org/abs/2609.11356
- S13 MonoMoE，2609.04244：https://arxiv.org/abs/2609.04244
- S15 TreeWY，2608.20961：https://arxiv.org/abs/2608.20961
- S17 A Thread-Register Decoupled GPU Execution Model for Efficient Tensor Computation（FIBER），2608.19628：https://arxiv.org/abs/2608.19628

作者技术文章与官方文档：
- S08 Thinking Machines，Defeating Nondeterminism in LLM Inference：https://thinkingmachines.ai/blog/defeating-nondeterminism-in-llm-inference/
- S14 Dao AI Lab，ReplaySSM：https://dao-lab.ai/blog/2026/replayssm/
- S18 NVIDIA CCCL determinism：https://developer.nvidia.com/blog/controlling-floating-point-determinism-in-nvidia-cccl/
- S19 NVIDIA PTX ISA，cp.async.bulk.tensor/tile::gather4：https://docs.nvidia.com/cuda/parallel-thread-execution/index.html
- S20 NVIDIA CUTLASS CuTe DSL cpasync：https://docs.nvidia.com/cutlass/latest/media/docs/pythonDSL/cute_dsl_api/cute_nvgpu_cpasync.html

本文件为独立Round04记录，未覆写Round01–03来源登记或其SHA清单。作者结论、我们的推断与建议实验分别标识；所有候选目前均未通过正式机制准入。
