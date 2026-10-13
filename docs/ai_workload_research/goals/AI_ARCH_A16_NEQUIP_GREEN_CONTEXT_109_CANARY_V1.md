# Round A16｜SM89 Green Context最小API及NequIP数值资格canary

**科学设计与后续独立审查：ChatGPT／AI-ARCH Discovery**  
**拟执行者：Codex Lane M／node109，一个新的独立worktree（继续复用原Codex窗口）。**  
**日期：2026-10-13。状态：USER_AGREED_SCOPED_CANARY / PREPARED_NOT_LAUNCHED / NO_PERFORMANCE_AUTHORIZATION。**

## 0. 授权范围的准确解释

用户在A14–A15交付之后明确回复“同意”。上一条给出的下一步是：先选一个科学对象，仅对**很小的109 Green Context API与数值资格**作检查，而不是立即做完整性能campaign。优先采用现成NequIP避免下载新模型。**本次同意只在这个已公布范围内生效**：允许下面更保守的自限额API/数值canary；不意味着批准Qwen下载、SM配额性能扫参、NCU/NSYS、改驱动或任何机制。

如果Codex在执行中发现必须改变模型、软件版本、已有AOT产物或调度/数值语义，或超过本合同预算，应按STOP提交证据，而不是把技术兼容问题升级成通用“工程修复”。

