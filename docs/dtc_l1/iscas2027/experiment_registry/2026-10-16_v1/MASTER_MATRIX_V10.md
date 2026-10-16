# DTC-L1 实验台账 V10：OO ATAX有限服务终止验收与论文增补

日期：2026-10-16。本文是ChatGPT对已发布GitHub证据的科学审查与协调快照，不是新Goal，不增加实验授权，不代表本会话直接查询了174进程或重新核验服务器全部raw字节。

## 1. 固定证据与本轮增量

- Lane A实际远端HEAD：`cec06d1a0c7ea59101c081ed682c219739cd3aba`，直接父提交为交接锚点`b7444fe6bfe453cfe33ee815f2bfb02afad133ea`。
- 本轮读取该HEAD上的LATEST_REPORT顶部、CLOSURE_REQUIREMENTS、checkpoint_20261016T1404Z/SUMMARY、有关逐行状态、OO ATAX原strict收据及补充完整范围审计；同时读取Hotspot V2准入和五臂完成报告。
- 原44行机器快照时间：`2026-10-16T14:03:36.242501+00:00`；OO ATAX补充范围审计时间：`2026-10-16T14:04:53.127532+00:00`。报告标题14:04Z不是本会话进程查询时间。
- Lane B实际远端HEAD仍为`d46cce269b88055decc2ca052dcb9baae0efee7e`；完整读取最终README及Btree、2DConvolution、LUD三个来源报告。
- 更新前实验台账分支HEAD为`5c07e1913f63351b43abd533d87c1443039ed114`，已完整读取MASTER_MATRIX_V9.md。V1—V9均保留。

本轮相对V9的新增执行结果只有原输入OO ATAX完成。当前研究目标不变：在有限数据、等待元数据与访问服务资源下，比较DTC的查询映射/数据保留分离及IO/OO完成组织，与扩大传统缓存/等待结构的性能和成本取舍。

## 2. 已发布状态

| 项目 | 本次已核状态 |
|---|---|
| 原44行 | 34 terminal/invariant PASS、7 RUNNING、3旧Hotspot admission HOLD；0合法未启动 |
| 仍在运行的原行 | BICG IO256、IO128、WAIT128；ATAX IO256；GESUMMV IO256、OO128、TRAD96 |
| 新增完成 | ATAX OO128：50,796,515 cycles，145,666,048 active-thread instructions，2个完整有序kernel |
| 原输入主三臂数值完整集合 | 仍为8项：Btree、2DConvolution、GEMM、DWT2D、Gaussian、LUD、NN、MRI-Q；ATAX IO未完成，不能增加为第9项 |
| 原增强传统 | 10条执行PASS；GESUMMV运行；旧Hotspot禁止启动 |
| Hotspot V2 | 独立新输入的5条strict/resource PASS保持；不加入原44行、不替换旧Hotspot的2个执行结果和3个HOLD |
| 输入科学层 | 原Hotspot为HOLD_SHARED_TRACE_INTERPRETATION；Btree/2DConvolution/LUD仍FORMAT_APPLICABILITY_REVIEW_PENDING |
| 实施成本 | 当前五设计统一RTL/DC、SRAM宏与关键时序材料未闭合；资源向量比较不等于等面积 |
| 总体统计 | 不计算未闭合GM12，也不擅自删除负载或混入派生输入生成替代平均 |

34条执行PASS中仍含原Hotspot的2个科学HOLD和其他格式待审输入；执行PASS数不是无条件可发表结果数。

执行端保持原174账户/容器，不是174-new。Lane A原DTC_SERVICE_AND_MODERN_BASELINE_CLOSURE_174_V1继续由既有唯一调度与strict watcher收尾。B/C/D不自动重启；现代DTC保持容量/端口HOLD，SpMV/LayerNorm的native与NOT_ADMITTED仿真边界不变。旧冻结实验不重开。

## 3. 新报告科学审查：接受OO ATAX当前限定范围

### 3.1 交叉一致性

