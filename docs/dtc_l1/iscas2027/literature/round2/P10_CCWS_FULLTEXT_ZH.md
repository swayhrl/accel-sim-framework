# P10｜Cache-Conscious Wavefront Scheduling

Timothy G. Rogers、Mike O'Connor、Tor M. Aamodt；MICRO2012，pp.72–83；DOI：10.1109/MICRO.2012.16。

**阅读记录。** 2026-09-26，用户上传12页PDF。正文§1–7、LLD/VTA/LLS、方法和主要结果已核读，图5/6、表1–3及Belady比较对照页面图像。版本见[来源表](UPLOADED_SOURCE_MANIFEST.tsv)。不再是上一轮仅首页状态，未做实现复现。

## 1. 真正的研究问题

**原文：§1–3。** 更多wavefront可隐藏延迟，也可能用更多访问破坏正在运行wavefront的重用。作者区分intra-wavefront与inter-wavefront局部性，并在所测高缓存敏感负载中强调前者。改变调度可改变引用间隔，而替换策略只能在既定到达顺序下选择驱逐对象。

CCWS要动态决定**哪些wavefront可以向存储系统发load，以及同时允许多少个**，不是只找一个全局内存请求队列的最佳大小。

## 2. 反馈信息从哪里来

**原文：§3.3.3，图5，PDF4页/印刷75页。** L1 miss分配/预留行时记录wavefront ID。该行被驱逐时，Tag存入原wavefront所属的VTA区域。后续该wavefront在L1 miss且自己的VTA命中，就报告lost locality。

VTA只保存历史Tag，不存cache data；VTA命中不提供数据，也不是对未完成miss的合并。它提供“本wavefront曾经使用、后来被驱逐”的信息，不能把它写成精确计算如果独占L1就必然命中的oracle。

## 3. 如何改变发射

**原文：§3.3.2–3.3.5，PDF4–5页。** 每个wavefront有lost-locality score(LLS)。VTA命中将其分数提升至LLDS；之后逐cycle衰减至base score。排序/前缀累计与cutoff产生Can Issue位图，限制低优先局部性wavefront的**load发射**；再与既有GTO等就绪/优先规则求交。

关键公式：

`LLDS = (VTAHitsTotal / InstIssuedTotal) × K_THROTTLE × CumLLSCutoff`

`CumLLSCutoff = NumActiveWaves × BaseLocalityScore`

这里NumActiveWaves是分配到core的上下文数量，与当下被允许发load的数量不同。CCWS不是把被限流warp的寄存器/CTA上下文驱逐，也不是所有非load指令一律禁止，更不等于DTC的GPU-wide lower-outstanding credit cap。

作者说明分数逻辑可流水化、不必每个core cycle重算；这不能替代实际目标RTL的时序证明。

## 4. SWL与适应性

**原文：§3.2、§5.1、§5.6。** SWL在kernel launch指定活动发射wavefront上限；Best-SWL扫1–32后每程序选最佳，属于oracle/profiling对照。SWL还讨论barrier处理：让同workgroup的其余wavefront追上barrier后继续限制。

CCWS靠反馈适应，而K_THROTTLE是选定的常量，默认8，base score100，VTA每wavefront16项、8-way（全core512项）。自适应的是运行中的发射许可，不是论文完全没有调参。高缓存敏感主测试不含kernel内workgroup/global同步；不能从该结果推广出所有同步程序的无饥饿/前进性证明。

## 5. “超过Belady最优”到底是什么意思

**原文：§4、§5.1，PDF5–7页。** GPGPU-Sim3.1.0负责时序性能；另一个SAGCS工具对各scheduler产生的cache访问trace应用LRU/Belady，只给cache miss/MPKI，不给Belady IPC。

CCWS+LRU可以比GTO流+Belady或LRR流+Belady有更少miss，原因是**访问流已经不同**。这不违反固定流上的最优替换，也不能写成CCWS在同一固定请求流上击败Belady，更不能声称测得“比Belady快24%”。

这对DTC很有用：固定trace payload不代表所有结构产生相同的跨warp到达/合并/缓存流，方法部分必须说明模拟中哪些顺序仍由调度决定。

## 6. 实验与数字范围

**原文：表1/2、§4–5。** 30 compute units，L1每core32KB/8way/128B，8个memory channels，core/interconnect/memory为1300/650/800MHz。十二程序分为4个HCS、4个MCS、4个CI；包括MEMC与GC等GPU-enabled server负载。KMN为较大输入修改了存储空间选择。作者声明全程运行，14M–1B指令；BFS另扫图规模。

性能主要比较LRR、GTO、调优2LVL-GTO、Best-SWL和CCWS。正文§5.1报告：HCS相对GTO的**调和平均**提升63%；HCS+MCS合并调和平均提升24%。CI另作稳健性验证。不能把24%写成十二程序的几何平均，更不能和DTC的GM直接相减。

## 7. 硬件开销的实际覆盖范围

**原文：§5.7，PDF9页/印刷80页。** CACTI5.3估算VTA，55nm下每core0.026mm²，全30core0.78mm²，对比参考芯片约0.17%。紧接着作者说明没有计入一些难量化的小开销：每L1行WID、32个10-bit分数、counter、heap及评分逻辑等。

因此0.17%是主要VTA估算，不是完整控制器经综合/物理实现的全成本。不能拿这个数字作为DTC面积设计的直接预算，更不能照搬“其余逻辑可忽略”来跳过自己的DC评估。

## 8. 与DTC的关系〔比较推断〕

CCWS改变请求何时由哪个wavefront进入；DTC改变接纳后的Tag、等待指令和物理数据行组织。控制位置和状态确实不同，但不自动证明性能正交或可直接叠加。

它已明确说明并发、局部性和隐藏延迟的权衡，所以DTC的限流正反向实验应解释本结构适用性，而非首次发现“并发越大不一定越快”。若以后提出自适应DTC控制，必须比较输入信号、控制对象、反馈时标及资源成本，而不是只把wavefront上限改名为cap。
