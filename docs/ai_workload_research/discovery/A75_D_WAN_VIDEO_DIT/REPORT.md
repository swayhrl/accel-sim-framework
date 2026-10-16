# Round A75｜D-A75：Wan2.2视频DiT的去噪生命周期、质量与强软件审查

执行者：Codex / 174-new；2026-10-16（Asia/Shanghai）。
固定启动HEAD：1eb14b0395bc898c3707ba850c36f17a9ec07b4e。只在 A75_D_WAN_VIDEO_DIT 前缀交付四文件。

## 0. 结论

**SOFTWARE_NEARBY_NO_SURVIVOR；0个推荐、0个备选。** Wan2.2是公开通用文本/图像生成视频模型，符合本轮主流生成AI对象；本报告没有因它不是LLM而降低其科研价值。源码确认真实跨步依赖、合法静态复用与A14B专家切换，但没有形成强软件之后、可与近似工作量/普通offload/准备成本区分的独立硬件问题。

本轮否定的是几个具体弱动机：同一latent形状反复出现不意味着每步特征相同；高/低噪声阈值不是专家调用比例；跨步feature cache或稀疏attention不是无损硬件cache oracle；逐步调用模型准备函数也不等于逐步搬运全模型。Cache-DiT已有双模型/CFG分开管理及按scheduler刷新上下文的实际源码。成本仍可能暴露，但尚未识别出的成本不自动构成硬件机会。

质量附加状态：**Wan2.2-TI2V-5B在固定完整设置下的跨runtime数值、缓存/稀疏组合质量与全链wall均UNKNOWN**。这不是native性能负结果，也不宣称所有视频DiT已被软件解决。QUESTION_CARDS.json为空；没有申请或启动native。

已完整读共同合同与D任务、A75笔记第0—4节和当前A74-C状态；协调协议第1—8节复用已经读过且与本起点完全相同的Git blob c8005351a6250451c82b78f7efe6e1a7b89a7c23。A74-C的iso-PPA/SFU问题继续PARKED，不因视频出现而重开；A70的serving/视觉理解、C16/AWMA/ISCAS等冻结不变。没有访问、等待或轮询R-A75。

## 1. 固定真实模型与输入身份

代码固定为 Wan-Video/Wan2.2@1ea34ff48f87168174e12956e200b1d908b1c5ff。主对象为TI2V-5B的**纯T2V入口**，不下载I2V图片或任何视频。公开文字prompt可作为任务输入，seed、负prompt、solver、CFG、尺寸/帧数及可选prompt扩写都是生成身份；官方展示prompt不是自然请求分布或独立质量集。默认base_seed<0会随机选择，未来不能只凭“same prompt”声称同一生成合同。

| 项目 | TI2V-5B主对象 | T2V-A14B结构变化对照 |
|---|---|---|
| 配置文件 | wan_ti2v_5B.py；dense DiT，30层、dim3072、FFN14336、24头 | wan_t2v_A14B.py；两套高/低噪声参数，各40层、dim5120、40头 |
| CLI有效默认 | 1280×704或纵向；121帧；24fps；50步；shift5；CFG5 | 可选1280×720；81帧；16fps；40步；shift12；CFG低3/高4；boundary0.875 |
| VAE/patch | stride(4,16,16)，latent48通道，patch(1,2,2) | stride(4,8,8)，Wan2.1 VAE；不是5B的压缩几何 |
| 参数/运算精度 | config.param_dtype与T5为BF16；噪声与部分modulation为FP32；convert_model_dtype显式控制参数转换 | 同样须分别冻结参数/激活/solver精度，不能统称全BF16 |
| 公开checkpoint身份 | Wan-AI/Wan2.2-TI2V-5B@921dbaf3f1674a56f47e83fb80a34bac8a8f203e；config再次确认48输入/输出通道 | Wan-AI/Wan2.2-T2V-A14B@c8c270b13ee05bfa474194ac9fb07a5868a97cea，含high_noise_model与low_noise_model |
| 资源说明 | 官方≥24GB VRAM的命令含offload/参数转换/T5_CPU；去掉这些提速的说明为≥80GB | 官方对应单卡示例≥80GB；多卡另含FSDP/Ulysses |

