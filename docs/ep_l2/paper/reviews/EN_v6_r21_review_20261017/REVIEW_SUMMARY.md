# EN-v6-r21 review — research argument and reader-facing revision

2026-10-17. REVIEW ONLY; no simulator, configuration, accepted result, Lane6 branch, or task change.

## Exact basis and review limits

Reviewed Lane6 publication `606d54610c2800ff4d8cf9178b23bc35cb2eff3d`, pack `docs/ep_l2/review_packs/FT20261017_LANE6_R21_LITERATURE_MERGE_r1`. Read the complete manuscript TeX, generated BBL, CITATION_SOURCE_MAP, MERGE_REVIEW and FIGURE_PROVENANCE, and the inherited `FT20261017_LANE6_R18_FIVE_PAIR_EN_V6_r1/PAIRED_RESULTS.csv`. Manuscript blob `0841663b635a4c6c77b58df0c76bcc780e7bde44`; CSV blob `245ffe2b4a5ba5f54e5d19a6b9023de28a3dbe55`.

The original full PDF bytes were not successfully downloaded for local rendering. This review therefore does **not** claim an independent page-by-page visual PDF check; figure/table comments concern exact source, captions and data. The 4+1-page and layout-pass statements remain Lane6's reported checks. This is not new raw-trace qualification or a fresh full-paper literature search. No later D4/Q4 result is silently substituted into this frozen manuscript.

## Overall judgement

近邻写回引用已经显著改善，H0五组、SAD近乎持平和CFD退化都保留，数字复算一致。这版的问题不再是只有计划没有结果，而是仍像严谨的阶段研究报告。若按此快照直接送审，审稿意见应是实质性大修；这不是否定当前实验或要求停止D4/Q4。

复算GM(C_B/C_U)=1.0016002037656606（+0.160020%），五组cycle reduction依次为SAD +0.021666%、Vector +0.199468%、CFD -0.213673%、Convolution +0.480316%、FWT +0.309618%。未发现这组主要数字抄写或平均方式错误；数值正确不等于独立弹性性能收益已经成立。

## Priority findings

### P0-1: baseline and independent elasticity

II-A承认B16为1024/128/16固定划分，同时当前未建立活跃bypass共存。因此动态U可利用原本闲置的bypass quota，审稿人会问为何不静态重新分配。补充这个参考组织的真实设计理由和来源，不以缺乏证据的通用GPU假设填空。同总1168-slot的强静态对照是容量主张的关键证据；1024/112/32只是一个拟议点，不是最佳静态分区。WBUF8、Q4/D4和静态重划分回答的问题不同，不能互相替代。现有D4/Q4继续，不必因本意见停跑；无强对照时最终声明应限定为相对指定B16。

### P0-2: say which replacement algorithm is implemented

II-B仍说遇跨周期victim变化时“保留原事务或完整回滚”。这是正确性要求，不是当前算法的明确描述。请从真实生产源码提炼一个短状态/事件表：预留哪些身份、哪个事件改变Tag、bank拒绝如何重试、何时commit/rollback、无合法landing或WAD满如何处理，以及WB-only面对同地址后续请求到底等待还是转发。编辑者不能替Lane1补造锁定、取消或回滚实现。保留三个真实退休事件，但压缩重复的泛化警告。

### P0-3: implementation value remains unproven

II-D当前主要是未确定事项清单。同容量/同bank吞吐不代表新增handle/owner checks、空闲选择、仲裁和事务控制具有相同命中延迟或可忽略成本。H0收益很小使这个问题更敏感，但不能直接断言增加一个周期一定抹平收益。不要求完整芯片物理设计；需要明确的关键控制实现/位宽/队列/端口和净增减成本，或后续准确延迟敏感性。不能由copy次数推出实测节能。

### P1-4: remove internal workflow vocabulary from the paper

Abstract/III-B/IV中的independent intake、Lane5、V2 authority、R19 authorizes、accepted-pair coverage是artifact协同语言，应移到开发/复现材料。native在本项目不表示实体GPU实测，主文宜写trace-driven simulation、non-atomic workloads。31/11gate命令和撤回管理不应比具体实验描述占更多篇幅。关键范围限制保留一处，不在摘要、引言、图注、方法、结果和结论反复用否定句展开。

### P1-5: actual workload and artifact entry

III-A只有五个名字与“accepted manifests”说明。应从现有准确manifest补一个紧凑输入/规模/完整执行范围/选型用途表，并给复现包明确的可获取入口。未知项直接保留未知，不能从4M或7_21名称推断输入。不建议任意增加或替换更有利的workload。

### P1-6: Fig.4 is a progress table, not a scientific figure

H0 2/2、Q4 0/2、D4 0/2明确是进度，不是造假，但不贡献技术论证。移入STATUS。数据未到时用准确H0/Q4/D4条件表；数据到后展示同条件S(h)、J(h)和四个cycle数。保留H0五组总体与两个代表负载的区别。不能把C_B(H0)/C_U(D4)当EP-L2单独效果。WBUF8未评估行和长TVD/RO资格状态段可移出主配置/主体，为机制与真实结果让位。

### P1-7: connect work, residency and throughput

IV/图3避免把累计事件当全GPU时间，做法正确；但大量篇幅仍是计数罗列加“不证明因果”。按copy是否消除、静态配额何时绑定、解除局部限制后怎样影响服务三问题组织。复用已有staging/WB occupancy、实际借用、lower服务率和WAD生命周期数据，不必为了多一张图重跑已合格H0。staging lifetime在B/U的起算事件不同，派生均值不得冒称完整WAD寿命或独立因果。

“issued-byte/atom-cycle fraction”需要明确定义分子/分母/采样位置，不要让读者当作实体DRAM总线利用率。平均较低也不排除通道/时间窗口热点；当前文字没有直接宣布饱和，这点应保留。

### P2-8: citation and terminology polish

R20的12条实际引用已有具体用途；不是数量不足。将“Unified GPU memory reallocates ...”改为“Gebhart et al. unify SM-local register, cache, and scratchpad storage”。以肯定的对象/机制差异取代“Neither ... originates here”“SMS does not establish ...”等重复防御性句子。正文保留1.0016x或+0.160%，完整精度留CSV。确定性单次观察不必重复运行同输入来制造统计含义，应保持鲁棒性与因果对照的区分。

## Lean merge order

现在可做：摘要/方法去内部化；从真源码提炼替换算法；从现有manifest补输入表与条件表；Fig4进度移出正文；精简未评估扩展与重复限制。必须靠后续证据的内容：D4/Q4实际效果、同总容量强静态对照、实现成本/时序。当前H0不重跑、31项资格不因文字修改重跑、不改V2账本、不新增源释放。

`SUGGESTED_REPLACEMENTS.tex` contains source-grounded text proposals only, not a complete paper or compiled submission version. Do not apply them over new Lane6 measured results without reconciliation. No new Codex Goal has been issued by this review.
