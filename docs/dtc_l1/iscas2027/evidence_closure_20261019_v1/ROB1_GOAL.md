# Goal: DTC_ROB1_SERVICE_AND_FAIR_CONTROL_174_V1

职责：准备最少但有判别力的服务敏感性与优化公平对照；无完整模拟派发权，AG4活动时不执行未被其合同识别的CPU进程。独立分支 `hrl/iscas2027-dtc-rob1-controls-174-v1`，pack `docs/dtc_l1/review_packs/DTC_ROB1_CONTROLS_V1/`。诊断Core独立从c8090115派生，常规C+从其已接受对应源码派生，不污染生产Core。

## A. 服务敏感性

从实际source/config核实collector quota、ready/select/WB边界，不把原4 banks各1 grant误读成集成4 reference/cycle。目标仅是现有F在GEMM/BICG上collect 4→1个32B sector/cycle；若已有已验证选项，直接使用，不写新机制。

若必须实现有界诊断开关，默认OFF/显式0完全保持旧路径，ON只降低collection quota；不改变数据返回、waiter、调度、WB grant、cycle>collect_done_cycle和Ref/fence。记录准确定义与成本解释。CPU验证每cycle额度、跨cycle收集、WB拒绝、OFF/0等价及quota1不丢sector；不为一个quota选项重做AE137项和整个V2。

## B. AE公平hash准备（只有协调者最终选择AE才做完整性能）

先读AE真实固定hash和C+已接受索引实现，建立相同bank-preserving XOR函数在各自sets下的对照；地址键、bank低位、容量/ways、LRU副作用及服务延迟保持其各自基线。不能把另一个现有随机/多项式hash称为相同AE，也不能把C+改成DTC容量/架构。

形成GEMM、BICG的DTC OFF/ON、C+ OFF/ON四元组需求清单，已有DTC控制能资格复用则不重跑。若传统源不同，明确记录版本/whole-line与ordinary差异，不要求假同binary。新增硬件XOR和固定Tag latency是模型假设，不宣称零成本或同频。

## C. AD机理准备

仅消费已实际输出的通知与公共边界；建立admitted/all-return→collect/retire及fanout/notification span的typed统计表。ready定义随AD变化，不能相减旧post-ready均值当因果周期。OFF无字段为UNAVAILABLE。BICG/DWT2D只需要最终F ON与O OFF的必要配对；不为一张漂亮图补全与结论无关的全部计数器。

## D. 出口和预算

三项可并行做源码/配置准备，真正执行分支由AG4结果决定。先发布CONTROL_DESIGN.md、DIFF_AND_OFF_EQUIVALENCE.md、CONTROL_REQUESTS.tsv、CPU结果和统计脚本；Coordinator按MASTER_PLAN合计R<=6、校准来自预备4，全量Popen只能由协调者执行。

保留所有错误与反向结果。新Core仅诊断用，不能默认为最终候选改进。不要新扫下游队列/DRAM/ICNT，不碰AC/AC2/AF、K1性能或AE+AD。完成后commit/push/fetch-back并报告准确SHA，不在自己的worktree留后台dispatcher。
