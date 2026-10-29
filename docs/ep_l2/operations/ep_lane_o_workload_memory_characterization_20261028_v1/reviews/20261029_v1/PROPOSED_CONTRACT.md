# Lane O 审查后建议采用的采集合同

这是对V1R1的具体修订建议，不修改原候选或既有统计，不是仿真启动规格。

## 请求边界

每份汇总声明以下边界及物理clock域；新增字段不能复用旧字段名改变含义。

| 字段 | 定义 | 用途 |
|---|---|---|
| ingress_parent | subpartition真实push收到的父请求；进入sector拆分前 | 父子闭合与入站请求规模 |
| ingress_child | sector拆分后的真实子请求首次登记，ROP延迟之前 | 入口地址流、同址到达间隔、以入口定义的fill前重访 |
| queue_enter | 进入ICNT→L2队列，texture直入与ROP迁移分别计 | 入口排队时间，不能当first-head |
| first_head | 请求第一次成为L2可检查的FIFO head，不重复更新 | 参考资源需求、head间隔、Tag同Set满路机会 |
| admission | 实际生产访问/服务获得准入 | 与现有FT/MS完成统计对应 |
| ready / response_enqueue / retire | 指定sector ready、响应成功入队及事务最后waiter退休分别定义 | 区分fill前重访与ready-only drain，不合并为单个“完成” |

地址间隔必须带边界标签。未增加入口hook时，只输出head间隔，`ingress_gap`标NOT_COLLECTED。T联合机会仍以head、目标Set和实际preview为准；入口请求到来不等于已经要求分配Tag。

入口只在真实push/split hook记录一次；queue→head→重试不是新到达。父请求、子请求及128B地址去重分别保留；32B sector空间触达不当作同sector时间重用。同tick不同子请求在做recency时需要明确batch/tie规则。跨epoch且尚未退休的事务不得因表清空丢失；地址域随精确模型资格冻结。

## 请求类别与分母

最少分别记录：global demand read、global demand write、atomic、local/其它被纳入的demand类别、L1 writeback、内部write-allocate/lower/WB、texture/未支持类别。每一项的具体枚举以实现资格合同列出，不能只按`is_write()`把所有写流量叫作程序store。

比率输出同时包含 `numerator_class`、`denominator_class`、`boundary`、`dedup_key`、`observer/schema`、`resolved/unknown/censored`。没有同人口证明时只给原始计数和边界，不发布精确发生率。

旧MS first-block数据保留其原定义；FT unique_requesters保留其排除L1_WRBK的定义。R2的具体两端点优先查已有absorbed/请求类别投影：例外为零则记录证据再保留百分比；例外不明则论文保留16,791/3,736,508、390/215,979等独立数与重复数，暂不称0.32045%/0.000912%为精确demand受阻率。

## 正式补采前逐格填写的缺口表

每行键为 `input SHA × source/ELF × exact geometry/resources × mode × metric schema`，最少包含：

- existing accepted artifact和精确字段；当前可否直接解析；0、DISABLED、NOT_EMITTED、NOT_APPLICABLE、UNACCEPTED、IDENTITY_UNRESOLVED分开。
- 指标需要的边界与分母；缺的是投影、旧小包身份、计数器还是动态联合分布。
- 既定Main运行是否能自然携带；若无法复用，写明为何确需补采；保持未授权。
- 依赖的CPU正确性控制、Source/ELF资格及OFF/ON证据；最终实施由Main登记。

先对Scan、Conv、FWT、Vector6M填写，不为凑四个输入而重跑。历史Motivation/Streaming的CSV与manifest先按已有保存索引定向读取，不能以找不到文件为由全盘遍历或重扫Trace。

## 新增hook与不干扰验证矩阵

| 新增路径 | 可复用的证据 | 执行前待填项 |
|---|---|---|
| ingress/sector/ROP/head | 现有push/split/preview代码位置与父子协议 | 去重、同tick、队列背压、入口与head先后；具体新Source的控制结果 |
| S dirty WB/WAD/Bank | 已有mandatory计数与drain闭合 | 新时间戳/分类不增加probe、bank或调度；实际S OFF/ON范围 |
| V retained entry | 现有response commit、generation、reclaim语义 | 新年龄采集的clean/staged/inflight/complete及回收删失；若本批不采则N/A |
| RO merge/ready/retire | 已有RO闭合和sector协议 | 正ready/负ready、多个同址transaction、response背压；适用F OFF/ON资格 |
| T structural联合 | 现有preview与RO状态及严格guard | first-head/ever-full直接联合、policy OFF不归零structural；新增几何的资格 |

每条写出“已覆盖证据 / 未覆盖路径 / 不适用原因”。一个S应用配对不等于F新hook已验证；一次host开销数值不能作为全workload上限。可由已有精确资格、有限CPU控制和有针对性的应用配对共同闭合，无需强制所有workload各跑一对。

先确定本批实际启用路径，再由Main计算必需ON与缺失OFF控制数。若暂定最多5次不足，则缩小本批范围或另审查精确控制，不能默认增加启动数。未闭合之前，所有拟议完整仿真仍为0次授权。
