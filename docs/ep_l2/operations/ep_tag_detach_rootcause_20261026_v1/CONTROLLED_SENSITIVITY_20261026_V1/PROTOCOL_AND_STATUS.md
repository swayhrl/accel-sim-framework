# 有限受控访存敏感性 Goal

Goal：`EP_L2_MEMORY_PATH_CONTROLLED_SENSITIVITY_20261026_V1`。用户2026-10-26明确授权启动。当前唯一主整合者EP-TAG-ROOTCAUSE，科研owner EP-MAIN；有界子任务已完成资源、独立验收和L1条件准备，没有长期科研Lane。

## 顺序与有限预算

|端点|唯一变化|完整应用额度|条件|
|---|---|---:|---|
|E1|DRAM850→935MHz；core/ICNT/L2仍1132MHz|1|先执行|
|E2|L1 MissQ16→32；DRAM仍850MHz|1（条件性）|E1有效接受，且L1 application accesses1500000、MissQ重试≥310197|

E2门限是预先冻结的信息价值标准（保留基线至少25%的单位访问重试压力），不是统计显著性检验，不按E1收益正负或detach筛选。E2比较旧850/MissQ16，不比较E1@935；不声称两因素交互。两端均无自动重试、无退款；850基线不重跑。

可并行的是资源/来源审查、E2配置准备、验收与分析工程；E2模型不能先于E1决策。既有接受基线UUID `a6b61f77-2ff6-45ad-897c-df0812d01ae8`、75039cycles、56M instructions，不与main61混合。原Tag-detach科学负结果仍保留。

## 精确来源与资格

- Core `1093d2629e3d6a9130ba25b9dd119b6f3e16c092`，Framework `9dd1ee57a83d83b56b7874bc7c716185ab52c8f7`，main SHA `e511cce7d8bcd5a3ebbe6255f42ebe153547484a69c6857ab55f7a8835a2dc33`。
- 原四config逐字节保留，第五份只有一个允许option；独立验收比较全部282个实际回显option，拒绝其它差异。
- 164 trace两成员因FUSE inode变化做了关闭重开完整SHA复核，内容与旧接受输入完全一致；两遍约2.384s，本地新trace payload0B。旧global stat binding没有改。
- 新native加载help资格每case最多1次；它不是应用接受。实际运行还需新intent/UUID、完整指令/CTA、64slice/drain、原212/r5及RO守恒和新clock/配置证明。
- 仍无SASS数值输出验证、物理GPU性能、PPA或T独立收益主张。

## 共用入口与互不干预

当前sole-entry只增加两个精确EP leaf，全部既有DTC/COPY_ONLY操作逐参数委派到原入口字节副本。没有改DTC运行源码、计划、控制器或父进程，没借用它的长期qualification lease。

新EP每case有私有运行锁；shared `REGISTRY_UPDATE.lock`只在register/consume/close短持。预算由本新授权追加，只消费对应新request，不借DTC remaining。INTENT和consume在fork之前；独立mock测试证明peer行不变及已消费request不可重试。

真实新写/restore/工程包络512MiB：结果128、恢复128、临时128、工程128；独立RSS cap9GiB、单CPU16/nice10、wall7200s。CPU16及sibling272避开全部已核查DTC planned模型/控制CPU。没有GPU调用。

为兼容DTC的5GiB floor与EP的7GiB+1GiB unknown门，登记给peer看到的reserve为3.5GiB：真实写入0.5GiB＋共享floor兼容余量3GiB。EP自身核算不再重复加入该3GiB。它不是大资产新副本，也未改变任何peer reserve。

admission按当前已承诺/claimed剩余写入及真实RAM包络判断；运行期按实际headroom和自身hard cap保护，不因peer合法futureclaim重新做准入或把短暂metadata变化误作物理不足。大资产默认真164，174只必要热输出；空间不足交用户清理。

## 实际执行状态

E1已通过prepare、fresh native help与独立新request登记，实际模型已启动：

- cohort：`EP_NATIVE_VECTOR_DRAM935_SENSITIVITY_20261026_V1`
- UUID：`375881f2-a811-4f71-a7cf-d171eed6fdf7`
- 原生模拟器PID：1408395（精确start_ticks见实际maps回执）
- raw回显DRAM935、L1 MissQ16；独立header审计全部282项仅clock变化。
- E2仅静态准备，未登记/未启动。

此时尚无E1终态或性能结论。后续结果统一写入FINAL_REPORT.md，不以中途日志充当科学接受。

## 验收与归档

独立工具保留冻结model numeric body并复用原r4/r5 decoder，替换为新EP-MAIN资格权威；科学接受不借用旧E签名。cycles、RO/merge、DRAM/WBbytes及detach均为观测结果，不预设改善或与基线相等。

结果自然结束后先验收、形成samebinary比较及E2决策，再COPY_ONLY到真164新namespace，关闭重开全SHA、native restore及第二个独立Target恢复。可移植恢复工具仅从bundle读取f/V9，独立于旧runtime/controller；payload COMMIT与补充工具SHA清单边界分开。直到归档恢复完成才CLOSED并释放预留。源KEEP。
