# Round A7｜非LLM发现性观察完整合同与执行前审查

**设计与审查执行者：ChatGPT／AI-ARCH Discovery。日期：2026-10-13。**  
**拟议运行执行者：Codex Lane N／node109的独立新worktree；尚未启动。**  
**Goal标识：AI_ARCH_NEQUIP_STATIC_BATCH_DISCOVERY_109_V1**  
**状态：DESIGN_COMPLETE / GPU_EXECUTION_REQUIRES_EXPLICIT_APPROVAL / NOT_NATIVE_VALIDATED。**

> 本轮把模型来源、软件组合、对照、数值检查、计时、统计、预算、失败处理和交付一起完成，不再拆成后续ChatGPT设计轮次。本文件不是GPU授权或已实现/测试的runner。只有用户明确批准本合同的109执行及所列获取/编译预算后，Codex才可连续执行下述阶段。当前没有下载模型、初始化CUDA、运行Codex、训练或模拟器。

研究入口为协调分支已核提交 `5fd748c3f2da64924ed84978c07bca90e7e6ea92`；承接[Round A6](../literature/AI_ARCH_ROUND_A6_NEQUIP_PATH_AND_PUBLIC_TRAINING_2026-10-13_V1.md)。工具Skill仅采用审查方法，不安装、不合并bootstrap或Lane分支。

## 1. 科学问题和可回答范围

**问题：** 对同一组真实Si结构，以同一训练好模型和同一个compiled OpenEquivariance执行产物完成能量、力和应力时，CPU/GPU构图放置及批量大小B=2/4/8怎样影响整组完成时间？可观测的变化主要出现在输入准备/传输、构图还是模型区间？

这是P01工作量组织与瓶颈迁移的有限发现性观察，为P13后续资源研究提供筛选依据；**不是物理SM、寄存器或内存带宽扩容实验**。比较的是两个已有构图方式及固定成熟模型后端，不宣称已经涵盖所有最快后端。批量变化同时影响launch数量、总活跃工作集及算子形状，不能将全部速度差归因于SM供给。

允许得到软件组织正结果、零结果、CPU构图更快、模型运行占比上升或观测不足。无需事前证明完整硬件oracle或达到5%整应用收益；任何结果都不自动晋升硬件机制、MD长期收益或跨模型定律。

## 2. 固定模型与输入；哪些已经核对、哪些在运行门检查

### 2.1 模型

