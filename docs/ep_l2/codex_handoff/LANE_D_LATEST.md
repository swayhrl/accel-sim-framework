# EP-L2 Lane D 最新状态

更新时间：2026-08-30

状态：三个必需里程碑已在隔离的 Framework 分析工作树中完成；当前输入范围严格限定为正式 22/26 中已完成的 11 个工作负载对。未中断、修改或读取后写回 Lane A/B/C 的运行目录或结果根。

## 已完成

- `TEMPORAL_ANALYSIS_READY`：原始 C7e 流审计确认 L2 窗口按 64 个 slice 产生、DRAM 窗口按 32 个 channel 产生；均只输出完整的 5K cycle 窗口。此前 interim summary 的两个相同计数来自后处理把 DRAM 记录数复用于 L2 列，属于分析摘要错误，不是 producer 漏采样。
- `CALIBRATION_ANALYZER_READY`：分析器以 workload、variant、Core/Framework SHA、config hash、descriptor 容量、L1 类别、频率和 trace identity 记录并校验来源。D512/L1 单元到达后可增量加入；目前不会把尚未完成的单元伪造成 delta。
- `D512_COST_READY`：D256→D512 的额外物理 metadata 估计为每 slice 2--4 KiB、全芯片 128--256 KiB（64--128 bit/descriptor 的透明范围），即 144 KiB/slice 与 9 MiB/chip payload 预算的 1.39--2.78%。这不是面积或性能结论。

## 验证与产物

- 单元/fixture 测试：7 项通过，覆盖精确 percentile、缺失字段、burst、D256/D512 与 L1 META/BANK 配对、来源不匹配、缺基线、重复记录。
- 真实数据 smoke：22 条记录（11 workload × Legacy/Banked），全部 cardinality `PASS_FULL_WINDOWS_ONLY`。
- 审查包：`docs/ep_l2/review_packs/CALIBRATION_ANALYSIS_INFRA_r1/`。
- 分析器源码：`hrl/ep-l2-cal-analysis-v0` 的 `1b1f5f3e1faecaf8a5344eb7687d00a032a194e9`。
- 成本报告：`docs/ep_l2/calibration/DESCRIPTOR_METADATA_COST.md`。

## 后续边界

收到工作板中 Lane A/B/C 对应行的 `DONE` 及精确证据路径后，Lane D 只刷新分析包。不会自行宣布 `BASELINE-DECISION`，也未实现 RO no-MSHR、TVD 或 Unified borrowing。
