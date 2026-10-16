# DTC-L1 / ISCAS2027：论文所需实验和证据总表 V1

**状态快照：2026-10-16，根据174已推送的`e1c474f31dd69a34c84f3222330e1c2518472104`、109的`890fb0be7e681a60419c49ca0a7aa85731d8c164`、容量科学决定`e13266ba207d8b8e47b56d62dfdb8bd04c8e2c5b`。** 当前活跃174程序的启动/进度可能晚于这些commits；“用户报告已启动”不等于逐行严格通过。除R1 qualified、109原生PASS和既有冻结成果之外，不将任何运行中行记为结果。

总原则：**论文需要的是可靠的主结果、合理替代方案、关键机制解释、模型服务成本和面积时序；不是凑齐大量扫描点。** 已登记的相互独立行按gate rolling，不加批次障碍，不reset分支、不重做冻结证据。

## 论文实验决策表

| 编号 | 层级 | 要回答的科学问题／最小实验 | 当前状态 | 归属 |
|---|---|---|---|---|
| E00 | P0 | 已有64-SM输入/Core/配置及基线身份核定：12负载629 ordered members; Core95/658例外; R2按当前定义复用 | ACCEPTED_FROZEN | 174 |
| E01 | P0 | 有限Tag/回填/唤醒/收集服务定义与正确性：1cy Tag+II1; 32B refill1/cy; waiter4/cy; collect4 sectors/cy; retire1/cy; OFF等价; NN ON | PASS_QUALIFIED_R1_V2 | 174 |
| E02 | P0 | 传统16KiB 128B新读参照：B16-N 12程序;原资源;已接受同Core控制 | FROZEN_EXACT_REUSE_REVALIDATE_ON_CONSUMPTION | 174 |
| E03 | P0 | 传统80KiB 128B新读参照：TC80-N 12程序;32set×20way;匹配128B | FROZEN_EXACT_REUSE_REVALIDATE_ON_CONSUMPTION | 174 |
| E04 | P0 | 更新后有限服务的DTC主性能试点：BICG/Btree/2DConvolution/Hotspot1 × IO256/OO128 =8行；下行cap32768 | PREREGISTERED_REPORTED_ACTIVE_NO_ROW_RECEIPTS | 174 |
| E05 | P0 | 增强传统缓存固定对照试点：同4程序×TRAD96-P256-M512=4行；32set×24way；20cy传统L1 | PREREGISTERED_REPORTED_ACTIVE_NO_ROW_RECEIPTS | 174 |
| E06 | P1 | 常规等待深度独立对照：同4试点×WAIT128=4行；16KiB传统data, PIB128,MSHR32 | REGISTERED_WAITING_GATE | 174 |
| E07 | P1 | 相同资源IO/OO完成与回收机制对照：同4试点×额外IO128=4行;复用已跑的OO128 | REGISTERED_WAITING_GATE | 174 |
| E08 | P0 | 完整12项新模型主结果：余下8程序 × IO256/OO128/TRAD96 =24行; 4试点12行单独登记 | REGISTERED_WAITING_PILOT_GATE | 174 |
| E09 | P1 | 有限服务敏感性、配置排序稳健性：少量代表程序;参数基于E01已有服务定义;先coarse screen | CONDITIONAL_PREDECLARED_SCOPE | 174 |
| E10 | P1 | 系统接纳/保留定向机制说明：集中/分散组、合并消费者、返回时差、hit/低MLP;已有R1定向用例复用 | PARTIALLY_QUALIFIED_VERIFY_COVERAGE | 174 |
| E11 | P0 | 4080本机原生并发/访存诊断：4类×3条件=12；SM89 SASS; 7独立批×10计时 | ACCEPTED_NATIVE_ONLY | 109 |
| E12 | P1 | SpMV现代真实程序与trace准入：SpMV 1138_bus; 36 CTA; 3 warmup+1 final SM89 tracer | NATIVE_PASS_TRACE_CONSUMER_PENDING | 109 producer / 174 consumer |
| E13 | P1 | LayerNorm现代原生结果：PyTorch2.5.1 FP32, 1024×1024主+8192×1024尺寸对照 | NATIVE_PASS_TRACE_NOT_ADMITTED | 109 |
| E14 | P0 | 4080模拟器传统基线验证：BICG/Btree/2DConvolution/Hotspot1 baseline-only;按有效kernel L1/shared分配 | REPORTED_ACTIVE_BASELINE_ONLY_UNCONFIRMED_RECEIPT | 174 |
| E15 | P0 | 4080固定128KiB容量合同审计：按kernel审计DTC80+传统side/data+shared不得超过128;真实端口/路径 | HOLD_SCIENTIFIC_CAPACITY_CONTRACT | 174 |
| E16 | P2 | 4080同预算DTC模拟配对：仅E15合法且E01/现代基线OK后，最多已准入代表性负载 | HOLD_NOT_AUTHORIZED_UNTIL_GATE | 174 |
| E17 | P3 | RTX3070交叉平台检查：最多3代表点，必须有相关模型证据 | OPTIONAL_NOT_LAUNCHED | 174 |
| E18 | P0 | 硬件面积及关键时序：C16/C80/C+/IO/OO同边界; SRAM+logic+reference/waiter/collector ports; target PVT/freq | WAITING_HARDWARE_EVIDENCE | USER / hardware lane |
| E19 | P0 | 研究结果表与图版本合入：性能图、机制时间图、资源表、方法表;保留回退/缺项 | PAPER_WORK_IN_PROGRESS | ChatGPT paper lane |
| E20 | CLOSED | 旧SG3下游容量扫参：queue128/DRAM/headroom/ICNT入口;已获限制结论 | CLOSED_NO_REDO | none |
| E21 | CLOSED | 旧FAST64/TC80/SG0和logical80：accepted core/input/fairness/finite scans及4个logical80失败保留 | CLOSED_NO_REDO | none |

