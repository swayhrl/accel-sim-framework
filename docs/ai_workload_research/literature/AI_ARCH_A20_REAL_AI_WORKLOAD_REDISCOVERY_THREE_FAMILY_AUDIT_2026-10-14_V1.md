# Round A20｜回归AI负载：3DGS、MLIP/MD、HSTU三类真实状态生命周期的实验组与强软件核查

**执行者：ChatGPT／AI-ARCH Discovery。日期：2026-10-14。**  
**阶段属性：`SOURCE/PAPER_RESEARCH_ONLY`，没有新109 GPU、174模拟器、Codex、模型训练、数据下载或任何旧分支变更。**  
**总裁决：`A20_THREE_FAMILIES_SCREENED / P14_3DGS_RESEARCH_PRIORITY_ONE / NO_NATIVE_GPU_ADMISSION / NO_NEW_HARDWARE_MECHANISM`。**

## 0. 出发点：不再追Green Context接口，回到具体AI行为

- 已独立接受的NequIP：原生OAM-S、32个Si静态结构、四臂完备energy/forces/stress，结果`ACCEPT_SCOPED_NATIVE_MIXED_RESPONSE`，主要体现B和CPU/GPU构图软件组织的变化。[A11](../reviews/AI_ARCH_ROUND_A11_LANE_M_T_JOINT_INDEPENDENT_REVIEW_2026-10-13_V1.md)。
- A16R1 Driver Green Context在109真实76SM中成功分配38SM，256输出tiny kernel正确，但G3仅source/capability、没有实际同进程模型执行，G4未跑。[A19](../reviews/AI_ARCH_ROUND_A19_LANE_M_A16R1_GREEN_G3_INDEPENDENT_REVIEW_2026-10-14_V1.md)。**该路线已经按原合同结束**，不能从API资格推SM资源新瓶颈。
- 因此优先问：不同真实AI模型/场景输入导致的**活动集、状态寿命、准备/迁移和完整执行时间**，是否在成熟软件之后仍暴露硬件资源限制？这不等于先设计新cache后找workload。

阅读方法：**原文报告中的真实实验对象、代码能力、作者归因、本研究推断分别列出**。未核的模型输入文件hash、GPU时间线、数值质量、最大容量不作填补。

## 1. Family A｜大场景3D Gaussian Splatting训练：当前最有研究价值的候选

### 1.1 固定作者原文与代码（严格区分发表实验和最新代码）

