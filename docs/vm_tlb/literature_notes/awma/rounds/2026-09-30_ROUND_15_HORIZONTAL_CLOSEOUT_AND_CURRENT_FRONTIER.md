# Round15｜AWMA横向收口与2026-09-30研究前沿重审

日期：2026-09-30。维护：ChatGPT。

> 本轮是**横向决策与文献更新**，不是execution Goal。没有启动109/174，没有下载模型，没有修改accepted实验分支。  
> 目的：把Round01–14的文献候选与后续真实execution结果重新对齐，回答“别人已经做到哪里、AWMA验证过哪些问题边界、哪些还没有、下一步最值得验证什么”。

---

## 0. 执行状态先于旧文献优先级

Round04等旧笔记中的“优先候选”不能直接继承，因为后续已有execution：

- 数值一致性归约P1：`P1_SOFTWARE_BASELINE_CLOSES_GAP`；
- 在线selector P2：`P2_COST_DOMINATED_BY_SELECTOR_COMPUTE`；
- R54 checkpoint：`R54_HOST_RUNTIME_COST_NOT_ARCH_LOCALIZED_V1`；
- R81 grammar合法词表：`R81_SOFTWARE_OPPORTUNITY_NO_ARCH_CLAIM`；
- R82 layout transfer：`R82_CURRENT_SOFTWARE_SUFFICIENT_IN_SCOPE`；
- R102：`R102_INPUT_AUTHORITY_NOT_QUALIFIED_V1`，没有真实before/after tensor，不能把随机mask当AI证据；
- R101在R101R2–R5完成了oracle→有限placement→Native真实性链，最终Native为
  `NATIVE_POST_L1_DOWNSTREAM_SUPPORT_NOT_OBSERVED`，因此R101 architecture-mechanism line应关闭。

所以本轮不再把P1/P2/R101列为待开发机制。

---

## 1. R101正式收口

### 1.1 最终证据链

R101从真实HiMuon fixed 5-step Newton–Schulz同map现象开始：

1. S128 author fused F128相对K128约20.86% Native graph timing improvement；
2. Native discard/persistence能改变写流量，但性能不改善；
3. FULL5 simulator M1显著减少writeback/DRAM read/L2 miss，但cycle仅约0.5%；
4. O2 post-translation/pre-L1 one-cycle service：62.13% CONTEXT2 ROI改善；
5. S1保留正常L1+request ICNT+partition hit/return：仅0.73%；
6. P0把O2收紧到finite scheduled=1/ready=16，仍完整保持62.13%；
7. P1保留正常L1 lookup/reservation/merge/fill，只短路L1 miss之后的downstream trip：8.31%；
8. Native R101R5三个matched L512 target均以math-pipe throttle主导（约51%–71%），LG throttle均<1%；long-scoreboard PC samples主要落在BAR/SEL等位置，没有得到ordinary LDG/ST post-L1 downstream主导压力的Native支持。

### 1.2 应冻结的结论

允许：

> 当前accepted simulator中存在明显post-L1 downstream sensitivity，但匹配RTX4080 Native证据没有显示该路径是三个L512核心kernel的主导限制。因此，不应继续以该simulator sensitivity为near-SM handoff/ICNT/L1/L2新硬件的现实动机。

不允许扩大成：

- “GPU memory不重要”；
- “ICNT没有问题”；
- “所有跨kernel handoff无价值”；
- “O2/P1是错误结果”。

它是**本工作负载+当前模型的Native realism negative**。

### 1.3 R101带来的方法资产

后续AWMA可复用：

```
Native phenomenon
→ existing software/ISA control
→ bounded simulator mechanism
→ oracle localization
→ progressively realistic placement/resource bounds
→ matched Native realism check
→ promote or kill
```

这比继续把positive simulator result直接推进机制更稳健。

---

## 2. 本轮外部文献重审范围

