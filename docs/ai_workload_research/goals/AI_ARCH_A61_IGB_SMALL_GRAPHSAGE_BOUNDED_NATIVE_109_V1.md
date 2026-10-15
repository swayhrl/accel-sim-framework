# A61｜IGB-small真实GraphSAGE强软件供数：有界连续原生Discovery

**执行状态：PREPARED_AWAITING_EXPLICIT_SCIENTIFIC_INPUT_CHANGE_APPROVAL / DO_NOT_LAUNCH_YET。** 本Goal已全部写好，用于取代A59在官方`ogbn-products`许可适用性未解决时尚未获得的训练观察，但**IGB-small是新的科学数据实体，既不是OGB的工程镜像，也不是原A59的继续执行**。前述“Codex可自行处理普通工程问题/后续默认确认”不自动授权变更冻结图结构、标签、特征和train split。需要用户把**明确包含“批准A61从ogbn-products切换IGB-small及本文件预算”的指令**交给109 Codex才激活。文件准备、发布不等于批准、执行或占用GPU。

Repo：`swayhrl/accel-sim-framework`  
Task branch：`hrl/aiarch-a61-igb-small-gnn-native-109-v1`  
独立协调parent：`cdd6cc293a9af8c898ce10e7eeaf85bc96fa9e50`；真正启动只能以**含本Goal的远端完整提交SHA**为固定起点。新独立109 worktree/venv/data/output/cache，不能改/merge A59、A50G、C16/AWMA的历史文件、环境与科学authority。

## 0. 唯一问题与为什么换数据

**Q-A61：** 在**IGB-small homogeneous/真实1024维embedding**且官方发布、合法数据范围和原生GraphSAGE语义不变的前提下，已经真正开启`GPU graph cache＋GPU feature cache/fallback＋异步/pinned供数`的强GraphBolt软件，是否仍有露在**sampling→feature-ready→forward/backward/Adam optimizer update完整自然train step wall**中的供数代价？若强缓存/overlap已经足够，必须接受负结果`NO_EXPOSED_SUPPLY_BOTTLENECK`，不得因此做新硬件Cache机制。

这不同于OGB：节点`1,000,000`，边作者表`12,070,502`（实际方向/数组形状需运行核），feature`1024 FP32`，labels选**19类**，author repo`synthetic=0`读取真实预计算NLP embedding，不准自动用随机特征替代。模型固定3层mean GraphSAGE、hidden256、fanout`10,10,10`、B1024、FP32/cross-entropy/Adam，完整训练样本来自其官方实际mask；不使用`ogbn-products`的旧销售排名split，也不能把新结果叫A59某一时间点的同数据反事实比较。

