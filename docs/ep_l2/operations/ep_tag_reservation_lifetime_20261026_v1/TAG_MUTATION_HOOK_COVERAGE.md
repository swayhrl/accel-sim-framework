# Tag状态写入覆盖与证据边界

主整合：以下是B对精确11c源码的只读证据表，保留其STATIC/CPU范围。当前完整Vector OFF/ON已另行接受且NI PASS；它不使未执行的policy/atomic/active-window flush路径自动变为已测。应用结果见OBSERVER_NONINTERFERENCE_REPORT.md；A首次HOLD及后续TLS、TVD、tick边界修复记录全部保留在工程证据。

# Tag mutation hook coverage — exact code evidence

审查身份：Core **11c02df1034112013523429894f1f931323adbef**，父提交 **1093d2629e3d6a9130ba25b9dd119b6f3e16c092**，tree **5495ec739845b075356a8c67ff289763c56ad2aa**。所有行号固定在11c；下表文件均相对 src/gpgpu-sim/，测试路径另外标明。简称 lifetime.h=ep-l2-reservation-lifetime.h，transactions.h=ep-l2-ro-transactions.h，runtime.inc=ep-l2-ro-runtime.inc。永久源码入口：[11c source](https://github.com/swayhrl/gpgpu-sim/tree/11c02df1034112013523429894f1f931323adbef/src/gpgpu-sim)。

**PROVEN / STATIC** 表示阅读精确源码证明钩子覆盖该写入点，不等于该分支在工作负载或CPU矩阵中执行。**CPU** 仅指已结束的合成组件22执行/11同binary OFF/ON pairs；本次没有测试、模型、GPU或运行中ON观察。该表不预判应用NI或最终科学结论。

## 实际状态写入与上下文

| Hook / 函数 | 精确位置 | 观察语义 / 已执行边界 |
|---|---|---|
| line_cache_block::allocate / fill / set_status | gpu-cache.h:205–217、219–230、243–246；lifetime_notify:191–194 | 写完状态后回调；整line RESERVED用15，INVALID用0。STATIC；本轮11pairs使用sector配置，不能声称line-cache运行覆盖。 |
| sector_cache_block::init / allocate / allocate_sector / fill / set_status | gpu-cache.h:322–337、340–369、372–397、400–416、450–454；lifetime_notify:313–319 | 每个真实原语后读取4sector状态；any-sector RESERVED定义episode。validmask是所有非INVALID位，包含RESERVED，并非ready mask。CPU：SECTOR_OVERLAP_REENTRY、LIFETIME_SECTOR_REENTRY。 |
| tag_array::lifetime_allocate / lifetime_allocate_sector / lifetime_fill / lifetime_set_status | gpu-cache.h:1088–1104 | 每次原有mutator调用期间绑定(owner,原block指针,index)；原API/参数/返回顺序保留。 |
| tag_array::access | gpu-cache.cc:489–547，allocation:516，sector:526，touch:545 | 真实MISS/SECTOR_MISS落到上述包装；RESERVATION_FAIL不touch。真实成功访问只增一次Tag requester。CPU：sector、realFAIL、merge等控制。 |
| tag_array::fill(addr) / fill(index) | gpu-cache.cc:556–585、588–597 | 原有probe后的allocate/sectorallocate及fill均包装；包含同tick allocation→ready/valid中间状态。CPU：sector乱序、reentry、generation。这里的probe是既有生产probe。 |
| tag_array::flush | gpu-cache.cc:600–615 | FLUSH reason:601；实际INVALID写:607。STATIC active-window覆盖；fixture.finish的flush在observer close/print后，不能算活动窗口flush验证。 |
| tag_array::invalidate | gpu-cache.cc:617–631 | INVALIDATE reason:618；真实逐sectorINVALID:623。STATIC；11pairs没有独立活动窗口invalidate分支覆盖证明。 |
| tag_array::tvd_bind | gpu-cache.h:1191–1203 | TVD_BIND reason:1192；TLS context:1194覆盖allocate:1198及所有set_status:1201。防止allocate→VALID零时长episode漏记。CPU：TVD_ZERO_DURATION、WAD_EARLY_NO_FAKE_ALLOC。 |
| l2_cache::ft_try_force_tag_access | ep-l2-ft-cache.inc:17–20；raw_notify在 lifetime.h:378–382 | untimed_scope恢复原timed标志；若观察活动期遇untimed写，置invalid8388608且不伪造timed allocation。header standalone已测；生产11pairs没有“活动期host prefill”定向执行。 |
| TLS owner/block/index检查、嵌套恢复 | ep-l2-reservation-lifetime.h:360–382 | 无block成员指针；wrong-block无事件，析构恢复外层；untimed嵌套同理。B standalone mutation_context / mutation_off / untimed_active实际PASS；具体生产调用点另由本表STATIC审计。 |

### 全部9处 block-alias lexical scopes

下列是绕过tag_array包装、直接持有cache_block_t* block的9处新增mutation_scope。**每处STATIC均已核对**；11pairs没有逐site访问计数，不把普通write成功扩张为9种policy/atomic分支全部实际执行。

| 函数 / 原有mutator范围 | gpu-cache.cc 行号 |
|---|---|
| baseline_cache::fill，atomic fill分支 | 函数1671；scope1707（覆盖后续atomic status/mask写入） |
| data_cache::update_m_readable | 函数1887；scope1889 |
| data_cache::wr_hit_wb | 函数1909；scope1917，真实MODIFIED写1921 |
| data_cache::wr_hit_wt | 函数1929；scope1943，真实MODIFIED写1947 |
| data_cache::wr_hit_we | 函数1959；scope1972，INVALID写1976 |
| data_cache::wr_miss_wa_fetch_on_write，命中reserved/full-write分支 | 函数2081；scope2105 |
| 同函数，read-for-write/miss分支的fill控制位 | scope2186 |
| data_cache::wr_miss_wa_lazy_fetch_on_read | 函数2214；scope2251 |
| data_cache::rd_hit_base，atomic read/write分支 | 函数2314；scope2324 |

这些scope也覆盖set_modified_on_fill等延迟控制位；真正的状态转换仍在原fill原语回调记录。并非所有metadata位写入都是新的RESERVED episode。

## RO detach、返回、人口及退休

| 生产函数 | 精确位置 | 证明 / CPU范围 |
|---|---|---|
| ep_l2_ro_runtime::ready / detach / matches | ep-l2-ro-runtime.inc:159–175 | ready先matches再包装VALID写:168；detach reason:172、包装INVALID:174、清Tag handle及生产generation++:175。CPU：GENERATION_DETACHED_OLD_RETURN、PRESSURE_ELIGIBLE、RESPONSE_BACKPRESSURE。 |
| transactions::admit | ep-l2-ro-transactions.h:149–156 | 真实admit成功后observe_lifetime。RO initial ready由observer出生单列，不能冒充下游return。 |
| transactions::merge；attached merge的真实Tag touch | transactions.h:196–205；runtime.inc:314–326（真实access:323）；gpu-cache.cc:545 | observe后merge_marker只加MERGE；实际access加一次REQUESTER。detached merge不touch新Tag。CPU：RO_MERGE_PACKET_ONCE断言2packet/1merge；sector控制同时验证initial-ready。 |
| transactions::can_detach / detach | transactions.h:210–227；observe_lifetime:363–367 | 原资格T && attached && !reuse_seen && required未ready不改；真实成功detach后观察。观察“eligible”复用同一纯predicate表达式，不新增relieve。 |
| transactions::lower_accepted | transactions.h:237–253 | 原实际lower接受、issued mask更新:249后才观察:250。发出人口不是ready返回人口。 |
| transactions::fill | transactions.h:255–273 | 原issued/repeat/tag-generation校验:258–261；fill_write失败:262直接返回；成功ready更新:263后观察:264；只有attached才tag_ready:268–270。旧detached返回不写新Tag。CPU：generation/late return、sector乱序、response背压。 |
| transactions::commit_response | transactions.h:299–312 | FIFO拒绝:304–305不释放waiter；真正接受、释放descriptor/erase waiter:308–310后观察:311。CPU：RESPONSE_BACKPRESSURE。 |
| transactions::retire_if_done | transactions.h:387–395 | 等waiters/prepared/required与issued pending全部清空；retiring观察:391在原unpin/release之前，随后live=false。CPU：上述所有完整drain控制。 |
| 观察端RO身份/出生/返回/退休 | ep-l2-reservation-lifetime.h:203–227 | live slot跨generation/set不一致置invalid；出生ready单列RO_INITIAL_READY:214；真实ready delta:220–221；retire时间/人口:227。standalone及linked merge/sector/oldreturn控制。 |

**两个generation命名空间不能混用**：observer的Tag-incarnation generation在lifetime.h:164–170增加；生产RO tag_binding generation在runtime.inc:332及detach:175改变。它们分别服务观察身份与原协议身份，数值相等不是联合身份的证明。

## 时钟、Frontend及Stage边界

| Hook | 精确代码 | 边界 |
|---|---|---|
| 观察启用、首tick seed | lifetime.h:71–74；gpu-cache.cc:243–260 | 只有环境变量EPL2_TAG_LIFETIME=1启用；只为64set/16way/sector几何创建observer，首tick从真实Tag状态seed carry。未发明冷启动allocation。 |
| co-timed domain之前准备所有slice | gpu-sim.cc:2139–2142；l2cache.cc:1210–1215 | next_clock_domain之后、CORE/ICNT/DRAM域动作前建立L2区间；cache_cycle入口可重复begin但不推进ticks。 |
| tick_end / window / finish | l2cache.cc:1759；lifetime.h:273–296、298–314 | end只增一个L2 tick；write_window的end<=window_begin守卫:274防重复begin重复发窗。unit=L2_tick，GPU锚点是core_cycle，非Tag API时间/host memcpy offset。 |
| RO epoch关闭 / print | runtime.inc:390–395、406–407 | 原完整drain门禁通过后finish，再打印一次。跨观察起点/终点分别left/right censor；不是截尾样本零时长。 |
| 真实Frontend观察 / commit | l2cache.cc:1469–1476、1594–1599 | 使用既有diagnostic_preview.raw；前端admit失败只观察head，不冒充allocation；真正access成功才NEW_COMMIT。 |
| 真实生产TagFAIL | ep-l2-ft-cache.inc:327–331 | 原生产probe结果为RESERVATION_FAIL才加PROD_TAGFAIL；紧随其后的relieve/第二probe是父1093已有逻辑。CPU：REAL_TAGFAIL_PREVIEW32、TAGPRESSURE_CAPTURE_JOINT。 |
| TVD early / downstream | l2cache.cc:1327–1330、1309–1310、1813、1842、2120、2685 | TVD_EARLY、lower queue阻塞、DRAM_SERVICE、DRAM_RETURN、RESPONSE_ACCEPT、L2_INGRESS均附着原事件位置。每项是事件/观察次数，不是可相加的GPU停顿cycles。 |
| L1/ICNT侧 | gpu-cache.cc:1627–1633、1822–1823、2514–2538；shader.cc:4718–4721 | 原L1成功/miss/merge/queue失败计数读取与实际send/inject位置；没有新传输或bank请求。 |

真实linked11pairs很短，未穿越8192tick窗；WINDOW边界的数学/打印由B standalone window（8194tick）及reference比对验证。全生产调度器的跨域窗边界在这里仍是**STATIC**，不能把它描述成11pairs已执行的8192边界测试。

## 实际CPU覆盖与未执行部分

V2权威矩阵 control/CPU_LINKED_FIXTURE_RESULTS_V2.json，SHA **6e86258fc3ccc3a614f96926e9ff2248f543b29c83cace794eadecf480c67839**。B独立review [FINAL_CPU_SOURCE_REVIEW_V2.json](v2/FINAL_CPU_SOURCE_REVIEW_V2.json)，SHA **b0971e5c275081a077f63104fdbf64b5b667f7889fe691e378082e034613c756**。

| 真正执行的同binary OFF/ON控制 | 生产测试源码入口 | 有界覆盖 |
|---|---|---|
| SECTOR_OVERLAP_REENTRY；RO_MERGE_PACKET_ONCE | tests/ep_l2/test_reservation_lifetime.cc:60、90 | 多sector重叠/乱序/re-reservation，同incarnation；packet/merge不双计、initial ready不伪装返回。 |
| REAL_TAGFAIL_PREVIEW32；GENERATION_DETACHED_OLD_RETURN | 同文件:102、128 | 真实16way+第17失败/relieve，32次preview内observer memcmp不变；detach后Tag重用及旧返回隔离。 |
| TVD_ZERO_DURATION；WAD_EARLY_NO_FAKE_ALLOC | 同文件:152、176 | TVD瞬时allocation/清reserved可见；真实dirty WB/WAD阻塞区间无假allocation，set_done后drain。 |
| LIFETIME_SECTOR_REENTRY | tests/ep_l2/test_detach_diagnostic.cc:186–207 | 最后一sector返回才EXIT；后续sector进入REENTER而非新ALLOC。 |
| TAGPRESSURE_CAPTURE_JOINT | 同文件:247–265 | 16pending、matching HIT_RESERVED、新TagFAIL；32preview前后整observer memcmp和r5覆盖人口不变。 |
| PRESSURE_ELIGIBLE；RESPONSE_BACKPRESSURE；NATIVE_REQUESTER_RO_VICTIM | 同文件:237、232、242–246 | detach reachability、response FIFO背压前进性、native前端未咨询relieve vs direct access后续directory拒绝的已知生产边界。 |

11pairs证明这些合成控制的原semantic witness全部字段OFF/ON相同，并在V2重编译后与保留V1 CPU witness相同。**不证明**：全部9种block-alias分支、活动窗口flush/invalidate/hostprefill、全应用64slice非干扰、任何真实应用TagFAIL存在、性能收益或真实硬件实现开销。

## 静态无额外probe / ABI / 有界状态合同

- **PROVEN / STATIC**：新增代码不调用额外Tag probe、directory CAM或bank arbitration。Frontend原raw来自父1093已有 detach_diag_snapshot（gpu-cache.cc:3033–3045，原probe:3038）；缺旧diag时不会新探测补数，l2cache.cc:1474置invalid2097152。因此本次合格域仍要求旧DIAG1/TAGPRESSURE1。
- 额外miss_queue_has_slots（l2cache.cc:1475–1476）是纯occupancy读取；total_fail_reason/select_stats_status（gpu-cache.cc:2515、2531–2538）读取既有counter/status。静态无额外模拟动作不等于对所有输入已证明无功能扰动；CPU及最终应用NI分别提供各自范围证据。
- **PROVEN / qualified native ABI**：没有cache_block_t/line/sector成员或virtual接口增长，TLS替代初版block指针。gpu-cache.h:143–188字段与r5相同；实际syntax proof agent_b/cache_layout_syntax.cc:400–403断言base24B和三类sizeof与精确r5相同；真实SDK重验回执 agent_b/runs/layout_retry_ebdbeef3-2b3c-4a83-a449-194efda2e8e5/RESULT.json。这不是任意编译器/配置ABI承诺。
- **PROVEN / declared qualified geometry**：lifetime.h:14–15固定64×16×4、RO1168、33bins、8192窗；345–351静态与factory限额。sizeof(observer)=211464B；64份=13533696B，含2MiB固定余量=15630848B<16MiB。tag_array的observer指针/attempted标志（gpu-cache.h:1082–1083）、transactions observer指针（transactions.h:91）和固定TLS/registry归入该固定余量；没有按max-cache-block人口新增字段。此合同不是整个模拟器RSS上界。
- OFF factory不分配observer（lifetime.h:346–351）；TLS只在原mutator调用期间绑定。header.counters饱和并置invalid（112–114；32bit人口/代数检查:141–142、167、178）；输出全局16MiB限制、fwrite错误/overflow明确标记（15、82–89、340–343）。溢出/缺END由严格解析拒收，不视为有效负结果。
- incarnation/episode不同：new allocation清packet/mask并增generation（164–170）；any-reserved 0→非0开episode，最后reserved清零才关闭（176–182）；同tick瞬态保留EVENT_PEAK（188）而tick末峰在295。面积/截尾闭合在298–313校验。反复preview不会调用这些生产写入hook，已由32次memcmp控制给出有界执行证据。

A最终静态结论见 agent_a/INTEGRATED_HOOK_REVIEW.md 的“Second integration review and final TVD follow-up”；前半部初版HOLD是保留历史，不能摘取成当前未修问题。B standalone与layout补证见 agent_b/VALIDATION_V3_REPORT.md（早期layout HOLD保留）及后续真实SDK PASS回执。C严格wire/数学review由SourceQ8ed的 independent_C_review_v2 绑定。以上来源按其实际执行/静态范围引用，均未把CPU证据升格为应用科学接受。
