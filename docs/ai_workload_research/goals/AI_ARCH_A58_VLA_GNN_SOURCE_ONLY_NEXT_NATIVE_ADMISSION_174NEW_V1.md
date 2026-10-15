# AI-ARCH A58｜VLA多请求与GNN供数下一真实AI负载：联合CPU/source-only资格

**状态：APPROVED_FOR_ONE_BOUNDED_CPU_SOURCE_GOAL / READY_FOR_CODEX，尚无实际执行回执。** 用户已同意AI-ARCH Discovery持续推进及已审边界下默认确认、减少人为轮次。A57独立审查决定当前固定GloVe CAGRA质量门下的GPU性能未获准，**不重复运行109、不续投GPU排故**。A58只验证下一项**真实AI模型**能否构成合法、强软件之后仍可证伪的GPU发现实验，**不授权真实GPU实验或数据/权重下载**。

- Repo：`swayhrl/accel-sim-framework`
- Branch：`hrl/aiarch-a58-vla-gnn-source-admission-174new-v1`，发布Goal后的完整固定HEAD为启动点，parent`b1558eb4f9f2f74308f011a1afe4d6a65c7e7e96`。
- 执行者：node174-new新独立Codex窗口/工作区（可复用此前已STOP Lane N聊天，不使用其旧worktree）；**CPU/source-only**。如果174的AWMA/C16有正式资源占用或swap压力，缩小到1 worker或`RESOURCE_DEFERRED_STOP`，**不得挤占AWMA/GPU109**。无109/164访问、无GPU共享锁触碰。
- 先读：`docs/ai_workload_research/COORDINATION_PROTOCOL.md`、`CURRENT_STATE.md`、[A51–A55联合Discovery](https://github.com/swayhrl/accel-sim-framework/blob/8502b7dcecc28b4762ffcb03afcabb11026a2436/docs/ai_workload_research/literature/AI_ARCH_A51_A55_CROSS_DOMAIN_AI_WORKLOAD_DISCOVERY_2026-10-15_V1.md)、[A57 A50G QUALITY_NO_GO审查](https://github.com/swayhrl/accel-sim-framework/blob/b1558eb4f9f2f74308f011a1afe4d6a65c7e7e96/docs/ai_workload_research/reviews/AI_ARCH_A57_A50G_RECOVERY_QUALITY_NO_GO_INDEPENDENT_SCIENCE_REVIEW_2026-10-15_V1.md)。本任务不要重审A47–A50G的GPU结果，只确认已STOP。

## 0. 唯一决策问题与硬资源

**Q-A58：** 在**不下载权重/数据、不安装软件、只读固定公开源码/元数据**的范围内，Q-V（SmolVLA机器人动作推理）与Q-G（GraphSAGE真实节点分类供数）哪个能够以更低成本形成真正可执行、非稻草人强软件之后有意义的下次**一个**RTX4080发现性合同？二者都不合格时输出`NONE_SELECTED`，不硬选“GPU上跑个东西”。

执行封顶：174-new CPU≤2有效workers、单任务RSS≤3GiB、新增Git/本地tmp≤40MiB、准备用时≤2小时，进程/worker无真实torch.cuda/CUDA上下文调用；**GPU/CUDA/NCU/NSYS/NVBit/模拟器/模型推理/下载权重、science dataset或PDF大包/安装/编译/新模拟器机制都为0**。公开GitHub/HF read-only代码与许可/文件大小元数据可访问，禁止传输实际weight shard和episode数据。不得触碰109锁、原A50G index、AWMA/C16冻结branch。Source-only缺口允许`NOT_DISCLOSED`/`UNKNOWN`，不为完美材料重复整套文献调研。

## 1. G0｜仅审阻塞资格的固定来源

优先复用已确认固定码：
- VLA：`huggingface/lerobot@53feaef37b67e8f4c23b6953e880ff535e39d6fe`，`src/lerobot/policies/smolvla/modeling_smolvla.py`和`smolvlm_with_expert.py`；`VinRobotics/vla.cpp@cff0cfb5e9e6cab31671d46082f7bdbff078816e`，`docs/ARCHITECTURE.md`、`docs/USAGE.md`、`src/serving/vla-bench.cpp`、`src/serving/server.cpp`。已知`vla-bench`输入合成、`vla-server`单线程REP的`recv→predict→reply`排队，不是多个模型阶段GPU并发；LeRobot已有prefix KV reuse与flow多步。最近邻KerColle PACT26已研究VLA CTA/HOL co-schedule，ICML26已有DP-Cache/V-AEFusion。无需重复推演已被覆盖的机制。
- GNN：`dmlc/dgl@3d16000b4170fa741ed9e9667f22ba84d3493026`的GraphBolt`neighbor_sampler.py`、`gpu_cached_feature.py`、`gpu_graph_cache.py`；另一合法强实现可能是当前`NVIDIA cuGraph-PyG`，**固定具体可用版本/接口**而不将跨库API相同当成结果相同。真实数据`ogbn-products`官方节点2,449,029、无向边61,859,140、100特征、47类别，sales-rank train/val/test，loader双向边数、feature dtype需精确绑定。现成GPU图/特征缓存、UVA和async已经有，不能提出“新热点Cache”作为未有软件的空白。
- ESA/SLGS最近邻公开正文如权威来源可直接获得可附加一段，不成为本Goal必要门；没有全文即按`PROGRAM_ONLY`登记。

## 2. G1｜优先VLA：真实模型、输入、强路径与“真GPU并发”资格矩阵

只用read-only发布元数据核：
1. 一个明确SmolVLA**模型/checkpoint lineage**（优先官方且许可允许）与可能GGUF转换版的源commit、权重文件名/大小、precision、量化、模型参数/flow steps/action chunk、tokenizer/camera/state的身份；**“GGUF可能可用”不等于原PyTorch模型bitwise等价**。缺输出一致性证据标UNKNOWN，按各自输入语义合法性决定能否组成强对照，不能跨dtype/权重/模型默认值硬比。
2. 至少一种合法可获取的**真实机器人观测/指令/状态**样本或公开LIBERO等episode（本次只查看file manifest/license/schema/时间字段，不能下载帧和episode），锁定B1相机数量/分辨率、自然action solver steps、每个请求的preprocess/模型完整执行/返回动作语义。真实action success无任务环境测量时标`NOT_MEASURED`，不能宣称策略成功率。
3. 一条已经存在的、无需大改模型算法的**真正多请求GPU overlap**路径：提供可核的源码入口，使两个独立请求的VLM-prefill和action expert在GPU上可能同时执行；普通多线程客户端连到单REP server不满足。对强基线以公开最成熟queue/reorder/async policy与相同截止期、输入、输出质量比较，不把单请求session vla-bench做跨请求调度实验。若无现成合法并发入口，记录`SERIAL_SERVER_NOT_A_GPU_CONCURRENCY_BASELINE`，VLA可转回单请求phase characterization但**本Goal不批准做它的新GPU实验**。
4. 给出唯一可以直接观察/验证的三个边界：`predict total`，`prefix/expert phase`，`request arrival→reply complete`；数据时间戳、队列等待、实际GPU互斥/并行的证据权属。未访问109，GPU concurrent overlap仍`UNQUALIFIED`，不得说“已发生”。

**VLA PASS只意味着下一原生canary“可以有界尝试”，不等于已具备真实资源收益。** 如果强软件已覆盖全部想法或只有合成输入，则`VLA_NO_GO_OR_PARTIAL`。

## 3. G2｜GNN：原采样分布、特征供数与完整训练步

选择单个GraphSAGE+`ogbn-products`真实任务及精确GraphBolt/cugraph版本；以静态入口核`fanout,layers,batch,seed,replacement,feature dtype,device,original split`、checkpoint/训练语义，不能随机换图/label/输入变造真实程序。

强基线至少包括**软件已经可用的**GPU graph cache、GPU feature cache/valid fallback、异步sample/fetch overlap（新版本可用且真实合法时才启），以及实际完整`neighbor sampling→feature ready→forward/backward/update`流水。明确其内存/host pinning/占用边界，禁止把\`overlap_fetch=false\`当现成最强实现。比较不同GPU采样系统时需要语义/分布和质量控制，不要求无意义的逐bit邻居身份但应保证统计等价和训练任务有效性。

单个未来低成本probe应能区分：离散sampling开销、miss fallback、被overlap隐藏的GPU/CPU等待、露在训练step critical path的真实headroom；没有训练数据/库版本/数值/自然批次资格则\`GNN_PARTIAL\`。本Goal**不下载**OGB数据或训练GPU。

## 4. G3｜一次收敛、不给长期工作台铺路

一张最多2页的\`Q-V vs Q-G\`科学投资矩阵：model/input/licence/bytes/version×完整native wall×数值质量×最强软件×现有实现可并发性×109 Ada 4080 ABI与GPU/Host预计容量（估算必须标\`ESTIMATE\`、没有本机实测标UNKNOWN）×独立holdout/负例×STOP成本。

最终仅三类状态之一：\`SELECT_VLA_CONDITIONAL_GPU_PROBE\`、\`SELECT_GNN_CONDITIONAL_GPU_PROBE\`、\`NONE_SELECTED_OR_SOURCE_GAP\`。若选择一个，只提出**一个**最小未来GPU experiment合同草案：一份真实输入、至多两条强路径、≤12个发现点建议、同语义合法数值/质量gate、完整request/step wall、GPU lock/盘/RAM/下载建议上限、明确negative STOP；所有上限只是\`PROPOSAL_NOT_AUTHORIZED\`，不得自动下载或启动。**不要开发GPU runner或把模型转换成GGUF，本轮只做科学资格判断。**

成果仅在该独立branch增加：
`docs/ai_workload_research/reviews/AI_ARCH_A58_VLA_GNN_MINIMUM_SOURCE_ADMISSION_174NEW_V1.md`（≤250行，核心结论+含证据等级的表）及确有必要的≤1MiB小型manifest CSV/JSON。不修A51–A55历史报告、不改coord、C16/AWMA、旧A50G。普通引用/path/manifest小问题有界solve-and-continue。科学语义无可比性、权限/资源不合时合法标UNKNOWN/STOP，而不是为追求完整PDF下载/运行模型。

Commit、push、fetch-back exact commit/tree/报告blob及SHA、clean后**STOP**。任务成功仅表明source/asset身份许可及下一GPU候选，不保证实际109运行合法，也不产生硬件cache/SMEM结论。