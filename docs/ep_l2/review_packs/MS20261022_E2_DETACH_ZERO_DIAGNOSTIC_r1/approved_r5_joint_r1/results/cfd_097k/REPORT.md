# cfd_097k: r5完整F诊断独立接收

E056_47abdc7f 为 CURRENT_ACCEPTED_DIAGNOSTIC_POINT；真实exit0、完整143129372条指令、79157周期、5条命令、64slice及source/input/ROC1/退尽独立核验通过。不是新S/F配对。

目标set联合观测：覆盖1524394个head-cycle exposure，需新Tag的MISS/FAIL合计162681，对应reserved-way最高3/16；全部覆盖观测最高4/16。已覆盖范围内没有全16-way RESERVED的新Tag请求，生产commit实际Tag失败0、relieve调用0、成功detach 0。

结构可用RO way exposure为105076，它与“需要解除全reserved阻塞”的触发条件不同；不能将不同维度边际拼成联合。上游跳过218239个head-cycle，其raw压力为NA，不能声称全局Tag永远充足。完整物理kernel阶段及真实requester/eligibility/route/admit/early联合见独立报告。

仅代表本次输入/配置已覆盖路径，不由CFD推断其余输入；保留全部负结果、旧计数、历史FAILED/INCOMPLETE/HOLD。原结果：/workspace/ep_l2_ms20261019_e_results/E056_47abdc7f。
