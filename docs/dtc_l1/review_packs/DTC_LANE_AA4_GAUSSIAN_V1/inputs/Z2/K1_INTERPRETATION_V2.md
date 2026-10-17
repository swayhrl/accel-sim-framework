# K1 interpretation V2 — source-request event alignment

合同ID：`Z2_K1_SOURCE_REQUEST_V2`。这是用户在Lane Z V1之后选择的新时间合同；供AA在任何新性能消费/执行前绑定本文件SHA、发布commit与fetch-back回执。本文件不授权模拟、不实现Core、不证明X/AA已符合合同，也不宣称早于T/U历史结果。Lane V固定来源为 `26abd496417d9392245052e54fbd9ba27c6ffd96` 的 `docs/dtc_l1/review_packs/DTC_LANE_V_SEMANTIC_V1/K1_SEMANTIC_CONTRACT.md`、`SOURCE_EVENT_MAP.md`；源基准Core `6fba0136f8465b59fe5858a950fa39efb265f654`、Framework build `18a68dcccd795f1b6cda75504e9450d00c9cee02`。V是语义审查合同，不能冒充K1实现验收。

## V1 → V2 的显式修正

Z V1 `ccf208c723f44387160c0edfe9e4d56855dfbafd` 的 `PREREGISTERED_INTERPRETATION.md` 将K1描述为“opt-in DTC kernel-boundary invalidation”，并要求“无 live Ref/pending/ownership 的安全边界”；其单kernel段也用“是否只在末尾”作诊断前提。这些时间描述不适用于新V2。V1全部文件（含78个typed字段、2790行证据、413个检查结果）原样保留；不回写、不换label，不谎称V1已采用source-request定义。

| 合同维度 | 历史V1 | 新V2 |
|---|---|---|
| 线性化点 | 描述为安全kernel边界，等待无live Ref/pending/ownership | source请求到达 `ldst_unit::invalidate()` 时撤销DTC查找可见性 |
| quiescence | V1文字作为前提 | 不需要global quiescence，不等待DTC/ordinary统一drain；只在回收具体allocation时要求所有旧owner结束 |
| 事件集合 | kernel-boundary措辞容易引入每kernel保证 | 严格继承源码已选择的SM集合与条件；实际kernel-done不自动产生invalidate |
| 重复idle | V1未给出准确的源事件语义 | 继承源码可逐cycle重复请求；幂等撤销、只free/计map-loss一次，不新造idle去重/epoch语义 |
| 单kernel解读 | 以末尾边界为主要诊断假设 | 单kernel也可遇idle-cluster、config或MEMBAR请求；不得先验断言K1只影响末尾或必与K0相同 |

K0保持冻结旧模型的source行为：ordinary `m_L1D->invalidate()` 等原逻辑照旧，独立DTC mapping不新增source-request失效。K1是在同一已发生的源请求处加入DTC lookup-visibility撤销。`flush()`不等同于`invalidate()`；不增加每kernel广播、写入自动撤销、PROXY_FENCE清Tag或更改原触发范围。

## 源事件与保护合同

事件标识为 `E(SM, sequence, source, cycle, phase)`，source分类继承Lane V的冻结调用图：

| source | 原条件与作用域 | 解释边界 |
|---|---|---|
| idle cluster | `gpgpu_flush_l1_cache`开启且该cluster `get_not_completed()==0`；向该cluster全部SM请求invalidate | 默认开关0；开启后idle可反复请求，其它cluster可先触发，不保证该SM/DTC已drain |
| cache config | 选定cache status变化时按原调用链遍历clusters | 条件不同于idle flag，不能扩成任意两个kernel间必触发 |
| ordinary MEMBAR | 原scoreboard pendingWrites条件满足、clear_membar且flush_l1开启，作用于该SM | 不能从源码注释推所有store ACK均完成；不是PROXY_FENCE |

普通L1仍按其pending invalidate/ordinary miss生命周期决定最终执行时刻；DTC撤销线性化在LDST源请求到达处。request与ordinary execution是两个事件，不得等ordinary drain后才处理DTC，也不得用ordinary pending标志代替DTC所有权检查。同cycle lookup/commit、response、collection、WB、retire与E的phase/调用次序须由实现提交确定并可复演；Z2不虚构未经发布的phase号或开关名。

