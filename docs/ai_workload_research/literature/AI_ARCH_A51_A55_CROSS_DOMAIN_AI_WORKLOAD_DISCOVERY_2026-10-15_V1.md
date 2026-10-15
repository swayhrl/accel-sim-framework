# AI-ARCH Round A51–A55｜真实AI负载跨方向Discovery：GNN供数、稀疏融合、JEPA、VLA与下一最小反证

**执行者：ChatGPT／AI-ARCH Discovery；2026-10-15。五项连续研究单元，在同一回合联合完成，不人为拆成五条Goal。**

**起点／协调 authority：** `swayhrl/accel-sim-framework`，长期branch `hrl/ai-workload-research-coordination@6cf703e460ab525dc3bebd6a4a80cc5f1deeda10`；写入前Git compare `identical`。前接[A34–A43十轮](AI_ARCH_A34_A43_TEN_ROUND_DISCOVERY_JOURNAL_2026-10-14_V1.md)和[A50独立审查](../reviews/AI_ARCH_A50_A47R2_DEFAULT_CAGRA_NATIVE_REVIEW_AND_ONE_GOAL_DECISION_2026-10-15_V1.md)。**当前A50G已获用户单次授权、独立109 Codex执行回执尚未交本窗口；不可凭文献进度说GPU已启动或结束。**

**任务边界：** 仅Web学术原文/作者官方文档＋GitHub固定源码读回。**没有SSH 109/174/164、没有GPU锁、没有启动Codex/模型/构图/训练/trace/模拟器、没有下载模型权重和科学数据**；既有A50G GPU Goal不打断。本文引用的所有作者结果都不是本机native。某论文只读摘要/会议程序时显式标`ABSTRACT_ONLY`／`PROGRAM_ONLY`，不能补造具体表格、底层code或测量平台。

## 0. 汇总判断与可证伪方向

发现四种截然不同的**真实AI模型状态寿命/竞争**，不能简单统一为“稀疏Cache”：

| 方向与核心状态 | 已有强软件 | 真正未回答的问题 | 本轮决定 |
|---|---|---|---|
| **Q-G GNN GraphBolt**：sampling邻域/feature rows/mini-batch | GPU图缓存＋LRU特征缓存＋async fetch/流水及最新GPU采样优化 | 在**采样—特征—计算完整训练流水**中，同样采样分布、命中和并发时是否仍有exposed data-supply关键路径？ | 新保留：真实AI图任务，先CPU/source与数据身份资格 |
| **Q-S点云/稀疏图算子**：结构坐标、映射、fusion中间量 | Spira、TorchSparse++、Minuet、FuseFlow | 强软件合法选优后，准备/重排/融合带来的额外工作是否抵消计算省下时间？ | A43方向维持；拒绝仅以模拟器收益冒称Ada native |
| **Q-J JEPA / Q-E TBE**：mask路由或embedding训练状态 | M-JEPA共享context/union target、FBTriton融合及分派 | 新残余必须在同语义全训练步和成熟优化器后才成立 | 保留但暂不优先实装，无独立native/模型资产资格 |
| **Q-V VLA**：VLM前缀KV、重复action steps、跨请求短核 | LeRobot SmolVLA已缓存prefix、V-AEFusion/DP-Cache、vla.cpp GGUF运行时、KerColle SM co-schedule | **在真实多请求与机器人控制期限下**，已有异步/调度优化后是否还有可观测的GPU dispatch/HOL剩余？ | 新增优先source-only模型/输入/请求边界资格；**不直接宣称新调度硬件** |

**建议下一次独立source-only前置工作优先Q-V，其后Q-G；无需等A50G结果便可继续纯文献/源码审查，但任何真实109 GPU或174重负载都是新的执行边界。** 选题优先级≠原生可部署性，见A55的受控停机门。

## A51｜GNN训练：供应链竞争不是“多点随机访存”的同义词

### 1. 原论文与既有强软件（区分来源）

