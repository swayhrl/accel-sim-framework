# 独立复核与实际检查边界

2026-10-26，主Agent汇总三个有界只读子任务；不共享修改生产源码。

- A：重新核对storage/RAM核算，35GiB并发ceiling未作为额外增长相加，ownE2 reserve不重复计。原full-model admission HOLD核算成立，含3条缺receipt历史保守保证，未擅自解除。后续独立设计复核确认同case收尾误用新模型准入；仅在完整原预留、自然DONE及明确写入/RAM硬限下使用continuation actual-headroom，不伪造原admission PASS。
- B：E1 exact身份、282option单delta、raw/terminal/64B0/32DRAM重提取一致；E1 archive range/full SHA、4项portable工具SHA、两个恢复Target各26行全inventory/metadata/fileSHA只读复核通过。E2接受后comparison.point重提取与已存variant逐项一致，TagFAIL/relieve/detach/closureerrors/mismatch均0。
- C：E2 live header282项键集与基线相同，唯一变化DL1 MissQ16→32，DRAM850。case-local genuine164 fresh proof与旧memberSHA一致；元数据未再漂移的Q/launch复用proof，不声称额外full-read。
- B：postrun_pins只读实际调用PASS。原spec52c1801b…未改，除shared entry外62pins+10env SHA一致；peer新增DTC前缀不匹配EP。准确措辞是去掉重复shebang/set-eu后EP dispatch body逐字保留，不是旧wrapper整文件suffix。

以上为源码、数据重提取及只读恢复验证；没有独立重跑第二份模型。新模型本身每端仅一次，验收不要求cycle改善或detach非零。

五项nonlaunch guard测试实跑，通过，real application forks0、real authority writes0。它们检查隔离消费、已消费拒绝再试、peer行不变及参数/容量边界；不能替代cache协议正确性fixture。

原T构造性压力、晚返回不污染新Tag等CPU fixture仅阅读既有源码和历史回执，本Goal没有新跑。实际E1归档/恢复及E2归档/恢复状态以各自回执为准，本文不单独授予科学接受。

新增收尾修复保留原admission HOLD：E2 archive17612800B已写164，关闭重开全SHA及两Target恢复通过，原登记CLOSED/reserve0。本地增量allocated35332096B，小于128MiB；没有启动model/help或修改peer预留。A仅设计审查，实际收尾由主Agent执行；B另做归档/adapter只读复核。

B最终实测只读闭合PASS：E2完整archive17612800B range/fullSHA806ebe44…，两Target各27行inventory/metadata/全fileSHA，4项supplement工具SHA一致；stageproof/closeout/currententry/spec/raw链一致。没有实际执行新的归档或恢复写。512MiB指两个主要Python进程包络，另有继承AS cap的短暂findmnt等helper。
