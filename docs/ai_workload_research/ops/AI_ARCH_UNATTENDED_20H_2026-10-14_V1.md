# AI-ARCH｜20小时无人值守连续推进计划 V1（2026-10-14）

**总协调：ChatGPT／AI-ARCH Discovery。执行者：174-new的既有Lane T和Lane N、109的既有Lane M。**  
**用户指令：接下来20小时无人值守，要求提前将可并行研究任务、正常工程问题的自主修复、保存与STOP安排完整。**  
**科学许可：`MULTI_LANE_CPU_SOURCE_ONLY_20H`；`ZERO_NEW_GPU_OR_SIMULATOR`。** 本许可不是无限期继续执行授权，不能从“无人值守20小时”推导出GPU探针、安装环境、下载大型数据、机制开发、AWMA/C16解冻或其它节点操作许可。

## 0. 时间、任务与“无人值守”的真实含义

- “20小时”是**用户无需再次交互的可用窗口**，不是要求Codex用满20小时、不断生成新实验或维持后台运行的理由。目标完成即STOP；若科学无足够输入/强基线则给可验证的`BLOCKED/PARKED`报告，**不为凑时长补弱样本**。
- ChatGPT此刻**可以**准备/更新GitHub源码与合同，**不能从这个对话主动打开已有Codex GUI窗口或SSH连节点执行任务**；以下任务要由用户在离开前**各发送一次**到指定已有Codex窗口。Git分支被创建**不代表远端Codex已经开始运行**。
- AI-ARCH源和产物跨节点保留独立分支/精确commit+tree+blob；没有异步跨Lane依赖、没有自动merge或GPU续跑。尽量用目标作者固定source/小文件，无大repo全量clone/联网依赖安装。
- 20小时终点将触发一次已安排的自动审查提醒/回收（若计划被取消则按Git权威收口）。提醒只是GitHub状态和科研资格**独立复审**，不会SSH操控Codex或执行任何GPU任务。

## 1. 三线并行分工：一人一份可复制指令，互不等待

| 执行者 | 唯一研究任务与科学目标 | 独立分支、交付 | 资源/截止 |
|---|---|---|---|
| **Lane T／174-new** | **A21**：核GS-Scale真实Mill-19场景、CPU-only源码/输入/质量/强基线资格（使用已准备合同）；A21 commit并STOP该子阶段；**A22**：仅依固定代码设计一条`per-step`活跃Gaussian→host state/optimizer→GPU准备→forward/backward→梯度/更新的来源/同步事件表，重点区分真正CPU等待与可重叠边界。若A21输入阻塞，A22仍可做**source-only**，但不伪造样本 | A21已有`hrl/aiarch-a21-gsscale-real-scene-source-174-v1`，交付其既有审查文档；A22全新branch+独立报告，绝不覆写A21 | CPU-only，最多4 workers，RAM≤8GiB，本任务新增≤200MiB，**A21≤3h；A22≤4h；总7h后强制收口** |
| **Lane N／174-new** | **A23**：独立核查3DGS硬件最近邻GSArch、GS-Cache与GS-Scale：原文明确哪些是真实GPU、哪些是架构模拟、自然/合成输入及强软件基线；再从代码/论文辨认3DGS动态工作集对L1/L2、host transfer、update、原子冲突的真正剩余证据。只做**竞争假设和反证**，不重复Lane T的场景下载/源码流程 | `hrl/aiarch-a23-gsarch-hardware-nearest-174-v1`、单份有界novelty审查和GO/NO-GO卡 | CPU/source-only，最多2 workers、RAM≤4GiB、文件新增≤100MiB、6h内STOP |
| **Lane M／109** | **A24**：极轻量本机**CPU-only**的GS-Scale实际可安装性门：CPU厂商/ISA、内存/磁盘余量、驱动/toolkit的**只读文件/metadata**、已安装torch/IPEX等版本包信息（不能import torch调用CUDA）；Intel-only和环境隔离必要条件，写清`PLATFORM_CONDITIONAL/BLOCKED`。不拉镜像不做安装，不运行历史NequIP模型 | `hrl/aiarch-a24-gsscale-109-cpu-platform-gate-v1`、小平台事实与预估资源差距报告 | **GPU锁占用0、CUDA初始化0、Torch import 0**；CPU≤1 worker、RAM≤1GiB、新文件≤30MiB、1小时内STOP |

三线分别读本计划的固定协调提交/合同；一个节点的工作不能覆盖另一个的Git文件、缓存和已完成STOP。174以前有root/swap压力：在启动Lane N前先只读检查容量，资源低则写`RESOURCE_DEFERRED`，不为了并行挤爆已有Lane T。

## 2. 每条Lane自行运行的通用状态机

`PREFLIGHT` → `SOURCE_IDENTITY` → `SCIENCE_EVIDENCE` → `REPORT_AND_SHA` → `PUSH_AND_FETCH_BACK` → `STOP`。

