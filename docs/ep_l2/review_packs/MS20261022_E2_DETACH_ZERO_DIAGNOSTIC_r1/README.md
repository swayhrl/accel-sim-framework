# detach=0：一次性交付的诊断准备

目标是把“RO未进入、没有局部压力、压力与候选未重合、复用保护、执行路径/闭合问题”分开量化。最终可得到可靠的零结果；不以产生非零detach为验收条件。

**本轮准备和投递，不启动完整应用。** A2在独立诊断分支准备观测实现、有限工程控制与producer交付；E2独立验收新身份并形成单端精确提案；D同步准备漏斗分析；C复用已完成正向证书，仅小文件绑定确认。原main61及50次历史、唯一controller、T0、10/24GiB累计生成与其他项目策略不变。

关键源码遗漏：preview会将raw Tag RESERVATION_FAIL在存在可detach候选时改成MISS；无候选时可能不进入access。因此必须在真实frontend head/physicalcycle观察点采集原始压力，再与commit/relieve分开对账。不能仅靠执行端失败数或现有TAG_SET_PENDING判断Tag充足。reuse_seen是黏性的，relieve又早于若干后续资源门禁，detach成功也不等于触发请求成功接收。

交付流水：

1. A2、D先完成上一轮E54本人最终小回执，不重复旧工作；随后直接接本包。A2先发schema/source设计，再一次性交付独立诊断producer、控制证据及成本。
2. D无需等待binary即可准备统计分母和结论表；C无需重扫trace。E2同步准备独立校验器。
3. A2真实release后E2验证观察不改变调度/机制、输入与新资格，立即给出精确一端配置及成本供最终批准。无需等无关lane。
4. 后续若批准，仅原中央流程执行一次完整SGEMM诊断F，真实终验后即交D。不是新S/F性能配对，不借旧S冒充新binary锚点；不并行执行旧main61单F提案。

详见[计数合同](COUNTER_CONTRACT.json)、[资格控制](QUALIFICATION_AND_ENGINEERING_CONTROLS.json)、[分工](BATCH.json)、[未来单端提案](EXECUTION_AND_COST_PROPOSAL.json)、[预登记结论](DECISION_OUTCOMES.json)。时间参考旧F约31分钟，新路径暂估30–60分钟；新增观测/正向RO成本须实测，未承诺完成时刻。未来单端输出384MiB内含诊断summary64MiB，运行加E metadata/collector暂定544MiB；A2 build/native物理增长另报并纳入实际门禁。

共享队列会投递至原A2/D/C，发布不等于本人ACK，也不能唤醒结束的窗口。若窗口空闲，只需一次“读取E2最新诊断任务包并按原队列推进”，无需粘贴科研材料。无后台轮询器、无第二调度器。