本轮重新核了截至2026-09-30最影响选题判断的十个问题族，重点使用作者/会议/arXiv/官方项目页，旧Round01–14作为背景，不把摘要信息升级成未核实的实现事实。

### A. GPU地址翻译

代表：
- Marching Page Walks, HPCA 2025
- LATPC, MICRO 2025
- HDPAT, HPCA 2026
- DEPOT, arXiv 2606.00486
- Towards Segmentation-Based Address Translation for LLM Inference, IEEE CAL 2026
- RIPPLE, GPGPU 2026（当前仅作者publication入口，本轮不补未读全文细节）

当前进展：
- page-walk并发、batching、prefetch、MSHR压缩、dead-entry replacement、wafer-scale分布式translation都已有明确机制；
- LLM-specific segmentation又利用weight read-only、长期存活、连续映射等语义绕开weight paging；
- 因此“GPU TLB miss很多”“LLM权重连续”本身已远不足以成为新问题。

AWMA边界：
- resident translation、classic intra-warp VPN能力、contextual replay、VM per-access、translation path calibration均做过；
- 当前resident AI样本最终为`NO_NEW_AI_TRANSLATION_PROBLEM_IDENTIFIED_V1`；
- model-derived UVM也未形成distinct problem；
- **未覆盖**wafer-scale/多GPU-IOMMU、真正的CXL/disaggregated VM，也未验证LLM segmentation论文的物理连续性前提。
- 这些是**不同问题域**，不能用AWMA negative否定，但当前没有理由强行迁移过去。

来源：
- MPW: https://doi.org/10.1109/HPCA61900.2025.00123
- LATPC: https://doi.org/10.1145/3725843.3756069
- HDPAT: https://doi.org/10.1109/HPCA68181.2026.11408538
- DEPOT: https://arxiv.org/abs/2606.00486
- Segmentation LLM: https://doi.org/10.1109/LCA.2026.3693796
- RIPPLE index: https://sarchlab.org/publication

---

## 3. 数值确定性 / reduction order：已从“潜在架构问题”快速变成强软件/编译器赛道

代表：
- LLM-42, arXiv 2601.17768
- CoRun, arXiv 2608.14376
- Taming Bitwise Behavior in GPU Kernels with Tensor Core, arXiv 2609.11356
- Accelerating the Mitigation of LLM Inference Nondeterminism Across GPU Architectures, arXiv 2609.25624
- NVIDIA CCCL determinism controls（官方）

截至9月底的新变化非常重要：

1. LLM-42用fast path + fixed-shape verify/rollback把determinism从“所有kernel都必须batch invariant”改成系统级按需验证；
2. CoRun用isolated prefill + fixed-shape batched decode/padding，绕过昂贵batch-invariant kernel；
3. Taming Bitwise Behavior已经进入compiler层：重建/描述reduction order、balanced-tree lowering、bit-equivalence class内autotune、静态checker；其报告中19/27 kernel在H100/GB300上距离free-order性能10%以内；
4. 2026-09-22的新工作进一步用shape-only fixed reduction order的fused-upcast GEMM在Ampere/Ada/Hopper之间实现线性层bitwise一致，并报告明显高于此前方案的端到端性能。

AWMA边界：
- P1已经做过强软件fixed-split-256 Triton、bitwise合同；
- 额外成本仅约0.887%，没有material residual；
- 因此我们已经完成了这个问题最关键的boundary test：**同一数值合同下，软件是否已经够好？答案在当前scope是“是”。**

决策：
- **关闭作为近期硬件候选。**
- 只有将来出现软件无法满足的新数值合同/跨设备合同，才重新立题；不能继续从“确定性会限制并行”泛化出硬件需求。

来源：
- https://arxiv.org/abs/2601.17768
- https://arxiv.org/abs/2608.14376
- https://arxiv.org/abs/2609.11356
- https://arxiv.org/abs/2609.25624

---

