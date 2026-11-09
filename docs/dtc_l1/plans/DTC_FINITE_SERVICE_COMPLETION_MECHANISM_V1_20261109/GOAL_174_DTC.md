# Goal：DTC-L1 FINITE SERVICE AND COMPLETION MECHANISM V1
**执行端：174-DTC（唯一Main，本机API会话“DTC-L1交接-1”）。**

## 0. 执行授权及唯一来源
当前本目录是GitHub固定科学合同，**发布不构成模型启动授权**。只有用户将该固定提交与`MAIN_FORWARD_INSTRUCTION.md`明确转交174-DTC并要求执行，才授权本Goal的完整有条件范围。已转交后，不必在每个CPU小步骤或每个已预登记点重复请示；范围外的新机制、CH、11–32输入扩展、GPU捕获与恢复HOLD仍须用户另批。没有转交、资格不通过、或范围无法按本合同实现时，STOP并报告；不自行寻找其他执行入口。

本轮最大新科学模型：**10个固定输入×候选OFF/ON各1＝20个真实新格，CH＝0；不得超支，不能从旧Oracle/DH-P0借用OFF、request、UUID或预算。** 每次真实注册须有本Goal对应的合法新科学request与一次性UUID，旧registry/OWNER保持来源记录但不重启。新CPU fixture不算科学格；完整SASS runtime不可称CPU-only。

唯一Main负责技术选择、代码review、Gate裁决、资源准入与发布；多个Agent可在隔离目录并行做证据/源码/CPU/独审，**不得建立第二dispatcher**。旧账户Main只供历史查询；109-DTC-L1当前在做109历史资产接手，本Goal不干预、不要求它重采。true164提供归档，`SOURCE_KEEP`；不删原始科学资产。

## 1. 科学问题与必须检验的假设
完整GPU L1 DTC是Tag搜索、physical-line生命周期、PIB/Ref、有限下游与完成服务的共同结构。原IO/OO出自赵皓宇博士论文第4章；新贡献必须是当代模型中确有可实现的有限机制，不能重复包装原始重命名。

E1：已接受CORE32 Oracle 128格，M/L2/L1 GM≈1.676759/1.280649/1.939912，L2有11精确零和2回退；强反事实收益不能自动称硬件可兑现。E2：现有真实结构参数改动只有部分小收益和明显负例（MVT physical有益、BICG有害；V2 R1 fixed8≈0.78/0.84%）；MVT/BICG原有lower-create和global-credit满事件均为0，不可默认再扩队列。E3：优先判断正常有限**返回/就绪通知/collect/operand-WB的服务选择顺序**是否阻碍本可合法独立进展的事务；亦须与physical释放、下游排序及地址重用替代解释竞争。详见`SCIENTIFIC_BACKGROUND.md`。

**目标：** 从明确的普通DTC服务callsite筛选并仅冻结一个有限状态/调度机制，提交源码、CPU资格、可证伪预测和成本上界；Gate全部通过后真实跑最多20格，判断在预冻结发现集上的性能、机制曝光及负例。禁止仅修改文案或在原Oracle模式上调参冒充现实候选。

