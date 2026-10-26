# 为什么Vector单set只有浅Tag压力

决定：**维持现有T，不放松reuse/sector/协议保护，不继续为了非零detach扫描参数。** 已接受同ELF OFF/ON中真实TagFAIL、生产relieve、detach均0；这是本次真实应用窗口缺少Tag容量机会的科学负结果。新被动observer通过完整非干扰核验，补足寿命与瞬时事件证据。

## PROVEN：压力发生在哪里、没有发生在哪里

375000个真正独立NEW全部成功commit；旧915784是重复head观察，不能当独立新请求。唯一NEW到达时，同目标set已有RESERVED的真实联合如下：

|到达前RESERVED|0|1|2|3|4–16|
|---|---:|---:|---:|---:|---:|
|unique NEW|120344|236185|18390|81|0|

有pending的unique NEW254656/375000；结构性eligible RO与unique NEW同现1409次，但没有TagFAIL。结构性observer判据不是额外生产can_detach调用；不能把这1409称为被浪费的detach收益，也不能用reuse边际量相乘产生联合机会。

全部4096set全run均收到NEW，每set91–93次（91:1904set、92:2120、93:72）；说明地址需求在64slice×64set间广泛且均衡分散。这里是整run覆盖，不是所有set同时活跃。每slice已有B0总RESERVED峰90–96，不能将全slice并发误称全GPU缺乏MLP，也不能将各set不同时间峰相加假装同时状态。

|每set峰值|2|3|4|
|---|---:|---:|---:|
|tick末峰|3034|1062|0|
|事件峰|60|3951|85|

85个set确实瞬时达到4/16，且全部area_R4=0；因此旧“最大3”是tick末口径，不能写成所有中间事件也只有3。新observer纠正了该口径，但离16路不可替换仍远。时间加权面积R0/R1/R2/R3分别74165027/181153693/51852375/188649 set-ticks，R4–16全0；描述性均值0.928633 reserved/set，不据此预测失败概率。

## PROVEN：零寿命占多数，但不是所有预约都很短

|人口|完成数|0tick数|总L2 tick暴露|均值/tick|
|---|---:|---:|---:|---:|
|NEW|375000|125000|285397933|761.061155（含0）|
|RE|375121|375000|26457|0.070529|
|非零NEW|250000|0|285397933|1141.591732|

总750121 episode，500000为同tick闭合；LEFT/RIGHT均0。RE只占0.009269%预约暴露。最大完整NEW3735tick、RE430tick。因此“所有Tag寿命很短所以没压力”被25万个千tick级非零NEW否定；零时长transition确实不积累持续占用，但正寿命预约的空间分散与到达重叠同样必要。NEW/RE直方图不带read/write标签，不能仅从0/非0直接给每个请求贴类型；生产TVD写入路径的0时长解释见源码覆盖，尚无逐请求类型交叉表。

## PROVEN / LIKELY：sector共享和RO合并减少身份并发

观察到1500000 requester、1500000个incarnation内不同sector请求和375000 unique NEW，四个sector共享一个Tag身份。RO有250118个事务、749882次merge、1000000 required/issued/新增ready位及最多4个waiter，全部闭合。不能把merge计数误报为节省DRAM包：实际issued仍为1000000 sector。相同line不同sector的共享有直接证据；未证明大量重复同sector访问。

INC closed人口含65536个seed carry记录，seed只为非INVALID owner建立incarnation，应与完整观察new incarnation分开。实际kernelslist两条16MB HtoD先于kernel，perf_sim_memcpy=1；精确源码路径将其连到首tick前untimed prefill，能解释非INVALID初始owner，不能称invalid空slot或旧科学结果。wire未单列carry requester sum，不把排除carry后的4/line算术包装成逐carry测量。最终65536个right owner不是未完成reservation或RO。最终CSV保留carry列和原始口径均值，读者不得把含carry的closed均值当无截断的新Tag平均。细节见EVIDENCE_INDEX中的C边界核对。

LIKELY：广泛set分散、sector/RO共享，以及多数零暴露RE同时限制独立预约Tag积累。没有实验识别三者排他份额，不强行唯一排序。前后级MissQ/lower queue/Frontend压力与这些浅预约同窗共存，相关性与限制边界见UPSTREAM_DOWNSTREAM_TEMPORAL_JOIN.md。

## 因果边界与下一决定

每set有限窗口均满足面积=NEW+RE+censor暴露，enter−exit=0；同人口率×完整平均寿命只作一致性恒等核验。不将全GPU到达率×RO平均延迟外推16路失败概率。没有同set16路与新Tag需求共现，T生产路径未获得触发机会；已执行构造性CPU压力可触发，当前数据不支持将零触发归于实现坏掉或仅统计漏报。

UNKNOWN：其它CFD/DWT/Conv窗口的事件级寿命分布、放宽保守eligibility的安全空间、真实TagFAIL之后各资源门禁抵消多少收益、T在有压力负载的端到端收益。本轮只对Vector新增寿命数据，不改其它应用历史结论。

HYPOTHESIS / 未执行：若未来独立授权需要进一步定位性能，可固定binary/trace/config，仅隔离DRAM服务条件的一个物理含义明确因素，比较本地服务、同set压力与cycles；此前DRAM域已验证敏感，单独L1 MissQ扩大已有负结果。该新实验不在本Goal自动执行。人工延寿、降associativity或放reuse guard制造压力，不能作为真实应用收益。本论文应称T为有CPU正确性支持、在这些真实应用中未获Tag压力机会的可选机制，不能宣称T贡献了已见端到端加速。