## 4. 在线稀疏attention selector / index ready / KV消费：活跃且软件算法推进非常快

代表：
- HISA, arXiv 2603.28458
- IndexCache, arXiv 2603.12201
- StreamIndex, arXiv 2605.02568
- SpecSA, arXiv 2605.19893
- FlashMemory-DeepSeek-V4, arXiv 2606.09079
- HiSparse, arXiv 2608.07009
- Self-Indexing Attention, arXiv 2609.13205
- 既有FlashInfer / NSA / DSA体系

当前进展已覆盖多个原先可能成为“硬件交接问题”的点：

- hierarchical/index head reduction；
- cross-layer top-k index reuse；
- streaming/chunked top-k，避免完整score tensor materialization；
- sparse attention与speculative verification协同；
- 预测未来KV working set，把physical KV footprint压到小比例；
- exact indexer-agnostic host/GPU hierarchical KV cache，甚至进入SGLang；
- prefill/decode共用1-bit retrieval representation。

AWMA边界：
- P2已经比较ONLINE selector chain与indices已就绪的诊断，确认主要残差可以由selector计算本身解释；
- indices/output一致，说明“索引发布/交接硬件”没有形成独立material residual；
- 但这**不是**完整DSA/NSA/HISA系统复现，也没有覆盖1M-context hierarchical KV placement。
- 因此我们已经验证的是**selector→consumer handoff是否独立值得硬件化**，不是整个sparse-attention领域。

决策：
- **不再把online index handoff作为近期架构入口。**
- 若未来重新进入，必须由一个新的、具体的未解决边界触发，例如exact KV residency/host-device IO，而不是“top-k在线生成”。

来源：
- https://arxiv.org/abs/2603.28458
- https://arxiv.org/abs/2603.12201
- https://arxiv.org/abs/2605.02568
- https://arxiv.org/abs/2605.19893
- https://arxiv.org/abs/2606.09079
- https://arxiv.org/abs/2608.07009
- https://arxiv.org/abs/2609.13205

---

## 5. MoE：从padding/grouped-GEMM问题发展到完整persistent mega-kernel与memory-aware routing/cache

代表：
- SonicMoE, arXiv 2512.14080
- MonoMoE, arXiv 2609.04244
- MegaScale-MoE, arXiv 2505.11432
- MoE-Lightning, ASPLOS 2025
- Cache-Aware Joint Router Adaptation, arXiv 2609.04895
- 以及已有MegaBlocks/ScatterMoE/FlashInfer grouped-MoE等

当前进展：
- SonicMoE同时处理activation IO、tile浪费和padding；
- MonoMoE针对**few-tokens-per-expert decode**直接采用weight-major persistent megakernel，融合routing/top-k/quantization/两次expert projection/activation/reduction，并集成vLLM；
- 系统层又有expert paging/offload/prefetch；
- 新工作甚至联合调router与expert-cache行为。

这意味着“每expert token少→padding浪费→做硬件”已经不是空白问题。

AWMA/C16边界：
- 已有Q30/DeepSeek/OLMoE真实routing/state/warp资产；
- E3做过Q30 natural/uniform/hotspot/permutation诊断，natural与uniform差异低于主要离散度、hotspot只作为合成极端；
- 这回答了“均匀routing proxy是否会严重失真”这一窄边界；
- **没有**做过当前MonoMoE级别的完整routed-MoE强软件baseline，也没有证明自然route下仍有硬件local residual。
- 不应因为我们有MoE trace就继续开发。

决策：
- **partial boundary only，当前降级。**
- 如再启，第一步必须是完整operator strong-baseline账本（useful MAC / padded MAC / routing+dispatch+expert+combine / weight traffic），不是新trace或硬件。

来源：
- https://arxiv.org/abs/2512.14080
- https://arxiv.org/abs/2609.04244

---

## 6. SSM / recurrent state：核心state-write和speculative-state问题已经被直接攻击

