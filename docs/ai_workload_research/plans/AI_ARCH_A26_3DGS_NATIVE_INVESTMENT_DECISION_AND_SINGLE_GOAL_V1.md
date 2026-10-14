# Round A26｜3DGS真实场景投入决策与单Goal门控实验设计（2026-10-14 V1）

**执行者：ChatGPT／AI-ARCH Discovery。**  
**本轮行为：一次性重审A25接受证据、作者冻结源码、原论文及已公布的软件发行元数据；只写GitHub科研协调文件。没有下载自然场景、修改109环境、初始化GPU、发Codex启动指令或创建实验执行分支。**  
**阶段裁决：`CONDITIONAL_GO_FOR_REAL_SCENE_DISCOVERY / NO_GO_FOR_IMMEDIATE_200K_FULL_TRAINING / NO_NATIVE_RESOURCE_APPROVAL_YET / NO_HARDWARE_MECHANISM_ADMISSION`。**

## 0. 本轮究竟同意做什么

用户对[A25联合审查](../reviews/AI_ARCH_A25_A21_A24_JOINT_3DGS_INDEPENDENT_REVIEW_2026-10-14_V1.md)建议“先评估获取真实场景与有限原生诊断是否值得资源，再采用一个明确预算、逐门授权的连续Goal”答复“我同意”。本轮据此完成**价值判断、预算建议和唯一未来合同设计**；由于此前明确指出A25未授予新数据/安装/GPU操作权限，本轮**不把笼统同意自动扩大为下载、装IPEX或锁住109 GPU**。后续在用户明确认可本文件中资源预算并将Goal交给Codex后才启动。

该项目唯一科学问题：在**原生真实Rubble大场景、最强合法GS-Scale host卸载**之后，CPU optimizer、GPU culling、阻塞ID/gradient D2H、H2D状态发布及同步窗口中的**未隐藏完成时间**占多少？能否由线程组织/异步流水/场景和kernel变化解释？这首先是`P08/P14`发现性问题，而非已成立的SM、L1/L2、PCIe或CPU带宽硬件瓶颈。

## 1. 固定证据与实际成本

