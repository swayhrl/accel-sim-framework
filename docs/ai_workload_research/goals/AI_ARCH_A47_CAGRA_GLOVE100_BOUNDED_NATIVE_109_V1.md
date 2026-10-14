# Round A47｜GloVe100／cuVS CAGRA：有界真实GPU发现连续Goal

**执行者：node109 Codex，可复用已STOP的Lane M窗口，但必须新建独立worktree。**
**授权：** 用户在A46明确提出单RTX4080、4正式点、最多12配置检查、GPU累计持锁≤45分钟、总下载≤6GiB（数据≤0.6GiB）、新盘≤12GiB、CPU≤4 workers、RAM≤8GiB、GPU显存≤12GiB后回复“做吧”。以上本次具体额度与下面G0→G4现已授权；不需要逐门再次询问。**发布本文件不表示节点已经执行。**

Repository：`swayhrl/accel-sim-framework`。
独立branch：`hrl/aiarch-a47-cagra-glove100-native-109-v1`。
协调parent：`e4bf84ff414c84576bd7dc1078d145910617b0f6`；**启动以用户提供的、含本Goal的最终发布commit为准，不回退到parent。**
建议私有输出根：`/data/c16/aiarch_a47_cagra_glove100_109_v1`；同名目录若已有本任务有效记录先核身份，不删除、覆盖或归零。旧A26GR1/A45H/A45S/C16/AWMA状态和资产保持只读。

## 0. 科学问题与唯一输出

**Q-A47：** 同一真实GloVe向量图和recall要求下，官方CAGRA AUTO与一条校准后的SINGLE_CTA+SMALL路径，在B=1和B=256时是否有稳定的完整search时间差？差异首先解释为现有软件的算法／历史保留／线程块选择，不直接宣称物理SMEM、Cache或硬件headroom。

最终仅四个正式点：两个batch×两条路径。功能与校准配置检查最多8项；合计≤12项。重复计时、同一索引加载和质量验证不算新配置，但全部消耗计入同一时间／资源账。无效、相同路径、AUTO充分和NO_GO都是有效科学终态。无论结果正负，完成必要证据后STOP，不自动追加第二数据集、NCU/NSYS/NVBit、模拟器、新机制或续Goal。

## 1. 固定研究入口（先读，不重做文献综述）

1. 本branch的`docs/ai_workload_research/COORDINATION_PROTOCOL.md`及`CURRENT_STATE.md`。旧导航“尚未授权”是A46时点；本文件记录用户随后对A47的明确授权，仅对本Goal有效。
2. `docs/ai_workload_research/reviews/AI_ARCH_A46_A45H_A45S_INDEPENDENT_SCIENTIFIC_REVIEW_2026-10-14_V1.md`。
3. A45S原报告在独立执行commit `e0236f9e34f25dc7c96d048b31754bcb74e05764`：`docs/ai_workload_research/reviews/AI_ARCH_A45S_SPARSE_ANNS_ONE_PROBE_ADMISSION_174NEW_V1.md`，报告blob `df46a84b7500defa52a4be7001f0adffcd5a9637`。只读fetch该文件，不merge其执行HEAD。
4. 已核发行源码：`NVIDIA/cuvs@24ee1bf1cb17cad0ac611e39643af39ee1870124`（A46的v26.10.00入口），`python/cuvs/cuvs/neighbors/cagra/cagra.pyx` blob `27880c8dd63e1d59a53c7e0cfbcbc8aef2727ae7`；`cpp/src/neighbors/detail/cagra/search_plan.cuh` blob `da42f637dcd6fd1b299c425d353c77b3f1fe2f85`。目标Python发行`cuvs-cu12==26.10.0`；实际wheel、native依赖、Python/driver兼容与上述来源的对应在G0/G2现场确认，不把源码存在当发行包已经安装。
5. 数据入口：`erikbern/ann-benchmarks@2e081ad32c1eccab72dcb739ad886c310b90f715/README.md`中`GloVe-100-angular`，作者链接`http://ann-benchmarks.com/glove-100-angular.hdf5`，优先同一作者站点的HTTPS/可溯源官方重定向。数据说明：1,183,514条100维base、10,000条query、top100 GT，标称463MB；真实bytes/SHA/字段/许可待G1。不是现代生产RAG请求。
6. 官方安装指引`https://docs.nvidia.com/cuvs/installation/python`可指导CUDA12包获取；在线文档不覆盖本次冻结发行源码。不要因控制端某次网页抓取失败就断言版本不存在。

