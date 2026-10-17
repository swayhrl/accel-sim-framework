# Source事件和时间边界

行为锚点：Core `c0a5e2c31e407c57e3a4af3ce529c921e8059a05`。Lane V合同固定`26abd496417d9392245052e54fbd9ba27c6ffd96`。X已发布Core push/fetch-back exact-match收据由Framework `741a56a0f1f6f3a66653538b3897aab764114747`的Git对象读取；Y2另自远端核对/fetch源，独立detached source和build。原STOP提交未用作K1。

|最小CPU序列|期望与实际|
|---|---|
|新flag=1，但source flush=0，Tag已有映射|无E，changed=0，Tag继续可查询|
|flush=1，cluster0内一SM未完成，cluster1全idle|cluster0保持可见；cluster1每个CPU SM收到E，changed=1，至少一条此前可查询Tag变成miss|
|下一cycle仍idle|重复请求计数增加，changed不再增加；不重复free/map-loss|
|MEMBAR仍有scoreboard pending|不发E；pending清除后按原flush条件只选本SM|
|cache status同/异|同状态无E；变化时遍历两个cluster，独立于idle flush条件；只提取条件广播部分，不执行真实cache配置重建|
|ordinary持有fill owner；cycle3 E，cycle4重复E，cycle5 owner drain|DTC在cycle3请求入口隐藏旧Tag；ordinary pending到cycle5才清，首次ordinary commit=5；旧DTC Ref仍为1|
|同cycle显式E→R→W、R→E→W、R→W→E|三种次序均只有一次目录变化，credit/inflight清零，关闭依赖一次；最后一种Ref0即时reclaim，其余保留到WB后最后Ref释放|

这里的source guard、cluster not_completed求和、SM传递和LDST hook均来自逐字提取的生产语句，环境值由CPU夹具提供。测试没有创建真实GPU的完整core/cluster对象，也没有观测Gaussian/GEMM真实事件计数。实际kernel-done并未添加事件；不能称为每个kernel必然统一broadcast。

ordinary对象使用真实L1D cache pending/drain实现，源码与冻结blob相同。commit观察是pending到clear的一次ordinary Tag invalidate调用，可包含未使用Tag-array的no-op；不声称ordinary内容一定变化。DTC positive control单独使用真实`will_new_miss()`前后查询及changed计数证明目录实际变化。

source E只撤销lookup，不推进return/waiter服务，不刷新allocation、bank、collection或retire quota。same_multi_bank用4个bank的实际grants及同bank拒绝测试E前后quota未重置；partial/late waiter/WB输入验证已有服务成本与引用保护。X的目录遍历在host调用内原子完成，**新增模拟cycle=0**，这是本轮明示模型假设；不是芯片单cycle实现、真实RMW带宽或PPA资格。

不新增全局kernel事件、store自动失效、proxy清Tag、额外drain或去重语义。跨SM数据一致性、全ISA值与实际硬件延迟均UNPROVEN；这里只认已执行的source选择和OO模型时序/身份资格。
