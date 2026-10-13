# Round A16｜用户同意的小型NequIP Green Context API与数值资格审查记录

**记录执行者：ChatGPT／AI-ARCH Discovery；日期：2026-10-13。**  
**执行者：Codex Lane M／109，复用旧Codex窗口但必须用新branch/worktree。**  
**状态：`USER_APPROVED_DIRECTION_AND_NARROW_CANARY / NOT_LAUNCHED / NO_TIMING_OR_MECHANISM_APPROVAL`。**

## 精确批准范围

- 用户在A14–A15最新报告提出“选择科学对象，必要时一次很小的109 Green Context API和数值资格检查；优先NequIP低成本原对象、不立即Qwen”的建议后，明确答复**“同意”**。
- 本窗口据此选择单对象C14-01：**之前已验证的NequIP OAM-S与两帧Si canary**，不涉及另一个Qwen模型、数据集、权重或新理论机制。
- [唯一科学执行合同](AI_ARCH_A16_NEQUIP_GREEN_CONTEXT_109_CANARY_V1.md) Git blob `4e00b0b3f3857cc11ee5b41771fc918fd3644153`，已由本窗口设置比旧A9更严的**自限资源上限**：仅一张109 RTX4080、一档约半数SM配额、GPU锁≤600s、显存≤4GiB、RAM≤12GiB/CPU workers≤4、本地增量≤512MiB、下载安装=0，仅绿流微canary与最多两帧五次均值数值校验；不开展任何性能比较或正式重复采样。
- **此记录不把用户同意泛化为所有将来的GPU实验**；若实地检查发现需要升级原环境、重编模型、替换AOT、改变数值/驱动或扩大时间/数据，需要另审，STOP。任何实现与平台不兼容也按证据STOP，不试多版本/多平台矩阵。
- 必须非阻塞取得共享GPU锁`/data/c16/locks/c16_gpu_campaign.lock`后才能执行CUDA API；锁忙立即DEFER，不能破坏GPU并发安全。
- 原Lane M V1R1 [`1f69559df4f51290589de72876f36a756c5439f0`](https://github.com/swayhrl/accel-sim-framework/commit/1f69559df4f51290589de72876f36a756c5439f0)与更早V1均已STOP且不可修改；新A16仅在独立分支`hrl/aiarch-a16-nequip-greencontext-109-v1`提交结果。
- 旧174 Lane T/N、C16、AWMA所有独立权威与终态保持原状。该GitHub批准记录**不表示Codex已经被启动或109 API资格已经通过**；只有用户向Lane M发送新的Goal后才有执行状态可报告。

**授权分类：`SCOPED_LOW_BUDGET_API_NUMERIC_CANARY_ONLY`。不授权性能扫参、SM实际扩容实验、NCU/NSYS、模型下载或硬件机制开发。**
