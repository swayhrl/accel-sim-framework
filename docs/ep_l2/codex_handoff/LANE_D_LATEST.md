# EP-L2 Lane D 最新状态

更新时间：2026-08-30

状态：已按 ChatGPT Lane-D 审查意见完成 V2 自修复并仅重处理既有数据；当前输入范围仍严格限定为正式 22/26 中已完成的 11 个工作负载对。未中断、修改或读取后写回 Lane A/B/C 的运行目录或结果根。

## 已完成

- `TEMPORAL_ANALYSIS_READY`：原始 C7e 流审计确认 L2 窗口按 64 个 slice 产生、DRAM 窗口按 32 个 channel 产生；22 条记录都通过行数、ID 集合、重复 `(stream,start)` 键和每流缺窗检查。DRAM 全局 cycle 起点按 5000/5001 间隔出现，是 850MHz DRAM 采样节拍的已验证语义；并非缺窗。此前 interim summary 的两个相同计数来自后处理把 DRAM 记录数复用于 L2 列，属于分析摘要错误，不是 producer 漏采样。
- `CALIBRATION_ANALYZER_READY`：分析器现在要求机器可读 lineage/effective-config contract。跨 SHA 单元只有在明确继承 formal C7e SHA、带 `PASS` 等价门证据、且 source delta 被声明时才能配对；D512/META-HR/BANK-HR 的 effective config 差分必须恰好等于授权字段。D512/L1 单元到达后可增量加入；目前不会把尚未完成的单元伪造成 delta。
- `D512_COST_READY`：D256→D512 的额外物理 metadata 估计为每 slice 2--4 KiB、全芯片 128--256 KiB（64--128 bit/descriptor 的透明范围），即 144 KiB/slice 与 9 MiB/chip payload 预算的 1.39--2.78%。这不是面积或性能结论。

## 验证与产物

- 单元/fixture 测试：12 项通过，覆盖精确 percentile、缺失字段、严格 burst gap、重复/缺失流键、D256/D512 与 L1 META/BANK 配对、同 SHA、经审查等价的跨 SHA、无等价证据/错误 base lineage、隐藏 config 改动、缺基线与重复记录。
- 真实数据 smoke：22 条记录（11 workload × Legacy/Banked），全部 cardinality `PASS_FULL_WINDOWS_ONLY`；原生 DRAM `bwutil/n_cmd` 已从保留 raw logs 重解析到 `NATIVE_DRAM_BANDWIDTH.csv`。
- C7e `bandwidth_util` 已更名为 `lower_admission_byte_rate_norm`；它是 lower-path admission 强度，不能解释为物理数据总线利用率。5K 物理总线窗口指标未保留，明确输出 `NOT_EMITTED`。
- 审查包：`docs/ep_l2/review_packs/CALIBRATION_ANALYSIS_INFRA_r1/`。
- 分析器源码：`hrl/ep-l2-cal-analysis-v0`（V2 provenance/config safety 修复）。
- 成本报告：`docs/ep_l2/calibration/DESCRIPTOR_METADATA_COST.md`。

## 后续边界

审查修复已完成，现请求 ChatGPT 复审。收到工作板中 Lane A/B/C 对应行的 `DONE` 及精确证据路径后，Lane D 只刷新分析包。不会自行宣布 `BASELINE-DECISION`，也未实现 RO no-MSHR、TVD 或 Unified borrowing。