## 2. 固定基点与不能混合的版本
- Framework主线固定来源 `02775fd795cde5aae1480d81cee6eb481d0a08f4`；传统现有DH-P0基Core `9eedb3131937748f0492fa83aad37d3691118d70`。建议从该正常、有限DH Core隔离派生，不从带虚拟响应的Oracle路径作为实现机制。真实实施前固定实际合法Base、源码差异、build工具与选项。
- Oracle实现 `e6b41ab8992e7d41651501c4d34cfe24195c4f96`仅作E1证据和有限事件语义参考，**OFF/M/L2/L1全部不是本Goal的实际控制组**；新候选路径中不得触发Oracle虚拟服务或stock ideal开关。
- 固定平台：SM70/V100-derived 64SM、L2 10MiB、DRAM 850MHz，原Hash/512 logical Tags/640 nominal physical lines/active OO PIB128/Ref13及原有限service。保持实际强DH基线的可比配置、输入、初态、trace及ROI，非目标时钟/L2/CH/Tag/physical/PIB/downstream容量不改变。若某处基线源码/配置/identity出现实质差异，先独立说明并HOLD，不借旧结果自动证明新build公平。
- 每输入新build真实OFF vs 同一binary候选ON，非候选effective options必须逐项一致；若新增一个选项，完整echo计数由实际源定义计算（旧270＋1时为271），绝不省略新选项。现有CH-P0/F128/F256、DH历史P0等是强基线背景与资格交叉参照，不填新OFF，也不得称等面积。
- 固定科学源：已接受结果`7ffcca…`、最终包`b9ff89f…`、科学接受`64cd088…`、Headroom`18b1ee9…`、V2 R1`e218746…`、物理反例`320b136…`。具体路径见`SOURCE_INDEX.json`。

## 3. Gate A：先证据选型，冻结唯一候选（允许并行CPU静态审查）
Main分配相互独立的证据/源码/成本/反证Agent，在同一决策表审查：
A1. 固定source真实read-flow：lower-create/inject→return/sector→refill/notify→ready/collect→operand-WB/retire，记录涉及的生产source文件/行/入口、队列和互斥条件。不得用旧缓存观察器名字推断本轮active服务；不普查全raw。
A2. 在已关闭CORE32与phase证据中复用MVT K1、BICG K2、GESUMMV、ATAX等，旁证GEMM/3MM L2精确零、vectorAdd无原有效OO valid/pending、myocyte/srad kernel异号。只用有效单位与reset/累计语义；missing/null=UNKNOWN。为每个候选写支持、最强反证及来源。
A3. 首选候选族：**有限ready/collect/WB或返回仲裁的“多个同时合法对象之间的选择规则”**，不增加无限服务、免费端口、逻辑Tag/physical容量或全局消费者优先级。允许在源审查显示首选已等价实现、没有选择自由度时，改选同一有限完成/return域内另一个**明确不同的单一候选**，但必须在任何科学启动前一次性冻结并披露落选理由。
A4. 必须有至少一个source-backed、可执行CPU正fixture，能给出“同周期有两项及以上合法候选、固定基线选A、新规则选B”的明确见证，且新规则在相同真实quota、端口、队列和clock假设下合法。CPU单独正fixture不证明应用性能；真实性能中还需对应`eligible_choice_different`或同等精确定义的动态曝光。
A5. 写出设计不变量、是否增状态/搜索窗口/比较器，最大每周期候选数、各端口、流水级、饥饿上界、公平性、背压、缓存占用、clock/cost风险。不能把`quota=2`写成2个实际执行端口或“查找32项零时延”。如要求大范围组合比较，须给分段/流水化实现和延迟影响。
A6. 只冻结一个候选，连同其强基线、输入10和可证伪预测、旧证据链接写到`CANDIDATE_FREEZE.json`。筛选依据须先于新模型结果。若没有合法见证、可实现成本或与现有行为有可验证差别，给`NO_GO/UNRESOLVED_SPEC`，新科学启动0；不要为了跑20格而造候选。