- 作者模型：`nequip.net:mir-group/NequIP-OAM-S:0.1`；[模型页](https://www.nequip.net/models/mir-group/NequIP-OAM-S%3A0.1)明确支持Si、OpenEquivariance modifier、cutoff 4.5 Å、两层、l_max=1、128/64特征、ZBL与parity=false，约0.6M参数。
- 锁定[Zenodo record 18775904](https://zenodo.org/records/18775904)中的 **`NequIP-OAM-S-0.1.nequip.zip`**，而非记录内其它模型或“newer version”。记录版本显示0.1a，文件/模型名称仍为0.1；保留这个区别，不自行改名。
- 官方列示大小约5.6MB；官方MD5 **`399a98bf36fc4550bc85d48f35451c6c`**。固定下载地址：`https://zenodo.org/records/18775904/files/NequIP-OAM-S-0.1.nequip.zip?download=1`。本轮仅查看网页元数据，未下载压缩包，因此**尚无本窗口独立SHA256、精确字节数或包内dtype鉴定**。
- 获批后只获取此文件，先验证官方MD5，再计算SHA256、size、zip成员清单和模型metadata。MD5是发布文件一致性检查，不替代SHA256身份记录。若来源/校验不符，STOP；不得改用注册入口的其它版本、随机权重、tutorial训练结果或Lennard-Jones。
- 预期模型FP32；必须从加载对象/metadata核验。cutoff、type_names、单位、modifier及输出取自实际模型包。不得用tutorial的5.0 cutoff覆盖4.5，不修改能量shift、模型层数或特征数。包中如携带源代码，记录其身份与加载路径；**安装的NequIP源码版本和包内模型源码是两个字段**，不要求把包内原模型替换成安装源码，但接口/输出必须满足本合同。
- 官方NequIP路径原生报错即停止相应资格，禁止MACE/LJ或其它模型fallback。

### 2.2 几何和固定选样

输入：[mir-group/nequip-tutorial@8f90935ba42fd9e03df323cf03428c456d87b881/sitraj.xyz](https://github.com/mir-group/nequip-tutorial/blob/8f90935ba42fd9e03df323cf03428c456d87b881/sitraj.xyz)。既有A5独立核验：784,661 bytes，Git blob `baac4e23364d00d29b2410fa60a92ade0cbf35a3`，SHA256 **`c08d3771a06beb82b0ed4258f78eecc7ce623f73ca6df20be99bd5722163e770`**，110帧、每帧64 Si。执行时只回读此小文件/已存在同hash副本，不下载MD22或其它数据。

零基帧索引：
- 编译与初始canary：`[0, 109]`。
- 正式固定32帧：`[1,5,8,12,15,18,22,25,29,32,36,39,42,46,49,53,56,60,63,67,70,73,77,80,84,87,91,94,97,101,104,108]`，由 `floor((2*i+1)*110/64), i=0..31`确定，不查看时间后选样。
- 正式集合固定顺序，按连续2/4/8个结构分组。每个条件都完成完全相同的32帧/2048原子；不是随机复制同一帧，也不是把多个周期盒合成一个相互作用晶体。
- 单独记录重复几何若存在，不静默替换。其它帧本轮不计时、不优化、不追溯命名为独立holdout；整个文件之前被解析过，不能宣称未见过数据。32帧也不被当作统计独立的MD轨迹样本。
- 没有连续时间身份，故不测跨帧skin复用率或MD重建频率。原标签只说明数据来源，不作OAM-S预测逐元素reference；训练DFT设置可能不同。

## 3. 拟议软件组合与可比性

这些是**选定的候选组合，源码接口核对不等于安装/运行资格通过**。禁止按性能挑版本或反复迁移后端。

| 项 | 拟固定值 | 依据和运行门 |
|---|---|---|
| Python | 3.11.x，实际patch和解释器路径入锁文件 | nvalchemi源要求>=3.11 |
| PyTorch | 2.10.0，官方cu126 wheel | 官方[历史版本页](https://pytorch.org/get-started/previous-versions/)给出该组合；设备driver/toolkit必须现场核验，不能沿用旧109环境推定合格 |
| NequIP | `27d9d2182da918ab7be0017d8300e53278f5e00e` | 本窗口核过batch编译、OEQ、alchemiops、dtype检查；只在新隔离环境安装 |
| OpenEquivariance | v0.7.0，commit `62aacc47557e9cdfc6dd370f410b684be1ee0a3f` | tag已核；TensorProductConv仍接受`torch_op/use_opaque`参数，use_opaque为deprecated；运行时验证modifier真正加载 |
| ALCHEMI Ops | `32445c5f00e83fccd475589f1a6f5ac9e81e6b02` | 固定pyproject要求Python>=3.11、Warp>=1.16、torch extra>=2.10；使用torch API，不装JAX |
| Warp | 1.16.0 | 满足上述源依赖；能否在本机driver执行须canary |
| e3nn | 0.6.0 | 固定NequIP依赖区间>=0.6,<0.7 |
| ASE / matscipy及叶依赖 | 在上述约束下进行一次依赖解析，生成完整版本及包hash锁；之后三个进程共用 | 叶依赖不按计时择优；依赖冲突/无可用wheel则环境门STOP，不另开版本扫描 |
| 精度 | FP32，TF32关闭，autocast关闭 | 不为获取positive使用更低精度；五次均值的官方数值检查见§5 |

优先复用109已有下载缓存/相同版本轮子，但不修改旧venv、全局Python、驱动、CUDA或编译缓存。非相同版本旧环境不自动替代该组合。若必须安装新系统驱动或新全局CUDA工具链，返回`ENVIRONMENT_BLOCKED`，而不是进入重型环境工程。

### 3.1 一个compiled模型产物，而非四个实现

- 使用官方 `nequip-compile`、AOTInductor、`--target batch --device cuda --modifiers enable_OpenEquivariance --no-tf32`。同一个`.nequip.pt2`产物SHA适用于四条件；不把ASE单帧产物混入B曲线。
- 源码允许动态界限：`--num-frames 2,8 --num-nodes 128,512 --num-edges 2,65536`。这些上限是本研究设计值。导出示例只用canary的已正确构图数据。
- **`--data-path`接收的是可被`torch.jit.load(...).state_dict()`读取的张量容器，不是XYZ文件。** 按固定compile.py接口从canary数据生成该小容器。`batch`目标可能复制示例构造双帧/批量形状；记录变换后的shape，不能用这个复制过程代替正式的不同结构集合。
- 官方编译内部正确性检查保留。对模型加速modifier的验证也保留，不跳过校验或放宽容差。
- 预热覆盖所有正式B和边数；同产物仍可能有内部形状选择。记录已生成/加载kernel及编译日志，不能据产物SHA相同断言GPU内部指令路径处处相同。
- 运行期出现新的compile、fallback、换产物或额外autotuning，则停受影响的正式比较并保留数据；不把该慢样本删掉后继续筛。第一次普通缓存/包装修复允许在正式阶段前完成，最多两次，固定最终runner/产物身份后才计时。
- 保持`model.eval()`；力/应力要用autograd，禁止用`torch.inference_mode()`或覆盖整个计算的`no_grad()`使导数消失。评估不是训练，不运行optimizer或double backward。

## 4. 四条件及合法测量边界

| 条件 | 构图 | B | 完整32帧调用批次数 | 实验含义 |
|---|---|---:|---:|---|
| N-C2 | CPU matscipy | 2 | 16 | 成熟CPU构图参考 |
| N-G2 | GPU alchemiops | 2 | 16 | 构图放置与传输整体差异，不称纯kernel单变量 |
| N-G4 | 同GPU后端 | 4 | 8 | 提交粒度变化 |
| N-G8 | 同GPU后端 | 8 | 4 | 更大同批工作量 |

全部采用普通邻居transform＋atomic OEQ路径，不强制Sobek CSR/双向排序，不把另一个deterministic算法混作同后端。GPU `max_neighbors=128`为事前固定容量；CPU参考逐原子邻居计数若超128或GPU有溢出，则STOP，不静默截断/加容量后挑点。

### 4.1 主指标：未插桩的整组wall

输入文件读取/解析、模型下载/加载、导出/编译和预热不计入稳态主指标，另报一次性成本。计时入口是同一批已驻留CPU内存的只读原子/位置/盒子记录；以下都在计时内：

`构造本批AtomicDataDict与类型映射 → 必要CPU/GPU搬运 → 当次构图 → 同一compiled模型的能量/力/应力 → 结果回传CPU并可用`。

每次全组前后同步设备，用`perf_counter_ns`得到完整wall；每批按相同策略完成CPU结果物化，输出按原帧号还原。每结构时间=`全组wall/32`，throughput=`32/全组秒数`。不从多个kernel duration求和反推wall。

CPU结构预处理与结果缓存必须一致：不调用可能直接命中上一结果的ASE查询缓存；每批新建必要输入字典，保持positions/grad生命周期正确，模型每批必须真实调用。不能提前缓存正式邻居表、复制上次输出、只计enqueue时间或在某臂省掉应力/CPU回传。所有重复为热模型、按原生allocator/缓存正常运行；不清L2、不伪称冷缓存。

### 4.2 辅助诊断：单独运行，不污染主计时

正式计时后才做每条件总计3个全组辅助sweep，记录CPU准备区间、构图、模型、传输边界及GPU-event时间、peak allocated/reserved memory。不得装Python模块hook来重新做C16 observer，不运行NSYS/NCU/NVBit；该任务不需要完整kernel语义归因。

Torch与Warp可能使用异步流，必须依公开依赖保证模型真的等待邻居输出，events需覆盖正确流；无法把辅助区间对到合法device时序则标`DIAGNOSTIC_UNRESOLVED`，保留完整wall，不用剩余时间猜测CPU或DRAM瓶颈。辅助区间时长不自动是关键路径权重；计数器/TFLOPs/occupancy缺失不是启动新profile的理由。

## 5. 数值、离散身份与资格门

以下是**冻结的研究验收规则**，不是已经通过的结果。

### 5.1 输入和边集合

逐帧核Si、64原子、有限坐标、可逆且正体积cell、PBC、类型映射、cutoff和统一单位。CPU/GPU构图使用一致FP32坐标和同模型cutoff；每批帧间无边、没有buffer溢出或padding边进入模型。

对CPU/GPU和单帧/批量结果，以`(frame_id, center_atom, neighbor_atom, shift_x,shift_y,shift_z)`规范化**有向边多重集合**进行整数精确比较。规范化只在正确性审查，不加入/删除原生计时路径的排序。周期image相异不能去重为一条边；零shift自身边与非零周期image自身边必须区分。模型用的edge方向、周期shift和半/全邻居表按NequIP消费者语义解释，不只凭source/target名字猜。

边界距离或浮点cutoff产生不同集合时记录第一个差异并STOP，不能删除困难帧、扩大cutoff、调结构或将不同图当作近似同义。

### 5.2 同一模型reference和FP32判据

- Reference R：同一模型包、原模型未启用OEQ的eager路径＋CPU matscipy构图，逐帧得到完整输出；它只作正确性，不是被故意选弱的性能baseline。另核同包eager-OEQ与compiled-OEQ的输出一致性。
- 输出固定：per-atom energy、每结构total energy、每原子force、每结构stress；统一原生单位后比较。不要拿数据集DFT标签要求模型逐元素一致，也不修改能量shift来“通过”。单位/输出字段身份无法确定则STOP。
- 按固定NequIP `nequip/utils/dtype.py`：每臂各评估5次，输出转double后取均值，逐元素`allclose(atol=5e-5, rtol=5e-5)`。保留单次输出、均值、最大绝对差及失败元素；这一门槛是库的FP32实现相似性检查，不代表化学精度或收敛承诺。不得更改NEQUIP容差环境变量。
- 先在canary两帧做reference-vs-reference重复性与原模型→OEQ→compiled检查，再对固定32帧作单帧/各批量、CPU/GPU构图的相同检查。重复性不合格时记`REFERENCE_REPEATABILITY_UNQUALIFIED`，不归咎候选算法，也不套用AWMA历史结论。
- 每个正式进程计时前完成四条件在32帧上的资格，计时后作一轮一致性检查。正式输出不能含NaN/Inf；任何输出/身份失败使对应性能不具科学排名资格，保留失败输入和结果再STOP。

## 6. 重复、顺序与统计

主计时：**3个fresh process，每个12个完整block，每block各跑四条件一次；共144个全组计时样本，每条件36个**。编译产物只建立一次并复用，进程启动时分别加载/预热。每条件固定2个完整32帧预热，不混入样本。

条件顺序采用4阶Latin轮转，12个block循环3次：`C2 G2 G4 G8`、`G2 G4 G8 C2`、`G4 G8 C2 G2`、`G8 C2 G2 G4`；后续进程轮转起点。只在两条件都完整有效的同block计算配对效果。

主比较为`C2/G2`、`G2/G4`、`G2/G8`。同时给每进程中位数、MAD、全样本原值及配对速度比`Tbase/Tcand`、时间减少`1-Tcand/Tbase`，不能混用百分比。可用固定seed=20261013、10000次按进程分层/按block重采样的bootstrap作运行波动描述；三个进程与32结构不足以支持总体泛化显著性。

不筛掉慢样本；外部GPU占用、热节流或编译污染被证实时标记整个受影响block/进程，停止正式执行而非无限补样。方向一致且误差范围能分离时只报告本工作量的稳定响应；否则`NO_RESOLVABLE_TIMING_RESPONSE`。没有5%晋升硬门，也不因一次快了5%就申请硬件。

## 7. 连续执行顺序：获批后一次Goal完成

1. **授权和资源预检**：核用户对本标识的执行授权；确认node109、可见GPU UUID/SM89/显存、驱动和工具链、磁盘及其它任务。未授权则只读文件后STOP。仓库沿现有配置读取，不reset原worktree。
2. **隔离准备**：在新worktree/branch `hrl/aiarch-nequip-static-batch-109-v1`（拟议，当前未创建）编写薄runner；从本合同经批准的固定发布commit出发，不从后来任意HEAD出发。环境、TORCH_EXTENSIONS_DIR、TORCHINDUCTOR_CACHE_DIR、Warp缓存与输出全放109独立数据目录，禁止清全局cache或触碰旧Stage A。
3. **输入/环境锁定**：只获取§2文件和§3必要依赖，生成来源/版本/hash锁、固定选样JSON、实验时序和runner commit；不得读模型包内未知远端路径自动下载训练集。
4. **独占与资格**：使用现有共享锁 `/data/c16/locks/c16_gpu_campaign.lock`，非阻塞取得；不得删锁/换路径绕过。锁覆盖可能触发CUDA的导入、OEQ/Warp JIT、设备编译、canary与正式测试。发现其它使用者则DEFER，不终止它们。
5. **官方导出＋canary**：核模型实际路径和modifier；动态batch产物；执行§5。普通runner索引/文件包装/版本元数据读取问题最多两次有界修复并继续；变更模型、容差、语义、核心版本或依赖边界则STOP，不变成新研究。
6. **冻结再正式执行**：先保存不可变的实验manifest、源/产物身份及全部门结果，然后按§6完成计时，再做辅助诊断和计时后正确性。
7. **自检与发布**：无论positive/negative/STOP均输出§9结果；结束本任务GPU进程、释放自己持有的锁；完整结果与必要raw按既有164 authority规则落盘回读。仅push自己的新分支，不合并到协调分支，不自动启动后续Goal。

任何阶段失败都应先保存最小可诊断记录再退出。停止不等于科学负面；可由已接受材料确定性重建的包装文件缺失允许顺手修，不恢复不存在的scientific payload。

## 8. 明确资源预算（这是拟申请的硬上限，不是用时预测）

| 资源 | 上限/权限 |
|---|---|
| 执行GPU | 109上一张RTX4080；单工作窗口串行，现有锁独占 |
| 模型＋几何 | 仅固定OAM-S包与Si文件；合计下载上限12MiB；不得扩成模型集合 |
| 新环境依赖获取 | 至多一次解析/安装路线，下载累计8GiB；优先已有同hash缓存；超出即STOP/DEFER |
| 109环境＋编译缓存＋产物磁盘 | 本任务增量上限25GiB；开始前至少35GiB可用，运行中保持8GiB余量；不在174已紧张根盘搭环境 |
| CPU/RAM | 建立/编译最多8个CPU worker、32GiB RAM，不新开多个agent或并发build |
| GPU显存 | 本任务峰值上限12GiB；超预算或OOM即停止，不换小模型或削减输出 |
| 执行时间 | 取得GPU锁起最多90分钟，包含可能触发CUDA的构建/资格；纯观测阶段最多15分钟，超过即记录未完成；不得排队持锁等无限下载 |
| 原始结果 | 除包/环境外的raw与日志不超过256MiB；优先结构/小张量/JSON/TSV，Git只入小review pack |
| 174/164 | 不启动174模拟或CPU Goal；获批执行时仅按既有164存储安排保存本任务小包/结果并核receipt，不移动或修改旧资产 |
| 禁止 | NSYS/NCU/NVBit、MD轨迹、训练、硬件机制、模型fine-tune、驱动升级、旧cache修复、其它GPU并发 |

## 9. 结果交付与分类

拟产物目录：`docs/ai_workload_research/review_packs/AI_ARCH_NEQUIP_STATIC_BATCH_DISCOVERY_109_V1/`。

必要小文件：`FINAL_REPORT.md`、`FINAL_DECISION.json`、`RUN_IDENTITY.json`、`INPUT_MANIFEST.json`、`ENVIRONMENT_LOCK.json`、`NUMERIC_AND_EDGE_CHECKS.json`、`TIMING_SAMPLES.tsv`、`PAIRED_SUMMARY.tsv`、`DIAGNOSTIC_STAGES.tsv`、`RAW_INDEX.tsv`和`SHA256SUMS`。可以合并重复机械receipt，避免为了文件数增加工作。metadata含全部原始/派生时间单位、统计单元、source commit、实际执行者与未完成项。

分类两轴独立：
- **运行资格**：`PASS / RESOURCE_DEFERRED / ENVIRONMENT_BLOCKED / MODEL_IDENTITY_FAIL / NUMERIC_UNQUALIFIED / TIMING_CONTAMINATED / BUDGET_STOP`。
- **科学观察（资格PASS后）**：`SCOPED_PLACEMENT_RESPONSE / SCOPED_BATCH_RESPONSE / MIXED_RESPONSE / NO_RESOLVABLE_RESPONSE / ATTRIBUTION_UNRESOLVED`。

不给`HARDWARE_MECHANISM_QUALIFIED`标签。发现CPU构图更快不算失败；只有软件调用摊销收益就按软件解释；模型区间变化也不直接命名为带宽/SM瓶颈。失败臂不入性能排名，合法子结果可保留并明确缺哪一比较，不用坏臂凑完整矩阵。

Markdown写入须显式UTF-8，检查标题/中文正文可读、无替换字符和成片问号，再fetch-back核byte hash；这吸取Lane N文本损坏教训，不再做长篇Skill烟测。

## 10. 执行前自审：主要混杂因素已如何处理

| 风险 | 合同处理 | 仍待实际验证 |
|---|---|---|
| 注册名漂移或模型fallback | 固定record/file/官方MD5，执行前SHA256和metadata；禁止换模型 | 真实包dtype、packaged code与runtime接口 |
| 为Sobek适配而改变科学对象 | 不用Sobek，采用OAM-S已公布的OEQ modifier | modifier实际加载和数值 |
| 没有连续MD帧 | 只研究静态结构固定工作量，不声称跨帧复用/重建率 | 无需先建立MD系统 |
| 单帧/批量编译切换 | 同一个batch AOT产物覆盖B2–8，固定shape边界 | 导出成功、无计时期重编译；内部kernel变更如实记录 |
| CPU/GPU邻居表不等价 | 有向周期边多重集合精确检查＋所有输出检查 | cutoff边界、overflow与stream依赖 |
| 去掉力/应力造成假加速 | 固定四类输出，eval仍允许导数，不用全局inference_mode | 加速模型所有输出有限/数值合格 |
| 数据集DFT与模型不相符 | 同包reference，标签不是逐元素金标准 | 本实验不声称化学准确度 |
| 把CUDA排队或ASE缓存当完成 | 完整CPU输入至CPU结果wall，验证每批模型实际调用 | 本机异步依赖和wall完整性 |
| 利用率/局部event替代收益 | 未插桩wall主指标，诊断另列、不相加推因果 | 可能只能解释为软件效应或UNKNOWN |
| 同一小数据集大量重复伪装统计样本 | 固定32帧、3进程、配对block；不宣称跨结构泛化 | 后续独立应用验证另议，不自动开启 |

本轮的审查依据为原始源码、作者网页和已有独立证据；**没有**运行模型/编译器/runner验证，也没有用缺失数据填满表格。运行时门不是新一轮ChatGPT设计任务，而是获批后该连续Goal的一部分；过门则继续、遇到预定STOP则交付。

## 11. 原始来源和现有边界

- [OAM-S作者模型页](https://www.nequip.net/models/mir-group/NequIP-OAM-S%3A0.1)、[固定模型发布记录](https://zenodo.org/records/18775904)：参数/文件/MD5本轮直接核实；包本身未下载。
- [NequIP compile.py@27d9d218](https://github.com/mir-group/nequip/blob/27d9d2182da918ab7be0017d8300e53278f5e00e/nequip/scripts/compile.py)：动态shape参数、data-path加载格式、modifier、TF32和编译校验。
- [NequIP dtype.py@同commit](https://github.com/mir-group/nequip/blob/27d9d2182da918ab7be0017d8300e53278f5e00e/nequip/utils/dtype.py)：FP32 5e-5、5次均值与allclose；blob `2e99a30da7f80c1bc22e1903fd0f74301cccd1d1`。
- [NequIP pyproject.toml](https://github.com/mir-group/nequip/blob/27d9d2182da918ab7be0017d8300e53278f5e00e/pyproject.toml)、[版本名查询](https://github.com/mir-group/nequip/blob/27d9d2182da918ab7be0017d8300e53278f5e00e/nequip/utils/versions/version_utils.py)：依赖及module-to-distribution映射；不将分发名nvalchemi-toolkit-ops与import名nvalchemiops混为“包缺失”。
- [OpenEquivariance v0.7.0固定commit](https://github.com/PASSIONLab/OpenEquivariance/tree/62aacc47557e9cdfc6dd370f410b684be1ee0a3f)，其中TensorProductConv明确atomic/deterministic区别及签名；[NequIP官方OEQ说明](https://nequip.readthedocs.io/en/latest/guide/accelerations/openequivariance.html)明确AOT路径和导入先后。
- [ALCHEMI固定pyproject](https://github.com/NVIDIA/nvalchemi-toolkit-ops/blob/32445c5f00e83fccd475589f1a6f5ac9e81e6b02/pyproject.toml)：Python、Warp与Torch依赖。
- A6其余已核的ASE/mixins/_nl/neighborlist/grad_output/_compile_utils固定源码沿用；不重复Hash旧大数据或全论文。

C16 Stage A与AWMA R27R3等旧实验保持原已接受终态；训练TorchTitan研究保留，不与本观察混并。Lane T维持原STOP；Lane N原174文档V2修复独立处理，不构成本合同执行前置条件。

## 12. 下一阶段只有实际执行／结果审查边界

**Round A8｜109静态结构有限观察（拟执行者：Codex Lane N／109；ChatGPT审查）。** 用户若明确批准本合同的GPU、模型获取、隔离环境与设备编译预算，即按§7一次Goal完成，不再为canary、计时、数据自检逐个开轮。当前没有创建执行分支或发送启动指令。

后续ChatGPT负责根据固定Git输出作独立科学审查；不会声称聊天结束后自动监控/继续执行。若用户调整模型、资源或数值合同，再对确有变更的部分处理，不重做全部方案。