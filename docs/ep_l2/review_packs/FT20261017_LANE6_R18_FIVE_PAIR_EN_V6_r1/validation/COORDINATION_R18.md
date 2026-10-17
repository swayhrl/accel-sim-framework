# EP-L2 / ISCAS2027 review_r18 — 五组正式接受：先完整论文接收，再定位结构压力的去向

2026-10-17，北京时间。协调者通过GitHub准确提交与实质结果文件核对，**只读科学解释及Lane6后续建议**。不修改Lane5 V2 scientific authority、不直接批准任何新增实验或Trace/硬件配置/资源合同调整、不启动已完成的Lane1/5/Storage-Ops窗口；避免把出版数据接收误认为现有性能结论显著。

## 0. 准确、最新权威
- Lane5 Framework HEAD `534338ed2219a3e719189c470414152987795fd8`，正式 `APPLICATION_ACCEPTANCE.json` **generation=8**，`revision=FT20261017_LANE5_A1_B1_FWT_7_21_ACCEPTED_r1`；共有10条新 `CURRENT_ACCEPTED`（五完整配对），保留10条历史（6 `SUSPENDED...`、4 `NOT_RUN...`）。原10h Goal已完成，无该Lane活跃进程/lease。未来任何消费必须重新fetch Live V2，不能静态认定gen8永不撤回。
- 完整原始群组 `docs/ep_l2/review_packs/FT20261017_LANE5_R0_1_A1_B1_PRIMARY_COHORT_r1/`，发布提交 `e6714dadb6cd5deb45185939a1bb3a2c488892c3`，终态提交 `534338ed...`，含`PAIRED_RESULTS.csv`、`RESOURCE_MOVEMENT.csv`、`SUMMARY.json`、完整原始日志引用和非原子SASS语义/全trace核验。
- Lane6 Framework HEAD `62e0972863aab5ba2e391e6d6dcfe221d7ab80ae`，`FT20261017_LANE6_R17_SAD_INTAKE_r1`：截至此版仅**SAD一组完成独立论文侧native intake**；其他四组的`next_adapters/*.json`为`PREPARED_METADATA_ONLY_NOT_INGESTED`。其报告已识别官方5/5而不自动升格为Lane6的数值接受，做法正确。
- 所有十条同Core `7b8e6ac70b8fe0f1bd37efca11acb5284938825d`、Framework `9bd17f9db3e8cbbc3fdad7283d1e292918546fd5`、binary `23094a9d6d6bc5edc4afae4dfc1c5ef0fb3b5d45fbfe56ffb4a33db46c597dee`，固定 `B16_BANKED` vs `U_WB16` ，1024 Tags/1168 payload slots/4 banks。当前V2认证范围仅`FULL_NATIVE_NONATOMIC...`、32B symbolic sector version、request/WB/lifecycle/64-slice，**不含数值SASS输出正确性或真实RTL PPA**。

## 1. 科学上必须保留的真实五对

| 完整工作负载 | B16 cycles | U-WB16 cycles | U相对B周期降低百分比 | B/U |
|---|---:|---:|---:|---:|
| sad | 110773 | 110749 | +0.0216659294% | 1.0002167062 |
| vectorAdd_4M | 73696 | 73549 | +0.1994680851% | 1.0019986676 |
| cfd_097k | 79093 | 79262 | **-0.2136725121%** | 0.9978678307 |
| convolutionSeparable | 292932 | 291525 | +0.4803162509% | 1.0048263442 |
| FWT_7_21 | 493189 | 491662 | +0.3096176111% | 1.0031057922 |

五组完整后Lane5算B16/U-WB16 **geomean `1.0016002037656606x`（约+0.160%）**。四正一负，**很弱/near-neutral**；不说统计显著、不说普遍GPU优化成功、不剔除CFD/SAD，不用旧SUSPENDED加速比。此数是五开发负载，不代表holdout/AI负载。

## 2. 结构/服务/下游共同审查表（各字段为原官方资源观测，不宣称已独立定位因果）

| workload | B16 WBUF-full | U WBUF-full | B16 copy lines | U copy lines | B16 bank wait (累计) | U bank wait (累计) | B16 L2→DRAM full-block events | U L2→DRAM full-block events |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| sad | 0 | 0 | 3975 | 0 | 2255 | 2233 | 0 | 0 |
| vectorAdd_4M | 440161 | 0 | 100568 | 0 | 445678 | 367415 | 1103500 | 1763609 |
| cfd_097k | 5 | 0 | 31123 | 0 | 102546 | 91029 | 0 | 0 |
| convolutionSeparable | 845097 | 0 | 546865 | 0 | 1122211 | 935249 | 218465 | 1131759 |
| FWT_7_21 | 890294 | 0 | 178569 | 0 | 405349 | 316103 | 12779 | 967911 |

