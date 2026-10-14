# AI-ARCH A45S｜点云稀疏卷积与 GPU ANNS：下一份最小原生发现合同选择

**执行性质：174-new / CPU 与公开源码只读。最终选择：`ONE_SELECTED_PROBE_Q-A / PROPOSAL_ONLY`。** 在已审 A33–A43 的两个候选里，选 **GloVe-100-angular 上的 NVIDIA cuVS CAGRA 单图搜索**作为下次最小发现对象。它的输入、真值、强 AUTO 参照与现成诊断参数比点云稀疏卷积更容易在 RTX4080 上有界资格化。此选择**没有证明硬件 headroom、新机制或109可运行**；本文件只是待用户另行审批的 GPU 合同草案。本轮 GPU/CUDA/模拟器/109/164/数据下载/依赖安装均为 0。

## 0. G0 起点、既有证据与资源

分支 `hrl/aiarch-a45s-next-probe-admission-174new-v1` 从用户固定 `65130892533d92c04a704deee1f037865fee5367` 创建；远端头和 merge-base 均为该 SHA，ahead=0。独立 worktree `/root/workspace/accel-sim-framework-aiarch-a45s-next-probe-admission-174new-v1`，初始约2.7MiB、status clean。Goal 正文称共同 parent `8446f14595d2b084f5bcaea7b0ff4eac4d029a5d`；以用户更晚给出的分支 HEAD 为执行起点，不回退 Goal 发布提交。

174-new 预检：512逻辑CPU、load 209.05/214.42/218.26，但 CPU pressure some avg10=0.11%/full=0；IO pressure some/full avg10=0；RAM available≈340GiB；swap 2/2GiB；overlay free≈80GiB。进程表当前命名空间未见高CPU长任务，旧AWMA launcher在sleep。只进行少量SSH/Git、论文及官方API元数据阅读；无持续worker、GPU或模型进程。遵守本 Goal CPU≤2、RSS≤3GiB、增量≤40MiB、≤2小时，且与其它worktree/tmp隔离。用户未授权109/164读取，**下文109资源只是未来建议上限，不是现场事实**。

依次只读：[CURRENT_STATE](../CURRENT_STATE.md)、[COORDINATION_PROTOCOL](../COORDINATION_PROTOCOL.md)、[A34–A43 journal](../literature/AI_ARCH_A34_A43_TEN_ROUND_DISCOVERY_JOURNAL_2026-10-14_V1.md)、[A33 ANNS](../literature/AI_ARCH_A33_GPU_ANNS_SEARCH_STATE_RESOURCE_DISCOVERY_2026-10-14_V1.md)、[A44线程归因审查](AI_ARCH_A44_A26GR1_NATIVE_THREAD_ATTRIBUTION_REVIEW_2026-10-14_V1.md)。A44已纠正跨线程同步并集的解释，M正式STOP；本选择不重开3DGS或借其30–32ms构造新候选。A33/A43的源级数据与算术沿用，不再作新十轮综述。

## 1. G1/G2 投资筛选矩阵

