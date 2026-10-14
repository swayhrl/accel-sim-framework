# AI-ARCH A26G｜真实Mill-19 Rubble的GS-Scale门控原生问题发现：一条连续Codex Goal

**科学设计/最终独立审查：ChatGPT／AI-ARCH Discovery。**  
**执行者：既有Codex Lane M／node109，仅新独立worktree、独立branch `hrl/aiarch-a26g-gsscale-rubble-gated-native-109-v1`。**  
**授权：用户在阅读[A26量化预算/科学合同](../plans/AI_ARCH_A26_3DGS_NATIVE_INVESTMENT_DECISION_AND_SINGLE_GOAL_V1.md)后明确答复“我批准。如果涉及到codex执行，你尽量一次给出建议，不然效率太低”。因此本Goal仅授权该A26范围的**单场景、单GPU、门控、条件性下载/安装和有限真实诊断**；不授权完整200k训练、换科学对象或新机制。**  
**最终状态：`EXPLICIT_USER_APPROVAL / READY_FOR_USER_TO_SEND_TO_CODEX / NOT_STARTED_BY_CHATGPT`。**

> **唯一科学问题**：真实Rubble强GS-Scale软件在RTX4080上完成训练step时，CPU Adam、可见ID/梯度回传、host状态H2D、GPU renderer/backward及同步中，有没有**未被软件重叠隐藏的完整wall关键时间**？能否与CPU线程超卖、相机顺序/动态Gaussian、算法与弱实现区分？本轮先发现现象，**不自称找到了SM/L2/PCIe瓶颈或设计新Cache**。

## 0. 冻结起点和已审证据——不要重复再开小Goal

