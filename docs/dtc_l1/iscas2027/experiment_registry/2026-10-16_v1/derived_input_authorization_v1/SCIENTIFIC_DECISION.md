# DTC-L1 科学授权：Hotspot派生输入与三个旧格式风险（2026-10-16）

**状态：USER_APPROVED_CONDITIONAL_WORK。** 用户同意：(1) 将Hotspot V2作为有独立身份的source-profile-derived新输入交给原174 Lane A进行正式准入；准入通过后可登记和执行必要的**新输入匹配**比较；(2) Btree、2DConvolution、LUD保留原terminal PASS，科学适用性待审，由Lane B有界CPU-only核实来源。**这不等于新输入现在已准入或模拟已运行，也不证明它与原ELF/native采集等价。**

## 证据锚点
- Hotspot资格：Framework \`0bd0e603f48a93414c47583b7c205595600e72af\`, \`docs/dtc_l1/review_packs/DERIVED_INPUT_QUALIFICATION_CANDIDATE/{QUALIFICATION_REPORT.md,EVIDENCE_BOUNDARY.md,MINIMUM_PAIRED_REVALIDATION.md,DERIVED_INPUT_IDENTITY.json}\`。
- 三项风险：Framework \`266a8e375eb21552774956222208848d5902f37a\`, \`docs/dtc_l1/review_packs/LEGACY_FORMAT_SCIENTIFIC_RISKS_V1/{README.md,btree/REPORT.md,2dconvolution/REPORT.md,lud/REPORT.md}\`。
- 原174主Goal \`hrl/iscas2027-dtc-service-closure-174-v1\`继续执行；交接时所见HEAD \`9457e853671a1050a105fcc1bf5f6ecfea267d37\`，仅为当时记录，执行前必须fetch实际HEAD及running/lock/identity。独立文档分支不替代运行分支。

## Hotspot独立派生输入：可准入范围

原成员SHA256 \`ea268780903d10f61a36634bf90f8b00b7e160c1e0703d345efd4ab3e9c3f1b8\`；
候选成员SHA256 \`21cd403581a94451e1f9e7a79950d7effd25319daccc101187233e4a0c985985\`；
bundle digest \`dd0da35f5a3e3a2467a1cd23a53ce3966cd7eb6ee31035733e26f48dc532c169\`。
名称 \`HOTSPOT_SOURCE_PROFILE_RECONSTRUCTION_V2\`，与原输入是两条独立lineage。

CPU证据覆盖185个observed PC的opcode-root/GPR profile，16,950,260个明确shared地址及3,720,992个明确global load地址的源模型匹配；派生候选仅修改6个PC、122,760条记录、2,944,024个活动lane地址。原始执行掩码、predicate/immediate、original ELF/tracer/JIT、temp/power数据与native结果并未得到完整身份绑定；2,897,648个shared地址改变仍依赖重建源码/SASS模型。**原trace不变；新输入不能称为对原native执行的已证实逐指令复现。**

Lane A R0必须独立核原成员/新bundle/list/SHA、每条原/候选修改、完整13,169,524条warp records/377,291,004条活动线程指令、六PC变更、指令/同步/宽度/输出序列未变、消费者parser读入与实际对应Core、两个设计族的运行语义。通用R1 V2证明只覆盖其原限定域，不能替代新输入资格。**存在新支持域、指令语义、来源映射或公平性差异无法解释时，停止在准入，不运行性能。**普通manifest/parser runner包装缺失若能由immutable evidence确定性恢复，可以自行修复。

R0通过后可写带输入SHA的\`DERIVED_INPUT_ADMITTED_FOR_SOURCE_PROFILE_SCOPE\`回执。然后采用原174**唯一**launch authority，在独立可回溯的attempt命名空间注册和滚动运行**同一派生输入**的B16-N、IO256、OO128。两类模拟器Core及binary本就不同，应逐项核其合法设计差异和共用平台/输入/ROI/统计/周期/服务条件，不能硬要求文件SHA一样；旧B16/TC80/增强传统的输入SHA不相同，**不可作新分母**。论文主资源对照若继续包括TRAD96及TC80，则在查看新性能前明确其必要性并预登记这两个新输入arm；按合法gate与主模拟资源排期滚动执行。IO128/WAIT128只有在明确该机制论点需它们时再注册；不为填满旧矩阵而多跑。

严格验证每条自然terminal、完整kernel/指令、input/trace/runner/Core/binary/config/ROI、所有相关credit/PIB/Ref/collection/drain指标。原44行执行及失败/日志/HOLD保持不可变；不停止重启已有模拟，不能新建第二个persistent launcher。新旧输入/源/配对不交叉计算GM12，旧Hotspot promotion HOLD不被这份授权自动解除。结果可负可正，严禁性能驱动的输入选择。

## 三负载CPU-only来源核查授权

1. **Btree（先）**：1成员，1个PC \`1c40/LDG.E.SYS\`，6000个full32 mode0列表，5792条在历史E-list约定下可能改变sector/line身份。核真实采集/producer是否遵循全E而非仅P列表；不能把单条访问数量相同当作缓存语义等价。
2. **2DConvolution（先）**：1成员10个PC，40940条非零起始lane+stride的mode1，其中36846是cacheable global load、12282可变sector/line数量。version3同时存在修复前后，须优先核tracer producer/source build绑定；不以版本字符串认定已修复。
3. **LUD（随后）**：57,536条mode1风险，11904条cacheable global read、7936条global store及37696条shared。优先两个kernel的global路径、0x80/0x40锚点反例；参考几何中shared单条bank服务相同不证明完整地址等价。

复用已登记65个成员、104476条风险索引；无新GPU/模拟器、无全629重审、无原trace/parser/运行binary修改。每项输出来源依据、精确PC/有条件地址差异、是否足以确定格式合同、尚缺的最小来源、可验证新输入方案或明确\`UNRESOLVED_FORMAT_APPLICABILITY\`。没有充分证据则不要猜地址或无限搜索工具链。B不拥有任何A运行权限。

## 论文与审计边界

原Btree/2D/LUD的\`terminal_validation=PASS\`保持，科学层\`FORMAT_APPLICABILITY_REVIEW_PENDING\`；不废除已执行结果，不把其主要收益当无条件native含义。A其他合法作业继续自然结束与strict validate；所需新Hotspot操作可与原作业流水但必须独立身份、成本和调度权。现代4080容量NO-GO、SpMV SM89 NOT_ADMITTED、LayerNorm NOT_ADMITTED、SG3/logical80关闭边界全部不改变。不计算未闭合GM12，也不将保留11项偷偷叫GM12。
