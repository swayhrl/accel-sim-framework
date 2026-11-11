# 条件性精确申请草案：Stencil Ext 负查询短路

**状态：DRAFT / NOT AUTHORIZED / NOT REGISTERED。**此文件是下一轮若工程门通过时的审查框架；现在不得创建科学 Goal、预算、dispatcher 或启动模型。

## 问题与预计成本

目标是检验在同一新 Source、ELF、Stencil 输入和完整应用人口下，无 false negative 的 Ext 负成员证明能否减少扩展查询净成本，并让 optional CLEAN128 的总应用效果超过同源 EXT0。拟申请 **3 个独立完整应用点，各一次消费**；历史 Stencil 单点约 3.7–5 小时只供排期，实际硬墙、RAM/写入和 164 归档上界须在正式 Spec 中按新工程及实时资源重新冻结。旧五点和 EXT1 预算均为 0，不复用。

| 拟议点 | 新 Source 内配置 | 回答的问题 |
|---|---|---|
| B0 | extension 0，负成员证明 OFF | 同源完整应用基线 |
| C2-OFF | extension 2，负成员证明 OFF | 新 Source 的未优化 CLEAN 总效果；与 B0 匹配 |
| C2-ON | extension 2，负成员证明 ON | 与 C2-OFF 比较，隔离负查询短路的净增量；与 B0 比较最终总净效果 |

三点均用同一固定 Stencil 输入、`WV_ZERO_RO`、850 MHz、G32×8、L100、有序 100 kernel、6400 CTA 与原应用数学体。新增开关及任何由实现改变的选项必须进入**完整实际配置**，不能声称旧 283 项原封不动；`B0` 与 `C2-OFF` 的关闭路径须先通过 CPU/配置回归。新 Source/ELF、输入 SHA、三份正式 Spec、Host/consumer pins、完整配置、预算和资源上界目前均为 **待工程门补齐**，不得预填旧 Source5 的 SHA。

主指标为应用 `gpu_tot_sim_cycle`：`C2-ON − C2-OFF` 检验优化净差，`C2-ON − B0` 检验含全部成本的最终净差，`C2-OFF − B0` 固定新 Source 的结构基准。Source5 的 17,534-cycle 回退仅作历史参照，不跨 Source 参与算术比较。附每 kernel cycles、负/正 Ext 查询、证明跳过、假阳性、真实保留响应、lower-issued 读、共享查询/selector/bank 等待，以及真实成本与人口守恒。所有局部计数与应用周期分层解释。

## 提交前必须补齐的工程门

1. 证明负成员证明对所有插入、回收、alias 失效、reader lease、重试、epoch 与跨 kernel 生命周期**无 false negative**，保留现有失败和有限生产 CPU 用例；OFF 路径语义保持一致。
2. 独立列出新增 metadata 位数、比较器/哈希、读写端口、扇出、更新冲突、查询周期与预计关键路径；物理 PPA、时序闭合若未测仍写 `UNKNOWN`。若无可信净收益机会，则撤回本草案。
3. 按新 Source 同步绑定三点的完整 Source/ELF、输入、实际选项、Host/consumer、Native epoch/registry、唯一 owner 与实时资源；保留 5 GiB Native 有效底线、单个全局 128 MiB 恢复保证及其他 owner 已承诺空间。
4. EP-L2-8 明确批准三点、每点一次的**新**科学权限后，才逐点登记、准入与执行；无自动重试或退款。每点验收沿既有完整人口、实际配置、硬件排空、lossless raw、真 164 全 SHA 归档和两个不同 Native 目标完整恢复；Source KEEP。

**停止判据：**无 false negative 证明失败、filter 增加串行正路径等待、成本无法上界、或工程证据显示可跳过的负查询不足以形成可信净收益机会，均不进入完整应用。若新 Source 的三点结果仍不能使 C2-ON 优于 B0，停止该输入上的 optional CLEAN 扩点；即便略优，未有物理成本与更多同源正负输入前也不宣称普适或可发表的硬件收益。