| 门 | 已知且可追溯（source/producer记录） | 仍缺，不能猜 |
|---|---|---|
| **真实场景输入** | [A21@9575a674…](https://github.com/swayhrl/accel-sim-framework/commit/9575a674e5aa5af60e5803c07399fb64ae2c8488)已由作者README定位自然Mill-19 `rubble-pixsfm.tgz`，HEAD报告Content-Length **9,773,995,561 bytes**（约9.10GiB），作者另提供合并train/test COLMAP；4×缩图、`test_every=83`、文件名排序、真实camera/point cloud | 原压缩包SHA256、授权/下载完整性、合并COLMAP实际manifest/hash、展开/4×生成后占用、每步camera序列、初始Gaussian字节 |
| **算法与阶段** | 固定[GS-Scale公开源`6471e958…`](https://github.com/SNU-ARC/GS-Scale/tree/6471e958f7e318f4870234d8107e0aa91c2d6932)的Rubble preset为**200,000步**、`refine_stop_iter=15000`、`batch=1`；GPU持有means/scales/quats和Adam、CPU持有opacity/SH和Adam；作者已有GPU-only、naive host、optimized host、split模式 | 达到15000及200000步的109真实时间、同一模型规模下CPU/GPU隐藏窗口、真实Gaussian birth/death时间；作者论文原始精确执行commit |
| **平台与环境** | [A24@fc73b042…](https://github.com/swayhrl/accel-sim-framework/commit/fc73b042726ef2312cb62bb9204941ec0ac195d5)：109 i7-13700 Intel 16核/24线程、RAM可用快照60–61GiB、共享文件系统剩余134–135GiB、RTX4080 16GB；现有Python3.11.17/torch2.10+cu126/NumPy2.4不匹配公开作者`Python3.10/torch2.2+cu121/IPEX2.2/NumPy<2` | 新隔离env依赖解析、CPUAdam扩展/PyTorch C++ ABI、实际GPU能否构建和跑完整scene、CPU/RAM/HBM峰值及会否挤占其它项目 |
| **线程混杂** | 冻结`cpu_adam/src/cpu_adam.cpp`中`adam_deferred_update`、`calculate_update_ids`含**`omp_set_num_threads(64)`**，目标16核/24线程；`OMP_NUM_THREADS` alone不会可靠覆盖源码显式设定 | CPU Adam 64线程与合理受限线程方案的真实差异；无法只凭CPU使用率/慢elapsed宣布内存带宽墙。线程限额必须真实验证并作为**独立软件配置身份** |
| **强近邻** | [A23@c096521…](https://github.com/swayhrl/accel-sim-framework/commit/c096521d06483517bf6772689e5cc2c513186173)：GS-Scale优化host状态/CPU Adam；GSArch HPCA25已提出冷热Gaussian buffer/grad/bank思路，但仅获摘要；GS-Cache训练以外的渲染复用 | 完整GSArch实验组、同一场景同强软件数值与实际残余wall；不能用摘要峰值当本机headroom |

**新增原文/源码核查**：[PyTorch官方历史版本页](https://pytorch.org/get-started/previous-versions/)确有CUDA12.1/torch2.2.0分发入口；[IPEX2.2.0 PyPI](https://pypi.org/project/intel-extension-for-pytorch/2.2.0/)有CPython3.10/3.11 manylinux2014 wheels，**不等于目标机器依赖与CPUAdam运行已PASS**。Intel官方[IPEX安装说明](https://pytorch-extension.intel.com/)显示该扩展已计划于2026年3月底EOL，属于可持续性/兼容性成本。冻结`examples/simple_trainer_hybrid_optimized.py`明文导入`intel_extension_for_pytorch.optim._functional`，不能不留identity就替换成现代Torch Adam。

**一个重要时间/状态门**：作者Rubble是200k步训练。若整次只给2h GPU锁，达到200k必须**全流程平均≤36ms/步且无初始化/质量评估开销**；109尚未测到任何有效步耗时，不能承诺完整复现。作者`simple_trainer_hybrid_optimized.py`当前在末步/指定save步保存的主要是`{step, splats.state_dict()}`，**没有明确保存CPU/GPU Adam moments、counter、数据加载器/RNG、densification全状态**；不得仅下载/制造该ckpt冒充合法后期训练resume。短跑前几百步不能外推大规模密集化后的资源行为。

## 2. 工程回报与科学回报：三条路线的明确取舍

| 路线 | 优点 | 核心代价/科学风险 | 决策 |
|---|---|---|---|
| **L0：继续只读小源码/论文轮次** | 0大下载/0GPU | A20–A25对该source族已够成熟，继续重复会产生低新增信息 | **STOP重复源码工作** |
| **L1：同一个门控Goal做真实Rubble资产+隔离环境+有界native发现性诊断** | 真实自然scene、同原训练栈、能首次测强GS-Scale状态交接/完整step等待 | >9.77GB外部档、COLMAP身份缺、旧IPEX/编译困难、可能2h到不了高Gaussian阶段；潜在硬件收益未知 | **唯一`CONDITIONAL_GO`**，先签实际预算且逐门科学核验；可在任何门停止 |
| **L2：立即跑200k步完整收敛/多GPU/新Cache机制** | 有机会取得训练质量或硬件成效 | 运行时长/内存未知、算法近邻非常强、真实硬件残余0证据、200k训练无法由有限预算保证 | **`NO_GO`**，不得自发执行或因L1成功自动续跑 |

价值门不是要先得到漂亮速度比，而是通过最低本机数据判断**(a)**强GS-Scale完整step中是否真的存在不能重叠的CPU/host状态服务；**(b)**软件线程、GPU-only可fit状态、动态Gaussian规模是否混杂；**(c)**是否值得另申请真实资源反事实。没有这些就不开发高斯cache和原子新机制。

## 3. 唯一连续Goal草案｜A26G单场景原生诊断（未获重型资源批准）

**拟执行者**：原109 **Lane M**复用Codex窗口，新的`hrl/aiarch-a26g-gsscale-rubble-gated-native-109-v1`分支和独立worktree（**目前未创建执行分支，不意味着正在运行**）。独立审查仍由ChatGPT／AI-ARCH Discovery。

所有阶段共享同一输入、作者代码、软件版本和资源预算；正常的小接口/manifest/构建问题在已批准的范围内**solve-and-continue**，不要人工拆A27/A28/A29等Goal。**没有理由在每个小工程问题处人为STOP；若科学输入、算法语义、下载/设备预算超界则STOP。**

### G0：只读身份/预算预检（必须在任何大下载前）

- Fetch本GitHub固定协调合同、A21–A25 accepted来源及作者代码`6471e958…`；核当前磁盘、RAM、根/共享盘、CPU/GPU锁、系统driver/ABI只读版本，确保老NequIP/C16/AWMA不被影响；先只读核官方数据下载权限、HEAD长度/accept-ranges、合并COLMAP文件清单/版本、gsplat/Torch/IPEX/NumPy依赖可获得性/版本。**缺合并COLMAP真实可复现身份和必要数据使用权限即STOP**；不得改用第三方未核同名数据或合成pose。
- **确保论文所需场景科学对象没被偷换**。可以先有一个轻量metadata manifest记录UNKNOWN，但不能从原Rubble raw的一小张照片/随机3D Gaussian声称已经得到“训练应用benchmark”。确认expanded tar与处理临时文件是否会超磁盘预算；不明就保留`STORAGE_BOUND_NOT_ESTABLISHED`，不无界尝试。

### G1：有界资产及环境资格（仅在明确同意重型预算后）

- 在**新目录**以固定source URL下载`rubble-pixsfm.tgz`，完成SHA256、header/安全tar entry audit；拒绝路径穿越、异常链接、无界解压；合并COLMAP到同一个合法scene manifest；4×处理、相机/文件名排序、train/test index，记录每个必要`cameras/images/points3D`文件hash及从原文件的派生步骤。**不要求原本未披露的hash事先匹配假定值**，接受新产物有可审来源身份，不声称作者原实验同byte。
- 隔离Python3.10+Torch2.2/cu121+IPEX2.2/gsplat/CPUAdam完整环境；先在CPU侧检查精确发行和原`cpu_adam`ABI/线程行为，再做GPU readiness。**旧环境全只读**。作者旧源固定不能默认改成最新gsplat/Torch新后端；如果冻结依赖不可安装，最多按预批准同版本、同语义小包装修复；遇到需要跨大版本/更换算法/源代码静态数据行为则STOP。
- 作者CPUAdam**硬编码64 OpenMP线程**，不能仅设`OMP_NUM_THREADS=1`假装安全。先检测`OMP_THREAD_LIMIT`/进程affinity能否在不改CPUAdam核心算法下实际封顶并记录完整有效线程数；不成立时STOP或提交`THREAD_RESOURCE_UNQUALIFIED`，不得大幅并发运行干扰共享机器。任何选优线程配置作为软件策略变化另行标记，数值/质量需重新核。

### G2：原生功能与质量canary（须G0/G1与GPU共享锁均通过）

- 使用作者一份真实完整Rubble数据源、固定相机/点云初始化，先进行最少必要的真实train step与forward/backward/CPU Adam，覆盖GPU-only（若在对应匹配规模合法fit）与full GS-Scale；严格检查loss、梯度、状态更新、训练camera、Gaussian数量和基本PSNR/SSIM/LPIPS API。**短程仅属于functional+early-step资格，不是200k完整收敛或time-to-quality**。
- 两条软件训练算法/optimizer epsilon和densification可能不同，首先记录数学差异，允许`APPLICATION_QUALITY_CONTRACT_PENDING`，不放宽容差凑`BITWISE_EQUIVALENT`。如果只能跑作者optimized host单臂，则只认证它的完整step；GPU-only OOM只报告容量结论，绝不构造计时分母。

### G3：有界真实等待诊断（只在G2合格且同一GPU预算内）

- **预注册科学窗口**：热身并跳过最早初始化，先观察初期真实camera窗口（例如step100–200）；若预算允许再观察densification阶段与其停止边界`refine_stop_iter=15000`（例如step14500–14600、step15100–15200）。观察窗口只反映其真实训练进程达到的状态，**不能跳到只含splats的普通checkpoint、重置optimizer或拿随机Gaussian冒充后期状态**。若在保守耗时估计下到不了后期，标`EARLY_TRANSIENT_ONLY / REPRESENTATIVE_LATE_STAGE_NOT_EVALUATED`并按时STOP。
- 分离**未插桩完整step wall**、诊断插桩GPU时间、CPU Adam/ID D2H/grad D2H/H2D及synchronize/join等待、重叠区间union（不能分段时间相加当wall），并记录相机ID和Gaussian ID的birth/death与active-set（跨densify重新映射）、真实copy bytes、GPU alloc/reserved及host/pinned peak。
- 仅对同一合法scene/软件策略和可比训练状态计算paired wall；没有相同状态/训练阶段就并列报告、不填速度比。诊断与未插桩分开，GPU-only OOM不可变成“无穷慢”。作者的`omp64` vs有效CPU线程上限、CUDA allocator和相机排序均显式报告。**禁用正式NCU/NSYS/NVBit、模拟器、SM quota扫参、Cache/原子新机制**。
- 若在至少两个独立相机/训练窗口有来源闭合、可观且未被软件调度吸收的host/设备服务时间，才标`SCOPED_EXPOSED_SERVICE_CANDIDATE`；否则`SOFTWARE_ABSORBED_OR_UNIDENTIFIABLE`。**即便标candidate也不是新的物理资源机制或已证明可加速。**

### G4：收口与结果分层

无论在哪门STOP，都发布输入/软件身份、实际资源账、原生正确性与**所达到的真实step阶段**，分别报告`REAL_SCENE_BYTE_QUALIFIED`、`SOFTWARE_RUNTIME_QUALIFIED`、`EARLY_FUNCTIONAL`、`LATE_STATE_OBSERVED`、`EXPOSED_SERVICE_IDENTIFIED`或`NOT_EVALUATED`。保留164独立小日志归档选择，但**不能复制巨型数据到164或覆盖旧authority**；只提交小型输入manifest/代码补丁/报告/哈希到**新执行branch**。科学评审前不merge协调分支，完成/STOP不自动升级新机制。

## 4. 建议一次性实际预算——全部仍为`PROPOSED_NOT_APPROVED`

| 资源轴 | 研究建议上限 | 设计理由及严格STOP |
|---|---|---|
| 外部下载/新增软件与数据 | **≤25GiB累计**，只有官方Rubble、作者合并COLMAP与已锁发行版本；超出或权限不明STOP | 原raw约9.10GiB；合并COLMAP与旧软件轮子大小未知，25GiB只是预算上限不是已知实际需求 |
| 新磁盘总增量 | **≤60GiB**（包括压缩包、解压、缩图、隔离env、cache、ckpt、运行日志）；须另保留**≥64GiB物理可用余量** | A24盘约134–135GiB快照，只说明理论上可能有空间；未知展开/ckpt不能挤掉旧工作 |
| host RSS/RAM | **≤48GiB**总任务峰值，包括DataLoader/CPU optimizer/pinned buffer，CPU并行尊重目标109独立隔离 | 主机约62–63GiB物理RAM，快照可用60–61GiB；32+GiB未知时需先预算 |
| CPU threads | 目标有效并发**≤24逻辑线程**，必须在CPUAdam实际执行时验证`omp_set_num_threads(64)`可被硬限或隔离控制；不能靠声称OMP_NUM_THREADS设置就PASS | 16核24线程机器，避免大CPU线程超卖；若源码级线程更改不可避免，另记方案身份与质量并按科学门STOP |
| GPU设备/锁 | node109**同一RTX4080**，`/data/c16/locks/c16_gpu_campaign.lock`非阻塞，累积持锁**≤2小时**；只允许单卡原生资格/早期诊断，不代表能完成200k训练 | 真正GPU阶段必须另获此预算明确批准，别的项目运行则DEFER；不删锁/不驱动reset |
| 显存任务上限 | **≤14GiB**，报告allocated/reserved/任务实际峰值，超限按科学合同STOP，不改输出/分辨率硬跑 | RTX4080 16GB留下安全余量；GS-Scale作者4080 Super成功不能保证109 |
| CPU环境/准备总时长 | **≤4小时**的受控下载/环境/转换准备；不可超过资源预算无限解决工具问题 | 同一个Goal内可有界fix少量路径/元数据/依赖包装，不把工具失败升级成科学失败；超界STOP |
| GPU样本和归因 | 单个Rubble自然scene、最多三段预注册真实训练窗口，GPU-only对照只有确实同条件fit时；**不授权完整200k收敛** | 没有足够后期步时保留早期资格；不得编造达成质量、late-stage headroom或模拟资源收益 |

**决策关系：** 用户目前“同意下一步”只批准本ChatGPT**做价值评估与合同准备**；以上下载/安装/正式109 GPU预算没有在此前对话中作为一项明确具体方案获得新的授权。若后续用户批准这些封顶数值，只需把**本文件作为唯一执行科学合同与批准记录**交给原109 Lane M窗口，新建一条独立Goal，连续按G0→G4推进。不能把准备分支/Goal文本当成已启动。

## 5. 实际投入价值的最终判断

**推荐：保留唯一`Q-A20-GS`并将其停留在`READY_FOR_BOUNDED_NATIVE_APPROVAL`，不执行完整Rubble 200k训练，也不继续拆新的小源码/依赖Goal。**

这样推进的理由是：真实输入、16GB消费级GPU和强GS-Scale方法对`CPU–GPU状态寿命`确实具有体系结构研究价值；但当前缺的是**强软件之后的可归因原生时间残余**，不是缺一个Cache方案。有限G0–G3若能确认这个残余，才值得继续申请真正物理资源因果与GSArch全文近邻审查；若软件已隐藏或预算无法到达有效动态Gaussian状态，应该直接`NO_GO/PARKED`并寻找其它AI负载。

**不会从此合同自动启动109任务，不修改C16/AWMA/NequIP旧环境与科学authority，不重启GreenCtx。**
