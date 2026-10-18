# EP-L2有限服务小改动：源码审查与并行Goal V1

2026-10-18。用户授权继续从源码寻找可实现的小型性能优化，RTL降本R3已给原Lane2执行。本文件新增的是隔离的性能候选，不修改已接受H0/四模式结果，不打断Lane2 R3。发布不是运行；各Lane收到对应指令后执行。对照优化后的强基线；不把通用控制改进冒称动态容量的独有收益。

## 0. 精确起点与资源边界

- 有限SIM规格Core `9bd30ed913c5058b5d952fbeb2e67cb5e4644b3f`；Framework `8ab6013ea90755fdc74819e92090c2de50f4f199`；binary `fb67448d08818bc8cbe72961580e8340f0e6f337a4df95e7c8ee9468472953f7`。新的候选源码/binary必须新命名；OFF与ON均用候选正式同binary，不用旧cycle恰好相同代替身份。
- 原H0 Core7b8/Framework9bd/binary2309和五输入1.0016002037656606不重写；已接受combined四模式比较独立保留。
- 本次读到Lane5 HEAD `bbffccf90fd21550df15170a85804d5dea2db7fd`，STATUS快照2026-10-17T20:14:08Z：28/72 starts，21 parallel rows CURRENT_ACCEPTED，generation47，0 active sim，`NO_CURRENT_SAFE_ENVELOPE_FOR_REMAINING_READY_CELLS`。这是已发布快照，不假定现在资源仍同样，也不声称有后台推进。
- 全应用仍只有原Lane5中央执行器有权启动；先读实时registry/current pointer/真实PID与start_ticks/boot、磁盘、source/撤回状态，保留他人/在途任务。
- 保留现行全局16GiB结果总额、72次总启动、原T0及2026-10-18T11:30:14.500719Z停止新增启动期限（北京时间19:30:14）。workspace48GiB/Share40GiB/availableRAM64GiB、全局4sim/8CPU/32GiB预约等不变；Lane2更严格own限制不动。新的全应用也计入原remaining starts；过期/无安全空间则交付候选及证据，不换campaign逃避边界。
- 本文件授权producer的小型定向测试/构建与下一轮配对设计。Lane5收到本增量后，才可在安全准入下注册最多24个新增full-app starts（含新source锚点及重试），仍从原72扣除，不另加72。新cell逐一列入manifest，未跑旧cell保留NOT_RUN而非删除。未触发场景、未合格与性能负例分别记录。

## 1. 本轮代码实际发现

### 1.1 MissQ只服务队头；WB bank等待会挡住后续独立demand read

`src/gpgpu-sim/gpu-cache.cc:1575附近 baseline_cache::cycle`仅取`m_miss_queue.front()`，在`!m_memport->full(...) && lower_ready(mf,cycle)`时pop/push。
`ep-l2-ft-cache.inc:390附近 l2_cache::lower_ready`对L2_WRBK_ACC必须再取得一次原payload/staging bank read，非WB直接返回true。
所以队头WB即使下层有位置，也可能因bank冲突停止整个MissQ；第二项独立读miss的向下请求不需这次本地WB read。这是可构造的结构机会，尚未测出全应用性能贡献。

### 1.2 bank逻辑保留了未消费grant，但未显式确认其消费者此刻就绪

`gpu-cache.h:2440起 ep_l2_payload_store::request`在新physical cycle将oldest pending移入m_granted，未消费选择跨周期保留；新op只有selected/pending全空才用空闲service。
`l2cache.cc:1180附近 cache_cycle`中，response只有!L2->ICNT full才调用ft_response_ready；fill按真实返回队头；WB lower_ready只有下层可接收时才调用。
因此必须检查“已保留选择的消费者受非bank背压而未就绪，另一个bank请求实际就绪，但本周期真实bank services=0”的场景。保留请求身份是正确性/前进性要求，永久独占未用端口并不是同一要求。只能通过当前实际ready信息优化，不能用‘本周期还没被C++调用’冒充not-ready。

### 1.3 不是所有直觉上的小技巧都值得立刻做

