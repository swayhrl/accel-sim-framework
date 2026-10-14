# AI-ARCH A47R2｜一次性纠正索引资格断言＋完成C0/C1最小对照

**执行者：109 Codex（可复用已STOP Lane M对话），必须使用全新独立worktree。**  
**用户授权：** 2026-10-15，用户收到A49确定性dtype断言错误和正常附着warning的独立审查后回复“继续吧。后续继续把下一步建议和具体怎么做给出，另外尽量合并轮次”。**本Goal批准小型1024×100 CAGRA资格确认及条件性的C1 stream单变量对照；不批准原118万GloVe构图、正式搜索/recall/性能、换版本或更多GPU配置。** 不把旧A47/A47R1未用完的预算续用。

Repository：`swayhrl/accel-sim-framework`  
独立branch：`hrl/aiarch-a47r2-cagra-index-fields-stream-109-v1`  
Git协调parent：`c3d235cd99f2698672dd40094fcd4502e397b055`；**实际启动使用包含本Goal的完整发布commit，不回退parent**。独立路径建议`/data/c16/aiarch_a47r2_cagra_index_fields_109_20261015_v1`；已有同名有效数据先比对来源，禁止盲删/覆盖/重置。

## 0｜研究裁决问题与禁止无限循环

**问题：** A47R1在默认内存资源/default stream下的`cagra.build`已返回且同步，却被包含`str(idx.dtype)=="float32"`的合取断言标成NO-GO。该断言由冻结cuVS26.10源码确定为不正确。**本轮首先要在相同合法输入和参数下，逐字段验证真实返回的index；若C0合格，则不等新Goal，立刻用另一fresh process做仅更改cuVS Resources stream的C1。**

严格单次连续`G0→G1(C0)→G2(conditional C1)→G3(科学裁决／Git closeout)`，普通Python/元数据/路径工程问题在GPU调用前充分预检并同Goal solve-and-continue；若发生真实科学身份、ABI、数值或预算门变化则STOP。**C0失败立即STOP，不用更多配置寻找PASS。每个可执行臂最多一次`cagra.build`，没有崩溃重试，不进行旧A47的pool+stream复现。**

### 证据阅读（只读）

