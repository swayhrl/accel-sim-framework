# 给 Lane X 的最小 K1 语义合同

状态：**CONTRACT_FOR_REVIEW；冻结 Core 未实现 K1。STOP-IMPLEMENTATION-CLAIM / STOP-ALL-ISA-CLAIM**。本包只读审查，不授权或修改 Core，不使 A/T/U 旧结果失效或自动升级。K1是最小地址查找失效和身份保留合同，不足以解决一般写后可见性。

## 1. 精确定义事件与作用域

K1仅挂接**源码已有 `ldst_unit::invalidate()` 请求入口**（C:shader.cc:4012），继承其上游选择的SM集合：idle-cluster flush flag+not_completed 条件、cache-config status变化、或普通membar清除且flush_l1启用。三个来源见 [SOURCE_EVENT_MAP](SOURCE_EVENT_MAP.md)。事件记 `E(SM, sequence, source, cycle, phase)`；审查/验收必须能区分 request 和 ordinary pending invalidate最终执行。

这是本最小合同选择的线性化点：**source请求到达LDST时**撤销DTC查找可见性，ordinary仍按其原有pending/drain实现执行。不能静默改成等待ordinary drain再处理DTC，也不能把ordinary m_invalidate_pending当作DTC drain。若实现选择不同点，须显式提出差异并重新审查时序，不能沿用K1 PASS。

不得额外加入每kernel统一broadcast、写入自动invalidate、PROXY_FENCE清Tag或`flush()`=invalidate。真实kernel-done本身没有该调用；不能把cluster条件提升成kernel边界总保证。重复idle事件必须幂等且不重复free/计账；本合同不额外为 idle 去重增加新语义。

## 2. 状态与顺序：lookup不可见，旧身份继续完成

将 lookup-visible（m_tags[].valid）与 allocated/ready/lifetime 分开。对OO，physical.tag_valid必须与有效映射一致；IO必须有可审计的等价映射身份，不能假造现有Ref字段。

1. E前已成功接纳某个coalesced reference的消费者保存旧 `{physical_id,generation}`。撤销每个当前可见Tag，OO同步清对应physical.tag_valid；记录map-loss事件，使finite map_loss_to_free统计继续守恒。**不得改旧generation、ready、Ref、pending_dependencies、waiter、PIB槽generation、lower信用或返回mask。**
2. 对E后才进行的地址查找，旧映射不可见。若同址新访问可以获得资源，则分配另一合法identity（或旧allocation完全安全回收后重新分配并generation++）；不得从隐藏旧allocation直接“命中”或新挂消费者。E前已经接纳的消费者仍使用自己的旧identity，不因失去Tag而重新lookup、重发或重计Ref。
3. pending lower/response/service_return保持原identity。最后sector返回→原complete→finite waiter更新→ready/collect/WB→最后consumer retire按原顺序完成；旧返回不能重新装回已撤销的Tag，也不能填进E后新同址allocation。新旧两笔可以共存，按UID/physical/generation辨别；这是必要的再miss，不应无条件记作错误重复。
4. 尚未被接纳的reference（含partial PIB的剩余reference）遵循E后的查找状态；已接纳部分保持。若lookup grant与commit跨E，明确grant仅预留服务还是已绑定identity。冻结finite `service_entry` grant只保存cycle，access在commit时查Tag；实现不可引入未核的旧结果缓存。E与同cyclelookup/response/retire必须有确定调用顺序，不能双重接纳或丢更新。
5. 最后使用者结束后才回收。OO通常由`!tag_valid && Ref==0`触发，但K1还必须证明该状态下没有旧lower/return-service/waiter/collection身份仍使用该physical。现有自然read生命周期让pending消费者持Ref；新失效实现不能破坏这个归纳前提。**只有地址不可见且所有旧owner结束**才可free；重新allocate时generation++。generation不在invalidate时统一++。

E前无live Ref且ready的OO retained allocation可即时回收；E前有Ref/在途/尚在metadata服务者必须保留。WB backpressure不允许提前Ref--。回收同时维护physical occupancy、Ref shadow和map-loss统计，不能删队列来“修平衡”。

## 3. IO 的额外 STOP 条件

冻结 IO没有Ref计数：Tag victim把旧physical交给替换者的release_on_retire；替换者FIFO退休保护之前所有旧消费者。source invalidate没有替换者，这个保护不能凭空复用。

**不得**将所有隐藏physical挂在当前head、任意一个现有PIB entry、下一条可能永远不来的新load上，也不得为失效创建虚构指令/假引用。这会分别导致提前free、永久泄漏或改变PIB/时序合同。