**上游必读（固定提交）：**
- [A14资源与负载筛选](../literature/AI_ARCH_ROUND_A14_SM89_RESOURCE_AXIS_AND_WORKLOAD_FEASIBILITY_2026-10-13_V1.md)
- [A15 CUDA12.6/torch2.10接口审查](../literature/AI_ARCH_ROUND_A15_GREEN_CONTEXT_CU126_SOURCE_INTERFACE_CLOSURE_2026-10-13_V1.md)
- [A11已审数值与整段时间](../reviews/AI_ARCH_ROUND_A11_LANE_M_T_JOINT_INDEPENDENT_REVIEW_2026-10-13_V1.md)
- [Lane M固定旧结果`1f69559df4f51290589de72876f36a756c5439f0`](https://github.com/swayhrl/accel-sim-framework/commit/1f69559df4f51290589de72876f36a756c5439f0)
- 原始V1合同blob `0101a33c27090ee5ef4f0f29ad5d98b492e6280b`。旧V1 `06674a96…`的STOP与V1R1正常STOP均保持。

## 1. 唯一科学对象和本轮不变量

- **仅C14-01（NequIP OAM-S:0.1）**。不用C14-02 Qwen，不下载任何权重/数据/系统wheel。
- **原静态输入**：之前固定的Si `sitraj.xyz`，SHA256 `c08d3771a06beb82b0ed4258f78eecc7ce623f73ca6df20be99bd5722163e770`；本次仅canary帧零基`[0,109]`，必要时B=2；不是32帧正式观测、更不是新holdout或MD轨迹。
- **原模型文件** SHA256 `63d4bafd872850a014fd21dedeea416b61173a17750dee0b2b8dd2b126f407aa`，原BATCH AOT文件`OAM-S.nequip.pt2` SHA256 `6b4ceb69ebaa7670f5bfdb06e8d0648644b467eec28983fb3d436a18f4f953f7`。
- **原109只读资产位置**：`/data/c16/aiarch_nequip_static_batch_109_v1r1_20261013/`。Codex开始时必须查询真实存在/哈希，不存在则`INPUT_OR_COMPILED_ASSET_MISSING_STOP`；不重新下载模型、不编译替代AOT、不迁移旧环境。
- Python3.11.17、PyTorch2.10.0+cu126、NequIP/OEQ/ALCHEMI及其依赖均使用原V1R1合法隔离环境的**只读**版本；不得更换核心版本、Torch wheel、CUDA driver或系统工具链。
- 数值语义：原`model_dtype=float32`、TF32 off、autocast off，原生FP64 Bessel/能量辅助常量保持；四字段`atomic_energy,total_energy,forces,stress`；**五次输出转double后取均值**，`atol=rtol=5e-5`，无NaN/Inf；精确有向周期边多重集合及原输出单位不变。未经平台确认的绿上下文数值不应进入正式性能排名。
- 本轮对比**同一个固定GPU与软件**在常规流vs一个Green Context SM配额流上的API/数值资格；**不允许采集、比较或发布性能速度比**。

## 2. 先澄清要证明的层级（绝不能跳门）

- **S0 SOURCE_CONFIRMED**：NVIDIA [CUDA 12.6 Driver API Green Contexts](https://docs.nvidia.com/cuda/archive/12.6.0/cuda-driver-api/group__CUDA__GREEN__CONTEXTS.html)明确8.x的资源划分接口及SM对齐，来源API存在≠109实际可调用。
- **G1 DEVICE_SM_QUOTA**：`cuDeviceGetDevResource`→按设备实际对齐/最小值分割SM→`cuDevResourceGenerateDesc`→`cuGreenCtxCreate`→`cuGreenCtxStreamCreate`→`cuStreamGetDevResource`，记录真实配额与相关driver返回码。分区仅取**一档约半数SM的合法配额**（按真实alignment向合法方向取整）；不默认请求36/38/40 SM成功，也不扩成扫描。
- **G2 STREAM_SEMANTICS**：通过最简单的单独小型非算力密集且可复算的CUDA kernel/stream输出校验：它确实在**自有green stream**上完成、正确同步、资源查询和stream/context所有权一致；此门只证明小内核/driver可用，不证明PyTorch/OEQ/AOT兼容。禁止无界编译、不同算法或复杂profile。
- **G3 FRAMEWORK_INTEROP**：**仅在G1/G2 PASS后**，检查原torch2.10已安装`torch.cuda.green_contexts.SUPPORTED`和实际可用API/stream所有权、AOTInductor、Warp/ALCHEMI与OEQ所用stream/context。PyTorch v2.10源码有条件性旧接口`GreenContext.create/set_context/pop_context`，**不能用现代文档`GreenContext(...).Stream()`样例猜想cu126版本能用**。不得强行monkeypatch、修改库、拿失效的外部stream地址、往旧runner插hook或变更GPU缓存权威。若不能**安全且可核地证明模型GPU操作走目标green stream**，停止并标`DRIVER_API_PASS_MODEL_INTEROP_UNQUALIFIED`，不冒称全模型quota实验成立。
- **G4 MODEL_NUMERIC**：仅当G3成立，以原模型和AOT结果/已接受reference，对帧0、109分别或合法B2执行最少必要的五次canary，比较energy/forces/stress和边集合，记录每字段max abs/relative与逐元素allclose、数值参考源的hash。**每个GPU操作的stream/依赖身份须有可追溯证据**；如果只知道green stream存在却不能说明实际模型kernel是否在其上，则`NUMERIC_UNDER_QUOTA_NOT_ESTABLISHED`。若结果不合格则`NUMERIC_STOP`；绝不调容差或更换算法。
- 不通过G1直接STOP；G2失败停止；G3不能合法完成则保留G1/G2的有限PASS并STOP；G4只有所有更早资格通过才可合法报告。任何G门的PASS都**不是**`P13_PHYSICAL_SM_BOTTLENECK`或`HARDWARE_MECHANISM_QUALIFIED`。

## 3. 前置科学/资源门及一次性连续执行

1. **代码起点**：使用执行分支`hrl/aiarch-a16-nequip-greencontext-109-v1`（将在GitHub事先创建）；只在**该分支新独立worktree**编写薄CLI/probe/小report，禁止在原`hrl/aiarch-nequip-static-batch-109-v1r1`上提交新观测，更不可修改164 raw、NequIP原包和所有历史manifest。
2. **CPU-only预检**：查旧inputs/compiled hashes、已装CUDA12.6 headers/compiler/driver可见版本和PyTorch源码API；原依赖已有且必须复用，无pip安装/无任何网络下载；此步不需CUDA context。若缺必要资产或编译工具，`PRECONDITION_STOP`，不从原C16/AWMA工作区拆文件。
3. **GPU前必须独占原锁**：`/data/c16/locks/c16_gpu_campaign.lock`，**非阻塞取得，不能更名/删锁/绕过**。锁忙则`RESOURCE_DEFERRED`并退出；检查有无其它GPU任务、正确设备UUID `GPU-ce6cba36-415b-4e27-40e2-bded6bc1ee59`与SM89/驱动。锁覆盖任意CUDA API初始化、GreenCtx、GPU kernel、库canary；借此避免干扰其它项目。
4. GPU测试采用一个隔离子进程或少量有界子进程，结束时显式同步、正确释放**自己拥有**的green stream/context，恢复之前线程context；不得调用全设备reset或销毁非自有资源。不同时运行多个不同quota任务，不做非实验组系统级GPU configuration修改。
5. 若G1/G2在老版本实现所需CPU薄C++/Driver代码可以直接用现有头文件编译，则最多一次明确实现路线、普通包装问题小范围修复；若必须升级工具链/自建PyTorch扩展/大量JIT，记录`TOOLCHAIN_GAP`并STOP。
6. 无论任意PASS/STOP都发布精简`API_QUOTA_RECEIPT.json`、`STREAM_OWNERSHIP.json`、`FRAMEWORK_INTEROP.json`、`NUMERIC_CANARY.json`（未运行明确写NULL/NOT_RUN）、`RUN_IDENTITY.json`、`RESOURCE_USAGE.json`、`FINAL_DECISION.json`、`FINAL_REPORT.md`和SHA；不存在的项目使用明示未执行字段，不捏造样本。用新独立输出目录`docs/ai_workload_research/review_packs/AI_ARCH_A16_NEQUIP_GREEN_CONTEXT_109_CANARY_V1/`；source及raw只落本任务路径，完成commit/push/远端readback后STOP。结果若需归档164只允许在既有权限下**新目录、小包、回读**，不改旧权威。无独立ChatGPT review不产生新机制/性能准入。

## 4. 本次自限资源预算（硬STOP，不是预期运行耗时）

| 类别 | 上限 |
|---|---|
| GPU | **只允许109现有RTX4080**，不启动第二GPU、MPS/MIG或其它独立GPU应用 |
| GPU锁占用 | 单次整个API/数值canary含GPU初始化与退出**≤10分钟（600秒）**，不包括锁忙等待（锁忙立即DEFER） |
| 显存 | 此任务峰值**≤4GiB**；OOM/超额STOP，不缩减数值合同去求通过 |
| CPU/RAM | ≤4 CPU workers，≤12GiB RAM；运行过程采集主机峰值与GPU显存 |
| 新文件/缓存/编译增量 | **≤512MiB**，全部任务本地独立目录，且保留原数据/全局缓存字节不变 |
| 下载/安装 | **0新权重、0新模型/数据、0依赖wheel或源码包、0 pip安装**；不得借任务升级PyTorch/cu128或CUDA Driver |
| 真正执行工作 | 仅一档有效SM配额、一个小driver kernel和最多2个固定Si canary frame，五次输出均值；**0正式timing blocks/0重复性能campaign** |
| 禁止 | NSYS、NCU、NVBit、Accel-Sim、训练、MD、holdout、Qwen模型、动态寄存器新机制、变更AWMA/C16、额外GPU任务、清理旧cache、驱动重启 |

**经用户同意的科学范围严格小于原A9；资源上限为本轮保守自限，不借用A9的90min锁或8GiB下载预算。** 任何后续性能/多配额扫描必须在本报告完成独立科学审查后另立合同并重新授权。

## 5. 终态标签

- **G0** `PRECONDITION_OR_LOCK_DEFERRED`
- **G1** `CUDA_GREEN_API_NOT_SUPPORTED` 或 `DEVICE_QUOTA_CREATED`
- **G2** `GREEN_STREAM_KERNEL_PASS` 或 `STREAM_TEST_STOP`
- **G3** `DRIVER_PASS_FRAMEWORK_INTEROP_UNQUALIFIED` 或 `INTEROP_QUALIFIED_WITH_SCOPE`
- **G4** `MODEL_NUMERIC_CANARY_PASS` 或 `NUMERIC_STOP`（仅G3合格后）
- **Scientific**：任何终态均为`API_FEASIBILITY_ONLY / P13_RESOURCE_HEADROOM_NOT_EVALUATED`；不得使用`SM_SCALING_SPEEDUP`或`HARDWARE_PROMOTION`。

下一步：Codex Lane M仅在本Goal被用户实际发送到109窗口后执行；ChatGPT从其Git commit/raw-small-report独立审查G1–G4，**不要求自动补新GPU测试**。
