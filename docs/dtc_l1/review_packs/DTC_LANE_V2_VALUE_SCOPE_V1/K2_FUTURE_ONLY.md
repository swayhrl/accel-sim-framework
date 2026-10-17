# K2候选研究的最小值规格——FUTURE ONLY

**NOT_IMPLEMENTED / NOT_AUTHORIZED_FOR_IMPLEMENTATION。** 用户只批准本文件的候选规格、源事件表与独立CPU合成见证。K2必须另行授权；本Goal不加开关、不写Core、不打开新机制、不运行性能，不以本文件授予Lane AA派发权。K1入口已裁决为source请求E，K2不得借机移动它。

## 要回答的新增问题

在没有选中E时，ordinary/bypass写或global atomic可以完成原路径，旧DTC同址映射仍可命中；即使有E，E也不发布写值。K2的备选目标是**地址感知的写后可见性**：对明确属于支持域、明确要求观察某写的后续读，拒绝用过期byte版本完成。它不是“所有写一律清空DTC”，也不是“多加一个完成屏障就全ISA正确”。

最小规格只约束结果和生命周期，不选定snoop、转发、写更新、读阻挡、重试或其它实现机制。CPU `value_oracle.py`只按fixture给定read-from检查字节，**没有K2缓存/hazard协议或时序实现**。

## 候选最小域 D2（尚待授权和证明）

起步候选为单SM、显式排序的单writer/consumer、global数据、规范化无alias地址、一个已限定width的标量访问、无竞争写；每笔写payload与byte mask可得，write visibility点能实际绑定。普通store及bypass store若声称支持，均须满足同一地址重叠判据。不能把本候选域写成现有Core/硬件已支持的域。

ordinary write policy分别审：先选能明确绑定publish的既定policy；WB/local-writeback若无下层或forwarding可见性证据，保持UNPROVEN并拒绝晋升。跨SM/CTA/kernel、host/DMA、alias、无同步race、mixed-size race、atomic/RED、shared/texture/constant/async/TMA/LDGSTS和modern sector均不是起步默认保证；后续要覆盖须独立列spec与授权，不用静默缩域来声称全ISA通过。

partial-byte与跨sector是必需的覆盖**判据**。初期生产支持若限制对齐/宽度，必须说明哪些合成用例只作规格边界或负控，不能把CPU跨sector通过当成真实访问准入已通过。相同line但无byte重叠不要求所有byte版本一起变新。

## 正确性条件（必须逐项绑定到实现证据）

令 `B(W)` 为W写入的实际byte集合、`B(L)`为L读取集合；`HB(W,L)`、scope与proxy关系来自已经绑定的目标ISA/执行域，不能由cycle号或sidecar退休发明；`V(W,D)`为W对读取域D真实可见的事件，而不是抽象命名的ACK。

1. **重叠与值**：在D2中，W已对D发布，W按该域的已证顺序先于L，且无中间冲突写时，对 `B(W)∩B(L)` 必须观察W payload；未写byte按各自最近允许写取值。用实际字节比较，不用whole-line generation相等代替。
2. **新读资格与在途旧请求**：write接纳、尚未发布、发布与后续load选值之间的重叠必须定义。只在write intent时撤映射不能充分覆盖“撤后提前新建旧映射，publish后继续hit”的VV24。只在publish时撤映射也不能自动解决已接纳的新读选择了哪个read-from；需完整顺序/结果证明。不得在无证明时静默改写、丢弃或提前完成旧PIB consumer。
3. **旧consumer保护**：K1保留旧identity的要求继续成立。较早load可以取哪个值由其合法read-from决定；旧physical晚返回不自动非法。若新增支持域要求某consumer观察W，而它原已绑定旧allocation，候选必须明确如何满足值条件且不破坏原Ref/return/retire守恒；不能把“保持旧identity”直接升级为“任意旧值允许”。
4. **返回隔离**：晚到旧payload不能污染E后或write版本变化后的新consumer/新allocation。UID、physical、generation区分owner，但同一allocation内的byte版本和写先后仍需独立值证据。sector片段乱序可以合法；重复/未请求/旧generation仍必须拒绝，不能为过关削弱断言。
5. **写恰好一次**：重试、coalesced多事务、拆sector回复、sidecar退休均不得重复或丢失真实store/atomic效果。future atomic扩展还须比较RMW旧返回值与最终新值，RED是否无返回不能混用。VV14只是合成重复效果负例，不是现有atomic故障报告。
6. **作用域**：单SM写入不能凭空使远端SM可见或清Tag；跨kernel的D记录也不自动提供E或payload顺序。扩域须给真实HB/scope、发布与consumer验证，不提供未经证明的全ISA读写保证。
7. **时间模型**：若未来选择增加查找、hazard、返回过滤或元数据状态，需明确latency/宽度/端口/重试/信用归属。正确性域和实现资格确定前不运行性能；CPU合成规格不假装测得新服务开销或硬件同频。

