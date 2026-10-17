# K0 default-OFF equivalence audit

**PASS_CPU_BOUNDED_OO_LDST**；完整输入等价性仍NOT_RUN/UNPROVEN。固定新Core `c0a5e2c31e407c57e3a4af3ce529c921e8059a05` 与冻结 `6fba0136f8465b59fe5858a950fa39efb265f654`，两套detached source、独立CMake Release/assertions-enabled库、匹配头文件重编探针。固定X Framework `49fb5d1b62b6f2387abc2d568bc8ae7543dc0df4`已fetch-back。

真实生产config/parser的默认值为0，显式0和1有效；原6项parser/echo比较保留。本次每次运行实际`option_parser_print`输出有效全配置至外部日志，收据绑定SHA。基底config拷贝冻结RTX4080文件，测试中缩为2cluster×1SM，每SM64线程、2warp；所有override在`abi_ldst_probe.cc defaults[]`及逐命令flags中可核。cacheable load是合成、预coalesced的一lane warp，实际进入生产`ldst_unit::issue`，没有SASS decode/functional load值证明。

四组严格三方比较：finite0/1 × 单/三load，各比较新flag omitted、新显式0、冻结无此flag。每组完全相同的内容包括40个LDST时间点、physical/generation/Ref/ready/Tag快照、实际packet cycle/address/size、全部103项公共`paper_frontend_stats`字段及43周期终态；ordinary API miss也发出真实下行请求并归还credit。实际装载库由各进程内`dladdr`核实，不以链接命令或`ldd`替代运行身份。

|finite1 三load例|新omitted|新0|冻结|
|---|---:|---:|---:|
|terminal cycle|43|43|43|
|DTC lower packets/bytes|1 / 128|1 / 128|1 / 128|
|ordinary lower packets/bytes|1 / 128|1 / 128|1 / 128|
|retired / refs / retained physical|3 / 0 / 1|3 / 0 / 1|3 / 0 / 1|
|finite samples / PIB integral / physical integral|43 / 52 / 41|43 / 52 / 41|43 / 52 / 41|
|WB refused cycles / map-loss count|3 / 0|3 / 0|3 / 0|

新ON对照确实不同：该序列DTC lower为2/256、最后allocated=0，map-loss sum/count=13/2。K1没有伪装成默认OFF，差异来自失效后同址再miss和旧生命周期保留。

新增occupancy edge与service edge分离；失效只采样占用，不推进metadata服务或额度。独立矩形面积oracle覆盖31..34的clock-gated区间及32的事件；map-loss按每个physical+generation的可见性丢失到释放独立累计。K0逐cycle及finite全11项严格一致，未发现插桩改变已测finite服务、周期或流量。原14个header probe的28个新/冻结比较仍为辅助证据。

差分审核：OFF仍构造原`l1_cache`，直接调用原ordinary invalidate/cycle；公共OO memory/lower issue/response/ready/WB/sidecar算法的7个函数体与冻结相同。新配置bool、ABI布局、source enum传递以及occupancy helper是明确差异，因此二进制和客户端必须按新头文件重编；新库不能冒充冻结库。

该结果不涵盖实际STORE/ATOMIC/BYPASS/ACK路径、SASS/frontend、完整NoC/DRAM、多SM活跃shader及完整Gaussian/GEMM。建议AA2在其既有authority下对完整同一输入跑新Core K0，形成严格配对，不能依赖旧冻结结果替代；本Lane未派发、未授权新执行。

详见`inputs/abi_sequence.json`、`supplement_r1/ABI_OBSERVATIONS.json`、`ABI_RECEIPTS.json`和`BUILD_IDENTITY.json`。原Y2只含API/源体的收据仍保留，当前完整对象资格由补充收据独立支撑。