- **进入时**：read-only检查`git status`、固定分支HEAD、作者source commit、机器资源；新独立worktree。发现未知未提交改动不用reset/clean，不可改老STOP成果。只有`git worktree add`等单独工作目录操作受限允许。
- **小工程问题solve-and-continue**：在以上预算内，修正URL路径、ref、元数据索引、文件名、git身份、report UTF-8、manifest/SHA打包错误；单个工程小修不需每次问用户。使用最多两条**确定性**包装替代途径（例如原官方Git raw、已固定GitHub file API），不可为了跑通任意切换研究问题或软件基线。
- **输入不完整不妨碍source工作**：自然场景下载文件未锁SHA、不可公开获取、无训练历史或目标CPU ISA未知，分别标`INPUT_IDENTITY_PENDING`/`PLATFORM_UNQUALIFIED`，继续完成**静态可审部分**；不进行实际数值/性能推断。
- **科学STOP边界**：模型/训练数据/optimizer ε算法等语义差异、申请GPU/新模拟资源、新模型或数据大下载、跨节点/超预算、身份无法辨识的强实验、实验需改变历史C16/AWMA authority——都须STOP并留下缺口。任何研究终态可以是合法负面结论，不造“可行”作为结果。
- **报告规则**：所有定量结果必须带分母、单位、输入、源、平台；`PAPER_AUTHOR_NATIVE`、`PAPER_AUTHOR_SIM`、`CODE_ONLY`、`OUR_INFERENCE`和`NOT_VERIFIED`严格区别。不构造虚假的node109本机GPU时间。每个输出须有exact commit/tree、文件blob、远端fetch-back，说明目标branch`ahead/behind`及旧分支不变；不merge协调分支。
- **任务结束**：当前Goal STOP且**禁止由无人值守“兜底”自动开启新GPU/再开Codex/无限论文扫查**。Lane T仅获本计划明确命名的A22 CPU跟进阶段，无其它连锁阶段。

## 3. 科学判断的判据与收口答案（即使全线否定也算成功）

**Q20H-01：3DGS真实活跃状态时间寿命与系统代价在强GS-Scale之后可否辨识？**

可见的最低因果链：
`同真实场景camera序列与初始化`
→`真实Gaussian ID集合/生灭及密度变化`
→`每步GPU/CPU state更新/传输/sync`
→`强软件完整训练wall+RAM/HBM+time-to-PSNR`
→`剩余未覆盖服务占比`
→`可区分软件重排与真正硬件容量/带宽的干预`。

必要反例：GS-Scale已经优化了host offload+CPU Adam，GSArch已经做Gaussian冷热存储/atomic近邻，gsplat GPU-only对小场景可能更强，训练质量因为deferred Adam忽略ε不能假定bitwise相同；作者能跑的GPU/CPU与node109不是同一台设备。没有强基线与剩余wall就明确`NO_HARDWARE_HEADROOM_ADMITTED`。

要回答、而不是自动跑的三个决策：
1. 公共源及Mill-19 Building/Rubble身份是否足以未来冻结一个真实训练场景？
2. GS-Scale是否**真的**可在目标109 CPU和隔离环境完整执行（source能力≠已安装）？
3. 已发表GSArch/GS-Scale之后，是否有能被完备指标区分、值得未来独立申请原生实验的剩余机制/瓶颈？如果只证明软件能力，收口并更换方向。

## 4. 不要做的事情

- 109 GPU内核、cuda-gdb、NCU、NSYS、NVBit、GreenCtx和任何更改GPU锁的操作；
- 174 Accel-Sim / C16 Stage A / AWMA R27R3、编译仿真程序或重启旧Goal；
- 下载Mill-19图像、Hugging Face模型、巨型gsplat scene/weights，pip/conda/docker环境安装或全局cache清理；
- 构造随机Gaussian当自然真实训练，虚构camera轨迹、时序reuse或所需CPU厂商；
- 因GS-Scale已发表就仓促提出“新高斯cache”；因用户离开而自动开启更重的科学实验。

## 5. 结束和异常情况回报

每条Lane正常完成或提前科学BLOCKED都独立push；**报告外显一个`UNATTENDED_20H_CLOSEOUT`段**，至少包括：branch/commit/tree、起止、身份、研究PASS/NO-GO、科学边界、资源用量、是否有未合格但可在未来补的最小合同、新命名任务是否结束、SHA回读。

当用户回来时，先交叉复核这三份提交；只有ChatGPT独立审查并更新协调`CURRENT_STATE.md`后，才能讨论下轮实验。若某Lane没有真实执行commit，就标`NOT_LAUNCHED`，不因有precreated branch/Goal就冒称做完。

**用户无需在20小时内逐步审批普通工具修复；严格科研/设备预算依旧被锁住。**
