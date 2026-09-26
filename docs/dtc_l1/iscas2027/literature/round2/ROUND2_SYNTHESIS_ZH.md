# 第二轮：四份全文补齐后的机制对照与论文建议

日期：2026-09-26。输入为用户上传的四份PDF，合计46页。本轮不扩展公共网页调研，参考文献仅登记为线索；不执行代码/模拟器实验。DTC一列使用[已记录的项目设计基础](../PROJECT_COMPARISON_BASIS.md)，并非本轮重新审RTL。

## 1. 本轮真正完成什么

DL-MSHR、MiCache从仅书目信息升级为正文及关键图表核读；CCWS从首页升级为正文核读；ICS2015 Decoupled L1D补齐完整论述。详细笔记见[P11](P11_DL_MSHR_FULLTEXT_ZH.md)、[P12](P12_MICACHE_FULLTEXT_ZH.md)、[P10](P10_CCWS_FULLTEXT_ZH.md)、[P03](P03_DECOUPLED_L1D_FULLTEXT_ZH.md)。

此前“取不到全文”的缺口关闭，但**全文读完不等于代码行为、严格正确性或全球首次性已证明**。对原文未完整描述的瞬态规则仍保留未知，不用猜测填表。

## 2. 四篇到底优化什么

| 工作 | 核心受控资源/事件 | 不能简化成 |
|---|---|---|
| DL-MSHR | 固定entry/slot绑定变成可动态链接slot-set；平衡独立地址数与同址消费者数 | 只是扩大MSHR、只是旁路、没有动态回收 |
| MiCache | cache data与miss子项复用同一entry空间；双流水线；stash处理冲突/溢出 | 完全没有MSHR、纯共享容量带来的全部性能、只有FPGA所以不相关 |
| Decoupled L1D | 用扩大的Tag历史、RC和Position决定数据是否进入L1 | GPU Tag/Data仍然一一紧耦合、RC就是未完成消费者计数 |
| CCWS | 历史Tag检测lost locality，用分数控制load发射资格 | 通用DRAM cap、驱逐warp上下文、固定流上击败Belady |

## 3. 与DTC的生命周期对照〔我们的综合推断〕

| 事件 | DL-MSHR | MiCache | Decoupled L1D | 当前DTC设计基础 |
|---|---|---|---|---|
| 新地址到达 | cache miss后创建head set | 候选位置形成MSHR entry，可覆盖cache entry或把旧MSHR迁stash | Tag miss登记历史并旁路，不立即分配data | 分配/关联逻辑Tag、物理数据行和PIB等待元数据 |
| 同址请求在响应前到达 | 追加tail slot或链接set | 追加子项；满时分出旧stash记录与新BRAM记录 | 已绑定data位置时保留常规hit-pending语义 | 对仍可见的Tag登记依赖/消费者，不需要独立传统MSHR查找 |
| 旧记录失去新请求匹配资格 | 非head set不参与地址比较，仍属于同一head链 | **f=1 stash不参与PEreq匹配，但仍被MEMresp匹配** | 正文未给全套已绑定/未完成Tag替换规则 | Tag失效不等于物理行立即释放；旧消费者继续持有引用 |
| 返回如何找到消费者 | 地址匹配super-entry，再遍历已登记slot | hash+stash查找，可同tag多匹配；response generator读子项 | cached/bypass两条返回路径 | 由既有物理行/依赖归属路由，具体以项目接受实现为准 |
| 回收什么 | 数据返回/转发后拆链回收等待slot；cache数据可继续驻留 | BRAM MSHR转为cache entry，stash记录失效 | 数据替换与Tag历史分别管理 | IO按顺序管理；OO结合Tag可见性与现有引用决定物理行释放 |

**不能跳过的重叠：** MiCache已经将新请求搜索资格与仍需服务旧请求的状态保留区分开；DL-MSHR已弹性组织并回收消费者slot。因此，DTC不能只以“保留旧状态”或“动态分配”四个字建立新颖性。

