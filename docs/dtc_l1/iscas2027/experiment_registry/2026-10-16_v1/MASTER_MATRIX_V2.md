# DTC实验与证据总表 V2（同步174已提交strict checkpoint）

**源快照：** 174 `59e1fd9b5f561f63647837c64582f43e755461f2`，检查点`checkpoint_20261016T0918Z`，其中`SUMMARY.json`标注2026-10-16 09:17:11 UTC；109 `890fb0be`；固定预算决策`e13266ba`。这是严格已发布快照，**不是服务器此时的实时进度**。保持旧V1不可删除。

| 关键状态 | 数据 |
|---|---|
| R1 V2源资格 | PASS，Core `6fba0136...`；default OFF等价、小NN ON/OFF和11项服务计数完成 |
| 新finite R2注册总量 | 44行＝12 pilot＋24 cohort＋8 mechanism controls |
| R2 snapshot | **3 strict PASS、6 RUNNING、35 REGISTERED_NOT_LAUNCHED** |
| strict PASS三行 | Btree/IO 247,940 cycles；Btree/OO 173,210；Btree/TRAD96 186,621 |
| 本地配对（单程序） | Btree IO vs TRAD96 0.753×；OO vs TRAD96 1.077×。**不能归纳GM12、等面积或原生加速** |
| 已复用基线 | 24条 B16-N/TC80-N accepted exact baseline，未重跑 |
| 4080传统baseline-only | 4个pilot全验收；旧SASS＋现代内存参数**反事实模拟**，不是原生同binary校准 |
| 4080 DTC | **HOLD**，0 DTC rows；预算128KiB，数组/端口共享和100KiB shared合法域未闭合 |
| SpMV | 生产端通过；174真实SM89 trace canary 因缺少binary89 dispatcher **NOT_ADMITTED**，无DTC结果 |
| LayerNorm | 真实native通过；SM86 cubin＋tracer跳过CALL指令，仍NOT_ADMITTED |
| 主研究 | R2 active rolling，不计算未完整的GM12 |

## 本轮科学决策表

