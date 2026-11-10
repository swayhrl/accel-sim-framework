# DTC 论文补证与 Short-Collect Native R0 复核

日期：2026-11-10。本文件补充 [首轮文献报告](LITERATURE_REPORT.md)，并记录本次正式授权的 R0 准入工程。论文母稿和外部 PDF 只在本机阅读；英文 v0.23、历史科学产物和原 HOLD 未修改。新科学 request、UUID、模型启动和预算消费均为 **0**。

## 1. 文献来源等级向前更新

本机 `D:/Downloads/DTC_ISCAS2027_HANDOFF_BUNDLE_2026-10-21_AG8R1_PAPER_V023.zip` 原字节 SHA256 为 `a6afbf0d803d520a5451b4678ceab26afbea27067e69d642defebf5136872a25`，外包 manifest 10/10 通过；其内英文 LaTeX v0.23 ZIP SHA256 为 `71b0982852984e4300a7ea40131dbb6a545517374e04fdeb0ca8b7deeddb0940`。包内 `START_HERE.txt` 把它指定为**2026-10-21 交接时**的权威母稿。已读取 README、五个正文 section、references.bib、citation map 和 v0.22 文献审查；这确认首轮报告“尚未读到 v0.23”的检索空缺已补上，**未证明 10 月 21 日之后不存在新版本**。私有母稿源码及原始会话均不纳入 Git 审阅包。

v0.23 Related Work 已引用 Decoupled L1D、DL-MSHR、MiCache、DC-L1、LoTUS 等；其 `related_conclusion.tex` 与 `references.bib` 未找到 Tag-Split 和 Elastic-Cache。此处是引用覆盖核查，不是要求直接改冻结稿。未来修稿前应按原文逐句判断：Tag-Split 的 shared/private tag、chunk mask、扩展 MSHR 与 DTC 的逻辑 Tag/physical 重命名、PIB/Ref/generation 生命周期是否构成真正的机制差异；Elastic-Cache 仍待全文核证，不宜照摘要补具体实验数字。

本机 `D:/Downloads/Tag-Split Cache for Efficient GPGPU Cache Utilization.pdf` 为 12 页，SHA256 `86608f21284bfa8d3f476b8f58048ef43343b8386d206b00bf7e582ff9a0de0f`。原文第 7–10 页解释 TSC/TSC+；第 8 页报告其平台和工作集上的 GM：TSC **15.6%**、TSC+ **17.2%** 相对作者基线改善；第 9 页说明 32B chunk 虽减少部分带宽和空间浪费，却可破坏 `srad_v1` 等的空间局部性，且固定细粒度的 `histo`/`srad_v1` 有 miss 回退。TSC+ 的粗细粒度选择可缓解，但训练/采样也有代价；第 10 页表 3 报告 TSC/TSC+ 各约 **0.58 KB** 的该实现 metadata。该论文与 DTC 均面对“细粒度减少过取却可能损失局部性”这一共同风险，**其百分比和成本不能换算为我们的 CORE32 GM、面积或收益预测**。

Elastic-Cache（DOI `10.1145/3322127`）的 ACM 全文入口仍返回 403；OpenAlex 和 Semantic Scholar 只指回 ACM/DOI。已作有界作者版检索但未取得可信全文，因此它仍为**摘要级**证据。首轮报告其余 18 篇的阅读等级保持原记录：元数据/摘要、重点段落 PDF、远端历史笔记不能混称全部全文已读。

## 2. 与本项目冻结观察的综合判断

CORE32 Oracle 的 32×4、96 对和 M/L2/L1 GM `1.676758525810 / 1.280648684508 / 1.939911577005` 是固定 trace 的受控反事实；L2 有 19 正、11 精确零、2 负，`myocyte +2` 与 `srad_v1 +14,652` 周期原样保留。Tag-Split 的 `srad_v1` 局部性反例与我们的 L2 回退仅是**同名负例线索**，平台、方案、binary、输入和因果路径不同，不能合并为一项重复验证。历史 F128 改善、F256 回退和 Tag `NO_FREE_LINE` HOLD 进一步提醒：更多容量或更细粒度并非单调收益。

对 Short-Collect 候选，最先需证伪的仍是正常有限路径中的自然 `eligible_choice_different>0`，随后核被延项、公平性、WB/retire-backed 完成与同一冻结 binary 的实际 OFF/ON 周期。与 TSC/TSC+、APCM、CLAMS 等比较时，应按**作用点与资源成本**对照：data/tag 粒度、load 准入和 collect 顺序不是同一干预；别把别人的 GM 作为候选目标。PPA、native 数值/capture、跨 kernel coherence、等面积与更广输入均仍需各自独立资格。

