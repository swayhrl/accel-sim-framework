# 机制分析首份交付：观察、竞争性解释、受控对照、结论范围

证据冻结：Lane5 generation38 / 44731833c67da9715d504fd3df6a40c615cf0d1f，42条 CURRENT_ACCEPTED，18个同源有限B/U配对、4个各自同源Ideal对照。AUTHORITY.json保存完整pointer与字节hash；不使用staged快照、旧R0/R1撤回值或在途状态作为性能。

## 1. 静态数据配额确实触发，但额外容量的边际性能尚不能归因

**观察。** H0 Conv B16有845097次wbuf_full重试，Unified为0；Unified WB-record峰值55，FWT峰值37，均超过16。真实采样WB-role均值分别为Conv2.16077/3.88125、FWT0.73994/1.18014，不能用record峰值代替物理占用。H0 S=B/U分别1.004826和1.003106。Producer S64的布局是1024/80/64，保持1168×128B/4banks，WB增加48槽来自bypass128→80，而非增加总数据容量。U_CAP16保持Unified组织和1168槽，仅限制本地WB reserved+live≤16。

**竞争性解释。** 收益可能来自消除copy、角色/落点变化、并发容量、排队/替换轨迹或其交互。U曾超过16只证明容量被使用，不证明这些额外槽位缩短关键路径；B16 wbuf_full很多也不等于同样多独占GPU stall。S64生产定向达到64并拒绝65，不证明当前应用下S64不满。

**受控对照。** 原矩阵内同一binary的B16/S64/U_CAP16/Unified Conv/FWT组，读真实reserved+live峰值/拒绝、copy、bank和下游，性能方向不作接受条件。不用source230的U与sourcefb的S64拼接。U与U_CAP16的对比检验额外本地并发；U_CAP16/B16仍包含组织、落点和复制差异，不能叫pure-copy。

**结论及范围。** S64是否消除数据配额限制、Unified相对U_CAP16边际是多少，当前均未裁决。STRONG_STATIC_DESIGN_SCOPE与availability表明确为缺数；未测不填0，也不声称胜过最优静态。

## 2. copy工作显著减少，整体收益仍小；bank落点是组织差异之一

**观察。** H0 Conv总RAM逻辑工作B=9217033、U=8124070，差1092963；B的546865次copy对应两个真实RAM操作共1093730，余量−767来自其他流量/调度差异。B的bank0工作占31.2564%，U占24.8036%。FWT减少356282个RAM操作；CFD减少63928个，但CFD cycles从79093升至79262（S=0.997868）。D4 Conv U的RAM工作和bank等待都少于B，仍慢1023cycles。

**竞争性解释。** first-free静态WB staging集中在低index bank，加上copy读写，符合B的落点不均；Unified原位WB和bank-compatible新landing改变分布。总工作下降不等于最长依赖链下降；counter大小或delta不能决定关键路径。两次copy操作的会计分解不是pure-copy反事实，也不是cycles分解。

**受控对照。** 同源同资源的B/U总工作、四bank落点与等待分别对照；已有A1测试复用victim固定、跨周期copy、lower-full及exact-once。新增HOL小case用真实cache和显式同bank竞争，pending head使另一bank就绪hit被拒绝；之后head与hit均完成且WB只创建一次。

**结论及范围。** copy与bank组织效应有直接操作级证据；HOL政策可在真实cache路径触发。尚无全应用“本来可并行的工作因此延后”的事件依赖证明，不能宣称HOL解释了全部退化或bank等待就是关键路径。

## 3. 下游解除后本地WB-data与WAD呈现不同约束；保留正负两向

**观察。** Conv Q4 B/U=290333/293709（S=0.988506），B/U本地record峰值2/4、wbuf_full均0，但WAD峰值均128，WAD-full重试55645/54516，scheduler拒绝/实际issue为0.15003/0.13266。WAD256_Q4只改变WAD metadata容量，B/U=292132/289899（S=1.007703），峰值173/170且WAD-full均0；scheduler拒绝仍0.15814/0.13882。相对Q4，B慢0.620%，U快1.314%，S的交互比为1.019420277（精确值以CSV计算为准）。增加的是每slice128项WAD控制，不是WB-data槽。

**竞争性解释。** 放大WAD改善责任持续期间的admission，并可能改变替换/到达交错；调度/流量差异也会影响结果。压力解除与相对收益翻转支持WAD交互，但不证明WAD-full重试数对应全部节省时间。单Conv结果不能外推FWT或最强静态竞争力。