## 4. Gate B：隔离实现、定向CPU资格与独立审查
在独立Core分支/worktree实现候选OFF/ON，保留原普通读路径、request identity与value/read semantics、精确sector mask/parent/physical generation、PIB/Ref、global credits、下游和所有非eligible路径。不要修改已冻结生产9eed、原Oracle e6b、其binary/RESULT或其他项目工作树。
- OFF禁用新增调度策略，但使用同一新binary和观测路径；ON只改变`CANDIDATE_FREEZE`声明的一个有限服务规则。若同时更改两处独立硬件行为，应在科学启动前缩减到单一改动；不得以组合收益声称单组件因果。
- 定向CPU检查至少覆盖：同时合法候选顺序选择、有限仲裁/每周期quota/反压、饥饿公平、队列满释放与竞争返回、32/64/128B及partial/unaligned sector、duplicate/stale response、parent/sector-mask/generation/Ref/credit exactly once、WB拒绝/完成后释放、store/atomic/fence/非eligible负控制、kernel-drain和终止。并行独立审核应包含故意破坏资格的负fixture。
- 对不影响的功能复用原受控结果和既有fixture资格，勿因换API窗口重复全量审查。局部CPU PASS不是完整科学模型PASS。
- 性能相关原路径有限服务不能为了改善周期被关掉；不得改变clock、memory scheduling、service port数或未预登记的其它参数。新probe必须真实执行且不会触发额外下游请求、改变OFF基线状态，要求独立telemetry-neutrality证据。
- 输出源码+编译器/构建/lib SHA与有效选项完整回显，独审明确通过的机制范围。出现潜在值语义破坏、liveness环路、unit mismatch、离散端口未建模或不闭合ref/credit，HOLD，不注册模型。
- 面积/时序先列状态位、比较器、队列、仲裁和额外stage的有限成本模型，给参数敏感性；无RTL/Liberty/SRAM依据时继续`PPA_UNKNOWN`，不拿名义80KiB或RSS作面积。若策略同样可用于CH，标注后续需要强CH匹配。

## 5. Gate C：20格真实性能科学矩阵（仅Gate A/B PASS后）
`INPUT_MATRIX10.json`固定10个全输入SHA、kernel/CTA总量及角色。它来自b9完整32结果索引，不允许用同名新capture、新规模、出色程序替代；新候选仅取**OFF/ON**二水平。

- C0：在新模型注册前预冻结一个强正动态曝光见证输入`W`（从GESUMMV/MVT/ATAX/BICG按源码/CPU证据选，不能用新模型性能结果选择），加`vectorAdd`负/背景控制。前4格＝`OFF(W), ON(W), OFF(vectorAdd), ON(vectorAdd)`；若W无法source/fixture资格，0格且HOLD。
- C1：对上述4格独立登记实际一次性新身份，在合法唯一owner下有限并行执行。必须自然完成、相同全输入/ROI/kernel与CTA/active instructions、same-build选项、真实ON正机制选择曝光（至少W一项`eligible_choice_different>0`或合法等义计数）、没有非法非eligible受益或生命周期违例、strict、true164全量归档与typed native恢复、独立gate review PASS。
- C2：C1通过后，才为另外8个固定输入×OFF/ON＝16格注册第二个精确科学request并执行。不同request、UUID全新且一次消费，不reset、不隐式延长原request。保护health与资源，按CPU/RSS/IO/归档及其他项目现状进行合理并行、短长混排；维护原始证据。合法性能退化、精确零、小收益不是停止一个合格候选的安全理由；不要以高收益筛选输入。
- 如果C1失败、0曝光、guard/身份/stop异常或机制违反安全，必须停止后续注册；如果只是暂时资源不足，保持STOP_NEW_ADMISSION并记录，不强杀健康任务。工程停止、before-PID、科学HOLD与合法回退按各自身份保留，无自动重试、退款、overwrite或补数。已消费身份绝不重派。

授权上限20格只在用户明确转交后生效，Gate不满足时真实启动0或小于20须如实报告。**CORE32其余22/44、任何CH、扩大预算、额外消融/多版本、复测一次已消费点，均不在本Goal中。**