代表：
- ReplaySSM（Dao AI Lab, 2026-06）
- TreeWY, arXiv 2608.20961
- SketchSSM, arXiv 2609.33051（2026-09-27）

当前进展：
- ReplaySSM不再每step写完整recurrent state，而是缓存输入、按需重建/直接算output，支持standard和speculative decode，并处理continuous batching和per-sequence flush；
- TreeWY针对Gated DeltaNet hybrid speculative verification，用tree WY transform避免每个draft位置的full-state snapshots，只重建accepted state；
- 最新SketchSSM进一步攻击“ReplaySSM仍需读full state”的问题，用compact sketch近似state read，换取明显traffic/kernel speedup，但这条路线有近似/质量合同，不是exact substitute。

AWMA边界：
- R54做过的是**prefix checkpoint / restore/runtime lifecycle**，结论是主要成本落在host runtime/events，restore本身只占被避免prefix compute的极小比例；
- R54**不是**ReplaySSM这种真实recurrent-state write/read实验；
- 所以直接SSM state问题在AWMA里尚未验证。
- 但外部工作已经非常强，尤其exact-state write/rollback的直观方案已被ReplaySSM/TreeWY覆盖。

决策：
- **未验证但当前低优先。**
- 不能因为“我们没测过”就认为有研究空白；只有发现这些方案之后的具体residual，才值得进入。

来源：
- https://dao-lab.ai/blog/2026/replayssm/
- https://arxiv.org/abs/2608.20961
- https://arxiv.org/abs/2609.33051

---

## 7. Cross-CTA / DSMEM / broader fusion / execution model：直接近邻非常强

代表：
- ClusterFusion, arXiv 2508.18850
- ClusterFusion++, arXiv 2604.23553
- CREDIT, arXiv 2609.01864
- FIBER, arXiv 2608.19628
- FlashAttention-4（2026）

当前进展：
- ClusterFusion把cluster-level collectives用于QKV/attention/output fusion；
- ClusterFusion++扩展到full Transformer decoder block；
- CREDIT不再假设“DSMEM总是好”，而是显式建模remote access、sync、occupancy等成本并预测profitable region，报告91.7% profitability prediction accuracy；
- FIBER直接从GPU execution model上解耦thread/register ownership，支持动态并行度与细粒度dataflow scheduling；
- FA4则展示现代Tensor Core/SMEM/TMEM/warp specialization已经需要算法-kernel-pipeline联合设计。

AWMA边界：
- R101本来提供了一个很好的跨kernel transient-data anchor；
- producer availability几乎全覆盖，simulator local-service oracle也有大响应；
- 但逐步现实化 + Native R101R5最终没有获得真实RTX4080支持。
- 因此**当前R101不能再为DSMEM/persistent scratchpad/new execution model提供现实动机**。
- AWMA没有泛化地否定这些机制，只是没有自己的qualified workload anchor。

决策：
- **当前关闭，不以R101继续。**
- 以后只有新负载先在Native上暴露具体execution-organization residual，再考虑这一族。

来源：
- https://arxiv.org/abs/2508.18850
- https://arxiv.org/abs/2604.23553
- https://arxiv.org/abs/2609.01864
- https://arxiv.org/abs/2608.19628
- https://arxiv.org/abs/2603.05451

---

## 8. Precision-gated RL weight updates：现象被多组工作独立确认，但AWMA真正的boundary test还没做

代表：
- PULSE / Understanding and Exploiting Weight Update Sparsity..., arXiv 2602.03839
- SparseRL-Sync, arXiv 2605.07330
- UCCL-Zip, arXiv 2604.17172
- Laminar, arXiv 2510.12633（system context）

