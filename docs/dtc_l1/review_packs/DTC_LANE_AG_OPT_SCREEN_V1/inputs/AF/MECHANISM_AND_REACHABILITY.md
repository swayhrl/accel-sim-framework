# AF reclaimable-victim opportunity — source and synthetic reachability

独立候选源基准：Core X2 `e32afdcf44be3374ff36d22568ed01a075459b6f`。分支 `hrl/iscas2027-dtc-lane-af-victim-fallback-core-174-v1`；Framework从X2发布 `631eb6418f6e7f1f548afd33351cbc0d98d27145` 新建独立分支。所有源码修改只在AF worktree，AA5及其它Lane的Core、raw、锁未读取或修改。本包不使其历史结果失效或自动升级。

## 原路径与机会的必要条件

`oo_frontend::access`先按原地址查Tag并附着既有identity，之后才检查allocation width、选本set victim、找RR free physical。原 `select_victim`优先invalid way，否则按现存LRU时钟选择；当free不存在且原victim不能由Ref0回收时，增加 `m_no_free_physical_events` 并返回 `NO_FREE_LINE`，没有搜索同set另一条可回收mapping。

AF窗口定义为：**在一次已到达access的whole-line OO miss commit上，allocation width尚可用，RR pool无free，原victim valid且有live Ref；同set至少一个不同mapping满足allocated/identity一致、tag-visible、ready、Ref0、waiters空且没有同identity finite service-return owner。** 这不是“所有NO_FREE_LINE”，也不是所有pool-full时刻。candidate queue full、PIB full及Tag bank失败发生在LDST上游，不能假装已经到达该窗口；allocation-width拒绝也返回相同enum，但有自己的事件计数。普通L1D/MSHR不替代DTC ownership。

没有free时大多数请求可能仍没有安全候选，AF继续原拒绝。不会因为平均physical/PIB occupancy低或高而判定该窗口存在；本轮没有真实输入事件序列，频度、覆盖和收益均UNKNOWN。

## 唯一候选开关与算法

`-gpgpu_dtc_l1_reclaimable_victim_fallback` 为OPT_BOOL，默认 `0`。ON仅支持PAPER_OO whole-line；其它模式在LDST构造时fail closed，不改变IO、PAPER_BASE、LEGACY或MODERN_OO_SECTOR的算法。sector路径及其返回mask身份守恒原样保留，不宣称sector fallback已实现。

ON且上述无free/live原LRU条件满足时，扫描**当前set**，在安全候选中取最老LRU；相同LRU按原way遍历顺序取首个。不存在候选则沿用原victim和原拒绝。已有free、原victim invalid、原LRU已经Ref0可回收、命中、allocation width不足时，不启用fallback。没有跨set偷取，没有额外allocation/retire/Tag服务配额，也没有改变physical RR算法。

选定后复用原Tag eviction→map-loss timestamp→Ref0 release→RR allocation→generation++→attach新consumer流程。旧LRU及其它set完全不受选择修改。fallback不会清Ref或ready/pending，不会改变已经接纳的consumer与generation；不重发旧请求、不重建frontend。E前/后的K1源请求继续按原identity生命周期完成。下一次相同行访问重新执行当前Tag lookup：若已有mapping则hit/merge，不再次进入fallback；旧physical已释放并重用时旧generation必须被拒绝。

安全候选的lower-owner排除来自冻结生产生命周期：pending lower保留已接纳consumer Ref；完整0xF返回按保存UID/physical/generation交付complete后才关闭inflight，finite metadata完成前physical仍不ready；Ref只在成功collection/WB之后frontend retire时减少。因此 `ready && Ref0 && waiters.empty && no service-return` 排除合法在途lower/collection/WB owner。frontend本身没有独立integration inflight表，所以这是一条源码不变量证明，而非伪造的新inflight查询；若未来改变该不变量，AF必须重新审查，不能沿用资格。

## 两种定向可达性见证

1. 2sets×3ways，4physical（少于6 Tag位）：set0的A有多个live Ref且最老，B/C为更年轻ready Ref0，set1的X也ready Ref0。目标miss在set0：OFF拒绝，ON回收最老安全B；C、X和A原identity保留。全target live时，即使其它set有安全X，两者仍拒绝。已有free时两者都替换原LRU。
2. 1set×2ways，3physical（physical多于全部Tag位）：先创建pending H，再A，再B；有free时B自然驱逐H的Tag但H的旧consumer保留，形成隐藏live H + 可见live A + ready Ref0 B，pool满。新miss的原LRU为A，ON可回收B，OFF拒绝。这证明机会并非仅由physical<Tag的特殊尺寸产生；不证明生产640/128或640/512下的真实频率。

LRU观察注意：冻结 `will_new_miss()` 内部调用会更新命中的LRU；AF不修改这项共用行为，也不将其当无扰动观察器。候选扫描使用已有tag/physical直接const检查，不调用find_tag；getter与shadow-ref检查重复读取不改变选择。未来事件采集禁止为观察候选而额外调用lookup。

## 时间与有效性边界

本候选模型在原access commit内执行有界set scan，没有新增simulated-cycle延迟或自由的延迟参数。它增加并行状态读取/最小值选择所需工作；这是一项显式软件时间模型假设，不是硬件免费、单周期可实现或同频证明。真实时序/端口/面积资格另见资源门槛。AF ON是新替换策略，旧性能不能直接视为AF结果；OFF differential仅限定CPU见证，不证明完整输入数值/性能等价。
