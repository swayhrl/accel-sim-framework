# Round A68｜A67 IGB-small GraphSAGE eager-scope全GPU驻留与缓存软件反证独立科学审查

**日期：2026-10-16；审查者：ChatGPT／AI-ARCH Discovery。**

**独立裁决：接受 `A67_SCOPED_FULL_RESIDENT_SOFTWARE_ALTERNATIVE / STOP`，只在固定IGB-small、RTX4080、PyG GraphSAGE、GraphBolt配置与eager短窗口内成立；不支持据此启动新硬件Cache机制。** 原A61 `DATA_OR_NUMERIC_NO_GO`及A65 `COMPILED_PATH_NUMERIC_NONALIGNMENT`继续冻结。没有编译合格证明，没有完整训练收敛、真实PCIe/DRAM字节或资源等待归因。

## 0. Git与独立证据范围

- 源分支：`hrl/aiarch-a67-igb-small-eager-scope-wall-109-v1`；批准前Goal起点`266314db14686b75d643c446824ebf8d59ba3a51`；最终commit`c425819d1f41e0cbd3053315cd5590697e808a3c`；tree`5ae9be2bf51ba959b9588a8111ae28bf6f03af84`。
- 使用GitHub连接器独立比较：Goal→final `ahead1`、89个新增路径；final→当前执行branch HEAD `identical`。独立读了FINAL_REPORT、GATES、六个`raw/wall_*.json`、`native_results.json`、`analysis.json`、数值/身份/预处理/资源/PID监督收据、`tools/aiarch_a67/native.py`与该次归档执行源码、源AST收据。Git的六个wall blob身份一致。
- **额外进行了独立SHA256重算：六个实际wall JSON逐字节SHA256与同commit的`SHA256SUMS`逐项完全一致，6/6 PASS**。manifest总计88个SHA条目，89个新增文件包括不自引用的manifest本身；审查没有逐字节重算其它82个Git文件，不把Lane M报告的全部89项回读冒充本次独立重算。
- 该审查仅GitHub读取与控制端纯计算，不SSH、不读当前109进程、不触发GPU/模拟器、不改A67原branch/raw；109的全部文件归档验收和本机现场由执行receipt承担，证据边界保持清楚。

## 1. 原数值身份与运行合同审查

- 原始输入真实：官方IGB homogeneous small，1000000节点、1024维FP32特征（`synthetic=0`）、19类；原有向边12070502，按作者自环约定派生CSC有向13070502条。train split seed20261015和两训练seed的冻结natural node-order与A61权威hash一致。未将IGB替换成OGB或随机features。
- 算法路径是同一个3层mean PyG SAGE、hidden256、fanout10/10/10、B1024、FP32 highest/TF32关闭、cross-entropy、Adam lr0.003/weight_decay0/defaultbetas eps1e-8。执行`raw/algorithm_ast_identity.json`核原A61七个关键定义AST匹配；A67执行runner只负责新的任务隔离、一次OFF canary、时间窗口和资源监督。编译路径完全未运行，属于独立批准的`EAGER_ONLY`范围，不能写成已通过torch.compile的strong software。
- G1新OFF路径16-seed CPU FP64数学oracle PASS（仅参考在FP64，训练仍FP32），max forward abs 1.42554694e-8、gradient 7.93477284e-9、首步Adam 7.45058e-9；FULL/ON以前eager资格保持，A67每arm/seed的两个真实warmup进行新输入、采样边、fallback/非零cache、参数有限性及真实GPU驻留检查。六窗口分别12 formal且Adam逐参数step=14，总1 canary+12 warmup+72 formal=85更新；短程loss finite，未计算epoch收敛/任务最终accuracy。
- 每个seed跨三arm具有相同初始模型SHA和正式seed-node-order SHA，但GPU采样邻域分布是独立、合法随机抽样，不存在逐边bitwise配对的强因果合同；各arm不是精确同一张采样子图的単变量性能消融。CPU侧重算六窗口正式batch平均输入节点在349066至349508之间，平均第一层采样边在593162至594498之间，规模同数量级；不把这种相近误称证明每次工作完全等价。

## 2. 六组native完整wall独立重算

| arm | seed 20261015：12 step wall (s) | seed 20261016：12 step wall (s) |
|---|---:|---:|
| FULL_RESIDENT_GPU | 0.310875250 | 0.435466565 |
| PINNED_CACHE_ON | 1.788361889 | 1.771150016 |
| PINNED_CACHE_OFF | 1.125984990 | 1.100230595 |

- seed20261015：ON/FULL=5.75267、OFF/FULL=3.62198、ON/OFF=1.58826（ON比OFF慢58.83%）。
- seed20261016：ON/FULL=4.06725、OFF/FULL=2.52656、ON/OFF=1.60980（ON比OFF慢60.98%）。
- **三个arm的排序两个seed均为FULL < OFF < ON。** 原始计时在创建formal iterator前开始、完整包含GraphBolt sampling→feature-ready→PyG前后向与Adam，末次GPU sync停止，无逐step `loss.item()`、显式sync或Profiler；只保留廉价shape/count元数据和loss张量，正式停表后完成hash/CPU审计。原源码支持这个边界，且每格保留了12个loss；`wall/12`是窗口平均，不等于12个独立每step latency。
- 每个batch实际平均请求FP32 feature约1.332GiB逻辑字节，同seed三arm平均输入规模仅千分量级差异；**逻辑feature request不可写成PCIe物理流量、DRAM读字节或缓存miss带来的实际额外传输**。
- FULL两seed的窗口0.311s与0.435s相差约40.1%（按较小者），这两格处于执行顺序首尾；ON两seed仅约1%差别，OFF约2.3%。只有每arm两次不同seed短窗口，未能区分seed、自然采样、时钟、运行顺序或服务状态。大排序有一致支持，但具体倍数不是跨设备/长训练置信区间。
- ON非零feature cache128MiB＋graph cache1000000edges确认生效；训练后feature累计miss为95.463%/95.431%，graph累计miss约87.817%。OFF仍使用pinned GraphBolt/UVA/异步路径，只关闭两种GPU缓存，因此它不是完全未优化的软件参照。**ON对OFF是graph+feature cache捆绑开关比较，不能单独把额外开销归因某一级缓存。**
- FULL不仅把全部原FP32 feature与CSC完全放到GPU（GPU端真实执行），还相应改变GraphBolt图采样和供数位置、overlap设置；**FULL/ON/OFF不是只改变CPU→GPU PCIe流量的单变量硬件因果对照**。可以公平地用其说明“存在更快的成熟软件执行方案”，但不能把数倍wall差全部称为PCIe停顿。

