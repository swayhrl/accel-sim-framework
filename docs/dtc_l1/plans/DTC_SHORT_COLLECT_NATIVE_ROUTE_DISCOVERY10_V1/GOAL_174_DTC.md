# 174-DTC新Goal：Short-Collect Native Admission & Discovery10 V1

## 0. 角色、执行与许可
接收者为唯一174-DTC Main（本机API会话“DTC-L1交接-1”），本机知识入口 `D:/Codex/Token-API/workspaces/DTC-L1/CONTEXT.md`。科学窗口负责固定证据审查，用户负责明确转交本新Goal及接回报告。此GitHub文件本身不触发执行。**用户转交本固定commit并要求执行，才授权这次完整但有门槛的任务**。前一Goal `32cbe...` 已在 `8dc2...` 以 `CPU_QUALIFIED_ONLY` 关闭；不得重开、reset、覆盖旧账本或将其20格未耗用上限当新额度。

本轮许可：在已冻结候选上补齐本Goal专属native执行链与独立CPU/科学审核；全部新准入R0合格后，先注册**GESUMMV、vectorAdd×OFF/ON=4个新科学格**；C1四格全部严格接受、归档恢复、独审且GESUMMV ON自然有效策略曝光>0后，再注册固定剩余8程序×OFF/ON=16格。**总新科学启动上限20；2个互不共享的一次性精确request，所有UUID新建，CH=0。** 一个未通过Gate的阶段不能借“流水化”跳过；合法性能回退/精确零不会阻止已合格机制按固定计划继续，但不接受替换输入、额外canary或重跑已消费身份。新Goal完成STOP。

禁止：第二结构候选、修改冻结策略语义/源、额外消融、CORE32剩余22输入/44格、CH新实验、原生GPU/NCU/新capture、Tag1024安全HOLD、SM89准入、数值或coherence自动晋升、英文v0.23修改；旧Main只读历史，109-DTC独立保全，不查询干预其工作。本项目与其他项目仅一个合法科学dispatcher；多个Agent仅从属Main在各自隔离目录做源码、工具、独审和结果分析。

## 1. 固定科学背景与候选
E1：Oracle CORE32固定trace 128格/96配对已在SM70/V100-derived64SM限定范围关闭，GM M/L2/L1分别约1.676759/1.280649/1.939912；L2的11精确零和myocyte+2/srad_v1+14652cycle回退保留。Oracle不证明短collect可实现加速、严格上界或等面积效果。E2：历史真实physical扩容改善MVT K1 4,076,476周期，却使BICG K2回退2,207,029；MVT/BICG lower-create queue/global credit满已打印0，不能盲扩容量或以request减少推关键路径。E3：短collect可能减少某些被older-ready大sector项占据的完成服务等待，竞争解释包括原有有限WB/retire、后续队列转移和不同地址/phase历史。只用真实ON事件和自然完整输入检验，不以旧平均等待宣称原因。

已冻结唯一候选 `PAPER_OO bounded short collect first`：当最早合法ready的ordinary cacheable load待collect>4 sector、ready age<8 cycles、未collect、没有sidecar/fence跨越时，优先允许窗口内一个<=4sector的合法年轻ready load使用**原有**collect配额4和WB/retire接口；OFF保持旧选择。四位置是第一个旧eligible之后附加的最多3个lookahead位置，原基线first-eligible/fence检查本身可能较长。所有Tag512、physical640、active PIB128、Ref13、finite create/inject/refill/collect/WB、L2 10MiB、DRAM850MHz及原时钟保留。严格限定硬件成本PPA_UNKNOWN，不把软件扫描当免费组合逻辑。