2026年10月`SDGraph: A scalable training system for GNNs with GPU sampling and parallel feature access`，[FGCS正式出版社摘要](https://www.sciencedirect.com/science/article/pii/S0167739X26001901)，文献层级为**作者摘要，不是完整分组表**。它**已经**提供warp协作采样、异步随机数池、hot/cold caching、跨迭代prefetch以及WarpGather合并索引与访问；作者对DGL声称**平均end-to-end训练1.89×**，但从可得摘要不能建立每个模型/硬件/数据规模的完整配对表，也不是109原生。不能把“第一次做warp collaborative sampling/聚合特征加载”当新增硬件创意。

GraphBolt官方2.5文档：
- [NeighborSampler](https://www.dgl.ai/dgl_docs/_modules/dgl/graphbolt/impl/neighbor_sampler.html)：`overlap_fetch`使pinned graph的UVA抓取与其它工作重叠；`num_gpu_cached_edges>0`且开启overlap时已有GPU邻域缓存；`gpu_cache_threshold`控制进入缓存所需访问次数；`asynchronous`允许后台采样与compaction。默认开关关闭≠软件没有能力，也不能故意用关闭版本冒充强基线。
- [GPUCachedFeature](https://www.dgl.ai/dgl_docs/generated/dgl.graphbolt.GPUCachedFeature.html)：带fallback的GPU LRU feature cache且暴露`read_async`，GPU上读feature的cache hit并非免费，miss、填充和host pinning也会改变重叠。
- NVIDIA cuGraph-PyG也是另一条合法GPU sampling系统；**不能把早期cuGraph-DGL路径冒充其现行唯一后端**。对比须各自以真实版本/接口为准。

**本轮固定Git源码（已实际读取）：** `dmlc/dgl@3d16000b4170fa741ed9e9667f22ba84d3493026`（master提交，日期2025-07-31；不是已核2026最新发行）：`python/dgl/graphbolt/impl/neighbor_sampler.py` blob`7ddba6d7ccacfb26708dab5a1975c7f557090587`的`overlap_fetch/asynchronous/num_gpu_cached_edges`实际存在；`gpu_cached_feature.py` blob`59a66413843c1062da866f6d51519b82c9a2b577`在`read_async`先询缓存再通过fallback读miss；`gpu_graph_cache.py` blob`a6a640dfa6c303cf2a67081e3cb714f979941856`实现邻域cache query/replace异步阶段。**这是源码能力，不是本机GraphBolt正确性/吞吐资格或所装版本。**

### 2. 固定真实图的可行性示例（没下载、无执行）

[OGB官方Node Property Prediction](https://ogb.stanford.edu/docs/nodeprop/)对`ogbn-products`定义：**2,449,029 nodes、61,859,140无向edge数、100维输入特征、47类，按sales rank划分训练/验证/测试（top 8%/next 2%/其余）**，不是可任意shuffle的普通random split。官方同时说明无向图在loaded representation可能转成双向边；若取反向展开，实际储存邻居ID可能对应**123,718,280 directed entries**，取决于具体loader。`2,449,029×100×4=979,611,600B`只是FP32 feature有效载荷；双向CSC neighbor index若int64约989,746,240B，另有indptr/label/optimizer/cache/复制。**不能凭“单卡16GB”宣称该图＋模型完整训练已经资格化**。

### 3. 研究问题、最小可证伪实验

**Q-G：** 在同一个真实GraphSAGE minibatch和GraphBolt/PyG强后端之后，改变GPU graph-cache/feature-cache与pipeline overlap是否引出**可计入训练步的剩余供数等待**？首先合法采样分布、fanout、seed/mini-batch集合、feature/label与实际训练精度；GraphBolt与cuGraph-PyG不要求逐bit相同采样轨迹时必须按分布与模型数值/accuracy约束分开比，不能以采样不同导致的少访问假装硬件提速。

最小研究单元建议：一个真实`ogbn-products` node-classification模型GraphSAGE，固定train split与采样fanout；强GraphBolt采样与GPU缓存完整开启为主参照，必要时加一个可复现的关闭控制用来做**敏感性诊断**，绝不把关闭版本当最终性能竞争者。观察三类有定义的分母：`T_sample_and_prefetch`、`T_feature_ready`、`T_forward_backward_update`以及完整`T_minibatch_wall`和跨batch稳态吞吐；区分**被overlap隐藏的等待**与真正critical-path暴露。只有强baseline仍显示稳定剩余并且硬件资源因果可进一步辨识时，才考虑新cache/硬件机制。

**STOP：** 无合法OGB输入/版本与采样语义门，或现有async/cache已掩盖大部分端到端成本，或者只改变feature hit-rate却不影响训练步wall，则`NO_HARDWARE_HEADROOM_EVIDENCE`并STOP。**本轮未授权该dataset下载与训练**。

## A52｜FuseFlow和Spira：稀疏融合的收益必须跟目标机器对齐

### 1. 逐实验组核原文（本轮可读HTML，非只读摘要）

[ASPLOS2026正式论文](https://compilers.stanford.edu/publications/asplos2026fuseflow/)、[arXiv全文`8](https://arxiv.org/html/2511.04768)。作者的`FuseFlow`是**PyTorch sparse expressions→SAMML→可重配置流式数据流体系**的编译与设计空间搜索，并不是CUDA原生GPU compiler。

**原文`8.1 Table2`逐组：**
- GCN与GraphSAGE：2层；`Cora(2708×1433)、Cora_ML(2995×2879)、DBLP(17716×1639)、OGB-Collab(235868×128)、OGB-MAG(1939743×128)`，输入zero-based lossless稀疏。
- Sparse Autoencoder：3层；`ImageNet224×224、NIH-CXR1024×1024、LUNA16 512×512`，作者人为的50% zero-based lossiness作用于weight；这组不是未经改造的自然稀疏权重。
- GPT-3 Small BigBird：125M、seq1024；IMDB mask稀疏53.9–86.5%，属于**block-sparse attention模式**，并不是普通稠密GPT3 token真实服务配置。
- 主`end-to-end`的性能在`Comal cycle-accurate simulator`里完成；DRAM模块Ramulator2 HBM2，作者称功能与dense PyTorch核对。小型硬件验证是Xilinx VU9P/AWS F1设计的**post-synthesis RTL simulation**，含KarateClub图和seq64的简化片上可装入程序，报告模拟器/RTL kernel cycle相关`R²=0.991`。**既不是整模型FPGA实物板卡native执行，也不是RTX4080实测speedup。**
- 原文完整fusion不是普遍最优，GCN/GraphSAGE的某些阶段会因重计算和坐标迭代次数爆炸吃亏；作者将fusion与dataflow ordering、blocking联合调优。对BigBird GPT3作者在模拟器中展示约2.7×相对unfused改进；**不能把这个系数搬到GPU Cache机制**。
- 正式`artifact setup`要求x86-64 Docker环境及≥64GiB RAM/200GiB disk等较大容量，不能当下一次无准备的174/109低成本probe。

### 2. 与A38 Spira、A43 Q-S关系

A38已核`SPIN-Research-Group/Spira@aee69c61f3e001f72828a6d5a70f6a1200166f65`：作者`end_to_end_experiment.py`在每输入reset后已将coordinate ordering、`add_all_kernel_maps`与model计进端到端时间。Spira完成真实GPU sparse-conv路径，与FuseFlow的**模拟流式RDA**是不同平台/算子体系/时钟分母的强近邻，不能强行排出“谁更快”的表。

**可研究但尚未测的关系：** 合法fusion粒度影响重复坐标遍历、重排和中间态实际寿命；是否在GPU native程序中构成物理资源限制，必须先对原真实坐标/层组、数值和完整`mapping→compute→consumer`做原生强对照，不能把模拟器指标解释成GPU已需片上状态压缩。

**STOP：** 当现成Spira/TorchSparse++/Minuet的融合/流水选优已消掉完整层差，或FuseFlow“收益”只存在另一个RDA后端时，拒绝引入GPU新状态单元。

## A53｜JEPA mask路由与推荐embedding：成熟软件能力阻止直接复制直观机制

### 1. JEPA前沿（摘要/官方会议程序，未逐表获取完整原文）

`M-JEPA: Mask-Aware Execution for Efficient JEPA Training`，[arXiv版本2609.22674](https://arxiv.org/abs/2609.22674)，2026-09-19；[PACT2026大会正式日程](https://pact2026.github.io/program/)标有10月22日报告。**本轮取得摘要和大会节目项，没有逐组PDF数据/固定实现commit，故以下是作者abstract-level而非我们审的原生数据**：五种JEPA、A100、2–10 masks，作者最多**1.7×训练端到端**，单独masked patch embedding高稀疏下**4.75×算子**。它已经实施`shared context encoder`、mask-dependent routing/slicing与backward fusion、target token union和patch embedding skip。因此这些本身**已经是软件已做过的机制**，不能直接作为未发表的AI硬件创新。

JEPA mask改变预测难度、target token集合与学习目标，因此必须固定每个mask ID/位置、数值梯度、一致的optimizer、训练质量，**不能为了更低访存把mask token删多而宣称等价加速**。本次没有合法代码release或同权重自然数据身份，不立刻部署。

### 2. TBE训练（延用A41作者原实验，禁止数值错误）

[PyTorch FBTriton官方技术文章2026-10-06](https://pytorch.org/blog/modernizing-table-batched-embeddings-with-fbtriton/)已有metadata hoist、按row/run聚合与分派和优化器融合；[FBGEMM官方TBE API](https://docs.pytorch.org/FBGEMM/fbgemm_gpu/python-api/tbe_ops_training.html)已有显式cache/optimizer选项。A41记录的作者一组B200配置（fwd`22.844→33.252ms`，bwd`56.693→32.931ms`）必须净算`79.537→66.183ms`，约16.79%，不是“backward节省”全转成应用级收益。训练时`(1+2)^2≠1²+2²`的标量反例指出同row多次Adagrad更新通常不等于先聚合梯度后一次更新。真实ID run-length/冷热变化、新旧embedding状态和多GPU sharding语义都需资格，不能把synthetic random IDs硬说为生产业务。

**Q-J/Q-E继续储备而非并行建重环境。** JEPA和TBE都已有正面成熟软件改进，目前缺一个“**这些软件之后依然暴露且物理资源可定位**”的真实native现象。之前已经download的模型资产不自动生成科学问题。

## A54｜VLA真实机器人负载：GPU两阶段强软件已优化，服务端并发身份却是关键缺口

### 1. 作者研究线的科学层级差异

- [`KerColle: Unlocking Fine-Grained GPU Concurrency in VLA Models`](https://arxiv.org/abs/2609.22335)，2026-09-16，[PACT2026官方技术日程](https://pact2026.github.io/program/)列10月22日发表报告，**本轮abstract与program level**：四种VLA，两种GPU architecture，作者用**模拟器**示范在线按SM utilization与kernel资源需求协调VLM和Action Head，缓解CTA dispatcher HOL，最多**28%吞吐改善**。这并不是109 native实验；**“第一次提出按SM实时利用率避开VLM/Action HOL”已被它覆盖**。
- [ICML2026`Characterizing VLA Models across XPUs`](https://proceedings.mlr.press/v306/zhou26e.html)正式论文摘要：跨GPU/edge NPU的CET（成本能耗时延）、作者的VLM偏计算密集、Action Expert偏访存敏感的分阶段画像；`DP-Cache`、`V-AEFusion`已做削减diffusion冗余和异步重叠，作者最多GPU2.9×/edge NPU6×且报告有少量成功率损失。**报告没有足以把这些数字准确映射到RTX4080、自然多机器人到达流的具体原始实验组**；不把“首次提出分两阶段pipeline/Cache”作为新机制。
- [SmolVLA官方作者发布与模型](https://huggingface.co/blog/smolvla)：450M参数、开源训练/真实机器人/LIBERO等，作者已有异步robot action execution与policy inference pipeline，任务成功/响应存在关联，不可用改变action chunks、flow步骤或异步控制期限得到的快慢假装同任务。
- 其它部署压力如FlashVLA、chunk lookahead都可能改变语义或降低任务精度；需归入强软件最近邻，而非新GPU资源证明。

### 2. 本轮**真正直接读取**的公开源码/部署入口

**`VinRobotics/vla.cpp@cff0cfb5e9e6cab31671d46082f7bdbff078816e`，2026-10-13：**
- `docs/ARCHITECTURE.md` blob`7f7939b240d9acabbcde59dbc49e3629a88423c8`将实际`prefix vision-language→action expert`分出，flow solver多步、DiT、多层或一次并行decode之间是**不同模型/算法**。权重可做GGUF，CPU/CUDA可用。
- `docs/USAGE.md` blob`52b5d44c64b08322d4c69be910eb531b22329a1d`：`vla-bench`对**合成像素、token、state、noise**在进程内计`predict()`，**不含机器人真实episode成功率、网络请求/传输或多机器人并发**；`--num-steps`改流积分迭代可改变数值/质量，`--flash-attn`可能改变结果。发布预编译Linux-x86_64 CUDA12.8声称支持sm89，**只是公开发行资格候选，不是109已验证ABI/执行**。
- `src/serving/vla-bench.cpp` blob`f7f602cc19104a6acf7e1d249fc4d6d62bfc90cf`：真实源码把pixel设`(x+2y+40c+17v)&255`，language token循环填值，state/noise人工生成；warmup后对单`vla::predict`计in-process平均/p50/p90。这类bench可以测模型形状的kernel供需，不能作为真实机器人动作成功、排队尾延迟或GPU多请求并发的原生证据。
- `src/serving/server.cpp` blob`7b51e44b75a3cab4906aa4071da91999c41194cd`：ZeroMQ REP socket单线程顺序`recv→vla::predict→send_reply`，返回包含`ms_vision/ms_inference/ms_prefill/ms_denoise`字段。**这是关键排除项：即使多个客户端同时发送请求，这条server本身也没有同时在GPU运行两个相互独立请求的VLM与Action Expert。**不能把它的“并发客户端数”冒充KerColle式GPU overlapping dispatch。
- GitHub latest v0.4.0 release存在多平台二进制，linux x86_64 cuda12.8含sm89但runtime依赖及实际模型GGUF的byte/hash/许可/108?均未资格化。本轮没有下载。

**`huggingface/lerobot@53feaef37b67e8f4c23b6953e880ff535e39d6fe`，2026-10-14：**
- `src/lerobot/policies/smolvla/modeling_smolvla.py` blob`8ebf7eecb77c0349631e7683cd9e1adb844103c4`的`sample_actions`先`embed_prefix`与`past_key_values`prefill，然后`euler_integrate`循环去噪，并在后续步骤裁剪suffix KV保留prefix；**共享prefix/KV复用早已存在**。
- `smolvlm_with_expert.py` blob`551292e8a12b65a4e8907391ed1066fa35b38e6d`根据`past_key_values`的有无填充/复用prefix cache，具备多种self/cross attention执行选择。不同`torch.compile`、flash attention、flow步数、真实摄像头和机器人state会改变kernel组合。源码不是已验证单卡109内存/时延资格。

### 3. 可证伪的硬件研究问题，而不是重做KerColle

**Q-V核心：** 真实已发布SmolVLA/相符GGUF权重和合法传感器/语言/state输入，在**多个独立机器人请求确实同时进入GPU**的前提下，应用层成熟异步推理/前缀复用/请求重排之后，是否仍有GPU CTA dispatch HOL或资源互补导致的**完整响应关键路径／deadline miss**？若本质差别只来自server顺序请求、网络序列化、CPU图准备或算法步数变化，这不属于硬件问题。

时间边界三层分账：(a)单请求`predict()`完整执行、VLM-prefill/Action Expert phases；(b)多请求从发起到动作结果的`queue+host preprocess+GPU+response`；(c)如要称机器人系统改进，真实action chunk执行/回控时限与task success另核。**若只需要阶段/SM竞争的架构characterization，(a)+(b)可以做有限原生发现，但不得自称机器人真实成功率提升**。Arrival process的seed、请求ID、相机/语言/state、action step数、dtypes与checkpoint都要冻结；不能拿重复一张合成图片/单server顺序吞吐装多机器人工作量。

**下一项推荐仅CPU/source/资产元数据资格（非GPU执行）**：选`SmolVLA`这一具体model lineage，在作者LeRobot与vla.cpp强路径之间建立`checkpoint/version/license/model bytes→输入episode合法性→precision/flow步数→可复算输出/校准模型语义→可执行GPU phase tags／真实独立请求并发策略`的最小清单。入口可能是官方`lerobot/smolvla_base`或合法对应`vrfai/smolvla-libero-gguf`，但**没有验证它们的byte/hash相同或输出数值互换性**。在源审可确定一条原生不降语义、输入真实的路径之前，不授权权重/episode下载、CUDA build或多请求GPU测试。

**STOP：** 数据/模型不可合法获取、RTX4080内存/ABI不满足、vla.cpp和PyTorch不是可匹配相同科学模型、只有合成输入或串行server、强软件吞掉所有端到端差异 →`VLA_CLAIM_BOUNDARY_NO_GO`或`PLATFORM_QUALIFICATION_PENDING`，并保留结果；不能为了维护VLA选题制造一个虚假多请求问题。

## A55｜跨方向投资裁决、近期论文反证提醒、下轮最低成本

### 1. 两维排序（研究直接性≠资源成本）

| 对象 | 与AI实际体系结构相关 | 直接近邻的新颖性压力 | 真实输入/软件准备门 | 下一最小动作 |
|---|---|---|---|---|
| **Q-V VLA多请求VLM/Action** | 高：真实边缘多任务GPU与控制时限 | **极高：KerColle已研究SM HOL、ICML26已有两阶段/异步、SmolVLA已async** | 中：小模型/预编译runtime存在，但合法episode、checkpoint转换/同语义、并发server缺口尚大 | **优先CPU/source-only**：确定可触发真正GPU phase共执行的强path；无则STOP |
| **Q-G GNN采样→feature→训练** | 高：图式真实AI模型供数与GPU占用 | 高：GraphBolt/SDGraph/GNNDrive和cache已经覆盖直观优化 | 中高：OGB Products真实可得但graph、依赖、外存/随机采样审计成本不小 | 源审一次冻结GraphBolt/PyG模型数据与同采样语义，找到合法完整训练步边界 |
| **Q-S稀疏点云卷积** | 高：直接神经网络、结构映射 | 高：Spira/TorchSparse++/Minuet/FuseFlow | 高：场景许可与多后端artifact较重 | 保留A43，来源/最小scene/合法复用寿命成立再建 |
| **Q-J JEPA** | 中高：新自监督/世界模型训练 | 高：M-JEPA已多mask软件优化 | 高：本轮仅摘要、exact源码和训练输入未核 | 不创建新部署任务；先找到公开exact代码/实验组 |
| **Q-E TBE推荐训练** | 高：大规模真实推荐训练，但不是所有环境有自然IDs | 高：FBTriton/FBGEMM成熟 | 中高：真实分布/optimizer正确性和Ada软件门未知 | 保留A41，先不要为GPU复制B200结论 |

**选择：** A50G是已授权的**唯一109 GPU科学执行候选**，其RUNNING/COMPLETE状态必须由独立Codex报告，Discovery不抢GPU。本轮新增的AI方向若需要调研实作，先集中**Q-V及Q-G的CPU/source-only最小资格**，可与A50G并行，**不是默认创建有GPU的新Lane**。用户偏好科学依赖合并：同一轮审完公开源码、输入/合法性、强软件、模型语义/实验边界，随后只针对真正值得做的一条原生实验建立连续Goal。

### 2. 本次大会程序中新出现的**待全文核**强近邻

2026-10-15查看[PACT2026官方program](https://pact2026.github.io/program/)（会议时间2026-10-19—22，尚未召开）：
- `ESA: Improving GPU Utilization with Elastic Isolation for ML Inference Services`（PACT26 Best Paper Candidate program），与多请求GPU资源隔离/公平/吞吐直接相关；**本轮仅PROGRAM_ONLY，不能声称其采用何机制、结果多少**。VLA/KerColle若有新硬件贡献须避免忽视这一近邻。
- `SLGS: A Structure-Aware Scanline Renderer for Efficient 3D Gaussian Splatting`（PACT26），[作者所属实验室页面](https://escal.yonsei.ac.kr/publications.html)也列出录用。它**是3DGS rendering方向近邻**，未取得全文及机制/原生数据；它与A26GR1重点观察的**训练CPUAdam与交接**阶段不自动同问题。不得只凭标题把它当训练CPU侧有同向硬件收益。
- 同场也有Block-sparse GPU transformer、GPU page-walk、多服务内存等工作；不为了列会议信息就改写AWMA/C16冻结实验。

这两篇高相关作品建议后续获得**实际全文/公开源码**时做一次紧凑精读，重点`实验组workload、硬件、实测/模拟、输入、对照、不能外推范围`；不能只依据日程造论文实验表。

### 3. 下一轮的**最小独立来源资格合同（提案，暂不启动新节点）**

**A56 CPU/source-only联合资格包**：同一控制端/一个CPU-only Codex工作区即可围绕Q-V+Q-G完成，避免人为两个Goal：
- `V1` 固定SmolVLA官方模型及vla.cpp可能使用的GGUF lineage，核实模型checkpoint/LICENSE/precision/flow积分步数/相机-state-text真实请求样本的可获得性（只读Web/git/HF元数据、**不下载权重/episodes**）；核两个服务框架有没有真正多请求GPU phase concurrent路径。若没有，返回`SERIAL_SERVER_NOT_A_CONCURRENCY_BASELINE`而不是自建KerColle长工程。
- `G1` 固定一个GraphSAGE+`ogbn-products`真实任务，核OGB原split/graph loader双向边、GraphBolt pin/miss cache与PyG当前正式发行及CUDA ABI，可否建立同采样分布＋数值的`end-to-end training step`。不下载数据、不启动GPU。
- `D1` ESA/SLGS若有权威公开全文，标明发现，否则保留`PAPER_FULLTEXT_NOT_AVAILABLE`、引用program。**不要为无公开论文无限爬取/猜测**。
- **唯一输出**：两方向`source/asset/implementation/strong baseline/budget authority`准入矩阵＋最多一项下一次真实GPU发现性合同建议；无完整数据/模型语义或无法触发真正GPU并发，最终`NONE_SELECTED`也合格。不重做A51–55这份源审。

**建议默认硬边界（若以后分配Codex才生效）**：node174-new CPU-only，单独Git worktree，CPU≤2有效workers、RSS≤3GiB、新文件≤40MiB、≤2h准备上限；GPU/CUDA、模拟器、模型/数据/依赖下载及安装全部0。若174存在AWMA共享资源竞争则DEFER/STOP。当前这个A56只是下一工作计划，不宣称已经启动或已获机器执行许可。对于控制端能读取的公开源码，未来同一ChatGPT轮次也可直接完成。

## 证据与阅读范围登记（2026-10-15）

| 权威 | 读取深度 | 本次使用的限定信息 |
|---|---|---|
| [SDGraph 2026 FGCS](https://www.sciencedirect.com/science/article/pii/S0167739X26001901) | **ABSTRACT_ONLY** | GPU邻域采样、prefetch、WarpGather；1.89×作者end-to-end摘要宣称，不逐实验表 |
| [DGL GraphBolt 2.5 docs](https://www.dgl.ai/dgl_docs/_modules/dgl/graphbolt/impl/neighbor_sampler.html), [GPUCachedFeature](https://www.dgl.ai/dgl_docs/generated/dgl.graphbolt.GPUCachedFeature.html) | 公开doc＋**固定源码3份** | 功能接口capability，非109平台资格 |
| [OGB nodeprop docs](https://ogb.stanford.edu/docs/nodeprop/) | 官方Dataset说明和shape/split | ogbn-products原始edges、训练任务与处理方向 |
| [FuseFlow ASPLOS2026](https://arxiv.org/html/2511.04768) | **全文HTML重点`8.1–8.3/附录** | 模拟器/数据流、模型×数据组与post-synth RTL相关，不GPU native |
| [Spira](https://github.com/SPIN-Research-Group/Spira/tree/aee69c61f3e001f72828a6d5a70f6a1200166f65) | 复用A38固定4源文件 | 合法mapping/full timer对照 |
| [M-JEPA PACT2026](https://arxiv.org/abs/2609.22674), [会议program](https://pact2026.github.io/program/) | **ABSTRACT + PROGRAM** | 作者A100 5 variants up to1.7×，尚无exact源码审计 |
| [FBTriton作者技术文](https://pytorch.org/blog/modernizing-table-batched-embeddings-with-fbtriton/) | 复用A41作者数值与本轮官方页 | 确切fwd/bwd总和及已有优化，B200不外推 |
| [KerColle PACT2026](https://arxiv.org/abs/2609.22335) | **ABSTRACT + PROGRAM** | 四VLA、两GPU simulated ≤28%；无109 native |
| [ICML2026 VLA XPU](https://proceedings.mlr.press/v306/zhou26e.html) | **正式出版页ABSTRACT** | 现有DP-Cache、V-AEFusion作者效果及success tradeoff |
| [SmolVLA作者](https://huggingface.co/blog/smolvla), [LeRobot源](https://github.com/huggingface/lerobot/tree/53feaef37b67e8f4c23b6953e880ff535e39d6fe/src/lerobot/policies/smolvla) | 官方model介绍＋**modeling / expert固定两源码** | 450M/真实输入域、前缀KV caching、action flow步数 |
| [vla.cpp源](https://github.com/VinRobotics/vla.cpp/tree/cff0cfb5e9e6cab31671d46082f7bdbff078816e) | **固定4源码：arch、usage、bench、server** | engine-only synthetic/REQ-REP sequential多请求无资格 |
| [PACT2026 program](https://pact2026.github.io/program/) | **PROGRAM_ONLY** | ESA/SLGS题目和日程，尚无全文机制与测量 |

**绝对未得到：** 新GPU头寸、任何VLA或GNN在109可执行证明、任何新硬件机制PPA/性能、ESA/SLGS实验表、M-JEPA逐实验组exact原文、VLA作者多机器人并发的固定真实请求到达trace、跨后端数值同一性。上述未获证据不得填补为“常识推定”。