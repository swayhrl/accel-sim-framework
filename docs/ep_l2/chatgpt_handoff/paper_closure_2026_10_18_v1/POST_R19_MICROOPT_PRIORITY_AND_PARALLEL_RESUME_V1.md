# EP-L2 — R19完成后的有限实验与投稿收敛：优先级及续行合同 V1

记录日期：2026-10-18（Asia/Shanghai）。本文件只是**向现有Codex窗口交付的建议增量合同**，不创建活动Goal/运行器/lease，也不扩大任何源端或运行预算。运行必须由用户把精确指令发给对应窗口。避免把已经完成的R19重新启动。

## A. 已核实不可混淆的四份状态

1. **R19 = 完成**。Lane5 commit `00312b9c22bf0274807c4ad3fc6b353b03876e3e`，`docs/ep_l2/review_packs/FT20261018_LANE5_R19_GOAL_COMPLETION_AUDIT_r1/RECEIPT.json`：原21/24 starts、20 CURRENT_ACCEPTED完整应用、10原矩阵配对；完成审计是只读的。H0五输入B/U几何均值`1.0016002037656606`与6项旧撤回身份冻结。D4/Q4/D2/L25及选定robustness不混用新source。R19已过期限，严禁重启或消耗剩余3次。
2. **Storage-Ops V8 = 完成**。174-new commit `7ed8a3d6f0af7a081d3a7a8d5755a448b7e312ad`，完成全部21项hash和164恢复确认；旧174三批准确源释放合计`9446871040`B的即时源端df增益，端点净增`8450060288`B，二者不同。禁止重复归档、源释放、第二迁移worker。Lane5独立2026-10-18T06:18:46Z复测/receipt commit `413d7300821f2d623ce8f638b866dd85fc6d729d`：物理workspace `60287987712`B（56.14756GiB），Share41.304GiB，足额RAM；1–3路模拟**资源条件**PASS，4路因实际workspace少378425344B且默认共享forecast超39361641B而BLOCKED；没有给任何应用发lease或资格。实际48GiB/Share40GiB/RAM64GiB底线不变。
3. **Lane2 = 结束**。commit `7c8ae4b5f32863c2f34f1eed0af3b51efc5fd395`，选定可综合有限RTL R3硬件 `e8d67d13b5205cdcda4c2c750a34f7cda6b0103b` 为未来DC入口；未运行DC。Nangate相同部分cut下B16/S64/Unified=1414058.128/1455472.200/1765551.858面积单位，U/B=1.24857，所有目标时序及2ns均未闭合，SRAM/原生Tag/MSHR/NoC未知。不下发R4，不因性能候选自行修改RTL。
4. **Parallel与MQ2/RG1未完成**。Lane5 R19完成回执表明新campaign `EPL2_PARALLEL_POTENTIAL_20261017_V1`累积32/72 starts，22条新CURRENT_ACCEPTED，MQ2/RG1 stage 0/24；旧R5 controller stopped，Lane5复测确认0活动模拟、0旧lease、R5 frozen expected 16GiB不匹配现在的**用户已批准20GiB**。原parallel T0不重置，**新增full application启动必须早于2026-10-18T11:30:14.500719Z（北京时间19:30:14）**。已接受run-key绝不重复跑。
   Lane1 producer status commit `a5a36d5db4ae42e049b9b2ac7819ec718493cd3d`: MQ2/RG1默认OFF候选 Core`84359d4ba492acb639a2092fa271e9169038bf7d`, Framework`197741be9be9b8e390a557d639503b416d8e95f0`，基础源码/standalone checks PASS，**没有正式producer binary、没有ON native验证/6profiles/必要guards**。旧Lane1短Goal为BLOCKED，原起止UTC03:02:03–07:02:03（北京时间11:02–15:02），没有后台worker。新资源条件单独PASS而非自动build授权；若用户指令到达时已超过原窗口，则使用一个**新的有界延续合同**，不伪造先前Goal继续运行。

## B. 协调优先级——先解锁新二进制，不等待第四模拟槽

**同一物理workspace上，正式Lane1 build与Lane5新的2/3路fullapp占用/预留可能竞争。** 不能凭当前56.15GiB静态快照同时允诺正式2-job build与3sim；优先通过中央registry锁进行**串行预检**，按真实组合内存/CPU/磁盘reserve决定，绝不杀在途任务或降低48GiB硬底线。

