# Lane 4｜局部资源理想化与完整数据访存潜力

合同：EPL2_PARALLEL_POTENTIAL_20261017_V1。与同目录公共合同、矩阵和Lane5中央调度共同执行。本轮Ideal是首要并行科研线，不要求先得到WB-only明显加速，也不等待TVD/RO。

## 0. 已有资产、准确起点与责任

先读当前本地状态，保留原hrl/ep-l2-ft20261016-lane4-v1及所有历史候选、测试、未编译记录、撤回结果。Lane4最新已知Framework为3a3950d974480477339f7cebc42027fe4810af65，Core候选8ff56eb0804a027f1e253e629dd2915b02bc03b5。该R1.1候选不是当前官方runtime，原18应用格仍NOT_RUN；旧1.721x及已撤回R0/R1不恢复为科学结果。

新工作使用与Lane2和运行worktree隔离的Core树，从正式7b8e6ac70b8fe0f1bd37efca11acb5284938825d精确rebase所需模块，建议hrl/ep-l2-potential20261017-lane4-v1。保留正式A1 victim绑定、B1/sector修正、WB lower承载、physical-cycle/Tag-time分离。不能将8ff56的gpu-cache/l2cache整文件覆盖到7b8；R1.1两文件patch曾针对更老review base，不能假设可直接应用。

本Lane实现源、生产路径定向、reference/模式资格材料，向Lane1逐模块交付。完整应用全部由Lane5执行、登记、独立接受；不能原地启动旧18格、私建acceptance ledger或后台等待器。全新合同72 full-starts/50 seed cells/至多24小时（绝对期限见总合同）、总4长期sim/8CPU/32GiB，不是本Lane独立配额。原R19 D2/L25的已选分支、预算、deadline及活动进程保持不变；本Lane不重发其Goal。

## 1. 先复用四种现成诊断，定义不得漂移

所有诊断默认OFF，具有独立ideal vector与run-key，普通B16/U_WB16保持原始数据预算和服务。将原reference、source-map、测试及已修host-prefill同步作为可复用工程资产，不将旧候选的通过记录直接升级为新release资格。

### I_WB：仅解除Static WB数据容量

仅在Static finite-WBUF路径使用；必要时按需增加明确超出1168预算的WB-only backing，preview无分配、真正reserve时才增长。ID维持modulo-4 bank映射。保留WAD128及其到set_done的生命周期、同地址ordering、resident source read、staging write、staging-to-lower read三次实际bank工作、共同128B latch、原copy阶段、bank仲裁、下游队列/credit/scheduler/DRAM及真实lower accept。

不能把WAD一起无限化，不能去掉copy或提前释放数据。必须有WB-data-full=0、超过16个真实staged、WAD128仍可拒绝和完整数据/生命周期退尽证据。额外diagnostic存储计数显式报告，不冒充等预算实现。

### I_META：仅解除三类metadata容量

解除Line-MSHR count、全局descriptor count、per-address request cap容量拒绝；复用动态descriptor vector/ordinary address-indexed table，保持合法ID与生命周期，不能只写一个未经验证的巨大常数。

保留Tag/payload、sector mask与合并、lower read去重、普通RAW/WAR/atomic处理、真实fills/response退休、bank及下游。三类capacity-full必须为0才叫这些metadata非绑定；其它资源仍满应如实报告。历史histogram可能以旧configured cap封顶，不能把被截断峰值当unbounded证据。

### I_WM（I_WB_META）：两类容量联合

仅联合以上两种放宽，其它不变。名称I_WM和历史I_WB_META在manifest给出一对一映射，不生成两个重复run-key。必须实际测试两组资源同时越过原限制并恰好一次退尽；不能从两个单项小收益推断组合无收益。

### I_READ_HIT：L2 demand-read miss消除参考

复用明确的ReferenceMemory服务：符合条件的demand read，包括冷读，在原正常L2路径基础延迟后响应；当前本合同原条件保持ROP160，并以实际完整config dump核对。原bank/NoC/真实L2→ICNT response FIFO保留。older producer、WAD、相关MSHR依赖保持；write、atomic、L1/L2 write-allocate伪read走普通路径。

它不是完整epoch/line RO oracle机制，也不是只理想化只读区域；禁止称为RO性能结果。冷read从reference获取typed byte-address/producer-version符号或已知字节，不读取未初始化payload。已有resident hit可维护正常替换年龄，冷reference服务不能虚构Tag或丢弃dirty victim。它改变真实miss/替换/lower流，不能当EP-L2可实现speedup。

保留原host_prefill修正：只重置被成功host写入的selected sectors到明确未知version0，保留未覆盖字节、已有producer顺序时钟和先前response snapshots；dirty/pending非quiescent预填充按正确语义拒绝。原子仍在真实producer路径，不在两个入口执行两次；应用资格可以保持现已证明的non-atomic trace范围。

