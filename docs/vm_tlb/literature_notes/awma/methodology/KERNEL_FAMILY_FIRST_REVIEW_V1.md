# Kernel-family-first评价规则 V1

日期：2026-10-02。前瞻方法规则，不追溯改变历史实验合同。

1. 固定目标族：phase/语义算子/实现/shape-regime/dtype/forward-backward/必要前序。不能只按名字，也不能事后只选赢家。
2. 同时报告四层：直接作用工作、计入必要准备后的净族成本、真实覆盖率及其他族退化、完整operator/应用效果。
3. 初始化、排序、list、数据转换、同步和输出提交不能移出净成本；共享准备计一次，明确摊销合同。
4. 未测非目标族记UNKNOWN。代码未改不等于无cache、occupancy、编译或调度副作用。
5. 完整应用5%仅是指定scope投入门槛，不是所有机制的统一否决门槛；局部与系统两个决策分别记录。
6. kernel级positive不自动代表新硬件。已有软件/算法能力、资源代价、真实性、独立验证分别审查。
7. 保留负例、数值失败、无输入、profile缺失、oracle和软件已解决的区别。未知不能变negative。
8. 回顾重分组标RETROSPECTIVE；旧discovery不是新holdout。不改变旧STOP，不重启R20。
9. profile只做解释，未插桩测量负责时延；kernel duration sum不等于wall贡献，graph节点与调用关联必须准确。
10. 下一轮family与噪声协议在采数据前冻结。失败先存输出和身份再结束；自动记录锁时段和环境。
11. 机制驱动小原型与现象驱动仍可并行；不强制先测完完整应用才能探索，但最终不能隐去实现成本。
12. 本文是评价方法，不是任何节点执行授权。

## 建议字段

family_id、source/callsite、phase、shape、dtype、direction、context、baseline/candidate identity、target gross time、mandatory preparation time、net family time、baseline time share、non-target median/worst regression、complete-region time、numerical status、novelty status、evidence level、scope、operational status。

若fusion改变kernel数，比较相同语义工作集合，不强制单个symbol一对一。新工作使用在线可得信息，不能用未来耗时或事后最快arm选择宣称可部署方案。
