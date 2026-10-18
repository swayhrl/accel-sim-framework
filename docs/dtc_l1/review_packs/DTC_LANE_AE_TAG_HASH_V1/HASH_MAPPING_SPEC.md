# Fixed bank-preserving Tag-row hash

Goal `DTC_LANE_AE_BANK_PRESERVING_TAG_HASH_174_V1`；原 `huangrulin-174` / root。固定父Core `e32afdcf44be3374ff36d22568ed01a075459b6f`；实现Core见`Core_SHA`。只有一个预先固定候选，没有应用trace输入或未来地址预知。

开关：`-gpgpu_dtc_l1_tag_hash_bankrow`，生产bool注册默认 **0**，可由原option parser echo。ON初始仅whole-line PAPER_OO + finite V1；其它mode、finite0明确abort。B必须4，S为2的幂，S>=4且S%4=0；其它ON geometry明确abort。外部custom-cache构造入口ON也明确STOP；常规生产LDST构造入口支持。OFF不加新的geometry约束，保留旧索引和旧模式边界。

对byte address A：

```
S = 2^s, B = 4, L = A >> 7
bank = L & 3
row  = ((L >> 2) ^ (L >> s)) & ((S / 4) - 1)
set  = 4 * row + bank
OFF: set = (A / 128) % S
```

ON中row范围[0,S/4)，故set范围[0,S)，且set%4=L%4。byte offset低7位不参与映射；所有uint64地址均按相同固定函数解释。S=4时row恒0，仍合法。每种geometry内ON/OFF的S、ways和总Tag数S×ways完全相同；32/64 sets、4/8 ways是四个独立配对，不能混成同一容量实验。

OO内部只有`tag_set(address)`这一set入口，委托纯函数`logical_tag_set`。bank服务、find_tag和select_victim共用它；new-miss、eviction、预检查找和prefetch由原调用链进入。Tag依然保存并比较完整aligned logical line地址，未截短key、未改变返回地址/line大小、physical寻址或Tag/physical数据字段。K1目录失效逐entry遍历整个m_tags，不重新分组，所以自动覆盖所有hashed entry。

保留原`will_new_miss -> find_tag`的LRU写副作用，ON和OFF都保留；不新增peek，不整理旧探测行为。不增加其它lookup调用，也不缓存grant时的旧identity。模式策略在frontend构造时固定，不能在有live Tag时在线切换hash。

未改80KiB/640行physical池、OO128 PIB、Ref/generation、metadata/collection/retire/lower quotas或ordinary C+。旧配置的Tag grant额度默认4全局/每bank1；whole-line LDST memory_cycle原本每次只提交一个reference，两者不同，均保持原样。没有把4-bank误当每cycle四倍reference吞吐。Tag grant→commit的原finite延迟保持；本轮假定XOR组合逻辑装入既有索引时序预算，不增加模拟cycle；硬件代价/时序可行性未证明。
