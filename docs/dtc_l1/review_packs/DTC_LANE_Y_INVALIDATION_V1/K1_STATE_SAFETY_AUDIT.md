# K1 状态安全审计

结论：**FAIL_CLOSED，不授权Lane AA。** Lane X发布Core只有科学STOP文档；新失效接口未实现。Lane V合同已绑定`26abd496417d9392245052e54fbd9ba27c6ffd96`，其状态是CONTRACT_FOR_REVIEW，不能提升为实现批准。引用文件的Git blob与SHA256见`CONTRACT_BINDING.json`。

独立源码核查确认：`gpu-sim.cc:2515`之后的idle-cluster条件可逐CORE tick重复，不要求其它cluster完成；cache配置切换不受flush_l1相同条件控制；MEMBAR检查本warp scoreboard。`ldst_unit::invalidate()`仅调用ordinary L1D。ordinary请求可等待miss queue、extra fill owners及MSHR排空后才使Tag失效，这个集合不含DTC owner。具体行号、片段和源SHA见`SOURCE_AUDIT.json`；这些是静态结论，没有捏造Gaussian/GEMM事件计数。

V合同选择在source-selected LDST请求入口撤销DTC lookup可见性；已接纳引用、physical/generation、ready、waiter、PIB slot generation、pending dependencies、lower信用/sector mask保持，旧owner完成后才能释放。新generation只在后续分配增加。E后同址新查询不能挂回隐藏旧identity。没有据此引入全局kernel广播、清空、额外drain或修改ordinary保护。

`inputs/events.json`有25组最小序列，IO/OO及SECTOR_OO共73次**参考模型**比较。每步携带明确输入与预期结果/拒绝码，最终状态预先写在fixture；输出保留完整观察状态。每项额外运行一个故意错误的free-count期望，要求比较器退出1。这是比较器灵敏性负控，不能当成生产故障注入证明。模型拒绝非法事件返回2并检查状态未变化。生产探针的非法返回则要求SIGABRT（Python returncode=-6，shell通常显示134），且匹配对应断言，不能把任意崩溃当PASS。

|用户要求|CPU证据|K1生产结论与缺口|
|---|---|---|
|K0关闭不变|参考K0序列；实际新选项0被parser拒绝|未实现，不能报K0 PASS|
|映射存在且ref0失效|MAPPED_REF_ZERO|OO生产E未实现；IO仅shadow owner模型|
|同物理行多个消费者|MULTI_CONSUMER；生产OO替换后末引用探针|已有替换保留已测；source E未测|
|pending四sector与E交错|E在0/1/2/3/4个返回之后的五组序列|whole-line端到端LDST E未实现|
|重复/乱序sector|重复、未请求、越界负例；生产sector/response guard|不同合法sector的乱序[3,1,0,2]应接纳；重复/非法/错代才拒绝|
|旧generation延迟返回|参考旧代拒绝；生产whole-line/sector负例|已有错代断言已测；E到真实response路由未测|
|PIB slot复用|参考复用负例；生产OO实际槽generation递增|source E期间复用未测|
|pending hit / late merge|参考pending hit；生产finite 4/6 waiter后追加第7个|已测旧metadata队列；E期间的队列保留未测|
|最后引用释放与重分配|FINAL_RELEASE_REALLOCATION / NO_EARLY_REUSE；生产2条旧行reclaim、id复用generation++|已有替换路径已测；E路径未实现|
|重复失效幂等|REPEATED_INVALIDATION / NO_MAPPING|生产E幂等与map-loss首时间戳未测|
|源条件不满足不失效|SOURCE_FALSE抽象谓词；独立源码guard核查|真实multi-SM/cluster/MEMBAR派发组合未执行|
|同bank/多bank Tag状态|lookup bank返回值/冲突，参考多映射失效|K1目录RMW、仲裁、同cycle更新次序和遍历成本未实现|

IO/OO共有部分仅涵盖地址映射与保存identity的抽象要求。IO生产实现没有OO数字Ref；参考模型IO的`refs`明确是**shadow owner集合**，不构成可用的生产orphan算法。生产IO探针保留原FIFO和`release_on_retire`机制。source失效没有替换者，不允许挂到任意head、下一条load、假指令或发明Ref以取得PASS；维持`IO_K1_UNIMPLEMENTED_STOP`。

`inputs/k1_contract_cases.json`和`TEST_MATRIX.tsv`逐项列V合同K1-01至K1-08的输入、期望、失败负例及缺口，全为生产NOT_RUN/FAIL_CLOSED。尚未覆盖：partial instruction全引用注册/关闭跨E、grant/commit跨E、lower credit/inflight实际路由、inflight已erase但metadata未完、collection中E、WB拒绝、多SM同cycle相位、既存IO release依赖、真实store/atomic/bypass/proxy副作用与写后值。

已有结构回归通过不证明新失效时序；结构安全也不证明ISA允许旧消费者得到旧值。旧消费者与在途返回的K1安全均未证实，门禁保持关闭。未为了PASS修改生产代码；验证器开发阶段的编译/加载问题只在Lane Y脚本内修正，最终全套重新执行，失败开发收据留在本Lane外部目录。