## 3. Fresh R0 资源与工程裁决

执行根为 174-new `/root/data/dtc_short_collect_native_discovery10_v1_20261109/`；冻结候选 Core `9a0de9b9f97144f481b3e3637e329ebab01acb74`、合同 `dfd6d7aa0383b8fda9ff08672f8c9efc392df26f` 保持。只读快照见 [R0_FRESH_ADMISSION.json](R0_FRESH_ADMISSION.json)。快照在 **2026-11-10 15:14:56 UTC** 取得，磁盘可用量随其他合法工作变化，不能当长期配额。

当前 Native registry SHA `04f11b84af86728dd854a5734622839e15f6e84052def40de0fc4c0a2732d1d2` 与 epoch SHA `cdeba85077011afe7de72df4282f69120b1cccb7481fa1c3cd974506e350ab92` 在锁内一致，epoch 2、72 个已登记 request；Short-Collect C1 仅是 `a5343229...` 的**准备稿**，registry 中不存在该 request。冻结 binary `a9ec6f...`、私有 libcudart `43b3dc...`、271 effective options、GESUMMV 输入绑定与 true164 trace 均通过本轮只读复核。

Native peer 保证（按当前 `route_guard.peer_reservation` 规则，包括历史静态 RUNNING）为 **78,512,501,732 B**；首格结果加恢复及临时窗口 **1,610,612,736 B**，5 GiB 底线 **5,368,709,120 B**，故本轮 guard 的严格门槛为 **85,491,823,588 B**。15:14:56 UTC 可用 **19,534,192,640 B**，差至少 **65,957,630,949 B** 才能满足严格大于。此为**准入保证差额**，不是已证明的真实未来写入量，也不是已写入 df 的物理字节；前次 owner 关账释放的承诺不能再当磁盘实际释放。占额最大的四个未闭合项是 V100 `37,580,963,840 B`、MLP `25,769,803,776 B`、Stage II-A Remaining48 `9,395,240,960 B`、Oracle initial8 `4,155,880,420 B`。不能擅自关闭它们或削弱 guard。

true164 已挂载且接收端约 **42.2 TB** 可用；旧 guard 对专属目标目录尚未创建直接失败。已在隔离工具修正为只读检查最近**已存在的真实 164 祖先目录**，同时限制目标解析路径仍在 164 挂载内。原 `route_guard.py` SHA `dfc1e206...` 已保存为 `route_guard_20261109.py`；修正后的 SHA `06195cc1...`。新回归 2/2 和原 guard 5/5 通过，均不启动模型；目标归档目录仍未创建，164 写入 0。该修正只消除了虚假的路径错误，不改变 Native 资源 HOLD。

R0 的生产 dispatcher/launcher、真实 parent lease→PID/maps→私有 loader 闭环和 true164 正路径 SOURCE_KEEP/typed restore 仍未取得合格证据。原 17/17 仅为合成 CPU 资格，不能提升为 `R0_NATIVE_ROUTE_QUALIFIED`。本轮结论为 **`R0_HOLD_NO_SCIENCE`**，C1/C2 不开放；没有登记 request、创建 UUID、启动模型、消费科学预算或改 registry/epoch、原结果、Source/HOLD。资源账和动态正路径都需独立闭合后，才能进行下一轮正式科学准入审查。

## 4. 后续最小动作顺序

1. DTC/共享 Native owner 先按正式事务证据核清上述仍占额的 request；任何减账须按原子锁、epoch/SHA 和其他 owner 保证不变协议。物理迁移或删除大资产另需用户明确任务；不能把仅有 164 归档等同于可删 Native Source。
2. 在独立 R0 工程任务中补生产 dispatcher/launcher 的真实进程身份、私有 loader 和受控 guard 资格，并在资源准入后完成小型真实 164 合成闭合文件的归档、COMMIT、回读、typed native restore 与损坏负例。CPU fixture 和路径预检只证明工具边界。
3. 独立审查 R0 全链；仅全部 PASS 且该轮用户科学任务仍明确授权时，才按新 request 和一次性 UUID 进入 C1 的 GESUMMV/vectorAdd 四格。若 GESUMMV ON 自然 `eligible_choice_different=0`，依合同 HOLD C2。不得用旧 Goal 未消费的 20 格额度、旧 OFF 或旧 UUID 补上。

本轮状态：**STOP，等待下一明确任务或可核资源变化**。
