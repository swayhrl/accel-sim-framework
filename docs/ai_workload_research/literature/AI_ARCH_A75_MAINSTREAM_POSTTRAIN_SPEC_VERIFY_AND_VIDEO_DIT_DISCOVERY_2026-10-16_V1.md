# Round A75｜把体系结构Discovery移到主流RL后训练和生成式视频DiT（同时筛掉旧推测验证动机）

**日期：2026-10-16；执行者：ChatGPT／AI-ARCH Discovery。证据性质：作者原文＋固定开源代码＋CPU算术，不是节点native或仿真。**
**最终状态：两个独立工作量方向值得下一步source核验；当前0个已证硬件headroom、0个GPU准入。** 本轮先审直接近邻，避免A70/A73已经出现的“现有软件功能直接吸收”循环。

科研协调基线：`hrl/ai-workload-research-coordination@05c1722066bda6a079d92fdfca34bdd28249a72f`，发布前compare identical。先前A74-C的SM100固定面积/SFU假说为`PARKED_FOR_PPA_OR_SIM_MODEL`，不因寻找新任务而再申请B200。C16/AWMA/ISCAS、GNN A61/A65/A67、Q-S/ScanNet、3DGS所有独立authority不动。不连109/174/164，无CUDA/模型/模拟器/下载大资产。

## 0. 轮次发现与范围结论

1. **RL后训练（候选R）明显不是已有C16局部静态推理的同一负载。** 一次真实GRPO训练步包含rollout生成、reward/验证、log-prob重算、policy backward/optimizer及权重发布；运行频率和分配方式发生阶段性变化。但是“加快rollout”、“推测解码”、“重叠rollout与训练”、“对齐训练/推理分组”都有强软件直接近邻。剩余要找的是**成熟系统之后仍暴露的计算／访存／并发资源需求差异**，不是重新发明异步调度。
2. **推测解码验证（候选V，暂不独立GPU立项）有作者实测瓶颈，且2026-10-14 vLLM的在线自适应验证已经直接覆盖减少无效verify slots的通用方法。** 后续研究只能在当前有效软件强路径之外找不同层次/语义变量；不能拿2026-03文章的空白当2026-10今日空白。
3. **Wan2.2/主流视频DiT（候选D）拥有与LLM不同的完整工作量：同一时空latent被跨多个去噪步反复处理，A14B的高低噪声专家按阶段更换。** 但TeaCache、Sliding Tile Attention、CacheDit和官方低显存/并行实现均为直接软件反证。值得先追**固定真实模型、时间步／输入与质量允许边界下的GPU计算组织残余**，不能将“跳过去噪步”视为语义不变的硬件加速。

仅准备R/D两条CPU/source独立审查；V在本报告只保留为交叉强近邻，避免三个Codex重复研究EAGLE/AV。没有自动启动新Codex，真正的前置合同另见A75 Goal包。

## 1. R｜真实GRPO后训练：作者native阶段分母

