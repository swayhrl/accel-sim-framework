# Round A9｜Lane M V1R1唯一依赖打包例外与有界109恢复——明确批准记录

**执行者：Codex Lane M／node109，独立新worktree；独立科学审查：ChatGPT／AI-ARCH Discovery。**  
**批准日期：2026-10-13。状态：`USER_EXPLICITLY_APPROVED_A_AND_B / EXECUTION_NOT_YET_LAUNCHED / V1_STOP_PRESERVED`。**

> 用户已在AI-ARCH主窗口针对上一轮[完整V1R1方案](AI_ARCH_NEQUIP_STATIC_BATCH_DISCOVERY_109_V1R1_WHEEL_EXCEPTION_DRAFT.md)明确回复“同意，批准”。本记录同时授权下述**A项和B项**。方案正文中`DRAFT / 需审批 / PROPOSAL_ONLY`是批准前的历史标注；**此固定批准记录是本次执行时该状态的唯一后续更新，不修改原方案技术边界**。写入Git并不表示GPU已执行。

## 1. 唯一科学对象与严格起点

- 原V1固定科学合同：[AI_ARCH_NEQUIP_STATIC_BATCH_DISCOVERY_109_V1.md](AI_ARCH_NEQUIP_STATIC_BATCH_DISCOVERY_109_V1.md)，blob `0101a33c27090ee5ef4f0f29ad5d98b492e6280b`。
- V1原合法STOP执行：[`06674a961632c107681ac146d735d932dde112d6`](https://github.com/swayhrl/accel-sim-framework/commit/06674a961632c107681ac146d735d932dde112d6)，`ENVIRONMENT_BLOCKED/NOT_EVALUATED/COMPLETE_STOP`；[独立review](../reviews/AI_ARCH_ROUND_A8_LANE_M_ENV_STOP_INDEPENDENT_REVIEW_2026-10-13_V1.md)。不得在旧V1执行branch写入新的运行样本，也不得改写任何归档。
- 技术边界采用[AI_ARCH_NEQUIP_STATIC_BATCH_DISCOVERY_109_V1R1_WHEEL_EXCEPTION_DRAFT.md](AI_ARCH_NEQUIP_STATIC_BATCH_DISCOVERY_109_V1R1_WHEEL_EXCEPTION_DRAFT.md)，提交前blob `60c50c55c1173441b4cd83cbeb166baf7e38b7e7`，不因批准变更其科学对象、后端、精度、输入、条件或预算。
- 专用执行分支：`hrl/aiarch-nequip-static-batch-109-v1r1`，从**原V1 STOP提交`06674a961632c107681ac146d735d932dde112d6`**创建，保留旧准备代码/证据但不得覆写；新产物必须进入新V1R1子目录。
- 原`Lane N`仅指174-new已完成的非LLM源审，`Lane T`指174-new已完成的训练源审；本次GPU执行窗口正式为**Lane M（109）**。不启动新的174或AWMA/C16任务。

## 2. 本次用户明确批准的两项

### A项：唯一sdist→wheel构建例外（CPU-only）

- 唯一允许例外：官方PyPI `antlr4-python3-runtime==4.9.3` 的 `antlr4-python3-runtime-4.9.3.tar.gz`，发布SHA256 `f224469b4168294902bb1efa80a8bf7855f24c99aef99cbefc1bcd3cce77881b`；117,034 bytes。
- 经SHA、归档安全与来源检查后，**在隔离CPU环境只尝试一次**使用冻结Python3.11.17和现有build依赖本地构建wheel。不得换版本、换包源、取第三方wheel、改Hydra/OmegaConf或重新解析82个冻结版本。
- 生成wheel需记录来源sdist hash、构建命令、依赖版本、wheel tag/metadata/文件hash、隔离导入验证，并**额外写V1R1派生wheel锁**，不得篡改原`RESOLVED_REQUIREMENTS.lock`或冒称wheel哈希等于sdist哈希。
- 在任何CUDA/JIT前检查全部其余冻结普通叶依赖的wheel可用性；若第二个非批准的sdist缺口、构建失败、来源/数值不符合，按方案保存结果后STOP。**A门不通过，B项绝不启动。**

### B项：A资格通过后的有界109 GPU恢复

- 执行原V1剩余的固定输入与模型身份、NequIP/OEQ原生模型加载、一个batch AOT编译产物、canary、全体正式输入数值/有向周期边集合检查、N-C2/N-G2/N-G4/N-G8四条件计时（3 fresh process×12完整blocks，144样本计划）、诊断、自检、164小包归档与最终STOP。
- 继续遵守原`FP32 / TF32-off / 5次均值 / atol=rtol=5e-5`与energy/force/stress合同、固定Si 32帧以及单OAM-S:0.1文件；不换模型/修算法/降低精度/放宽容差/启用额外holdout。
- 任何可能触发GPU CUDA/JIT/编译前必须**非阻塞获取原共享锁`/data/c16/locks/c16_gpu_campaign.lock`**；锁忙则DEFER，不删除/绕过锁、不抢占别人。只有本任务获得许可与锁、A门通过时才开始B。

## 3. 原累计硬预算不重置

| 项目 | 审批上限与剩余 |
|---|---|
| 依赖下载累计 | V1+V1R1合计≤8GiB；前轮已保守记`3,333,112,827` bytes，本次最多再计`5,256,821,765` bytes（约4.90GiB） |
| 模型与几何 | 仅原OAM-S文件及Si；前轮字节身份已报告PASS，优先只读复用；总12MiB旧上限不重置 |
| 磁盘 | 本任务所有增量累计≤25GiB（含原轮约1.25GB）；开工前可用≥35GiB，全程至少留8GiB |
| CPU/RAM | ≤8 CPU worker、≤32GiB，记录解析/构建/安装和执行内存；前轮整体resolver RAM未测，不推定已PASS |
| 109 GPU | 原单RTX4080，峰值显存≤12GiB；GPU锁持有累计≤90分钟（V1实占0秒）；正式观察阶段累计≤15分钟 |
| 结果 | 原raw/log≤256MiB，上轮正式样本为0；按新独立receipt追溯 |
| 全面禁止 | NSYS/NCU/NVBit、Accel-Sim、MD、训练、额外模型与大数据、driver/全局CUDA升级、旧C16/AWMA任务、并发GPU campaign |

允许按原V1规定有限解决确定性的路径/manifest包装小问题，但不得借“修环境”扩大科学合同或重试多套Python/torch依赖矩阵。预冻结FAIL-CLOSED，正常完成或任何STOP均只交付有证据的有限结果。

## 4. 执行与审查界面

- 本批准覆盖**一个**独立Lane M V1R1 Goal：A门及条件B门**顺序连续执行**，不为包构建与正式canary反复开窗口。每一步均保留独立状态和STOP证据。
- Codex仅向`hrl/aiarch-nequip-static-batch-109-v1r1`提交、push，远端readback并报告精确commit/tree、packaging gate、numeric gate、四臂样本、资源用量、164 receipt和最终结论；**不得合并协调branch、自动开始新Goal或直接晋升硬件机制**。
- ChatGPT收到结果后依据实际Git提交进行独立科学审查；Git记录和用户文字并不等于当前109实时运行证据。只有用户将启动指令实际发给Lane M，才记录`USER_REPORTED_LAUNCHED`。

**授权裁决：`EXPLICIT_APPROVAL_V1R1_A_AND_B`。本记录仅许可上述一次最小打包例外及门控的有限109恢复，不代表V1历史STOP改变。**
