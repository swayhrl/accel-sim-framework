# EP-L2：以生命周期解耦实现原位写回与等预算数据池共享

<!-- PAGE 1 -->

## 摘要

GPU L2中的地址可见性、数据保存和事务排序并不在同一时刻结束。脏受害者退出Tag后，数据仍需保存至下层接收，地址顺序还可能延续至写回完成。固定分区既引入resident到写回缓冲的搬运，也限制空闲容量在角色间复用。EP-L2用带代际的payload句柄分离三种责任，使resident数据原位转为写回暂存，并为新resident分配独立落点。在相同数据容量、四Bank与单周期服务上限下，分别检验copy消除、容量共享和应用吞吐。本文给出机制、正确性门槛与字段成本；应用效果由修复后重新取得独立科学资格的配对执行确定，不预设加速方向。

## 1. 引言

一次缓存替换同时牵涉三类对象。Tag决定某地址是否仍可被resident访问；payload保存返回或写回所需的实际数据；WAD维护旧写回与后续访问的顺序。Tag退出后立即释放payload可能丢数据，反过来让Tag一直等待事务完成又会阻挡新驻留。三者需要可分别释放的身份与生命周期，而不能仅由“缓存行已替换”驱动。

静态设计为resident、bypass和写回暂存各留配额。dirty line需要搬入WBUF时，源读取、目的写入和随后向下层发送的读取均占用数据阵列。共享池改变数据owner而保留物理位置，可省去前两次操作；合法空闲落点还可能接纳超过静态WBUF配额的暂存。但服务次数减少不必然解除容量阻塞，解除容量阻塞也不必然改变应用完成时间。计算、请求依赖或下层排队都可能吸收局部改善。

本文的核心是以真实写回消费者约束释放边界，在等预算下单独回答三个问题：是否省去copy服务，是否在真实压力下利用跨角色空闲容量，以及这些变化是否改善固定下层系统中的端到端吞吐。评估保留负控制、低效与退化，不用历史影子计数或理想读路径代替预算内实现。

## 2. 三种责任与因果链

记脏数据读出或原位转交时刻为t_r，下层实际接收为t_a，写回完成为t_d。数据暂存责任覆盖[t_r,t_a]，地址顺序责任持续至t_d；预留可能早于t_r。软件队列只保存指针，不能据此认定接收方已拥有数据。只有下层已计账的数据承载完成交接，源payload才可释放。

| 事件 | Tag／数据／顺序的责任 |
|---|---|
| 替换预留 | 保护旧数据，先取得合法落点及控制资源 |
| 原位转交或copy完成 | 旧Tag可退出；旧数据由WB_STAGED独占 |
| 下层真实接收 | WB源数据可释放；WAD继续维护顺序 |
| 写回完成 | 释放WAD；不反向依赖新resident分配 |

原位转交直接改变copy操作数；容量共享则必须另外观察到静态配额约束与合法跨角色分配。两条路径最终都要经过Bank排队、下层接收和请求依赖，才可能改变应用cycles。这是后续图表与对照的组织依据。

例如地址A的dirty数据仍在写回，旧Tag的位置已被地址B复用。B的填充必须写入B的新句柄，A的晚到完成只能结束A的排序责任；即使两次请求来自相同地址或相同Tag index，也不能凭位置相同合并身份。A数据已被下层接收时，其payload可释放，而A的WAD仍活跃。这一例子说明驻留容量、数据暂存容量与地址并发容量是不同的资源。

机制的贡献因而不是增加缓存字节，而是使已有字节的归属能按真实消费者交接。它同时提出一项评估责任：共享模式的额外分配、引用与选择逻辑必须进入成本账，静态模式也必须支付真实copy端口服务。只有在两侧资源、时钟和终止口径一致时，性能差异才能用于解释共享机制。

<!-- PAGE 2 -->

## 3. 等预算实现与生命周期约束

### 3.1 数据组织

每slice有1024个Resident Tag，line为128B，含四个32B sector。主比较B16_BANKED与U_WB16共有1168项数据；8项WBUF敏感性配置共有1160项。静态主配置为1024 resident、128 bypass、16 WBUF，共享配置在同一数据预算内按实际owner分配。四Bank分别有292或290项，每Bank每物理GPU周期最多一次line-sized服务。

双方另有同样的128B copy pipeline latch，它位于1168/1160项可分配数据之外，空闲时也不能作为额外共享槽。描述符512项、Line-MSHR和WAD各128项、每地址最多32个请求保持不变。全芯片64 slices、32 memory channels，主DRAM为850MHz，L1沿用校准配置；不以扩大其它资源替代共享池本身。

### 3.2 预留、copy与原位转交

静态模式在破坏dirty victim前，同时预留WAD、WBUF数据落点和必要发行容量。copy执行resident source read和WBUF destination write，下层发送还需staging read；同Bank操作必须跨物理周期服务。共享模式将旧resident句柄原位转为WB_STAGED，只省去源到目的copy，仍支付发送读取、fill、吸收写和真实响应读取的服务。