冻结源码和实物：
- normal baseline Core `9eedb3131937748f0492fa83aad37d3691118d70`，candidate Core `9a0de9b9f97144f481b3e3637e329ebab01acb74`，Framework `02775fd795cde5aae1480d81cee6eb481d0a08f4`。
- 现有冻结 `accel-sim.out` SHA256 `a9ec6f231d9491690eb913d1cb69d7d2dae0f769f8854efc4df0512b5f1fd00c`、私有`libcudart.so` SHA256 `43b3dc2f3e04d577e6c682f632691aca637b2670aee52c18b809f4d4c4e64860`，须验证真正LD_LIBRARY_PATH/ELF解析。CPU审查另编的lib不是这次科学库。
- 完整静态4格与binary/confighash来自 `8dc2.../evidence/FIRST4_GESUMMV_STATIC_ROUTE.json`、`FRONTEND_DRYRUN_MANIFEST.json`；旧270 effective options加单一short_collect位为271，OFF/ON非候选选项相同；Oracle虚拟开关全部关闭。10输入精确SHA在 `INPUT_AND_GATE.json`和原`32cbe...` INPUT_MATRIX10。只读复用原17/17 CPU资格，不重做17项或128格Oracle。

若实际模型需要改候选Core语义/冻结binary/配置源（不含合法新native adapter），不得用相同身份继续；STOP并报告必需的新Core/build合同，而非暗改源码或换old OFF。

## 2. 阶段R0：新科学native路由与独立资格，模型启动0
Main在独立本Goal执行根复用已合格native/registry/strict/true164原语，**不得直接复用历史Oracle exact owner/cohort/request/UUID/strict verdict**。已知 `oracle_native.py`、`oracle_ops.py`、`NATIVE_ROUTE_BLOCK.sh`绑定旧E2-DTCORACLE cohort/owner，必须设计新Goal专属接入层；`sweep_native_cap1m.py`的原子消费模式可作为结构参考，不能直接把旧namespace开启。

R0应完成且经过独立审查的具体工作：
1. 资格化完整新request/plan/4格spec schema与旧native registry的**append-only原子注册**，保留全部历史和外部项目身份、预算、状态。真实same-PID/different-FD flock与mutation callgraph测试必须覆盖EX锁中不递归shared reader、INTENT一次落盘、before-PID错误真实归档、重复调用不会二次消耗。**R0内部CPU演练只用临时隔离registry/fixture，不提前登记真实科学request。**
2. 新唯一合法dispatcher、parent lease、PID/start/maps/loader/ELF/strace、cwd/argv/env/limits/FD与可预防竞争的资源guard；采样local/fresh，不在持锁过程中依赖FUSE/164共享挂载，不降低历史cadence。保护其他任务；内存/CPU/IO/native空余或164接收空间不足即STOP_NEW_ADMISSION，不杀健康模型。不得因旧静态RUNNING/blocked改写历史registry。
3. 新binary/lib及完整271 effective options/source/input/命令/ROI/trace SHA贯通，OFF和ON同构，唯一新开关不同；旧Oracle OFF与DH-P0仅背景不填分母。loader必须绑定冻结私有lib，失败fail-closed。
4. **新机制专属strict adapter**：确认自然完整工作量与kernel序列/CTA/active-thread instructions、总/逐kernel周期、真实pid/loader/options与有效正常DTC request-sector/parent/generation/Ref/credit/PIB/ledger/fence/store/atomic/WB/retire/drain。ON要求退休后有效选择事件、OFF应0；保留`choice_decision_different`与`eligible_choice_different`的不同口径。缺失/null保持UNKNOWN；坏选项、错库、错误UUID、重复reply、未闭合drain、虚假exposure、意外非eligible改动的CPU负fixture必须被拒绝。
5. 用**CPU合成的小型闭合文件**而非隐藏真实模型完成归档/恢复工具资格：真实true164接收者与SOURCE_KEEP，chunk/whole SHA、index/COMMIT、native typed restore及损坏负例；不能以复制exit0或旧Oracle receipt代替。R0仅说明工具可用，科学真实raw仍需逐格归档恢复。
6. 独立审阅者与route实现者分离，核新strict及全身份链、预算、launcher/guard、资源及archive/restore、源冻结。给出机器可核的`R0_NATIVE_ROUTE_QUALIFIED`或`R0_HOLD`，R0失败/受限则本轮在**0真实注册/模型**结束；不得以空请求消费试运行。

R0可由工具/资格/独审Agent并行推进，Main统一审收与发布；不要求原源码/CPU候选重开发，也不调用完整simulator --help作为所谓免费canary。R0通过前不能发出任何正式实际模型身份。

