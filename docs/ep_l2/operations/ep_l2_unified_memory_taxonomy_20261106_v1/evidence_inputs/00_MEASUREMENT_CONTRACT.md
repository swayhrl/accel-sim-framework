# Lane O V1R2 访存特征计量合同

适用范围：新统计的设计和Main小汇总接口，不修改旧字段含义或既有验收。优先级高于Agent附录中的早期采集建议。默认关闭；本轮只有文档，未实现、编译、资格化或启动新模型。

## 四个请求边界

| 边界 | 精确含义 | 可回答的问题 |
|---|---|---|
| ingress_parent | subpartition真实push接收父请求，sector拆分前 | 原始包数、父子闭合；不是程序指令数 |
| ingress_child | 同次push内sector拆分后登记子请求，ROP之前 | 此入口需求流的地址间隔、入口定义的fill前重访 |
| queue_enter | 子请求实际进入ICNT→L2 FIFO；texture直入与ROP迁移均只记一次 | 入队到first-head的排队；不是ingress时间 |
| first_head | 子请求首次成为可检查的FIFO head | head地址间隔、实际资源需求、Tag联合机会 |
| admission | 实际生产路径接受该请求 | 准入、服务与现有FT计数闭合 |

Source78锚点：`l2cache.cc`的`memory_sub_partition::push()`（约2692行）、ROP迁移（1749行）、head检查（1351行）、FT实际准入（2811行）。具体新Source行号须由Main冻结，不能直接把旧行号当新接口资格。

**首批复用只报告已有边界。** MS/LIFE属于head域，ROV1 accepted计数属于已接受域，FT requester属于准入域。未增加真实入口hook时，`ingress_gap`和`ingress_before_ready`标NOT_COLLECTED；允许只完成head域采集，不承诺恢复完整入口流。不得读取或扫描FIFO来伪造逐请求入口时间。

每个边界只计一次。去重键是子请求UID及生命周期/代次；另存父UID、128B line、32B sector mask和请求类型。重试不更新arrival序号；sector拆分不是新程序指令。跨epoch仍live的对象保留origin，禁止通过清表使旧事务丢失或重复计数。同cycle多sector的recency先明确batch/tie规则。

## 请求类别与比率

每份输出固定一张类型枚举到类别的映射，至少分global demand read/write、atomic、local/其它已纳入demand、texture/模型限制类、L1 writeback、内部write-allocate/lower/WB、UNKNOWN。atomic优先分类；`is_write()`不是程序store的充分定义。任何尚未资格化的类型保持UNKNOWN，不混入已证明的RO分母。

每个比率携带：`numerator_class`、`denominator_class`、`boundary`、`dedup_key`、`eligibility`、分子/分母整数及观察状态。同边界、同类、同过滤和同完成范围均匹配才称发生率；静态证书line比例不充当动态request比例。

旧FT `unique_requesters`明确排除`L1_WRBK_ACC`，MS head原因计数不天然排除。Conv/Scan精确受阻率在V1R2撤回：保留16,791/3,736,508和390/215,979的distinct/observations。22份小JSON未找到absorbed投影，不能声称例外为零，也不声称已有除法算术错误。Main若已有请求类型投影可补证；没有就保留未知，不为此另扫raw/Trace或启动模型。

## M 重访与并发

分别输出`ingress_before_ready`、`head_before_ready`、`ready_only_drain`，不得互相替代。以到达时该请求所需sector是否已ready为判定；另列line任何sector pending的状态，避免部分fill被叫作整个line完成。live merge只证明事务仍存活，不直接给出before-ready比例。

新requester重入的分子与所有同类/同边界requester分母配对；“至少一次重入的事务比例”另以created transaction为分母。未被接受的请求也不能从入口到达人口静默删除，应另记最终接受/退出/尾部未完成。

`U_pending`为存在已issue但未ready sector的独立128B地址数；`U_live`为尚有未退休requester的独立地址数。normal、RO及两者地址并集分别计，不把transaction数当地址数，也不把各slice峰值相加当同时峰。用现有索引/有界refcount在事件处更新；不得周期扫描所有Tag/请求。表溢出显式使精确指标失效，不丢弃记录后继续声称exact。

## T 联合机会

T需求在first-head及后续实际preview拒绝时观察：同一UID、目标Set、同一clock时刻的`R==ways && structural_candidate_count>0`。同时保留首次NEW、ever-full unique、repeat checks、Tag拒绝ticks和总head→admission；这些不是同一个指标。

结构候选按当前协议中attached、generation/owner匹配、未受reuse保护、required-not-ready等必要条件冻结，**不包含T enable位**；policy允许、preview改写、实际relieve/detach和新请求commit另计。结构计数不授予生产detach权限，不放松原guard。S没有RO事务的运行时联合为N/A；正静态证书不是同时存在RO候选的证据。

## W V 与等待

W沿同一个WB token/generation记录reservation、copy read/write、lower accept、true set_done。S与pooled不存在的copy阶段标N/A，不能以两个不同born起点的均值作同一延迟比较。同址访问按R/W/A与WB阶段归类；旧MS是head域的条件观察，不是全部入口访问或单原因独占损失。

V区分128B line重复、首次访问新32B sector的空间延续、同sector时间重访。间隔、不同地址reuse distance、post-eviction首访年龄、实际V response commit分别命名；response/install/query均非可互换分母。先复用历史小CSV/manifest；有界抽样须记录采样率、hash/seed、碰撞、表回收、左/右删失，不能只对survivor外推全人口。

每原因MS等待保持首次blocked→首次known-clear；仅ANY项延伸至admission。新增累计拒绝ticks另命名，未知期间不能作为确定阻塞/非阻塞。原因重叠不能求和称GPU独占stall。

## 最小输出外壳

每条metric带完整输入内容SHA/ordered commandlist绑定、Source/ELF、精确几何/资源/模式、证书与地址域、observer/schema、边界/类型/clock、去重与采样、population status。状态为OBSERVED、DISABLED、NOT_EMITTED、NOT_APPLICABLE、UNACCEPTED、IDENTITY_UNRESOLVED、NOT_COLLECTED或UNKNOWN；OBSERVED且分母有效才能填写数值0。

时间使用真实CORE/L2/DRAM域，不加memcpy偏移或隐式换算。固定log2桶输出count/sum/max/overflow及censor；桶分位数只给区间。占用输出area/observed_ticks及hist；每slice分位数不能平均为全局分位数。

有界状态≤16MiB、compact新增输出≤8MiB仍是待实测目标；padding、实际序列化和最长commandlist预检后才能称达标。不为压缩输出截断人口或生成per-set×kernel×window全笛卡尔积。