**受控对照。** Q4→WAD256_Q4为同source230、同输入、同B/U资源的单因素metadata变化。既有真实partition定向达到256个WAD、本地数据已lower_accept释放但set_done为0；第257次拒绝及同地址顺序检查通过；恢复真实DRAM后257个set_done闭合。D2/D4/L25作为独立下游点保留；FWT D2=456123/458508为负例，D4=452758/451254为正例，不能只选最好配置。

**结论及范围。** 数据槽释放和完成控制债务必须区分。WAD256是一个已接受Conv有限正例，但同条件强静态/U_CAP16、FWT配对及原预算内验证输入尚缺，不能据此宣布普适贡献。原WAD256_D2联合候选仍须00/10/01/11和budget准入，不在本Goal新增应用。

## 4. 上游加速未自动放大EP效应

**观察。** Conv ROP40为290203/291161（S=0.996709724），ICNT2为293491/296184（S=0.990907679），都不改善H0的相对收益。ROP40降低固定前置延迟；ICNT2只有网络域加倍。原定向实际时钟、队列进入时间和drain均已验证，不能把负结果解释为无效旋钮。

**竞争性解释。** 更快供给可加重有限下游队列/调度压力，改变bank/替换轨迹；也可能存在其他SM/数据依赖限制。ICNT2 B16 wbuf_full仍1096396、scheduler拒绝率0.43607，支持“其他瓶颈仍在”，不证明唯一瓶颈。

**受控对照与范围。** 同binary H0与各单因素B/U比较，分别给绝对cycles与S/J。未提供FWT的已接受上游点时不生成组均值；不把更快某一域写成更快整个系统。

## 5. 局部与完整Ideal：哪些机会被测试，哪些尚未同源分解

**观察。** vectorAdd在Corea26/binary37dc的B16_OFF=73696：I_WB=73843（headroom0.998009），I_META=73696（1.0），I_READ_HIT=43020（1.713064）。I_WB确实把wbuf_full440161→0，峰值16→34，但cycles反而增加147。其copy_lines100568→100693、bank工作2801704→2802079；因此不是未触发，而是解除容量未带来这个输入下的吞吐提升。I_META基线WAD95<128、无WAD-full，不能用持平证明所有metadata都不重要。

另一个严格自洽的比较：combined Core9bd30/binaryfb67 OFF=73696，ALL_DATA=17247（4.272975）。ALL_DATA reference有1500000个request ready/consumed、无ready-latency违反、无memory-resource-wait、pending归零；32000000字节为producer-version符号、known_numeric_bytes=0。reference-ready到architectural-consume累计16120cycles/4030次寄存器等待，是不同事件口径，不相加为总执行时间。

**竞争性解释。** WB/META近零但READ_HIT较大，支持需求读/lower服务机会比这两个局部容量干预更显著；ALL_DATA还解除更广数据层次等待，保留真实指令发射、producer顺序与实际寄存器消费。两组OFF恰好同cycles不等于两个binary相同；不能用不同release的局部/全数据差构造同源归因。

**受控对照。** 每个Ideal都只使用本release、同输入的OFF。需要严格局部→全数据的同源阶梯时，等原预算内combined runtime的局部点；不重跑已接受source37端点凑图。

**结论及范围。** vectorAdd显示显著需求读/全数据操作性潜力，非WB容量单独决定；不能把ALL_DATA的4.273×称EP-L2 speedup、RO上限或任意调度下数学上界。Conv/FWT/CFD的完整局部/ALL_DATA组尚缺，不能声称它们“局部/全局都小”或给全套机会均值。

## 6. kernel/窗口与输入边界

Conv2、FWT19、CFD5个kernel-shared区间均检查了overlap_detected和边界；本快照这些案例无区间重叠。但计数仍为共享路径delta，包含其真实采样/launch/drain边界，不把64slice或重叠窗口相加为独占周期。kernel_shared_intervals.csv保留起止、overlap与操作数；不建立新critical-path框架。

现成run.sh给出Conv --size3072、FWT -logK7 -logD21、vectorAdd --size4000000、CFD ./data/fvcorr.domn.097K；未执行这些脚本。CFD目录9.1与脚本CUDA_VERSION10.1冲突，按两者分别披露，不臆断统一工具链版本。SAD未定位literal capture脚本，记未披露。完整commandlist只证明当前捕获范围，不等于源码默认循环。EN-v10附件未取得，因此本交付仅为独立段落/表图，没有重建或修改母稿。

H0_KERNEL_SHARED_COMPARISON.csv进一步保留阶段差异：Conv两个共享边界span的B−U差为392与1015；FWT前6个区间相同，后续既有负也有正（例如kernel12为−712、kernel13为1511），不只列有利阶段；CFD前4区间相同，第5为−169。这些是共享区间边界差，不命名独占stall或据此分解资源因果。