## 6. 实测结果与科学验收
逐点交付实际OFF/ON整数总周期及per-kernel归属、精确加速`S=C_OFF/C_ON`、`H=1-C_ON/C_OFF`、exact正/零/负和missing，10格成功配对的同集合GM；如果不完整，只报告实际接受交集和缺失，不冒称完整10。报告已宣布的候选正曝光计数与候选选择变化、合法请求/sector/Ref/credit生灭、各stage服务结果及等待改变、单位/reset语义。速度变化只作为与机制相关联的E4新实测，仍不得从计数直接推唯一关键路径因果。
完整kernel序列及workload identity，pid/start/maps/env/cwd/argv, immutable Core/Framework/build/lib/config/options/payload、真实guard与source pins；strict、true164 chunk/index/COMMIT、SOURCE_KEEP和typed restore；独立D审校、逐格M分析及Main数值交叉核对。原生数值/capture/coherence/等面积/PPA仍待独立资格。
未来若评估实际价值，需在新合同下考虑传统CH的对应机制控制和匹配成本；本轮不将历史CH-P0相对数当candidate同build CH公平结果。
三类交付：`NO_GO`（Gate A反证，不实现或不启动）；`CPU_QUALIFIED_ONLY`（实施与CPU审阅闭合但科学门槛未过，模型0）；`DISCOVERY10_COMPLETED / PARTIAL`（按实际每格结果和缺失）。任何有效slowdown保留，不因性能不漂亮改筛选标准或扩大下游条件。

## 7. 环境、权限、冻结与停止
本机项目由174-DTC唯一写：`D:/Codex/Token-API/workspaces/DTC-L1/`，入口`CONTEXT.md`。真实执行主机路径必须通过现有合格owner/runbook自行确认，不猜路径、不从D盘路径推导174主机目录。隔离Git分支与新docs结果包，不动原科学registry历史、publisher、archived result、true164来源；原Source及历史负例`SOURCE_KEEP`。原Main旧账户只读历史；109-DTC-L1接手独立，非GPU权限移交。

用户未授权的新科学模拟/request/其他模型0。旧1024Tag/physical640`NO_FREE_LINE` 16格HOLD、跨组回收、modern SM89与原始native/capture资格不释放；英文v0.23、赵皓宇IO/OO归属、旧`F=null`不变。不得自启109 GPU/native/profile/capture或AI-ARCH/AWMA/EP任务。

## 8. Agent协调与交付包
Main可以安排四类并行小任务：A证据和phase反证；B源码/候选和成本；C独立CPU/负fixture审核；D科学登记、受控资源/归档及结果审计（只有Gate通过才启动D科学部分）。Main负责共享决定和唯一dispatcher，每个Agent的证据/时间/Source/negative可回读。

独立交付目录建议`docs/dtc_l1/review_packs/DTC_FINITE_SERVICE_COMPLETION_V1/`，新Git文档分支。至少发布：
- `REPORT.md`：E1/E2/E3/E4分层结论，NO_GO或正式结果与最强反证；
- `CANDIDATE_FREEZE.json`：候选语义/基线/状态位/配额/端口/预测/Gate A；
- `SOURCE_AND_BUILD_IDENTITY.json`：旧Source、派生Source和真实binary/Lib/config/option全SHA；`CPU_QUALIFICATION_AND_INDEPENDENT_REVIEW.md`：正负fixture/明确范围；
- `INPUT10_OFF_ON_RESULTS.csv`与`KERNEL_AND_MECHANISM_EVIDENCE.json`：仅已有实际启动和合法结果，未启动为空；
- `SCIENCE_GATE_RECEIPTS.json`、`MANIFEST.json`、`SOURCE_INDEX.json`和独立远端回读收据；若有实际模型，含strict/archive/native restore及身份链；
- `NEXT_DECISION.md`：是否继续独立22/44、CH、成本PPA、数值/capture，所需最小资格及新的精确预算建议；
- 实际更新本机`CONTEXT.md`，写固定本Goal提交、结果、负例、来源与未决项。跨会话不自动同步；109只以独立回执交Main，Main自行合并。

对CPU-only阶段可先发布独立冻结设计回执，但不要反复要求授权；Gate通过后可在当前用户转交的20格许可内接续。最终从GitHub固定结果提交回读，回复用户实际commit/身份/门槛/新运行数/科学结论，**STOP_AFTER_GOAL**。若Gate未过亦及时交付可复核的NO_GO和下一最小建议，不为流程而跑虚假模型。