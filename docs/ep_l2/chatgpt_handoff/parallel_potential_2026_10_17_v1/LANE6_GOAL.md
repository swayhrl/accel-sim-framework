# Lane 6｜EN-v8增量接收、潜力图接口与实现成本

先完整阅读同目录 [PARALLEL_CONTRACT.md](PARALLEL_CONTRACT.md)，再执行本Goal。公共合同定义四条并行线、首轮50个实验单元、总计最多72次启动、依赖关系和统一身份；这些是全局预算，不是每条Lane各自的额度。Lane 5统一管理最多4条应用模拟器。**Lane 6不启动应用模拟器，不等待全矩阵结束。** 本文件不重新分配其他Lane资源，不代替独立科学资格。

## 0. 身份、母稿与已授权范围

- 使用原Lane 6窗口、原worktree和原分支 `hrl/ep-l2-ft20261016-lane6-v1`；不reset、不force、不覆盖已有发行目录。
- 当前母稿提交：`1740009d1579b2402b32076f4f65f27619396c01`。
- 母稿目录：`docs/ep_l2/review_packs/FT20261017_LANE6_EN_V7_OWNERSHIP_D4_r1/`；完整阅读 `EP_L2_EN_v7.tex`、`README.md`、`NATIVE_INTAKE_AND_RESULTS.md`、`SOURCE_MECHANISM_EVIDENCE_MAP.md`、`UNFINISHED_AND_NEXT.md`、`RECEIVED_NATIVE_PAIRS.json`、`analysis/checkpoint1/INTERACTIONS.json`。
- 该稿已完成4技术页加1参考页，已接收H0五组、D4 Convolution/FWT、Q4 Convolution。沿用其正文、已核引用和真实图；本轮做增量更新，不重新写一篇论文。
- 本轮可修改Lane 6自己的论文、派生图表与脚本、接收记录、图表接口、成本账和状态；不得修改其他Lane的科学ledger、原始输入、raw结果、配置或运行进程。
- 运行前核对原分支实际HEAD。如已有后续合法论文提交，先保留并阅读它的差异，在其上继续；本母稿SHA是继承入口，不是回退目标。

## 1. 本轮Goal

完成当前已经到达的完整配对的论文侧接收，把H0/Q4/D4从“局部动作减少”更新成可直接判断绝对性能与相对机制效果的结果图；同时为新50格并行矩阵准备统一的结果、ideal潜力、有限配置、结构对照和成本接口。当前已到结果、真实图、接口及源级成本完成后即可正常结束本短Goal。

论文必须分别回答以下问题，不能用一个结果代替另一个：

1. 固定输入在明确定义的ideal访存服务下还有多少性能空间。
2. 解除哪一项具体限制改变了执行时间和机制的相对效果。
3. 有限配置中EP-L2相对匹配参考是否更好。
4. S64等合理静态分割能否获得同类收益，U-cap16揭示的本地WB额度作用是什么。
5. 上述能力需要多少实际存储与控制代价，附加时序是否影响收益。

保留每项实验的正、近零和负结果。未通过资格、没有实际触发目标路径、尚未完成分别记录，不能写成“机制无效”，也不能填零。

## 2. 立即接收现成结果

