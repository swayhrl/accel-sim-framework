# DTC-L1 / ISCAS2027 实验台账 V12 — Btree条件派生输入准入审查

时间：2026-10-16。基于明确SHA的GitHub已发布证据，不是ChatGPT直接SSH读取原174实时进程。V1–V11保留；本文新增独立科学审查，不修改任何Lane执行分支/模拟器/原44行/输入。

## 最新固定来源

- Lane D（本次隔离CPU窗口）`hrl/iscas2027-dtc-btree-format-stability-174-v1`，实际HEAD `fb13326a7d8d6b72f0cfd47151c8c898b967a62e`。审阅包 `docs/dtc_l1/review_packs/BTREE_E_LIST_STABILITY_CPU_V1/`。
- Lane A原174执行分支 `hrl/iscas2027-dtc-service-closure-174-v1`，核至 `33d935c498a43a3d28ea21072b5fceb230574096`。 `checkpoint_20261016T1541Z/SUMMARY.json` 的机器快照2026-10-16 15:41:35 UTC：原44中37条`PASS_CHECKED_SCOPE`、4运行、3原Hotspot HOLD；原Goal ACTIVE，无总体平均。四条仍运行的是BICG IO128和GESUMMV IO/OO/TRAD96。
- A自V11又完成ATAX IO256 83,797,212 cycles，对应C+ 30,981,690、OO128 50,796,515；BICG WAIT128 84,049,733 cycles与同原输入B16-N 79,721,847相比慢5.43%，虽PIB full事件从8,804,793减为0。完整strict和资源/输入证明见A的两个最新review pack；该事件计数不是阻塞周期因果分解。
- 原44现有**10个**主三臂数值完整；这不代表10项全scientifically promotable，Btree/2D/LUD的`FORMAT_APPLICABILITY_REVIEW_PENDING`不变。Hotspot V2五组独立派生输入已完成，不计原44。现代128KiB DTC HOLD；SpMV/LayerNorm DTC模拟NOT_ADMITTED。尚无完整GM12或统一PPA/等面积结论。

## 本次科学审定

**接受Btree G0–G3，仅限 `BTREE_FIXED_PC1C40_CONDITIONAL_FULL_E_LIST_TO_P_LIST_V1` 条件输入的CPU准入。**

- 历史producer revision `0e2fddcdef37fc59ad786553892b75567a5f2cdb` / SHA256 `8dcb5ad444a6cb6a3cfb1271308e27b8395ee16afae0135703b3ac3820b09d4a` 支持ascending E-list格式，但并未绑定该历史capture。
- 原Btree固定kernel-1的PC1c40共6000条width4/mode0/单P/full32记录均一规则选择raw_word[active_lane_id]；5792地址和sector/line身份变化，208相同；其他记录、完整list与kernel-2不变。新kernel-1 SHA `6295eb13625bbc8f25a712917b1b92a02ffcd2e1faba542e555f7845a1288722`，bundle `6e59d31e018befcdd8d9244e6c90d09ab8dd51c665c77785857b690f051ed585`。
- CPU真实冻结生产trace_parser与独立reference完整消费两个kernel：15609327 warp记录、444467849活动线程指令、2011551访存记录；每kernel活动地址流与指令流SHA匹配，未运行模拟器。初始工具错套4B的失败和修复已独立保存，非输入/模拟器修改。
- 静态Core合法域已核，有限服务动态运行资格仍未核。原Btree数值PASS保留，但`FORMAT_APPLICABILITY_REVIEW_PENDING`继续；不能由新输入推断原ELF/native等价。
- 2DConvolution：局部30见证尚不足以确定整kernel E/P及PC/SASS/输出基址；`UNRESOLVED_FORMAT_APPLICABILITY`，本轮STOP，不生成新正式输入/仿真。LUD不追加任务。

## 后续既有批准范围

新审阅决议：`btree_format_stability_v1/CHATGPT_SCIENCE_ACCEPTANCE_AND_LANE_A_CONTINUATION_V1.md`。它明确规定只有**原174现有Lane A唯一调度权**可在独立再准入、绑定新bundle、资源预检及六臂新lineage/UUID登记后运行：B16-N、TC80-N、TRAD96/C+、IO256、OO128、IO128。全部新臂统一cap32768、共同新输入；不得直接复用旧cap8192的C16/C80结果作为分母或将新旧性能差异完全归因于trace解释。跨输入稳健性重点审原/新本来就统一cap32768的C+与DTC设计。IO128/OO128可提供同PIB深度的机制比较，但不等于等面积。

此合同**不是**第二个A Goal、模拟器启动收据或44行登记更新；CPU窗口全部六臂`NOT_RUN`。原A剩余四作业不被停止/重启；若唯一authority暂无法安全接纳新lineage，必须STOP并审查，不新起第二套launcher。性能与失败按新独立审阅包记录，负结果与排序反转保留；完成六臂后停止扩展，不扫参数。

## 英文论文影响

英文v0.7 STYLE尚缺实际LaTeX源包，本轮不假称已修改。新增Btree派生结果须待六臂严格收口才能进图表，并以`conditional derived-input sensitivity`为限定；原Btree/2D的优势暂不升级为native application performance。BICG/ATAX明确回退须与增强传统C+成本向量同时呈现，资源向量不是统一面积报告。禁算未闭合GM12，禁拿旧1.326/1.592几何平均及原博士4.7%面积移植为本次新数据。
