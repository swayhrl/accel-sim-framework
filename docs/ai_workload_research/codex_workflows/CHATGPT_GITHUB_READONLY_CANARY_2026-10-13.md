# ChatGPT GitHub 直连只读验收（2026-10-13）

**性质：已实际读取固定GitHub文件的只读样例。** 本记录不是在远端Codex运行两个新Skill的验收，也不是GPU/raw独立重算，不授予新实验权限。本轮没有SSH访问109/174/164。

## 可核对操作

1. 成功读取协调分支 `hrl/ai-workload-research-coordination` 的 `README.md`、`CURRENT_STATE.md`、`COORDINATION_PROTOCOL.md`、2026-10-13 AI-ARCH完整handoff、问题图谱和证据索引。
2. 成功读取以下**不可变**来源，并记录审查口径：
   - [AWMA R27R3独立审阅（commit d6e9bbf）](https://github.com/swayhrl/accel-sim-framework/blob/d6e9bbfb562814bcd5dc5adb444d3c572e7f446b/docs/vm_tlb/literature_notes/awma/empirical/R27R3_B0_REFERENCE_REPEATABILITY_REVIEW_2026-10-13.md)
   - [AI-ARCH P01/P13实验组审计（commit 2048f23）](https://github.com/swayhrl/accel-sim-framework/blob/2048f23b1a765393cbf27c3ee413ccae1addcf45/docs/ai_workload_research/literature/AI_ARCH_P01_P13_EXPERIMENT_GROUP_AUDIT_2026-10-13_V1.md)
3. 通过GitHub独立bootstrap分支发布了两套Skill、精简AGENTS.md和174-new的验证Goal，并比较原协调HEAD到bootstrap commit的文件清单（仅新增工作流配置）。

## A. AWMA来源中的实际科学结论

**观察：**独立审阅接受R27R3的 `R27R3_B0_REFERENCE_NOT_REPEATABLE` STOP。相同R26 CPU起点、固定R27R2 WikiText-2 bank step k=0、B=1及相同数值合同条件下，两个独立新进程B0的完整BF16总梯度 `[128256,2048]` 有25/262,668,288个元素越过原始逐元素 `atol=rtol=1e-2` 门槛，其他规定检查通过。

**结论边界：**本次读取的是GitHub上已完成的独立审阅，而非亲自重新读取164上的两个约3.15GB张量并执行独立逐元素比较。审阅自身也明确限定了其重算范围。因STOP，C1/S2组件归因、自然容量及32步没有运行；不能把B0本身重复性失败解释为B0数学错误、S2正确性负例、训练容量结果或硬件瓶颈。

**本轮标签：**`GITHUB_ONLY_NOT_RAW_REVALIDATED`；`ACCEPT_EXISTING_SCOPED_REVIEW_AS_REPORTED`，不是新scientific acceptance。

## B. AI-ARCH P01/P13文献审计中的实际证据层次

协调文档明确把以下内容拆分成不同的**作者论文实验组**（本轮未重新下载和逐页二次核对这些论文）：

| 作者论文组 | 协调文档登记的证据层级 | 不可省略的解释边界 |
|---|---|---|
| NanoFlow NF-01 | MODEL_ESTIMATE | 理论资源下限/比值分析；不是RTX4080上实际stall周期 |
| NanoFlow NF-03 | NATIVE_SERVING_OFFLINE | A100离线吞吐；真实长度数据不等于自然到达时刻重放 |
| NanoFlow NF-04 | NATIVE_SERVING_WITH_SYNTHETIC_ARRIVALS | GPU上真实服务时间，指数分布请求间隔为人工生成 |
| MPK MP-01 | NATIVE_OFFLINE_BENCHMARK | 多GPU世代和batch系统对照；不等于SM数的单变量扩展实验 |
| MPK MP-03 | NATIVE_MULTI_GPU | H100 TP2/4/8系统比较；与弱PyTorch基线的大数值不能替代与强系统基线对照 |
| MPK MP-06 | SOURCE/INTERNAL_NATIVE | 可作寄存器/任务边界的源码约束线索，尚不是独立扩寄存器的资源敏感度实验 |
| Exclusive Batching EB-03 | NATIVE_SATURATED_SERVICE | 相同vLLM build的饱和服务比较，模型/硬件/策略交互；不能简化为“低带宽GPU一定更适合EB” |

**本轮标签：**`SECONDARY_COORDINATION_DOCUMENT_READ`; source paper recheck `NOT_PERFORMED_THIS_CANARY`。这证明GitHub直连可给科研讨论提供有边界的固定来源，不证明我已对这七组原始PDF重新验算。

## C. 交付与未做项目

- **成功**：GitHub fixed-file read、跨项目状态查阅、独立分支/单commit 8文件提交与远端fetch-back/ref验证。
- **尚未验证**：174-new Codex发现仓库Skills；具体CLI版本的subagent、`codex review`、hooks API；Codex双Skill的实际使用质量。
- **明确未做**：远端进程检查、GPU/模拟器运行、raw SHA重算、模型下载、全论文原文重读、旧实验重启、Git merge、长期配置修改。

下一个合理动作是让174-new执行本目录 `CODEX_174NEW_SAFE_VALIDATION_GOAL_V1.md` 的有限CPU-only验收，在相同固定来源上检验两个Skill，而不是新开科学实验。