来源：[官方README](https://github.com/Wan-Video/Wan2.2/blob/1ea34ff48f87168174e12956e200b1d908b1c5ff/README.md)、[5B配置](https://github.com/Wan-Video/Wan2.2/blob/1ea34ff48f87168174e12956e200b1d908b1c5ff/wan/configs/wan_ti2v_5B.py)、[A14B配置](https://github.com/Wan-Video/Wan2.2/blob/1ea34ff48f87168174e12956e200b1d908b1c5ff/wan/configs/wan_t2v_A14B.py)、[5B checkpoint config](https://huggingface.co/Wan-AI/Wan2.2-TI2V-5B/blob/921dbaf3f1674a56f47e83fb80a34bac8a8f203e/config.json)。官方checkpoint页面标Apache-2.0；未接受额外数据条款或下载权重。每个读取源码的Git blob和本地SHA见RECEIPT。

5B Hub文件树发布总大小约34.2GB，其中DiT三shard合计约20GB、T5约11.4GB、VAE约2.82GB；这是**远端文件清单元数据**，不是本机下载或运行显存。不能按“5B×2B”估完整下载量，也不据文件大小推断存储dtype。权重逐文件内容SHA未在本轮验证。109的16GB 4080不构成上述官方设置的等价平台，禁止通过缩帧、裁分辨率、换量化/蒸馏权重假装同任务。

## 2. 一次完整生成与跨步依赖

generate.py把未指定的frame_num/sample_steps/shift/guide_scale从对应task config补齐。generic Python函数的81帧默认不能覆盖CLI的5B 121帧。主链为：

文字/负prompt与可选扩写 → T5编码/传输 → FP32初始噪声与scheduler → 模型上卡 → 每步条件/无条件DiT两次forward → CFG组合 → scheduler更新latent及历史 → 下一步 → DiT下卡（若启用）→ VAE decode → CPU视频编码/导出。

只要同一视频仍保留该solver数学合同，下一步需要当前步的噪声预测及更新后的latent；UniPC还有model_outputs等求解器历史。不能把50个step当相互独立batch并行。条件/无条件forward在官方代码中顺序执行，不能把它们的时间求和或改batch顺序后自动认为数值完全一致。

### 合法可复用与不能直接复用的对象

| 对象 | 寿命/合法复用要求 |
|---|---|
| T5正/负context、尺寸/patch grid、部分位置频率表 | 在固定prompt、预处理和模型身份内稳定；可以预处理，跨请求必须键入完整身份 |
| cross-attention的text projection/KV | 固定context、层、参数、dtype等时可讨论精确预计算；A14B切专家后权重不同，CFG正负分支也须分开。属于普通软件准备/复用机会，不凭重算源码称硬件创新 |
| latent、自注意力Q/K/V、DiT residual | latent和timestep每步变化；数值接近不等于相同，复用旧输出是近似算法，需要质量门 |
| 专家权重 | 在其噪声区间内复用；专家切换是参数身份变化，不能复用另一专家特征而声称无损 |
| 缓存初态 | 同一视频内与新prompt/seed请求间分开；warmup、refresh、CFG及两专家上下文不能隐含跨请求沿用 |

固定block包含self-attention→cross-attention→FFN及modulation。dense 5B的序列几何、层数和GEMM形状不会仅因timestep值改变；若某区间执行量减少，应先检查cache/mask/CFG/solver算法和backend分支，而不是先宣布硬件服务能力变化。原实现已有FA3/FA2选择与SDPA fallback；源存在不证明任何SKU最终选中的kernel相同。

### A14B切换与offload的时间顺序

text2video.py按 t≥0.875×1000 选择high_noise_model，否则low_noise_model；同一步的cond/uncond用同一专家。_prepare_model_for_timestep每步调用，但仅当inactive专家在GPU或required专家在CPU时才搬运。对默认单调UniPC轨迹，不能描述成高低专家逐步交替迁移。

5B T2V在循环前model.to(device)，循环后才model.cpu；因此该官方路径**不是每个step完整HtoD一次**。A14B在阶段首次使用时可能有权重搬运，两模型均驻留的合法配置则不同。主机t.item()判断、位置/元数据准备、dtype转换和cache刷新如有成本，应先归软件/依赖解释；本轮未测其暴露wall，不将它们命名为新GPU同步瓶颈。

## 3. 纯CPU可复算结果（DERIVED，非模型执行）

未import torch/numpy/diffusers，只用整数、标准库float32端点仿真及源代码公式：

- 5B默认T2V：latent=[48,31,44,80]；patch grid=[31,22,40]；S=27,280 tokens。50步×2 CFG forward=100次DiT，100×30=3,000个block访问。
- 单份S×3072 hidden内容在BF16为167,608,320 B，在FP32为335,216,640 B。**不是峰值、HBM traffic或cache收益**；QKV、modulation、scratch、VAE和权重另算。缓存数K、CFG/专家私有状态、别名和保留策略须从真实对象测量，不能拿所有block内容简单相乘当物理峰值。
- T2V-A14B固定UniPC、40步、shift12：依source的sigma端点、linspace、shift和int64 timestep生成规则，得到high26步/low14步，CFG调用52/28次，发生一次区间切换。未调用真实scheduler或GPU；此推导不适用于I2V/DPM++、不同shift/步数，也不是两阶段耗时比例。
- boundary0.875是训练噪声时刻阈值，不是87.5%步数；同理Cache-DiT示例的“30%”注释不能取代其split_inference_steps实际计算。

## 4. 三组原论文精审及一个直接实现组

| 组 | 核验对象/质量与时间分母 | 对Wan2.2的有效含义 |
|---|---|---|
| P01 TeaCache | CVPR25论文族；CVF正文403后读公开arXiv2411.19108v1 §4/Table1。Open-Sora-Plan 65帧512²、150步、单A80080GB；FlashAttention启用；原99.65s/80.39 VBench→slow22.62s/80.32 | 近似residual复用已有软件；差0.07为**百分点**。不是Wan2.2实验；精度及冷启动/T5/VAE/export计时完整边界未充分披露 |
| P02 STA | ICML25正式入口＋2502.04507v3 §4/Table3：HunyuanVideo 117帧1280×768、BF16、H100；50步training-free mask搜索组501s/1.89×，SSIM87.67/PSNR28.76 | 作者所谓end-to-end明确**排除VAE与text encoder**；不能当整视频wall。稀疏mask改变必需attention项；finetuned结果另组，不能拼成无损same-weight收益 |
| P03 BWCache | ICLR26正式PDF Table1/AppendixB：Wan2.1 81帧480P、FlowMatch50步、单A80080GB；原912s/82.17 VBench，BWCache457s/81.99，TeaCache644s/81.73 | 比更老模型接近，但仍非Wan2.2；视频reference相似度与VBench分开。缓存会增加显存，补充材料已有部分block/状态开销讨论，不能忽略容量代价 |
| S01 Cache-DiT | 固定source 089df6b6895a3bc15ebcd3f7546d90ec6eb592e8，Wan adapter与run_cache_refresh_wan_2.2.py；双transformer、separate CFG、分专家warmup/cache限制与按scheduler刷新 | 真有A14B代码入口；示例480×832、81帧、steps16/28/50、seed0和Diffusers，不是官方5B 720P50步同合同实测。pipeline计时也排除导出/初始加载，且未建立Wan2.2质量组 |

原始入口：[TeaCache公开正文](https://arxiv.org/html/2411.19108v1)、[STA正式入口](https://proceedings.mlr.press/v267/zhang25m.html)、[STA所读v3](https://arxiv.org/html/2502.04507v3)、[BWCache正式PDF](https://proceedings.iclr.cc/paper_files/paper/2026/file/ac8ec9b4d94c03f0af8c4fe3d5fad4fd-Paper-Conference.pdf)、[Cache-DiT例程](https://github.com/vipshop/cache-dit/blob/089df6b6895a3bc15ebcd3f7546d90ec6eb592e8/examples/api/run_cache_refresh_wan_2.2.py)。BWCache第7页Table1已渲染并视觉核对；PDF仅留私有tmp，不入Git。

作者quality/inference均为AUTHOR_NATIVE，不是本项目复现；我们的几何/步数为DERIVED。三组模型、steps、frames、稀疏/缓存阈值、质量baseline不同，收益不能相乘，也不能把训练后STA、TeaCache、DBCache、TaylorSeer、Cache CFG和FP8全部拼成已验证最强系统。

## 5. 强软件适用性与质量门

Cache-DiT固定Wan adapter实际区分transformer和transformer_2，并标has_separate_cfg；例程按当前scheduler与boundary_ratio分别求高/低噪声步数后refresh_context。cache_adapter还带每次pipeline调用reset逻辑。这反驳“无人处理双专家cache生命周期”，但不证明切换/刷新为零成本。其Diffusers checkpoint/solver配置与官方repo并非天然bitwise等价；5B同版本接入、质量和内存资格均未实测。

固定TeaCache@7c10efc4702c6b619f47805f7abe4a7a08085aa0的Wan集成目录为TeaCache4Wan2.1，不能据此宣称Wan2.2已原生通过。官方README列Cache-DiT和DiffSynth能力只作接口入口，不把FP8、layer offload、sequence parallel支持当无条件互相兼容。稀疏、蒸馏、减少steps、CFG cache及近似feature reuse都须单独标算法变化。

未来数值/质量至少分两层：相同计算合同的执行重排应核噪声预测、solver轨迹和视频输出，先冻误差与reference重复性；近似方法还需同prompt/seed/frame/steps、覆盖运动/语义/主体稳定性的质量集。VBench均值接近不等于每视频动作/语义不退化，LPIPS/PSNR对reference接近也不等于任务成功。小canary只证明接口，不用几条随机视频宣称统计质量。探索mask/threshold的prompt不得兼任holdout。

本轮没有生成视频、测VBench或采集真实中间tensor；模型/权重/数据文件内容未获native资格。质量缺口如实保留，而非为了凑强基线降低质量门。

## 6. 筛选与为何0卡

| 被筛思路 | 反证/竞争解释 | 裁定 |
|---|---|---|
| 重复时空latent，所以应做硬件跨step特征cache | latent/t变化；TeaCache/BWCache及DBCache已做有质量代价的自适应复用 | 通用想法SOFTWARE_NEARBY，不给硬件无损oracle |
| A14B高低噪声“路由”制造专家访存热点 | 是阶段参数更换；源码是单调schedule选择，Cache-DiT已分专家管理 | 不与C16 token MoE混同；普通offload/预取首先是软件问题 |
| 静态text KV/位置表反复准备是新硬件瓶颈 | 精确预计算可能合法，但属于可直接检查的软件准备；完整占比未知 | SOFTWARE_OPPORTUNITY，不自动升架构 |
| 去噪早/晚天然具有不同GPU工作粒度 | dense5B shape不变；缓存/mask/solver改变工作，数据值变化的真实设备作用尚未知 | 没有独立硬件资源变量与强组合质量对照，不晋升 |
| 24GB模型迁到16GB后改帧数跑通 | 违反官方完整输入范围与质量合同 | 不执行，不命名原任务负例 |

这与A70视频理解链不同，也不复开A74的SM100资源/PPA问题。本次0源于具体输入/计算/复用语义和直接近邻；不由“还没跑GPU”单独推出，也不声称强软件已吸收所有真实剩余成本。

## 7. 未来完整生成的最小方法模板——无推荐执行、PROPOSAL_NOT_AUTHORIZED

若以后出现一个明确独立新变量，另立CPU资格与native合同；当前不申请租机/下载：

1. 主baseline保持官方5B 1280×704、121帧24fps、UniPC50/shift5/CFG5，固定正负prompt、是否扩写、seed、tokenizer与checkpoint，以及完整precision/offload配置。同一个科学输入若合法改用Diffusers强路径，先核模型/solver与输出资格；至多两条强路径，不用故意慢fallback或默认不启kernel作稻草人。
2. 主分母是完整生成：T5/条件准备与传输、模型HtoD/offload、所有去噪和solver、VAE decode、CPU导出；另分model load/cold start与稳态请求wall。denoiser总wall与每步/CFG分支/专家边界仅作分解；多GPU还要纳入FSDP/Ulysses collective、padding和rank同步。
3. 诊断只改相同计算的执行组织或已冻结的cache/mask配置；固定实际命中/完整计算序列与缓存初态，质量需重新过门。保存同次真实latent用于层级replay只回答局部，不替代完整视频。删步、降分辨率、改seed/solver或将预处理免费移出主分母不算同任务硬件上界。
4. 独立验证冻结未参与阈值/掩码选择的自然prompt与多个seed，关注复杂运动及主体/语义稳定性；A14B只作独立结构对象，不是5B的expert开关。许可、prompt/seed表与评估程序版本在新Goal前明确，不下载真实视频来补本次材料。
5. STOP：强软件解释了暴露、仅算法工作量变化、完整wall没有可重复净效应、质量/reference失败、缓存内存抵消收益、平台/依赖/数据权限不合或范围/预算改变。若只是allocator/offload/准备小修，归软件；无法区分因果则UNKNOWN。

资源资格：≥24GB只适用于官方含offload等原命令，不保证加入缓存后仍适配；≥80GB驻留路径是不同部署。未来至少先做显存/host RAM/磁盘静态门，权重清单约34.2GB不能塞入一个20GB下载预算；额外cache/scratch和host中间副本未知。10916GB现无等价完整运行资格；本轮不扫描资产、不改输入、不自动部署。

## 8. 执行回执与STOP

工具计算worker1，主源码/CPU helper affinity509、OMP/BLAS及Git pack/index单线程；私有output/tmp独立。仅读源码/元数据、公开原论文及小型CPU算术；无GPU/CUDA/JIT、模型栈import/运行、权重/视频数据下载、安装、Profiler、模拟器、164访问或清理。具体资源与source blob/SHA、访问失败及替代来源在RECEIPT.json。

四文件语法、引用、候选去重和路径白名单自审后commit/push；单次fetch-back核精确commit/tree/四blob与SHA、worktree clean后STOP。最终commit/tree写私有回读及用户回执，避免RECEIPT自引用。无自动native，无等待R。
