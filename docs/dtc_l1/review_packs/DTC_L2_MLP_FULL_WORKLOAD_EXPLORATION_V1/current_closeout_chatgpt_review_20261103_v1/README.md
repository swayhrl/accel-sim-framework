# DTC 已登记实验收尾审阅包 — 2026-11-03

当前只收尾原登记实验；CH 匹配与组合搜索留下一阶段。请优先阅读本页、[完整35输入结果表](RESULTS.md)、[状态与各参数GM/覆盖率](STATUS_AND_METRICS.json)、[失败清单](ARCHIVED_NEGATIVES.json)。全量配对值、各套件统计、输入/SHA/UUID与原始/独立引用角色位于 REPORT.json.gz；350格CSV位于 results.csv.gz。

## 当前状态

- 原始350格严格接收330格（324次原始新测量＋6个合法P0引用）；18格原始归档失败、1格scan/M16原始工程负例、1格正在运行。原始失败全部保留，未用修复结果覆盖。
- 独立 named 视图335/350，缺15格。其增加来自预先约定的R2与4个IR引用，不能写成原始accepted增加5格，也不能选择最快/PASS来源。
- 原360个实际启动身份已全部消费，未启动0点；当前仅 lavamd DH-Q64 在跑。UUID `77d92c33-7dd9-4b4a-a756-dee52e41e4ee`，PID 3403414，start_ticks 1044152256。历史同输入DH配置约4.6–6.5小时，本点暂估启动后5–7小时（北京时间今天20:00–22:00，另加归档验证）。实际运行状态不代表accepted性能。
- 最后一点曾因最新RSS预测比canonical资源账本高9,830 bytes而被 OFFICIAL_FORECAST_REFRESH_REQUIRED 挡住。现通过原生官方未启动身份资源刷新接口修正，仅更新RAM/RSS/AS资源字段及其SHA；输入、源代码、模拟配置、时钟、预算和历史UUID均未变。未新增grant，未重跑失败。

## 当前能支持的性能结论

原始结果在同一31程序集合上：F128 GM=1.008258561，F256 GM=1.011580804。F256可用33程序GM=1.022440468，分母不同，不能把它与31程序GM直接解释成新进展。E384/E768的有效匹配 cycles 相同；扩大entries的收益已饱和至少在现有可比集合上成立。全部正负案例和每程序cycles保留在RESULTS.md及原始结构化结果中。

这些是DH相对自身P0的收益。尚无非P0 CH匹配结果，不能推出DTC相对CH优势扩大、统一最优配置或等面积硬件收益；不把不同参数的每程序最优值拼成统一GM。缺失计数器仍为缺失，不作为零。

## 历史长尾单独统计

固定3条EP历史任务已全部 STRICT_ACCEPTED：SYRK S=22,589,807 cycles，F=20,263,252 cycles，S/F=1.114816x（F周期下降10.30%）；lavamd F=5,738,976，对其已严格接收S=5,581,479，F周期增加2.82%。EP机制、binary/Core/Framework/1132MHz core合同与本轮DTC不同，不混入DTC GM。精确配置差异与每项来源在 REPORT.json.gz historical_fixed3 中。

ATAX/MVT/BICG downstream18仍为18/18严格归档通过。完整CH/DH P0=1表见RESULTS.md。PQ只改变partition queues；PS改变DRAM850→1700MHz，因此PS保持与当前固定850MHz扫描分开。

## 后台及发布修复

10月29日遗留的空index.lock没有持有进程；在取得唯一发布程序git互斥后保全并移除。原发布程序已自行恢复旧pending提交（3091dde），未reset、未改写其STATE或启动第二个publisher。本包另行提交当前完整结果，避免等待下一次30分钟快照。

独立分析进程继续每分钟消费结果，既有唯一publisher每半小时提交。还修正了分析进程终态HTTPS核验未继承代理的问题：同源码、同配置、同namespace授权的数据分析进程以已验证代理重启；没有重启/干预模型、模型owner或发布程序。剩余点完成后，会自动刷新结果表和发布。

## 请ChatGPT重点审阅

1. 330原始accepted、335独立引用与缺失/负例的科学身份是否表达清楚；不得把335替换成原始统计。
2. 在固定人群、可用人群和套件子集之间比较GM是否公平；F256的小幅平均收益是否足以支撑下一阶段CH匹配。
3. SYRK及lavamd负例的资源保护停止，是否留下需要另行授权的诊断；本轮未自动重跑。
4. EP历史结果、PQ与DRAM1700MHz PS是否保持独立合同。
5. 下一阶段CH统一配置及组合搜索的优先级。请勿据本包把full35阶段标为全部成功，也不要改英文v0.23母稿。

## 证据位置

174 native：`/root/data/dtc_l2_mlp_exploration_20261027_v1`；164归档及本包源：`/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1/coordinator/CURRENT_CLOSEOUT_CHATGPT_REVIEW_20261103_V1`。原始结果UTF-8及其SHA完整保存在 primary_structured_RESULTS.jsonl.gz；R2/IR/工程角色在 separate_structured_RESULTS.jsonl.gz 中独立保存。全成员SHA见 MANIFEST.json。
