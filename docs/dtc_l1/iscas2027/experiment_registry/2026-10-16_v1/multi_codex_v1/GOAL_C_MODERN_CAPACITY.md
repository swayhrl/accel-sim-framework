# Goal: DTC_MODERN_128K_LAYOUT_FEASIBILITY_174_V1

原174账户的新独立Codex窗口。先读本目录README；现有主模拟继续。本任务针对已完成容量审计给出最小设计决策，不重复审计629个成员，不启动现代DTC性能行。

建议独立分支`hrl/iscas2027-dtc-modern-layout-174-v1`。只读主Core6fba0136、构建Framework18a68dcc和主执行最新e3dbe3db及后续提交。结果只写自己的worktree/review_pack。当前用户已经选择128KiB总统一data/shared预算，未授权208KiB扩容、路由改写或静默减少100KiB shared支持。

先读主执行中的`MODERN_CAPACITY_CONTRACT_REVIEW.md`及`review_pack/modern_capacity_v2/`，固定决策e13266ba207d8b8e47b56d62dfdb8bd04c8e2c5b，4080资产8d1f14a32f5538660d74da86ccb03a2c504c5735。逐kernel有效shared/L1已有人计算；直接用hash匹配的表，避免第二次完整扫描。

## 回答三个具体问题

1. **物理字节和服务能否不双计？** 现有DTC80KiB与常规L1是独立对象。提出最小结构：它们各自对应统一存储的哪段容量、如何选择bank、共享或独立哪些端口；shared访问和store/atomic/旁路所需的普通路径如何继续正确工作。仅把两个数组尺寸相加不等于已经建模共同物理服务。
2. **支持域怎样保持？** 无shared时80+48+0、shared32时80+16+32是容量算式，不是完整架构实现。shared100时只余28KiB L1，无法同时容纳固定80KiB池。明确哪些可选方案会改变DTC池、Tag覆盖、前进条件或路由。不能未经决定选择动态缩池、禁用shared100、静默fallback或牺牲原功能。
3. **最小实现及验证代价有多大？** 列需要改动的source functions、可复用的状态/配额、需要的新验证，以及是否触及协议/支持域。提出一个首选和至多一个备选，说明哪一处需要用户决定；不要写泛泛的“需要进一步设计”。

可用CPU布局/容量测试验证算式及边界，不改主线功能协议。即便单个固定pilot可以使用80+48，也不能外推全支持域。资源向量要含Tag/PIB/事务/引用/唤醒和端口，128KiB数据预算不等于总面积相同。

若能在原协议和已接受资源合同内给出明确有限服务方案，提交候选设计与局部验证计划，现代DTC仍待批准后由A启动；若必须增加机制或工作量超出短期预算，明确建议保留native/modern baseline-only证据，本次不做现代DTC主结果。不得为了填论文图而长时间改造整个L1/shared模型。

约2小时交首份可决策报告；工程路径问题自行处理，新的资源/协议决定留在NEXT_DECISION。输出`docs/dtc_l1/review_packs/DTC_MODERN_LAYOUT_PROPOSAL_V1/`：README、LAYOUT_AND_PORTS.tsv、SOURCE_IMPACT.tsv、LEGAL_DOMAIN.md、NEXT_DECISION.md。推送并回读；不改全局LATEST_REPORT或44行队列。