1. **Lane1首先恢复正式MQ2 producer构建（不重启旧R19或旧microopt Goal）**。用户将指令给原Lane1窗口后，读`microopt/RESUME.md`、其BLOCKED_AUDIT_r4及本V1，核实时下真实物理路径、50GiB producer门槛、central leases、源码/Framework/runner绑定与是否有残留编译进程。若仍安全，启用原候选的唯一正式build（有界2-job）和**MQ2首要**native tests（计划52cases、三模式6profiles及5 negative guards，按原合同，不为了抢时间伪称简化检查PASS）。每通过一组发布精确producer正/负、binary和effective config；只有达到相应正式科学资格才handoff给Lane5。RG1在MQ2通过且存在足以支持其实际ready-path的证据和剩余资源/时间后再做；否则RG1保留为源候选NOT_QUALIFIED。支持普通编译修复，但不得变更默认OFF、容量、银行数/端口、oldest request的liveness合同或业务语义后仍冒称原二进制。若过去UTC07:02，显式建立新有界短延续且不延长原T0。可重用已有合格输入/negative，不重复无影响的40min检查。**producer不启动全应用**。
2. **Lane5独立的新Parallel/R6续接，而非重新打开R19**。收到原Lane5用户指令后，先审R19完成回执、OPS V8独立复测、现有R5 stopped的真正原因、live registry/PID/lease/current V2、uncommitted R6本地草稿及全部20GiB预算绑定。R5 expected16GiB 与用户现在20GiB的合同不一致，应使用最小兼容性修复、正/负合同测试与原锁审计形成新的R6 `resume-current-campaign` 控制器；不要重新使用旧冻结R5校验值、不重启原R19。只有fresh preflight、source/input资格和对应预算都通过，才能启动唯一runner。所有原attempt、RESOURCE_LIMIT、失败、用户四点forecast例外过期等身份保留，**不自动重复失败点**。
3. **配对次序与纸面价值**：优先完整合格且仍在当前候选集中的高信息量局部控制/结构配对；若Lane1 MQ2到达，先Conv的B16/S64/U三模式OFF/MQ2同新binary六逻辑端点，随后FWT对应六端点；所有OFF只复用同binary输入完全相同的已经接受锚点，不拼旧fb674/2309数据。若只MQ2 PASS则不等待RG1、也不为凑18端点跑未完成的RG1。真正测得在同线组的缩短cycles、按来源划分的accepted/stall/wait和绝对差才能作为论文证据。RG1必须先有效ready witness，后配对，同条件公平放给B16/S64/U。若Lane1不可及时交付新binary，Lane5优先完成已有qualified source的incomplete paired/Ideal subset，不为实验数量而增加新机制。
4. **空间/开始时间**：Lane5与Lane1每次launch/admission时under lock重新测真实workspace/Share/RAM与combined reservation。优先producer build，资源许可时Lane5至多1–2路老资格运行；Lane1释放build lease后可考虑至多3sim，但每次要实际下界通过，**禁止因四路只差0.35GiB降低原48GiB floor**。原20GiB共享结果、Lane2 own12GiB无新增拨款，单run raw2GiB cap、parallel72总starts、microopt stage24 within72、最高4sim/8CPU/32GiB仍生效。准时停止**新增开始**，已获准正在运行的按原中止/到期契约执行。超过UTC11:30:14不要换个campaign名字重新起相同full apps。
5. 任何Candidate失败/源目标身份不闭合/预算不足/超时：保留原raw，发布有来源的`READY / BLOCKED / NOT_RUN`，不要写论文已验证的MQ2/RG1性能。不要为性能挑选隐藏静态基线。**不干预其他DTC/AWMA/C16作业**。

## C. 时间与论文决策（作者端）

- 当前基线稿：本聊天生成EN-v12 PDF+LaTeX；由ChatGPT负责后续收敛，**远端Lane6仍是EN-v8，不允许未经传递自行重写/覆盖EN-v12**。已接受的Conv/FWT四模式结构结果、R19正负样本与I_MEM_ALL_DATA参考保留；H0几何均值不可修改。
- 仅当正式MQ2/RG1完整应用被Lane5独立接收并显示可复现收益时，才在EN-v12后续稿中开“bounded service interaction”小节，否则把候选留在讨论/未来实现，不作为效果贡献。
- R3成本已有实际面积改善和负WNS，必须同时披露未知SRAM、传统外围、时序尚不闭合、SIM/RTL前端II4/II3等不匹配；不拼成应用净硬件收益。若DC尚未取得，正文正确限定并按收到的真实报告迭代。
- 不需要Lane2、Storage-Ops或Lane3的新Goal，全部已交付/关闭；需要的是**Lane1有界恢复 + Lane5独立Parallel续接**。

## D. 最小回执要求

Lane1交新source/Core/Framework/binary SHA、6 mode profiles, affected native tests/negative guards, exact application-qualification scope and STOP/BLOCKED blockers；Lane5交read-only preflight、原registry generation/input/run-key、每次attempt/qualification/clock、matched cycles正负、保存旧historical scope、deadline/预算和中央并发记录。双方均只在各自分支commit/push并远端回读；不要交叉改别的Lane工作树。
