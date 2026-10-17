# Source request and ordinary commit timing

固定Core `c0a5e2c31e407c57e3a4af3ce529c921e8059a05`，X Framework `49fb5d1b62b6f2387abc2d568bc8ae7543dc0df4`，V合同 `26abd496417d9392245052e54fbd9ba27c6ffd96`；均独立fetch-back。完整差分没有新增kernel-done事件、STORE自动失效或PROXY清Tag。

本次完整ABI对象最小序列：

|cycle/phase|实际操作与核验|
|---|---|
|1、5|实际LDST issue；5仅三消费者输入，pending hit共享旧physical|
|8|真实ordinary L1D API接受miss，产生fill owner/MSHR/credit和下行packet|
|9|真实warp MEMBAR标志+真实Scoreboard pendingWrites；不选E，已存在Tag仍可查询|
|10，LDST request|两次明确IDLE_CLUSTER source请求，经core→LDST；首次立即隐藏Tag，第二次幂等；ordinary pending且commits=0；service edge保持旧值。这里为受控入口调用，不是完整idle guard见证|
|11|第三load（若启用）实际issue，ON重新miss至新physical；OFF pending merge旧physical|
|12..15|旧请求实际sector child按3、1、0、2交付；Ref继续保护metadata/collection/WB|
|15..20|真实operand collector bank占用导致WB拒绝，不提前释放|
|23|ordinary root fill后实际MSHR consumer drain；ordinary cache cycle使pending清除，observer首次commit=23；没有用DTC drain替代ordinary条件|
|24..27|ON三消费者新physical的四个返回；与旧identity隔离|
|31..34|不调用LDST service，保留clock-gated间隔|
|32|暂置flush flag=0；真实`change_cache_config`先同状态、后不同状态、再重复同状态；只有不同状态向两cluster各SM发E；执行完整原cache配置后续处理，几何保持相同；恢复flush1|
|36|真实MEMBAR pendingWrites=0清除，仅本SM收到E；第二次调用不发E|
|41..43|真实`gpgpu_sim::cycle()`执行三个空CORE tick，两idle cluster每tick均有请求。没有kernel/trace/runtime模拟线程；重复idle不去重、不重复free/map-loss|

finite1三消费者ON：SM0 source totals idle5/membar1/config1（requests7），SM1 idle3/config1（requests4）；首次request10、首次ordinary commit23。observer提交是ordinary pending→clear的一次invalidate尝试，可能是unused Tag array no-op，不声称ordinary数据一定变化。DTC positive control另以实际`will_new_miss`及changed=1核验Tag确实不可查询。

活动cluster部分SM未完成、跨cluster不同活跃状态只由原Y2逐字生产条件/求和/传递fixture验证，因此K1-01整体PARTIAL；不能从本次空GPU tick推断真实kernel边界语义。cache-config独立于flush flag，MEMBAR依赖该warp scoreboard及flush flag；静态完整差分确认上游guard未改变。

同cycle E→R→W、R→E→W、R→W→E，以及grant/commit跨E、same/multi-bank quota继续由原逐字源体/API用例给出确定调用次序；本次没有把这些全排列都放入完整shader调度。K1-08 PASS仅指这个已披露OO模型范围。

`ldst_unit::invalidate`先做occupancy观察采样再撤销DTC lookup，再调用原ordinary invalidate；采样不advance return service、也不补充bank/allocation/collection/retire quota。目录sweep是**source请求时原子、零新增模拟cycle**的当前模型假设，不是硬件零延迟/端口带宽/PPA证明。事件顺序不证明architectural load值、写后可见性、跨SM coherence或完整ISA。
