# Round A15｜CUDA12.6 Green Context与PyTorch 2.10适配资格：只读源码闭环

**执行者：ChatGPT／AI-ARCH Discovery。日期：2026-10-13。**  
**性质：紧接A14、同窗口可连续完成的有限原始源码/官方API核查；没有登录109/164、初始化CUDA、安装工具、修改NequIP旧env或开GPU任务。**  
**科学状态：`CUDA126_DRIVER_API_EXISTS / TORCH210_PYTHON_SHIM_CONDITIONAL / RUNTIME_DEVICE_AND_LIBRARY_INTEROP_NOT_QUALIFIED / NO_GPU_ADMISSION`。**

## 0. 为什么要做这一小步

[A14](AI_ARCH_ROUND_A14_SM89_RESOURCE_AXIS_AND_WORKLOAD_FEASIBILITY_2026-10-13_V1.md)发现Green Context SM access quota是一条理论可辨识的GPU资源轴；但109已接受NequIP V1R1使用`torch2.10.0+cu126`，而**现代PyTorch文档**要求Green Context包装Cuda≥12.8。不能从新文档倒推“原环境已经有可工作的`GreenContext.Stream()`”，也不能反过来声称“CUDA12.6绝无Green Context”。

## 1. 四个独立技术层级，固定原始资料