## 2. 资源、隔离与安全硬边界

| 项目 | 本次累计硬上限 |
|---|---|
| GPU | node109单RTX4080；不得改用其它卡或节点 |
| GPU共享锁持有时间 | ≤2700秒，包含设备canary、必要运行库JIT、唯一完整构图、保存／加载、质量与全部计时、失败尝试；预留退出／释放裕量 |
| 总实际下载 | ≤6GiB，所有重复／中断字节、wheel、runtime、Python及数据均计入；其中科学数据≤0.6GiB |
| 新增磁盘 | ≤12GiB，独立worktree、env、wheel/cache/tmp、数据、索引、日志全部计入；不得清理旧资产来腾空间；维持同文件系统空闲≥64GiB |
| Host | CPU≤4有效workers，OMP／BLAS等也限额；任务进程树RSS≤8GiB，禁止以swap规避；准备阶段自身主动执行≤2小时作为收口上限，不是预计耗时 |
| GPU memory | 本任务GPU进程总显存≤12GiB，含上下文／库／临时量；pool设置留上下文裕量，并独立采样，不能只核输入向量大小 |
| 科研输出 | raw／summary≤64MiB；大HDF5、索引和环境只留109私有任务目录，不入Git、不复制164 |

**复用原共享锁，不发明新锁：** 已冻结M执行器使用`/data/c16/locks/c16_gpu_campaign.lock`，来源为`cf80f6ec.../tools/aiarch_a26gr1/verified_late_native_supervisor.py`。父监督进程持有`flock(LOCK_EX|LOCK_NB)`直到自身所有GPU子进程结束。锁忙即`GPU_LOCK_DEFERRED/STOP`，不抢占、不轮询等空闲、不kill其它任务。锁文件缺失/归属不清也不能另建一个同名替代锁绕过协调。

G0只读CPU环境和NVML/nvidia-smi元数据检查可在锁前完成；任何可能初始化CUDA context的cuVS/CuPy导入、设备数组、执行、runtime JIT都在锁内。检查其它GPU用户，锁空闲但发现外部任务也不能并发测时。不得变更驱动、系统CUDA、GPU时钟／功率／持久模式、系统服务、其它用户进程或旧环境。只记录频率／温度／负载，不主动锁频。所有计时期间关闭本任务的并行下载和重CPU准备。

允许两条CPU准备支路在同一监督与总额度内并行：发行依赖元数据／独立环境准备，以及唯一数据下载／HDF5检查。正式GPU测量串行，不能以提高效率为由同卡多臂并测。

## 3. G0｜发行与资源闭包，随后连续执行

确认实际node109、旧M/H已经STOP、当前CPU/RAM/磁盘余量；新建独立worktree，不在旧STOP目录checkout/reset。日志与下载账从首次动作起累加，失败重试不归零。

优先用已存在的兼容Python≥3.11创建新venv，不使用或修改旧Torch2.2/IPEX环境。若需Python，仅允许官方可验证的小型发行，在总下载／盘／CPU预算内取得；不能变成漫长的源码工具链建设。按官方PyPI／NVIDIA源解析cuVS CUDA12 26.10.0的完整依赖、wheel平台、Requires-Python、SHA256及大小，固定resolved lock后获取／安装到本任务环境。只用所需NumPy/h5py/CuPy/cuVS及依赖，不安装完整ML框架或Docker整套artifact。

核心发行版本、dtype与算法不可静默更换；若目标实际不可用则保存检索证据、区分包装缺口与科学失败，STOP。缺一个机械wrapper、wheel下载重定向、同版本official包路径等问题可以在当前Goal内有界修复；不能仅因“下一门尚未运行”就写死STOP。若官方包需要正常runtime JIT，计入锁、时间与cache；不下载新源码重编整套cuVS。

## 4. G1｜唯一真实输入与预登记

下载前核来源、合理使用／许可、声明大小和累计预算，流式监控实际字节；有限续传必须绑定同一HTTP实体。无需发布方预先给SHA：完整取得后计算本地SHA并绑定来源/实体，这是本次数据身份，不冒充上游已认证SHA。不得镜像替换、随机张量、截小base或另换数据来挽救失败。HDF5读取拒绝未知外部链接／扩展代码，不执行文件内内容。

