# 本轮审查范围、发现与保留缺口

## 1. 本轮实际做了什么

以C16为项目范围，枚举`swayhrl/accel-sim-framework`和`swayhrl/gpgpu-sim`中名称匹配c16的全部分页：282条Framework、9条Core。对主要阶段的终局文件、原有E1/MoE账本、host候选与qualification、最新Lane1/3/6/7交付入口回读，并与用户提供的冻结主handoff/已审报告对照。

70条工作记录覆盖：历史平台/管线6条，trace与早期模型10条，MoE15条，E1主链11条，simulator/机制准备10条，host对照10条，论文/文献3条，独立探索5条。它们是逻辑记录，不是70次独立实验。

没有：SSH到109/174/164、重新启动任何实验、重算全部raw bundle、验证每个当前运行PID、扫描Lane4 active输出、逐行复审282条分支的代码。文献内容以原笔记阅读等级记录，没有在本轮重新外部调研。

因此本轮结果是**全量分支盘点＋主要阶段证据级整理**，不是“所有源文件和所有raw已重新认证”。

## 2. 需要防止历史状态误导后续工作

### A. 旧MoE日志中的E3待执行状态已经过时

`C16_MOE_EXPLORATION_LOG.md`仍保留当时E3 planned/not executed的叙述；后续`378487015e513ed666c0929ca3f6c00392ff11c3`已完成E3。新总账将其链接到EXP01，不修改旧日志正文，不因旧状态再启动相同诊断。[S02/S25]

### B. Host候选表重复，不能多计

`CANDIDATES.tsv`中相同header及整组候选行出现两次。本轮按(candidate,comparison)去重并对照`QUALIFICATION.json`；没有把两份重复文本当成独立repetition。原文件未改。[S35/S35a]

### C. SHiP-SW早期PARTIAL已经被后继资格关闭

`060e48.../49a110...`阶段没有完整SHiP-SW合同；`857abd.../013370...`closeout已补齐。当前应记为四baseline实现合格，但仍无full timing，而不是继续显示唯一SHiP缺口。[S36/已审交付]

### D. Lane5计划已经有Lane7执行结果

Lane5的`MINIMAL_NATIVE_AB_PLAN.md`仍保持当时DESIGN_ONLY，不回写历史；当前总账指向Lane7的`OPERATOR_SPECIFIC_SPLIT_POLICY_ONLY`。不因读到旧plan重新执行split8-vs-1。[S39/S41]

### E. Lane3 binary检查从格式检查修复为精确身份检查

初始prep `06a044...`与修复后`4f45bf...`分别保留。后者为当前入口；继续保留无数值materiality阈值时`REQUIRES_PROJECT_REVIEW`的边界，不临时补阈值。[S37/已审交付]

### F. Lane6相邻non-detection不能扩大成全部时间结构不存在

FINAL_DECISION中的question_answer具体限制在adjacent-set correlation。后续聊天发现lag11候选，属于post-hoc新问题；本轮未见新的终局交付，不用聊天计算替代正式audit，也不据其宣布cache机会。[S40/C0]

### G. 记录数量不代表科学证据数量

不同producer/consumer提交可能是同一批raw的独立检查；variant修复、coordination、transport retry不是新的workload；候选相对不同baseline也不是独立机制。70条总账保留这些区别，291条分支清单仅用于找入口。[B0]

## 3. 保留而不擅自调和的分歧

CUDA targeted persistence的producer给出较积极的design-review状态，strict consumer未通过natural DRAM materiality；raw仍一致。新账本同时保留，不替任一方改结论。[S30]

局部驻留收益与whole-decode无material净收益同时成立，不选其一。Representative attention NCU近乎不变与aggregate self-attention slowdown也同时保留，不替来源发明统一微架构原因。[S31–S34a]

原始SHiP、AutoScratch-style比较与C16适配的训练方式/状态不强行视为同一实现。文献中PIPP参数冲突按LR05保留，本轮不修文献也不新增baseline实验。[S36/S38]

## 4. 覆盖缺口

以下有分支入口，但本轮没有逐个展开其全部source/result/raw：

- 早期3090/AutoDL/retry570各局部恢复、Route-B Q1/Q2和Llama support子版本。
- RTX4080迁移R1–R4各次底层日志、用户态runtime/bootstrap、旧174归档/clean-up的逐文件实体验证。
- 每个模型资产完整性与tokenizer canonical42清单的当前重验证。
- Qwen3 S3 KV V20/V21所有结果文件。若将它纳入论文主张，应补精确producer/consumer内容核读，而不是根据branch名称填写PASS。
- 原source/bin与物理node164 raw当前在盘状态。本轮只读已提交的authority/receipt，不冒充现场复验。

某些早期pack本身只有简短FINAL_DECISION或README。本轮据此记录原标签，不填入其没有披露的性能、容量因果、scale结果。猜测文件名返回404只说明该路径不存在，不说明整个实验未做。

## 5. 不应混入本账本的相邻项目

AWMA地址翻译baseline可以是C16历史source/platform依赖；旧EP-L2/FRC可以提供工程经验，但不是本次C16缓存策略比较的独立performance baseline。DTC-L1/ISCAS及AWMA其他科学分支不属于本轮全项目审查范围，不能把本次C16整理宣称为全部GPU研究仓库的完整复核。

## 6. 发布与维护边界

只向新的work-history分支添加记录。不改原实验branch、主handoff、文献分支、模型、Core、config、catalog或raw。不自动修改被发现有旧状态/重复行的冻结pack。

本账本的SHA/树校验只校验新记录自身的发布一致性；不能把它称为全部历史实验再qualification。更新时采用追加新版本/新行与显式supersedes关系，不删除失败和无收益阶段。
