# A50G｜GloVe100/CAGRA 默认资源完整原生发现：单次连续Goal

**状态：PREPARED_AWAITING_EXPLICIT_USER_GPU_APPROVAL / DO_NOT_LAUNCH_YET。** 本文件与A50审查同时提前发布，不构成新GPU授权。只有用户之后明确批准本文件全部上限并把“已批准执行A50G”的指令发给109 Codex，才允许G0→G4一次连续执行；此发布时标签是历史准备状态，不覆盖未来用户明确指令。未经新批准，Codex只能只读本Goal，不得启动本任务。

Repository：`swayhrl/accel-sim-framework`。独立branch：`hrl/aiarch-a50g-glove100-default-native-full-109-v1`。协调起点：`9cd8597066a2ba6e3890e6978861dc75eeab06b5`；启动时应以包含本Goal的实际完整发布HEAD为准，不回退parent。node109使用**新worktree/输出/预算**；可复用已STOP的Lane M对话，旧A47/R1/R2资产仅只读。

## 0. 科学问题、authority和硬边界

**Q-A50G：** 固定同一真实GloVe-100-angular全部FP32向量、一次实际CAGRA图、同一查询与recall要求时，官方AUTO与已在校准查询上选定的SINGLE_CTA+SMALL，在B1、B256上是否留下稳定的**完整search wall**差别？差异如有，首先按已有软件调度/hash/CTA策略解释；本Goal不证明硬件SMEM/Cache机会，不开发机制。