| ID | 等级 | 实验问题／预注册范围 | 最新快照状态 | 归属 |
|---|---|---|---|---|
| E00 | P0 | 已有64-SM输入/Core/配置及基线身份核定：12负载629 ordered members; Core95/658例外; R2按当前定义复用 | R0_PASS_FROZEN_ASSET_VERIFIED | 174 |
| E01 | P0 | 有限Tag/回填/唤醒/收集服务定义与正确性：1cy Tag+II1; 32B refill1/cy; waiter4/cy; collect4 sectors/cy; retire1/cy; OFF等价; NN ON | PASS_QUALIFIED_R1_V2 | 174 |
| E02 | P0 | 传统16KiB 128B新读参照：B16-N 12程序;原资源;已接受同Core控制 | BASELINE_24_EXACT_REUSES_ACCEPTED_AS_OF_CHECKPOINT | 174 |
| E03 | P0 | 传统80KiB 128B新读参照：TC80-N 12程序;32set×20way;匹配128B | BASELINE_24_EXACT_REUSES_ACCEPTED_AS_OF_CHECKPOINT | 174 |
| E04 | P0 | 更新后有限服务的DTC主性能试点：BICG/Btree/2DConvolution/Hotspot1 × IO256/OO128 =8行；下行cap32768 | PILOT_IOOO_2_STRICT_PASS_5_RUNNING_1_QUEUED | 174 |
| E05 | P0 | 增强传统缓存固定对照试点：同4程序×TRAD96-P256-M512=4行；32set×24way；20cy传统L1 | PILOT_TRAD96_1_STRICT_PASS_1_RUNNING_2_QUEUED | 174 |
| E06 | P1 | 常规等待深度独立对照：同4试点×WAIT128=4行；16KiB传统data, PIB128,MSHR32 | REGISTERED_WAITING_GATE | 174 |
| E07 | P1 | 相同资源IO/OO完成与回收机制对照：同4试点×额外IO128=4行;复用已跑的OO128 | REGISTERED_WAITING_GATE | 174 |
| E08 | P0 | 完整12项新模型主结果：余下8程序 × IO256/OO128/TRAD96 =24行; 4试点12行单独登记 | COHORT_24_REGISTERED_WAITING_SLOT_ON_PILOT_ARMS_PASS | 174 |
| E09 | P1 | 有限服务敏感性、配置排序稳健性：少量代表程序;参数基于E01已有服务定义;先coarse screen | CONDITIONAL_PREDECLARED_SCOPE | 174 |
| E10 | P1 | 系统接纳/保留定向机制说明：集中/分散组、合并消费者、返回时差、hit/低MLP;已有R1定向用例复用 | PARTIALLY_QUALIFIED_VERIFY_COVERAGE | 174 |
| E11 | P0 | 4080本机原生并发/访存诊断：4类×3条件=12；SM89 SASS; 7独立批×10计时 | ACCEPTED_NATIVE_ONLY | 109 |
| E12 | P1 | SpMV现代真实程序与trace准入：SpMV 1138_bus; 36 CTA; 3 warmup+1 final SM89 tracer | NATIVE_PASS_SASS_NOT_ADMITTED_SM89_DISPATCH | 109 producer / 174 consumer |
| E13 | P1 | LayerNorm现代原生结果：PyTorch2.5.1 FP32, 1024×1024主+8192×1024尺寸对照 | NATIVE_PASS_TRACE_NOT_ADMITTED | 109 |
| E14 | P0 | 4080模拟器传统基线验证：BICG/Btree/2DConvolution/Hotspot1 baseline-only;按有效kernel L1/shared分配 | MODERN_BASELINE_4_ACCEPTED_OLD_SASS_COUNTERFACTUAL | 174 |
| E15 | P0 | 4080固定128KiB容量合同审计：按kernel审计DTC80+传统side/data+shared不得超过128;真实端口/路径 | MODERN_DTC_HOLD_CPU_CAPACITY_AUDIT_COMPLETE | 174 |
| E16 | P2 | 4080同预算DTC模拟配对：仅E15合法且E01/现代基线OK后，最多已准入代表性负载 | MODERN_DTC_HOLD_NO_ROWS | 174 |
| E17 | P3 | RTX3070交叉平台检查：最多3代表点，必须有相关模型证据 | OPTIONAL_NOT_LAUNCHED | 174 |
| E18 | P0 | 硬件面积及关键时序：C16/C80/C+/IO/OO同边界; SRAM+logic+reference/waiter/collector ports; target PVT/freq | WAITING_HARDWARE_EVIDENCE | USER / hardware lane |
| E19 | P0 | 研究结果表与图版本合入：性能图、机制时间图、资源表、方法表;保留回退/缺项 | PAPER_SETUP_V0_6_COMPILED_RESULTS_PENDING | ChatGPT paper lane |
| E20 | CLOSED | 旧SG3下游容量扫参：queue128/DRAM/headroom/ICNT入口;已获限制结论 | CLOSED_NO_REDO | none |
| E21 | CLOSED | 旧FAST64/TC80/SG0和logical80：accepted core/input/fairness/finite scans及4个logical80失败保留 | CLOSED_NO_REDO | none |

逐行执行真源仍为174的`docs/dtc_l1/iscas2027/service_closure_174_v1/review_pack/r2/REGISTERED_ROWS_V2.tsv`；最新44行状态见`review_pack/checkpoint_20261016T0918Z/REGISTERED_R2_STATE.tsv`。此概览不取代两者，既有失败/中止保留。

**效率判断：** Btree的三个试点arm均已通过，因此同arm cohort的`ANY_VALID_PILOT_SAME_ARM`要求已满足。174可在释放的worker槽位尽早启动已登记的慢行（GESUMMV/GEMM/MRI-Q），与剩余试点和短行流水并发，不应人为加“4个pilot必须全部完成”的屏障；当下6个worker和2-heavy上限由执行环境测量决定。需要注意当前已有6行RUNNING，不意味着闲槽可以超资源启动。

**论文解释：** Btree上增强传统组织已经显著快于IO，但略慢于OO。该负结果必须保留，不能挑选结果推导设计全面优越。原64-SM finite性能主表待完整12项。现代DTC若需重新定义容量/端口，应另行审定；不为继续空转开发而扩实验。
