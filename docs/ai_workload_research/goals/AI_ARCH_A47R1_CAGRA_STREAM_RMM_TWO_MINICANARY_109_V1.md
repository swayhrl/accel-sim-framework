# Round A47R1｜cuVS CAGRA stream/RMM分配路径：最多两项小型原生canary

**执行者：109上的Codex新执行工作区，可复用已STOP的Lane M对话。** 科学状态由本Goal的实际结果决定，不能预写PASS。  
**明确授权来源：** A48提出只检查两个独立fresh-process的1024×100合成CAGRA IVF-PQ构图API、GPU共享锁累计不超过5分钟、无数据下载/驱动更动后，用户回复“好的，排查”。**本批准只覆盖这一次工程兼容性canary，不延续旧A47的完整GloVe构图、四点计时、质量检测或45分钟预算。**

- Repository：`swayhrl/accel-sim-framework`
- 独立branch：`hrl/aiarch-a47r1-cagra-stream-mr-minicanary-109-v1`
- 协调parent：`ebbb9f8e60a9b8a3afe6d644289f9f4eb70ebf8f`；实际启动严格使用包含本Goal的发布HEAD，不回退parent。
- 109既有A47完整STOP：`hrl/aiarch-a47-cagra-glove100-native-109-v1@ce92807ca80e1a694e41376eab3dd6b146824fd8`；本Goal读其source/env/GDB/receipts、**不修改**。
- A48独立审查：`docs/ai_workload_research/reviews/AI_ARCH_A48_A47_CAGRA_PLATFORM_NO_GO_STREAM_RESOURCE_AUDIT_2026-10-14_V1.md`（与协调`CURRENT_STATE.md`、`COORDINATION_PROTOCOL.md`先读）。原小fixture：`tools/aiarch_a47/api_fixture.py@ce92807…`，原GDB：`docs/ai_workload_research/runs/AI_ARCH_A47_CAGRA_GLOVE100_109_V1/raw/small_api_gdb.log@ce92807…`。
- 公开作者源码：`NVIDIA/cuvs@24ee1bf1cb17cad0ac611e39643af39ee1870124`的`python/cuvs/cuvs/common/resources.pyx`；`rapidsai/rmm@v26.10.00`的`cpp/include/rmm/mr/detail/stream_ordered_memory_resource.hpp`；读原文/ABI而不将源码等于本机执行状态。

## 0. 这次唯一科学／工程问题

**Q-R1：** 在固定109 RTX4080、原26.10官方wheel/驱动/运行时及**相同1024×100输入和CAGRA build语义**下，去掉A47使用的显式RMM池和非默认stream后，默认cuVS执行路径是否能合法完成小型构图？若默认成功，只把cuVS Resources关联的stream换成显式非默认CuPy stream，是否重新出现同类故障？

A47当时组合为：`PoolMemoryResource+set_current_device_resource+cp.cuda.set_allocator(rmm_cupy_allocator)` **以及** `CuPy(non_blocking=True) stream+Resources(stream=stream.ptr)`。这种同时改变多维度的旧失败，不能直接归因给单个变量。本R1最多观察两项：

| 代码路径 | C0（先运行） | C1（仅C0真正PASS后运行） |
|---|---|---|
| 同一固定Python/cuVS/cuPy发行、1024×100合法FP32合成向量、cosine、IVF-PQ、degree64/intermediate128 | 相同 | 相同 |
| RMM per-device资源/allocator | **官方默认**；不显式调用`rmm.mr.set_current_device_resource`、`PoolMemoryResource`或`cp.cuda.set_allocator` | **与C0完全相同**，不改变pool或allocator |
| cuVS Resources | `res=Resources()`，使用默认stream | `stream=cp.cuda.Stream(non_blocking=True); res=Resources(stream=stream.ptr)`，原Python stream对象保留至子进程结束 |
| 数据准备与归属 | 先在**默认CuPy stream**制作`g=cp.asarray(x)`，完整device同步；`ds=make_device_padded_dataset(g,resources=res)`，保留`x/g/ds/res`至构图/同步结束 | 与C0相同；只在`Resources`选择的stream不同 |
| API | `cagra.build(IndexParams(...),ds,resources=res)`，成功后`res.sync()`及必要设备同步 | 同左 |