依次阅读：
1. 本branch `docs/ai_workload_research/CURRENT_STATE.md`、`COORDINATION_PROTOCOL.md`。
2. [A50独立审查@9cd85970](https://github.com/swayhrl/accel-sim-framework/blob/9cd8597066a2ba6e3890e6978861dc75eeab06b5/docs/ai_workload_research/reviews/AI_ARCH_A50_A47R2_DEFAULT_CAGRA_NATIVE_REVIEW_AND_ONE_GOAL_DECISION_2026-10-15_V1.md)。
3. [A47R2实际报告@c37bfa97](https://github.com/swayhrl/accel-sim-framework/blob/c37bfa976f556442f9a6856b899edb537b204875/docs/ai_workload_research/runs/AI_ARCH_A47R2_CAGRA_INDEX_FIELDS_STREAM_109_V1/FINAL_REPORT.md)与`tools/aiarch_a47r2/canary.py`；C0默认Resources真实tiny索引通过，C1显式非默认Stream初始化SIGSEGV，因此**全程仅用默认Resources/RMM/CuPy stream**。
4. [原A47真实输入及环境@ce92807c](https://github.com/swayhrl/accel-sim-framework/blob/ce92807ca80e1a694e41376eab3dd6b146824fd8/docs/ai_workload_research/runs/AI_ARCH_A47_CAGRA_GLOVE100_109_V1/FINAL_REPORT.md)，及该固定提交下`PREREGISTRATION.json`、`DATA_AND_INDEX_IDENTITY.json`、`ENV_LOCK.json`、`QUALITY_AND_TIMING.json`及`tools/aiarch_a47/native.py`。复用其冻结输入/查询/实验规则，**不直接执行未修正的旧native.py**。
5. cuVS官方固定`NVIDIA/cuvs@24ee1bf1cb17cad0ac611e39643af39ee1870124`，其`cagra.pyx`/`resources.pyx`/`cydlpack.pyx`。实际以旧A47 26.10官方wheel和本机lib SHA为ABI authority，不改发行版本。

## 1. 新批准前不得执行的资源额度

| 项目 | 拟议累计硬上限 |
|---|---|
| GPU | 109唯一RTX4080，原锁`/data/c16/locks/c16_gpu_campaign.lock`非阻塞`flock(LOCK_EX|LOCK_NB)`；包含canary、构图、JIT、save/load、校准、4点计时、失败/清理累计**≤2700秒（45分钟）** |
| 下载与安装 | **全部新增0**：不pip/conda、不更新驱动/CUDA/cuVS/RMM，不重新编译核心库 |
| 文件 | 新worktree/output/cache/index/raw总新增**≤2GiB**，维持同FS free≥64GiB，不清理旧资产 |
| CPU与内存 | 有效workers≤4，任务进程树RSS≤8GiB，CPU预准备≤30分钟 |
| GPU内存 | 任务显存≤12GiB，含context、IVF-PQ build scratch/临时分配，持续采样及预留余量 |
| 实验/提交 | **一遍完整原base构图调用**，≤8个功能/校准配置检查＋4个正式配置点；raw/summary≤64MiB |

锁忙/外部GPU任务/资源或身份不合即STOP，不轮询、不kill他人进程、不变更时钟和系统设置。GPU父supervisor先获得原锁并保持至所有**本任务**GPU子进程完成后释放；GPU操作仅锁内进行，正式计时停止本任务后台CPU/I/O负载。资源总账覆盖失败和重试，不能重置；短时显存采样可能漏峰，配合安全预算而非宣称精确最大值。

建议新私有output：`/data/c16/aiarch_a50g_glove100_default_full_109_v1`。只读旧A47 root：`/data/c16/aiarch_a47_cagra_glove100_109_v1`，包含冻结`venv`、原HDF5、`base_fp32_unit.npy`、`queries_fp32_unit.npy`、`gt_ids.npy`、`gt_distances.npy`、`preregistration.json`。输入和venv必须就地只读使用，不重复制大数据，不在旧目录创建cache/pyc；新HOME/TMP/XDG/CuPy/driver cache重定向任务私有路径。

## 2. G0｜锁外资源/科学输入/脚本预检，一次闭包

确认原A47/R1/R2已STOP且原文件SHA/mtime和工作区身份不变；核109驱动/设备、环境包身份及来源。原官方HDF5实际`485413888B`、SHA256 `544af1d5e84e112cd4749571dcfd8ca109818a572f850af75a3a09e093a953c4`；原base`1183514×100 FP32`、10k查询/top100 GT，使用历史合法FP32 cosine单位化文件。无原完整数据、安装或ABI变更即`ASSET_OR_PLATFORM_NO_GO`；不随机替代真实base。

必须沿用原A47冻结查询分组：`calibration_ids`=2000、`report_ids`=8000互斥，`timing_ids`=2048个不同report query；`split_sha256=0fb3e14cd9b4b9c97397235c5dddcd73b1a53bb5979b04ac5e3762f8c559c650`、`timing_ids_sha256=f7ebf0825b6ba7e351df18c20f8e0cb559b37fdbf0775142d989161df7baafea`。不重划/调换以获得更好结果。科学输入/metric/dtype/GT/正常化规则变更STOP。

在GPU前以CPU AST/compile和静态检查确认：所有运行阶段均不使用`cp.cuda.Stream(non_blocking=True)`、`PoolMemoryResource`、`rmm.mr.set_current_device_resource`、`cp.cuda.set_allocator`；CuPy与cuVS统一默认Stream和`res=Resources()`；A49修正的`np.dtype(idx.dtype)==np.dtype('float32')`有效，五个index属性必须独立记录而非合取短路。R2公开Graph视图通过DLPack曾失败，**不可将其作为必需门或为其新建转换框架**。`Resources()`显式传API时有些调用不自动sync，按实际CUDA依赖做`res.sync()+deviceSynchronize()`。普通包装问题在G0自行修好，不反复询问。

## 3. G1｜真实完整构图一次，save/load后数值资格

取得原锁且无人竞争后，默认CuPy stream把完整单位化FP32 base传入GPU；`res=Resources()`、`ds=make_device_padded_dataset(g,resources=res)`，g/ds/res及其数据owner全程保活。唯一实际完整构图：

`cagra.build(cagra.IndexParams(metric="cosine",build_algo="ivf_pq",graph_degree=64,intermediate_graph_degree=128),ds,resources=res)`。

一次API build即计入唯一许可，SIGSEGV/OOM/错误返回不得重试，后面NOT_RUN；训练好tiny C0不代表full已经合格。同步后独立记录`trained,size,dim,graph_degree,dtype_repr,dtype_normalized`并要求`True,1183514,100,64,float32`。首次dataset attach前`new dimension100 vs old0`警告本身不是失败。

**容量口径**：源FP32 base`473405600B`＋degree64×uint32图`302979584B`＝`776385184B≈740.42MiB`，这只是存储下界，**不是index序列化大小、构图临时VRAM或总运行峰值**；临近2GiB新增盘、12GiB VRAM和45分钟上限提前STOP，绝不超预算或再构图一次。

索引通过后`cagra.save(path,index,include_dataset=True,resources=res)`，同步，记录序列化字节+SHA；重载必须`idx2=cagra.Index(); owner=cagra.Dataset(); cagra.load(idx2,path,out_dataset=owner,resources=res)`，保持owner生命期，并核重载属性与相同32查询输出。若graph view经合法API不能读，标`GRAPH_LOGICAL_HASH_UNKNOWN`，仅宣称序列化SHA、owner和search结果身份；不可说逐元素graph hash已核。首次功能canary在32条校准query，返回ID合法/不重复、distance finite、与原**完整base**FP64 cosine精确参考的一致性（atol1e-5/rtol1e-4），使用原GT第10距离+0.001 tie门；仅核返回ID距离不等于完整top-k参考。数值或reload不合格STOP。

## 4. G2｜同recall门和限定校准

正式对照共同固定`k10,itopk_size128,search_width1,max_iterations64,min_iterations0,hashmap_max_fill_rate.5,persistent=False,num_random_samplings1,rand_xor_mask0x128394,team_size0,max_queries=B`。

路径A：`algo="auto",hashmap_mode="auto",thread_block_size=0`；路径B：`algo="single_cta",hashmap_mode="small",thread_block_size=128`，`hashmap_min_bitlen`仅可9/11。先至多6固定校准配置：B∈{1,256}×AUTO/h9/h11，另≤2功能canary，总≤8；不得加新的h、迭代数/itopk。校准2000查询上每B均要求两臂`recall@10≥0.95`且同B绝对差`≤0.005`，在可用h中选两B`完整host wall/query几何平均`最小的一个统一h，tie取9；选择后冻结，不参考report性能重调。

用剩余8000条独立report query逐B按该B真实`max_queries`校验四点recall≥0.95和同B差≤0.005，质量不达标立即`QUALITY_NO_GO`，不能降低阈值、换metric/GT、缩base/样本。尾批padding只能用其它真实query、质量统计只计有效条目；B1必须真实单query分批，不能用B256替代。记录AUTO实际有效single/multi CTA、SMALL/HASH/reset和block/team：Python传入只叫`REQUESTED`，从固定源码推导叫`SOURCE_DERIVED`，真正运行观测叫`DEVICE_OBSERVED`，缺内部迭代/距离数允许UNKNOWN，不为此先建tracer。

## 5. G3｜4正式点和未插桩真实wall

只有G0–G2均PASS且余预算足够才能进入。每次正式测量进程只加载同一个已保存index**不构图**，3fresh processes、先warmup，B1/B256各10个ABBA/BAAB配对blocks，2048个不同已冻结report query，保存所有原始进程/顺序/值/背景、不得剔除慢样本。

两个**不能相加**的计时边界：
- GPU已驻留query→完整同步`cagra.search`的`GPU-resident synchronized HOST service`，含软件/同步，不声称纯kernel。
- CPU已有query→H2D→search→D2H→CPU结果可用的**完整未插桩host wall**；两臂使用同类预分配buffer、全部操作default Stream、显式完成同步。build/save/load/JIT/warmup另列但计入累计资源账，不偷混入稳态search。

报告B1延迟、B256每批总耗时/吞吐以及`batch wall/256`（不冒称单请求在线p99），按3进程及配对block分层评估不确定性。AUTO是官方启发式非全参数最优；SMALL快首先判现有软件选择/历史状态组织差异，不直接宣称SMEM/Cache物理headroom；AUTO充分、差异不稳或全路径相同即合法负面STOP。

## 6. G4｜精确归档、独立Git与条件性下轮建议后STOP

只在本新执行branch新增`docs/ai_workload_research/runs/AI_ARCH_A50G_GLOVE100_CAGRA_DEFAULT_FULL_109_V1/`的`FINAL_REPORT.md,GATES.json,ENV_LOCK.json,DATA_AND_INDEX_IDENTITY.json,QUALITY_AND_TIMING.json,RESOURCE_RECEIPT.json,SHA256SUMS`和必要raw；小脚本仅`tools/aiarch_a50g/`。大HDF5、完整序列化index、venv绝不入Git或传164。保留所有负证据和NOT_RUN；当前所有A47/R1/R2 STOP、C16/AWMA、旧GPU worktree不改。父监督退出自身进程并释放原锁。

终态根据实际选择`GPU_LOCK_DEFERRED,ASSET_OR_PLATFORM_NO_GO,NATIVE_BUILD_NO_GO,INDEX_RELOAD_OR_NUMERIC_NO_GO,QUALITY_NO_GO,BUDGET_STOP,COMPLETE_SCOPED_NATIVE_NO_GAP,COMPLETE_SCOPED_SOFTWARE_CONFIGURATION_GAP,COMPLETE_UNEXPLAINED_SEARCH_DIFFERENCE`。普通工程问题同一Goal有界solve-and-continue；真实版本/输入/精度/资源改变必须STOP。报告结尾直接按证据给出**唯一最小下一步建议**，不能自动追加GPU、NCU/NSYS/NVBit、第二数据集、trace、Accel-Sim/RTL、新机制或新holdout。

完成一次commit/push，远端fetch-back核exact commit/tree/新增blob及SHA、worktree clean、锁释放，报告后STOP。不因任一阶段PASS再单独开Codex目标或重复请示，**也绝不把本Goal的准备文件当作运行授权**。