新resident优先取得与Tag相同Bank class的落点，避免把placement变化混入共享收益。共享并不提供无限WB控制对象：WAD、发行容量、物理payload和pin仍限制在途工作。若任一预留失败，回滚必须保持旧Tag、owner、pending及数据完整；旧WB排空不依赖新resident分配，避免循环等待。

共享allocator的空闲总数还不等于某个Bank class可用的落点数。全池有空而目标Bank没有合法槽时，仍须拒绝并保留reservation的原子性。预留槽、已形成的WB包与已下层接收的数据分别计数；只有前两者才可能占用当前staging数据。完成token可以活得更久，却不能被重复计成仍持有完整line数据的缓冲。

### 3.3 句柄、sector与时钟

句柄由payload ID和generation组成。访问先确认项仍存活、代际与owner匹配，再处理sector有效性、pending和pin；旧返回不得写入复用后的Tag或payload。每个物理项只有一个主owner，读取引用是附属责任。WB到lower_accept才释放数据，WAD到set_done才结束排序，二者不可合并成一个释放事件。

Tag替换先后次序所用的memcpy offset不是物理时间。Bank单周期限额、WB/WAD年龄须绑定实际GPU cycle，非零offset也要逐Bank检查。untimed host prefill建立有效Tag时，必须通过唯一allocator建立或安全复用resident句柄；dirty victim、活跃返回、pin、pending与epoch边界需要明确拒绝或单独验证，不能关闭owner断言代替正确性。

### 3.4 独立扩展

TVD在Tag miss后增加一拍查找，按有效sector服务，并分别处理clean promotion、dirty read-forward及写／atomic等待。served bytes只是响应服务量；定向lower读请求从两包变为一包不能推出应用或DRAM节省。RO使用完整commandlist、line粒度closed-world oracle，排除写、atomic及无法证明安全的外部更新；detach与Line-MSHR bypass分开控制。新版本的Tag／lower／epoch接线仍须独立资格，不能继承旧模块PASS。

<!-- PAGE 3 -->

## 4. 证据、归因与条件性对照

### 4.1 有效配对与正确性范围

首批五个开发负载固定为convolutionSeparable、FWT_7_21、cfd_097k、vectorAdd_4M和sad；sad保留为负控制，btree、dwt2d用于策略冻结后的验证，scan单独调度。主比较在相同修复版binary中切换B16与U_WB16，匹配非模式配置、完整trace、epoch和终止合同。

每条结果绑定源码、producing Framework、binary、ordered config／aux／environment、trace内容及显式功能和ideal向量。生产者测试后还须独立资格，包含physical_bank_clock、memcpy_payload_identity及受影响的原有门槛。当前接收表中的明确撤回优先于历史资格和正常终态；新修复使用新身份、新run-key与新目录。

SASS不含完整数值payload。应用验证限定于独立sector-version reference、owner／返回身份、requester恰好一次响应、WB创建—接收—完成和终态退尽；已知数值的定向fixture另列范围。指令数一致、正常退出或编译成功都不能单独证明上述性质。

### 4.2 分开验证三条因果路径

第一条路径是copy消除。对照实际copy lines／bytes、source read、destination write、lower-send read及Bank logical operations；重试attempt不能当作新的逻辑操作。若copy减少而容量压力未触发，只能讨论搬运与端口服务变化。

第二条路径是容量共享。记录预留占用与已创建WB占用、staging峰值、WB-data-full／pool-full、借用来源、拒绝和实际等待。resident转为WB的角色事件本身不证明容量突破；需要看到静态配额确实约束进度，而共享使用了合法跨角色空闲项。

第三条路径是端到端效果。固定指令计数I且口径一致时，吞吐代理(I/C_U)/(I/C_B)=C_B/C_U。Bank等待是逐操作等待和，不能从它直接减出GPU elapsed cycles。还须同时核对lower队列、WAD及实际DRAM读写，区分局部服务、下游限制和总完成时间。

| 条件成立后才追加的对照 | 能回答的问题及边界 |
|---|---|
| 当前合格配对出现容量压力及共享效应 | 同1168项的静态1024/112/32重划分；同时报告bypass缩减代价 |
| copy变化可能解释共享优势 | 准备等copy服务成本的归因变体；先冻结新配置与独立资格，不能私加端口 |
| L2服务改变而应用无变化 | 一档有证据的下层headroom四格：B／U×原下层／选定下层；另列诊断身份 |
| 修复R1.1有独立资格与自身B16 | 同binary I_WB、I_META、I_READ_HIT；I_WB_META仅预定两点 |

对照还须保留代价转移：扩大静态WBUF会减少bypass空间，copy服务变化可能影响Bank公平性，扩大在途WB可能提高下层排队而延长WAD占用。因此强静态对照不是无代价的单变量替换，必须同时呈现各角色约束和下游blocking。若所选负载没有有效压力，则把对照记为未触发解释条件，不据此选择只保留更好看的结果。

