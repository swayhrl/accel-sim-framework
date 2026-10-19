# Goal: DTC_SEM1_PRODUCTION_VALUE_AND_SCOPE_174_V1

职责：在已有结构资格之外，推进实际生产路径的值与顺序支持域；避免重新运行一遍V2外部条件化oracle后仍然production value tests=0却称已关闭。无完整GPU模拟/EDA自动派发权；遵守AG4保护门禁。

分支 `hrl/iscas2027-dtc-sem1-values-174-v1`，独立review pack `docs/dtc_l1/review_packs/DTC_SEM1_VALUES_V1/`；需要测试插桩时用隔离Core分支 `hrl/iscas2027-dtc-sem1-core-174-v1` 从c8090115派生，不修改AG4生产树/库。

## 1. 从既有缺口继续，不重做已结束调查

先读固定V2 LATEST_REPORT、VALUE_VISIBILITY_SCOPE、SOURCE_ROUTING_CROSSWALK，以及Y2/X2/AG3实际LDST证据。区分source请求E、ordinary提交C、kernel完成D和无E的写后读；不得把Ref/generation、store sidecar退出或fence当全局值发布。保留K1现有eager E定义，不改变事件来源。

用一次不超过90分钟的源码/ABI检查定位真实数据来源、store payload/byte mask、refill内容、物理池数据及consumer结果是否可在当前生产路径观察。输出接口图和精确缺失点，而非泛称模拟器不能验证数值。

## 2. 一个紧凑、真的能证伪的生产路径测试组

在可以观测的实际生产对象上，准备最多12个定向序列和固定seed的有界组合测试。覆盖：只读共享/pending merge；Tag换出后原consumer读数据；旧generation返回；WB拒绝保持Ref；不同byte mask；同址更新后有E/无E；late merge/slot复用；AD先通知consumer早收集但未通知者不能提前；AE不改变返回身份。已有纯状态corner case只作复用来源，不又计为新增值测试。

预期值由独立参考内存与明确允许的同步/发布合同计算，实际值必须来自真实被测load/refill/collection路径。禁止把期望值塞回被测结果、在observer中直接读参考内存充当production load、由守恒残差补返回数据。负控应检测错值、缺sector、错generation、提前释放或错误发布。

若当前SASS timing路径缺少真实payload，可在独立、默认OFF的测试桥接中携带显式测试数据，但结果必须标CONDITIONAL_PRODUCTION_ROUTING_VALUE_TEST，声明数据注入点/外部可见性假设；不得升级为完整原生/ISA值正确。纯shadow monitor结果单列，不将其通过当真实执行逐load对比。

若补齐真实payload意味着引入整个functional ISA或新coherence协议，在此停止扩展该实现分支；交付最小缺口和scope修订，不让其它工作包停摆。不得重开K2、引入per-store自动invalidate、修改主K0来掩盖反例，也不重新申请旧AA5性能四格。

## 3. 把语义证据落实到输入

消费COV1已固定的源码/访问索引；将每个输入分为：READ_ONLY_OR_PROVEN_NONALIAS、SUPPORTED_BY_EXPLICIT_EVENT_CONTRACT、UNRESOLVED_READ_AFTER_WRITE、OBSERVED_COUNTEREXAMPLE等，并给可核证据。不由缺失alias分析推断无alias，不由kernel名推断只读；计时可用和数值可用分开。

出现K0反例时明确保留：真实哪种请求/值/事件错，是否影响已测输入仍需另外证实。既有K1只做本CPU域诊断；若拟将主方案改K1或更强策略，发布需要科学裁决的最小方案和资源影响，不自动合入/启动性能。

## 交付

PRODUCTION_VALUE_PATH.md、LITMUS_MATRIX.tsv（观测、预期、注入点、值来源、资格级别）、最小测试代码和结果、WORKLOAD_SCOPE.tsv、COUNTEREVIDENCE.md、MAIN_CLAIM_IMPACT.md、LATEST_REPORT.md。真实生产值、条件化路由见证、结构回归、原生验证四栏分别计数。测试组一次收口后发布；普通工程问题继续，真实语义变化提交协调者，不反复堆外部oracle测试。
