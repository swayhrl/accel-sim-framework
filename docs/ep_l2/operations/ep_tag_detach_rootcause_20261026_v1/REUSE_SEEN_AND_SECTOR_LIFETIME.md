# reuse_seen 与 Sector 生命周期

证据身份：除另注外，源码行号对应 GPGPU-Sim Core `1093d2629e3d6a9130ba25b9dd119b6f3e16c092`。r4的transactions文件与r5相同blob `c3b766434bf8641d2c0ec3830e5f499a4779c0ee`；native/main61不同，不套用行号或统计。审查只读，未改guard。

## reuse_seen 的含义

**PROVEN**：`ep-l2-ro-transactions.h:120–160,181–202,205–223,346–352`。

1. admit用新 `entry()` 初始化事务，reuse_seen=false。
2. 成功merge完成descriptor预留、添加waiter并合并required mask后，于198行设置reuse_seen=true。一次成功merge就足够；失败merge不应视作成功reuse。
3. 212–215行注释明确：merged waiter退出后该保护仍持续。位在整个entry生命期不清零，只有新事务构造时重置。
4. can_detach条件是 `T && attached && !reuse_seen && (required & ~ready)`；runtime还要求live并限制同一目标set。

因此它描述“这个事务曾成功复用过”，不等于“现在有几个waiter”，不等于“Tag已被另一个line复用”，也不等于当前有硬件数据复用收益。不能从reuse累计数推导当前多waiter或TagFAIL共现。

## required、issued、pending、ready、response 的顺序

|阶段|状态变化|精确源码|
|---|---|---|
|admit/merge|required为waiter需要的sector并集；创建waiter及资源保留|`transactions.h:120–160,181–202`|
|issue|构造带payload id/generation的sector lower包并放MissQ，不等同已被lower接受|`ep-l2-ro-runtime.inc:299–309`|
|lower accepted|真实lower接受才设置issued与payload.pending；重复/不合法接受受保护|`ep-l2-ft-cache.inc:626–632`，`transactions.h:226–246`|
|fill|旧包定位旧identity，真实bank写成功才清对应pending、设置ready；attached才更新Tag|`transactions.h:248–264`、`ep-l2-ro-store-port.h:61–79`|
|response|waiter所需mask全ready；付费bank读取，真实FIFO接受才释放该waiter/descriptor|`transactions.h:269–303`、`runtime.inc:348–369`|
|retire|waiters空、无prepared、required及issued都无未ready时unpin；detached释放payload；M-OFF再释放line MSHR|`transactions.h:372–379`、`store-port.h:39–49`|

can_detach看 `required & ~ready`，不是 `issued & ~ready`。因此“eligible RO”可以包含还在MissQ、没有lower accept的sector；它不是DRAM飞行人口。ready也不等于requester已收到response；ICNT满可使ready payload继续持有pin/descriptor。

detached旧事务没有Tag仍可完成：Tag解绑仅清映射并增加Tag generation；payload保持RO ownership/pin。lower packet携带旧payload identity；fill不查新Tag地址来落数据；detached不会tag_ready。response/retirement依赖旧entry及waiters，直到真实完成才释放资源。

## 与实际压力的联合

本轮实际执行的 [离线复核](OFFLINE_CHECK_RESULT.json) 对Vector的同set snapshot联合重新求和：

|统计|值|单位/含义|
|---|---:|---|
|reuse way总暴露|3884686|每个covered head下live RO way累积，非独立事务|
|newTag且reuse way|706461|同一raw/set snapshot的way暴露|
|任意reuse的head|2856709|reasonPresence bit4，同set至少一条RO有reuse|
|newTag且任意reuse的head|673364|真实head联合|
|rawFAIL且reuse way|0|真实rawFAIL联合|
|rawFAIL且任意reuse的head|0|真实head联合|

predicate mask bit2表示reuse；reasonPresence bit4表示HAS_REUSE。newTag只选raw MISS/RESERVATION_FAIL。统计来自单次snapshot，未相乘边际；TVDskip375000的这些维度为NA。结论 **PROVEN（covered域）**：reuse发生了，但没有与实际TagFAIL共现；不能说它阻断了这些应用的detach。

CFD/DWT本轮核对的approved projections未给完整reuse联合，保持 **UNKNOWN/NA**。它们已观测production rawFAIL=0，但这不补出TVDskip和其它未覆盖路径的reuse统计。

## 哪些条件保守，以及哪些仍未证明

**PROVEN（策略）**：曾merge、但merged waiter已退休的RO仍不准detach。历史PRESSURE_STICKY_REUSE fixture特意构造先merge再退休部分waiter、仍有pending的情形，detach为0；它证明guard生效，不证明guard必须或可以删除。

**HYPOTHESIS（可另行证明空间）**：fill/response/retire保存多waiter和payload，似乎不要求事务从未merge。可以研究仅剩一个waiter或一般多waiter情况下的证明，但本轮没有证明地址唯一性、descriptor寿命、同line重请求、generation与响应顺序在放松后仍安全。当前不能宣称“存在已证明安全的reuse detach”。

**PROVEN（排除）**：all-ready但等ICNT的attached RO不满足missing条件。**LIKELY**：Tag通常已经没有RESERVED sector，这类事务不是all16 RESERVED TagFAIL的主要可救对象；不应把它当零触发根因。

**PROVEN（另一条边界）**：非RO requester即使同set有eligible RO，也可能在Frontend被拒绝，未到relieve。direct access能够解绑不等于开放Frontend后完整执行正确。相关生产代码与历史fixture见 [代码审计](PREVIEW_TO_COMMIT_CODE_AUDIT.md)。

## 测试覆盖边界

历史PRESSURE_ELIGIBLE验证旧返回不把同line新Tag误标ready；RESPONSE_BACKPRESSURE验证旧detached返回在真实ICNT满时保持payload直到consumer恢复。sector lifetime测试验证一个sector返回不清另一个pending。它们不是“detach＋多sector乱序＋同line新Tag＋ICNT满”的完整组合证明。该组合保留为一个可选CPU case，见 [最小计划](MINIMAL_DIAGNOSTIC_PLAN.md)；本轮未执行，也未据此放松任何协议条件。