E撤销当前可查询Tag；OO同步保持physical.tag_valid与目录一致，并记录一次map-loss。E前已接纳消费者继续用原 `{physical_id,generation}`；保护inflight UID/返回mask、Ref、waiter、pending dependencies、PIB slot generation、lower credits、ready与collection/WB状态。E不统一增加generation、不清队列、不丢旧消费者、不重发已接纳reference。旧返回只能完成原identity，不复活已撤销Tag，也不填入E后新同址allocation。未接纳的reference（含partial PIB剩余部分）在commit查E后的目录；grant不自动表示已接纳或已保存旧命中结果。

地址不可见且所有旧owner（包括lower/return-service/waiter/collection/WB）完成才可回收；后续重新allocate才generation++。ready retained且无owner的allocation可回收，有Ref或在途者继续活着；WB拒绝不得提前Ref--。重复E可增加source-request次数，但不能对同一仍隐藏identity重复计map-loss或free；request count、实际撤销mapping count与reclaim count必须分开。不能把必要的E后同址再miss无条件标错误duplicate。

四格研究对象仍为OO128。若扩展到IO，须另给等价orphan/live-owner证明，不能假造IO现有Ref或把隐藏physical挂给任意PIB/未来load；未证明时保持 `IO_K1_UNIMPLEMENTED_STOP`。K1不提供数据payload更新、一般coherence、store ACK全局可见性或全ISA数值正确性；A/T/U terminal strict及源事件合同均不能代替值oracle。

## 四格与公式逐式核对

令 `a=C(K0,32×4)`、`b=C(K0,64×8)`、`c=C(K1,32×4)`、`d=C(K1,64×8)`；C表示同一完整输入的whole-run core-cycle，全部严格为正。K1的事件语义改了，但四个数的代数定义未变。新四格必须采用同一V2、source/build/runtime/clock/observer/effective options与完整输入合同，除K与Tag外匹配；不能把旧T/U当新K0。

| 量 | V2公式 | 逐式核对与方向 |
|---|---|---|
| Q32 | c/a | 同32×4下K1/K0；>1为K1周期更长 |
| Q64 | d/b | 同64×8下K1/K0；>1为K1周期更长 |
| T0 | b/a | K0下64×8/32×4；<1为扩大Tag周期降低 |
| T1 | d/c | K1下64×8/32×4；<1为扩大Tag周期降低 |
| I | Q64/Q32=(d/b)/(c/a)=ad/(bc)=(d/c)/(b/a)=T1/T0 | V1代数仍成立；>1表示K1在大Tag的相对周期惩罚更大，或扩大Tag收益在K1减弱 |
| log(I) | ln(ad/(bc))=ln(a)+ln(d)−ln(b)−ln(c) | 使用自然对数，I>0；与乘法交互同号，不是百分比或周期 |
| Δ | (d−b)−(c−a)=a+d−b−c | 加性描述性交互，单位GPU core-cycle；与V1公式相同，不是retained mapping精确因果份额 |

整数分子分母先保存，quotient不使用显示舍入值。四格缺失、strict不合格、合同不同或周期非正，则相应商/交互UNAVAILABLE，不补格；无重复估计不声称显著性。`FORMULA_VALIDATION.json`以精确有理数和正值数值见证独立核对全部公式，属于CPU算术，未读取任何新四格性能。

解释层面只允许说“source-request失效策略×Tag交互”。不得继续称“全部kernel边界清空效应”，也不能将c−a或Δ精确归因跨kernel retained reuse。必须报告实际source事件分布（SM/cluster/sequence/phase）、ready/pending/new、lower创建/成功注入、physical/PIB积分与分母、post-ready退化、map-loss sum/count及缺失状态；无直接事件观察时相关解释保持有界。单kernel收益、跨kernel可能保留收益、源事件时序影响与post-ready条件退化分开描述。

## AA消费前绑定要求

AA应在新性能之前绑定本文件SHA、含本文件的不可变Z2发布commit及fetch-back验证、固定Lane V提交、实现Core/build/binary/config、有效K开关与observer合同，以及四格输入/Tag身份。这里规定绑定要求，不声称AA已经绑定或新性能尚未产生；本次没有读取AA状态或性能。任何偏离源事件集合、线性化点、重复idle或身份保护的实现都须另列合同偏差，不能沿用V2名义。观测插桩前后cycle仍不直接混比。