## 2. 新端点I_MEM_ALL_DATA：原SM上的数据访存无资源排队参考

语义名I_MEM_ALL_DATA；若实现接口使用I_MEM_NOSTALL，在manifest明确为同一模式，不重复排应用。

固定定义：完整SASS指令流、SM发射和计算资源、寄存器依赖、屏障及合法producer-consumer顺序保持。请求真实发起且必要先行producer已合法可见的eligible时刻之后，reference-ready必须在下一物理GPUcycle发生，即t_ready=t_eligible+1；不得把额外资源等待藏进eligible。该路径不保留有限memory admission、response/LDST FIFO、每拍返回配额或链路服务等待，也不因L1/L2/ICNT/DRAM容量或bank排队。

禁止同步回调、删除内存指令、直接清scoreboard、跳过store或推进假的physical cycle。完成事件必须按真实请求/指令协议消费snapshot、更新pending计数，并在实际寄存器写回和依赖完成后释放scoreboard。SM原有寄存器端口约束若保留，分别记录reference-ready与architectural consume，归属明确SM约束；不能把普通LDST/response FIFO等待包装成SM约束。真实producer依赖另行记账。

global/local data必须覆盖。shared、constant、texture要么纳入理想数据服务，要么从全trace及实际等待证明该样本不存在这些空间的remaining stall。没有覆盖/证明时输出PARTIAL_GLOBAL_LOCAL_REFERENCE，不得宣称已满足ALL或填入完整端点格。取指路径单列，保持原配置；若另用perfect instruction cache，必须单独条件，不能混成只理想化数据访存。

可选择有界、改动最少且可证正确的实现：

1. 在生产事务/lifecycle上理想化服务与容量，每次真实数据状态变化和完成仍经过明确钩子；或者
2. 在LDST之后建立独立有序reference服务，使用既定访问地址/byte mask/sector/producer版本，发出受控真实完成事件。模式从quiescent起点启用，不再创建普通cache dirty状态；每个原始store提交reference恰好一次。进入前已有dirty/WB必须正常drain或明确拒绝启动，不能直接discard。若该路径仍产生WB，必须完成其数据提交与恰好一次退休。

第二种端点改变物理cache/WB轨迹是明确的诊断选择，不能把未经过的物理WB路径填成“0成本/0能耗”或声称已通过该路径。物理L2/64-slice WB字段在此模式可标NOT_APPLICABLE并说明原因，不能要求新reference满足不存在的传统WB路径事件数，也不能用N/A绕过原始store/reference/完成检查。

原-gpgpu_perfect_mem仅把请求回送cluster response FIFO，仍可能受L1、FIFO和LDST消费限制，并无本reference完整语义；不得直接贴ALL标签。当前-l2_ideal只凭名称也不合格。可以复用相关接口骨架，但新增正确性、延迟和scope必须真实闭合。

### 必需独立资格

- 全trace/kernel/warp/instruction身份及原始load/store/空间覆盖不变；任何访问删减、截断或unsupported opcode fail-closed，不悄悄排除。
- 地址/byte mask、partial-store、RAW、WAR、同地址多producer、跨warp合法排序、barrier及response snapshot保持；已知字节定向与dataless SASS符号作用域分别描述。
- 每原始store一次reference commit，每请求一次完成；未知冷值为typed symbol，不伪造数值；无旧dirty/WB丢失。
- 实际reference-ready严格满足t_ready=t_eligible+1；eligible只受真实指令发起与必要producer依赖约束。记录remaining dependency、SM issue/register consume、memory resource wait及各space覆盖。若仍有未解除的memory排队、返回配额或多余服务周期，先修复或明确PARTIAL，不能宣布满足ALL。
- request/store/reference/snapshot/ownership全部drain；reference持有的完成事件不可因普通应用“结束”而遗留。
- 新模式单独scope/feature vector/qualification，沿用Lane5 native trace identity及科学接收框架，按实际路径选择检查，不伪造普通64-slice WB证书。

## 3. I_BANK和I_L2_SERVICE：按证据追加的组合准备

准备I_BANK为明确无限/非绑定的L2 bank服务诊断，区别于Lane2有限P2。逻辑bank读写仍逐操作执行和记账，数据不丢、请求不重复完成；只去掉相应仲裁等待，原基础延迟不被一并设0。

I_L2_SERVICE建议组合I_READ_HIT、WB数据容量、metadata容量及bank非绑定，保留原L1/SM/ICNT/ROP160和真实response消费。它回答“当前上游条件下L2服务还剩多少潜力”，不等于I_MEM_ALL_DATA。

当前8ff56代码明确禁止I_READ_HIT与I_WB/I_META/U_WB组合。若实施联合模式，应新增显式组合语义与生产定向；不能删除guard便称支持。特别检查read reference与普通write/WB并存、old producer依赖、partial byte状态、同周期多bank grant、response背压、host-prefill及epoch drain。某组合尚未资格时保持拒绝，其它已ready模式继续交付。

