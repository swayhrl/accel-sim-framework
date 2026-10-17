# AA2 Gaussian source-request invalidation factorial

AA2继承AA V1 `c381b6e49b483e01c1c8a73118a3d450eeaf3b7f` 的零实际启动和四个预留UUID，合计实际starts上限仍为4，不增加额度、不重启旧Goal、不覆盖旧报告、不复用旧运行目录。本包及raw root完全独立；AA V1仅按不可变Git对象读取，保留其0/4科学STOP历史。

四点固定为K0_32x4、K0_64x8、K1_32x4、K1_64x8，继续用户指定的四个UUID。任何匹配的实际RUN_START都阻止该UUID再次发射；失败、不完整、timeout或性能差均不重新启动。当前PRE_REGISTRATION.tsv、spec与config为CPU设计草稿，**不是完整可执行预注册，也不是运行批准**。任何新性能之前必须先绑定全部依赖、源码与唯一runtime/library/default options、真实计数合同及完整strict/runner脚本SHA，再提交并push/fetch-back。

K1采用V `26abd496417d9392245052e54fbd9ba27c6ffd96` 与Z2 `Z2_K1_SOURCE_REQUEST_V2`：已有source请求到达ldst_unit::invalidate时撤销可查映射。继承原idle-cluster、MEMBAR、cache-config条件、SM集合和可重复请求；不是逐kernel广播，不等待global drain。旧Ref、physical/generation、UID、PIB、inflight、late/sector response、waiter和collection/WB继续按原身份完成。ordinary invalidate的pending/drain/Tag提交不变；不引入store自动失效、PROXY_FENCE清Tag、新事件或物理池重建。

K0必须为同一新Core与同一runtime、shared library、defaults、observer合同下OFF。K0省略/显式0的生产option/行为对照属于CPU准入检查，不增设第五个full attempt。两个新K0完整运行都先于任何K1，逐项strict PASS后分别精确校准3,798,174与3,278,356cycles。旧OO/T周期只是同Tag历史校准参考，不算新K0；有任一不匹配即STOP所有K1，保留差异，不retune、不补跑。

公共参数全部冻结：OO128、physical640×128B、ordinary16KiB、shared96KiB、64SM、4 Tag banks及原有限服务率、finite V1、global cap32768、1410MHz、flush_l1=1。仅K开关与logical Tag sets/ways可以变化，Tag为32×4和64×8。所有原默认及有效options须完整闭合；不能仅看显式配置文件就宣称默认等价。Framework build source与AA2 orchestration commit分开记录，不能把文档发布SHA误写为已编译源码SHA。

输入为原Gaussian完整list，513条命令含3条HtoD和510个kernel；Gaussian成员数严格为510。T的GEMM+Gaussian总511不是Gaussian成员数。逐成员重新SHA256并绑定accepted original Gaussian manifest、原kernel顺序、CTA、active instructions和FULL_ORIGINAL_LIST ROI。总active-thread instructions为283,685,120；禁止截断、采样、修改trace或换输入。

W完整逐地址body scan仍UNAVAILABLE，不宣称实测跨kernel复用、别名已解除或内存值正确。AA2用户已明确：输入身份、V/source事件、Y2独立OO安全及真实计数均闭合后，该缺项保留为机制归因缺口；不据此声称没有K1作用。V1条款逐项审查及本次显式变化见W_SCOPE_CLAUSE_REVIEW.md，不无声删除门槛。

当前候选Core c0a5e2c3为真实功能实现，不能与历史f8b34dd7文档STOP Core混淆。绑定X发布和真实binary不代表Y2已经PASS；只接受针对该精确Core及option的PASS_K1_OO_MODEL_SCOPE与K0等价门槛，任何FAIL_CLOSED都不绕过。Y旧f8b34dd7 FAIL_CLOSED是历史事实，既不改写，也不自动当作c0a5e2c3的Y2裁决。事件observer只在K1路径启用的源码事实单独审查；作者声明零额外模拟周期不能自行替代四格同一observer合同及开销的独立资格。AA2不修改Core或请求第二套Core来修平。

当前所有其他DTC authority、进程和锁必须实时审查。旧U终止只能证明U终止，不授予当前执行权。AA2只有自己的单一authority，默认最多一个新sim；不获取旧锁、建立共享执行权、终止他人进程或删除他人文件。外部EP_L2/RTL等项目全部计入RSS、cgroup headroom、swap、PSI、磁盘和I/O。存在可派发旧DTC authority或未核控制进程时保持HOLD/STOP，资源数值充足也不能绕过。

timeout固定每点7200秒，首次实际启动定义不可重置的绝对deadline；每点最多一次实际simulator启动。授权允许确定性wrapper恢复的前提是证明同UUID/同deadline且没有第二次simulator启动；本阶段不提供自动重试。CPU准备和外部检查不消耗四点额度，也不得误写RUN_START。

严格验收合同见STRICT_ACCEPTANCE.md。真实source请求数、各来源计数、mapping changed、retained/reclaimed必须分开，不能用eviction或kernel数代替。K1没有实际E或没有mapping失效可保留为负结果/模型未暴露，不改事件集合制造效果。无直接字段为UNAVAILABLE；不补零、不伪装PASS。物理retained但无live owner的合法状态不被误判泄漏。内存值正确性、全ISA/native/PPA/硬件zero-cost主张均不授予。

比较固定K/Tag主效应、加性交互及Z2 Q32/Q64/T0/T1/I/logI，分母和单位明确，不把条件服务均值变成整机周期因果份额。任一必要点缺失/不合格则相应效果UNAVAILABLE；负结果、退化、timeout、deadlock、FAIL/HOLD均列入四格，不补格、不选最佳Tag、不声称统计显著。

不启动T2、GEMM、BICG/DWT2D复测、第三输入、额外Tag、现代DTC、新Core增强或第二套Core，不生成GM12，不晋升主配置，不修改论文或原44行。Git仅保存小型审查证据；大raw/编译/运行产物仅在AA2 raw root。最终STOP/HOLD不留下自动派发进程。
