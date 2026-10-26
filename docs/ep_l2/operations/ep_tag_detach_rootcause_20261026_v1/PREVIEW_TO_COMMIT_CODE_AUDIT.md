# Preview 到 Commit 的生产代码审计

状态：READ_ONLY_CODE_AUDIT；本轮没有执行 simulator fixture。源码权威为 [swayhrl/gpgpu-sim@1093d2629e3d6a9130ba25b9dd119b6f3e16c092](https://github.com/swayhrl/gpgpu-sim/tree/1093d2629e3d6a9130ba25b9dd119b6f3e16c092)。下文文件都在 `src/gpgpu-sim/`，行号只属于该提交。函数短名不表示其它版本具有相同行号。

## 生产路径与可验证反例

|环节与函数|文件、行号|代码证据和结论|最小反例/验证，及状态|
|---|---|---|---|
|raw probe，`tag_array::probe`|`gpu-cache.cc:340–453`，尤其411–427|先返回匹配Tag的HIT/HIT_RESERVED/SECTOR_MISS；INVALID可分配，VALID可替换，MODIFIED有dirty fallback。只有无匹配且所有way `is_reserved_line()` 才rawFAIL。**PROVEN**|16路VALID/MODIFIED满占用仍可MISS；16路有pending sector且第17条不同line才FAIL。历史真实fixture支持，未本轮重跑|
|认证与早期查询，`ep_l2_ro_runtime::candidate/query_admissible`|`ep-l2-ro-runtime.inc:100–135,200–209,251–262`|certified GLOBAL demand read才进入RO；resident HIT不创建RO；directory/TVD及单slice ticket/每GPU cycle查询可提前拒绝。plan的RESERVATION_FAIL不必是raw TagFAIL。**PROVEN**|QUERY early denial可以无rawFAIL；SGEMM visible候选全resident hit、transaction0是接受的应用反例|
|RO preview，`ep_l2_ro_runtime::preview`|`ep-l2-ro-runtime.inc:263–296`|existing RO映射HIT_RESERVED；新地址rawFAIL且same-set detachable才概念性改MISS。随后capacity/WAD仍可拒绝；preview只预测，不detach。**PROVEN**|detachable为真但D512耗尽：最终plan拒绝；直接调用access可能detach后deny，不代表Frontend可达|
|native fallback，`l2_cache::preview_access`|`gpu-cache.cc:2727–2754`|nonRO在RO preview返回false后走native fallback；rawFAIL直接all_reserved并return，没有调用detachable。**PROVEN路径限制**|all16 pending RO + nonRO新line：eligible存在，但frontend deny、relieve未consult。已有NATIVE_REQUESTER控制实际执行|
|Frontend，`memory_sub_partition::cache_cycle`|`l2cache.cc:1332–1344,1414–1425,1456–1465,1521,1559–1563`|snapshot→preview→admission；line_available=false或exact&&!admit阻止调用access。生产不等于直接fixture access。**PROVEN**|上行nonRO反例直接access可relieve，却不能绕过Frontend作为应用证据|
|commit入口，`l2_cache::access/ft_access`|`gpu-cache.cc:2508`；`ep-l2-ft-cache.inc:299–338`|query admissible、owner冲突、merge、directory先于raw probe。326–329只有实际rawFAIL才relieve→reprobe。**PROVEN**|若raw TagFAIL从未出现，eligible/reuse计数再大也不会调用relieve；三r5应用符合|
|选择，`ep_l2_ro_runtime::detachable/relieve`|`ep-l2-ro-runtime.inc:232–249`|仅扫描目标set，从低索引选第一个live且can_detach的handle；调用tx.detach。**PROVEN**|eligible只在其它set时不能救当前set；PRESSURE_ONLY_OTHER_SET_RO已覆盖|
|资格，`transactions::can_detach/detach`|`ep-l2-ro-transactions.h:205–223`|T enabled、attached、!reuse_seen、required&~ready；runtime还要求live。detach执行再次验证。**PROVEN**|16条pending但全部sticky reuse可FAIL而0detach；历史PRESSURE_STICKY_REUSE支持，不是三应用的联合证据|
|Tag解绑，`ep_l2_ro_runtime::detach` / store port|`ep-l2-ro-runtime.inc:159–175`；`ep-l2-ro-store-port.h:105–109`|先校验Tag generation/handle/owner；失效4个Tag sector，清Tag→payload并增加Tag generation；旧payload保持owned/pinned，转DETACHED。**PROVEN**|同line新Tag有新handle；旧返回不能靠line地址落到它。PRESSURE_ELIGIBLE历史实际验证|
|sector发出与lower接受|`ep-l2-ro-runtime.inc:299–309`；`ep-l2-ft-cache.inc:626–632`；`transactions.h:226–246`|issue把包放MissQ；真实lower accept才调用lower_accepted设置issued/payload.pending。required-not-ready不能直接称DRAM在飞。**PROVEN**|包排在MissQ仍可能可detach；在lower accept前fill应被拒绝，不可伪造返回完成|
|旧返回，`ro_fill/transactions::fill`|`l2cache.cc:1259–1261`；`ep-l2-ro-runtime.inc:392–399`；`transactions.h:248–264`；`store-port.h:61–79`|以包内payload id/generation找旧landing；bank写未获准留在ReturnQ；获准才ready；仅attached才tag_ready。**PROVEN**|detached旧fill不操作新Tag；旧handle过期或重复fill报错。有限fixture已验证新Tag不被旧返回标ready|
|响应，`prepare_response/commit_response`|`transactions.h:269–303`；`runtime.inc:348–369`；`l2cache.cc:1219–1249`|waiter mask全ready后，真实bank read grant和同cycle入队才完成。入队拒绝保留descriptor/选定身份；retry重新付费读取，无隐藏data buffer。**PROVEN**|真实ICNT满时payload须保留，consumer恢复后finish；RESPONSE_BACKPRESSURE历史实际验证|
|退休，`transactions::retire_if_done` / store port|`transactions.h:372–379`；`store-port.h:39–49`|所有waiter无、无prepared、required及issued无未ready sector才unpin；detached释放payload，M-OFF释放line MSHR；attached转resident。**PROVEN**|仅第一个sector返回不能清除另一pending；分项sector fixture覆盖，完整组合仍UNKNOWN|

上述 `transactions.h`、`runtime.inc`、`store-port.h` 分别简称 `ep-l2-ro-transactions.h`、`ep-l2-ro-runtime.inc`、`ep-l2-ro-store-port.h`，不是其它文件。

## 真正 TagFAIL 与各类拒绝必须分列

raw TagFAIL特指 `tag_array::probe` 的all-reserved返回。Frontend最终plan拒绝、descriptor不足、同地址waiter满、directory未完成、MissQ满或payload pins不能统称TagFAIL。source r5新增 `commit_raw_probe_reached/raw_tag_fail_commit` 与observer head raw计数分别用于生产调用域与covered head-cycle域；二者分母不同。

detachable是结构资格，不包含新请求已经通过owner、ticket、directory、capacity、WAD、MissQ等条件；T-OFF的结构观察也不能当作执行机会。

## detach之后仍会遇到的门禁

|门禁|精确出处|对收益的含义|
|---|---|---|
|共享descriptor512、每地址32 waiter、M-OFF line128与地址唯一性|`runtime.inc:215–230`、`transactions.h:137–147`|Tag解绑不释放旧descriptor，不能凭空增加这些容量|
|MissQ|`ep-l2-ft-cache.inc:334,376`|新请求即使Tag可用仍可能无法发包|
|held frontend与同地址WAD|`ep-l2-ft-cache.inc:335–338`|顺序/写地址保护仍有效|
|payload pins/pending|`ep-l2-ft-cache.inc:355–357`|有replacement候选也不保证commit立即可替换|
|dirty WAD/TVD安装、WB staging/local quota|`ep-l2-ft-cache.inc:377–413`|还需写回身份与容量；不可把保护关掉以求触发|
|同bank landing、bank port|`ep-l2-ft-cache.inc:402–406,148–169,487–521`|detach保留旧payload占用，bank争用不会消失|
|ReturnQ、response/ICNT|`l2cache.cc:1219,1261`|旧事务持有资源直到真实消费者与返回路径推进|

这些路径的存在为 **PROVEN**；其对当前应用关键路径的净影响为 **UNKNOWN**。已有DETACH_THEN_LATER_DENIAL控制证明direct access可先detach后因capacity拒绝，不证明正常preview必让这种调用发生。

## Observer 与执行语义

- `gpu-cache.cc:2978–3014` 的 `detach_diag_snapshot` 调真正probe，传空mf以免修改held-request身份telemetry；r5取同一时刻目标set的16路及live RO predicate。
- `ep-l2-tagpressure-diag.h:58–82` 同一snapshot计raw/reserved/eligible/reuse/reason，结构谓词与can_detach相同；运行T开关与runtime-off的NA另列。
- `gpu-cache.cc:3019–3030` 的Frontend实际callback只记录一次route/admit；实际生产probe执行时核验snapshot raw一致。RO preview的rawFAIL分支才设置consulted，不能以“访问了RO preview”代替“咨询了relief”。
- TVD handled在 `l2cache.cc:1313–1319` 绕开普通RO/FT relief observer域。TVD分支本身可能做probe，WAIT后也可能回普通路径，因此skip不是全路径无probe/无压力证明。
- 重复preview32次已证observer不增数并有最终semantic witness；每次preview的完整模型snapshot不变，测试覆盖仍有限。
- phase是event-time标签，不是requester/victim kernel的因果身份。NA不填0，不乘独立边际。

结论：没有发现会把三应用的实际TagFAIL正数全部隐藏成零的已证统计故障；完整未覆盖域仍为 **UNKNOWN**。Vector本轮raw重解码与已接受终态一致，不独立证明observer之外的所有cache状态。

## 源码谱系核验

A2 Core9243 与 r5 Core1093，逐字相同的blob：

|文件|Git blob|
|---|---|
|`ep-l2-ro-transactions.h`|`c3b766434bf8641d2c0ec3830e5f499a4779c0ee`|
|`ep-l2-ft-cache.inc`|`a1a86322555bd238b7be3547fceb2aab4263ea1e`|
|`l2cache.cc`|`0ff2c0bd752e163e243d11773a62228ee0df079d`|

runtime差为r5 observer注册/销毁/输出，gpu-cache差为r5 registry/snapshot/Frontend记录；本轮读取精确提交，不借用branch最新源码。native d010事务blob为 `2a17e5f9967cea5a3225036132b405b1ef97954c`，ft blob为 `892358e5b00bd58017aefde6b934f887693f3ea7`，均不同；持久reuse guard、same-set first eligible及nonRO preview限制在该版本也可见，但不能由此继承binary或统计资格。

证据获取：原生repo是partial clone；只读git show触发promisor lazy fetch挂起后，停止本轮发起的读取，改由GitHub connector按精确commit取blob。没有checkout、修改或构建protected source。**本文件的所有代码结论是阅读源码；历史执行支持详见 [最小诊断计划](MINIMAL_DIAGNOSTIC_PLAN.md)。**
