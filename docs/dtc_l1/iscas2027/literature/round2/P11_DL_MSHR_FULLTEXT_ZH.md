# P11｜Dynamically Linked MSHRs for Adaptive Miss Handling in GPUs

Yongbin Gu、Lizhong Chen；ICS2019，pp.510–521；DOI：10.1145/3330345.3330390。

**阅读记录。** 2026-09-26，依据用户上传12页PDF。正文§1–7已阅读，关键结构、配置和面积表已对照页面图像。全文版本哈希见[来源表](UPLOADED_SOURCE_MANIFEST.tsv)。以下“原文”指该版本，不混入后续论文介绍；“比较”是我们基于既有DTC定义的推断。未做代码复现。

## 1. 作者要解决什么问题

**原文：§2–3，PDF2–4页。** 固定MSHR有两种不同的不足：不同地址过多造成entry-full；同一未完成地址的消费者过多造成merge-full。前者可能在每个entry还有空slot时发生，后者可能在其他entry空闲时发生。因此，问题不仅是总状态不够，也可能是固定entry×slot分割不适合当前访问。

作者在SDK、Rodinia、Parboil中区分primary-miss-predominant与secondary-miss-predominant行为；另用GTX960上的三个微基准和Nsight memory-dependency stall作动机佐证。**作者自己说明不试图反推未公开MSHR细节；memory-dependency stall也不是直接读取某个硬件MSHR满事件。** 不应把动机实机测量当成DL-MSHR硬件已制造验证。

## 2. 创新点不是“多加一些MSHR”

**原文：§4.1、4.3，图6/7，PDF5–6页。** 把固定entry中的slot分成可独立分配的slot set。一个set可作为处理新地址的head，也可链接到已有地址的链尾，形成super-entry。各链不必等长；请求模式改变时，资源在“更多独立地址”和“更多同址消费者”之间调整。

图7示例把4×4的静态布局转成8个两slot的set：同样16个slot，可以组成不同数量、不同长度的链。**不要把示意图的“所有set可归一条链”当成最终无约束配置**：§4.6还引入head预留，作者最终将一半set保留为不能附着到其他链的head，以免一个地址耗尽所有资源。

DAU放在原Tag & Control与MSHR阵列之间，维持原接口。本文替换的是独立miss handling array，未将cache data阵列改成cache/MSHR共享存储，也未提出DTC式Tag失效后物理数据行的引用保留。

## 3. 按事件记录状态

| 事件 | 论文中的动作 | 定位 |
|---|---|---|
| 新地址miss | 比较各super-entry地址；未匹配且nFreeSet>0时取free set作为head，记录请求者、offset等并下发 | §4.4，PDF6页 |
| 同址secondary miss | 将请求放入尾set空slot；尾set满但全局有free set时再链接 | §4.4，PDF7页 |
| 全池耗尽 | 无法形成新head或扩展既有链的请求等待；动态组织不等于无限容量 | §4.4 |
| 返回/完成 | 数据返回并转发给请求者后拆链，清H/L/P等状态、增加nFreeSet；缓存数据本身可继续命中 | §4.4，PDF7页 |
| 写miss | slot的数据缓冲保存写数据；文中L2示例强调不能随意合并会破坏W/R顺序的写请求 | §2–3，PDF2–3页 |

控制状态包括H、L、P、S_free、S_full及nFreeSet。S_free/S_full可同时为0，表示部分使用，不应把它们当互为反相的一位状态。

## 4. 关键实现成本与优化

**原文：§4.5–4.6，PDF7–8页。** 四项优化是：两slot成组减少链接/比较器开销；非head比较器关闭；head中存tail指针避免逐链寻找；预留head set避免独占。分组越大链接成本越低，但自适应自由度下降。关闭比较器主要节约功耗，不意味着所有查找延迟随活动比较器数量等比例下降。

标准部件使用CACTI6.5；新增控制、状态及DAU用Verilog和Design Compiler/NanGate45nm评估。§6.3的MSHR规模对照令传统MSHR一律1-cycle，DL-MSHR为2-cycle；这是文中对照条件，不是宣称任意大真实CAM都能1-cycle。

## 5. 实验到底比什么

**原文：§5–6，表1–3，PDF8–11页。**

- GPGPU-Sim3.2.2，28SM，L1 16KB/4-way，8个128KB L2分区；L1每SM 32×8、L2每bank 32×4的传统MSHR；主要结果同时改L1和L2。
- 30个SDK/Rodinia/Parboil程序，声明全部运行到结束并保留访存coalescing。未给出逐项精确输入/二进制manifest，不能据程序同名做本项目exact workload对照。
- 对照包括原MSHR、两倍entry、两倍entry且两倍slot、同总slot数DL-MSHR、MRPB及DL-MSHR+MRPB。
- 总slot数相同不等于每一项电路成本相同：DL-MSHR增加地址比较器、链指针和DAU。论文另外报告面积/功耗，而非把“same slots”写成严格等面积。
- 还有关闭L1只改L2、调度器变化、大MSHR/理想查找延迟等对照。

§6.1报告DL-MSHR相对baseline的IPC几何平均提升19.2%；§6.2报告RF数量降低88.1%。§6.2明确指出RF下降与性能提升不成比例，不能从一个stall counter直接推出总体收益。

## 6. 数字引用必须保留的边界

**26.3%歧义。** PDF2页引言写成在MRPB之上“additional 26.3%”，但§6.1延续至PDF10页明确说DL-MSHR+MRPB相对Baseline为26.3%。笔记记录两处不一致；引用优先写成“正文报告组合相对baseline为26.3%”，不把它扩写成相对MRPB再乘1.263，也不静默修成另一数值。

**面积分母。** 表3的L1 non-MHA面积为0.11mm²，MHA从0.00386变为0.00449mm²。论文约0.6%的小幅面积增加是相对cache相关分母，不是说MSHR模块自己只增0.6%，更不是全GPU面积。按表值直接计算，MHA模块自身增幅约16.3%。L2也须区分non-MHA、MHA和全芯片分母。

**当前DTC不与19.2%直接排名。** 该文同时优化两级、程序集合/输入/平台/主性能统计都不同。我们的1.592×不能与其1.192×相除推导胜负。

## 7. 与DTC的关系〔比较推断，不是该文作者结论〕

最清楚的对照是：**DL-MSHR弹性组织“哪个地址拥有多少等待请求slot”；DTC把可搜索Tag、等待指令元数据和物理数据行生命周期分开。** 两者共同目标都是提高缺失处理效率，不能把前者归到“仍只有固定MSHR”的背景里。

不能写“DTC去掉MSHR，因此不需要等待状态”。应列出这些状态在Tag、PIB、依赖信息、引用计数和返回目的地中如何保存、如何定价。DL-MSHR并不直接证明与DTC可无成本叠加；若未来要比较，先做状态/端口/延迟预算，而不是自动启动复現。

## 8. 本文带出的后续阅读线索

参考文献[17]是ICS2016 *Tag-split cache for efficient GPGPU cache utilization*；[6]是ISCA1994 *Complexity/Performance Tradeoffs with Non-Blocking Loads*；[31]是MICRO2006 *Scalable Cache Miss Handling for High Memory-Level Parallelism*。本轮仅从引用表定位，未取得/审核这些原文，不能替它们填写机制细节。
