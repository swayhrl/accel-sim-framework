# EP-L2 workload覆盖：首版决策报告

当前完整方案主S/F确实只有 **5个独立workload**：Conv、CFD、DWT、SAD、Vector；共21次动态kernel调用/端。13个条件控制和同五输入的新capacity OFF/ON不会增加独立workload数。原七输入中的FWT仍INCOMPLETE、Btree仍HOLD；原七输入GM仍UNKNOWN。所有负结果与费用保留。

**判断：五个足以支持这五个精确输入的案例与受控机理分析，对跨GPU应用普遍有效的结论覆盖偏窄。** 现有五个MAIN F的成功Tag detach均为0，动态working set、地址不规则度及DRAM饱和度缺少量化。补输入应先填机制空白；不能按已知F加速比挑选，也不能靠多kernel、多配置或同应用尺寸变化凑应用数。

可把8–10个独立workload作为覆盖工作目标，这是本轮建议而非投稿硬门槛。先审查最接近现成证据的两项，再根据完整输入可得性选择1–2个有增量的代表。当前没有新的探索候选已取得E全资格可立即启动。

|优先级|对象|已有证据与缺口|若以后单独批准的运行成本|
|---|---|---|---|
|P0|FWT恢复|原登记完整19kernel/791609344指令；旧main61资格仅在全部身份匹配时复用；缺新恢复授权，新capacity binary下FWT资格不存在；旧INCOMPLETE不追认exit0|2次；结果硬预留768MiB；旧版本成本先验S80–110min、F85–120min，不是已接受完成耗时|
|P0|SGEMM medium|D已有完整2.216GB、1.659b指令、语法/非原子证明；仍缺E完整producer/input/oracle/profile资格与正式探索登记|2次；硬预留768MiB；真实walltime未知|
|P1|不规则SpMV/BFS或迭代Hotspot/stencil中1–2项|有官方源码依据，尚无本地完整、已资格的新输入证明；旧SpMV/Scan/Btree HOLD不得提升；按中性画像及完整来源选择|每对2次、硬预留768MiB；实际准备量与walltime待证|

新输入应独立登记探索集合，冻结候选、选择标准及排除原因后再观测新F结果；原七输入/32行身份及GM分母不变。若将来汇总扩展集合，必须明确新比较范围。保留负结果、零触发、语义失败及不合格候选，不能把新增成功输入替换旧失败。

原子histogram暂不进首批：当前atomic/RED、完整data/oracle与idealized ON语义未证明。也不直接接纳新H200 ML trace。官方2026-10-20 v2.0.1更改trace发布方式且说明部分kernel被剔除，不能默认旧公共suite的完整trace今天仍可获取，或新格式/指令兼容冻结binary。[官方发布说明](https://github.com/accel-sim/accel-sim-framework/releases/tag/v2.0.1)。

本轮为只读小型元数据、文件stat、已有统计和一手网页调研：**零完整应用、零native启动、零大trace下载/正文扫描、零中央台账修改**。取消次数/时间门槛的修订在独立工程流程中处理；本调研不授予新科学条件、重试或结果额度。后续仍保留新增10GiB/总24GiB、每端384MiB及所有物理资源保护，运行前重新按真实增长与未释放的结果预留准入。

本地和机制子报告的2/5capacity计数是各自采集时快照；本次root汇总时SAD已新验收，实际为 **3/5**（CFD、Vector、SAD），各对已由原流程推送回读并交D。主模拟继续；本调研没有重启或增加正式端点。

- [本地完整输入及来源盘点](LOCAL_COVERAGE_INVENTORY.md)
- [机制覆盖与缺证审查](MECHANISM_COVERAGE_REVIEW.md)
- [官方来源与候选语义调研](PRIMARY_SOURCE_WORKLOAD_SURVEY.md)
- [机器可读决策、准确路径与来源SHA](DECISION_REPORT.json)
