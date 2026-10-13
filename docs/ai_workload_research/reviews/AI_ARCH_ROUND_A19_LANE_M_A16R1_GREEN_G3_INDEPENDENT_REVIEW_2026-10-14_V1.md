# Round A19｜Lane M A16R1：38/76 SM Green Context与G3模型互操作STOP独立科学审查

**执行者：ChatGPT／AI-ARCH Discovery。审查日期：2026-10-14。**  
**固定执行身份：** [`6953ac1690b7a905b6000833a879f9164c7c9e43`](https://github.com/swayhrl/accel-sim-framework/commit/6953ac1690b7a905b6000833a879f9164c7c9e43)，tree `5d993895142148886b24e7cc32d3035acf308361`，parent `3dfc5826960ada62548183365d5ad7489f89ae12`。执行branch `hrl/aiarch-a16r1-nequip-greencontext-109-v1`已核对HEAD一致。  
**裁决：`ACCEPT_SCOPED_SM89_GREEN_QUOTA_AND_ONE_KERNEL / G3_INTEROP_NOT_TESTED_UNQUALIFIED / G4_NOT_EVALUATED / P13_NO_HARDWARE_HEADROOM_CLAIM / CLOSED_NO_AUTOMATIC_RETRY`。**

> 此审查直接取GitHub固定提交下的Driver G1/G2原始JSON、256个输出、实际C++/CUDA/Python runner、框架G3 source/runtime receipt、资源及164索引，并交叉核固定`pytorch/pytorch@v2.10.0` C++ source。是`GITHUB_FIXED_COMMIT_INDEPENDENT_RECOMPUTE`，**不是重新连接109/164本机运行、不是独立复算164二进制raw**。

## 0. 审计对象与真正执行内容

执行完整报告：[AI_ARCH_A16R1_NEQUIP_GREEN_CONTEXT_109_CANARY_V1/FINAL_REPORT.md](https://github.com/swayhrl/accel-sim-framework/blob/6953ac1690b7a905b6000833a879f9164c7c9e43/docs/ai_workload_research/review_packs/AI_ARCH_A16R1_NEQUIP_GREEN_CONTEXT_109_CANARY_V1/FINAL_REPORT.md)。原A16 `3dfc5826960ada62548183365d5ad7489f89ae12`处于合法`G1_INTERFACE_CONTRACT_GAP` STOP，V1R1 NequIP强编译原生 `1f69559df4f51290589de72876f36a756c5439f0`保持先前`ACCEPT_SCOPED_NATIVE_MIXED_RESPONSE`和独立STOP。此次从旧STOP精确起点追加一条执行提交，未合并协调branch。

本轮唯一修正是以CUDA12.6已有的`cuStreamGetCtx_v2`+ `cuGreenCtxGetDevResource`证明green stream归属与SM配额，而不再强求旧A16误用的`cuStreamGetDevResource`。继续只允许一档SM quota、一个小kernel和条件性的Si帧0/109原模型数值canary；正式性能计时、profiling和新GPU机制均**从未授权**。

## 1. G1：实际SM资源分配PASS，但要说清具体证明层级

直接读[`DRIVER_G1_G2_RESULT.json`](https://github.com/swayhrl/accel-sim-framework/blob/6953ac1690b7a905b6000833a879f9164c7c9e43/docs/ai_workload_research/review_packs/AI_ARCH_A16R1_NEQUIP_GREEN_CONTEXT_109_CANARY_V1/DRIVER_G1_G2_RESULT.json)、`API_QUOTA_RECEIPT.json`与[实际`driver_probe.cpp`](https://github.com/swayhrl/accel-sim-framework/blob/6953ac1690b7a905b6000833a879f9164c7c9e43/tools/ai_workload_research/a16r1_greencontext_canary/driver_probe.cpp)：

| 核查点 | 固定执行侧原始事实 | ChatGPT独立裁决 |
|---|---|---|
| 平台 | 109 RTX4080、CC8.9，76个设备物理SM，CUDA头文件版本`12060`，driver API返回版本`13000` | 目标设备/头文件/Driver的标识没有被混为一谈 |
| 分区 | `cuDevSmResourceSplitByCount`对最小请求38 SM、flags0、一次candidate返回实际38 SM/one group | **是实机Driver资源分配行为**，不是论文模拟值或仅API文档存在 |
| 归属 | `cuStreamGetCtx_v2`查询的`CUgreenCtx` handle与刚创建的handle严格相等；`cuGreenCtxGetDevResource`对该handle返回38 SM | 建立了一条**stream-bound 38/76 SM资源配额证据链**；返回的普通/primary context另行记录，**不当作Green证明** |
| 变更幅度 | 实际配额38，占76物理SM的50%；没有其它quota点 | 是**可用SM配额缩减**，同时减少该SM份额附带的寄存器/SMEM/算力资源，不是物理“扩SM”或“仅改寄存器容量” |

全部冻结G1必要Driver API调用报告`CUDA_SUCCESS`，相关stream/资源值一致，支持`G1_PASS_STREAM_BOUND_QUOTA`。**没有硬件SMID轨迹/NCU物理驻留采样**；但这个额外观察本来不属于本次Driver资源身份合同，不影响有范围的API PASS，也不能由此扩大为“已实际使用全部38个SM”的主张。

## 2. G2：一个真实Green Stream小kernel正确，256/256由本窗口重算

冻结`tiny_kernel.cu`仅计算`output[i]=3*i+11`；grid=(2,1,1)、block=(128,1,1)、N=256，GPU数据对象与pinned host各1024字节。GPU Driver launch、异步D2H、显式stream同步、二次owner handle核验均报告成功。

**本ChatGPT从GitHub直接重读`DRIVER_G1_G2_RESULT.json`的完整256项`kernel_output`数组，并独立执行`for all i∈[0,255]: result[i]===3*i+11`，结果**256/256严格PASS**。首值11/14/17/20、末值767/770/773/776。复核34个Driver调用receipt全为`CUDA_SUCCESS`，green handle相等、post-kernel归属相等、原线程context从NULL恢复NULL，`cleanup_success:true`；没有跨进程复用已经销毁的stream或context句柄。

此证据支持`G2_PASS_ONE_DRIVER_KERNEL_UNDER_GREEN_STREAM`，但一个只有2个CTA的小kernel不足以测试SM并行度、实际占满38SM或完整模型性能。不应把这个小kernel视为NequIP GPU工作负载的数值资格。

## 3. G3：最关键的审查发现——当前STOP并不是实测框架不兼容

执行者[`FRAMEWORK_INTEROP.json`](https://github.com/swayhrl/accel-sim-framework/blob/6953ac1690b7a905b6000833a879f9164c7c9e43/docs/ai_workload_research/review_packs/AI_ARCH_A16R1_NEQUIP_GREEN_CONTEXT_109_CANARY_V1/FRAMEWORK_INTEROP.json)及[`gpu_gates.py`](https://github.com/swayhrl/accel-sim-framework/blob/6953ac1690b7a905b6000833a879f9164c7c9e43/tools/ai_workload_research/a16r1_greencontext_canary/gpu_gates.py)显示：G2的Driver probe在**一个独立子进程**内创建并销毁green context/stream，然后G3在**另一个独立Python进程**里仅检查已装库的能力标志与部分source identity。两个进程间**没有继续使用已销毁的Driver句柄**，这避免了不安全跨进程指针复用。

G3实际得到：`torch2.10.0+cu126`、`torch.cuda.green_contexts.SUPPORTED=True`、C++`_CUDAGreenContext`存在、旧`create/set_context/pop_context`接口存在、`ExternalStream`存在、现代`.Stream()`包装不存在；`torch.cuda.is_initialized()==False`；**未加载模型、未执行原AOT/OEQ/ALCHEMI任何GPU操作、也未执行PyTorch GreenContext.create/set/pop**。

**真实runner中的重要方法学局限**：无论`SUPPORTED`是否为True，`gpu_gates.py`当前G3分支最终都按设计生成`G3_INTEROP_UNQUALIFIED_STOP`并退出，**没有安排在同一个活的Green Context上实际执行有界的Torch/ALCHEMI/OEQ/AOT流归属验证**。因此这不是“框架执行失败”，不是“库逃逸Green quota”，也不是“CUDA cu126不支持框架Green”；它是**只读能力检查后没有进行模型级互操作实验的资格未建立**。

固定[pytorch/pytorch v2.10.0 `CUDAGreenContext.cpp`](https://github.com/pytorch/pytorch/blob/v2.10.0/aten/src/ATen/cuda/CUDAGreenContext.cpp) blob `a579e45e160669415d3b615d2630af61e9d0b011`进一步证实：该版本C++实现确有`create`、`setContext`、`popContext`，检查运行时Driver版本不少于12080并在进入Green Context时设置当前CUDA流为默认流，保留父流并用事件处理依赖。本轮Driver API报告`13000`，**这个特定版本检查从日志看不是显然阻塞**；但源码API存在不证明NequIP整体能使用该流，也不证明已装C++扩展在实际模型条件下成功。

**科学处置**：接受`G3_NOT_QUALIFIED / SOURCE_AND_CAPABILITY_ONLY / NO_EXECUTED_MODEL_INTEROP`。执行者的STOP安全且与本次合同的“证据不足即停止”一致；但不要把此次当作**有意义的运行时互操作性负例**。从效率角度，这轮的G3实现已预置必停，与“逐门验证、能够通过后续G4”的完整预期存在设计缺口。应在未来科研Goal中避免用必停程序代替已授权的有界实证，或应提前明确仅做SOURCE gate而非描述为可以达到GPU/model资格的条件执行。

若今后想做不同任务，必须**先通过源码/平台资格设计一个真正可运行的同进程、小范围、可回退的互操作canary**；不能通过复制前轮失效的Driver handle、强行改AOT、monkeypatch库或升级整个CUDA环境寻找PASS。本轮既未实际证实不兼容，也未找到值得立即再次投入的GPU硬件剩余。

## 4. G4与资源归档

- `NUMERIC_CANARY.json`严格记`NOT_RUN_G3_STOP`、帧数组为空、无模型调用、无四个output、无5次均值及有向周期边核对。原V1R1的`FP32 model_dtype/原FP64辅助`、TF32/AMP-off、`atol=rtol=5e-5`和旧OAM-S/AOT/Si输入SHA保持冻结，但**不能继承旧V1R1数值PASS为Green版本PASS**。
- 执行侧资源：共享GPU锁**1.159878s**，报告单次≤4 CPU worker、子进程最大RSS **770,711,552 bytes（约735MiB）**、新增本地磁盘**2,340,563 bytes（约2.23MiB）**、下载安装升级均0。Driver进程显式device allocation仅1024字节；GPU显存**0MiB是采样值，短暂Green context/module峰值未被完整捕获**，不能陈述成GPU运行实际内存总占用0。没有OOM或已知预算越限。
- 执行侧164归档报告**28 raw + 25 closeout文件**回读PASS，含manifest与原包SHA；本ChatGPT未直接连接node164对二进制raw复核。
- **独立Git完整性抽核**：本ChatGPT逐个从固定HEAD重新下载7份最相关的UTF-8文本/JSON（`FINAL_REPORT`、`FINAL_DECISION`、`API_QUOTA_RECEIPT`、`DRIVER_G1_G2_RESULT`、`FRAMEWORK_INTEROP`、`G3_RUNTIME_STDOUT`、`NUMERIC_CANARY`），重算SHA256，**7/7与执行`SHA256SUMS`严格一致**。其余23项及164大包仅以执行者的自检为证，不冒称23/23由本窗口重算。
- 固定执行提交相对A16 STOP为**ahead1/behind0**，执行branch HEAD已核对，原V1R1/旧A16未merge、不被新的结果覆盖。

## 5. 科研决策：技术可行性结果留下，不自动继续R2/R3

| 问题层次 | 本次真实证据 | 裁决 |
|---|---|---|
| SM89可否由当前驱动创建Green配额？ | 真机Driver 38/76 SM、stream-bound owner proof | **`DEVICE_GREEN_QUOTA_AVAILABLE`** |
| 这个Green stream能否执行GPU工作？ | 一个短小sm89内核256整数PASS | **`DRIVER_GREEN_KERNEL_EXECUTES`** |
| PyTorch2.10是否完全不支持GreenCtx？ | 当前wheel`SUPPORTED=True`、上游C++有旧接口 | **“完全不支持”不能成立**；具体运行时尚未测 |
| NequIP AOT/OEQ/ALCHEMI是否全部在绿流中执行？ | 没有活的同进程互操作性执行 | **`MODEL_INTEROP_NOT_EVALUATED`**，不是失败 |
| NequIP Green 38SM相对全76SM有何性能差？ | 数值资格和性能样本都为零 | **`P13_RESOURCE_HEADROOM_NOT_EVALUATED`**，绝不能给加速/减速百分比 |
| 新硬件机制能否晋升？ | 没有强软件之后的真实剩余 | **`NO_HARDWARE_MECHANISM_ADMISSION`** |

本轮的真实贡献是**SM89、旧Driver接口下的SM quota native资格**，纠正了A16 API版本错误。**下一步按已审批的一次性修复边界正式收口当前Green Context探索。** 不为“已经能分38SM”而继续发A16R2/R3、强行迁移旧编译栈或者开展SM quota扫参。

若未来有新的、独立的科研问题与合法工作量、真实数值和强软件基线，SM quota可以作为一个**已证明设备级可用的资源控制候选**，但不能自动继承到那个负载的编译/多库stream、数值和性能因果。应优先寻找具有完整执行时间价值的AI应用问题，而不是扩大平台API调试本身。

**最终科研状态：`ROUND_A19_SCOPED_G1_G2_ACCEPTED / G3_NOT_RUNTIME_TESTED / G4_NOT_RUN / GREENCTX_EXECUTION_LINE_CLOSED / P13_NO_NEW_MECHANISM`。**
