# 用户明确的收口边界（2026-10-18，Asia/Shanghai）

K1科学合同已明确，权威来源为Lane V分支 `hrl/iscas2027-dtc-lane-v-semantic-audit-174-v1` 的固定HEAD `26abd496417d9392245052e54fbd9ba27c6ffd96`：

- `docs/dtc_l1/review_packs/DTC_LANE_V_SEMANTIC_V1/K1_SEMANTIC_CONTRACT.md`
- `docs/dtc_l1/review_packs/DTC_LANE_V_SEMANTIC_V1/SOURCE_EVENT_MAP.md`

用户定义K1为：冻结源码已有 `ldst_unit::invalidate()` 收到source-defined失效请求时撤销DTC查询映射，同时保护已经接纳的physical generation和所有未完成消费者。它不是统一kernel-end广播，也不是普通L1实际Tag commit时刻。不需要等待Lane X实现才能继续只读分析。

用户确认Lane U已正式完成，但要求重新检查原174的IO PSI、磁盘、资源及其他模拟器活动。若仍超过本Lane安全门槛，保留DEFERRED_SAFE_STOP，不启动body scan；资源允许时才单worker、流式、低优先级读取原Gaussian/GEMM，先验证decoder CPU fixtures。不得创建大型解压副本、无界输出地址集合或修改原trace/parser/旧raw。

本Lane不做K1性能外推，没有完整模拟器启动权。必须区分跨kernel地址相交、同SM查询复用、实际Tag驻留和数值正确性，缺动态证据为UNAVAILABLE。

明确的结束条件是：**“若资源始终不合格，就以已发布的有界审查结果收口；不要为追求表格完整强行扫描。”** 因此有界收口不要求把未扫描地址字段填成数值，也不能将DEFERRED_SAFE_STOP称为完整body扫描完成。