当前进展：
- PULSE与SparseRL-Sync均报告RL post-training中working-precision权重变化高度稀疏（常见>99%），并做lossless sparse patch/weight sync；
- PULSE明确把sparsity解释为compute-visible / precision-gated：FP32 master update近dense，但BF16 cast后大多数小变化不可见；
- SparseRL-Sync在不同算法/规模上做了更广泛实证，并把index/value payload与bucketing做成系统；
- UCCL-Zip说明lossless compression还可直接融合进GPU communication primitive；
- Laminar说明weight sync本身已经是异步RL系统的重要系统设计对象。

AWMA边界：
- R102只完成了Helix源码/输入authority审计；
- **没有真实before/after完整tensor，因此CUDA=0，真正的changed-element分布、compare/compact成本、consumer apply成本完全没有在AWMA中验证。**
- 这是一个真正的“我们还没做过问题边界”的方向。
- 但**现象本身不需要我们重新证明新颖性**：外部证据已经很强。
- 我们应该问的不是“更新是否稀疏”，而是：
  > 在真实step-level payload、bit-exact reconstruct合同和强fused software baseline下，detect→compact→bucket→publish→consumer apply是否仍留下GPU-local material residual？

决策：
- **高价值未验证边界之一。**
- 第一gate仍然是获取真实scientific payload；没有payload不运行synthetic mask。
- 即使成立，也必须面对PULSE/SparseRL-Sync/UCCL-Zip，不能把“稀疏同步”当新机制。

来源：
- https://arxiv.org/abs/2602.03839
- https://arxiv.org/abs/2605.07330
- https://arxiv.org/abs/2604.17172
- https://arxiv.org/abs/2510.12633

---

## 9. Large-vocab loss/backward生命周期：软件很强，AWMA未做boundary test

代表：
- Cut Cross-Entropy (CCE), arXiv 2411.09009
- Liger Kernel, arXiv 2410.10989

进展：
- CCE已经避免完整logits materialization，在flash memory/on-the-fly完成正确token与LSE；另有gradient skip优化，但skip与exact合同必须分开；
- Liger已有fused/chunked CrossEntropy和FusedLinearCrossEntropy，并在多种training/post-training loss上持续扩展。

AWMA边界：
- **从未正式执行这一问题。**
- Round11只把它列为后备；
- 所以“同一无过滤/exact合同下，强CCE/Liger之后还有没有material lifecycle residual”仍未知。

决策：
- **未验证、但论文空白度不高。**
- 优点是边界实验成本低、现有模型可承载；适合作为quick falsification，不适合作为默认硬件主线。
- 若strong exact/no-filter software已经把gap关闭，应快速STOP。

来源：
- https://arxiv.org/abs/2411.09009
- https://arxiv.org/abs/2410.10989

---

## 10. Lossless compressed execution：已出现format+kernel co-design，单纯“压缩后少访存”不够

代表：
- DFloat11, arXiv 2504.11651
- ZipServ, arXiv 2603.17435
- UCCL-Zip, arXiv 2604.17172

进展：
- 已经从“压缩存储”走到on-the-fly/fused decode + compute；
- ZipServ明确设计fixed-length GPU-friendly format和fused decompression-GEMM；
- UCCL-Zip将compression融合进persistent communication kernels。

AWMA边界：
- C16 E1 RAW/AWQ做的是quantized implementation/shape interaction，不等于lossless compressed execution；
- AWMA还没有验证lossless compressed resident compute的完整cost；
- 但直接最近邻已经强。

决策：
- **未验证但低优先**，除非出现新的格式/消费端行为使现有fused decode明显不足。

来源：
- https://arxiv.org/abs/2504.11651
- https://arxiv.org/abs/2603.17435
- https://arxiv.org/abs/2604.17172

---

## 11. VLA / inference-time compute / gradient-VJP：真正的新执行形态之一，AWMA尚未验证

