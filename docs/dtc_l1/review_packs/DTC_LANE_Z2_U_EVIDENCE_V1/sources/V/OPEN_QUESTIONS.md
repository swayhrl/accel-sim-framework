# 未闭合问题与 STOP 等级

本审计任务可完成交付；下述 STOP 限制科学主张或后续实现资格，不是要求重新启动A/T/U或运行完整模拟器。`PROVEN_SOURCE`只表示固定源码存在这条行为，`UNPROVEN`表示证据不足，`ABSENT_SOURCE_HOOK`表示已核路径没有相应调用；后两者都不能包装成数值正确性 PASS。

|ID / 等级|可验证缺口|最小补证与审查落点|
|---|---|---|
|V01 STOP-K1-CURRENT|冻结LDST invalidate/flush仅ordinary，没有DTC hook/API|实现Lane X提交独立source delta与K1-01/02/08，明确请求线性化、source选择范围；本包不是实施授权|
|V02 STOP-WRITE-VISIBILITY|ordinary store/atomic/bypass不会自动更新或撤销独立DTC Tag；sidecar也无地址引用|同址 L→S/ATOM→L、partial-byte、pending-return-over-write、cacheable/bypass混用事件/期望值；若要加write coherence属K1之外新合同|
|V03 STOP-IO-IMPLEMENTATION|IO无Ref，source invalidate无victim替换者，无法直接复用release_on_retire保证最后owner|明确IO orphan/live-owner机制、idle retained释放、partial/FIFO与重复事件证明；否则IO_K1_UNIMPLEMENTED_STOP|
|V04 STOP-ALL-ISA-CLAIM|源码/header tests和trace terminal没有architectural load读值oracle|绑定真实可执行memory litmus、数据payload、expected values及ISA scope/ordering依据；没有这些保持VALUE_CORRECTNESS_UNPROVEN|
|V05 STOP-ORDERING-CLAIM|PROXY_FENCE仅async source path与same-warp younger-retire过滤，无普通全局memory coherence|分开普通MEMBAR、proxy、regular FENCE；给可到达opcode/作用域及happens-before测试。regular LDST fence会assert，不宣称全面支持|
|V06 STOP-KERNEL-GUARANTEE|实际kernel-done与source idle-cluster invalidate不等价；并发kernel或其它SM未完成会改变事件集合|逐SM/cluster/kernel ID事件记录、开关与并发条件；只允许写“源条件触发时”，不能写“所有kernel边界均已失效”|
|V07 STOP-TIMING-QUALIFICATION|K1目录撤销带宽、同cycle lookup/response/retire顺序、ordinary pending与DTC失效时间差尚未定义到实现|K1-03/04/05/08；列服务宽度/latency/仲裁/可重演phase。不能把一键遍历的软件循环称成真实单周期硬件|
|V08 STOP-PPA-PROMOTION|metadata/端口/Ref/waiter/orphan成本及真实宏/RTL/STA未闭合|延续既有硬件审查边界；K1的source/timing证据不得替代PPA或同频证明|
|V09 CONDITION-RETEST|禁用L1D与invalidate空指针路径、perfect memory/SST、local writeback、现代sector/async/TMA组合|逐组合源码准入和定向验证；不把默认global load通过外推到全部组合|
|V10 EVIDENCE-BOUNDARY|A/T/U发布包未提供K1测试；U最终external final receipt不在Git自引用链中|本包只核已提交报告/内容回读和远端对象；不读取或接管其它Lane raw、终态工具与锁，不把内容回执冒充独立重验全部最终结果|

## 明确支持域

1. **本次有证据的对象**：上述Core下PAPER_IO/PAPER_OO的128B映射/physical生命周期、非legacy M4 sidecar、普通L1与DTC响应所有权分派；whole-line IO/OO finite metadata/retire机制有源代码和小型header测试。A/T/U公开证据可支持其已声明decoded trace timing/accounting范围，不提升到load值正确性。
2. **只作source识别的扩展**：MODERN_OO_SECTOR有sector identity/waiter实现及既有header测试，未做完整K1失效审查/实施；现代容量/端口资格保留原HOLD。proxy enum支持范围与冻结trace可达范围分别报告。shared、texture、constant不自动纳入DTC cacheable domain。
3. **必须另测**：普通写后同址load、atomic返回与写效果、部分byte/sector写、store ACK晚于sidecar退休、跨SM/warp/CTA、并发kernel、跨kernel地址复用、HOST memcpy/DMA与GPU共享、release/acquire/不同scope、cache config变化、L1关闭、perfect/SST、sector/TMA/LDGSTS混用。这里是缺口清单，没有启动权，也没有未经证明的ISA保证。

## 给 X / Y / W / AA 的同一审查基准

* **Lane X**：按K1-01至08逐项提交。核心判据是source-selected事件撤销地址查找、旧physical/generation生命周期保留、最后owner回收。一个reset/clear-all补丁不能通过；IO扩展须单列证明。
* **Lane Y / Lane W / Lane AA**：本用户未给出三者更具体分工，因此不代分配写目录或实现责任。审任何候选时使用同一个五状态矩阵，分别标结构、时间、load值结论；未测项保持UNPROVEN。所有Lane均不得用PROXY_FENCE/terminal balance补数值可见性证据，也不得把Tag覆盖变化推成数据容量/area公平。
* 实现改动若改变源事件集合、数据一致性、有限服务时序或输入/build身份，须重新列差异与影响范围；本包不预先批准新全ISA协议、不替换冻结Core，不重新标记原A/T/U历史结果。

## 小型检查的边界

[CPU_CHECKS.json](CPU_CHECKS.json)中的PASS是五个小型程序与源码断言的结果：既有common、finite、completion、bad-generation，外加本包sidecar保留映射见证。completion的重复关闭负测与bad-generation父进程PASS均要求其子进程按预期SIGABRT；stderr作为负测证据保留，禁止core dump。临时目录名归一化以便复核。

本次没有实现或测试新的invalidate功能。`visibility_witness.cc`只调用生产frontend sidecar API，证明其不会撤销映射；不声称模拟了一次真实store/atomic写payload。静态调用链审查才把它与实际分类/完成位置对应。头文件没有数据payload，因此新旧值相等或不等都没有被测量。
