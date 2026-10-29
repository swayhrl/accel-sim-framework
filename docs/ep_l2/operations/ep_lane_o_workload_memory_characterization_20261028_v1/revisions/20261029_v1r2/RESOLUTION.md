# Lane O V1R2 审查问题落实记录

基于独立审查提交`4e026ac982e7802357810efe7be683a57794ef0b`。本次落实仅修改文档和新增小型派生表；无Core候选、构建、CPU fixture、仿真或正式账本写入。

| 问题 | 已完成修订 | 关闭方式及保留边界 |
|---|---|---|
| R1 ingress与first-head混用 | MEASUREMENT_CONTRACT固定四个边界，COLLECTION_PLAN/METRICS及M/V附录按其解释 | 设计歧义已关闭。旧head数据不回填入口；实际ingress指标仍NOT_COLLECTED，不声称采集已经完成 |
| R2 精确受阻百分比缺同人口证明 | 定向检查Conv/Scan共22份≤1MiB的小JSON，总1,086,440B，无absorbed/L1_WRBK投影；O2与W附录撤下精确发生率 | 以收窄结论关闭当前论文表述问题，原始distinct/observations不改。零例外尚未证明；无需为此重跑或解压raw |
| R3 单个S配对泛化到F/WV | NI_MATRIX逐路径列CPU/应用证据需求；COLLECTION_PLAN撤销固定4+1足够假定 | 设计问题关闭；运行资格仍NOT_PREPARED/NOT_QUALIFIED，由Main按实际候选补齐，不是新增启动许可 |

[DENOMINATOR_AUDIT.json](DENOMINATOR_AUDIT.json)保存22份小文件的路径、大小、SHA及字段搜索结果；未保存或扫描任何Trace正文。没有匹配字段不等于各运行的L1 writeback为0。

PILOT_GAPS以完整输入SHA连接既有W/V/M冻结投影，区分可直接复用、实现已有但未投影、缺动态联合、旧证据身份待核验和模式N/A。它是4个候选输入的缺口表，不是4个新模型，也不替代42程序覆盖母表。

原始冻结JSON/CSV和旧审查正文保持字节不变。原REPORT_QA仅代表第一阶段一致性，V1R2另有REVISION_QA.json和更新的根SHA256SUMS。最新交接见根MAIN_HANDOFF.md。
