# Q1 独立科学审阅（CPU-only）

2026-11-09。审阅结论：**接受为有边界的真实晚期原生窗口证据**；不接受完整训练质量等价、逐 bit 数值等价、GPU 硬件瓶颈或 PPA 收益的升级表述。执行报告已发布，本文件是独立审阅，不改旧实验终态。

## 固定身份与方法

交接 `00abf55d44ad02a18d529eb0afe4d02dc0ceadfe` / tree `37023a6d5f5966463d9ec1f2c01f2a167f81f516`；Q1 `5787826ca21f7af958e6e1c1f828d62fd58a1ec4` / tree `a070243a93fee5594dd88d515f08e228677ebf75`。两者从 `origin` 重新 fetch 核对。协调分支实际 HEAD 仍为 `66b2dffc6141edf1c9f9f089091b3922556583f1` / tree `c9491cbc37d41c2155218763bf215615ef72b39b`。

独立脚本 `q1_independent_recompute.py` 只以标准库读取固定 Q1 Git blob：`FORMAL_SAMPLES.tsv`、`FORMAL_ANALYSIS.json`、`NATIVE_INPUT_WINDOW_IDENTITY.json`、`COST_LEDGER.json`、`DIAGNOSTIC_ANALYSIS.json`。输出 `Q1_RECOMPUTED_STATISTICS.json`。没有 import 旧 worker/supervisor，未读取活动 raw、私有 state 或启动 CUDA/NVML。审阅其余项目使用固定公开 JSON、源码静态阅读和结束收据；不声称独立重测 GPU 或重新哈希约 19.5 GB 私有状态。

## 独立复算与接受范围

| 检查 | 独立结果 | 判定 |
| --- | --- | --- |
| 正式样本 | 20 行、job 唯一，四格各 5 次；`valid=True`、51 实际步、N=6,720,398；round 3–7 每轮 T8/T16 成对且顺序交错，无正式样本筛除 | 通过公开 TSV 的完整性检查 |
| 发现 T8/T16 | 中位数 8.6833069306 / 7.6291784169 秒；MAD 0.0508074863 / 0.0261692470 秒；T16 相对 T8 降低 12.1397127% | 与发布统计一致 |
| 验证 T8/T16 | 中位数 8.7396176877 / 7.6790669160 秒；MAD 0.0374065228 / 0.0550388182 秒；T16 相对 T8 降低 12.1349790% | 与发布统计一致 |
| camera | 同 phase 全部正式样本 SHA 一致、各 51 ID；发现与验证 ID 交集 0；同一 Rubble scene | 通过公开身份记录检查；不是跨 scene 验证 |
| 数值 | 初始 semantic exact 与有限性在固定收据中；20 个终态指纹不相同，样本数值敏感 | **不**升级逐 bit/质量等价 |

T16 是原接受基线；12.14% 是相对 T8 的窗口时延差异，并非相对原基线的新加速。T8/T16 是 OMP cap，Torch intra 请求仍为 64，亲和集合 8–21 共 14 logical、10 topology core ID，CPU 非独占；不能解释成 8/16 个独立物理核。仅有 50 目标 camera + 1 closure 的两段自然晚期窗口，不外推 200000 步训练。

## 状态、credit、计时和归因审查

