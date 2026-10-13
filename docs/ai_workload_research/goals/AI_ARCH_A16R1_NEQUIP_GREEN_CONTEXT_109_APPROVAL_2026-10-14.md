# Round A18｜Lane M A16R1一次性CUDA12.6 G1接口修正与条件性数值canary——用户批准记录

**日期：2026-10-14（本AI-ARCH主窗口）。**  
**协调与后续独立审查执行者：ChatGPT／AI-ARCH Discovery；实际拟执行者：Codex Lane M／109。**  
**状态：`EXPLICIT_USER_APPROVAL_A16R1_ONE_SHOT / PREPARED_NOT_LAUNCHED / ZERO_PERFORMANCE_AUTHORIZATION`。**

## 1. 审批事实与权威链

用户收到[A17独立审查](../reviews/AI_ARCH_ROUND_A17_LANE_M_A16_GREEN_INTERFACE_STOP_REVIEW_2026-10-14_V1.md)及[A16R1固定修订提案](AI_ARCH_A16R1_NEQUIP_GREEN_CONTEXT_109_CORRECT_G1_PROPOSAL.md)之后，明确回复“同意”。**此回复批准提案中已经说明的单次有界G1接口修正，并在G1/G2/G3顺次资格PASS时继续G4 NequIP数值canary。** 没有授权任何正式性能测试或其它候选任务。

- 审批前协调分支固定提交：`c006bdbfb2cb8323d428d07d5f158d6e1080e0b6`。
- A16R1技术合同（当时标为`PROPOSAL_ONLY`）Git blob：`4c96cd4026523274bfbb8fc621bff8808675109d`。**批准仅改变执行权限，不更改合同技术条款、模型、验证门和预算**。该文中的“需要批准”是历史设计状态，以本条独立审批记录为最新授权状态。
- 原A16最终合法STOP：[执行`3dfc5826960ada62548183365d5ad7489f89ae12`](https://github.com/swayhrl/accel-sim-framework/commit/3dfc5826960ada62548183365d5ad7489f89ae12)，tree `4fc624eff43882134e3bad7b2a1cfeda36612259`，`G1_INTERFACE_CONTRACT_GAP / STOP`；旧运行branch`hrl/aiarch-a16-nequip-greencontext-109-v1`不能重新启动或改写。
- 新独立执行branch预定`hrl/aiarch-a16r1-nequip-greencontext-109-v1`，**从原A16合法STOP固定提交`3dfc5826960ada62548183365d5ad7489f89ae12`创建**；与协调提交分开fetch。只有用户在109的Lane M窗口发送新Goal后才算实际启动。
- 原更早NequIP V1R1原生执行[`1f69559df4f51290589de72876f36a756c5439f0`](https://github.com/swayhrl/accel-sim-framework/commit/1f69559df4f51290589de72876f36a756c5439f0)已独立审查接受的科学结果/原封装及164档案不改变。

## 2. 唯一获准改动与四个验证门

- **G1版本接口修正**：去掉原合同指定但CUDA12.6不可用的`cuStreamGetDevResource`，采用[官方CUDA 12.6 Green API](https://docs.nvidia.com/cuda/archive/12.6.0/cuda-driver-api/group__CUDA__GREEN__CONTEXTS.html)的分区/资源查询和[官方Stream API](https://docs.nvidia.com/cuda/archive/12.6.0/cuda-driver-api/group__CUDA__STREAM.html)的`cuStreamGetCtx_v2`；须以实际Cuda12.6头文件检查ABI和Driver返回码，以与新建`CUgreenCtx`**句柄相等**和`cuGreenCtxGetDevResource`读回真实配额建立G1资格。仅一档约半数合法SM配额，当前物理76SM不等于已分配quota。
- **G2**仅在G1 PASS之后：一个最小的合法Green stream小kernel，必要的`cuCtxFromGreenCtx`/current context设置与恢复、输出与同步，严格所有权与自有资源清理。
- **G3**仅在G2 PASS之后：核实际现有torch2.10+cu126、OEQ/ALCHEMI/AOT的Green stream/context接管证据；不能只用`ExternalStream`存在或`SUPPORTED`声明替代已执行的stream归属。兼容性不明、需要换软件/重编旧AOT时STOP，不得继续迭代R2/R3。
- **G4**仅在G3 PASS之后：复用旧OAM-S包、旧AOT SHA与原Si零基帧0、109，五次输出double均值，原`model_dtype=float32`及FP64辅助原样、TF32-off/AMP-off、`atol=rtol=5e-5`与四字段能量/力/应力、周期边多重集合与单位；未取得数值PASS绝不晋升性能或硬件主张。

## 3. 不可扩大硬预算及旧项目冻结

| 项目 | 允许范围 |
|---|---|
| 设备与共享锁 | node109唯一RTX4080（冻结UUID/SM89），`/data/c16/locks/c16_gpu_campaign.lock`**非阻塞独占**，锁忙DEFER；GPU锁持有≤600秒 |
| GPU显存 | ≤4GiB |
| CPU/RAM | ≤4 CPU workers、≤12GiB RAM |
| 新文件/缓存 | 新A16R1独立路径累计≤512MiB，旧A16/V1R1资产、模型、AOT、依赖及全局缓存只读 |
| 下载/安装 | **全部零**：不下载权重、模型、输入、wheel，不`pip install`或更换驱动/工具链/PyTorch |
| 执行上限 | 一档SM quota、一次短小kernel验证、至多2帧×5次输出均值；**0正式计时block、0 SM扫参** |
| 明确未授权 | NCU/NSYS/NVBit、Accel-Sim、训练、MD、Qwen、其它模型/holdout、新硬件机制、C16/AWMA旧项目恢复或任意新GPU campaign |

正常完成或任一门STOP后保存独立V1R1 raw/小report、SHA和164小包回读（仅在旧权限下新目录），commit/push独立branch、远端fetch-back后STOP；**不merge协调分支、不自动再次启动。**

**授权标签：`A16R1_SCOPED_ONE_TIME_API_FIX_AND_CONDITIONAL_NUMERIC_CANARY_APPROVED`。本Git记录不意味着Codex在node109已运行、Green quota已建立或任何G2–G4已经PASS。**