验证字段、shape、dtype、ID范围、finite、zero-norm、query/GT数量。使用全部原base，FP32、非压缩，保留cosine定义；仅允许同一cosine语义下有记录的规范化，不转FP16或更换GT。按发布者GT的tie规则计recall并注明容差；不能事后改tie规则提高结果。

**预登记查询身份：** 对索引i=0..9999计算SHA256(UTF8(`20261014:`+十进制i))并排序，前2000用于校准及canary，其余8000仅用于最终报告。report排序前2048个不同查询为固定计时集合，写出索引清单与SHA。校准与报告无交集；同一2048集合以B1和B256分批，不能复制一条query冒充并发。

完整recall评估必须按被测B和相同`max_queries`调用；不能将8000查询一次AUTO调用所得recall冒充B1路径。B256尾批不足256时，可用未在该批出现的真实report query补齐，并只对原尾批query计质量，不新增人工向量，不用于计时。索引与图不使用query/GT构建。

## 5. G2｜唯一完整构图、索引重载与功能canary

锁内先核设备/driver/runtime与加载库身份，再将全部base装入GPU。唯一完整构图：`metric="cosine"`、`build_algo="ivf_pq"`、`graph_degree=64`、`intermediate_graph_degree=128`；保持非压缩FP32搜索数据。记录所有有效build参数／库默认种子；API不暴露种子时明确UNKNOWN，不假造random_state参数。**只构图一次，之后同一序列化索引复用，避免把构图非确定性带入A/B。** 必要的小型API fixture不作科学数据或第二张正式图。

按冻结接口完成真实save/load及数据寿命检查：保存`include_dataset=True`时，用预创建Index和Dataset调用`load(index,filename,out_dataset=dataset)`并保持owner存活；若合法采用graph-only序列化，则必须用原完整FP32 base显式`update_dataset`。不得用旧版`load(filename)`伪接口；序列化格式只在同一发行复用。保存index文件SHA与graph身份（可读取数组时另hash；不可读时明确序列化SHA覆盖的范围，不伪造graph blob）。重新加载后以同一canary验证结果/距离，禁止为不同臂重新构图。

用校准集固定32条query验证输出ID合法、同query结果无重复、distance有限、与原GT/cosine定义一致。可在CPU分块对这些query与**完整base**计算精确参考；内存／线程总额度不变。只对返回ID重算距离不足以验证top-k，局部base真值不能与全图ANN混用。FP32距离绝对/相对容限在首次结果前登记，默认atol=1e-5、rtol=1e-4；边界ties说明，不降低recall门。canary证明功能与距离身份，不把小样本recall当总体质量。

## 6. G3｜有限校准、同质量与四点计时

### 6.1 固定搜索合同

共同设置：`k=10, itopk_size=128, search_width=1, max_iterations=64, min_iterations=0, hashmap_max_fill_rate=0.5, persistent=False`，无filter；`num_random_samplings=1, rand_xor_mask=0x128394`。按B显式设置`max_queries=B`，team_size用同一发行descriptor合法默认并记录。现有planner如规范化迭代上限，保存request/effective值，不误称指定数值已经严格运行；正常不同算法内部工作差异不是函数错误。

| 臂 | 设置 |
|---|---|
| A | `algo="auto", hashmap_mode="auto", thread_block_size=0`，官方启发式reference，不声称全参数最优 |
| B | `algo="single_cta", hashmap_mode="small", thread_block_size=128`；h只可从`hashmap_min_bitlen={9,11}`校准择一 |

B=1、256各测A、B。校准最多6个既定候选配置（2batch×AUTO/h9/h11），加最多2个功能配置检查，总≤8项；正式四点后总≤12。**同一个h用于两种batch**：候选h须在两个batch的校准query上均满足recall≥0.95且与同batch A相差≤0.005，再按两batch完整host边界每query耗时的几何平均最小选一个；tie取h9。随后冻结h、参数、stream/allocator和query顺序，不看report结果再调。不可扫其它h/itopk、提高迭代合同、降低recall或新增路径来找正例。

正式report集8000条query上，每臂每batch要求recall@10≥0.95，同batch A/B差异≤0.005（绝对值）。失败即`QUALITY_NO_GO`，原结果保存，不再调参；这不等于领域没有研究价值。若A/B有效路径完全一致，记为`EFFECTIVE_PATHS_IDENTICAL`的有意义负例，不用重调制造差异。

