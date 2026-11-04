# DTC-L1 Performance-First V2
## Resource Co-design and Liveness-Safe Optimization — CPU-Only Parallel Preparation Goal

### 0. 用户授权与目标

用户正式同意启动DTC-L1 Performance-First V2的CPU-only准备阶段。

本Goal与正在执行的Performance-First V1并行，主要完成新机制设计、资源组合探索规划、前进性验证、关键负例科学分析及独立审查。

**当前不授权V2新的GPU/模拟器科学运行。** 合法的CPU-only fixture、源码分析、静态设计、已有归档证据消费和独立复核可以立即执行。不得以准备Goal之名改变正在执行的V1。

本阶段要形成有价值且可直接进入后续科学执行的方案，不要把流程拆成不必要的多轮“准备—复核—再准备”。

### 1. 固定科学基线

使用以下Authority：

- Stage I：`361fa6fa0700825bb9cda43e25b9fd1f60e0b262`
- Stage II-A First16：`5f67b4d6b94568a9f1acc80c3e56736bd81e4753`
- 已完成核心32来源：`b665d5ea77b5ae022a86cd03c6c464f5b11cb15e`
- Performance-First V1已发布快照：`018d6440c17265205d7b1eab31d9bfa4ee51690d`

Core：`9eedb3131937748f0492fa83aad37d3691118d70`

Framework：`02775fd795cde5aae1480d81cee6eb481d0a08f4`

沿用原64SM、10MiB L2、DRAM850MHz及DH-P0作为结构探索基线。

完整32程序基线的GM CH/DH为1.100072；下游F128/F256交互GM为0.996830/0.998523。现有证据支持继续研究DTC内部结构，不必重新运行已接受的P0。

V1已有32个非Tag候选启动，16个Tag扩容候选为安全HOLD。V1继续由原DTC-MAIN owner负责，不增加竞争dispatcher，不访问活动raw、不重启和不改变原有任务。

### 2. Main与四个Agent并行分工

Main负责统一科学方向、任务依赖、证据版本、资源边界、独立复核与最终决策。四条工作线可以并行，不必等待其他Agent全部结束。

**Agent A：Tag/Physical前进性与安全机制**

基于固定Core原始头文件，完整复核1024逻辑Tag/640物理行的CPU无前进反例。

现有关键状态是：物理池中640个有效Tag映射持有已完成且Ref=0的物理行，而新请求所在组存在无效Tag槽。当前目标组victim无法释放跨组持有的物理资源，导致后续NO_FREE_LINE。

必须区分三类情况：可通过现有victim回收前进；物理行因合法在途引用暂时不可释放；存在可回收的Ref=0物理行却无法取得进展。

研究两条安全设计路线：

A1. 保持总Tag512不变，探索128×4、32×16等不同组相联组织的可行性，分析Hash行映射与容量的耦合。它们只是待验证候选，不得预设安全或有性能收益。

A2. 针对更大Tag容量，研究可证明安全的跨组回收、victim选择或物理资源预留策略。任何策略必须保留物理generation、live Ref、pending return、waiter和完成生命周期的正确性。

可以在隔离的CPU-only研究目录建立设计原型和定向fixture，但不得修改生产Core、替换现有Tag HOLD配置或自动启动科学模拟。

现有Lane X source-event invalidation历史与语义边界必须保留；不能直接把全局清空或源事件invalidate当成普通物理资源回收修复。

CPU测试至少覆盖无活动引用、多个活动引用、在途返回、Tag替换、不同组地址、重复地址、物理池满、PIB部分占用、generation复用及重复释放防护。

有限定向测试PASS不等于普适前进性证明。应提供可检查的安全不变量、进展条件及未覆盖边界；不能证明的候选继续HOLD。

**Agent B：MVT/BICG性能差异与机理证据**

优先分析已完成且严格接受的Physical768结果。

MVT整体从34,687,540降至30,609,855 cycles，主要节省集中于Kernel 1：33,032,429→28,955,953。

BICG整体从28,685,812升至30,892,841 cycles，回退集中于Kernel 2：27,030,465→29,237,494。

2DCONV与GEMM作为精确零响应控制；vectorAdd保持无明显缓存复用的控制身份。ATAX、scan与convolutionSeparable继续作为现有证据补充。

复用合法关闭的结果、资源轨迹、真实kernel周期和已有计数；不读取活动模拟的中途raw。

区分Tag映射保留、physical引用生命周期、PIB占用、下游请求数量、完成服务及执行阶段关系。重点检查性能变化是否伴随请求量、映射替换、物理行保留周期或完成时序变化。

必须明确现有证据中没有的计数。不可将平均occupancy、Tag eviction次数、MSHR retry或最终physical gauge直接解释为关键路径阻塞时间。

输出能够被后续实验检验的具体假设及相反证据，不预设Physical扩容一定是正优化。

**Agent C：Physical×PIB及完成服务协同设计**

复用Performance-First V1已有的单变量结果，不重新运行基线。

优先形成如下组合设计矩阵：

| Physical lines | OO PIB128 | OO PIB192 |
|---|---|---|
| 640 | 固定DH-P0 | V1已有单因素 |
| 768 | V1已有单因素 | V2新组合候选 |
| 1024 | V1已有单因素 | V2新组合候选 |