已接受H0五输入B/U的RESOURCE_MOVEMENT.csv中pin_block=0、pool_full=0；现有计数不能证明所有前端阻塞已完整覆盖，但暂不支持先把pin-aware victim或任意跨bank landing设为主性能方向。
Tag::probe原本不看payload pins、ft_access之后可拒绝，确有可改点；在没有激活证据时先降优先级。
现有前端pending还保护预检过的MissQ资源和victim身份，不能简单删除`m_ft_pending.request!=mf`拒绝条件来获取假并行。
`cache_cycle`先写fill，再在响应路径读payload，有限的refill-to-response forwarding也是后备候选；必须有真实有界数据载体、byte/sector合并与snapshot/响应口预算，本轮不自动开发第三种机制。

## 2. 两个首轮候选

### MQ2：两项MissQ窗口的独立demand-read越过受bank阻塞的WB

范围严格限L2 finite ordinary nonatomic路径，独立开关默认OFF。原MissQ总容量不变，查看最多队头+下一项，不扫全队列、不新增数据储存、不提高每slice每cycle一个lower enqueue上限。

规则：先按原路径尝试队头；若队头为L2 WB、下层可接收但WB本地bank未grant，检查第二项是否为普通demand read。仅当其128B line与所有被越过请求不同、不会越过atomic/fence/volatile/acquire/release或其它顺序约束、下层确实可接收、请求身份/发射合同有效时，允许服务第二项。无法从现有输入/请求元数据证明安全顺序则不越过。head WB保留原handle、generation、WAD、年龄及pending-op，绝不取消或重复发出。任何同line、写、write-allocate、atomic、控制/未知请求均保留原顺序；queue pop按选中项精确执行；bank实际已消耗服务不能撤销。

该优化对B16/S64/Unified同样开放。硬件账包括二项指针/selector、地址/类型比较、必要head-age与仲裁逻辑；若队列RAM不能两项可见，需要真实小型head prefetch/指针窗口及其成本，不能只因C++ list支持就宣称零代价。首版depth=2不扫参。测试必须证明head恢复就绪后按原优先服务，无starvation。

### RG1：保留请求身份与年龄，但不把bank给当前不可服务的消费者空占

独立开关默认OFF。先构造真实生产队列背压的定向例；若无法在合法路径复现，报告未证实，不编造性能收益。

实现采用有界真实client ready信息（response/fill/lower-WB/frontend实际队头及各自当前phase），每physical cycle对bank选择oldest-ready，不丢弃old pending/sequence，只允许显式not-ready的老请求暂时不占用当cycle grant。旧请求重新ready时恢复年龄优先；不得固定每cycle清空m_granted，不得重复grant、在P1消费>1、以timeout取消数据，不得把尚未按C++调用顺序到达的请求一律视为不ready。

必须处理ready在同cycle内变化、grant-consume错位、取消/rollback、同slot读写及generation复用；如旧(r,id,write)不能区分并行逻辑请求，需要有限可综合的client/transaction token并实际计费，不用无界oracle。调用顺序/收集与仲裁的阶段变化必须清楚披露；额外register/latency不隐藏。持续ready请求不能饿死；旧READY ownership liveness regression必须保留。

必要计数：per-bank physical services，held-not-ready周期、其中存在another-ready的周期，actual recovered grants，first-ready/first-attempt/consume间隔，按client的最长等待和取消；这些是机制观测，不求和冒充GPU独占stall。

## 3. Lane1新Goal：EPL2_FINITE_SERVICE_MICROOPT_PRODUCER_V1

1. 原Lane1窗口独立新worktree/候选分支，不reset旧release；读本文件及相应源函数。先检查相关源是否已有新修正，精确冻结基线。
2. 按MQ2先、RG1后顺序交付两项独立开关；每项生产定向验证通过即发布，不等两项全齐。MQ2先解决最小MissQ head问题；RG1需先合法复現empty-service场景再改arbiter。
3. 建立OFF逐项回归、B16/S64/U功能和物理clock/offset/host-prefill/byte-mask/sector/UID/WAD/drain、同line顺序、bank双花、head恢复与晚到重试的定向证据；只重跑受影响部分。不得注入非法状态伪造自然触发。
4. 发布生产core/framework源码、精确binary/config/effective dump、模式组合支持矩阵、可复用测试、有限控制metadata/比较器/额外buffer预算。若加 pipeline或改变tag/数据接口，单列成本与性能合同。RTL R3仍在Lane2，不同步改其源码；仅交一页delta供后续整合。
5. 默认OFF、现有Ideals/RO/TVD/atomic等不继承新资格；首轮只支持H0有限B16/S64/U。不能用对原生控制的共性修正仅加在Unified上。
6. 45分钟交定位与第一例，2小时交首个producer候选，最多4小时交两项/实际阻塞，不建大型调度框架或常驻poller。普通工程问题solve-and-continue；行为边界改变要单列候选，不伪称等价修复。发布原Lane1和独立Core分支，nonforce push回读。
7. 不启动完整应用；release就绪交Lane5。任何编译/测试均按现行中央lease和资源下限，不挤掉正在跑的Lane2/其他项目。