代表：
- Real-Time Execution of Action Chunking Flow Policies (RTC), arXiv 2506.07339
- Training-Time Action Conditioning for Efficient RTC, arXiv 2512.05964
- Guided Action Flow, arXiv 2607.02092
- VERITAS, RSS 2026 / arXiv 2606.18247
- GPC, RA-L 2026 / arXiv 2502.00622
- Robion VLA serving, arXiv 2609.12075
- INSPO, arXiv 2609.21220

当前趋势不是一个统一算法，而是**推理本身越来越像在线优化/验证/控制闭环**：

- RTC在生成新action chunk时执行inference-time guidance，并把计算与真实动作执行重叠；
- training-time RTC说明一部分RTC runtime overhead可以搬回训练，因此不能把RTC本身的gradient cost视为不可避免；
- Guided Action Flow则明确在frozen VLA采样过程中使用action gradients，属于真正的inference-time backward/gradient workload；
- VERITAS走gradient-free verifier路线，是重要反例：并非所有test-time improvement都必须反向传播；
- GPC用world model进行test-time ranking/refinement；
- Robion表明VLA serving已经开始做VLM/Action-Diffusion stage级资源调度和SLO管理；
- 最新INSPO又探索低runtime的gradient-guidance替代。

AWMA边界：
- **没有任何正式问题边界实验。**
- Round11只做了文献卡，没有真实policy/state/source/kernel证据；
- 因此以下都未知：
  - inference-time gradient/VJP在真实VLA中占多少GPU时间；
  - activation/state需要保留多久；
  - forward→critic/gradient→sampler之间有没有跨kernel materialization/lifecycle residual；
  - 这些开销是否被torch.compile/fusion/checkpointing等软件隐藏；
  - 最重要的是，它是否在真实-time-to-action关键路径，而不是仅kernel局部很贵。

决策：
- **当前最有研究新鲜度、但工程门槛也最高的未验证边界。**
- 正确第一步不是下载一个巨大机器人模型，也不是做硬件，而是选一个开源、可运行的小型frozen policy/critic路径，做完整“forward + inference-time gradient/VJP + consumer”native census和状态生命周期。
- 同时必须保留gradient-free / training-time替代作为强反例。

来源：
- https://arxiv.org/abs/2506.07339
- https://arxiv.org/abs/2512.05964
- https://arxiv.org/abs/2607.02092
- https://arxiv.org/abs/2606.18247
- https://arxiv.org/abs/2502.00622
- https://arxiv.org/abs/2609.12075
- https://arxiv.org/abs/2609.21220

---

## 12. AWMA问题边界总账

| 问题族 | 外部进展 | AWMA boundary test | 当前状态 |
|---|---|---|---|
| resident GPU translation | MPW/LATPC/DEPOT等机制成熟 | **已做**：classic能力、context、Native/sim校准、residual | 当前scope关闭 |
| LLM segmentation translation | 已有CAL2026 | **未做该特定前提** | 不因AWMA negative否定；当前无必要迁移 |
| UVM/resource capacity | 系统/架构研究成熟 | **已做** model-derived UVM/resource map | 当前scope关闭 |
| deterministic reduction | 2026 compiler/system快速成熟 | **已做** P1 strong software bitwise | 关闭 |
| online sparse selector handoff | HISA/IndexCache/StreamIndex/SpecSA等快速成熟 | **已做窄边界** P2 ONLINE vs READY | handoff方向关闭 |
| grammar legal-vocab | indexed/ragged software已有 | **已做** R81 | software opportunity |
| on-chip layout transfer | compiler/layout work强 | **已做** R82 | software sufficient |
| recurrent checkpoint host/runtime | 系统软件已有 | **已做** R54 | 不arch-localized |
| true SSM recurrent-state traffic | ReplaySSM/TreeWY/SketchSSM很强 | **未做** | 低优先 |
| R101 transient NS intermediate | fusion/cluster/DSMEM近邻强 | **已做完整链** R101–R101R5 | Native realism negative，关闭 |
| MoE routing proxy | Sonic/MonoMoE/serving很强 | **部分** E3 natural/uniform/hotspot + routing资产 | 低优先，需full-op strong baseline才可重开 |
| precision-gated weight updates | PULSE/SparseRL-Sync现象与系统已强验证 | **未做**：R102卡在真实input authority | **值得做boundary**，先真实payload |
| large-vocab loss/backward | CCE/Liger strong software | **未做** | quick falsification候选 |
| lossless compressed execution | ZipServ/UCCL-Zip等强 | **未做直接边界** | 低优先 |
| VLA inference-time gradient/VJP | 算法/系统快速出现，GPU arch层仍较少 | **未做** | **值得做problem discovery** |
| generic DSMEM/cross-CTA | ClusterFusion/CREDIT强 | R101提供过anchor但Native未支持 | 当前无qualified workload anchor |