- `SOURCE_AND_INPUT_IDENTITY.json` 绑定 GS-Scale/Rubble downscale4、原 trainer SHA `17e70b64…`、CPUAdam binary SHA `c451fda9…`、`max_steps=200000` 与 `refine_stop=15000`。工具实际入口在 `util/ai_workload_research/q1_3dgs_completion/`；原实验 worktree 在 `/home/huangrulin/workspace/worktrees/accel-sim-aiarch-q1-completion-109`，热资产仍在 `/data/c16/aiarch_a26gr1_gsscale_rubble_109_20261014`。`MEASUREMENT_BOUNDARY.json` 中 `PREEXECUTION_FROZEN_BOUNDARY_NOT_RUN` / 0 formal 是冻结时历史字段，不能代替最终 `RECEIPT.json` 与正式 TSV。
- `STATE_AND_NUMERIC_CONTRACT.json` 与 `STATE_INDEPENDENT_INSPECTION.json` 记录 `C_D(next15140)`、`C_V(next15240)`、`C_FINAL(next15301)`，每态 44 Tensor、35 完整浮点字段有限、chunk/metadata SHA PASS；固定 W2 收据记录实际 GPU 重载。末态 frontier 为 GPU processed15300、CPU applied through15299、pending15300、prepared15301。目标 15250–15299 的更新 credit 已闭合，但下一 camera 所需 pending 保留；不称全数学队列为空。此次未独立读大状态，接受的是这些固定收据的有界证据。
- 正式 OFF 与三个 ON 诊断分池。脚本重新核 ON 主线程已分类 Host **并集小于闭合窗口**、显式 join/sync 并集小于主线程并集，且 ledger 算术一致：发现 T16 Adam+参数转发 75.5867%，验证 T16 74.6992%；显式 join/sync 分别 0.1654% / 0.1040%。发现 T8 ON 的 Adam+转发 77.4979%。这些是主线程路径的部分归因，ON 不能充当 OFF 的精确成本分解，也不能把局部区间之和当无重叠全窗口收益。当前脚本核对的是已发布并集与算术，未从每个原始 Host interval 独立重建并集。
- 三组 ON GPU 事件跨度各 51 个值的中位数与 ledger 一致，发现 T16 为 27.0961 ms、验证 T16 为 25.6135 ms。事件含 launch gap；Host monotonic 与 GPU event 时钟未校准，不能相减求纯 GPU 时间。发现 T16 的 H2D/D2H 约 8.4505/9.3432 GB 是 Tensor 调用逻辑 operand，不是 DMA、PCIe 或 DRAM 计数。CPU 计算/访存、真实链路服务及 SM/DRAM 限制仍未闭合。`NO_HARDWARE_CANDIDATE_PROMOTED` 维持。

## 共享资源和工程收口审查

固定源码 `process_observation.py` 对自身消失线程的 affinity 只在 `ProcessLookupError`、两次 task 路径消失、parent/root/worker 健康且无其它 gap 时记 `None/censored`；活线程不可读或身份冲突走 gap/STOP。`q1_supervisor.py`、`terminal_protocol.py` 的 READY 绑定 worker 身份与结果 hash，检查 GPU quiescent、live 资源后 ACK，读取真实退出码和 charged before/after，再确认 context 清理。静态控制流与 W2 收据相符；此次没有运行旧监督器回归。

W1 原 `RESOURCE_RECEIPT.json` 仍是 `RESOURCE_STOP`，不改成 PASS。W2 32 个 job 完成后状态 `NATIVE_Q1_MATRIX_COMPLETE`，整体根 `RECEIPT.json` 为 `NATIVE_Q1_LATE_PIPELINE_COMPLETE`。W1/W2 各持共同锁 2182.335/2354.855 秒，共 4537.190 秒；固定资源记录显示自身 context、锁和预约已清。W1 affinity censored 6 个且存在 2 个实际 gap；W2 终止握手区间累计 27.204 秒缺连续 tree RSS 采样，只有 kernel charged peak 保留。共享 desktop 逐进程活动遥测和非独占 CPU 条件仍限制无干扰结论。`RESOURCE_AND_INTEGRITY_NOTES.md` 已披露 W2 CPU 计划器路径错误曾覆盖根目录两个控制元数据文件；本审查不把它们当原 W1 冻结计划，依据原队列、事件和实际收据。

## 独立判定与未决

可接受：固定输入与完整恢复的两段晚期窗口中，T16 比 T8 的完整 OFF 时延低约 12.14%；已测 ON 主线程成本主要位于 CPU Adam 与参数生产/转发，显式 join/sync 很小。不能据此升格完整训练质量/数值等价、CPU 子瓶颈因果拆分、GPU 硬件资源因果或芯片收益。原 V1/R1/R2 STOP、W1 STOP 和当前数值差异都保留。若 AI-ARCH-5 要求重新从原始 Host interval 重建并集或完整私有状态审计，那是额外证据任务，当前独审没有把它们写成已完成。

本审阅建议交 AI-ARCH-5 做科学终审；协调状态修订仅见独立提案，不直接修改协调分支。后续 GPU 资格仍为 `NO_GPU_PROBE_READY`，直到有明确新任务、冻结输入/质量/强软件及当前资源窗口。