**仍可准确比较的区别：** MiCache保留的主要是等待者记录并以cache/MSHR模式共享payload空间；DTC讨论的是可搜索映射之外的物理数据行保留及PIB/指令依赖组织。区别应由逐事件数据归属和释放条件说明，不由名称不同或平台不同推出。这个判断是技术定位，不是当前已证明比前人更好。

## 4. 对当前论文的直接修改

### 架构定位

把“首次分离Tag/Data、移除MSHR限制”改成：在既有DTC设计基础上，明确分开查询映射、等待指令信息和物理行生命周期，并说明如何承接未完成访问。列出前人已经分离/复用哪些状态，以及DTC具体改变的关联关系。

“无独立传统MSHR”后必须立即说明地址匹配、未完成响应、消费者归属和回收状态放在哪里。PIB不预留完整返回向量可作为具体实现事实，但不能把全部等待信息的成本删掉。

### 相关工作

最直接的结构对照应包含Decoupled L1D、DL-MSHR、MiCache；调度对照用CCWS及上一轮已读的代表。NuRAPID/V-Way说明基础思想已有历史。不要把所有前人合称“修改策略但不修改结构”。

### 实验解释

现有资源干预保持冻结。新文献不自动使已通过的结果失效，也不自动授权复现矩阵。当前证据可以支持DTC在本平台上的收益及限制，不能支持“数值优于所有这些方案”或“解决问题的唯一架构”。没有同平台同预算对照就不写该类胜负句。

### 硬件成本

至少分列数据SRAM、Tag/映射、PIB/等待状态、引用/依赖、返回更新、选择/仲裁及端口；报告分母和实现工具。参考论文自己的面积数也常有范围限制，不能直接当作我们的预算。

## 5. 四个数字/方法风险已记录

1. DL-MSHR的组合26.3%在引言与正文参照对象表述不同；引用正文时明确相对baseline，不自行包装成相对MRPB额外收益。[P11 §6]
2. MiCache四bank相近BRAM的1.15×平均排除了更差点，不能当总体平均；1.56×摘要与1.50×正文分组也不能强行统一。[P12 §7]
3. CCWS的24%是HCS+MCS调和平均，非十二程序GM；Belady只有cache统计、访问流取决于scheduler。[P10 §5–6]
4. Decoupled L1D的30.3%是七个CNF子集GM，不是十八程序总GM；所有论文的同名workload都不能直接当本项目exact input。[P03 §6]

## 6. 更值得保留的启发，而非立即开实验

**资源池要同时说明“总量”和“分配形状”。** DL-MSHR显示同样总slot数可因每地址分配不同而表现不同；MiCache显示最高MSHR数量充足仍可能受每地址子项数/流水线限制。DTC不能仅以物理行/PIB峰值说明所有输入都不阻塞。

**保留资格和搜索资格可以不一致，但其目的不同。** MiCache的f位是有用对照；将DTC状态按“新查询可见、响应待回、已有消费者未读完、可回收”解释有助于准确写架构。不过这是解释方法，不是本轮新提出的机制。

**吞吐、存储弹性和访问流改善要分开归因。** MiCache包含双流水线和hash改变；CCWS改变访问流。当前DTC也应区分结构、资源规模、执行顺序和下游服务敏感性，不把配置整体收益全称为单一原因。

## 7. 下一轮只保留几个有明确依据的阅读问题

- Farkas/Jouppi1994 *Complexity/Performance Tradeoffs with Non-Blocking Loads*：MiCache明确承认的in-cache MSHR先例。仅引用线索，尚未核原文。
- ICS2016 *Tag-split cache for efficient GPGPU cache utilization*：DL-MSHR引用[17]，可能直接邻近Tag组织；本轮不依据标题猜机制。
- FPGA2019 *Stop Crying Over Your Cache Miss Rate*：MiCache的直接baseline，需理解数千miss处理与子项池。
- 若要作实现级排他比较，再核MiCache源码的overflow/双流水线并发、Decoupled L1D的瞬态Tag替换规则，以及DTC接受实现对应规则。只读代码不等于自动新增仿真。

无需再向用户索取本轮四篇，也不继续把它们记成未取得。下一轮阅读完成前仍不声称相关工作查全。
