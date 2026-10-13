# Round A17｜Lane M A16 Green Context G1 STOP独立审查：错误命名接口与合法替代验证链

**审查执行者：ChatGPT／AI-ARCH Discovery；审查日期：2026-10-14（北京时间）。**  
**结论：`ACCEPT_SCOPED_A16_CONTRACT_STOP / OUR_GOAL_INTERFACE_DEFECT_CONFIRMED / DEVICE_SM_QUOTA_NOT_EVALUATED / ZERO_NEW_HARDWARE_CLAIM`。**  
**证据等级：GitHub固定提交逐项只读、7份关键文本独立SHA256、NVIDIA CUDA12.6与新版官方Driver API文档对照。未访问109或164重新执行或校验二进制raw，不授权新GPU。**

## 0. 固定执行身份与历史科学边界

- A16执行branch：`hrl/aiarch-a16-nequip-greencontext-109-v1`，HEAD [`3dfc5826960ada62548183365d5ad7489f89ae12`](https://github.com/swayhrl/accel-sim-framework/commit/3dfc5826960ada62548183365d5ad7489f89ae12)，commit tree `4fc624eff43882134e3bad7b2a1cfeda36612259`，parent `56c7901b452138d2beeed754a401a84d8db091e9`；GitHub compare基于该parent为ahead1/behind0。
- [执行`FINAL_REPORT.md`](https://github.com/swayhrl/accel-sim-framework/blob/3dfc5826960ada62548183365d5ad7489f89ae12/docs/ai_workload_research/review_packs/AI_ARCH_A16_NEQUIP_GREEN_CONTEXT_109_CANARY_V1/FINAL_REPORT.md)和`API_QUOTA_RECEIPT.json`、`DRIVER_G1_RESULT.json`、`DRIVER_EXPORTED_SYMBOLS.txt`、`RUN_IDENTITY.json`、`RESOURCE_USAGE.json`、[实际C++探针](https://github.com/swayhrl/accel-sim-framework/blob/3dfc5826960ada62548183365d5ad7489f89ae12/tools/ai_workload_research/a16_greencontext_canary/driver_entry_probe.cpp)直接读取。
- 原A16 Goal Git blob `4e00b0b3f3857cc11ee5b41771fc918fd3644153`。上游V1R1 NequIP [`1f69559df4f51290589de72876f36a756c5439f0`](https://github.com/swayhrl/accel-sim-framework/commit/1f69559df4f51290589de72876f36a756c5439f0)已接受软件批量响应、AOT数值资格和164归档仍独立STOP；**不继承它的num PASS为Green Context G4**。

## 1. 到底运行了什么，确认到哪一层？

| 阶段 | 由GitHub原始receipt支持的事实 | 边界 |
|---|---|---|
| G0 | 固定原模型SHA256 `63d4bafd872850a014fd21dedeea416b61173a17750dee0b2b8dd2b126f407aa`、Si `c08d3771a06beb82b0ed4258f78eecc7ce623f73ca6df20be99bd5722163e770`、AOT `6b4ceb69ebaa7670f5bfdb06e8d0648644b467eec28983fb3d436a18f4f953f7`重新身份核对；目标RTX4080 SM89、UUID、driver；非阻塞GPU共享锁通过 | 复用的是旧科学资产**字节身份**，没有在Green配额下做模型计算 |
| G1 | `cuInit`、`cuDriverGetVersion`、`cuDeviceGetAttribute`、`cuDeviceGetDevResource`返回成功；设备与未分区资源均读为**76物理SM**；`cuGetProcAddress("cuStreamGetDevResource",…,CUDA_VERSION=12060,…)`本身返回`CUDA_SUCCESS`但`CUdriverProcAddressQueryResult=1`（`CU_GET_PROC_ADDRESS_SYMBOL_NOT_FOUND`）、函数地址NULL | **没有**调用资源分区函数；没有任何已分配Green SM quota。物理SM数量76不能填写为Green quota76或0 |
| G2–G4 | 未创建`CUgreenCtx`或Green stream；0 kernel、0 NequIP forward/force/stress、0数值比较、0性能样本 | 均`NOT_RUN_G1_STOP`，不能说“设备不支持Green”或“数值失败” |

执行侧资源receipt：共享锁**0.301507秒**，已报告GPU显存峰值0MiB、子进程maxRSS**74,092,544 bytes**，新磁盘约**2,016,143 bytes**，下载/安装/工具链升级全为零。实际GPU没有产生Green context、stream或新任务kernel。执行侧报告164**17个raw文件＋23个closeout文件回读PASS**；本ChatGPT未直接登录164检验其二进制包。旧A16和旧V1R1工作区/分支均保留。

**独立完整性抽核**：ChatGPT直接重取GitHub的`FINAL_REPORT.md`、`FINAL_DECISION.json`、`API_QUOTA_RECEIPT.json`、`DRIVER_EXPORTED_SYMBOLS.txt`、`DRIVER_G1_RESULT.json`、`RESOURCE_USAGE.json`、`STREAM_OWNERSHIP.json`，重新计算UTF-8 SHA256，**7/7与`SHA256SUMS`严格相等**。不能将此表述为21/21文件或164 raw独立复核通过；那些是执行侧报告。

## 2. 根因：A16合同使用了与冻结CUDA12.6不匹配的必要符号

- [CUDA12.6 Green Context原始Driver API](https://docs.nvidia.com/cuda/archive/12.6.0/cuda-driver-api/group__CUDA__GREEN__CONTEXTS.html)正式列有`cuDeviceGetDevResource`、`cuDevSmResourceSplitByCount`、`cuDevResourceGenerateDesc`、`cuGreenCtxCreate`、`cuGreenCtxStreamCreate`、**`cuGreenCtxGetDevResource`**和`cuStreamGetGreenCtx`；**没有列出`cuStreamGetDevResource`**。
- [CUDA12.6 Stream Management](https://docs.nvidia.com/cuda/archive/12.6.0/cuda-driver-api/group__CUDA__STREAM.html)支持`cuStreamGetCtx_v2(CUstream, CUcontext*, CUgreenCtx*)`，能查询流关联的normal/green context；对green stream输出`pGreenCtx`，并非根据流名推断。
- [更新版Driver API的Green Context说明](https://docs.nvidia.com/cuda/cuda-driver-api/cuda_driver_api/group__CUDA__GREEN__CONTEXTS.html)才列有`cuStreamGetDevResource`，不应倒灌到本次冻结的CUDA12.6头文件与node109 driver接口。
- 本机`DRIVER_EXPORTED_SYMBOLS.txt`显示**`cuStreamGetCtx_v2`、`cuGreenCtxGetDevResource`两者实际已导出**，而必需的`cuStreamGetDevResource`在CUDA12.6头文件和驱动中不可查。本机另外没在该有限符号清单中出现`cuStreamGetGreenCtx`，**不能推断该项动态调用实际存在**，后续优先使用已核的`cuStreamGetCtx_v2`。
- `cuGetProcAddress`的调用返回值与out参数的`queryResult`是两种不同状态；Lane M正确处理了`CUDA_SUCCESS + SYMBOL_NOT_FOUND + nullptr`，没有伪造成功或猜ABI。接口不存在**并不说明其它Green Context API失败**，因为它们根本没被调用。

**归责与方法学修正**：这是**ChatGPT设计的A16科学合同中误放入版本不适用的命名接口**，属于`GOAL_SOURCE_INTERFACE_DEFECT`，不是Lane M工程执行不合格，也不意味着RTX4080的Green Context特性已经被实机证伪。正确的前置source审查应将每个强制API与冻结`cuda.h`、本机导出符号/driver、官方同版本文档一一比对，**不该仅依据最新文档列函数名**。原A16按冻结合同STOP仍应保留不回写。

## 3. 有官方依据的替代G1验证链（proposal，不是已执行的PASS）

要求**用已有CUDA12.6明文接口而不是发明同名ABI**，最小可审链：

1. 既有`cuDeviceGetDevResource`返回设备SM资源；`cuDevSmResourceSplitByCount`按8.x官方最低4 SM、2对齐约束尝试**恰好一个**约半SM合法分区，记录API真实返回与实际`smCount`，不假定请求38就一定实际38。
2. `cuDevResourceGenerateDesc`→`cuGreenCtxCreate`→`cuGreenCtxStreamCreate`，仅创建**自己拥有**的Context与Stream，保留正确flags、thread/context ownership和清理。
3. 对**该刚创建的stream**执行`cuStreamGetCtx_v2(stream,&normalCtx,&returnedGreenCtx)`，必须返回和Step2 **相同的`CUgreenCtx`句柄**；不是看默认primary context是否存在。
4. 对上述实际green handle执行`cuGreenCtxGetDevResource(returnedGreenCtx,&quotaResource,CU_DEV_RESOURCE_TYPE_SM)`，必须报告quota的`smCount`与Step1/2同一份分区资源相符，且**严格小于76物理SM**。这样由文档函数的句柄关联与资源查询建立G1的**stream-bound实际可用SM quota证明**。
5. G1通过之后才可按原批准的一档green kernel→框架stream归属证明→最多帧0、109的五次均值数值资格继续。无法证明ALCHEMI/OEQ/AOT在目标流上运行，依旧停止于G3；不会因为Driver链PASS就认证模型。
6. 若本地已有的`cuStreamGetCtx_v2`/GreenGet接口虽导出却调用失败，记录返回码并`DEVICE_OR_DRIVER_G1_STOP`；不扫其它版本、quota组合、kernel参数或将CUDA context更换误认为模型正确性。

**所有步骤必须先获得一个新、明确获准的最小修订合同；不在旧已STOP A16分支上补跑。** [原A16合同](../goals/AI_ARCH_A16_NEQUIP_GREEN_CONTEXT_109_CANARY_V1.md)不应静默改成新版。

## 4. 研究是否值得再试？

- 此次失败消耗的GPU持锁不到1秒，且修复对象是唯一指定API的错误，**不是反复试不同版本/不同科学假设**。因此**一次**在新V1R1分支的有界定点源接口修复与G1–G4资格恢复有工程合理性。
- 但它最多形成**`API_AND_NUMERIC_FEASIBILITY`**，即便G4 PASS也不能证明P13 SM瓶颈、SM扩容收益或需要新硬件。后续任何性能扫参应按额外科学资格与用户授权单列。
- 如果替代链仍不能在既有driver/toolkit上合法创建Green stream，或者G3要求改变NequIP/ALCHEMI/OEQ旧环境才能接管，**停止该NequIP GreenCtx方向**，避免Codex在接口层消耗无限轮次。
- 不允许简单改成新PyTorch/驱动/Toolkit、第三方wheel/持久patch旧数据缓存或直接选择Qwen替代；那是另一个新的负载/版本合同。

**最终审查：`A16_STOP_ACCEPTED / G1_NAMED_API_DEFECT_DESIGN_ERROR / ONLY_ONE_BOUND_REPAIR_PROPOSABLE / NO_GPU_AUTO_RETRY`。**
