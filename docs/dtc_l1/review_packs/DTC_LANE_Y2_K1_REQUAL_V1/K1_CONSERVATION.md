# OO K1模型守恒资格

**PASS_K1_OO_MODEL_SCOPE**，仅限本包实际执行的OO逻辑模型/API及逐字生产函数体范围。绑定Lane V `26abd496417d9392245052e54fbd9ba27c6ffd96`；行为Core `c0a5e2c31e407c57e3a4af3ce529c921e8059a05`。不以全ISA数值正确性作为OO结构资格的假定前提。IO=`IO_K1_UNIMPLEMENTED_STOP`，MODERN=`HOLD`。

两层独立实现于Y2测试包：

- **直接生产API**：真实`oo_frontend`、`source_invalidation_observer`及链接真实ordinary L1D的invalidate/cycle/drain，finite OFF/ON各测；物理容量1迫使同ID generation递增、多个消费者保护及最后引用回收。使用生产protected custom-Tag构造入口，避开完整GPU perf-counter注册；未修改cache源码。
- **逐字生产函数体夹具**：提取行为Core的源选择、传递、LDST hook、返回路由、ready选择、collection、WB、sidecar和lower-credit方法；21项提取绑定包括冻结K0对照。除给两个source-selected block加可调用wrapper、给冻结方法改名，函数体无改写。`EXTRACTED_BODY_BINDING.json`记录原文件/位置/SHA。clock、scoreboard、packet accessor、WB grant和寄存器/scoreboard完成后端是显式夹具；OO状态机、服务、observer及ordinary cache均为生产实现。没有完整GPU/LDST ABI对象或NoC模拟。

|V合同|已运行输入与观察|证据边界|
|---|---|---|
|K1-01|source_negative、idle-cluster部分SM未完成、跨cluster选择、重复idle、MEMBAR scoreboard guard、cache status同/异|真实选择语句在4个CPU SM上下文执行；没有模拟真实warp调度或kernel|
|K1-02|ready retained Ref0即时free、pending Ref>0隐藏保留、E后同址新identity、旧新返回分离|直接生产API与源函数体均有positive changed Tag证据|
|K1-03|grant只存cycle，E跨grant/commit；width1阻止第二引用，E不回滚第一引用；前端ready但LDST引用未全接纳时不可选择；全接纳后关闭2个依赖|没有真实coalescer/dispatch流水；选择与所有权算法是提取的生产语句|
|K1-04|四sector按乱序完成、重复/address/write非法返回断言、旧generation断言、PIB slot递增、inflight已erase但finite metadata仍pending、4/6 waiter后late第7个|packet访问器/析构为夹具，不覆盖真实mem_fetch构造/NoC；distinct乱序应接纳|
|K1-05|collection中E、真实WB拒绝分支连续两次、Refs不减、最后成功WB后close/retire/free；同warp older proxy阻止younger ready退休|WB grant为受控输入，未运行真实operand collector仲裁；完成后端用生产completion_accounting，不验证寄存器值|
|K1-07|STORE/ATOMIC/BYPASS/PROXY四种sidecar的生产admit/complete/retire；无E负控不清Tag；E与sidecar不破坏外部依赖；同warp proxy过滤保留|没有执行真实store/atomic payload或WRITE_ACK；不可提升为coherence或ISA保证|
|K1-08|请求与ordinary提交分离、重复请求、同bank quota保留、多bank撤销、同cycle E→R→W / R→E→W / R→W→E|给定调用序列可重演；目录sweep仍是X明示的原子零新增模拟cycle理想化操作，不是硬件端口/PPA结论|

实际状态采样含physical allocated、Ref/shadow、frontend/LDST PIB、inflight、credit acquired/released/outstanding、关闭依赖、WB拒绝计数和map-loss计账。每个snapshot调用生产shadow-ref断言；每次检查`acquired-released==outstanding`。两个同址lower请求各有独立保存的physical/generation与sector mask，final distinct sector才归还credit/erase inflight；metadata仍保留Ref，最后真实成功WB分支才释放。capacity压力输入和最终drain状态额外约束物理重用。

`inputs/production_cases.json`预先保存各phase的期望字段和退出码，`production_cases.cc`是可核合成序列。最终结果保留完整观察字段而非只报PASS。非法返回/错代和不支持模式要求指定SIGABRT及对应诊断（Python退出码-6，shell通常134）；不是任意崩溃即可通过。每个比较另有故意缺失字段的错误期望，要求独立比较器退出1；这只证明比较器拒绝错误期望，不冒充生产故障注入。

`UNCHANGED_PATHS.json`进一步核对7个生产方法与冻结函数体逐字相同，包括OO memory-cycle、lower-create/issue、response、WB、sidecar及ready选择。K1的hook只改lookup/安全回收，未改这些队列算法。完整lower-create/ICNT注入和真实packet的端到端组合未执行，静态相同不替代该集成测试。

尚未测到的真实寄存器load值、store/atomic效果、跨SM coherence、release/acquire/scopes、真实mem_fetch/NoC与完整shader/LDST对象集成保持**UNPROVEN / NOT_RUN**。不把这些未测项报告为PASS，也不据此抹掉已有OO模型结构资格。未修改Lane X源码，未发现需要X修复的生产bug；开发期夹具的构造/命名/时序输入问题已只在Y2修正，开发输出留在独立external目录。