记录resolved算法、hash类型/bitlen、reset、block/team和实际batch。优先使用现成日志/API；仅从固定源＋输入可推导的字段标`SOURCE_DERIVED`，不是`DEVICE_OBSERVED`。缺距离计算数／迭代数等扩展telemetry允许UNKNOWN，**不为它们先建tracer或否定有效wall测量**。

### 6.2 计时与比较

每个测量进程均加载同一已保存index，不构图。三fresh processes顺序运行，先warmup，再对四点进行10个预登记ABBA配对块；反序安排部分块以控制漂移。每个A/B测量使用相同2048条不同query，按目标B分批；输出保留process/block/order和原始值。所有臂全部完成不得越过累计2700秒。

分别记录：(a)query已经在GPU时的search服务时间，包含其内部visited/reset/sort，不含H2D/D2H；(b)CPU query已就绪→H2D→search→D2H→CPU结果可用的未插桩host wall。不得省略完成同步；不得误把异步函数返回当结果完成。原生CUDA events仅在已核stream覆盖全部search依赖时作为GPU计时，否则如实降级为同步完成的host search时间，不冒称纯kernel；cuVS装饰器可能自动同步，必须按实际版本核对。正式外层计时不新增内部region profiler；不把(a)+(b)相加。

两臂预分配相同形态的输出/transfer buffer、使用同一合法pool及host buffer策略，保持必要dataset owner；构图、env、加载、首次JIT、warmup和校准耗时分别报告，不偷移出累计预算。记录原有设备频率／温度／背景负载；不写系统锁频命令。出现外部负载污染即保留样本标记并有界STOP，不杀他人进程。

报告每batch wall、每query摊销成本及吞吐，B256的batch wall/256不得伪装成单请求响应延迟或线上SLO。先给三进程逐进程配对效应与离散度；需要bootstrap只对进程/配对块分层重采样，不把同一进程中数千query误当独立重复。不删慢样本来美化结果。

## 7. G4｜科学判断、归档、发布后STOP

只在质量／身份／时间边界成立时比较性能。AUTO不劣、差异不稳定或有效路径相同，接受强软件充分的负面结果；SMALL胜AUTO首先归为既有软件启发式／状态策略差异，不能直接推SMEM容量或硬件收益。只有存在待解释的完整时间差才给一个后续定位建议，**本Goal仍STOP，不自动实施**。

规范终态任选实际符合者：`COMPLETE_SCOPED_NATIVE_NO_GAP`、`COMPLETE_SOFTWARE_CONFIGURATION_GAP_ONLY`、`COMPLETE_UNEXPLAINED_SEARCH_DIFFERENCE`、`QUALITY_NO_GO`、`PLATFORM_OR_ASSET_NO_GO`、`BUDGET_STOP`、`GPU_LOCK_DEFERRED`。工程NO_GO、质量不达标、软件负例与机制结论分开。未通过门的后续字段写NOT_RUN，不能伪造PASS；只有实际门失败或不再有安全合法执行路径才停止。

报告目录：`docs/ai_workload_research/runs/AI_ARCH_A47_CAGRA_GLOVE100_109_V1/`，至少含`FINAL_REPORT.md`、`GATES.json`、`RUN_IDENTITY.json`、`ENV_LOCK.json`、`DATA_AND_INDEX_IDENTITY.json`、`PREREGISTRATION.json`、质量与逐次计时、`RESOURCE_RECEIPT.json`和校验清单。必要小脚本限`tools/aiarch_a47/`。不要commit环境、HDF5或大index，不修改协调CURRENT_STATE或旧报告，不merge其它执行HEAD。

退出前确保本任务GPU子进程已结束，再释放同一campaign锁；异常同样释放并保留已产生数据。一次commit/push/fetch-back核对exact commit/tree/新增blob/SHA及clean，再向用户报告结果与STOP。HTTPS传输故障可使用已认证GitHub SSH做相同分支推送，不改权限或凭据，不泄露token。不得重置已耗预算、无限重试或后台续跑。

**普通包装问题同Goal有界solve-and-continue；科学输入／精度／算法／资源上限变化则停止。不得把CPU/版本准备PASS后“尚未验证GPU”当拒绝尝试已授权G2/G3的理由。**
