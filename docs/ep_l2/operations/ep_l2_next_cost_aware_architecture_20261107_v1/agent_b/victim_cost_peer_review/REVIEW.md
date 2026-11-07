# Victim extra128：有限写前成本与配对peer审查

结论：Main收窄的**base128/WAD128不变、固定Data1168/四BankP1、CLEAN-only extra128 metadata、单128-row比较器分两段查询**可以继续单版私有实现。此审查不授予Source/生产CPU/科学PASS，也不重开已结束的RO探索。

原V1设计文件中的LRU措辞已被Main后续方向替换为**RR固定indexed slot、有费read/recheck/write**；不要求A另开LRU版本。dirty和WB_COMPLETE不迁入Ext、Ext write/atomic不做双row dirty promotion，都是合理的安全收窄。

## 最要紧的三项实现门

1. **证明所有owner创建路径，而不只Ext-hit。** Native Tag-hit写/原子、部分sector Native fill、prefill/force-tag、Base普通install及dirty-promotion重绑都不能留下旧clean Ext副本。Ext命中但sector不足也必须先付端口、等reader退役、验证ticket/handle再失效，或走已实现的合法same-handle路径；不能保留Ext live后直接native miss。A已接受该分支。Native Tag-hit若用免费Ext CAM决定正常HOLD/修复，属于隐藏查询；仅验证不参与正常路由的assert与功能查询应明确区分。

2. **Base创建epoch需要完整覆盖和更新上界。** 至少包括commit_install、dirty-promotion等所有新Base owner入口。二段查询或缓存negative被使用前，要有epoch重核/有费Base重查，或有生产单head/无跨段迁移等明确不变量证明其间不可能出现新owner。global64与snapshot64、phase/segment/valid及新增UID/line副本均计入，除非实际实现证明复用。若同tick多创建事件合并成一次epoch进位，必须排除query snapshot夹在其中而漏掉第二次变化；不能只用“每tick一次”口头忽略客户端并发。

3. **所有端口及有限合并真实计费。** Base/Ext共用一个128比较器地址query gate，base miss后Ext再付1周期，重放再占同一gate。RR的indexed read/recheck/write也需要明确端口、每tickclient上界及仲裁；不能以RR之名仍免费扫描128/256行找合适row。Ext一个write port只能按冻结的有限操作矩阵合并同row/incarnation的合法更新，仍须核lease/UID/sector/Payload/generation；不同row HOLD，install/invalidate不能与不相关reader任意合并。预约先于reader pin、bank服务和实际response enqueue；取消不退已耗周期。

这些是新实现需要关闭的门，不是对既有接受Source判错，也不要求扩成第二实现或新归因项目。

## 仍须保持的固定资源

mandatory只在base128，WAD上限仍128；不能把constructor容量扩到256后顺便放宽mandatory或completion CAM。Ext只允许EMPTY/CLEAN，不接WB_STAGED/INFLIGHT，不迁WB_COMPLETE。Base原completion路径与packet/credit退役守卫保留。

Data1168、四Bank/P1、实际同bank landing及Payload身份不变。多128条metadata不是多128份Data，不得赠独立Victim Data Array、copy带宽或免费landing。metadata成本须列真实字段宽度、read/write ports、RR/epoch/ticket寄存器和组合逻辑；C++ ABI大小、功能packed下界和未测RTL/PPA不能混写。已核Source78 PayloadHandle的id与generation均声明unsigned，目录incarnation才uint64；不沿用先前讨论中错误的generation64猜测。

首版拒绝post-allocation host prefill/flush是可接受边界，必须在所有实际入口mutation前执行，不能仅检查“当前无reader”。初始quiescent prefill可保留其已支持范围。

## 三点成本控制与两点净对照

| mode | 逻辑配置 | Ext物理metadata | base hit | base miss后完成查询 | mandatory/WAD |
|---|---|---:|---:|---:|---:|
| 0 | legacy128 | 0 | 1周期 | 1周期 | 128 |
| 1 | segmented，Ext禁止安装 | 128 | 1周期 | 2周期，真实查空Ext | 128 |
| 2 | segmented，Ext允许CLEAN | 128 | 1周期 | 2周期 | 128 |

这张表是Main设计的成本意图，尚非完成的硬件/Source证据。

GEMM的1对0测分段pipeline/control代价；2对1在同分段硬件下测启用保留的净效果，也包含实际发生的metadata动态更新；2对0是相对legacy的总资源/性能折中。若mode1因Ext禁用或occupancy0而短路第二段，它只能叫default-off golden，不能叫分段成本控制。

Stencil的0对2是该输入的净对照，不拿GEMM测出的代价当Stencil参考。所有新点应使用同一个新Source/ELF、同输入/clock/Tag/Data及冻结其他配置；旧Source78接受结果只是context，不能继承成新Source baseline。固定Data也不等于总硬件成本相同：legacy128与segmented256的metadata资源明确不同，不宣称等面积。

计划的3+2点仅记录Main后续研究意图，本审查不提交科学申请、不建立预算、不启动模型。

## 审查边界与交付

与A已做只读讨论；Main决定门的关闭和最终方案。peer只写本目录，不修改A源码/文档，不做第二实现。REVIEW_FINDINGS.json给出七项具体门；PAIR_AND_COST_CONTRASTS.json保留有限设计算术；REVIEW_SCOPE_AND_EVIDENCE.json区分原V1与Main后续RR/epoch收窄；读时副本及SHA在SNAPSHOT_EVIDENCE_MANIFEST.json。

原RO收敛五文件保持冻结，本peer不会改变其结论。新增Source/Native/历史/预算/dispatcher/Git/模型均为0。
