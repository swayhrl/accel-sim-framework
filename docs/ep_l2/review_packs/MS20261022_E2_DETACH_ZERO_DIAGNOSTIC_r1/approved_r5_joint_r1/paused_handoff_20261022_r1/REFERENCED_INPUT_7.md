# 四组已接受点的 L2 请求流分析

本报告仅读取 CFD E052、DWT E053、Vector E054、Conv E055 已发布独立终验及其准确引用的 normalized summary；没有重扫 raw/trace，也没有干预本轮 r5 build。四点同 r4 Core9243/main d99，均是完整 F 诊断点，不是新 S/F 配对。

**共同可证原因：实际 production Tag probe 从未返回 RESERVATION_FAIL，故 relieve/detach 的必要触发分支没有进入。四组均产生真实 RO 事务，零 detach 不能解释为“没有 RO”。同 set RESERVED 占用、请求类别与 raw/route 联合分布在 r4 尚缺，不能进一步断言 Tag 总是充足。**

|应用|covered head-cycle|production probe 次数|RO 事务|RO 合并请求|production FAIL|detach|

|---|---:|---:|---:|---:|---:|---:|

|cfd_097k|1524394|1163176|51678|154770|0|0|

|dwt2d|1863454|1793713|9965|29871|0|0|

|vectorAdd_4M|3400296|831673|250118|749882|0|0|

|convolutionSeparable|7587714|4716184|371495|880056|0|0|



漏斗必须分域：observed/skipped/covered 是按 head UID×slice×物理周期去重后的观测；“once covered”不是每个请求一生只计一次。raw status、requester、primary gate 各自是 covered-head 域的边际分区；不能由边际表构造 requester×raw×gate 联合表。FT 调用/production probe 是调用次数；RO admit 是新事务、merge/response 是 requester 事件，WB 与 bytes 又属不同域。四点均有原 exact-once 总数闭合：FT accepted + TVD read responses = 原 unique_requesters = 原 responses；这不是补造逐请求轨迹。

逐物理 kernel 的212项事件已单独导出并逐项验证分区之和等于全局。CFD 的 RO 创建只在物理 kernel4/5（3,036/48,642）；DWT 在 kernel1（9,965）；Vector 在唯一 kernel1（250,118）；Conv 在 kernel1（371,495），kernel2仍有2,849,311次 production probe而没有新RO事务。这里 kernel 是事件发生时 active phase，不证明 requester/victim 的因果归属。

上游阻塞的实证：Vector MISS_QUEUE_FULL有818,741条 blocked observations、161,872个本原因first-block请求；Conv MISS_QUEUE_FULL590,686/98,263，LINE_MSHR_FULL150,118/6,058，SAME_ADDRESS_WB538,426/749，READONLY_LOOKUP1,251,627/1,251,627；DWT BANK_COMPATIBLE_LANDING148,372/5,099，WAD_FULL34/4；CFD READONLY_LOOKUP206,448/206,448及VICTIM_LOOKUP160,847/160,847。它们证明存在上游流控/服务等待，不能把非互斥原因相加成时间份额，也不能直接认定它们“导致”零TagFAIL。

Conv完整请求流新增：9,307,288个观测head-cycle，1,719,574次跳过全属TVD；7,587,714个covered中，raw MISS1,883,144、SECTOR_MISS5,098,494、HIT491,332、HIT_RESERVED114,744、FAIL0。实际FT调用5,596,242，返回accepted5,211,766/denied384,476；denied主要bank357,747与landing26,727，另promotion2。实际merge880,056，实际Tag probe4,716,184。所有 denied_capacity/missq 为0仅限实际FT-return分类；前端 missq mask590,686、line mask150,118仍非零，不能把实际commit分类的0当作整个系统未受容量/队列限制。

WB/TVD不能遗漏：四点WB created/lower accepted/completed分别29,962、163,840、100,762、546,813且每点三项相等。TVD read responses分别49,962、23,305、0、36；TVD真实served bytes分别1,598,784、745,760、0、1,152。精确lower read/write/WB bytes和RO专属bytes均从原字段输出，不用请求数×128猜字节；local_service和RO resource scopes可能包含关系，禁止相加重复计数。

容量语义：新RO descriptor/address只对实际consulted人口解释pass/fail；not-consulted保持NA；M1下传统line检查可能NA。未触发pressure-way扫描时eligible/reuse/no_missing的0是无观测人口，不是不存在这些结构属性。

r5结束后按 ANALYSIS.json 的Q1–Q5查询：先 raw×reservedWays，再 wayClass / eligibleCount / reasonPresenceMask，最后 supplied route_joint 中 physical phase×raw×reservedWays×requester×eligibilityState×productionRoute×admitted×earlyReason。只使用实际联合表，不从分散hist作笛卡尔积，不拿 r5 回填 r4 历史。

机读表：REQUEST_FLOW_PAPER_TABLE.csv；GLOBAL_COUNTERS_212.csv（准确单位与分母）；PHYSICAL_KERNEL_COUNTERS_212.csv（完整逐phase事件）；UPSTREAM_FLOW_CONTROL.csv；WB_TVD_RO_BYTES_AND_SERVICE.csv。每行都有源文件绝对路径、SHA和JSON pointer。没有普遍workload覆盖度、隔离T性能收益、跨binary加速比或真实SASS数值输出保证的推断。
