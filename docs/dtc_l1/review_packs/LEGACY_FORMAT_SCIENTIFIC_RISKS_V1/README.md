# 三项独立历史地址格式科学风险

本包按用户选择，将 Btree、LUD、2DConvolution 分别登记为 **OPEN、科学适用性高优先级风险**。高优先级表示需要审查来源和解释边界，不是已有结果错误判定；也未证明它们不受影响。没有新输入解释、主parser修改、trace改写、状态/HOLD变更或模拟器启动。

Hotspot V2 的 [独立资格报告](../DERIVED_INPUT_QUALIFICATION_CANDIDATE/QUALIFICATION_REPORT.md) 已先于本报告在提交 `0bd0e603f48a93414c47583b7c205595600e72af` 推送并fetch-back核对，供ChatGPT最终审查。它的派生输入定义、六PC/122760条变更、独立地址核验、采集身份缺口及最小新输入配对范围均已交付。本包的三项风险不再阻塞该资格包，也不因相似编码现象沿用其地址模型。

| 独立报告 | 本轮细查成员 | 格式风险记录 | 涉及可缓存global load | 关键有界结论 |
|---|---:|---:|---:|---|
| [Btree](btree/REPORT.md) | 1/2 | 6000 | 6000（其中5792条条件地址不同） | 单PC1c40/LDG.E.SYS，full32原始列表；5792条的sector/line身份可变，单条数量仍1 |
| [LUD](lud/REPORT.md) | 63/94 | 57536 | 11904 | 95个kernel限定PC/opcode项；另有7936条STG和37696条shared；保留0x80/0x40锚点反例 |
| [2DConvolution](2dconvolution/REPORT.md) | 1/1 | 40940 | 36846 | 10个PC各4094条；version3同时存在于mask修复前后，不能认证producer合同 |

## 范围与证据

只读取既有格式筛查标记出的65个成员、1274544001字节，顺序单CPU约75秒；没有重读未标记成员，也没有重复629成员完整审计。对每个选中成员，结果都与旧mode0_excess/nonzero-anchor数量完全匹配。既有body SHA身份收据复用；本轮只检查文件size并为风险原始行/代表行计算SHA，**没有重新声明全正文SHA已验证**。来源/几何/ISA/指令总量或native输出不在这个细查范围。

每个程序有独立 `RISK_SUMMARY.json`、完整 `PC_OPCODE_RISK_COUNTS.tsv` 和报告，明确事实、条件推论、证据缺口及建议最小处理范围。公共 [RISK_DETAIL_RECEIPT.json](RISK_DETAIL_RECEIPT.json) 记录65个成员、原身份收据、计数对照和完整104476条风险索引的位置及压缩/解压SHA。外部index包含每条风险记录的workload/kernel/PC/opcode、行号/字节偏移、原行SHA、冻结地址及备选地址向量。它是诊断表，不是候选科学输入，不提交Git。

模式1枚举全部历史encoder兼容 first(E)=0..min(first(P),30)，保留冻结消费结果，不选择其中之一。mode0只比较原full32向量的历史lane关联与冻结parser前popcount(P)项消费。CPU projection分别计算32B sector和128B line的字节footprint；shared服务使用明确参考几何（32banks、4B word、单warp分区、unlimited broadcast），与冻结Core“每lane首个地址、每bank不同word最大数”的逻辑一致。该参考config的身份已有收据，但没有证明所有历史arm配置与它等价。footprint不是已执行的cache状态、完整coalescer事务或时序模拟。

[CONSUMER_AND_ENCODING_SOURCES.json](CONSUMER_AND_ENCODING_SOURCES.json) 绑定冻结Framework/Core源码、两个都宣称version3的历史编码源及几何参考config；本地文件已逐字匹配其指定Git blob。[CAPTURE_FAMILY_METADATA.json](CAPTURE_FAMILY_METADATA.json) 仅保存三组代表header/launcher/list小文件，没有把路径/版本标签升级为不可变采集身份。独立三条原始记录向量的CPU测试覆盖：LUD不同地址但相同bank服务、2DConvolution跨sector/line计数反例、Btree单请求数量不变但tag身份变化。

## 最小处理边界

建议审查者分别决定是否需要后续独立窗口：Btree先做单成员/单PC的producer关联取证；LUD先做两个kernel的global-load/store锚点来源；2DConvolution先绑定修复前后producer合同，再决定是否需要10个PC的动态E重建。没有无界源码/工具链重建承诺，没有新增候选输入、重跑矩阵或调度建议的实际执行。

继续保留原始结果和所有既有HOLD，当前准入状态不变。需要采纳新地址解释、调整支持/外推范围或作新科学结论时再交用户审查；之后只有Lane A拥有正式准入与独立配对实验登记权限。不得用这些局部发现自动宣告整个负载不受影响/已错误、静默剔除负载，或以新旧输入混算加速比。FILES_SHA256.tsv及VALIDATION.json绑定本包证据与保护核验。

## 重现本轮细查

先复用上一包已产生的FORMAT_MEMBERS.tsv及原r0 inventory；不要重跑完整629 auditor或再次执行整个11负载筛查。输出必须在独立新目录。

```bash
python3 util/dtc_l1/test_legacy_format_risk_detail_v1.py
python3 util/dtc_l1/legacy_format_risk_detail_v1.py --format-members docs/dtc_l1/review_packs/DERIVED_INPUT_QUALIFICATION_CANDIDATE/FORMAT_MEMBERS.tsv --inventory docs/dtc_l1/iscas2027/service_closure_174_v1/review_pack/r0/PAYLOAD_MEMBERS.tsv --output-dir /workspace/dtc-hotspot-format-174-v1/reproduce-three-risk-detail
```

枚举/计数结果与PC表、index解压SHA应一致；elapsed time不是复现身份。该程序没有trace规范化、parser写入、结果接受或运行调度功能。