1. 只读获取Lane 5原分支 `hrl/ep-l2-ft20261016-lane5-v1` 的最新 `STATUS.md`、`RECEIPT.json`、当前独立科学接受/撤回索引以及对应immutable result packs。已核的交接快照为 `73d3e3eedbfd92643db2f674a49e16605d3e2260`（2026-10-17 10:43:05 UTC）：R19为12次启动、12条接受、0条活动，V2 generation17；**Q4 FWT、D4 vectorAdd_4M、D4 SAD三组均已CURRENT_ACCEPTED，应立即逐组进行新增论文接收。** 包 `docs/ep_l2/review_packs/FT20261017_LANE5_R19_ROBUSTNESS_DELIVERY_AND_PRODUCER_WAIT_r1/` 提供六份分别对应单pair的adapter。核对这一包及新的分支回读，按正确单pair adapter消费，不把母稿的“Q4未完成”沿用为现状。
2. 对尚未在论文中消费、且已满足当前科学资格的完整配对，沿用现有 `receive_condition_native.py` / native intake和派生分析入口，每次使用新attempt目录；完整pair到达即接收，不等待其它workload或条件。
3. 对仍在运行或缺少独立资格的配对，只记录依赖和确切缺项。继续完成本Goal其它工作，不建立后台poller，不反复等它。
4. 所有数值来自完整native接收包和原始计数重解析。完整输入/commandlist/trace body、source/binary/ordered config、真实run key、当前target-row资格、原有native-byte/nonatomic语义证明以及64-slice终止/drain必须成立。不得用协调摘要、进程状态、来源不明CSV或只读source资格替代应用结果。
5. 已接收immutable pack允许复用其已验证的字节身份和native proof。应记录复用的pack/hash、原校验范围及本次新增检查；当前target rows的身份、条件资格和撤回状态仍要查询。**全局generation因无关新结果append而上升，不自动否定原immutable输入，也不自动触发几十分钟的全trace重hash。** 只有相关输入/二进制/配置/raw身份改变、实际撤回、证明范围变化或无法确定一致性时，才重验受影响的部分；不能放松实质native资格。
6. 如果旧工具把“任何分支前进”都当作目标失效，先比较目标row及其所有实质依赖是否保持不变。允许为严格等价且无撤回的目标建立可审查的包装/适配记录；不修改科学authority、不跳过目标身份、不把旧PASS强行用于变化后的payload。普通工程/包装问题在本Lane解决并继续；真正的资格冲突保留失败证据，排除该点，其余写作继续。
7. 现有r19 receiver若仅支持Convolution/FWT或少数regime，在新版本中做增量scope/condition支持：当前普通SAD/vector及未来已资格化D2/L25都应依赖各自真实、完整、source-bound native input与condition证明。保留旧reader/pack不变，复用已有native引擎；不能移植旧r17证明替代当前输入、不能伪装成另一个workload或regime，也不新建一套平台。新增映射须检查误绑workload/config/condition会被拒绝；仅allowlist或包装扩展不放宽完整trace、数据语义、模式配置和64-slice闭合门槛。未来D2/L25没有实际accepted配对时只准备接口，不填数值。

### 冻结的统计组

| 统计组 | 固定成员 | 发布规则 |
|---|---|---|
| H0 primary five | SAD、vectorAdd_4M、cfd_097k、convolutionSeparable、FWT_7_21 | 原geomean `1.0016002037656606`保持此组身份；CFD负例和SAD近零均保留 |
| R19 D4 primary two | convolutionSeparable、FWT_7_21 | 既有两组均值保持独立，不因新增样本改名或替换 |
| R19 Q4 primary two | convolutionSeparable、FWT_7_21 | Q4 FWT完整接收后才计算该两组均值；不再把已完成实验写成未运行 |
| R19 D4 extension | vectorAdd_4M、SAD为追加成员 | 单列追加身份；扩展视图同时显示原Convolution/FWT，包括负Convolution。不得只画新增有利点，不用扩展mean替代原两组mean |

不得把诊断组、扩展组、新结构组或ideal结果混进H0五组均值。新50格矩阵的组定义、成员与比较关系来自公共合同/正式manifest；不能根据已看到的性能挑选或重命名统计组。

## 3. 先用已有数据形成真实图

### A. 绝对执行时间与相对效果

立即从已完整接收的H0/Q4/D4生成派生表和图，至少保留每个workload、condition下的B/U绝对GPU cycles，以及：

\[
S_w(h)=C_{B,w}(h)/C_{U,w}(h),\qquad J_w(h)=S_w(h)/S_w(H0).
\]

同时报告B和U各自相对同模式H0的变化。`C_B(H0)/C_U(h)`不是纯机制收益，不能作为EP-L2 speedup。cycles取native完整应用GPU累计值，不是slice求和，不因DRAM域变化改用另一分母。

图必须让读者看到“双方都变快但U优势减小”“解除拒绝但U变慢”“效果近零”等实际情况。D4 Convolution和Q4 Convolution的负例保留；已收到的正例不覆盖它们。图轴不能暗示细小差异是显著提升；不为确定性单次仿真捏造误差棒或统计显著性。

