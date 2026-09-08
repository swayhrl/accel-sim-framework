# C12 激进并行验收标准

本文件只验收并发调度是否安全、可审计；22 点科学结果仍以 `C12_ACCEPTANCE_MATRIX.md` 为准。

必须满足：

- [ ] 当前健康 F0 worker 未被为了并发而无故终止。
- [ ] 总 simulator 并发已尝试提升到 6-way；若资源持续 GREEN，可试 8-way。
- [ ] 每个 arm 使用独立 output dir。
- [ ] 已实现 per-arm 独占锁，ROI/arm/lseg 唯一。
- [ ] 同一 arm 同一 output dir 任意时刻最多一个真正 `accel-sim.out` owner。
- [ ] shell/tee parent 不被误判为重复 simulator。
- [ ] 发现重复 launcher 时只处理 C12 自己的后发重复 worker，不触碰其他窗口。
- [ ] 猜测性提前运行 arm 标记为 `SPECULATIVE_EARLY_EXECUTION_PENDING_BASELINE_GATE`。
- [ ] 两个 F0 PASS 后对早跑 arm执行 promotion audit；identity/gate一致才晋升 PASS。
- [ ] F0 暴露全局 identity/执行问题时，受影响早跑 arm 被 invalidated/quarantine，并重跑。
- [ ] live arm state 包含 owner/simulator PID、attempt、hash、progress，并可避免重复调度。
- [ ] 资源采样记录 MemAvailable、PSI、iowait、swap、RSS、并发数；GREEN/YELLOW/RED 动态降级可用。
- [ ] 单 arm failure 不导致其他健康 arm被杀；失败 evidence 有隔离记录。
- [ ] resource victim 降并发后重跑；parser-only 问题不无谓重跑 simulator。
- [ ] 并发没有改变 binary/config/trace/registration/PA contract/22点矩阵。
- [ ] 仍以同 ROI C5 F0 为唯一正式性能 baseline。
- [ ] 22/22 最终 terminal gate 不因早跑或并行而放宽。

最终 review pack 中的 `FAILURE_RETRY_AUDIT.md` / `RESOURCE_HISTORY.tsv` 应能追溯所有并行 attempt、重复 launcher处置、并发升降和 early-result promotion。
