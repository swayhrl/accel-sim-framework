# EP-L2 — R2 RTL源码审查与R3元数据结构降本Goal

审查日期：2026-10-18。**源代码审查结论：R2的52.2%是本次部分标准单元切口真实相对面积，不是合理硬件组织的不可压缩下界，也不是完整L2的面积增幅。** 当前最值得优化的是每payload slot重复的metadata算术/读写译码与状态组织，而非再次单纯优化ABC/时钟缓冲或修改约束。

## 0. 本Goal的精确输入与不能改变的事实

- R2用户报告与可核源码：Framework原Lane2远端commit `1b011c6a51900462db9ae169d33bca742999abdb`；五文件RTL硬件commit `f54d3c054a6a03c85b40a1c5018751958c78a129`；审查包 `docs/ep_l2/review_packs/RTL_COST_TIMING_REFINEMENT_R2_r1/`。
- 性能模拟器有限WB协议规格：Core `9bd30ed913c5058b5d952fbeb2e67cb5e4644b3f`、Framework `8ab6013ea90755fdc74819e92090c2de50f4f199`、binary `fb67448d08818bc8cbe72961580e8340f0e6f337a4df95e7c8ee9468472953f7`。R3不能因源码/RTL修改而继承任何新SIM性能数字；旧H0和Lane5 CURRENT_ACCEPTED保持冻结。
- 精确固定硬件：`N_TAG=1024`, `N_PAYLOAD=1168`, `N_WAD=128`, `GEN_W=32`, 四个bank各292条×1024bits payload、每bank每物理GPU cycle最多1次真实grant（P1）。B16=1024/128/16，S64=1024/80/64，U为物理pool角色复用。现有RTL`req_ready/native_commit/lower_accept/set_done`、请求ID、byte masks、sector readiness、pin/参考数、重试回滚、bank兼容、generation/饱和策略不得隐式删改。
- R2三模式使用相同Nangate typical1.1V/25C Liberty、SDC、fast-clean effort：B16控制/访问面积**1,598,557.058**，S64 **1,627,498.656**，Unified **2,432,606.442**。B16/S64/Unified WNS@0.883392226ns为**-1.413025/-1.400875/-1.700971 ns**；@2ns为**-0.296418/-0.284268/-0.584364 ns**。三模式均未闭合时序。R2 `UNIFIED/B16=1.5217514`，但**仅限SRAM/传统Tag/MSHR之外的实际映射标准单元切口**。
- `PER_MODULE_AREA.csv`精确分解Unified−B16的面积**834,049.384**：metadata word汇总 **691,123.328（82.8636%）**；1024×11-bit dynamic Tag-map **84,439.040（10.1240%）**；top `ep_l2_slice_ctrl` **55,651.988（6.6725%）**；其余 **2,835.028（0.3399%）**。Unified 1168个metadata word，单word area1166.144（seq284.886+comb881.258），合计1,362,056.192。B16的1024 resident words+16 WB-only words合计670,932.864。**这是诊断目标，不是待删的全部有用硬件**。
- 参考源位置：
  - `rtl/ep_l2/rtl/ep_l2_metadata_word.sv` 第23–65行：逐槽GEN32前缀递增及pin、role、sector/owner并行赋值；
  - `rtl/ep_l2/rtl/ep_l2_slice_ctrl.sv` 第73–105/385–404/455–502行：全池metadata表、约19路选读MUX、逐槽写使能及Tag-map；第146–180行：WAD/四bank合法free搜索；第189–285行：同沿准入/三client P1 bank/WAD完成；第286–380行：写回与控制更新。
  - `rtl/ep_l2/r2/SYNTHESIS_ACCOUNTING_R2.md`、`STRUCTURAL_PROOF.md`、`SIM_RTL_TIMING_DELTA.md`、`COVERAGE_R2.md`保留先前局部证明与明确缺口。
- 当前SIM/RTL仍有read II4/write II3、copy阶段、返回延迟、仲裁和native approval差异。**优化RTL不等于匹配当前应用加速**。没有匹配实际SRAM宏，SRAM成本/延迟为UNKNOWN；原生Tag/LRU/MSHR/NoC/队列成本UNKNOWN。不能把未闭合的WNS和52.2%说成目标产品PPA。

## 1. 科学审查识别的四种真实架构优化机会（按优先级）

### P0：逐slot重复的32位算术和状态更新