论文：[Accelerating RL Post-Training Rollouts via System-Integrated Speculative Decoding](https://arxiv.org/html/2604.26779v1)（2026-04-29），以及[NVIDIA的逐实验解释](https://research.nvidia.com/labs/nemotron/rl-speculative-decoding/)。

**真实执行实验组：**
- Policy：RL-Think为Qwen3-8B、RL-Zero为Qwen3-8B-Base；训练prompt来自DAPO-Math-17K，验证为AIME-2024。**这些是作者选择的实际训练对象，并非本项目109上的accepted模型/数据。**
- 系统：NeMo RL + MegatronLM训练／vLLM rollout；8节点×每节点4 GB200 NVL72 GPU（作者写每GPU186GB），GRPO；EAGLE-3 draft通常离线以同训练域初始化，长度k=3。模型变化时rollout权重需要同步。paper Table1是**作者native训练步**而不是GPU模拟结果。
- Table1逐步时间（秒，取各训练step均值）：RL-Think AR: Data0.3/Prepare2.1/Generate133.6/Logprob17.9/Train31.4/**overall185.3**；EAGLE-3:0.2/1.6/87.0/18.1/30.5/**overall137.4**（1.35×）。RL-Zero AR:0.2/1.9/100.0/17.8/31.3/**overall151.2**；EAGLE-3:0.2/2.1/56.6/18.1/30.5/**overall107.5**（1.41×）。
- 作者同实验组的n-gram即使RL-Zero可接受长度2.47，其generation从100.0s升至140.2s；RL-Think acceptance2.05而generation262.9s，不能把接受长度直接当性能收益。文中k5、k7对RL-Think回归到低于AR，若未来研究需固定draft policy/权重和k，不能为了看好压榨输出差异。
- 原生质量图示作者认为AIME accuracy曲线近似，推测解码理论上遵循verifier策略；**这不是本项目独立相同seed逐token/梯度复现**。在线draft训练可复用Megatron forward的detached hidden states以训练drafter，但这不等于policy backward activation零成本。

**极关键分母：** 这个原生组中单是生成优化后的RL-Zero 56.6/107.5=52.65% step仍在generation，Logprob+Train=48.6s（约45.2%）。RL-Think相应为87.0/137.4=63.32%，Logprob+Train=48.6s（约35.37%）。这是真实*作者不同阶段的时间比*的再次算术归纳，**不能等同于单张GPU的SFU/TC/HBM占用或建议芯片资源比例**。长尾输出、reward、权重拷贝和异步策略可改变全局关键路径，不能将同步阶段分摊到完全重叠系统上。

作者§4对235B/512或2048 GB200的加速使用**proprietary kernel-aware性能模拟器**而非同规模完整RL native；“235B RL训练2.5×”必须标`AUTHOR_SIMULATED_PROJECTION`，不可用本项目Accel-Sim的卡名套入或称109已测。

### R直接强软件反证

- [RolloutPipe，arXiv2606.26997v2](https://arxiv.org/html/2606.26997v2)：真实Qwen3-1.7B/8×RTX4090训练＋2×A100 rollout（**两个GPU pool**）、K8、R=32/64/96、4组科学/逻辑任务；complete-group pipelining (CGP)与frontier group dispatch (FGD)在完整group合法完成后开始训练；作者rollout→train-end缩短30.7–42.3%，不是完整8B单卡训练step、也不是硬件资源替换。用K8组均值/方差算GRPO advantage，不能从单条response完成就提前做同一组的合法策略更新。
- [NeMo-RL源码@540d2568](https://github.com/NVIDIA-NeMo/RL/blob/540d2568c9cd184e01964c7de0a42026334f0a38/docs/guides/eagle3-speculative-decoding.md)，Git blob`cb8285334ba3eff9799eb4ae5c702f871b2bb233`：online/offline EAGLE-3已集成；与当前[grpo_sync.py](https://github.com/NVIDIA-NeMo/RL/blob/540d2568c9cd184e01964c7de0a42026334f0a38/nemo_rl/algorithms/grpo_sync.py) blob`cdb5f9471c6e73f98be58dac4150cc5bdfa26be5`已有独立的同步TransferQueue路径；**不能声称NeMo完全不支持分段回传/异步/推测**，同时源存在不代表每个模式同时开启。
- [Libra RL固定源码@506a54](https://github.com/NetX-lab/Libra/blob/506a54edf3854fbf25537a758707df83a623e1c2/README.md)把train、rollout和elastic混合池分开，global planner联合选择训练/推理并行度，工具完成事件指导bucket scheduler；源能力直接覆盖通用弹性pool主张，**需要审对应原文GPU实验，不能借README复制最高倍数**。
- [HetRL MLSys2026](https://proceedings.mlsys.org/paper_files/paper/2026/hash/5321b1dabcd2be188d796c21b733e8c7-Abstract-Conference.html)已研究异构GPU/网络的RL训练配置与受限调度。原厂摘要的3.17×平均改进是作者不同工作负载/硬件对照，不代表定额单RTX4080资源协调。
- [AReaL v5](https://arxiv.org/abs/2505.24298)研究异步生成与训练，策略滞后/质量约束需要独立合同；不同于同步合法group。不能把异步造成的不同参数版本训练结果冒充“同训练语义无代价加速”。

**R剩余问题（暂仅候选）：** 把本组中不同阶段放回*当前最强合法优化组合*后，是否存在可量化的、超出调度/算法必需工作与不同设备部署的**GPU内生资源服务限制**？必须区分阶段wall占比、全GPU忙闲（不同pool不能相加）、组等待、batch内输出长度，以及政策版本/训练质量；需要本机/未来平台的真实样本和不改变GRPO同组梯度/权重边界的最小反证。不能由表格自动晋升一个新可变TC/DRAM资源架构。

输入入口：官方[DAPO-Math-17K数据卡](https://huggingface.co/datasets/BytedTsinghua-SIA/DAPO-Math-17k)当前标Apache-2.0和文本问答；**卡页面展示的split行数与名字17K不等价**，必须冻结官方文件revision、原作者采样、mask及tokenizer，而不是按名称任意取17K行或将公开内容等同已授权/已下载。本文未取得真实原始数据SHA、没有启动训练或评估任务。

## 2. V｜推测解码验证：2026-10-14强软件已覆盖一般动态预算

- [Speculative Decoding: Performance or Illusion? arXiv2601.11580v2](https://arxiv.org/html/2601.11580v2) §3,§5：作者在vLLM0.10.1.1、H100 80GB（8B 1GPU、70B 4GPU）、Qwen3-8B/Llama3.1-8B/Llama70B/GLM106B，六种任务含ShareGPT/InstructCoder/GSM8K/AIME等对比SD变体及batch。CNN/DailyMail的500请求执行分解中验证占SD各方法总执行42–95%，draft对小模型负担可大幅不同。这个是**AUTHOR_NATIVE_SERVING**，不是RL训练stage；由于温度0条件下批次变更仍有数值生成长度离散，作者用tokens/s而非默认固定Nout时延，注意请求质量和分母。
- 同一作者§8提出oracle只验证最终被接受的token与基于各位置接受率切换策略；这种oracle包含未来信息，不是已实现硬件加速或合法same-output机制。SpecDecode-Bench发布了[作者profiling code](https://github.com/SpecDecode-Bench/vllm)，不是我们需要再写一次profiling框架的理由。
- **关键时序反证：** [vLLM 2026-08-14自适应验证介绍](https://vllm.ai/blog/2026-08-14-dspark-adaptive-verification)及[2026-10-14在线无confidence-head估计器](https://vllm.ai/blog/2026-10-14-adaptive-verification-online-estimator)已实现根据per-token acceptance置信与当前batch负载缩短verify长度。固定[vLLM@9a16d43e](https://github.com/vllm-project/vllm/blob/9a16d43ef0413b0a2a222e7f5baa4498c291ae5b/docs/features/speculative_decoding/adaptive_verification.md) blob`d560b5af3e4faf8ff4cf7c64b9e9a429d13a7923`说明EAGLE/MTP/DFlash/DSpark等的在线估计与适用边界；[speculator实现](https://github.com/vllm-project/vllm/blob/9a16d43ef0413b0a2a222e7f5baa4498c291ae5b/vllm/v1/worker/gpu/spec_decode/speculator.py) blob`c54df5ac17c777dd084a003cf0b3bc1e7426ba6e`确实按开关构造`OnlineAcceptanceEstimator`。
- 自适应验证不是无条件总开：需要可变长attention/全CUDA Graph与兼容配置；FP32等数值核可能有差异，输出概率语义受限；该方案的作者B300 DeepSeek V4配置不是109/4080或NeMo Qwen3-8B现成基线。**但一般“少验证低置信token”已属SOFTWARE_NEARBY_DIRECT，不能新设计相同调度作为硬件机制。**

**V结论：** 对通用验证预算/树形宽度选择，暂`SOURCE_ONLY_DIRECT_SOFTWARE_PRIOR`，不新增独立Codex/GPU任务。只有新的机制层输入，例如当前合法强路径下由特定GPU执行限制产生的独立剩余wall且直接近邻没有覆盖，才可恢复。不能仅因vLLM某SKU不兼容就认定硬件瓶颈。

## 3. D｜视频扩散Transformer：主流但不同于LLM Prefill/Decode

官方[Wan2.2 fixed Git commit 1ea34ff](https://github.com/Wan-Video/Wan2.2/blob/1ea34ff48f87168174e12956e200b1d908b1c5ff/README.md)，Git blob`c656fa3b1d124935b7190845ac88764157f09f88`：

- Wan2.2-TI2V-5B提供真实文本生成视频与图生视频的完整模型/代码；官方说明单GPU720P 1280×704 offload/T5_CPU/转换dtype需要**至少24GB VRAM（4090级）**，因此109 RTX4080/16GB不得直接等价当作该官方高画质完整输入的无裁剪GPU运行平台，也不自动下载权重。
- 14B A14B的所谓MoE是**跨去噪噪声阶段切换高噪声和低噪声专家**，不同于Qwen MoE每个token TopK路由；不能把C16 E3专家直方图复制为视频路由证据。作者官方单卡14B部分配置有80GB需求，多卡含FSDP/Ulysses，不把全链成本当一个简单kernel。
- 单次生成是多step去噪→文本/VAE/条件控制→每step多层DiT，其软件组织有时序、空间、跨step状态及输出质量四重合同；随机噪声seed是生成输入一部分，不可仅按同prompt比较延迟而忽略实际图像视频质量。

**直接已有强软件：**
- [TeaCache CVPR2025](https://openaccess.thecvf.com/content/CVPR2025/html/Liu_Timestep_Embedding_Tells_Its_Time_to_Cache_for_Video_Diffusion_CVPR_2025_paper.html)训练免费基于timestep embedding变化选择缓存/跳过部分计算，作者Open-Sora-Plan组报告最高4.41×和VBench差-0.07%；**不是Wan2.2质量/完整同配置实验**，且跳过模型计算可能影响采样输出，不能作为数值逐bit相同的硬件替换。
- [Sliding Tile Attention，ICML2025](https://proceedings.mlr.press/v267/zhang25m.html)已对HunyuanVideo类3D attention直接提出GPU tile级局部性与内核，作者宣称对Hunyuan的FA3 attention局部1.6–10×、end-to-end 1.36–3.53×（质量/工作量合同具体实验另审），不能把“第一次发现3D时空局部性”当创新。
- 官方Wan2.2 README列有Cache-DiT的DBCache/TaylorSeer/Cache CFG及DiffSynth-Studio的层级offload、FP8、sequence parallel；这些是**README所指软件能力**，不代表全都在Wan2.2的同一版本同时合法启用或没有数值/质量代价。
- [BWCache ICLR2026](https://openreview.net/pdf/8689bfed983875d218851fe827d2e03157cc4ab5.pdf)说明DiT block级跨step缓存已进入直接近邻；本轮只读公开摘要，未系统审其原视频/硬件实验组或质量指标，不能直接说它胜过TeaCache。

**D剩余研究入口（待下一轮源码审查）：** 在官方真实模型/相同质量需求下，去噪step数与噪声区间、A14B专家阶段切换、模型有效工作集、Attention执行layout与数据搬运是否形成无法被现有缓存/Tile/Offload/融合充分解决的**必要计算**与资源竞争？必须先确认是否改变生成数值路径：不允许以“跳过更多step”提升吞吐后再宣布片上Cache硬件space。未来可选**5B真实入口优先**，但不因10916GB装不下原设置就擅自降分辨率/帧数当官方同任务。

## 4. 交叉排序、最小探针与止损

| 类别 | 主流性/来源资格 | 直接近邻 | 本轮阶段 | 下一步否定方式 |
|---|---|---|---|---|
| R / RL posttraining | Qwen3-8B GRPO真实作者native、合法公开任务入口 | NeMo RL spec、RolloutPipe、AReaL/Libra/HetRL | `SOURCE_QUESTION_FOR_STAGE_CENSUS`，未选机制 | 同训练参数/同组/权重与强软件后，剩余只归异步排队、组截止、算法必需工作或普通backend；关掉硬件提案 |
| V / SpecVerify | Qwen3/Llama大模型H100 native论文与当前vLLM | vLLM DSpark AV、online estimator | `SOFTWARE_NEARBY_DIRECT / PARKED` | 强AV后不存在新的合法验证成本变量，停止，不凭理论oracle申GPU |
| D / Video DiT | Wan2.2真实视频生成模型与官方采样路径，但无本机样本 | STA、TeaCache、Cache-DiT、官方offload | `SOURCE_QUESTION_FOR_NATURAL_STEP_LIFETIME`，未选机制 | 强软件＋不改变视频质量和模型工作量后，原差异由跳步、降分辨率、offload包装或软件kernel解释，停止 |

**下一轮并行：** 一条R核NeMo/RolloutPipe/Libra的*精确训练步阶段资源分母与正确性*；一条D核Wan2.2*自然steps/专家切换/内存和强视觉质量基线*。每条可0问题，不是要求通过。两者独立且不重复；将来如存在1—2个候选，再统一为最小测量资格，不因文献阅读0候选重发四个同质窗口。

不得访问164扫描资产、接受第三方数据许可或启动真实GPU/模型/模拟器。任何future NATIVE_PROBE只是另行批准的合同，不从本A75报告自动发放。

## 5. 主要固定身份与披露

- NeMo RL `NVIDIA-NeMo/RL@540d2568c9cd184e01964c7de0a42026334f0a38`（2026-10-16 05:12UTC前），guide Git blob`cb8285334ba3eff9799eb4ae5c702f871b2bb233`。
- vLLM `vllm-project/vllm@9a16d43ef0413b0a2a222e7f5baa4498c291ae5b`（2026-10-16 09:54UTC前）；adaptive_verification文档及speculator源码 Git blob如§2。
- SpecDecode-Bench `SpecDecode-Bench/vllm@f967d11c99867e893361b612ef575ed8605e5d4f`；没有本机跑作者profiling。
- Libra `NetX-lab/Libra@506a54edf3854fbf25537a758707df83a623e1c2`，README blob`8eb6ee9692082e36079be7af8c145cbe18fc657b`。
- Wan2.2 `Wan-Video/Wan2.2@1ea34ff48f87168174e12956e200b1d908b1c5ff`；TeaCache `ali-vilab/TeaCache@7c10efc4702c6b619f47805f7abe4a7a08085aa0`。
- 引用结果严格维持作者实验与控制端算术之分。NeMo 235B结果为作者模拟；RolloutPipe train pool为8×4090而rollout 2×A100；SpecDecode H100结果为served requests非RL；TeaCache原对象Open-Sora-Plan非Wan；STA原对象Hunyuan不是Wan2.2；不将软件能力当实际111平台验收。
**A75终态：证据已支持转向R/D两个有别于旧LLM serving/SM100资源问题的source-only候选，当前没有新硬件机制或GPU授权。**