| 核查项 | 本轮读取或复算结果 |
|---|---|
| 原attempt | `a58df5fb-f532-467d-8bb6-f9e99d866a27`，注册行R2_V2_COHORT_OO_ATAX |
| 模型身份 | Core `6fba0136f8465b59fe5858a950fa39efb265f654`；binary `fe2d2737ebaed01680ebfc2346f727306c8db58ee0ca20b1e1f038056e99833b` |
| strict收据 | `a58df5fb-f532-467d-8bb6-f9e99d866a27.strict.json`；补充审计与包清单记录SHA256 `54b357c03c32d0aeb0f4264f0c3a1368746d7b744278cda1897238c4ab990d82` |
| 完整指令范围 | 两kernel分别71,380,992与74,285,056条active-thread instructions，复算总计145,666,048 |
| 终止及资源 | 原strict的natural_exit、完整kernel、单epoch、身份、引用/PIB/lower/inflight排空、physical/credit/dependency/ordinary balances均为true |
| 输入范围补证 | 补充审计记录原2个成员的大小与SHA、trace-list终止身份，以及逐kernel完整指令范围；未重新扫描629成员 |
| 64SM采样分母 | 64 × 50,796,515 = 3,250,976,960，与service samples一致 |
| 完成时间分解 | ready-to-collect 2,369,782 + collection 5,785,440 + WB wait 14,922 = fully-ready-to-complete 8,170,144 |
| 退休计量单位 | 2,097,408条可缓存warp指令；不是145,666,048条active-thread instructions |

这些是对已发布收据及其数字的一致性复核，不是本会话在174上重新运行validator或重算trace哈希。原strict中的所有检查通过支持该注册行按原合同验收，不扩展到native等价、全ISA或硬件服务校准。

### 3.2 对照与判断

同原输入的TRAD96/C+为30,981,690 cycles，attempt为`a5366566-8b68-4e63-ad89-761241e6f1c0`，传统Core/binary保持独立身份。两条逐行状态与补充审计中的比较一致。

`speedup(OO128,C+) = 30,981,690 / 50,796,515 = 0.6099176291916877`。

因此OO128周期比C+多63.9566%。这是完整注册输入上的负结果，接受并保留；不因其方向不利而重跑、调服务参数、改cap或改输入。ATAX IO256尚在运行；此结果不完成ATAX主三臂，也不提供ATAX同深度IO/OO消融。C+和OO的查询覆盖、PIB深度、完成组织及服务路径不同，不能把这项差异单独归因于某一机制。

新结果与此前BICG OO相对C+约0.533×一起，进一步要求论文同时呈现增强传统有利的负载。它不证明DTC没有研究价值，也不支持DTC普遍优于扩大传统结构。最终性能—成本判断仍依赖有效输入集合、剩余对照与硬件材料。

## 4. 已完成证据的科学范围

Hotspot V2的B16-N、TC80-N、C+、IO256、OO128分别为152,914、107,774、82,873、85,718、84,456 cycles。五臂使用同一派生bundle，独立准入状态为DERIVED_INPUT_ADMITTED_FOR_SOURCE_PROFILE_SCOPE。C+最快；IO/OO相对C+为0.966810×/0.981257×。只用于公开定义的源码/SASS轮廓重建输入，原ELF/tracer/JIT、temp/power数据与native输出等价未建立。

Btree和2D的同128深度配对保留执行及计量PASS，但不解除输入语义风险。Lane B三个来源调查已完成并STOP，科学适用性仍未决。特别保留证据强度差别：

- Btree：单PC的6000条单P/full32列表，在已检E-list合同下关联明确，P-only serializer与长度不相容；实际capture绑定仍缺。三个已检ELF均不能匹配原PC。
- 2DConvolution：version3下存在打印P/编码E与打印P/编码P两种真实源码，版本/日期不足以选择；未知动态E锚点不能用任意逐行端点取代。
- LUD：40个global PC、19,840条记录的限定源码模型支持冻结first(P)=16地址，这是正面证据；原编译/predicate/producer绑定和shared完整地址语义仍未闭合。

不把“来源调查结束”解释为风险解除，也不把未绑定历史身份无限升级为禁止一切公开定义的派生研究。

## 5. 下一项需要用户决定的科学问题

是否授权Btree/2DConvolution的有界输入解释稳健性或独立源模型候选，是下一项输入/论文范围决定；本文件没有授予该权限。

建议先审Btree单PC/full32的固定E-list候选：要求候选在声明producer合同下自洽、逐条地址来自原字节、有不可变身份和独立consumer准入，再讨论最小配对臂。2D只有能在整个kernel内建立有来源支持的统一解释时才进入候选，不为凑两端性能点虚构动态E。LUD已有global正面证据，可后置，不自动强改锚点或重扫shared投影。

在用户决定前，A原有7行继续自然完成；不派新Goal、不生成正式新trace、不启动额外模拟。即使后续两种合法解释排序一致，也仅支持声明候选集合内的稳健性，不能声称恢复原native采集或穷尽所有E解释。集合/claim变化与是否刊出最终平均需另行明确。

## 6. 论文工作状态与待合入文本