初步覆盖同一固定8程序，两个新组合共16个待批准科学候选。16格是当前组合研究范围，不是整个研究项目的任意总实验次数上限。

这些新候选必须首先完成CPU安全与有效配置资格检查。PIB192实际上同时影响OO PIB和lower-create queue，不允许将其当作纯PIB容量变化。

研究Physical容量、PIB候选数量、有限create/inject、collect、retire及writeback之间的关系。

现有Tag服务2/bank、8 total的V1实验仍在执行。现阶段可研究其与完成路径的资源关系，但不要在未有证据时宣布增加Tag服务端口必然提高总吞吐。

组合的性能评价须同时给出相对DH-P0加速、相对CH-P0绝对性能，以及与两项单因素的交互。对完整合法配对可使用：

J = S_combo / (S_physical × S_PIB)

J大于1表示组合收益超过两个单因素加速比的乘积，但不等于该组合在绝对性能、成本或全程序集合上最优。

不得只保留MVT等正例；BICG、零响应与回退全部进入固定统计范围。

**Agent D：独立科学审查与硬件成本**

独立检查Agent A/B/C提出的源码结论、前进性反例、CPU fixture、参数生效条件、输入身份、实验矩阵、结果统计与候选安全边界。

严格区分声明的128B整行物理身份容量、模拟器元数据结构、实际功能性数据存储及未来RTL/SRAM实现成本。

Physical768相对640增加20%的名义物理行容量；PIB192及lower-create queue各增加50%的深度。不得假设增加的存储、Tag比较、回收搜索与仲裁没有面积、端口、频率或能耗代价。

审查每个方案是否仍是原有DTC机制的参数变体，还是已经改变Tag替换、物理回收或完成语义的新机制。新机制必须使用独立版本与科学身份，不能混入固定V1结果。

保留现有HtoD、source/capture ELF及数值一致性未认证边界。不以CPU前进性PASS替代完整应用正确性验证。

### 3. 工作流程与并行执行原则

Main应立即将以上四项工作并行分配。

各Agent可独立阅读冻结源码、复用历史CPU fixture与已关闭的证据、编写CPU-only验证程序、生成候选矩阵及执行独立检查。尽量一次完成完整范围，避免为了形式性小步骤多次往返。

优先复用V1已经验证过的源码事实、配置有效性、原始header fixture和统计工具，不重新制造同样的验证包。

如Agent A发现可行Tag回收设计，不必等Agent B/C结束才继续CPU-only验证；Agent C完成组合矩阵后，也不必等Tag路线证明才形成组合执行方案。

但任何新原生模拟、GPU任务、生产Core语义修改或新的科学执行request均不属于本CPU-only授权。需要另行提交明确的科学执行合同。

V1仍在运行时，所有CPU-only工作必须服从现有host/cgroup/IO及归档资源保护要求。不创建竞争owner、dispatcher或会干预活动raw的消费者。

### 4. V1结果如何改变V2

已有32程序公平匹配结果可直接作为当前V2方向依据。

当V1的32个非Tag候选最终完成，Main可以在不阻塞CPU-only工作的情况下进行一次方向复核。

若V1表明某些参数族完全无效，则停止相关新实验的后续准入，保留原研究与反例证据；若出现新的明显结构机会，则在既定CPU-only准备范围内更新候选优先级。

不要求为每个新的accepted结果重发Goal。仅当出现模型语义、科学执行范围或资源权限的实质变化时，才触发新的批准边界。

### 5. 阶段交付与结束条件

建立独立V2准备分支，输出完整且可复现的GitHub审阅包。

建议目录：

`docs/dtc_l1/plans/DTC_PERFORMANCE_FIRST_V2_CPU_PREPARATION_20261104_V1/`

交付内容应包括：

- `A_TAG_LIVENESS_AND_DESIGN.md`：前进性反例、安全设计和CPU验证。
- `B_MVT_BICG_MECHANISM.md`：性能差异、实际kernel及可信机理证据。
- `C_RESOURCE_CODESIGN_MATRIX.json`：新组合身份、有效配置、约束及复用的V1对照。
- `D_INDEPENDENT_SCIENTIFIC_REVIEW.md`：独立检查、安全性、成本和未解决边界。
- `V2_SCIENTIFIC_DECISION.md`：Root综合判断、优先级及未来研究方向。
- `NEXT_EXECUTION_GOAL_PENDING_APPROVAL.md`：下一阶段真实科学实验的完整待批准Goal。

所有结果需有冻结源码与文件SHA、CPU-only复现证明、独立审查及GitHub远端回读。

最终提案应将无需修改Core的合法组合实验，与需要新机制实现的Tag安全实验分开安排，避免相互阻塞。

**目标是直接交付下一阶段可授权的完整实验方案，而不是只完成讨论或形成空泛的研究建议。**

### 6. 不变边界

不重启或修改V1，不访问其活动raw，不增加第二执行者，不复用任何旧UUID或预算。

不自动启动新模拟、GPU、capture、109任务，不更改历史接受结果，不把16项Tag HOLD算作性能负例。

不修改英文论文v0.23，不臆造RTL面积、时序或功耗结果。

本CPU-only准备Goal完成并独立审查后，停止在科学执行授权边界，提交完整下一阶段实验提案供审阅。