## 可达源事件候选及尚缺的接口

|候选事件|源码可达位置（编号见路由表）|能收集的东西|不能默认成立的事情|
|---|---|---|---|
|WRITE_INTENT / WRITE_ACCEPT|R02、R05、R06；成功cache/ICNT接受每个实际事务|UID、space/address、byte/sector mask、route、重试边界|没有通用store payload，也没有“所有lane同址写的确定次序”保证|
|WRITE_DISPATCH_COMPLETE|R08 sidecar/source完成|指令完成观察与PIB状态|不是每笔事务ACK、不是V(W,D)|
|WRITE_ACK_LOCAL / LOWER|R07/R09，按policy与路径区分|本地WB hit ack或lower回复、outstanding计数|统一WRITE_ACK=publish不合法；必须另证目标域的数据可见性|
|ATOMIC_SERIALIZE / RESULT|R03/R10原global原子路径|atomic标志和route、source完成|真正RMW取值与新值/一次性尚无oracle；不是现成可用于D2的发布事件|
|LOAD_ACCEPT / SELECT|R01/R04，lookup与原pending reference绑定|地址、UID、physical/generation、ready/pending|generation不是数据版本，不能推出合法read-from|
|RETURN_ACCEPT / METADATA_READY|R11原UID/root/sector返回和finite服务|返回owner、片段、waiter与ready阶段|原请求何时采样byte值未知；lower credit释放不等于所有值处理结束|
|E / C / D|R12–R15分别记录|source请求、ordinary commit、真实kernel-done|三者不得互换，也不能当V(W,D)|
|BARRIER / PROXY|R14/R16，source已有guard与pipeline规则|到达与source状态|不得拿PROXY_FENCE退休构造一般全局HB/发布|

本轮结论是**没有已证明的统一生产 V(W,D) 和普通load payload oracle**。若必须新增Core功能才能获取这些材料，记录STOP，不在V2里“顺手实现”。

## 授权后才可进入的最小验收门槛

* 对每个宣称支持的opcode/space/cache route/policy/order/scope明确可达性和payload来源；原始producer/capture与SASS语义绑定、逐load独立oracle不可缺。
* 以完整动态UID+transaction+byte mask比较W与L，覆盖无E L-S-L、partial byte/sector、bypass混用、dispatch/ACK错序、pending-old/new交错、真实E/C/D区别。正例和错误byte/错误read-from/重复效果负例必须成对。
* 对无HB、无visibility点或域外指令明确UNPROVEN/UNSUPPORTED，禁止给模糊“允许旧或新”的兜底值集合。跨SM/kernel与atomic只有通过相应扩域验收才可晋升。
* 生产身份/Ref/return安全验收与payload值验收分开；既有Y V1 FAIL_CLOSED不会被本包改成新K1 PASS。K0等价与任何后续performance派发资格由原负责Lane独立处理，本包没有触发动作。

未满足上述条件时保持 **STOP-K2-IMPLEMENTATION / STOP-VALUE-CLAIM**。这是缺证据的边界，不是宣称地址感知写可见性必然不可能。
