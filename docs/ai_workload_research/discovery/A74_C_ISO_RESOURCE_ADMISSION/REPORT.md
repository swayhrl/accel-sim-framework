# Round A74-C｜SM100非矩阵资源与TC固定预算取舍：独立CPU/source资格审查

**日期：2026-10-16；执行者：ChatGPT／AI-ARCH Discovery（不是109 Codex进程）。**

**科学终态：`PARKED_FOR_PPA_OR_SIM_MODEL / STOP`。** 近邻核验通过，H73-Q1的“面积/功耗固定＋完整模型机会成本＋每硬件点重调软件”仍为一个可描述、可能被反证的研究问题；但当前仓库缺少被资格确认的SM100/TMEM/tcgen05/async/exp服务性能模型，也没有可引用的同工艺TC↔SFU面积和功耗边际成本。原生B200仅能做机会门，不能做物理资源交换。**不发B200/GPU、模拟器、Profiler、模型或数据下载Goal，不宣称硬件性能/新颖性成立。**

## 0. 来源、权限和审查方法

- 科学父：协调A74固定`54d2e153ca927c5dd990714cd772ae3593543fb4`；A74-C准备Goal及独立分支固定`f5ac43b4eb6adc29d040bdf65993cbd7de063db5`；H原报告`06b17a72f683316a4088292a4b424c9d97c7437c`。已阅读A74原Goal、A74审查及H的报告/问题卡，未改H/W/C16/AWMA的原始终态。
- 实际执行方式：ChatGPT通过GitHub连接器、公开论文HTML/PDF只读、NVIDIA官方资料、CPU整数算术完成；在当前对话无法直接SSH/启动109 Codex，**不能将本报告写成109 Codex或109环境静态审计实测**。未调用任何GPU、CUDA、编译或模型运行。GitHub文件由API独立分支发布，非本机SSH git push；发布SHA在最终聊天回执，不写入自身文件造成自引用。
- 公开FA4 arXiv v1 PDF已通过web页图复核第5页公式；MLSys正式会议摘要页面可访问，**正式会议PDF约14.5MB在网页入口因抓取大小报错，本轮未逐页核正式PDF**。因此正式版与v1仅核出版身份、官方摘要层技术/数量级的一致性，不强断其它图表逐项相同或v1附录设备冲突已消失。
- 源码的`G0/G1/G2`准入是分层观察，不是执行科学PASS。技术权威和不足逐条列于`PRIOR_AND_FEASIBILITY.tsv`；总状态由`DECISION.json`独立机读固定。

## 1. G0｜已存在的最直接软硬件先例

### 1.1 FlashAttention-4版本与强软件

