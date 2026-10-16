# Round A76｜A75 R/D真实大模型后训练与视频DiT双线独立审查及Discovery方法复盘

**日期：2026-10-16；审查者：ChatGPT／AI-ARCH Discovery；性质：连接器远端Git身份、作者固定源码与原文HTML、纯整数算术的独立审查。**

**总裁决：分别接受R、D原终态`SOFTWARE_NEARBY_NO_SURVIVOR / STOP`，后缀`SOURCE_SCOPE_ACCEPTED_NOT_NATIVE_NEGATIVE`。** R与D各为0个主/备选，没有自然同语义强软件之后的可归因芯片内剩余瓶颈，不自动创建新GPU或模拟器任务。两个0不是整个GRPO/RL后训练、视频DiT或大模型的硬件机会被否定；它们只排除了本轮具体弱假说，并提高后续合法资格边界。

## 0. Git执行与证据结构独立核验

共同A75固定Goal：`1eb14b0395bc898c3707ba850c36f17a9ec07b4e`，原科研协调`05c1722066bda6a079d92fdfca34bdd28249a72f`。

| Lane | final commit | Git tree | 原报告与任务类型 | 结构审查 |
|---|---|---|---|---|
| R / 109｜Qwen3 RL posttraining | `8e53641295068cdef653362d0f8d7f441c636b11` | `8861ec3174330260b8faaa205e80efca80183f69` | [R固定REPORT](https://github.com/swayhrl/accel-sim-framework/blob/8e53641295068cdef653362d0f8d7f441c636b11/docs/ai_workload_research/discovery/A75_R_RL_POSTTRAIN/REPORT.md) | 27条、14列证据、0坏行、各ID唯一，`QUESTION_CARDS=[]` |
| D / 174-new｜Wan2.2 video DiT | `6421e6768ff3df2ec20cddd87b3aa28b932c113a` | `f10bb08891193d01b5ad98534f4514610df48eb3` | [D固定REPORT](https://github.com/swayhrl/accel-sim-framework/blob/6421e6768ff3df2ec20cddd87b3aa28b932c113a/docs/ai_workload_research/discovery/A75_D_WAN_VIDEO_DIT/REPORT.md) | 18条、17列证据、0坏行、各ID唯一，`QUESTION_CARDS=[]` |

通过GitHub连接器独立比较两Lane：Goal→final均`ahead=1`，仅新增本Lane`REPORT/EVIDENCE/QUESTION_CARDS/RECEIPT`四个文件；final→各自执行分支HEAD均`identical`；Git-data commit parent为共同Goal、tree与用户回执一致。读取全部8个固定交付文件，并独立抽核作者实测论文HTML和NeMo/Wan/Cache-DiT固定源码。**用户所述全部4blob/SHA fetch-back与本地worktree clean由原Lane收据负责；本审查确认Git身份/blob但没有重新在109/174计算其私有下载文件SHA或检测节点当前RSS。**

资源：R/D均据各自RECEIPT称CPU/source-only、未运行CUDA/GPU/模型/模拟器、未下载权重或真实数据、未安装、未清理旧资产、不相互等待。R有RU_MAXRSS与parent瞬时记录，D无连续进程树RSS监控。不能将这些当作精确连续系统资源峰；现有缺口与科研裁决无关，不为补监控重启两Lane。

## 1. R：完整GRPO正确性、已发表native分母与芯片内因果缺口

### 1.1 原生Table1实证

来自[NeMo RL arXiv:2604.26779v1 §3.1/3.2 Table1](https://arxiv.org/html/2604.26779v1)，本独审再次核原文实际group：
- Qwen3-8B RL-Think及Qwen3-8B-Base RL-Zero；DAPO-Math-17K训练、AIME-2024验证；8节点×4 GB200 GPU，Megatron train＋vLLM rollout；主结果为GRPO同步、离线in-domain EAGLE-3 k=3。paper没有充分给出全部模型checkpoint SHA、采样随机状态和数值版本细节，因此不能用当前公开config组成完美同一baseline。
- 作者训练step各阶段 Data/Prepare/Generation/Log-prob/Training（秒）：
  - Think AR：0.3/2.1/133.6/17.9/31.4，总185.3；Spec：0.2/1.6/87.0/18.1/30.5，总137.4，整体185.3/137.4=1.3486×。
  - Zero AR：0.2/1.9/100.0/17.8/31.3，总151.2；Spec：0.2/2.1/56.6/18.1/30.5，总107.5，整体151.2/107.5=1.4065×。
- 审查用整数/浮点复算四组各阶段和overall完全一致；Spec后generation Think占63.319%、Zero占52.651%，Logprob＋training分别48.6s，占35.371%/45.209%。**这是同步全系统时间比例，不是每GPU TC/L2/HBM利用率，也不是完整异步关键路径的分解**。Reward未独立列行，不能当0。
- 同原文§4的235B推测性能是作者专用模拟器预测，绝不是8B作者native，更非本项目模拟器；不能乘RolloutPipe改善，不能拿作者32GB200数据证明16GiB 4080可复现这条完整模型训练。

### 1.2 R的新科学边界及最近邻是否完备

- R已经区别同K完整prompt group、reward/advantage/mask合法完成后可训练，与一条response率先完成两种不同规则。 [RolloutPipe 2606.26997v2](https://arxiv.org/html/2606.26997v2)的CGP/FGD在Qwen3-1.7B、8×4090 train＋2×A100 rollout、K8/R32/64/96上已直接做合法complete-group流水。作者报告30.7—42.3%为rollout-start→train-end，并非当前NeMo 8B端到端并发开销。此前NeMo vLLM EAGLE-3与在线draft已有互斥约束，不能将所有强功能拼成无条件同一生产路径。
- 独立源回读：[NeMo-RL固定`grpo_sync.py`](https://github.com/NVIDIA-NeMo/RL/blob/540d2568c9cd184e01964c7de0a42026334f0a38/nemo_rl/algorithms/grpo_sync.py)确为分离的同步TransferQueue训练入口；[同步rollout actor](https://github.com/NVIDIA-NeMo/RL/blob/540d2568c9cd184e01964c7de0a42026334f0a38/nemo_rl/experience/sync_rollout_actor.py)自称同步全step收集，分组数据在TQ中传递；[EAGLE-3指南](https://github.com/NVIDIA-NeMo/RL/blob/540d2568c9cd184e01964c7de0a42026334f0a38/docs/guides/eagle3-speculative-decoding.md)已支持离线/在线draft。源码存在≠这些功能同时合法开启；其具体互斥/分组/权重发布由R细表记录，未在109执行。
- Libra、HetRL、AReaL的池调度/弹性/异步已经直接处理Q/S（缺就绪样本与强软件排队）的主要候选解释。R唯一真正可能出新问题的变量是**合法完整group进入活动GPU后，在同一策略版本/精确训练微批下的计算或访存服务敏感度**。R没有同语义pair的native数据或直接结构扰动能将其从Q/S分离，因此0卡是合理的，不是“没有运行GPU便必须为0”。
- 进一步明确：同步控制律固定每轮rollout权重，不必和滞后异步对照保持bitwise相同训练轨迹；训练曲线接近不是每step optimizer等价。reference/old logprob、权重可见性ack、真实KV状态和group身份属于模型质量/算法合同，不能靠模拟器计算硬件上界时忽略。

**R独立裁决：`SOURCE_SCOPE_NO_SURVIVOR`。** 不再做一轮“换名字的GRPO软件流水”；任何将来native probe必须先有一个不同于已知CGP/FGD/弹性pool的芯片内资源变量和真实已就绪组的实验输入。

## 2. D：Wan2.2自然生成周期、相同数值与近似加速严格区分

### 2.1 固定官方代码身份与静态负载

本独立审查回读`Wan-Video/Wan2.2@1ea34ff48f87168174e12956e200b1d908b1c5ff`：
- `wan/configs/wan_ti2v_5B.py` blob `d5d5aed0d5a6c88b58b5661538d575036b22caa2`：121帧、24fps、50steps、shift5、CFG5、dim3072、30层、patch(1,2,2)、VAE stride(4,16,16)，模型5B dense DiT。
- `wan/configs/wan_t2v_A14B.py` blob `a5220a52433dd9da0ad2c0af1bb3634ffd263717`：两套高/低噪声模型、40steps、shift12、threshold0.875、40层、dim5120、VAE stride(4,8,8)。它是随噪声步切换专家，不是token路由MoE；两模型结构不同，5B→A14B不是一个模型的专家开关消融。
- `wan/textimage2video.py` blob `67e9fd29acc2300eac0f0d070de135f6a9383879` 与 `wan/text2video.py` blob `7c79c66760b891f18ce7fd3e023a4947e06f691e`：每轮条件/无条件两次forward再CFG、scheduler更新latent；5B模型在去噪循环前上卡、循环后才下卡（在offload配置下），并非每轮重传所有权重。A14B调用`_prepare_model_for_timestep`每步不等于每步都进行完整专家搬运；启用offload时只在所需模型设备状态变化时迁移。
- 独立整数重算默认5B：latent`[48,31,44,80]`、patch-grid`[31,22,40]`、`27,280`token、50steps×2CFG=100个DiT forward、30层=3,000个block访问，单个BF16 hidden `27,280×3072×2=167,608,320B`。**是逻辑内容量，不是实际SMEM/L2、HBM traffic、峰值内存或性能因果。**
- A14B报告的默认40步`high26/low14`来自CPU按UniPC timestep端点公式推算，并非本独立审查运行过其Torch scheduler；0.875是**timestep阈值**不是87.5%调用。真实运行因solver、实现精度、I2V/DPMSolver不同可能改变交界。

### 2.2 直接软件先例足以排除哪些弱动机

- [TeaCache](https://arxiv.org/html/2411.19108v1)在Open-Sora-Plan做近似residual复用，降低视频生成算术但不保逐bit输出；其论文结果不转移到Wan2.2。
- [Sliding Tile Attention ICML2025](https://proceedings.mlr.press/v267/zhang25m.html)在HunyuanVideo做三维空间/时间稀疏注意力；有别于Wan2.2，同样属于mask改变计算/质量的算法层，不是免费的片上Cache硬件oracle；D指出其所谓end-to-end未计T5/VAE。
- [BWCache ICLR2026](https://proceedings.iclr.cc/paper_files/paper/2026/file/ac8ec9b4d94c03f0af8c4fe3d5fad4fd-Paper-Conference.pdf)在Wan2.1 81帧480P/50step下用block缓存，源数据的VBench与完整wall属于作者该模型实验；不能当Wan2.2 5B准入或数值一致。此PDF由D原Lane读取，本审未逐页视觉复核作者正式PDF，不复述比值作为本机测量。
- 独立复读[Cache-DiT固定双专家入口](https://github.com/vipshop/cache-dit/blob/089df6b6895a3bc15ebcd3f7546d90ec6eb592e8/examples/api/run_cache_refresh_wan_2.2.py)：按实际scheduler的timestep拆分high/low步、分别对`pipe.transformer`与`pipe.transformer_2`刷新cache context；[adapter](https://github.com/vipshop/cache-dit/blob/089df6b6895a3bc15ebcd3f7546d90ec6eb592e8/src/cache_dit/caching/block_adapters/adapters.py)有`has_separate_cfg=True`及双transformer结构。这是真实源能力，直接反证“无人处理双专家/CFG缓存寿命”；但不是Wan2.2 5B与官方完整T2V数值、视频质量、可用后端已经本机PASS。Cache-DiT示例为Diffusers、480×832/81帧，而非官方5B 720P 121帧同合同。
- 同一几何跨50步重复出现≠自注意力Q/K/V、latent、residual不变；将其用旧值替代就是训练免费/推理近似算法，必须计质量和额外缓存峰值。精确可复用的文本投影等优先是普通软件缓存/准备机会，不因生命周期长就自动具芯片内瓶颈。

**D独立裁决：`SOURCE_SCOPE_NO_SURVIVOR`。** 原用户强调主流大模型，Wan2.2确有真实主流价值；但该方向目前唯一强实验证据都在其它模型/分辨率/缓存质量组，仍缺同视频、同solver、同质量、合法精度与强后端的完整性能候选，0卡合理，不申请≥24GB/80GB GPU、下载34GB资源或擅自降低视频生成任务规模。

## 3. 综合：两个0不是更多“硬件空间=0”的证据

| 维度 | R / RL后训练 | D / 视频DiT |
|---|---|---|
| 已经可靠确立的真实应用现象 | 原生完整GRPO训练step阶段变化与推测解码带来的时间份额转移 | Wan2.2跨步完整调用结构，two-CFG与A14B高/低噪声专家切换 |
| 直接强软件反证 | NeMo spec和online/offline限制、RolloutPipe complete-group、Libra弹性分池 | TeaCache/BWCache/STA近似算法、Cache-DiT双专家/CFG缓存与官方offload |
| 没有被此次回答的科学问题 | 强软件之后**活动设备**本身的计算/访存/资源瓶颈以及是否值得设计硬件 | 在固定完整任务和质量之后的真实资源成本与近似算法的质量-吞吐Pareto |
| 硬件结论 | 未测，不能从trainer idle推SM未饱和 | 未测，不能从逻辑hidden大小推L2/HBM瓶颈 |
| 109 RTX4080可否直接执行作者完整强对象 | 不可等价；原32×GB200 GRPO和强模型状态需独立资格 | 不可等价；官方720P 5B至少24GB含offload配置，权重/缓存和质量仍需资格 |

**本轮没有发现同自然语义、强软件和GPU服务关键路径完全闭合的硬件候选。这是审查正确的STOP，不是AI-ARCH主线应无界停止。**

## 4. 新的研究策略：不再仅做“论文/源码扫描，交0卡”的轮次

自A70四线0、A73 W因输入PARKED、A74 H/C因SM100 PPA/PPA_MODEL停车、A75 R/D再次0，问题不在并行窗口数不够，而是**目前只允许读源码却要求证明强软件之后的独特硬件残余**。对成熟主流模型，这一要求会系统性地产生0个问题。必须把创新性审查和早期现象发现分开，同时仍坚持原实验的语义/权重/数值、软件对照和资源边界。

**建议下一阶段Round A77转为有限的“自然主流负载×硬件资源上限”体系结构特性研究（characterization），而不是第7次论文邻近清单。**
1. 先做一份**严格CPU-only方案**：从已经完成native资格的主流模型／算子（C16等旧项目只是只读证据与输入映射，绝不自动继承GPU任务）选择真实自然负载及阶段，核其是不是与已接受模拟器/config/算法合同相同；源与软件能力、实现/对象身份、输入与原生完整wall的版本资格是第一道门。
2. 定义**与论文候选正向机制无关的受控资源放大/削弱及理想上界**：例如在适合的设备/模拟器上分别控制issue、TensorCore/FMA、L1/L2、内存服务、warp资源与跨SM供给，建立真实业务的资源饱和曲线和交互项。理想化无限资源只是`UNPHYSICAL_ORACLE`，不承诺可制造；调软件后需要再看全应用占比与独立输入。不同资源不可随意一项调参后认定因果，必须校准config和各项计数。
3. 对**哪怕没有表现出明显硬件瓶颈**的对照负结果也成体系保存。若现有强backend已吸收关键效果，标`SOFTWARE_EXPLAINS`；若当前模拟器/真实输入不匹配，标`MODEL_OR_INPUT_NO_GO`，不是设备没优化空间。
4. 先准备有一个清晰问题的有限方案/资源资格，再单独批准109/174的native/simulator执行，不现在开GPU。以“从真实现象到潜在机制”与用户此前认可的“先试探资源再确认现象”双路径并行，禁用未经批准的新机制和旧项目权限继承。
5. 合适的**并行分工**是一个Lane只读核真实软件与科学输入/全部旧权威，另一个Lane审资源反事实与模拟器准确性／资源成本，最后由ChatGPT合成一个低预算实验Goal。**不是立即再派4个同质search Codex**。如果两线无法提供同一可信模型的输入和本地/模拟器可用资源，及时STOP。

这与用户长期想做的GPU资源扩展规律和饱和限制更一致：体系结构论文不必从别人的完整实现里“找一个遗漏API”起步，而应有真实负载的资源需求曲线与相反预测。**但本轮未实际批准A77，也未准备新的GPU Goal或CPU Codex命令。**

## 5. 状态、冻结与资源

- 原R/D的`SOFTWARE_NEARBY_NO_SURVIVOR`不改写，4个文件和所有归档SHA保留；A75完整研究笔记仍保持其首次原始论据。
- A70四线0、A73 W/H、A74-C SFU iso-PPA PARKED、A61/A65/A67 GNN、A69 Q-S、C16/AWMA/ISCAS全部冻结，109/174/164无新本轮任务；不自动进入数据/权重下载、租机/Profiler/新模拟器结构。
- 本A76审查使用固定GitHub应用和原作者HTML，只将独立审查及协调导航写协调分支，不合并两条执行HEAD，不抹掉任何negative或source缺口。

**Round A76最终：两条source-only结果分别合法STOP；新的科研投入应放在一次可审计的真实主流AI资源characterization方案，而不是再启动只读论文平行搜索。**
