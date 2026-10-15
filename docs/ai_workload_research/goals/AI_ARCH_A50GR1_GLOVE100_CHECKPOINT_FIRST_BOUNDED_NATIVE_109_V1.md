# AI-ARCH A50GR1｜真实GloVe CAGRA checkpoint-first恢复及四点原生发现（单次连续Goal）

**授权状态：APPROVED_STANDING_USER_CONFIRMATION_FOR_EXACT_BOUNDED_SCOPE / READY_FOR_CODEX；未执行。** 用户在2026-10-15明确“后续我默认确认，你可以一并给出。有意见我会说”，本次A50G执行者提出的最小修复后再完整构图已在Round A56独立审查收敛，**科学对象、平台、模型/数据/数值、默认Resources、质量门和原45min/2GiB/12GiB等资源硬上限不扩大**。因此此明确的单次修复闭环使用该默认确认；如果用户对该具体范围提出异议，执行者应以用户最新指令为准停机。**授权只限本Goal一次全base构图＋一个小型工程烟测，不允许连续扩权、多个真实full build或自动下一GPU Goal。发布/批准不意味着109 Codex已经启动。**

- Repo：`swayhrl/accel-sim-framework`
- Branch：`hrl/aiarch-a50gr1-glove100-checkpointed-native-109-v1`
- 起点：协调提交`6912dc7dc779f88a7a0d30355d3cc396822aa9ea`，**实际启动SHA采用含本Goal文件的提交HEAD**，不回退、不merge历史实验HEAD。
- node109：可复用已STOP的Lane M Codex聊天，但必须新建独立worktree/output/tmp、独立预算；旧A47/A47R1/A47R2/A50G worktrees、旧raw、manifest、source、缓存和锁都只读。
- 上一轮科学执行结束：`hrl/aiarch-a50g-glove100-default-native-full-109-v1@d74ba0225516e60aa1c18b7ee87c88abfc34e0c9`，其历史STOP和一次构图额度已消耗，不得声称从它继续运行未保存的GPU对象。
- 首先读`docs/ai_workload_research/CURRENT_STATE.md`、`COORDINATION_PROTOCOL.md`、[A56独立审查](https://github.com/swayhrl/accel-sim-framework/blob/6912dc7dc779f88a7a0d30355d3cc396822aa9ea/docs/ai_workload_research/reviews/AI_ARCH_A56_A50G_NATIVE_FULL_BUILD_WRAPPER_STOP_INDEPENDENT_REVIEW_2026-10-15_V1.md)；固定A50G `FINAL_REPORT.md`、`ENGINEERING_REPAIR.json`，以及**A47@ce92807ca80e1a694e41376eab3dd6b146824fd8下的`PREREGISTRATION.json`与`DATA_AND_INDEX_IDENTITY.json`**；对照A50G真正已执行`tools/aiarch_a50g/native_executed.py`、**仅CPU修复未运行**`tools/aiarch_a50g/native.py`，两者blob/SHA必须分开记录。冻结cuVS26.10`cagra.save`含dataset及`cagra.load(Index(),out_dataset=Dataset())`版本入口已有官方源码对应。

## 0. 唯一科学问题与提前STOP条件

沿原[A50G获批准科学合同](https://github.com/swayhrl/accel-sim-framework/blob/ea32eb190cf9697556f3560263b7a637563c69e7/docs/ai_workload_research/goals/AI_ARCH_A50G_GLOVE100_CAGRA_DEFAULT_FULL_NATIVE_109_V1.md)不变：

**Q-A50GR1：** 同一官方完整GloVe-100-angular base`1,183,514×100 FP32`、同一个实在GPU中构出的CAGRA index并永久绑定其serialized SHA、真实查询同recall≥0.95条件下，`B1/B256 × AUTO/校准SINGLE_CTA+SMALL`是否出现稳定的端到端完整search wall差异？

之前A50G全图API PASS但被`np.frombuffer(pinned)`对齐reshape错误中断；修正包装不是新科学机制。**新增工程顺序只为防止单次full build之后继续因包装错误丢索引**，不准重新定义原图、输入精度/GT、检索参数、GPU物理资源或测量分母以挽救负结果。

合法STOP：
- G0/G1小型烟测未能资格化→`WRAPPER_OR_SAVELOAD_PREQUAL_NO_GO`，**不调用任何真实full-base构图**；
- 原完整GloVe一次build异常/字段错/显存或时间越界→`NATIVE_BUILD_NO_GO`，后续全部NOT_RUN；
- 完整build字段PASS但立即save失败/无合法serialized checkpoint→`CHECKPOINT_NO_GO`，后续STOP且**不得第二次full build**；
- checkpoint存在但load/owner/32个真实query数值失败→`RELOAD_OR_NUMERIC_NO_GO`；真实recall或同batch差异不满足原阈值→`QUALITY_NO_GO`；
- 四点存在并同质量：`COMPLETE_SCOPED_NATIVE_NO_GAP`或`COMPLETE_SCOPED_SOFTWARE_CONFIGURATION_GAP`；差异归因仍不充分则`COMPLETE_UNEXPLAINED_SEARCH_DIFFERENCE`（不是硬件创新）。
所有STOP保留原始证据、真实统计和未执行字段，不重启已耗尽的build额度。

## 1. 节点与资源：同额度新独立总账

| 资源 | 单次累计硬限 |
|---|---|
| GPU/锁 | node109单RTX4080，既有`/data/c16/locks/c16_gpu_campaign.lock`非阻塞`flock(LOCK_EX | LOCK_NB)`；**≤2700秒/45分钟**，包含小烟测、一次完整构图、save/load、校准、四点和可合法load-only工程修复 |
| 下载/安装/升级 | **0**；只读沿用A47已验证`Python3.12.3/cuVS/RMM26.10.0/CuPy14.0.1`、env/HDF5/base/query/GT；不重配驱动/CUDA、核心库、不编译/搬迁依赖 |
| 新文件与空间 | 本次单独worktree、私有cache/tmp、最多一个真实serialized index、raw合计**≤2GiB**，所在FS余量始终≥64GiB；小测试文件同一预算计数 |
| Host/GPU内存 | ≤4有效CPU workers，任务进程树RSS≤8GiB，任务GPU显存≤12GiB，必须监控且为NVML短峰留裕量 |
| 准备/日志 | CPU准备≤30分钟；`raw/summary≤64MiB`，不提交超过小文本限制的科学data/index |
| 构图与调参 | `1024×100 synthetic tiny smoke最多一次CAGRA build`（纯工程API资格）**加**`真实原1,183,514×100完整base build最多一次`；≤8个资格/校准配置点＋4正式点；绝不多次full build或改h范围 |

这是一笔**全新的、独立45min累计预算**，不能把A50G历史已消费3.959s或“剩余时间”混到本次账，也不能因为早前成功就无条件占满45min。只有父监督进程非阻塞取得原锁，确认无其它GPU作业才开始所有GPU初始化；锁忙立即DEFER，**不轮询、不kill别人的进程、不触碰C16/AWMA锁以外资产**。所有自己的GPU子进程结束后释放原锁，异常也应清理；禁止影响他人跑作业。GPU计时阶段停止本任务CPU/I/O后台负载。随机短时峰不可由NVML样本精确上界，靠小工作量、保守裕量和watchdog共同约束。不可改功率/时钟。

**旧数据：** 只读`/data/c16/aiarch_a47_cagra_glove100_109_v1`与旧A50G ref。新私有输出建议`/data/c16/aiarch_a50gr1_glove100_checkpointed_109_v1`；若已存在先核owner/identity，禁清空或覆盖别的任务。

## 2. G0｜在锁外完成确定性CPU修补审查，不消耗唯一大图

1. 仅CPU核身份和来源：旧GloVe官方HDF5`485413888B`/SHA256`544af1d5e84e112cd4749571dcfd8ca109818a572f850af75a3a09e093a953c4`，base`1183514×100FP32`、原query/GT与pre-reg hash`split=0fb3e14cd9b4b9c97397235c5dddcd73b1a53bb5979b04ac5e3762f8c559c650`、timing`f7ebf0825b6ba7e351df18c20f8e0cb559b37fdbf0775142d989161df7baafea`。禁止变更GT tie、input normalization、dtype、算法或查询分组。核旧env/已接受报告与所有必需源hash；原A50G终态独立封存。
2. 只在新branch引用并隔离已接受的`native.py`修正版作候选，**不得执行旧`native_executed.py`**。做static AST/compile、NumPy纯CPU测试与必要的固定shape fixture：检查`Buffers(1/256)`的pinned/view字节数、`np.frombuffer(...,count=...)`长度、array strides/C-contiguous、三种query/uint32 ID/float32 distance字段，以及校准1792和正式2048 pinned view的`count`。用人为512B等round-up byte buffer复现旧B1问题，证明新代码不会错误取得128个elements。事前核`save(index, include_dataset=True)`在**任何**下游`Buffers/evaluate/quality`之前，索引文件路径预算、owner与`cagra.load(Index, filename, out_dataset=Dataset, Resources)`的正确参数及生命周期。
3. CPU静态预演合成小图、构图后save-first/checkpoint状态机和后续load-only路径的阶段及异常分支；至少检查※`完全不存在二次full build path/隐式create_index fallback`，※已落盘index SHA作为后续操作唯一输入，※配对计时只在质量门PASS才触发。元数据包装错误（None.module、dtype、npz shape、数组长度）在锁外自测完成，不能把它升级成科学输入缺失。
4. 如实记录CPU-only验证条件/未覆盖GPU API。先不称GPU PASS。GPU锁外不import/运行可能初始化CUDA context的CuPy/cuVS调用。

## 3. G1｜GPU小烟测必须先通过，才可实际一次完整build

取得原GPU锁并开始**统一总账**后，先运行一个或两个独立小型engineering child（可按科学依赖合并）：

**S1｜真实CuPy pinned/transfer检查**：在该freeze env、默认`Resources()`/CuPy默认stream下实际分配`Buffers(1)`和`Buffers(256)`、校准1792和timing2048的host pinned数据视图；验证请求bytes、实际暴露bytes、通过`count`得到的shape/stride/dtype、元素隔离、H2D/D2H roundtrip。无需读取完整GloVe、无search index。**GPU断言/包装不通过→停止，不消耗唯一大图。**

**S2｜tiny API完整链**：只做一次冻结seed20261014、1024×100FP32合成合法数据的默认`Resources()` CAGRA cosine/IVF-PQ degree64/128构图；数值属性/同步PASS后立刻`cagra.save(include_dataset=True)`到**小型临时index**并SHA/hash→新建`cagra.Index()`与`Dataset()`再`cagra.load(...,out_dataset=owner, resources=res)`；验证owner/type/size/dim/degree/dtype，与B1/B256合法`cagra.search`结果ID范围、无重复、有限distance，按返回ID的FP64合成向量算distance做基本数值核对（只是tiny API smoke，不要求tiny recall≥.95、不能冒充真实GloVe质量）。**此tiny构图不占完整真实base的一次额度，但计入GPU锁、新盘和全部进程预算。** 如果save/load/搜索API失败，合法`SMOKE_NO_GO`直接STOP，不替换后端或改CUDA版本。公开Graph-view DLPack转换是非必需项，已知失败的可选诊断不应阻碍S1/S2科学核心资格。
**省工程时间原则**：真实packed/index API小烟测完全合格后在**同一个已授权Goal**直接G2，勿因“还没资格测真实大图”另开Goal或另问确认。

## 4. G2｜一次真实完整base构图，先save/hash再运行所有查询

保持原资源/driver/26.10版本、冻结`1,183,514×100FP32`真实单位向量、cosine/IVF-PQ`degree64/intermediate128`及同默认Resources，无非默认Stream或显式RMM pool。调用唯一`cagra.build`并完整同步，逐字段记录`trained==True,size=1183514,dim=100,degree=64,np.dtype(dtype)==float32`，任一失败STOP。旧首次attach维度0 warning不得被误判为最终index错误。

**强制持久化顺序（优先于一切buffer/quality调用）**：
1. full build五字段PASS立即（除了必要资源卫兵）使用官方`cagra.save(path, index, include_dataset=True, resources=res)`，完成`res.sync()+deviceSynchronize()`；用任务私有路径和合法临时文件名避免留下假完成文件；记录`bytes/SHA256/index_version/input_id`并**在原索引仍存在时**将已完成checkpoint标志原子落盘；新盘/文件系统余量全程监控。不存在checkpoint不得转入下一阶段；save失败虽已构图PASS也应`CHECKPOINT_NO_GO`而非换后端/重复full build。
2. 在另一个**fresh GPU子进程**只使用`cagra.Index()`/`Dataset()`从此文件load，保持owner，验证重载元数据5字段以及其32条真实全base oracle canary；可在build原live进程保存后有限测试，若能合法保留其查询结果，再与重载做ID/距离对照。不把图公开DLPack无法转换当必需门，只绑定可审的serialized bytes SHA和同source/object owner。
3. 从该时刻**禁止再次完整构图**：若后续buffer/log/CLI/manifest是确定性的可修包装，可在原Goal累计≤45min GPU锁内至多两次surgical repair＋fresh process **load-only**恢复，修复前后保存script SHA、raw fail及数值/参数身份。真实GPU数值、recall/quality、意外native SIGSEGV、身份/参数/版本变化不属于包装，必须STOP。新恢复不覆盖第一个失败原始收据，也不重置lock/disk/time预算；若无法合法原位修复，保留checkpoint与STOP供独立审查。

## 5. G3｜数值、同recall校准和四点未插桩真实时间

**完全复用A47/A50G冻结科学合同**：
- GloVe原`2000 calibration`与`8000 report`集合不交叉、正式`2048 distinct report timing queries`不替换；`k=10,itopk=128,search_width=1,max_iterations=64,min_iterations=0,hashmap_max_fill_rate=.5,persistent=False,seed/mask原值`均固定；`B1/B256`。算法路径`AUTO algo=auto/hashmap_mode=auto`，`SINGLE_CTA+SMALL algo=single_cta/hashmap_mode=small/hash min bitlen∈{9,11}`，其它block等原值，不临时多试h/iters。
- 32条实际GPU canary的returned IDs/距离应可审核，与**原1,183,514×100完整base精确CPU oracle/GT tie**匹配（距离`atol=1e-5,rtol=1e-4`），不只算返回的ID局部距离就称exact topk；完整search结果可能近似，不要求每个返回ID必须是exact top10，但必须按冻结recall门。
- 最多`6`个功能/校准格：B∈{1,256}×AUTO/h9/h11，另最多2项functional canary。2000 calibration query每batch的AUTO和合格SMALL`recall@10≥.95`，同batch绝对差`≤.005`；合法h9或11由两batch`完整host wall/query`几何平均选择**同一个h**，report前冻结，不能窥report挑h/调参。若都不合法则`QUALITY_NO_GO`、正式NOT_RUN，不放宽标准。
- 使用8000真实report query逐batch/两路径重新验证四个配置recall≥.95及差≤.005，B1必须按单query测试而非用B256计quality；合法batch尾巴只从其他真实query填充，计数只含有效元素。没有报告recall就不能继续计时。
- 四点只有B1/B256 × AUTO/已校准SMALL。三fresh process仅load同一serialized index SHA，按原预登记10`ABBA/BAAB`配对block并以2048真实不同report query执行；所有样本、warmup、背景和时间原样保留。**计时双分母分开**：GPU-resident查询`synchronized host service`（包含Python/调用/同步，绝不是GPU-only kernel），以及CPU-ready→H2D→search→D2H/CPU结果ready`完整host wall`；不可相加，也不可把B256均摊值当单请求在线latency。计时期间停止本任务其它重负载，保留三进程分层/配对差异与尾部。
- 比较首要含义：`AUTO`是官方软件启发式，不是全参数最优；SMALL赢AUTO首先表明已有软件搜索资源/哈希与线程块选择，不直接变成SMEM/Cache硬件新意。AUTO足够或差不稳即合法负结果`SCOPED_NO_GAP`并STOP；两路径有效算法相同也承认`EFFECTIVE_PATHS_IDENTICAL`，不编造不同物理状态。

## 6. G4｜一份完整报告、失败收据、下一阶段分岔与硬STOP

唯一新输出：`docs/ai_workload_research/runs/AI_ARCH_A50GR1_GLOVE100_CHECKPOINTED_109_V1/`（`FINAL_REPORT.md,GATES.json,PRECHECK_AND_TINY_SMOKE.json,ENV_AND_INPUT_IDENTITY.json,INDEX_SERIALIZATION_RECEIPT.json,QUALITY_AND_TIMING.json,RESOURCE_RECEIPT.json,SHA256SUMS`＋小raw），执行代码限`tools/aiarch_a50gr1/`。不要将HDF5、venv或真实full serialized index大二进制推Git/164；保存index在node109原新task私有路径，报告精确SHA/bytes。必须清楚区分`SMOKE_SYNTHETIC_API`、`FULL_GLOVE_NATIVE_BUILD`、`FULL_GLOVE_QUALITY`和`FOUR_POINT_NATIVE_PERFORMANCE`证据等级。

终态根据实际出现选择`GPU_LOCK_DEFERRED,ASSET_OR_PLATFORM_NO_GO,WRAPPER_OR_SAVELOAD_PREQUAL_NO_GO,NATIVE_FULL_BUILD_NO_GO,CHECKPOINT_NO_GO,LOAD_ONLY_WRAPPER_STOP,INDEX_RELOAD_OR_NUMERIC_NO_GO,QUALITY_NO_GO,BUDGET_STOP,COMPLETE_SCOPED_NATIVE_NO_GAP,COMPLETE_SCOPED_SOFTWARE_CONFIGURATION_GAP,COMPLETE_UNEXPLAINED_SEARCH_DIFFERENCE`。失败后后续门`NOT_RUN`，不可填PASS。完成Git commit/push/fetch-back核对exact SHA/tree/all new blob与checksum、清理**自己**GPU子进程/释放共享锁/工作区clean，然后`STOP`。不用为每个工程门另开Goal或请求批准。

**下一科研动作同报告一次给出**：若full真实index/save/load/recall均PASS，且无有效软件残差则`Q-A强软件充分/暂退役`；若在同recall下有稳定完整wall差也只能提出一项**单独有界物理资源定位**并列强软件反证，不得自动开展NCU/NSYS/NVBit/Accel-Sim/RTL或新Cache机制；若这次再因wrapper/vendor路径无效而未获得真实index或quality，**停止在当前cuVS26.10/109上不断重建原base**，将主精力交回Q-V/GNN及A43 Q-S discovery。所有历史run/authority、C16和AWMA保持冻结。

本Goal无论成功/失败都不能自行启动A50GR2或修改冻结的科学主线。