- 执行前必须从GitHub fetch并验证**本Goal所在的固定协调提交**（以最终启动消息给出的完整SHA为准）、本文件Git blob和紧邻的[A26G用户授权回执](AI_ARCH_A26G_GSSCALE_RUBBLE_GATED_NATIVE_109_APPROVAL_2026-10-14.md)。在独立branch/worktree写代码与结果，不在协调branch及原Lane M A16R1、NequIP V1R1、C16/AWMA历史目录commit。**创建Git branch不表示节点执行已开始**。
- 已接受的联合scientific authority：[A25](../reviews/AI_ARCH_A25_A21_A24_JOINT_3DGS_INDEPENDENT_REVIEW_2026-10-14_V1.md)；Lane T [A21真实Rubble输入来源](https://github.com/swayhrl/accel-sim-framework/blob/9575a674e5aa5af60e5803c07399fb64ae2c8488/docs/ai_workload_research/reviews/AI_ARCH_A21_GSSCALE_REAL_SCENE_SOURCE_ADMISSION_174NEW_V1.md)、[A22动态状态依赖](https://github.com/swayhrl/accel-sim-framework/blob/3b46ae8f94b5a72d1af4e06d352058bd2140abe6/docs/ai_workload_research/reviews/AI_ARCH_A22_GSSCALE_STEP_STATE_LIFETIME_SOURCE_MAP_174NEW_V1.md)；[A23强硬件近邻](https://github.com/swayhrl/accel-sim-framework/blob/c096521d06483517bf6772689e5cc2c513186173/docs/ai_workload_research/reviews/AI_ARCH_A23_3DGS_HARDWARE_PRIOR_AND_RESIDUAL_SCOPE_174NEW_V1.md)、[A24主机资格](https://github.com/swayhrl/accel-sim-framework/blob/fc73b042726ef2312cb62bb9204941ec0ac195d5/docs/ai_workload_research/reviews/AI_ARCH_A24_GSSCALE_NODE109_CPU_PLATFORM_PREFLIGHT_V1.md)。不得恢复旧已STOP任务。
- 作者公开代码只锁定[`SNU-ARC/GS-Scale@6471e958f7e318f4870234d8107e0aa91c2d6932`](https://github.com/SNU-ARC/GS-Scale/tree/6471e958f7e318f4870234d8107e0aa91c2d6932)及其中[README](https://github.com/SNU-ARC/GS-Scale/blob/6471e958f7e318f4870234d8107e0aa91c2d6932/README.md)、`install.sh`、`examples/simple_trainer.py`、`examples/simple_trainer_hybrid_optimized.py`、`cpu_adam/src/cpu_adam.cpp`；不同于作者论文的确切运行commit，不能伪称复刻原paper bytes。自然目标仅**Mill-19 Rubble**。其原始官方tar URL：`https://storage.cmusatyalab.org/mega-nerf-data/rubble-pixsfm.tgz`；前A21 HEAD报告9,773,995,561 bytes，原hash和官方合并COLMAP仍未冻结。
- 109上一轮只读硬件资格：Intel i7-13700（16物理核/24逻辑线程）、RTX4080 SM89/16GB、driver 580.178.04、当前CUDA SDK12.6、旧NequIP Python3.11+torch2.10+cu126/NumPy2.x。作者示例入口Python3.10、torch2.2+cu121、IPEX2.2、NumPy<2和C++ CPUAdam；仅**新的隔离env**可以安装作者版本，禁止覆盖老env、驱动、GPU SDK或清理共享缓存。

## 1. 时间和资源**硬上限**——要预算约束，不是强制把预算用满

| 对象 | 已批准的上限与实机执行方式 |
|---|---|
| 官方网络下载 | **累计实际下载字节≤25 GiB**：只能官方Rubble、作者发布的合并COLMAP和固定版本软件分发物/源码；限速/断线只允许受控Range续传与校验、记累计流量，不另找镜像或替换scene。所有HTTP头、下载URL不带密钥写public Git |
| 磁盘 | 本任务**全部新增≤60 GiB**（raw、展开、缩图、env、build、日志、checkpoint和临时cache累计）；任一阶段**同一底层文件系统至少保持64 GiB可用**。A24空间数据为过去快照，不是现在的预算资格；不能把同一文件系统下两个路径的空闲量相加 |
| 主机RAM | 本任务**RSS/数据加载器/pinned buffer合计≤48 GiB**；运行前核空闲内存及其它任务影响，任何越界风险及时终止自己的子进程；不能干扰其他实验 |
| CPU线程 | **同时有效≤24逻辑线程（整个任务进程树）**；作者CPUAdam源码的`omp_set_num_threads(64)`必须检查`OMP_THREAD_LIMIT`/cgroup/affinity**实际执行时**生效，不能仅设`OMP_NUM_THREADS`冒充封顶。数据加载器/其它worker与OpenMP总和也计入。若只能改作者科学核心算法才能限线程，STOP；允许仅隔离控制及记录为软件策略身份 |
| CPU准备时长 | G0/G1的数据、依赖、编译、预处理**累计wall≤4小时**，超过即安全归档已有结果并STOP；不要把下载失败变成无期限背景下载 |
| GPU | **仅109同一RTX4080**，所有CUDA初始化、Torch CUDA导入触发设备初始化、GPU kernel/拷贝/训练/监控均先非阻塞独占取得`/data/c16/locks/c16_gpu_campaign.lock`，忙则`RESOURCE_DEFERRED`立即退出；按每个GPU阶段累计真实**持锁≤2小时**，不跨锁继续GPU也不将CPU预处理算入GPU；release之后若继续GPU需重新非阻塞申请 |
| 显存 | **任务最大GPU占用≤14GiB**，记录`allocated`、`reserved`及设备实际抽样峰值/采样间隙；限额按实际可观测峰值与保守预测共同判断，不能仅用`allocated`隐瞒reserved/上下文 |
| 训练/测量 | 只一个自然Rubble；最多**三个已预注册真实训练阶段窗口**，不允许随机Gaussian、其它场景、SM quota扫参、NCU/NSYS/NVBit/Accel-Sim或新Cache/atomic机制。**不授权200,000步完整收敛或大规模多seed**。若现有时窗到不了后期，**EARLY_ONLY**，不可合成后期state或声称已观测 |
| 代码/输出 | 新工作目录和仓库worktree自有；全部instrumentation和包装修改opt-in、默认OFF，原作者强算法输出和原数据保持。小量Git受控report/probe源码与hash可公开，大场景raw和wheel不得commit Git或直接复制到164 |

**资源管理**：开始预检GPU锁/主机空闲、运行中周期核真实资源占用；任一限制接近则先安全停止自己任务并归档，不得清理别人的数据、杀别人的PID、执行`git reset --hard`覆盖未提交工作、设备reset、sudo安装或降低真实科学工作量来凑PASS。任何公共仓库/远端report应脱敏个人路径、账号、令牌、私有host等。

## 2. 单Goal连续执行：G0→G1→G2→G3→G4，普通工具问题就地solve-and-continue

每一阶段形成可机器复核的`GATES.json`，字段`PASS/PARTIAL/NOT_RUN/STOP`及真实失败命令、返回码、资源与输入身份。G门能够合法通过就**继续下一门**，不要把`尚未证明`硬编码为预设STOP。普通pip metadata、相容官方同版本wheel/sdist、tar索引、下载Range、C++链接、路径/manifest、报告生成的确定性问题，采用原版本/原hash/原语义的**诊断→有界修复→重试→原样验收**；所有修复保存diff/来源、时长/资源，不再开新Codex窗口或要求普通小问题审批。

### G0｜在任何下载、安装或GPU之前完成只读科学输入与预算检查

1. 核作者固定Git commit、现有仓库分支与干净新worktree、任务权限、`nvidia-smi`如会初始化GPU则**先锁**，否则仅查旧本机CPU/驱动文件元数据；资源（同文件系统disk ≥64 GiB尾部余量、RSS headroom、网络下载权限）。核软件版本精确依赖图（包括gsplat、IPEX、torch、torchvision、Python、NumPy、cuda source/binary ABI），先做**官方版本元数据可用性**检查，不盲`pip install -r`。
2. 核官方Rubble URL HEAD、real license/access、Content-Length和可续传，另核作者**合并COLMAP**的真实可访问来源/文件列表及生成处理方法。注意**缺事先发布的SHA256本身不是科学payload缺失**：允许原作者官方tar下载后计算冻结hash；但如果场景的**真正pixsfm/COLMAP图像/相机/点云科学payload**在可靠公开来源中缺失，且无法依据作者源输入确定性重建/对应，则在大下载前`INPUT_SCIENTIFIC_PAYLOAD_BLOCKED` STOP。不可暗换第三方同名场景、随机相机或其它轻量基准。
3. 预估raw+解包+4×缩图+合并COLMAP+新env+中间缓存+最多小checkpoint总增量，并留余量；若原tar展开规模未知，先用可靠小元数据/同源tar索引，不能确认不爆盘则`STORAGE_BOUND_UNKNOWN_STOP`，不直接边下载边无限解压。新checksum和扩展盘总预算先读全局真实资源，不能只看一个data目录。

### G1｜获准的有界真实资产下载+隔离环境一次性闭环（G0通过才做）

1. 只下载官方Rubble tar及必要作者正式COLMAP/公开依赖到任务新路径；HTTP Range续传需验证`Content-Range`与partial SHA，记录累计字节。完整`sha256sum`、文件头、tar成员路径/链接安全检查、解包总量上限、扩展占用；解析真实COLMAP`cameras/images/points3D`对应关系，按作者固定`4× downsample/test_every=83/filename sort`生成**实际可回放scene manifest**，记录每个输入/派生文件及必要相机列表SHA。作者不存在公开前置hash可使用本轮第一次合法下载的具体SHA作为**新输入身份**，不可反称论文作者用过同bytes。
2. 在隔离目录创建作者旧`Python3.10/torch2.2.0+cu121/torchvision0.17.0+cu121/IPEX2.2.0/gsplat`与`numpy<2.0`依赖，锁住发行URLs、版本、wheel/sdist hash与分发license。预核CUDA12.6 SDK与cu121扩展编译的真实ABI/compatibility；Torch CUDA extension/CPUAdam的compiler和OpenMP真实thread limit均须合格。冻结作者代码，所有有效的工程小修补放**独立补丁目录并opt-in**；不得直接升级Torch/IPEX/重写cpu_adam数学实现/用新gsplat路由代替无依据的旧强路径。
3. CPUAdam的硬编码64线程在109的24逻辑线程上有资源风险：先在最小有界、无GPU或有锁的合法CPUAdam测试中验证任务**总实际线程≤24**；若只能通过修改计算算法才能满足上限，`THREAD_RESOURCE_UNQUALIFIED_STOP`并保留证据。若包装可合法限制线程，其性能按**显式线程策略**报告，并对作者原源码策略不得声称同机强基线已充分调优。
4. 任何单个依赖缺失前先查全组wheel/source权限及依赖闭包；包装错误允许最多**2次定点源同版本修复/同原因有界重试**（合计不超过4h CPU预算），不是每叶包失败就开一轮。需要跨版本、改变模型/优化器/输出质量/原COLMAP身份就scientific STOP。G1成功须有`ASSET_MANIFEST.json`、`ENV_LOCK.json`、`BUILD_RECEIPT.json`、`THREAD_LIMIT_RECEIPT.json`，没有GPU模型资格暂不称runtime PASS。

### G2｜真实Rubble功能与数值/质量canary（G0/G1 PASS且拿到GPU锁）

1. **实际运行最少的真实train steps**：固定相机RNG和数据顺序、真实SfM/初始化和GPU-only、full optimized host软件；至少全强软件路径确实执行`frustum→gather→render→loss→backward→H2D/D2H→CPU Adam→状态发布`，记录loss finite、梯度/优化器更新、正确输出、Gaussian数及camera身份；不可只用部分kernel烟雾测试冒充完整应用。数值稳定条件和原论文质量指标需在执行前预登记，不临时松门。
2. **GPU-only只有能在相同真实Gaussian/相机/配置下fit才执行配对**；OOM仅报告`CAPACITY_NO_TIMING_BASELINE`，不可当无穷慢。optimized host的deferred Adam与GPU-only优化算法不严格bitwise相同、densification可能改变Gaussian ID与模型容量；分别标`APPLICATION_QUALITY_MATCHED_IF_EVIDENCED`和`BITWISE_EQUIVALENCE_NOT_CLAIMED`，不能把几个正常早期step当长期PSNR收敛证明。
3. 最短真实step可能处于初始化小Gaussian状态：合格称`REAL_EARLY_FUNCTIONAL_PASS`，**不**称具有后期大规模负载。若需修改强库/剪掉output/换其他数据或使用synthetic fake，则科学STOP，不硬跑。

### G3｜仅通过G2后、同一已批准GPU锁预算内的有界真实时间诊断

1. 预登记至多三种**真实连续训练状态**：warmup后的early窗口（例如真实step100–200）、有预算才到的真实densification前窗口（如14500–14600）、真实refine后窗口（如15100–15200）。**必须确实按真实训练路径从头连续走到该step**；作者现有保存`{step,splats.state_dict()}`不证明完整Adam moments/counter/RNG可恢复，不能把它当完整state checkpoint跳到晚期。根据前若干真实step的耗时预测是否到得了后期；达不到立即记`EARLY_ONLY / LATE_STAGE_NOT_EVALUATED`，不在2h预算内无意义追15k。
2. 未插桩`whole_step_wall`与诊断版`CUDA event/host monotonic`必须分开采样：记录camera ID、Gaussian数量、`frustum/cull`、valid ID D2H、pinned H2D、GPU render/backward、grad/info D2H、CPU Adam有效线程/随机内存service、`synchronize/join`实际暴露等待；不允许各分段时长**直接相加**当critical wall，需用时间窗口的union/overlap。observer opt-in、默认OFF，检查其数据量与额外时间开销，不覆盖作者输入输出。
3. 如需跨step活跃状态复用率，必须有Gaussian稳定identity或birth/death/densification映射；只有数组row-index时标`REUSE_IDENTITY_UNQUALIFIED`，不得把平均8.28%单步活跃率当时间cache hit。CPUAdam64线程的资源约束与实际隔离策略必须单独列为**软件混杂**，无CPU带宽单因子事实不得叫`MEMORY_BANDWIDTH_BOUND`。
4. 报告`complete wall`的**未隐藏**CPU/host或GPU等待是否在同语义强软件条件下可观察，并给负面/UNKNOWN判据：未隐藏部分接近测量离散度、软件线程策略可解释、无同scene input/一致的训练阶段、只有早期小Gaussians、相机/PSNR不同，则`SOFTWARE_ABSORBED_OR_UNIDENTIFIABLE`，不晋升新硬件。出现稳定显著候选也仅`SCOPED_EXPOSED_SERVICE_CANDIDATE`，**不因该候选自动跑物理resource×2/Cache机制**。
5. 不运行NCU、NSYS、NVBit、Accel-Sim、不改SM/L1/L2/寄存器/内存带宽和GPU驱动，不启动另一GPU/模型或论文正式大campaign。

### G4｜所有合法终态都要完整归档+发布并STOP

- 必需结构化小报告：`RUN_IDENTITY.json`、`GATES.json`、`ASSET_MANIFEST.json`（未下载写NOT_RUN）、`ENV_LOCK.json`（未安装写NOT_RUN）、`THREAD_LIMIT_RECEIPT.json`、`BUDGET_USAGE.json`（真实下载、磁盘、RAM、GPU锁累计、显存peak采样局限）、`FUNCTIONAL_QUALITY.json`、`OBSERVABILITY_SUMMARY.json`（未测写NOT_RUN）、`FINAL_DECISION.json`、`FINAL_REPORT.md`、小`SHA256SUMS`。raw大数据保存在任务隔离目录、不进Git；若原有164只读/小包归档权限已允许，可另目录归档**小元数据**并readback，**不复制巨型场景**。
- `FINAL_REPORT`记录哪些科研门通过和必须Stop的确切限制；至少区分`INPUT_SCIENTIFIC_PAYLOAD_BLOCKED`、`STORAGE_BUDGET_STOP`、`PLATFORM_PACKAGING_BLOCKED`、`GPU_LOCK_RESOURCE_DEFERRED`、`REAL_EARLY_FUNCTIONAL_PASS`、`LATE_STATE_NOT_EVALUATED`、`SCOPED_EXPOSED_SERVICE_CANDIDATE`、`SOFTWARE_ABSORBED_OR_UNIDENTIFIABLE`。科学结果可以是UNKNOWN/负面，不拼凑加速比。
- 只提交**本独立A26G branch**的脚本/小manifest/报告/哈希，执行者push后远端fetch-back核对**准确commit/tree/blob、所提交文件SHA及clean worktree**，保存真实工具/预算成功或错误收据后STOP。旧NequIP/V1R1/A16R1、A21–A24、AWMA/C16所有已接受历史不变，绝不自行merge到协调branch。

## 3. 一次性执行/失败恢复策略（强制）

- **只发一条Goal，不再人为拆“下载数据”“装依赖”“CPUAdam线程”“数值”“性能”五个Codex窗口。** 有效科学阶段PASS则立刻按本合同继续下一门；可并行的只读下载meta/依赖闭包预检先CPU并行，GPU阶段顺序受共享锁限制。普通确定性工程故障可在严格预算内有界解决，不因为`manifest/index/runner/package`包装缺失而把可确定性恢复的权威文件误判为真实科学payload缺失。
- **严禁为提高完成率硬编码提前STOP**（上一轮A16R1 G3只有静态查看、没实际测试就预写STOP，此处不能复制该错误）。若没有安全、合法、可执行的功能/质量/时间probe，必须在G0/G1直接明确`RUNTIME_PROOF_PLAN_UNQUALIFIED`；不可假装做了G2/G3，也不能通过弱合成负载换目标。
- 真科学payload缺失、官方data身份/授权不成立、CPU/GPU资源/预算越线、数学等价与质量要求改变、需要新模型/硬件机制时**FAIL-CLOSED**，归档已证成果、终止该科学分支；不要瞎猜或无限修软件。无须用户中途为工具小修确认，**用户审批只覆盖这一条有界科学/资源合同**。
- 任何阶段完成或STOP都**不自动开启下一Goal**。ChatGPT从固定Git提交独立审查后，才会决定是否继续论文/硬件研究。本执行不是后台自动任务：需要用户在原Lane M的Codex窗口发**一次**完整启动指令。

**最终业务状态：`A26G_ONE_GOAL_NATIVE_DISCOVERY_APPROVED_WITH_CAPS / EXECUTION_NOT_YET_LAUNCHED`。**