## 3. 阶段C1/C2：真实性能只按硬Gate
**C1 4格**：R0全部通过且原生资源准入合法后，追加新的精确4格科学request和全新一次性UUID，仅 `GESUMMV_OFF, GESUMMV_ON, vectorAdd_OFF, vectorAdd_ON`；固定GESUMMV全输入SHA `769e6d9fd5f9cd5386556211112b1a1dec6d2b46bf69881db357257752aa22e4`、vectorAdd `e7bb67e63e3c38478ff50db4dcc25dee9262fe195b30589547b1ac5e2bc3d799`。程序范围/工作量必须来自已冻结完整CORE32，不得替换。动态资源调度可并行但仍是单owner；所有实际消费UUID保留原始status，before-PID和工程失败不造PID或有效cycles。

四格自然终态、严格语义/资源/版本、真实164逐成员/whole归档、SOURCE_KEEP、typed native restore与独立审阅全部PASS，且GESUMMV **ON自然`eligible_choice_different>0`**（成功真实writeback/retire-backed）才可进行C2。仅CPU fixture、config echo、decision counter、kernel未完成或未严格确认事件不能代替。若GESUMMV ON=0，则固定见证失败，C2 HOLD，不能把W换成MVT/ATAX/BICG；vectorAdd作为控制允许非零响应，不预设一定零。合法性能负加速/零加速仍保留、不会作为安全拒绝理由。

**C2 16格**：只有C1 Gate通过后注册另一个新的精确16格request，每程序独立OFF/ON：MVT、ATAX、BICG、scan、3MM、GEMM、myocyte、srad_v1。与首4同冻结Core/binary/lib及原非候选选项、初态、输入；不能根据首4结果重新调策略或逐程序替换。按CPU/RSS/native与true164实际约束混排、SOURCE_KEEP，所有合法slowdown/zero与工程失败都保留。历史已消费身份不重启、不退款；任何新预算超出20、重跑/改build必须新授权。

计算`S=C_OFF_this_newbuild/C_ON_this_newbuild`，用真实整数周期判exact正零负；完整10对都strict/归档/恢复accepted才报告10输入GM，否则只能报告实际接受交集并注明`PARTIAL_NOT_FULL10`。同时报告实际机制有效事件、阶段计数、单位/端点、逐kernel行为及反例，不能由统计相关自动推唯一critical path。历史CH和Oracle结果不得填候选OFF，也不能称面积/能耗/CH公平性已证明。

## 4. 交付与最终STOP
在独立执行/文档分支发布 `docs/dtc_l1/review_packs/DTC_SHORT_COLLECT_NATIVE_DISCOVERY10_V1/`，最少含：`REPORT.md`（R0、C1、C2终态及E1/E2/E3/E4区分）；`NATIVE_ROUTE_AND_GUARD.md`、`ROUTE_CPU_AND_INDEPENDENT_REVIEW.md`（真实原子行为/负fixture/资格）；`CANDIDATE_SOURCE_AND_BUILD_PINS.json`、`REQUEST_UUID_LEDGER.json`（只登记实际身份）、`C1_C2_RESULTS.csv`、`KERNEL_AND_MECHANISM.json`、`STRICT_ARCHIVE_RESTORE_RECEIPTS.json`、`SOURCE_INDEX.json`、`MANIFEST.json`，以及远端固定commit readback。
Main前向更新自己的`CONTEXT.md`：新Goal固定commit、实际gate、新native route新身份、科学结果的整数周期/负例、source/true164证明/未决项和STOP；不得假定109聊天与CONTEXT同步。原生应用数值、capture ELF/数据内容、跨kernel coherence、RTL/PPA、匹配CH以及CORE32剩余22输入均属未来独立资格。英文v0.23和IO/OO原赵皓宇博士第4章归属不动。

终态为`R0_HOLD_NO_SCIENCE`、`C1_COMPLETE_OR_HOLD`或`C2_COMPLETE_OR_PARTIAL`，真实消费与HOLD如实记录，完整报告固定GitHub commit后**STOP_PENDING_NEXT_USER_TASK**。