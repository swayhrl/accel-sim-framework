# 共享资产库进度与独立审查入口 V9

日期：2026-10-27。EP-MAIN 延续现有资产工程；整个 Goal 尚未完成。本文更新 V8，保留历史证据，不将 CPU 候选、入流程或 HOLD 当作资产交付。

## 已核定状态

- SM70 V13R2 原监督1424444/start_ticks974977586、driver1424449/974977662和唯一恢复companion1431348/975253539仍为同一活进程。目标对象尚无 COMMIT，同run尚无 EXACT_BATCH_COMPLETE，不能声称归档完成。
- streamcluster 的原完整记录验证已自然结束：1611 kernels、5518423824 records、1611 source files通过。原worker继续POST2；归档、receiver读回、CURRENT闭合仍未完成。已保存原全量验证、map与EXECUTION小元数据检查点，不需要为恢复CPU后处理重复GPU采集。
- 最近已核定目录为41常规/41裁剪；原33待采及SDK/reduction有限边界继续。历史4失败中3项已有精确合格successor；原失败记录不改。剩余simpleTemplates精确输入不等同于其他Templates。
- 161专项全部进入真实CPU适配流程，V4独立验收全161行、errors0、peak2；当前主等待ISA117、runtime14、input19、mapping5、精确GPU4、variant1、SDK1。269为重叠证据请求数，不是workload数；不据此授予trace/consumer/科学资格。

## 本轮真实推进

1. **109真实资源及验证器组件**：独立user-systemd服务实际落实20GiB memory.max、Swap0；8个不同CPU worker继承私有ext4 OFD并自然退出。另32MiB自有测试组实际OOM只终止本组新CPU fixture，清理闭合。实际账户测试发现原nice19→15越权提升问题，Root V5改为只降低优先级。
2. **Mother集成修正**：Root发现并修复validator ACK目录与worker数误传POST两处问题。POST保持2；新的1/2/4/8验证器通过真实109服务basic及98项组件正反例；实际CLI8闭合回执被Mother真实判定函数接受。当前仅组件验收，未部署、未排队、无新GPU或生产锁。
3. **原streamcluster有效工作留存**：完整记录验证绑定原f9/f4、binary/producer与map。检查点不是原始body重新哈希或归档COMMIT，不据此扩张资格。
4. **SM70清理与恢复审查**：R6独审发现弱CLOSED/START身份关联和begin失败FD泄漏，冻结a27修复。Native174仅对本次新建空cgroup测试memory委派，返回EBUSY；自有空组已移除，未移动其他进程或修改父限制。R7改为新的显式进程AS候选，原8GiB cgroup模式保留，不伪称16GiB VM预算等于物理内存硬限额。独立实测进一步发现3处构造阶段异常清理缺陷：Popen失败泄漏预算锁/FD，ticks读取失败或parent_started异常可留下已启动runner，而START/CLOSED尚未建立。全部自有探针已精确清理；R7明确拒绝生产准入，R8须先修复这些路径，再独立重放。未授予实际Native body读取许可。R8逐对象并行恢复另在有限CPU准备。
5. **采集首次授权协议**：V6同host CPU首次授权流程经Root完整源码审查和两族独立复放，保留首次30s、真实idle及fresh双clock门禁。V7固定GPU leaf桥接代码和CPU回归已冻结，但174 keeper到109的精确startup/witness/remote-cleanup ACK链未闭合，生产资源authority尚缺，状态明确HOLD。V8正在实际补齐该链；没有将其称为109可启动入口，也没有执行GPU。

## 审阅顺序

先读 snapshots/root 下Root正式验收，再查 snapshots/ordinary_v5 的原字节Mother、适配器、资源校验及前像。CODE_MANIFEST.json和本页 SNAPSHOT_MANIFEST.json 均保留原始SHA与NAS源路径。

- ROOT_BOUNDED_VALIDATOR_PIPELINE_V5_COMPONENT_ACCEPTANCE_V1.json：真实109服务、98组件用例、Mother ACK合并及非生产范围。
- ROOT_109_USER_SYSTEMD_CPU8_FD_MEMORY_QUALIFICATION_V2.json 与 ROOT_109_USER_SYSTEMD_MEMORY_QUALIFICATION_V1.json：实际资源/私有租约测试，不能用空闲数值冒充预算。
- ROOT_STREAMCLUSTER_F9_CLOSED_VALIDATION_CHECKPOINT_V1.json：原验证闭合检查点及局限。
- ROOT_FIRST_ADMISSION_V6_CPU_PROTOCOL_ACCEPTANCE_V1.json：仅同host CPU协议验收。
- R7 ROOT_ENTRY_V2.json / resource delta / process_budget_r7.py：显式AS候选及未准入边界。
- V7 ROOT_ENTRY_V7.json / FINAL_REPORT_V7.json：固定GPU leaf候选与明确未实现部分。

## 完成条件与保留项

仍须严格SM70长归档成功、125输入/22769对象/25149成员的真实Native读取与恢复、5类consumer适用验收；补齐剩余4080 trace和裁剪，实际解决161专项，完成公共工具及跨项目验收。合成trace和CPU组件测试不能替代全量实际资产验证。

所有大数据、代码及日志持久化真164；源KEEP、释放0；Native实际余量至少5GiB。健康原任务不打断，无新科研性能模拟、无历史/资格/预算改写。外部ChatGPT审稿尚未收到。用户提出重建Goal时，工具仍返回旧Goal active并拒绝创建；目标修订全文已另存164，不虚标旧Goal完成。

本文和精确小快照将提交原分支并API读回，远端读回回执单独存真164。此页不是公共入口启用或最终整库完成回执。