Lane X若包含IO，必须提供等价的live-owner/orphan lifetime机制和证明：覆盖当前及partial已接纳reference、返回/metadata队列、已存在release_on_retire依赖；重复事件只标记一次，最后owner自然消失才释放。没有live PIB时也必须能回收已ready的隐藏retained行。新增计数/列表及其服务成本必须显式披露，不能伪称冻结IO本来有OO Ref。

若只交付OO K1，应显式标 `IO_K1_UNIMPLEMENTED_STOP`，不能称IO/OO共同通过。若没有可证明的IO orphan机制，本轮合同在此 **STOP-IO-IMPLEMENTATION**，允许继续阅读/设计，不允许一键清空代替。

## 4. 一键清空裁决

`m_tags.clear(); m_phys.clear(); PIB/inflight/waiters.clear()`、重建frontend、全局generation++、清所有Ref或pending计数：**ILLEGAL_K1**。现有source事件只检查线程/scoreboard/配置条件，不承诺DTC排空；已接纳请求仍必须返回原physical。即使ordinary已drain也不足以保证DTC无owner。

一次性使**lookup目录**不可见可以作为逻辑失效的实现选择，条件是旧physical/lifetime原样保留，带宽/周期成本显式，重复事件幂等且统计可审计。不能据此称整套DTC硬件“零cycle清空”。只有另行证明quiescence（包括return-service/collection/partial/ordinary等）才可讨论安全整体reset；这不属于当前K1假设。

## 5. memory ordering 与写后可见性边界

K1不更新写入payload，不刷出ordinary dirty数据，不提供多SM coherence或atomic序列化。source MEMBAR只用其现有条件；proxy只提供其source pipeline规则和DTC同warp younger retire过滤。STORE sidecar在dispatch exit完成观察，并不逐笔等WRITE_ACK。因此：

* `L(x)→S(x)→L(x)` 若无选中的source invalidate，旧DTC映射仍可能被命中；K1没有补这个洞。
* 即使E确实撤销Tag，重新miss读到何值仍取决于write policy、下层可见性、真实happens-before与scope；本合同只保证新查找不能使用撤销的地址映射。
* 旧消费者在E后用旧physical完成是**生命周期安全**，不是宣称某ISA允许其观察旧值。需要对每个声称支持的ordering场景做独立值测试。
* PROXY_FENCE退休、credit排空或A/T/U terminal strict都不能充当数据一致性证明。未实现的regular FENCE、acquire/release/scopes不得推定支持。

## 6. 最小可复核验收（交给实现/验证 Lane；本次未执行 K1）

|编号|必备见证|必须验证的结果|
|---|---|---|
|K1-01|flag0/1、一个cluster内部分SM未完成、跨cluster不同状态、配置同/异、MEMBAR pendingWrites条件|仅source-selected SM收到E；真实kernel-done不会凭空多一次E；重复idle事件幂等|
|K1-02|ready retained Ref0；ready live Ref>0；pending old、E后同址new|lookup旧Tag不可见，旧identity不变，old/new返回互不污染，Ref0且无owner才free|
|K1-03|partial allocation，lookup grant/commit跨E，多line一个warp|已接纳reference保留，未接纳的重查新目录；全引用注册/关闭恰好一次|
|K1-04|sector fragment乱序/重复、请求已erase inflight但finite return尚未处理完、late waiter、PIB槽重用|保存physical+generation；不丢waiter，不复活Tag；错误generation/重复sector被明确拒绝，不能静默忽略|
|K1-05|operand-collector WB拒绝、collection中发生E、最后Ref多cycle才退|不提前减Ref/free，final-ref free一次；generation仅在后续分配增加|
|K1-06|IO无PIB retained、live/partial旧refs、已有victim release依赖、连续E|orphan可追踪、无提前free/双free/泄漏；无需未来请求解锁；不改FIFO/深度|
|K1-07|STORE/ATOMIC/BYPASS/PROXY_FENCE经过sidecar，E不存在/存在分别测|不偷加invalidate，不重复架构副作用；source完成、ACK、sidecar retirement分别记事件|
|K1-08|source E与lookup/refill/retire同cycle、多SM、普通L1 pending|request/ordinary execution/DTC visibility的phase与顺序可重演；原ordinary pending保护不被破坏|

上述每项要给source SHA、有效配置、事件序列与守恒断言；单一总PASS不够。值正确性另测同址store/atomic/bypass后cacheable读、跨kernel及多SM同步的期望值；trace只有地址/时序时明确 `VALUE_CORRECTNESS_UNPROVEN`，不能制造expected value。对X/Y/W/AA共同的停止条件见 [OPEN_QUESTIONS.md](OPEN_QUESTIONS.md)。
