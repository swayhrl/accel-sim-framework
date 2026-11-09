# 科学背景：E1观察、E2真实结构、E3待验机制
下面数据均来自已关闭固定来源。证据归类要求贯穿选型、CPU资格和真实结果。不得将不同Core/config/输入集合的几何均值相除计算“兑现率”。

## E1｜CORE32 Oracle完整32输入观察（不是可实现硬件）
同一Oracle Core `e6b41ab8992e7d41651501c4d34cfe24195c4f96`，Framework `02775fd795cde5aae1480d81cee6eb481d0a08f4`，固定32输入×OFF/M/L2/L1＝128自然闭合格、96同build OFF配对，全128 D独审PASS，M完整32分析和Main签署完成，科学窗口接受在SM70/V100-derived 64SM固定trace范围内关闭。正式运行结果 `7ffcca7f908a21f45ba1a6ebb3b335ff962f97df`，Main审阅 `b9ff89f00ea8ff889e4189136501c714c5d7e345`，科学接受 `64cd088b2de575157846f07a21ce09748220f7e2`。

CORE32 GM：M＝1.676758525810×，32/0/0；L2＝1.280648684508×，19/11/2；L1＝1.939911577005×，32/0/0（正/整数精确零/负）。L2的11精确零和myocyte慢2cycles、srad_v1慢14652cycles不删；bfs快5cycles、mri-q快692cycles保持正。
GESUMMV的M/L2/L1分别约10.288/4.132/35.851×；MVT、ATAX、BICG的L1分别约20.230/18.593/16.723×。3MM/GEMM L2为精确零，M与L1均有响应；M在部分输入反而比L1快。三模式既不严格嵌套，也不能用差值分层相加。
myocyte/L2的5993个kernel为0快/5992相等/1慢；srad_v1/L2的502个为215快/13相等/274慢。应用周期改善≠所有kernel同向，也不是可唯一归因的关键路径证据。
E1不是原生数值认证、capture时ELF/输入绑定、完整coherence、严格数学上界、PPA或等面积优势。缺失计数器保持UNKNOWN，sector32B/DRAM atom32B/128B line/request object分开。

## E2｜既有真实结构结果与不利对照
- 固定CORE32的CH/DH P0公平比较：GM(CH/DH)约1.100072；F128/F256同时改变FR-FCFS窗口与shared credits，CH和DH均可能受益，整体未加强DH相对CH优势（相对交互GM约0.99683、0.99852）。不能将F结果写成单独L2容量因果。
- V1非Tag共28 accepted加4个scan cadence工程负例；两种1024Tag/physical640共16个计划格保持NO_FREE_LINE安全HOLD，未成为16个性能回退。
- Physical640→768：MVT 34,687,540→30,609,855（主要K1 33,032,429→28,955,953）；BICG 28,685,812→30,892,841（主要K2 27,030,465→29,237,494），说明容量改动在相似指令规模下仍可能反向。
- MVT下游new requests 12,127,693→6,793,725、DRAM32B reads 20,574,896→19,993,536；BICG new requests 11,201,149→7,045,657但DRAM reads 17,688,864→20,596,672。减少请求数≠减少DRAM工作或改善周期的充分条件。
- 已打印的MVT/BICG lower-create-queue-full与lower-credit-full为0；因此不能未加证明就把“继续扩大这两个资源”定为首选。L2 entry/missQ retries是事件，不是关键路径阻塞周期。
- PIB192同时将lower-create深度128→192，GEMM有小幅改善但2DCONV/convolutionSeparable回退；不能归因为单独PIB容量。
- V2 R1 physical×PIB两组合fixed8 GM分别约1.007827/1.008379×；7个已完成对照周期相同，scan不同且J缺失，负例保留；不拿fixed8 GM与本轮CORE32 Oracle GM直接相比或计算收益兑现率。
- vectorAdd历史有效OO valid/pending均为0，结构变化常近零，是负控制候选；但Oracle三模式也可响应，不能将它定义为“访存无关”。
所有E2使用原接受Core、binary、输入和原参数，不能与E1共用OFF分母。

## E3｜竞争性、可证伪的有限机制解释
首选调查区域：**正常DTC路径的有限回复/ready通知/collect/operand写回与retire的调度顺序**。关注的不是让服务免费，而是当两项及以上合法服务对象同时存在、当前固定策略选非关键或排队较久对象时，有限队列/端口下改变选择顺序能否降低有效等待。下列为筛选假设，均非已证明瓶颈：
- H1：已有ready/notify/collect或WB服务仲裁在某些phase存在真实独立候选和可避免的队头等待；有界年龄/就绪感知选择在**相同端口和quota**下可能提高进展。反证：现有实现已等效选择；没有同时合法可服务候选；新选择不改变实际服务序列；改善仅转移拥塞。
- H2：sector返回/parent完成的有限仲裁使需要多sector的指令等待被不相关返回占位影响。反证：无所需sector的合法选择自由度；算法破坏required mask/parent/credit不变量；既有关键路径从不经过该选择。
- H3：PIB/Ref/physical释放约束是受限资源而非完成带宽。反证：高physical占用只是Ref-free保留映射，实际准入未发生physical/PIB阻塞；改完成顺序后准入与周期不变。
H1/H2可作为候选域，但只允许最终冻结**一个**硬件改动；H3主要作为替代解释和第二优先方向，不得悄悄把PIB/physical扩容混入本Goal。

## 候选选择的可证伪要求
对每个E3保留支持、反证、现有计数器范围、源码callsite、是否存在至少两个**同时合法**服务对象、受约束端口/时延及可测的“实际策略选择不同”事件。先在只读证据+可执行CPU fixture证明候选机制的正路径可达，仍需真实模型中有有效曝光后才谈性能。仅改变配置echo、未证明的平均等待下降或count差异不是因果结论。
若选定策略也适用于传统CH，DH改善可作为发现，但DTC专有优势与等成本公平性仍独立待验。