| 准入项 | Q-S：真实坐标的点云稀疏卷积 | Q-A：真实GloVe向量的 CAGRA 搜索 |
|---|---|---|
| 输入及真实性 | [Spira固定loader](https://github.com/SPIN-Research-Group/Spira/blob/aee69c61f3e001f72828a6d5a70f6a1200166f65/scripts/loaders.py)从`.npy`读真实稀疏坐标，shuffle/平移，**FP16 feature 用 `torch.randn` 生成**；脚本未证明训练好网络的分割精度。官方[README](https://github.com/SPIN-Research-Group/Spira/blob/aee69c61f3e001f72828a6d5a70f6a1200166f65/README.md)列Waymo/ScanNet/SemanticKITTI的许可/账户/邮件取数路径；本轮无某单scene可直接下载的固定byte/SHA。结构型研究可合法，但必须限定claim。 | [ANN-Benchmarks固定README](https://github.com/erikbern/ann-benchmarks/blob/2e081ad32c1eccab72dcb739ad886c310b90f715/README.md)列GloVe-100-angular HDF5约463MB、1,183,514条100维base、10,000查询与top100真值；上游[GloVe页面](https://nlp.stanford.edu/projects/glove/)声明预训练向量PDDL1.0。HDF5衍生包的具体条款、真实bytes/SHA、zero-norm/tie及GT与cuVS距离一致性尚未核；它是词向量发现集，不等于生产RAG请求。 |
| 强软件和完整边界 | 固定[Spira `aee69c61…`](https://github.com/SPIN-Research-Group/Spira/blob/aee69c61f3e001f72828a6d5a70f6a1200166f65/scripts/end_to_end_experiment.py)每输入reset，在计时内排序、`add_all_kernel_maps`与model；不能把已计准备移出去造弱基线。TorchSparse++/Minuet需作者补丁、FP16/坐标和layer组对齐。完整结构寿命及真实重复消费需先确认。 | 固定[cuVS `bc23aa84…` planner](https://github.com/NVIDIA/cuvs/blob/bc23aa84a0ef26d85900185ad5e68d3372be487e/cpp/src/neighbors/detail/cagra/search_plan.cuh)已有 SMALL/HASH/AUTO、single/multi-CTA与清表。官方[Python API](https://docs.nvidia.com/cuvs/api-reference/python-api-neighbors-cagra)可固定同一 build、save/load、搜索参数和返回结果。强参照必须是同图、同recall的 **AUTO**，另一臂仅用一次校准选优的显式 `SINGLE_CTA+SMALL`；只研究CAGRA家族，不拿旧CPU榜单冒充GPU强基线。完整区间为CPU查询就绪→H2D→GPU search（含visited、排序/清表）→D2H→CPU结果可用；kernel-only及一次性build另列。 |
| 平台/依赖风险 | Spira整套artifact[建议](https://github.com/SPIN-Research-Group/Spira/blob/aee69c61f3e001f72828a6d5a70f6a1200166f65/README.md)≥64GB host、≥256GB盘、16GB GPU、SM7.5+、CUDA12.4+，并推荐Docker与多后端patch。RTX4080 16GB满足**标称**GPU下界，不证明一场景/两后端可fit或当前driver/ABI合格。单scan或许更小，但未冻结来源与费用。 | [cuVS安装文档](https://docs.nvidia.com/cuvs/installation)列Linux x86_64、CUDA≥12.2、Ampere/CC≥8.0；4080的SM89满足架构条件，具体109 driver/ABI尚未核。官方[Python wheel指引](https://docs.nvidia.com/cuvs/installation/python)支持`cuvs-cu12`。当前[PyPI 26.10.0](https://pypi.org/project/cuvs-cu12/26.10.0/)有Linux x86_64、Python≥3.11 wheel；对应[release `v26.10.00`](https://github.com/NVIDIA/cuvs/releases/tag/v26.10.00) commit `24ee1bf1cb17cad0ac611e39643af39ee1870124`。其`search_plan.cuh` blob `da42f637…`与A33 main快照 blob `a6d1bd…`不同；本轮只读确认release仍含AUTO query/SM选择及SMALL reset逻辑，**不能**把A33精确字节账当发行包运行收据。版本/API/依赖须首次canary冻结并复核。 |
| 诊断区分力 | 映射准备→布局→真实多个消费者的寿命，与Spira/TorchSparse++强实现比较有直接NN意义；但没有冻结小scene、匹配精度/特征和两后端ABI前，高概率消耗主要在移植/数据。A38已否定“eager map必然内存爆炸”。 | 同图/同查询/同recall下对 AUTO 和校准过的单CTA SMALL 比较 B1 与B256；actual planner algo、bitlen、reset、block/team、迭代工作需保留。若 AUTO 已够或差异只由这些现成策略解释，则是合法软件负例。两臂并非纯物理SMEM干预，不能从它们直接宣称硬件因果。 |
| 下载、样本和取舍 | 全artifact大且三类scene需许可；一个small真实scan需要另核合法最小URL、byte/SHA。强后端patch/构建空间和训练质量无门。保留后续结构研究，不将其“不方便”说成方向无价值。 | HDF5标称463MB，源/质量对象单一；base约473,405,600B，degree64 uint32最终图约302,979,584B，base+图约740.42MiB（A33纯算术，**非峰值显存**）。图建中间量、依赖/allocator和HDF5副本未知，可在有界canary安全检查。固定10k查询可分校准/独立报告；本机GPU成本仍待批准。 |

**选择逻辑**：Q-S研究价值高且直接关联神经网络，保留为候选；但A45S的目标是**下一次单RTX4080上最小、合法、强软件有效的发现**。Q-A已具公开单文件输入、ground truth、Python/C++现成搜索策略与不被架构代际排除的发行入口，且无需训练模型或三套scene。故选Q-A。若其数据/同recall/发行门失败，A45S的后备决定是 `NONE_SELECTED`，**不自动切换到Spira下载或GPU任务**。

## 2. `ONE_SELECTED_PROBE_OR_NO_GO`：Q-A 唯一未来草案

**科研问题（发现层）**：在同一真实GloVe图与相同recall@10要求下，既有 cuVS AUTO 与最优可用的显式单CTA小表路径，在小/大自然查询batch上是否留下稳定的完整search时间差？差值若存在，是已知AUTO算法/重算/清表/CTA选择解释，还是有需要**下一轮再定位**的片上状态—并发代价？本probe只发现/反证，不做RF/SMEM×2模拟或硬件机制。

**固定对象与两个最终路径**（未来授权后、正式测量前冻结）：`GloVe-100-angular` HDF5唯一输入，FP32、不压缩；CAGRA `k=10`、`metric="cosine"`，一次构图 `graph_degree=64`、`intermediate_graph_degree=128`、官方`build_algo="ivf_pq"`；固定随机种、index与graph blob SHA，保存/读回同一index给所有臂。每臂 `itopk_size=128`、`search_width=1`、`max_iterations=64`、`hashmap_max_fill_rate=0.5`、`persistent=False`、无filter，预设输入batch∈{1,256}。路径 A＝官方`algo="auto", hashmap_mode="auto"`，保留实际解析出的single/multi-CTA、HASH/SMALL与参数；路径 B＝`algo="single_cta", hashmap_mode="small", thread_block_size=128`，`hashmap_min_bitlen`从{9,11}只在**校准query**中按“同质量→完整时间”选一个并锁定。`team_size`由同一已审发行版的descriptor确定，记录effective值；若不能证明两臂其它search设置一致，停止比较。正式发现矩阵仅**2 batch×2路径=4点**；校准/功能canary另限≤8个预定配置检查，总不超过12个实验点。h9与h11不是两个正式臂；不反复扫更大hash找正数。

**输入与质量门**：首次取得官方 HDF5 后记录原件URL、许可核对、Content-Length/实际bytes/SHA256、HDF5字段与shape、0-norm/NaN、top100 ID范围；采用文件内原始train/query/ground truth，确认 angular 与 cuVS cosine 距离、规范化和tie规则。以固定seed `20261014` 对10k查询索引作确定性hash划分：约20%仅用于配置校准和小canary，余约80%独立用于报告；在报告集上预选固定2048不同查询作时间样本，完整报告集用于 recall。首个canary对32查询核结果ID范围、距离/小规模精确参考和recall；要求两正式路径在独立报告集 **recall@10≥0.95 且差异≤0.005绝对值**。若合法配置不能在校准范围达标，或真值/距离身份不合，STOP，不放宽质量阈值、不更换向量集。recall不是逐bit邻居顺序，tie处理须先冻结。

**完整时间与辨识**：同一index和query顺序，记录（1）预载query的未插桩GPU search时间（含内部visited/reset/sort），（2）CPU查询→H2D→search→D2H→CPU结果可用的host wall；build、保存/加载、一次性初始化另报，不暗中摊入/挪出。B1和B256各报告每查询延迟、batch吞吐与分布，避免把复制同一query伪装并发。三fresh process，各按ABBA顺序做至少10个配对重复，测时前warmup、GPU锁下固定时钟/背景任务和allocator状态；按配对差及bootstrap区间报告，不将NCU序列化时长当wall。记录A/B effective算法、SMALL bitlen、reset interval、block/team、实际迭代/距离数（若现成接口可得；否则UNKNOWN）。**只有**同recall且强AUTO后仍有稳定完整search差异，才值得另行申请少量资源定位；即便出现差异，本轮也不能归因物理SMEM/occupancy。

**最低后续资源建议，未获批准**：仅109一张RTX4080，原共享GPU锁非阻塞；新隔离Python≥3.11 CUDA12 wheel环境，不改旧torch/driver。数据网络≤0.6GiB，含官方包/依赖的总下载≤6GiB；新磁盘≤12GiB、host peak RSS≤8GiB、CPU≤4 worker、GPU峰值≤12GiB、累计持锁≤45分钟，raw/summary≤64MiB；仅一次图构建/序列化及4正式点，最多12配置检查。数据只是463MB标称，build峰值与109当前空闲/驱动/发行ABI均**未验证**；任何一项超额、锁忙或GPU上有旧正式任务即STOP，不扩预算。正常小包装问题在此未来合同内有界解决，科学输入/算法/质量变化不得静默改。

**预冻结 STOP/反证**：
1. 官方 HDF5 获取权/bytes/SHA/字段或与cosine GT一致性失败；release与109 driver/Python/SM89不兼容；图构建或序列化无法在预算内完成；或锁忙。
2. `SMALL`/AUTO路径被发行版合法性检查拒绝、实际planner回退/调整导致最终两臂同一或不可比；两者不能在校准上满足既定recall；报告集质量差异超0.005。
3. 同recall下AUTO不劣于显式臂，或差异落在配对不确定性/完整host时间误差内；这是强软件充分的负面结果。若显式臂优于AUTO但只因已知block/清表/重算选择，归普通软件改进，不申请硬件。
4. 真正的稳定剩余若只在局部kernel出现、完整结果可用时间不响应，或原路径的距离读、排序已解释差异，则停止state硬件解释；本次不自动加NCU、第二数据集、模拟器或RF/SMEM机制。

**独立样本与适用边界**：校准/报告query不重叠，图和base固定；GloVe发现不代表现代embedding/RAG或全部ANN算法。若以后提出通用检索硬件，Jasper、IVF-RaBitQ与独立现代embedding是另一次科学验证门，不属于这份4点草案。GPU执行需要用户另行明确批准预算并指定原Lane M STOP之后的独立worktree/lock；本 A45S 只交付可审合同。

## 3. 当前不足与 closeout

源审能够证明“值得申请一次小型**发现/否定**合同”的可追溯入口，不能证明同recall实际两臂都能达标、109可安装、实际GPU时间或硬件瓶颈。A33 CAGRA论文/旧CPU ANN榜单的数字不搬到4080；A43 Spira真实坐标/随机特征身份与原计时边界保留。软件包`v26.10.00` release源码与A33 `bc23`研究快照的 planner blob不同，未来以**实装版本**的完整配置、binary/version与日志为权威，不混版本读旧字节表。

本报告唯一输出 `docs/ai_workload_research/reviews/AI_ARCH_A45S_SPARSE_ANNS_ONE_PROBE_ADMISSION_174NEW_V1.md`（≤260行），仅本分支提交。提交后在远端 fetch-back 核 commit/tree/blob、报告 SHA256 和clean状态；Git文件不能稳定自含自己的commit hash，exact值在执行回执报告。**当前状态：`Q-A_SELECTED_CONDITIONAL_PROBE_PROPOSAL / NO_GPU_AUTHORIZATION`；若未来任何首门失败则`NONE_SELECTED/NO_GO`，STOP。**
