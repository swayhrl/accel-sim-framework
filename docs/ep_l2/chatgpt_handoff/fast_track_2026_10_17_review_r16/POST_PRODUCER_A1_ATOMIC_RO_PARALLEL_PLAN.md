# EP-L2 / ISCAS2027 — Review r16｜21/21正式生产构建后，按正确性依赖并行推进
2026-10-17（北京时间）。**仅协调续行与有限修复授权建议，不是新的性能资格、Ledger更新、后台任务或科学合同放宽。** 原R0/R1六组科学SUSPENDED保持、CURRENT_ACCEPTED pair=0；所有Lane的原分支/历史构建/失败日志不覆盖。本文件需用户转发给对应Codex原窗口才会形成执行；GitHub文档发布不会启动任何Goal。

## 0. 已发生事实，避免以旧截图指挥新状态
- Storage-Ops原旧174 `7aa1dec737a11524022531985ff3f71913e1ed9c`，目标 `54f9a591e031b1df6e4c7db12bb4ce4d1c8fdd48`：**仅**PolyBench correlation/covariance两条已授权closeout.stage源目录释放；旧174前后实测净+66,329,825,280B，目标报告+66,326,937,600B（跨阶段采样时点不同，不可混成同一次瞬时净值）。最后源盘可用约80.4GiB；164整档SHA/恢复指针、原tgz/其它科学资源均保留。Storage-Ops这一主任务**已关闭，不需唤醒/继续清理**，旧ROOT已不再是主要阻塞。
- Lane1最新**发布**Framework `9898c56d7a010c934de327784076ba0b9a36c9c4`，`FT20261017_LANE1_R0_1_PRODUCTION_RELEASE_r1`。准确 producing Core `088146f7f85b4073deb5d166a0a4484c7f3b48b2`、producing Framework `861a06b91e309832161eab0836b512853c833ffb`、vendor `f90c430c3a1ce8f08c09942a5a1c3a797bb2295b`，formal output binary SHA256 `e42432c7328e0ed17c1fbec6e823af5dc373e4abbc60ce335612da6953c77a4b`。生产CMake/5目标PASS、21/21 production directed PASS，中央lease已RELEASED；所有旧访问/host fixture失败构建保留。此**仅**`PRODUCER_TESTS_PASS_NOT_INDEPENDENTLY_QUALIFIED`，不是可跑五配对/获得论文性能/改写旧撤回结论的证据。
- Lane5最新Framework `acb45bf64d4642360ff1e0c99bdc22f6b06f4106`：原有十小时Goal仍**ACTIVE**、截止 2026-10-17 12:19:03 UTC（20:19北京），独立11gate尚未PASS；其r15 A1受影响方案已发布 `FT20261017_LANE5_R15_A1_QUALIFICATION_ADDENDUM_r1/A1_AFFECTED_GATE_PLAN.json`，明确需真正的16-way生产回归，不能把21/21当科学acceptance。此前Lane5 status在Lane1 9898新发布**之前**，下次应从准确git HEAD消费新发布，不以旧status推断没binary。
- 已发布协调r15 `8985f602a425d3049b77f68c6e90911dde2c4920`，真实**抽取代码**反例：共用FT跨周期pending victim与重新Tag probe发生不一致；RO两项Bank重试前进性反例。**缩小模型非真实生产验证**。源级公共FT重试/Tag probe主体从c948到本次producer088146没有改变，r15的A1风险仍相关。不得为了让fixture PASS而关断断言/增加不预算的port/buffer。
- Lane2 TVD Framework `c46f9d67049a4eeb56eff59656096b9f56b85e7d` Core `be5dcbe1fa5b9a501e81a77a6c399e6f6530e536`；Lane3 RO Framework `646e1b7dfead3f27fdf97ff60d3fe8bcd6a4b5f2` Core `3f3a8149b1ba18c1421a2a1a7f4073d76ad641f3`；Lane4 Ideal Framework `3a3950d974480477339f7cebc42027fe4810af65` Core `8ff56eb0804a027f1e253e629dd2915b02bc03b5`；Lane6 EN-v4 Framework `113eb6accb520db409b40193fba901089a723d20`。各短Goal已结束，TVD/RO最新增量C++未编译，Ideal18格NOT_RUN，不存在合法的跨机制科学PASS。

## 1. 优先级第一：Lane1仅负责公共主线r15-A1修复与最终producer

