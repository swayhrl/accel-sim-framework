# Stencil EXT0/1/2 迁移成本审查与下一步决定

2026-11-11，EP-L2 Main。此件使用已接受的 Source5 三点和既有逐 kernel 证据；没有新模型、预算、dispatcher 或 Trace 扫描。共享 Native registry 的 3 个 EP 请求外层状态已先由 owner 收为 `CLOSED_COMPLETED`，见相邻 `owner_closeout_v1/`。

## 1. 可确认的对照

三点 Source archive、ELF、输入、有序 100 kernel、6400 CTA、2,193,446,000 指令和 283 项实际配置相同，只有 extension 0/1/2 变动。全部 `CLOSED_ACCEPTED`、真 164 归档并双恢复。

| Stencil | cycles | 与前点差值 | 解释口径 |
|---|---:|---:|---|
| EXT0 | 4,768,893 | — | 同源基线 |
| EXT1 | 4,787,045 | +18,152（+0.381%） | 空 Ext 扩展硬件与串行查询的**迁移包净差** |
| EXT2 | 4,786,427 | −618（相对 EXT1 为 −0.0129%） | 同扩展硬件下启用 CLEAN 的**策略包净差** |

EXT2 相对 EXT0 仍净慢 17,534 cycles（+0.368%）。100 个 kernel 的迁移差全部为正，最小 34、中位 187.5、最大 335 cycles；策略差为 59 快、1 平、40 慢。按 EXT2 是否有 Ext response 分为两个各 50 kernel 的组，迁移包分别净慢 8,996/9,156 cycles，策略包分别净快 312/306 cycles。分组并非独立实验，跨 kernel 状态延续，不能把这两组当响应的因果效应。

EXT1 无 Ext install、spill、response，运行结束的 64 个 slice 均 `ext_live=0`，但有 2,373,035 次 Ext query 与 2,393,910 次 selector read。EXT2 有 2,410,324 次 Ext query、56,712 次 Ext retained response、6,729 次 CLEAN install，且相对 EXT1 的实际 lower read 少 66,306 次；结束时各 slice `ext_live=1..9`，仅是终态快照。`response/query` 不是命中率，response 也不逐一等于省下的 DRAM 请求。`block_payload` 从 EXT0 到 EXT1 增 7,145,446 是宽泛事件分类，不能解释为 7,145,446 个独占 GPU 阻塞周期。现有导出明确将 Ext 专属等待标为 `UNKNOWN`，故不能把 +18,152 cycles 唯一归因到某一个查询门或端口。

同 Source5 GEMM 是必要反例：EXT0/1/2 为 550,642/550,109/550,109 cycles；EXT0→EXT1 **快 533 cycles**，EXT1→EXT2 为 0，Ext 无 install 或 response。迁移包的全应用方向与输入有关，不能将 Stencil 的回退推广为普遍固定开销。现有文献复核也提醒，局部 miss、保留响应或查询次数不能直接代替全应用收益；见本项目 `EP_L2_LITERATURE_AND_EVIDENCE_REVIEW_20261110.md`。

## 2. Source5 路径与可证伪假设

固定 Core `3d3887bb2e8d5073d13b0792ff9116834e89fe2f` 的 `src/gpgpu-sim/ep-l2-tvd-cache.inc`：约第 243–269 行在 Base miss 后先确认 Base absence，再经共享查询周期进入 Ext `find`；约第 67–78 行 Base selector 收费两周期；第 93–124 行仅模式 2 执行 CLEAN spill。工程申请明确 Base 查询 1 周期、真实 miss 后 Ext 再 1 周期，共享 128 项比较结构；物理 PPA 仍未知。模式 1 的 Ext 为空仍走扩展查询路径，因此可作为迁移包的负对照，但已导出计数不足以定位关键路径。

**候选假设 H1：**Stencil 的大量可确定为 Ext 不存在的 Base miss，在串行 Ext 查询和共享端口上引入关键路径等待。一个与 Base 查询并行、**无 false negative** 的 Ext 负成员证明若能跳过这些负查询，可能降低迁移包净成本，同时保留真实 Ext 命中、CLEAN 生命周期与既有仲裁。实现形式只作为工程候选，例如有界计数式过滤器；其额外元数据、哈希/更新端口、读时序和假阳性必须计入成本，不能声称免费或已经可综合。

H1 目前**尚未证明**：EXT2 的最终非零占用不能推断运行中占用；查询、indexed read 和 response 的分母不同；现有 `lookup_wait_cycles` 不完整覆盖 Ext 等待。若增加分项计数后，负查询并未阻塞前端，或过滤器自身串行延迟抵消跳过成本，H1 即被否证。若过滤器无法在 insert、reclaim、reader lease、alias 失效、重试和跨 kernel 状态下保持无 false negative，也应停止该方向。

## 3. 决定与执行门

**建议先做有界工程可行性与成本审查，暂不申请或启动新的完整应用点。**即使理想地抹去 Stencil 现测全部迁移包，原 CLEAN 策略包只改善 618 cycles（约 0.013%），而 optional CLEAN128 已有 58,880 逻辑位/slice 的模型估算，新增过滤器还会增加成本。这个理想上限仅用于本轮取舍，不是新 Source 的性能预测。GEMM 没有 CLEAN 增量。因此没有依据立即扩大负载或再跑一个昂贵科学点。

工程门只复用既有 CPU/Input/Host 资格，并要求：证明无 false negative 与状态守恒；清楚导出负/正 Ext probe、被跳过数、Ext 等待与端口竞争，说明计数是否重叠；对过滤器位数、读写端口、更新时序、查询与关键路径做可复核上界；过滤器关闭时保持 Source5 语义；保留所有原失败用例。无需重跑历史 Goal、巨大 Trace、109 GPU 或论文编辑。若上述门全部通过且有可信的净收益机会，才把相邻 `EXACT_REQUEST_DRAFT.md` 补齐 Source/ELF、完整选项和资源合同，交 EP-L2-8 决定是否授予**新的**三点科学执行权限。此次用户同意的是审查与准备，未登记或消费该草案。

## 4. 固定证据

- 最终三点汇总：`final_ext1_v1/FINAL_SUMMARY.json`，SHA256 `5d85e7bbf19889fc939e9c322e277ba6e33c8424e0806c85be4ea73e395dcdf3`。
- 逐 kernel 阶段证据：`final_ext1_v1/TRIPLET_PHASE_EVIDENCE.json`，SHA256 `529119440454c7daffbbabbd82bbd8162527b0562542835242b6a25a8d0e2289`。
- EXT2 接受 bundle：`cases/EP_PERF_CLEAN128_STENCIL_WV_EXT2_20261109_V1/run/aede460f-6e30-4416-b5af-c64c92127db6/VALIDATED_APPLICATION_BUNDLE.json`，SHA256 `e160382e7c778fd78decac89b377cdcc89dbe3f6fa705c704561f7ef1aa4c779`。
- Source5 路径文件 SHA256 `571ca7dff27f9cd2e5666594b7a4f7befafe08d11952ba5eda9996b0b1424e1f`；工程申请基点 `ea480a05fb32eeb6b88dd1d8be1b0b9c89eb8526`。