在R2中，每个有效slot的`ep_l2_metadata_word`含一个GEN32 add1/add2前缀网络、重复更新优先逻辑，尽管本周期更新的slot远少于总1168。**优先尝试以事务事件为中心的共享GEN/metadata更新引擎，按真实并发写端口与bank物理服务分类，而不是为每个slot保留独立的加法器**。例如按事件类别或bank构造少量共用GEN加法器和分发写数据，把已注册的每槽generation保留在明确计费的存储中。前提是严格统计和证明：`req_fire` reservation、`native_commit` install、`lower_accept` release、`abort_fire` rollback、`fill_fire`、pin/response、`done_fire`在同一物理cycle可怎样**同时发生、落在同槽或不同槽**。不可假定一次只能修改一个slot，亦不能用新增串行化暗中替代现有并发；不能丢失操作优先级或GEN+1/+2规则。受条件约束的共享加法运算若组合critical path恶化，应如实记录。

### P1：Tag-驻留状态、payload所有权状态和WAD状态合理分层

R2每个动态payload槽存`role[2:0]`、`generation[31:0]`、`owner_tag[9:0]`、`pins[5:0]`、三组4位sector状态；但驻留tag总数最多1024，且dirty victim只在`pins=0`和`pending_sector=0`时可被转为WB。检查能否把**resident-only pins/ready/pending/dirty**按tag-index保存（仍实际计费），让payload-slot只保留被WB/重用真正需要的state；WB-only数据及地址债务应归WAD。这个方向可能减少角色变换时的重复全槽读写和动态状态，但**不能简单把迁移的位交给外部Tag/MSHR并声称免费**。如果移动到本研究控制切口外，必须提供对所有三模式一致的新增/共用物理存储面积、读写端口与时序账。

特别核查`owner_tag_fill_pid`：当前实际用途是`fill_identity`校验。已有`tag_live`、Tag→PID映射、payload generation/role。可以独立尝试使用`tag_live[fill_tag] && tag_map[fill_tag]==fill_pid`与现有gen/role/sector guards替代逐payload反向owner字段，但必须证明**多次slot复用、late fill、持有的response pin、Tag rebind、stale generation、同bank并发和同沿pin/admission**全不出现额外可接受或错误拒绝；若导致多一个读端口或增加路径，应明确计费/报告。owner冗余论证未通过则原字段保留。

### P2：压缩无用多读口逻辑，按bank局部读

`ep_l2_slice_ctrl.sv`目前实例化多个`ep_l2_index_mux`，实际多次从1168槽的role/gen/pins/sector读出；把真正需要同cycle独立访问的端口分类，基于四bank与使用时机共享可证明互斥的选读网络，保持所有并行fill/frontend/WB与pin/done处理能力。对部分全池可写metadata使用分bank寄存器文件或受限端口SRAM是另一条候选，但若缺匹配实物宏Liberty，先交**精确端口/宽度/时序预算及标准单元独立计费的实现**，不生成‘SRAM宏免费’的漂亮面积。不能假设常规1RW RAM满足多并发metadata事件。

### P3：generation宽度与reset网络只作为有证明的后续优化

GEN32每slot×1168成本可观，但暂不授权直接缩位、更改生命周期或假定wrap永不发生。只有提出严格的最大在途寿命/最坏分配频率/唯一身份/耗尽处理证明，并且通过受控缩位/溢出测试，才能提供另一组**单独标注为新硬件合同的**结果；主表仍以GEN32为基准。reset同步分发、动态owner与所有真实cell必须计费；不可用false path/multicycle或未计费clock/reset树人为改善WNS。

## 2. 新Codex Goal：EPL2_RTL_R3_METADATA_AND_COST_OPT

**Owner:** 原Lane2 Codex窗口，新独立RTL工作树+分支；原R1/R2工作树、候选、所有raw/归档一律只读保留。原R2 Goal已完成，不重启它。用户已经明确授权继续RTL实现优化；本文件发布本身不等于远端Goal已经启动。

