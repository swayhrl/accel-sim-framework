# Lane O V1R2 路径资格与不干扰验证矩阵

这是设计矩阵，不是已完成NI的声明。本轮新Core、ELF、CPU fixture、应用OFF/ON均不存在，统一为NOT_PREPARED/NOT_QUALIFIED。旧Source78的Vector事件observer NI可引用为旧实现证据，不能转移给待写的新统计模块。

| 路径 | 已有可复用语义/数据 | 必需CPU控制设计 | 未来应用验证范围与当前状态 |
|---|---|---|---|
| ingress/sector/ROP/queue/head | Source78真实push、split及head源位置；旧MS/LIFE人口明确 | 父子闭合、texture/ROP双路、head长阻塞时后继先到、同tick多sector、UID重试与尾部退出 | 若实现入口hook，S/F实际启用者各列覆盖；当前没有新NI |
| S dirty WB/WAD/Bank | 48个参考端点的mandatory计数、copy与WB完成闭合 | sequential same-line WB、并行WB、lower-accept与set_done分离、retry/unknown、clock无memcpy偏移 | 优先Scan或Conv；需要同新ELF同输入/配置的S OFF/ON或Main接受的明确已有资格，当前未完成 |
| V retained age/service | 当前F/WV实际response commit及generation/reclaim语义 | clean/staged/inflight/complete、首次服务/未服务回收、bank/response背压、censor | 合法WV FWT或正V F端点覆盖；S配对不覆盖此路径。若本批不采则N/A，不继承S PASS |
| RO merge/ready/retire | 现有RO事务闭合、Vector合并与sector协议 | 未ready/部分ready/ready-only drain、未准入入口重访、同址多transaction、descriptor背压、最后waiter退休 | 合格F Conv/Vector6M；候选Source重新证明证书绑定和开关，当前未完成 |
| T structural联合 | 原strict detach保护与已接受237/1,141/27实际事件 | T-OFF下structural仍可非零、firstNEW后才ever-full、generation/pin/reuse保护、无eligible的负例、实际漏斗与总等待分开 | 仅采合法F。默认几何与已有缩容点不混合资格；构造正例不等于真实应用收益，当前未完成 |
| 状态/输出上限 | 固定数组和compact输出方案 | sizeof/容器上界、所有桶满值、最大kernel数、溢出/删失、实际序列化字节 | 每个启用schema都要检查；既有旧格式上限不继承 |

## 应用NI登记规则

Main选择Source基点和本批实际启用路径后，在上表填写精确fixture结果、已有应用NI的范围、剩余OFF/ON点。旧ELF端点不能直接充当新ELF OFF。CPU证明可以减少重复模型控制，但不能把未覆盖的F/WV hook称作已经验证。

每个应用配对须同Source/ELF、完整输入、硬件/队列/时钟、模式/证书和输出人口，只差被动observer开关。比较cycles、instructions/CTA/kernel、原有完整协议/请求完成投影、已存在的有序闭合摘要与真实流量。新增观测字段本身当然不要求OFF与ON相等。若既有工具没有全请求顺序证据，不能仅凭相同总量声称所有请求顺序已经逐条验证；用CPU路径证明与已存在的有界有序摘要说明其范围，不为NI另造海量日志。

host wall/RSS/新增输出按实测报告，至少覆盖本批实际使用的路径；一次Vector开销不能充当全负载≤5%的证明。≤5%只作候选目标；若超标先减少可选shadow/分层，不改实际仿真时序。

## 计数而非预分配启动

四个候选输入是问题覆盖集，不是四次启动承诺。先复用PILOT_GAPS中的现有统计，然后定义本批确有缺口的ON点与缺失的OFF控制，计算`N_ON + N_missing_OFF`。V1R1“4 ON加1 OFF足够”的假定撤销；若资格在暂定范围内无法闭合，缩小指标/模式或另报精确控制。当前新完整仿真授权为0；本文不增加预算、不修改Main既有规格。
