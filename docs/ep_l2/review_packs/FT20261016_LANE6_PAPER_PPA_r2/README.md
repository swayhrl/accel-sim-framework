# Lane 6 r2 — 紧凑投稿正文、生产成本差分与增量结果接收

续行：`aec01450d3c527524ee09ee59242f582fafe5354`；保留原 `r1` 不改。
同分支 `hrl/ep-l2-ft20261016-lane6-v1` 延续执行，未重建初始 Goal。

先读 `PAPER_DRAFT_ZH_V2.md`：真实 WB 池是主线，TVD/RO 为扩展；正文已移出
项目管理、Lane、hash/status 与 NOT_RUN 表格。`EVIDENCE_SUPPLEMENT.md`
保存这些精确可审查信息；`PPA_LEDGER.md` 逐项区分代码字段、参数化表示和
未知 RTL/工艺。R0 data RAM 外共同128B/slice copy latch 已计账；RO r3模块
completion 容量按 payload_budget 映射，不再以128项算例冒充真实容量。

图：`FIG02_HISTORICAL_OPTIMISTIC_READ` 为单点旧静态乐观参考；
`FIG03_VERIFIED_SECTOR_LOCALITY` 使用已重新核验的完整13行历史 checkpoint。
两图各有 PDF/SVG；紧凑 3.35-inch 单栏尺寸是当前工作版式，不声称已核实特定
会议页数/模板。完整数据、显示子集、hash 与正确性范围见 figure/source manifest。

阶段末新增并核验首个正式 sad pair：110593/110573 cycles，1.000180876×，
基本持平；两侧peak1，无capacity压力。第三张图 `formal_sad/WB_PAIRS` 只显示
实际1/5 pair，其余缺失显式保留、五点均值null；正文包含实际copy/Bank/DRAM
对照与有限结论，未把小的周期变化写成容量收益。

使用 `/usr/bin/python3`（Matplotlib/Pillow）执行：

```bash
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 PATH/build_revision.py \
  --framework-repo FRAMEWORK_PRODUCER_WORKTREE \
  --core-repo READ_ONLY_CORE_REPO \
  --streaming-worktree READ_ONLY_HISTORICAL_STREAMING_WORKTREE \
  --output-dir NEW_OUTPUT_DIR
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 PATH/test_result_intake.py
```

producer commit 与准确原输入在 manifest 中。13行 checkpoint 原 CSV 不修改，
按原聚合器逐 row 检验 source/config/raw/sector/Motivation 闭合并重算数值；
原始路径与 hashes 保留，规范化 JSON 图输入提交到本包以便远端读者复核。
没有本地历史资产时可使用已核验图输入检查制图数据，不能伪称重做 raw 审计。

`RESULT_INTAKE_CONTRACT.md`、`result_intake.py` 与 `plot_qualified_pairs.py`
支持完整 pair 滚动发布、全五点前不求均值、保留失败/未完成，区分实际
finite_wbuf 参数与优化位，并允许如实标记 SASS 数值不可观测。
`native_pair_intake.py` 优先直接映射 Lane-5 已发布的原生 CSV/PAIR_RECEIPT，
不强制其创建新 normalized packet；资格、run-key、source/binary/config/trace、
本地冻结 raw/config/executable 的校验均在接收侧执行。
测试均为轻量 synthetic intake；不是新模拟器资格或性能结果。

本包不触碰 R0/R1 binary、trace、机制代码、实验输入、共享配额或旧科学 CSV。
Lane-5 独立资格与 B16/U_WB 主实验优先，其他机制与论文不作为其先决条件。
