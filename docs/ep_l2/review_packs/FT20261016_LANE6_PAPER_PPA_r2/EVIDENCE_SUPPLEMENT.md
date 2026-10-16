# r2 证据附件：来源、阶段资格与正文边界

续行 authority：Framework `aec01450d3c527524ee09ee59242f582fafe5354`，
原科学/资源合同仍为 `6c136e2a56a008695f8c8b815723bf8f1a760db9`。
review_r1 的 CONTINUE 未执行；本轮延续同一 Lane-6 分支，r1 pack 保留不改。

## 生产 R0 与理想诊断版本

- R0 发布 `02982b65e87f170103b44c6dbd562a8ffb03841e`；Core
  `126394be46b15f55b9756d43eb9ca9a9baae1c84` / Framework runtime
  `37dec04d223ae65167c5584e56887c74f6540d27`；binary
  `0b504f5573ea0721709bc3439334f7f97a177286eaf73a36876403c7c9228698`。
  原 producer 合同 runtime_ready=true、independent_qualification=false；后续已消费
  Lane-5 发布 `221c7f65cd881ca5da2d20dd0f63a50e35bbc009` 的独立资格证书，
  B16/U_WB16 已为 `INDEPENDENTLY_QUALIFIED`，证书准确绑定同一 R0 source/binary。
  模型内 scope 为 symbolic32B sector版本与实际 requester/lifecycle，非数值 SASS。
  主应用 pair 已由 Lane 5 启动，不等待其他功能；该快照尚无完成的应用 pair。
- Lane-4 发布 `96fbcb612773900fd75268ffe4e00ed9f13d3d42` 的新候选：Core
  `b8b3d55b392fcff793d0aec684bddb73ba3065a9` / Framework
  `438df99dd5138ec42acd7ae9d05e76b9b01e2e5e` / binary `63f26de2…`。
  这是 R0 上的诊断候选，尚不能用 R0 的 B16 作为同 binary ideal numerator。
- 已执行的历史 OLD_D512_STATIC vectorAdd pair 使用更早的**共同** Core
  `6c5dc9f8d6bc4c61a2bae686bad25d05b952bda5`、Framework
  `992ed2d7519fd127c647d581505bf41dcb775afd`、binary `c0405d83…`。
  它们不是上述新诊断候选 binary。图与 manifest 保留实际逐 run 身份，不能把
  publication/latest build SHA 填进历史 row。

完整 binary、ordered config/aux、trace、epoch、feature/ideal、run_key、raw
来源与验证见 `FIGURE_INPUT_MANIFEST.json`、`SOURCE_EVIDENCE_MANIFEST.json`。
历史诊断的 actual raw log、status、input_spec/audit 与重解析 summary 在接收时
重新核对；图中仅两条真实执行行，另 18 格 B16_FIRST_WAVE 保留原 missing 状态。

## 正文事实与证据映射

| Claim | 实现/观测来源 | 当前可说的内容 | 未取得的证据 |
|---|---|---|---|
| 有限 staging、原位 U_WB 与 Bank 服务 | R0 `ep-l2-ft-cache.inc`、`gpu-cache.h`，producer 12 组生产定向与 all-OFF 七 CSV；Lane-5同源独立证书 | 生产 release 已交付、B16/U_WB16独立资格通过 | 完成的应用 pair |
| 数据预算含共同 latch | Lane-1 STORAGE_AND_PORT_LEDGER | 1168/1160 项＋B/U 共同128B/slice；copy 三次 vs 原位 send | 匹配 RTL/工艺差分 PPA |
| 动态借用改善性能 | borrow来源/拒绝、WB-data-full、bank/copy/lower 指标 | 尚不预设正收益；定向 peak126 不是应用 peak | 真实主实验、静态重分区与 copy 归因 |
| sector locality 差异 | 13 行 checkpoint、runtime `db1c9018` / Core `ca3e7bc0` | 工作负载动机；line 与 sector 时间重用不同 | 不是 TVD hit、borrowing 或加速 |
| 历史乐观读参考 | Lane-4 CEILING_RESULTS 两行＋实际 run manifests | 单点 OLD_D512_STATIC 1.721259×，读 DRAM32MB→0 | 非新 B16、非严格上界、非全负载均值 |
| TVD serve/promotion/forward | Lane-2目录/适配模块；R0 尚未包含该功能 | 扩展设计及模块范围 | actual l2_cache hook、matched avoided reads/bytes |
| RO detach / MSHR bypass | Lane-3 whole-commandlist closed-world oracle 与 r3共享 store 适配 | 分开开关、空 FWT 证书负覆盖、completion 实际槽数 N | actual Tag/memport/epoch 接线及独立资格 |
| SASS 模型内正确性 | producer版本/reference与requester实际源汇审计；Lane-5独立资格scope准确绑定 | sector版本、请求identity、退尽等范围 | 不存在的 full-byte/atomic 数值应用输出不假报 PASS |

## 历史 Streaming 13 行的接收

r1 为避免未归档输入只使用 12 行 prefinal。本轮允许核验并使用本地已完成
13 行 checkpoint：`STREAMING13_VERIFICATION.json` 绑定 formal spec、原 CSV、
aggregation manifest、每个 status、sector/Motivation manifest、raw digest，及
聚合器准确源码。按聚合器的闭合/身份规则重新验证并逐数值对照，不改原 CSV。
被接收的是历史 locality，不补填新 B16 结果。所有 13 行保留在 JSON 图输入，
正文紧凑图只按预定 development/validation/scan 顺序选 8 行，完整行在附件。

## 运行与资格快照

开始读取真实 `/workspace/ep_l2_ft20261016_shared/RUN_REGISTRY.json` 时，在
REGISTRY.lock 下观察到9条 COMPLETE_VALID；提交启动记录时再次读取，已出现
两条由 Lane 5 管理的 sad RUNNING 记录，准确 run-key/PID 见 STARTUP_SNAPSHOT。
这些仅是读取时快照，不授权或推断未来运行。Lane 6 无 Core 分支、build、仿真或 lease，不占 Lane 5
正式运行配额。后来完成的 pair 按准确 publication/manifest 增量接收。

续行消费快照另绑定 Lane-1 `2556909e` 和 Lane-4 `be21c95d`；二者保护 R0，
诊断 R1 单独接入与资格仍待完成。Lane-5 资格已解除旧的 runtime/qualification
阻塞。准确 certificate、checks blob 的 hash 和全部逐 gate 引用已核对，见
`DEPENDENCY_SNAPSHOT.json`。Lane 6 没有重新执行 Lane-5 测试。

`RESULT_COVERAGE.json` 独立保留实施、理想诊断、失败/未完成的覆盖；完整五点
之前不算全组 geomean。正文不嵌入 Lane、SHA、任务状态或项目管理过程。