### 4.3 当前可引用的观测

当前没有可接受的预算内应用性能配对，因此主性能图和组均值留空。旧R0/R1应用因物理Bank时钟与host预热身份缺陷撤回，不能据其加速、退化或占用判断机制是否有效。新五点均合格后才计算预定集合geomean；失败、未完成和负结果都保留。

历史13行locality显示line重用与同sector时间重用不同：vectorAdd约75%与0%，scan约78.82%与16.04%，仅作工作负载动机。另一旧静态系统的乐观读参考为73873／42918 cycles、1.721259倍；它不是新B16结果、全负载均值或严格数学上界，不填补修复版结果。

<!-- PAGE 4 -->

## 5. 可审核成本与关键路径

### 5.1 数据预算与字段

主数据RAM为1168×128B=146KiB/slice，敏感配置为145KiB/slice。双方共同latch再计128B/slice，全芯片8KiB；阵列加latch分别为146.125与145.125KiB/slice。下层FIFO、scheduler及其数据承载仍按共同资源计账，软件容器只存指针并不能使这些字节消失。

Payload寻址宽度P=ceil(log2 N)=11。代码slot保存allocation_role、status、owner、generation、pending／ready sector masks与pins。若独立编码三种分配角色、八种状态，压缩line key宽A−7，代际G、pin宽K，则候选表示为N[2+3+(A−7)+G+4+4+K] bits。这只是字段编码算例，不是已合成结构，也不是相对基线全部新增成本。

| 可计算字段 | 参数化成本与尚缺的映射 |
|---|---|
| 1024个Tag句柄 | 1024(P+G) bits；若静态侧同样pointerized，两侧共同 |
| 最多128个WB句柄 | 128(P+G) bits；packet binding及状态另计 |
| 一笔前端reservation | 三句柄、landing ID、Tag index、phase与flags；旧状态保存、地址与控制另计 |
| 四Bank选择与重试 | busy／selected控制、Q_b个等待项及age宽E；不能把软件vector当免费队列 |
| RO completion | 已读模块按N配置，而非128；共享D512约束live数，不自动压缩配置槽数 |

versions、expected和逐WB reference是数据正确性审计sidecar；它们不代替128B数据RAM，也不直接当作必要硬件。generation拒绝wrap不证明某个硬件最小位宽，pin的最大引用数也需要生产上界证明。任何复用、压缩或省去字段都需对应实现；不同时赠送免费shadow保存和回滚能力。

### 5.2 比较逻辑与时序责任

句柄验证需要索引、occupied检查、G-bit generation相等比较，owner复核还涉及A−7位地址键。Bank class取低两位并不等于免费分配器：292／290项内的可用项选择仍需位图或free-list、编码与角色／pin检查；替代结构不能无故同时相加。

若Q_b个候选用平衡树选择oldest，单Bank需要Q_b−1个E-bit比较节点，理想选择树深为ceil(log2 Q_b)；实际布线、扇出、选择器与tie-break仍需实现。WAD或TVD若全并行比较128个line key，需显式计128组A−7位相等比较；串行／分级替代可能改变查找时延，不能把软件map搜索当零延迟硬件。

关键路径至少分开审视Tag命中到句柄／Bank授权、miss预留到free-slot选择、WB owner转交到下层接收，以及独立TVD查询。只读detached fill还要核对generation、sector与response背压。当前没有匹配RTL、SRAM宏、工艺与约束，不能给出mm²、mW或STA频率；四Bank一op／cycle和TVD额外一拍只是需实测遵守的模型合同。

动态能量也需要按真实事件而非元数据字节推断。可写为各Bank读写次数乘匹配宏的单次能量，加latch／线网转交及控制逻辑活动；若RAM读写已计入，copy附加项不能再重复算一次阵列。能量乘积、空闲功耗和执行时间的组合必须来自同工艺与同频率条件。这里没有这些测量输入，故只保留事件方程，不给出节能百分比。

## 6. 讨论与结论边界

EP-L2以可分别释放的Tag、payload与顺序状态组织原位写回，并在固定容量与端口预算下开放角色共享。copy操作数、容量压力与应用吞吐是三个需要独立证据的结论。静态重划分与同binary ideal只有满足前置证据后才执行；oracle辅助扩展不与真实WB主线混为一谈。本文当前交付机制与成本论证，应用优劣等待修复版的有效配对。

## 证据引用

[1] EP-L2资源／生命周期合同及静态源字段；[2] 独立物理时钟、host预热与科学撤回记录；[3] 完整13行历史locality核验；[4] 旧静态系统的独立乐观读诊断。精确SHA、模型限制、图表占位及当前接收状态见本稿附带证据映射，不作为正式出版参考文献的替代。
