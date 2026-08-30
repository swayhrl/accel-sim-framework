# EP-L2 Lane D 最新状态

更新时间：2026-08-30

状态：`FINAL_CALIBRATION_CONVERGENCE_REVIEW_READY`。已完成只读的最终校准收敛与 13-workload archetype checkpoint；未启动模拟、重建或修改 B/C/E 结果根。

## Final convergence r1

- 消费的主矩阵只有已提升且 V2-contract-bound 的六个 cell：D256/D512 BASE 各 26 行，四个 Lane-C L1 敏感性 cell 各 7 行，共 80 行；Lane-E Line-MSHR 2×2 保持为补充受控敏感性，未混入主维度。
- 修复并测试了一个 provenance 入口兼容性 bug：已提升 D512 运行把运行时配置哈希放在 `run_status.audit`；分析器现优先使用此权威逐运行审计字段，仍严格与 contract 精确匹配。18 项测试通过。
- 建议（非默认变更、待 ChatGPT 决策）为 D512 / L1 BASE / MSHR128：D512 消除有界成本的 descriptor256 结构性节流；小的周期响应和 Lane-E 0.38% Line-MSHR 敏感性表明下游替代，不是“选择 D512 以制造 MSHR bottleneck”。
- Unified/RO/TVD 的决定性机会条件均标为 `UNKNOWN_NEEDS_TELEMETRY`；M0 observation-only 与 M1 behavior-preserving substrate 是推荐的下一阶段，而非功能实现授权。
- 审查包：`docs/ep_l2/review_packs/FINAL_CALIBRATION_CONVERGENCE_r1/`，含 13-row 分类、合同路径、最终矩阵、时间/原生带宽摘要、Lane-E supplement、基线与机制建议、SHA256SUMS。

## 已完成

- `TEMPORAL_ANALYSIS_READY`：原始 C7e 流审计确认 L2 窗口按 64 个 slice 产生、DRAM 窗口按 32 个 channel 产生；22 条记录都通过行数、ID 集合、重复 `(stream,start)` 键、每流缺窗，以及“每个精确时间组包含完整 64/32 个唯一 stream”的对齐检查。DRAM 全局 cycle 起点按 5000/5001 间隔出现，是 850MHz DRAM 采样节拍的已验证语义；并非缺窗。通道不均衡计算现在把 `bandwidth_util_denominator_bytes` 视为必填字段，缺失或任一时间组不完整会显式输出 `NOT_EMITTED`，绝不静默丢行。
- `CALIBRATION_ANALYZER_READY`：分析器现在要求机器可读 lineage/effective-config contract，且在读取记录前验证实际 `runtime_config_composite_sha256` 与 contract 的精确绑定，并要求 `config_delta_gate.status=PASS` 及证据路径。跨 SHA 单元只有在明确继承 formal C7e SHA、带 `PASS` 等价门证据、且 source delta 被声明时才能配对；D512/META-HR/BANK-HR 的 effective config 差分必须恰好等于授权字段。D512/L1 单元到达后可增量加入；目前不会把尚未完成的单元伪造成 delta。
- `D512_COST_READY`：D256→D512 的额外物理 metadata 估计为每 slice 2--4 KiB、全芯片 128--256 KiB（64--128 bit/descriptor 的透明范围），即 144 KiB/slice 与 9 MiB/chip payload 预算的 1.39--2.78%。这不是面积或性能结论。

## 验证与产物

- 单元/fixture 测试：17 项通过，新增不等权双通道快照（验证加权聚合而非末通道）、不完整快照 fail-closed、运行时配置哈希绑定、缺失分母和跨流时间错位拒绝。
- 真实数据 smoke：22 条记录（11 workload × Legacy/Banked），全部 cardinality `PASS_FULL_WINDOWS_ONLY` 且通过精确时间组对齐；每条原生 DRAM 指标都从保留 raw logs 的最后一个完整 32-channel snapshot 重解析到 `NATIVE_DRAM_BANDWIDTH.csv`，输出 `n_cmd` 加权均值、p50/p95/max 和 `n_cmd` 总和。
- C7e `bandwidth_util` 已更名为 `lower_admission_byte_rate_norm`；它是 lower-path admission 强度，不能解释为物理数据总线利用率。5K 物理总线窗口指标未保留，明确输出 `NOT_EMITTED`。
- 审查包：`docs/ep_l2/review_packs/CALIBRATION_ANALYSIS_INFRA_r1/`。
- 分析器源码：`hrl/ep-l2-cal-analysis-v0`（V3 native aggregation / runtime-config binding 修复）。
- 成本报告：`docs/ep_l2/calibration/DESCRIPTOR_METADATA_COST.md`。

## 后续边界

审查修复已完成，现请求最终 ChatGPT 复审。收到工作板中 Lane A/B/C 对应行的 `DONE` 及精确证据路径后，Lane D 只刷新分析包。不会自行宣布 `BASELINE-DECISION`，也未实现 RO no-MSHR、TVD 或 Unified borrowing。