### B. 内部机制证据

沿用并按需合并真实H0 Fig2/Fig3，展示copy数量、logical bank operations、成功bank grants、bank wait总和、WBUF/WAD与下游拒绝等。不同计数定义保持分列：

- repeated refusal attempts不是unique stalled requests，也不是GPU elapsed cycles；没有合格分母时比例为null。
- bank wait总和与bank grants分别保留，不能把等待总和直接从应用cycles中扣除。
- B16 staging_lifetime从实际copy readout开始，U从producer commit开始，二者都到lower-FIFO acceptance；跨模式均值不是同一个时间区间。只做同模式跨条件比较，或明确说明不同端点；不为漂亮图改原统计口径。
- WB record event peak与post-drain sampled WB-role occupancy是不同观察量。采样为零不意味着无瞬时WB数据；不能互相替代，也不能将一个字段伪称另一个字段。
- WAD寿命到WB completion，WB本地data寿命到lower acceptance。WAD-full与本地WB-data-full必须分开。

### C. 修正摘要及正文的范围

母稿摘要的“neither design records local-buffer refusals”过宽。按实际观测明确写WB-data admission与L2-to-DRAM queue refusals等具体类别；Q4仍可能有WAD/scheduler限制。全文统一此口径，不宣称所有本地/下游资源均不约束。

## 4. 新矩阵只准备接口，不等待或预填结果

对公共合同首轮50格准备派生schema与制图接口，未来的结果必须经过相应release/profile/condition独立资格及对应scope的独立接收后才能入图。本轮不能创造尚不存在的run key、source SHA、cycle或效果。

新矩阵按公共合同采用对应native或reference接收scope。合法绕过物理L2的ALL_DATA端点检查原始指令/请求、store/reference恰好一次提交、producer顺序、返回snapshot及全部状态退尽，不要求伪造64-slice物理WB活动；普通有限配置和本轮R19配对继续现有native检查。新矩阵均值按profile/condition与预声明workload集合计算，不把同属IDEAL或L2_STRUCTURE的不同模式合并平均。

最少字段包括：experiment/cohort/workload/input identity、reference/profile、condition、source/binary/ordered-config identity、mode/profile资格、ideal开关及作用范围、改变的资源/服务、accepted target rows、packet/raw hashes、cycles、比较分母、S/J适用性、关键机制计数及有效分母、终止/drain、当前撤回检查、接收状态。尚未到达值用null/缺项和状态，不用数值零。

准备以下可复用图组：

1. **Ideal潜力图**：同一完整输入和明确比较基准下，原有限配置与指定ideal的归一化cycles。精确列出移除和保留的延迟、队列/服务、依赖与排序；只移除global-memory/L2以下约束时不得称“全部memory无阻塞”。这是该理想定义下的潜力参照，不是EP-L2可实现speedup，更不是物理PPA。
2. **具体限制解除图**：各单项/合同允许组合的独立归一化柱或效果矩阵；不能把重叠阻塞项堆叠为可相加的周期分解。未触发目标限制与解除后无收益分别说明。
3. **有限配置图**：有限参数和匹配B/U并列，附具体资源增量；将绝对加速与同条件机制优势分开。无效和退化条件进入相同视图。
4. **结构对照图**：B16/S64/U-cap16/U及公共合同明确的其它profile。`U/U-cap16`检验原位协议下本地WB额度作用；`S64/B16`检验同总容量静态配额；`U/S64`检验竞争力。`U-cap16/B16`仍含落点/bank分布等差异，不能自动命名pure-copy-only消融。
5. **成本/时序敏感性表**：当前及未来正式release的公共/增量字段、数据carrier、端口与pipeline假设。+1cycle等附加时序敏感性是模拟实验，不是STA证明。

新机制/source尚未发行时只写预期接口与待核项，正式发布后按确切diff更新。不要根据“S64”“P2”等名字推断实际配置。

## 5. 更新当前源级成本与未来差分入口