1. **T0审计（立即，≤45min）。** 在原Lane2获取最新GitHub状态、冻结上述两版文件身份、读完整 `ep_l2_slice_ctrl.sv` 和 `ep_l2_metadata_word.sv`，从R2 `PER_MODULE_AREA`归因每段实际面积/端口并列出**最少两种**结构重写（prefer P0和P1）。检查当周期可能并发的写/读集合，形成`R3_PORT_AND_STATE_CONTRACT.md`；记录GEN/owner/mask何者是不可复制、不可移走或可由其它状态严格推出。无需从头再跑R1、R2长任务。
2. **R3A可逐周期等价优化（首个2小时检查点）。** 独立实现P0/P2中最可能的共享GEN更新/真实局部读写路径；在不增加寄存器流水/服务latency/改变最低free选择/对外顺序的前提下，与R2做少量有界逐周期对照。为B16/S64/Unified应用**相同适用的优化**，已证明固定不变量允许静态模式单独硬连线；不允许人为劣化基线以缩小相对比例。
3. **R3B结构性候选（在R3A后并行准备）。** 尝试P1中移除反向owner或Tag-index resident metadata重排；先提交不变量和明确读写接口/状态账，再实现。若无法在既有接口保持实际同cycle吞吐，分为**新时序微架构候选**，不混入R3A所谓等价优化面积主表，不用现有SIM收益匹配该数字。若非等价/无法证明，明确STOP本候选，不为赶deadline牺牲正确性。
4. **验证门槛（每个可发布版本）。** 全1024/1168/128、GEN32、4×292/P1；复用R2已有效的功能套件+Lane3十组真RTL numeric-byte reference、bank3最后槽、真实WB lower_accept vs WAD done、old-red/new-green pin race、WAD129、最少两个互相独立并发GEN更新、同地址hazard、same-slot同时事件优先级、GEN3耗尽、stale/late fill、abort+rollback与保持victim、全部资源drain。新增**并发读写端口组合穷举小规模miter/SAT**，明示环境前提；不得把参考代码自检称RTL数值验证。R2已知SIM/RTL时序差异和未覆盖动态late rollback、unbounded generation等继续保留。
5. **真实PPA门槛。** 至少三模式在同一当前Nangate Liberty/SDC/GEN32/容量/ABC effort下取得Yosys+OpenSTA实际完整映射和路径；同时报**绝对切口面积**、`U−B`、`U/S64`、metadata/Tag-map/top面积与seq/comb cells、0.883392226ns/2ns WNS/TNS；标注所有reset/DRC和SRAM/Tag/MSHR边界。对任一共享逻辑引入的分配/读写服务端口与延迟必须真实计费。将`R2->R3` Pareto变化按逻辑机制分类。目标是实质降低动态控制溢价，而非只降低一个WNS；不设“必须<20%”之类可诱发造假的硬通过线。失败或变慢同样交付。
6. **实物宏可行性（轻量）。** 可加一个隔离的banked-metadata SRAM interface探索，但不凭空生成不计时/不计面积宏。需要真实可用macro .lib时才做定量SRAM加总；否则仅报告端口需求、已计费logic与未定量memory成本，独立于可信主表。
7. **DC入口和性能边界。** 更新最佳**实际合格RTL**的filelist/SDC/`run_dc.tcl`或脚本，保持实际库配置接口、PVT和单位；旧R2 DC入口不动。DC未运行则写UNRUN。任何改动II、SRAM读延迟、copy阶段/return/仲裁/native-approval协议都必须在`R3_SIM_RTL_DELTA.md`显式标注并只提交Lane1审查建议；无授权不改官方SIM/不启动Lane5应用。
8. **时间/资源/发布。** 优先2小时内推送首个可验证的`ROOT_CAUSE_AND_R3A_CHECKPOINT`，完整R3工程探索最多**6小时**；普通工程问题solve-and-continue，但首次遇到科学contract或必要时序变化先隔离为候选。到边界即发布实测最优、未闭合/失败源因和DC-ready文件，不无限延期。遵守中央真实workspace、当前有效的aggregate result限额、Lane2更严格的own限额及workspace48GiB/Share40GiB/availableRAM64GiB、CPU/RAM lease；其他DTC/AWMA/C16/Lane5进程不可触碰。所有计费EDA文件在真实workspace，lossless归档须有原始SHA且不改变接受数据。按原Lane2分支发review pack，独立R3 RTL分支推源；non-force push并远端逐字回读源码、表和receipts。

## 3. 投稿稿件的结果门槛

- 当前R2成本只能写作“被真实映射的未闭合控制/访问RTL原型，面积比1.522×”；不推成全L2面积/能耗/目标频率。
- 若R3A保持逐cycle等价且面积改善，可进入论文“implementation feasibility”或成本小表；若R3B更优但增加stage/降低II，必须有独立性能反馈或单列设计空间，不与旧H0或Unified/S64的模拟加速拼净收益。
- 优先给作者完成DC的是真实合格的最佳结构RTL，不一定是WNS最不负的版本；应选择功能完整、界面定义清楚、库与端口成本透明的一版。强静态、动态容量和成本结论均需保留负结果。
