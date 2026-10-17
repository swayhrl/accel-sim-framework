# 值可见性相关的可达源事件表

此表补充V1的值路由证据，不重新选择K1入口。`C0`=冻结Core `6fba0136f8465b59fe5858a950fa39efb265f654`；`CX`=已发布X Core `c0a5e2c31e407c57e3a4af3ce529c921e8059a05`；`F`=Framework build `18a68dcccd795f1b6cda75504e9450d00c9cee02`。路径相对各自仓库，行号按对应版本。全部源码通过固定Git对象读取；文件hash见 [SOURCE_SHA256.tsv](SOURCE_SHA256.tsv)。不进入X/Y写目录，不读取实际trace body。

|ID/事件|可达条件与实际路由|可用身份/状态|尚无的值语义；future K2审查用途|
|---|---|---|---|
|R01 trace解码普通LDG/LDL|F:gpu-simulator/trace-driven/trace_driven.cc:369–404，width/address；LDG/LDGSTS/LDL默认CACHE_ALL，STRONG且GPU或BYPASS置CACHE_GLOBAL|活动mask、地址、width、opcode、register依赖；LDGSTS单列|不能把任何SYS字符串自动视为同一路由或完整scope实现；不推native值|
|R02 trace解码STG/STL|同文件:406–420，普通store，global/local分类；STRONG.GPU/BYPASS条件同上|每动态指令UID、width、活动lane地址；后续生成coalesced byte mask|解码不执行通用store payload写；不能将所有SASS store等同write-evict或统一旁路|
|R03 global atomic/red|同文件:422–430：ATOMG/RED/ATOM设LOAD_OP、isatomic=true、global、CACHE_GLOBAL；shared ATOMS:447–451另路|opcode与atomic标志，原请求/完成路径|global atomic在此到L2；不是DTC可合并load；需值、RMW、结果寄存器/RED语义区分|
|R04 cacheable/bypass分类|C0:src/gpgpu-sim/shader.cc:3880–3982；global/local/param-local；CACHE_GLOBAL/L1空/global skip条件；atomic优先|所选route；load的128B line refs；非load sidecar没有地址引用|K2不能在sidecar admission凭空推每个transaction写地址/byte/实际接受；shared/texture/constant不自动纳入|
|R05 合并覆盖|C0:src/abstract_hardware_model.cc:558–584、716–772，逐lane width建bytes/chunks，再压缩segment并构造mem_access|128B内byte mask、32B sector mask、active lanes及实际下层事务地址|mask表示范围，未提供写byte内容或读取版本；K2最少需地址区间交集与稳定动态transaction键|
|R06 store成功接受|C0:shader.cc:3728–3813、3933–3981；ordinary可能HIT/MISS/RESERVATION_FAIL，旁路须ICNT接受才pop accessq|transaction/UID、was_write_sent/read_sent、重试与真正accepted可区分|future write intent候选，不能在重试时重复登记；allocation/dispatch admission不等于数据发布|
|R07 ordinary write policy|C0:src/gpgpu-sim/gpu-cache.cc:1551–1631、1919–1932：WB改modified，WT发write并更新自身metadata，WE发write并invalid自身sector；miss另有WA/FOW/LFOR配置|ordinary byte mask、Tag状态、write事件|只作用ordinary，未更新独立DTC；不同policy需各自定义可见性点，不能把WE当全domain事实|
|R08 store侧完成|C0:shader.cc:5307–5310，dispatch退出observe_complete；2621–2680是external-dependency sidecar，地址refs=0|source_completed、external dep、PIB退休|不是逐事务ACK，也非byte publication；K2不能用它代表写完成|
|R09 store ACK|C0:shader.cc:5083–5089→6937–6943；WB hit且无write_sent还可3780–3789本地ack，部分WA路径3800–3813也可本地ack|每warp outstanding计数与reply；source route/policy可辨|ACK不统一代表下层持有新值；WB无lower write就是反证条件。要补不同策略的V(W,domain)，不能套通用WRITE_ACK|
|R10 原global完成/atomic|C0:shader.cc:4523–4529、4571–4632，原writeback_complete与atomic count；F:trace_driven.h:65–75 should_do_atomic=false|原完成与sidecar关闭分开；不重复执行架构副作用|没有从header给真实RMW结果；不能把完成数量当exactly-once值证明|
|R11 pending fill|C0:shader.cc:3140–3176、3451–3483，UID/root UID、address/mask后complete(record.physical)；C0 common.h:633–685有限metadata/waiter|原physical+generation、sector已收/未收、waiter/PIB slot generation|返回晚于store不代表取样晚于store；generation不表示byte版本；future K2需保留既有consumer与分离新lookup/read-from资格|
|R12 K1-source-request E|CX:shader.cc:4014–4025；opt-in OO调用observer.request；CX:dtc-l1-invalidation.h:60–87，先frontend.invalidate_lookup后ordinary.invalidate|selected SM、source/cycle/order、旧identity/Ref、delta changed/retained/reclaimed|用户已定入口；common.h:573–606只撤映射与安全回收，没有写payload；不是K2|
|R13 ordinary pending-commit C|C0:gpu-cache.cc:1268–1285、gpu-cache.h:1474–1476；CX observer在request/cycle返回观察pending变化|ordinary queue/owner/MSHR是否排空，C可晚于E，多个请求可合并至一次退休|C不是E，不是byte visibility；unused Tag时commit观察也不代表Tag改变|
|R14 source E的上游条件|C0:gpu-sim.cc:1749–1755配置变化；2515–2527 flag+各cluster not_completed==0；shader.cc:6875–6889 MEMBAR清除且flush_l1；CX对应source enum已标注|被选SM集合和原guard可直接读；MEMBAR只查询该warp scoreboard|不把idle反复触发变为唯一kernel-end，不把MEMBAR注释当store ACK证明；不更改用户第3项入口|
|R15 真正kernel-done D|C0:shader.cc:5484–5527→gpu-sim.cc:1027–1043；stop_all_running_kernels:1046–1052也可记finished|kernel ID/end-cycle/finished记录|不证明自然排空、API同步、所有SM选中E、地址重用或lower数据版本|
|R16 PROXY_FENCE|F:trace_driven.cc:715–720只明确FENCE.VIEW.ASYNC.S；C0:shader.cc:5205–5228、4656–4678、2683–2707|source flag、external dep、OO同warp年轻候选退休阻挡；shared/SYNCS/TMA issue规则|不发布通用store payload；不阻所有年轻global请求、不提供跨SMcoherence；regular LDST fence assert不支持|
|R17 可选trace值字段|F:trace-parser/trace_parser.h:81–107；trace_parser.cc:368–376；trace_driven.cc:508–513、725–848有限BAR/SYNCS消费|schema可以有reg_dest_vals/reg_src_vals，不能断言“格式无值”|没有通用普通load/store payload传播/逐load比较闭环；本轮不核实际trace含量或capture绑定，归W|

上表所有future K2事件候选都只是**可达源码位置**，不是已存在的coherence事务接口。写意图、真实接受、ordinary sidecar完成、ACK、本地/下层发布、consumer选值必须分开。新研究若需要生产payload或新hazard状态，应另行授权；V2只给规格，不注册开关、不插入hook、不改变服务/仲裁。

发布快照：初读X Framework `0c8fcb…`旧报告绑定 `f8b34dd7a738caddf4f23dd417e34c0b63c206d9`；Y V1也是该Core。发布前已补fetch/read-back X Framework `49fb5d1b62b6f2387abc2d568bc8ae7543dc0df4`，确认其报告已绑定CX=`c0a5e2c3…`的source请求K1，状态为本地CPU通过、Lane Y独立验证pending。旧STOP只作历史，不再当成入口待定。所审5份F路由源码在冻结build18、X trace-build `0c8fcb…`及最终review之间逐字节相同；这不证明binary/runtime同一。V2的header probe不验证observer/普通cache整体集成、全部K1条件或performance，也不假定Y V1已验证CX。