**P0：r15-A1跨周期Victim identity**。16-way同一Set，t周期唯一可替换dirty victim A被m_ft_pending持有，B16 phase0读到copy latch尚未commit；t+1别的RESERVED way因已有lower fill转VALID且LRU旧，新的native probe会选另一个way，造成pending.index与native实际选择不一致。必须保证preview+pending victim+真正Tag access共用同一事务身份；或者在任何native破坏前完整取消/rollback旧copy/WAD/staging/landing/granted bank token/generation并重新precheck。只改assert或仅覆盖index都不是修复。U_WB也须覆盖重试变更/预留；保持B/U同4bank、1line-size op/bank/physical-cycle、128B copy-latch、Tag1024、slot1168/1160、WAD128、D512。
- **先加真实、可失败的生产回归**：实际cache/tag/partition 16-way、其它way pending、被选择dirty victim、在phase0与retry间另一个way fill成为可替换；验证新source修复前确实触发老失败/错误身份，且修复后B8/B16/U_WB8/U_WB16均通过，结合lower-full、同bank、WAD set_done、sector data/version、exact-once、drain、无多grant。可先仅编译目标directed，不能拿抽取反例代替。
- 再最小语义修复，保留已经封版 `9898…`原源码/二进制/21PASS；在**新隔离source/build/output**内跑新特异门槛+原21项修复后生产定向、冻结全部hash与日志，publish可被Lane5独立回读的**新**正式release。没有Lane5 PASS之前只标producer，不开五对。
- 共享核心其它高风险原子sector问题见§2；如果Lane2在A1正确性修复期间已经交付小范围B1补丁，Lane1按明确源级可证/编译风险审查后可将其合并到这一轮**一次**新构建，避免连续多轮全量编译；但不能因为等B1而使A1无限等待。

## 2. Lane2平行：公共atomic/sector correctness（与TVD分支隔离）＋小统计/旁路修正

这三项是前一轮详细源码审查 `EP_L2_CODE_REVIEW_2026-10-17.md` 中 **B1/C1/C2**；其命名与r15的A1/A2/A3不同，不要混淆。**原附录实际缩小模型只提供反例，尚未跑正式生产。**

- **B1（可能是核心正确性）**：`gpu-cache.cc::mshr_table::add`将atomic记录为整个line的 `m_has_atomic`，`mark_ready`不筛实际完成descriptor/sector，`baseline_cache::fill`据此把恰好返回的普通read sector置MODIFIED。在128B line-key D512中同line sector0 atomic+sector1 ordinary read、sector1先返回时，可错误把sector1标dirty，进而扰乱dirty bytes/eviction/WB。Lane2在其**独立隔离补丁，不合入Lane1发布**，提交至少两种返回次序、多atomic与普通read/late response回归，使用真实MSHR/Tag路径证明问题及影响并提供最小修复建议。**同时核对atomic真正完成的version/byte mask**；Lane5既有ordinary data oracle不覆盖atomic。不能仅凭五个负载名字认为没有atomic。若确认相关负载全trace无atomic，需真实内容证明并注明限定范围，不等同于全模式无bug。
- **C1（统计可信度）**：`ep_l2_m0a_accum::sample_resident(occupied,1024)`的 `unsigned capacity-occupied`在U预留old resident+landing（occupancy可能1025+）时下溢；分离resident Tag可见数、暂时landing、整个physical pool，可做observer-only修补或严格禁止旧字段入纸面因果图，绝不默默改旧字段单位口径。提供最小负面模型和输出核验。C1不要强迫未使用的observer抢原A1科学验证资源。
- **C2（旁路兼容）**：memory_sub_partition texture-only/nontexture或L2-off直接对`m_L2_dram_queue->push()`未查full（fifopipeline assert）。只为旁路队列加合法backpressure/保持frontend head不pop；不得因修旁路给正常cache hit添加lowerq-full总闸门。注意Lane2 r14已有texture-only TVD eligibility/token补丁，不要覆盖。
- TVD本身的r14 source candidate/三组定向**仍NOT_COMPILED**；此窗口只输出`COMMON_DELTA_REVIEW_FOR_LANE1`及`TVD_R2_REBASE_NOT_RUN`，无需未获许可就合并RO/TVD或跑应用。若能在合法资源内进行非常轻量的isolated编译/短定向，必须真实记录，不能抢Lane1唯一大构建。

## 3. Lane3平行：RO仅对r15-A2/A3做隔离有界修复