| 层级 | 固定来源和本轮实际核实 | 结果/界限 |
|---|---|---|
| CUDA Driver API早期版本 | [NVIDIA官方CUDA 12.6.0 Driver API §6.35 Green Contexts](https://docs.nvidia.com/cuda/archive/12.6.0/cuda-driver-api/group__CUDA__GREEN__CONTEXTS.html) | **确实**已公布`cuDeviceGetDevResource`、`cuDevSmResourceSplitByCount`、`cuDevResourceGenerateDesc`、`cuGreenCtxCreate`及Green Context相关stream能力；8.x描述至少4SM且以2对齐的分区约束，但实际设备/驱动允许值以API结果为准。**API文档存在≠109实际设备调用已PASS** |
| PyTorch固定版本的Python shim | [pytorch/pytorch v2.10.0 `torch/cuda/green_contexts.py`](https://github.com/pytorch/pytorch/blob/v2.10.0/torch/cuda/green_contexts.py)，Git blob `2b8f7f176499818c3cdc842683b825771031eea5` | Python文件实际存在，`SUPPORTED = hasattr(torch._C, "_CUDAGreenContext")`，当C++扩展没有该对象时抛出“PyTorch was not built with Green Context support!”；仅提供`GreenContext.create(num_sms,device_id)`与`set_context/pop_context`兼容路线。**不等于在node109的具体cu126 wheel中`SUPPORTED=True`** |
| 可包装外部CUDA stream | [PyTorch v2.10.0 `torch/cuda/streams.py`](https://github.com/pytorch/pytorch/blob/v2.10.0/torch/cuda/streams.py)，Git blob `3670937cf9b75136201f2de68243ca905c367053`，`ExternalStream` | 确实存在包装外部`cudaStream_t`的Python类，但它不管理外部流寿命，设备身份错误时可失败。**仅有`ExternalStream`存在不能证明可以在不改变AOTInductor/OEQ/ALCHEMI Context及缓存身份时安全接管green stream** |
| 现代高层API接口边界 | [PyTorch官方GreenContext文档](https://docs.pytorch.org/docs/stable/generated/torch.cuda.green_contexts.GreenContext.html)、[CUDA文档](https://docs.pytorch.org/docs/stable/cuda) | 最新高层包装接受`GreenContext(...)`、`.Stream()`并要求`cuda.bindings`及CUDA≥12.8；beta/实验性且跨stream同步由用户负责。**这与v2.10.0固定源码的简化shim不是相同API**；不能把当前文档的样例直接复制到109已冻结环境 |

NVIDIA最新CUDA Guide还说明，Green Context通过创建执行流限制可用SM集合；并不会改变物理GPU规模，也可能受workqueue/共享GPU资源影响，无法保证多green context之间无条件并行；以设备API实际可申请的group/alignment和stream返回为准。

## 2. 具体可行性裁决：并非必须先升级整个CUDA环境，但尚未证明旧强库能接管

本轮能严格区分三条不同命题：

- **命题A，CUDA12.6有底层合法接口：SOURCE_CONFIRMED。** 因为12.6官方Driver API已发布，可以在将来具备明确执行授权的环境中考虑最小`cuDeviceGetDevResource`/green context创建与资源查询；不用仅凭现代PyTorch便利API就断言必须先换系统驱动/全量Torch版本。
- **命题B，现有node109 torch2.10+cu126可以直接做现代`GreenContext.Stream()`：NOT_QUALIFIED。** PyTorch v2.10源码接口与现代文档不同，CUDA扩展是否编译支持还受具体wheel构建；**本ChatGPT并未检查运行时`SUPPORTED`值**，不能猜TRUE或FALSE。
- **命题C，NequIP旧编译产物和GPU AlchemiOps/OEQ完全可在新GreenCtx外部流运行且语义不变：NOT_QUALIFIED。** 外部流寿命、context ownership、Warp使用current Torch stream、AOT设备与缓存选择、CUDA异步依赖及数值gate必须独立验证；只有Python`ExternalStream`的代码并不能担保它们自动合法。

更严格地说：如果以后有权限试最小API-canary，GPU锁、stream所有权和共享缓存不应由一个source-only研究文件默默改变。若只验证Driver API创建就宣布整个强模型可以换SM quota，则在第一个设备Context归属门就属于科学合同越界。

## 3. 对A14两候选的实际影响

| 候选 | 本轮新结论 | 当前处理 |
|---|---|---|
| C14-01 原已资格化NequIP + SM quota | 原数值/模型/强AOT baseline存在；原cu126工具链**文档层确有可能存在低层Green API**，但不能证明原编译GPU库沿自定义green stream正确运行 | `PARKED_DRIVER_INTERFACE_NOT_RUNTIME_VALIDATED`，**不要复用Lane M V1R1 runner偷偷加入新Context** |
| C14-02 Qwen2.5-0.5B BF16 Attention +强FA2/SDPA | 一样受Green stream兼容影响，另外权重、token与单4080强后端的正式model whole-step尚未闭合 | `PARKED_TOKEN_AND_SOFTWARE_IDENTITY`，没有下载或运行授权 |
| Carveout对照 | RTX4080/SM89确有L1/shared互换偏好，但只属driver hint，若想讨论实际容量轴还需核`launch__shared_mem_config_size` | 不作为本轮只改变物理寄存器/Cache的实验 |

## 4. 明确停止与是否需要更多科研工作

A14+A15已经完成了在**没有109运行权限**时对当前SM89资源能力和PyTorch现存接口能够做出的主要source-only核查，没必要再用新ChatGPT轮次重复搜同类版本说明。

**要继续产生新信息，必须经过一个新的科学/资源选择和新的明确权限**：或者挑C14-01作为低成本验证对象，首次只验证Green Context设备/stream/实际SM配额及同原V1输出的正确性，在所有门闭合后才决定是否有研究价值；或者选更有代表性的C14-02，首先锁自然输入/模型和最强软件identity。不允许边跑边换对象、补新版本矩阵或把M的科学接受结果回写为新实现。

**本轮未批准任何后续GPU Goal，未运行109 CUDA、未触碰旧锁/Cache、未修改历史C16/AWMA/NequIP scientific authority。**

**终态：`A14_A15_SOURCE_FEASIBILITY_COMPLETE / PHYSICAL_SM_QUOTA_API_CANDIDATE_ONLY / NO_NATIVE_OR_MECHANISM_ADMISSION`。**