说明：`PASS_QUALIFIED_R1_V2`仅表示已完成的定向服务资格及小NN验收，不能当作完整12项性能；`NATIVE_PASS`不是模拟器trace准入；`HOLD`不能被rolling supervisor绕开。

## 执行矩阵唯一真源（不得另建冲突的逐行清单）

- 174 finite V2 **44个已登记的独立新行**：`docs/dtc_l1/iscas2027/service_closure_174_v1/review_pack/r2/REGISTERED_ROWS_V2.tsv`，提交`e1c474f`。其中**试点12行**（4程序×IO/OO/TRAD96），**后续24行**（余8程序×三设计），**机制控制8行**（同4程序×IO128/WAIT128）。这些是**注册数**，不是当前已完成数。无需发出第二套启动矩阵。
- C16/B16-N与TC80-N此前已严格接受，先核完整身份、cap非绑定和配置/ROI相同；不因为新主表更新而重跑。
- 109原生15个case及SpMV/LayerNorm生产端资料：`docs/dtc_l1/review_packs/DTC_NATIVE_COVERAGE_109_V1/`，提交`890fb0be`。SpMV的consumer准入独立；LayerNorm trace为`NOT_ADMITTED`。
- 原来的64-SM finite模型与现代4080比较**不是一个矩阵**：现代 DTC容量gate仍HOLD；用户要求128KiB总物理预算，不允许运行208KiB冒充同预算。

## 里程碑（严格按结果验收）

1. **科学/正确性门**：R1 V2服务资格已PASS，后续新Core/改动须重做相应定向资格；保留被替代的R1 V1失败/invalidated attempts。
2. **第一结果门**：一条试点terminal→严格验证→发布单行receipt；独立注册行立即滚动补位，不等四个程序全做完。C16/TC80基线复用必须合法。异常fail-closed，普通launcher/parser修复后继续。
3. **主结果门**：12项×同一设计条件的完整结果＋不利样本；两个模型之间不拼接原整数。Heavy工作的启动顺序根据成本优先，别到最后才开始GESUMMV等慢行。
4. **机制门**：完整接纳的ready-to-collection、最后引用释放和物理驻留时间，分别区分共享写回排队；采用4个代表应用的matched depth controls。
5. **硬件门**：传统增强的相应代价不能从PIB/MSHR单纯计数推成面积；PPA到位才填性能/面积，不用学位论文4.7%替代。
6. **现代门**：4080 baseline-only可以并行；固定预算容量合同未通过前，**没有现代DTC性能行**。该门失败时应及时缩减论文现代主张，而非扩建完整模拟器。

详见同目录`EXECUTION_PIPELINE.md`（并发与调度）、`UPDATE_PROTOCOL.md`（状态维护）、`PAPER_SETUP_REQUIREMENTS.md`（论文实验方法）。
