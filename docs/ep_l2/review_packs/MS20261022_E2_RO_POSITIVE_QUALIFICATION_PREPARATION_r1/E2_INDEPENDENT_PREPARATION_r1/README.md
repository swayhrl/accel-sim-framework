# E2已完成的独立准备与Goal跟踪

用户要求启动Goal并并行做可独立工作。实际Goal已创建，仅协调本轮RO资格交付；约每5分钟前台查C/A2/D远端HEAD，变更时读取新增小型事件/证据。不建立后台poller/第二controller，不重启历史Goal，不增加应用许可。

C、A2、D已各自发布真实本人ACK并自报WORKING；D第一份FWT模型内零可认证行/SGEMM未知回退增补已核验接收。不是从E2投递推断ACK，也不从STATUS推断进程/lease。

E2并行完成：

- 旧S复用合同：E047仍有效，但manifest/ranges属于auxiliary资产，SHA进入比较不变量，原accept_pair不能直接接受旧S与新正向证书F。若申请只新增F，需要显式的基线等价复用/比较规则修订；不改旧端点、不全局放宽不变量。否则另提两端新比较，均未获启动批准。
- 成本：旧SGEMM S/F实测29.23/30.72分钟，RSS约7.85GiB；两端allocated合计190201856B。正向RO可能改变流量/占用/耗时，这些不是未来上界。单新F建议申请544MiB总增长封套；两端方案928MiB，含资格metadata与collector，均不是旧额度续用或当前资源PASS。
- 正向证书的十项准入/解释清单：准确输入、C工具/证书/域、独立制品验证、既有native适用性、新Q、比较规则、预算/资源、完整终验与应用触发声明均分开。技术验收不得以detach>0或性能有利为前提；正常的零/负结果照样保留。

仍待C实际正向覆盖或ZERO/MISSING，以及A2源码/native适用性与D最终候选决定。已接受旧S/F、累计50、原T0与当前累计10/24GiB政策保持不变。本轮新增app/native/build均0。

第二次有变更检查：已接收A2静态适用性图、C资源/输入预检、D条件决策及成本增量；它们不等于C最终覆盖或正向资格。A2十二个源码blob与d010逐一匹配，无新native。A2明确已有F与WV_M_ONLY的T条件对照源码支持，但没有因此新增控制授权。

成本合并澄清：C预检另列256MiB监控增长上限，E预案544/928MiB未包含这项。保守全部组件为800/1184MiB两项互斥包络；未来按C实际已生成及剩余增长去重核算，而非重置或重复计费。

补充：E2已直接核对d010 ro_init的OFF路径，确认S两开关OFF时m_ro为空，证书不会激活RO runtime；见S_OFF_NONINTERFERENCE_SOURCE_PREMISE.json。旧S复用仍须C精确制品、新F Q及显式比较合同批准；已备BASELINE_EQUIVALENCE_AMENDMENT_DRAFT.json草稿，所有新F/证书SHA保持null、未登记不可执行。
