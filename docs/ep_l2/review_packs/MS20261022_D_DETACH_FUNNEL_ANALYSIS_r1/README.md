# D：detach=0诊断分析准备（r1）

本lane准备已完成；尚无新诊断应用数据。响应E2-00000059-feda8eeb49a1，完整读取E的10文件任务包（冻结1b562df6，事件发布258865b0）。[E54最终科学结论](../MS20261022_D_RO_POSITIVE_FINAL_SCIENTIFIC_DECISION_r1/README.md)已交付，直接复用。

四个不能混淆的层次是：真实frontend head/物理周期看到的原始Tag压力、preview实际是否咨询/改写、ft_access实际relieve/握手、victim事务闭合。原始压力不能从最终FAIL/MISS或detach0反推；重复preview不能增加分母。原生非RO路径可能从未咨询relief，即使只读shadow看到同Set合法候选也保持原路径。

[分析合同](ANALYSIS_CONTRACT.json)列出五种计量域、带适用条件的等式和NULL/NA/覆盖规则；[结论表](CLAIM_OUTCOME_TABLE.json)与[原因树](CAUSE_TREE.json)预登记零、非零、路径拦截、成功后拒绝和无效结果。pending eligibility使用required-not-ready，不冒充issued-not-ready；reuse_seen在合并waiter退出后仍黏滞，不能重置。真实detach先于后续资源门禁，成功detach不等于触发请求接收，更不等于程序加速。

[表图接口](TABLE_AND_FIGURE_INTERFACE.json)按GLOBAL、64slice、requester/victim kernel或明确interval/unattributed组织。重叠interval、原因mask、多slice/重试/sector等待不相加成为GPU stall。[控制覆盖映射](CONTROL_TO_CLAIM_MAP.json)仅关联E的16类既定控制，不额外要求D运行。

D语义字段不是A2实际日志字段。A2发布精确schema后由E独立检查全部enum分支（包括可能的existing-target HIT_RESERVED）、源代码/非干扰/资格，再绑定已接受小摘要；D不另建验收器，不以缺字段补0。既有E accepted-evidence投影流程继续使用，新增独立diagnostic命名空间即可，不重复原图和trace扫描。

新任务默认仅未来一个SGEMM正向RO诊断F，不是S/F性能对。旧main61单F提案依E59延后且未批准；不会联合启动。当前没有新binary/Q/正式应用记录，全部结果保持UNKNOWN。成功或零detach均不证明T独立性能收益。原MAIN、独立SGEMM、容量诊断及EN-v22保持原样。

[本lane回执](D_INCREMENTAL_RECEIPT.json)记录完成范围和后续依赖。A2/C/E分别签自己的交付；D不等待binary完成本次准备、不重启Goal，不建立后台轮询器。
