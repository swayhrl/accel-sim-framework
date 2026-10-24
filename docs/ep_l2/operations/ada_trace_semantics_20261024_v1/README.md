# Ada trace语义修复与原生验证（阶段一）

原SM89 HOLD具有实际原因：旧producer丢弃UGPR/PRED、宽寄存器高半、隐式UR descriptor与constant地址；旧消费者还将LDC固定4B、ULDC仅归统一ALU。仅派发binary89不能证明兼容。本阶段给出普通域v7 producer冻结候选及两个真实epoch2消费者验证，未改EP的V100基线或旧科学结果。

最终109工具为/data/c16/ada_trace_semantics_20261024_v1/frozen/producer_v7_55c6f482/producer.so，SHA256：55c6f4829e8c92e11e0ab54496bf8f507f6cfa3a10cd01a857c6de147ee68b73。实际GPU为RTX4080、UUID GPU-ce6cba36-415b-4e27-40e2-bded6bc1ee59，NVBit1.7.5/CUDA12.8；header89与tracer7不替换。

|同一最终工具的实际输入|CTA/warp|源SASS记录|有效lane指令|逐lane核验|
|---|---:|---:|---:|---|
|VectorAdd 4M，256线程|15625/125000|2125000|64000000|12000000个global地址满足base+4*i；28000000个constant访问|
|constant table64，65元素，64线程|2/4|54|1353|65个bank3 offset精确等于4*((i*7+3)&63)，65个global store地址|

两输入native和capture均exit0、数值正确。每个执行PC的完整SASS与typed读写匹配同binary cubin的nvdisasm12.8 PLR assignment/usage/read-modify-write，非live-in/out。Vector保留125000条零mask记录，constant保留2条；全部CTA/warp退出，退出lane无后续有效执行。宽高半、隐式UR及谓词依赖齐全。

R0..254为GPR；256..318映射UR0..62；320..326映射P0..6；328..334映射UP0..6；零寄存器不建依赖。v7保留active和predicate mask，并记录每个有效lane的constant bank+byte offset；该地址是符号tuple，不冒充GPU VA/PA。IMAD.WIDE常量加数宽度由旧NVBit错误4B修成8B，并受实际宽指针运行及PLR高半约束。完整字段/来源/pin见CONTRACT.json。

## 真实消费者执行

新converter保留typed scoreboard依赖，arch_reg只填GPR，UR/P/internal token不增加GPR occupancy或GPR RF端口计数；源kernel nregs保持。零mask不写回目的寄存器、不发aux。embedded constant在消费者内显式拆为const-load aux和原ALU，以内部token384等constant返回；原trace仍每SASS一条，原PC不变。采用per-kernel独立冷constant命名空间，不声称跨kernel warm cache或硬件并行重叠等价。

|独立exact request，各预算1|实际结果|资格边界|
|---|---|---|
|EP_ADA_TRACE_COMPAT_MICRO65_20261024_V1|exit0；1997有效lane uop=1418源+579aux；constant lane644|继承perfect_inst_const_cache=1，L1C请求0，不能算const-cache完成|
|EP_ADA_TRACE_COMPAT_CONST65_V7_20261024_V1|exit0；1802有效lane uop=1353源+449aux；constant lane579|关闭perfect，L1C27访问/18 miss/9 hit，gpgpu_n_mem_const11，L2 CONST_ACC_R非零|

父EP-MAIN分别独立join通过，回执附在两request子目录。原生namespace mnt:[4026535153]/ext4设备2128；spec/auth/Q及实际映射依赖逐SHA绑定；每case1次、128MiB输出、4GiB内存、120秒上限。总授权最多8次，已消费2次，不退款、不改写已注册root；后续不同输入/修订须新exact request。这不是旧Goal重跑。

真实parser CPU probe另通过base+delta/立即数、深拷贝回归、5负例及micro57源→78内部uop/21aux/2零mask。CPU fixture不替代原生运行。新profile是明确的序列化aux-memory工程模型，不授予硬件时延/吞吐标定资格；EP/DTC/AWMA旧消费者也不自动获得v7资格。

## 普通域和剩余专项

普通域限定单CUDA context、固定SM89 cubin、无device-call/ABI窗口、每SASS至多一个明确MREF或CBANK、普通直接launch、全kernel无ROI/采样的已审核classic suite。必须绑定source/input/binary/tool/map/GPU并先native校验，再全记录验收和归档。

以下仍保留在全suite完成分母：texture/surface；双MREF/LDGSTS/async/TMA；动态warp同步mask；CALL/RET/间接分支、related-function同relative PC和ABI窗口；JIT/动态函数；CUDA Graph/new launch API、多context、多流事件和并发时序；WARPSYNC/shared ATOM/RED的具体consumer侧效应资格。

55将texture/surface/双MREF/缺MREF内存项置qualified0，CALL.REL.NOINC直接报错；formal validator还拒绝calls/间接控制/async等域。动态WARPSYNC/BAR.WARP的参与mask尚需专项，不得因active mask已在而授完整控制资格。55没有完整CUDA API事件日志，不能用几个kernel文件证明mixed Graph尾段无漏；带这些机制的输入需预flight拒绝，后续新工具显式日志/guard。tracer强制launch前后sync，只产生串行replay资产，不证明原多流端到端并发时序等价。不支持项保存attempt并继续补修，不永久排除，不改89为86或漏函数宣称完整。

## 后处理及保留

新参考后处理使用external stable sort(z,y,x,warp)、64MiB sort RAM及XZ close/fsync/重开CRC，保留每warp原序。最终Vector grouped SHA为21302c908a7445f93f36250ecccd0cd0f5fd49c174355686057616910f80a8b2，展开264817471B。旧postprocessor会在XZ子进程结束前返回，已观察短时无效文件，不能只看exit0。

大输入NAS暂存、2D/3D/跨桶等价和空间预算由bulk agent独立实现，参考64GiB scratch cap不直接用于80GiB展开输入。旧/新attempt保留；早期prototype若干旧ELF曾原地重建，未逐个保留，不能承诺这些失败版本逐字重现。最终55的源、ELF、map及回执已在独立目录冻结，旧prototype不作正式工具。

阶段一已归档真164 bulk_20261024_v1/objects：stage_evidence_ada7_109_20261024_v1为75571200B/208成员，archive SHA e4bf2a9a43696a92886428eb8bfbf23c32e7d498be72ab8ed6ac5cfcc3192213；stage_evidence_ada7_174new_20261024_v1为74526720B/143成员，archive SHA e281c3760ee20d9bced68d05c755623d38fd08722ed8b82873ce047badb5a6ed，包含两个consumer root、实际加载依赖pack72MB及Gitbundle。两个对象均close/reopen archive/逐成员SHA通过，174new另独立完整tar成员重读通过，COMMIT与读取回执附各子目录；来源KEEP，释放0。其kind是工程证据，不增加formal workload分母。旧SM70及GPU来源未知资产与新4080资产分别标注；SM70 cubin不可直接跨major作为SM89证据，PTX可JIT也不能替代实际loaded-code/map证明。