1. 本branch的`docs/ai_workload_research/CURRENT_STATE.md`、`COORDINATION_PROTOCOL.md`。
2. `docs/ai_workload_research/reviews/AI_ARCH_A49_A47R1_C0_PREDICATE_SOURCE_AUDIT_2026-10-15_V1.md`；其前身[A47R1执行@13ea8acc](https://github.com/swayhrl/accel-sim-framework/blob/13ea8acc7f19d13eca0aa3c049984db5c4256e83/docs/ai_workload_research/runs/AI_ARCH_A47R1_CAGRA_STREAM_RMM_MINICANARY_109_V1/FINAL_REPORT.md)、[R1旧测试代码](https://github.com/swayhrl/accel-sim-framework/blob/13ea8acc7f19d13eca0aa3c049984db5c4256e83/tools/aiarch_a47r1/minicanary.py)及`raw/C0.log`只读。
3. 已认证环境和数据来自A47@`ce92807ca80e1a694e41376eab3dd6b146824fd8`，复用`/data/c16/aiarch_a47_cagra_glove100_109_v1/venv`及官方wheel身份：Python3.12.3、cuVS/RMM等26.10.0、CuPy14.0.1、源commit`24ee1bf1cb17cad0ac611e39643af39ee1870124`；GPU RTX4080/SM89；原数据/HDF5不参与本轮GPU。
4. [cuVS固定Python`cagra.pyx`](https://github.com/NVIDIA/cuvs/blob/24ee1bf1cb17cad0ac611e39643af39ee1870124/python/cuvs/cuvs/neighbors/cagra/cagra.pyx)blob`27880c8dd63e1d59a53c7e0cfbcbc8aef2727ae7`；[`cydlpack.pyx`](https://github.com/NVIDIA/cuvs/blob/24ee1bf1cb17cad0ac611e39643af39ee1870124/python/cuvs/cuvs/common/cydlpack.pyx)blob`aa3fbae5f2354491d0f817edecc64a5d962d4eca`，FP32返回`np.float32`类型对象，不是dtype实例；[C++`cagra.cuh`](https://github.com/NVIDIA/cuvs/blob/24ee1bf1cb17cad0ac611e39643af39ee1870124/cpp/src/neighbors/cagra.cuh)首次attach的dimension=0 warning可为正常。

## 1｜资源和隔离硬门

| 对象 | 这一次的累计上限 |
|---|---|
| GPU共享锁 | node109原`/data/c16/locks/c16_gpu_campaign.lock`；`flock(LOCK_EX|LOCK_NB)`；包括初始化/子进程/清理**累计≤300秒**；锁忙直接`GPU_LOCK_DEFERRED`，不轮询不抢占 |
| GPU | 仅RTX4080；任务进程显存≤2GiB，包括库/context；不用另外设备 |
| Host | 实际CPU有效workers≤2，进程树RSS≤2GiB；CPU准备≤30分钟 |
| 文件与网络 | 独立worktree、output、tmp/cache新增≤128MiB；同文件系统空闲≥64GiB；**所有新下载与pip/conda/编译/安装为0** |
| GPU构图调用 | C0最多一次，只有C0科学PASS才C1最多一次；相同1024×100输入；不得加其它配置、图、查询 |

- **旧A47和R1原资产只读**：原env、HDF5、raw、编译库、worktree、预算和Git树不得reset/patch/清理。仅只读核旧文件SHA、冻结manifest、旧STOP、现有驱动/GPU背景任务/资源。不能操作C16/AWMA资产，也不改系统CUDA/驱动、锁频、功率、时钟、RMM/cuVS源或ABI。
- 父监督进程先锁，后允许GPU子进程import CUDA/cuVS；占用GPU的小检查/实际构图均在锁内，所有子进程结束后释放锁。GPU上有他人任务也不做干扰式benchmark。极短任务的NVML采样可能漏峰，需用小输入、无大Pool、监督和峰值记录共同守护，不声称sample0=true0。
- GPU正常科学配置两进程串行、**总`cagra.build`≤2**。CPU纯静态预检充分后才启动C0：针对上一轮`allocator.__module__ is None`做字符串处理静态自测；检查`np.dtype(np.float32)==np.dtype('float32')`；AST/compile检查脚本，准备log目录、Git、收据、资源监控、stream对象所有权。**若确有非科学prebuild包装错误，允许在本Goal内有界修复，但不得超过一次prebuild修复、同一GPU锁总预算且总GPU子进程启动≤3；一旦调用`cagra.build`不得重试。** 修复日志完整保留，科学身份与进程计数不重置。若已启动两条有效臂，不再有第3进程。
- 不因为发现了错误断言就假定C0已经PASS，必须记录实际每个索引字段；不因为C++输出`new dimension 100 vs old 0`的正常warning就停机。另一个真正失败字段、kernel异常、SIGSEGV、身份或资源错误仍要按合同STOP。

## 2｜G0：纯CPU预检，先验固定两条臂

使用旧R1`tools/aiarch_a47r1/minicanary.py`的科学对象作为参考，**只在新branch创建自己的简单子进程和监督**。冻结：
- `seed=20261014`，NumPy`Generator.standard_normal((1024,100),dtype=np.float32)`，每行以原算法FP32 norm归一化。先验从旧R1绑定input SHA256：`01a2c2f8a7e56b7a440fa183734d4297a1945a3dbbd6baedb27c1c3695b2478c`；不同则停止并查数值/依赖，不能暗换seed/形状。
- 原Dataset路径保持一致：GPU上默认CuPy stream中`g=cp.asarray(x)`，真实同步且CPU往返与x字节一致；`ds=make_device_padded_dataset(g,resources=res)`，原日志`layout='padded',is_owning=false, memory_type='device'`，所有x/g/ds/res对象持续存活到build后资格确认。只输入1024 synthetic，不加载GloVe真实base。
- `cagra.IndexParams(metric='cosine',build_algo='ivf_pq',graph_degree=64,intermediate_graph_degree=128)`固定，只有这两个原选项，不能把构图算法改为NN-descent为了PASS。
- **C0：默认RMM per-device资源、默认CuPy allocator、`res=Resources()`**；不显式Pool、不`set_current_device_resource`、不`cp.cuda.set_allocator`。
- **C1：其余完全与C0相同**，仅创建保活`cupy.cuda.Stream(non_blocking=True)`并令`res=Resources(stream=stream.ptr)`。两者都在默认CuPy stream生成输入后同步，随后传对应res给相同Dataset/build调用；不增加另一种内存配置。旧A47 pool+stream的SIGSEGV仍是历史，R2不重新复现。

## 3｜G1/G2：正确记录属性，然后判断与条件继续

两条fresh process都必须在`build_enter`之前flush input hash、shape、dtype、dataset layout/is_owning/memory_type、device标识和`Resources`请求stream类别；C++实际内部stream指针/故障句柄没有验证时标`UNKNOWN`，不用Python请求值冒充。

执行`idx = cagra.build(params,ds,resources=res)` **至多一次**，同步`res.sync()`及`cp.cuda.runtime.deviceSynchronize()`。**紧接着，逐字段单独捕获并打印/写JSON，不能先合取assert**：

\`\`\`python
fields = {
    "trained": bool(idx.trained),
    "size": int(len(idx)),
    "dim": int(idx.dim),
    "graph_degree": int(idx.graph_degree),
    "dtype_repr": repr(idx.dtype),
    "dtype_normalized": str(np.dtype(idx.dtype)),
}
# 若单个property读取抛异常，分别记录FIELD_READ_ERROR后STOP，不伪造其它值。
qualified = (
    fields["trained"]
    and fields["size"] == 1024
    and fields["dim"] == 100
    and fields["graph_degree"] == 64
    and np.dtype(idx.dtype) == np.dtype("float32")
)
\`\`\`

对应每字段输出同时需要保留`assert_predicate_map`（每项True/False）与原始warnings、stderr，便于独立审查。**返回的`dtype`是类或dtype对象均可通过正确归一化验证，不用`str(np.float32)=="float32"`。**

- **C0完整PASS**＝API无SIGSEGV/异常、调用返回且同步、上述字段全部匹配，`BUILD_FIELDS_PASS`和`CLEAN_EXIT`以及子进程exit0；此时**立即执行C1，不额外发Goal或请示**，只改变Resources stream。若C0未完整PASS：`C0_REAL_FIELD_OR_API_FAILURE`，**C1 NOT_RUN/STOP**，不得用旧正常warning取代属性数据。
- C1全部通过＝`C0_C1_TINY_API_QUALIFIED_ORIGINAL_POOL_INTERACTION_UNRESOLVED`。C0通过、C1失败/崩溃＝`C0_DEFAULT_PASS_C1_STREAM_SENSITIVE`，但是由于stream交互的根因仍未知，不能直接叫驱动bug。属性和warnings都要保存。
- 附带`idx.graph`公开视图若可以用冻结发行接口、无需引入新依赖轻量读取，可额外对1024×64的图索引shape和合法范围做**可选诊断**，区分metadata和完整图内容；如果此可选操作因原API不支持而失败，标`OPTIONAL_NOT_QUALIFIED`但不静默改变已冻结的五项**必需**资格门；若实际读出明显无效图，必须记录为下一次问题，**不能宣称完整图数值验证已通过**。
- 这里**没有GPU检索、recall、GloVe索引、性能时钟或正式A/B实验**；tiny build duration只是资源管理，不得报告为CAGRA真实检索性能。

## 4｜G3：合并收口、条件性下一步建议与Git核验

只给一份完整结论，包括每条原始单次结果、未运行门、正确性/对象属性表、资源、GT/APP边界及**下一步选择树**：

| 本轮终态 | 在同一报告给出的下一步建议（不自动执行） |
|---|---|
| `C0_C1_TINY_API_QUALIFIED_ORIGINAL_POOL_INTERACTION_UNRESOLVED` | 小API运行资格建立。若确有下一轮科学价值，可申请**一条**使用默认资源/默认stream、复用原GloVe文件及同质量门的完整index build→save/load→recall→4点原生发现Goal；先确认旧A47 original pool/stream差异不会被误叫硬件收益 |
| `C0_DEFAULT_PASS_C1_STREAM_SENSITIVE` | 默认API可作为保守软件路径，正式GloVe仍需独立许可；不为解释RMM源码投入无限bug调试。若未来申请完整探针，统一默认Resources，不在benchmark中比较不同stream设置 |
| `C0_REAL_FIELD_OR_API_FAILURE` | 逐字段判明首个真实字段/错误，对应官方接口能力；若严重/不能由已知最小包装纠正，则平台方向STOP，转研究Q-S/其它独立真实AI负载；不连续申请多轮vendor workaround |
| `PACKAGING_OR_RESOURCE_STOP` | 优先判是否独立环境/资源暂态，仅在有新证据时再讨论；不更换科学输入或版本 |

所有下一步建议至少给出**唯一问题／新增证据／最小资源建议／软件近邻反证／STOP条件**，不只说“继续优化”。用户明确要求合并轮次，**执行者不得完成C0后停下来另写C1 Goal，也不得把轻微工程问题拆成单独轮次**。但下一个**完整GloVe索引或四点GPU发现**已越过本轮授权，**只能提出合同草案，不能启动或标已授权**。

单一成果目录：`docs/ai_workload_research/runs/AI_ARCH_A47R2_CAGRA_INDEX_FIELDS_STREAM_109_V1/`，至少`FINAL_REPORT.md`、`GATES.json`、`CONFIG_AND_FIELDS.json`、`RESOURCE_RECEIPT.json`、原始C0/C1日志（未运行者准确标NOT_RUN）、SHA256SUMS；最小runner代码放`tools/aiarch_a47r2/`。不修改`CURRENT_STATE.md`、旧A47/A47R1的raw/report/Goal或其他冻结分支，不merge其它工作。Git一次commit/push/远端fetch-back exact SHA/tree/blob、clean/锁释放后STOP。若合法HTTPS推送故障，可复用已认证SSH，不重配凭据或泄露token。

**严禁本任务尾声擅自开启A47R3、完整数据下载/构图/recall、4点搜索、NCU/NSYS/NVBit、模拟器/RTL、新硬件机制。**