证据必读：
- [A60独立review](https://github.com/swayhrl/accel-sim-framework/blob/cdd6cc293a9af8c898ce10e7eeaf85bc96fa9e50/docs/ai_workload_research/reviews/AI_ARCH_A60_A59_LICENSE_AUTHORITY_AND_IGB_ALTERNATIVE_REVIEW_2026-10-15_V1.md)，A59原`DATA_LICENSE_NO_GO`和许可后续`AUTHORITY_PARTIAL`历史STOP保持。
- [作者官方IGB源码固定提交](https://github.com/IllinoisGraphBenchmark/IGB-Datasets/tree/fc36357f2c1d861870b4c13a58f73da2b93d1e73)：`ODC-By-1.0` blob`dab29a14b77b9cd9b523e4aeaaf6fdb2aaa3624b`，`LICENSE` blob`931d368d8f65923bb22d8d059da3d45ab3afac1c`，`igb/download.py` blob`478bf8d1f24ebefa4aed43cca44ced7dd4e39210`，`igb/dataloader.py` blob`b4b6e342df4511ef99a488336b57502fff754fe4`。ODC数据许可与MIT**仅代码**许可证必须各自准确适用；ODC条款明确不自动覆盖数据库内容的其它独立权利，未经核对不能声称全面法律无争议。
- [官方DGL GraphBolt＋PyG高级缓存示例固定版本](https://github.com/dmlc/dgl/blob/3d16000b4170fa741ed9e9667f22ba84d3493026/examples/graphbolt/pyg/node_classification_advanced.py)支持`gpu_cached_feature`、`num_gpu_cached_edges`、pinned overlap、async及完整GraphSAGE+Adam，但它默认用`BuiltinDataset(ogbn-products)`，**本任务必须完成IGB原作者资产→GraphBolt合法数据结构的确定性转换并验证结果**；不是运行旧OGB cache例程就算PASS。
- A59原109缓存Torch/DGL wheel及source只读可复用元数据，不强迫必须采用其具体版本，必须选能合法满足实际RTX4080 SM89/PyG/DGL API/数值的**官方发行闭包**；不直接从master编译整套DGL，不允许driver/sys升级。

## 1. 资源硬预算：需用户明确批准新输入后的唯一累计账

| 类别 | A61整个Goal的硬限 |
|---|---|
| GPU | node109 RTX4080唯一一张，既有`/data/c16/locks/c16_gpu_campaign.lock`，父supervisor先`flock LOCK_EX|LOCK_NB`非阻塞并持有至自己所有子进程结束，GPU时间累计≤1800秒（30min），含小数值、JIT、正式训练、诊断及清理；忙则立即STOP，不轮询/kill他人任务 |
| 下载 | **总新增≤6GiB**，其中唯一官方IGB homogeneous small tar.gz实体≤4.5GiB、隔离官方wheel/依赖≤1.5GiB；原用户/系统缓存仅只读且hash/版本身份合格后才复用，所有失败retry传输仍计入 |
| 新盘 | 新worktree、venv、压缩归档、解包数据、GraphBolt graph/index cache、临时/日志累计≤14GiB，源FS可用容量持续≥64GiB；禁止清理旧资产。特别关注官方small真实1024-dim FP32 feature约`4,096,000,000B`，一个完整数据副本已经接近4GiB |
| RAM/CPU | 任务进程树RSS≤20GiB，CPU有效workers≤4，锁外CPU准备≤3h；不得因构建CSC/处理.npy无限分配或使用swap挽救超限 |
| GPU显存 | 当前任务≤12GiB；cache容量只按**实际**余量预选一次，不能为了出现更大差距后视改容量。NVML监测可能漏瞬时峰，需要模型与样本上界共同守护 |
| 测量 | 单一官方IGB-small input、两个冻结seeds`20261015/20261016`；强cache+async ON与同语义cache OFF诊断×每seed最多64自然B1024训练batch，正式train updates≤256；不跑全epoch/完整收敛，不称最终validation accuracy |
| 结果 | raw/summary≤64MiB，既有CPU/GPU工作不得互相影响；禁止NCU/Nsight/NVBit、模拟器/RTL、其它模型/数据集和硬件机制 |

**不得把A59未用网络、GPU额度带入本任务，也不得因为IGB-small压缩大小未知就盲下载或用IGB-tiny顶替。** 若small原实体大于4.5GiB或总下载6GiB、展开峰值14GiB或剩余可用盘64GiB不足，`ASSET_OR_BUDGET_STOP`，不切换medium/tiny、不给PCA压缩/FP16来节省空间。不能试多个来源直到某一份文件碰巧可用；确认实际官方镜像/MD5和源出处。

## 2. G0｜锁外CPU资源＋权利与身份资格，工程由Codex自行闭环

**第一步确权与版本**：作者Git`ODC-By-1.0`对公开共享IGB数据的声明、`README`与小规模`download.py`的同发布授权，登记适用范围、原始来源(MAG/Semantic Scholar)及其潜在独立rights；若实际归档/特征带额外限制不能确定用于本地非再分发学术实验，`DATA_RIGHTS_SCOPE_NO_GO`。不触碰原ogbn-products历史license门，也不假造全覆盖授权意见。

唯一科学档案：
- 官方`https://igb-public-awsopen.s3.amazonaws.com/igb-homogeneous/igb_homogeneous_small.tar.gz`，预发布`MD5=6781c699723529902ace0a95cafe6fe4`，没有预发布SHA256则下载完成后计算并绑定新的实体SHA、etag/bytes；
- 不从第三方“IGB-optimised split”代替原作者元数据。实际feature/edge/19类label与作者IGB`synthetic=0`解释闭合，固定node IDs、边方向、train/val/test mask与seed。作者small mask默认`torch.randperm`可受随机seed控制，必须在训练前写入split ID集合/hash，且所有cache路径共用该split。
- DGL仓库可能已经分发名为`igb-hom-small`的重打包图，不能仅因名字接近视为此作者原small的同一身份；**本任务只下载作者上述唯一archive**，GraphBolt转换可在本地确定性生成CSC及引用原始feat，而不能再次下载DGL另一个科学图。

网络与解包：CPU-only先查可信HTTP HEAD/Range与Content-Length、元数据、当前剩余盘；字节 ≤4.5GiB后以独立临时路径**一次**下载/恢复，记录所有流量。完整文件MD5必须与作者源一致，同时新增本次SHA256。压缩tar应**先只读流扫描全部成员/尺寸/路径安全**，拒绝绝对路径、`..`逃逸、冲突覆盖、symlinks/hardlinks/special files/异常PAX；预估最大展开+归档+GraphBolt转换的**同时间实际存储峰**≤14GiB且free≥64GiB才写盘。作者的`tarfile.extractall`无安全成员门，禁止未经检查盲调用。科学原资产备份/只读，cache/compiled仅新私有目录，保留归属与SHA。

CPU/source能力与正式PyTorch/DGL/PyG wheel闭包确定后，**只能在G1/G2合法进入前一次性冻结唯一计算实现**。允许按固定发行接口/源事实选择强GraphBolt+PyG例程或同源DGL GraphSAGE例程＋缓存接线，但不能跨PyG/DGL借不同torch.compile/损失定义混成一个软件速度比较；失败仍可在本合同预算内自主解决小版本路径、缺wheel、venv、manifest等工程问题，严禁源码编译整个DGL或更换系统CUDA/driver。

## 3. G1｜GPU锁内数据转换/抽样、强缓存功能与训练数值

仅在G0真实许可/图SHA/展开/合法环境/容量门全PASS后非阻塞获取共享锁。全GPU操作锁内，先用实际`author small real train node split`做**1–4个自然mini-batch`、原特征及label readback、GraphSAGE前/反向/Adam，可选择保留强cache测试和OFF同语义诊断，查看采样方向、合法fanout、重复节点、batch大小、loss/gradient finite、固定seed小样本数学或同软件oracle一致性（FP32容差从权威算子规则事前登记）。若缓存miss/fallback错误、GPU graph cache改变合法采样语义、ABI/OOM/数值错误，`NATIVE_INPUT_OR_CACHE_NO_GO`并STOP，不回退cache-OFF当强软件主路径。

**必须真实开启主路径**GPU graph cache（非零缓存边数）＋GPU feature cache（非零容量和正确fallback）＋pinned/UVA overlap＋async；同后端cache OFF仅用于验证本软件能力的敏感性。缓存占用初始候选`feature128MiB＋graph1,000,000 edges`，可以按首次VRAM容量资格确定不超过12GiB的一组合法非零配置并在任何正式计时前冻结；不因后来性能结果改大小。torch.compile若目标真实官方ABI支持，需要区分cold compile和warm steady-state；无法启用则明示`STRONG_COMPILED_PATH_UNQUALIFIED`，结果只能是eager scope characterization不能宣称最强软件余量。

## 4. G2｜≤256自然更新、真实wall与供数等待

新IGB-small固定两个种子，每个seed强ON与同语义OFF各最多64自然train minibatches，均从本次官方train mask取节点，不伪造热点/labels。首先记录**无每步强制同步的完整自然训练窗口`iterator sampling→feature fetch→copy→forward→loss→backward→Adam update`**，结尾一次合法GPU同步完成才停表，保留真实并行预取；JIT、初始化、解包及warmup另行计时并保持完整资源账。

**独立诊断**最多同已批准自然batch的轻量取样，记录采样/feature-ready/fallback字节或cache命中/等待、真实GPU active/CPU/PCIe headroom。诊断同步可能破坏overlap，不相加诊断阶段时间来宣称完整吞吐收益。主cache ON若仍出现与完整wall一致的暴露等待，属于`SCOPED_EXPOSED_SUPPLY_COST`，**尚非新硬件cache机制**；如果开启成熟缓存和异步后供数等待完全被隐藏或仅OFF弱对照差，`SCOPED_SOFTWARE_CACHE_SUFFICIENT`是有效负结果。科学输入一致性/样本形状/短程loss错误优先STOP，不卡用户多次确认。

**质量边界**：只测有界短训练窗口、有限数值/更新，必须标`CONVERGENCE_NOT_EVALUATED`，不拿64batch训练当官方任务最终accuracy；不把DGL/cugraph或PyG原本不同模型数值作“正性能”展示。没有完整短训练步结束的wall实测不能硬件归因。

## 5. G3｜报告、失败收据及STOP

成果只在新任务branch：`docs/ai_workload_research/runs/AI_ARCH_A61_IGB_SMALL_GNN_NATIVE_109_V1/`下`FINAL_REPORT.md, GATES.json, DATA_LICENSE_AND_AUTHORITY.json, GRAPH_AND_TRAIN_IDENTITY.json, STRONG_SOFTWARE_AND_MODEL_NUMERIC.json, NATIVE_STEP_WALL_AND_SUPPLY.json, RESOURCE_RECEIPT.json,SHA256SUMS`及必要raw/最小独立runner`tools/aiarch_a61/`。原图和venv/cache/体积大payload保留任务私有，不加入Git/164、不公开个人数据或涉及原文档重分发。报告含作者IGB来源及ODC-By归属、若提供输出需带数据署名。

合法终态至少：`DATA_RIGHTS_SCOPE_NO_GO,ASSET_OR_BUDGET_STOP,OFFICIAL_ABI_NO_GO,DATA_OR_NUMERIC_NO_GO,STRONG_CACHE_PATH_NO_GO,GPU_LOCK_DEFERRED,BUDGET_STOP,SCOPED_SOFTWARE_CACHE_SUFFICIENT,SCOPED_EXPOSED_SUPPLY_COST,SCOPED_INCOMPLETE_ATTRIBUTION`。未执行步骤全部`NOT_RUN`；不把source-only/metadata资格填成native性能。不向其他项目分支写文件，不自动启动A62、第二GNN图、NCU、模拟器或新硬件机制。

Codex可在这**一条Goal**内自己解决合法版本wheel、路径、预处理、缓存API、runner/script、编译warmup等全部小工程问题，工程重试都计入预算，科学数据/质量/模型/后端选择（冻结后）或资源权限变化必须STOP。最后归档全部正负证据、commit/push、远端fetch-back exact SHA/tree/blob与checksum、释放锁/清理自己GPU进程、worktree clean后`STOP`。**该Goal直到收到明确的用户新输入授权前都不得真正执行下载或GPU。**