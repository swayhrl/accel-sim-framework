# 174-new科研工作流安全验证 — 接收与决策记录（2026-10-13）

> **来源与层级**：本文件依据用户转交的174-new Codex验证报告整理，属 `CODEX_REPORTED_VALIDATION`，不是本ChatGPT通过SSH再次执行的远程复验。GitHub配置分支及固定科研来源此前已在ChatGPT侧只读核查。**本文件不产生新的科研执行授权，不表示Skill自动发现和自动调用已通过。**

## 1. 执行身份与资源

- 审查范围：`swayhrl/accel-sim-framework`，bootstrap提交 `289143ffc322c6accda020c8c1617563ff8ce9a9`；报告为独立、干净的约2.1MB worktree，原工作树HEAD未移动。
- 报告环境：174-new根文件系统显示100%使用率（约14GB可用），swap已满；未创建大型文件。
- 报告称未访问109、运行Accel-Sim、下载模型、修改实验、合并分支或改变全局Codex配置。
- 所报告CLI：VS Code扩展自带 `codex-cli 0.154.0-alpha.6.2`。
- 本轮用量：185,708 tokens、9分33秒（报告提供，非独立计时）；之后不应重复做长篇资格烟测。

## 2. 功能资格矩阵（不要互相替代）

| 项目 | 本轮能支持的状态 | 缺少的证明 |
|---|---|---|
| GitHub固定SHA直接读取/核查 | `DIRECT_GITHUB_READ_VERIFIED`（ChatGPT上一轮） | 不是node164大型raw的直接读取 |
| 两个Skill的元数据和参考模板 | `FILES_PRESENT_AND_MANUALLY_APPLIED`（Codex报告） | CLI自动发现/调用未通过 |
| AWMA R27R3固定canary | `SCOPED_AUDIT_PASS`（报告） | 未读node164两个原始tensor；属于 `GITHUB_ONLY_NOT_RAW_REVALIDATED` |
| AI-ARCH P01/P13固定canary | `BOUNDED_PAPER_AUDIT_PASS`（报告） | 只抽核NanoFlow/MPK/Exclusive Batching/Bullet；不是逐篇全文重核 |
| `skill_search` / `multi_agent` / `hooks` feature flag | `ENTRY_VISIBLE`（报告） | 不能推出各功能在远端CLI已经完成运行测试 |
| `codex review --help` | `HELP_VISIBLE`（报告） | 不能推出实际PR/commit审查已经运行 |
| CLI端自动Skill加载 | `UNVERIFIED_AUTH_BLOCKED` | 只读 `codex exec` 在模型请求前因缺少当前配置要求的 `WCLQ_API_KEY` 失败 |
| 本次会话的两位只读子Agent | `SESSION_DELEGATION_REPORTED` | 报告约28次Git读取，结论与单Agent一致且无决定性新发现；无独立token/耗时开销测量，不等于远端CLI子Agent资格 |

## 3. 已审查科学样例的结果边界

**AWMA R27R3**：本轮报告核验Git审查包20/20文件清单哈希，承接[固定独立审阅](https://github.com/swayhrl/accel-sim-framework/blob/d6e9bbfb562814bcd5dc5adb444d3c572e7f446b/docs/vm_tlb/literature_notes/awma/empirical/R27R3_B0_REFERENCE_REPEATABILITY_REVIEW_2026-10-13.md)的有限结论：两个B0 fresh process的BF16完整总梯度25/262,668,288元素违反预冻结逐元素容差；C1/S2组件归因、自然容量和32步未执行。**不**推导B0数学错误、S2失败或硬件headroom。原实验COMPLETE/STOP不变。

**AI-ARCH P01/P13**：对[原有实验组审计固定版](https://github.com/swayhrl/accel-sim-framework/blob/2048f23b1a765393cbf27c3ee413ccae1addcf45/docs/ai_workload_research/literature/AI_ARCH_P01_P13_EXPERIMENT_GROUP_AUDIT_2026-10-13_V1.md)中的若干原文核查无发现的单位/分母冲突，仍需区分模型估算、局部Native、离线执行、实际服务和跨GPU比较。**不**据此断言RTX4080资源扩展性能，也不授权新AI-ARCH实验。

## 4. 现阶段采用方案

1. **日常默认**：直接用ChatGPT-GitHub固定commit只读审查，或让Codex单Agent**明确读取**两份Skill文件及相应模板；这条手动路径已经能用，不以CLI自动发现为阻塞。
2. **高风险独立审查**：仅在具体结论需要不同证据视角时开启两个互不修改状态的read-only子Agent；必须分别约束任务，评估增量发现和重复读文件成本。不作为所有Goal默认模式。
3. **CLI认证**：可在一个新的隔离子进程、已有配置/已有凭据体系下安全修复环境传递（优先复用既有配置，检查变量**是否存在**即可；不输出secret、不写入仓库、不改全局config，不影响VS Code app-server）。若认证不可用，报告 `CLI_SMOKE_DEFERRED` 并停止，不进行长时间重试。
4. **Review/Hooks**：不安装任何持久hooks、不改CLI版本或全局模型、不把hook退出码当科学PASS。只有明确日常节省成本的机械问题时才设计opt-in门禁，优先检查存在性、路径、status和manifest schema，不声称远端raw独立校验。
5. **Branch/authority**：本次bootstrap仅为候选分支。正式传播只允许**选择性移植**AGENTS.md/Skills至未来非运行分支，经差异审查后显式批准。绝不整体merge进入AWMA/C16冻结执行树。

## 5. ChatGPT侧补充仓库检查

- 2026-10-13读到bootstrap head仍为 `289143ffc322c6accda020c8c1617563ff8ce9a9`（写入本receipt前）。
- 同时读到AI-ARCH协调分支的远端head为 `3e6d4e2dd6f3532e87aae9976cf3b9aab20b3763`。二者已经**分叉**，GitHub `compare_commits`显示协调分支相对bootstrap为 `ahead=7`、`behind=2`。故**不应通过简单的整分支merge实现推广**；未来必须先从协调分支的当前HEAD建立新的集成分支，只移植所需配置文件，先审diff。
- 没有再次SSH验证174环境；以上源于本轮GitHub ref/compare与用户转交的Codex报告。

**Decision**：`MANUAL_WORKFLOW_ACCEPTED_WITH_SCOPE / CLI_SKILL_DISCOVERY_UNVERIFIED / NO_AUTOMATIC_PROMOTION / STOP`。