当前目标稿仍是英文DTC_ISCAS2027_LATEX_V0_7_STYLE_SOURCE.zip，不是早期中文v0.7。本会话附件清单和容器只有主交接MD、博士论文及历史handoff；两次Files检索未取得英文源ZIP、配套PDF或PAPER_V0_7_ACTIVE_SOURCE镜像。因此下列内容是基于已核实验的待合入文本，不是假称已修改/编译v0.7，也不产生v0.8版号。收到真实源码后须核对原段落、引用键、图表和版面再合入。

### 输入方法段候选

```latex
The evaluation distinguishes the original traces from a separately admitted
Hotspot input reconstructed under a disclosed source/SASS profile.
Producer-format ambiguities remain unresolved for the original Btree,
2DConvolution, and LUD traces; their results are retained as conditional
simulation observations. The reconstructed Hotspot is evaluated with its own
five matched-input configurations, and its results are kept separate from the
original-input cohort.
```

### ATAX结果段候选

```latex
For the complete ATAX trace, finite-service OO128 takes 50,796,515 cycles,
compared with 30,981,690 cycles for C+, giving a normalized speedup of
$0.610\times$. This regression shows that the selected DTC organization does
not outperform the enhanced conventional design on this workload.
```

本段可用于已核OO/C+两臂说明，不补未完成IO柱，不宣称完成ATAX三臂或定位唯一回退原因。与BICG及其他程序的整体表述应在剩余合法行完成后统一组织。

### 独立Hotspot案例段候选

```latex
On the source-profile-derived Hotspot input, IO256 and OO128 take 85,718 and
84,456 cycles, respectively, compared with 82,873 cycles for C+.
Both DTC designs outperform C16 and C80 on this input, but C+ is faster.
These results apply to the disclosed reconstruction, whose equivalence to
the original native capture has not been established.
```

### 合入约束

原44行结果、Hotspot派生案例和格式待审案例应可辨识，不用一个无说明的平均隐藏输入差异。保留有限服务假设与96KiB总数据预算；当前没有现代DTC性能结果，删除对此类待报告结果的期待。硬件表继续等待用户真实材料，不移植旧4.7%面积或旧1.326×/1.592×性能。机制图中Btree/2D的科学风险须与配对结果同时可见。

## 7. 固定来源入口

以下均为本轮读取的精确commit路径；A分支可能随后前进，不要求回退。

- [A LATEST_REPORT](https://github.com/swayhrl/accel-sim-framework/blob/cec06d1a0c7ea59101c081ed682c219739cd3aba/docs/dtc_l1/codex_handoff/LATEST_REPORT.md)
- [A closure ledger](https://github.com/swayhrl/accel-sim-framework/blob/cec06d1a0c7ea59101c081ed682c219739cd3aba/docs/dtc_l1/iscas2027/service_closure_174_v1/CLOSURE_REQUIREMENTS_V1.tsv)
- [本次checkpoint](https://github.com/swayhrl/accel-sim-framework/tree/cec06d1a0c7ea59101c081ed682c219739cd3aba/docs/dtc_l1/iscas2027/service_closure_174_v1/review_pack/checkpoint_20261016T1404Z)：SUMMARY.json、REGISTERED_R2_STATE.tsv、a58df5fb-f532-467d-8bb6-f9e99d866a27.strict.json、ATAX_OO_COMPLETE_SCOPE_AUDIT.json。
- [Hotspot独立准入](https://github.com/swayhrl/accel-sim-framework/blob/cec06d1a0c7ea59101c081ed682c219739cd3aba/docs/dtc_l1/iscas2027/service_closure_174_v1/review_pack/hotspot_derived_admission_v1/ADMISSION.json)
- [Hotspot五臂完成](https://github.com/swayhrl/accel-sim-framework/blob/cec06d1a0c7ea59101c081ed682c219739cd3aba/docs/dtc_l1/iscas2027/service_closure_174_v1/review_pack/hotspot_derived_complete_v1/README.md)
- [B最终来源调查](https://github.com/swayhrl/accel-sim-framework/tree/d46cce269b88055decc2ca052dcb9baae0efee7e/docs/dtc_l1/review_packs/LEGACY_FORMAT_SOURCE_BINDING_V1)：README.md、BTREE_SOURCE_BINDING.md、2DCONVOLUTION_SOURCE_BINDING.md、LUD_SOURCE_BINDING.md。
- [V9](https://github.com/swayhrl/accel-sim-framework/blob/5c07e1913f63351b43abd533d87c1443039ed114/docs/dtc_l1/iscas2027/experiment_registry/2026-10-16_v1/MASTER_MATRIX_V9.md)

本文只新增独立协调文档，不修改Lane A/B执行分支、Core、配置、输入、launcher、报告或任何已有授权。