**C0也显式传`Resources()`，避免把“是否使用resources参数/装饰器自动同步”偷偷变成第二个变量。** C0/C1为独立fresh process；同seed`20261014`、同形状/数据hash、同构图参数、相同初始化与计时外准备。不要为了C1通过让数据准备换成显式stream、改allocator或删除`make_device_padded_dataset`；那将破坏单变量解释。若版本接口不匹配，只允许符合冻结源码语义的最小包装修复并留记录；科学输入/ABI变化STOP。

**如果C0 SIGSEGV/failed，立即STOP，不试C1。若C0 PASS，C1至多实际调用一次。** 禁止重复崩溃的旧`显式pool＋非默认stream`配置；禁止“顺手”尝试更多memory resource、替换IVF-PQ构图后端、切换库版本或后续真实图构建。每个路径最多**一次**`cagra.build`，无自动崩溃重试。

## 1. G0｜只读身份及资源闭包（在GPU锁外）

1. 基于当前task branch建**独立worktree／输出／tmp**。旧A47`/data/c16/aiarch_a47_cagra_glove100_109_v1`与其venv/HDF5/ENV_LOCK全只读；核实际路径、核心文件SHA、旧STOP及109当前可用资源。**必须使用原A47隔离环境，不新建/安装/升级/修补包，不下载任何科学数据或依赖，不改系统驱动/CUDA/时钟/功率，也不清理旧资产。** 旧venv不可用／不一致即`FROZEN_ENV_MISSING_STOP`。
2. 先用CPU-only静态源码检查`Resources()`和`Resources(stream=stream.ptr)`签名与`make_device_padded_dataset`参数，核发行`cuVS-cu12/libcuvs-cu12/pylibraft-cu12/RMM 26.10.0`、Python3.12.3、CuPy14.0.1、冻结内嵌commit/已发布wheel SHA；必要时read-only检查`cudaStreamGetId`所处调用链和原GDB。CPU预检不得初始化CUDA context；GPU探测、device数组、CUDA／cuVS import可能初始化context的部分必须在原锁内。**不要求在锁外真正import+run GPU包证明入口**。
3. 确认109真实CPU/内存/磁盘余量和其它正式GPU任务；无许可竞争、容量足够才进入G1。旧GPU锁为**已存在**`/data/c16/locks/c16_gpu_campaign.lock`，不可另建锁替代。
4. 资源上限：**GPU共享锁累计≤300秒（包括初始化、两次canary、异常、清理）；CPU/母进程准备≤30分钟，CPU有效workers≤2，任务进程树RSS≤2GiB，GPU进程显存≤2GiB（包含context与临时量），新增output/worktree/tmp≤128MiB，全部新的数据/依赖下载为0**。余量不足或其它GPU任务繁忙则STOP，不以swap和额外磁盘挽救。保留FS空闲≥64GiB。显存瞬间峰值可能无法完全由NVML采样捕获，必须以小输入、不设大pool和有界监管共同约束，不伪称采样0等于真0。

## 2. G1｜独立fresh process两个有限原生canary

