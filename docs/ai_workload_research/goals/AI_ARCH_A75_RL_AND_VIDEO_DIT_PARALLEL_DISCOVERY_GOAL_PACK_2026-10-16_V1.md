# Round A75｜RL后训练与视频DiT双线轻量Discovery（独立Codex Goal包）

**日期：2026-10-16；准备者：ChatGPT；状态：READY_FOR_USER_DISPATCH、NO_GPU_AUTHORIZATION。** 文档和Git分支准备不等于节点Codex已运行。仅用户给对应窗口发起固定HEAD的Goal指令并取得回执才进入RUNNING。

## 0. 背景、源与科学去重

科研起点：2026-10-16主流大模型协调HEAD `05c1722066bda6a079d92fdfca34bdd28249a72f`；本轮研究笔记`docs/ai_workload_research/literature/AI_ARCH_A75_MAINSTREAM_POSTTRAIN_SPEC_VERIFY_AND_VIDEO_DIT_DISCOVERY_2026-10-16_V1.md`已完成；两线的共同固定启动commit须使用**包含本Goal本身**的明确SHA，由协调者在派发时填写。后续CURRENT_STATE变动不改变Goal起点。

先读A75研究笔记0/1/2/3/4节并只读查：`docs/ai_workload_research/CURRENT_STATE.md`、`COORDINATION_PROTOCOL.md`1—8、A72四线综合或A74-C最后状态相关条目。不能直接把A70的四条0候选理解成LLM领域已否定；但也不能重做A70的serving队列/混合KV/专家分组/视觉编码缓存或A74的MUFU资源配比。

**共同目标：** 对不在原A70/A74 scope中的主流生成AI负载，先固定原模型、自然任务、准确性/质量要求、成熟强软件与可测量时间分母，寻找0—2个最小可证伪的架构机会或如实给0，不以论文数量或工程完成度强求阳性。

## 1. 两个无数据依赖的独立Lane

| Lane/建议节点 | Git branch（协调者准备） | 独立输出前缀 | 唯一研究主轴 |
|---|---|---|---|
| **R-A75／node109** | `hrl/aiarch-a75r-rl-posttraining-discovery-109-v1` | `docs/ai_workload_research/discovery/A75_R_RL_POSTTRAIN/` | 主流Qwen3 GRPO真实rollout／reward／logprob／训练与权重发布的完整阶段资源；强NeMo/RolloutPipe/Libra后是否有独立硬件约束 |
| **D-A75／174-new** | `hrl/aiarch-a75d-wan22-video-dit-discovery-174new-v1` | `docs/ai_workload_research/discovery/A75_D_WAN_VIDEO_DIT/` | 主流Wan2.2真实视频DiT跨去噪步与专家噪声阶段；强STA/TeaCache/Cache-DiT/官方offload下的数值质量和GPU资源 |

R不再泛泛调研vLLM speculative acceptance（A75已经确认2026-10-14 AV直接覆盖）；D不调视频多模态理解模型（A70 P研究的是Qwen3-VL）；D也不把14B跨step高低噪声专家混同token路由MoE。两个Lane相互独立，**不等待另一Lane或修改对方输出**。协调者收到哪条回执就先审哪条。

## 2. 轻量执行资源及不可越线边界

- 每Lane工具CPU worker≤1，实际进程树RSS≤2GiB、新增盘≤128MiB、公开论文/源码/模型卡下载累计≤64MiB、90分钟内完成（提前闭合提前STOP）；同一节点已有其它活动，资源不足或只读内容不可得则`RESOURCE_DEFERRED`，不抢GPU/锁或抢其它任务。只读外部GitHub/HF元数据与原作者HTML/PDF。
- **GPU/CUDA初始化/JIT/torch/vllm/SGLang模型import或调用、权重/真实文本或视频数据集下载、安装/构建、Profiler、任何模拟器运行、164访问、资产清理/缓存更改全部禁止。** 阅读PyTorch/CUDA源码文本可以，不能import运行或编译。本Goal绝不因“source缺GPU证据”默默申请资源。
- 独立sparse worktree、专用tmp/output、git branch和输出前缀；不得并发写共享`CURRENT_STATE`、共同manifest、问题图谱、A70/A73/A74原材料或AWMA/C16/ISCAS任何内容。读旧Git commit/text，不拷贝模型盘，不执行Git clean/gc/repack/reset；OMP/BLAS、Git pack/index设置单线程，不修改全局配置。
- 原论文涉及模拟器/投影，应将`AUTHOR_SIMULATED`与`AUTHOR_NATIVE`分开；架构资源hypothesis不可凭GPU利用率标题或logical bytes直接定性。论文未披露就写NOT_DISCLOSED；只有完整实验组/数据配置才可量化。

## 3. R-A75精确科学任务：GRPO完整训练步骤再评估

**自然对象**：先固定NeMo RL官方论文`2604.26779v1`的Qwen3-8B RL-Think（Qwen3-8B）与RL-Zero（Qwen3-8B-Base）、DAPO-Math-17K、AIME-2024，硬件32×GB200；从已读Table1的Data/Prepare/Generation/Logprob/Training/Overall逐项核作者原文数值与控制项。不能为了4080自动改成任意缩维。另至少核RolloutPipe Qwen3-1.7B 8×4090训练/2×A100 Rollout的合法K8完整group与R32/64/96边界；作者两个不同模型/系统不形成可相加的一个强系统。