## 4. Lane3新短Goal：EPL2_SERVICE_OPPORTUNITY_AND_MATCHED_EFFECT_V1

先读已有accepted raw、bank/队列/窗口数据和本源码位置，用≤1小时完成“已实测/源码可构造/未证实”的机会表；不凭aggregate count补不存在的ready/服务时序。重点核实MQ2被挡读、RG1 retained-grant空转、frontend/WAD等待是否发生在代表输入。

复用旧数据：明确H0 pin/pool计数为0，避免浪费本轮在未激活优化上；WAD-full、same-address等待和lower背压分开。若缺新事件，只给Lane1最小observer接口并在其小型case中核对，不另起全应用观测工程。为Lane5生成三模式OFF/MQ2/RG1同源比较表和结论模板，计算绝对cycles与交互，而非只取最佳点。

Lane1给producer或Lane5给结果时做短增量；无结果不等待、不后台轮询。不改原始ledger，不跑完整应用；将已有四模式及对照结构用于进一步归因。独立脚本/derived/简短中英文段落/失败边界一并发布。Lane2仅继续R3，不给它插入新performance任务。

## 5. Lane5增量CONTINUE与配对次序

收到明确本轮CONTINUE后，核实控制器是否仍活着；活着只增量登记兼容单元，不重复起Goal/执行器；若已正常STOP，按新阶段续接原ledger并保留T0、starts、PID历史，不当作新campaign。当前报告无安全空间时先fresh preflight，仍不安全则发布确切瓶颈，不能因为CPU空闲就绕过磁盘限制。

先独立资格，后完整应用。初始矩阵为Conv/FWT × B16/S64/Unified × OFF/MQ2/RG1，共18个逻辑端点。各端点在同一候选binary上；已接受同binary且内容不变锚点可复用。producer只有MQ2先到时，可先做对应OFF/MQ2，同一个有意固定的producer发行策略避免为了小改频繁换binary而重跑全部；若二版binary新生成仍要严格源一致，不拼数。实际最多24次new full starts含额外锚点/重试/组合，且所有starts仍计入原72。源端只有一个候选证实时只做相应子集，不凑18点。

单因素齐后，仅在真实就绪/等待证据支持且剩余预算与原期限允许时，追加MQ2+RG1同配置三模式，优先一个输入3次（00/10/01均已测）。单因素近零不自动排除联合收益，但不能无依据全扫。失败、未触发、无安全空间、负收益原样保留。超过预算需新授权。

至少报告：C_B, C_S64, C_U及各OFF对照；S_EP(o)=C_B(o)/C_U(o)，S_static(o)=C_S64(o)/C_U(o)，interaction=S_EP(o)/S_EP(OFF)，同模式绝对提速。若两边都变快而S_EP不扩大，这是一项通用服务优化，不是EP独占收益；论文可作为更强基线，不能只拿B(OFF)对U(ON)。最终候选的适用范围和独立输入验证另列，不以本轮两个开发样本冒称普适。

若定位的是模拟器记账/正确性错误而不是新调度机制，先按实际影响修正B/S/U共有基线，保留原证据并做范围审查，不把错误修复算作EP-L2新增贡献。

## 6. 暂不实施的候选与论文边界

- 不直接撤销frontend pending锁：它保护victim、预留issue/WAD/landing和跨周期回滚。若要hit-under-pending，需要可证明的独立读路径与Tag端口预算，不是删除if。
- 不在lower_accept提前清WAD：本地payload可释放不等于同地址排序责任结束。
- 不关闭symbolic/UID/byte-mask/终态验证换快数据，不改变host offset或计时起终点。
- 暂不跨bank任意landing、不扩大payload/metadata容量、不加理想端口；上述属于新结构，必须实价控制。
- refill-to-response forwarding可作为后备，但本轮无第三机制授权；它需有界sector/line snapshot、未被更新覆盖的版本、同line dirty-protection合并、返回口/寄存器/缓存写入预算和全部对照。
- 最终稿只收入accepted实际性能和对应新增硬件/时序边界。本合同交付的是计划与代码审查，不是性能测量。