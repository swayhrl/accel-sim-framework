# Round A18候选｜Lane M A16R1 Green Context G1文档接口定点修正与数值canary恢复

**设计执行者：ChatGPT／AI-ARCH Discovery；拟执行者：Codex Lane M／node109新worktree。**  
**状态：`PROPOSAL_ONLY / USER_APPROVAL_REQUIRED / NO_GPU_OR_CODEX_LAUNCH`。**  
**性质：** 只修复前A16合同错误引用的`cuStreamGetDevResource`API；同一个NequIP对象、同一SM89设备、一档合法SM quota、同一数值/数据合同；不发任何正式性能、Profiling或硬件机制实验。

## 0. 固定A16 STOP、已经审过的修复依据

- 原A16执行正式STOP [`3dfc5826960ada62548183365d5ad7489f89ae12`](https://github.com/swayhrl/accel-sim-framework/commit/3dfc5826960ada62548183365d5ad7489f89ae12)／tree `4fc624eff43882134e3bad7b2a1cfeda36612259`，科学为`SOURCE_INTERFACE_CONTRACT_GAP / P13_RESOURCE_HEADROOM_NOT_EVALUATED`。原V1R1正常STOP[`1f69559df4f51290589de72876f36a756c5439f0`](https://github.com/swayhrl/accel-sim-framework/commit/1f69559df4f51290589de72876f36a756c5439f0)不变。
- [Round A17独立审查](../reviews/AI_ARCH_ROUND_A17_LANE_M_A16_GREEN_INTERFACE_STOP_REVIEW_2026-10-14_V1.md)已经证明：`cuStreamGetDevResource`不是CUDA12.6官方Green API，原Goal制定错误；设备查询76 SM成功却没有建立quota。Lane M遵循冻结合同STOP正确，旧receipt/164归档不可覆写。
- **冻结官方同版本接口**：[CUDA12.6 Green Contexts](https://docs.nvidia.com/cuda/archive/12.6.0/cuda-driver-api/group__CUDA__GREEN__CONTEXTS.html)、[CUDA12.6 Stream Management](https://docs.nvidia.com/cuda/archive/12.6.0/cuda-driver-api/group__CUDA__STREAM.html)；实际109`nm`日志已经显示`cuStreamGetCtx_v2`、`cuGreenCtxGetDevResource`均导出。
- **唯一允许变更**：G1不再引用`cuStreamGetDevResource`，改用**文档明确且本机已导出的**`cuStreamGetCtx_v2`核stream/green handle关系，结合`cuGreenCtxGetDevResource`核真实SM quota。在使用前静态核函数原型、CUstruct layout与返回状态，不以手写ABI代替CUDA头文件；若不匹配则STOP。
- 原A16合同[Goal V1](AI_ARCH_A16_NEQUIP_GREEN_CONTEXT_109_CANARY_V1.md)和批准记录为历史，**本稿不是那个合同的静默变更，也不会“恢复旧A16已经STOP的进程”**。

## 1. CPU-only预检：最小实现，避免第二次API版本STOP

1. **前提**：需用户再次明确批准本A16R1以后才启动；用户在109将一条连续新Goal发送到原**Lane M Codex窗口**。若无批准，仅本Markdown方案存在，不操作节点。
2. Codex开始独立`hrl/aiarch-a16r1-nequip-greencontext-109-v1`branch/worktree，**拟从原正式STOP提交`3dfc5826960ada62548183365d5ad7489f89ae12`创建**；保留其原`docs/ai_workload_research/review_packs/AI_ARCH_A16_NEQUIP_GREEN_CONTEXT_109_CANARY_V1/`与tools源码/结果不变。新runner、raw、报告只放`A16R1`独立目录。
3. 源码静态验证已有CUDA12.6头文件、`cuStreamGetCtx_v2(CUstream,CUcontext*,CUgreenCtx*)`、`cuGreenCtxGetDevResource(CUgreenCtx,CUdevResource*,CUdevResourceType)`的确切函数签名，与当前驱动可解析符号；禁止假API、`dlsym`后错误强制cast或暗中改CUDA/cu126。
4. 只读核旧输入`sitraj.xyz` SHA256 `c08d3771a06beb82b0ed4258f78eecc7ce623f73ca6df20be99bd5722163e770`、OAM-S包SHA256 `63d4bafd872850a014fd21dedeea416b61173a17750dee0b2b8dd2b126f407aa`、AOT SHA256 `6b4ceb69ebaa7670f5bfdb06e8d0648644b467eec28983fb3d436a18f4f953f7`，旧隔离Python3.11.17/torch2.10+cu126环境；**缺失STOP**，不得重新下载、升级或重新编译旧模型。
5. 源代码/二进制已有就尽量复用，少量薄C++ Driver canary只编一次候选路线；无GPU阶段不安装新依赖，不全repo重构、不清Cache，资源超限STOP。

## 2. 顺序GPU G1–G4，禁止跳门

**GPU前置：** 仅109同一RTX4080 UUID `GPU-ce6cba36-415b-4e27-40e2-bded6bc1ee59`/SM89，非阻塞独占共享锁`/data/c16/locks/c16_gpu_campaign.lock`，锁忙立即`RESOURCE_DEFERRED`。进入任何CUDA API/green context/stream/kernel前均需持锁，所有自有stream/context正确同步并在退出前释放，不reset设备或销毁其它进程资源。

**G1：严格建立stream-bound配额身份。**

1. `cuDeviceGetDevResource`读实际device SM count（原为76，本次不盲信），仅一次`cuDevSmResourceSplitByCount`按CUDA12.6的8.x最低4SM、偶数/架构实际可行alignment指定**一档约半SM**，尊重API返回实际分组与`smCount`；不尝试其它配额排列提高通过率。
2. `cuDevResourceGenerateDesc`→`cuGreenCtxCreate(...,CU_GREEN_CTX_DEFAULT_STREAM)`→`cuGreenCtxStreamCreate`，所有符号使用实际CUDA12.6声明。只保存自有green handle和stream。
3. 必须`cuStreamGetCtx_v2(stream,&normalCtx,&queriedGreenCtx)`返回`CUDA_SUCCESS`且`queriedGreenCtx`**严格等于实际创建的Green Context句柄**；不可把返回的regular/primary context当作green证明。
4. `cuGreenCtxGetDevResource(queriedGreenCtx,&quota,CU_DEV_RESOURCE_TYPE_SM)`返回`CUDA_SUCCESS`，记录quota`sm.smCount`，应与创建的分区资源数量一致且**0<quota<device physical SM count**；不从76物理SM冒充已分配quota，也不把无quota记为0。
5. 若本机版本不支持任一上述函数的正确调用、创建或归属核验，提交实际CUDA返回值并`STOP_G1_PLATFORM_OR_QUOTA`；不绕过证明链转去G2。

**G2：** G1 PASS后仅允许一个最小已安装工具链可编译的Green Stream CUDA kernel（短小、可确定性验输出），验证正确同步及stream/context所有权。按照CUDA12.6规范，执行需要current-context的Driver操作时应先以`cuCtxFromGreenCtx`转换为可设为current的`CUcontext`，采用文档规定的`cuCtxPushCurrent`/`cuCtxPopCurrent`或等价受控配对恢复先前上下文；不得把`CUgreenCtx`直接冒充`CUcontext`，也不得复用外部用户context的所有权。离开前同步并只销毁自己创建的stream/green context。上述函数原型及导出应在CPU预检一并核对。不得运行NCU/NSYS/NVBit/性能profiling/大benchmark。若失败STOP。

**G3：** G2 PASS后，只读取现成torch2.10中`torch.cuda.green_contexts.SUPPORTED`、已允许的早期API和`ExternalStream`包装，验证**NequIP AOT、OEQ、ALCHEMI每类必须GPU操作确实在对应自有Green Context stream/其合法同步链运行**。不因`ExternalStream`接口存在就声称全模型绿流执行。不得monkeypatch现有扩展、改变compiled artifact或model graph、更新全局CUDA/PyTorch、安装其它wheel/升级driver。找不到可审的所有权证据→`G3_INTEROP_UNQUALIFIED_STOP`；Driver G1/G2结果保留，不能自动推G4。

**G4：** 仅G3 PASS，重复旧冻结`Si` zero-based帧0与109，最多2个canary，必要时合法B2；NequIP original model_dtype FP32、TF32/AMP-off、原FP64辅助参数和同AOT/四字段`atomic_energy/total_energy/forces/stress`、原有向周期边multiset、5次double均值和`atol=rtol=5e-5`。对照此前合格V1R1的**相同模型软件参考**，不使用DFT标签冒充bitwise reference。不一致/流归属缺失→`G4_NUMERIC_NOT_QUALIFIED_STOP`，不得更换包或改容差。

**严禁正式性能**：不给任何G1–G4的完成耗时生成`SM_sensitivity`速度比；0 SM quota sweep /0 raw性能重复block /0硬件机制。

## 3. 沿用原A16的保守硬预算，不因新方案放大

| 项目 | 本次上限 |
|---|---|
| 设备与锁 | 109单RTX4080、原共享锁非阻塞；锁占用≤600秒，未授权排队/抢占 |
| GPU显存 | ≤4GiB |
| CPU与主机RAM | ≤4 workers、≤12GiB，按实际阶段记录峰值 |
| 文件/缓存增量 | 新A16R1本地路径≤512MiB，旧A16/V1R1原有资产和全局缓存不变 |
| 下载/安装 | 全部0：不能下载新模型、数据、pip依赖、驱动/工具链或新GPU SDK |
| 执行样本 | 一档SM quota，一次有界kernel验证，至多Si0/109两帧5次均值；正式计时0 |
| 禁令 | 不得跑Accel-Sim、NCU/NSYS/NVBit、Qwen、训练、MD、其它SM比例、跨模型/硬件机制、holdout或C16/AWMA旧任务 |

**新增关键工程防止环**：如果G1合法链已验证，但G3由于框架/库接口无法安全支持旧AOT/流归属，则**结束当前GreenContext可行性探索**，不再连续创建A16R2/A16R3去改Torch/驱动/科学方法。

## 4. 交付与退出

只写独立V1R1结果目录`docs/ai_workload_research/review_packs/AI_ARCH_A16R1_NEQUIP_GREEN_CONTEXT_109_CANARY_V1/`及独立工具目录；记录fixed input/source/driver/ABI/API实际返回、requested and actual SM count、stream与green句柄关系、G1–G4逐门、未执行=NOT_RUN、资源、原始小log及SHA、最终`FINAL_REPORT.md`。`164`如需存放仅创建新小包并回读，不重写旧目录。

Codex提交push执行**独立分支**并远端readback exact commit/tree、SHA后STOP；ChatGPT独立审查后才可能讨论是否进一步科学准入。**未获用户对本A16R1新合同明确同意前，不创建执行branch、不发Codex启动指令、不触发CUDA。**

**提案裁决：`BOUNDED_ONE_TIME_INTERFACE_REPAIR_REASONABLE / NO_AUTOMATIC_GPU_APPROVAL`。**