- 一个**父监督进程**先对原锁`flock(LOCK_EX|LOCK_NB)`，成功后才允许任何子进程导入并初始化CUDA；若锁忙`GPU_LOCK_DEFERRED/STOP`，不轮询、不kill其它用户进程。确认无旁路GPU作业干扰。父进程守护一条累计deadline、子进程组、RSS/VRAM、输出大小；子进程退出／SIGSEGV／timeout一律回收，再在finally释放锁。两条可合法运行的进程串行，不并发占GPU。
- 每条子进程中，官方`cupy`和`cuvs`冻结原版本，固定`os.environ`与numpy随机生成`1024×100 FP32`、归一化；不对全真实GloVe进行内存加载、上传或构图。数组摘要以正式build前记录且不改变输入来保证C0/C1相同。合法`IndexParams(metric="cosine",build_algo="ivf_pq",graph_degree=64,intermediate_graph_degree=128)`；输入合法，索引成功则核`trained/size/dim/graph_degree`和返回行为，不运行近邻search、recall或任何profiling。
- stdout/stderr实时flush关键阶段`IMPORT_PASS`、`GPU_INPUT_PASS`、`PADDED_DATASET_PASS`、`BUILD_ENTER`、`BUILD_PASS`、`CLEAN_EXIT`；由监督记录每条exit code/signal、构图次数、库/driver/runtime实际identity、cuda资源stream身份的合法可观测值、load/memory/lock receipt及原始日志。若只能记录Python资源请求状态，将字段标`REQUESTED_STREAM`，不冒称已看见C++内部faulting handle。
- **单变量**：C0默认RMM+默认stream；通过后才C1默认RMM+显式非默认CuPy stream。第二项若失败，A可用B失败，只支持`STREAM_CONFIGURATION_SENSITIVE_IN_FROZEN_ENV`，尚不能宣称驱动Bug/无效stream已证实；两项都PASS则旧带显式pool的组合或其交互仍是待查近邻；C0失败则默认路径也未合格。不要依照结果动态选择一个新的第三臂。
- 若C0和C1任何一个出现SIGSEGV，保留原始stderr/exit/timeout和轻量源解释即可。已有A47 GDB栈足够说明前序故障，不追加第三次GDB运行、改装库或启动新的构图重试。
- **无性能测量**：不得给API tiny canary计时填成真实应用性能，更不得推算GloVe118万base的构图/搜索耗时。

## 3. G2｜裁决、Git发布及硬STOP

原G0/G1通过不等于恢复原A47 G2或G3；本R1每条只审API小路径资格。

终态中择实际符合者：
- `DEFAULT_API_STILL_FAILS`（C0失败，C1 NOT_RUN）
- `DEFAULT_PASS_EXPLICIT_STREAM_FAILS`（C0通过、C1失败；只能称配置敏感）
- `BOTH_TINY_CONFIGS_PASS_ORIGINAL_COMBINATION_UNRESOLVED`（C0/C1都通过；原pool或交互未排除）
- `FROZEN_ENV_MISSING_STOP`、`RESOURCE_OR_GPU_LOCK_DEFERRED`、`BUDGET_STOP`（按实际前置/运行门）
- 其他语义不合格，报告`INCOMPLETE_EVIDENCE_STOP`，不伪造成功。

只在本执行branch新增：`docs/ai_workload_research/runs/AI_ARCH_A47R1_CAGRA_STREAM_RMM_MINICANARY_109_V1/`下的`FINAL_REPORT.md`、`GATES.json`、`RUN_IDENTITY.json`、`CONFIG_AND_OBSERVATION.json`、`RESOURCE_RECEIPT.json`、原始小日志和SHA256索引；最少的supervisor/child Python脚本限`tools/aiarch_a47r1/`。不提交原venv、HDF5、raw训练、core dumps或二进制大文件；敏感内存地址可只在私有收据中保存必要非机密标识，发布报告不泄漏token/path secret。旧任务工作区/HEAD/input/output SHA与clean状态再次只读核对。

普通路径/包装问题同一个Goal **有界solve-and-continue**；一旦涉及新GPU调用、改变两个变量、预算或ABI/core版本，严格STOP。报告连同准确的`NOT_RUN`、失败/负证据、限制与不自动续跑声明，commit/push/远端fetch-back核对**exact commit/tree/新增blob及SHA、clean**之后STOP。GitHub HTTPS出问题可以用已认证SSH Git通道，不改GitHub身份或凭据。

**绝对禁止：** 完整GloVe图构建、CAGRA搜索、所有B1/B256四点、质量/recall测试、长profiling、NCU/NSYS/NVBit、模拟器/RTL、修补RMM/cuVS或CUDA驱动、下载/安装/重新配置核心包、额外GPU设备／节点、A47 R2或后续机制。**R1无论成功或失败都STOP；若想恢复正式A47，需要单独审查科学价值、资产与GPU新预算，再获用户新授权。**