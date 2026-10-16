# V8｜Hotspot V2五组验收、Legacy三负载来源审查结论

**证据锚点：** Lane A `cd7b7b61094ba81a5dacff4f94aa7e16f8f20efb`、Lane B `d46cce269b88055decc2ca052dcb9baae0efee7e`。A Snapshot `2026-10-16T13:23:17Z`（源branch committed 13:24:57Z）；B `2026-10-16T13:16:58Z`。这里是已推送收据的静态状态，并非实时进程监控。

## 严格审核决定

| 成果 | 结论 | 限制 |
|---|---|---|
| 新Hotspot独立派生输入 | **ACCEPT: DERIVED_SOURCE_PROFILE_SCOPE_ONLY**；5条同bundle完整严格PASS，单成员377291004 active-thread instructions，源SHA与输入身份一致 | 原ELF/traceall/JIT/input temp-power/native输出未绑定；不能替换旧trace语义 |
| B16-N | 152914 cycles | 只属于新Hotspot V2输入 |
| TC80-N | 107774 cycles | 同输入 |
| TRAD96 | 82873 cycles | **快于IO和OO**，必须保留 |
| IO256 | 85718 cycles；vsB16 1.783919×；vsTC80 1.257309×；vsTRAD96 0.966810× | DTC服务显式有限，但IO/OO是不同PIB深度 |
| OO128 | 84456 cycles；vsB16 1.810576×；vsTC80 1.276096×；vsTRAD96 0.981257× | 没有等面积或原生加速结论 |
| Legacy Btree | **UNRESOLVED_FORMAT_APPLICABILITY** | 6000条full32, 5792 cacheable load可能变sector/line identity；实际producer缺失，三个ELF候选不符 |
| Legacy 2DConvolution | **UNRESOLVED_FORMAT_APPLICABILITY** | 2021 fork version3仍按E；header不区分前/后修复；部分cacheable load改变line/sector数 |
| Legacy LUD | **UNRESOLVED_FORMAT_APPLICABILITY** | 19840个global风险记录与所假定源码模型一致，支持冻结firstP16，但缺采集ELF/predicate绑定 |

A源`hotspot_derived_admission_v1/`独立核对当前consumer所有1,161,860 memory records；5个新attempt全部严格验收且上层资源平衡。一次补充validator的cap字段选择错误经修正，失败receipt留存、没有重跑模拟。固定baseline与DTC Core不同是被比较设计的本来差别，模型/输入/范围的公平性按`PAIRING_CONTRACT.json`核查，**不得声称五种方案完全同binary**。

## 主线当前发布状态

- 原注册44行：**33 terminal/invariant PASS**（包括2条原Hotspot科学HOLD）、**8 RUNNING**、3条原Hotspot admission HOLD。新的5条派生Hotspot不计入44的进度分母。
- Btree/LUD/2DConvolution原terminal PASS不变，科学解释标`FORMAT_APPLICABILITY_REVIEW_PENDING`；不认定错误，也不声称native准确。
- 现代4080DTC、SpMV SM89、LayerNorm trace都未获准入，原定边界不变；不继续扩大。
- 不计算混搭GM12/GM11或以派生Hotspot替代原Hotspot后声称“12项原始工作负载已具备同等语义可比性”。论文可在标明输入语义下报告5条Hotspot配对为单独案例。

## ISCAS论文决定性风险及建议

当前可写的明确观察是：DTC原设计通过不同lookup/等待/数据保留结构产生负载依赖的结果，**强增强传统参照并非处处落后**；派生Hotspot中TRAD96胜过IO/OO，原BICG显著回退仍必须列明。此前一些重要收益程序Btree/2D的历史trace源绑定不充分。因此在未完成科学格式适用性解释前，文章不能声称这些是准确复现原程序的无条件性能收益，更不能以GM12作总括。

建议把论文与下一轮实验分为两条**由用户另行授权**的路径：
1. **稳妥主稿**：固定已验收数字作为带输入语义的周期级模型证据；对未认证程序限制应用外推，明确横向配置身份、所有回退及硬件面积缺项。
2. **可选有限稳健性比较**：只针对Btree/2D的真实风险，根据已有来源明确两套预先指定的地址解释，先CPU-only确定候选的合法/可解释边界，若确有合法双解，再各做新输入匹配的最少传统/DTC配对，检验结论是否随条件改变。LUD源模型已支持冻结地址，后置。不能从实验结果反选输入；若没有可正当化第二解释则STOP，不按“猜测E”跑出一组速度。

Lane B已完成授权的有界核查并STOP。Lane A保留唯一调度权限与8个live进程；不重置/重跑/插入新的旧44模拟。未获得新授权前，不启动后续双解敏感性或重编trace程序。不为了填满论文实验矩阵而追加新workload。**重要待办仍是面积与时序成本，在成本缺失时不能将性能对照写成能效/等面积优势。**