- **r15-A2**：Bank retry按(role,id,write)匹配，但RO最后fill会把role转RESIDENT，遗留old RO-read grant无人消费。使retry有**稳定操作身份**（真实payload id+generation及操作/显式bank token），或等价的精确取消/迁移协议；不要清空整Bank pending/granted绕过公平。
- **r15-A3**：prepare Bank denial后重新按cursor扫描ready事务，可选到后ready的更低index，老选中授权请求再也没人重试。固定denied候选直到合法完成/取消，区分waiting-selected和granted-selected；同bank两个事务交错ready+ICNT full、跨周期及不同角色路径。
- 优先先写能在旧源码上失败的真实directed(或小的源绑定C++回归)，再最小源码修复；**只动Lane3隔离RO分支**。如需改公共arbiter ABI，请先给Lane1准确patch/风险报告，由Lane1决定公共引入及Lane5共同gate；RO-OFF R0.1不能被迫等RO A2/A3。不得以RO源码候选通过静态/缩小模型就宣称生产19项PASS。

## 4. Lane5：独立科学资格唯一owner，已有Goal不重启

- 原继续Goal仍ACTIVE，当前该Lane发布的r15 addendum是正确执行边界。读新Lane1 `9898` producer receipt可做独立来源/path/binary/21日志回读，但**r15-A1没有真实生产闭合时不准签正式11gate或开启新应用**。不要为此重复正式21、全量hash直到更正候选发布的临界事件；可以一次性准备受影响gate真正测试基准/标准和注册后的调度。
- 后续若Lane1发新正确修复binary，验证新source、binary、真正16way A1回归，11原gate、WB/atomic视所宣称scope、旧old-six withdrawal保留、当前V2权威、完整trace/config/content/64slices、中央运行quota。合法后**事先固定首个开发pair选择规则**，同binary B16 vs U_WB16，先一对CURRENT_ACCEPTED及时给Lane6；剩余四对。五对全齐才算geomean，sad作为事先冻结的negative control，不择优汇报。
- 不能把原`e424…` producer success自动升级为`INDEPENDENTLY_QUALIFIED`；B1原子问题若尚未修，要么真实定向修复独立验证，要么由Lane5根据完整input与科学声明明确裁定scope，不可默默忽略。无独立资格不启动应用。

## 5. Lane4 / Lane6 / Storage-Ops不做无意义持续等待

- Lane4 R1.1 Ideal两项C++新回归/18格暂不占共享重资源；只按准确新父版本准备不可重复合并的最小diff，等公共R0真正CURRENT_ACCEPTED后由Lane1决定是否开展R1.1独立集成。不要用旧1.721x或直接把R0.1 binary标成Ideal。
- Lane6 EN-v4审稿/PPA源级账已完成。当前最重要的审稿缺口一是**同预算强静态分割对照**（现WBUF8/16接口无法直接表达原拟1024/112/32，不可强制升到WBUF32而悄悄变1184 slots），二是可证明的copy/borrow因果证据。可在无模拟器情况下准备静态预算实现**可行性提案**，不擅改正式机制/添加矩阵；首个新CURRENT_ACCEPTED pair后才填真正数字和图，五对后geomean。PPA保留源估，未有RTL综合不可写面积/功率节省。
- Storage-Ops双原Goal已经结束、164归档/恢复位置已冻结、旧174约80.4GiB available；当前**无需重新唤醒迁移、不得进一步释放R1/M5/Git/source**。旧Source-Ops出具的真实`df`增量不是模拟器性能许可。
- 所有窗口按原共享资源/独占REGISTRY.lock/50GiB build gate/64GiB RAM／最多2长sim等工作；任何新编译需要真实合规lease，不设多个GateWaiter，也不因新进展直接kill旧DTC-L1/C16。

## 6. 关键触发，不在“工具PASS”上报科学成功

**最先实现**：在官方源码中真实复现r15-A1 → 最小修正 → 源码/真实定向PASS → 受影响及21套正式生产重跑并新publish → Lane5独立11gate＋实际A1/atomic eligibility → 第1个真实完整配对 → Fig2/3代表证据 → 完成五对 → 视发现决定R2(TVD/RO)与R1.1(Ideal)是否进入ISCAS正文。这几段是条件依赖，不是说所有实验必须串行：Lane2 B1+C1+C2和Lane3 A2/A3在自己的隔离源和轻量测试线上可**并行修复**；Lane6静态对照可行性同理。

**STOP边界**：任何源规范改变、bank或Tag budget放宽、跨分支合并新机制、无法证明原grant取消/rollback、独立gate科学FAIL、trace/controller替换等需保留完整证据并请用户裁决。小编译修复、fixture错误在准确原scope内可solve-and-continue。禁止以“论文赶稿”跳过独立科学资格。
