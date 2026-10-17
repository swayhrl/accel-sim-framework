# 结论与证据边界

所有主表来自固定九个accepted original运行；完整identity和原值在INPUT_RUN_IDENTITIES.json/COUNTER_EVIDENCE.json，source SHA在SOURCE_SHA256.tsv。没有Gaussian或任何新candidate运行/性能读取。DWT2D只在HYPOTHESES_PRE_HOLDOUT.md及其SHA封存后读取两个旧accepted raw，单列而不进入发现集或选择均值。

| 结论 | 分类 | 支持与限制 |
|---|---|---|
| GEMM OO128用1,377,919cycles，比C+1,511,333少133,414cycles（8.83%） | EVIDENCE_SUPPORTED | 同原输入/full739,246,080活动线程指令；设计族Core/服务/资源并不相同 |
| GEMM OO128成功下行读3,993,335，高于C+2,603,998约53.35%；L2读需求511,146,880B高于333,311,744B | EVIDENCE_SUPPORTED | 共同GLOBAL_ACC_R成功注入及L2四sector关系闭合；不是credit估算DRAM |
| GEMM三臂DRAM读/写传输均0 | EVIDENCE_SUPPORTED | stdout20个controller及终端CSV一致；仍有L2/ICNT/finite服务代价，host preload/初始L2驻留不等于测到了DRAM带宽收益 |
| GEMM OO128比IO256 ready-to-collect短（6.0614 vs842.6816cycle/cacheable warp），collection均1.0，WB等待0.15468 vs0.00891 | EVIDENCE_SUPPORTED | 是规定fully-ready后的分解；不是完整replay；256/128不同深度 |
| OO的退休组织有利于隐藏服务等待，可能解释GEMM更快却更多L2读 | CORRELATION_ONLY | 不可把836余cycle的指令均值差乘retired后等同于GPU节省cycles；C+同义分解缺失；H1仍需T0 |
| GEMM finite mean PIB181.05/79.19，physical159.05/124.79；大量Tag替换与较短OO map-loss寿命并存 | EVIDENCE_SUPPORTED | 全64SM全周期、非active-only、非唯一可查询数据工作集；不是“物理池耗尽”证明 |
| 更大Tag覆盖可能减少新分配/重复查询负担 | CORRELATION_ONLY | GEMM IO观察291,546条驱逐后原分配仍pending的重复下行；OO无同义重复字段，无法比较；T1才是有界干预 |
| BICG matched IO128/OO128 cycles93,312,525/47,533,116，OO约1.9631×更快 | EVIDENCE_SUPPORTED | 同finite Core/binary、同128 active PIB/full145,666,048活动线程指令；不等总面积，组织变化会反馈请求时间顺序 |
| BICG IO/OO成功下行读17,826,128/17,814,872，仅差11,256（约0.063%） | EVIDENCE_SUPPORTED | 单凭请求数量解释不了约一半的cycles差；不能推出其它量恒定 |
| BICG IO/OO DRAM读payload1,841,007,744/943,113,728B、L2读reservation retry604,002,611/268,516,902 | EVIDENCE_SUPPORTED | 同量纲实际下层结果；拒绝事件不是停顿cycle、DRAM量不是原矩阵字节数 |
| BICG OO仍慢于C+（47,533,116 vs25,353,488），同时比C+多约1.21%成功下行读、约101.30% DRAM读payload | EVIDENCE_SUPPORTED | C+ DRAM468,501,632B；新OO下层命中率分布更差，但没有地址/PC/时间因果归属 |
| BICG组织/时序及下层时间局部性是回退解释的候选 | CORRELATION_ONLY | IO平均ready-to-collect3557.95 vsOO1.1590，OO collection略长2.7630 vs2.75；mean PIB4.983/2.232不是饱和率。缺反事实干预，不能单归因Tag或refill |
| BICG C16/C80/WAIT128的cycles79,721,847/26,555,809/84,049,733，DRAM读624,048,384/431,602,688/731,557,120B | EVIDENCE_SUPPORTED | WAIT128为N型16KiB、PIB128/MSHR32；C80为N型80KiB、PIB8/MSHR32；都不是IO/OO同机制深度控制，不得混成一个capacity因果结论 |
| C+ GEMM MSHR merge-full有243,363,286次，BICG C16 PIB-full8,804,793次、C80为9,299,861次 | EVIDENCE_SUPPORTED | 说明这些是重复事件；C80更多PIB-full却更快，直接用事件排序瓶颈/速度无效 |
| C+与OO的同义ready分解、OO Tag/pool拒绝、OO重复在途line地址及每stage饱和周期 | UNAVAILABLE | 原输出和CSV无对应完整字段；不得把0或传统side-cache统计充作替代 |

独立旧DWT2D核对：C+247,588 / OO237,887cycles，成功下行读219,173 /232,173，DRAM读11,268,992 /11,307,264B。其“略快但读量略增”不反驳M-G的非单调关系；它不证明M-G机制链、更大Tag胜出或holdout candidate成功。OO ready-to-collect1.2697、collect1.0740、WB0.1152，只是同定义描述，C+分解仍缺。原假设未据此改写。

**后续建议：** M的身份/语义门槛通过，支持T继续其CPU资源/正确性/authority预检，并在全部独立条件满足、不可变manifest push+fetch-back后执行既已预声明的T0及最多六点T1。T0直接补GEMM同深度组织对照；T1只验证候选Tag结构路径，当前计数不保证任何点满足R_min/R_g门槛。保留Gaussian固定发现样本、DWT2D/BICG独立holdout及所有负结果。M不给运行权，不新增点、不修改阈值。

当前未观察到能单独证明应提高collection/refill/WB服务配额的可比较压力分解。collection工作量/间隔可见，但没有端口拒绝周期、refill队列等待或C+同义阶段统计，故T2仍未授权；不能把IO长ready等待当成应笼统提高所有finite端口的依据。
