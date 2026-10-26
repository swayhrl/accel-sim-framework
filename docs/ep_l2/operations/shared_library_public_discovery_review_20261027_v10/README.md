# 共享资产库公共目录查询验收 V10

2026-10-27，EP-MAIN。整个资产库 Goal 继续运行，尚未完成。

## 新增可用入口

174-new同一项目命名空间现在可从任意项目目录直接运行：

```sh
/root/workspace/assets/traces/tools/trace-assets-list
/root/workspace/assets/traces/tools/trace-assets-list --architecture SM70 --program COVAR
/root/workspace/assets/traces/tools/trace-assets-list --architecture SM89 --program vectorAdd
```

这是**只读元数据查询**：显示有什么、位于哪个精确输入/资产范围、状态证据来自何时。它不运行应用、不读trace body、不恢复、不授予模拟器或科研资格。完整公共物化/恢复工具仍未启用。

当前目录分别包含：

| 单位 | 数量 | 含义 |
|---|---:|---|
| SM70精确输入 | 125 | 100常规、25裁剪，保留全部25149成员声明 |
| SM70历史访问记录 | 118 | 旧快照，不代表本轮全量Native读回 |
| SM89常规资产 | 41 | 当前SHA目录中的已提交资产 |
| SM89裁剪资产 | 41 | 精确parent manifest关联，不继承consumer资格 |
| SM89历史采集任务 | 242 | 独立任务单位，含41提交、1运行、33待采、4失败保留、161专项及2 superseded |

这些数字不能相加当作workload覆盖率。vectorAdd查询得到12个资产记录，不是12个独立程序。完整索引保留生成步骤的原字节及private schema标签；之后的元数据发布由独立Root发布回执证明，不修改旧生成历史。

## 验收证据

- 从冻结SM70计划及当前SM89两个CAS目录构建；41个常规资产的ASSET.json逐一绑定原MANIFEST及COMMIT，裁剪资产只继承精确parent的程序、binary、argv与input身份。
- 21项组件反例拒绝重复身份、计数膨胀、资格抬升、错误/缺失parent、危险CURRENT路径及错误SHA。另一份不导入builder的源码实现重新逐项核对125输入、82资产、242任务，并拒绝5类内容篡改；这不是外部ChatGPT审稿。
- 实际通过公共可执行路径，从EP、DTC和独立/tmp目录查询；统计一致，SM70 COVAR与SM89 vectorAdd过滤有效。三个SM89源CURRENT和队列快照当时均匹配；命令以后每次报告新旧状态。
- 公共工具从已校验的原始源码bytes编译，避免读取或写入pycache；运行前后版本目录不变。正式工具CodeID b3ef238ed1b694a691dc07b0678458e672eebd9b6f2a19b051ec041acb45c87b。
- 完整索引SHA 6795f73eb8af5e4502046a0160591cf963582c33a45a64c2eee9d7bde226d942。相关代码、原字节索引和小型验收回执在本目录snapshots中，来源与SHA见SNAPSHOT_MANIFEST.json。

## 仍在推进

SM70 V13R2与唯一恢复器仍是原进程，COMMIT/同run EXACT尚缺；后续125输入真实Native恢复和5类consumer验收不能由本查询代替。streamcluster全记录验证已闭合1611 kernels/5518423824 records，原POST仍在处理，归档/receiver/CURRENT未闭合。保留原f9/map检查点；若自然超时，优先CPU-only续作，避免重复GPU。

R8已修复初始化阶段及子进程身份读取失败的清理遗漏，合成双65MiB真实并行、断点恢复和错账反例通过；但Root审查发现coordinator取消后仍须独立核owned descendants闭合，已另开有限修复，旧R8明确不准入真实恢复。Root反例与拒绝准入回执均保留。

跨174/109采集回执链正在完成真实双host CPU验收，尚未因此开GPU或授予生产资格。161项实际适配仍缺117 ISA、14 runtime、19 input、5 mapping及6 GPU/variant/SDK主项；不将CPU准备或HOLD清单当作完成。

所有大数据和代码写真164；源KEEP、释放0，Native实际余量保持至少5GiB。健康任务不打断，科研历史、预算和资格不改。外部ChatGPT审稿尚未收到。