- **原论文**：[GS-Scale: Unlocking Large-Scale 3D Gaussian Splatting Training via Host Offloading](https://arxiv.org/html/2509.15645)，ASPLOS 2026正式发表（本轮实际阅读arXiv HTML的§2–§5、重点§3.2–3.4、§4.2–4.4、§5.1–5.8、Table1–3和文字结果；未从PDF图像逆推全部曲线）。
- **公开实现快照**：[SNU-ARC/GS-Scale@`6471e958f7e318f4870234d8107e0aa91c2d6932`](https://github.com/SNU-ARC/GS-Scale/tree/6471e958f7e318f4870234d8107e0aa91c2d6932)，README blob`3785173f83be3e95515bbc67a959ae5e8f4dbaf8`、`install.sh` blob`8d793af62397fae2385a74ef186267b0342f2466`、`examples/simple_trainer.py` blob`c16b7b34e277401f675d0f6c9554f73c88df6660`、`simple_trainer_hybrid_baseline.py` blob`9993a462219d32aa5bd372b3d520f24bdb5fdd28`、`simple_trainer_hybrid_optimized.py` blob`e37d13e3f7514aa81320994dab9853b06a9bb275`、`cpu_adam/src/cpu_adam.cpp` blob`f1b40eb4283cfd95c9b26b01448d7275f5aa0958`。
- **不能反向宣称**上述2026-10选取的Git`main` HEAD就是作者ASPLOS论文全部原始运行的精确commit。论文报告在**gsplat v1.5.0、CUDA12.4、torch2.2.0**，其当前公开`install.sh`建议`torch2.2.0+cu121`、Intel Extension for PyTorch 2.2.0；源码README明确**当前仅支持Intel CPU**。这些差异与目标109的旧`torch2.10+cu126`及其CPU品牌/ISA**未核实**，不能只因GPU为RTX4080就宣布本机可运行。
- **严格的强软件对照**：论文/代码公开三条路径：原`gsplat` GPU-only `simple_trainer.py`、naive offload `simple_trainer_hybrid_baseline.py`、已优化GS-Scale `simple_trainer_hybrid_optimized.py`，还有`_split.py`处理极端视图。**不能只与naive host offload比较，然后把收益声称为新硬件headroom。**

### 1.2 原文逐实验组接受范围

| 组与原文位置 | 对象、输入与平台 | 控制和比较 | 作者真正给出的有限结果 | 科学不能推出 |
|---|---|---|---|---|
| A-S1，§3 Fig3/4 | Building真实场景，变化分辨率；其它大型真实场景统计 | 固定3DGS训练，分析不同状态类型占比与每step可见Gaussian集合 | Building的Gaussian参数/梯度/优化器状态约占显存90%；大型场景训练一次step平均实际使用**8.28%**的Gaussians | 不代表所有3DGS场景固定8.28%、也不说明这8.28%跨step时间复用 |
| A-S2，§5.1 Table1/2 | **真实Mill-19 Rubble/Building、GauU-Scene LFLS/SZIIT/SZTU**及合成MatrixCity Aerial；RTX4070 Mobile/RTX4080 Super/H100 PCIe；分辨率如Rubble1152×864、LFLS1600×1064、Aerial1600×900 | 作者gsplat v1.5.0，单图像batch1，质量指标PSNR/SSIM/LPIPS；不同densification配置调Gaussian数量 | 真实场景与消费级GPU执行分母存在，含单张16GB**RTX4080 Super**，比纯H100 16卡的论文更接近本地节点 | **RTX4080 Super≠RTX4080**，且CPU、GPU带宽、代码版本不同；不能据此断言109实际速度 |
| A-S3，§5.2–5.4 Fig11/12 | 同6场景、笔记本/桌面；部分小化场景便于GPU-only可比，Aerial初始化时GPU-only已OOM | GPU-only、naive host offload、优化后无deferred、完整GS-Scale | 相对GPU-only的峰值allocated GPU memory几何均值降约**3.98×**；对naive offload epoch吞吐几何均值提高笔记本**4.47×**、桌面**4.57×**（排除OOM），不是相对GPU-only；作者报告GS-Scale/GPU-only吞吐geomean笔记本**1.22×**、桌面**0.84×**，OOM点排除 | “节约内存”不等于同比加速；不把不同densification产生的不同高斯个数当同一工作量；OOM GPU-only时无法得完整paired时间 |
| A-S4，§5.5 Table3、§5.6 Fig13 | 同六场景；显式质量与容量点 | 以相同训练设置比较训练质量，扩大可完成Gaussian数量 | Rubble质量Original PSNR26.63、GS-Scale26.62；Aerial 27.69/27.66。作者RTX4080 Super约**9M→40M**的可训练Gaussian容量扩展，几何均值LPIPS下降30.5% | GS-Scale的deferred Adam近似**忽略ε项**，质量指标接近不等于每个step梯度/参数bitwise相等；最大模型规模变了，不能把质量提升全归单次kernel速度 |
| A-S5，§5.7–5.8 Fig14–16 | H100 PCIe多NUMA server、4070Super/4090 GPU、Rubble分辨率与mem_limit扫描 | 改分辨率、GPU整机、image split阈值，观察host/GPU相对吞吐 | 作者指出高GPU/CPU内存带宽比不利于隐藏host更新，**PCIe不是作者所测主耗时**，NUMA/CPU随机访问也是实际因素；mem_limit越低省显存更多但多次cull/gradient accumulation拖慢；图像分辨率高使GPU执行更长也可能给CPU更新更多重叠窗口 | 更换整张GPU同时改变SM、HBM带宽、容量、kernel和CPU平台；不能由平台比率直接推单独扩CPU/PCIe带宽的物理因果 |

**每条是作者报告，不是本项目原生测量或保证本机可重现。** 其“epoch throughput”与NequIP前轮的`32-frame eval wall`不是一个时间分母。原代码中`set_random_seed(42+local_rank)`只是训练seed入口；自然场景camera、COLMAP、点云预处理、train/test split及动态densification历史仍必须以实际文件hash/完整运行记录冻结，不能只靠seed称输入完全复现。

### 1.3 最近邻反证：不能再声称下列基本机制是空白

- **GS-Scale本身**已经把参数与Adam optimizer states放host、活动子集迁移GPU，通过GPU frustum culling、parameter forwarding、deferred update、image splitting优化；`cpu_adam.cpp`已有OpenMP并行和deferred update/计数接口。
- **GSArch，HPCA 2025**：[IEEE原文摘要](https://ieeexplore.ieee.org/document/10946749/)明确提出按Gaussian热点冷热分片上buffer、低贡献梯度过滤及bank conflict重排，并报告专用架构评价的有限收益；它不是RTX4080强软件原生结果，但**“缓存热点Gaussian/降低atomic冲突”已有硬件最近邻**。
- **GS-Cache**：[arXiv:2502.14938](https://arxiv.org/abs/2502.14938)已经讨论跨帧计算缓存，但主要是**渲染inference**而非GS-Scale的可训练Adam状态，不能相互等价；只是对泛化“Gaussian跨帧缓存全新”的反证。
- **2026 3DGS²-TR**：[ICML 2026正式发表](https://proceedings.mlr.press/v306/hsiao26a.html)提供矩阵无关的二阶训练近邻且训练质量/迭代数改变，与固定Adam的软件同语义A/B不同。

### 1.4 A20唯一优先候选Q-A20-GS（目前仍非执行合同）

> **在高质量大场景3DGS的强软件GS-Scale已经实现稀疏状态迁移/延迟优化器更新后，剩余的完整训练时间损失究竟受host内存服务、可隐藏重叠窗口、GPU梯度/原子聚合，还是图像/活跃集规模长尾主导？这些约束随场景和GPU:CPU资源配比如何迁移？**

这是`P08/P13/P14`交叉的**发现性问题**，而不是直接提出Gaussian专用cache。最小严谨观察合同须同时分离：
- **正确性/质量**：同数据版本、camera和初始化、同训练优化器/数值及有效dense/sparse update，另报PSNR/SSIM/LPIPS和完整训练收敛；不要拿NequIP原来5e-5等价门强加到GS-Scale论文含ε近似的训练策略上。
- **两种不同实验分母**：同一Gaussian规模/场景的完整step/epoch时间（含cull、CPU Adam、D2H/H2D、排序、forward/backward、optimizer同步），以及给定显存能完成多少Gaussians的**容量—质量前沿**。绝不能把不同模型容量下的吞吐和画质直接当纯硬件单因果。
- **动态工作集身份**：每train step的camera ID、可见Gaussian ID集合、与前后多个step的集合交集/失效时刻、densification时的ID重用/新增删减、CPU optimizer的真实更新与迁移bytes，及必要的epoch统计。**8.28%平均活跃比例不是时间复用率**，不能据此宣称cache可提升8倍。
- **资源与强基线**：仅在本机确实可以跑已优化GS-Scale、或一个有合法数值/质量匹配的gsplat强路径后，才考虑整步时间中的host/内存/PCIe/GPU关键路径；CPU Intel IPEX与torch2.2的环境资格、真实数据SHA、场景授权/磁盘、高斯数量和时间预算均未通过。
- **明确反证**：作者已经报告PCIe在其测试中耗时较小、host优化已重叠、热点片上缓存与atomic专用硬件已有近邻；如果本机强实现也无可分辨的大wall残余，或残余由软件camera order/compile/kernel选择解释，**STOP新Cache/硬件机制**。

**当前准入等级**：`GS_SCALE_STRONG_SOFTWARE_PAPER_CODE_CONFIRMED / REAL_SCENE_INPUT_AVAILABLE_EXTERNALLY / LOCAL_FULL_TRAINING_AUTHORITY_MISSING / P13_HARDWARE_HEADROOM_UNKNOWN`。下一步优先做一次**source/asset资格**，不能马上跑GPU、下载大场景或宣称有一篇硬件新论文。

## 2. Family B｜MLIP/MD：真实物理语义，但新图重建不是空白

- **本机既有原生**：NequIP OAM-S Si静态32帧完整energy/forces/stress，`N-C2/G2/G4/G8`总wall **20.758/26.044/13.548/7.602 ms**；属于不同batch组织，不代表连续真实MD时间。
- **成熟作者近邻**：[NequIP等变势训练/推理AOT与OEQ](https://doi.org/10.1039/d5dd00423c)，2026，作者报告专用AOT/TP加速MD若干形状（上限5–18×，不得直接写为单RTX4080）；[NVIDIA ALCHEMI Batched Molecular Dynamics NIM原生性能说明](https://docs.nvidia.com/nim/alchemi/alchemi-bmd/latest/performance.html)明确benchmark采用MACE-MPA-0、NVT与time-per-atom-per-step分母，RTX6000 Ada 7.34μs/atom/step（估算40k atom batch），且系统在启动时估算最优batch；不同MACE/OAM-S、硬件和NVT/静态评估，**数字不能直接比较**。
- [Zhang & Guo, NEMP，Chemical Science 2026](https://doi.org/10.1039/d5sc07248d)原文可核的摘要/结论明确报告把张量积从edge改到node空间、降低内存/计算量、以及通过CPU邻居表与GPU力计算异步流水处理大体系；其CPU-only或GPU benchmark模型/导数阶/具体数据未按图逐一完整审读，归类`PAPER_AUTHOR_ABSTRACT_PLUS_SELECTED_TEXT`，不伪装成整篇实验组audit。
- **最近邻**：重复“提出CPU/GPU邻居表流水”“用skin减少重建”“把大edge tensor搬到更少node tensor”并非无人做过。未来如果有连续真实MD trajectory、合法邻居skin失效与多模型强kernel，才有P10的**真实拓扑寿命**研究；当前NequIP tutorial110帧没有资格声称相邻时间采样，**本轮不给新的native GPU Goal**。
- **科学决定**：`P10_NATIVE_STATIC_COMPLETE / MD_TRAJECTORY_NOT_QUALIFIED / STRONG_SOFTWARE_NEAREST_WORK_EXISTS / PARKED`。

## 3. Family C｜HSTU推荐与embedding：强软件对照罕见地公开了负收益

- **实际公开代码来源**：[NVIDIA/recsys-examples@`6b983fc950ac49bd131e0411d6e72968e9f343bf`](https://github.com/NVIDIA/recsys-examples/tree/6b983fc950ac49bd131e0411d6e72968e9f343bf)，[`examples/hstu/training/benchmark/E2E_BENCHMARK.md`](https://github.com/NVIDIA/recsys-examples/blob/6b983fc950ac49bd131e0411d6e72968e9f343bf/examples/hstu/training/benchmark/E2E_BENCHMARK.md) blob`0627baa1973444b9d91688f8443a85a88bba3dd1`；[`inference/benchmark/README.md`](https://github.com/NVIDIA/recsys-examples/blob/6b983fc950ac49bd131e0411d6e72968e9f343bf/examples/hstu/inference/benchmark/README.md) blob`254615cb20d710a210d8485d426e27420c4810cf`。
- **HSTU训练真实执行外部报告**：2个节点**16×H100-SXM5 80GB**，8层/hidden1024/4头/每头256，DynamicEmb的item与user_id各**5000万行×128维**，batch per GPU32、maxSeq4096、optimizer Adam；训练1000 iter。**长度Zipf(α1.2)，ID Zipf(α1.05)均为合成生成**，不是公开自然用户历史或原用户token bank。发布的版本是2026-10所选Git snapshot，原训练trace run标`cwdfw_benchmark_cont_full_nsys_20260528_202615`/代码commit`bc40d89c`，本窗口未取得作者对应原raw或确认它与现行HEAD一致。
- **依次累计的对照，不是每项相对于原baseline单变量**：

| 实验组 | 平均TFLOPS/GPU（作者） | 对前一组的实际变化 | 与基础baseline总体比（作者） | 解读 |
|---|---:|---:|---:|---|
| E0 Triton no shuffler | 75.6 | — | 1.00× | 原基线 |
| E1 +workload-balanced shuffler | 115.8 | +53.2% | 1.53× | Zipf长度不平衡有软件机会 |
| E2 +CUTLASS HSTU Attention | 302.6 | +161.3% | 4.00× | 换强kernel影响最大 |
| E3 +DynamicEmb HBM cache | 296.8 | **-1.9%** | 3.93× | 扩大缓存能力≠提高当前吞吐 |
| E4 +hash-roundrobin placement | 308.6 | +4.0% | 4.08× | 数据布局改善 |
| E5 +prefetch pipeline | 310.6 | **+0.65%** | 4.11× | 预取净headroom极小 |

- 作者profile的最优window里，最后一项只使显式prefetch kernel时间约0.014ms；文档直述NCCL在该比较窗中是较小份额，重叠空间有限。切勿从“巨大embedding表”直接推全部step主要等待主存/PCIe。
- **HSTU inference公开单L20实验也用合成序列**（长度256→4096、候选256个、batch1/2/4/8），KV cache与CUDA Graph共同变化，报告整推理1.3–2.6×，但不能只归因于一个cache改动；B200 block结果的head维与L20不同，不能跨设备比较。
- **科学决定**：`P03/P05_HSTU_STRONG_SOFTWARE_AVAILABLE / SYNTHETIC_ZIPF_INPUT_ONLY_IN_AUDITED_GROUP / 16H100_RESOURCE_MISMATCH / NO_NATIVE_ADMISSION`。如未来有真实用户序列与受控部署，值得研究不平衡与embedding驻留；当前不给109 16GB复刻任务。

## 4. 跨三家族的结构区别：为何选3DGS而不是继续用NequIP静态batch或合成推荐

| 目标资格 | GS-Scale/3DGS | NequIP/MLIP | HSTU |
|---|---|---|---|
| 明确真实应用输入 | **5个真实场景＋1个合成场景**，原论文明确 | 本地32个真实但独立Si静态几何，不能声称连续MD | 本次作者训练与推理基准**合成Zipf** |
| 已发表接近109的设备 | **RTX4080 Super 16GB**，同容量/代际但不等机型 | 本地RTX4080 16GB已原生QUALIFIED | **16×H100 80GB**训练，单L20 synthetic推理 |
| 成熟强软件和开源代码 | gsplat GPU-only、naive host、完整GS-Scale，读到实际代码 | NequIP AOT+OEQ、ALCHEMI、NEMP等 | CUTLASS、shuffle、DynamicEmb、KV Graph |
| 数值/质量身份 | 真实场景PSNR/SSIM/LPIPS，但deferred Adam不是bitwise相等 | 原包数值和边multiset强，但无真实MD连续时序 | 这组合成benchmark无可冻结真实用户token bank |
| 已有系统/硬件近邻覆盖 | **很强**：GS-Scale软件与GSArch缓存/atomic；需找到剩余实际成本 | **很强**：AOT、GPU NL、异步skin、node-space算子 | **很强**：动态embedding和预取已有，当前cache甚至负吞吐 |
| 当下最短有价值步骤 | **只读锁定一个自然场景、软件版本/训练语义、host资源和真正工作集ID；尚不GPU** | 继续需要自然时间轨迹/跨模型质量；不再重复B2/G8 | 需真实用户序列和更合适平台，暂缓 |

**选择依据不是“已有哪款模型下载”**：3DGS在真实消费级16GB GPU、自然场景、训练全链time/quality上有最强现成依据，即使它的软件机会已被占用，仍最适合用来学习硬件headroom必须满足的可辨识性门。

## 5. 唯一下一阶段准入建议：`Q-A20-GS`先做源/输入资格，不开发机制

**问题：** 在强GS-Scale软件已将大部分3DGS显存状态移到host并流水化更新后，*完整真实训练*剩余的CPU内存带宽/隐藏窗口/可见集长尾是否形成可重复且具有工程成本的约束？

**最小可证伪的source/identity合同（尚未执行）**：

1. **源与方法冻结**：原公开Git commit`6471e958…`及gsplat所依赖精确依赖版本，CPU端Intel Extension/torch2.2/cuda工具链，确定被比较的GPU-only与GS-Scale原代码目标；只读环境检查能否在原node109替代安装，**不动现有torch2.10/cu126和C16/AWMA环境**。若需新大环境，先报告储存/RAM/GPU预算与无污染隔离策略。
2. **真实输入**：优先Mill-19 Building或Rubble（而非拿合成Aerial优先），需原始图像、pixsfm/Colmap、点云版本，真实camera列表与选样/分辨率、训练/验证划分、作者提供的数据处理步骤，精确大小、SHA/来源。**本次没有下载任何数据，亦未授权**。数据过大/没有可复现许可则`INPUT_BLOCKED`不做原生任务。
3. **强软件时间与质量语义**：固定相同Gaussians/初始化、camera顺序和densification/Adam配置，对GPU-only和GS-Scale报告每step与完整epoch wall（CPU优化器、GPU kernel、D2H/H2D、等待同步全部计入）、CUDA alloc+reserved峰值、CPU RAM、实际字节传输以及PSNR/SSIM/LPIPS。基线OOM只支持容量可完成性而不是吞吐成对比较。
4. **存在真正“硬件剩余”的最低门**：观察`wall`中有可核的未被异步隐藏的GPU/host资源服务时间，并有至少一种合理的**单因素物理资源干预或可靠模型**把它和软件camera/场景/编译切换分开；记录强软件支持的自动分组、defer与image-split成本。若没有则`SOFTWARE_ABSORBED/PARKED`。
5. **独立样本**：一个训练场景用于方法，另一个自然场景或固定部分iteration作为独立检查，不预先盲搜阈值再把同组结果当holdout；任何GPU执行、下载、环境安装、profile或新硬件机制必须新合同及显式资源审批。

**当前科学状态：`Q_A20_GS_PRIMARY_SOURCE_AND_INPUT_FEASIBILITY_CANDIDATE / NOT_A_GPU_GOAL`。**

用户此前要求工具问题一次性闭环；因此下一阶段**不再人为拆成数据URL检查→环境wheel检查→源码核查三轮**。如果批准正式启动，按一个CPU/source-only Goal一次完成全部可公开验证的source/input/resource预算及强基线资格，**不要中途启动GPU或下载大型场景**。科学/数值语义、主执行软件路线、预算或场景范围变化才STOP。

**本轮裁决：3DGS优先进入下一次CPU-only完整源/输入准入，MLIP和HSTU有明确强最近邻与场景缺口暂不继续；0项新的GPU/模拟器和硬件机制资格。**