- B16的copy总数被U全部消除、bank wait计数普遍降低；但主任务gain仅0.16%，且CFD变慢，说明不能把逻辑bank/copy减少线性折算为cycles。WBUF-full event可能是反复同frontend head的阻塞尝试，不是唯一事务/排队时间，更不等于节省的全局cycle数。
- vectorAdd/Convolution/FWT发生非常多的B16 WBUF-full，U为0；U进一步出现capacity_above_C16_observed与resident借用；这**表明静态quota在B16确实可能是绑定条件**、U发生真实借用，但**不能仅凭counter证明动态弹性独立改善了IPC**。
- 同三工作负载的L2→DRAM full-block events随U显著提高，Convolution 218465→1131759，FWT 12779→967911；意味着可能出现**压力向下游迁移**。由于事件按slice/尝试累计并存在重叠，必须结合真正下层排队/DRAM服务、全局cycle及交互实验确认因果，不可以简单从阻塞差中扣减gpu cycles。
- SAD缺容量压力且几乎持平，是预定义negative control；CFD的U-B周期恶化，尽管copy/Bank wait降低，需保留WAD-hazard B9841/U13400、实际WB 31123/31063、DRAM流量和run identity作为反例分析。

## 3. Lane6立即值得启动的**一次**有界工作（不启动任何新GPU simulation）

1. 在已有原Lane6窗口**新的短Goal**中读取最新Lane5 HEAD、V2账本generation及最终群组pack，不依赖第一次SAD使用的旧gen7/历史快照。读已有原Lane6 R17 `INCREMENTAL_INTAKE.md`及四个`next_adapters`，逐一执行existing原生V2/native intake+内容hash/64-slice parser/symbolic proof/当前撤回检查；每组独立新目录、新精确回执，不覆盖SAD，异常FAIL-CLOSED。需要时只修证据包装/解释层，不默默改trace。只在**全部5个Lane6独立PASS**后采用当下Live V2计算/复核geomean与图。
2. 形成完整`PAPER_CURRENT_FIVE_PAIR_INTAKE`的B/U paired cycles, instructions, resource movement、负对照及CFD退化；独立重算官方geomean；在图里不画人为baseline+宏大speedup，更不隐藏<1的CFD。区分figure2的performance（比例或准确差值）与completed copy/bank工作量。
3. 在EN-v5基础上修订**真实结果驱动**的EN-v6：更新过期状态，把真正的5组图和简洁表/归因代替此前`MEASUREMENTS PENDING`面板。abstract不要宣称明显性能加速/能耗优势；应如实描述固定容量下copy去除、near-neutral平均、B16 WBUF-full与U下游队列影响。PPA/相应静态预算/strong-static对照尚未执行，必须保留明确边界。
4. 针对Fig3出**可执行的下一步有限诊断方案**（非授权实验）：优先以Convolution和FWT作为存在显著WBUF-full及下游迁移的代表，用冻结同binary、同trace的B/U分别在原配置与**单一受控、可解释的下游headroom变化**做2×2交互；headroom变更需先核查确切物理资源/队列范围、公平和模型语义，由用户单独批准才能启动。对照静态`1024/112/32`也需另行实现和科学资格，不可把总payload变成1184或直接用WBUF8冒充。
5. 输出**科研决策**：在当前5组结果下，WB-only作为“应用加速机制”的价值尚未建立；若后续交互实验仍不产生可观收益，需要审慎考虑收窄论文主张或把TVD/RO增量作为独立机制评估，而不是造更有利的输入/故意调参寻求加速。维持4技术+1参考排版，原en-v5、R17 SAD完整保留；不编造RTL/STA/area/power。
6. 工作结束后出版新目录和精确STATUS/RECEIPT，push+remote readback；没有持续watcher/第二结果源。Lane1/5/2/3/4/双Storage-Ops不为这个论文接收重启。

## 4. 必须尊重的限制

- 允许：既有5对完整样本的只读科学分析、一次native intake、论文/图/结果布局、非执行性的下一实验设计。
- 不允许：无新合同地扩大阵列/改变工作负载、默认开启TVD/RO/Ideal、清理先前撤回证据、跳过source/atomic scope、用C1旧1024 resident-free下溢口径报告容量收益、使用未验证的零填充值、新建长期sim、假设数值SASS正确性。
- **结果关键判断：** 不是“5/5已经结束所以论文可以投”，而是已获得足够可靠的五组数据来证明目前提议的WB-only性能主张很弱；下一阶段应重点定位阻塞资源是否从L2数据池移向下游服务。