这些模式不是首批全cross-product：I_READ_HIT与I_MEM_ALL_DATA差距较大时优先用I_L2_SERVICE解释残余；WB+META单项弱但联合强时再与有证据的系统条件做有限组合。追加点由中央矩阵和剩余budget登记，不由本Lane私开。

## 4. 准确应用矩阵：由Lane5运行24格

原18格为四个负载分别B16/I_WB/I_META/I_READ_HIT，共16格，再Convolution/FWT各I_WM，共2格。新22格加四个I_MEM_ALL_DATA；再加CFD的B16与I_MEM_ALL_DATA两个端点，合计24格。

| 条件 | convolutionSeparable | FWT_7_21 | vectorAdd_4M | sad | cfd_097k |
|---|---|---|---|---|---|
| B16 OFF锚点 | 是 | 是 | 是 | 是 | 是 |
| I_WB | 是 | 是 | 是 | 是 | — |
| I_META | 是 | 是 | 是 | 是 | — |
| I_WM | 是 | 是 | — | — | — |
| I_READ_HIT | 是 | 是 | 是 | 是 | — |
| I_MEM_ALL_DATA | 是 | 是 | 是 | 是 | 是 |

这是科学条件表，不许可忽略实际full-start计数或重复跑相同键。已有B16锚点只有满足新release/source/config及关闭等价的正式复用规则才可复用；不能自行将旧binary B16当新reference同binary结果。全部应用只交Lane5排队，保留独立application/trace/run-key/terminal及当前接受记录。

优先滚动生产：I_WB、I_META或其组合任何一个先ready就交Lane1发布/请求Lane5资格，不等I_MEM_ALL_DATA、完整TVD/RO或所有新模块一起build。I_MEM_ALL_DATA也可在其独立scope先闭合时优先交付端点。多个release的锚点复用由Lane1/5按受影响范围决定，不能靠将版本标签改相同避免必要验证。

## 5. 正、零、负结果均要可解释

每点必须给出cycles、instructions、真实执行范围、reference/ordinary路径请求和store完成、被解除资源exact need/block/峰值、剩余资源/依赖等待、数据/生命周期退尽。历史cap截断或新路径不存在的统计标明范围，不填0。

至少比较C0、C_WB、C_META、C_WM；不能从两个单项小收益推断组合也小。I_READ_HIT显著而WB/META弱，支持转向读miss/复用潜力；I_L2_SERVICE弱而I_MEM_ALL_DATA强，支持调查L1/ICNT/LDST/固定延迟；I_MEM_ALL_DATA也弱才支持这些样本的总数据访存余量有限。诊断因交错改变而变慢也必须保留，核对后解释，不夹到1、不挑有利条件。

普通EP-L2实效始终是同系统条件B/U之比。C_B(H0)/C_ideal只是资源或系统乐观参考，不能称EP-L2 speedup，也不能用它替代H0五组或已有R19正负结果。全memory参考不声称是所有调度下严格数学上界。

## 6. 滚动交付与结束

每模块给准确base/source/changed blobs、最小patch、CLI与模式合法性表、reference与生产路径source map、compiler/test/binary证据、OFF等价范围、新scope检查、未完成项和预计应用矩阵输入。Lane1逐模块集成、Lane5独立资格与运行；本Lane不改科学ledger、不启动完整应用、不建立等待后台。

普通工程故障自行修复继续。不能为过关删除ordering/ownership/clock断言、丢请求、取消依赖或冒充路径覆盖。遇到不可解释数据丢失、范围外语义变化、资源不足，只停止受影响模块，继续交付其它ready诊断；不因性能小而结束科学工作。

## 固定源码与历史模块参考

- https://github.com/swayhrl/accel-sim-framework/blob/3a3950d974480477339f7cebc42027fe4810af65/docs/ep_l2/codex_handoff/fast_track_2026_10_16_v1/lane4/STATUS.md
- https://github.com/swayhrl/accel-sim-framework/blob/3a3950d974480477339f7cebc42027fe4810af65/docs/ep_l2/review_packs/FT20261016_LANE4_IDEAL_DIAGNOSTICS_r2/IDEAL_MODE_SOURCE_MAP.md
- https://github.com/swayhrl/gpgpu-sim/blob/8ff56eb0804a027f1e253e629dd2915b02bc03b5/src/gpgpu-sim/ep-l2-ideal-reference.h
- https://github.com/swayhrl/gpgpu-sim/blob/8ff56eb0804a027f1e253e629dd2915b02bc03b5/src/gpgpu-sim/l2cache.cc
- https://github.com/swayhrl/gpgpu-sim/blob/7b8e6ac70b8fe0f1bd37efca11acb5284938825d/src/gpgpu-sim/shader.h
- https://github.com/swayhrl/gpgpu-sim/blob/7b8e6ac70b8fe0f1bd37efca11acb5284938825d/src/gpgpu-sim/shader.cc