---

## 13. 下一阶段选择

### 第一优先：VLA / inference-time gradient-VJP workload discovery

理由：
- 它是新的execution shape：推理阶段出现局部反向/gradient guidance，而不是传统forward-only inference；
- 有真实应用关键路径（robot time-to-action/SLO），不是为了体系结构人工制造的算子；
- 外部算法路线分化明显：gradient guidance、gradient-free verifier、training-time conditioning都存在，天然提供反例；
- AWMA完全没有做过边界验证，因此信息增益最高。

但第一轮只做**characterization + strong-software boundary**：
1. 选小型公开policy/critic路径；
2. 固定真实输入/state；
3. native census；
4. 分解forward / VJP-gradient / state materialization / consumer；
5. 检查compile/fusion/checkpointing强基线；
6. 若局部VJP贵但不在time-to-action critical path，STOP；
7. 若training-time/gradient-free方案改变任务合同，作为不同算法路线，不冒充同一合同baseline。

### 第二优先：precision-gated real weight-update detect/compact/apply

理由：
- 现象由PULSE/SparseRL-Sync独立强验证，不需再证明“可能存在”；
- AWMA R102恰好没有真正越过input authority，因此仍是明确的missing boundary；
- 可以先做很便宜的source/payload gate；
- 若拿到真实step-level before/after tensor，则直接比较reference与强fused compare/compact软件。

停止条件：
- 没有真实payload；
- fused software encode/apply成本低；
- 端到端受网络/系统而非GPU-local encode/apply支配；
- 方案仅重复PULSE/SparseRL-Sync/UCCL-Zip。

### 第三：CCE/Liger exact-loss quick falsification（低成本旁线）

不作为主要论文方向，但它是“未验证而且现有资产就能做”的好边界测试。若强软件立即关闭，就用很小成本排除；若意外有material exact-contract residual，再升级。

---

## 14. 当前不建议立即重开的方向

- R101任何后续P2/P3/H1/DSMEM；
- deterministic reduction hardware；
- selector-index handoff；
- generic MoE padding hardware；
- ReplaySSM式state write-back硬件；
- generic cluster/DSMEM机制；
- 再找TLB positive sample；
- lossless compression因为“少访存”就设计硬件。

这些方向不是“学术上已经全部解决”，而是：
**已有直接强近邻 + AWMA已有negative/partial evidence + 当前没有新的qualified residual**。

---

## 15. 本轮方法结论

今后选题默认先问四层：

1. **现象是否真实存在于自然AI执行？**
2. **强软件/编译器/系统方案已经解决到哪里？**
3. **AWMA是否真的测过这个边界，而不是只拥有相关模型/trace？**
4. **剩余成本是否在实际关键路径，并且需要新的硬件能力？**

“我们没有做过”不等于“有空白”；  
“论文没有完全解决”也不等于“值得我们做”；  
只有**外部强基线之后仍有、且AWMA能用真实输入验证的residual**，才进入机制。

本轮建议下一步不立即启动GPU/模拟器机制：
先把VLA/VJP与R102真实payload两张problem-contract写清，再决定第一个执行Goal。
