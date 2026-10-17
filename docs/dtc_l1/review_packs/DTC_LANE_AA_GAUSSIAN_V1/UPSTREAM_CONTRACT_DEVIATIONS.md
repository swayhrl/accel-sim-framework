# Observed upstream contracts: execution remains STOP

这些是本包 inputs/LANE_V、W、X、Y、Z 的带SHA快照，不把尚未发布的工作文件视作最终科学准入。X的已发布Framework及Core另经fetch-back逐blob/树绑定。上游交付时间与本包CPU准备重叠，初次close脚本检测到新证据后主动拒绝沿用“全缺失”分类；CPU_TOOLING_EVENTS.json保留这次刷新，没有模拟启动或UUID变化。

| Lane | 已核内容 | 对AA的裁决 |
| --- | --- | --- |
| V | K1待审合同选source的LDST invalidate **请求入口**为线性化点，继承源条件选择的SM，包含可重复idle-cluster、配置变化和带原guard的MEMBAR路径；先接纳的旧Ref/physical/generation须继续合法完成 | 可作为最小语义约束；不是K1实现/时序/数值正确性PASS，事件次数和模型支持域未闭合 |
| W | DEFERRED_SAFE_STOP；原访问分布与输入身份已核，地址/PC扫描因I/O压力暂停；跨kernel别名、同SM retained复用、动态invalidate调用次数均未证明 | 不认定Gaussian事件为0，也不从510个kernel直接推导invalidate次数；不启动性能矩阵 |
| X | SCIENTIFIC_STOP_SOURCE_EVENT_CONTRACT_MISMATCH；Core f8b34dd7仅增加STOP文档，src树等于6fba0136；没有注册新开关，没有K1 | 这是阻止所有新full点的已发布决定性证据。独立基线build/4项既有测试不能替代K1验证 |
| Y | 已观察独立SOURCE_AUDIT，确认X可执行源码与冻结基线一致，普通invalidate仅触达m_L1D | 支持“未实现”判断；没有独立K1 PASS可绑定 |
| Z | 已观察METRIC_DEFINITIONS/MISSING_FIELDS/PREREGISTERED_INTERPRETATION草稿，定义typed counters、累计终值、条件人群、cycle ratios和乘法交互 | 定义可供审查，最终发布未绑定，且K1边界表述尚需与V对齐 |

Z快照把K1描述为“kernel-boundary…无live Ref/pending/ownership的安全边界清除”；V则明确请求入口允许旧消费者仍存活，并禁止人为改成全局drain/kernel broadcast。二者不能静默合并成同一实现合同。本AA以用户“只响应原source-defined invalidate、失效后持有引用仍合法”为约束，保持STOP，不选用Z草稿中的额外安全边界来改写自变量。

Z的Q32/Q64/T0/T1/I/logI与本包的周期差主效应、加性交互可以并列；cycle quotient与speed ratio方向必须明确。本包已预先列出两种方向及公式，没有新测量、没有显著性或结果筛选。Z要求分母为0标UNDEFINED_ZERO_DENOMINATOR；缺字段仍UNAVAILABLE，跨单位/人群不可比为UNCOMPARABLE。本次所有新点未运行，不进行任何比率数值计算。