当前已接收WB-only实现：Core `7b8e6ac70b8fe0f1bd37efca11acb5284938825d`，Framework `9bd17f9db3e8cbbc3fdad7283d1e292918546fd5`，binary SHA256 `23094a9d6d6bc5edc4afae4dfc1c5ef0fb3b5d45fbfe56ffb4a33db46c597dee`。

1. 以当前源码及母稿 `core_source/`/`SOURCE_MECHANISM_EVIDENCE_MAP.md`为入口，保留旧成本账的历史身份；将当前字段、真实控制变化与原账逐项对照。相同blob/字段可复用核验，不复制旧表伪称新测量。
2. 分别列数据RAM、共同latch、tag/WB handles、generation/owner/pin/sector state、pending transaction/rollback、allocator、bank arbitration、WAD和下层数据carrier。gross表示、B/U共同项、真实增量项、未确定硬件编码分别标明；不把所有字段都当增量，也不全部免费抵消。
3. 当前1168×128B=146KiB/slice；4×292槽，64 slices数据9.125MiB，共同128B latch合计8KiB/chip。相等字节和模型bank服务不等于相等面积、hit latency、频率或能量。
4. 为S64/U-cap16/P2与有限资源条件建立差分入口：S64是等总槽静态重划分，不能由现有wbuf=64导致总槽增大；U-cap16需核本地data责任token及其释放边界；P2按正式定义计入真实服务、端口、仲裁/队列或其它改变；有限下游资源按实际宽度/深度计费。尚未实现的改动不填写测得成本。
5. 如其它Lane在本Goal运行期间发布新release，读取确切源码差分与qualified配置，仅更新涉及字段、端口/服务、时序路径及成本责任；不得默默把7b8成本用于新实现。分清原7b8已接收数据与新release结果，不覆盖原发行。
6. lower acceptance后必须定位实际数据carrier。避免把同一数据在流水途经多队列重复算成多份RAM，也不能把软件指针当免费数据存储。symbolic versions是验证sidecar，不替代128B payload，也不能按C++ sizeof估面积。
7. 没有匹配RTL、SRAM宏、工艺与约束时，完成参数化bit/端口/控制账和明确未知项；不得造mm²、MHz、mW或节能比例。若已有可直接用的匹配实现材料，只在本Lane成本范围内整理与核对，不启动未经公共合同分配的大规模物理设计任务。附加一周期敏感性、模型logical operations减少均不是STA或实测能耗。

## 6. 论文增量收敛与交付

在新的独立review-pack目录输出EN-v8或明确的下一增量版，保持4技术页+1参考页，原字体/页边距不变。不把新50格任务进度、Lane编号或全量审计流程塞进正文。保留母稿机制主线，通过重新组织/合并结果图、删重复语句给新证据腾出空间，不追加一篇新稿。

必须交付：

- 可编译TeX、PDF、准确引用和必要图资产；完整构建入口、页图检查、图/表数值来源。
- 当前新增完整pair的native接收记录与增量结果表，固定cohort和mean映射。
- 已有H0/Q4/D4的绝对cycles及S/J真实图；新矩阵schema、条件/比较关系接口和制图入口。
- 当前Core源级公共/增量成本表，以及未来S64/U-cap16/P2/finite release差分入口；不能将未知PPA写成零。
- 精简的claim–evidence表：ideal潜力、具体限制解除、有限配置效果、静态对照、成本分别标已证/待证及精确来源。
- `STATUS.md`、`RECEIPT.json`与未到结果依赖清单，明确此次已消费哪些配对、保留哪些组、下一事件是什么。

数值结果改变后只重建受影响图/表和正文，再完成一次最终4+1页编译与视觉核验；不无意义重跑producer测试或全部历史native输入。校验原pack不被覆盖、无未解析引用、无不可读图/越界版式。按原分支正常非force提交推送，回读确切包含提交/关键文件身份；不得用自引用SHA伪证。

**停止条件：** 本轮开始及执行中已到达、可合法接收的结果已完成接收；上述真实图、未来接口、当前成本与增量正文完成并发布，即报告Goal完成。未来accepted pair、正式new release或物理实现资料到达后再用事件驱动短任务续接；不把等待所有50格、全部72次额度或其它Lane全部结束列为完成前提，不建立persistent poller。
