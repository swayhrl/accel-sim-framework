# 共享资产库：独立验收与修复进展 V6

Goal 保持 ACTIVE。本报告延续统一 SM70/V100 与 RTX4080/SM89 资产库目标，不将候选、CPU PASS 或单项完成当作整库完成。RTX 当前 CURRENT 为 41 常规 / 41 裁剪；exact161 已全部进入真实 CPU 适配流程，但仍存在 255 条非独占证据请求。

## 本轮实际完成

- Root 在全新真164私有目录逐字节核验 R5 production21 文件，独立执行真实安装→prepare/publish/restore/cross/finish、publish 与 restore 收据后崩溃恢复、7 个协议反例、2 个原监督锁反例及 37 项资源边界检查，均通过。仅使用三对象合成数据，未读真实 trace 正文、未生产安装/启用、未写 Native。
- 额外 Root 反例发现真实阶段时限漏检：restore 预算 2 秒，原 restore_one 前插入 3.1 秒 CPU 延迟，实际 4.7279 秒后仍报告 PASS。生产模板另有 14 天预算与代码 7 天上限不一致。原候选冻结保留，新的 deadline 传递修复正在私有范围实施；未批准正式125输入恢复。
- Root fresh 核验 WARPSYNC V2 全64引用，独立复放 31+41+10 项原 CPU 测试均通过。额外反例确认 known PID 的 header-only、unavailable 和 missing 活动采样均会被误接受。已排入独立私有 guard 修复；没有 GPU 准入或 producer SO 加载。
- simpleTemplates Epoch V3 已冻结40文件候选，按 exact ELF owner/PC/full SASS/有类型操作数合同核验立即数，并拒绝缺失或不可解释的 known-PID pmon 样本。原8b12 SO和CU/INC/H不变；Root已读全部新门与运行代码差异，另一个独立CPU lane正在复审。尚未授权真实采集。
- reg255 角色/控制流有限工程已交付全部5888 PC：4940明确角色、948精确HOLD；34直接目标闭合，21控制位点保留未知。6包65580 PLR行完整对照，支持的52827行匹配，其余差异原样保存。尚未Root正式接入，原5个HOLD保持。
- 真实SM70 consumer decoder正在有限CPU集成：DTC原decoder已对合成记录实际执行；EP依赖仍在准备。不能据此宣称全125输入或全部ISA已兼容。一次旧EP partial-clone git archive引发自动lazy-fetch，已只停止本次owned helper/子Git并留证；不声称该scope Native写0，不清理原.git未知文件。

## 当前后台边界

Root最近核实 SM70监督1424444/driver1424449、唯一恢复1431348、RTX1376608、SDK50k1410582、reduction entry1501892与issuer1501891均精确PID/start_ticks匹配存活。SM70 driver rchar从889.62GB增至918.19GB；目标COMMIT与同run EXACT仍缺，读量不代表完成。109 whole-record validator849258/start_ticks361246237仍运行，rchar50.29GB，不以压缩输入大小为百分比。

reduction控制器已真实arm并等待原批准自然边界；尚未因此声称GPU窗口已执行。所有现有健康进程保持原样。Native最近可用37,774,176,256B，源KEEP，源释放0。

## 后续真正交付门

修复并独立复放新的R5 deadline版本；在Source2真实COMMIT/同run完成和监督owned cleanup后，冻结真实归档身份、proof relocation及Root完整spec/policies，完成Native合成集成后才执行125输入/22769对象/25149成员/972603859656B的正式恢复与跨项目验收。公共/root/workspace/assets/traces路径存在不等于公共工具和全范围读取已验收。

继续原4080队列、已批准SDK/reduction边界与exact161实际适配；对新合法证据增量接入，分别记录trace、producer、consumer和科学资格。没有新科研性能模拟、没有改变历史结果或科学预算。外部ChatGPT审稿未收到。

本目录 snapshots 与 source_snapshots 为小型精确证据/源码快照；大型payload、运行日志和原始证据保留真164。SNAPSHOT_MANIFEST.json可核对原路径和完整SHA。候选失败和已发现缺陷全部保留。
