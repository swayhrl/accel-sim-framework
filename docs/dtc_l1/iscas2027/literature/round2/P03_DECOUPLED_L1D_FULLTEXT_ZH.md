# P03｜Locality-Driven Dynamic GPU Cache Bypassing

Chao Li、Shuaiwen Leon Song、Hongwen Dai、Albert Sidelnik、Siva Kumar Sastry Hari、Huiyang Zhou；ICS2015；DOI：10.1145/2751205.2751237。

**阅读记录。** 2026-09-26，用户上传11页PDF，正文全部章节与关键设计/配置/结果图表核读。本文页码统一为PDF物理页码。版本见[来源表](UPLOADED_SOURCE_MANIFEST.tsv)。补充第一轮定向阅读，不把本论文的局部性类别转移为本项目的程序分类。

## 1. 作者的问题与贡献

**原文：§1、3。** GPU L1的访问流中存在无复用、低复用或长重引用间隔的数据；全部插入会污染缓存并争用资源，全部旁路又损失有用复用。本文把局部性过滤融入既有Tag查询，避免另设前置过滤器再查一次地址。

结构明确命名为Decoupled L1D：扩大Tag记录的覆盖范围、独立管理数据插入和替换，并用SM dueling使不适合过滤的负载走原策略。这是直接的GPU Tag/Data解耦先例。

## 2. 默认结构与字段

**原文：§4.1、表3，PDF5–6页。** Tag为32set×8way=256项，data为32set×4way=128行、每行128B。两者保持相同set数。Tag的RC为6-bit复用频次，Position为2-bit组内数据位置；另有status及原有字段。每个data set有Free Line计数。候选Tag可存在而没有data line。

**比较注意：** 它不是任意Tag映射到任意全局Data行的无限池；2-bit Position对应当前组内位置。RC不是“仍有几个消费者未读完”的live-reference counter，不决定DTC式旧消费者保护。

## 3. 逐事件动作

| 事件 | 原文动作 | 定位 |
|---|---|---|
| Tag probe miss | 建新Tag；若无空项按LFU选择RC最小者；返回bypass，不进入常规cache miss handler，不分配data line | §4.2，PDF5页 |
| Tag hit，Position无效 | RC加一，与locality threshold比较；不满足则继续旁路，满足则分配/替换data line | §4.2，PDF5–6页 |
| Tag hit，Position有效 | 按原L1进行cache hit或hit-pending处理 | §4.2，PDF6页 |
| data分配/驱逐 | 更新Position/Free Line相关状态，data按LRU等策略替换；相应RC及同组RC做重置/aging | §4.1–4.2 |
| bypass响应 | 经旁路填回路径直接送寄存器，而不是填预留L1数据行 | §2.2，PDF2–3页 |
| 常规miss响应 | 原基线路径填预留cache行并更新相应MSHR状态 | §2.2；§4.2保留hit-pending语义 |

文中新增的是bypass状态，仍保留hit、hit-pending、miss、reservation-failed。因此不能把它写成完全取消MSHR或不追踪任何未完成请求。

## 4. 本轮不能替原文补完的瞬态规则

原文清楚给出局部性过滤与两个存储的主要动作，但没有完整列出所有已绑定/未完成Tag被选为victim时的逐状态排除、反向定位和在途响应更新合同。图7也不是完整的一致性状态机。

因此，对“这个设计能否在Tag被替换后继续保护旧物理行”不能凭简图下排他结论。可说其**正文重心是插入/局部性过滤，没有给出与DTC完全相同的生命周期机制**；不可说“源码绝对不支持”，因为本轮未核源码。这不是要求修补论文，而是我们比较的证据边界。

## 5. 适应性并非所有参数都在线学习

**原文：§4.3、§6.2、表3。** SM0/SM1分别采用新旧策略作dueling；默认500-cycle检查、10% miss-rate差阈值。RC局部性阈值取2，作者在§6.2明确没有实现逐workload在线阈值选择，而是依据所测负载选择该值。

因此可以说运行时切换/动态过滤，不能说阈值完全无需经验选择或所有配置在线优化。§4.3用threshold=0解释关闭RC检查；本文不擅自把这个描述转成未展示的cycle级状态迁移协议。

## 6. 实验与收益范围

**原文：§5、表1–3，PDF3/6–7页。** GPGPU-Sim3.2.2，generic Fermi-like 15SM，L1 16KB/4way，L2 768KB；18个工作负载，含14个Rodinia默认输入、MM/FFT、Lonestar的BH/SSSP，声明全部运行至结束。cache unfriendly/friendly/insensitive由该文bypass-all相对L1路径的表现划分，不是永久程序属性。

§6.1的几何平均30.3%、最高56.8%是**七个cache-unfriendly负载子集**上的比较，不是全部18程序GM。友好/不敏感负载另报。MRPB含重排和旁路；PDP-best按workload选最优静态PD；Profiled-BYPASS未计profiling成本。基线替换策略匹配，但Tag项数量和额外状态增加，不应简化为严格等面积。

§6.5以CACTI6.5估计开销，承认Tag probe额外1-cycle。没有DC流片级时序证据；面积段混有45nm估算与40nm产品参照，本轮不把该百分比换算成同工艺实测结论。

## 7. 对DTC的意义〔比较推断〕

应承认相同技术基础：GPU中Tag和Data可分离，指针连接，Tag可保存非驻留地址信息。应比较不同控制对象：本文决定数据值得缓存与否；DTC定义映射失效、旧消费者引用、返回和物理行回收。只有这些具体事件可支持技术区别。

这个对照不要求现在复现该方案，也不意味着DTC没有价值。它要求把“Tag/Data解耦”从笼统首创句改成准确的架构组织和生命周期描述，并明确DTC自身既有学位论文来源。
