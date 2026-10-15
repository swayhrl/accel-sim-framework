# AI-ARCH A59｜GraphSAGE/ogbn-products强GraphBolt缓存+异步供数：单次连续原生Discovery

**状态：APPROVED_ONE_BOUNDED_NATIVE_DISCOVERY_BY_STANDING_USER_CONSENT / READY_FOR_CODEX / EXECUTION_NOT_OBSERVED。** 用户此前明确“后续我默认确认，你可以一并给出，有意见我会说”，本轮又强调“如果不涉及大方向的问题，其实可以授权Codex去自己解决，提高效率，别每次都这么反复迭代”。A58在固定真实数据与源审后选择唯一Q-G，A59继续**这一明确的同一研究方向**；只授权本Goal下述各项真实环境/数据与有限GPU执行，**不得自行升级GPU预算/更换科学对象/放宽质量**。目标是最大程度委托普通工程，不做每个G门一次审批。用户的新指令如与本合同冲突，以新指令优先，超界先STOP。GitHub授权≠真正109已启动。

- Repository：`swayhrl/accel-sim-framework`
- 独立branch：`hrl/aiarch-a59-graphsage-products-bounded-native-109-v1`
- 固定协调parent：`ad20e74f7168ced42444264b3600e54f4bb3d2a5`；**启动以本Goal发布完整commit为准，不回退parent**。
- 执行者：node109新独立Codex worktree/output/venv；可以使用已STOP的109 Lane M对话，但绝不能在旧A50G/R1/R2 worktree、venv、数据、index、原报告上继续写。174-new A58 STOP且host swap/I/O压力较重，不向它分配本次图下载/解包工作。AWMA、C16原工程不受本次任务影响。
- 起点：[A58严格SOURCE_ONLY报告](https://github.com/swayhrl/accel-sim-framework/blob/9560b28ee85618a9059e309cb640c210b4575dfc/docs/ai_workload_research/reviews/AI_ARCH_A58_VLA_GNN_MINIMUM_SOURCE_ADMISSION_174NEW_V1.md)、[A59独立科学复审](https://github.com/swayhrl/accel-sim-framework/blob/ad20e74f7168ced42444264b3600e54f4bb3d2a5/docs/ai_workload_research/reviews/AI_ARCH_A59_A58_GNN_NATIVE_PRIORITY_AND_ENGINEERING_AUTONOMY_REVIEW_2026-10-15_V1.md)、`docs/ai_workload_research/COORDINATION_PROTOCOL.md`、`CURRENT_STATE.md`。现有A50G GPU执行已`QUALITY_NO_GO/STOP`，不得重启或复用其GPU额度。

## 0｜唯一科学问题、允许的自动工程解法

**Q-A59：** 在官方真实`ogbn-products`固定数据与GraphSAGE训练语义下，已经启用**GPU graph cache＋GPU feature cache（含正确fallback）＋pinned/UVA异步sampling/feature-fetch**的强GraphBolt训练路径，是否仍暴露在连续自然mini-batch`sampling→feature ready→forward→backward→Adam update`**完整wall**中的供数延迟？如果只有关闭缓存后变慢、或异步覆盖了全部等待，**没有证明额外硬件headroom**。

**一次Goal内全链G0→G1→G2→G3→G4**，不要一门一条Goal。
- **Codex被明确允许自主solve-and-continue**：已冻结语义和预算内的Python/CLI/日志、目录、数据manifest格式、合法镜像/Range/压缩审计、同版本官方wheel/隔离环境构建、torch/DGL/PyG API机械适配、cache容量合法初始化、随机种子可复现、tensor shape/contiguous/dtype、GPU显存安全回收、数值/计时wrapper、准确归档。可做合理多次工程尝试，不机械限制“一处小错误一轮”；**全部计入同一累计CPU、网络、盘、GPU账**。每次原始错误与diff保留、修后同数值门重新验证。
- **不允许自动变更的科学轴**：节点/图、OGB split/方向/标签/特征、GraphSAGE3层hidden256、fanout`10,10,10`、batch1024、真实训练任务/optimizer/loss/dtype、计时边界/种子与质量gate、正式后端冻结、缓存对照的合法功能/采样分布，以及任何被隐藏的GPU硬件设计。若需要换其他数据集、synthetic graph、FP16、缩小graph、更多样本、再下载未知大型资产、CUDA驱动/系统修改、源码重编整个DGL/PyTorch、附加GPU或新机制，必须STOP并在报告中说明提案，不得视为工程小修。
- 发生真实数据/模型质量失败、无法合法取得源码/二进制/数据许可、科学变更或预算将超界时，按G4终止，未运行的结果标`NOT_RUN`。不要为了得到“正发现”而降低质量、切后端或多扫缓存容量。

## 1｜总资源合同（全新独立，不能借C16/AWMA旧额度）

| 类别 | 硬上限与纪律 |
|---|---|
| 109 GPU | 单RTX4080/SM89、GPU进程≤1并发；**共享锁`/data/c16/locks/c16_gpu_campaign.lock`用LOCK_EX/LOCK_NB非阻塞且父监督全程持有，累计≤1800秒（30分钟）**，含CUDA导入初始化、torch.compile/JIT、data canary、真实训练、诊断和清理；锁忙立即`GPU_LOCK_DEFERRED`，不轮询、不强占 |
| 网络 | **总新增下载≤4GiB**，其中科学OGB图源包最多2.5GiB、隔离官方wheel/依赖≤1.5GiB；明确记录真实bytes/每个实体URL/etag/实际SHA。可重用已存在、身份合格、用户有权访问的只读本地缓存；不能抄写不存在的预发布SHA |
| 磁盘 | **所有新worktree/venv/archive/extracted/processed/cache/日志合计≤8GiB**，目标所在FS空闲始终≥64GiB；不得清理/覆盖旧任务/系统模型/用户目录来腾空间 |
| CPU/Host | 总实际CPU有效workers≤4、任务进程树峰RSS≤16GiB，锁外CPU预备≤2h；禁无限压缩展开、无限编译、后台retries或独占其余服务 |
| VRAM | 所有当前任务GPU进程显存≤12GiB，留额外空间给系统/驱动，NVML短采样不能证明瞬时绝对峰值，需主动限制图缓存和预留OOM裕量 |
| 工作量 | **一份真实官方OGB图**、一种正式冻结GraphSAGE模型实现、两种缓存开关路径（ON强主、OFF诊断）×两个事前固定seed ×最多64真实自然train minibatches/路径/seed，正式GPU训练≤256步，不启动全epoch长训练；CPU-only实验/数据资格可单独STOP |
| 额外 | raw/summary≤64MiB，不保存大量独立子图、没有模型大checkpoint/视频，禁止NCU/Nsight/NVBit、Accel-Sim、系统driver/firmware操作、其它GPU任务与新机制 |

**下载/解包要求：** 下载前尽量核压缩实体大小/返回字段/可信链接以及新磁盘峰值，下完在不解压实体数据的条件下stream列举zip/tar目录，检查展开尺寸/路径安全/重复/symlink/hardlink/special file/异常压缩比和所需临时文件；执行时全程对≤8GiB硬限实时监督。如出版方未给预存SHA，在下载完成后计算真实实体SHA及内容shape/label/split，不伪造提前授权的SHA；无法确定展开尺寸就合法先下载后审索引，但不可以盲解包。仅DGL/OGB官方认可图来源，需记录适用学术研究/数据使用条件，不把代码开源许可证当原始图实体许可证。**任何有争议/不可查的实体使用权、异常路径或超预算→STOP**。不得经未知镜像暗换科学内容。

GPU共同资源限制：先非阻塞持已有锁，确认无其他GPU计算进程，CUDA/RMM/torch GPU初始化和任何显存探测在持锁期内，锁从首个GPU子进程到最后子进程退出保持。GPU计时前停止本任务所有下载/解包/重CPU hash；不kill其他任务，仅管理自有进程组。GPU时间/数据/盘/RAM/CPU累计，不因包装修复或重启子进程重置。

## 2｜G0：事前确定“官方有ABI＋真实图合法”的唯一实现方案

A58发现`dmlc/dgl@3d16000b4170fa741ed9e9667f22ba84d3493026/examples/graphbolt/node_classification.py`可以完整运行训练步，但普通例程没有GPU feature+graph cache。A59又已确认**同一Git commit**的[`examples/graphbolt/pyg/node_classification_advanced.py`](https://github.com/dmlc/dgl/blob/3d16000b4170fa741ed9e9667f22ba84d3493026/examples/graphbolt/pyg/node_classification_advanced.py)提供缓存容量、异步采样、pinned graph/feature和`@torch.compile`训练。
- **优先实现路线P：** 从该高级官方例程的**一个固定训练实现**生成最小私有runner；依赖`PyG/GraphBolt`的稳定官方发行版本，提前核对应Torch/cu12/driver/SM89、pip精确wheel和API；不可把master源码签名当已安装wheel。
- **许可内备选路线D，仅G0/G1科学计时开始之前**：若PyG发行二进制和GraphBolt复杂依赖不能在网络/盘/时间硬限内资格化，可选固定正式DGL GraphBolt版本，在其原`node_classification.py`里以同发行已存在的`GPUCachedFeature`和`NeighborSampler`相关API**最小接线**，确保graph/feature cache真正非零和fallback合法。DGL原生层不是PyG层，必须标明`IMPLEMENTATION=DGL_SAGE`并独立冻结数值oracle，**不能跨P/D混合样本或沿用另一路的计时/数值**。P/D选择并固定在任何正式训练测量之前；至多一个备选，不继续探索许多不同PyTorch/CUDA/DGL发行版本。若高级官方PyG无法合法安装而DGL接线又不合格，`OFFICIAL_SOFTWARE_NO_GO/STOP`，不进行弱无cache实验凑出结果。
- **DGL发布风险**：DGL v2.4官方CUDA GraphBolt wheel需要与PyTorch/CUDA次版本相配，NVIDIA于25.08后不再维护DGL容器，`cuGraph-DGL`在RAPIDS 25.08移除；只读源审cuGraph-PyG作为强近邻，不要求本次额外安装整个RAPIDS。已安装wheel需commit/版本/API/sha/预编译CUDA资格后再冻结，不能为追求最大速度临时切换。
- **真实工作负载冻结**：OGB`ogbn-products` 2,449,029 nodes、61,859,140无向edges、100 feature、47 classes，**固定sales-ranked train/val/test**，DGL BuiltinDataset可能增双向边；逐项核实际有向CSC数、feature dtype/range、label对应ID、split成员不重合与原正式任务。GraphSAGE**3层mean**、hidden256、fanout`10,10,10`、seed节点B1024、FP32、cross entropy、Adam，学习率/weight_decay采用**选定官方例程版本中的原配置**，在运行前记下数值，整个对照保持相同；不从P示例挑一半参数与D示例另一半拼成更快模型。
- 采用两个预冻结seed`20261015`和`20261016`，各从原官方train split shuffle顺序中取最多`64`个自然batch（每个1024个真实训练seed节点），不随机造图/节点标签。模型初始化/优化器相同seed在ON/OFF两臂复位，缓存初态和自然warmup明示；不同异步sampler随机流允许统计等价，但要区分相同sample-ID形状测试与不同采样历史，不悄悄将差异作缓存因果。
- 先用固定小mini-batch及实际官方聚合数值，预登记适用FP32 shape/label/feature hash、forward/loss/gradient/optimizer canary容差和**可测指标**；不事后因训练loss变差改门。全训练收敛/最终test准确率不在本次≤256步合同内，必须标`CONVERGENCE_NOT_EVALUATED`；仅固定小样本层输出或loss/gradient与合法同后端计算oracle核一致性。

若既有DGL模型组件无法合规取得/data使用许可未确定、torch ABI无可用官方包、压缩包超过预算或109真实RSS/VRAM余量不足，**G0/G1停止、GPU训练标NOT_RUN**；所有普通version/CLI/archive包装问题Codex在额度内自行解决，不再拆Goal。

## 3｜G1：在原GPU锁内小型功能与强缓存资格

- 获取锁后一个任务专用GPU进程首次构造真正的GraphBolt data loader与GraphSAGE，SAGE模型权重从既定seed确定性初始化。使用原训练集mini-batch但先对**一到四个真实mini-batch**（计入全部GPU预算，若发生optimizer训练更新同样计入正式任务步骤上限）检查：采样节点ID/各层fanout与合法边方向、实际feature读回、loss finite、backward非零有限、optimizer更新合法，主缓存ON和关闭cache诊断均能使用相同合法图/标签。
- 必须验证GPU feature cache对命中与缺失路径的**返回值与fallback正确**，GPU graph cache命中与正常邻域采样语义一致（允许随机采样分布，不允许反向边重复改变模型输入定义）。cache值和训练精度gate不成立STOP，不能回退仅无缓存版本作为强baseline。不得为强制cache hit制造额外非自然热点节点；如果自然输入低命中，也将其作为有效负现象。
- 事前按当前可用VRAM一次选择两种明确非零cache额度，参考初始`feature cache 128MiB`、`GPU graph cache 1,000,000 edges`，两者实际峰值加网络模型/loader必须≤12GiB；**仅为可用内存预调一次，不允许根据后续正式timing/recall/结果调cache大小找正结论**。如果该配置不满足合法显存预算且找不到任何非零合法容量，`CACHE_STRONG_PATH_UNQUALIFIED_STOP`。
- 若Python/torch.compile后端存在包装错误，可自主在该Goal内按官方ABI与同数值要求有界修；`torch.compile`支持时主路径ON并**完整计冷JIT/首次图编译时间**，稳态测时将其另记。若compile不支持而采用eager路径，ON/OFF都eager，标`COMPILED_STRONG_BASELINE_NOT_QUALIFIED`，只能作eager的有界characterization，**不宣称覆盖最强compile软件或产生待开发硬件机会**。不要为编译重试无限消耗GPU锁。

## 4｜G2：一次真实train step wall与数据供数归因，不造假重叠

**完整自然阶段、强路径先测**：对每个seed的缓存ON和OFF诊断各最多64自然训练mini-batches，总正式训练更新≤256；算法模型/训练窗口/graph/label/worker/thread都冻结、分别从相同初始参数出发，每臂合法warmup（建议8自然batch；warmup也计实际GPU锁/资源并与正式数据分离）。缓存OFF仅是诊断，不可称世界最强软件比较对象。

**第一优先指标：未插桩的整段训练完成wall**。
- timer启动在预登记采样迭代器开始消费前，覆盖真实`ItemSampler→neighbor sampling→feature fetch/fallback→copy→GraphSAGE forward→loss→backward→Adam optimizer.step`。保留后端合法pipeline异步与预取，**中途禁止每step调用`torch.cuda.synchronize()`或`loss.item()`等人为同步**；结束后唯一`torch.cuda.synchronize()`使最后设备工作全完成才停表。记录起始/结束所有阶段状态、整段step数、cold/warm编译和cache warmup；并单独记录data loading/extraction/JIT初始化总时间，不偷移到稳态声称全应用收益。
- 诊断阶段**另一次轻量受控执行**才能查看`loader iterator wait, feature-ready wait, GPU compute vs CPU prep, cache hit/miss/fallback/bytes`，必须注明插桩同步对原overlap的扰动。不能将各阶段单独耗时相加当完整wall，也不使用Python异步enqueue耗时冒充GPU完成时间。若对应cache API没有真实counter则写UNKNOWN，不靠从逻辑request个数反推DRAM字节或SMEM占用。
- 同seed下ON/OFF公平：同train node batches、初始化、optimizer超参、模型前/后状态、精度；记录真实sample邻域数/重复率/节点度分布，允许async采样不逐bit相同则只能称分布控制不等于严格配对因果。只在样本/梯度可比时解释缓存作用。必要的一两个负控制来自同一官方train split低热点自然批或较低fanout会**改变一个科学轴**，本Goal不自动扩大训练；优先用已有天然低命中窗口诊断。
- 初始任务不验证完整epoch收敛。可读取原官方validation split的**固定微量功能canary**核输出形状/标签合理，但不作训练后test success或完整accuracy claim；test set保持未用。确认模型/抽样、数学loss/gradient gate不变，错一项则`QUALITY_OR_SEMANTICS_NO_GO/STOP`。

**结果分类**：
1. 完整wall上强缓存ON已经让sampling/feature等待消失/在噪声范围内，`SCOPED_NO_EXPOSED_SUPPLY_BOTTLENECK`（合法负结果）。
2. ON强路径仍有可重复、被完整wall揭露的等待且能排除cache wrapper/host I/O/torch compile不均后，`SCOPED_EXPOSED_SUPPLY_COST`，属于体系结构characterization**候选**，不是缓存硬件机制或外推整个GNN训练。
3. 只有OFF弱对照显著慢，而ON完整wall无问题时，`SOFTWARE_CACHE_SUFFICIENT`，不能把OFF/ON差异充当新硬件headroom。
4. 两臂科学样本/ABI/caches不合格，`QUALITY_OR_PLATFORM_NO_GO`、不报告速度优势。所有测量保持源/实际计时/纯估算三级清晰。

## 5｜G3/G4合并归档与NEXT：真正一轮后不再回报小问题

一个完整收据目录`docs/ai_workload_research/runs/AI_ARCH_A59_GRAPHSAGE_PRODUCTS_NATIVE_109_V1/`包含`FINAL_REPORT.md`、`GATES.json`、`ENV_AND_DATA_AUTHORITY.json`、`STRONG_SOFTWARE_AND_VALIDATION.json`、`NATIVE_WALL_AND_WAIT.json`、`RESOURCE_RECEIPT.json`、`SHA256SUMS`及限量raw；必要新脚本`tools/aiarch_a59/`。脚本与日志≤64MiB，不把OGB zip/processed graph/venv/模型大checkpoint放Git。按资产SHA和实际运行版本、科学source tag/归属、采样/缓存强基线、命中、完整wall与分段wait、所有失败和stop、进程/温度/CPU/GPU内存/锁、累计下载/盘、修复diff留完整证据。

Codex同一Goal完成：合法包/数据预检→隔离安装→真实数据/采样及缓存正确性→有限本机训练测量→原始与负面证据→科学自审/唯一下一问题选择→commit/push/fetch-back exact SHA/tree/blob及原始SHA→工作区clean、释放GPU锁、`STOP`。**不允许因为某个轻微CLI或manifest问题自动报告“科学输入缺失”而提前停掉整个已批准主线；真正scientific dataset缺失、无官方ABI、精度/采样意义改变或预算/安全越界才按规定STOP。**

若未完成实际原生训练，精确归因`DATA_LICENSE_NO_GO / OFFICIAL_ABI_NO_GO / DATA_OR_DISK_BUDGET_STOP / CACHE_STRONG_PATH_UNQUALIFIED / CUDA_NUMERIC_NO_GO / GPU_LOCK_DEFERRED / BUDGET_STOP`；主阶段通过且无新剩余`SCOPED_NO_EXPOSED_SUPPLY_BOTTLENECK`，正候选`SCOPED_EXPOSED_SUPPLY_COST`。未执行点全部`NOT_RUN`，不能填漂亮表。

**硬STOP且未经授权不可自动做**：更多图/模型/全epoch大训练、GPU profiler、第二CUDA后端大安装、额外GPU、174/164大数据作业、改变节点/梯度/optimizer/质量、A50G CAGRA重启、AWMA/C16、模拟器/RTL/新cache。即使实验表现可能有硬件价值，也先在一份报告中提出**恰好一个**有证据的下一小合同，Codex不得自行越界开后续GPU任务。