**必须补的source审计：**
1. [NeMo RL固定源码](https://github.com/NVIDIA-NeMo/RL/tree/540d2568c9cd184e01964c7de0a42026334f0a38)中的speculative Eagle3 guide、GRPO actor、policy logprob、weight refresh、同步/异步路径，确认能否共用/互斥，不要把存在的可配置功能拼成无条件同一运行实例；rollout K、accuracy、token count/quality和训练数据窗口应同一科学状态。
2. RolloutPipe、Libra、HetRL、AReaL等选择其中最直接的**2—4个论文×实验组**，核是否已有固定rollout/training GPU资源池比例、权重同步和on-policy group pipelining。不能将同步系统的空闲训练GPU叫作SM/L2硬件瓶颈。
3. 找一个明确的**阶段服务量/计算状态变量**，诸如真实输出长度长尾、不同step的generation占比/训练微批、权重版本推进、policy lag；必须说清新的模型/训练语义与三组相反解释（纯排队、强软件分配、实质设备级资源需求）如何区分。
4. 给最多**1个**推荐问题，另最多1个备选；若全部属于软件调度则0。最小实验包括合法数据、冻结模型/梯度/采样、强软件具体可兼容版本、baseline、真实阶段诊断、holdout、否定条件；资源需要32GB/多GPU时说明为何必需，不能伪称10916GB可做32GB200 Qwen完整训练。A75的235B模拟预测不是原生GPU性能；不要新跑NeMo。
5. 突出**是否确有芯片内架构约束**而非RLOutput等待；决定是否该停在软件研究。如果只是一种新pipeline名称没有完整step/GPU因果证据，报告`SOFTWARE_NEARBY`并STOP。

交付四份：`REPORT.md`、`STAGE_EXPERIMENT_GROUPS.tsv`、`QUESTION_CARDS.json`、`RECEIPT.json`。0—2卡，要求主要分母清楚、作者claim与我们推断分开；不能将作者最终质量曲线说成逐step证明bitwise同轨迹。

## 4. D-A75精确科学任务：真实视频DiT的自然完整生成

**自然对象**：官方`Wan-Video/Wan2.2@1ea34ff48f87168174e12956e200b1d908b1c5ff`，先优先TI2V-5B（dense、原720P生成官方要求≥24GiB且offload等）、再以A14B高/低噪声专家切换作为机制变更对照。只读模型配置、generate.py、denoise调度、DiT block和专家切换以及公开默认video长度、prompt/seed/输入质量说明，固定文件blob，不运行生成。**5B和A14B不是同一模型结构，跨模型对照不是一个无损expert开关。**
1. 追每轮step是否有真实可复用的中间结构和同步/跨step依赖；界定不同timestep、latent形状、视频帧数和输出质量如何改变输入和工作量，不拿重复same prompt随机视频当自然分布。
2. 精审[TeaCache CVPR2025](https://openaccess.thecvf.com/content/CVPR2025/html/Liu_Timestep_Embedding_Tells_Its_Time_to_Cache_for_Video_Diffusion_CVPR_2025_paper.html)、[Sliding Tile Attention ICML2025](https://proceedings.mlr.press/v267/zhang25m.html)、[BWCache ICLR2026](https://openreview.net/pdf/8689bfed983875d218851fe827d2e03157cc4ab5.pdf)与官方列Cache-DiT实现中的最直接**2—4组**：输入/分辨率/帧数/steps/模型、质量VBench或其他、完整time vs局部kernel、硬件、precision、缓存初态与算法变化；不能把TeaCache Open-Sora数字当Wan2.2实测。
3. 区分**任务质量/近似算法**（跳步、稀疏attention、缓存旧特征）与**相同生成计算合同的执行优化**（等价重新排布/内存事务、优选kernel、SMEM占用）；前者需要质量对照，不可当硬件无损上界。确认官方FFN/attention/T5/VAE/CPU offload及多GPUUlysses准备时间分母，不能只测denoiser kernel冒充整视频成本。
4. 一个可否定的具体自然资源候选即可（至多1推荐1备选），也可0：例如在强算法方案完成后不同denoise噪声区间，实际GPU执行是否存在额外的片上服务/同步/带宽/资源映射成本；但**尚未测到**，不能先命名“时空cache硬件”。先验若官网>=24GB则不自动在4080缩帧/分辨率/降精度作相同任务。列未来强软件+自然完整generation baseline与诊断/holdout/STOP。
5. 用户明确优先主流大模型；必须证明Wan2.2是真实通用视频生成模型而非重新落回ScanNet专用点云。若与LLM主线相比研究价值不足，诚实`PARKED_BELOW_MAINSTREAM_LLM_PRIORITY`。

交付：`REPORT.md`、`VIDEO_MODEL_AND_PAPER_GROUPS.tsv`、`QUESTION_CARDS.json`、`RECEIPT.json`。

## 5. STOP、科学结论和用户回执

每Lane终态：`SOURCE_QUESTION_READY_FOR_CROSS_REVIEW`、`SOFTWARE_NEARBY_NO_SURVIVOR`、`SOURCE_INCOMPLETE`、`DATA_OR_QUALITY_INCOMPLETE`、`RESOURCE_DEFERRED`。不得输出`NATIVE_SPEEDUP`、`HARDWARE_HEADROOM_PROVEN`、`PERFORMANCE_NEGATIVE_MEASURED`或未经授权GPU Goal。

每Lane完成后**只**提交自己的4份文件至独立执行branch，push/fetch-back exact commit/tree/blob SHA、worktree clean；如平台实际能力不支持其中步骤，诚实记录部分成功和阻断。不得轮询等待另一Lane，结果报告即STOP。ChatGPT统一独立审查，跨线去重，只对确有新变量和可区分解释的题再准备原生合同；不自动开始模型下载或租机。

**本A75 Goal包本身不创建109或174的真实Codex运行。用户派发后再登记RUNNING。**