## 3. 准备成本与可用性

- FULL各seed在任务内`ctx`准备约0.21830s和0.21842s，公共pin准备一次0.95742s，warmup额外0.33440s和0.33636s。FULL真实正式窗口Torch峰值reserved 9.539/9.594GiB，实测采样NVML峰的全任务总量10416MiB；可在12GiB合同内持续2warmup＋12正式自然更新，不是纸面估计。
- 为检验是否单纯“预复制后隐藏成本”，独立计算`ctx准备+正式12步wall`：FULL=0.52917s/0.65389s；OFF=1.12608s/1.10031s；ON=1.78932s/1.77157s。**12步范围内，即使加回FULL独有的该项准备，优势仍在。** 但该算术不含公共pin、warmup/审计、初始化和进程冷启动，也不代表独立测得的应用端到端方案速度。真实业务改变驻留区间、GPU并发、模型或输入规模时，这个比较可能变动。
- 当前1M×1024 FP32 feature总量4096000000B；可驻留不等于更大IGB、多任务显存竞争、动态特征、分布式CPU/GPU服务都可驻留。若未来研究大规模图，需要另立新的科学对象、容量反证和严格资源授权，不能拿本轮作为大图硬件收益先验。

## 4. GPU监督与资源独立审查

- 独立读取`gpu_pid_snapshots.jsonl`全41行：8条无NVML compute进程，33条分类为`OWN_LIVE_PID`；均无`stop_reason`。唯一自有PID3560580的初始`start_ticks=274674203`、PGID/SID和NVML/`proc`采样一致；最后一次FINAL_DRAIN中子进程返回0、NVML为空。
- `gpu_ledger.json`另记录`status=COMPLETE,reason=null,exclusivity_evidence_complete=true,shared_lock_released=true,all_owned_processes_ended=true`；非阻塞使用原GPU锁，实际持锁20.544467s≤900s；采样task RSS峰9.350GiB、NVML峰10416MiB，CPU线程4，下载安装0，完整正式72+warmup12+资格1。采样可能漏瞬时峰；各窗口Torch allocator另有精确峰，容量未观察到越界。
- 原A65最后PID证据缺口在本次监督器改善，**本次完成充分、未观察到第三方GPU进程**。这不反过来推断旧A65一定误报或修改其原STOP。
- 任务新增盘保守`56336384B≈53.73MiB`（含预估Git对象；raw/log实占`11829248B≈11.28MiB`），均低于256MiB及32MiB硬门；用户回报的50.13MiB/11.31MiB可能使用不同账口径，不以简化数字替代原receipt。`post_readonly_audit`回报旧A61/A65目录、原模型/Graph/运行库状态未变；本窗口没有现场独立重hash旧109资产。

## 5. 科学结论与下一阶段

**接受终态`SCOPED_FULL_RESIDENT_SOFTWARE_ALTERNATIVE`，对“固定IGB-small/RTX4080/eager下GraphBolt缓存ON后的供数缺口值得新硬件缓存”的路线本轮及时止损/STOP。**

- 有力支持：完整GPU驻留在这份真实数据、同数学模型和有界连续训练中合法、容量可行、在两seed下均大幅快于pinned软件路径；当前固定CACHE_ON相较同平台CACHE_OFF反而稳定退化。
- 尚不能证明：所有GNN/更大图皆可全驻留；性能瓶颈只在PCIe；某一cache结构有59%硬件headroom；更换缓存容量/实现一定有效；eager就是包含torch.compile的最强软件；最终收敛与泛化性能等价。
- 不安排A67R1、GPU profiler、缓存参数后视扫、多GPU/更大IGB、编译器精度重试或模拟器机制。它们不由本轮结果自动授权，也不是修一个STOP所必需。
- **下一Discovery建议回到Q-S真实点云/稀疏卷积的source-only资格**：选一个真实输入坐标／特征／必要梯度闭合的自然层组，对照Spira、WarpConvNet及其它强后端，建立“结构构建→布局→fwd/dgrad/wgrad→末次消费”的合法寿命与准备成本分母；逐组说明算法/版本/实际模型状态、作者真实数据、已包含的软件map cache和反向选优能力，不下载大资产、不启动109/174/164。若无法找到合法且有增量的真实层组，按source NO_GO结束这一具体候选，不造合成性能机会。
- GNN仅在后续独立发现了**确实超出GPU可驻留容量、真实业务必须使用pinned/UVA或其它供数层次**的对象时再作为新科学问题评估；不从小图结果推出大图一定有硬件机会。独立项目C16/AWMA/ISCAS所有冻结边界不受影响。

**本轮A68为CPU/连接器只读独立审查，不是新GPU执行Goal；A67及A61/A65原始终态全部保持冻结。**