- [MLSys 2026正式论文页面](https://proceedings.mlsys.org/paper_files/paper/2026/hash/ae8b0b5838ba510daff1198474e7b984-Abstract-Conference.html)确认FA4为MLSys 2026论文：异步MMA与更大tile、FMA多项式软件指数、按需rescale、TMEM和2-CTA的backward；摘要给出**BF16 B200单算子**至多相对cuDNN9.13 `1.3×`、相对Triton `2.7×`，最高约1613TFLOPs/s/71%。这不是Qwen3-8B全Prefill或新chip配比结果。
- [arXiv v1完整HTML及第5页PDF](https://arxiv.org/html/2603.05451v1)的§2.2/§3.1明确列B200每SM每cycle BF16 TC8192 FLOPs、MUFU 16 exponent ops、SMEM读128B；同稿已注记B300/GB300指数32 ops/cycle。因此增加指数吞吐及其动机**在原作者论文中已有事实**，不能声称本轮首次提出。
- v1作者列有Timmy Liu，正式会议摘要页面列出5名作者；**书目显示存在署名版本差异**，本轮不解释原因。v1正文§5 B200/AppA.1 B100 180GB以及cuDNN9.13/更新版本共存，正式PDF未逐页读，仍记录`FORMAL_NUMERIC_AND_DEVICE_IDENTITY_UNRESOLVED`；不能凭v1数字校准B200。
- 固定[FA4 forward源](https://github.com/Dao-AILab/flash-attention/blob/e9d8944c855489e03c66262d07ba4c81d9d8dd31/flash_attn/cute/flash_fwd_sm100.py) Git blob`1660b9214f2f9f5b6b679f66dd79a4b96695e4b3`，和[softmax源](https://github.com/Dao-AILab/flash-attention/blob/e9d8944c855489e03c66262d07ba4c81d9d8dd31/flash_attn/cute/softmax.py) blob`39ff94867d5ec6c08c8955db95cf3dca0893c3bb`：源码已经按2CTA、causal、head_dim、is_sm103等条件组织`ex2_emu_freq`、寄存器/warp分配，并使用TMEM/TMA/异步流水。静态存在不是某cuDNN、SM100 SKU或BF16 GQA实际dispatch和数值资格。强基线必须在**每个假定硬件资源点**重新合法优化，不能拿旧FA3/弱Triton制造机会。

### 1.2 量产Blackwell Ultra不是“加SFU”空白

- [NVIDIA 2026-02-25原厂实测报告](https://developer.nvidia.com/blog/making-softmax-more-efficient-with-nvidia-blackwell-ultra/)明确声称Blackwell Ultra指数SFU吞吐翻倍；GB200→GB300单独`MUFU.EX2`微基准的BF16约4938→9738 Gop/s、FP32约4943→10024 Gop/s；另一**特定FP8 GQA前向**组约`1.35×`吞吐。两个数字**不同实验分母**：一个是指令微基准，另一个是GQA FPROP，既不是完整Qwen BF16 Prefill，也不是公开逐请求质量对照。
- [NVIDIA 2025-08-22架构说明](https://developer.nvidia.com/blog/inside-nvidia-blackwell-ultra-the-chip-powering-the-ai-factory-era/)还给出FP4 TC密集吞吐约1.5×、较大HBM配置、160 SM/4TC每SM等；[Blackwell Ultra规格](https://resources.nvidia.com/en-us-gpu-resources/blackwell-ultra-datasheet)给出GB300 NVL72与HGX B300不同TDP配置上限。硬件其它部分和平台功耗同时变化，跨代GB200→GB300**不能当作同面积/功耗下TC让位给SFU的单变量**。
- 上述原厂microbench文章关于`sm100f`/`sm103a`的示例描述和编译参数需要另以固定CUDA Toolkit的官方ABI证实，本轮不将博客示例标签当作109或SM100 ISA合格。原厂文章本身明确包含其它软件优化（cuDNN、LDTM.STAT、低精度KV）。

### 1.3 其它直接硬件先例

- [VEXP，arXiv:2504.11227](https://arxiv.org/abs/2504.11227)：RISC-V向量/浮点单元增加BF16指数近似自定义块，作者声称约1%面积开销与软件协同的FlashAttention-2局部/模型效果；是**近似算法＋不同处理器/不同数值合同**，不提供NVIDIA SM100 TC↔MUFU的同工艺PPA价格，但否定“硬件加速exp没人做”。
- [Kim等，IEEE TCAS-I 2024](https://pure.kaist.ac.kr/en/publications/hardware-efficient-softmax-architecture-with-bit-wise-exponentiat/)：8-bit softmax的bit-wise指数/LUT和倒数硬件，出版社元数据含3.12GHz、25G inputs/s等局部设计数字；与BF16 TensorCore和完整Prefill没有相同数值/工艺/任务分母。
- [H-FA，IEEE TCASAI 2026](https://ieeexplore.ieee.org/document/11231140/)摘要提出浮点＋对数混合的专用attention处理、28nm硬件面积/功耗比较；它改变数值形式且不改造SM100通用GPU。全文未取得，仅`ABSTRACT_SCREEN`，不用于宣布Qwen BF16同语义硬件收益。

**新颖性结论：** 泛化“Softmax指数SFU不够、增加指数硬件更快”是已有软硬件联合工作；只可能保留**固定PPA预算、TC↔MUFU的边际价格、每配置强软件重调及完整通用模型的净收益**作为不同的科学问题。仍未广泛穷尽所有芯片DSE论文，因此不是已证明全新机制。

## 2. G1｜真正的完整Qwen3-8B Prefill分母

官方固定[Qwen3-8B config](https://huggingface.co/Qwen/Qwen3-8B/blob/b968826d9c46dd6066d109eabc6255188de91218/config.json)：36层、hidden4096、intermediate12288、32 Q heads/8 KV heads/head128、BF16、causal/full attention、40960 max positions；当前只冻结model config**不等于权重/tokenizer/准确率/FA4运行态已合格**。没有缩层、删FFN、改精度或向模型喂随机文本。

按每层QKV/O投影和三项SwiGLU FFN（忽略层norm/rotary/token embedding/logit、softmax及padding）：

```text
P_mac_per_token = 4096^2 + 2*4096*1024 + 4096^2 = 41,943,040
F_mac_per_token = 3*4096*12,288 = 150,994,944
Attention_QKPV_mac(N) = 4096*N*(N+1)   # 32 heads*128dim*2 matmuls*triangular_pairs
Nominal_masked_scores_per_layer = 32*N*(N+1)/2
```

| Prefill N | 每层QK/PV矩阵MAC | 每层投影＋FFN矩阵MAC | 仅矩阵MAC的Attention占比 | 每层名义有效softmax score数量 |
|---:|---:|---:|---:|---:|
| 4,096 | 68,736,253,952 | 790,273,982,464 | 8.00% | 268,500,992 |
| 8,192 | 274,911,461,376 | 1,580,547,964,928 | 14.82% | 1,073,872,896 |
| 16,384 | 1,099,578,736,640 | 3,161,095,929,856 | 25.81% | 4,295,229,440 |

该表为CPU整数复算、自然长度的**形状诊断**，没有下载、挑选或生成真实4K/8K/16K的请求；score是逻辑下三角位置数，不是实际MUFU指令、也不包含在线softmax二次统计、mask tile填充、exp仿真或分支重缩放；Attention MAC占比**绝不能代替实际Attention wall占比**。官方模型逐层结构与实际服务可走不同融合/量化后端，本轮不推断真实FFT、FMA或DRAM压力。

若真实原时间比例f（attention）/1-f（非目标），目标加速s、非目标资源让渡后慢r，在严格串行可加条件下`T_new/T_old=f/s+(1-f)*r`，净收益要求`f>(r-1)/(r-1/s)`；例`s=1.2,r=1.05`须`f>3/13≈23.08%`。这里只是反证模型，**f/s/r均未测，抢占/流水/服务重叠要采用实际关键路径，且没有任何证明s/r对应固定PPA可行点**。

**强后端合法性：`BACKEND_RUNTIME_UNQUALIFIED`。** 存在SM100 FA4 CUDA源、TMA/TMEM设计与causal/GQA分支不能证明选定B200、CUDA/CuTe DSL/cudnn版本及Qwen3-8B完整BF16模式可以import/编译/数值PASS。本轮不安装，不读取设备，不生成kernel；后续每次设备资格和数值门单独冻结。

**真实输入候选：** [QASPER官方数据卡](https://huggingface.co/datasets/allenai/qasper)公开完整科研论文QA/证据字段，标CC-BY-4.0；适合在未来取原始长文自然输入、冻结tokenizer/QA评分并分离探索与验证。但目前只有卡元数据：原论文权利、字段和样本真实模型token数、4K/8K/16K自然分布、固定SHA/使用合规都未核，状态`INPUT_AUTHORITY_PENDING`，不能调整文本、复制片段或无损截断来制造N。LongBench v2虽然Apache-2.0标签，但长度8K—2M是**words**，不能直接说其天然适合Qwen的8K-token完整Prefill；无本轮payload访问。

## 3. G2｜项目模拟器与固定预算PPA审计

**仓库源码层面的事实**（只读固定[Accel-Sim协调Goal commit](https://github.com/swayhrl/accel-sim-framework/tree/f5ac43b4eb6adc29d040bdf65993cbd7de063db5/gpu-simulator)）：

- `gpu-simulator/configs/tested-cfgs/`当前列Kepler、Pascal/Turing/Volta、SM80 A100和SM86 RTX3070等9个目录，**无SM100实验配置**。
- `gpu-simulator/ISA_Def/`列Ampere/Kepler/Pascal/Turing/Volta等ISA mapping；固定`ampere_opcode.h` blob`afc997df1add4556f5ce6ebcc98f671c17da3d36`把MUFU映为通用`SFU_OP`、HMMA映到专用单元，但未见`tcgen05`、TMEM或SM100 ISA mapping。固定`trace_opcode.h` blob`e1b3c2ff6e53b9f1bc6f0476da7f6a881834963a`含OP_MUFU/OP_HMMA，**不能将通用opcode名当SM100硬件语义**。
- `gpu-simulator/README.md` blob`04a91ae2dc51945fc3e9a3b36b39ac1b23f925e5`说明GPGPU-Sim 4.x模型**由环境脚本外部获取**；`setup_environment.sh` blob`4f93a70c38094060bd95a1397e37e31a19fbc58b`有外部git clone；故**不能从Git仓库缺文件证明所有174实际checkout绝无扩展**，但本轮没有访问109/174、没有任何被固定commit支持的SM100性能模型、ISA映射和验证收据。
- `AccelWattch.md` blob`77ca73db0989105a7ee81b5b5a09d3ea47f00747`明确原AccelWattch针对Volta GV100动态/静态功率建模，并非SM100上MUFU/TC/FMA/TMEM同工艺单位面积、功率和频率模型。其已有`power`一词不等于可以构造新面积/功耗可行的Pareto点。

因此，**不是全系统技术存在性判决`MODEL_MISMATCH_CONFIRMED`**（外部checkout未审），而是明确`SM100_MODEL_AUTHORITY_NOT_ESTABLISHED`、`MODEL_CAPABILITY_UNVERIFIED`，可用于本题的准入结果为`SIM_AND_PPA_NOT_QUALIFIED`。不能在旧A100/Ada trace上改服务率后声称SM100的片上依赖、TMEM容量或带宽性能。

物理同预算方案至少需要：同一设计工艺和目标频率下SM内TC子单元/MUFU exp端口/FP32 FMA、发射和寄存器文件、SMEM/TMEM/TMA service、互联时钟的**可交换单位**面积/动态静态功率与性能函数；必须计算移除TC后FFN/投影的损失、潜在SFU复用issue瓶颈、路由/线长/温度/时序对总体性能影响。NVIDIA公开给的是跨GPU功能和整卡规格而非这些可交换单元的成本。当前无可审计单位PPA报价，不能报告可制造iso-area优化点。

**独立因果门：** SM100真实单卡运行只能测原硬件下FA4/cuDNN是否暴露MUFU/矩阵/SMEM关键路径及全Prefill占比；即使GB200/GB300跨代对照也不是物理单元交换；假想TC×0.8/SFU×1.2 ideal oracle即使对模型有用，也只有`IDEAL_UNPHYSICAL_SENSITIVITY`层级，不是PPA约束下真实芯片提案。

## 4. G3｜可证伪路径以及STOP阈值

**明确分三道门，均非当前执行授权：**

1. **资料与模型层**：固定正式FA4版本、真实支持的CUDA/CuTe/cuDNN runtime、固定Qwen3-8B完整权重/自然可用tokenized请求及QA质量，确认理想前向、GQA/causal、数值误差和返回Logits身份。任何数据、后端不合格即先STOP。
2. **原生机会层**：只有上一步可行且资源获另批，才用SM100/GB300或B200单卡观察强FA4与最优合法cuDNN在真实输入的完整Prefill wall、Attention/非目标时间份额、kernel layout与依赖；Profiler需要独立批准。若强软件已隐藏目标exp服务或全模型时间权重太小、成本在噪声内，就关掉研究问题；**这一门不证明iso-PPA取舍**。
3. **资源反事实层**：必须有可校准的SM100 ISA/async/TMEM模型及同工艺单元代价。若模型找不到可实现端口扩展、代价无法约束或仿真不能复现基线与瓶颈排序，则STOP在`PARKED_FOR_PPA_OR_SIM_MODEL`，不能用旧模拟器或面积猜测填补。只有这个前提满足才讨论逐设计点软件重调、整模型Pareto、Qwen3.5-4B独立模型/请求验证、PPA。

**资源和优先级判断：** 不申请B200、GB300、Profiler，也不先下载15GiB级权重。B200租赁的价值取决于后续同面积实验是否有建模链，否则只是测一遍作者已有FA4问题；目前这条链不闭合。若以后另取得可复核PPA或目标模型，重审而不把本次PARKED升级为默认GO。无需继续重复搜索软max硬件近邻来保持任务活跃。

## 5. 最终三门结论

| 门 | 裁决 | 原因 |
|---|---|---|
| nearest-hardware-prior | `DIRECT_PRIOR_EXISTS` | Blackwell Ultra 2×exp；VEXP/专用Softmax硬件已有，FA4软件补偿已有；不允许“更多SFU”新颖性 |
| compatible software & whole Prefill | `SOURCE_ONLY_RUNTIME_AND_WALL_PENDING` | Qwen config/算术可复核，真实strong dispatch、完整wall与任务质量未取得 |
| iso-PPA model legitimacy | `NOT_ESTABLISHED` | 本仓库无SM100已测配置/新ISA映射、外部性能模型未审；无同工艺TC↔SFU面积/功耗对价 |

**终态`PARKED_FOR_PPA_OR_SIM_MODEL / STOP`；H73-Q1继续只是被明确限定的理论问题，未获native、simulator或PPA执行资格。**
