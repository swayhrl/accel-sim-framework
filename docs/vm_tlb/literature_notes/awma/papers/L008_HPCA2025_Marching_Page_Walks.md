# L008｜Marching Page Walks（MPW）全文核查

Jiwon Lee等，HPCA 2025，DOI 10.1109/HPCA61900.2025.00123。

## 来源与阅读深度

2026-09-26收到用户提供的IEEE会议版PDF（16页，印刷页1662–1677）。已读正文I–VII、讨论和实验；核查Fig.6–12、Table I/II、Fig.18–23等页面。不是代码复现，不是独立重测。此前Round 01/02只读摘要的状态留在旧笔记和Git历史中。

来源定位一律区分PDF页与印刷页。本文L4是页表根、L1是叶；它们不是L1/L2 TLB。与LATPC的层级命名比较时先按root/leaf对齐。

## 1. 作者解决什么，而不是标题能让人误会什么

原设计每个walker一次推进一个walk。排队请求很多时，增加walker能降低等待，但跟踪在途访存的CAM大小、端口和搜索代价也增长。MPW让一个walker处理同一页表层级的多项请求，连续发出多笔读请求以重叠访存。它的主要效果是降低排队，不是让每个PTE读取更快，也不是把不同VPN当作同一翻译。（II-B/C、III、IV）

已有能力被保留：TLB请求合并、L2 TLB、PWC、并发walker属于论文基线（VI，PDF13）。Neighborhood对照在此论文的32B sector模型中，一次返回至多覆盖四个8B PTE；这个限制属于本文适配条件，不是所有Neighborhood实现永远只能合并四项。

## 2. 具体机制与真实边界

1. 256项PWQ在默认实现中分给32个walker，每份8项；请求round-robin分配。baseline也采用per-walker queue，不能把分队列本身全部算成MPW相对baseline的新收益。（V-A/Table I）
2. walker空闲时先按FCFS选一项，然后扫描其分区，纳入目标页表层级相同且没有被处理的请求。默认最多8项，不跨其他分区，不要求同VPN、同PTE sector或同叶级页表页。（IV-A/B）
3. PWQ新增PFN、sector offset、PL、W；WST保存walker状态、层级和请求bit vector。walker连续发出读请求，而非一周期内免费产生无限请求。（IV-C）
4. 每个返回可以更新其部分翻译；最终叶级结果可逐项完成。但walker须等当前batch的所有请求结束才空闲并组新batch，存在慢请求拖延下一批的风险。（IV-C、V-C）
5. 每walker计数Bloom filter过滤返回时无关队列的CAM搜索。默认128项、3bit counter，假阳性意味着额外精确搜索，不是错误翻译。（IV-D）
6. shootdown刷新相关PWQ/WST；不应把“页表读取是读操作”概括成无需处理映射变动。（IV-E）

## 3. 配置、数据与分母

主模型是Accel-Sim RTX2060-like：30SM、1365MHz，4KB页；L1 TLB32项/20cycle/4banks/32MSHR，L2 TLB1024项/80cycle/4banks/256MSHR；32walkers，合计256PWQ项；L1数据cache64KB/28cycle，L2数据cache3MB/160cycle；32B sector。（Table I，PDF10/印刷1671）

Table II的12个workload已经逐行入empirical/ROUND03_DATA.json，保留原文MB单位、footprint与walker requirement。没有从footprint反推矩阵或图输入形状，也没有估读未标注的性能柱高。

关键实验必须拆开：
- II-B增加walker的动机扫描假设零延迟CAM；Table II的walker requirement是作者特定模型下的峰值需求，不能作为芯片配置真值。
- II-C的CAM成本是45nm综合加跨节点缩放/端口估算，非12nm GPU完整实测。
- RTX3090 BIC是真机页大小动机实验，256–640MB，driver515.65.01/CUDA11.7；两次launch测第二次以排除迁移时间。并未实际改变GPU walker数量，曲线只支持作者对有限吞吐的推断。（II-B/Fig.3）
- 2MB页实验同时选用3.1–6.7GB输入，不能与4KB Table II当作只改页大小的同源比较。每点具体新footprint未给齐。（V-D）
- V-E另测L1访问不先翻译的路径；Fig.19共同分母仍是先翻译再L1的原baseline，不能直接把每根柱高当成该新baseline下的机制增量。

## 4. 正文明确报告的观察

主模型：MPW平均性能改善55.6%，Neighborhood16.6%；PTW排队延迟下降86.7%，完整PTW延迟下降62.4%。这三类分母不同，且不是LLM端到端结果。（V-B/C）

BH的PWQ请求以突发产生，ST更连续且有低占用时段；更宽地址范围的同层batch对BH更有用。图8每5000cycle采样，不能当逐周期完整burst分布。（III-A/B，Fig.8/9）

主机制平均batch约3.1，Neighborhood约1.5；动机里的全范围batched-PTW平均吞吐3.90×不能替代最终MPW的3.1。（III-A对比V-B）

batch拖尾影响9.7%的walk，使这些walk排队延迟增加27.0%，作者报告对MPW性能损失1.6%；不是“零等待代价”。额外2cycle组批诊断性能损失0.06%。（V-C）

L1不先翻译的实验平均L1数据命中21.2%，walk请求下降18.3%。这是作者样本下的过滤效果，不是AWMA或所有现代GPU的固定比例。（V-E）

## 5. 硬件/实现尚未独立核实的点

额外状态3088B=1504B PWQ字段+48B WST+1536B Bloom；CACTI报告0.473mm²与6.6mW。保留工具与缩放条件，不能当实测芯片代价。

3bit计数器作者称对所测workload足够；8项可能同hash时的溢出协议未完整披露。全结构实现若复现需明确饱和/溢出与无假阴性处理，不能从正文缺失就断言作者代码错误。

“多笔请求back-to-back”不等于无限发射带宽；具体每cycle发射与返回端口的完整实现需代码核对。本文未独立获得或运行代码。

## 6. 与AWMA的关系：审阅者判断

AWMA已接受结果32854024…主要暴露hit-dominated L1 lookup时序，而MPW针对last-level TLB miss之后的排队。这不是当前四点的直接修复方案；walk少也不能仅靠总数排除局部burst，需实际队列等待和关键路径证据。

最值得迁移的是观察方式：同一时间窗的不同页数、页表层级、地址覆盖范围、入队突发、active/queued比例、真正服务时间。它们是问题选择维度，不是新机制。

不能仅把本文的“同层并发”改成“AI感知batch”便宣称新颖。更宽范围/更多并发也不是无成本；需要证明既有batch之后仍有何种限制。

## 可用于Related Work / 不可写

可写：MPW以有限分区队列和同页表层级组批提高单walker在途访存并发，降低其所测GPU负载的walk排队，Bloom filter减少返回匹配的搜索成本。

不可写：MPW证明所有AI程序缺少walker；其55.6%适用于当前AWMA；本文的32walker就是RTX2060公开真实配置；所有实现均可免费同时返回8个请求。
